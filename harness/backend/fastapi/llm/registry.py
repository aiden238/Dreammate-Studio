"""Model registry — concrete 모델 카탈로그 (Phase 11 A안 Slice 1).

제안서 §5.1 / §18.A. registry 는 "어떤 concrete 모델인가"를 선언한다 (provider /
model_id / json_mode / max_tokens / cost). aliases.py 가 논리명 → registry key 로
해석하고, gateway 가 registry.get_model(key) 로 메타를 조회한다.

A안 범위 (제안서 §18.A):
  - gpt-4o-mini  : workhorse (intent/planning/rewriter/memory)
  - gpt-4o       : critic (standard)
  - gemini-cross : cross_validation (★ gated, default 사용처 없음)

B안 추가 (제안서 §18.B, Phase 12 Slice 1 — ★ gated, default alias 미연결):
  - claude-haiku  : Anthropic workhorse (model_id = settings.anthropic_model_haiku)
  - claude-sonnet : Anthropic critic-급 (model_id = settings.anthropic_model_sonnet)
  - gemini-flash  : Google workhorse (3-plan 슬롯 3 후보)
  ★ model_id 는 전부 placeholder — 사용자 dev 페이지 확인값 확정 필요(config Field override).

★ Gemini 의 실제 model_id 는 config Field(`cross_validation_model`, 기본
"gemini-2.5-flash" placeholder)로 — 사용자가 정확한 ID 를 확정한다. registry 는
조회 시점에 settings 에서 그 값을 읽어 model_id 를 결정한다 (provider 추가 = registry
항목 + config Field, agent 코드 0 변경 — 제안서 §2/§5.2).

★ behavior-preserving: 본 Slice 는 카탈로그 정의만 — 기존 agents 미연결.
"""

from __future__ import annotations

from typing import Any

from ..config import get_settings

# provider 식별자 (canonical).
PROVIDER_OPENAI = "openai"
PROVIDER_GOOGLE = "google"
# ★ Phase 12 B안: Anthropic(Claude) provider (additive).
PROVIDER_ANTHROPIC = "anthropic"


def _registry() -> dict[str, dict[str, Any]]:
    """concrete 모델 카탈로그 (조회 시점에 settings 반영).

    ★ Gemini model_id 는 settings.cross_validation_model 로 — 사용자 확정 가능.
    cost 는 제안서 §18.0 (2026-06) per-1M-token 입력/출력 기준 (관측/추정용, 본 Slice
    미사용 — 후속 cost_control 재조정 §18.D 대비).
    """
    settings = get_settings()
    return {
        # ── OpenAI (기존 동작 보존: gpt-4o-mini / gpt-4o) ──────────────
        "gpt-4o-mini": {
            "provider": PROVIDER_OPENAI,
            "model_id": "gpt-4o-mini",
            "json_mode": True,
            "max_tokens": 1500,
            "cost": {"input": 0.00015, "output": 0.0006},
            "tier_allowed": ["free", "paid"],
        },
        "gpt-4o": {
            "provider": PROVIDER_OPENAI,
            "model_id": "gpt-4o",
            "json_mode": True,
            "max_tokens": 1500,
            "cost": {"input": 0.0025, "output": 0.01},
            "tier_allowed": ["free", "paid"],
        },
        # ── Google Gemini (A안 cross_validation, ★ gated/default-off) ──
        # model_id 는 config Field 로 교체 가능 (사용자 정확한 ID 확정 필요).
        "gemini-cross": {
            "provider": PROVIDER_GOOGLE,
            "model_id": settings.cross_validation_model,
            "json_mode": True,
            "max_tokens": 1500,
            "cost": {"input": 0.002, "output": 0.012},
            "tier_allowed": ["free", "paid"],
        },
        # ── Anthropic Claude (B안 3-provider, ★ gated/default-off) ─────
        # ★ model_id 는 config Field(anthropic_model_*) 로 교체 가능 — placeholder
        #   (제안서 §18.B 2026-06 라인업). 사용자 dev 페이지 확인값 확정 필요.
        #   cost 는 제안서 §18.0 (2026-06) per-1M-token (관측/추정용, 본 Slice 미사용).
        "claude-haiku": {
            "provider": PROVIDER_ANTHROPIC,
            "model_id": settings.anthropic_model_haiku,
            "json_mode": True,
            "max_tokens": 1500,
            "cost": {"input": 0.001, "output": 0.005},
            "tier_allowed": ["free", "paid"],
        },
        "claude-sonnet": {
            "provider": PROVIDER_ANTHROPIC,
            "model_id": settings.anthropic_model_sonnet,
            "json_mode": True,
            "max_tokens": 1500,
            "cost": {"input": 0.003, "output": 0.015},
            "tier_allowed": ["free", "paid"],
        },
        # ── Google Gemini workhorse (B안 3-plan 슬롯 3, ★ gated/default-off) ──
        # model_id placeholder (제안서 §18.B: Gemini 3 Flash) — config Field 미신설로
        # 직접 문자열. 사용자 dev 페이지 확인값 확정 필요. cost: §18.0 ($0.5/$3).
        "gemini-flash": {
            "provider": PROVIDER_GOOGLE,
            "model_id": "gemini-3-flash",
            "json_mode": True,
            "max_tokens": 1500,
            "cost": {"input": 0.0005, "output": 0.003},
            "tier_allowed": ["free", "paid"],
        },
    }


def get_model(key: str) -> dict[str, Any]:
    """registry key → concrete 모델 메타 dict.

    Args:
        key: registry key ("gpt-4o-mini" / "gpt-4o" / "gemini-cross").

    Returns:
        모델 메타 dict (provider / model_id / json_mode / max_tokens / cost / tier_allowed).
        호출자가 mutate 해도 카탈로그에 영향 없도록 매 호출 새 dict (얕은 사본).

    Raises:
        KeyError: 미등록 key.
    """
    catalog = _registry()
    if key not in catalog:
        raise KeyError(f"unknown registry model key: {key!r} (known: {sorted(catalog)})")
    return dict(catalog[key])


def known_keys() -> list[str]:
    """등록된 registry key 목록 (정렬)."""
    return sorted(_registry())
