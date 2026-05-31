"""Canonical (provider-neutral) LLM request/response types — Phase 11 A안 Slice 1.

제안서 §4.2 / §3 근거. provider(OpenAI / Google Gemini / 후속 Anthropic) 응답 차이를
흡수하는 단일 표준 모델. agents 는 이 타입을 통해 "무엇을(alias)"만 알고, "어떤
모델/provider 로(registry)"는 gateway 가 결정한다.

★ behavior-preserving: 본 Slice 는 gateway 를 만들기만 하고 agents 에 연결하지 않는다
(Stage A 연결은 후속 Slice). 따라서 기존 코드/테스트 0 영향.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

# OpenAI chat role 과 동형 (provider-neutral). 후속 provider 매핑 시 흡수.
LLMRole = Literal["system", "user", "assistant"]


@dataclass(frozen=True)
class LLMMessage:
    """canonical 대화 메시지 (provider-neutral)."""

    role: LLMRole
    content: str

    def to_openai(self) -> dict[str, str]:
        """OpenAI chat.completions messages shape 로 변환."""
        return {"role": self.role, "content": self.content}


@dataclass(frozen=True)
class LLMRequest:
    """canonical 완성 요청 (provider-neutral).

    adapter 가 provider별 SDK 호출 인자로 매핑한다.
    """

    messages: list[LLMMessage]
    model_id: str
    temperature: float = 0.7
    max_tokens: int = 1500
    json_mode: bool = True


@dataclass(frozen=True)
class LLMUsage:
    """토큰 사용량 (canonical). provider 가 제공하지 않으면 0."""

    prompt_tokens: int = 0
    completion_tokens: int = 0

    @property
    def total_tokens(self) -> int:
        return self.prompt_tokens + self.completion_tokens


@dataclass(frozen=True)
class LLMResponse:
    """canonical 완성 응답 (provider-neutral) — 제안서 §4.2.

    Critic 의 normalize_to_canonical(0–5→0–1) 정신과 동형: provider 응답 차이를 흡수.

    Attributes:
        text: 모델이 생성한 본문 (JSON mode 면 JSON 문자열).
        model_id: 실제 호출된 concrete 모델 ID (registry.model_id).
        alias: 호출에 사용된 논리명(planning/critic/...). 관측성/로깅용.
        usage: 토큰 사용량.
        raw: provider 원본 응답 객체 (optional, 디버깅/확장용).
    """

    text: str
    model_id: str
    alias: str
    usage: LLMUsage = field(default_factory=LLMUsage)
    raw: Any = None
