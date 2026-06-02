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
    DIMENSIONS_RICH,
    PROMPT_ID,
    PROMPT_VERSION,
    RICH_PROMPT_VERSION,
    _derive_verdict,
    normalize_to_canonical,
    run_critic,
    select_best_plan_index,
)
from backend.fastapi.config import get_settings
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
    """P-007 / v1.1.0 매핑 확인 (Phase 8 ADR-029 adapter, output_schema.md §9)."""
    assert PROMPT_ID == "P-007"
    assert PROMPT_VERSION == "v1.1.0"


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
    """run_critic 0–5 출력 → normalize_to_canonical → CriticEvaluation canonical 검증.

    Phase 9.5 ADR-034: orchestrator 흐름 모방. CriticEvaluation 은 canonical(overall_score
    0–1 + dimensions) 만 보존하고 deprecated 0–5 키(scores / overall_score_avg)는
    extra='ignore' 로 무시 → 회귀 0.
    """
    scores = _full_scores(4)
    client = _make_fake_client(_make_response(scores=scores, verdict="approve"))

    result = run_critic(_SAMPLE_PLAN, client=client, model="gpt-4o")
    verdict = normalize_to_canonical(result)  # orchestrator wiring (ADR-032)
    evaluation = CriticEvaluation(**verdict)
    assert evaluation.target_plan_id == _SAMPLE_PLAN["plan_id"]
    assert evaluation.overall_verdict == "approve"
    # canonical (ADR-018): overall_score 0–1 + dimensions 0–1
    assert evaluation.overall_score == pytest.approx(0.8)  # 4/5
    assert evaluation.dimensions["hook_strength"] == pytest.approx(0.8)
    assert evaluation.revise_round == 0
    # deprecated 0–5 키는 extra='ignore' 로 모델에 미존재 (ADR-034)
    assert not hasattr(evaluation, "scores")
    assert not hasattr(evaluation, "overall_score_avg")


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


# ─── Phase 4.5 Slice 3 — select_best_plan_index (Z-X3) ────────────────


def test_select_best_plan_index_returns_highest_score() -> None:
    """canonical overall_score 기준 가장 높은 verdict 의 index 반환.

    Phase 9.5 ADR-034: deprecated 0–5 fallback(overall_score_avg) 제거 — canonical
    overall_score(0–1) 만 소비. DeprecationWarning 미발행.
    """
    verdicts = [
        {"overall_score": 0.5},
        {"overall_score": 0.9},
        {"overall_score": 0.6},
    ]
    assert select_best_plan_index(verdicts) == 1


def test_select_best_plan_index_tie_breaking_prefers_lower_index() -> None:
    """동점 시 plan_index 가 더 작은 쪽 (deterministic) — canonical overall_score.

    Phase 9.5 ADR-034: canonical-only (deprecated 0–5 fallback 제거).
    """
    verdicts = [
        {"overall_score": 0.8},
        {"overall_score": 0.8},  # tie with idx 0
        {"overall_score": 0.6},
    ]
    assert select_best_plan_index(verdicts) == 0


def test_select_best_plan_index_empty_returns_none() -> None:
    """빈 list → None."""
    assert select_best_plan_index([]) is None


def test_select_best_plan_index_all_invalid_returns_none() -> None:
    """모든 verdict 가 invalid (None / 빈 dict / 비숫자) → None.

    Phase 9.5 ADR-034: deprecated 0–5 키(overall_score_avg)는 더 이상 score 추출에
    사용되지 않으므로 canonical 부재 → None (DeprecationWarning 미발행).
    """
    verdicts: list[dict[str, Any]] = [
        {"overall_score": None},
        {},
        {"overall_score": "not a number"},
        {"overall_score_avg": 4.0},  # deprecated 키 — ADR-034 이후 무시 → None 기여
    ]
    assert select_best_plan_index(verdicts) is None


