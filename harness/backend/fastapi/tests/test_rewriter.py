"""Phase 4.5 Slice 2 — Rewriter agent (P-008) unit tests.

검증 항목 (acceptance.md A1 매핑):
  - 기본 revise: LLM 응답 dict → 개선된 plan dict 반환 + _rewriter_model 메타
  - graceful fallback: LLM exception → 원본 plan + _rewriter_warning
  - non-dict 응답 fallback: LLM이 JSON string 등 비-dict 반환 → 원본 plan + warning
  - plan_id / option_index 보존: LLM이 빠뜨려도 원본에서 복원
  - 빈 JSON 응답 (dict) → 원본 plan 의 meta 보존 + _rewriter_model 추가
"""
from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.fastapi.agents.rewriter import (
    PROMPT_ID,
    PROMPT_VERSION,
    run_rewriter,
)


def _make_fake_client(response_payload: str) -> Any:
    """Minimal stub mimicking AsyncOpenAI client with chat.completions.create."""
    client = MagicMock()

    async def _create(**kwargs: Any) -> Any:
        mock_message = MagicMock()
        mock_message.content = response_payload
        mock_choice = MagicMock()
        mock_choice.message = mock_message
        mock_completion = MagicMock()
        mock_completion.choices = [mock_choice]
        return mock_completion

    client.chat = MagicMock()
    client.chat.completions = MagicMock()
    client.chat.completions.create = AsyncMock(side_effect=_create)
    return client


# ─── 메타 ────────────────────────────────────────────────────────────


def test_rewriter_prompt_meta_constants() -> None:
    """P-008 / v1.0.0 메타 노출 확인."""
    assert PROMPT_ID == "P-008"
    assert PROMPT_VERSION == "v1.0.0"


# ─── 기본 동작 ────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_basic_revise_returns_dict() -> None:
    """LLM 응답이 정상 dict → 개선된 plan dict 반환."""
    plan = {
        "plan_id": "plan-uuid",
        "option_index": 0,
        "name": "원본",
        "hook": "약한 hook",
        "flow": [{"beat_index": 0, "beat": "intro", "duration_sec": 3, "purpose": "도입"}],
    }
    verdict = {
        "overall_verdict": "revise",
        "blocking_issues": ["hook 약함"],
        "suggestions": {"hook_strength": "질문형 hook 권장"},
    }
    fake_response = (
        '{"name": "개선", "hook": "질문형 강한 hook 적용",'
        ' "flow": [{"beat_index": 0, "beat": "강화 도입", "duration_sec": 3, "purpose": "관심"}]}'
    )
    client = _make_fake_client(fake_response)
    result = await run_rewriter(plan, verdict, client=client)

    assert isinstance(result, dict)
    assert result["name"] == "개선"
    assert result["hook"] == "질문형 강한 hook 적용"
    assert result["_rewriter_model"] == "gpt-4o-mini"
    # plan_id / option_index 보존
    assert result["plan_id"] == "plan-uuid"
    assert result["option_index"] == 0


@pytest.mark.asyncio
async def test_rewriter_uses_custom_model() -> None:
    """model 파라미터 변경 시 _rewriter_model 메타에 반영."""
    plan = {"name": "원본"}
    verdict = {"overall_verdict": "revise"}
    client = _make_fake_client('{"name": "개선"}')
    result = await run_rewriter(plan, verdict, client=client, model="gpt-4o")
    assert result["_rewriter_model"] == "gpt-4o"


# ─── graceful 실패 경로 ───────────────────────────────────────────────


@pytest.mark.asyncio
async def test_rewriter_failure_returns_fallback() -> None:
    """LLM 호출 자체가 exception → 원본 plan + _rewriter_warning."""
    plan = {"plan_id": "p1", "name": "원본", "hook": "원본 hook"}
    verdict = {"overall_verdict": "revise"}

    client = MagicMock()
    client.chat = MagicMock()
    client.chat.completions = MagicMock()
    client.chat.completions.create = AsyncMock(
        side_effect=RuntimeError("network down"),
    )

    result = await run_rewriter(plan, verdict, client=client)

    # 원본 plan 보존
    assert result["name"] == "원본"
    assert result["hook"] == "원본 hook"
    assert result.get("_rewriter_warning", "").startswith("rewriter_failed:")
    assert "RuntimeError" in result["_rewriter_warning"]


@pytest.mark.asyncio
async def test_rewriter_non_dict_response_falls_back() -> None:
    """LLM이 JSON string (객체 아님) → 원본 plan + warning."""
    plan = {"name": "원본", "hook": "원본 hook"}
    verdict = {"overall_verdict": "revise"}
    # JSON parsing 자체는 성공 (string도 valid JSON) — but not dict.
    client = _make_fake_client('"plain string not dict"')
    result = await run_rewriter(plan, verdict, client=client)

    assert result["name"] == "원본"
    assert "_rewriter_warning" in result
    assert result["_rewriter_warning"].startswith("rewriter_failed:")


@pytest.mark.asyncio
async def test_rewriter_invalid_json_falls_back() -> None:
    """LLM이 JSON parse 불가능한 응답 → fallback."""
    plan = {"name": "원본"}
    verdict = {"overall_verdict": "revise"}
    client = _make_fake_client("not a json at all {")
    result = await run_rewriter(plan, verdict, client=client)

    assert result["name"] == "원본"
    assert "_rewriter_warning" in result


@pytest.mark.asyncio
async def test_rewriter_empty_dict_response_preserves_plan_id() -> None:
    """LLM이 빈 dict {} 반환 → plan_id / option_index 복원 + _rewriter_model 추가."""
    plan = {
        "plan_id": "plan-xyz",
        "option_index": 2,
        "name": "원본",
    }
    verdict = {"overall_verdict": "revise"}
    client = _make_fake_client("{}")
    result = await run_rewriter(plan, verdict, client=client)

    # 빈 dict 라도 plan_id / option_index 가 보존 (rewriter.py 의 preserve_key 로직)
    assert result["plan_id"] == "plan-xyz"
    assert result["option_index"] == 2
    assert result["_rewriter_model"] == "gpt-4o-mini"
    # warning 없음 — 정상 응답
    assert "_rewriter_warning" not in result
