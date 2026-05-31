"""Phase 7 Slice 2 — eval_rubric tests (간이 3 dim).

Phase 10 Slice 3 추가 (additive): rag_eval_rubric.md 정식화 ↔ 구현 정합 (CC-009).
  - 기존 5 테스트(3 dim 회귀) 보존 (behavior-preserving — 구현 차원 변경 0).
  - rag_eval_rubric.md 존재 + §1.A 차원(relevance/clarity/safety) 명시 정합 검증.

References:
  - backend/fastapi/rag/eval_rubric.py
  - eval/rag_eval_rubric.md (Phase 10 정식화 — §1.A 구현 3 dim 정합)
  - docs/decisions/phase_7_promotion_logic.md (ADR-026 §3)
"""
from __future__ import annotations

from pathlib import Path

from backend.fastapi.rag.eval_rubric import evaluate, overall

# eval/rag_eval_rubric.md 위치 (harness 루트 기준).
#   본 파일: harness/backend/fastapi/tests/test_rag_eval_rubric.py → parents[3]=harness
_RUBRIC_DOC = Path(__file__).resolve().parents[3] / "eval" / "rag_eval_rubric.md"


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


# ── Phase 10 정식화 정합 (rag_eval_rubric.md) ────────────────────────

def test_rag_eval_rubric_doc_exists() -> None:
    """eval/rag_eval_rubric.md 정식 문서 존재 (Phase 10 NG1 이관 승격, CC-009)."""
    assert _RUBRIC_DOC.exists(), f"rag_eval_rubric.md 없음: {_RUBRIC_DOC}"


def test_rag_eval_rubric_doc_documents_impl_dimensions() -> None:
    """rubric.md §1.A 가 구현 3 dim(relevance/clarity/safety)을 명시 — 구현↔문서 정합."""
    text = _RUBRIC_DOC.read_text(encoding="utf-8")
    impl_dims = set(evaluate("영상 기획 콘텐츠").keys())
    assert impl_dims == {"relevance", "clarity", "safety"}
    for dim in impl_dims:
        assert dim in text, f"rubric.md 가 구현 차원 '{dim}' 미문서화"
    # 검색 활용 단계 정식 차원도 정의되어 있어야 함 (Phase 10 §1.B).
    for dim in ("retrieval_relevance", "groundedness", "hallucination_absence", "topk_accuracy"):
        assert dim in text, f"rubric.md 가 검색 차원 '{dim}' 미정의"
