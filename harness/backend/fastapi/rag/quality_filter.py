"""Phase 7 Slice 2 — quality_filter (PII + 인젝션 + 광고적 표현).

ADR-026 §pending → filtered 자동 조건.
ADR-025 §5 graceful (실패 시 pending 유지 + reason 메타 기록).

References:
  - knowledge/rag/quality_filter.md (5종 필터 상세)
  - docs/contracts/llm_security_contract.md (PII 패턴)
  - docs/contracts/output_schema.md §14 (광고 단어 정책)
  - knowledge/llm_wiki/style_guide/ad_phrase_blocklist.md (단일 출처)
"""
from __future__ import annotations

import re
from typing import NamedTuple

# PII patterns (Phase 1 baseline + Phase 5 보강)
# 참조: knowledge/rag/quality_filter.md §2.1
_PII_PATTERNS = [
    re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),        # email
    re.compile(r"\b\d{2,3}-\d{3,4}-\d{4}\b"),                                  # 한국 전화번호
    re.compile(r"\b\d{6}-[1-4]\d{6}\b"),                                       # 주민등록번호
    re.compile(r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b"),                # 카드번호
]

# 인젝션 patterns (Phase 1 baseline)
# 참조: docs/contracts/llm_security_contract.md (인젝션 차단 패턴)
_INJECTION_PATTERNS = [
    re.compile(
        r"ignore\s+(previous|above|prior)\s+(instructions?|prompts?)",
        re.IGNORECASE,
    ),
    re.compile(r"system\s*:\s*", re.IGNORECASE),
    re.compile(r"<\s*script\b", re.IGNORECASE),
    re.compile(r"```\s*system", re.IGNORECASE),
]

# 광고적 표현 차단 단어 (확정 결정 [9])
# 참조: output_schema §14 + knowledge/llm_wiki/style_guide/ad_phrase_blocklist.md
_AD_WORDS = [
    "최고의",
    "혁신적인",
    "혁명적인",
    "압도적인",
    "놀라운",
    "최고급",
    "프리미엄",
    "독보적인",
    "유일한",
    "획기적인",
]


class QualityFilterResult(NamedTuple):
    """quality_filter 결과.

    Attributes:
        passed: 전체 통과 여부
        reasons: 실패 사유 list (passed=False 시) — 'pii_detected', 'injection_detected',
                 'ad_word: <단어>' 형태
    """

    passed: bool
    reasons: list[str]


def quality_filter(content: str) -> QualityFilterResult:
    """PII + 인젝션 + 광고적 표현 검사 (3종).

    Phase 7 Slice 2 — pending → filtered 자동 전이 조건 (ADR-026 §1.1).

    Args:
        content: 검사 대상 텍스트 (candidate_knowledge.content)

    Returns:
        QualityFilterResult:
          - passed=True 시 reasons=[]
          - passed=False 시 reasons=실패 사유 list
    """
    reasons: list[str] = []

    # PII check (첫 매칭만 기록 — 노출 최소화)
    for pattern in _PII_PATTERNS:
        if pattern.search(content):
            reasons.append("pii_detected")
            break

    # Injection check
    for pattern in _INJECTION_PATTERNS:
        if pattern.search(content):
            reasons.append("injection_detected")
            break

    # 광고적 표현 check (첫 매칭 단어 기록 — 디버깅 보조)
    for word in _AD_WORDS:
        if word in content:
            reasons.append(f"ad_word: {word}")
            break

    return QualityFilterResult(passed=len(reasons) == 0, reasons=reasons)
