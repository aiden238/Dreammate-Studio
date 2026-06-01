"""Anthropic (Claude) provider adapter — Phase 12 B안 Slice 1.

제안서 §8 / §18.B. B안 3-provider(GPT/Claude/Gemini) 다양성을 위해 Anthropic
Messages API 를 canonical LLMRequest/LLMResponse 로 래핑한다:

    import anthropic
    anthropic.Anthropic(api_key=...).messages.create(
        model=req.model_id,
        max_tokens=req.max_tokens,
        temperature=req.temperature,
        system=<system 메시지 분리>,            # ★ Anthropic 은 system 을 별도 파라미터로
        messages=[{"role": "user"/"assistant", "content": ...}, ...],
    )

→ canonical LLMResponse. provider 예외(anthropic.AnthropicError 등) → LLMError 정규화.

★ behavior-preserving / gated: 본 Slice 는 adapter 를 만들기만 — 기존 agents 미연결
  (default 호출 경로 OpenAI 불변). anthropic 미설정(키 없음) → gateway graceful LLMError.
★ DI: client 주입 가능 → 테스트가 mock anthropic client 주입(실 API 0).
★ SDK import 는 지연(complete 시점) — anthropic 미설치 환경에서도 모듈 import 는 성공(graceful).

OpenAI chat 의 role 기반 messages 와 달리 Anthropic 은 system 을 별도 파라미터로 받고
(messages 의 role="system" 미지원), messages 는 user/assistant turn 만 허용한다.
canonical LLMMessage(system/user/assistant)를 Anthropic shape 로 매핑한다:
  - role=="system" → system= 파라미터 (병합)
  - 그 외        → messages (user/assistant turn)

JSON 모드: Anthropic Messages API 는 response_format 이 없다 → system 지시문에
"JSON 으로만 응답" 을 덧붙이고, "{" prefill assistant turn 으로 JSON 시작을 유도한다
(req.json_mode=True 시). prefill 한 "{" 는 응답 text 앞에 다시 이어붙여 완전한 JSON 을
복원한다.
"""

from __future__ import annotations

import logging
from typing import Any

from ..errors import LLMError
from ..types import LLMMessage, LLMRequest, LLMResponse, LLMUsage

logger = logging.getLogger(__name__)

# JSON 모드 system 지시문 (Anthropic 은 response_format 미지원 → prompt 로 유도).
_JSON_SYSTEM_HINT = (
    "You must respond with a single valid JSON object only. "
    "Do not include any prose, markdown, or code fences."
)
# JSON 모드 assistant prefill — "{" 로 시작을 강제하면 모델이 JSON 본문만 잇는다.
_JSON_PREFILL = "{"


class AnthropicAdapter:
    """anthropic SDK 래퍼 (ProviderAdapter 구현)."""

    provider = "anthropic"

    def __init__(self, client: Any = None) -> None:
        """Args:
            client: anthropic.Anthropic 호환 client (테스트 mock 주입용 DI hook).
                    None 이면 complete() 시점에 api_key 로 실 client 생성(SDK 지연 import).
        """
        self._client = client

    def _resolve_client(self, api_key: str) -> Any:
        if self._client is not None:
            return self._client
        try:
            import anthropic  # 지연 import (미설치 환경 graceful)
        except ImportError as e:  # pragma: no cover - 설치 환경에서 미발생
            raise LLMError(
                self.provider,
                "",
                "anthropic SDK 미설치 (requirements.txt: anthropic)",
                cause=e,
            ) from e
        return anthropic.Anthropic(api_key=api_key)

    def complete(self, req: LLMRequest, *, api_key: str) -> LLMResponse:
        client = self._resolve_client(api_key)
        system, messages = _split_messages(req.messages)

        if req.json_mode:
            # response_format 부재 → system 지시 + assistant prefill 로 JSON 유도.
            system = f"{system}\n\n{_JSON_SYSTEM_HINT}".strip()
            messages = messages + [{"role": "assistant", "content": _JSON_PREFILL}]

        kwargs: dict[str, Any] = {
            "model": req.model_id,
            "max_tokens": req.max_tokens,
            "temperature": req.temperature,
            "messages": messages,
        }
        if system:
            kwargs["system"] = system

        logger.info(
            "anthropic adapter call model=%s json_mode=%s", req.model_id, req.json_mode
        )

        try:
            response = client.messages.create(**kwargs)
        except Exception as e:  # anthropic 예외 계층(AnthropicError 등)을 canonical 로 정규화
            logger.exception("Anthropic adapter 호출 실패 model=%s", req.model_id)
            raise LLMError(
                self.provider, req.model_id, f"Anthropic 호출 실패: {e}", cause=e
            ) from e

        text = _extract_text(response)
        if req.json_mode:
            # prefill 한 "{" 는 응답에 포함되지 않으므로 앞에 다시 이어붙여 완전한 JSON 복원.
            text = _JSON_PREFILL + text
        usage = _extract_usage(response)
        return LLMResponse(
            text=text,
            model_id=req.model_id,
            alias="",  # gateway 가 alias 를 채워 반환.
            usage=usage,
            raw=response,
        )


def _split_messages(messages: list[LLMMessage]) -> tuple[str, list[dict[str, str]]]:
    """canonical messages → (system, anthropic_messages).

    Anthropic 은 system 을 별도 파라미터로 받고(messages role="system" 미지원),
    messages 는 user/assistant turn 만 허용한다. system 메시지는 한 문자열로 병합한다.
    """
    system_parts: list[str] = []
    out_messages: list[dict[str, str]] = []
    for m in messages:
        if m.role == "system":
            system_parts.append(m.content)
        else:
            out_messages.append({"role": m.role, "content": m.content})
    return "\n\n".join(system_parts), out_messages


def _extract_text(response: Any) -> str:
    """Anthropic Messages 응답 → 본문 텍스트 (없으면 "").

    response.content 는 ContentBlock 리스트 — TextBlock 의 .text 를 이어붙인다
    (type="text" 만; tool_use 등 비텍스트 블록은 무시).
    """
    content = getattr(response, "content", None)
    if not content:
        return ""
    chunks: list[str] = []
    for block in content:
        # TextBlock 만 추출 (type 속성이 있으면 "text" 인 것만).
        block_type = getattr(block, "type", None)
        if block_type is not None and block_type != "text":
            continue
        block_text = getattr(block, "text", None)
        if isinstance(block_text, str) and block_text:
            chunks.append(block_text)
    return "".join(chunks)


def _extract_usage(response: Any) -> LLMUsage:
    """Anthropic usage(input_tokens/output_tokens) → canonical LLMUsage (없으면 0)."""
    usage = getattr(response, "usage", None)
    if usage is None:
        return LLMUsage()
    prompt = getattr(usage, "input_tokens", 0) or 0
    completion = getattr(usage, "output_tokens", 0) or 0
    try:
        return LLMUsage(prompt_tokens=int(prompt), completion_tokens=int(completion))
    except (TypeError, ValueError):
        return LLMUsage()
