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

from typing import Any, Literal

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


# ─── Phase 9 Slice 3 — Select / Feedback (ADR-030) ────────────────────
# 실 plans 테이블 정합: selected_option_index 0–2 (plan_candidates JSONB 배열 인덱스).
# routers/plans.py 의 thin adapter 가 SelectionRepo / FeedbackRepo 로 위임.


class SelectPlanRequest(BaseModel):
    """POST /plans/{plan_id}/select body.

    selected_option_index 는 plan_candidates(3-plan) 배열 인덱스 (0–2).
    selection_reason 은 자유 입력 (옵션, max 2000).
    """

    selected_option_index: int = Field(..., ge=0, le=2)
    selection_reason: str | None = Field(default=None, max_length=2000)


class SelectPlanResponse(BaseModel):
    plan_id: str
    selected_option_index: int
    selection_reason: str | None = None
    selected_at: str


class FeedbackRequest(BaseModel):
    """POST /plans/{plan_id}/feedback body.

    event_type 은 like / dislike / reject / regenerate enum.
    option_index 는 특정 candidate 대상 (0–2). None = plan 전체.
    reason 은 자유 입력 — FeedbackRepo 가 저장 전 PII 마스킹 (security-review T1).
    """

    event_type: Literal["like", "dislike", "reject", "regenerate"]
    option_index: int | None = Field(default=None, ge=0, le=2)
    reason: str | None = Field(default=None, max_length=2000)


class FeedbackResponse(BaseModel):
    plan_id: str
    event_type: str
    option_index: int | None = None
    recorded_at: str


class FeedbackListResponse(BaseModel):
    plan_id: str
    events: list[dict[str, Any]]


# ─── Phase 18 Slice S2 — Branding session (topic_discovery 배선) ──────
# 주제를 모르는 사용자를 LLM 동적 스무고개(Akinator식)로 좁히는 세션 endpoint.
# routers/plans.py 의 thin adapter 가 agents/topic_discovery.py 의
#   run_topic_discovery_ask / run_topic_discovery_finalize 로 위임한다.
# 상태(Q&A history + candidates)는 plan_entry.wizard_data.branding 에 누적 (in-memory).
# auth-optional (익명 OK, wizard 와 동일). PKM 시드는 S4 범위 밖.


class BrandingNextRequest(BaseModel):
    """POST /plans/{plan_id}/branding/next body.

    사용자의 **직전 질문 답변** (카드 선택 or 자유입력). 첫 호출(질문 생성 전)에는 둘 다 None.
      - selected_option: 카드(선택지) 중 하나를 고른 경우.
      - answer:          자유입력으로 답한 경우.
    둘 다 주어지면 selected_option 을 우선 채택 (카드 선택이 더 명시적).
    """

    answer: str | None = Field(default=None, max_length=2000)
    selected_option: str | None = Field(default=None, max_length=500)


class BrandingNextResponse(BaseModel):
    """POST /plans/{plan_id}/branding/next 응답 — topic_discovery ask 결과 + 진행도.

    agent-io 매핑 (topic_discovery.run_topic_discovery_ask → 본 응답):
      mode      ← ask 결과 mode ("ask" | "done")
      question  ← ask 결과 question (mode="done" 시 None)
      options   ← ask 결과 options (2~4개, mode="done" 시 None)
      step      = 누적 history 길이 (현재까지 질문 수)
      max_questions = N고개 상한 (topic_discovery.MAX_QUESTIONS)
    """

    mode: Literal["ask", "done"]
    question: str | None = None
    options: list[str] | None = None
    step: int
    max_questions: int


class BrandingFinalizeResponse(BaseModel):
    """POST /plans/{plan_id}/branding/finalize 응답 — 후보 주제 3개.

    agent-io 매핑 (topic_discovery.run_topic_discovery_finalize → 본 응답):
      candidates ← finalize 결과 candidates (각 {topic,tone,target,format,why_fit} 5필드 보장).
    """

    candidates: list[dict[str, Any]]