def test_select_best_plan_index_uses_dimensions_fallback() -> None:
    """overall_score 부재 시 canonical dimensions dict 평균 fallback.

    Phase 9.5 ADR-034: deprecated 0–5 scores fallback 제거 — canonical dimensions(0–1)
    만 fallback. DeprecationWarning 미발행.
    """
    verdicts = [
        {"dimensions": {k: 0.4 for k in DIMENSIONS}},  # avg 0.4
        {"dimensions": {k: 0.8 for k in DIMENSIONS}},  # avg 0.8
        {"dimensions": {k: 0.6 for k in DIMENSIONS}},  # avg 0.6
    ]
    assert select_best_plan_index(verdicts) == 1


def test_select_best_plan_index_skips_invalid_uses_remaining() -> None:
    """일부 invalid 섞여 있어도 유효한 canonical verdict 중 최고 점수 index 반환.

    Phase 9.5 ADR-034: canonical-only (deprecated 0–5 fallback 제거).
    """
    verdicts: list[dict[str, Any]] = [
        {"overall_score": None},  # invalid → skip
        {"overall_score": 0.6},
        {},  # invalid → skip
        {"overall_score": 0.8},
    ]
    assert select_best_plan_index(verdicts) == 3


def test_select_best_plan_index_deprecated_keys_ignored_returns_none() -> None:
    """Phase 9.5 ADR-034: deprecated 0–5 키(overall_score_avg / scores / eight_dim_scores)
    만 있는 verdict 는 canonical 부재로 간주 → None (fallback 제거)."""
    verdicts: list[dict[str, Any]] = [
        {"overall_score_avg": 4.5},
        {"scores": {k: 4 for k in DIMENSIONS}},
        {"eight_dim_scores": {k: 4 for k in DIMENSIONS}},
    ]
    assert select_best_plan_index(verdicts) is None


# ─── Phase 6 Slice 2: canonical priority (ADR-018) ───────────────────


def test_select_best_plan_index_canonical_overall_score_preferred() -> None:
    """Phase 6 ADR-018: overall_score (canonical) 가 dimensions / overall_score_avg 보다 우선.

    canonical key 만 있는 verdict 는 DeprecationWarning 발행 없이 동작.
    """
    verdicts = [
        {"overall_score": 0.3},  # canonical
        {"overall_score": 0.9},  # canonical — best
        {"overall_score": 0.6},  # canonical
    ]
    # canonical key 사용 → DeprecationWarning 발행 없어야 함
    import warnings as _warnings
    with _warnings.catch_warnings():
        _warnings.simplefilter("error", DeprecationWarning)
        # canonical key 만 사용하므로 DeprecationWarning 발생 시 즉시 fail
        assert select_best_plan_index(verdicts) == 1


def test_select_best_plan_index_canonical_dimensions_fallback() -> None:
    """Phase 6 ADR-018: overall_score 부재 시 dimensions (canonical) 평균 사용.

    canonical fallback — DeprecationWarning 발행 없이 동작.
    """
    verdicts = [
        {"dimensions": {"hook": 0.2, "target": 0.3}},  # avg 0.25
        {"dimensions": {"hook": 0.8, "target": 0.9}},  # avg 0.85 — best
        {"dimensions": {"hook": 0.5, "target": 0.6}},  # avg 0.55
    ]
    import warnings as _warnings
    with _warnings.catch_warnings():
        _warnings.simplefilter("error", DeprecationWarning)
        assert select_best_plan_index(verdicts) == 1


def test_select_best_plan_index_canonical_overrides_deprecated() -> None:
    """Phase 6 ADR-018: overall_score (canonical) + overall_score_avg (deprecated) 동시 존재.

    canonical 우선 — overall_score_avg 미사용이므로 DeprecationWarning 발행 없음.
    """
    verdicts = [
        # canonical 0.9 vs deprecated avg 1.0 (의도적 불일치 — canonical 우선 검증)
        {"overall_score": 0.9, "overall_score_avg": 1.0},
        {"overall_score": 0.5, "overall_score_avg": 5.0},
        {"overall_score": 0.3, "overall_score_avg": 4.0},
    ]
    # canonical 만 사용되어야 함 → idx 0 (0.9 가 최고)
    import warnings as _warnings
    with _warnings.catch_warnings():
        _warnings.simplefilter("error", DeprecationWarning)
        assert select_best_plan_index(verdicts) == 0


