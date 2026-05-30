"""Phase 9.5 — revise loop 개선 효과 eval (ADR-033, Phase 4.5 D6 해소). mock-based.

revise attempt별 canonical overall_score(0–1) delta 측정.
revise_history(ReviseAttempt: attempt/action/revised/max_reached) 정합.

설계 (ADR-033 §2.3):
  - revise effect 는 canonical overall_score(0–1) 변화로 측정한다 (deprecated 0–5 불필요 —
    ADR-034 제거 정합).
  - mock fixture 기반 (실 LLM 미호출). attempt 0 (초기 critic) → 1 (revise 후 재평가) → 2.
    `delta = final_score - initial_score` + 방향성(improved/no_change/regressed) 집계.
  - regressed_rate (revise 후 점수 하락) 추적 — Phase 4.5 우려 "revise 가 기획을 평범하게"
    검증 지표.

revise_history(ReviseAttempt — Phase 4.5 ADR-016 / Phase 6 ADR-018 구조) 와 attempt 정렬 정합:
  scores_by_attempt[i] 는 revise_history[i].attempt 의 재평가 canonical 점수.
"""
from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

# 방향성 판정 epsilon — 부동소수 잡음(<1e-9) 을 정체로 흡수. 의미 있는 변화 임계.
_DIRECTION_EPS = 1e-9


def _direction(delta: float) -> str:
    """delta 부호 → 방향성 라벨 (improved / regressed / no_change)."""
    if delta > _DIRECTION_EPS:
        return "improved"
    if delta < -_DIRECTION_EPS:
        return "regressed"
    return "no_change"


def measure_revise_effect(
    revise_history: list[dict[str, Any]] | None,
    scores_by_attempt: list[float] | None,
) -> dict[str, Any]:
    """단일 plan 의 revise 전/후 canonical score delta + 방향성.

    Args:
        revise_history: ReviseAttempt dict list (attempt/action/revised/max_reached).
            None 또는 빈 list 면 revise 미발생 (approve 즉시) 로 간주.
        scores_by_attempt: attempt 순서별 canonical overall_score(0–1) list.
            scores_by_attempt[0] = 초기 critic, [-1] = 최종. None/빈 list → 측정 불가.

    Returns:
        {
          initial_score: float | None,   # attempt 0 canonical 점수
          final_score: float | None,     # 마지막 attempt canonical 점수
          delta: float,                  # final - initial (round 4)
          direction: "improved" | "regressed" | "no_change",
          improved: bool,                # delta > 0
          regressed: bool,               # delta < 0
          attempts: int,                 # revise_history 길이 (attempt 수)
          revised_count: int,            # revised=True 인 attempt 수 (실제 Rewriter 호출)
          max_reached: bool,             # 어느 attempt 라도 max_reached=True
        }

    측정 불가(점수 없음) 시 initial/final=None, delta=0.0, direction="no_change".
    """
    history = revise_history or []
    scores = list(scores_by_attempt or [])

    attempts = len(history)
    revised_count = sum(1 for a in history if isinstance(a, dict) and a.get("revised"))
    max_reached = any(
        isinstance(a, dict) and bool(a.get("max_reached")) for a in history
    )

    if not scores:
        return {
            "initial_score": None,
            "final_score": None,
            "delta": 0.0,
            "direction": "no_change",
            "improved": False,
            "regressed": False,
            "attempts": attempts,
            "revised_count": revised_count,
            "max_reached": max_reached,
        }

    initial_score = scores[0]
    final_score = scores[-1]
    delta = round(final_score - initial_score, 4)
    direction = _direction(delta)

    return {
        "initial_score": round(initial_score, 4),
        "final_score": round(final_score, 4),
        "delta": delta,
        "direction": direction,
        "improved": direction == "improved",
        "regressed": direction == "regressed",
        "attempts": attempts,
        "revised_count": revised_count,
        "max_reached": max_reached,
    }


def aggregate_revise_effects(plans_effects: list[dict[str, Any]] | None) -> dict[str, Any]:
    """다중 plan 집계: 평균 delta + improved_rate + regressed_rate (revise 악화 비율).

    Args:
        plans_effects: measure_revise_effect 반환 dict list.

    Returns:
        {
          mean_delta: float,        # 평균 delta (round 4)
          improved_rate: float,     # direction=="improved" 비율
          regressed_rate: float,    # direction=="regressed" 비율 (Phase 4.5 우려 검증)
          no_change_rate: float,    # direction=="no_change" 비율
          n: int,                   # 집계 대상 plan 수
        }

    빈 list → 모든 비율 0.0 + n=0 (graceful, 예외 X).
    """
    effects = plans_effects or []
    n = len(effects)
    if n == 0:
        return {
            "mean_delta": 0.0,
            "improved_rate": 0.0,
            "regressed_rate": 0.0,
            "no_change_rate": 0.0,
            "n": 0,
        }

    deltas = [float(e.get("delta", 0.0)) for e in effects]
    improved = sum(1 for e in effects if e.get("direction") == "improved")
    regressed = sum(1 for e in effects if e.get("direction") == "regressed")
    no_change = sum(1 for e in effects if e.get("direction") == "no_change")

    return {
        "mean_delta": round(sum(deltas) / n, 4),
        "improved_rate": round(improved / n, 4),
        "regressed_rate": round(regressed / n, 4),
        "no_change_rate": round(no_change / n, 4),
        "n": n,
    }
