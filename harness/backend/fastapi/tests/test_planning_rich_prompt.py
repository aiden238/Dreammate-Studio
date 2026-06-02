"""Phase 13 Slice 2 — planning P-006 rich 프롬프트(v1.1.0) 검증 (CC-013).

acceptance 매핑:
  - A3: 프롬프트 확장 + P-006 bump — rich SYSTEM_PROMPT 가 S1 rich 슬롯을 채우도록 지시 +
        v1.0.0 → v1.1.0 (prompt-version-review). ★ 기존 compact 프롬프트 보존.

핵심 검증 (★ behavior-preserving — rich 프롬프트는 S2 시점 런타임 미연결):
  1. RICH_SYSTEM_PROMPT 가 rich 12 슬롯 지시를 포함.
  2. 기존 compact SYSTEM_PROMPT 보존 (rich-only 토큰 미포함 — 분리 유지).
  3. RICH_PROMPT_VERSION == "v1.1.0" / PROMPT_VERSION == "v1.0.0" (compact 불변).
  4. _build_rich_system_prompt_with_hint = RICH 기반 + hint 주입 / compact 헬퍼는 compact 기반 (미오염).
  5. prompt_registry.md §7 P-006 doc 가 v1.1.0 rich 를 등록 (doc ↔ code 정합).
"""
from __future__ import annotations

from pathlib import Path

from backend.fastapi.agents.planning import (
    PROMPT_VERSION,
    RICH_PROMPT_VERSION,
    RICH_SYSTEM_PROMPT,
    SYSTEM_PROMPT,
    _build_rich_system_prompt_with_hint,
    _build_system_prompt_with_hint,
)

# S1 rich 슬롯 — rich 프롬프트가 반드시 지시해야 하는 키.
_RICH_SLOT_TOKENS = [
    "hook_variants",
    "target_audience",
    "tone",
    "visual",
    "dialogue",
    "caption",
    "shots",
    "thumbnail",
    "title_candidates",
    "cta",
    "references",
    "length_variants",
]

_REGISTRY_DOC = (
    Path(__file__).resolve().parents[3] / "ai_system" / "prompts" / "prompt_registry.md"
)


# ─── 1. rich 프롬프트가 12 슬롯 지시 ─────────────────────────────────


def test_rich_prompt_covers_all_rich_slots() -> None:
    for token in _RICH_SLOT_TOKENS:
        assert token in RICH_SYSTEM_PROMPT, f"RICH_SYSTEM_PROMPT 가 rich 슬롯 '{token}' 미지시"
    # 제품 경계(브리프 — 완성 대본/제작 아님) 명시.
    assert "브리프" in RICH_SYSTEM_PROMPT
    # JSON-only 규칙 계승.
    assert "JSON" in RICH_SYSTEM_PROMPT


# ─── 2. compact 프롬프트 보존 (분리 유지) ────────────────────────────


def test_compact_prompt_preserved_and_separate() -> None:
    # compact 의 핵심 구조/규칙 유지.
    assert '"plan"' in SYSTEM_PROMPT
    assert "광고" in SYSTEM_PROMPT  # 광고 표현 금지 규칙
    # ★ rich-only 슬롯 토큰이 compact 프롬프트에 새지 않음 (오염 0).
    for token in ["hook_variants", "title_candidates", "length_variants", "thumbnail"]:
        assert token not in SYSTEM_PROMPT, f"compact SYSTEM_PROMPT 에 rich 토큰 '{token}' 오염"


# ─── 3. 버전 상수 ────────────────────────────────────────────────────


def test_prompt_versions() -> None:
    assert PROMPT_VERSION == "v1.0.0"  # compact 불변
    assert RICH_PROMPT_VERSION == "v1.1.0"  # rich (minor bump)


# ─── 4. build 헬퍼 (hint 주입 + 기반 프롬프트 정합) ──────────────────


def test_build_helpers_use_correct_base() -> None:
    hint = "narrative — 스토리텔링 중심, 감정 연결"

    rich = _build_rich_system_prompt_with_hint(hint)
    assert rich.startswith(RICH_SYSTEM_PROMPT)
    assert hint in rich
    assert "hook_variants" in rich  # rich 기반 → 슬롯 지시 포함

    compact = _build_system_prompt_with_hint(hint)
    assert compact.startswith(SYSTEM_PROMPT)
    assert hint in compact
    assert "hook_variants" not in compact  # compact 기반 → rich 토큰 없음


# ─── 5. registry doc ↔ code 정합 ─────────────────────────────────────


def test_registry_doc_registers_rich_version() -> None:
    text = _REGISTRY_DOC.read_text(encoding="utf-8")
    assert RICH_PROMPT_VERSION in text, "prompt_registry.md 에 P-006 v1.1.0 미등록"
    # rich 슬롯이 registry output schema 에 문서화되었는지(대표 토큰).
    for token in ["hook_variants", "title_candidates", "length_variants"]:
        assert token in text, f"prompt_registry.md 가 rich 슬롯 '{token}' 미문서화"
    # gated 공존(deprecate 아님) 명시.
    assert "gated" in text
