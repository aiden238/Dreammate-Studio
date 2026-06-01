"""Phase 11 A안 Slice 3 — cross-validation orchestrator gated 연결 단위 테스트.

`orchestration/moa_orchestrator.py::generate_plan` 의 cross-validation hook 검증:
  - flag OFF (default): cross_validate 호출 0 + 응답 Envelope 동일 (기존 경로 100% 보존)
  - flag ON: cross_validate 호출됨(mock) + Envelope 불변(cross 결과 응답 미혼입) + 로깅 발생
  - graceful: cross_validate 예외/available=False 여도 generate_plan 정상 완료 (차단 0)

★★ behavior-preserving / gated default-off:
  - cross_validation_enabled(default False) → hook 미동작.
  - hook 은 **로깅(관측성)만** — Envelope/output_schema/응답 필드 0 변경 (flag ON 에서도 불변).
  - 전부 mock — 실 LLM 호출 0, 실 키 불필요.

monkeypatch 대상:
  - agent 함수: `backend.fastapi.routers.plans.*` (orchestrator 가 router namespace call-time 해석).
  - cross_validate/compare: `backend.fastapi.llm.cross_validation.*` (orchestrator late-import 경로).
"""

from __future__ import annotations

import copy
import logging
from typing import Any

import pytest

from backend.fastapi.config import get_settings
from backend.fastapi.db.types import PersistenceResult
from backend.fastapi.llm.cross_validation import CrossCheck
from backend.fastapi.orchestration import generate_plan
from backend.fastapi.rag.types import RetrievalResult
from backend.fastapi.schemas.output import Envelope
from backend.fastapi.schemas.plans import GenerateRequest


# ─── helpers ──────────────────────────────────────────────────────────

_INTENT_OK: dict[str, Any] = {"intent_ok": True, "category": "video_planning"}


def _make_plan_entry() -> dict[str, Any]:
    return {
        "plan_id": "test-plan-id",
        "status": "created",
        "created_at": "2026-06-01T00:00:00Z",
        "updated_at": "2026-06-01T00:00:00Z",
        "locale": "ko-KR",
        "initial_input": "유튜브 쇼츠 만들기",
        "wizard_data": {},
        "envelope": None,
    }


def _parallel_3_payload() -> list[dict[str, Any]]:
    labels = ["narrative", "informational", "experiment"]
    out: list[dict[str, Any]] = []
    for i in range(3):
        out.append(
            {
                "plan": {
                    "name": f"기획안 {i + 1}",
                    "concept": f"콘셉트 {i + 1}",
                    "hook": f"후크 {i + 1} — 시청 유지율 검증",
                    "flow": [
                        {"beat_index": 0, "beat": "도입", "duration_sec": 3, "purpose": "관심"},
                        {"beat_index": 1, "beat": "전개", "duration_sec": 20, "purpose": "핵심"},
                        {"beat_index": 2, "beat": "마무리", "duration_sec": 7, "purpose": "CTA"},
                    ],
                    "pros": "장점",
                    "risks": "위험",
                    "approach_label": labels[i],
                }
            }
        )
    return out


def _critic_approve(plan: dict[str, Any], *args: Any, **kwargs: Any) -> dict[str, Any]:
    scores = {
        "intent_fit": 4, "target_clarity": 4, "hook_strength": 4, "message_clarity": 4,
        "structure": 4, "feasibility": 4, "brand_consistency": 5, "differentiation": 4,
    }
    return {
        "target_plan_id": str(plan.get("plan_id") or ""),
        "scores": scores,
        "reasons": {k: "—" for k in scores},
        "suggestions": {k: "—" for k in scores},
        "overall_score_avg": round(sum(scores.values()) / len(scores), 4),
        "overall_verdict": "approve",
        "blocking_issues": [],
        "revise_round": 0,
    }


def _db_save_ok(**kwargs: Any) -> PersistenceResult:
    return PersistenceResult(
        status="saved",
        project_id="fake-project-uuid",
        plan_candidate_ids=["fake-plan-candidate-uuid"],
        error_reason=None,
    )


def _rag_fallback(*args: Any, **kwargs: Any) -> RetrievalResult:
    return RetrievalResult(
        references=[], used_fallback=True, fallback_reason="pgvector_unreachable",
    )