def test_select_best_plan_index_eight_dim_scores_ignored_no_warning() -> None:
    """Phase 9.5 ADR-034: eight_dim_scores deprecated fallback 제거 — canonical 부재로
    간주되어 무시 (DeprecationWarning 미발행, None 반환). canonical 우선은 불변."""
    import warnings as _warnings
    verdicts = [
        {"eight_dim_scores": {k: 2 for k in DIMENSIONS}},
        {"eight_dim_scores": {k: 4 for k in DIMENSIONS}},
    ]
    with _warnings.catch_warnings():
        _warnings.simplefilter("error", DeprecationWarning)
        # deprecated 키만 → canonical 부재 → None (warning 미발행)
        assert select_best_plan_index(verdicts) is None
    # canonical 동반 시 canonical 만 사용 (eight_dim_scores 무시)
    mixed = [
        {"overall_score": 0.3, "eight_dim_scores": {k: 5 for k in DIMENSIONS}},
        {"overall_score": 0.9, "eight_dim_scores": {k: 1 for k in DIMENSIONS}},
    ]
    with _warnings.catch_warnings():
        _warnings.simplefilter("error", DeprecationWarning)
        assert select_best_plan_index(mixed) == 1


# ─── Phase 6 Slice 2: CriticEvaluation canonical fields (ADR-018) ────


def test_critic_evaluation_canonical_fields_optional() -> None:
    """Phase 6 ADR-018: CriticEvaluation canonical (overall_score + dimensions) 단독 인스턴스화."""
    evaluation = CriticEvaluation(
        overall_score=0.85,
        dimensions={"hook_strength": 0.8, "target_clarity": 0.9},
        overall_verdict="approve",
    )
    assert evaluation.overall_score == pytest.approx(0.85)
    assert evaluation.dimensions["hook_strength"] == pytest.approx(0.8)
    # Phase 1 호환 메타는 None / 기본값
    assert evaluation.target_plan_id is None
    # Phase 9.5 ADR-034: deprecated 0–5 필드(scores / overall_score_avg) 제거 → 모델에 미존재
    assert not hasattr(evaluation, "scores")
    assert not hasattr(evaluation, "overall_score_avg")


def test_critic_evaluation_ignores_deprecated_0_5_keys() -> None:
    """Phase 9.5 ADR-034: verdict dict 의 deprecated 0–5 키(scores / overall_score_avg)는
    extra='ignore' 로 무시되고 canonical 만 추출 → CriticEvaluation(**verdict) 회귀 0.

    orchestrator 가 normalize_to_canonical 산출 verdict(0–5 병행)를 그대로 넘기는 흐름 모방.
    """
    evaluation = CriticEvaluation(
        target_plan_id="plan-abc",
        scores={k: 4 for k in DIMENSIONS},  # deprecated 0–5 — 무시되어야 함
        overall_score_avg=4.0,  # deprecated 0–5 — 무시되어야 함
        overall_score=0.8,  # canonical
        dimensions={k: 0.8 for k in DIMENSIONS},  # canonical
        overall_verdict="approve",
        blocking_issues=[],
        revise_round=0,
    )
    # Phase 1 호환 메타 유지
    assert evaluation.target_plan_id == "plan-abc"
    # canonical 유지
    assert evaluation.overall_score == pytest.approx(0.8)
    assert evaluation.dimensions["hook_strength"] == pytest.approx(0.8)
    # deprecated 0–5 키는 무시 (모델 속성 미존재)
    assert not hasattr(evaluation, "scores")
    assert not hasattr(evaluation, "overall_score_avg")


