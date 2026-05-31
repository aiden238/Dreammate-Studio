"""ProviderAdapter Protocol — Phase 11 A안 Slice 1.

제안서 §3 providers/base.py. provider별 SDK 호출을 단일 인터페이스로 추상화한다.
gateway 는 registry 의 provider 식별자로 adapter 를 선택하고 `.complete(req, api_key=...)`
를 호출한다. provider 추가 = adapter 1개 + registry 항목, agent 코드 0 변경.

★ behavior-preserving: 인터페이스 정의 — 기존 agents 미연결.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from ..types import LLMRequest, LLMResponse


@runtime_checkable
class ProviderAdapter(Protocol):
    """provider SDK 래퍼 인터페이스.

    구현체(openai_adapter / gemini_adapter)는 LLMRequest 를 provider별 SDK 호출로
    매핑하고, 응답을 canonical LLMResponse 로 변환한다. provider 예외는 LLMError 로
    정규화한다.
    """

    #: provider 식별자 ("openai" / "google" / 후속 "anthropic").
    provider: str

    def complete(self, req: LLMRequest, *, api_key: str) -> LLMResponse:
        """canonical 요청을 실행하고 canonical 응답 반환.

        Args:
            req: canonical LLMRequest (messages / model_id / temperature / ...).
            api_key: provider API 키 (gateway 가 settings 에서 주입).

        Returns:
            canonical LLMResponse.

        Raises:
            LLMError: provider 호출 실패를 정규화한 예외.
        """
        ...
