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

from ..agents.brand_memory_extractor import (
    CONFIDENCE_EXPLICIT,
    extract_brand_memory_candidates,
    run_brand_memory_extractor,
)
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
    run_planning_multi_provider_3,
    run_planning_parallel_3,
)
from ..agents.rewriter import run_rewriter
from ..agents.topic_discovery import (
    MAX_QUESTIONS as BRANDING_MAX_QUESTIONS,
    run_topic_discovery_ask,
    run_topic_discovery_finalize,
)
from ..config import get_settings
from ..db import (
    BrandMemoryRepo,
    BrandRepo,
    FeedbackRepo,
    PkmRepo,
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
from ..rag import (
    RetrievalResult,
    build_candidate_from_feedback,
    enqueue_feedback_candidate,
    run_rag_retrieval,
)
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
    BrandingFinalizeResponse,
    BrandingNextRequest,
    BrandingNextResponse,
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

# Phase 9 Slice 4 (ADR-031): feedback → candidate_knowledge 적재 경로 (Brand Memory 준비).
#   - feedback 저장 후 candidate_knowledge(status='pending') 로 graceful 적재 (데이터 누적 인프라).
#   - ★ pending 까지만 — 자동 승격 X (NG12). P-AUX-2 agent 미구현 (NG1).
#   - Supabase 사용 가능 시 candidate_knowledge INSERT, 아니면 본 in-memory list fallback.
_candidate_store: list[dict[str, Any]] = []

# Phase 17 다-S5 (브랜드 anchor + brand_memory 적재): brand get-or-create + Brand Memory CRUD.
#   - _brand_repo: 인증 사용자의 기본 brand get-or-create (가-S3 BrandRepo, graceful).
#   - _brand_memory_repo: 추출된 후보의 영속화 대상 (가-S2 주입이 읽는 동일 테이블).
#   - Supabase 사용 가능 시 PostgreSQL, 아니면 각 repo 의 in-memory fallback (회귀 0).
_brand_repo: BrandRepo = BrandRepo(
    supabase_client=get_supabase(),
    in_memory_store={},
)
_brand_memory_repo: BrandMemoryRepo = BrandMemoryRepo(
    supabase_client=get_supabase(),
    in_memory_store={},
)

# Phase 17 다-S6 (개인 PKM 추출 루프): feedback 신호 → pkm_entries(scope=personal) 적재.
#   - 다-S3 이 만든 동일 테이블(가-S3 PkmRepo) — 가-S3 주입(읽기)이 읽는 그 테이블.
#   - ★ brand-독립 (User 계층) — brand 해결 불필요, auth_user_id 만으로 격리/적재.
#   - Supabase 사용 가능 시 PostgreSQL(pkm_entries), 아니면 in-memory fallback (회귀 0).
_pkm_repo: PkmRepo = PkmRepo(
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
async def plans_generate(plan_id: str, req: GenerateRequest, request: Request):
    """Phase 8 Slice 2 (ADR-027): thin adapter — orchestration/moa_orchestrator 위임.

    plans_generate() god-function 본문은 behavior-preserving 으로
    orchestration/moa_orchestrator.py::generate_plan() 으로 이관됨.
    router 는 HTTP 경계(plan_id 조회 + 404) 만 담당하고 orchestration 은 위임한다
    (moa_policy §2 "오케스트레이터가 항상 중개").

    Phase 17 가-S1 (신원 plumbing): auth_middleware 가 주입한 request.state.user 에서
    auth_user_id 를 추출(_auth_user_id, 없으면 None graceful)하여 generate_plan 에
    **선택적** 인자로 전달한다. ★ 익명(None) 요청은 기존과 byte-identical (회귀 0) —
    신원은 cookie/JWT 출처이므로 request body/schema 불변(contract 무변경).
    """
    plan_entry = _plan_store.get(plan_id)
    if not plan_entry:
        return not_found_response(plan_id)
    # Phase 8 Slice 3 (ADR-028): StoreProgressSink 주입 → generate stage 진행을
    # progress_store 에 기록 (sse.py 가 read). Slice 2 default(NullProgressSink) 대비
    # 부수효과(store 기록)만 추가 — Envelope/응답 동일 (회귀 0).
    # Phase 17 가-S1: 신원 전달 (anon 이면 auth_user_id=None → 기존 경로 그대로).
    #   brand_id 는 현재 request↔brand 매핑 source 부재(assumptions U2) → None 유지 (가-S2 확정).
    result = await generate_plan(
        plan_id, plan_entry, req,
        progress=StoreProgressSink(plan_id),
        auth_user_id=_auth_user_id(request),
    )
    # Phase 15 S3 (gated 직렬화 분기 — live POST):
    #   ★ 성공 Envelope 은 항상 generate_plan 이 plan_entry["envelope"] 에 저장한 **mode 별 직렬화 dict**
    #   (envelope_to_response_dict(output_mode) — compact: rich+director 제외 / rich: director 제외 /
    #   director: 전부)를 JSONResponse 로 반환한다. Envelope 모델을 그대로 반환하면 FastAPI 가 rich+director
    #   Optional 슬롯(None/[])까지 직렬화 → compact/rich byte-identical 깨짐. 에러(JSONResponse)는 그대로 전달.
    if isinstance(result, Envelope):
        stored = plan_entry.get("envelope")
        if stored is not None:
            return JSONResponse(content=stored, status_code=200)
    return result


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


# ─── Phase 17 다-S5 — brand_memory 추출 루프 배선 (gated, graceful) ────
async def _run_brand_memory_extract_hook(
    plan_id: str,
    auth_user_id: str | None,
    *,
    feedback_repo: FeedbackRepo | None = None,
    selection_repo: SelectionRepo | None = None,
    brand_repo: BrandRepo | None = None,
    brand_memory_repo: BrandMemoryRepo | None = None,
) -> None:
    """feedback/selection 신호 → brand_memory_entries 추출·적재 (★ gated default-off, best-effort).

    feedback(또는 selection) 이 영속화된 **후** 호출하는 부가 처리. settings.brand_memory_extract_enabled
    가 켜져 있고 신원(auth_user_id)이 있을 때만:
      1. BrandRepo.get_or_create_default(auth_user_id) 로 사용자의 기본 brand 를 해결(가-S3 anchor,
         idempotent — 기존 있으면 그 id, 없으면 1개 생성). 미해결(None) → 적재 skip.
      2. 누적 신호 로드 — 현재 plan 의 feedback_events(list_for_plan) + selected_plans(get).
         ★ "list by user" repo 메서드는 본 슬라이스 범위 밖(migration/repo 확장 X) — plan 단위로
         reasonably available 한 신호를 로드한다(graceful). 후속 슬라이스에서 user 단위 누적 확장 가능.
      3. 기존 brand_memory(list_for_brand) 로드 — extractor 의 dedup(conflicts 분리) 입력.
      4. run_brand_memory_extractor(..., persist=True) 호출.
         ★ governance (ADR-031 §P-AUX-2 / agent_io §7.5): persist=True 여도 자동 INSERT 는
         confidence ≥ 0.9 (persist_min_confidence 기본) 명시-선호 후보만 — 0.3/0.7 은 제안만(쓰기 0).
         blanket 자동 승격 0 (NG12 계승). reason 은 feedback_repo 가 이미 마스킹 + extractor 이중 방어(T5).

    ★ behavior-preserving: flag OFF(default) OR 익명(auth_user_id None) → 즉시 return,
      brand_memory_entries 쓰기 0, BrandRepo 미호출 (no surprise write). feedback/selection 응답
      byte-identical.
    ★ graceful: 어떤 단계 실패도 raise 금지 — 추출 실패가 feedback/selection 기록을 차단하지 않는다
      (호출자도 try/except 로 이중 방어). 추출 결과는 로깅만 (응답 schema 불변).

    ★ DI seam: feedback_repo / selection_repo / brand_repo / brand_memory_repo 인자로 실 Supabase
      없이(in-memory) 배선을 단위 테스트한다 (test_brand_injection / test_brand_repo 패턴).
    """
    settings = get_settings()
    # ★ 게이트 — flag OFF 또는 익명이면 추출/쓰기 0 (byte-identical, no surprise write).
    if not (settings.brand_memory_extract_enabled and auth_user_id):
        return

    feedback_repo = feedback_repo if feedback_repo is not None else _feedback_repo
    selection_repo = selection_repo if selection_repo is not None else _selection_repo
    brand_repo = brand_repo if brand_repo is not None else _brand_repo
    brand_memory_repo = (
        brand_memory_repo if brand_memory_repo is not None else _brand_memory_repo
    )

    # 1. 사용자의 기본 brand 해결 (get-or-create — brand_memory anchor). 미해결 → 적재 skip.
    brand_id = await brand_repo.get_or_create_default(auth_user_id)
    if not brand_id:
        logger.info(
            "brand_memory_extract skip — brand 미해결 plan_id=%s (graceful)", plan_id,
        )
        return

    # 2. 누적 신호 로드 (현재 plan 단위 — reasonably available, graceful).
    feedback_events = await feedback_repo.list_for_plan(plan_id)
    selection = await selection_repo.get(plan_id)
    selected_plans = [selection] if selection else None

    # 3. 기존 brand_memory 로드 (extractor dedup/conflict 입력).
    current_brand_memory = await brand_memory_repo.list_for_brand(brand_id)

    # 4. 추출 + (gated 자동) 영속화 — persist=True 여도 confidence ≥ 0.9 만 INSERT (§7.5 governance).
    extraction = await run_brand_memory_extractor(
        feedback_events,
        selected_plans,
        brand_id=brand_id,
        current_brand_memory=current_brand_memory,
        repo=brand_memory_repo,
        persist=True,
    )
    logger.info(
        "brand_memory_extract triggered: plan_id=%s brand_id=%s proposed=%d persisted=%d",
        plan_id,
        brand_id,
        len(extraction.get("proposed_entries", [])),
        len(extraction.get("persisted", [])),
    )


# ─── Phase 17 다-S6 — 개인 PKM 추출 루프 배선 (gated, graceful) ────────
async def _run_personal_pkm_extract_hook(
    plan_id: str,
    auth_user_id: str | None,
    *,
    feedback_repo: FeedbackRepo | None = None,
    selection_repo: SelectionRepo | None = None,
    pkm_repo: PkmRepo | None = None,
    feedback_events: list[dict[str, Any]] | None = None,
    selected_plans: list[dict[str, Any]] | None = None,
) -> None:
    """feedback/selection 신호 → pkm_entries(scope=personal) 추출·적재 (★ gated default-off, best-effort).

    다-S5 `_run_brand_memory_extract_hook` 의 **개인 scope 대칭**. feedback 이 영속화된 **후**
    호출하는 부가 처리. settings.personal_pkm_extract_enabled 가 켜져 있고 신원(auth_user_id)이
    있을 때만:
      1. ★ brand 해결 불필요 — personal scope 는 brand-독립(User 계층). auth_user_id 가 곧 키다
         (다-S5 의 get_or_create_default 단계 없음).
      2. 누적 신호 로드 — 현재 plan 의 feedback_events(list_for_plan) + selected_plans(get).
         ★ 호출자가 이미 로드한 feedback_events/selected_plans 를 인자로 넘기면 재로드하지 않는다
         (brand hook 과 DB 읽기 공유 — graceful double-read 회피). 미전달 시 repo 로 로드(graceful).
      3. 기존 personal PKM(list_for_user, scope=personal) 로드 — extractor 의 dedup(conflicts 분리)
         입력. entry_type enum 은 brand_memory_entries 와 동일하므로 current_brand_memory 로 전달.
      4. 순수 extract_brand_memory_candidates(...) 호출 (LLM 0, heuristic).
         ★ run_brand_memory_extractor(persist=True) 의 add_entry 는 **brand-keyed** 시그니처라
         PkmRepo 에 맞지 않음 → 순수 추출기만 부르고 영속화는 본 helper 가 PkmRepo 로 직접 수행.
      5. governance (ADR-031 §P-AUX-2 / agent_io §7.5): confidence ≥ CONFIDENCE_EXPLICIT(0.9)
         명시-선호 후보만 PkmRepo.add_entry(scope='personal') 자동 INSERT — 0.3/0.7 은 제안만(쓰기 0).
         blanket 자동 승격 0 (NG12 계승 — 다-S5 와 거버넌스 parity).

    ★ behavior-preserving: flag OFF(default) OR 익명(auth_user_id None) → 즉시 return,
      pkm_entries 쓰기 0, 추출기 미호출 (no surprise write). feedback 응답 byte-identical.
    ★ graceful: 어떤 단계 실패도 raise 금지 — 추출 실패가 feedback 기록을 차단하지 않는다
      (호출자도 try/except 로 이중 방어). 추출 결과는 로깅만 (응답 schema 불변).

    ★ DI seam: feedback_repo / selection_repo / pkm_repo 인자로 실 Supabase 없이(in-memory)
      배선을 단위 테스트한다 (test_brand_memory_extract_wiring / test_pkm_repo 패턴).
    """
    settings = get_settings()
    # ★ 게이트 — flag OFF 또는 익명이면 추출/쓰기 0 (byte-identical, no surprise write).
    if not (settings.personal_pkm_extract_enabled and auth_user_id):
        return

    feedback_repo = feedback_repo if feedback_repo is not None else _feedback_repo
    selection_repo = selection_repo if selection_repo is not None else _selection_repo
    pkm_repo = pkm_repo if pkm_repo is not None else _pkm_repo

    # 2. 누적 신호 — 호출자가 이미 로드한 값을 재사용(DB 읽기 공유), 없으면 plan 단위 로드 (graceful).
    if feedback_events is None:
        feedback_events = await feedback_repo.list_for_plan(plan_id)
    if selected_plans is None:
        selection = await selection_repo.get(plan_id)
        selected_plans = [selection] if selection else None

    # 3. 기존 personal PKM 로드 (extractor dedup/conflict 입력 — entry_type enum 호환).
    current_pkm = await pkm_repo.list_for_user(auth_user_id, scope="personal")

    # 4. 순수 추출 (LLM 0, heuristic). persist 는 PkmRepo 키 시그니처 차이로 본 helper 가 직접 수행.
    result = extract_brand_memory_candidates(
        feedback_events,
        selected_plans,
        current_brand_memory=current_pkm,
    )

    # 5. (gated 자동) 영속화 — confidence ≥ 0.9 명시 선호 후보만 INSERT (§7.5 governance parity).
    persisted = 0
    for entry in result.get("proposed_entries", []):
        if float(entry.get("confidence", 0.0)) < CONFIDENCE_EXPLICIT:
            continue  # 0.3/0.7 은 제안만 (쓰기 0, pending UX — NG12)
        try:
            await pkm_repo.add_entry(
                auth_user_id,
                entry["entry_type"],
                entry["content"],
                scope="personal",
                confidence=float(entry["confidence"]),
            )
            persisted += 1
        except Exception as exc:  # pragma: no cover — graceful (저장 실패 무시)
            logger.warning(
                "personal_pkm_persist_failed: %s entry_type=%s (graceful)",
                exc.__class__.__name__, entry.get("entry_type"),
            )

    logger.info(
        "personal_pkm_extract triggered: plan_id=%s auth_user_id=%s proposed=%d persisted=%d",
        plan_id,
        auth_user_id,
        len(result.get("proposed_entries", [])),
        persisted,
    )


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

    # Phase 9 Slice 4 (ADR-031): feedback → candidate_knowledge(pending) 적재 (Brand Memory 준비).
    #   - graceful: 적재 실패해도 feedback 응답 차단 X (try/except).
    #   - ★ pending 까지만 — 자동 승격 X (NG12). reason 은 repo 가 이미 마스킹한 값(row) 사용 (T5 이중 방어).
    try:
        candidate = build_candidate_from_feedback(
            plan_id,
            req.event_type,
            reason=row.get("reason"),
            option_index=req.option_index,
        )
        await enqueue_feedback_candidate(
            candidate,
            supabase_client=_feedback_repo.client,
            in_memory_store=_candidate_store,
        )
    except Exception as exc:  # pragma: no cover — graceful (적재 실패 시 응답 차단 0)
        logger.warning(
            "feedback_candidate_enqueue_failed: %s (feedback 저장은 성공)",
            exc.__class__.__name__,
        )

    # Phase 17 다-S5 (P-AUX-2 배선): feedback 저장 후 brand_memory 추출 루프 best-effort 호출.
    #   - ★ gated default-off: settings.brand_memory_extract_enabled OFF 또는 익명이면 _run_brand_memory_
    #     extract_hook 가 즉시 return → 추출/쓰기 0 (응답 byte-identical, no surprise write).
    #     (Phase 10 S2 의 proposed-only 로깅 hook 을 본 gated persist hook 으로 승격 — agent_io §7.5.)
    #   - ★ governance (ADR-031 §P-AUX-2 / agent_io §7.5): ON+신원이어도 자동 INSERT 는 confidence ≥ 0.9
    #     명시-선호 후보만 — 0.3/0.7 은 제안만 (쓰기 0). blanket 자동 승격 0 (NG12 계승).
    #   - graceful: 추출 실패해도 feedback 응답 차단 0 (helper 내부 + 본 try/except 이중 방어).
    #     reason 은 feedback_repo 가 이미 마스킹 + extractor 이중 방어 (T5).
    auth_user_id = _auth_user_id(request)
    try:
        await _run_brand_memory_extract_hook(plan_id, auth_user_id)
    except Exception as exc:  # pragma: no cover — graceful (추출 실패 시 응답 차단 0)
        logger.warning(
            "brand_memory_extract_hook_failed: %s (feedback 저장은 성공)",
            exc.__class__.__name__,
        )

    # Phase 17 다-S6 (P-AUX-2 개인 scope 배선): feedback 저장 후 개인 PKM 추출 루프 best-effort.
    #   - ★ gated default-off: settings.personal_pkm_extract_enabled OFF 또는 익명이면
    #     _run_personal_pkm_extract_hook 가 즉시 return → 추출/쓰기 0 (응답 byte-identical).
    #   - ★ brand-독립 (User 계층): brand 해결 없이 auth_user_id 만으로 pkm_entries(personal) 적재.
    #   - ★ governance (ADR-031 §7.5): 자동 INSERT 는 confidence ≥ 0.9 명시 선호만 (다-S5 parity).
    #   - graceful: 추출 실패해도 feedback 응답 차단 0 (helper 내부 + 본 try/except 이중 방어).
    #     brand hook 과 별개 관심사이므로 별도 try/except — 한쪽 실패가 다른 쪽을 막지 않는다.
    try:
        await _run_personal_pkm_extract_hook(plan_id, auth_user_id)
    except Exception as exc:  # pragma: no cover — graceful (추출 실패 시 응답 차단 0)
        logger.warning(
            "personal_pkm_extract_hook_failed: %s (feedback 저장은 성공)",
            exc.__class__.__name__,
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


# ─── Phase 18 Slice S2 — Branding session (topic_discovery 배선) ──────
# 주제를 모르는 사용자를 LLM 동적 스무고개(Akinator식)로 좁혀 후보 주제를 발굴한다.
# thin adapter: plan_entry 존재 확인(404) → topic_discovery agent 위임 → 상태 누적 → 응답.
#
# 상태 누적 (in-memory, _plan_store[plan_id]["wizard_data"]["branding"]):
#   {
#     "history": [{"question": str, "options": [str], "answer": str|None}, ...],
#     "candidates": [{topic,tone,target,format,why_fit}, ...]  # finalize 후 채워짐
#   }
#   - ask: pending 질문(answer=None)을 history 끝에 1개 둔다. 다음 next 호출에서
#     answer/selected_option 이 오면 그 pending 항목에 채운 뒤 다음 질문을 만든다.
#   - mode="done": 새 질문 추가 없음 (상한 도달 또는 충분히 좁혀짐).
#
# agent-io 매핑 (docs/contracts/agent_io_contract.md P-AUX-3 정합 — 본 파일은 runtime only):
#   ask     → {"mode","question","options","rationale"}  ↔ BrandingNextResponse{mode,question,options,step,max_questions}
#   finalize→ {"candidates":[{topic,tone,target,format,why_fit}×3]} ↔ BrandingFinalizeResponse{candidates}
#
# auth-optional (익명 OK, wizard 와 동일) — 인증 요구 X (PKM 시드는 S4).


def _branding_state(plan_entry: dict[str, Any]) -> dict[str, Any]:
    """plan_entry.wizard_data.branding 를 get-or-init 해서 반환 (history 보장)."""
    wizard_data = plan_entry.setdefault("wizard_data", {})
    branding = wizard_data.setdefault("branding", {"history": []})
    # graceful — history 가 비정상이면 list 로 정규화.
    if not isinstance(branding.get("history"), list):
        branding["history"] = []
    return branding


@router.post(
    "/plans/{plan_id}/branding/next",
    response_model=BrandingNextResponse,
    responses={404: {"model": ErrorEnvelope, "description": "plan_id 미발견 (INV-006)"}},
    summary="브랜딩 스무고개 — 다음 질문 / 종료 (Phase 18 Slice S2)",
    description=(
        "직전 질문 답변(카드 선택 or 자유입력)을 받아 다음 적응형 질문 1개 + 선택지 2~4개를 "
        "반환하거나(mode=ask), 충분히 좁혀졌으면 종료 신호(mode=done)를 반환한다. "
        "Q&A 상태는 plan_entry.wizard_data.branding 에 누적 (in-memory). "
        "topic_discovery.run_topic_discovery_ask 위임 (N고개 상한 강제). auth-optional."
    ),
)
def plans_branding_next(plan_id: str, req: BrandingNextRequest):
    plan_entry = _plan_store.get(plan_id)
    if not plan_entry:
        return _not_found_response(plan_id)

    branding = _branding_state(plan_entry)
    history: list[dict[str, Any]] = branding["history"]

    # 1. 직전 질문 답변 기록 — pending(answer=None) 항목이 있고 답이 왔으면 채운다.
    #    카드 선택(selected_option)을 자유입력(answer)보다 우선 (더 명시적).
    answer = req.selected_option if req.selected_option else req.answer
    if answer and history and history[-1].get("answer") is None:
        history[-1]["answer"] = answer

    # 2. 다음 질문 생성 (또는 종료) — topic_discovery ask 위임.
    state = {"history": history, "max_questions": BRANDING_MAX_QUESTIONS}
    try:
        result = run_topic_discovery_ask(state)
    except Exception as exc:  # graceful — agent 실패가 plan 흐름을 차단하지 않는다 (500 금지).
        logger.warning(
            "branding_next agent_failed: %s plan_id=%s (graceful done fallback)",
            exc.__class__.__name__, plan_id,
        )
        plan_entry["updated_at"] = _now_iso()
        return BrandingNextResponse(
            mode="done",
            question=None,
            options=None,
            step=len(history),
            max_questions=BRANDING_MAX_QUESTIONS,
        )

    mode = result.get("mode")
    plan_entry["status"] = "wizard_in_progress"
    plan_entry["updated_at"] = _now_iso()

    # 3-a. ask: pending 질문 1개를 history 에 추가하고 반환.
    if mode == "ask":
        question = result.get("question")
        options = result.get("options") or None
        history.append({"question": question, "options": options, "answer": None})
        logger.info(
            "branding_next ask plan_id=%s step=%d options=%d",
            plan_id, len(history), len(options or []),
        )
        return BrandingNextResponse(
            mode="ask",
            question=question,
            options=options,
            step=len(history),
            max_questions=BRANDING_MAX_QUESTIONS,
        )

    # 3-b. done: 새 질문 추가 없음 (상한 도달 또는 충분히 좁혀짐).
    logger.info("branding_next done plan_id=%s step=%d", plan_id, len(history))
    return BrandingNextResponse(
        mode="done",
        question=None,
        options=None,
        step=len(history),
        max_questions=BRANDING_MAX_QUESTIONS,
    )


@router.post(
    "/plans/{plan_id}/branding/finalize",
    response_model=BrandingFinalizeResponse,
    responses={404: {"model": ErrorEnvelope, "description": "plan_id 미발견 (INV-006)"}},
    summary="브랜딩 스무고개 — 후보 주제 3개 합성 (Phase 18 Slice S2)",
    description=(
        "누적된 Q&A 히스토리를 종합해 후보 영상 주제 3개(각 {topic,tone,target,format,why_fit})를 "
        "합성·반환하고 plan_entry.wizard_data.branding.candidates 에 저장한다. "
        "topic_discovery.run_topic_discovery_finalize 위임. graceful (실패 시 빈 후보). auth-optional."
    ),
)
def plans_branding_finalize(plan_id: str):
    plan_entry = _plan_store.get(plan_id)
    if not plan_entry:
        return _not_found_response(plan_id)

    branding = _branding_state(plan_entry)
    state = {"history": branding["history"]}

    try:
        result = run_topic_discovery_finalize(state)
        candidates = result.get("candidates", [])
    except Exception as exc:  # graceful — finalize 실패가 plan 흐름을 차단하지 않는다 (500 금지).
        logger.warning(
            "branding_finalize agent_failed: %s plan_id=%s (graceful empty candidates)",
            exc.__class__.__name__, plan_id,
        )
        candidates = []

    branding["candidates"] = candidates
    plan_entry["updated_at"] = _now_iso()
    logger.info("branding_finalize plan_id=%s candidates=%d", plan_id, len(candidates))
    return BrandingFinalizeResponse(candidates=candidates)