@pytest.fixture
def patch_agents_ok(monkeypatch: pytest.MonkeyPatch) -> None:
    """정상 경로 — Intent allow + RAG fallback + 3-plan + Critic approve + DB save ok."""

    async def fake_parallel(*args: Any, **kwargs: Any) -> list[dict[str, Any]]:
        return copy.deepcopy(_parallel_3_payload())

    monkeypatch.setattr("backend.fastapi.routers.plans.run_intent", lambda *a, **k: dict(_INTENT_OK))
    monkeypatch.setattr("backend.fastapi.routers.plans.run_rag_retrieval", _rag_fallback)
    monkeypatch.setattr("backend.fastapi.routers.plans.run_planning_parallel_3", fake_parallel)
    monkeypatch.setattr("backend.fastapi.routers.plans.run_critic", _critic_approve)
    monkeypatch.setattr("backend.fastapi.routers.plans.save_video_planning", _db_save_ok)


def _set_cross_flag(monkeypatch: pytest.MonkeyPatch, enabled: bool) -> None:
    """settings.cross_validation_enabled override (lru_cache 재생성)."""
    monkeypatch.setenv("CROSS_VALIDATION_ENABLED", "true" if enabled else "false")
    get_settings.cache_clear()
    assert get_settings().cross_validation_enabled is enabled


class _CallCounter:
    """cross_validate / compare mock — 호출 카운트 + 인자 캡처."""

    def __init__(self) -> None:
        self.cross_calls: list[tuple[Any, ...]] = []
        self.compare_calls: list[tuple[Any, ...]] = []

    def cross_validate(self, plan_text: str, *args: Any, **kwargs: Any) -> CrossCheck:
        self.cross_calls.append((plan_text, args, kwargs))
        return CrossCheck(
            available=True,
            model_id="gemini-3.5-flash",
            overall_score=0.8,
            dimensions={"intent_fit": 0.8},
            verdict="approve",
            comment="mock cross",
        )

    def compare(self, critic_canonical: dict[str, Any], cross: CrossCheck) -> dict[str, Any]:
        self.compare_calls.append((critic_canonical, cross))
        return {
            "available": True,
            "agreement": True,
            "openai_score": 0.8,
            "gemini_score": 0.8,
            "score_delta": 0.0,
            "divergent_dimensions": [],
            "recommendation": "consensus",
        }


def _patch_cross(monkeypatch: pytest.MonkeyPatch, counter: _CallCounter) -> None:
    """orchestrator late-import 경로(llm.cross_validation)를 mock 으로 교체."""
    monkeypatch.setattr(
        "backend.fastapi.llm.cross_validation.cross_validate", counter.cross_validate,
    )
    monkeypatch.setattr(
        "backend.fastapi.llm.cross_validation.compare", counter.compare,
    )


def _check_names(env: Envelope) -> list[str]:
    return [c.name for c in env.validation.checks]


# ─── 1. flag OFF (default) — cross_validate 호출 0 + Envelope 동일 ──────

