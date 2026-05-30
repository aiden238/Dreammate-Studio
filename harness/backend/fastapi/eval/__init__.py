"""Phase 9.5 — eval module (ADR-033).

golden_set 회귀 runner (mock-deterministic primary + 실 LLM mode flag).

Public API:
  - load_golden_set: eval/golden_set.md → 11 GS 케이스 구조화 (단일 출처 파싱).
  - score_case: schema 준수(100%) + structural(plan/hook/flow/광고·차단 단어) 채점.
  - run_golden_set_eval: 11 케이스 → mock pipeline → 채점 → 요약 + 임계값 게이트.
  - check_thresholds: eval-run §6 임계값 게이트.
  - write_report / render_report: regression_results §5 형식 출력.
"""
from __future__ import annotations

from .golden_set_loader import load_golden_set
from .report import render_report, write_report
from .runner import (
    check_thresholds,
    detect_ad_words,
    detect_blocked_words,
    run_golden_set_eval,
    score_case,
)

__all__ = [
    "load_golden_set",
    "score_case",
    "run_golden_set_eval",
    "check_thresholds",
    "detect_ad_words",
    "detect_blocked_words",
    "render_report",
    "write_report",
]
