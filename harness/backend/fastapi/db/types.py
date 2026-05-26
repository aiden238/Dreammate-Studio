"""DB persistence 공용 타입 (Slice 5).

Phase 1 정책:
  - 모든 저장 동작은 graceful — 실패해도 사용자 응답을 차단하지 않는다.
  - 호출자는 PersistenceResult.status 로 분기하고, 응답 meta.project_id 에
    project_id (성공) 또는 None (skip/fail) 을 노출한다.

3 가지 상태:
  - "saved":           Supabase에 video_projects (+선택적으로 plan_candidates) row 생성 성공
  - "skipped_no_db":   SUPABASE_URL / SUPABASE_ANON_KEY 미설정 (정상적인 graceful skip)
  - "failed_db_error": 클라이언트 init 실패, 네트워크 오류, insert 예외 등 (graceful 흡수)
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

SaveStatus = Literal["saved", "skipped_no_db", "failed_db_error"]


class PersistenceResult(BaseModel):
    """DB 저장 1회의 결과.

    Slice 4 RAG `RetrievalResult` 와 동일한 graceful 패턴.
    """

    status: SaveStatus
    project_id: str | None = Field(
        default=None,
        description="video_projects.id (uuid). skip/fail 시 None.",
    )
    plan_candidate_ids: list[str] = Field(
        default_factory=list,
        description="plan_candidates.id 목록 (Phase 1은 보통 1개).",
    )
    error_reason: str | None = Field(
        default=None,
        description="failed_db_error 발생 시 사유 코드 또는 메시지 요약.",
    )


__all__ = ["PersistenceResult", "SaveStatus"]
