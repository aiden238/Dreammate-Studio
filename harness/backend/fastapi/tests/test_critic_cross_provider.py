"""Phase 31 cross-provider judge — 단위 테스트 (hermetic, mock adapter, 실 API 0).

검증:
  - default Settings → critic_judge_provider == "openai" (기본 byte-identical).
  - run_critic provider="anthropic" + client 미주입 → Claude(mock adapter) 경로 라우팅,
    Claude 점수에서 verdict 도출, OpenAI 미호출(self-review 편향 차단의 배선 증거).
  - _judge_via_anthropic 가 critic system_prompt + json_mode + registry claude-sonnet
    model_id 로 LLMRequest 구성.
  - ANTHROPIC_API_KEY 미설정 → ValueError(안전 차단).
  - client 주입 시 provider 무관하게 그 client 사용(테스트 결정성/byte-identical 보존).

근거: eval/regression_results/2026-06-21-cross-provider-judge.md (false-approve 10/10→0/10).
참조: config.py critic_judge_provider, agents/critic.py _judge_via_anthropic.
"""

from __future__ import annotations

import json
from unittest.mock import MagicMock

import pytest

from backend.fastapi.agents import critic as critic_mod
from backend.fastapi.agents.critic import DIMENSIONS, run_critic
from backend.fastapi.config import Settings
from backend.fastapi.llm.types import LLMResponse, LLMUsage

# _judge_via_anthropic 의 지연 import 대상(module attribute) — monkeypatch seam.
_ADAPTER_PATH = "backend.fastapi.llm.providers.anthropic_adapter.AnthropicAdapter"


def _payload(score: int) -> str:
    """8차원(compact) 모두 동일 점수인 critic 응답 JSON."""
    return json.dumps(
        {
            "scores": {k: score for k in DIMENSIONS},
            "reasons": {k: "r" for k in DIMENSIONS},
            "suggestions": {k: "s" for k in DIMENSIONS},
            "overall_verdict": "approve",
            "blocking_issues": [],
        },
        ensure_ascii=False,
    )


class _FakeAdapter:
    """AnthropicAdapter mock — 실 API 0. 받은 req 를 기록하고 canned JSON 반환."""

    last_req = None
    last_api_key = None
    payload = _payload(2)  # 낮은 점수 → reject (Claude stricter judge 시뮬레이션)

    def __init__(self, *a, **k) -> None:
        pass

    def complete(self, req, *, api_key):  # noqa: ANN001
        type(self).last_req = req
        type(self).last_api_key = api_key
        return LLMResponse(
            text=self.payload,
            model_id=req.model_id,
            alias="",
            usage=LLMUsage(prompt_tokens=11, completion_tokens=22),
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


# ─── 기본값(byte-identical) ───────────────────────────────────────────

def test_default_provider_is_openai() -> None:
    assert Settings().critic_judge_provider == "openai"


# ─── anthropic 라우팅 ────────────────────────────────────────────────

def test_anthropic_routing_uses_claude_and_skips_openai(monkeypatch) -> None:
    _FakeAdapter.last_req = None
    _FakeAdapter.last_api_key = None
    monkeypatch.setattr(_ADAPTER_PATH, _FakeAdapter)
    monkeypatch.setattr(
        critic_mod,
        "get_settings",
        lambda: Settings(critic_judge_provider="anthropic", anthropic_api_key="k"),
    )

    # OpenAI 가 생성되면 즉시 실패 — cross-provider 경로가 OpenAI 를 안 건드림을 보증.
    def _boom(*a, **k):  # noqa: ANN002, ANN003
        raise AssertionError("cross-provider 경로에서 OpenAI 호출 금지")

    monkeypatch.setattr(critic_mod, "OpenAI", _boom)

    out = run_critic({"plan_id": "p"})  # client 미주입 → anthropic 분기

    assert out["overall_verdict"] == "reject"  # Claude 점수 2 → avg 2.0 → reject
    assert out["target_plan_id"] == "p"

    req = _FakeAdapter.last_req
    assert req is not None and req.json_mode is True
    assert "품질 평가자" in req.messages[0].content  # critic system prompt 전달
    assert _FakeAdapter.last_api_key == "k"


def test_anthropic_missing_key_raises(monkeypatch) -> None:
    monkeypatch.setattr(_ADAPTER_PATH, _FakeAdapter)
    monkeypatch.setattr(
        critic_mod,
        "get_settings",
        lambda: Settings(critic_judge_provider="anthropic", anthropic_api_key=""),
    )
    with pytest.raises(ValueError, match="ANTHROPIC_API_KEY"):
        run_critic({"plan_id": "p"})


# ─── client 주입은 provider 와 무관(테스트 결정성/byte-identical) ──────

def test_injected_client_overrides_provider(monkeypatch) -> None:
    monkeypatch.setattr(
        critic_mod,
        "get_settings",
        lambda: Settings(critic_judge_provider="anthropic", anthropic_api_key="k"),
    )
    client = _openai_fake(_payload(4))
    out = run_critic({"plan_id": "p"}, client=client)
    assert out["overall_verdict"] == "approve"  # 주입 client(4점) 사용 → approve
    client.chat.completions.create.assert_called_once()
