"""Phase 10 Slice 3 — eval LLM mode capability (ADR-033 §1) 단위 테스트.

실 LLM eval mode 의 capability 경로 검증 (★ 실 API 호출 0):
  - resolve_mode: mock default / 환경변수 EVAL_MODE / real graceful fallback (키·caller 부재)
  - has_real_key: 키 읽기만 (placeholder / 빈 문자열 graceful)
  - run_golden_set_eval(mode="real", ctx=...): caller 주입 + 키 stub → real 분기 호출 검증
    (실 client import/network 0 — 주입된 stub caller 로만 분기 확인)

forbidden 무수정 (additive): agents/schemas/orchestration/routers/db/apps/web/golden_set 케이스 로직.

★ 본 test 는 실 LLM/네트워크를 절대 호출하지 않는다:
  - mock 경로: 기존 _mock_envelope_for_case (deterministic).
  - real 경로: monkeypatch 없이, ScoreContext.llm_caller 에 순수 파이썬 stub 주입 + env dict 로
    가짜 키 제공. stub 은 결정적 dict 반환 (실 API 미접촉). 분기 진입만 검증.
"""
from __future__ import annotations

from typing import Any

import pytest

from backend.fastapi.eval import (
    MODE_MOCK,
    MODE_REAL,
    ScoreContext,
    has_real_key,
    resolve_mode,
    run_golden_set_eval,
)
from backend.fastapi.eval.runner import _mock_envelope_for_case


# ── resolve_mode ─────────────────────────────────────────────────────

def test_resolve_mode_default_mock() -> None:
    """ctx 없음 → default mock (Phase 9.5 동작 불변)."""
    assert resolve_mode(ScoreContext(env={})) == MODE_MOCK


def test_resolve_mode_explicit_mock() -> None:
    """requested_mode='mock' → mock."""
    assert resolve_mode(ScoreContext(requested_mode="mock", env={})) == MODE_MOCK


def test_resolve_mode_env_default() -> None:
    """EVAL_MODE 환경변수로 default 지정 (requested 미지정 시). caller 없으면 fallback."""
    ctx = ScoreContext(env={"EVAL_MODE": "real"})  # caller 없음 → mock fallback
    assert resolve_mode(ctx) == MODE_MOCK


def test_resolve_mode_real_no_caller_fallback() -> None:
    """real 요청 + caller 미주입 → mock graceful fallback (CI 안전)."""
    ctx = ScoreContext(requested_mode="real", env={"OPENAI_API_KEY": "sk-fake"})
    assert resolve_mode(ctx) == MODE_MOCK


def test_resolve_mode_real_no_key_fallback() -> None:
    """real 요청 + caller 있음 + 키 미설정 → mock graceful fallback."""
    ctx = ScoreContext(
        requested_mode="real",
        llm_caller=lambda case: {},
        env={},  # 키 없음
    )
    assert resolve_mode(ctx) == MODE_MOCK


def test_resolve_mode_real_active_with_caller_and_key() -> None:
    """real 요청 + caller 주입 + 키 존재 → real 활성 (opt-in capability)."""
    ctx = ScoreContext(
        requested_mode="real",
        llm_caller=lambda case: {},
        env={"OPENAI_API_KEY": "sk-fake-test-only"},
    )
    assert resolve_mode(ctx) == MODE_REAL


def test_resolve_mode_invalid_raises() -> None:
    """지원하지 않는 모드 → ValueError."""
    with pytest.raises(ValueError):
        resolve_mode(ScoreContext(requested_mode="bogus", env={}))


# ── has_real_key ─────────────────────────────────────────────────────

def test_has_real_key_present() -> None:
    assert has_real_key(ScoreContext(env={"OPENAI_API_KEY": "sk-x"})) is True
    assert has_real_key(ScoreContext(env={"ANTHROPIC_API_KEY": "ak-x"})) is True


def test_has_real_key_absent() -> None:
    assert has_real_key(ScoreContext(env={})) is False


def test_has_real_key_blank_is_absent() -> None:
    """빈 문자열/공백 키 → 미설정 (placeholder .env 안전)."""
    assert has_real_key(ScoreContext(env={"OPENAI_API_KEY": "   "})) is False
    assert has_real_key(ScoreContext(env={"OPENAI_API_KEY": ""})) is False


# ── run_golden_set_eval real 분기 (stub caller — 실 호출 0) ───────────

def _stub_real_caller(case: dict[str, Any]) -> dict[str, Any]:
    """real eval 의 LLM caller stub — 실 API 미접촉. 결정적 mock envelope 재사용.

    운영에서는 OpenAI 8차원 채점 → Envelope 합성이지만, test 는 분기 진입만 검증하므로
    deterministic mock envelope 를 그대로 반환 (schema 통과 보장).
    """
    _stub_real_caller.calls.append(case.get("id"))  # type: ignore[attr-defined]
    return _mock_envelope_for_case(case)


_stub_real_caller.calls = []  # type: ignore[attr-defined]


def test_run_eval_real_branch_uses_injected_caller() -> None:
    """mode='real' + stub caller + 키 → real 분기로 caller 호출 (실 LLM/네트워크 0)."""
    _stub_real_caller.calls = []  # type: ignore[attr-defined]
    cases = [
        {"id": "GS-001", "priority": "P0", "mode": "discovery",
         "prompt_target": "P-001", "input": {}, "expected_properties": {}},
        {"id": "GS-002", "priority": "P0", "mode": "quick",
         "prompt_target": "P-005", "input": {}, "expected_properties": {}},
    ]
    ctx = ScoreContext(
        requested_mode="real",
        llm_caller=_stub_real_caller,
        env={"OPENAI_API_KEY": "sk-fake-test-only"},
    )
    result = run_golden_set_eval(mode="real", cases=cases, ctx=ctx)
    # real 분기 진입 → stub caller 가 각 케이스로 호출됨 (실 호출 아님).
    assert result["mode"] == "real"
    assert _stub_real_caller.calls == ["GS-001", "GS-002"]  # type: ignore[attr-defined]
    assert result["summary"]["total"] == 2
    assert result["gate"]["passed"] is True


def test_run_eval_real_request_without_caller_is_mock() -> None:
    """mode='real' 인데 ctx 미주입 → 실효 mock (CI 기본 경로 — 실 호출 0 입증)."""
    cases = [
        {"id": "GS-001", "priority": "P0", "mode": "discovery",
         "prompt_target": "P-001", "input": {}, "expected_properties": {}},
    ]
    result = run_golden_set_eval(mode="real", cases=cases)
    assert result["mode"] == "mock"


def test_run_eval_default_mode_unchanged() -> None:
    """기본 호출(mode 미지정) → mock 결과 — Phase 9.5 동작 불변 (behavior-preserving)."""
    cases = [
        {"id": "GS-001", "priority": "P0", "mode": "discovery",
         "prompt_target": "P-001", "input": {}, "expected_properties": {}},
    ]
    result = run_golden_set_eval(cases=cases)
    assert result["mode"] == "mock"
    assert result["gate"]["passed"] is True
