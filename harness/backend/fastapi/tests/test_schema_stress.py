"""Phase 6 Slice 3 — Schema stress test (ADR-018 / ADR-019).

기존 test_critic.py / test_rewriter.py 단위 테스트와 별도 layer 로,
canonical + deprecated 공존 / typing 강화 / frontend mirror 호환 등을
matrix 형태로 검증한다.

검증 영역:
  1. CriticEvaluation canonical (overall_score / dimensions) + deprecated 공존
  2. ReviseAttempt canonical enum + max_reached + graceful warning 필드
  3. select_best_plan_index canonical fallback (no DeprecationWarning) vs
     deprecated keys (DeprecationWarning 발행)
  4. RewriterInput / RewriterOutput Pydantic 모델 동작
  5. Body.revise_history typing 호환 (Phase 4.5 dict vs Phase 6 ReviseAttempt)

회귀 0 보장:
  - Phase 1~4.5 응답 (deprecated 필드만) → 그대로 검증 통과
  - Phase 6 응답 (canonical + deprecated) → DeprecationWarning 없이 통과
"""
from __future__ import annotations

import warnings
from typing import Any

import pytest
from pydantic import ValidationError

from backend.fastapi.agents.critic import select_best_plan_index
from backend.fastapi.agents.rewriter import RewriterInput, RewriterOutput
from backend.fastapi.schemas.output import (
    Body,
    CriticEvaluation,
    Plan,
    PlanFlowBeat,
    ReviseAttempt,
)


# ─── Fixtures ─────────────────────────────────────────────────────────


def _make_plan(option_index: int = 0) -> Plan:
    """Body 검증에 필요한 최소 Plan 인스턴스."""
    return Plan(
        plan_id=f"plan-{option_index:08x}",
        option_index=option_index,
        name=f"테스트{option_index}",
        concept="스트레스 테스트 컨셉",
        hook="이 영상은 stress test 용 hook 예시입니다.",
        flow=[
            PlanFlowBeat(beat_index=0, beat="도입", duration_sec=10, purpose="훅"),
            PlanFlowBeat(beat_index=1, beat="전개", duration_sec=30, purpose="본문"),
        ],
        pros="간결",
        risks="없음",
        approach_label="informational",
        rag_used=[],
    )


# ─── 1. CriticEvaluation canonical + deprecated 공존 ─────────────────


def test_critic_evaluation_canonical_minimal_instantiation() -> None:
    """Phase 6 canonical 필드(overall_score + dimensions) + 필수 overall_verdict 만으로 인스턴스화."""
    ce = CriticEvaluation(
        overall_score=0.78,
        dimensions={"hook_strength": 0.9, "target_clarity": 0.7},
        overall_verdict="approve",
    )
    assert ce.overall_score == pytest.approx(0.78)
    assert ce.dimensions["hook_strength"] == pytest.approx(0.9)
    assert ce.overall_verdict == "approve"
    # deprecated 필드는 default 값 (Optional / 빈 dict)
    assert ce.overall_score_avg is None
    assert ce.scores is None
    assert ce.reasons == {}


def test_critic_evaluation_deprecated_only_backward_compat() -> None:
    """Phase 1~4.5 응답: canonical 미존재 + deprecated 필드만 → 그대로 통과 (backward-compat).

    DeprecationWarning 은 backend 모델 자체에서 발행하지 않음 (호환성). Skip silent.
    """
    ce = CriticEvaluation(
        target_plan_id="plan-deadbeef",
        scores={
            "intent_fit": 3,
            "target_clarity": 3,
            "hook_strength": 4,
            "message_clarity": 3,
            "structure": 3,
            "feasibility": 4,
            "brand_consistency": 4,
            "differentiation": 3,
        },
        overall_score_avg=3.375,
        overall_verdict="approve",
        blocking_issues=[],
        revise_round=0,
    )
    # canonical 필드는 default (None / 빈 dict)
    assert ce.overall_score is None
    assert ce.dimensions == {}
    # deprecated 필드는 입력값 유지
    assert ce.overall_score_avg == pytest.approx(3.375)
    assert ce.scores is not None
    assert ce.scores.hook_strength == 4


def test_critic_evaluation_canonical_and_deprecated_coexist() -> None:
    """Phase 6 응답: canonical + deprecated 동시 존재 — 둘 다 보존."""
    ce = CriticEvaluation(
        overall_score=0.7,
        dimensions={"hook_strength": 0.7, "target_clarity": 0.7},
        overall_score_avg=3.5,  # 0~5 호환 필드
        overall_verdict="approve",
    )
    assert ce.overall_score == pytest.approx(0.7)
    assert ce.overall_score_avg == pytest.approx(3.5)
    assert "hook_strength" in ce.dimensions


