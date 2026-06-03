"""Phase 16 S2 — 강한(binding) 주입 + 적합도(fit/adherence) 측정 단위 테스트 (mock-only, CI-safe).

검증 대상 (S1 §4(a) 처방의 구현):
  - build_constraint_preamble: pack → 구속 제약 프리앰블(locked/tone/avoid/series directive 포함).
    빈/무효 pack → "".
  - ★ 강한 주입 통제 증명: recording mock planning client 로 Arm B_strong 의 planning user 메시지가
    preamble + base_input, Arm A 가 base_input 임을 입증 — 차이는 오직 preamble prefix 이고,
    rag_context=[] 이므로 어느 system prompt 에도 "참고 자료" 블록이 없다 (단일 변수 = preamble).
  - score_fit 객관 파트: 금지어 포함 plan → avoid_clean False + 위반 토큰; clean plan → True.
    mock judge 가 고정 fit_score JSON 반환 → fit_0_1 파싱 + 위반 시 페널티 적용.
  - run_ab_pair_fit: arm_a / arm_b_strong + generic·fit delta 산출 (mock 채점).

★ CI-safe: 실 LLM 호출 0 (mock client 주입). API 키 미사용/미기록.
"""

from __future__ import annotations

import asyncio
import json
from typing import Any
from unittest.mock import MagicMock

import pytest

from backend.fastapi.eval.ab_experiment import (
    ARM_A,
    ARM_B_STRONG,
    CONSTRAINT_PREAMBLE_HEADER,
    build_constraint_preamble,
    run_ab_pair_fit,
    score_fit,
)
from backend.fastapi.eval.ab_personas import CAFE_PERSONA, FITNESS_PERSONA

# A/B 공유 고정 입력/모델 (통제: arm 간 동일 — preamble 만 다름).
BASE_INPUT = "우리 동네 카페 신메뉴 원두를 소개하는 30초 영상 기획해줘"
MODELS = ["gpt-4o-mini", "gpt-4o-mini", "gpt-4o-mini"]

# CAFE_PERSONA directive content (프리앰블에 들어가야 함).
CAFE_LOCKED = "과한 자막을 지양하고 손글씨 톤의 담백한 자막을 선호한다"
CAFE_TONE = "따뜻하고 솔직한 동네 가게 톤"
CAFE_SERIES = "오프닝 5초는 원두 로스팅 b-roll 로 고정하는 시리즈 포맷"
CAFE_AVOID_TOKEN = "최저가"  # _collect_avoid_phrases 가 작은따옴표에서 뽑는 토큰


# ─── mock client ──────────────────────────────────────────────────────

# planning 이 받는 최소 유효 plan envelope (clean — 금지어 없음).
_CLEAN_PLAN = {
    "plan": {
        "name": "원두 한 잔의 시간",
        "concept": "신메뉴 원두를 담백하게 소개하는 브이로그",
        "hook": "이 원두, 왜 다른지 3초 안에 보여드릴게요",
        "flow": [
            {"beat_index": 0, "beat": "도입 클로즈업", "duration_sec": 3, "purpose": "관심 유발"},
            {"beat_index": 1, "beat": "추출 과정", "duration_sec": 15, "purpose": "핵심 메시지"},
            {"beat_index": 2, "beat": "시음 + CTA", "duration_sec": 12, "purpose": "CTA"},
        ],
        "pros": "담백한 톤이 브랜드와 맞음",
        "risks": "추출 샷이 단조로울 수 있음",
        "approach_label": "narrative",
    }
}

# 금지어('최저가')를 포함하는 더러운 plan (avoid 위반 케이스).
_DIRTY_PLAN_BODY = {
    "name": "최저가 원두 한 잔",
    "concept": "동네 최저가로 즐기는 신메뉴 원두",
    "hook": "지금 우리 동네 최저가 원두입니다",
    "flow": [
        {"beat_index": 0, "beat": "가격 강조 도입", "duration_sec": 3, "purpose": "관심 유발"},
    ],
    "approach_label": "informational",
}

