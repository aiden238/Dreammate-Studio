"""RAG 모듈 — Phase 1 Slice 4 (RAG Lite + graceful fallback).

pgvector 미가용 시 router 가 200 응답 + 빈 references 로 계속 진행하도록
모든 실패를 흡수한다 (`rag_data_contract.md §5.4`, `retrieval_policy.md §7.2`).
"""

from .fallback import fallback
from .retriever import run_rag_retrieval
from .types import FallbackReason, RAGReference, RetrievalResult

__all__ = [
    "run_rag_retrieval",
    "fallback",
    "RAGReference",
    "RetrievalResult",
    "FallbackReason",
]
