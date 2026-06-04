"""Phase 20 Slice 1 — commercial_viral tier (output_mode 4th tier) 스키마/직렬화 검증.

acceptance 매핑:
  - A1: output_mode enum 4-tier(+commercial_viral) — effective_output_mode 매핑.
       COMMERCIAL_FIELDS(7) + CommercialScene 2필드(scene 7필드) additive.
       model_dump_for_mode 가 compact/rich/director 에서 commercial 제외 → byte-identical.

핵심 검증:
  1. Plan commercial 슬롯 default(None) + scene 상업 2필드 default(None).
  2. model_dump_for_mode 4-tier:
     - commercial_viral → 전부(rich+director+commercial 7슬롯 + scene 7필드).
     - director → commercial 7슬롯 제외 + scene 5필드(상업 2필드 제외) BUT scene_breakdown 포함.
     - rich → director + commercial 제외.
     - compact → 전부 제외(legacy 10키만) byte-identical.
  3. ★ byte-identical guard: compact/rich/director 어디에도 commercial 키 누수 0.
  4. effective_output_mode("commercial_viral") == "commercial_viral".
  5. envelope_to_response_dict(output_mode="commercial_viral").
"""
from __future__ import annotations

from backend.fastapi.config import Settings, effective_output_mode
from backend.fastapi.schemas.output import (
    COMMERCIAL_FIELDS,
    DIRECTOR_FIELDS,
    PLAN_RICH_FIELDS,
    SCENE_COMMERCIAL_FIELDS,
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
    """rich + director + commercial 슬롯 전부 채운 Plan (scene 7필드)."""
    return Plan(
        plan_id="plan-0", option_index=0, name="이름",
        concept="콘셉트", hook="이 영상은 commercial 테스트 후크입니다.",
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
                # commercial scene 2필드 (commercial_viral 에서만 노출)
                brand_signal="동네 가게의 따뜻함",
                commercial_signal="첫 방문 유도",
            )
        ],
        # commercial (7슬롯)
        market_context="로컬 카페 쇼츠 경쟁 심화",
        audience_psychology="가성비+분위기 동시 추구",
        brand_positioning="동네 단골의 거실 같은 공간",
        commercial_conversion="영상 말미 첫 방문 쿠폰 안내",
        platform_packaging="쇼츠: 0~3초 비주얼 훅 + 해시태그 #동네카페",
        production_feasibility="1인 스마트폰 촬영 가능",
        measurement_plan="저장수/방문 쿠폰 사용률 추적(보장 아님, 학습용)",
    )


# ─── 1. default ──────────────────────────────────────────────────────


def test_commercial_slots_default_none() -> None:
    p = Plan(
        plan_id="p", option_index=0, name="n", concept="c",
        hook="열글자이상의후크문장입니다", flow=[_beat(0), _beat(1)],
    )
    for f in COMMERCIAL_FIELDS:
        assert getattr(p, f) is None
    # scene 상업 2필드도 default None
    sc = DirectorScene(
        scene_intent="i", viewer_emotion="e", retention_device="r", why_this_works="w",
    )
    assert sc.brand_signal is None and sc.commercial_signal is None


# ─── 2. model_dump_for_mode 4-tier ───────────────────────────────────


def test_commercial_viral_includes_all() -> None:
    d = _full_plan().model_dump_for_mode("commercial_viral")
    # rich + director + commercial 7슬롯 전부
    assert "target_audience" in d  # rich
    assert DIRECTOR_FIELDS <= set(d.keys())  # director 3
    assert COMMERCIAL_FIELDS <= set(d.keys())  # commercial 7
    assert d["market_context"] == "로컬 카페 쇼츠 경쟁 심화"
    # scene 7필드 (상업 2필드 포함)
    scene = d["scene_breakdown"][0]
    assert scene["brand_signal"] == "동네 가게의 따뜻함"
    assert scene["commercial_signal"] == "첫 방문 유도"
    assert SCENE_COMMERCIAL_FIELDS <= set(scene.keys())