# critic 최소 유효 verdict (compact 8차원 — default output_mode=compact).
_FAKE_CRITIC = {
    "scores": {
        "intent_fit": 4,
        "target_clarity": 4,
        "hook_strength": 4,
        "message_clarity": 4,
        "structure": 4,
        "feasibility": 4,
        "brand_consistency": 4,
        "differentiation": 3,
    },
    "reasons": {},
    "suggestions": {},
    "overall_verdict": "approve",
    "blocking_issues": [],
}

# judge 고정 응답 (fit_score 0.9 + reasons).
_FAKE_JUDGE = {"fit_score": 0.9, "reasons": "톤·잠금 선호를 잘 반영함"}

# critic system prompt 식별 문구 (mock 분기용).
_CRITIC_MARKER = "품질 평가자(Critic)"
# judge system prompt 식별 문구 (mock 분기용 — _FIT_JUDGE_SYSTEM_PROMPT 의 고유 토큰).
_JUDGE_MARKER = "개인화 적합도(fit)"


def _make_recording_client() -> MagicMock:
    """planning·critic·judge 호출을 모두 처리하는 recording mock OpenAI client.

    chat.completions.create 호출마다 messages 를 client._calls 에 기록하고,
    system prompt 로 critic / judge / planning 을 구분해 알맞은 유효 JSON 을 반환한다.
    """
    client = MagicMock()
    client._calls = []

    def _create(*, messages, **kwargs):  # type: ignore[no-untyped-def]
        client._calls.append({"messages": messages, "kwargs": kwargs})
        system = messages[0]["content"] if messages else ""
        if _CRITIC_MARKER in system:
            payload: Any = _FAKE_CRITIC
        elif _JUDGE_MARKER in system:
            payload = _FAKE_JUDGE
        else:
            payload = _CLEAN_PLAN
        msg = MagicMock()
        msg.content = json.dumps(payload, ensure_ascii=False)
        choice = MagicMock()
        choice.message = msg
        response = MagicMock()
        response.choices = [choice]
        return response

    client.chat.completions.create.side_effect = _create
    return client


def _make_fixed_judge_client(fit_score: float) -> MagicMock:
    """fit_score 를 고정 반환하는 judge-only mock client."""
    client = MagicMock()

    def _create(**kwargs):  # type: ignore[no-untyped-def]
        msg = MagicMock()
        msg.content = json.dumps(
            {"fit_score": fit_score, "reasons": "고정 판정"}, ensure_ascii=False
        )
        choice = MagicMock()
        choice.message = msg
        response = MagicMock()
        response.choices = [choice]
        return response

    client.chat.completions.create.side_effect = _create
    return client


def _planning_calls(client: MagicMock) -> list[dict[str, Any]]:
    """기록된 호출 중 planning 호출(critic/judge 아님)만 추린다."""
    return [
        c
        for c in client._calls
        if _CRITIC_MARKER not in c["messages"][0]["content"]
        and _JUDGE_MARKER not in c["messages"][0]["content"]
    ]


# ─── build_constraint_preamble ────────────────────────────────────────

def test_build_constraint_preamble_contains_directives() -> None:
    """pack → 구속 프리앰블: 헤더 + locked/tone/avoid/series directive 를 포함한다."""
    out = build_constraint_preamble(CAFE_PERSONA["pkm_pack"])
    assert out.startswith(CONSTRAINT_PREAMBLE_HEADER)
    # locked → "반드시 지킬 것"
    assert "반드시 지킬 것" in out
    assert CAFE_LOCKED in out
    # brand preferred_tone → "톤:"
    assert "톤: " + CAFE_TONE in out
    # brand avoid_phrase → "금지:"
    assert "금지: " in out
    # series_format → "시리즈 포맷:"
    assert "시리즈 포맷: " + CAFE_SERIES in out


