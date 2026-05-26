"""POST /api/v1/generate — Phase 1 Slice 3.

Phase 1 deviation from api_contract.md §8.3:
  - Contract: POST /api/v1/plans/{plan_id}/generate (async + SSE, 3 plans)
  - Slice 1/2/3: POST /api/v1/generate (sync, 1 plan)
  - Reason: Simplest Slice 원칙 (phase-start v1.1.0 §6.2)
  - Migration: Phase 4 MOA Lite 완성 시 contract endpoint로 정합

Slice 2 변경:
  - Intent + Planning 분리 (직렬 2회 호출)
  - INV-001 (Intent 차단) → ErrorEnvelope 정식 응답 (HTTP 422)

Slice 3 변경:
  - Critic 추가 (직렬 3회 호출: Intent → Planning → Critic)
  - body.critic_evaluation 활성화 (revise 없음, 평가만)
  - validation.warnings에서 "phase_1_no_critic" 제거
"""

from __future__ import annotations

import logging
from typing import Union
from uuid import uuid4

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from ..agents.critic import (
    PROMPT_ID as CRITIC_PROMPT_ID,
    PROMPT_VERSION as CRITIC_PROMPT_VERSION,
    run_critic,
)
from ..agents.intent import (
    PROMPT_ID as INTENT_PROMPT_ID,
    PROMPT_VERSION as INTENT_PROMPT_VERSION,
    run_intent,
)
from ..agents.planning import (
    PROMPT_ID as PLANNING_PROMPT_ID,
    PROMPT_VERSION as PLANNING_PROMPT_VERSION,
    run_planning,
)
from ..config import get_settings
from ..schemas.input import GenerateRequest
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
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["generate"])


# ─── Helpers ─────────────────────────────────────────────────────────

def _error_response(
    *,
    status_code: int,
    code: str,
    message: str,
    user_message: str,
    retry_allowed: bool = False,
) -> JSONResponse:
    """ErrorEnvelope를 JSONResponse로 변환 (error_response_contract.md §1)."""
    envelope = ErrorEnvelope(
        error=ErrorBody(
            code=code,
            message=message,
            user_message=user_message,
            retry_allowed=retry_allowed,
        ),
        meta=ErrorMeta.make(),
    )
    return JSONResponse(
        status_code=status_code,
        content=envelope.model_dump(mode="json"),
    )


# ─── Endpoint ─────────────────────────────────────────────────────────

