"""Phase 7 Slice 3 — pgvector retrieval (ADR-025).

cosine similarity + top-k=5 + threshold=0.7 + brand_id 격리 + dedupe.
graceful fallback (Supabase 미설정 / embedding 실패 / RPC 실패 시 빈 list + warning).

Phase 1 retriever.py (psycopg 기반)와 별개로 구현 — Phase 7부터 Supabase RPC 패턴 채택.

References:
  - docs/decisions/phase_7_rag_architecture.md (ADR-025 §3 Retrieval)
  - knowledge/rag/retrieval_policy.md
"""
from __future__ import annotations

import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)


async def search(
    query: str,
    *,
    top_k: int = 5,
    threshold: float = 0.7,
    brand_id: Optional[str] = None,
    auth_user_id: Optional[str] = None,
    embedding_client: Any | None = None,
    supabase_client: Any | None = None,
) -> list[dict[str, Any]]:
    """pgvector retrieval — query embedding + cosine similarity search.

    파이프라인 (ADR-025 §3):
      1. query → embed() (1536 dim)
      2. Supabase RPC `match_approved_knowledge` 호출 (cosine `<=>` operator 기반)
      3. brand_id / auth_user_id 격리 (retrieval 단계 강제 — ADR-025 §3 isolation)
      4. dedupe by content
      5. top_k cap

    Args:
        query: 사용자 query (자동 embed; 빈 / 공백만 → [] 반환).
        top_k: 결과 개수 (기본 5, ADR-025 §3).
        threshold: cosine similarity 최소값 (기본 0.7, ADR-025 §3).
        brand_id: brand 격리 (None 시 전체 검색).
        auth_user_id: user 격리 (None 시 anon 검색 — RLS 정책에 위임).
        embedding_client: embed() wrapper용 OpenAI client (mock 가능).
        supabase_client: Supabase client (None 시 get_supabase() 호출).

    Returns:
        retrieval 결과 list (각 dict: id + content + similarity + metadata).
        graceful: 실패 시 빈 list + warning (plan 차단 X — ADR-025 §5).

    Graceful 실패 marker (ADR-025 §5):
      - embedding 실패 → `embedding_failed`
      - Supabase 미설정 / RPC 실패 → `rag_unavailable`
    """
    if not query or not query.strip():
        return []

    # 1) Embed query
    from backend.fastapi.rag.embedding import embed

    embedding = await embed(query, client=embedding_client)
    if embedding is None:
        logger.warning(
            "rag_unavailable: query embedding failed (graceful)"
        )
        return []

    # 2) Supabase client
    if supabase_client is None:
        from backend.fastapi.db.client import get_supabase

        supabase_client = get_supabase()

    if supabase_client is None:
        logger.warning(
            "rag_unavailable: supabase unconfigured (graceful)"
        )
        return []

    # 3) pgvector RPC (Supabase RPC pattern)
    # Supabase function `match_approved_knowledge`는 Phase 7 Slice 5 또는 운영
    # 단계에서 SQL로 정의 (ADR-025 §3 — 1 - (embedding <=> $1::vector) AS similarity).
    try:
        rpc_params: dict[str, Any] = {
            "query_embedding": embedding,
            "match_threshold": threshold,
            "match_count": top_k,
        }
        if brand_id is not None:
            rpc_params["filter_brand_id"] = brand_id
        if auth_user_id is not None:
            rpc_params["filter_auth_user_id"] = auth_user_id

        resp = supabase_client.rpc(
            "match_approved_knowledge", rpc_params
        ).execute()
        if not resp or not getattr(resp, "data", None):
            return []
        results = resp.data if isinstance(resp.data, list) else []
    except Exception as exc:
        logger.warning(
            "rag_unavailable: rpc failed %s (graceful)",
            exc.__class__.__name__,
        )
        return []

    # 4) Dedupe by content (ADR-025 §3 — dedupe)
    seen_contents: set[str] = set()
    deduped: list[dict[str, Any]] = []
    for r in results:
        if not isinstance(r, dict):
            continue
        content = r.get("content", "")
        if content in seen_contents:
            continue
        seen_contents.add(content)
        deduped.append(r)

    # 5) top_k cap
    return deduped[:top_k]


__all__ = ["search"]
