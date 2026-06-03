"""Phase 13 Slice 1 — output_schema rich 슬롯 additive 검증 (CC-012).

acceptance 매핑:
  - A1: 스키마 확장(additive) — rich 12 필드 전부 Optional default None/[], 기존 7필드 회귀 0.
  - A2: output_schema contract-change(additive) — Pydantic 모델 ↔ §8.1 v1.2.0 정합.
  - A5-PP: flag OFF byte-identical — Plan.model_dump_compact() 가 rich 키 제외 → 기존 7필드(+rag_used)
           출력과 완전 동일 (S3 OFF 경로가 호출할 capability 를 S1 에서 제공·검증).

핵심 검증:
  1. PlanFlowBeat rich 3종(visual/dialogue/caption) default None.
  2. Plan rich 9종 default None/[].
  3. compact Plan.model_dump_compact() == 기존 7필드(+rag_used) dict (rich 키 0개) — byte-identical.
  4. rich 채운 Plan: model_dump 보존 / model_dump_compact 제외.
  5. max_length 가드 (hook_variants ≤3 / title_candidates ≤5 / references ≤5).
  6. Body(plan_candidates=[compact]) 검증 통과 (소비자 회귀 0).
  7. 상수(PLAN_RICH_FIELDS / BEAT_RICH_FIELDS) ↔ 실제 필드 정합 (drift guard).
"""
from __future__ import annotations

import pytest
from pydantic import ValidationError

from backend.fastapi.schemas.output import (
    BEAT_RICH_FIELDS,
    PLAN_RICH_FIELDS,
    Body,
    Plan,
    PlanFlowBeat,
)

# Phase 12 이전(compact) Plan 직렬화 키 — byte-identical 기준선.
_LEGACY_PLAN_KEYS = {
    "plan_id",
    "option_index",
    "name",
    "concept",
    "hook",
    "flow",
    "pros",
    "risks",
    "approach_label",
    "rag_used",
}
_LEGACY_BEAT_KEYS = {"beat_index", "beat", "duration_sec", "purpose"}


def _compact_plan(option_index: int = 0) -> Plan:
    """rich 슬롯을 일절 주지 않은 compact Plan (Phase 12 이전 형태)."""
    return Plan(
        plan_id=f"plan-{option_index:08x}",
        option_index=option_index,
        name=f"테스트{option_index}",
        concept="compact 컨셉",
        hook="이 영상은 rich schema 테스트용 hook 예시입니다.",
        flow=[
            PlanFlowBeat(beat_index=0, beat="도입", duration_sec=10, purpose="훅"),
            PlanFlowBeat(beat_index=1, beat="전개", duration_sec=30, purpose="본문"),
        ],
        pros="간결",
        risks="없음",
        approach_label="informational",
        rag_used=[],
    )


# ─── 1. PlanFlowBeat rich default ────────────────────────────────────


def test_beat_rich_fields_default_none() -> None:
    beat = PlanFlowBeat(beat_index=0, beat="도입", duration_sec=3, purpose="훅")
    assert beat.visual is None
    assert beat.dialogue is None
    assert beat.caption is None


# ─── 2. Plan rich default ────────────────────────────────────────────


def test_plan_rich_fields_default() -> None:
    p = _compact_plan()
    assert p.target_audience is None
    assert p.tone is None
    assert p.thumbnail is None
    assert p.cta is None
    assert p.hook_variants == []
    assert p.shots == []
    assert p.title_candidates == []
    assert p.references == []
    assert p.length_variants == []


# ─── 3. byte-identical (A5-PP capability) ────────────────────────────


def test_model_dump_compact_excludes_all_rich_keys() -> None:
    """compact Plan.model_dump_compact() 는 rich 키를 일절 노출하지 않는다."""
    dumped = _compact_plan().model_dump_compact()
    assert set(dumped.keys()) == _LEGACY_PLAN_KEYS
    assert PLAN_RICH_FIELDS.isdisjoint(dumped.keys())
    for beat in dumped["flow"]:
        assert set(beat.keys()) == _LEGACY_BEAT_KEYS
        assert BEAT_RICH_FIELDS.isdisjoint(beat.keys())


