"""Anthropic (Claude) adapter 단위 테스트 — Phase 11 B안 Slice 1 (제안서 §8 / §18.B).

검증 대상 (전부 mock — 실 API 호출 0, 실 키 불필요):
  - AnthropicAdapter.complete: mock client 주입 → messages.create 호출 인자 검증
    (system 분리 / max_tokens / model / temperature) + LLMResponse 파싱(text/usage)
  - JSON 모드: response_format 부재 → system 지시문만 덧붙여 JSON 유도 (assistant
    prefill 미사용 — Phase 11 B안 sonnet-4-6 prefill 미지원 400 회피). 모델이 완전한 JSON 을
    직접 반환하므로 응답을 그대로 파싱하고 messages 는 user turn 으로 끝난다.
  - system/user/assistant role 매핑 (system → system= 파라미터, 나머지 → messages)
  - 예외(anthropic.AnthropicError 등) → LLMError 정규화
  - registry: claude-haiku / claude-sonnet 항목 (provider=anthropic, config Field model_id)
  - gateway.complete 가 anthropic provider 를 AnthropicAdapter 로 dispatch (mock client)
  - graceful: anthropic_api_key="" → 명시적 LLMError("missing key")

★ behavior-preserving: 본 Slice 는 adapter/registry 항목을 만들기만 — 기존 agents 미연결.
  default alias 표에 claude 미등록(자동 호출 경로 0). 기존 435 test 무영향.
★ 전부 mock — 실 anthropic API 0, 실 키 0.
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
    get_model,
)
from backend.fastapi.llm import registry as registry_mod
from backend.fastapi.llm.gateway import LLMGateway
from backend.fastapi.llm.providers.anthropic_adapter import AnthropicAdapter


# ─── Helpers ──────────────────────────────────────────────────────────

def _msgs() -> list[LLMMessage]:
    return [
        LLMMessage(role="system", content="당신은 평가자다."),
        LLMMessage(role="user", content="이 plan을 평가해줘."),
    ]


def _make_fake_anthropic_client(text: str) -> MagicMock:
    """anthropic.Anthropic client mock — messages.create 응답 1개 주입.

    response.content = [TextBlock(type="text", text=...)],
    response.usage = {input_tokens, output_tokens}.
    """
    client = MagicMock()
    block = MagicMock()
    block.type = "text"
    block.text = text
    usage = MagicMock()
    usage.input_tokens = 25
    usage.output_tokens = 9
    response = MagicMock()
    response.content = [block]
    response.usage = usage
    client.messages.create.return_value = response
    return client


# ─── AnthropicAdapter.complete: mock client → 호출 인자 + 파싱 ─────────

def test_complete_passes_system_and_params_non_json() -> None:
    client = _make_fake_anthropic_client("plain answer")
    adapter = AnthropicAdapter(client=client)
    req = LLMRequest(
        messages=_msgs(),
        model_id="claude-haiku-4-5",
        temperature=0.3,
        max_tokens=900,
        json_mode=False,
    )
    resp = adapter.complete(req, api_key="sk-ant-x")

    assert resp.text == "plain answer"
    assert resp.model_id == "claude-haiku-4-5"
    assert resp.alias == ""  # adapter 는 alias 를 비운다 (gateway 가 채움).
    assert resp.usage.prompt_tokens == 25
    assert resp.usage.completion_tokens == 9

    _, kwargs = client.messages.create.call_args
    assert kwargs["model"] == "claude-haiku-4-5"
    assert kwargs["max_tokens"] == 900
    assert kwargs["temperature"] == 0.3
    # ★ system 메시지는 별도 system= 파라미터로 분리 (messages role="system" 미사용).
    assert kwargs["system"] == "당신은 평가자다."
    # messages 는 user/assistant turn 만 (system 제외).
    assert kwargs["messages"] == [{"role": "user", "content": "이 plan을 평가해줘."}]


def test_complete_json_mode_adds_system_hint_no_prefill() -> None:
    # ★ Phase 11 B안 의도된 delta: JSON 모드는 system 지시문만 덧붙이고 assistant prefill 을
    #   사용하지 않는다 (sonnet-4-6 등 prefill 미지원 신모델 400 회피). 모델이 완전한
    #   JSON 을 직접 반환하므로 응답을 그대로 파싱하고, messages 는 user 로 끝난다.
    client = _make_fake_anthropic_client('{"verdict": "approve"}')
    adapter = AnthropicAdapter(client=client)
    req = LLMRequest(messages=_msgs(), model_id="claude-sonnet-4-6", json_mode=True)
    resp = adapter.complete(req, api_key="sk-ant-x")

    # ★ 모델 응답을 그대로 파싱 (prefill 복원 없음 — 완전한 JSON).
    assert resp.text == '{"verdict": "approve"}'

    _, kwargs = client.messages.create.call_args
    # system 에 JSON 지시문이 덧붙는다.
    assert "JSON" in kwargs["system"]
    assert "당신은 평가자다." in kwargs["system"]
    # ★ assistant prefill turn 미추가 → messages 는 user turn 으로 끝난다 (prefill 미지원 호환).
    assert kwargs["messages"][-1] == {"role": "user", "content": "이 plan을 평가해줘."}
    assert all(m["role"] != "assistant" for m in kwargs["messages"])


def test_complete_no_system_message_omits_system_param() -> None:
    # system 메시지가 없으면 system= 파라미터를 생략 (non-json).
    client = _make_fake_anthropic_client("ok")
    adapter = AnthropicAdapter(client=client)
    req = LLMRequest(
        messages=[LLMMessage(role="user", content="hi")],
        model_id="claude-haiku-4-5",
        json_mode=False,
    )
    adapter.complete(req, api_key="sk-ant-x")
    _, kwargs = client.messages.create.call_args
    assert "system" not in kwargs


def test_complete_multi_block_text_concatenated() -> None:
    # content 가 여러 TextBlock 이면 .text 를 이어붙인다 (비텍스트 블록 무시).
    client = MagicMock()
    b1 = MagicMock(); b1.type = "text"; b1.text = "part-A "
    b2 = MagicMock(); b2.type = "text"; b2.text = "part-B"
    tool = MagicMock(); tool.type = "tool_use"; tool.text = "SHOULD-IGNORE"
    usage = MagicMock(); usage.input_tokens = 1; usage.output_tokens = 2
    response = MagicMock(); response.content = [b1, tool, b2]; response.usage = usage
    client.messages.create.return_value = response

    adapter = AnthropicAdapter(client=client)
    req = LLMRequest(messages=[LLMMessage(role="user", content="x")],
                     model_id="claude-haiku-4-5", json_mode=False)
    resp = adapter.complete(req, api_key="sk-ant-x")
    assert resp.text == "part-A part-B"


def test_complete_empty_content_returns_empty_text() -> None:
    client = MagicMock()
    usage = MagicMock(); usage.input_tokens = 0; usage.output_tokens = 0
    response = MagicMock(); response.content = []; response.usage = usage
    client.messages.create.return_value = response
    adapter = AnthropicAdapter(client=client)
    req = LLMRequest(messages=[LLMMessage(role="user", content="x")],
                     model_id="claude-haiku-4-5", json_mode=False)
    resp = adapter.complete(req, api_key="sk-ant-x")
    assert resp.text == ""


def test_complete_missing_usage_yields_zero() -> None:
    client = MagicMock()
    block = MagicMock(); block.type = "text"; block.text = "hi"
    response = MagicMock(); response.content = [block]; response.usage = None
    client.messages.create.return_value = response
    adapter = AnthropicAdapter(client=client)
    req = LLMRequest(messages=[LLMMessage(role="user", content="x")],
                     model_id="claude-haiku-4-5", json_mode=False)
    resp = adapter.complete(req, api_key="sk-ant-x")
    assert resp.usage.prompt_tokens == 0
    assert resp.usage.completion_tokens == 0
    assert resp.usage.total_tokens == 0


# ─── 에러 정규화: anthropic 예외 → LLMError (제안서 §12) ───────────────

def test_complete_error_normalized_to_llmerror() -> None:
    import anthropic

    client = MagicMock()
    # AnthropicError 는 anthropic 예외 계층의 base.
    client.messages.create.side_effect = anthropic.AnthropicError("boom")
    adapter = AnthropicAdapter(client=client)
    req = LLMRequest(messages=_msgs(), model_id="claude-haiku-4-5")

    with pytest.raises(LLMError) as ei:
        adapter.complete(req, api_key="sk-ant-x")
    assert ei.value.provider == "anthropic"
    assert ei.value.model_id == "claude-haiku-4-5"


def test_complete_generic_exception_normalized_to_llmerror() -> None:
    client = MagicMock()
    client.messages.create.side_effect = RuntimeError("network down")
    adapter = AnthropicAdapter(client=client)
    req = LLMRequest(messages=_msgs(), model_id="claude-sonnet-4-6")

    with pytest.raises(LLMError) as ei:
        adapter.complete(req, api_key="sk-ant-x")
    assert ei.value.provider == "anthropic"
    assert ei.value.model_id == "claude-sonnet-4-6"


# ─── registry: claude-haiku / claude-sonnet 항목 (제안서 §18.B) ────────

def test_registry_claude_haiku_uses_config_field() -> None:
    haiku = get_model("claude-haiku")
    assert haiku["provider"] == "anthropic"
    assert haiku["model_id"] == get_settings().anthropic_model_haiku
    assert haiku["json_mode"] is True


def test_registry_claude_sonnet_uses_config_field() -> None:
    sonnet = get_model("claude-sonnet")
    assert sonnet["provider"] == "anthropic"
    assert sonnet["model_id"] == get_settings().anthropic_model_sonnet
    assert sonnet["json_mode"] is True


def test_registry_gemini_flash_added() -> None:
    flash = get_model("gemini-flash")
    assert flash["provider"] == "google"
    assert flash["json_mode"] is True


def test_registry_known_keys_include_claude() -> None:
    keys = registry_mod.known_keys()
    assert {"claude-haiku", "claude-sonnet", "gemini-flash"}.issubset(set(keys))


def test_registry_existing_keys_preserved() -> None:
    # ★ behavior-preserving: 기존 A안 키 0 수정.
    keys = set(registry_mod.known_keys())
    assert {"gpt-4o-mini", "gpt-4o", "gemini-cross"}.issubset(keys)


# ─── gateway dispatch: anthropic provider → AnthropicAdapter (mock client) ─

def test_gateway_dispatches_anthropic_via_mock_client(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # alias 표에 claude 미등록 → registry key 직접 + 임시 alias 주입으로 dispatch 검증.
    # (실제로는 B안 Slice 2 에서 alias 표에 claude 가 등록되지만, 본 Slice 는 registry
    #  + adapter dispatch 만 — alias 표 unchanged. 임시 monkeypatch 로 경로 검증.)
    from backend.fastapi.llm import aliases as alias_mod

    monkeypatch.setitem(alias_mod._ALIAS_TABLE, "_claude_test", "claude-haiku")
    gw = LLMGateway()
    # ★ Phase 11 B안 의도된 delta: prefill 미사용 → 모델이 완전한 JSON 을 직접 반환하므로
    #   mock 응답 text 를 그대로 파싱한다 (앞에 "{" 복원 없음).
    client = _make_fake_anthropic_client('{"ok": true}')
    resp = gw.complete("_claude_test", _msgs(), client=client)

    assert resp.text == '{"ok": true}'
    assert resp.alias == "_claude_test"
    assert resp.model_id == get_settings().anthropic_model_haiku
    assert resp.usage.prompt_tokens == 25
    # Anthropic SDK shape: system 분리.
    _, kwargs = client.messages.create.call_args
    assert kwargs["system"].startswith("당신은 평가자다.")


def test_gateway_select_adapter_anthropic() -> None:
    # _select_adapter 가 anthropic provider 를 AnthropicAdapter 로 매핑.
    gw = LLMGateway()
    adapter = gw._select_adapter("anthropic", client=None)
    assert isinstance(adapter, AnthropicAdapter)


def test_gateway_api_key_for_anthropic(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test")
    get_settings.cache_clear()
    gw = LLMGateway()
    assert gw._api_key_for("anthropic") == "sk-ant-test"
    get_settings.cache_clear()


# ─── graceful: anthropic_api_key="" → 명시적 LLMError ──────────────────

def test_gateway_missing_anthropic_key_raises_graceful_llmerror(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from backend.fastapi.llm import aliases as alias_mod

    monkeypatch.setenv("ANTHROPIC_API_KEY", "")
    monkeypatch.setitem(alias_mod._ALIAS_TABLE, "_claude_test", "claude-haiku")
    get_settings.cache_clear()
    gw = LLMGateway()
    with pytest.raises(LLMError) as ei:
        gw.complete("_claude_test", _msgs())
    assert ei.value.provider == "anthropic"
    assert "key" in ei.value.message.lower()
    get_settings.cache_clear()


# ─── S2b-1: json_mode 코드펜스 정규화 (라이브 관찰 haiku 펜스 방어) ──────
# 일부 Claude 모델(haiku 등)이 system 지시에도 ```json ... ``` 펜스를 덧붙여 반환 →
# json_mode 응답에 한해 _strip_json_fences 로 벗겨 clean JSON 으로 정규화한다.
# clean JSON / json_mode=False 는 불변(behavior-preserving).

from backend.fastapi.llm.providers.anthropic_adapter import _strip_json_fences


def test_complete_json_mode_strips_json_lang_fence() -> None:
    # ```json\n{...}\n``` (lang 지정) → 펜스 제거된 clean JSON.
    client = _make_fake_anthropic_client('```json\n{"a":1}\n```')
    adapter = AnthropicAdapter(client=client)
    req = LLMRequest(
        messages=[LLMMessage(role="user", content="x")],
        model_id="claude-haiku-4-5",
        json_mode=True,
    )
    resp = adapter.complete(req, api_key="sk-ant-x")
    assert resp.text == '{"a":1}'


def test_complete_json_mode_strips_bare_fence() -> None:
    # bare ```\n{...}\n``` (lang 없음) → 펜스 제거.
    client = _make_fake_anthropic_client('```\n{"b":2}\n```')
    adapter = AnthropicAdapter(client=client)
    req = LLMRequest(
        messages=[LLMMessage(role="user", content="x")],
        model_id="claude-haiku-4-5",
        json_mode=True,
    )
    resp = adapter.complete(req, api_key="sk-ant-x")
    assert resp.text == '{"b":2}'


def test_complete_json_mode_clean_json_unchanged() -> None:
    # 펜스 없는 clean JSON → 불변 (behavior-preserving).
    client = _make_fake_anthropic_client('{"c":3}')
    adapter = AnthropicAdapter(client=client)
    req = LLMRequest(
        messages=[LLMMessage(role="user", content="x")],
        model_id="claude-sonnet-4-6",
        json_mode=True,
    )
    resp = adapter.complete(req, api_key="sk-ant-x")
    assert resp.text == '{"c":3}'


def test_complete_non_json_mode_does_not_strip_fence() -> None:
    # ★ json_mode=False → 펜스가 있어도 벗기지 않는다 (원본 유지).
    fenced = '```json\n{"d":4}\n```'
    client = _make_fake_anthropic_client(fenced)
    adapter = AnthropicAdapter(client=client)
    req = LLMRequest(
        messages=[LLMMessage(role="user", content="x")],
        model_id="claude-haiku-4-5",
        json_mode=False,
    )
    resp = adapter.complete(req, api_key="sk-ant-x")
    assert resp.text == fenced


# ─── _strip_json_fences 직접 단위 테스트 ──────────────────────────────

def test_strip_json_fences_lang_fence() -> None:
    assert _strip_json_fences('```json\n{"a":1}\n```') == '{"a":1}'


def test_strip_json_fences_bare_fence() -> None:
    assert _strip_json_fences('```\n{"b":2}\n```') == '{"b":2}'


def test_strip_json_fences_no_fence_returns_original() -> None:
    # 펜스로 시작하지 않으면 원본 그대로 (불변).
    assert _strip_json_fences('{"c":3}') == '{"c":3}'
    assert _strip_json_fences('plain text {"x":1}') == 'plain text {"x":1}'


def test_strip_json_fences_leading_trailing_whitespace() -> None:
    # 앞뒤 공백/개행이 있어도 펜스를 인식하고 벗긴다.
    assert _strip_json_fences('  \n```json\n{"e":5}\n```\n  ') == '{"e":5}'
