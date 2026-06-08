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

from fastapi import APIRouter, Depends, Request, status
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
from ..middleware import enforce_rate_limit
from ..db import (
    BrandMemoryRepo,
    BrandRepo,
    DomainRepo,
    FeedbackRepo,
    PkmRepo,
    PlansRepo,
    SelectionRepo,
    SeriesRepo,
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
    BrandingSelectRequest,
    BrandingSelectResponse,
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

# Phase 25 Slice S1 (wizard↔4계층 link): 브랜딩 택1 → domain/series auto-seed.
#   - 택1 주제 → DomainRepo.get_or_create(brand_id, topic), 포맷 → SeriesRepo.get_or_create(domain_id, format).
#   - Phase 21/22 graph 가 그대로 렌더 (additive). me.py 의 동일 repo 와 별개 in-memory store —
#     hermetic 단위 테스트는 DI seam(아래 _auto_create_domain_series 인자)으로 격리.
#   - Supabase 사용 가능 시 PostgreSQL(domains/series), 아니면 in-memory fallback (회귀 0).
_domain_repo: DomainRepo = DomainRepo(supabase_client=get_supabase(), in_memory_store={})
_series_repo: SeriesRepo = SeriesRepo(supabase_client=get_supabase(), in_memory_store={})


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
        "images": req.images or [],  # Phase 29 A — 멀티모달 레퍼런스(이미지).
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
    # Phase 27 S3 — 비용 endpoint rate limit (gated default-off → no-op = byte-identical).
    dependencies=[Depends(enforce_rate_limit)],
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
        images=plan_entry.get("images"),  # Phase 29 A — 첨부 레퍼런스(이미지) 멀티모달.
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

    # 5. (gated 자동) 영속화 — confidence ≥ 0.9 명시 선호 후보만 (§7.5 governance parity).
    #   ★ Phase 28 S2: add_entry → consolidate_entry (반복 강화 + 노이즈/중복 제거).
    #     유사 재등장 = confidence↑·dedup(강화), 노이즈 = skip. 이후 안 건드린 약한 entry 는
    #     decay_and_prune 로 점진 제거(불필요 제거). user_locked 는 보호.
    persisted = 0
    touched: set[str] = set()
    for entry in result.get("proposed_entries", []):
        if float(entry.get("confidence", 0.0)) < CONFIDENCE_EXPLICIT:
            continue  # 0.3/0.7 은 제안만 (쓰기 0, pending UX — NG12)
        try:
            action = await pkm_repo.consolidate_entry(
                auth_user_id,
                entry["entry_type"],
                entry["content"],
                scope="personal",
                confidence=float(entry["confidence"]),
                source_plan_id=plan_id,  # Phase 26 S2 — provenance.
            )
            if action is not None:  # None = 노이즈 스킵
                touched.add(action[1])
                persisted += 1
        except Exception as exc:  # pragma: no cover — graceful (저장 실패 무시)
            logger.warning(
                "personal_pkm_persist_failed: %s entry_type=%s (graceful)",
                exc.__class__.__name__, entry.get("entry_type"),
            )

    # 5b. 이번 피드백에서 강화/삽입 안 된 약한 entry 점진 제거 (불필요 제거, graceful).
    try:
        await pkm_repo.decay_and_prune(auth_user_id, scope="personal", protect=touched)
    except Exception as exc:  # pragma: no cover — graceful
        logger.warning("personal_pkm_decay_failed: %s (graceful)", exc.__class__.__name__)

    logger.info(
        "personal_pkm_extract triggered: plan_id=%s auth_user_id=%s proposed=%d persisted=%d",
        plan_id,
        auth_user_id,
        len(result.get("proposed_entries", [])),
        persisted,
    )


# ─── Phase 18 Slice S4 — 브랜딩 후보 택1 → brand_memory 시드 (gated, graceful) ──
# 사용자가 발굴한 브랜딩 후보(주제/톤/타깃/포맷)를 택1 하면, 그 **브랜딩 방향**을 인증 사용자의
# 기본 brand_memory_entries 로 시드한다 (발굴 P18 → 축적 brand_memory → 주입 P17 가-S2 루프의 축적).
#
# candidate → brand_memory entry_type 매핑 (brand_memory_repo._VALID_ENTRY_TYPES 정합):
#   tone   → preferred_tone   ("<tone>")            — 선호 톤 (가장 직접적인 브랜딩 방향)
#   target → preferred_phrase ("타깃 시청자: <target>") — 타깃을 선호 표현 노트로 적재
#   format → preferred_phrase ("선호 포맷: <format>")    — 포맷을 선호 표현 노트로 적재
# ★ target/format 은 전용 enum 이 없어 preferred_phrase 로 노트화한다(접두어로 구분).
#   브랜딩 방향 = 명시 택1 = 고신뢰 → confidence 0.9 (P17 ≥0.9 auto-persist 선례).


# tone 외 필드는 전용 enum 부재 → preferred_phrase 노트로 적재 (접두어로 의미 구분).
_BRANDING_SEED_PREFIX = {
    "target": "타깃 시청자: ",
    "format": "선호 포맷: ",
}
# 브랜딩 방향 시드 신뢰도 — 명시 택1 = 사용자 선택 = 고신뢰 (P17 ≥0.9 auto-persist 선례).
_BRANDING_SEED_CONFIDENCE = 0.9


def _branding_seed_entries(req: BrandingSelectRequest) -> list[tuple[str, str]]:
    """택1 후보 → 시드할 (entry_type, content) 튜플 리스트 (결정적, 빈 값은 skip).

    tone → preferred_tone, target/format → preferred_phrase(접두어 노트).
    """
    entries: list[tuple[str, str]] = []
    tone = (req.tone or "").strip()
    if tone:
        entries.append(("preferred_tone", tone))
    for field in ("target", "format"):
        value = (getattr(req, field) or "").strip()
        if value:
            entries.append(("preferred_phrase", _BRANDING_SEED_PREFIX[field] + value))
    return entries


async def _seed_branding_pkm(
    plan_id: str,
    auth_user_id: str | None,
    req: BrandingSelectRequest,
    *,
    brand_repo: BrandRepo | None = None,
    brand_memory_repo: BrandMemoryRepo | None = None,
) -> int:
    """택1한 브랜딩 방향을 brand_memory 로 시드 (★ gated default-off, authed, best-effort).

    settings.branding_pkm_seed_enabled 가 켜져 있고 신원(auth_user_id)이 있을 때만:
      1. BrandRepo.get_or_create_default(auth_user_id) 로 기본 brand 해결(anchor, idempotent).
         미해결(None) → 시드 skip (0 반환).
      2. 기존 brand_memory(list_for_brand) 로드 → (entry_type, content) 동일 행은 dedup skip.
      3. 남은 항목을 BrandMemoryRepo.add_entry(..., confidence=0.9) 로 적재 (명시 택1=고신뢰).

    ★ behavior-preserving: flag OFF(default) OR 익명(auth_user_id None) → 즉시 0 반환,
      brand_memory 쓰기 0, BrandRepo 미호출 (no surprise write).
    ★ graceful: 어떤 단계 실패도 raise 금지 — 시드 실패가 select 응답을 차단하지 않는다
      (호출자도 try/except 로 이중 방어). 부분 실패 시 성공한 개수만 반환.

    ★ DI seam: brand_repo / brand_memory_repo 인자로 실 Supabase 없이(in-memory) 단위 테스트
      (다-S5 _run_brand_memory_extract_hook 패턴).

    Returns:
        새로 적재된 entry 수 (gated/익명/미해결/전부 dedup → 0).
    """
    settings = get_settings()
    # ★ 게이트 — flag OFF 또는 익명이면 시드/쓰기 0 (byte-identical, no surprise write).
    if not (settings.branding_pkm_seed_enabled and auth_user_id):
        return 0

    seed_entries = _branding_seed_entries(req)
    if not seed_entries:
        return 0

    brand_repo = brand_repo if brand_repo is not None else _brand_repo
    brand_memory_repo = (
        brand_memory_repo if brand_memory_repo is not None else _brand_memory_repo
    )

    # 1. 기본 brand 해결 (get-or-create — anchor). 미해결 → 시드 skip.
    brand_id = await brand_repo.get_or_create_default(auth_user_id)
    if not brand_id:
        logger.info(
            "branding_pkm_seed skip — brand 미해결 plan_id=%s (graceful)", plan_id,
        )
        return 0

    # 2. 기존 brand_memory 로드 → dedup 키 집합 (entry_type, content) 구성.
    existing = await brand_memory_repo.list_for_brand(brand_id)
    existing_keys = {
        (str(e.get("entry_type")), str(e.get("content")))
        for e in existing
        if isinstance(e, dict)
    }

    # 3. 신규 항목만 confidence 0.9 로 적재 (명시 택1 = 고신뢰 — agent_io §7.5 / P17 선례).
    seeded = 0
    for entry_type, content in seed_entries:
        if (entry_type, content) in existing_keys:
            continue  # dedup — 동일 행 재적재 0 (re-select 멱등)
        try:
            await brand_memory_repo.add_entry(
                brand_id,
                entry_type,
                content,
                source_plan_id=plan_id,
                confidence=_BRANDING_SEED_CONFIDENCE,
            )
            existing_keys.add((entry_type, content))  # 동일 호출 내 중복도 방지
            seeded += 1
        except Exception as exc:  # pragma: no cover — graceful (저장 실패 무시)
            logger.warning(
                "branding_pkm_seed_persist_failed: %s entry_type=%s (graceful)",
                exc.__class__.__name__, entry_type,
            )

    logger.info(
        "branding_pkm_seed plan_id=%s brand_id=%s seeded=%d/%d",
        plan_id, brand_id, seeded, len(seed_entries),
    )
    return seeded


# ─── Phase 25 Slice S1 — 브랜딩 택1 → domain/series auto-seed (wizard↔4계층 link) ──
# 사용자가 브랜딩 세션을 완료하고 후보를 택1 하면, 그 주제→domain / 포맷→series 를 사용자의
# 기본 brand 아래 auto-create 한다. 그러면 브랜딩 흐름만으로 /brain 4계층(Phase 21/22 graph)이
# 자동으로 채워진다. ★ _seed_branding_pkm 와 동일 게이트(branding_pkm_seed_enabled)/신원/graceful.

# format 미지정 시 series 기본 이름 (택1 주제 domain 아래 anchor series).
_DEFAULT_SERIES_NAME = "기본 시리즈"


async def _auto_create_domain_series(
    plan_id: str,
    auth_user_id: str | None,
    req: BrandingSelectRequest,
    *,
    brand_repo: BrandRepo | None = None,
    domain_repo: DomainRepo | None = None,
    series_repo: SeriesRepo | None = None,
) -> tuple[str | None, str | None]:
    """택1한 브랜딩 후보로 domain(주제)+series(포맷)를 사용자 brand 아래 auto-seed (★ gated/authed/멱등/graceful).

    settings.branding_pkm_seed_enabled 가 켜져 있고 신원(auth_user_id)이 있을 때만:
      1. BrandRepo.get_or_create_default(auth_user_id) 로 기본 brand 해결(anchor, idempotent).
         미해결(None) → skip ((None, None) 반환).
      2. DomainRepo.get_or_create(brand_id, req.topic) — 택1 주제 → domain (동일 주제 재택1 → 재사용, 중복 0).
      3. SeriesRepo.get_or_create(domain_id, req.format or 기본) — 포맷 → series.

    ★ behavior-preserving: flag OFF(default) OR 익명 → 즉시 (None, None) (no surprise write, BrandRepo 미호출).
      _seed_branding_pkm 와 동일 게이트 — 새 flag 없음.
    ★ idempotent: get_or_create 가 name 일치 row 를 재사용 → 동일 주제 재택1 시 domain/series 중복 0.
    ★ graceful: 어떤 단계 실패도 raise 금지 — 확보한 것까지만 반환 (호출자도 try/except 이중 방어).
    ★ DI seam: brand_repo/domain_repo/series_repo 인자로 실 Supabase 없이(in-memory) 단위 테스트.

    Returns:
        (domain_id, series_id). skip/실패 단계는 None (둘 다 None = gated/익명/brand 미해결).
    """
    settings = get_settings()
    # ★ 게이트 — flag OFF 또는 익명이면 생성 0 (byte-identical, no surprise write).
    if not (settings.branding_pkm_seed_enabled and auth_user_id):
        return (None, None)

    brand_repo = brand_repo if brand_repo is not None else _brand_repo
    domain_repo = domain_repo if domain_repo is not None else _domain_repo
    series_repo = series_repo if series_repo is not None else _series_repo

    domain_id: str | None = None
    series_id: str | None = None
    try:
        # 1. 기본 brand 해결 (get-or-create — anchor, _seed_branding_pkm 와 동일).
        brand_id = await brand_repo.get_or_create_default(auth_user_id)
        if not brand_id:
            logger.info(
                "branding_4layer skip — brand 미해결 plan_id=%s (graceful)", plan_id,
            )
            return (None, None)

        # 2. 택1 주제 → domain (멱등 — 동일 주제 재택1 시 기존 domain 재사용).
        domain_name = (req.topic or "").strip()
        if not domain_name:
            return (None, None)
        domain = await domain_repo.get_or_create(brand_id, domain_name)
        if not domain or not domain.get("id"):
            logger.info(
                "branding_4layer skip — domain 미생성 plan_id=%s (graceful)", plan_id,
            )
            return (None, None)
        domain_id = str(domain["id"])

        # 3. 택1 포맷 → series (포맷 비면 기본 시리즈 이름, 멱등).
        series_name = (req.format or "").strip() or _DEFAULT_SERIES_NAME
        series = await series_repo.get_or_create(domain_id, series_name)
        if series and series.get("id"):
            series_id = str(series["id"])
    except Exception as exc:  # pragma: no cover — graceful (생성 실패해도 raise 0)
        logger.warning(
            "branding_4layer_auto_create_failed: %s (graceful, 확보분 반환)",
            exc.__class__.__name__,
        )

    logger.info(
        "branding_4layer plan_id=%s domain_id=%s series_id=%s",
        plan_id, domain_id, series_id,
    )
    return (domain_id, series_id)


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

    # Phase 29 — 상황 버튼 goal(예: sns_validation) 보존 → 질문 프레이밍 분기.
    if getattr(req, "goal", None) and not branding.get("goal"):
        branding["goal"] = req.goal

    # 2. 다음 질문 생성 (또는 종료) — topic_discovery ask 위임.
    state = {
        "history": history,
        "max_questions": BRANDING_MAX_QUESTIONS,
        "goal": branding.get("goal"),
    }
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


@router.post(
    "/plans/{plan_id}/branding/select",
    response_model=BrandingSelectResponse,
    responses={404: {"model": ErrorEnvelope, "description": "plan_id 미발견 (INV-006)"}},
    summary="브랜딩 후보 택1 — planning 연결 + brand_memory 시드 (Phase 18 Slice S4)",
    description=(
        "발굴한 후보 주제 1개를 택1 한다. (1) 택1 후보를 plan_entry.wizard_data.branding.selected 에 "
        "저장하고 plan_entry.initial_input 을 그 주제로 설정해 후속 generate 가 그대로 받게 한다 "
        "(planning 연결). (2) ★ gated+authed: settings.branding_pkm_seed_enabled 가 켜져 있고 신원이 "
        "있으면 그 브랜딩 방향(tone→preferred_tone, target/format→preferred_phrase)을 사용자의 기본 "
        "brand_memory 로 confidence 0.9 시드한다 (발굴→축적→주입 루프, P17 주입이 다음 generate 부터 읽음). "
        "★ flag OFF / 익명 → brand_memory 쓰기 0 (selected/initial_input 은 항상 저장 — byte-identical). "
        "graceful (시드 실패해도 200). auth-optional."
    ),
)
async def plans_branding_select(
    plan_id: str, req: BrandingSelectRequest, request: Request,
):
    plan_entry = _plan_store.get(plan_id)
    if not plan_entry:
        return _not_found_response(plan_id)

    # 1. planning 연결 — 택1 후보 저장 + initial_input 을 택1 주제로 설정 (시드 유무와 무관, 항상).
    #    후속 generate(plans_generate → generate_plan)가 plan_entry["initial_input"] 을 입력으로 받는다.
    branding = _branding_state(plan_entry)
    branding["selected"] = {
        "topic": req.topic,
        "tone": req.tone,
        "target": req.target,
        "format": req.format,
    }
    plan_entry["initial_input"] = req.topic
    plan_entry["status"] = "wizard_in_progress"
    plan_entry["updated_at"] = _now_iso()

    # 2. ★ gated+authed brand_memory 시드 (best-effort) — 발굴→축적→주입 루프의 축적 단계.
    #    flag OFF / 익명이면 _seed_branding_pkm 가 즉시 0 반환 (쓰기 0, BrandRepo 미호출).
    #    graceful: 시드 실패해도 select 응답 차단 0 (helper 내부 + 본 try/except 이중 방어).
    auth_user_id = _auth_user_id(request)
    seeded = 0
    try:
        seeded = await _seed_branding_pkm(plan_id, auth_user_id, req)
    except Exception as exc:  # pragma: no cover — graceful (시드 실패 시 응답 차단 0)
        logger.warning(
            "branding_pkm_seed_hook_failed: %s (select 저장은 성공)",
            exc.__class__.__name__,
        )

    # 3. ★ gated+authed domain/series auto-seed (Phase 25 S1, best-effort) — wizard↔4계층 link.
    #    flag OFF / 익명이면 _auto_create_domain_series 가 즉시 (None, None) (생성 0, BrandRepo 미호출).
    #    graceful: 생성 실패해도 select 응답 차단 0 (helper 내부 + 본 try/except 이중 방어).
    domain_id: str | None = None
    series_id: str | None = None
    try:
        domain_id, series_id = await _auto_create_domain_series(plan_id, auth_user_id, req)
    except Exception as exc:  # pragma: no cover — graceful (생성 실패 시 응답 차단 0)
        logger.warning(
            "branding_4layer_hook_failed: %s (select 저장은 성공)",
            exc.__class__.__name__,
        )

    logger.info(
        "branding_select plan_id=%s seeded=%d domain_id=%s series_id=%s",
        plan_id, seeded, domain_id, series_id,
    )
    return BrandingSelectResponse(
        ok=True, seeded=seeded, domain_id=domain_id, series_id=series_id,
    )
