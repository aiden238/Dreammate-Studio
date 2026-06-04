"""Phase 15 Slice 1 — director tier (output_mode 3rd tier) 스키마/직렬화 검증.

acceptance 매핑:
  - A1: output_mode enum 일반화(additive, backward-compat) — effective_output_mode 매핑.
  - A2: director 스키마 슬롯(additive) — DirectorScene + Plan 3슬롯 + DIRECTOR_FIELDS.
  - A3-PP: compact/rich byte-identical — model_dump_for_mode 가 상위 tier 슬롯 제외(director 누수 0).

핵심 검증:
  1. DirectorScene + Plan director 슬롯 default.
  2. model_dump_for_mode: compact(rich+director 제외) / rich(director만 제외) / director(전부).
  3. model_dump_compact() == model_dump_for_mode("compact") (Phase 13 호환 별칭).
  4. effective_output_mode 매핑 (compact/rich_enabled/output_mode 명시).
  5. envelope_to_response_dict: rich_enabled backward-compat + output_mode 분기.
  6. DIRECTOR_FIELDS drift guard.
"""
from __future__ import annotations

import pytest
from pydantic import ValidationError

from backend.fastapi.config import Settings, effective_output_mode
from backend.fastapi.schemas.output import (
    BEAT_RICH_FIELDS,
    DIRECTOR_FIELDS,
    PLAN_RICH_FIELDS,
    Body,
    DirectorScene,
    Envelope,
    Meta,
    Plan,
    PlanFlowBeat,
    Validation,
    ValidationCheck,
    envelope_to_response_dict,
)

_LEGACY_PLAN_KEYS = {
    "plan_id", "option_index", "name", "concept", "hook", "flow",
    "pros", "risks", "approach_label", "rag_used",
}


def _beat(i: int) -> PlanFlowBeat:
    return PlanFlowBeat(
        beat_index=i, beat=f"beat{i}", duration_sec=5, purpose="p",
        visual="화면", dialogue="대사", caption="자막",
    )


def _full_plan() -> Plan:
    """rich + director 슬롯 전부 채운 Plan."""
    return Plan(
        plan_id="plan-0", option_index=0, name="이름",
        concept="콘셉트", hook="이 영상은 director 테스트 후크입니다.",
        flow=[_beat(0), _beat(1)], pros="장점", risks="위험",
        approach_label="informational", rag_used=[],
        # rich
        target_audience="20대", tone="담백", hook_variants=["변형1"],
        shots=["B-roll"], thumbnail="썸네일", title_candidates=["제목1"],
        cta="구독", references=["사례1"], length_variants=["30초"],
        # director
        hook_system=["첫 후크", "재후크 @0:15"],
        retention_architecture="3초 호기심 갭 + 중반 재후크",
        scene_breakdown=[
            DirectorScene(
                scene_intent="도입 의도", viewer_emotion="호기심",
                retention_device="질문 던지기", why_this_works="갭 유발 패턴",
            )
        ],
    )


# ─── 1. 모델 default ──────────────────────────────────────────────────


def test_director_slots_default() -> None:
    p = Plan(
        plan_id="p", option_index=0, name="n", concept="c",
        hook="열글자이상의후크문장입니다", flow=[_beat(0), _beat(1)],
    )
    assert p.hook_system == []
    assert p.retention_architecture is None
    assert p.scene_breakdown == []


def test_director_scene_requires_core_fields() -> None:
    with pytest.raises(ValidationError):
        DirectorScene(scene_intent="", viewer_emotion="v", retention_device="r", why_this_works="w")


# ─── 2. model_dump_for_mode (byte-identical 핵심) ────────────────────


def test_compact_mode_excludes_rich_and_director() -> None:
    d = _full_plan().model_dump_for_mode("compact")
    assert set(d.keys()) == _LEGACY_PLAN_KEYS
    assert PLAN_RICH_FIELDS.isdisjoint(d.keys())
    assert DIRECTOR_FIELDS.isdisjoint(d.keys())
    for beat in d["flow"]:
        assert BEAT_RICH_FIELDS.isdisjoint(beat.keys())


