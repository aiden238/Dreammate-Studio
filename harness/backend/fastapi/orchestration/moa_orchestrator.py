"""Phase 8 — MOA Orchestrator (ADR-027).

`routers/plans.py::plans_generate()` 약 400줄 god-function 본문을
**behavior-preserving** 이관한 service layer.
moa_policy §2 "agent 간 직접 호출 금지. 오케스트레이터(backend service layer)가
항상 중개한다" 정합.

핵심 원칙 (★ 절대 — ADR-027 Constraints):
  - Envelope byte-identical (meta / body / validation 조립 순서·필드·
    validation.checks 7개 순서·warnings 병합 순서 100% 보존).
  - 에러 코드(E-LLM-001/002/003, INV-001/006) + graceful skip(Critic/Rewriter/RAG/DB)
    분기 100% 보존.
  - pure move only — 로직 변경 0, 위치만 이동.
  - NullProgressSink default → emit no-op → 회귀 0.

★ monkeypatch 보존 (behavior-preserving 게이트):
  기존 pytest fixtures 는 `backend.fastapi.routers.plans.run_intent` 등
  router 모듈 namespace 의 심볼을 monkeypatch 한다. 따라서 orchestrator 는
  agent 호출을 `routers.plans` 모듈 attribute 로 **call-time 해석**하여
  monkeypatch 를 honor 한다 (직접 import 한 이름은 patch 가 닿지 않음).
  → 순환 import 회피 위해 함수 내부 late import.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any
from uuid import uuid4

from fastapi import status
from fastapi.responses import JSONResponse

from ..agents.critic import (
    PROMPT_ID as CRITIC_PROMPT_ID,
    PROMPT_VERSION as CRITIC_PROMPT_VERSION,
    normalize_to_canonical,
)
from ..agents.intent import (
    PROMPT_ID as INTENT_PROMPT_ID,
    PROMPT_VERSION as INTENT_PROMPT_VERSION,
)
from ..agents.planning import (
    PARALLEL_3_PROMPT_ID,
    PARALLEL_3_PROMPT_VERSION,
)
from ..config import effective_output_mode, get_settings
from ..rag import RetrievalResult
from ..schemas.output import (
    Body,
    CriticEvaluation,
    Envelope,
    Meta,
    Plan,
    PlanFlowBeat,
    Validation,
    ValidationCheck,
    compute_validation_warnings_phase4,
)
from ..schemas.plans import GenerateRequest
from .progress_sink import NullProgressSink, ProgressSink
from .responses import error_envelope_response, now_iso

logger = logging.getLogger(__name__)


# ─── Phase 14 S1: 위저드 입력 조립 (additive, behavior-preserving) ────
# 위저드(/new/quick·/new/discovery)가 누적한 wizard_data(step별 WizardStepRequest dump)를
# 단일 user_input 문자열로 조립한다. ★ 랜딩 `/` 는 initial_input 을 채우므로 이 경로를 타지
# 않는다(byte-identical). generate 입력 우선순위: initial_input > wizard_data 조립 > "(빈 입력)".
_WIZARD_STEP_ORDER: tuple[str, ...] = (
    "step1", "step2", "step3", "step4", "step5", "step6", "step7",
    "quick.initial", "quick.clarify", "quick.direction",
)


def build_user_input_from_wizard(wizard_data: dict[str, Any] | None) -> str:
    """wizard_data(step→{selected_card_id?, user_input?, extra}) → user_input 문자열.

    Phase 14 S1 (additive): 위저드가 백엔드에 누적한 step 입력을 결정적 순서로 조립한다.
    known step(step1~7 / quick.*) 먼저, 그 외 step 은 사전순. 각 step 에서 selected_card_id /
    user_input / extra(비어있지 않은 값)를 모아 한 줄로, step 사이는 개행. 의미있는 입력이
    없으면 "" 반환(호출자가 "(빈 입력)" 폴백 유지).

    ★ behavior-preserving: 본 함수는 신설이며 initial_input 이 없을 때만 호출된다 →
      랜딩 경로(initial_input 채움)는 영향 0.
    """
    if not wizard_data:
        return ""
    ordered = [k for k in _WIZARD_STEP_ORDER if k in wizard_data]
    ordered += sorted(k for k in wizard_data if k not in _WIZARD_STEP_ORDER)

    lines: list[str] = []
    for key in ordered:
        step = wizard_data.get(key)
        if not isinstance(step, dict):
            continue
        seg: list[str] = []
        card = step.get("selected_card_id")
        if card:
            seg.append(str(card))
        ui = step.get("user_input")
        if ui:
            seg.append(str(ui))
        extra = step.get("extra")
        if isinstance(extra, dict):
            for ek, ev in extra.items():
                if ev not in (None, "", [], {}):
                    seg.append(f"{ek}: {ev}")
        if seg:
            lines.append(" / ".join(seg))
    return "\n".join(lines).strip()


async def generate_plan(
    plan_id: str,
    plan_entry: dict[str, Any],
    req: GenerateRequest,
    *,
    progress: ProgressSink = NullProgressSink(),
    auth_user_id: str | None = None,
    brand_id: str | None = None,
) -> Envelope | JSONResponse:
    """MOA orchestration — Intent → RAG → 3-plan parallel → Critic+revise → DB save → Envelope.

    `plans_generate()` body(line 230~632) 를 그대로 이관 (behavior-preserving).
    plan_entry 는 호출자(thin adapter)가 _plan_store 에서 조회해 전달하며,
    본 함수가 끝에서 plan_entry dict 를 mutation (status="generated" + envelope).

    Phase 17 가-S1 (신원 plumbing only — 주입 X):
        - auth_user_id / brand_id 는 라우터(auth_middleware request.state.user)에서 흘러온
          **선택적** 신원이다. 본 슬라이스는 신원을 함수 내부에서 **관측 가능**하게만 만든다
          (로깅 + plan_entry 에 stash) — brand_memory 로드/주입은 가-S2 영역.
        - ★ behavior-preserving: 신원 미존재(익명, None) 경로는 기존과 byte-identical.
          신원이 있어도 Envelope/프롬프트/LLM 호출/DB 저장 인자는 전혀 변하지 않는다
          (로깅·stash 만 부수효과 — 응답 schema·출력 0 변경).

    Returns:
        성공 시 Envelope (router 가 그대로 200 응답), 에러 시 JSONResponse(ErrorEnvelope).
    """
    # ★ monkeypatch 보존 — agent 함수를 routers.plans 모듈 namespace 로 call-time 해석.
    #   (기존 fixtures 가 backend.fastapi.routers.plans.run_* 를 patch — honor 필수)
    from ..routers import plans as plans_router

    settings = get_settings()

    # Phase 17 가-S1 (신원 관측 — 주입 0): 신원이 orchestrator 까지 도달했음을 로깅하고
    #   plan_entry 에 stash 한다 (가-S2 의 brand_memory 로드가 여기서 읽는다). 익명(None)은
    #   "anon" 으로 로깅되며 동작/출력에 영향 0. ★ 신원→brand_memory 구속 주입 hook 지점.
    plan_entry["auth_user_id"] = auth_user_id  # stash (가-S2 read 지점)
    plan_entry["brand_id"] = brand_id
    logger.info(
        "generate_plan identity plan_id=%s auth_user_id=%s brand_id=%s",
        plan_id,
        auth_user_id or "anon",
        brand_id or "none",
    )
    # Phase 14 S1 (additive): initial_input(랜딩 `/` — byte-identical) 우선,
    #   없으면 위저드 누적 입력(wizard_data) 조립, 그래도 없으면 기존 폴백.
    user_input = (
        plan_entry.get("initial_input")
        or build_user_input_from_wizard(plan_entry.get("wizard_data"))
        or "(빈 입력)"
    )
    locale = plan_entry.get("locale", "ko-KR")

    # 1. Intent ──────────────────────────────────────────────────────
    progress.emit("intent", step=1, message="의도 분석 중...")
    try:
        intent_result = plans_router.run_intent(user_input)
    except ValueError as e:
        logger.warning("Intent LLM JSON 파싱 실패: %s", e)
        return error_envelope_response(
            status_code=status.HTTP_502_BAD_GATEWAY,
            code="E-LLM-002",
            message=f"Intent LLM response parse failed: {e}",
            user_message="AI 응답을 정리하는 중 문제가 생겼어요. 다시 시도해주세요.",
            retry_allowed=True,
        )
    except Exception as e:
        logger.exception("Intent LLM 호출 실패")
        return error_envelope_response(
            status_code=status.HTTP_502_BAD_GATEWAY,
            code="E-LLM-001",
            message=f"Intent LLM call failed: {e}",
            user_message="AI 응답이 늦어져서 멈췄어요. 다시 시도해주세요.",
            retry_allowed=True,
        )

    if not intent_result.get("intent_ok", False):
        reason = intent_result.get("reason", "영상기획 외 요청")
        logger.info("Intent 차단: %s", reason)
        return error_envelope_response(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            code="INV-001",
            message=f"Intent blocked: {reason}",
            # Phase 16: 재작성 가이드(구체 예시) — 하드 차단이 아니라 안내 (generate.py 와 동일).
            user_message=(
                "영상기획과 거리가 있는 내용 같아요. 만들 영상의 주제를 적어보세요 — "
                "예: '대학생활 꿀팁 30초 쇼츠', '자취 요리 브이로그', '재테크 기초 정보형 영상'."
            ),
            retry_allowed=False,
        )

    # 2. RAG (graceful) ──────────────────────────────────────────────
    # Phase 1 baseline (preserved): pgvector psycopg retriever.
    # Phase 7 Slice 4 (additive): agents/rag.py `run_rag` graceful marker 통합.
    #   - Phase 1 `run_rag_retrieval` 결과 우선 (회귀 0 보장).
    #   - Phase 7 marker는 validation.warnings에 추가 (ADR-025 §5 5종).
    progress.emit("rag", step=2, message="지식 검색 중...")
    if req.use_rag:
        try:
            rag_result = plans_router.run_rag_retrieval(user_input)
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

    # Phase 7 Slice 4: RAG Lite marker 수집 (Supabase RPC pattern, graceful).
    # 실패해도 plan 생성 차단 X — warnings에 추가만 (ADR-025 §5).
    phase7_rag_warnings: list[str] = []
    if req.use_rag:
        try:
            from ..agents.rag import run_rag as run_rag_lite

            rag_lite_result = await run_rag_lite(user_input)
            phase7_rag_warnings = list(rag_lite_result.get("rag_warnings", []))
        except Exception as exc:  # pragma: no cover — graceful 흡수
            logger.warning(
                "phase_7_rag_lite raised: %s (graceful)",
                exc.__class__.__name__,
            )
            phase7_rag_warnings = [
                f"rag_unavailable: {exc.__class__.__name__}"
            ]

    # 3. 3-plan parallel (★ multi-model 인터페이스) ────────────────────
    progress.emit("planning", step=3, message="영상기획안 3개 생성 중...")
    try:
        if settings.multi_provider_plans_enabled:
            # B안(§18.B): 3안을 3-provider(GPT/Claude/Gemini) alias 로 다양화 (★ gated, default OFF).
            #   flag OFF 시 아래 else 의 기존 OpenAI 3-call 경로와 100% 동일(behavior-preserving).
            #   다중-provider 증거는 run_planning_multi_provider_3 의 슬롯별 로깅으로 관측.
            planning_results = await plans_router.run_planning_multi_provider_3(
                user_input,
                rag_context=rag_refs,
            )
        else:
            planning_results = await plans_router.run_planning_parallel_3(
                user_input,
                rag_context=rag_refs,
                # models=None → settings.openai_models_for_3plan_list 사용.
                # 향후 req에 models 파라미터 추가 시 여기서 주입 (Phase 21+).
            )
    except Exception as e:
        logger.exception("Planning parallel 3 호출 실패")
        return error_envelope_response(
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
                        # Phase 13 S3 (additive rich read — OFF 경로엔 키 없어 None).
                        visual=b.get("visual"),
                        dialogue=b.get("dialogue"),
                        caption=b.get("caption"),
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
                # Phase 13 S3 (additive rich read): rich 프롬프트(ON) 응답에만 채워지고,
                # OFF 경로는 키 부재 → default(None/[]). 직렬화 분기가 OFF 면 제외.
                hook_variants=plan_raw.get("hook_variants", []),
                target_audience=plan_raw.get("target_audience"),
                tone=plan_raw.get("tone"),
                shots=plan_raw.get("shots", []),
                thumbnail=plan_raw.get("thumbnail"),
                title_candidates=plan_raw.get("title_candidates", []),
                cta=plan_raw.get("cta"),
                references=plan_raw.get("references", []),
                length_variants=plan_raw.get("length_variants", []),
                # Phase 15 S6 (director read): output_mode=director 응답에만 채워짐. scene graceful.
                hook_system=plan_raw.get("hook_system", []),
                retention_architecture=plan_raw.get("retention_architecture"),
                scene_breakdown=[
                    {
                        "scene_intent": s.get("scene_intent") or "(미상)",
                        "viewer_emotion": s.get("viewer_emotion") or "(미상)",
                        "retention_device": s.get("retention_device") or "(미상)",
                        "why_this_works": s.get("why_this_works") or "(미상)",
                        "fallback_scene": s.get("fallback_scene"),
                    }
                    for s in (plan_raw.get("scene_breakdown") or [])
                    if isinstance(s, dict)
                ],
            )
            plans_list.append(p)
        except Exception as e:
            logger.warning("plan %d schema fail: %s — skipping this plan", i + 1, e)

    if len(plans_list) == 0:
        return error_envelope_response(
            status_code=status.HTTP_502_BAD_GATEWAY,
            code="E-LLM-003",
            message="all 3 plans failed schema validation",
            user_message="AI가 형식에 맞지 않게 답했어요. 다시 시도해주세요.",
            retry_allowed=True,
        )

    # 5. Critic + revise loop (Phase 4.5 Slice 2) ────────────────────
    # Plan별로 Critic 평가 → verdict가 'revise' 면 Rewriter(P-008) 호출 → 다시 Critic
    # 최대 critic_max_revise(기본 2) 회 차단. attempt 별 dict 를 revise_history 에 누적.
    progress.emit("critic", step=4, message="Critic 검증 중...")
    critic_evaluation: CriticEvaluation | None = None
    revise_histories: list[list[dict[str, Any]]] | None = None
    recommended_idx: int | None = None  # Phase 4.5 Slice 3 (Z-X3)
    # Phase 11 A안 Slice 3 (cross-validation hook): plan 별 critic canonical verdict
    #   누적 — recommended plan 의 canonical(overall_score + dimensions) 추출용.
    #   ★ additive: 기존 흐름/Envelope 무영향 (cross-validation 게이트 OFF 시 미사용).
    per_plan_verdicts: list[dict[str, Any] | None] | None = None

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
                # Phase 9 Slice 3 (ADR-032): run_critic 결과를 normalize_to_canonical 로 감싸
                #   critic_evaluation 에 canonical(overall_score 0–1 + dimensions) 추가.
                #   helper 는 비파괴 사본 — deprecated 0–5(scores / overall_score_avg) 병행 유지 (NG3, 회귀 0).
                try:
                    loop = asyncio.get_event_loop()
                    raw_verdict = await loop.run_in_executor(
                        None, plans_router.run_critic, current_plan_dict,
                    )
                    verdict = normalize_to_canonical(raw_verdict)
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
                    revised_plan_dict = await plans_router.run_rewriter(current_plan_dict, verdict)
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
                            # Phase 13 S3 (rich 보존): revise 왕복 dict 에서 rich 슬롯 유지.
                            visual=b.get("visual"),
                            dialogue=b.get("dialogue"),
                            caption=b.get("caption"),
                        )
                        for j, b in enumerate(current_plan_dict.get("flow") or [])
                    ] or list(plan_model.flow),
                    pros=str(current_plan_dict.get("pros") or plan_model.pros or ""),
                    risks=str(current_plan_dict.get("risks") or plan_model.risks or ""),
                    approach_label=current_plan_dict.get("approach_label") or plan_model.approach_label,
                    rag_used=current_plan_dict.get("rag_used") or list(plan_model.rag_used),
                    # Phase 13 S3 (rich 보존): rewriter dict 에 rich 슬롯이 있으면 유지,
                    # 없으면 원본 plan_model 의 rich 값으로 fallback (revise 왕복 유실 방지).
                    hook_variants=current_plan_dict.get("hook_variants") or list(plan_model.hook_variants),
                    target_audience=current_plan_dict.get("target_audience") or plan_model.target_audience,
                    tone=current_plan_dict.get("tone") or plan_model.tone,
                    shots=current_plan_dict.get("shots") or list(plan_model.shots),
                    thumbnail=current_plan_dict.get("thumbnail") or plan_model.thumbnail,
                    title_candidates=current_plan_dict.get("title_candidates") or list(plan_model.title_candidates),
                    cta=current_plan_dict.get("cta") or plan_model.cta,
                    references=current_plan_dict.get("references") or list(plan_model.references),
                    length_variants=current_plan_dict.get("length_variants") or list(plan_model.length_variants),
                    # Phase 15 S6 (director 보존): rewriter dict 에 없으면 원본 plan_model director 값 fallback.
                    hook_system=current_plan_dict.get("hook_system") or list(plan_model.hook_system),
                    retention_architecture=current_plan_dict.get("retention_architecture") or plan_model.retention_architecture,
                    scene_breakdown=current_plan_dict.get("scene_breakdown") or list(plan_model.scene_breakdown),
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
            # Phase 11 A안 Slice 3 (cross-validation hook): plan 별 canonical verdict
            #   누적 (plans_list 와 동일 순서). recommended plan 의 canonical 추출에 사용.
            #   ★ additive — Envelope 무영향.
            per_plan_verdicts = [r[1] for r in results]
            # Phase 4.5 Slice 3 (Z-X3): plan 별 final verdict 누적 → best-plan idx.
            final_verdicts = [r[1] for r in results if r[1] is not None]
            if final_verdicts:
                try:
                    # `results` 순서 == `plans_list` 순서 보장 (asyncio.gather 정렬).
                    # None verdict (graceful skip) 가 섞인 경우 select_best_plan_index 의
                    # _score 가 None 반환하므로 안전. 원본 순서 보존을 위해 full list 전달.
                    recommended_idx = plans_router.select_best_plan_index([r[1] for r in results])
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

    # 5.5 Cross-validation hook (Phase 11 A안 Slice 3 — ★ gated default-off, additive) ─
    # recommended/best plan 이 정해진 직후(Envelope 조립 전), Gemini 독립 교차검증을
    # 1회 수행하여 OpenAI Critic 평가와 비교한다 (single-model self-bias 완화).
    # ★★ behavior-preserving:
    #   - settings.cross_validation_enabled(default False) → 아무 동작 안 함(기존 경로 100% 동일).
    #   - 결과는 **로깅(관측성)만** — Envelope/output_schema/응답 필드 0 변경.
    #     (응답 노출은 후속 phase + output_schema contract-change 대상.)
    #   - 모든 예외/실패는 graceful 흡수 → 기존 흐름 절대 차단 X.
    if settings.cross_validation_enabled:
        try:
            # late import — 순환 회피 + 테스트 monkeypatch 용이.
            from ..llm.cross_validation import compare, cross_validate

            # recommended plan = best-plan idx(없으면 대표 0). plans_list/per_plan_verdicts
            #   는 동일 순서 보장 (asyncio.gather 정렬).
            rec_idx = recommended_idx if recommended_idx is not None else 0
            rec_plan = plans_list[rec_idx] if 0 <= rec_idx < len(plans_list) else plans_list[0]
            rec_plan_text = rec_plan.model_dump_json()
            rec_critic_canonical: dict[str, Any] = {}
            if per_plan_verdicts is not None and 0 <= rec_idx < len(per_plan_verdicts):
                rec_critic_canonical = per_plan_verdicts[rec_idx] or {}

            cross = cross_validate(rec_plan_text)
            cmp = compare(rec_critic_canonical, cross)
            logger.info(
                "cross_validation: model=%s gemini=%s openai=%s agreement=%s -> %s",
                cross.model_id,
                cmp.get("gemini_score"),
                cmp.get("openai_score"),
                cmp.get("agreement"),
                cmp.get("recommendation"),
            )
        except Exception:
            logger.exception("cross_validation hook 실패 (graceful — 응답 무영향)")

    # 6. DB save (graceful) ──────────────────────────────────────────
    request_id = str(uuid4())
    rag_refs_serialized = [r.model_dump(mode="json") for r in rag_refs]
    try:
        persistence = plans_router.save_video_planning(
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
    # Phase 7 Slice 4: RAG Lite graceful marker (ADR-025 §5) 통합.
    # 중복 방지 — Phase 4 baseline에 동일 marker 없을 때만 추가.
    for marker in phase7_rag_warnings:
        if marker not in warnings:
            warnings.append(marker)

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
    # Phase 15 S3 (gated 직렬화 분기): output_mode 별 (compact: rich+director 제외 byte-identical /
    #   rich: director 제외 / director: 전부). plans_list 는 최종 plan 리스트 (Critic+revise 반영).
    from ..schemas.output import envelope_to_response_dict

    response_payload = envelope_to_response_dict(
        envelope, plans_list, output_mode=effective_output_mode(settings),
    )
    plan_entry["status"] = "generated"
    plan_entry["envelope"] = response_payload  # GET /plans/{plan_id} read 와 동일 직렬화.
    plan_entry["updated_at"] = now_iso()

    logger.info(
        "plans/generate ok plan_id=%s plans=%d verdict=%s rag_refs=%d db_status=%s",
        plan_id,
        len(plans_list),
        critic_evaluation.overall_verdict if critic_evaluation else "skipped",
        len(rag_refs),
        persistence.status,
    )
    progress.emit("complete", step=4, message="완료")
    return envelope
