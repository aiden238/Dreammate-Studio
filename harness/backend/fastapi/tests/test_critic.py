"""Critic Agent (P-007) 단위 테스트 — Phase 1 Slice 3.

검증 대상:
  - run_critic() 가 OpenAI 클라이언트 mock으로 동작
  - 정상 plan → 8 차원 점수 + verdict 반환
  - 약한 hook plan (FC-001 풍) → hook_strength ≤ 2 + suggestion 채움
  - 모호한 target plan (FC-002 풍) → target_clarity ≤ 2
  - 광고적 표현 plan (FC-004 풍) → brand_consistency ≤ 2 + reject + blocking
  - overall_score_avg 산출 정확성
  - scores 0~5 clamp (LLM이 범위 밖 값 반환 시 보정)
  - schema validation (scores 누락 시 ValueError)
  - JSON 파싱 실패 → ValueError
  - CriticEvaluation Pydantic 모델 직렬화 통과
"""

from __future__ import annotations

import json
from typing import Any
from unittest.mock import MagicMock

import pytest

from backend.fastapi.agents.critic import (
    DIMENSIONS,
    PROMPT_ID,
    PROMPT_VERSION,
    _derive_verdict,
    run_critic,
)
from backend.fastapi.schemas.output import CriticEvaluation


# ─── Helpers ──────────────────────────────────────────────────────────

def _make_fake_client(content: str) -> MagicMock:
    """OpenAI client mock — chat.completions.create 응답 1개 주입."""
    client = MagicMock()
    msg = MagicMock()
    msg.content = content
    choice = MagicMock()
    choice.message = msg
    response = MagicMock()
    response.choices = [choice]
    client.chat.completions.create.return_value = response
    return client


def _full_scores(value: int = 4) -> dict[str, int]:
    return {k: value for k in DIMENSIONS}


def _make_response(
    *,
    scores: dict[str, int],
    verdict: str = "approve",
    blocking: list[str] | None = None,
) -> str:
    """완전한 critic LLM 응답 JSON 문자열 생성."""
    payload = {
        "scores": scores,
        "reasons": {k: f"{k} 평가 사유" for k in DIMENSIONS},
        "suggestions": {k: f"{k} 개선 제안" for k in DIMENSIONS},
        "overall_verdict": verdict,
        "blocking_issues": blocking or [],
    }
    return json.dumps(payload, ensure_ascii=False)


_SAMPLE_PLAN: dict[str, Any] = {
    "plan_id": "22222222-2222-2222-2222-222222222222",
    "option_index": 0,
    "name": "첫 영상 시작하기",
    "concept": "초보 유튜버를 위한 채널 첫 영상",
    "hook": "구독자 0명에서 시작한 채널이 첫 영상으로 한 일",
    "flow": [
        {"beat_index": 0, "beat": "도입", "duration_sec": 3, "purpose": "관심 유발"},
        {"beat_index": 1, "beat": "전개", "duration_sec": 20, "purpose": "신뢰 형성"},
        {"beat_index": 2, "beat": "마무리", "duration_sec": 7, "purpose": "재방문"},
    ],
    "pros": "친근함",
    "risks": "후크 약함 가능",
    "approach_label": "narrative",
}


# ─── 메타 ─────────────────────────────────────────────────────────────

def test_critic_prompt_meta() -> None:
    """P-007 / v1.0.0 매핑 확인 (output_schema.md §9)."""
    assert PROMPT_ID == "P-007"
    assert PROMPT_VERSION == "v1.0.0"


# ─── 정상 plan → approve verdict ──────────────────────────────────────

def test_critic_returns_8_dim_scores_and_verdict() -> None:
    """좋은 plan → 모든 점수 ≥ 3, verdict approve, blocking 비어있음."""
    scores = _full_scores(4)
    client = _make_fake_client(_make_response(scores=scores, verdict="approve"))

    result = run_critic(_SAMPLE_PLAN, client=client, model="gpt-4o")

    assert result["target_plan_id"] == _SAMPLE_PLAN["plan_id"]
    assert set(result["scores"].keys()) == set(DIMENSIONS)
    for k, v in result["scores"].items():
        assert v == 4, f"{k} expected 4, got {v}"
    assert result["overall_verdict"] == "approve"
    assert result["overall_score_avg"] == pytest.approx(4.0)
    assert result["blocking_issues"] == []
    assert result["revise_round"] == 0