# ─── Phase 13 Slice S4 — gated depth_actionability (9차원, ON 경로) ────
#
# 검증:
#   - ON(rich_output_enabled=True): RICH_SYSTEM_PROMPT + DIMENSIONS_RICH 9차원 평가
#     → result["scores"] 에 depth_actionability 포함, avg 가 9 점수 평균.
#   - "88점 함정" 해소: 8 차원 강함 + depth 낮음(rich 슬롯 빈약) plan 이
#     ON(9차원 avg) 에서 OFF(8차원 avg) 보다 낮게 채점된다.
#   - OFF 경로는 위 기존 테스트가 byte-identical 보장(8키, depth_actionability 미존재).
#
# config override 는 기존 관례 (monkeypatch.setenv("RICH_OUTPUT_ENABLED") + cache_clear).
# 전부 mock — 실 LLM 호출 0, 실 키 불필요.


def _set_rich_flag(monkeypatch: pytest.MonkeyPatch, enabled: bool) -> None:
    """settings.rich_output_enabled override (lru_cache 재생성)."""
    monkeypatch.setenv("RICH_OUTPUT_ENABLED", "true" if enabled else "false")
    get_settings.cache_clear()
    assert get_settings().rich_output_enabled is enabled


def _full_scores_rich(value: int = 4) -> dict[str, int]:
    """9차원(depth_actionability 포함) 동일값 점수."""
    return {k: value for k in DIMENSIONS_RICH}


def _make_response_rich(
    *,
    scores: dict[str, int],
    verdict: str = "approve",
    blocking: list[str] | None = None,
) -> str:
    """9차원 critic LLM 응답 JSON 문자열 생성 (reasons/suggestions 9키)."""
    payload = {
        "scores": scores,
        "reasons": {k: f"{k} 평가 사유" for k in DIMENSIONS_RICH},
        "suggestions": {k: f"{k} 개선 제안" for k in DIMENSIONS_RICH},
        "overall_verdict": verdict,
        "blocking_issues": blocking or [],
    }
    return json.dumps(payload, ensure_ascii=False)


def test_critic_rich_version_constant() -> None:
    """gated rich 버전 상수 — ON 경로 P-007 v1.2.0 (OFF=v1.1.0 불변)."""
    assert PROMPT_VERSION == "v1.1.0"  # OFF/active 불변
    assert RICH_PROMPT_VERSION == "v1.2.0"  # gated rich 9차원
    assert DIMENSIONS_RICH == DIMENSIONS + ("depth_actionability",)
    assert len(DIMENSIONS_RICH) == 9


def test_critic_on_returns_9_dim_scores(monkeypatch: pytest.MonkeyPatch) -> None:
    """ON: 9차원 mock → result["scores"] 에 depth_actionability 포함, avg=9 평균."""
    _set_rich_flag(monkeypatch, True)
    scores = _full_scores_rich(4)
    client = _make_fake_client(_make_response_rich(scores=scores, verdict="approve"))

    result = run_critic(_SAMPLE_PLAN, client=client, model="gpt-4o")

    assert set(result["scores"].keys()) == set(DIMENSIONS_RICH)
    assert "depth_actionability" in result["scores"]
    assert result["scores"]["depth_actionability"] == 4
    # reasons/suggestions 도 9키 보강
    assert "depth_actionability" in result["reasons"]
    assert result["suggestions"]["depth_actionability"]
    # avg = 9 점수 평균 (전부 4 → 4.0)
    assert result["overall_score_avg"] == pytest.approx(4.0)
    assert result["overall_verdict"] == "approve"


def test_critic_on_requires_depth_dimension(monkeypatch: pytest.MonkeyPatch) -> None:
    """ON: depth_actionability 누락 시 ValueError (9키 검증)."""
    _set_rich_flag(monkeypatch, True)
    scores = _full_scores(4)  # 8키만 — depth_actionability 없음
    client = _make_fake_client(_make_response(scores=scores, verdict="approve"))

    with pytest.raises(ValueError, match="누락"):
        run_critic(_SAMPLE_PLAN, client=client, model="gpt-4o")


