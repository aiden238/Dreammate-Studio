"""Phase 4 plans router — 4 contract endpoints.

api_contract.md §8 정합. Phase 1 endpoint `/api/v1/generate`와 공존.
ADR-014 (phase_4_endpoint_migration.md) 채택: Phase 8+ 제거 정책.

Slice 1: skeleton — 4 endpoints baseline + in-memory plan_store.
Slice 2 (이번): POST /plans/{id}/generate 본격 — Intent → RAG → 3-plan parallel
                 (multi-model 인터페이스) → Critic 1회 평가 → DB save → Envelope.
  - 사용자 결정 4-b: 3 parallel async + 모델 추가 가능 구조 (ADR-015).
  - Critic revise loop / Rewriter / SSE는 Phase 4.5+ deferred (GPT 검토 채택).
Slice 3: frontend 연동 (`/plan/[plan_id]` 페이지 3-plan 표시).
Phase 5+: Supabase 본격 — in-memory store → DB, SSE Progress, Auth/RLS.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse

from ..agents.critic import (
    PROMPT_ID as CRITIC_PROMPT_ID,
    PROMPT_VERSION as CRITIC_PROMPT_VERSION,
    run_critic,
    select_best_plan_index,
)
from ..agents.intent import (
    PROMPT_ID as INTENT_PROMPT_ID,
    PROMPT_VERSION as INTENT_PROMPT_VERSION,
    run_intent,
)
from ..agents.planning import (
    PARALLEL_3_PROMPT_ID,
    PARALLEL_3_PROMPT_VERSION,
    run_planning_parallel_3,
)
from ..agents.rewriter import run_rewriter
from ..config import get_settings
from ..db import (
    FeedbackRepo,
    PlansRepo,
    SelectionRepo,
    get_supabase,
    save_video_planning,
)
from ..orchestration import (
    StoreProgressSink,
    error_envelope_response,
    generate_plan,
    not_found_response,
    now_iso,
)
from ..rag import RetrievalResult, run_rag_retrieval
from ..schemas.output import (
    Body,
    CriticEvaluation,
    Envelope,
    ErrorBody,
    ErrorEnvelope,
    ErrorMeta,
    Meta,
    Plan,
    PlanFlowBeat,
    Validation,
    ValidationCheck,
    compute_validation_warnings_phase4,
)
from ..schemas.plans import (
    FeedbackListResponse,
    FeedbackRequest,
    FeedbackResponse,
    GenerateRequest,
    PlanResource,
    PlanStartRequest,
    PlanStartResponse,
    SelectPlanRequest,
    SelectPlanResponse,
    WizardStepRequest,
    WizardStepResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["plans"])


# ─── Phase 4 in-memory plan store ─────────────────────────────────────
# Phase 4: 단일 프로세스 in-memory 저장 (재시작 시 휘발).
# Phase 5 Slice 2: PlansRepo (graceful — Supabase 사용 가능 시 영속화, 아니면 in-memory).
#   - 본 _plan_store 는 그대로 유지 (graceful fallback 저장소 역할 + 회귀 0 보장).
#   - _plans_repo 는 PlansRepo wrapper. Slice 3 Auth 활성 후 본격 사용.
#     현 Slice 2 baseline: _plan_store 직접 사용 = PlansRepo(supabase=None, store=_plan_store) 와 동일 동작.
_plan_store: dict[str, dict[str, Any]] = {}
_plans_repo: PlansRepo = PlansRepo(
    supabase_client=get_supabase(),   # None if SUPABASE_URL/ANON_KEY 미설정 (graceful)
    in_memory_store=_plan_store,      # graceful fallback 저장소
)

# Phase 9 Slice 3 (ADR-030): selection / feedback 영속화 (graceful, PlansRepo 패턴).
#   - _plan_store 와 별도 in-memory 저장소 (selected_plans 1:1 / feedback_events 1:N).
#   - Supabase 사용 가능 시 PostgreSQL, 아니면 in-memory fallback (회귀 0).
_selection_repo: SelectionRepo = SelectionRepo(
    supabase_client=get_supabase(),
    in_memory_store={},
)
_feedback_repo: FeedbackRepo = FeedbackRepo(
    supabase_client=get_supabase(),
    in_memory_store={},
)


# ─── helper re-export (backward-compat 별칭) ──────────────────────────
# Phase 8 Slice 2 (ADR-027 §3): _now_iso / _not_found_response /
# _error_envelope_response 를 orchestration/responses.py 로 이동 (public).
# plans_start / wizard / get 가 기존 private 이름을 참조하므로 별칭 유지 →
# 동작·출력 100% 보존 (behavior-preserving).
_now_iso = now_iso
_not_found_response = not_found_response
_error_envelope_response = error_envelope_response


# ─── POST /plans/start ────────────────────────────────────────────────

@router.post(
    "/plans/start",
    response_model=PlanStartResponse,
    status_code=201,
    summary="신규 plan_id 발급 (Phase 4 Slice 1)",
    description=(
        "Phase 4 contract endpoint (api_contract.md §8). "
        "신규 plan_id를 발급하고 in-memory plan_store에 등록한다. "
        "Phase 5 Auth 도입 시 user_id 연결 + Supabase 저장으로 교체."
    ),
)
def plans_start(req: PlanStartRequest) -> PlanStartResponse:
    plan_id = str(uuid4())
    now = _now_iso()
    _plan_store[plan_id] = {
        "plan_id": plan_id,
        "status": "created",
        "created_at": now,
        "updated_at": now,
        "locale": req.locale,
        "initial_input": req.user_input,
        "wizard_data": {},
        "envelope": None,
    }
    logger.info("plans/start created plan_id=%s locale=%s", plan_id, req.locale)
    return PlanStartResponse(plan_id=plan_id, created_at=now, locale=req.locale)


# ─── POST /plans/{plan_id}/wizard/{step} ──────────────────────────────

@router.post(
    "/plans/{plan_id}/wizard/{step}",
    response_model=WizardStepResponse,
    responses={404: {"model": ErrorEnvelope, "description": "plan_id 미발견 (INV-006)"}},
    summary="wizard step 진행 — Phase 4 skeleton",
    description=(
        "Discovery 7-step (step1~step7) 또는 Quick 4-step (quick.initial/clarify/direction/generate) 진행. "
        "Phase 4 Slice 1은 skeleton — 200 + 입력 저장 + next_step hint만. "
        "실제 step 처리 (LLM 호출, 분기 로직)는 Phase 5+ Auth/DB 본격화 이후."
    ),
)
def plans_wizard_step(plan_id: str, step: str, req: WizardStepRequest):
    plan = _plan_store.get(plan_id)
    if not plan:
        return _not_found_response(plan_id)

    plan["wizard_data"][step] = req.model_dump()
    plan["status"] = "wizard_in_progress"
    plan["updated_at"] = _now_iso()

    # next_step hint — Discovery 7-step + Quick 4-step
    next_step: str | None = None
    if step.startswith("step") and step[4:].isdigit():
        n = int(step[4:])
        if n < 7:
            next_step = f"step{n + 1}"
        elif n == 7:
            next_step = "generate"
    elif step == "quick.initial":
        next_step = "quick.clarify"
    elif step == "quick.clarify":
        next_step = "quick.direction"
    elif step == "quick.direction":
        next_step = "generate"

    logger.info(
        "plans/wizard step accepted plan_id=%s step=%s next_step=%s",
        plan_id, step, next_step,
    )
    return WizardStepResponse(
        plan_id=plan_id,
        step=step,
        accepted=True,
        next_step=next_step,
    )


# ─── POST /plans/{plan_id}/generate — Slice 2 본격 ────────────────────

@router.post(
    "/plans/{plan_id}/generate",
    responses={
        200: {"model": Envelope, "description": "3-plan Envelope (Phase 4 Slice 2)"},
        404: {"model": ErrorEnvelope, "description": "plan_id 미발견 (INV-006)"},
        422: {"model": ErrorEnvelope, "description": "Intent 차단 (INV-001) 등"},
        502: {"model": ErrorEnvelope, "description": "LLM 호출 실패 (E-LLM-*)"},
    },
    summary="3-plan generation — Phase 4 Slice 2 본격",
    description=(
        "Phase 4 Slice 2: Intent → RAG → 3-plan parallel (multi-model 인터페이스) → "
        "Critic 1회 평가 → DB save → Envelope 200 응답. "
        "사용자 결정 4-b: 3 parallel async (asyncio.gather) + 향후 모델 추가 가능 구조 (ADR-015). "
        "Critic revise loop / Rewriter / SSE는 Phase 4.5+ deferred."
    ),
)
async def plans_generate(plan_id: str, req: GenerateRequest):
    """Phase 8 Slice 2 (ADR-027): thin adapter — orchestration/moa_orchestrator 위임.

    plans_generate() god-function 본문은 behavior-preserving 으로
    orchestration/moa_orchestrator.py::generate_plan() 으로 이관됨.
    router 는 HTTP 경계(plan_id 조회 + 404) 만 담당하고 orchestration 은 위임한다
    (moa_policy §2 "오케스트레이터가 항상 중개").
    """
    plan_entry = _plan_store.get(plan_id)
    if not plan_entry:
        return not_found_response(plan_id)
    # Phase 8 Slice 3 (ADR-028): StoreProgressSink 주입 → generate stage 진행을
    # progress_store 에 기록 (sse.py 가 read). Slice 2 default(NullProgressSink) 대비
    # 부수효과(store 기록)만 추가 — Envelope/응답 동일 (회귀 0).
    return await generate_plan(
        plan_id, plan_entry, req, progress=StoreProgressSink(plan_id),
    )


# ─── GET /plans/{plan_id} ─────────────────────────────────────────────

@router.get(
    "/plans/{plan_id}",
    response_model=PlanResource,
    responses={404: {"model": ErrorEnvelope, "description": "plan_id 미발견 (INV-006)"}},
    summary="plan 상태 + envelope 조회",
    description=(
        "Slice 1: status + 메타데이터만 반환 (envelope=null). "
        "Slice 2 generate 완료 후 envelope 필드에 3-plan Envelope 채워짐."
    ),
)
def plans_get(plan_id: str):
    plan = _plan_store.get(plan_id)
    if not plan:
        return _not_found_response(plan_id)

    return PlanResource(
        plan_id=plan_id,
        status=plan["status"],
        created_at=plan["created_at"],
        updated_at=plan["updated_at"],
        envelope=plan.get("envelope"),
    )


# ─── Phase 9 Slice 3 — Select / Feedback (ADR-030) ────────────────────
# thin adapter: plan_entry 존재 확인(404) → repo 위임 → response.
# auth_user_id 는 request.state.user (Phase 5 auth_middleware) 에서 추출 (없으면 None graceful).


def _auth_user_id(request: Request) -> str | None:
    """request.state.user (auth_middleware 주입) 에서 user_id 추출. anon 시 None."""
    user = getattr(request.state, "user", None)
    if isinstance(user, dict):
        uid = user.get("user_id")
        return str(uid) if uid else None
    return None


@router.post(
    "/plans/{plan_id}/select",
    response_model=SelectPlanResponse,
    responses={404: {"model": ErrorEnvelope, "description": "plan_id 미발견 (INV-006)"}},
    summary="plan 선택 저장 (Phase 9 Slice 3)",
    description=(
        "3-plan 중 하나를 선택 저장한다 (selected_option_index 0–2 = plan_candidates 배열 인덱스). "
        "SelectionRepo 위임 (graceful — Supabase 또는 in-memory). plan_store status 를 plan_selected 로 갱신."
    ),
)
async def plans_select(plan_id: str, req: SelectPlanRequest, request: Request):
    plan_entry = _plan_store.get(plan_id)
    if not plan_entry:
        return not_found_response(plan_id)

    row = await _selection_repo.select(
        plan_id,
        req.selected_option_index,
        auth_user_id=_auth_user_id(request),
        selection_reason=req.selection_reason,
    )

    now = now_iso()
    # plan_store status 갱신 (PlanResource.status enum: "selected" 정합).
    plan_entry["status"] = "selected"
    plan_entry["updated_at"] = now

    logger.info(
        "plans/select plan_id=%s option_index=%d",
        plan_id, req.selected_option_index,
    )
    return SelectPlanResponse(
        plan_id=plan_id,
        selected_option_index=int(row.get("selected_option_index", req.selected_option_index)),
        selection_reason=row.get("selection_reason"),
        selected_at=str(row.get("created_at") or now),
    )


@router.post(
    "/plans/{plan_id}/feedback",
    response_model=FeedbackResponse,
    responses={404: {"model": ErrorEnvelope, "description": "plan_id 미발견 (INV-006)"}},
    summary="피드백 저장 (Phase 9 Slice 3)",
    description=(
        "like / dislike / reject / regenerate 피드백을 저장한다. "
        "reason 자유 입력은 FeedbackRepo 가 저장 전 PII 마스킹 (security-review T1). "
        "FeedbackRepo 위임 (graceful — Supabase 또는 in-memory)."
    ),
)
async def plans_feedback(plan_id: str, req: FeedbackRequest, request: Request):
    plan_entry = _plan_store.get(plan_id)
    if not plan_entry:
        return not_found_response(plan_id)

    row = await _feedback_repo.record(
        plan_id,
        req.event_type,
        option_index=req.option_index,
        reason=req.reason,  # repo 가 PII 마스킹
        auth_user_id=_auth_user_id(request),
    )

    now = now_iso()
    logger.info(
        "plans/feedback plan_id=%s event_type=%s option_index=%s",
        plan_id, req.event_type, req.option_index,
    )
    return FeedbackResponse(
        plan_id=plan_id,
        event_type=str(row.get("event_type", req.event_type)),
        option_index=row.get("option_index"),
        recorded_at=str(row.get("created_at") or now),
    )


@router.get(
    "/plans/{plan_id}/feedback",
    response_model=FeedbackListResponse,
    responses={404: {"model": ErrorEnvelope, "description": "plan_id 미발견 (INV-006)"}},
    summary="피드백 목록 조회 (Phase 9 Slice 3)",
    description="해당 plan 의 피드백 events 목록을 반환한다 (FeedbackRepo 위임, graceful).",
)
async def plans_feedback_list(plan_id: str):
    plan_entry = _plan_store.get(plan_id)
    if not plan_entry:
        return not_found_response(plan_id)

    events = await _feedback_repo.list_for_plan(plan_id)
    return FeedbackListResponse(plan_id=plan_id, events=events)
