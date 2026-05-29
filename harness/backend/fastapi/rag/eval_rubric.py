"""Phase 7 Slice 2 — 간이 eval rubric (3 dim).

ADR-026 §1.2 + §3 — filtered → evaluated 자동 조건.

3 dim:
  - relevance: 영상기획 도메인 키워드 매칭 비율
  - clarity: 문장 명료성 heuristic (평균 단어 수 기반)
  - safety: PII / 인젝션 재검사 (quality_filter 정합)

Phase 9+ deprecated 경로 (ADR-026 §3.4):
  - eval-run Skill 정식화 시 본 rubric은 deprecated
  - golden_set.md 기반 5~8 dim cross-encoder rubric으로 교체
"""
from __future__ import annotations

from typing import TypedDict


class EvalScores(TypedDict):
    """eval_rubric 3 dim 점수."""

    relevance: float
    clarity: float
    safety: float


# 영상기획 도메인 키워드 (relevance 측정용 — 간이)
# 참조: knowledge/llm_wiki/index.md 기반 영상기획 코어 어휘
_DOMAIN_KEYWORDS = [
    "영상",
    "기획",
    "콘텐츠",
    "타겟",
    "톤",
    "후크",
    "스토리",
    "구성",
    "메시지",
    "브랜드",
    "마케팅",
    "유튜브",
    "릴스",
    "썸네일",
    "타이틀",
    "오프닝",
    "엔딩",
    "CTA",
]


def _score_relevance(content: str) -> float:
    """영상기획 도메인 키워드 매칭 비율 (간이).

    3개 이상 매칭 시 1.0, 그 외 비례 감점.
    """
    if not content:
        return 0.0
    matched = sum(1 for kw in _DOMAIN_KEYWORDS if kw in content)
    return min(matched / 3.0, 1.0)


def _score_clarity(content: str) -> float:
    """문장 명료성 heuristic — 평균 단어 수 기반.

    평균 단어 수 5~20 = 명료 (1.0).
    < 5: 짧음 (비례 감점, 최소 0.3).
    > 20: 김 (역비례 감점, 최소 0.3).
    """
    if not content:
        return 0.0
    sentences = [
        s.strip()
        for s in content.replace("?", ".").replace("!", ".").split(".")
        if s.strip()
    ]
    if not sentences:
        return 0.0
    avg_len = sum(len(s.split()) for s in sentences) / len(sentences)
    if 5 <= avg_len <= 20:
        return 1.0
    if avg_len < 5:
        return max(0.3, avg_len / 5.0)
    # avg_len > 20
    return max(0.3, 20.0 / avg_len)


def _score_safety(content: str) -> float:
    """PII / 인젝션 재검사 (간이) — quality_filter 정합.

    1.0 (passed) or 0.0 (failed).
    """
    from backend.fastapi.rag.quality_filter import quality_filter

    result = quality_filter(content)
    return 1.0 if result.passed else 0.0


def evaluate(content: str) -> EvalScores:
    """3 dim 점수 산출 (ADR-026 §3.2 API).

    Returns:
        EvalScores: {relevance, clarity, safety} 각 0.0~1.0
    """
    return {
        "relevance": _score_relevance(content),
        "clarity": _score_clarity(content),
        "safety": _score_safety(content),
    }


def overall(scores: EvalScores) -> float:
    """종합 점수 (단순 평균).

    Phase 9+: 가중 합 (golden_set 기반)으로 교체 예정 (ADR-026 §3.4).
    """
    values = [scores["relevance"], scores["clarity"], scores["safety"]]
    return sum(values) / len(values)
