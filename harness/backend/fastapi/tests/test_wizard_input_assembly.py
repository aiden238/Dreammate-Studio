"""Phase 14 Slice 1 — 위저드 wizard_data → 생성 user_input additive 조립 검증.

acceptance 매핑:
  - A1: 백엔드 wizard_data 조립(additive) — initial_input 없고 wizard_data 있으면 step 입력 조립.
  - A2-PP: 랜딩 `/` byte-identical — initial_input 있으면 wizard_data 무시(기존 경로 불변).

핵심 검증:
  1. build_user_input_from_wizard 순수 함수: 빈 입력 / 순서(known→sorted) / card·extra / 빈 값 skip.
  2. generate_plan 우선순위: wizard_data 사용(initial_input 없을 때) / initial_input 우선(랜딩 불변).
"""
from __future__ import annotations

from typing import Any

import pytest

from backend.fastapi.orchestration import generate_plan
from backend.fastapi.orchestration.moa_orchestrator import build_user_input_from_wizard
from backend.fastapi.schemas.plans import GenerateRequest


# ─── 1. build_user_input_from_wizard 순수 함수 ───────────────────────


def test_build_empty_returns_blank() -> None:
    assert build_user_input_from_wizard(None) == ""
    assert build_user_input_from_wizard({}) == ""


def test_build_quick_steps_ordered() -> None:
    wd = {
        "quick.direction": {"user_input": "방향 승인 텍스트", "extra": {}},
        "quick.initial": {"user_input": "자취요리 30초 영상", "extra": {}},
    }
    out = build_user_input_from_wizard(wd)
    # known 순서: quick.initial 이 quick.direction 보다 먼저.
    assert out.index("자취요리 30초 영상") < out.index("방향 승인 텍스트")


def test_build_discovery_card_and_extra() -> None:
    wd = {
        "step2": {"selected_card_id": "domain-cooking", "extra": {}},
        "step1": {"selected_card_id": "brand-A", "extra": {"note": "감성"}},
        "step7": {"user_input": "최종 방향", "extra": {}},
    }
    lines = build_user_input_from_wizard(wd).splitlines()
    assert "brand-A" in lines[0] and "note: 감성" in lines[0]
    assert "domain-cooking" in lines[1]
    assert lines[2] == "최종 방향"


def test_build_unknown_steps_sorted_after_known() -> None:
    wd = {
        "zzz": {"user_input": "Z"},
        "step1": {"user_input": "one"},
        "aaa": {"user_input": "A"},
    }
    assert build_user_input_from_wizard(wd).splitlines() == ["one", "A", "Z"]


def test_build_skips_empty_values() -> None:
    wd = {"step1": {"selected_card_id": "", "user_input": "", "extra": {"k": "", "k2": None, "k3": []}}}
    assert build_user_input_from_wizard(wd) == ""


def test_build_ignores_non_dict_step() -> None:
    wd = {"step1": "not-a-dict", "step2": {"user_input": "ok"}}
    assert build_user_input_from_wizard(wd) == "ok"


# ─── 2. generate_plan 입력 우선순위 (orchestrator 통합) ──────────────


def _capture_intent(monkeypatch: pytest.MonkeyPatch, sink: dict[str, Any]) -> None:
    """run_intent 인자(user_input)를 캡처하고 ValueError 로 즉시 중단(502 graceful)."""

    def fake_intent(user_input: str, *a: Any, **k: Any) -> dict[str, Any]:
        sink["user_input"] = user_input
        raise ValueError("stop-after-capture")

    monkeypatch.setattr("backend.fastapi.routers.plans.run_intent", fake_intent)


@pytest.mark.asyncio
async def test_generate_uses_wizard_data_when_no_initial_input(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sink: dict[str, Any] = {}
    _capture_intent(monkeypatch, sink)
    plan_entry = {
        "plan_id": "p", "status": "created", "locale": "ko-KR",
        "initial_input": None,
        "wizard_data": {"quick.initial": {"user_input": "자취요리 30초 영상"}},
        "envelope": None,
    }
    await generate_plan("p", plan_entry, GenerateRequest())
    assert sink["user_input"] == "자취요리 30초 영상"


@pytest.mark.asyncio
async def test_generate_initial_input_wins_landing_byte_identical(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """initial_input(랜딩) 있으면 wizard_data 무시 — 랜딩 경로 byte-identical."""
    sink: dict[str, Any] = {}
    _capture_intent(monkeypatch, sink)
    plan_entry = {
        "plan_id": "p", "status": "created", "locale": "ko-KR",
        "initial_input": "유튜브 쇼츠 만들기",
        "wizard_data": {"quick.initial": {"user_input": "무시되어야 함"}},
        "envelope": None,
    }
    await generate_plan("p", plan_entry, GenerateRequest())
    assert sink["user_input"] == "유튜브 쇼츠 만들기"


@pytest.mark.asyncio
async def test_generate_blank_fallback_preserved(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """initial_input·wizard_data 둘 다 없으면 기존 '(빈 입력)' 폴백 유지."""
    sink: dict[str, Any] = {}
    _capture_intent(monkeypatch, sink)
    plan_entry = {
        "plan_id": "p", "status": "created", "locale": "ko-KR",
        "initial_input": None, "wizard_data": {}, "envelope": None,
    }
    await generate_plan("p", plan_entry, GenerateRequest())
    assert sink["user_input"] == "(빈 입력)"