# ─── overall_score_avg 산출 검증 ──────────────────────────────────────

def test_critic_average_calculation_correct() -> None:
    """8개 점수 산술 평균 = overall_score_avg."""
    scores = {
        "intent_fit": 5,
        "target_clarity": 4,
        "hook_strength": 3,
        "message_clarity": 4,
        "structure": 4,
        "feasibility": 3,
        "brand_consistency": 5,
        "differentiation": 2,
    }
    expected_avg = sum(scores.values()) / 8  # 30/8 = 3.75
    client = _make_fake_client(_make_response(scores=scores, verdict="approve"))

    result = run_critic(_SAMPLE_PLAN, client=client, model="gpt-4o")
    assert result["overall_score_avg"] == pytest.approx(expected_avg)


# ─── FC-001 후킹 약함 ────────────────────────────────────────────────

def test_critic_flags_weak_hook_fc001() -> None:
    """FC-001 패턴: '안녕하세요' 형 hook → hook_strength ≤ 2 + suggestion 채움."""
    scores = _full_scores(4)
    scores["hook_strength"] = 1
    client = _make_fake_client(_make_response(scores=scores, verdict="revise"))

    weak_plan = dict(_SAMPLE_PLAN)
    weak_plan["hook"] = "안녕하세요, 오늘은 재테크에 대해 알아보겠습니다."

    result = run_critic(weak_plan, client=client, model="gpt-4o")

    assert result["scores"]["hook_strength"] <= 2
    assert result["suggestions"]["hook_strength"], "hook_strength suggestion 비어있으면 안 됨"
    # 1개 차원 < 2 → revise (output_schema §9.2)
    assert result["overall_verdict"] == "revise"


# ─── FC-002 타겟 모호 ────────────────────────────────────────────────

def test_critic_flags_vague_target_fc002() -> None:
    """FC-002 패턴: '모든 사람' 타겟 → target_clarity ≤ 2."""
    scores = _full_scores(4)
    scores["target_clarity"] = 1
    client = _make_fake_client(_make_response(scores=scores, verdict="revise"))

    vague_plan = dict(_SAMPLE_PLAN)
    vague_plan["concept"] = "건강에 관심 있는 모든 사람 (10~60대)"

    result = run_critic(vague_plan, client=client, model="gpt-4o")

    assert result["scores"]["target_clarity"] <= 2
    assert result["overall_verdict"] == "revise"


# ─── FC-004 광고적 표현 ──────────────────────────────────────────────

def test_critic_flags_ad_phrases_fc004() -> None:
    """FC-004 패턴: 광고 표현 다수 → brand_consistency 낮음 + reject + blocking."""
    # 3개 이상 차원 < 2 → reject (output_schema §9.2)
    scores = {
        "intent_fit": 3,
        "target_clarity": 1,
        "hook_strength": 1,
        "message_clarity": 1,
        "structure": 2,
        "feasibility": 3,
        "brand_consistency": 1,
        "differentiation": 1,
    }
    client = _make_fake_client(
        _make_response(
            scores=scores,
            verdict="reject",
            blocking=["광고 표현 다수: 혁신적, 최고의, 완벽한", "전면 재작성 필요"],
        )
    )

    bad_plan = dict(_SAMPLE_PLAN)
    bad_plan["hook"] = "혁신적인 수제 비누의 최고의 경험을 만나보세요."

    result = run_critic(bad_plan, client=client, model="gpt-4o")

    assert result["scores"]["brand_consistency"] <= 2
    assert result["overall_verdict"] == "reject"
    assert len(result["blocking_issues"]) >= 1


# ─── score clamp (LLM이 범위 밖 값 반환) ──────────────────────────────

