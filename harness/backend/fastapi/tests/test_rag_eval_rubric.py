"""Phase 7 Slice 2 — eval_rubric tests (간이 3 dim).

References:
  - backend/fastapi/rag/eval_rubric.py
  - docs/decisions/phase_7_promotion_logic.md (ADR-026 §3)
"""
from __future__ import annotations

from backend.fastapi.rag.eval_rubric import evaluate, overall


def test_evaluate_returns_3_dim() -> None:
    """3 dim 모두 반환 (relevance + clarity + safety)."""
    scores = evaluate("영상기획 가이드입니다.")
    assert "relevance" in scores
    assert "clarity" in scores
    assert "safety" in scores
    # 각 값 0.0~1.0 범위 검증
    for v in (scores["relevance"], scores["clarity"], scores["safety"]):
        assert 0.0 <= v <= 1.0


def test_evaluate_relevance_high_for_domain_keywords() -> None:
    """영상기획 도메인 키워드 3+ 매칭 시 relevance 1.0."""
    scores = evaluate("영상 기획 콘텐츠 타겟 분석을 위한 가이드")
    assert scores["relevance"] >= 1.0


def test_evaluate_relevance_low_for_unrelated() -> None:
    """도메인 키워드 미매칭 시 relevance 0.0."""
    scores = evaluate("python programming general note")
    assert scores["relevance"] == 0.0


def test_evaluate_safety_blocks_pii() -> None:
    """PII 포함 시 safety 0.0."""
    scores = evaluate("email: user@example.com 으로 보내주세요")
    assert scores["safety"] == 0.0


def test_overall_average() -> None:
    """overall = 3 dim 단순 평균."""
    scores = {"relevance": 0.8, "clarity": 0.7, "safety": 1.0}
    result = overall(scores)
    assert abs(result - 0.8333) < 0.01
