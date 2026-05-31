"""Google Gemini provider adapter — Phase 11 A안 Slice 1.

제안서 §3 / §7 / §18.A. A안 cross_validation(다른 family 1회 교차검증)용 adapter.
google-genai SDK 래핑:

    from google import genai
    genai.Client(api_key=...).models.generate_content(
        model=req.model_id,
        contents=...,
        config={"response_mime_type": "application/json", "temperature": ..., ...},
    )

→ canonical LLMResponse. provider 예외 → LLMError 정규화.
JSON 모드 = config.response_mime_type="application/json".

★ gated/default-off: A안에서 cross_validation alias 는 정의되지만 default 호출 경로
없음(제안서 §7). 본 Slice 는 adapter 를 만들기만 — agents 미연결(behavior-preserving).
★ DI: client 주입 가능 → 테스트가 mock genai client 주입(실 API 0).
★ SDK import 는 지연(complete 시점) — google-genai 미설치 환경에서도 모듈 import 는 성공(graceful).

OpenAI chat 의 role 기반 messages 와 달리 Gemini 는 system_instruction + contents 분리.
canonical LLMMessage(system/user/assistant)를 Gemini shape 로 매핑한다:
  - role=="system" → config.system_instruction (병합)
  - 그 외        → contents (user/assistant turn)
"""

from __future__ import annotations

import logging
from typing import Any

from ..errors import LLMError
from ..types import LLMMessage, LLMRequest, LLMResponse, LLMUsage

logger = logging.getLogger(__name__)


class GeminiAdapter:
    """google-genai SDK 래퍼 (ProviderAdapter 구현)."""

    provider = "google"

    def __init__(self, client: Any = None) -> None:
        """Args:
            client: genai.Client 호환 client (테스트 mock 주입용 DI hook). None 이면
                    complete() 시점에 api_key 로 실 genai.Client 생성(SDK 지연 import).
        """
        self._client = client

    def _resolve_client(self, api_key: str) -> Any:
        if self._client is not None:
            return self._client
        try:
            from google import genai  # 지연 import (미설치 환경 graceful)
        except ImportError as e:  # pragma: no cover - 설치 환경에서 미발생
            raise LLMError(
                self.provider,
                "",
                "google-genai SDK 미설치 (requirements.txt: google-genai)",
                cause=e,
            ) from e
        return genai.Client(api_key=api_key)

    def complete(self, req: LLMRequest, *, api_key: str) -> LLMResponse:
        client = self._resolve_client(api_key)
        system_instruction, contents = _split_messages(req.messages)

        config: dict[str, Any] = {
            "temperature": req.temperature,
            "max_output_tokens": req.max_tokens,
        }
        if system_instruction:
            config["system_instruction"] = system_instruction
        if req.json_mode:
            config["response_mime_type"] = "application/json"

        logger.info("gemini adapter call model=%s json_mode=%s", req.model_id, req.json_mode)

        try:
            response = client.models.generate_content(
                model=req.model_id,
                contents=contents,
                config=config,
            )
        except Exception as e:  # google-genai 예외 계층을 canonical 로 정규화
            logger.exception("Gemini adapter 호출 실패 model=%s", req.model_id)
            raise LLMError(
                self.provider, req.model_id, f"Gemini 호출 실패: {e}", cause=e
            ) from e

        text = _extract_text(response)
        usage = _extract_usage(response)
        return LLMResponse(
            text=text,
            model_id=req.model_id,
            alias="",  # gateway 가 alias 를 채워 반환.
            usage=usage,
            raw=response,
        )


def _split_messages(messages: list[LLMMessage]) -> tuple[str, str]:
    """canonical messages → (system_instruction, contents).

    Gemini 는 system 을 config.system_instruction 으로 분리한다. system 외 메시지는
    한 prompt 문자열로 병합(Phase 11 A안 단순화 — multi-turn 정밀 매핑은 후속).
    """
    system_parts: list[str] = []
    content_parts: list[str] = []
    for m in messages:
        if m.role == "system":
            system_parts.append(m.content)
        else:
            content_parts.append(m.content)
    return "\n\n".join(system_parts), "\n\n".join(content_parts)


def _extract_text(response: Any) -> str:
    """Gemini 응답 → 본문 텍스트 (없으면 "")."""
    text = getattr(response, "text", None)
    if isinstance(text, str):
        return text
    return ""


def _extract_usage(response: Any) -> LLMUsage:
    """Gemini usage_metadata → canonical LLMUsage (없으면 0)."""
    meta = getattr(response, "usage_metadata", None)
    if meta is None:
        return LLMUsage()
    prompt = getattr(meta, "prompt_token_count", 0) or 0
    completion = getattr(meta, "candidates_token_count", 0) or 0
    try:
        return LLMUsage(prompt_tokens=int(prompt), completion_tokens=int(completion))
    except (TypeError, ValueError):
        return LLMUsage()
