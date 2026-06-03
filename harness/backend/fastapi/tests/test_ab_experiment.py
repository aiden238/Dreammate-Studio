"""Phase 16 S1 — A/B 실험 하네스 단위 테스트 (mock-only, CI-safe).

검증 대상 (acceptance A1 통제 입증 중심):
  - 통제 증명(★ 핵심): 동일 mock client·동일 입력·동일 models 로 Arm A/B 를 run_arm 으로 돌릴 때,
    planning system prompt 가 Arm B 에서만 PKM snippet 을 포함하고, 나머지는 byte-identical
    임을 입증 — 두 arm 의 유일한 차이 = 주입 "참고 자료" 블록 (단일 변수 통제, A1).
  - pkm_pack_to_rag_context: §7.4 pack → [{title, snippet}] 형식.
  - build_arms 불변식: arm_a.rag_context == [] / arm_b 비어있지 않음 / 공유 필드 동일.
  - run_arm / run_ab_pair: 채점 평균 + B−A delta 산출 (mock 채점).

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
    ARM_B,
    ArmSpec,
    build_arms,
    pkm_pack_to_rag_context,
    run_ab_pair,
    run_arm,
)
from backend.fastapi.eval.ab_personas import CAFE_PERSONA, FITNESS_PERSONA

# A/B 가 공유하는 고정 입력/모델 (통제: arm 간 동일).
USER_INPUT = "우리 동네 카페 신메뉴 원두를 소개하는 30초 영상 기획해줘"
MODELS = ["gpt-4o-mini", "gpt-4o-mini", "gpt-4o-mini"]

# 통제 증명에서 찾을 PKM snippet (CAFE_PERSONA 의 잠금 선호 content).
PKM_SNIPPET = "과한 자막을 지양하고 손글씨 톤의 담백한 자막을 선호한다"


# ─── mock client ──────────────────────────────────────────────────────

# planning 이 받아들이는 최소 유효 plan envelope (parser 는 "plan" 키만 필수).
_FAKE_PLAN = {
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

# critic 이 받아들이는 최소 유효 verdict (compact 8차원 — default output_mode=compact).
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


def _make_recording_client() -> MagicMock:
    """planning·critic 호출을 모두 처리하는 recording mock OpenAI client.

    chat.completions.create 호출마다 messages 를 self._calls 에 기록한다.
    system prompt 로 planning/critic 을 구분해 알맞은 유효 JSON 을 반환한다
    (parallel_3 의 3 동시 호출 + critic 호출 모두 서빙).
    """
    client = MagicMock()
    client._calls = []  # list[dict] — 각 호출의 messages 기록

    def _create(*, messages, **kwargs):  # type: ignore[no-untyped-def]
        client._calls.append({"messages": messages, "kwargs": kwargs})
        system = messages[0]["content"] if messages else ""
        # critic system prompt 는 "품질 평가자(Critic)" 문구 포함 — 그것으로 분기.
        is_critic = "품질 평가자(Critic)" in system
        payload = _FAKE_CRITIC if is_critic else _FAKE_PLAN
        msg = MagicMock()
        msg.content = json.dumps(payload, ensure_ascii=False)
        choice = MagicMock()
        choice.message = msg
        response = MagicMock()
        response.choices = [choice]
        return response

    client.chat.completions.create.side_effect = _create
    return client


def _planning_calls(client: MagicMock) -> list[dict[str, Any]]:
    """기록된 호출 중 planning 호출(= Critic 아님)만 추린다."""
    return [
        c for c in client._calls
        if "품질 평가자(Critic)" not in c["messages"][0]["content"]
    ]


# ─── pkm_pack_to_rag_context ──────────────────────────────────────────

def test_pkm_pack_to_rag_context_shape() -> None:
    """§7.4 pack → list of {title, snippet} dict (각 의미 entry 1개)."""
    rc = pkm_pack_to_rag_context(CAFE_PERSONA["pkm_pack"])
    assert isinstance(rc, list) and len(rc) > 0
    for item in rc:
        assert set(item.keys()) == {"title", "snippet"}
        assert isinstance(item["title"], str) and item["title"]
        assert isinstance(item["snippet"], str) and item["snippet"]
    # 잠금 선호 content 가 어느 snippet 에든 들어가 있어야 한다.
    assert any(PKM_SNIPPET in item["snippet"] for item in rc)


def test_pkm_pack_to_rag_context_empty_graceful() -> None:
    """빈/None pack → 빈 list (graceful)."""
    assert pkm_pack_to_rag_context({}) == []
    assert pkm_pack_to_rag_context(None) == []  # type: ignore[arg-type]


def test_pkm_pack_to_rag_context_deterministic() -> None:
    """동일 pack 2회 변환 → 동일 결과 (결정적)."""
    p = FITNESS_PERSONA["pkm_pack"]
    assert pkm_pack_to_rag_context(p) == pkm_pack_to_rag_context(p)


# ─── build_arms 불변식 ────────────────────────────────────────────────

def test_build_arms_invariant() -> None:
    """arm_a.rag_context == [] / arm_b 비어있지 않음 / name 만 다르고 type 동일."""
    arm_a, arm_b = build_arms(CAFE_PERSONA["pkm_pack"])
    assert isinstance(arm_a, ArmSpec) and isinstance(arm_b, ArmSpec)
    assert arm_a.name == ARM_A
    assert arm_b.name == ARM_B
    assert arm_a.rag_context == []
    assert len(arm_b.rag_context) > 0
    # arm_b 의 rag_context 는 pack 변환 결과와 동일 (통제: B 만 주입).
    assert arm_b.rag_context == pkm_pack_to_rag_context(CAFE_PERSONA["pkm_pack"])


# ─── ★ 통제 증명 (A1 핵심 테스트) ─────────────────────────────────────

def test_control_proof_only_injected_context_differs() -> None:
    """동일 mock client·입력·models 로 Arm A/B 생성 시, planning system prompt 의
    유일한 차이가 주입 PKM "참고 자료" 블록임을 입증 (단일 변수 통제, acceptance A1).

      (a) Arm B 의 system prompt 는 PKM snippet 을 포함한다.
      (b) Arm A 의 system prompt 는 PKM snippet 을 포함하지 않는다.
      (c) PKM 참고 자료 블록을 제거하면 A 와 B 의 system prompt 가 byte-identical.
    """
    arm_a, arm_b = build_arms(CAFE_PERSONA["pkm_pack"])

    # 동일 client 를 재사용해 A → B 순서로 생성 (입력·models 동일).
    client = _make_recording_client()
    asyncio.run(run_arm(
        USER_INPUT, arm_a,
        planning_client=client, critic_client=client, models=MODELS,
    ))
    a_planning = _planning_calls(client)

    client_b = _make_recording_client()
    asyncio.run(run_arm(
        USER_INPUT, arm_b,
        planning_client=client_b, critic_client=client_b, models=MODELS,
    ))
    b_planning = _planning_calls(client_b)

    # parallel_3 → 각 arm 당 정확히 3 planning 호출.
    assert len(a_planning) == 3
    assert len(b_planning) == 3

    a_sys = a_planning[0]["messages"][0]["content"]
    b_sys = b_planning[0]["messages"][0]["content"]

    # (a) Arm B 는 PKM snippet 포함.
    assert PKM_SNIPPET in b_sys
    # (b) Arm A 는 PKM snippet 미포함.
    assert PKM_SNIPPET not in a_sys
    # B 에는 "참고 자료" 섹션 헤더가 있고 A 에는 없다.
    assert "참고 자료" in b_sys
    assert "참고 자료" not in a_sys

    # (c) B 에서 주입 블록(참고 자료 섹션)을 잘라내면 A 와 동일.
    #     planning._format_rag_context 는 "\n참고 자료 ..." 로 시작하는 블록을 추가하므로,
    #     "참고 자료" 헤더 직전까지 자르면 base system prompt 만 남는다.
    cut = b_sys.find("참고 자료")
    b_base = b_sys[:cut].rstrip("\n")
    a_base = a_sys.rstrip("\n")
    assert b_base == a_base, "주입 블록 제외 시 A/B system prompt 가 동일해야 한다 (단일 변수)"

    # user 메시지·temperature·max_tokens·model 등 나머지 호출 파라미터도 A=B 동일 (통제).
    assert a_planning[0]["messages"][1] == b_planning[0]["messages"][1]
    assert a_planning[0]["kwargs"] == b_planning[0]["kwargs"]


def test_control_proof_user_and_params_identical_across_arms() -> None:
    """통제 보강: 3 슬롯 각각의 user 메시지·kwargs(model/temp/max_tokens)가 A/B 동일."""
    arm_a, arm_b = build_arms(FITNESS_PERSONA["pkm_pack"])
    ca = _make_recording_client()
    cb = _make_recording_client()
    asyncio.run(run_arm(USER_INPUT, arm_a, planning_client=ca, critic_client=ca, models=MODELS))
    asyncio.run(run_arm(USER_INPUT, arm_b, planning_client=cb, critic_client=cb, models=MODELS))
    a_planning = _planning_calls(ca)
    b_planning = _planning_calls(cb)

    # 슬롯별(approach hint 순서 보존) 비교 — user 메시지·kwargs 전부 동일.
    for a_call, b_call in zip(a_planning, b_planning):
        assert a_call["messages"][1] == b_call["messages"][1]  # user 메시지
        assert a_call["kwargs"] == b_call["kwargs"]            # model/temp/max_tokens


# ─── run_arm / run_ab_pair 채점 ───────────────────────────────────────

def test_run_arm_scores_three_plans() -> None:
    """run_arm → 3 plan 채점 + 평균(0~5 / 0~1) 산출."""
    arm_a, _ = build_arms(CAFE_PERSONA["pkm_pack"])
    client = _make_recording_client()
    result = asyncio.run(run_arm(
        USER_INPUT, arm_a,
        planning_client=client, critic_client=client, models=MODELS,
    ))
    assert result["arm"] == ARM_A
    assert result["n_plans"] == 3
    assert len(result["per_plan"]) == 3
    # _FAKE_CRITIC 평균 = (4*7 + 3)/8 = 3.875 (0~5), 0.775 (0~1).
    assert result["avg_0_5"] == pytest.approx(3.875)
    assert result["avg_0_1"] == pytest.approx(0.775)
    for p in result["per_plan"]:
        assert p["verdict"] == "approve"


def test_run_ab_pair_delta() -> None:
    """run_ab_pair → arm_a/arm_b + delta. mock 채점이 동일하므로 delta = 0 (sanity)."""
    client = _make_recording_client()
    result = asyncio.run(run_ab_pair(
        USER_INPUT, CAFE_PERSONA["pkm_pack"],
        planning_client=client, critic_client=client, models=MODELS,
    ))
    assert result["arm_a"]["arm"] == ARM_A
    assert result["arm_b"]["arm"] == ARM_B
    # mock critic 이 양 arm 에 동일 점수 → delta 0 (채점 로직 sanity; 실 측정은 opt-in real-mode).
    assert result["delta_0_5"] == pytest.approx(0.0)
    assert result["delta_0_1"] == pytest.approx(0.0)


def test_run_ab_pair_no_real_llm_calls() -> None:
    """CI-safe 입증: 주입 mock 만 호출되고 실 OpenAI 생성자가 호출되지 않는다."""
    client = _make_recording_client()
    asyncio.run(run_ab_pair(
        USER_INPUT, CAFE_PERSONA["pkm_pack"],
        planning_client=client, critic_client=client, models=MODELS,
    ))
    # arm 당 (3 planning + 3 critic) × 2 arm = 12 호출.
    assert client.chat.completions.create.call_count == 12
