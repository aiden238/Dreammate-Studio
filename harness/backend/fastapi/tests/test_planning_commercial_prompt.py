"""Phase 20 Slice 2 — planning P-006 commercial_viral 프롬프트(v1.3.0) 검증.

acceptance 매핑:
  - A2: 프롬프트 + P-006 v1.3.0 — commercial_viral SYSTEM_PROMPT 가 상업 슬롯(10섹션) +
        §3.3 제약(기획경계/일반론금지/★보장표현금지/★추측표기)을 포함 + gated 공존.
        ★ 기존 compact/rich/director 프롬프트 보존 + 런타임 미연결(behavior-preserving, S3 wiring 전).

핵심 검증:
  1. COMMERCIAL_SYSTEM_PROMPT 가 commercial 7슬롯 + scene 상업 2필드 지시 포함.
  2. director 슬롯 계승(commercial = director + 상업) + §3.3 제약 문구.
  3. 기존 compact/rich/director 프롬프트에 commercial-only 토큰 미오염.
  4. 버전 상수 (compact v1.0.0 / rich v1.1.0 / director v1.2.0 / commercial_viral v1.3.0).
  5. _build_commercial_system_prompt_with_hint = COMMERCIAL 기반 + hint.
  6. prompt_registry §7 P-006 v1.3.0 commercial 등록 (doc↔code 정합).
"""
from __future__ import annotations

from pathlib import Path

from backend.fastapi.agents.planning import (
    COMMERCIAL_PROMPT_VERSION,
    COMMERCIAL_SYSTEM_PROMPT,
    DIRECTOR_PROMPT_VERSION,
    DIRECTOR_SYSTEM_PROMPT,
    PROMPT_VERSION,
    RICH_PROMPT_VERSION,
    RICH_SYSTEM_PROMPT,
    SYSTEM_PROMPT,
    _build_commercial_system_prompt_with_hint,
)

# commercial-only 슬롯/필드 토큰 (compact/rich/director 에는 없어야 함).
_COMMERCIAL_TOKENS = [
    "market_context",
    "audience_psychology",
    "brand_positioning",
    "commercial_conversion",
    "platform_packaging",
    "production_feasibility",
    "measurement_plan",
    "brand_signal",
    "commercial_signal",
]

_REGISTRY_DOC = (
    Path(__file__).resolve().parents[3] / "ai_system" / "prompts" / "prompt_registry.md"
)


def test_commercial_prompt_covers_commercial_slots() -> None:
    for token in _COMMERCIAL_TOKENS:
        assert token in COMMERCIAL_SYSTEM_PROMPT, f"COMMERCIAL_SYSTEM_PROMPT 가 '{token}' 미지시"
    # director 슬롯 계승 (commercial = director + 상업)
    for token in ["hook_system", "retention_architecture", "scene_breakdown"]:
        assert token in COMMERCIAL_SYSTEM_PROMPT
    # rich 슬롯도 계승
    assert "hook_variants" in COMMERCIAL_SYSTEM_PROMPT and "target_audience" in COMMERCIAL_SYSTEM_PROMPT


def test_commercial_prompt_has_risk_guards() -> None:
    """★ §3.3 제약 — 보정1(보장 금지) / 보정2(기획 경계) / 보정3(추측 표기) / 일반론 금지."""
    p = COMMERCIAL_SYSTEM_PROMPT
    assert "보장" in p  # 조회수/바이럴 보장 표현 금지(보정1)
    assert "브리프" in p  # 기획 브리프 경계(보정2)
    assert "추정" in p  # 실데이터 없으면 추측 표기(보정3)
    assert "일반론" in p  # 막연한 일반론 금지


def test_lower_tier_prompts_not_polluted_by_commercial() -> None:
    # commercial-only Plan 슬롯 토큰은 하위 tier 프롬프트에 없어야 함.
    # (단 brand_signal/commercial_signal/scene_breakdown 류 일부 단어 중복 가능성 회피 위해
    #  commercial 전용 Plan 슬롯 7종으로 검사.)
    commercial_only = [
        "market_context", "audience_psychology", "brand_positioning",
        "commercial_conversion", "platform_packaging", "production_feasibility",
        "measurement_plan",
    ]
    for token in commercial_only:
        assert token not in SYSTEM_PROMPT, f"compact 오염 '{token}'"
        assert token not in RICH_SYSTEM_PROMPT, f"rich 오염 '{token}'"
        assert token not in DIRECTOR_SYSTEM_PROMPT, f"director 오염 '{token}'"


def test_prompt_versions_4tier() -> None:
    assert PROMPT_VERSION == "v1.0.0"          # compact
    assert RICH_PROMPT_VERSION == "v1.1.0"     # rich
    assert DIRECTOR_PROMPT_VERSION == "v1.2.1"  # director (+특이성·정직가드 Phase 31)
    assert COMMERCIAL_PROMPT_VERSION == "v1.3.0"  # commercial_viral (minor bump)


def test_build_commercial_helper() -> None:
    hint = "informational — 정보 전달 중심"
    out = _build_commercial_system_prompt_with_hint(hint)
    assert out.startswith(COMMERCIAL_SYSTEM_PROMPT)
    assert hint in out
    assert "market_context" in out  # commercial 기반 → 슬롯 지시 포함


def test_registry_doc_registers_commercial_version() -> None:
    text = _REGISTRY_DOC.read_text(encoding="utf-8")
    assert "v1.3.0" in text
    for token in ["market_context", "commercial_conversion", "measurement_plan"]:
        assert token in text, f"prompt_registry 가 commercial 슬롯 '{token}' 미문서화"
    assert "commercial_viral" in text