def test_director_excludes_commercial_but_keeps_scene_5fields() -> None:
    d = _full_plan().model_dump_for_mode("director")
    # ★ commercial 7슬롯 누수 0
    assert COMMERCIAL_FIELDS.isdisjoint(d.keys())
    # director 슬롯은 유지
    assert "hook_system" in d and "scene_breakdown" in d and "target_audience" in d
    # scene_breakdown 은 포함되되 상업 2필드는 제외 → 5필드 byte-identical
    scene = d["scene_breakdown"][0]
    assert SCENE_COMMERCIAL_FIELDS.isdisjoint(scene.keys())
    assert scene["scene_intent"] == "도입 의도"  # director 5필드는 유지


def test_rich_excludes_director_and_commercial() -> None:
    d = _full_plan().model_dump_for_mode("rich")
    assert "target_audience" in d  # rich 포함
    assert DIRECTOR_FIELDS.isdisjoint(d.keys())  # director 누수 0
    assert COMMERCIAL_FIELDS.isdisjoint(d.keys())  # commercial 누수 0


def test_compact_byte_identical() -> None:
    d = _full_plan().model_dump_for_mode("compact")
    # ★ legacy 10키만 — rich/director/commercial 전부 제외 (Phase 12 이전 byte-identical)
    assert set(d.keys()) == _LEGACY_PLAN_KEYS
    assert PLAN_RICH_FIELDS.isdisjoint(d.keys())
    assert DIRECTOR_FIELDS.isdisjoint(d.keys())
    assert COMMERCIAL_FIELDS.isdisjoint(d.keys())


def test_commercial_keys_never_leak_into_lower_tiers() -> None:
    """★ byte-identical guard: commercial 키는 commercial_viral 에서만, 하위 tier 누수 0."""
    p = _full_plan()
    for mode in ("compact", "rich", "director"):
        keys = set(p.model_dump_for_mode(mode).keys())
        assert COMMERCIAL_FIELDS.isdisjoint(keys), f"commercial leak in {mode}"
    # scene 상업 2필드도 director(scene 포함 tier)에서 누수 0
    director_scene = p.model_dump_for_mode("director")["scene_breakdown"][0]
    assert SCENE_COMMERCIAL_FIELDS.isdisjoint(director_scene.keys())


# ─── 3. effective_output_mode (A1) ───────────────────────────────────


def test_effective_output_mode_commercial_viral() -> None:
    s = Settings(output_mode="commercial_viral")
    assert effective_output_mode(s) == "commercial_viral"
    # 명시 우선 — 레거시 rich flag 와 무관
    s2 = Settings(output_mode="commercial_viral", rich_output_enabled=True)
    assert effective_output_mode(s2) == "commercial_viral"


# ─── 4. COMMERCIAL_FIELDS drift guard ────────────────────────────────


def test_commercial_fields_constant_matches_model() -> None:
    plan_fields = set(Plan.model_fields)
    assert COMMERCIAL_FIELDS <= plan_fields
    # 4-tier 분할: 전체 = legacy ∪ rich ∪ director ∪ commercial (상호 배타).
    assert COMMERCIAL_FIELDS == (
        plan_fields - _LEGACY_PLAN_KEYS - PLAN_RICH_FIELDS - DIRECTOR_FIELDS
    )
    # scene 상업 2필드도 모델에 실재.
    assert SCENE_COMMERCIAL_FIELDS <= set(DirectorScene.model_fields)


# ─── 5. envelope_to_response_dict (commercial_viral 모드) ────────────


def test_envelope_response_commercial_viral_mode() -> None:
    plan = _full_plan()
    env = Envelope(
        meta=Meta.make(prompt_id="P-006", prompt_version="v1.3.0", model="gpt-4o-mini"),
        body=Body(plan_candidates=[plan]),
        validation=Validation(passed=True, checks=[ValidationCheck(name="x", status="ok")]),
    )
    out = envelope_to_response_dict(env, [plan], output_mode="commercial_viral")
    pc = out["body"]["plan_candidates"][0]
    assert COMMERCIAL_FIELDS <= set(pc.keys())
    assert pc["scene_breakdown"][0]["commercial_signal"] == "첫 방문 유도"
    # ★ 하위 모드(director)는 commercial 누수 0
    out_d = envelope_to_response_dict(env, [plan], output_mode="director")
    assert COMMERCIAL_FIELDS.isdisjoint(out_d["body"]["plan_candidates"][0].keys())
