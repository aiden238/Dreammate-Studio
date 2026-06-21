"""Phase 15 Slice 2 — planning P-006 director 프롬프트(v1.2.0) 검증 (CC-018).

acceptance 매핑:
  - A4: 프롬프트 확장 + P-006 v1.2.0 — director SYSTEM_PROMPT 가 director 슬롯을 채우도록 지시 +
        gated 공존. ★ 기존 compact/rich 프롬프트 보존 + 런타임 미연결(behavior-preserving).

핵심 검증:
  1. DIRECTOR_SYSTEM_PROMPT 가 director 슬롯 + DirectorScene 필드 지시 포함.
  2. 기존 compact/rich 프롬프트에 director-only 토큰 미오염 (분리 유지).
  3. 버전 상수 (compact v1.0.0 / rich v1.1.0 / director v1.2.0).
  4. _build_director_system_prompt_with_hint = DIRECTOR 기반 + hint.
  5. prompt_registry §7 P-006 v1.2.0 director 등록 (doc↔code 정합).
"""
from __future__ import annotations

from pathlib import Path

from backend.fastapi.agents.planning import (
    DIRECTOR_PROMPT_VERSION,
    DIRECTOR_SYSTEM_PROMPT,
    PROMPT_VERSION,
    RICH_PROMPT_VERSION,
    RICH_SYSTEM_PROMPT,
    SYSTEM_PROMPT,
    _build_director_system_prompt_with_hint,
)

# director-only 슬롯/필드 토큰 (rich/compact 에는 없어야 함).
_DIRECTOR_TOKENS = [
    "hook_system",
    "retention_architecture",
    "scene_breakdown",
    "scene_intent",
    "viewer_emotion",
    "retention_device",
    "why_this_works",
]

_REGISTRY_DOC = (
    Path(__file__).resolve().parents[3] / "ai_system" / "prompts" / "prompt_registry.md"
)


def test_director_prompt_covers_director_slots() -> None:
    for token in _DIRECTOR_TOKENS:
        assert token in DIRECTOR_SYSTEM_PROMPT, f"DIRECTOR_SYSTEM_PROMPT 가 '{token}' 미지시"
    # rich 슬롯도 계승 (director = rich + 연출/리텐션)
    assert "hook_variants" in DIRECTOR_SYSTEM_PROMPT and "target_audience" in DIRECTOR_SYSTEM_PROMPT
    # 제품 경계 + 보장 금지
    assert "브리프" in DIRECTOR_SYSTEM_PROMPT
    assert "보장" in DIRECTOR_SYSTEM_PROMPT  # 조회수/바이럴 보장 금지 규칙


def test_compact_rich_prompts_not_polluted_by_director() -> None:
    for token in _DIRECTOR_TOKENS:
        assert token not in SYSTEM_PROMPT, f"compact 프롬프트에 director 토큰 '{token}' 오염"
        assert token not in RICH_SYSTEM_PROMPT, f"rich 프롬프트에 director 토큰 '{token}' 오염"


def test_prompt_versions() -> None:
    assert PROMPT_VERSION == "v1.0.0"        # compact
    assert RICH_PROMPT_VERSION == "v1.1.0"   # rich
    assert DIRECTOR_PROMPT_VERSION == "v1.2.1"  # director (+특이성·정직가드 Phase 31)


def test_build_director_helper() -> None:
    hint = "narrative — 스토리텔링 중심"
    out = _build_director_system_prompt_with_hint(hint)
    assert out.startswith(DIRECTOR_SYSTEM_PROMPT)
    assert hint in out
    assert "scene_breakdown" in out  # director 기반 → 슬롯 지시 포함


def test_registry_doc_registers_director_version() -> None:
    text = _REGISTRY_DOC.read_text(encoding="utf-8")
    assert "v1.2.1" in text  # Phase 31 director patch (특이성·정직가드)
    for token in ["hook_system", "retention_architecture", "scene_breakdown"]:
        assert token in text, f"prompt_registry 가 director 슬롯 '{token}' 미문서화"
    assert "director" in text
