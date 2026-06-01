"""LLM Gateway 단위 테스트 — Phase 11 A안 Slice 1 (제안서 §3~§5, §18.A, §12).

검증 대상 (전부 mock — 실 API 호출 0, 실 키 불필요):
  - alias resolve (planning/intent/rewriter/memory → gpt-4o-mini, critic standard→gpt-4o,
    critic cost_saving→gpt-4o-mini, cross_validation→gemini-cross)
  - registry get_model (provider/model_id/json_mode)
  - gateway.complete: mock adapter / mock client 주입 → canonical LLMResponse 반환
  - 에러 정규화: adapter 예외(OpenAIError / 일반 예외) → LLMError
  - graceful: api_key="" → 명시적 LLMError("missing key")
  - ★ resolve_model 이 현 settings default(openai_model_default / openai_model_critic)와
    동일 값 반환 — behavior-preserving 근거 (제안서 §11 M2 / §15 alias drift 방어)

★ 본 Slice 는 gateway 를 만들기만 — agents 미연결. 기존 381 test 무영향.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

import pytest

from backend.fastapi.config import get_settings
from backend.fastapi.llm import (
    LLMError,
    LLMMessage,
    LLMRequest,
    LLMResponse,
    LLMUsage,
    get_gateway,
    get_model,
    resolve_alias,
)
from backend.fastapi.llm import aliases as alias_mod
from backend.fastapi.llm import registry as registry_mod
from backend.fastapi.llm.gateway import LLMGateway
from backend.fastapi.llm.providers.gemini_adapter import GeminiAdapter
from backend.fastapi.llm.providers.openai_adapter import OpenAIAdapter


# ─── Helpers ──────────────────────────────────────────────────────────

def _msgs() -> list[LLMMessage]:
    return [
        LLMMessage(role="system", content="당신은 평가자다."),
        LLMMessage(role="user", content="이 plan을 평가해줘."),
    ]


def _make_fake_openai_client(content: str) -> MagicMock:
    """OpenAI client mock — chat.completions.create 응답 1개 주입 (test_critic.py 패턴)."""
    client = MagicMock()
    msg = MagicMock()
    msg.content = content
    choice = MagicMock()
    choice.message = msg
    usage = MagicMock()
    usage.prompt_tokens = 42
    usage.completion_tokens = 7
    response = MagicMock()
    response.choices = [choice]
    response.usage = usage
    client.chat.completions.create.return_value = response
    return client


def _make_fake_gemini_client(text: str) -> MagicMock:
    """genai.Client mock — models.generate_content 응답 1개 주입."""
    client = MagicMock()
    meta = MagicMock()
    meta.prompt_token_count = 30
    meta.candidates_token_count = 5
    response = MagicMock()
    response.text = text
    response.usage_metadata = meta
    client.models.generate_content.return_value = response
    return client


# ─── alias resolve 단위 (제안서 §5.2 / §18.A) ─────────────────────────

def test_resolve_workhorse_aliases() -> None:
    assert resolve_alias("planning") == "gpt-4o-mini"
    assert resolve_alias("intent") == "gpt-4o-mini"
    assert resolve_alias("rewriter") == "gpt-4o-mini"
    assert resolve_alias("memory") == "gpt-4o-mini"


def test_resolve_critic_standard_vs_cost_saving() -> None:
    assert resolve_alias("critic", mode="standard") == "gpt-4o"
    assert resolve_alias("critic", mode="cost_saving") == "gpt-4o-mini"


def test_resolve_critic_default_mode_is_standard() -> None:
    # mode 미지정 default="standard" → gpt-4o.
    assert resolve_alias("critic") == "gpt-4o"


def test_resolve_critic_unknown_mode_falls_back_to_standard() -> None:
    # graceful: 미지원 mode → standard.
    assert resolve_alias("critic", mode="premium") == "gpt-4o"


def test_resolve_cross_validation_alias() -> None:
    # ★ A안 cross_validation → gemini-cross (gated, default 사용처 없음).
    assert resolve_alias("cross_validation") == "gemini-cross"


def test_resolve_unknown_alias_raises() -> None:
    with pytest.raises(KeyError):
        resolve_alias("nonexistent_alias")


def test_known_aliases_list() -> None:
    known = alias_mod.known_aliases()
    for a in ("planning", "intent", "rewriter", "memory", "critic", "cross_validation"):
        assert a in known


# ─── B안(Phase 12 S2a): 3-plan 다양성 슬롯 alias (★ gated, 직접 연결 X) ──

def test_resolve_plan_diversity_slot_aliases() -> None:
    # 슬롯별 provider 다양성: OpenAI / Anthropic / Google.
    assert alias_mod.resolve("plan_primary") == "gpt-4o-mini"
    assert alias_mod.resolve("plan_secondary") == "claude-haiku"
    assert alias_mod.resolve("plan_tertiary") == "gemini-flash"


def test_known_aliases_includes_plan_diversity_slots() -> None:
    known = alias_mod.known_aliases()
    for a in ("plan_primary", "plan_secondary", "plan_tertiary"):
        assert a in known


def test_plan_diversity_aliases_roundtrip_to_registry() -> None:
    # alias → registry key → get_model: KeyError 없이 dict 반환 + provider 검증.
    primary = registry_mod.get_model(alias_mod.resolve("plan_primary"))
    assert primary["provider"] == registry_mod.PROVIDER_OPENAI

    secondary = registry_mod.get_model(alias_mod.resolve("plan_secondary"))
    assert secondary["provider"] == registry_mod.PROVIDER_ANTHROPIC

    tertiary = registry_mod.get_model(alias_mod.resolve("plan_tertiary"))
    assert tertiary["provider"] == registry_mod.PROVIDER_GOOGLE


def test_plan_diversity_aliases_ignore_tier_and_mode() -> None:
    # 단일 str alias 이므로 tier/mode 파라미터는 결과에 무영향.
    assert alias_mod.resolve("plan_secondary", tier="paid", mode="cost_saving") == "claude-haiku"


def test_plan_diversity_aliases_preserve_existing_behavior() -> None:
    # ★ behavior-preserving 회귀 가드: 기존 alias 동작 불변 재확인.
    assert alias_mod.resolve("planning") == "gpt-4o-mini"
    assert alias_mod.resolve("critic", mode="standard") == "gpt-4o"


# ─── registry get_model 단위 (제안서 §5.1) ────────────────────────────

def test_registry_openai_models() -> None:
    mini = get_model("gpt-4o-mini")
    assert mini["provider"] == "openai"
    assert mini["model_id"] == "gpt-4o-mini"
    assert mini["json_mode"] is True

    full = get_model("gpt-4o")
    assert full["provider"] == "openai"
    assert full["model_id"] == "gpt-4o"


def test_registry_gemini_cross_uses_config_field() -> None:
    # ★ gemini model_id 는 config Field(cross_validation_model)로 교체 가능 (사용자 확정).
    gem = get_model("gemini-cross")
    assert gem["provider"] == "google"
    assert gem["model_id"] == get_settings().cross_validation_model
    assert gem["json_mode"] is True


def test_registry_get_model_returns_copy() -> None:
    # 호출자가 mutate 해도 카탈로그 불변.
    a = get_model("gpt-4o-mini")
    a["model_id"] = "tampered"
    b = get_model("gpt-4o-mini")
    assert b["model_id"] == "gpt-4o-mini"


def test_registry_unknown_key_raises() -> None:
    with pytest.raises(KeyError):
        get_model("no-such-model")


def test_registry_known_keys() -> None:
    keys = registry_mod.known_keys()
    assert {"gpt-4o-mini", "gpt-4o", "gemini-cross"}.issubset(set(keys))


# ─── ★ behavior-preserving: resolve_model == 현 settings default ──────

def test_resolve_model_planning_equals_settings_default() -> None:
    """resolve_model("planning") == settings.openai_model_default (제안서 §11 M2)."""
    gw = get_gateway()
    settings = get_settings()
    assert gw.resolve_model("planning") == settings.openai_model_default


def test_resolve_model_critic_standard_equals_settings_critic() -> None:
    """resolve_model("critic", mode="standard") == settings.openai_model_critic."""
    gw = get_gateway()
    settings = get_settings()
    assert gw.resolve_model("critic", mode="standard") == settings.openai_model_critic


def test_resolve_model_intent_rewriter_memory_equal_default() -> None:
    gw = get_gateway()
    settings = get_settings()
    for alias in ("intent", "rewriter", "memory"):
        assert gw.resolve_model(alias) == settings.openai_model_default


def test_resolve_model_cross_validation_equals_config_field() -> None:
    gw = get_gateway()
    settings = get_settings()
    assert gw.resolve_model("cross_validation") == settings.cross_validation_model


# ─── gateway.complete: mock adapter 주입 → LLMResponse ────────────────

class _StubAdapter:
    """ProviderAdapter mock — complete() 호출 인자 기록 + 고정 응답."""

    provider = "stub"

    def __init__(self, text: str = '{"ok": true}') -> None:
        self.text = text
        self.last_req: LLMRequest | None = None
        self.last_api_key: str | None = None

    def complete(self, req: LLMRequest, *, api_key: str) -> LLMResponse:
        self.last_req = req
        self.last_api_key = api_key
        return LLMResponse(
            text=self.text,
            model_id=req.model_id,
            alias="",
            usage=LLMUsage(prompt_tokens=11, completion_tokens=3),
        )


def test_complete_with_mock_adapter_returns_canonical_response() -> None:
    gw = LLMGateway()
    stub = _StubAdapter(text='{"verdict": "approve"}')
    resp = gw.complete("planning", _msgs(), adapter=stub)

    assert isinstance(resp, LLMResponse)
    assert resp.text == '{"verdict": "approve"}'
    assert resp.model_id == "gpt-4o-mini"  # planning → gpt-4o-mini
    assert resp.alias == "planning"  # gateway 가 alias 채움
    assert resp.usage.total_tokens == 14


def test_complete_maps_alias_to_model_in_request() -> None:
    gw = LLMGateway()
    stub = _StubAdapter()
    gw.complete("critic", _msgs(), mode="standard", adapter=stub)
    assert stub.last_req is not None
    assert stub.last_req.model_id == "gpt-4o"  # critic standard


def test_complete_cost_saving_critic_uses_mini() -> None:
    gw = LLMGateway()
    stub = _StubAdapter()
    gw.complete("critic", _msgs(), mode="cost_saving", adapter=stub)
    assert stub.last_req is not None
    assert stub.last_req.model_id == "gpt-4o-mini"


def test_complete_accepts_dict_messages() -> None:
    gw = LLMGateway()
    stub = _StubAdapter()
    resp = gw.complete(
        "planning",
        [{"role": "user", "content": "hi"}],
        adapter=stub,
    )
    assert resp.model_id == "gpt-4o-mini"
    assert stub.last_req is not None
    assert stub.last_req.messages[0].content == "hi"


def test_complete_passes_json_mode_and_params() -> None:
    gw = LLMGateway()
    stub = _StubAdapter()
    gw.complete(
        "planning", _msgs(), temperature=0.2, max_tokens=900, json_mode=False, adapter=stub,
    )
    assert stub.last_req is not None
    assert stub.last_req.temperature == 0.2
    assert stub.last_req.max_tokens == 900
    assert stub.last_req.json_mode is False


# ─── gateway.complete via mock OpenAI client (DI) ─────────────────────

def test_complete_openai_via_mock_client() -> None:
    gw = LLMGateway()
    client = _make_fake_openai_client('{"plan": {}}')
    resp = gw.complete("planning", _msgs(), client=client)

    assert resp.text == '{"plan": {}}'
    assert resp.model_id == "gpt-4o-mini"
    assert resp.alias == "planning"
    assert resp.usage.prompt_tokens == 42
    assert resp.usage.completion_tokens == 7
    # OpenAI SDK shape (기존 agents 와 동일): response_format json_object 주입 확인.
    _, kwargs = client.chat.completions.create.call_args
    assert kwargs["model"] == "gpt-4o-mini"
    assert kwargs["response_format"] == {"type": "json_object"}


def test_complete_openai_json_mode_false_omits_response_format() -> None:
    gw = LLMGateway()
    client = _make_fake_openai_client("plain text")
    gw.complete("planning", _msgs(), json_mode=False, client=client)
    _, kwargs = client.chat.completions.create.call_args
    assert "response_format" not in kwargs


# ─── gateway.complete via mock Gemini client (DI, cross_validation) ───

def test_complete_gemini_cross_validation_via_mock_client() -> None:
    gw = LLMGateway()
    client = _make_fake_gemini_client('{"cross_check": "agree"}')
    resp = gw.complete("cross_validation", _msgs(), client=client)

    assert resp.text == '{"cross_check": "agree"}'
    assert resp.alias == "cross_validation"
    assert resp.model_id == get_settings().cross_validation_model
    assert resp.usage.prompt_tokens == 30
    assert resp.usage.completion_tokens == 5
    # Gemini SDK shape: response_mime_type application/json (json_mode).
    _, kwargs = client.models.generate_content.call_args
    assert kwargs["config"]["response_mime_type"] == "application/json"
    # system 메시지는 system_instruction 으로 분리.
    assert kwargs["config"]["system_instruction"] == "당신은 평가자다."


# ─── 에러 정규화: adapter 예외 → LLMError (제안서 §12) ────────────────

def test_openai_adapter_error_normalized_to_llmerror() -> None:
    from openai import OpenAIError

    client = MagicMock()
    client.chat.completions.create.side_effect = OpenAIError("boom")
    adapter = OpenAIAdapter(client=client)
    req = LLMRequest(messages=_msgs(), model_id="gpt-4o-mini")

    with pytest.raises(LLMError) as ei:
        adapter.complete(req, api_key="sk-x")
    assert ei.value.provider == "openai"
    assert ei.value.model_id == "gpt-4o-mini"


def test_gemini_adapter_error_normalized_to_llmerror() -> None:
    client = MagicMock()
    client.models.generate_content.side_effect = RuntimeError("gemini boom")
    adapter = GeminiAdapter(client=client)
    req = LLMRequest(messages=_msgs(), model_id="gemini-x")

    with pytest.raises(LLMError) as ei:
        adapter.complete(req, api_key="g-x")
    assert ei.value.provider == "google"
    assert ei.value.model_id == "gemini-x"


def test_gateway_propagates_adapter_llmerror() -> None:
    gw = LLMGateway()

    class _BoomAdapter:
        provider = "stub"

        def complete(self, req: LLMRequest, *, api_key: str) -> LLMResponse:
            raise LLMError("stub", req.model_id, "adapter failed")

    with pytest.raises(LLMError):
        gw.complete("planning", _msgs(), adapter=_BoomAdapter())


# ─── graceful: api_key="" → 명시적 LLMError ───────────────────────────

def test_complete_missing_openai_key_raises_graceful_llmerror(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # adapter/client 미주입 + 키 없음 → graceful LLMError("missing key").
    monkeypatch.setenv("OPENAI_API_KEY", "")
    get_settings.cache_clear()
    gw = LLMGateway()
    with pytest.raises(LLMError) as ei:
        gw.complete("planning", _msgs())
    assert "key" in ei.value.message.lower()
    assert ei.value.provider == "openai"
    get_settings.cache_clear()


def test_complete_missing_google_key_raises_graceful_llmerror(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("GOOGLE_API_KEY", "")
    get_settings.cache_clear()
    gw = LLMGateway()
    with pytest.raises(LLMError) as ei:
        gw.complete("cross_validation", _msgs())
    assert ei.value.provider == "google"
    get_settings.cache_clear()


def test_complete_with_client_di_bypasses_key_check(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # client 주입 시 키 없어도 graceful LLMError 미발생 (DI 우선).
    monkeypatch.setenv("OPENAI_API_KEY", "")
    get_settings.cache_clear()
    gw = LLMGateway()
    client = _make_fake_openai_client("{}")
    resp = gw.complete("planning", _msgs(), client=client)
    assert resp.model_id == "gpt-4o-mini"
    get_settings.cache_clear()


# ─── get_gateway 싱글톤 ───────────────────────────────────────────────

def test_get_gateway_singleton() -> None:
    assert get_gateway() is get_gateway()
