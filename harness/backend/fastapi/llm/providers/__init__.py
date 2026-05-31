"""LLM provider adapters — Phase 11 A안 Slice 1.

제안서 §3. provider별 SDK 래퍼. gateway 가 registry provider 식별자로 선택한다.

  base.ProviderAdapter — Protocol (.complete(req, api_key) -> LLMResponse)
  OpenAIAdapter        — OpenAI SDK 래핑 (기존 agents 호출 shape 흡수)
  GeminiAdapter        — google-genai SDK 래핑 (A안 cross_validation, gated)

★ behavior-preserving: adapter 정의만 — 기존 agents 미연결.
"""

from __future__ import annotations

from .base import ProviderAdapter
from .gemini_adapter import GeminiAdapter
from .openai_adapter import OpenAIAdapter

__all__ = ["ProviderAdapter", "OpenAIAdapter", "GeminiAdapter"]
