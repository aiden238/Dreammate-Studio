"""Phase 33 — 결정적 pacing 게이트 (plotter structure_pacing_issues 이식) 단위 테스트.

검증 (hermetic, mock client, 실 API 0):
  - gate OFF(default) → bloated plan 도 verdict 불변(byte-identical).
  - gate ON + payoff(마무리) 비대(>30%) → approve→revise 비-LLM 강등 + blocking_issue.
  - gate ON + 현실적 균형 flow(짧은 close) → 강등 없음.
  - gate ON + flow<2 / total 0 / 비정형 → 미발동(graceful).

근거: ADR-0031(plotter, 40s 마무리/90s=44% bloat) + calib-ab-preliminary.md:43(결정적 게이트+cross-provider 합산).
"""
from __future__ import annotations

import json
from unittest.mock import MagicMock

import pytest

from backend.fastapi.agents import critic as critic_mod
from backend.fastapi.agents.critic import DIMENSIONS, run_critic
from backend.fastapi.config import Settings


def _approve_payload() -> str:
    """8차원(compact) 전부 5점 + approve."""
    return json.dumps(
        {
            "scores": {k: 5 for k in DIMENSIONS},
            "reasons": {k: "r" for k in DIMENSIONS},
            "suggestions": {k: "s" for k in DIMENSIONS},
            "overall_verdict": "approve",
            "blocking_issues": [],
        },
        ensure_ascii=False,
    )


def _openai_fake(content: str) -> MagicMock:
    client = MagicMock()
    msg = MagicMock()
    msg.content = content
    choice = MagicMock()
    choice.message = msg
    resp = MagicMock()
    resp.choices = [choice]
    client.chat.completions.create.return_value = resp
    return client


def _bloated_plan() -> dict:
    # 마지막 beat(마무리) 40s/90s=44% > 30% → bloat (ADR-0031 라이브 사례 정합)
    return {
        "plan_id": "p",
        "flow": [
            {"beat_index": 0, "duration_sec": 3},
            {"beat_index": 1, "duration_sec": 47},
            {"beat_index": 2, "duration_sec": 40},
        ],
    }


def _balanced_plan() -> dict:
    # 현실적: 짧은 close(15s/90s=17% < 30%)
    return {
        "plan_id": "p",
        "flow": [
            {"beat_index": 0, "duration_sec": 5},
            {"beat_index": 1, "duration_sec": 70},
            {"beat_index": 2, "duration_sec": 15},
        ],
    }


def _settings(gate: bool) -> Settings:
    return Settings(critic_pacing_gate_enabled=gate)


def test_pacing_gate_off_default_no_change(monkeypatch) -> None:
    """default OFF → bloated plan 도 approve 불변(byte-identical)."""
    monkeypatch.setattr(critic_mod, "get_settings", lambda: Settings())
    out = run_critic(_bloated_plan(), client=_openai_fake(_approve_payload()))
    assert out["overall_verdict"] == "approve"
    assert not any("pacing" in b for b in out["blocking_issues"])


def test_pacing_gate_on_demotes_bloated_payoff(monkeypatch) -> None:
    """ON + payoff 44% > 30% → approve→revise + blocking_issue."""
    monkeypatch.setattr(critic_mod, "get_settings", lambda: _settings(True))
    out = run_critic(_bloated_plan(), client=_openai_fake(_approve_payload()))
    assert out["overall_verdict"] == "revise"  # 비-LLM 강등
    assert any("pacing_bloat" in b for b in out["blocking_issues"])


def test_pacing_gate_on_balanced_keeps_approve(monkeypatch) -> None:
    """ON + 현실적 짧은 close(17%) → 강등 없음."""
    monkeypatch.setattr(critic_mod, "get_settings", lambda: _settings(True))
    out = run_critic(_balanced_plan(), client=_openai_fake(_approve_payload()))
    assert out["overall_verdict"] == "approve"
    assert not any("pacing" in b for b in out["blocking_issues"])


def test_pacing_gate_on_graceful_on_degenerate_flow(monkeypatch) -> None:
    """ON + flow<2 / total 0 → 미발동(graceful, approve 유지)."""
    monkeypatch.setattr(critic_mod, "get_settings", lambda: _settings(True))
    for plan in (
        {"plan_id": "p"},  # flow 없음
        {"plan_id": "p", "flow": [{"duration_sec": 30}]},  # beat 1개
        {"plan_id": "p", "flow": [{"duration_sec": 0}, {"duration_sec": 0}]},  # total 0
    ):
        out = run_critic(plan, client=_openai_fake(_approve_payload()))
        assert out["overall_verdict"] == "approve", plan
