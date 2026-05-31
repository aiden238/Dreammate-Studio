"""Model alias — 논리명 → registry key 해석 (Phase 11 A안 Slice 1).

제안서 §5.2 / §6 / §18.A. agents 는 concrete 모델명이 아니라 **alias**(논리명)만
참조한다 → provider/모델 교체 시 agent 코드 0 변경. alias 해석은 tier(무료/유료) ×
mode(standard/cost_saving) 를 입력으로 받는다 (기존 cost_control_policy 의 user tier
× cost mode 위에 매핑 — 새 축 추가 X, 제안서 §6).

A안 alias 표 (제안서 §18.A / §5.2):
  planning  → gpt-4o-mini
  intent    → gpt-4o-mini
  rewriter  → gpt-4o-mini
  memory    → gpt-4o-mini
  critic    → { standard: gpt-4o, cost_saving: gpt-4o-mini }   # 현 cost_saving 폴백 정식화
  cross_validation → gemini-cross   (★ gated, default 사용처 없음)

★ behavior-preserving 근거: resolve("planning") == "gpt-4o-mini" (= 현
settings.openai_model_default), resolve("critic", mode="standard") == "gpt-4o"
(= 현 settings.openai_model_critic). gateway.resolve_model 단위 test 로 강제.
"""

from __future__ import annotations

# tier×mode → registry key 표 (제안서 §6 / §18.A).
# 값이 str 이면 mode 무관 단일 모델. dict 이면 mode 별 분기.
_ALIAS_TABLE: dict[str, object] = {
    "planning": "gpt-4o-mini",
    "intent": "gpt-4o-mini",
    "rewriter": "gpt-4o-mini",
    "memory": "gpt-4o-mini",
    # 현 cost_saving 의 "Critic gpt-4o→gpt-4o-mini 폴백"을 alias 로 선언적 정식화.
    "critic": {"standard": "gpt-4o", "cost_saving": "gpt-4o-mini"},
    # ★ A안 cross_validation: gated/default-off. registry gemini-cross 로 해석.
    "cross_validation": "gemini-cross",
}


def known_aliases() -> list[str]:
    """등록된 논리 alias 목록 (정렬)."""
    return sorted(_ALIAS_TABLE)


def resolve(alias: str, tier: str = "free", mode: str = "standard") -> str:
    """논리 alias → registry key.

    Args:
        alias: 논리명 ("planning" / "critic" / "cross_validation" / ...).
        tier: user tier ("free" / "paid"). A안에서는 모델 분기에 미사용
              (B안에서 premium mode 도입 시 확장 — 제안서 §6 후속). 시그니처는 미리 수용.
        mode: cost mode ("standard" / "cost_saving"). critic 만 분기.

    Returns:
        registry key (예: "gpt-4o-mini" / "gpt-4o" / "gemini-cross").

    Raises:
        KeyError: 미등록 alias.

    Note:
        mode 가 표에 없으면 "standard" 로 graceful fallback (분기 dict 인 경우).
    """
    if alias not in _ALIAS_TABLE:
        raise KeyError(
            f"unknown alias: {alias!r} (known: {known_aliases()})"
        )
    entry = _ALIAS_TABLE[alias]
    if isinstance(entry, dict):
        # mode 분기 alias (critic). 미지원 mode → standard graceful fallback.
        return entry.get(mode, entry["standard"])
    return entry  # type: ignore[return-value]
