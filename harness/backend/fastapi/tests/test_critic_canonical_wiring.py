"""Phase 9 Slice 3 — normalize_to_canonical wiring (ADR-032).

orchestrator critic step 이 run_critic 결과를 normalize_to_canonical 로 감싸
critic_evaluation 에 canonical(overall_score 0–1 + dimensions) 을 추가하는지 검증.
deprecated 0–5(scores / overall_score_avg) 병행 유지 (NG3, 회귀 0).

검증 항목 (ADR-032 §Verification):
  1. test_wiring_adds_canonical    : critic_evaluation 에 overall_score 0–1 + dimensions 존재
  2. test_wiring_keeps_deprecated  : scores 0–5 + overall_score_avg 0–5 병행 유지
  3. test_canonical_in_range       : overall_score / dimensions 값 0.0~1.0 clamp
  4. test_canonical_matches_scores : dimensions[dim] == scores[dim] / 5.0

monkeypatch 대상은 routers.plans.* (orchestrator 가 router namespace 로 call-time 해석).
RecordingSink 불필요 — generate_plan 직접 호출 + mock agents.
"""

from __future__ import annotations

import copy
from typing import Any

import pytest

from backend.fastapi.db.types import PersistenceResult
from backend.fastapi.orchestration import generate_plan
from backend.fastapi.rag.types import RetrievalResult
from backend.fastapi.schemas.output import Envelope
from backend.fastapi.schemas.plans import GenerateRequest

_INTENT_OK: dict[str, Any] = {"intent_ok": True, "category": "video_planning"}

# 8-dim 0–5 (helper 가 /5.0 → 0–1 canonical 산출). avg = 4.0 → overall_score 0.8.
_SCORES_0_5 = {
    "intent_fit": 4, "target_clarity": 4, "hook_strength": 4, "message_clarity": 4,
    "structure": 4, "feasibility": 4, "brand_consistency": 4, "differentiation": 4,
}


def _make_plan_entry() -> dict[str, Any]:
    return {
        "plan_id": "test-plan-id",
        "status": "created",
        "created_at": "2026-05-30T00:00:00Z",
        "updated_at": "2026-05-30T00:00:00Z",
        "locale": "ko-KR",
        "initial_input": "유튜브 쇼츠 만들기",
        "wizard_data": {},
        "envelope": None,
    }


def _parallel_3_payload() -> list[dict[str, Any]]:
    labels = ["narrative", "informational", "experiment"]
    out: list[dict[str, Any]] = []
    for i in range(3):
        out.append({
            "plan": {
                "name": f"기획안 {i + 1}",
                "concept": f"콘셉트 {i + 1}",
                "hook": f"후크 {i + 1} — 시청 유지율 검증",
                "flow": [
                    {"beat_index": 0, "beat": "도입", "duration_sec": 3, "purpose": "관심"},
                    {"beat_index": 1, "beat": "전개", "duration_sec": 20, "purpose": "핵심"},
                    {"beat_index": 2, "beat": "마무리", "duration_sec": 7, "purpose": "CTA"},
                ],
                "pros": "장점",
                "risks": "위험",
                "approach_label": labels[i],
            }
        })
    return out


def _critic_0_5(plan: dict[str, Any], *args: Any, **kwargs: Any) -> dict[str, Any]:
    """run_critic 산출 형식 — 0–5 deprecated 형식만 반환 (canonical 미포함).

    orchestrator 의 normalize_to_canonical wiring 이 canonical 을 추가해야 정상.
    """
    return {
        "target_plan_id": str(plan.get("plan_id") or ""),
        "scores": dict(_SCORES_0_5),
        "reasons": {k: "—" for k in _SCORES_0_5},
        "suggestions": {k: "—" for k in _SCORES_0_5},
        "overall_score_avg": round(sum(_SCORES_0_5.values()) / len(_SCORES_0_5), 4),
        "overall_verdict": "approve",
        "blocking_issues": [],
        "revise_round": 0,
    }


def _db_save_ok(**kwargs: Any) -> PersistenceResult:
    return PersistenceResult(
        status="saved", project_id="fake-project", plan_candidate_ids=["fake-pc"],
        error_reason=None,
    )


