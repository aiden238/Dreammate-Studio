"""Phase 7 Slice 3 — OpenAI embedding wrapper (ADR-025).

text-embedding-3-small (1536 dim) 호출.
graceful fallback: 실패 시 None + warning (chunk 저장 X, plan 차단 X).

References:
  - docs/decisions/phase_7_rag_architecture.md (ADR-025 §2 Embedding)
  - knowledge/rag/metadata_schema.md
"""
from __future__ import annotations

import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)

# Gemini embedding taskType 비대칭 (A9 측정: 이 비대칭이 ko 0.7 통과의 핵심).
#   문서 적재(ingest/promote)는 DOCUMENT, 검색 쿼리는 QUERY 로 임베딩해야 측정된
#   +0.20~0.34 이득이 실현된다. OpenAI 경로(client 주입/provider=openai)는 taskType 무시 → no-op.
TASK_TYPE_QUERY = "RETRIEVAL_QUERY"
TASK_TYPE_DOCUMENT = "RETRIEVAL_DOCUMENT"


async def _embed_gemini(
    text: str, *, task_type: str = TASK_TYPE_QUERY
) -> Optional[list[float]]:
    """gemini-embedding-2 임베딩 (httpx REST, taskType 비대칭). graceful None.

    A9 측정: ko 숏폼에서 OpenAI 압도(0.7 통과). ★ 임베딩만 Gemini, 생성은 GPT 계열(분리).
    문서=RETRIEVAL_DOCUMENT, 쿼리=RETRIEVAL_QUERY 비대칭 최적화.
    """
    from ..config import get_settings

    s = get_settings()
    key = getattr(s, "google_api_key", "") or ""
    if not key:
        logger.warning("embedding_failed: google_api_key 미설정 (graceful)")
        return None
    model = getattr(s, "rag_embedding_gemini_model", "gemini-embedding-2")
    dim = int(getattr(s, "rag_embedding_dim", 1536))
    try:
        import httpx

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:embedContent"
        body = {
            "content": {"parts": [{"text": text}]},
            "outputDimensionality": dim,
            "taskType": task_type,
        }
        async with httpx.AsyncClient(timeout=40) as c:
            r = await c.post(url, params={"key": key}, json=body)
        if r.status_code != 200:
            logger.warning("embedding_failed: gemini %s (graceful)", r.status_code)
            return None
        vals = r.json().get("embedding", {}).get("values")
        return vals if isinstance(vals, list) else None
    except Exception as exc:
        logger.warning("embedding_failed: gemini %s (graceful)", exc.__class__.__name__)
        return None


async def embed(
    text: str,
    *,
    model: str = "text-embedding-3-small",
    client: Any | None = None,
    task_type: str = TASK_TYPE_QUERY,
) -> Optional[list[float]]:
    """OpenAI embedding API → 1536 dim float list.

    Args:
        text: 임베딩할 텍스트 (빈 / 공백만 → None)
        model: embedding model (env RAG_EMBEDDING_MODEL override 가능)
        client: AsyncOpenAI mock or runtime client. None 시 지연 import.

    Returns:
        embedding vector (list[float], 1536 dim) 또는 None (graceful 실패).

    Graceful 실패 사유 (모두 None 반환 + warning):
      - 빈 text / 공백만
      - openai 패키지 미설치
      - API 호출 예외 (network / quota / 인증)
      - 응답 empty / data 비어 있음
    """
    if not text or not text.strip():
        return None

    # Phase 27 A9: RAG 임베딩 provider 분기 (gated, default openai). client 주입(테스트 mock)이면
    #   provider 무시 → openai 경로(behavior-preserving). provider=gemini 면 gemini 경로 반환
    #   (openai 폴백 금지 — 임베딩 공간 불일치 방지).
    if client is None:
        try:
            from ..config import get_settings

            _provider = getattr(get_settings(), "rag_embedding_provider", "openai")
        except Exception:
            _provider = "openai"
        if _provider == "gemini":
            return await _embed_gemini(text, task_type=task_type)

    if client is None:
        try:
            from openai import AsyncOpenAI  # type: ignore[import-not-found]

            client = AsyncOpenAI()
        except ImportError:
            logger.warning(
                "embedding_failed: openai package not installed (graceful)"
            )
            return None
        except Exception as exc:
            logger.warning(
                "embedding_failed: client init %s (graceful)",
                exc.__class__.__name__,
            )
            return None

    try:
        resp = await client.embeddings.create(input=text, model=model)
        if not resp or not getattr(resp, "data", None):
            logger.warning("embedding_failed: empty response (graceful)")
            return None
        first = resp.data[0]
        embedding = getattr(first, "embedding", None)
        if embedding is None:
            logger.warning(
                "embedding_failed: data[0].embedding missing (graceful)"
            )
            return None
        if not isinstance(embedding, list):
            return list(embedding)
        return embedding
    except Exception as exc:
        logger.warning(
            "embedding_failed: %s (graceful)", exc.__class__.__name__
        )
        return None


async def embed_many(
    texts: list[str],
    *,
    model: str = "text-embedding-3-small",
    client: Any | None = None,
    task_type: str = TASK_TYPE_DOCUMENT,
) -> list[Optional[list[float]]]:
    """다중 텍스트 embedding (graceful — 개별 실패 시 None).

    Phase 7 MVP: 순차 호출 (batch_size=10 정책은 ADR-025 §2 명시했으나
    Phase 9+ 운영 단계에서 동적 batch 도입). 본 함수는 단순 wrapper.

    ★ task_type 기본 = RETRIEVAL_DOCUMENT (배치 임베딩 = 문서 적재/승격 경로).
    Gemini provider 일 때만 적용(taskType 비대칭) — OpenAI/client 주입 시 no-op,
    byte-identical. 검색 쿼리 임베딩은 단건 embed()(default QUERY)를 쓴다.
    """
    results: list[Optional[list[float]]] = []
    for text in texts:
        emb = await embed(text, model=model, client=client, task_type=task_type)
        results.append(emb)
    return results


__all__ = ["embed", "embed_many", "TASK_TYPE_QUERY", "TASK_TYPE_DOCUMENT"]
