"""Phase 9.5 — eval module (ADR-033).

golden_set 회귀 runner (mock-deterministic primary + 실 LLM mode flag).

Public API:
  - load_golden_set: eval/golden_set.md → 11 GS 케이스 구조화 (단일 출처 파싱).
  - score_case: schema 준수(100%) + structural(plan/hook/flow/광고·차단 단어) 채점.
  - run_golden_set_eval: 11 케이스 → mock pipeline → 채점 → 요약 + 임계값 게이트.
  - check_thresholds: eval-run §6 임계값 게이트.
  - measure_revise_effect / aggregate_revise_effects / run_revise_effect_eval:
    revise loop 개선 효과 eval (ADR-033 §2.3, Phase 4.5 D6 — canonical 0–1 delta, mock).
  - write_report / render_report: regression_results §5 형식 출력.
  - ScoreContext / resolve_mode / has_real_key (Phase 10 S3 — 실 LLM eval mode capability):
    default mock-deterministic + real 경로 opt-in wire (키/caller 부재 시 graceful mock fallback,
    CI/test 실 LLM 호출 0). ADR-033 §1 "mock primary + 실 LLM mode flag" 의 코드 실현.
"""
from __future__ import annotations

from .golden_set_loader import load_golden_set
from .mode import (
    MODE_MOCK,
    MODE_REAL,
    ScoreContext,
    has_real_key,
    resolve_mode,
)
from .report import render_report, write_report
from .revise_effect import aggregate_revise_effects, measure_revise_effect
from .runner import (
    check_thresholds,
    detect_ad_words,
    detect_blocked_words,
    run_golden_set_eval,
    run_revise_effect_eval,
    score_case,
)

__all__ = [
    "load_golden_set",
    "score_case",
    "run_golden_set_eval",
    "check_thresholds",
    "detect_ad_words",
    "detect_blocked_words",
    "measure_revise_effect",
    "aggregate_revise_effects",
    "run_revise_effect_eval",
    "render_report",
    "write_report",
    # Phase 10 S3 — 실 LLM eval mode capability (default mock, real opt-in).
    "ScoreContext",
    "resolve_mode",
    "has_real_key",
    "MODE_MOCK",
    "MODE_REAL",
]