def test_critic_clamps_scores_to_0_5_range() -> None:
    """LLM이 6 또는 -1 같은 범위 밖 값 반환 → 0~5로 clamp."""
    scores = _full_scores(3)
    scores["intent_fit"] = 7  # out of range
    scores["differentiation"] = -2  # out of range
    client = _make_fake_client(_make_response(scores=scores, verdict="approve"))

    result = run_critic(_SAMPLE_PLAN, client=client, model="gpt-4o")
    assert result["scores"]["intent_fit"] == 5
    assert result["scores"]["differentiation"] == 0


# ─── verdict 보정 (LLM이 모순된 verdict 내면 규칙 우선) ───────────────

def test_critic_server_corrects_inconsistent_verdict() -> None:
    """LLM이 낮은 점수 (avg=1.5) 인데 verdict=approve로 보내면 reject로 보정."""
    scores = _full_scores(1)  # avg = 1.0 → reject 규칙
    client = _make_fake_client(_make_response(scores=scores, verdict="approve"))

    result = run_critic(_SAMPLE_PLAN, client=client, model="gpt-4o")
    # output_schema §9.2: avg < 2.5 → reject 강제
    assert result["overall_verdict"] == "reject"


# ─── _derive_verdict 헬퍼 단위 테스트 ─────────────────────────────────

def test_derive_verdict_rules() -> None:
    """output_schema §9.2 verdict 규칙 단위 검증."""
    # approve: avg≥3.5 AND 모든 점수≥2
    avg, v = _derive_verdict(_full_scores(4))
    assert avg == pytest.approx(4.0) and v == "approve"

    # revise: 2.5 ≤ avg < 3.5
    scores = _full_scores(3)
    avg, v = _derive_verdict(scores)
    assert v == "revise"

    # revise: 1~2개 차원 < 2 (나머지 평균은 높아도)
    scores = _full_scores(4)
    scores["hook_strength"] = 1
    avg, v = _derive_verdict(scores)
    assert v == "revise"

    # reject: 3개+ 차원 < 2
    scores = _full_scores(4)
    scores["hook_strength"] = 1
    scores["target_clarity"] = 1
    scores["feasibility"] = 0
    avg, v = _derive_verdict(scores)
    assert v == "reject"

    # reject: avg < 2.5
    avg, v = _derive_verdict(_full_scores(2))
    assert avg == pytest.approx(2.0) and v == "reject"


# ─── Pydantic 직렬화 (router 흐름 모방) ───────────────────────────────

def test_critic_output_passes_pydantic_schema() -> None:
    """LLM 응답이 CriticEvaluation Pydantic 모델로 검증 통과."""
    scores = _full_scores(4)
    client = _make_fake_client(_make_response(scores=scores, verdict="approve"))

    result = run_critic(_SAMPLE_PLAN, client=client, model="gpt-4o")
    evaluation = CriticEvaluation(**result)
    assert evaluation.target_plan_id == _SAMPLE_PLAN["plan_id"]
    assert evaluation.overall_verdict == "approve"
    assert evaluation.scores.hook_strength == 4
    assert evaluation.revise_round == 0


# ─── 오류 케이스 ──────────────────────────────────────────────────────

def test_critic_raises_on_invalid_json() -> None:
    """깨진 JSON → ValueError."""
    client = _make_fake_client("not a json")
    with pytest.raises(ValueError, match="JSON 파싱 실패"):
        run_critic(_SAMPLE_PLAN, client=client, model="gpt-4o")


def test_critic_raises_on_missing_scores() -> None:
    """scores 객체 누락 → ValueError."""
    client = _make_fake_client(json.dumps({"overall_verdict": "approve"}))
    with pytest.raises(ValueError, match="scores"):
        run_critic(_SAMPLE_PLAN, client=client, model="gpt-4o")


def test_critic_raises_on_partial_scores() -> None:
    """scores 차원 일부 누락 → ValueError."""
    partial = {"intent_fit": 4, "hook_strength": 3}  # 나머지 6개 누락
    client = _make_fake_client(
        json.dumps(
            {
                "scores": partial,
                "reasons": {},
                "suggestions": {},
                "overall_verdict": "approve",
                "blocking_issues": [],
            }
        )
    )
    with pytest.raises(ValueError, match="누락"):
        run_critic(_SAMPLE_PLAN, client=client, model="gpt-4o")
