"""LLM Gateway 패키지 — Phase 11 A안 Slice 1 (제안서 §3~§5, §18.A).

agent 는 "무엇을(alias)"만 알고, "어떤 모델/provider 로(registry)"는 gateway 가 결정한다.
provider 추가 = adapter 1개 + registry 항목, agent 코드 0 변경.

공개 API:
  get_gateway() / LLMGateway — 단일 진입 seam (complete / resolve_model)
  resolve_alias              — 논리명 → registry key (aliases.resolve)
  get_model                  — registry key → concrete 모델 메타
  LLMRequest / LLMResponse / LLMMessage / LLMUsage — canonical 타입
  LLMError                   — provider 에러 정규화

★ behavior-preserving: 본 Slice 는 gateway 를 만들기만 — 기존 agents/routers/
  orchestration 미연결(Stage A 연결은 후속 Slice). 기존 381 test 무영향.
"""

from __future__ import annotations

from .aliases import resolve as resolve_alias
from .errors import LLMError
from .gateway import LLMGateway, get_gateway
from .registry import get_model
from .types import LLMMessage, LLMRequest, LLMResponse, LLMUsage

__all__ = [
    "get_gateway",
    "LLMGateway",
    "resolve_alias",
    "get_model",
    "LLMRequest",
    "LLMResponse",
    "LLMMessage",
    "LLMUsage",
    "LLMError",
]
