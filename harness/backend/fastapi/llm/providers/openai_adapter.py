"""OpenAI provider adapter — Phase 11 A안 Slice 1.

제안서 §3 / §4. 기존 agents(critic.py / planning.py / intent.py / rewriter.py)의
OpenAI 호출 형태를 그대로 흡수한다:

    OpenAI(api_key=...).chat.completions.create(
        model=req.model_id,
        messages=[...],
        response_format={"type": "json_object"} if json_mode else (생략),
        temperature=..., max_tokens=...,
    )

→ canonical LLMResponse 로 변환. OpenAIError → LLMError 정규화.

★ behavior-preserving: 호출 shape 가 기존 agents 와 동일(결과 보존). 본 Slice 는
adapter 를 만들기만 — 기존 agents 미연결(기존 OpenAIError 전파 경로 불변).
★ DI: client 를 주입 가능 → 테스트가 mock OpenAI client 주입(실 API 0).
"""

from __future__ import annotations

import logging
from typing import Any

from openai import OpenAI, OpenAIError

from ..errors import LLMError
from ..types import LLMRequest, LLMResponse, LLMUsage

logger = logging.getLogger(__name__)


class OpenAIAdapter:
    """OpenAI SDK 래퍼 (ProviderAdapter 구현)."""

    provider = "openai"

    def __init__(self, client: Any = None) -> None:
        """Args:
            client: OpenAI 호환 client (테스트 mock 주입용 DI hook). None 이면
                    complete() 시점에 api_key 로 실 OpenAI client 생성.
        """
        self._client = client

    def _resolve_client(self, api_key: str) -> Any:
        if self._client is not None:
            return self._client
        return OpenAI(api_key=api_key)

    def complete(self, req: LLMRequest, *, api_key: str) -> LLMResponse:
        client = self._resolve_client(api_key)
        # 기존 agents 와 동일: json_mode True 면 response_format 주입, 아니면 생략.
        kwargs: dict[str, Any] = {
            "model": req.model_id,
            "messages": [m.to_openai() for m in req.messages],
            "temperature": req.temperature,
            "max_tokens": req.max_tokens,
        }
        if req.json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        logger.info("openai adapter call model=%s json_mode=%s", req.model_id, req.json_mode)

        try:
            response = client.chat.completions.create(**kwargs)
        except OpenAIError as e:
            logger.exception("OpenAI adapter 호출 실패 model=%s", req.model_id)
            raise LLMError(
                self.provider, req.model_id, f"OpenAI 호출 실패: {e}", cause=e
            ) from e

        text = response.choices[0].message.content or ""
        usage = _extract_usage(response)
        return LLMResponse(
            text=text,
            model_id=req.model_id,
            alias="",  # gateway 가 alias 를 채워 반환(adapter 는 모델만 안다).
            usage=usage,
            raw=response,
        )


def _extract_usage(response: Any) -> LLMUsage:
    """OpenAI 응답 usage → canonical LLMUsage (없으면 0)."""
    usage = getattr(response, "usage", None)
    if usage is None:
        return LLMUsage()
    prompt = getattr(usage, "prompt_tokens", 0) or 0
    completion = getattr(usage, "completion_tokens", 0) or 0
    try:
        return LLMUsage(prompt_tokens=int(prompt), completion_tokens=int(completion))
    except (TypeError, ValueError):
        return LLMUsage()
