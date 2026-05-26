"""RAG Retriever — Phase 1 Slice 4 (pgvector + graceful fallback).

설계 원칙:
  1. 사용자 요청을 절대 차단하지 않는다. 모든 실패는 fallback 으로 흡수.
  2. env 미설정 / 연결 실패 / 쿼리 오류 / 빈 결과 — 각 경로마다 별도 fallback_reason 기록.
  3. Phase 1은 실제 knowledge base 없이도 동작 (대부분 호출이 fallback 통과).

`retrieval_policy.md §2` 검색 파라미터 (top_k, threshold)는 config에서 주입 가능.
"""

from __future__ import annotations

import logging
from typing import Any

from ..config import get_settings
from .fallback import fallback
from .types import RAGReference, RetrievalResult

logger = logging.getLogger(__name__)


# pgvector / psycopg는 optional. import 실패해도 fallback으로 동작.
try:  # pragma: no cover — import-time fallback
    import psycopg  # type: ignore[import-not-found]
except Exception:  # pragma: no cover
    psycopg = None  # type: ignore[assignment]


# ─── 임베딩 (Phase 1: optional) ───────────────────────────────────────

def _embed_query(query: str) -> list[float] | None:
    """쿼리 임베딩 생성 (text-embedding-3-small, 1536차원).

    Phase 1: OpenAI 호출이 실패하거나 키가 없으면 None 반환 → 호출자가 fallback 분기.
    실제 호출은 DB가 연결되었을 때만 의미가 있으므로 lazy import.
    """
    settings = get_settings()
    if not settings.openai_api_key:
        return None
    try:
        from openai import OpenAI  # lazy import

        client = OpenAI(api_key=settings.openai_api_key)
        resp = client.embeddings.create(
            model="text-embedding-3-small",
            input=query,
        )
        return list(resp.data[0].embedding)
    except Exception as e:  # pragma: no cover — 네트워크/키 오류
        logger.warning("RAG embedding failed: %s", e)
        return None


# ─── 메인 진입점 ───────────────────────────────────────────────────────

def run_rag_retrieval(
    query: str,
    *,
    top_k: int | None = None,
    threshold: float | None = None,
) -> RetrievalResult:
    """pgvector 검색 1회 수행. 실패 시 fallback() 반환.

    Args:
        query: 검색 텍스트 (Phase 1은 사용자 input 그대로).
        top_k: 상위 N개 chunk (기본 settings.pgvector_top_k).
        threshold: cosine similarity 최소값 (기본 settings.pgvector_threshold).

    Returns:
        RetrievalResult — 성공 시 references 채워짐, 실패 시 빈 배열 + fallback_reason.
        절대 예외를 호출자에게 던지지 않는다 (router는 항상 200 응답 가능해야 함).
    """
    settings = get_settings()
    db_url = settings.pgvector_database_url or settings.database_url
    _top_k = top_k if top_k is not None else settings.pgvector_top_k
    _threshold = threshold if threshold is not None else settings.pgvector_threshold

    if not db_url:
        return fallback(reason="env_missing")

    if psycopg is None:  # pragma: no cover — install 누락 시
        logger.warning("psycopg not installed; RAG fallback")
        return fallback(reason="pgvector_unreachable")

    embedding = _embed_query(query)
    if embedding is None:
        return fallback(reason="query_error")

    try:
        with psycopg.connect(db_url, connect_timeout=3) as conn:  # type: ignore[union-attr]
            with conn.cursor() as cur:
                # pgvector cosine similarity = 1 - (embedding <=> query_vec)
                # rag_data_contract §5.3 와 동일한 쿼리 형태.
                sql = (
                    f"SELECT chunk_id, title, content, metadata, "
                    f"       1 - (embedding <=> %s::vector) AS similarity "
                    f"FROM {settings.pgvector_table} "
                    f"ORDER BY embedding <=> %s::vector "
                    f"LIMIT %s"
                )
                cur.execute(sql, (embedding, embedding, _top_k))
                rows = cur.fetchall()
    except Exception as e:
        logger.warning("RAG retrieval failed (pgvector), using fallback: %s", e)
        return fallback(reason="pgvector_unreachable")

    references = _rows_to_references(rows, threshold=_threshold)
    if not references:
        return fallback(reason="empty_result")

    return RetrievalResult(
        references=references,
        used_fallback=False,
        fallback_reason=None,
    )


# ─── DB row → RAGReference 변환 ────────────────────────────────────────

def _rows_to_references(
    rows: list[Any],
    *,
    threshold: float,
) -> list[RAGReference]:
    """psycopg rows → RAGReference 목록.

    Row 형식 (run_rag_retrieval SQL과 매칭):
        (chunk_id, title, content, metadata, similarity)

    threshold 미통과 chunk는 제외 (retrieval_policy §2).
    """
    out: list[RAGReference] = []
    for row in rows:
        try:
            chunk_id, title, content, metadata, similarity = row
        except (TypeError, ValueError):  # pragma: no cover
            continue

        sim_f = float(similarity or 0.0)
        if sim_f < threshold:
            continue

        meta_dict: dict[str, Any] = metadata if isinstance(metadata, dict) else {}
        snippet = (str(content or "")[:300])

        out.append(
            RAGReference(
                source_id=str(chunk_id),
                title=str(title or ""),
                snippet=snippet,
                used_reason=None,  # Phase 1: router에서 채우지 않음
                similarity=max(0.0, min(1.0, sim_f)),
                metadata=meta_dict,
            )
        )

    return out


__all__ = ["run_rag_retrieval", "RetrievalResult", "RAGReference"]