@pytest.mark.asyncio
async def test_cross_validation_flag_off_no_call(
    patch_agents_ok, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """cross_validation_enabled=False → cross_validate 호출 0 + 기존 응답 동일."""
    _set_cross_flag(monkeypatch, False)
    counter = _CallCounter()
    _patch_cross(monkeypatch, counter)

    result = await generate_plan("test-plan-id", _make_plan_entry(), GenerateRequest())

    assert isinstance(result, Envelope)
    # ★ hook 미동작 — cross_validate / compare 0 호출.
    assert counter.cross_calls == []
    assert counter.compare_calls == []
    # 기존 응답 형태 보존 (3-plan + checks 7개 순서).
    assert len(result.body.plan_candidates) == 3
    assert _check_names(result) == [
        "schema_envelope", "intent_filter", "rag_retrieval", "plan_count",
        "critic_evaluation", "db_persistence", "multi_model",
    ]


# ─── 2. flag ON — cross_validate 호출됨 + Envelope 불변 + 로깅 ──────────

@pytest.mark.asyncio
async def test_cross_validation_flag_on_called_envelope_unchanged(
    patch_agents_ok, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture,
) -> None:
    """cross_validation_enabled=True → cross_validate 호출 + Envelope 불변 + 로깅."""
    _set_cross_flag(monkeypatch, True)
    counter = _CallCounter()
    _patch_cross(monkeypatch, counter)

    # flag OFF 기준 응답(reference) — 동일 mock 경로로 산출.
    monkeypatch.setenv("CROSS_VALIDATION_ENABLED", "false")
    get_settings.cache_clear()
    ref = await generate_plan("test-plan-id", _make_plan_entry(), GenerateRequest())
    assert isinstance(ref, Envelope)
    ref_dump = ref.model_dump(mode="json")

    # flag ON 으로 재실행.
    monkeypatch.setenv("CROSS_VALIDATION_ENABLED", "true")
    get_settings.cache_clear()
    with caplog.at_level(logging.INFO, logger="backend.fastapi.orchestration.moa_orchestrator"):
        result = await generate_plan("test-plan-id", _make_plan_entry(), GenerateRequest())

    assert isinstance(result, Envelope)
    # ★ hook 동작 — cross_validate + compare 각 1회.
    assert len(counter.cross_calls) == 1
    assert len(counter.compare_calls) == 1
    # cross_validate 는 recommended plan 의 직렬화 텍스트를 받는다 (str).
    assert isinstance(counter.cross_calls[0][0], str)
    assert len(counter.cross_calls[0][0]) > 0
    # compare 는 critic canonical(dict) + CrossCheck 를 받는다.
    assert isinstance(counter.compare_calls[0][0], dict)
    assert isinstance(counter.compare_calls[0][1], CrossCheck)

    # ★★ Envelope/output_schema/응답 필드 0 변경 — flag ON 응답이 OFF 응답과 동형.
    result_dump = result.model_dump(mode="json")

    def _strip_volatile(env: dict[str, Any]) -> dict[str, Any]:
        """매 호출 변동(plan_id=uuid4 / target_plan_id) 필드 정규화 — 구조 비교용.

        plan_id 는 generate_plan 호출마다 새 uuid4 → cross-validation 과 무관한 기존
        비결정성. 이를 제거하면 flag ON/OFF 응답이 구조적으로 동일함을 보일 수 있다.
        """
        e = copy.deepcopy(env)
        for cand in e["body"].get("plan_candidates") or []:
            cand["plan_id"] = "<plan_id>"
        ce = e["body"].get("critic_evaluation")
        if isinstance(ce, dict) and "target_plan_id" in ce:
            ce["target_plan_id"] = "<target_plan_id>"
        return e

    norm_result = _strip_volatile(result_dump)
    norm_ref = _strip_volatile(ref_dump)
    assert norm_result["body"]["plan_candidates"] == norm_ref["body"]["plan_candidates"]
    assert norm_result["body"]["critic_evaluation"] == norm_ref["body"]["critic_evaluation"]
    assert norm_result["body"]["recommended_plan_index"] == norm_ref["body"]["recommended_plan_index"]
    assert norm_result["validation"] == norm_ref["validation"]
    # cross 결과(gemini/consensus 등)가 응답 어디에도 새 키로 새지 않음.
    assert set(result_dump["body"].keys()) == set(ref_dump["body"].keys())
    assert "cross" not in result_dump["body"]
    assert "cross_validation" not in result_dump["body"]

    # 로깅(관측성) 발생 — cross_validation 라인.
    assert any("cross_validation:" in rec.message for rec in caplog.records)


# ─── 3. graceful — cross_validate 예외여도 generate_plan 정상 완료 ──────

@pytest.mark.asyncio
async def test_cross_validation_exception_graceful(
    patch_agents_ok, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """cross_validate 가 예외를 던져도 generate_plan 정상 완료 (차단 0)."""
    _set_cross_flag(monkeypatch, True)

    def boom(*args: Any, **kwargs: Any) -> CrossCheck:
        raise RuntimeError("gemini exploded")

    monkeypatch.setattr("backend.fastapi.llm.cross_validation.cross_validate", boom)

    result = await generate_plan("test-plan-id", _make_plan_entry(), GenerateRequest())

    # 예외 흡수 — Envelope 정상.
    assert isinstance(result, Envelope)
    assert len(result.body.plan_candidates) == 3
    assert _check_names(result) == [
        "schema_envelope", "intent_filter", "rag_retrieval", "plan_count",
        "critic_evaluation", "db_persistence", "multi_model",
    ]


# ─── 4. graceful — cross available=False (키없음/503 모사) 정상 완료 ────

@pytest.mark.asyncio
async def test_cross_validation_unavailable_graceful(
    patch_agents_ok, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """cross_validate 가 available=False(graceful) 반환해도 generate_plan 정상 완료."""
    _set_cross_flag(monkeypatch, True)

    def unavailable(*args: Any, **kwargs: Any) -> CrossCheck:
        return CrossCheck(available=False, error="gemini 호출 실패: no api key")

    monkeypatch.setattr(
        "backend.fastapi.llm.cross_validation.cross_validate", unavailable,
    )

    result = await generate_plan("test-plan-id", _make_plan_entry(), GenerateRequest())

    assert isinstance(result, Envelope)
    assert len(result.body.plan_candidates) == 3
    assert result.body.critic_evaluation is not None
