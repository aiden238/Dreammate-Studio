"""Phase 15 Slice 3 — gated wiring (output_mode 분기) 검증.

acceptance 매핑:
  - A5: gated wiring — generate/orchestrator/planning 이 output_mode(compact/rich/director) 로 분기.
  - A3-PP: compact/rich byte-identical — effective_output_mode 매핑(rich_output_enabled=True→rich).

핵심 검증 (planning 프롬프트 선택 = S3 wiring 핵심):
  1. output_mode=compact → run_planning 이 compact SYSTEM_PROMPT 사용.
  2. output_mode=rich → RICH_SYSTEM_PROMPT (director 토큰 없음).
  3. output_mode=director → DIRECTOR_SYSTEM_PROMPT (hook_system/scene_breakdown 지시 포함).
  4. backward-compat: rich_output_enabled=True (output_mode 미지정) → rich 프롬프트.
"""
from __future__ import annotations

from typing import Any

import pytest

from backend.fastapi.agents.planning import run_planning
from backend.fastapi.config import get_settings

_PLAN_JSON = (
    '{"plan": {"name": "n", "concept": "c", "hook": "열글자이상의후크문장",'
    ' "flow": [{"beat_index": 0, "beat": "b", "duration_sec": 5, "purpose": "p"},'
    ' {"beat_index": 1, "beat": "b2", "duration_sec": 5, "purpose": "p2"}],'
    ' "pros": "", "risks": "", "approach_label": "informational"}}'
)


class _FakeCompletions:
    def __init__(self, sink: dict[str, Any]) -> None:
        self.sink = sink

    def create(self, **kwargs: Any) -> Any:
        self.sink["system"] = kwargs["messages"][0]["content"]

        class _Msg:
            content = _PLAN_JSON

        class _Choice:
            message = _Msg()

        class _Resp:
            choices = [_Choice()]

        return _Resp()


class _FakeClient:
    def __init__(self, sink: dict[str, Any]) -> None:
        self.chat = type("C", (), {"completions": _FakeCompletions(sink)})()


def _system_prompt_for(monkeypatch: pytest.MonkeyPatch, *, output_mode: str, rich: str) -> str:
    monkeypatch.setenv("OUTPUT_MODE", output_mode)
    monkeypatch.setenv("RICH_OUTPUT_ENABLED", rich)
    get_settings.cache_clear()
    try:
        sink: dict[str, Any] = {}
        run_planning("자취요리 30초 영상", client=_FakeClient(sink))
        return sink["system"]
    finally:
        get_settings.cache_clear()


def test_compact_mode_uses_compact_prompt(monkeypatch: pytest.MonkeyPatch) -> None:
    sp = _system_prompt_for(monkeypatch, output_mode="compact", rich="false")
    assert "hook_variants" not in sp  # rich 토큰 없음
    assert "scene_breakdown" not in sp  # director 토큰 없음


def test_rich_mode_uses_rich_prompt(monkeypatch: pytest.MonkeyPatch) -> None:
    sp = _system_prompt_for(monkeypatch, output_mode="rich", rich="false")
    assert "hook_variants" in sp and "target_audience" in sp  # rich
    assert "scene_breakdown" not in sp  # director 토큰 없음


def test_director_mode_uses_director_prompt(monkeypatch: pytest.MonkeyPatch) -> None:
    sp = _system_prompt_for(monkeypatch, output_mode="director", rich="false")
    assert "hook_system" in sp and "scene_breakdown" in sp  # director
    assert "hook_variants" in sp  # rich 계승


def test_legacy_rich_flag_backward_compat(monkeypatch: pytest.MonkeyPatch) -> None:
    # output_mode 미지정(compact default) + 레거시 rich_output_enabled=True → rich 프롬프트
    sp = _system_prompt_for(monkeypatch, output_mode="compact", rich="true")
    assert "hook_variants" in sp  # rich
    assert "scene_breakdown" not in sp  # director 아님
