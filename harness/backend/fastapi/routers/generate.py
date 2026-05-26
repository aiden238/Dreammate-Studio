"""POST /api/v1/generate — Phase 1 Slice 1.

Phase 1 deviation from api_contract.md §8.3:
  - Contract: POST /api/v1/plans/{plan_id}/generate (async + SSE, 3 plans)
  - Slice 1: POST /api/v1/generate (sync, 1 plan)
  - Reason: Simplest Slice 원칙 (phase-start v1.1.0 §6.2)
  - Migration: Phase 4 MOA Lite 완성 시 contract endpoint로 정합

Slice 1 응답: output_schema v1.0 envelope (1 plan + dummy validation).
Slice 2: Intent Filter INV-001 분리.
Slice 3: Critic 추가.
"""

from __future__ import annotations

import logging
from uuid import uuid4

from fastapi import APIRouter, HTTPException, status

from ..agents.intent_planning import (
    PROMPT_ID,
    PROMPT_VERSION,
    run_intent_planning,
)
from ..config import get_settings
from ..schemas.input import GenerateRequest
from ..schemas.output import (
    Body,
    Envelope,
    Meta,
    Plan,
    PlanFlowBeat,
    Validation,
    ValidationCheck,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["generate"])


# ─── Endpoint ─────────────────────────────────────────────────────────

@router.post(
    "/generate",
    response_model=Envelope,
    status_code=status.HTTP_200_OK,
    summary="영상기획 1개 생성 (Phase 1 Slice 1)",
    description=(
        "Phase 1 Slice 1 — synchronous endpoint.\n"
        "Phase 4에서 api_contract.md §8.3 (async + SSE) 형식으로 migration 예정.\n"
        "Intent 차단(INV-001)은 Slice 2에서 추가."
    ),
)
def generate(req: GenerateRequest) -> Envelope:
    """단일 LLM 호출 → output_schema v1.0 envelope 반환."""
    settings = get_settings()

    # 1. LLM 호출 (Intent + Planning 통합)
    try:
        llm_result = run_intent_planning(req.input)
    except ValueError as e:
        logger.warning("LLM JSON 파싱 실패: %s", e)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={
                "code": "E-LLM-002",
                "message": "LLM 응답 JSON 파싱 실패",
                "phase_1_note": "Slice 2에서 정식 error envelope로 교체 예정",
            },
        ) from e
    except Exception as e:
        logger.exception("LLM 호출 실패")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={
                "code": "E-LLM-001",
                "message": "LLM 호출 실패",
                "phase_1_note": str(e),
            },
        ) from e

    # 2. Intent 차단 처리 (Slice 1 임시 — Slice 2에서 INV-001 error envelope로 교체)
    if not llm_result.get("intent_ok", False):
        logger.info("Intent 차단: %s", llm_result.get("reason"))
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "code": "INV-001",
                "message": "영상기획 외 요청은 처리할 수 없습니다.",
                "reason": llm_result.get("reason", ""),
                "phase_1_note": "Slice 2에서 ErrorEnvelope 정식 응답으로 교체",
            },
        )

    # 3. plan dict → Pydantic Plan 모델
    plan_raw = llm_result.get("plan") or {}
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
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={
                "code": "E-LLM-003",
                "message": "LLM 응답 구조 검증 실패",
                "phase_1_note": str(e),
            },
        ) from e

    # 4. Envelope 조립
    envelope = Envelope(
        meta=Meta.make(
            prompt_id=PROMPT_ID,
            prompt_version=PROMPT_VERSION,
            model=settings.openai_model_default,
            locale=req.locale,
        ),
        body=Body(plans=[plan]),
        validation=Validation(
            passed=True,
            checks=[
                ValidationCheck(name="schema_envelope", status="ok"),
                ValidationCheck(name="plan_count", status="ok", detail="1 (Phase 1 deviation)"),
            ],
            warnings=[
                "phase_1_single_plan",  # 1 vs contract 3
                "phase_1_no_rag",  # Slice 4에서 해소
                "phase_1_no_critic",  # Slice 3에서 해소
            ],
        ),
    )

    logger.info(
        "generate ok plan_id=%s request_id=%s",
        plan.plan_id,
        envelope.meta.request_id,
    )
    return envelope
