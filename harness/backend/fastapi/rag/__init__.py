"""RAG 모듈 — Phase 1 Slice 4 (RAG Lite + graceful fallback) + Phase 7 5단계 core.

Phase 1 baseline (preserved):
  - pgvector 미가용 시 router 가 200 응답 + 빈 references 로 계속 진행 (graceful).
  - 참조: rag_data_contract.md §5.4, retrieval_policy.md §7.2.

Phase 7 Slice 2 신규 (5단계 RAG Lite — ADR-024/025/026):
  - promotion: 5단계 transition logic + promotion_history append-only
  - quality_filter: PII + 인젝션 + 광고적 표현 차단
  - eval_rubric: 간이 3 dim (relevance + clarity + safety) — Phase 9+ deprecated 예정

Phase 9 Slice 4 신규 (Brand Memory 준비 — ADR-031):
  - feedback_to_candidate: feedback/selection → candidate_knowledge(pending) 적재 경로.
    자동 승격 X (NG12) — Phase 7 promotion 본체 import/호출 0. P-AUX-2 agent 미구현 (NG1).
"""

from .eval_rubric import EvalScores, evaluate, overall
from .fallback import fallback
from .feedback_to_candidate import (
    PENDING_STATUS,
    SOURCE_KIND_CHOICE,
    SOURCE_KIND_FEEDBACK,
    build_candidate_from_feedback,
    enqueue_feedback_candidate,
)
from .promotion import (
    AUTO_APPROVE_THRESHOLD,
    EVAL_PASS_THRESHOLD,
    KnowledgeStage,
    promotion_history_entry,
    transition,
)
from .quality_filter import QualityFilterResult, quality_filter
from .retriever import run_rag_retrieval
from .types import FallbackReason, RAGReference, RetrievalResult

__all__ = [
    # Phase 1 baseline (preserved)
    "run_rag_retrieval",
    "fallback",
    "RAGReference",
    "RetrievalResult",
    "FallbackReason",
    # Phase 7 Slice 2 신규
    "transition",
    "promotion_history_entry",
    "KnowledgeStage",
    "AUTO_APPROVE_THRESHOLD",
    "EVAL_PASS_THRESHOLD",
    "quality_filter",
    "QualityFilterResult",
    "evaluate",
    "overall",
    "EvalScores",
    # Phase 9 Slice 4 신규 (Brand Memory 준비 — ADR-031)
    "build_candidate_from_feedback",
    "enqueue_feedback_candidate",
    "SOURCE_KIND_FEEDBACK",
    "SOURCE_KIND_CHOICE",
    "PENDING_STATUS",
]