def test_model_dump_compact_byte_identical_to_legacy() -> None:
    """rich 키 제외 후 dict 가 Phase 12 이전 7필드(+rag_used) 출력과 완전 동일."""
    p = _compact_plan(option_index=1)
    expected = {
        "plan_id": "plan-00000001",
        "option_index": 1,
        "name": "테스트1",
        "concept": "compact 컨셉",
        "hook": "이 영상은 rich schema 테스트용 hook 예시입니다.",
        "flow": [
            {"beat_index": 0, "beat": "도입", "duration_sec": 10, "purpose": "훅"},
            {"beat_index": 1, "beat": "전개", "duration_sec": 30, "purpose": "본문"},
        ],
        "pros": "간결",
        "risks": "없음",
        "approach_label": "informational",
        "rag_used": [],
    }
    assert p.model_dump_compact() == expected
    # mode="json" 경로(orchestrator 가 실제로 쓰는 모드)도 동일.
    assert p.model_dump_compact(mode="json") == expected


# ─── 4. rich 채운 Plan: 보존 vs 제외 ─────────────────────────────────


def test_rich_plan_full_dump_preserves_rich_compact_drops() -> None:
    p = _compact_plan()
    p.target_audience = "20대 자취생"
    p.tone = "담백하고 솔직한"
    p.hook_variants = ["변형 후크 1", "변형 후크 2"]
    p.shots = ["B-roll: 냄비 클로즈업"]
    p.thumbnail = "글자 크게 + 음식 클로즈업"
    p.title_candidates = ["3분 자취요리", "초간단 한끼"]
    p.cta = "구독하면 매주 레시피"
    p.references = ["요리 쇼츠 채널 A"]
    p.length_variants = ["30초 컷", "60초 컷"]
    p.flow[0].visual = "타이트 클로즈업"
    p.flow[0].dialogue = "오늘은 3분 요리"
    p.flow[0].caption = "3분 완성"

    full = p.model_dump()
    assert full["target_audience"] == "20대 자취생"
    assert full["hook_variants"] == ["변형 후크 1", "변형 후크 2"]
    assert full["flow"][0]["dialogue"] == "오늘은 3분 요리"

    compact = p.model_dump_compact()
    assert PLAN_RICH_FIELDS.isdisjoint(compact.keys())
    for beat in compact["flow"]:
        assert BEAT_RICH_FIELDS.isdisjoint(beat.keys())


# ─── 5. max_length 가드 ──────────────────────────────────────────────


@pytest.mark.parametrize(
    "field,values",
    [
        ("hook_variants", ["a", "b", "c", "d"]),  # >3
        ("title_candidates", ["a", "b", "c", "d", "e", "f"]),  # >5
        ("references", ["a", "b", "c", "d", "e", "f"]),  # >5
    ],
)
def test_rich_list_max_length_guards(field: str, values: list[str]) -> None:
    base = _compact_plan()
    payload = base.model_dump()
    payload[field] = values
    with pytest.raises(ValidationError):
        Plan(**payload)


# ─── 6. 소비자 회귀 0 (Body 검증) ────────────────────────────────────


def test_body_accepts_compact_plan() -> None:
    """compact plan (rich 부재) 으로 Body 검증 통과 — 기존 소비자 회귀 0."""
    body = Body(plan_candidates=[_compact_plan()])
    assert len(body.plan_candidates) == 1


# ─── 7. 상수 drift guard ─────────────────────────────────────────────


def test_rich_field_constants_match_model() -> None:
    """PLAN_RICH_FIELDS / BEAT_RICH_FIELDS 가 실제 모델 필드와 정확히 일치 (drift 방지).

    ★ Phase 15 (의도된 delta): Plan 에 director 슬롯(DIRECTOR_FIELDS)이 추가됨 →
    rich = 전체 - legacy - director (director 는 별도 tier 슬롯). beat 필드는 director 무관(불변).
    """
    from backend.fastapi.schemas.output import DIRECTOR_FIELDS

    plan_fields = set(Plan.model_fields)
    beat_fields = set(PlanFlowBeat.model_fields)
    # 상수가 가리키는 필드는 전부 모델에 실재.
    assert PLAN_RICH_FIELDS <= plan_fields
    assert BEAT_RICH_FIELDS <= beat_fields
    # rich = 모델 필드 - legacy - director (rich/director 는 상호 배타 tier 슬롯).
    assert PLAN_RICH_FIELDS == plan_fields - _LEGACY_PLAN_KEYS - DIRECTOR_FIELDS
    assert BEAT_RICH_FIELDS == beat_fields - _LEGACY_BEAT_KEYS
