"""Phase 20 Slice 3 — gated wiring (output_mode=commercial_viral 분기) 검증.

acceptance 매핑:
  - A3: gated wiring — planning 이 effective_output_mode=commercial_viral 에서 COMMERCIAL_SYSTEM_PROMPT 사용.
  - A6 byte-identical — compact/rich/director 경로는 commercial-only 토큰 미오염(누수 0).

핵심 검증 (planning 프롬프트 선택 = S3 wiring 핵심):
  1. output_mode=commercial_viral → run_planning 이 commercial 프롬프트(market_context/measurement_plan) 사용.
  2. director 슬롯 계승 (commercial = director + 상업).
  3. compact/rich/director 경로는 commercial-only 토큰 미사용 (byte-identical 보존).
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
        self.sink["max_tokens"] = kwargs.get("max_tokens")

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


def _call(monkeypatch: pytest.MonkeyPatch, *, output_mode: str) -> dict[str, Any]:
    monkeypatch.setenv("OUTPUT_MODE", output_mode)
    monkeypatch.setenv("RICH_OUTPUT_ENABLED", "false")
    get_settings.cache_clear()
    try:
        sink: dict[str, Any] = {}
        run_planning("동네 카페 런칭 쇼츠", client=_FakeClient(sink))
        return sink
    finally:
        get_settings.cache_clear()


_COMMERCIAL_ONLY = ["market_context", "audience_psychology", "commercial_conversion", "measurement_plan"]


def test_commercial_mode_uses_commercial_prompt(monkeypatch: pytest.MonkeyPatch) -> None:
    sp = _call(monkeypatch, output_mode="commercial_viral")["system"]
    for token in _COMMERCIAL_ONLY:
        assert token in sp, f"commercial 프롬프트에 '{token}' 미포함"
    # director + rich 계승
    assert "scene_breakdown" in sp and "hook_system" in sp
    assert "hook_variants" in sp and "target_audience" in sp


def test_commercial_mode_bumps_max_tokens(monkeypatch: pytest.MonkeyPatch) -> None:
    # ★ commercial 출력(10슬롯+7필드 scene)은 1500 절단 방지 위해 상향.
    assert _call(monkeypatch, output_mode="commercial_viral")["max_tokens"] == 4500


def test_director_mode_not_polluted_by_commercial(monkeypatch: pytest.MonkeyPatch) -> None:
    sp = _call(monkeypatch, output_mode="director")["system"]
    for token in _COMMERCIAL_ONLY:
        assert token not in sp, f"director 프롬프트에 commercial 토큰 '{token}' 오염"
    assert "scene_breakdown" in sp  # director 슬롯은 유지


def test_compact_rich_byte_identical_no_commercial(monkeypatch: pytest.MonkeyPatch) -> None:
    for mode in ("compact", "rich"):
        sink = _call(monkeypatch, output_mode=mode)
        sp = sink["system"]
        for token in _COMMERCIAL_ONLY:
            assert token not in sp, f"{mode} 프롬프트에 commercial 토큰 '{token}' 오염"
        # compact/rich 는 max_tokens 1500 불변 (byte-identical)
        assert sink["max_tokens"] == 1500
