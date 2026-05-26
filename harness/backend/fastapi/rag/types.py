"""RAG 모듈의 공용 Pydantic 타입.

`rag_data_contract.md §5` + `metadata_schema.md §2` 정합:
  - source_id == rag_chunks.chunk_id (uuid 문자열)
  - title    == rag_documents.title
  - snippet  == chunk content 발췌 (≤300자)
  - used_reason: LLM이 왜 이 chunk를 참고했는지 (Phase 1은 router에서 비워둘 수 있음)
  - similarity: pgvector cosine similarity (0.0~1.0)
  - metadata: rag_chunks.metadata JSONB (선택, Phase 1은 빈 dict 허용)

`schemas/output.py` Body.rag_references 필드의 타입으로 그대로 사용한다.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class RAGReference(BaseModel):
    """Planning 단계에 주입되는 1개의 RAG chunk 표현.

    Phase 1 (Slice 4):
      - 실 데이터 없음. fallback 시 [] 반환.
      - mock fixture(`mock_rag_ok`)에서 seed 2개로 동작 검증.

    Phase 2+:
      - metadata.brand_id / approach_label / format 등 추가 필터 키 활용.
    """

    source_id: str = Field(..., description="rag_chunks.chunk_id (uuid)")
    title: str = Field(..., description="rag_documents.title")
    snippet: str = Field(
        ...,
        max_length=300,
        description="chunk 본문 발췌 (≤300자, Planning prompt 주입용)",
    )
    used_reason: str | None = Field(
        default=None,
        description="LLM이 이 chunk를 참고한 사유 (Phase 1 router에서는 비워둠)",
    )
    similarity: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="pgvector cosine similarity (0.0~1.0)",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="rag_chunks.metadata JSONB",
    )


FallbackReason = Literal[
    "env_missing",
    "pgvector_unreachable",
    "query_error",
    "empty_result",
]


class RetrievalResult(BaseModel):
    """RAG 검색 1회 결과.

    - references: prompt에 주입할 후보들 (threshold 통과한 chunk들).
    - used_fallback: True 시 references는 보통 빈 배열 (Phase 1 정책).
    - fallback_reason: graceful fallback 트리거 사유 (관측 / validation.checks용).

    `routers/generate.py`는 used_fallback 값으로 validation.checks 의 status를 결정한다.
    """

    references: list[RAGReference] = Field(default_factory=list)
    used_fallback: bool = Field(default=False)
    fallback_reason: FallbackReason | None = Field(default=None)


__all__ = ["RAGReference", "RetrievalResult", "FallbackReason"]
