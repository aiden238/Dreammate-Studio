"""Phase 4 plans router schemas.

Phase 4 endpoint contract (api_contract.md §8):
  POST /api/v1/plans/start
  POST /api/v1/plans/{plan_id}/wizard/{step}
  POST /api/v1/plans/{plan_id}/generate
  GET /api/v1/plans/{plan_id}

Phase 4 Slice 1 — skeleton 단계. wizard step 진행은 200 + 저장만,
generate는 202 (Accepted) skeleton. Slice 2에서 본격 3-plan generation 구현.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class PlanStartRequest(BaseModel):
    """POST /plans/start body.

    Phase 4 Slice 1은 user_input optional — 사용자가 Discovery/Quick 진입 전에도
    plan_id를 발급할 수 있어야 한다 (frontend wizard 시작 시점).
    """

    user_input: str | None = Field(
        default=None,
        max_length=2000,
        description="optional initial prompt",
    )
    locale: str = Field(default="ko-KR")


class PlanStartResponse(BaseModel):
    plan_id: str
    created_at: str
    locale: str


class WizardStepRequest(BaseModel):
    """POST /plans/{plan_id}/wizard/{step} — Phase 4 skeleton.

    Phase 4는 skeleton — 200 응답 + selected data를 in-memory 저장만.
    실제 step 처리 (LLM 호출, 분기 로직)는 Phase 5+ Auth/DB 본격화 이후.
    """

    selected_card_id: str | None = None
    user_input: str | None = Field(default=None, max_length=2000)
    extra: dict[str, Any] = Field(default_factory=dict)


class WizardStepResponse(BaseModel):
    plan_id: str
    step: str  # 1~7 (Discovery) 또는 quick.* 등
    accepted: bool
    next_step: str | None = None  # next step hint


class GenerateRequest(BaseModel):
    """POST /plans/{plan_id}/generate — Slice 2에서 본격 구현.

    Phase 4 Slice 1은 skeleton (202 Accepted).
    Slice 2에서 use_rag / use_critic 등 본격 처리 + multi-model 파라미터 추가.
    """

    use_rag: bool = True
    use_critic: bool = True
    # multi-model 파라미터는 Slice 2에서 추가 (config.openai_models_for_3plan)


class PlanResource(BaseModel):
    """GET /plans/{plan_id} 응답.

    Slice 1: status + 메타데이터만 반환.
    Slice 2: envelope 필드에 3-plan Envelope (Phase 1 호환 구조) 채움.
    """

    plan_id: str
    status: str  # "created" | "wizard_in_progress" | "generated" | "selected"
    created_at: str
    updated_at: str
    envelope: dict[str, Any] | None = Field(
        default=None,
        description="Slice 2 generate 완료 후 채워짐 (3-plan Envelope).",
    )