def _rag_fallback(*args: Any, **kwargs: Any) -> RetrievalResult:
    return RetrievalResult(references=[], used_fallback=True, fallback_reason="pgvector_unreachable")


@pytest.fixture
def patch_agents_0_5(monkeypatch: pytest.MonkeyPatch) -> None:
    """Intent allow + RAG fallback + 3-plan + Critic(0–5 only) + DB save ok."""

    async def fake_parallel(*args: Any, **kwargs: Any) -> list[dict[str, Any]]:
        return copy.deepcopy(_parallel_3_payload())

    monkeypatch.setattr("backend.fastapi.routers.plans.run_intent", lambda *a, **k: dict(_INTENT_OK))
    monkeypatch.setattr("backend.fastapi.routers.plans.run_rag_retrieval", _rag_fallback)
    monkeypatch.setattr("backend.fastapi.routers.plans.run_planning_parallel_3", fake_parallel)
    monkeypatch.setattr("backend.fastapi.routers.plans.run_critic", _critic_0_5)
    monkeypatch.setattr("backend.fastapi.routers.plans.save_video_planning", _db_save_ok)


# ─── 1. canonical 추가 ────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_wiring_adds_canonical(patch_agents_0_5) -> None:
    """run_critic 가 0–5 만 반환해도 wiring 후 critic_evaluation 에 canonical 추가."""
    result = await generate_plan("test-plan-id", _make_plan_entry(), GenerateRequest())
    assert isinstance(result, Envelope)
    critic = result.body.critic_evaluation
    assert critic is not None
    # canonical (ADR-018) — wiring 으로 채워져야 함
    assert critic.overall_score is not None
    assert critic.dimensions  # non-empty dict
    assert len(critic.dimensions) == 8


# ─── 2. deprecated 0–5 병행 유지 (NG3) ────────────────────────────────


@pytest.mark.asyncio
async def test_wiring_keeps_deprecated(patch_agents_0_5) -> None:
    """canonical 추가에도 deprecated scores 0–5 + overall_score_avg 0–5 병행 유지 (회귀 0)."""
    result = await generate_plan("test-plan-id", _make_plan_entry(), GenerateRequest())
    assert isinstance(result, Envelope)
    critic = result.body.critic_evaluation
    assert critic is not None
    # deprecated 병행 유지 (helper 비파괴)
    assert critic.scores is not None
    assert critic.overall_score_avg is not None
    # scores 는 0–5 정수 (helper 가 원본 보존)
    assert critic.scores.intent_fit == 4
    assert critic.overall_score_avg == pytest.approx(4.0)


# ─── 3. canonical 0.0~1.0 범위 ────────────────────────────────────────


@pytest.mark.asyncio
async def test_canonical_in_range(patch_agents_0_5) -> None:
    """overall_score / dimensions 값 모두 0.0~1.0 범위."""
    result = await generate_plan("test-plan-id", _make_plan_entry(), GenerateRequest())
    assert isinstance(result, Envelope)
    critic = result.body.critic_evaluation
    assert critic is not None
    assert 0.0 <= critic.overall_score <= 1.0
    for dim, val in critic.dimensions.items():
        assert 0.0 <= val <= 1.0, f"{dim}={val} out of [0,1]"


# ─── 4. canonical 값 정합 (scores / 5.0) ──────────────────────────────


@pytest.mark.asyncio
async def test_canonical_matches_scores(patch_agents_0_5) -> None:
    """dimensions[dim] == scores[dim] / 5.0, overall_score == avg / 5.0."""
    result = await generate_plan("test-plan-id", _make_plan_entry(), GenerateRequest())
    assert isinstance(result, Envelope)
    critic = result.body.critic_evaluation
    assert critic is not None
    # 4 / 5.0 = 0.8
    assert critic.dimensions["intent_fit"] == pytest.approx(0.8)
    assert critic.dimensions["hook_strength"] == pytest.approx(0.8)
    # avg(4.0) / 5.0 = 0.8
    assert critic.overall_score == pytest.approx(0.8)
