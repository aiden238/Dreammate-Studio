"""RAG fallback 경로 — pgvector 미가용 또는 검색 실패 시 graceful degradation.

`rag_data_contract.md §5.4` + `retrieval_policy.md §7.2` 정합:
  - DB / pgvector 실패 시 Planning을 `rag_context=[]` 로 계속 진행 (graceful)
  - 사용자 요청 절대 차단 금지 (Phase 1 정책 — Slice 4 acceptance)

Phase 1 정책:
  - hardcoded seed 사용 안 함 (knowledge base 부재 — Slice 4 spec).
  - references=[] + used_fallback=True + fallback_reason 만 노출.
"""

from __future__ import annotations

import logging

from .types import FallbackReason, RAGReference, RetrievalResult

logger = logging.getLogger(__name__)


def fallback(reason: FallbackReason = "pgvector_unreachable") -> RetrievalResult:
    """빈 references + 사유를 담은 RetrievalResult 반환.

    Args:
        reason: graceful fallback 트리거 사유 (관측용).

    Returns:
        RetrievalResult(references=[], used_fallback=True, fallback_reason=reason)
    """
    logger.info("RAG fallback engaged reason=%s", reason)
    return RetrievalResult(
        references=[],
        used_fallback=True,
        fallback_reason=reason,
    )


__all__ = ["fallback", "RAGReference", "RetrievalResult"]