def test_rich_mode_excludes_director_only() -> None:
    d = _full_plan().model_dump_for_mode("rich")
    # rich 슬롯 포함
    assert "target_audience" in d and "hook_variants" in d
    assert "visual" in d["flow"][0]  # beat rich 포함
    # ★ director 슬롯 제외 (Phase 13 rich byte-identical — director 키 누수 0)
    assert DIRECTOR_FIELDS.isdisjoint(d.keys())


def test_director_mode_includes_all() -> None:
    d = _full_plan().model_dump_for_mode("director")
    assert "target_audience" in d  # rich
    assert "hook_system" in d and "retention_architecture" in d and "scene_breakdown" in d
    assert d["scene_breakdown"][0]["scene_intent"] == "도입 의도"


def test_model_dump_compact_alias() -> None:
    p = _full_plan()
    assert p.model_dump_compact() == p.model_dump_for_mode("compact")


# ─── 3. effective_output_mode 매핑 (A1) ──────────────────────────────


@pytest.mark.parametrize(
    "output_mode,rich_flag,expected",
    [
        ("compact", False, "compact"),
        ("compact", True, "rich"),   # ★ backward-compat: 레거시 rich_output_enabled=True → rich
        ("rich", False, "rich"),
        ("director", False, "director"),
        ("director", True, "director"),  # 명시 output_mode 우선
    ],
)
def test_effective_output_mode(output_mode: str, rich_flag: bool, expected: str) -> None:
    s = Settings(output_mode=output_mode, rich_output_enabled=rich_flag)
    assert effective_output_mode(s) == expected


# ─── 4. envelope_to_response_dict (backward-compat + 모드) ───────────


def _envelope(plan: Plan) -> Envelope:
    return Envelope(
        meta=Meta.make(prompt_id="P-006", prompt_version="v1.0.0", model="gpt-4o-mini"),
        body=Body(plan_candidates=[plan]),
        validation=Validation(passed=True, checks=[ValidationCheck(name="x", status="ok")]),
    )


def test_envelope_response_rich_enabled_backward_compat() -> None:
    plan = _full_plan()
    env = _envelope(plan)
    # rich_enabled=False → compact (rich+director 제외)
    compact = envelope_to_response_dict(env, [plan], rich_enabled=False)
    pc = compact["body"]["plan_candidates"][0]
    assert PLAN_RICH_FIELDS.isdisjoint(pc.keys()) and DIRECTOR_FIELDS.isdisjoint(pc.keys())
    # rich_enabled=True → rich (director 제외 — byte-identical, 누수 0)
    rich = envelope_to_response_dict(env, [plan], rich_enabled=True)
    pcr = rich["body"]["plan_candidates"][0]
    assert "target_audience" in pcr and DIRECTOR_FIELDS.isdisjoint(pcr.keys())


def test_envelope_response_director_mode() -> None:
    plan = _full_plan()
    env = _envelope(plan)
    out = envelope_to_response_dict(env, [plan], output_mode="director")
    pc = out["body"]["plan_candidates"][0]
    assert "hook_system" in pc and "scene_breakdown" in pc and "target_audience" in pc


# ─── 5. DIRECTOR_FIELDS drift guard ──────────────────────────────────


def test_director_fields_constant_matches_model() -> None:
    from backend.fastapi.schemas.output import COMMERCIAL_FIELDS

    plan_fields = set(Plan.model_fields)
    assert DIRECTOR_FIELDS <= plan_fields
    # ★ Phase 20 (의도된 delta): commercial 슬롯(COMMERCIAL_FIELDS) 추가 →
    #   director = 전체 - legacy - rich - commercial (4-tier 상호 배타).
    assert DIRECTOR_FIELDS == plan_fields - _LEGACY_PLAN_KEYS - PLAN_RICH_FIELDS - COMMERCIAL_FIELDS
