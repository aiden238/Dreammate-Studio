"""Phase 17 가-S2 — brand_memory 구속(binding) 프리앰블 빌더 (production).

Phase 16 실측(commit a0487ec, eval/regression_results/2026-06-04_phase-16-s2-fit.md)이
입증한 메커니즘을 운영에 옮긴다: PKM/brand_memory 는 `rag_context`("그대로 복제하지
말고 참고자료") 가 아니라 **user_input 앞에 prepend 되는 구속 지시**로 주입할 때만
fit 이 오른다(+0.425). 본 모듈은 그 구속 프리앰블을 **brand_memory_entries 행에서**
결정적으로 만든다.

★ 입력 차이 (eval/ab_experiment.py 와의 분리):
  - eval 의 build_constraint_preamble 은 설계서 §7.4 pack(dict) 을 받는다(실험용).
  - 본 production 빌더는 BrandMemoryRepo.list_for_brand() 가 돌려주는 **row dict 리스트**
    ({entry_type, content, ...}) 를 직접 받는다. eval/ 에서 import 하지 않는다(layering).

설계 원칙:
  1. 결정적 — 동일 entries → 동일 출력 (random/now 미사용, 입력 순서 보존).
  2. graceful — entries 가 비었거나 유효 directive 0개면 "" 반환(주입 0 → byte-identical).
  3. entry_type 5종(brand_memory_repo._VALID_ENTRY_TYPES)을 구속 지시로 매핑.
"""

from __future__ import annotations

from typing import Any

# 구속 프리앰블 헤더 (eval/ab_experiment.py 와 의미·문구 정합 — "참고 자료" 의 정반대).
BRAND_CONSTRAINT_PREAMBLE_HEADER = "[기획 제약 — 반드시 반영]"

# entry_type → 구속 지시 라벨 매핑 (brand_memory_entries enum 5종).
#   톤/금지/선호표현은 직접 구속, 패턴은 반영/회피 지시로 표기한다.
_ENTRY_TYPE_LABELS: dict[str, str] = {
    "preferred_tone": "톤",
    "avoid_phrase": "금지",
    "preferred_phrase": "선호 표현",
    "success_pattern": "성공 패턴(반영)",
    "rejection_pattern": "회피 패턴",
}


def build_brand_constraint_preamble(entries: list[dict[str, Any]]) -> str:
    """brand_memory_entries 행 리스트 → 구속(binding) 제약 프리앰블 문자열 (결정적).

    각 행의 entry_type 을 _ENTRY_TYPE_LABELS 로 구속 지시 라벨에 매핑하고, content 를
    bullet("- <라벨>: <content>") 로 만든다. 입력 순서를 보존한다(결정적).

    Args:
        entries: BrandMemoryRepo.list_for_brand() 결과 — 각 행은 최소 {entry_type, content}.
            None/빈 리스트/유효 directive 0개면 "" 반환 (graceful, 주입 0 → byte-identical).

    Returns:
        헤더 1줄 + directive bullet 들로 구성된 문자열. 유효 directive 0개면 "".
        동일 entries → 동일 출력.
    """
    if not entries:
        return ""

    directives: list[str] = []
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        content = entry.get("content")
        if not isinstance(content, str) or not content.strip():
            continue
        etype = entry.get("entry_type")
        label = _ENTRY_TYPE_LABELS.get(str(etype))
        if not label:
            # 알 수 없는 entry_type → graceful skip (스키마 enum 외 행 무시).
            continue
        directives.append(f"- {label}: {content.strip()}")

    if not directives:
        return ""

    return BRAND_CONSTRAINT_PREAMBLE_HEADER + "\n" + "\n".join(directives)


__all__ = [
    "BRAND_CONSTRAINT_PREAMBLE_HEADER",
    "build_brand_constraint_preamble",
]
