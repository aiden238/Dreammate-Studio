"""POST /api/v1/generate — Phase 1 Slice 5.

Phase 1 deviation from api_contract.md §8.3:
  - Contract: POST /api/v1/plans/{plan_id}/generate (async + SSE, 3 plans)
  - Slice 1~5: POST /api/v1/generate (sync, 1 plan)
  - Reason: Simplest Slice 원칙 (phase-start v1.1.0 §6.2)
  - Migration: Phase 4 MOA Lite 완성 시 contract endpoint로 정합

Slice 2 변경:
  - Intent + Planning 분리 (직렬 2회 호출)
  - INV-001 (Intent 차단) → ErrorEnvelope 정식 응답 (HTTP 422)

Slice 3 변경:
  - Critic 추가 (직렬 3회 호출: Intent → Planning → Critic)
  - body.critic_evaluation 활성화 (revise 없음, 평가만)
  - validation.warnings에서 "phase_1_no_critic" 제거

Slice 4 변경:
  - RAG Lite 추가 (Intent 통과 후 → RAG 검색 → Planning에 rag_context 주입)
  - pgvector 미가용 시 graceful fallback (절대 사용자 차단 금지)
  - body.rag_references 활성화 (fallback 시 빈 배열)
  - plan.rag_used 채움 (실제 prompt에 주입된 references)
  - validation.checks에 rag_retrieval 추가 (status=ok|warn)
  - validation.warnings에서 "phase_1_no_rag" 제거

Slice 5 변경:
  - Critic 후 Supabase 저장 단계 추가 (video_projects + plan_candidates).
  - DB 실패는 절대 사용자 차단 금지 (graceful 정책 — RAG와 동일).
  - meta.project_id 노출 (성공 시 uuid, skip/fail 시 None).
  - validation.checks에 db_persistence 추가 (status=ok|warn).
  - 익명 저장 (user_id=NULL) — Phase 5 Auth 도입 시 사용자 binding.

Phase 4 Slice 1 변경 (이번):
  - X-API-Deprecation 응답 header 추가 (실 동작 / body / status 무변경).
  - ADR-014 채택: Phase 1 endpoint Phase 8+ 제거 (마이그 완료 후, 사용자 결정 5-a).
  - 새 contract endpoint: POST /api/v1/plans/{plan_id}/generate (Slice 2에서 본격).
"""

from __future__ import annotations

import logging
from typing import Union
from uuid import uuid4

from fastapi import APIRouter, Response, status
from fastapi.responses import JSONResponse

