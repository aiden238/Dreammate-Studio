"""Phase 7 Slice 4 — agents/rag.py (RAG Lite 통합).

Phase 1 baseline (preserved):
  - `rag/retriever.py` + `rag/fallback.py` 기반 graceful retrieval — `routers/plans.py` 직접 호출.
  - 본 모듈은 Phase 7 RAG Lite 통합 wrapper (Phase 1 retriever와 별개로 공존).

Phase 7 Slice 4 신규 (ADR-025 RAG > LLM Wiki 우선순위):
  - `run_rag()` async wrapper: rag.retrieval.search() + rag.llm_wiki.lookup() 통합
  - graceful 5종 marker (rag_unavailable / rag_no_results / llm_wiki_unavailable /
    embedding_failed / supabase_unconfigured) — ADR-025 §5
  - RAG 실패 시 plan 생성 차단 X (P-GRACEFUL-001 계승)

References:
  - docs/decisions/phase_7_rag_architecture.md (ADR-025 §4 LLM Wiki vs RAG + §5 graceful)
  - docs/decisions/phase_7_promotion_logic.md (ADR-026)
"""
from __future__ import annotations

import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)


async def run_rag(
    user_input: str,
    *,
    brand_id: Optional[str] = None,
    auth_user_id: Optional[str] = None,
    embedding_client: Any | None = None,
    supabase_client: Any | None = None,
) -> dict[str, Any]:
    """RAG 검색 — Phase 7 Lite 통합 (ADR-025 §4).

    우선순위 정책: **RAG > LLM Wiki** (ADR-025 §4 결정)
      - priority 1: approved_knowledge (동적, retrieval.search)
      - priority 2: LLM Wiki (정적, llm_wiki.search_by_tags) — 보조

    Args:
        user_input: 사용자 query
        brand_id: brand 격리 (ADR-025 §3 retrieval isolation)
        auth_user_id: user 격리 (RLS)
        embedding_client: OpenAI embedding client (mock 가능)
        supabase_client: Supabase client (mock 가능)

    Returns:
        dict:
          - references: list[dict] — RAG (approved_knowledge) + LLM Wiki 결과
          - rag_used_fallback: bool — graceful 마커 발생 여부 (RAG 실패 또는 0 results)
          - rag_warnings: list[str] — graceful 마커 list (ADR-025 §5 표준)

    Graceful 정책 (ADR-025 §5):
      - plan 생성 차단 X — 모든 실패는 warnings에 marker 추가하고 진행
      - RAG 결과 0 → LLM Wiki fallback (보조 context)
    """
    references: list[dict[str, Any]] = []
    warnings: list[str] = []
    rag_used_fallback = False

    if not user_input or not user_input.strip():
        # 빈 입력 — 양쪽 모두 skip + warning
        warnings.append("rag_no_results")
        return {
            "references": references,
            "rag_used_fallback": True,
            "rag_warnings": warnings,
        }

    # 1) RAG (approved_knowledge) — priority 1 (ADR-025 §4)
    try:
        from backend.fastapi.rag.retrieval import search as rag_search

        rag_results = await rag_search(
            user_input,
            brand_id=brand_id,
            auth_user_id=auth_user_id,
            embedding_client=embedding_client,
            supabase_client=supabase_client,
        )
        if rag_results:
            for r in rag_results:
                references.append({
                    "source": "rag",
                    "content": r.get("content", ""),
                    "similarity": r.get("similarity"),
                    "metadata": r.get("metadata", {}),
                })
        else:
            rag_used_fallback = True
            warnings.append("rag_no_results")
    except Exception as exc:
        rag_used_fallback = True
        warnings.append(f"rag_unavailable: {exc.__class__.__name__}")
        logger.warning(
            "rag_unavailable: %s (graceful)", exc.__class__.__name__
        )

    # 2) LLM Wiki — priority 2 (보조, ADR-025 §4)
    try:
        from backend.fastapi.rag.llm_wiki import search_by_tags

        # 간이 keyword → tags 매핑 (영상기획 도메인 기본 5개)
        wiki_results = search_by_tags(
            ["hook", "target", "tone", "structure", "cta"]
        )
        # 최대 2개 보조 (RAG context 과부담 방지 — ADR-025 §3 top_k=5 정합)
        for w in wiki_results[:2]:
            references.append({
                "source": "llm_wiki",
                "topic": w.get("topic"),
                "content": w.get("content", ""),
                "tags": w.get("tags", []),
            })
    except Exception as exc:
        warnings.append(f"llm_wiki_unavailable: {exc.__class__.__name__}")
        logger.warning(
            "llm_wiki_unavailable: %s (graceful)", exc.__class__.__name__
        )

    return {
        "references": references,
        "rag_used_fallback": rag_used_fallback,
        "rag_warnings": warnings,
    }


__all__ = ["run_rag"]
