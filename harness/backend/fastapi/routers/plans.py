"""Phase 4 plans router — 4 contract endpoints.

api_contract.md §8 정합. Phase 1 endpoint `/api/v1/generate`와 공존.
ADR-014 (phase_4_endpoint_migration.md) 채택: Phase 8+ 제거 정책.

Slice 1 (이번): skeleton — 4 endpoints baseline + in-memory plan_store.
Slice 2: POST /plans/{id}/generate 본격 구현 (Intent → RAG → 3-plan parallel → Critic → DB → Envelope).
Slice 3: frontend 연동 (`/plan/[plan_id]` 페이지 3-plan 표시).
Phase 5+: Supabase 본격 — in-memory store → DB, SSE Progress, Auth/RLS.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from ..schemas.output import ErrorBody, ErrorEnvelope, ErrorMeta
from ..schemas.plans import (
    GenerateRequest,
    PlanResource,
    PlanStartRequest,
    PlanStartResponse,
    WizardStepRequest,
    WizardStepResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["plans"])


# ─── Phase 4 in-memory plan store ─────────────────────────────────────
# Phase 5 Auth/DB 도입 전까지 단일 프로세스 in-memory 저장.
# 재시작 시 휘발됨. Phase 5에서 Supabase video_projects + wizard_states로 교체.
_plan_store: dict[str, dict[str, Any]] = {}


def _now_iso() -> str:
    """ISO8601 UTC ("...Z" 형식)."""
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _not_found_response(plan_id: str) -> JSONResponse:
    """plan_id 미발견 시 ErrorEnvelope (INV-006 — 4계층 참조 무결성)."""
    envelope = ErrorEnvelope(
        error=ErrorBody(
            code="INV-006",
            message=f"plan_id not found: {plan_id}",
            user_message="이전에 만든 데이터를 못 찾았어요. 페이지를 새로고침해주세요.",
            retry_allowed=False,
        ),
        meta=ErrorMeta.make(),
    )
    return JSONResponse(status_code=404, content=envelope.model_dump(mode="json"))


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


# ─── POST /plans/{plan_id}/generate ───────────────────────────────────

@router.post(
    "/plans/{plan_id}/generate",
    responses={
        202: {"description": "Accepted — Phase 4 Slice 1 skeleton (Slice 2에서 본격)"},
        404: {"model": ErrorEnvelope, "description": "plan_id 미발견 (INV-006)"},
    },
    summary="3-plan generation — Phase 4 Slice 1 skeleton",
    description=(
        "Phase 4 Slice 1은 skeleton (202 Accepted). "
        "Slice 2에서 본격 — Intent → RAG → 3-plan parallel (multi-model 가능) → "
        "Critic 8-dim verdict → DB 저장 → Envelope 응답."
    ),
)
def plans_generate(plan_id: str, req: GenerateRequest) -> JSONResponse:
    plan = _plan_store.get(plan_id)
    if not plan:
        return _not_found_response(plan_id)

    plan["status"] = "generated"
    plan["updated_at"] = _now_iso()
    logger.info(
        "plans/generate skeleton accepted plan_id=%s use_rag=%s use_critic=%s",
        plan_id, req.use_rag, req.use_critic,
    )
    return JSONResponse(
        status_code=202,
        content={
            "ok": True,
            "data": {
                "plan_id": plan_id,
                "status": "accepted",
                "message": (
                    "Phase 4 Slice 1 skeleton — Slice 2에서 본격 3-plan generation 구현. "
                    "GET /api/v1/plans/{plan_id}로 결과 폴링 (Slice 2 후 envelope 채워짐)."
                ),
            },
        },
    )


# ─── GET /plans/{plan_id} ─────────────────────────────────────────────

@router.get(
    "/plans/{plan_id}",
    response_model=PlanResource,
    responses={404: {"model": ErrorEnvelope, "description": "plan_id 미발견 (INV-006)"}},
    summary="plan 상태 + envelope 조회",
    description=(
        "Slice 1: status + 메타데이터만 반환 (envelope=null). "
        "Slice 2 generate 완료 후 envelope 필드에 3-plan Envelope (Phase 1 호환 구조) 채워짐."
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
