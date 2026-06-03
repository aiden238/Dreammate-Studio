"""Phase 5 — Supabase / PostgreSQL database layer (canonical).

graceful 정책 (Phase 1 계승):
  - 모든 실패는 graceful (raise 금지). 사용자 응답 차단 0건.
  - env 미설정 → None (Phase 5) or status="skipped_no_db" (legacy).
  - client init / insert 실패 → in-memory fallback (Phase 5) or status="failed_db_error" (legacy).

---

Phase 5 canonical (권장 — 신규 코드 사용):
  - get_supabase(): Protocol-based Supabase client factory (graceful).
  - SupabaseClientLike: Protocol type for client (or mock).
  - PlansRepo: graceful CRUD wrapper for plans table (in-memory fallback).

Legacy backward-compat (Phase 1 Slice 5, DEPRECATED Phase 5.5):
  - get_supabase_client(): Phase 1 legacy factory.
  - save_video_planning(...): Phase 1 legacy orchestrator (Intent/RAG/Planning/Critic).
  - PersistenceResult / SaveStatus: legacy 저장 결과 타입.

Removal 일정: Phase 7+ RAG 통합 후 검토 (ADR-023 참조).
legacy 사용 시 DeprecationWarning 발행:
  - supabase_client 모듈 import 시 1회.
  - save_video_planning() 호출 시 1회/호출.
"""

from __future__ import annotations

import logging
import warnings as _warnings
from typing import Any

from .client import SupabaseClientLike, get_supabase
from .repositories import (
    DEFAULT_BRAND_NAME,
    BrandMemoryRepo,
    BrandRepo,
    FeedbackRepo,
    PlansRepo,
    SelectionRepo,
    insert_plan_candidate,
    insert_video_project,
    mask_pii,
)
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
    """DEPRECATED (Phase 5.5) — Intent → RAG → Planning → Critic 결과를 Supabase에 저장.

    Phase 1 Slice 5 legacy orchestrator. Phase 5 신규 코드는 `PlansRepo.create() / .update()`
    인터페이스 사용을 권장한다 (ADR-023 참조).

    Removal 일정: Phase 7+ RAG 통합 후 검토.

    저장 단계:
      1. Supabase client 획득 (None이면 status="skipped_no_db" 즉시 반환).
      2. video_projects insert → project_id.
         실패 시 status="failed_db_error" 반환.
      3. project_id 가 있으면 plan_candidates insert → plan_candidate_id.
         (plan_candidates 실패는 부분 성공으로 간주: video_projects 만 saved)

    Phase 1 정책 (계승):
      - 모든 실패는 graceful — raise 안 함.
      - 호출자(router)는 결과를 meta.project_id 와 validation.checks 에 반영만 함.
    """
    # Phase 5.5 ADR-023 — legacy orchestrator deprecation marker.
    _warnings.warn(
        "save_video_planning is deprecated (Phase 5.5). "
        "Use PlansRepo.create() / .update() (from backend.fastapi.db import PlansRepo) instead. "
        "Scheduled removal: Phase 7+ (see ADR-023).",
        DeprecationWarning,
        stacklevel=2,
    )

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
    # Phase 5 canonical (권장)
    "get_supabase",
    "SupabaseClientLike",
    "PlansRepo",
    # Phase 9 Slice 2 — 결과 저장 + 피드백 + Brand Memory 준비 (graceful, ADR-030/031)
    "SelectionRepo",
    "FeedbackRepo",
    "mask_pii",
    "BrandMemoryRepo",
    # Phase 17 가-S3 — 기본 브랜드 get-or-create (graceful, brand_memory anchor)
    "BrandRepo",
    "DEFAULT_BRAND_NAME",
    # Legacy backward-compat (Phase 1 Slice 5, DEPRECATED Phase 5.5 — ADR-023)
    "get_supabase_client",
    "save_video_planning",
    "PersistenceResult",
    "SaveStatus",
]
