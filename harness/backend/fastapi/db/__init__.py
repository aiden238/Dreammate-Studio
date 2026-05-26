"""DB persistence 모듈 — Phase 1 Slice 5.

Public API:
  - get_supabase_client(): Supabase Client or None (graceful)
  - save_video_planning(...): orchestrator — Intent/RAG/Planning/Critic 결과 저장
  - PersistenceResult / SaveStatus: 저장 결과 타입

Phase 1 정책:
  - 모든 실패는 graceful (raise 금지). 사용자 응답 차단 0건.
  - env 미설정 → status="skipped_no_db"
  - client init / insert 실패 → status="failed_db_error"
  - 성공 → status="saved" + project_id, plan_candidate_ids 채움
"""

from __future__ import annotations

import logging
from typing import Any

from .repositories import insert_plan_candidate, insert_video_project
from .supabase_client import get_supabase_client
from .types import PersistenceResult, SaveStatus

logger = logging.getLogger(__name__)


def save_video_planning(
    *,
    request_id: str,
    input_text: str,
    locale: str,
    plan_dict: dict[str, Any],
    critic_dict: dict[str, Any] | None,
    rag_refs: list[dict[str, Any]],
) -> PersistenceResult:
    """Intent → RAG → Planning → Critic 결과를 Supabase에 저장.

    저장 단계:
      1. Supabase client 획득 (None이면 status="skipped_no_db" 즉시 반환).
      2. video_projects insert → project_id.
         실패 시 status="failed_db_error" 반환.
      3. project_id 가 있으면 plan_candidates insert → plan_candidate_id.
         (plan_candidates 실패는 부분 성공으로 간주: video_projects 만 saved)

    Phase 1 정책:
      - 모든 실패는 graceful — raise 안 함.
      - 호출자(router)는 결과를 meta.project_id 와 validation.checks 에 반영만 함.
    """
    client = get_supabase_client()

    if client is None:
        # env 미설정 또는 패키지 미설치 — 정상적인 graceful skip
        logger.info("DB 저장 skip — Supabase env 미설정 또는 클라이언트 init 실패")
        return PersistenceResult(
            status="skipped_no_db",
            project_id=None,
            plan_candidate_ids=[],
            error_reason=None,
        )

    # 1. video_projects insert
    project_id = insert_video_project(
        client,
        request_id=request_id,
        input_text=input_text,
        locale=locale,
    )
    if project_id is None:
        # video_projects 저장 실패 — 전체 fail (FK 무결성 때문에 plan_candidates 도 skip)
        return PersistenceResult(
            status="failed_db_error",
            project_id=None,
            plan_candidate_ids=[],
            error_reason="video_projects_insert_failed",
        )

    # 2. plan_candidates insert (Phase 1은 1개)
    plan_candidate_id = insert_plan_candidate(
        client,
        project_id=project_id,
        plan=plan_dict,
        critic=critic_dict,
        rag_refs=rag_refs,
    )

    if plan_candidate_id is None:
        # 부분 성공 — video_projects 는 저장됨, plan_candidates 실패.
        # Phase 1 정책: 사용자에게는 project_id 노출 (관측은 status=warn으로).
        logger.warning(
            "plan_candidates insert 실패 (video_projects 만 저장됨): project_id=%s",
            project_id,
        )
        return PersistenceResult(
            status="failed_db_error",
            project_id=project_id,
            plan_candidate_ids=[],
            error_reason="plan_candidates_insert_failed",
        )

    return PersistenceResult(
        status="saved",
        project_id=project_id,
        plan_candidate_ids=[plan_candidate_id],
        error_reason=None,
    )


__all__ = [
    "get_supabase_client",
    "save_video_planning",
    "PersistenceResult",
    "SaveStatus",
]