@router.post(
    "/generate",
    response_model=Envelope,
    responses={
        422: {"model": ErrorEnvelope, "description": "Intent 차단 (INV-001) 등"},
        502: {"model": ErrorEnvelope, "description": "LLM 호출 실패"},
    },
    status_code=status.HTTP_200_OK,
    summary="영상기획 1개 생성 + Critic 평가 (Phase 1 Slice 3)",
    description=(
        "Phase 1 Slice 3 — Intent + Planning + Critic 직렬 호출.\n"
        "Critic은 8 차원 평가만 수행 (revise 없음, Phase 4+).\n"
        "Phase 4에서 api_contract.md §8.3 (async + SSE) 형식으로 migration 예정.\n"
        "Intent 차단 시 INV-001 ErrorEnvelope 반환."
    ),
)
def generate(req: GenerateRequest) -> Union[Envelope, JSONResponse]:
    """Intent → Planning → Critic 직렬 호출 → output_schema v1.0 envelope 반환."""
    settings = get_settings()

    # ── 1. Intent Agent (P-001) ──────────────────────────────────────
    try:
        intent_result = run_intent(req.input)
    except ValueError as e:
        logger.warning("Intent LLM JSON 파싱 실패: %s", e)
        return _error_response(
            status_code=status.HTTP_502_BAD_GATEWAY,
            code="E-LLM-002",
            message=f"Intent LLM response parse failed: {e}",
            user_message="AI 응답을 정리하는 중 문제가 생겼어요. 다시 시도해주세요.",
            retry_allowed=True,
        )
    except Exception as e:
        logger.exception("Intent LLM 호출 실패")
        return _error_response(
            status_code=status.HTTP_502_BAD_GATEWAY,
            code="E-LLM-001",
            message=f"Intent LLM call failed: {e}",
            user_message="AI 응답이 늦어져서 멈췄어요. 다시 시도해주세요.",
            retry_allowed=True,
        )

    # ── 2. Intent 차단 → INV-001 ErrorEnvelope ──────────────────────
    if not intent_result.get("intent_ok", False):
        reason = intent_result.get("reason", "영상기획 외 요청")
        logger.info("Intent 차단: %s", reason)
        return _error_response(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            code="INV-001",
            message=f"Intent blocked: {reason}",
            user_message="영상기획과 거리가 있는 내용 같아요. 다른 방식으로 도와드릴까요?",
            retry_allowed=False,
        )

    # ── 3. Planning Agent (P-006) ────────────────────────────────────
    try:
        planning_result = run_planning(req.input)
    except ValueError as e:
        logger.warning("Planning LLM JSON 파싱 실패: %s", e)
        return _error_response(
            status_code=status.HTTP_502_BAD_GATEWAY,
            code="E-LLM-002",
            message=f"Planning LLM response parse failed: {e}",
            user_message="AI 응답을 정리하는 중 문제가 생겼어요. 다시 시도해주세요.",
            retry_allowed=True,
        )
    except Exception as e:
        logger.exception("Planning LLM 호출 실패")
        return _error_response(
            status_code=status.HTTP_502_BAD_GATEWAY,
            code="E-LLM-001",
            message=f"Planning LLM call failed: {e}",
            user_message="AI 응답이 늦어져서 멈췄어요. 다시 시도해주세요.",
            retry_allowed=True,
        )

    # ── 4. plan dict → Pydantic Plan 모델 ─────────────────────────────
    plan_raw = planning_result.get("plan") or {}
    try:
        plan = Plan(
            plan_id=str(uuid4()),
            option_index=0,
            name=plan_raw.get("name", "(이름 없음)"),
            concept=plan_raw.get("concept", "(콘셉트 없음)"),
            hook=plan_raw.get("hook", "후크 미생성"),
            flow=[
                PlanFlowBeat(
                    beat_index=b.get("beat_index", i),
                    beat=b.get("beat", ""),
                    duration_sec=int(b.get("duration_sec", 5)),
                    purpose=b.get("purpose", ""),
                )
                for i, b in enumerate(plan_raw.get("flow", []))
            ],
            pros=plan_raw.get("pros", ""),
            risks=plan_raw.get("risks", ""),
            approach_label=plan_raw.get("approach_label", "informational"),
            rag_used=[],  # Slice 4에서 채움
        )
    except Exception as e:
        logger.exception("Plan 모델 검증 실패")
        return _error_response(
            status_code=status.HTTP_502_BAD_GATEWAY,
            code="E-LLM-003",
            message=f"Plan schema validation failed: {e}",
            user_message="AI가 형식에 맞지 않게 답했어요. 다시 시도해주세요.",
            retry_allowed=True,
        )

    # ── 5. Critic Agent (P-007) — Slice 3 추가 ────────────────────────
    # plan을 dict로 변환 (Pydantic model_dump). plan_id를 critic이 echo한다.
    plan_dict = plan.model_dump(mode="json")
    try:
        critic_result = run_critic(plan_dict)
    except ValueError as e:
        logger.warning("Critic LLM JSON 파싱 실패: %s", e)
        return _error_response(
            status_code=status.HTTP_502_BAD_GATEWAY,
            code="E-LLM-002",
            message=f"Critic LLM response parse failed: {e}",
            user_message="AI 응답을 정리하는 중 문제가 생겼어요. 다시 시도해주세요.",
            retry_allowed=True,
        )
    except Exception as e:
        logger.exception("Critic LLM 호출 실패")
        return _error_response(
            status_code=status.HTTP_502_BAD_GATEWAY,
            code="E-LLM-001",
            message=f"Critic LLM call failed: {e}",
            user_message="AI 응답이 늦어져서 멈췄어요. 다시 시도해주세요.",
            retry_allowed=True,
        )

    try:
        critic_evaluation = CriticEvaluation(**critic_result)
    except Exception as e:
        logger.exception("CriticEvaluation 모델 검증 실패")
        return _error_response(
            status_code=status.HTTP_502_BAD_GATEWAY,
            code="E-LLM-003",
            message=f"Critic schema validation failed: {e}",
            user_message="AI가 형식에 맞지 않게 답했어요. 다시 시도해주세요.",
            retry_allowed=True,
        )

    # ── 6. Envelope 조립 ──────────────────────────────────────────────
    # meta.prompt_id 는 응답 본문 생성기인 Planning(P-006)을 노출.
    # Intent(P-001) + Critic(P-007) 은 각각 validation check로 별도 기록.
    envelope = Envelope(
        meta=Meta.make(
            prompt_id=PLANNING_PROMPT_ID,
            prompt_version=PLANNING_PROMPT_VERSION,
            model=settings.openai_model_default,
            locale=req.locale,
        ),
        body=Body(plans=[plan], critic_evaluation=critic_evaluation),
        validation=Validation(
            passed=True,
            checks=[
                ValidationCheck(name="schema_envelope", status="ok"),
                ValidationCheck(
                    name="intent_filter",
                    status="ok",
                    detail=f"{INTENT_PROMPT_ID}@{INTENT_PROMPT_VERSION}",
                ),
                ValidationCheck(name="plan_count", status="ok", detail="1 (Phase 1 deviation)"),
                ValidationCheck(
                    name="critic_evaluation",
                    status="ok",
                    detail=f"{CRITIC_PROMPT_ID}@{CRITIC_PROMPT_VERSION}",
                ),
            ],
            warnings=[
                "phase_1_single_plan",  # 1 vs contract 3
                "phase_1_no_rag",  # Slice 4에서 해소
                # "phase_1_no_critic" — Slice 3에서 해소 (Critic 활성화)
            ],
        ),
    )

    logger.info(
        "generate ok plan_id=%s verdict=%s request_id=%s",
        plan.plan_id,
        critic_evaluation.overall_verdict,
        envelope.meta.request_id,
    )
    return envelope