def test_critic_evaluation_overall_score_range_validation() -> None:
    """overall_score 는 0.0~1.0 범위 강제 — 초과 시 ValidationError."""
    with pytest.raises(ValidationError):
        CriticEvaluation(overall_score=1.5, overall_verdict="approve")
    with pytest.raises(ValidationError):
        CriticEvaluation(overall_score=-0.1, overall_verdict="approve")


# ─── 2. ReviseAttempt canonical ───────────────────────────────────────


def test_revise_attempt_canonical_minimal() -> None:
    """attempt=0 초기 critic 케이스."""
    ra = ReviseAttempt(attempt=0, action="approve", revised=False)
    assert ra.attempt == 0
    assert ra.action == "approve"
    assert ra.revised is False
    assert ra.max_reached is None
    assert ra.critic_warning is None


def test_revise_attempt_max_reached_marker() -> None:
    """attempt=2 + max_reached=True — Phase 4.5 max_revise=2 도달 케이스."""
    ra = ReviseAttempt(attempt=2, action="revise", revised=False, max_reached=True)
    assert ra.attempt == 2
    assert ra.max_reached is True


def test_revise_attempt_unknown_action_allowed() -> None:
    """Critic 이 미정의 verdict 반환 시 'unknown' 폴백 — Literal 허용."""
    ra = ReviseAttempt(attempt=1, action="unknown", revised=False)
    assert ra.action == "unknown"


def test_revise_attempt_graceful_warning_fields() -> None:
    """critic_warning + rewriter_warning graceful 마커 동시 보존."""
    ra = ReviseAttempt(
        attempt=1,
        action="revise",
        revised=True,
        critic_warning="critic_failed: OpenAIError",
        rewriter_warning="rewriter_failed: TimeoutError",
    )
    assert ra.critic_warning == "critic_failed: OpenAIError"
    assert ra.rewriter_warning == "rewriter_failed: TimeoutError"


def test_revise_attempt_invalid_action_rejected() -> None:
    """Literal 외 action 값은 Pydantic ValidationError."""
    with pytest.raises(ValidationError):
        ReviseAttempt(attempt=0, action="invalid_value", revised=False)  # type: ignore[arg-type]


def test_revise_attempt_negative_attempt_rejected() -> None:
    """attempt >= 0 강제 (ge=0)."""
    with pytest.raises(ValidationError):
        ReviseAttempt(attempt=-1, action="approve", revised=False)


# ─── 3. select_best_plan_index — canonical vs deprecated matrix ──────


def test_stress_select_best_canonical_overall_score_no_warning() -> None:
    """canonical overall_score 만 사용 시 DeprecationWarning 발행 없음."""
    verdicts = [
        {"overall_score": 0.3},
        {"overall_score": 0.9},
        {"overall_score": 0.6},
    ]
    with warnings.catch_warnings():
        warnings.simplefilter("error", DeprecationWarning)
        # canonical only — warning 발생 시 즉시 fail
        assert select_best_plan_index(verdicts) == 1


def test_stress_select_best_canonical_dimensions_fallback_no_warning() -> None:
    """canonical: overall_score 부재 시 dimensions 평균 → DeprecationWarning 없음."""
    verdicts = [
        {"dimensions": {"a": 0.5, "b": 0.5}},  # avg 0.5
        {"dimensions": {"a": 0.9, "b": 0.9}},  # avg 0.9
        {"dimensions": {"a": 0.7, "b": 0.7}},  # avg 0.7
    ]
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        idx = select_best_plan_index(verdicts)
        assert idx == 1
        deprecation_warns = [
            w for w in caught if issubclass(w.category, DeprecationWarning)
        ]
        assert deprecation_warns == [], (
            f"canonical fallback should not warn; got {len(deprecation_warns)}"
        )


def test_stress_select_best_deprecated_eight_dim_scores_warns() -> None:
    """deprecated eight_dim_scores 사용 시 DeprecationWarning 발행 + 결과 정확."""
    verdicts = [
        {"eight_dim_scores": {"hook": 0.5, "story": 0.5}},  # avg 0.5
        {"eight_dim_scores": {"hook": 0.9, "story": 0.9}},  # avg 0.9
    ]
    with pytest.warns(DeprecationWarning, match="eight_dim_scores"):
        assert select_best_plan_index(verdicts) == 1


