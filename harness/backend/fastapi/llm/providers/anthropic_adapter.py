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
"JSON 으로만 응답" 을 덧붙여 JSON 출력을 유도한다 (req.json_mode=True 시).
assistant prefill 기법은 사용하지 않는다 — claude-sonnet-4-6 등 신모델이 prefill 을
미지원("conversation must end with a user message", 400 BadRequest)하기 때문이며,
system 지시문 방식은 모든 Claude 모델(haiku-4-5 / sonnet-4-6 등)과 호환된다.
messages 는 user turn 으로 끝나도록 유지된다(prefill assistant turn 미추가).
펜스 방어 정규화: 일부 모델(haiku 등)이 system 지시에도 ```json ... ``` 펜스를 덧붙이므로
json_mode 응답에 한해 코드펜스를 벗겨 clean JSON 으로 정규화한다(다운스트림 json.loads 안정화).
"""

from __future__ import annotations

import logging
from typing import Any

from ..errors import LLMError
from ..types import LLMMessage, LLMRequest, LLMResponse, LLMUsage

logger = logging.getLogger(__name__)

# JSON 모드 system 지시문 (Anthropic 은 response_format 미지원 → prompt 로 유도).
# ★ assistant prefill 미사용 (prefill 미지원 신모델 sonnet-4-6 400 회피) — 모든 Claude
#   모델 호환. 모델이 완전한 JSON 을 직접 반환하므로 응답 후처리 복원도 불필요.
_JSON_SYSTEM_HINT = (
    "You must respond with a single valid JSON object only. "
    "Do not include any prose, markdown, or code fences."
)


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
            # response_format 부재 → system 지시문만 덧붙여 JSON 유도 (prefill 미사용).
            # ★ assistant prefill turn 을 추가하지 않으므로 messages 는 user 로 끝나
            #   sonnet-4-6 등 prefill 미지원 모델에서도 400 없이 동작한다.
            system = f"{system}\n\n{_JSON_SYSTEM_HINT}".strip()

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

        # ★ prefill 미사용 → 모델이 완전한 JSON 을 직접 반환하므로 복원 후처리 불필요.
        text = _extract_text(response)
        if req.json_mode:
            text = _strip_json_fences(text)   # ★ Claude 펜스 정규화 (json_mode 한정)
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


def _strip_json_fences(text: str) -> str:
    """마크다운 코드펜스로 감싼 JSON 을 벗긴다 (json_mode 정규화용).

    일부 Claude 모델(haiku 등)은 system 지시에도 ```json ... ``` 펜스를 덧붙인다.
    펜스로 시작하지 않으면 원본을 그대로 반환(비-펜스/clean JSON 은 불변 = behavior-preserving).
    """
    s = text.strip()
    if not s.startswith("```"):
        return text  # 펜스 아님 → 원본 그대로 (clean JSON / 비-Claude 불변)
    lines = s.splitlines()
    if lines and lines[0].startswith("```"):   # 첫 줄: ``` 또는 ```json 등 제거
        lines = lines[1:]
    if lines and lines[-1].strip() == "```":   # 마지막 줄: 닫는 ``` 제거
        lines = lines[:-1]
    return "\n".join(lines).strip()


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
