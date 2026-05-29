"""Phase 7 Slice 2 — 5단계 transition logic tests.

References:
  - backend/fastapi/rag/promotion.py
  - docs/decisions/phase_7_promotion_logic.md (ADR-026)
  - docs/contracts/rag_data_contract.md §18.3
"""
from __future__ import annotations

import pytest

from backend.fastapi.rag.promotion import (
    AUTO_APPROVE_THRESHOLD,
    EVAL_PASS_THRESHOLD,
    promotion_history_entry,
    transition,
)


def test_transition_pending_to_filtered() -> None:
    """1단계 → 2단계 자동 (quality_filter PASS)."""
    item: dict = {"stage": "pending"}
    result = transition(item, "filtered", reason="quality_pass")
    assert result["stage"] == "filtered"
    assert len(result["promotion_history"]) == 1
    entry = result["promotion_history"][0]
    assert entry["from"] == "pending"
    assert entry["to"] == "filtered"
    assert entry["reason"] == "quality_pass"
    assert "at" in entry


def test_transition_filtered_to_evaluated_with_scores() -> None:
    """2단계 → 3단계 자동 (eval_rubric ≥ 0.6) + scores 기록."""
    item: dict = {"stage": "filtered"}
    scores = {"relevance": 0.8, "clarity": 0.7, "safety": 1.0}
    result = transition(item, "evaluated", scores=scores, overall_score=0.83)
    assert result["stage"] == "evaluated"
    entry = result["promotion_history"][0]
    assert entry["scores"] == scores
    assert entry["overall"] == 0.83


def test_transition_evaluated_to_approved_auto() -> None:
    """3단계 → 4단계 hybrid (자동, overall ≥ 0.8)."""
    item: dict = {"stage": "evaluated"}
    result = transition(item, "approved", overall_score=0.85)
    assert result["stage"] == "approved"
    entry = result["promotion_history"][0]
    assert entry["method"] == "auto"
    assert entry["threshold"] == AUTO_APPROVE_THRESHOLD


def test_transition_evaluated_to_approved_manual_threshold() -> None:
    """3단계 → 4단계 hybrid (수동, 0.6 ≤ overall < 0.8)."""
    item: dict = {"stage": "evaluated"}
    result = transition(item, "approved", overall_score=0.7)
    assert result["stage"] == "approved"
    entry = result["promotion_history"][0]
    assert entry["method"] == "manual"
    assert entry["threshold"] == EVAL_PASS_THRESHOLD


def test_transition_evaluated_below_threshold_raises() -> None:
    """3단계 → 4단계 거부 (overall < 0.6)."""
    item: dict = {"stage": "evaluated"}
    with pytest.raises(ValueError, match="below threshold"):
        transition(item, "approved", overall_score=0.5)


def test_transition_approved_to_promoted() -> None:
    """4단계 → 5단계 자동."""
    item: dict = {"stage": "approved"}
    result = transition(item, "promoted")
    assert result["stage"] == "promoted"
    entry = result["promotion_history"][0]
    assert entry["from"] == "approved"
    assert entry["to"] == "promoted"


def test_transition_out_of_order_raises() -> None:
    """단계 건너뛰기 차단 (pending → evaluated)."""
    item: dict = {"stage": "pending"}
    with pytest.raises(ValueError, match="Invalid transition"):
        transition(item, "evaluated")


def test_transition_evaluated_to_approved_requires_score() -> None:
    """evaluated → approved 시 overall_score 필수 (method 미지정 시)."""
    item: dict = {"stage": "evaluated"}
    with pytest.raises(ValueError, match="overall_score required"):
        transition(item, "approved")


def test_promotion_history_appends_all_stages() -> None:
    """5단계 모두 transition 시 history 4 entry 누적."""
    item: dict = {"stage": "pending"}
    item = transition(item, "filtered", reason="quality_pass")
    item = transition(
        item,
        "evaluated",
        scores={"relevance": 0.7, "clarity": 0.7, "safety": 1.0},
        overall_score=0.8,
    )
    item = transition(item, "approved", overall_score=0.85)
    item = transition(item, "promoted")
    assert item["stage"] == "promoted"
    assert len(item["promotion_history"]) == 4
    # 순서 검증
    stages_seen = [(e["from"], e["to"]) for e in item["promotion_history"]]
    assert stages_seen == [
        ("pending", "filtered"),
        ("filtered", "evaluated"),
        ("evaluated", "approved"),
        ("approved", "promoted"),
    ]


def test_promotion_history_entry_structure() -> None:
    """promotion_history entry 표준 schema 검증."""
    entry = promotion_history_entry(
        "pending", "filtered", reason="quality_pass"
    )
    assert entry["from"] == "pending"
    assert entry["to"] == "filtered"
    assert "at" in entry
    assert entry["reason"] == "quality_pass"
    # ISO8601 형식 (느슨한 검증)
    assert "T" in entry["at"]