def test_build_constraint_preamble_fitness_directives() -> None:
    """두 번째 페르소나에서도 directive 가 구속 형태로 변환된다 (견고성)."""
    out = build_constraint_preamble(FITNESS_PERSONA["pkm_pack"])
    assert out.startswith(CONSTRAINT_PREAMBLE_HEADER)
    assert "반드시 지킬 것: 운동 효과를 과장하거나 단기간 보장 표현을 절대 쓰지 않는다" in out
    assert "톤: 차분하고 신뢰감 있는 코치 톤" in out
    assert "금지: " in out


def test_build_constraint_preamble_empty_graceful() -> None:
    """빈/None/무효 pack → "" (graceful)."""
    assert build_constraint_preamble({}) == ""
    assert build_constraint_preamble(None) == ""  # type: ignore[arg-type]
    assert build_constraint_preamble({"unknown_key": []}) == ""


def test_build_constraint_preamble_deterministic() -> None:
    """동일 pack 2회 → 동일 출력 (결정적)."""
    p = CAFE_PERSONA["pkm_pack"]
    assert build_constraint_preamble(p) == build_constraint_preamble(p)


# ─── ★ 강한 주입 통제 증명 (단일 변수 = preamble) ──────────────────────

def test_strong_injection_control_proof() -> None:
    """recording mock 으로 Arm A/B_strong 의 planning user 메시지를 비교:
      (a) Arm B_strong 의 user 메시지 = preamble + "\\n\\n" + base_input.
      (b) Arm A 의 user 메시지 = base_input.
      (c) 두 arm 모두 rag_context=[] → 어느 system prompt 에도 "참고 자료" 블록이 없다.
      (d) B_strong user 메시지에서 preamble prefix 를 제거하면 A 와 동일 (단일 변수 = preamble).
    """
    pack = CAFE_PERSONA["pkm_pack"]
    preamble = build_constraint_preamble(pack)
    expected_strong = preamble + "\n\n" + BASE_INPUT

    client = _make_recording_client()
    result = asyncio.run(
        run_ab_pair_fit(
            BASE_INPUT, pack,
            planning_client=client, critic_client=client, judge_client=client,
            models=MODELS,
        )
    )

    planning = _planning_calls(client)
    # arm 당 3 planning 호출 × 2 arm = 6.
    assert len(planning) == 6
    a_calls = planning[:3]
    b_calls = planning[3:]

    # (a)(b) user 메시지 (messages[1]) 검증 — 슬롯별 동일해야 함.
    for c in a_calls:
        assert c["messages"][1]["content"] == BASE_INPUT
    for c in b_calls:
        assert c["messages"][1]["content"] == expected_strong

    # (c) 어느 system prompt 에도 "참고 자료" 없음 (rag_context=[] 양 arm).
    for c in planning:
        assert "참고 자료" not in c["messages"][0]["content"]

    # (d) preamble prefix 제거 시 A 와 동일 (단일 변수).
    b_user = b_calls[0]["messages"][1]["content"]
    assert b_user.startswith(preamble + "\n\n")
    assert b_user[len(preamble) + 2 :] == BASE_INPUT
    # system prompt(approach hint 동일)도 슬롯별 A=B 동일 (preamble 은 user 측에만).
    for a_c, b_c in zip(a_calls, b_calls):
        assert a_c["messages"][0]["content"] == b_c["messages"][0]["content"]

    # preamble 은 결과에도 투명하게 노출된다.
    assert result["preamble"] == preamble


# ─── score_fit (객관 + judge 결합) ────────────────────────────────────

def test_score_fit_clean_plan() -> None:
    """금지어 없는 clean plan → avoid_clean True, fit_0_1 = judge_score (페널티 없음)."""
    judge = _make_fixed_judge_client(0.9)
    out = score_fit(_CLEAN_PLAN["plan"], CAFE_PERSONA["pkm_pack"], judge_client=judge)
    assert out["avoid_clean"] is True
    assert out["avoid_violations"] == []
    assert out["judge_score"] == pytest.approx(0.9)
    # 위반 없으므로 페널티 미적용.
    assert out["fit_0_1"] == pytest.approx(0.9)


