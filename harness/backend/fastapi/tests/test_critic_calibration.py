"""HIP-007 S1 critic 낙관편향 보정 — 단위 테스트 (hermetic, mock client).

검증:
  - _derive_verdict 핵심차원 게이트: OFF(인자 없음) byte-identical / ON approve→revise 강등 /
    핵심차원 충분 시 approve 유지
  - run_critic: calibration OFF 시 기존 approve 보존 (byte-identical) /
    ON 시 얕은 plan(높은 평균 + 낮은 핵심차원) approve→revise / ON 시 프롬프트에 보정 지침 포함
참조: meta/audits/2026-06-05.md (HIP-007), meta/improvement_roadmap_hip006-010.md (007-S1).
"""

from __future__ import annotations

import json
from unittest.mock import MagicMock

import pytest

from backend.fastapi.agents import critic as critic_mod
from backend.fastapi.agents.critic import DIMENSIONS, _derive_verdict, run_critic
from backend.fastapi.config import Settings


def _fake_client(content: str) -> MagicMock:
    client = MagicMock()
    msg = MagicMock()
    msg.content = content
    choice = MagicMock()
    choice.message = msg
    resp = MagicMock()
    resp.choices = [choice]
    client.chat.completions.create.return_value = resp
    return client


def _shallow_but_high() -> dict[str, int]:
    # 평균은 approve 권(3.5) + 핵심 차원(hook_strength/structure)만 낮음(얕음) = 88점 함정 케이스
    s = {k: 4 for k in DIMENSIONS}
    s["hook_strength"] = 2
    s["structure"] = 2
    return s


def _payload(scores: dict[str, int]) -> str:
    return json.dumps(
        {
            "scores": scores,
            "reasons": {k: "r" for k in DIMENSIONS},
            "suggestions": {k: "s" for k in DIMENSIONS},
            "overall_verdict": "approve",
            "blocking_issues": [],
        },
        ensure_ascii=False,
    )


# ─── _derive_verdict 게이트 단위 ──────────────────────────────────────

def test_gate_off_is_byte_identical() -> None:
    avg, verdict = _derive_verdict(_shallow_but_high(), dimensions=DIMENSIONS)
    assert verdict == "approve"  # avg=3.5, 모든 ≥2 → 기존 규칙대로 approve
    assert avg == pytest.approx(3.5)


def test_gate_downgrades_approve_when_key_dim_low() -> None:
    _, verdict = _derive_verdict(
        _shallow_but_high(),
        dimensions=DIMENSIONS,
        calibration_key_dims=("hook_strength", "structure"),
        calibration_min=3,
    )
    assert verdict == "revise"  # 핵심 차원 < 3 → approve 차단 (88점 함정)


def test_gate_keeps_approve_when_key_dims_ok() -> None:
    _, verdict = _derive_verdict(
        {k: 4 for k in DIMENSIONS},
        dimensions=DIMENSIONS,
        calibration_key_dims=("hook_strength", "structure"),
        calibration_min=3,
    )
    assert verdict == "approve"


# ─── run_critic 통합 (gated) ──────────────────────────────────────────

def test_run_critic_calibration_off_keeps_approve(monkeypatch) -> None:
    monkeypatch.setattr(
        critic_mod, "get_settings", lambda: Settings(critic_calibration_enabled=False)
    )
    out = run_critic({"plan_id": "p"}, client=_fake_client(_payload(_shallow_but_high())))
    assert out["overall_verdict"] == "approve"  # OFF byte-identical


def test_run_critic_calibration_on_downgrades(monkeypatch) -> None:
    monkeypatch.setattr(
        critic_mod, "get_settings", lambda: Settings(critic_calibration_enabled=True)
    )
    out = run_critic({"plan_id": "p"}, client=_fake_client(_payload(_shallow_but_high())))
    assert out["overall_verdict"] == "revise"  # 88점 함정 차단


def test_run_critic_calibration_on_injects_preamble(monkeypatch) -> None:
    monkeypatch.setattr(
        critic_mod, "get_settings", lambda: Settings(critic_calibration_enabled=True)
    )
    client = _fake_client(_payload({k: 4 for k in DIMENSIONS}))
    run_critic({"plan_id": "p"}, client=client)
    system_msg = client.chat.completions.create.call_args.kwargs["messages"][0]["content"]
    assert "보정 지침" in system_msg
