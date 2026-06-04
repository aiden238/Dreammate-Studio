"""Phase 20 Slice 4 — Critic commercial_viral 17차원 (P-007 v1.4.0) 검증 (CC-027).

acceptance 매핑:
  - A4: Critic commercial 차원(gated) — output_mode=commercial_viral 에서 17차원(director 10 + 상업 7).
        compact(8)/rich(9)/director(10) byte-identical.

핵심 검증:
  1. DIMENSIONS_COMMERCIAL = DIMENSIONS_DIRECTOR + 상업 7 (17) / COMMERCIAL_PROMPT_VERSION=v1.4.0.
  2. COMMERCIAL_SYSTEM_PROMPT 가 상업 차원 + 17차원 표기 포함, director(10)는 미포함.
  3. run_critic: output_mode=commercial_viral → COMMERCIAL_SYSTEM_PROMPT + 17차원 + result scores.
  4. byte-identical: compact/rich/director critic 프롬프트 commercial 토큰 누수 0.
"""
from __future__ import annotations

import json
from typing import Any

import pytest

from backend.fastapi.agents.critic import (
    COMMERCIAL_PROMPT_VERSION,
    COMMERCIAL_SYSTEM_PROMPT,
    DIMENSIONS_COMMERCIAL,
    DIMENSIONS_DIRECTOR,
    DIRECTOR_SYSTEM_PROMPT,
    RICH_SYSTEM_PROMPT,
    SYSTEM_PROMPT,
    run_critic,
)
from backend.fastapi.config import get_settings

_PLAN = {"plan_id": "p", "name": "n", "concept": "c", "hook": "후크", "flow": []}

_COMMERCIAL_DIMS = (
    "viral_potential", "brand_memory", "commercial_conversion", "non_genericity",
    "execution_feasibility", "platform_fit", "shareability",
)


class _FakeCompletions:
    def __init__(self, sink: dict[str, Any], dims: tuple[str, ...]) -> None:
        self.sink = sink
        self.dims = dims

    def create(self, **kwargs: Any) -> Any:
        self.sink["system"] = kwargs["messages"][0]["content"]
        self.sink["max_tokens"] = kwargs.get("max_tokens")
        payload = json.dumps(
            {
                "scores": {d: 4 for d in self.dims},
                "reasons": {d: "r" for d in self.dims},
                "suggestions": {d: "s" for d in self.dims},
                "overall_verdict": "approve",
                "blocking_issues": [],
            }
        )

        class _Msg:
            content = payload

        class _Choice:
            message = _Msg()

        class _Resp:
            choices = [_Choice()]

        return _Resp()


class _FakeClient:
    def __init__(self, sink: dict[str, Any], dims: tuple[str, ...]) -> None:
        self.chat = type("C", (), {"completions": _FakeCompletions(sink, dims)})()


# ─── 1. 상수 ──────────────────────────────────────────────────────────


def test_dimensions_commercial() -> None:
    assert DIMENSIONS_COMMERCIAL == DIMENSIONS_DIRECTOR + _COMMERCIAL_DIMS
    assert len(DIMENSIONS_COMMERCIAL) == 17
    assert COMMERCIAL_PROMPT_VERSION == "v1.4.0"
    # retention_design 은 director 에 이미 있어 중복 없음
    assert DIMENSIONS_COMMERCIAL.count("retention_design") == 1


def test_commercial_prompt_content() -> None:
    for d in _COMMERCIAL_DIMS:
        assert d in COMMERCIAL_SYSTEM_PROMPT, f"commercial critic 프롬프트에 '{d}' 미포함"
    assert "17차원" in COMMERCIAL_SYSTEM_PROMPT and "17개 키" in COMMERCIAL_SYSTEM_PROMPT
    # director(10) 프롬프트엔 상업 차원 없음
    for d in _COMMERCIAL_DIMS:
        assert d not in DIRECTOR_SYSTEM_PROMPT, f"director 프롬프트에 commercial 차원 '{d}' 오염"


# ─── 2. run_critic output_mode 분기 ─────────────────────────────────


def _run(monkeypatch: pytest.MonkeyPatch, mode: str, dims: tuple[str, ...]) -> tuple[dict, dict]:
    monkeypatch.setenv("OUTPUT_MODE", mode)
    monkeypatch.setenv("RICH_OUTPUT_ENABLED", "false")
    get_settings.cache_clear()
    try:
        sink: dict[str, Any] = {}
        result = run_critic(_PLAN, client=_FakeClient(sink, dims))
        return sink, result
    finally:
        get_settings.cache_clear()


def test_commercial_critic_17dim(monkeypatch: pytest.MonkeyPatch) -> None:
    sink, result = _run(monkeypatch, "commercial_viral", DIMENSIONS_COMMERCIAL)
    assert sink["system"] == COMMERCIAL_SYSTEM_PROMPT
    for d in _COMMERCIAL_DIMS:
        assert d in result["scores"]
    assert sink["max_tokens"] == 2800  # 17차원 절단 방지 상향


def test_lower_tiers_critic_not_polluted(monkeypatch: pytest.MonkeyPatch) -> None:
    # compact/rich/director critic 프롬프트는 commercial 차원 미포함 + max_tokens 1500 불변(byte-identical).
    from backend.fastapi.agents.critic import DIMENSIONS, DIMENSIONS_RICH

    for mode, dims, expect_sp in (
        ("compact", DIMENSIONS, SYSTEM_PROMPT),
        ("rich", DIMENSIONS_RICH, RICH_SYSTEM_PROMPT),
        ("director", DIMENSIONS_DIRECTOR, DIRECTOR_SYSTEM_PROMPT),
    ):
        sink, _ = _run(monkeypatch, mode, dims)
        assert sink["system"] == expect_sp
        for d in _COMMERCIAL_DIMS:
            assert d not in sink["system"], f"{mode} critic 에 commercial 차원 '{d}' 오염"
        assert sink["max_tokens"] == 1500