from ..agents.critic import (
    PROMPT_ID as CRITIC_PROMPT_ID,
    PROMPT_VERSION as CRITIC_PROMPT_VERSION,
    normalize_to_canonical,
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
from ..config import effective_output_mode, get_settings
from ..db import save_video_planning
from ..rag import RetrievalResult, run_rag_retrieval
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


# Phase 4 Slice 1: ADR-014 채택 — Phase 1 endpoint deprecation 안내.
# 실 동작 / body / status 무변경 — header만 추가 (사용자 결정 5-a, Phase 8+ 제거).
# HTTP header 값은 latin-1만 허용되므로 ASCII로만 작성한다 (em-dash 등 unicode 금지).
_DEPRECATION_HEADER_VALUE = (
    "Phase 4 - use POST /api/v1/plans/{plan_id}/generate"
)


# ─── Helpers ─────────────────────────────────────────────────────────

def _error_response(
    *,
    status_code: int,
    code: str,
    message: str,
    user_message: str,
    retry_allowed: bool = False,
) -> JSONResponse:
    """ErrorEnvelope를 JSONResponse로 변환 (error_response_contract.md §1).

    Phase 4 Slice 1: X-API-Deprecation header 동봉 (success path와 동일하게 안내).
    """
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
        headers={"X-API-Deprecation": _DEPRECATION_HEADER_VALUE},
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
    summary="영상기획 1개 생성 + RAG + Critic 평가 + Supabase 저장 (Phase 1 Slice 5)",
    description=(
        "Phase 1 Slice 5 — Intent → RAG → Planning(rag_context) → Critic → DB save 직렬 호출.\n"
        "RAG는 pgvector 미가용 시 graceful fallback (빈 references, 200 응답 유지).\n"
        "Critic은 8 차원 평가만 수행 (revise 없음, Phase 4+).\n"
        "DB 저장은 Supabase 미설정/실패 시 graceful skip (meta.project_id=null, 200 응답 유지).\n"
        "Phase 4에서 api_contract.md §8.3 (async + SSE) 형식으로 migration 예정.\n"
        "Intent 차단 시 INV-001 ErrorEnvelope 반환."
    ),
)
def generate(req: GenerateRequest, response: Response) -> Union[Envelope, JSONResponse]:
    """Intent → RAG → Planning(rag_context) → Critic 직렬 호출 → envelope 반환.

    Phase 4 Slice 1: X-API-Deprecation header 추가 (success path 동봉).
    Error path는 _error_response()가 동일 header 동봉 (ADR-014).
    """
    # Phase 4 Slice 1: deprecation 안내 — 실 동작 무변경.
    response.headers["X-API-Deprecation"] = _DEPRECATION_HEADER_VALUE

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
            # Phase 16: 차단 시 재작성 가이드(구체 예시) 제공 — 하드 차단이 아니라 안내.
            user_message=(
                "영상기획과 거리가 있는 내용 같아요. 만들 영상의 주제를 적어보세요 — "
                "예: '대학생활 꿀팁 30초 쇼츠', '자취 요리 브이로그', '재테크 기초 정보형 영상'."
            ),
            retry_allowed=False,
        )

    # ── 3a. RAG 검색 (Slice 4) ─────────────────────────────────────────
    # 사용자 요청을 절대 차단하지 않는다 — 모든 실패는 retriever 내부에서
    # fallback으로 흡수되어 RetrievalResult로 반환된다. 그래도 만약을 위해
    # router 측에서도 try/except로 한 번 더 감싼다 (방어 코드).
    try:
        rag_result = run_rag_retrieval(req.input)
    except Exception as e:  # pragma: no cover — retriever가 swallow하지만 방어
        logger.warning("RAG retriever raised unexpectedly, using empty refs: %s", e)
        rag_result = RetrievalResult(
            references=[],
            used_fallback=True,
            fallback_reason="pgvector_unreachable",
        )

    rag_refs = list(rag_result.references)
    rag_check_status = "ok" if not rag_result.used_fallback else "warn"
    rag_check_detail = (
        f"references={len(rag_refs)}, fallback={rag_result.used_fallback}"
        + (f", reason={rag_result.fallback_reason}" if rag_result.fallback_reason else "")
    )

    # ── 3b. Planning Agent (P-006) — Slice 4: rag_context 주입 ────────
    try:
        planning_result = run_planning(req.input, rag_context=rag_refs)
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
                    # Phase 13 S3 (additive rich read — OFF 경로엔 키 없어 None).
                    visual=b.get("visual"),
                    dialogue=b.get("dialogue"),
                    caption=b.get("caption"),
                )
                for i, b in enumerate(plan_raw.get("flow", []))
            ],
            pros=plan_raw.get("pros", ""),
            risks=plan_raw.get("risks", ""),
            approach_label=plan_raw.get("approach_label", "informational"),
            # Slice 4: rag_used는 실제 prompt에 주입된 chunk 요약만 (≤3, contract §5.5).
            # fallback인 경우 빈 배열.
            rag_used=[
                {
                    "source_id": r.source_id,
                    "title": r.title,
                    "used_reason": r.used_reason,
                }
                for r in rag_refs
            ],
            # Phase 13 S3 (additive rich read): rich 프롬프트(ON) 응답에만 채워지고,
            # OFF 경로(compact 프롬프트)는 키 부재 → default(None/[]). 직렬화 분기가
            # OFF 면 model_dump_compact() 로 제외 → byte-identical.
            hook_variants=plan_raw.get("hook_variants", []),
            target_audience=plan_raw.get("target_audience"),
            tone=plan_raw.get("tone"),
            shots=plan_raw.get("shots", []),
            thumbnail=plan_raw.get("thumbnail"),
            title_candidates=plan_raw.get("title_candidates", []),
            cta=plan_raw.get("cta"),
            references=plan_raw.get("references", []),
            length_variants=plan_raw.get("length_variants", []),
            # Phase 15 S6 (director read): director 프롬프트(output_mode=director) 응답에만 채워짐.
            #   다른 모드는 키 부재 → default([]/None). scene 은 graceful(필수 필드 누락 시 placeholder).
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
                for s in plan_raw.get("scene_breakdown", [])
                if isinstance(s, dict)
            ],
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

    # Phase 9.5 Slice 4 (ADR-034): run_critic 0–5 출력을 normalize_to_canonical 로 감싸
    #   canonical(overall_score 0–1 + dimensions) 생성 후 CriticEvaluation 으로 검증.
    #   CriticEvaluation 은 deprecated 0–5 키(scores / overall_score_avg)를 extra='ignore'
    #   로 무시 → canonical 만 노출 (orchestrator moa_orchestrator.py 와 동일 wiring, ADR-032).
    critic_verdict = normalize_to_canonical(critic_result)
    try:
        critic_evaluation = CriticEvaluation(**critic_verdict)
    except Exception as e:
        logger.exception("CriticEvaluation 모델 검증 실패")
        return _error_response(
            status_code=status.HTTP_502_BAD_GATEWAY,
            code="E-LLM-003",
            message=f"Critic schema validation failed: {e}",
            user_message="AI가 형식에 맞지 않게 답했어요. 다시 시도해주세요.",
            retry_allowed=True,
        )

    # ── 6. DB save (Slice 5) — graceful, 실패해도 사용자 차단 금지 ──────
    # request_id 를 먼저 생성하여 Meta + video_projects 양쪽에 동일하게 주입.
    request_id = str(uuid4())

    rag_refs_serialized = [r.model_dump(mode="json") for r in rag_refs]

    try:
        persistence = save_video_planning(
            request_id=request_id,
            input_text=req.input,
            locale=req.locale,
            plan_dict=plan.model_dump(mode="json"),
            critic_dict=critic_evaluation.model_dump(mode="json"),
            rag_refs=rag_refs_serialized,
        )
    except Exception as e:  # pragma: no cover — save_video_planning이 graceful 흡수하지만 방어
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

    # ── 7. Envelope 조립 ──────────────────────────────────────────────
    # meta.prompt_id 는 응답 본문 생성기인 Planning(P-006)을 노출.
    # Intent(P-001) + Critic(P-007) 은 각각 validation check로 별도 기록.
    # Slice 4: rag_references (body 최상위) + rag_retrieval check.
    # Slice 5: meta.project_id (DB 저장 결과) + db_persistence check.
    envelope = Envelope(
        meta=Meta.make(
            prompt_id=PLANNING_PROMPT_ID,
            prompt_version=PLANNING_PROMPT_VERSION,
            model=settings.openai_model_default,
            locale=req.locale,
            request_id=request_id,
            project_id=persistence.project_id,  # None일 수 있음 (skip/fail 시)
        ),
        body=Body(
            plan_candidates=[plan],
            critic_evaluation=critic_evaluation,
            rag_references=rag_refs,
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
                ValidationCheck(name="plan_count", status="ok", detail="1 (Phase 1 deviation)"),
                ValidationCheck(
                    name="rag_retrieval",
                    status=rag_check_status,
                    detail=rag_check_detail,
                ),
                ValidationCheck(
                    name="critic_evaluation",
                    status="ok",
                    detail=f"{CRITIC_PROMPT_ID}@{CRITIC_PROMPT_VERSION}",
                ),
                ValidationCheck(
                    name="db_persistence",
                    status=db_check_status,
                    detail=db_check_detail,
                ),
            ],
            warnings=[
                "phase_1_single_plan",  # 1 vs contract 3 (Phase 4+ 해소)
                # "phase_1_no_rag" — Slice 4에서 해소 (RAG retriever 활성화)
                # "phase_1_no_critic" — Slice 3에서 해소
                # Slice 5는 DB가 graceful이므로 별도 warning 추가하지 않음.
            ],
        ),
    )

    logger.info(
        "generate ok plan_id=%s verdict=%s rag_refs=%d rag_fallback=%s db_status=%s project_id=%s request_id=%s",
        plan.plan_id,
        critic_evaluation.overall_verdict,
        len(rag_refs),
        rag_result.used_fallback,
        persistence.status,
        persistence.project_id,
        envelope.meta.request_id,
    )
    # Phase 15 S3 (gated 직렬화 분기): output_mode 별 직렬화 (compact: rich+director 제외 byte-identical /
    #   rich: director 제외 / director: 전부). ★ 모든 모드를 envelope_to_response_dict 로 통일 →
    #   rich 경로도 director 키 누수 0 (Phase 13 rich byte-identical). deprecation header 보존(status 200).
    from ..schemas.output import envelope_to_response_dict

    payload = envelope_to_response_dict(
        envelope, [plan], output_mode=effective_output_mode(settings)
    )
    return JSONResponse(
        content=payload,
        status_code=200,
        headers={"X-API-Deprecation": _DEPRECATION_HEADER_VALUE},
    )
