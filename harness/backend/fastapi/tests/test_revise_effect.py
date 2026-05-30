"""Phase 9.5 Slice 3 — eval/revise_effect (ADR-033 §2.3, Phase 4.5 D6) 단위 테스트.

mock-based revise loop 개선 효과 검증 (canonical overall_score 0–1):
  - measure_revise_effect: 개선(delta>0) / 악화(delta<0 regressed) / 무변화 / revise 0회(approve 즉시) / max_reached
  - aggregate_revise_effects: 다중 plan 평균 delta + improved_rate + regressed_rate + 빈 list graceful
  - runner 통합: run_golden_set_eval(include_revise_effect=True) → summary/result revise_effect + report 섹션

forbidden 무수정 (additive): agents(critic/rewriter — import만)/schemas(ReviseAttempt import만)/
orchestration/routers/db/apps/web/golden_set.md.
"""
from __future__ import annotations

from backend.fastapi.eval import (
    aggregate_revise_effects,
    measure_revise_effect,
    render_report,
    run_golden_set_eval,
    run_revise_effect_eval,
)
from backend.fastapi.eval.runner import _REVISE_EFFECT_FIXTURES
from backend.fastapi.schemas.output import ReviseAttempt


# ── measure_revise_effect ────────────────────────────────────────────

def test_measure_improved() -> None:
    """revise 후 점수 상승 → delta>0, improved, direction='improved'."""
    history = [
        {"attempt": 0, "action": "revise", "revised": True},
        {"attempt": 1, "action": "approve", "revised": False},
    ]
    eff = measure_revise_effect(history, [0.6, 0.82])
    assert eff["initial_score"] == 0.6
    assert eff["final_score"] == 0.82
    assert eff["delta"] == 0.22
    assert eff["direction"] == "improved"
    assert eff["improved"] is True
    assert eff["regressed"] is False
    assert eff["attempts"] == 2
    assert eff["revised_count"] == 1


def test_measure_regressed() -> None:
    """revise 후 점수 하락 → delta<0, regressed (Phase 4.5 우려 검증 지표)."""
    history = [
        {"attempt": 0, "action": "revise", "revised": True},
        {"attempt": 1, "action": "approve", "revised": False},
    ]
    eff = measure_revise_effect(history, [0.74, 0.69])
    assert eff["delta"] == -0.05
    assert eff["direction"] == "regressed"
    assert eff["regressed"] is True
    assert eff["improved"] is False


def test_measure_no_change() -> None:
    """동일 점수 → delta=0, no_change."""
    history = [
        {"attempt": 0, "action": "revise", "revised": True},
        {"attempt": 1, "action": "approve", "revised": False},
    ]
    eff = measure_revise_effect(history, [0.7, 0.7])
    assert eff["delta"] == 0.0
    assert eff["direction"] == "no_change"
    assert eff["improved"] is False
    assert eff["regressed"] is False


def test_measure_no_revise_approve_immediate() -> None:
    """revise 0회 (초기 approve) → delta=0, revised_count=0, attempts=1."""
    history = [{"attempt": 0, "action": "approve", "revised": False}]
    eff = measure_revise_effect(history, [0.85])
    assert eff["initial_score"] == 0.85
    assert eff["final_score"] == 0.85
    assert eff["delta"] == 0.0
    assert eff["direction"] == "no_change"
    assert eff["attempts"] == 1
    assert eff["revised_count"] == 0
    assert eff["max_reached"] is False


def test_measure_max_reached() -> None:
    """max_revise 도달 attempt → max_reached=True 집계."""
    history = [
        {"attempt": 0, "action": "revise", "revised": True},
        {"attempt": 1, "action": "revise", "revised": True},
        {"attempt": 2, "action": "revise", "revised": False, "max_reached": True},
    ]
    eff = measure_revise_effect(history, [0.58, 0.63, 0.66])
    assert eff["max_reached"] is True
    assert eff["delta"] == 0.08
    assert eff["direction"] == "improved"
    assert eff["revised_count"] == 2


def test_measure_empty_scores_graceful() -> None:
    """점수 없음 → initial/final=None, delta=0, no_change (graceful)."""
    eff = measure_revise_effect([{"attempt": 0, "action": "approve", "revised": False}], [])
    assert eff["initial_score"] is None
    assert eff["final_score"] is None
    assert eff["delta"] == 0.0
    assert eff["direction"] == "no_change"
    assert eff["attempts"] == 1


def test_measure_none_history_graceful() -> None:
    """revise_history=None + scores 단일 → attempts=0, delta=0 (graceful)."""
    eff = measure_revise_effect(None, [0.7])
    assert eff["attempts"] == 0
    assert eff["revised_count"] == 0
    assert eff["delta"] == 0.0


def test_measure_revise_history_revise_attempt_compat() -> None:
    """ReviseAttempt(Pydantic) → dict 변환 입력 정합 (schemas/output 구조)."""
    attempts = [
        ReviseAttempt(attempt=0, action="revise", revised=True),
        ReviseAttempt(attempt=1, action="approve", revised=False),
    ]
    history = [a.model_dump() for a in attempts]
    eff = measure_revise_effect(history, [0.6, 0.75])
    assert eff["attempts"] == 2
    assert eff["revised_count"] == 1
    assert eff["direction"] == "improved"