def test_score_fit_avoid_violation_penalized() -> None:
    """금지어('최저가') 포함 plan → avoid_clean False + 위반 토큰, fit_0_1 에 페널티(×0.5)."""
    judge = _make_fixed_judge_client(0.8)
    out = score_fit(_DIRTY_PLAN_BODY, CAFE_PERSONA["pkm_pack"], judge_client=judge)
    assert out["avoid_clean"] is False
    assert CAFE_AVOID_TOKEN in out["avoid_violations"]
    assert out["judge_score"] == pytest.approx(0.8)
    # 위반 → judge_score × 0.5 페널티.
    assert out["fit_0_1"] == pytest.approx(0.4)


def test_score_fit_judge_failure_graceful() -> None:
    """judge 응답이 무효(fit_score 없음) → judge_score None, fit_0_1 None (graceful)."""
    bad = MagicMock()

    def _create(**kwargs):  # type: ignore[no-untyped-def]
        msg = MagicMock()
        msg.content = json.dumps({"no_score": True}, ensure_ascii=False)
        choice = MagicMock()
        choice.message = msg
        resp = MagicMock()
        resp.choices = [choice]
        return resp

    bad.chat.completions.create.side_effect = _create
    out = score_fit(_CLEAN_PLAN["plan"], CAFE_PERSONA["pkm_pack"], judge_client=bad)
    assert out["judge_score"] is None
    assert out["fit_0_1"] is None
    # 객관 파트는 여전히 동작.
    assert out["avoid_clean"] is True


# ─── run_ab_pair_fit ──────────────────────────────────────────────────

def test_run_ab_pair_fit_structure() -> None:
    """run_ab_pair_fit → arm_a / arm_b_strong + generic·fit delta. mock 채점은 동일 → delta 0."""
    client = _make_recording_client()
    result = asyncio.run(
        run_ab_pair_fit(
            BASE_INPUT, CAFE_PERSONA["pkm_pack"],
            planning_client=client, critic_client=client, judge_client=client,
            models=MODELS,
        )
    )
    assert result["arm_a"]["arm"] == ARM_A
    assert result["arm_b_strong"]["arm"] == ARM_B_STRONG
    assert result["arm_a"]["n_plans"] == 3
    assert result["arm_b_strong"]["n_plans"] == 3
    # generic: _FAKE_CRITIC 평균(0~1) = 3.875/5 = 0.775.
    assert result["arm_a"]["avg_generic_0_1"] == pytest.approx(0.775)
    # fit: clean plan(_CLEAN_PLAN 금지어 없음) → judge 0.9 그대로.
    assert result["arm_a"]["avg_fit_0_1"] == pytest.approx(0.9)
    assert result["arm_b_strong"]["avg_fit_0_1"] == pytest.approx(0.9)
    # mock 이 양 arm 동일 채점 → delta 0 (sanity; 실 신호는 opt-in real-mode).
    assert result["delta_generic_0_1"] == pytest.approx(0.0)
    assert result["delta_fit_0_1"] == pytest.approx(0.0)
    # per_plan 에 fit/adherence 필드가 실린다.
    p0 = result["arm_a"]["per_plan"][0]
    assert set(["index", "generic_0_1", "verdict", "fit_0_1", "judge_score",
                "avoid_clean", "avoid_violations"]).issubset(p0.keys())


def test_run_ab_pair_fit_no_real_llm_calls() -> None:
    """CI-safe 입증: 주입 mock 만 호출되고 실 OpenAI 생성자가 호출되지 않는다.

    arm 당 (3 planning + 3 critic + 3 judge) × 2 arm = 18 호출.
    """
    client = _make_recording_client()
    asyncio.run(
        run_ab_pair_fit(
            BASE_INPUT, CAFE_PERSONA["pkm_pack"],
            planning_client=client, critic_client=client, judge_client=client,
            models=MODELS,
        )
    )
    assert client.chat.completions.create.call_count == 18
