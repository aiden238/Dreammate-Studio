"""Phase 15 Slice 4 — Critic director 차원 retention_design (P-007 v1.3.0) 검증 (CC-019).

acceptance 매핑:
  - A6: Critic director 차원(gated) — output_mode=director 에서 retention_design(10번째) 추가.
        compact(8)/rich(9) byte-identical.

핵심 검증:
  1. DIMENSIONS_DIRECTOR = DIMENSIONS_RICH + retention_design (10) / DIRECTOR_PROMPT_VERSION=v1.3.0.
  2. DIRECTOR_SYSTEM_PROMPT 가 retention_design + 10차원 표기 포함, rich(9)는 미포함.
  3. run_critic: output_mode 별 system prompt + 차원 (compact 8 / rich 9 / director 10).
  4. director: result scores 에 retention_design 포함.
"""
from __future__ import annotations

import json
from typing import Any

import pytest

from backend.fastapi.agents.critic import (
    DIMENSIONS,
    DIMENSIONS_DIRECTOR,
    DIMENSIONS_RICH,
    DIRECTOR_PROMPT_VERSION,
    DIRECTOR_SYSTEM_PROMPT,
    RICH_SYSTEM_PROMPT,
    SYSTEM_PROMPT,
    run_critic,
)
from backend.fastapi.config import get_settings

_PLAN = {"plan_id": "p", "name": "n", "concept": "c", "hook": "후크", "flow": []}


class _FakeCompletions:
    def __init__(self, sink: dict[str, Any], dims: tuple[str, ...]) -> None:
        self.sink = sink
        self.dims = dims

    def create(self, **kwargs: Any) -> Any:
        self.sink["system"] = kwargs["messages"][0]["content"]
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


def test_dimensions_director() -> None:
    assert DIMENSIONS_DIRECTOR == DIMENSIONS_RICH + ("retention_design",)
    assert len(DIMENSIONS_DIRECTOR) == 10
    assert DIRECTOR_PROMPT_VERSION == "v1.3.0"


def test_director_prompt_content() -> None:
    assert "retention_design" in DIRECTOR_SYSTEM_PROMPT
    assert "10차원" in DIRECTOR_SYSTEM_PROMPT and "10개 키" in DIRECTOR_SYSTEM_PROMPT
    # rich(9) 프롬프트엔 retention_design 없음
    assert "retention_design" not in RICH_SYSTEM_PROMPT


# ─── 2. run_critic output_mode 분기 ─────────────────────────────────


def _run(monkeypatch: pytest.MonkeyPatch, mode: str, dims: tuple[str, ...]) -> tuple[str, dict]:
    monkeypatch.setenv("OUTPUT_MODE", mode)
    monkeypatch.setenv("RICH_OUTPUT_ENABLED", "false")
    get_settings.cache_clear()
    try:
        sink: dict[str, Any] = {}
        result = run_critic(_PLAN, client=_FakeClient(sink, dims))
        return sink["system"], result
    finally:
        get_settings.cache_clear()


def test_compact_critic_8dim(monkeypatch: pytest.MonkeyPatch) -> None:
    sp, _ = _run(monkeypatch, "compact", DIMENSIONS)
    assert sp == SYSTEM_PROMPT
    assert "retention_design" not in sp and "depth_actionability" not in sp


def test_rich_critic_9dim(monkeypatch: pytest.MonkeyPatch) -> None:
    sp, _ = _run(monkeypatch, "rich", DIMENSIONS_RICH)
    assert sp == RICH_SYSTEM_PROMPT
    assert "depth_actionability" in sp and "retention_design" not in sp


def test_director_critic_10dim(monkeypatch: pytest.MonkeyPatch) -> None:
    sp, result = _run(monkeypatch, "director", DIMENSIONS_DIRECTOR)
    assert sp == DIRECTOR_SYSTEM_PROMPT
    assert "retention_design" in sp
    assert "retention_design" in result["scores"]
