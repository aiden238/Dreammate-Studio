"""Canonical LLM error — Phase 11 A안 Slice 1.

provider별 예외(openai.OpenAIError / google.genai 예외 / 후속 anthropic 예외)를
gateway 경계에서 단일 LLMError 로 래핑한다. agents 는 provider 예외 타입에 의존하지
않는다 (제안서 §3 errors.py, §12 "에러 정규화 OpenAIError→LLMError").

★ 본 Slice 는 gateway 전용 — 기존 agents 의 OpenAIError 전파 경로는 불변(behavior-preserving).
"""

from __future__ import annotations


class LLMError(Exception):
    """provider 에러를 canonical 로 래핑한 gateway 경계 예외.

    Attributes:
        provider: "openai" | "google" | (후속) "anthropic".
        model_id: 호출 대상 concrete 모델 ID (없으면 "").
        message: 사람이 읽을 수 있는 사유.
        cause: 원본 provider 예외 (optional, 디버깅용 — `raise ... from cause` 권장).
    """

    def __init__(
        self,
        provider: str,
        model_id: str,
        message: str,
        *,
        cause: BaseException | None = None,
    ) -> None:
        self.provider = provider
        self.model_id = model_id
        self.message = message
        self.cause = cause
        super().__init__(f"[{provider}:{model_id or '?'}] {message}")