def test_critic_88_trap_resolved_shallow_plan_scores_lower(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """"88점 함정" 해소: 8차원 강함 + 깊이 낮은 얕은 plan 이 ON(9차원) 에서
    OFF(8차원) 대비 avg 하락.

    같은 8차원 점수(평균 ~4.4 = 0.88 정규화 = "88점")를 OFF 와 ON 양쪽에 주되,
    ON 에서는 depth_actionability=1(rich 슬롯 빈약한 얕은 plan)을 추가 → 9차원 평균이
    8차원 평균보다 낮아진다. 즉 OFF 에서 approve 되던 얕은 plan 이 깊이 페널티를 받는다.
    """
    # 8차원: 평균 4.375 ≈ 0.875 정규화 ("88점 함정" 재현용 고득점)
    eight_dim = {
        "intent_fit": 5,
        "target_clarity": 4,
        "hook_strength": 5,
        "message_clarity": 4,
        "structure": 4,
        "feasibility": 5,
        "brand_consistency": 4,
        "differentiation": 4,
    }
    off_avg_expected = sum(eight_dim.values()) / 8  # 35/8 = 4.375

    # OFF: 8차원만 채점 (depth 미평가) → 기존 "88점" 결과 재현.
    _set_rich_flag(monkeypatch, False)
    off_client = _make_fake_client(_make_response(scores=eight_dim, verdict="approve"))
    off_result = run_critic(_SAMPLE_PLAN, client=off_client, model="gpt-4o")
    assert off_result["overall_score_avg"] == pytest.approx(off_avg_expected)
    assert "depth_actionability" not in off_result["scores"]

    # ON: 동일 8차원 + depth_actionability=1 (얕은 plan — rich 슬롯 빈약).
    nine_dim = dict(eight_dim)
    nine_dim["depth_actionability"] = 1
    on_avg_expected = sum(nine_dim.values()) / 9  # 36/9 = 4.0
    _set_rich_flag(monkeypatch, True)
    on_client = _make_fake_client(_make_response_rich(scores=nine_dim, verdict="approve"))
    on_result = run_critic(_SAMPLE_PLAN, client=on_client, model="gpt-4o")

    # ★ 88점 함정 해소: ON avg < OFF avg (깊이 페널티 반영)
    assert on_result["overall_score_avg"] < off_result["overall_score_avg"]
    assert on_result["overall_score_avg"] == pytest.approx(on_avg_expected)
    assert on_result["scores"]["depth_actionability"] == 1


def test_critic_on_canonical_includes_depth(monkeypatch: pytest.MonkeyPatch) -> None:
    """ON: normalize_to_canonical → CriticEvaluation.dimensions 에 9번째 키 additive.

    dimensions 가 자유 dict 이므로 depth_actionability 가 스키마 위반 없이 들어간다.
    """
    _set_rich_flag(monkeypatch, True)
    scores = _full_scores_rich(4)
    scores["depth_actionability"] = 2  # 2/5 = 0.4
    client = _make_fake_client(_make_response_rich(scores=scores, verdict="approve"))

    result = run_critic(_SAMPLE_PLAN, client=client, model="gpt-4o")
    verdict = normalize_to_canonical(result)
    evaluation = CriticEvaluation(**verdict)
    assert len(evaluation.dimensions) == 9
    assert evaluation.dimensions["depth_actionability"] == pytest.approx(0.4)


def test_derive_verdict_rich_dimensions_arg() -> None:
    """_derive_verdict(dimensions=DIMENSIONS_RICH): 9차원 평균 + 미달 카운트.

    OFF 호출(인자 생략)은 기존 8차원 — byte-identical (test_derive_verdict_rules 가 보장).
    """
    # 8차원 전부 4 + depth 1 → 9 평균 = (32+1)/9 = 3.666... → revise (1개 < 2)
    scores = _full_scores_rich(4)
    scores["depth_actionability"] = 1
    avg, v = _derive_verdict(scores, dimensions=DIMENSIONS_RICH)
    assert avg == pytest.approx((4 * 8 + 1) / 9, abs=1e-4)  # round(.,4)
    assert v == "revise"  # depth 1 < 2 → 1개 차원 미달

    # 8차원 인자 생략(기본값) → depth 무시, 8차원 평균만 (기존 동작)
    avg8, v8 = _derive_verdict(scores)
    assert avg8 == pytest.approx(4.0)
    assert v8 == "approve"
