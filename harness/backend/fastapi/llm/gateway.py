"""LLMGateway — 단일 진입 seam (Phase 11 A안 Slice 1).

제안서 §3 / §4 / §6. agent 는 "무엇을(alias)"만 알고, "어떤 모델/provider 로(registry)"는
gateway 가 결정한다. provider 추가 = adapter 1개 + registry 항목, agent 코드 0 변경.

흐름 (complete):
  1. key   = aliases.resolve(alias, tier, mode)      # 논리명 → registry key
  2. model = registry.get_model(key)                 # concrete 메타
  3. provider adapter 선택(openai/google) + api_key = settings.<provider>_api_key
  4. api_key 없으면 graceful: LLMError("missing key")
  5. adapter.complete(req, api_key) → LLMResponse (alias 채워 반환)

★ behavior-preserving: 본 Slice 는 gateway 를 만들기만 — agents 미연결(Stage A 후속).
  - resolve_model(alias, tier, mode) 가 현 settings default 와 동일 값 반환(단위 test 강제).
  - client DI: 테스트가 mock adapter/client 주입 → 실 API 0.
★ flagship 기본 호출 0: cross_validation alias 는 gated(제안서 §7) — gateway 는 호출만
  중계, default 호출 경로 없음(agents 미연결).
"""

from __future__ import annotations

import logging
from typing import Any

from ..config import get_settings
from . import aliases, registry
from .errors import LLMError
from .providers.anthropic_adapter import AnthropicAdapter
from .providers.base import ProviderAdapter
from .providers.gemini_adapter import GeminiAdapter
from .providers.openai_adapter import OpenAIAdapter
from .registry import PROVIDER_ANTHROPIC, PROVIDER_GOOGLE, PROVIDER_OPENAI
from .types import LLMMessage, LLMRequest, LLMResponse

logger = logging.getLogger(__name__)


def _coerce_messages(messages: Any) -> list[LLMMessage]:
    """messages 입력을 list[LLMMessage] 로 정규화.

    LLMMessage 시퀀스 또는 {"role","content"} dict 시퀀스 둘 다 허용(호출 편의).
    """
    out: list[LLMMessage] = []
    for m in messages:
        if isinstance(m, LLMMessage):
            out.append(m)
        elif isinstance(m, dict):
            out.append(LLMMessage(role=m["role"], content=m["content"]))
        else:
            raise TypeError(f"unsupported message type: {type(m).__name__}")
    return out


class LLMGateway:
    """provider-neutral 완성 게이트웨이."""

    def resolve_model(
        self, alias: str, tier: str = "free", mode: str = "standard"
    ) -> str:
        """alias(+tier×mode) → concrete model_id (registry 해석).

        ★ behavior-preserving 검증 헬퍼: 현 settings default 와 동일 값을 반환함을
        단위 test 로 강제한다(제안서 §11 M2 / §12).
          resolve_model("planning")              == settings.openai_model_default
          resolve_model("critic", mode="standard") == settings.openai_model_critic

        Returns:
            concrete model_id (예: "gpt-4o-mini" / "gpt-4o" / settings.cross_validation_model).
        """
        key = aliases.resolve(alias, tier, mode)
        return registry.get_model(key)["model_id"]

    def _select_adapter(self, provider: str, client: Any) -> ProviderAdapter:
        """registry provider 식별자 → adapter (client DI 주입)."""
        if provider == PROVIDER_OPENAI:
            return OpenAIAdapter(client=client)
        if provider == PROVIDER_GOOGLE:
            return GeminiAdapter(client=client)
        # ★ Phase 12 B안: Anthropic(Claude) provider (additive).
        if provider == PROVIDER_ANTHROPIC:
            return AnthropicAdapter(client=client)
        raise LLMError(provider, "", f"지원하지 않는 provider: {provider!r}")

    def _api_key_for(self, provider: str) -> str:
        """provider → settings API 키 (graceful default="")."""
        settings = get_settings()
        if provider == PROVIDER_OPENAI:
            return settings.openai_api_key
        if provider == PROVIDER_GOOGLE:
            return settings.google_api_key
        # ★ Phase 12 B안: Anthropic(Claude) provider (additive).
        if provider == PROVIDER_ANTHROPIC:
            return settings.anthropic_api_key
        return ""

    def complete(
        self,
        alias: str,
        messages: Any,
        *,
        tier: str = "free",
        mode: str = "standard",
        temperature: float = 0.7,
        max_tokens: int = 1500,
        json_mode: bool = True,
        client: Any = None,
        adapter: ProviderAdapter | None = None,
    ) -> LLMResponse:
        """alias 기반 단일 완성 호출.

        Args:
            alias: 논리명 ("planning" / "critic" / "cross_validation" / ...).
            messages: list[LLMMessage] 또는 [{"role","content"}, ...].
            tier: user tier ("free"/"paid").
            mode: cost mode ("standard"/"cost_saving").
            temperature / max_tokens / json_mode: 완성 파라미터.
            client: provider SDK client DI (테스트 mock 주입). adapter 미주입 시 사용.
            adapter: ProviderAdapter DI (테스트가 mock adapter 통째 주입). 우선 적용.

        Returns:
            canonical LLMResponse (alias 필드 채워 반환).

        Raises:
            LLMError: provider 키 미설정(graceful) 또는 adapter 호출 실패(정규화).
            KeyError: 미등록 alias / registry key.
        """
        key = aliases.resolve(alias, tier, mode)
        model = registry.get_model(key)
        provider = model["provider"]
        model_id = model["model_id"]

        req = LLMRequest(
            messages=_coerce_messages(messages),
            model_id=model_id,
            temperature=temperature,
            max_tokens=max_tokens,
            json_mode=json_mode,
        )

        used_adapter = adapter if adapter is not None else self._select_adapter(provider, client)

        # ★ graceful: api_key 없으면(그리고 adapter/client 미주입) 명시적 LLMError.
        api_key = self._api_key_for(provider)
        if adapter is None and client is None and not api_key:
            raise LLMError(
                provider,
                model_id,
                f"{provider} API key 미설정 (graceful) — alias={alias!r}",
            )

        logger.info(
            "gateway.complete alias=%s tier=%s mode=%s provider=%s model=%s",
            alias, tier, mode, provider, model_id,
        )

        response = used_adapter.complete(req, api_key=api_key)
        # adapter 는 모델만 안다 → gateway 가 alias 를 채워 반환(관측성).
        return LLMResponse(
            text=response.text,
            model_id=response.model_id,
            alias=alias,
            usage=response.usage,
            raw=response.raw,
        )


_GATEWAY: LLMGateway | None = None


def get_gateway() -> LLMGateway:
    """LLMGateway 싱글톤."""
    global _GATEWAY
    if _GATEWAY is None:
        _GATEWAY = LLMGateway()
    return _GATEWAY