# ── aggregate_revise_effects ─────────────────────────────────────────

def test_aggregate_mixed() -> None:
    """개선 2 + 악화 1 + 무변화 1 → mean_delta + 비율 집계."""
    effects = [
        measure_revise_effect([{"attempt": 0, "action": "revise", "revised": True}], [0.6, 0.8]),
        measure_revise_effect([{"attempt": 0, "action": "revise", "revised": True}], [0.5, 0.7]),
        measure_revise_effect([{"attempt": 0, "action": "revise", "revised": True}], [0.7, 0.6]),
        measure_revise_effect([{"attempt": 0, "action": "approve", "revised": False}], [0.8, 0.8]),
    ]
    agg = aggregate_revise_effects(effects)
    assert agg["n"] == 4
    assert agg["improved_rate"] == 0.5
    assert agg["regressed_rate"] == 0.25
    assert agg["no_change_rate"] == 0.25
    # deltas: +0.2, +0.2, -0.1, 0.0 → mean 0.075
    assert agg["mean_delta"] == 0.075


def test_aggregate_empty_graceful() -> None:
    """빈 list → 모든 비율 0.0 + n=0 (graceful, 예외 X)."""
    agg = aggregate_revise_effects([])
    assert agg == {
        "mean_delta": 0.0,
        "improved_rate": 0.0,
        "regressed_rate": 0.0,
        "no_change_rate": 0.0,
        "n": 0,
    }


def test_aggregate_none_graceful() -> None:
    """None 입력 → graceful 빈 집계."""
    agg = aggregate_revise_effects(None)
    assert agg["n"] == 0
    assert agg["mean_delta"] == 0.0


def test_aggregate_rates_sum_to_one() -> None:
    """improved+regressed+no_change 비율 합 == 1.0 (분류 누락 없음)."""
    eff = run_revise_effect_eval()
    agg = eff["aggregate"]
    total = agg["improved_rate"] + agg["regressed_rate"] + agg["no_change_rate"]
    assert round(total, 4) == 1.0


# ── run_revise_effect_eval (mock fixture) ────────────────────────────

def test_run_revise_effect_eval_default_fixtures() -> None:
    """기본 fixture 5종 → effects + aggregate. regressed 사례 포함 (Phase 4.5 우려)."""
    result = run_revise_effect_eval()
    assert len(result["effects"]) == len(_REVISE_EFFECT_FIXTURES)
    agg = result["aggregate"]
    assert agg["n"] == len(_REVISE_EFFECT_FIXTURES)
    # fixture 에 regressed 1건 포함 → regressed_rate > 0 (검증 지표 작동).
    assert agg["regressed_rate"] > 0.0
    assert agg["improved_rate"] > 0.0


def test_run_revise_effect_eval_deterministic() -> None:
    """동일 입력 2회 → 동일 결과 (mock-deterministic)."""
    r1 = run_revise_effect_eval()
    r2 = run_revise_effect_eval()
    assert r1 == r2


def test_run_revise_effect_eval_injected_fixtures() -> None:
    """fixtures 주입 → 주입 fixture 만 집계."""
    fixtures = [
        ([{"attempt": 0, "action": "revise", "revised": True}], [0.5, 0.9]),
    ]
    result = run_revise_effect_eval(fixtures=fixtures)
    assert result["aggregate"]["n"] == 1
    assert result["aggregate"]["improved_rate"] == 1.0
    assert result["effects"][0]["delta"] == 0.4


# ── runner 통합 (include_revise_effect) ──────────────────────────────

def test_golden_set_eval_include_revise_effect() -> None:
    """include_revise_effect=True → result/summary 에 revise_effect 추가 + 게이트 불변."""
    result = run_golden_set_eval(mode="mock", include_revise_effect=True)
    assert "revise_effect" in result
    assert "revise_effect" in result["summary"]
    re = result["summary"]["revise_effect"]
    assert {"mean_delta", "improved_rate", "regressed_rate", "no_change_rate", "n"} <= set(re)
    # revise effect 통합은 golden_set 게이트(schema/광고/차단/P0)에 영향 없음.
    assert result["gate"]["passed"] is True


def test_golden_set_eval_default_no_revise_effect() -> None:
    """기본(include_revise_effect 미지정) → revise_effect 미포함 (Slice 2 동작 불변)."""
    result = run_golden_set_eval(mode="mock")
    assert "revise_effect" not in result
    assert "revise_effect" not in result["summary"]


def test_report_includes_revise_effect_section() -> None:
    """render_report → revise effect 섹션 (mean_delta / improved_rate / regressed_rate)."""
    result = run_golden_set_eval(mode="mock", include_revise_effect=True)
    md = render_report(result, trigger="phase-9.5_baseline")
    assert "## revise effect" in md
    assert "mean_delta" in md
    assert "regressed_rate" in md
    assert "improved_rate" in md


def test_report_no_revise_effect_section_when_absent() -> None:
    """revise_effect 없는 result → 섹션 미출력 (Slice 2 리포트 불변)."""
    result = run_golden_set_eval(mode="mock")
    md = render_report(result, trigger="phase-9.5_baseline")
    assert "## revise effect" not in md
