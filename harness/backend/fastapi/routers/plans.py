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

from fastapi import APIRouter, status
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
from ..db import PlansRepo, get_supabase, save_video_planning
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


def _error_envelope_response(
    *,
    status_code: int,
    code: str,
    message: str,
    user_message: str,
    retry_allowed: bool = True,
) -> JSONResponse:
    """generic ErrorEnvelope 응답 (E-LLM-* / INV-* 등)."""
    envelope = ErrorEnvelope(
        error=ErrorBody(
            code=code,
            message=message,
            user_message=user_message,
            retry_allowed=retry_allowed,
        ),
        meta=ErrorMeta.make(),
    )
    return JSONResponse(status_code=status_code, content=envelope.model_dump(mode="json"))


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
    """Phase 4 Slice 2 본격 — 3-plan parallel + Critic + DB save."""
    plan_entry = _plan_store.get(plan_id)
    if not plan_entry:
        return _not_found_response(plan_id)

    settings = get_settings()
    user_input = plan_entry.get("initial_input") or "(빈 입력)"
    locale = plan_entry.get("locale", "ko-KR")

    # 1. Intent ──────────────────────────────────────────────────────
    try:
        intent_result = run_intent(user_input)
    except ValueError as e:
        logger.warning("Intent LLM JSON 파싱 실패: %s", e)
        return _error_envelope_response(
            status_code=status.HTTP_502_BAD_GATEWAY,
            code="E-LLM-002",
            message=f"Intent LLM response parse failed: {e}",
            user_message="AI 응답을 정리하는 중 문제가 생겼어요. 다시 시도해주세요.",
            retry_allowed=True,
        )
    except Exception as e:
        logger.exception("Intent LLM 호출 실패")
        return _error_envelope_response(
            status_code=status.HTTP_502_BAD_GATEWAY,
            code="E-LLM-001",
            message=f"Intent LLM call failed: {e}",
            user_message="AI 응답이 늦어져서 멈췄어요. 다시 시도해주세요.",
            retry_allowed=True,
        )

    if not intent_result.get("intent_ok", False):
        reason = intent_result.get("reason", "영상기획 외 요청")
        logger.info("Intent 차단: %s", reason)
        return _error_envelope_response(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            code="INV-001",
            message=f"Intent blocked: {reason}",
            user_message="영상기획과 거리가 있는 내용 같아요. 다른 방식으로 도와드릴까요?",
            retry_allowed=False,
        )

    # 2. RAG (graceful) ──────────────────────────────────────────────
    if req.use_rag:
        try:
            rag_result = run_rag_retrieval(user_input)
        except Exception as e:  # pragma: no cover — retriever swallow하지만 방어
            logger.warning("RAG retriever raised unexpectedly: %s", e)
            rag_result = RetrievalResult(
                references=[], used_fallback=True, fallback_reason="pgvector_unreachable",
            )
    else:
        rag_result = RetrievalResult(
            references=[], used_fallback=True, fallback_reason=None,
        )

    rag_refs = list(rag_result.references)

    # 3. 3-plan parallel (★ multi-model 인터페이스) ────────────────────
    try:
        planning_results = await run_planning_parallel_3(
            user_input,
            rag_context=rag_refs,
            # models=None → settings.openai_models_for_3plan_list 사용.
            # 향후 req에 models 파라미터 추가 시 여기서 주입 (Phase 21+).
        )
    except Exception as e:
        logger.exception("Planning parallel 3 호출 실패")
        return _error_envelope_response(
            status_code=status.HTTP_502_BAD_GATEWAY,
            code="E-LLM-001",
            message=f"Planning parallel call failed: {e}",
            user_message="AI 응답이 늦어져서 멈췄어요. 다시 시도해주세요.",
            retry_allowed=True,
        )

    # 4. plan dict → Pydantic Plan × 3 ────────────────────────────────
    plans_list: list[Plan] = []
    rag_used_payload = [
        {
            "source_id": r.source_id,
            "title": r.title,
            "used_reason": r.used_reason,
        }
        for r in rag_refs
    ]
    for i, planning_dict in enumerate(planning_results):
        plan_raw = planning_dict.get("plan", {}) if isinstance(planning_dict, dict) else {}
        try:
            p = Plan(
                plan_id=str(uuid4()),
                option_index=i,
                name=(plan_raw.get("name") or f"(생성 {i + 1})")[:20],
                concept=plan_raw.get("concept") or "(콘셉트 없음)",
                hook=plan_raw.get("hook") or "후크 미생성 (재시도 권장)",
                flow=[
                    PlanFlowBeat(
                        beat_index=b.get("beat_index", j),
                        beat=b.get("beat", "") or "—",
                        duration_sec=int(b.get("duration_sec", 5)),
                        purpose=b.get("purpose", "") or "—",
                    )
                    for j, b in enumerate(plan_raw.get("flow") or [])
                ] or [
                    PlanFlowBeat(beat_index=0, beat="—", duration_sec=1, purpose="—"),
                    PlanFlowBeat(beat_index=1, beat="—", duration_sec=1, purpose="—"),
                ],
                pros=plan_raw.get("pros", ""),
                risks=plan_raw.get("risks", ""),
                approach_label=plan_raw.get("approach_label", "informational"),
                rag_used=rag_used_payload,
            )
            plans_list.append(p)
        except Exception as e:
            logger.warning("plan %d schema fail: %s — skipping this plan", i + 1, e)

    if len(plans_list) == 0:
        return _error_envelope_response(
            status_code=status.HTTP_502_BAD_GATEWAY,
            code="E-LLM-003",
            message="all 3 plans failed schema validation",
            user_message="AI가 형식에 맞지 않게 답했어요. 다시 시도해주세요.",
            retry_allowed=True,
        )

    # 5. Critic + revise loop (Phase 4.5 Slice 2) ────────────────────
    # Plan별로 Critic 평가 → verdict가 'revise' 면 Rewriter(P-008) 호출 → 다시 Critic
    # 최대 critic_max_revise(기본 2) 회 차단. attempt 별 dict 를 revise_history 에 누적.
    critic_evaluation: CriticEvaluation | None = None
    revise_histories: list[list[dict[str, Any]]] | None = None
    recommended_idx: int | None = None  # Phase 4.5 Slice 3 (Z-X3)

    if req.use_critic:
        max_revise = settings.critic_max_revise

        async def _critic_revise_for_plan(
            plan_model: Plan, plan_idx: int,
        ) -> tuple[Plan, dict[str, Any] | None, list[dict[str, Any]]]:
            """Returns (final_plan, final_verdict_dict_or_none, history)."""
            history: list[dict[str, Any]] = []
            current_plan_dict: dict[str, Any] = plan_model.model_dump(mode="json")
            final_verdict_dict: dict[str, Any] | None = None

            for attempt in range(max_revise + 1):
                # critic 호출 (sync 함수 — thread pool 에서 실행하여 다른 plan 과 병렬 가능).
                try:
                    loop = asyncio.get_event_loop()
                    verdict = await loop.run_in_executor(
                        None, run_critic, current_plan_dict,
                    )
                except Exception as exc:
                    logger.warning(
                        "Critic call failed plan_idx=%d attempt=%d: %s — graceful skip",
                        plan_idx, attempt, exc,
                    )
                    history.append({
                        "attempt": attempt,
                        "action": "approve",
                        "revised": False,
                        "critic_warning": f"critic_failed: {exc.__class__.__name__}",
                    })
                    break

                final_verdict_dict = verdict
                action = str(verdict.get("overall_verdict") or "").lower()
                entry: dict[str, Any] = {
                    "attempt": attempt,
                    "action": action or "unknown",
                    "revised": False,
                }
                history.append(entry)

                if action != "revise":
                    break  # approve / reject / unknown → loop 종료
                if attempt >= max_revise:
                    entry["max_reached"] = True
                    break  # max 도달 — revise 시도하지 않음

                # revise 실행 (Rewriter — async).
                try:
                    revised_plan_dict = await run_rewriter(current_plan_dict, verdict)
                    current_plan_dict = revised_plan_dict
                    entry["revised"] = True
                except Exception as exc:  # pragma: no cover — run_rewriter 가 graceful 처리
                    logger.warning(
                        "Rewriter raised unexpectedly plan_idx=%d attempt=%d: %s",
                        plan_idx, attempt, exc,
                    )
                    entry["revised"] = False
                    entry["rewriter_warning"] = f"rewriter_raised: {exc.__class__.__name__}"
                    break

            # Plan 모델 재구성 — rewriter가 dict 를 반환하므로 schema 재검증.
            try:
                final_plan = Plan(
                    plan_id=str(current_plan_dict.get("plan_id") or plan_model.plan_id),
                    option_index=int(current_plan_dict.get("option_index", plan_model.option_index)),
                    name=(str(current_plan_dict.get("name") or plan_model.name))[:20],
                    concept=str(current_plan_dict.get("concept") or plan_model.concept),
                    hook=str(current_plan_dict.get("hook") or plan_model.hook),
                    flow=[
                        PlanFlowBeat(
                            beat_index=int(b.get("beat_index", j)),
                            beat=str(b.get("beat", "") or "—"),
                            duration_sec=int(b.get("duration_sec", 5)),
                            purpose=str(b.get("purpose", "") or "—"),
                        )
                        for j, b in enumerate(current_plan_dict.get("flow") or [])
                    ] or list(plan_model.flow),
                    pros=str(current_plan_dict.get("pros") or plan_model.pros or ""),
                    risks=str(current_plan_dict.get("risks") or plan_model.risks or ""),
                    approach_label=current_plan_dict.get("approach_label") or plan_model.approach_label,
                    rag_used=current_plan_dict.get("rag_used") or list(plan_model.rag_used),
                )
            except Exception as exc:
                logger.warning(
                    "Plan re-schema after revise failed plan_idx=%d: %s — using original",
                    plan_idx, exc,
                )
                final_plan = plan_model
            return final_plan, final_verdict_dict, history

        # 모든 plan 에 대해 parallel 실행 (asyncio.gather — Planning parallel 패턴과 동일).
        try:
            results = await asyncio.gather(
                *(_critic_revise_for_plan(p, i) for i, p in enumerate(plans_list)),
                return_exceptions=False,
            )
            plans_list = [r[0] for r in results]
            revise_histories = [r[2] for r in results]
            # Phase 4.5 Slice 3 (Z-X3): plan 별 final verdict 누적 → best-plan idx.
            final_verdicts = [r[1] for r in results if r[1] is not None]
            if final_verdicts:
                try:
                    # `results` 순서 == `plans_list` 순서 보장 (asyncio.gather 정렬).
                    # None verdict (graceful skip) 가 섞인 경우 select_best_plan_index 의
                    # _score 가 None 반환하므로 안전. 원본 순서 보존을 위해 full list 전달.
                    recommended_idx = select_best_plan_index([r[1] for r in results])
                except Exception as e:
                    logger.warning(
                        "select_best_plan_index failed: %s — graceful skip", e,
                    )
                    recommended_idx = None
            # 대표 verdict — 첫 plan 의 마지막 verdict (output_schema 호환 유지).
            first_verdict = results[0][1] if results else None
            if first_verdict is not None:
                try:
                    critic_evaluation = CriticEvaluation(**first_verdict)
                except Exception as e:
                    logger.warning(
                        "CriticEvaluation schema fail: %s — graceful skip", e,
                    )
                    critic_evaluation = None
        except Exception as e:
            logger.warning("Critic+revise loop unexpectedly failed: %s — graceful skip", e)
            critic_evaluation = None
            revise_histories = None
            recommended_idx = None

    # 6. DB save (graceful) ──────────────────────────────────────────
    request_id = str(uuid4())
    rag_refs_serialized = [r.model_dump(mode="json") for r in rag_refs]
    try:
        persistence = save_video_planning(
            request_id=request_id,
            input_text=user_input,
            locale=locale,
            plan_dict=plans_list[0].model_dump(mode="json"),
            critic_dict=critic_evaluation.model_dump(mode="json") if critic_evaluation else None,
            rag_refs=rag_refs_serialized,
        )
    except Exception as e:  # pragma: no cover — save_video_planning이 graceful 흡수
        logger.warning("save_video_planning raised unexpectedly: %s", e)
        from ..db.types import PersistenceResult

        persistence = PersistenceResult(
            status="failed_db_error",
            project_id=None,
            plan_candidate_ids=[],
            error_reason="unexpected_exception",
        )

    db_check_status = "ok" if persistence.status == "saved" else "warn"
    db_check_detail = (
        f"status={persistence.status}, project_id={persistence.project_id}"
        + (f", reason={persistence.error_reason}" if persistence.error_reason else "")
    )

    # 7. Envelope 조립 ───────────────────────────────────────────────
    has_revise_loop_engaged = (
        req.use_critic
        and revise_histories is not None
        and any(h for h in revise_histories)
    )
    warnings = compute_validation_warnings_phase4(
        plans_count=len(plans_list),
        rag_used_fallback=rag_result.used_fallback,
        critic_present=critic_evaluation is not None,
        has_revise_loop=has_revise_loop_engaged,  # Phase 4.5 Slice 2: revise loop 동작 여부
    )

    models_list = settings.openai_models_for_3plan_list
    rag_check_status = "ok" if not rag_result.used_fallback else "warn"
    rag_check_detail = (
        f"references={len(rag_refs)}, fallback={rag_result.used_fallback}"
        + (f", reason={rag_result.fallback_reason}" if rag_result.fallback_reason else "")
    )

    envelope = Envelope(
        meta=Meta.make(
            prompt_id=PARALLEL_3_PROMPT_ID,
            prompt_version=PARALLEL_3_PROMPT_VERSION,
            model=models_list[0],  # 대표 모델 (multi-model 정보는 validation.checks에 상세 노출)
            locale=locale,
            request_id=request_id,
            project_id=persistence.project_id,
        ),
        body=Body(
            plan_candidates=plans_list,
            critic_evaluation=critic_evaluation,
            rag_references=rag_refs,
            revise_history=revise_histories,  # Phase 4.5 Slice 2
            recommended_plan_index=recommended_idx,  # Phase 4.5 Slice 3 (Z-X3)
        ),
        validation=Validation(
            passed=True,
            checks=[
                ValidationCheck(name="schema_envelope", status="ok"),
                ValidationCheck(
                    name="intent_filter",
                    status="ok",
                    detail=f"{INTENT_PROMPT_ID}@{INTENT_PROMPT_VERSION}",
                ),
                ValidationCheck(
                    name="rag_retrieval",
                    status=rag_check_status,
                    detail=rag_check_detail,
                ),
                ValidationCheck(
                    name="plan_count",
                    status="ok" if len(plans_list) == 3 else "warn",
                    detail=f"{len(plans_list)} plans (Phase 4 target: 3)",
                ),
                ValidationCheck(
                    name="critic_evaluation",
                    status="ok" if critic_evaluation else "warn",
                    detail=(
                        f"{CRITIC_PROMPT_ID}@{CRITIC_PROMPT_VERSION}"
                        if critic_evaluation
                        else "skipped or failed"
                    ),
                ),
                ValidationCheck(
                    name="db_persistence",
                    status=db_check_status,
                    detail=db_check_detail,
                ),
                ValidationCheck(
                    name="multi_model",
                    status="ok",
                    detail=f"models={models_list}",
                ),
            ],
            warnings=warnings,
        ),
    )

    # plan_store 저장 (GET /plans/{plan_id} 에서 envelope 반환).
    plan_entry["status"] = "generated"
    plan_entry["envelope"] = envelope.model_dump(mode="json")
    plan_entry["updated_at"] = _now_iso()

    logger.info(
        "plans/generate ok plan_id=%s plans=%d verdict=%s rag_refs=%d db_status=%s",
        plan_id,
        len(plans_list),
        critic_evaluation.overall_verdict if critic_evaluation else "skipped",
        len(rag_refs),
        persistence.status,
    )
    return envelope


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