def test_stress_select_best_canonical_overrides_all_deprecated() -> None:
    """canonical + 모든 deprecated key 동시 존재 — canonical 만 사용, warning 없음."""
    verdicts = [
        {
            "overall_score": 0.9,
            "dimensions": {"a": 0.9},
            "overall_score_avg": 1.0,  # deprecated — 무시되어야 함
            "scores": {"hook_strength": 1},  # deprecated — 무시
            "eight_dim_scores": {"hook": 1.0},  # deprecated — 무시
        },
        {
            "overall_score": 0.3,
            "dimensions": {"a": 0.3},
            "overall_score_avg": 5.0,  # deprecated — 무시 (canonical 우선이므로 idx 0 가 이김)
        },
    ]
    with warnings.catch_warnings():
        warnings.simplefilter("error", DeprecationWarning)
        # canonical overall_score 우선 → idx 0 (0.9 > 0.3)
        assert select_best_plan_index(verdicts) == 0


def test_stress_select_best_tie_canonical_prefers_lower_index() -> None:
    """canonical 동점 시 더 작은 index — deterministic."""
    verdicts = [
        {"overall_score": 0.7},
        {"overall_score": 0.7},
        {"overall_score": 0.7},
    ]
    with warnings.catch_warnings():
        warnings.simplefilter("error", DeprecationWarning)
        assert select_best_plan_index(verdicts) == 0


# ─── 4. RewriterInput / RewriterOutput Pydantic 모델 (ADR-019) ──────


def test_rewriter_input_minimal() -> None:
    """plan + critic_verdict 만으로 인스턴스화 — model 은 default."""
    ri = RewriterInput(
        plan={"name": "test"},
        critic_verdict={"overall_verdict": "revise"},
    )
    assert ri.plan["name"] == "test"
    assert ri.critic_verdict["overall_verdict"] == "revise"
    assert ri.model == "gpt-4o-mini"


def test_rewriter_output_graceful_warning_marker() -> None:
    """LLM 실패 시 _rewriter_warning 마커 — alias 호환."""
    ro = RewriterOutput.model_validate(
        {
            "revised_plan": {"name": "orig"},  # 실패 시 원본 plan
            "_rewriter_warning": "rewriter_failed: OpenAIError",
        }
    )
    assert ro.rewriter_warning == "rewriter_failed: OpenAIError"
    assert ro.revised_plan["name"] == "orig"


def test_rewriter_output_with_model_marker() -> None:
    """정상 케이스 — _rewriter_model 마커만 존재."""
    ro = RewriterOutput.model_validate(
        {
            "revised_plan": {"name": "revised"},
            "_rewriter_model": "gpt-4o-mini",
        }
    )
    assert ro.rewriter_model == "gpt-4o-mini"
    assert ro.rewriter_warning is None


# ─── 5. Body.revise_history typing 호환 (dict vs ReviseAttempt) ──────


def test_body_revise_history_dict_form_phase_4_5_compat() -> None:
    """Phase 4.5 dict 형태 revise_history — 회귀 0 보장."""
    body = Body(
        plan_candidates=[_make_plan(0)],
        revise_history=[
            [
                {"attempt": 0, "action": "revise", "revised": True},
                {"attempt": 1, "action": "approve", "revised": False},
            ]
        ],
    )
    assert body.revise_history is not None
    assert len(body.revise_history) == 1
    assert body.revise_history[0][0]["action"] == "revise"
    assert body.revise_history[0][1]["action"] == "approve"


def test_body_revise_history_none_default() -> None:
    """Phase 4 이하 호출 시 revise_history None — backward-compat."""
    body = Body(plan_candidates=[_make_plan(0), _make_plan(1)])
    assert body.revise_history is None
    assert body.recommended_plan_index is None


def test_body_recommended_plan_index_within_range() -> None:
    """recommended_plan_index 0~2 허용 + None 허용."""
    for idx in (0, 1, 2, None):
        body = Body(
            plan_candidates=[_make_plan(0), _make_plan(1), _make_plan(2)],
            recommended_plan_index=idx,
        )
        assert body.recommended_plan_index == idx


# ─── 6. Round-trip: select_best_plan_index ↔ Body.recommended_plan_index ──


def test_round_trip_select_best_to_body_recommended() -> None:
    """select_best_plan_index 결과를 Body.recommended_plan_index 에 주입 round-trip.

    canonical verdicts → best idx → Body 검증 → 동일 idx 보존.
    """
    verdicts: list[dict[str, Any]] = [
        {"overall_score": 0.5},
        {"overall_score": 0.8},  # best
        {"overall_score": 0.4},
    ]
    with warnings.catch_warnings():
        warnings.simplefilter("error", DeprecationWarning)
        best_idx = select_best_plan_index(verdicts)
    assert best_idx == 1

    body = Body(
        plan_candidates=[_make_plan(0), _make_plan(1), _make_plan(2)],
        recommended_plan_index=best_idx,
    )
    assert body.recommended_plan_index == 1
