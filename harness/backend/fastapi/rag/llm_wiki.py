"""Phase 7 Slice 4 — LLM Wiki (정적 지식, ADR-025).

LLM Wiki = static (영상기획 패턴, hook 유형, 타겟 페르소나)
RAG = dynamic (candidate_knowledge → approved_knowledge)
우선순위: RAG > LLM Wiki (동적이 최신)

본 모듈은 in-memory cache (정적). Phase 11+ 사용자 데이터 누적 후 RAG에 통합 검토.

References:
  - docs/decisions/phase_7_rag_architecture.md (ADR-025 §4 LLM Wiki vs RAG)
  - knowledge/llm_wiki/index.md
"""
from __future__ import annotations

import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)

# 정적 LLM Wiki 항목 (영상기획 도메인 — 영상 자동 편집/TTS/BGM는 MVP 제외)
_WIKI: dict[str, dict[str, Any]] = {
    "hook_patterns": {
        "topic": "hook_patterns",
        "content": "영상 시작 hook 패턴: 충격적 질문, 통계 인용, 반전 예고, 공감 시작.",
        "tags": ["hook", "intro", "engagement"],
    },
    "target_persona": {
        "topic": "target_persona",
        "content": "타겟 페르소나 4계층: 연령대, 관심사, 플랫폼 사용 시간, 구매력.",
        "tags": ["target", "persona", "audience"],
    },
    "tone_guide": {
        "topic": "tone_guide",
        "content": "영상 톤 가이드: 친근 / 전문 / 유머 / 다큐. Brand tone에 정합.",
        "tags": ["tone", "brand", "style"],
    },
    "structure_3act": {
        "topic": "structure_3act",
        "content": "3-Act 구조: 도입 (hook + 문제 제시) → 본론 (해결 / 인사이트) → 결말 (CTA).",
        "tags": ["structure", "narrative"],
    },
    "cta_types": {
        "topic": "cta_types",
        "content": "CTA 유형: 구독, 좋아요, 댓글, 외부 링크, 시리즈 다음편 예고. 1 CTA / 1 영상 권장.",
        "tags": ["cta", "engagement"],
    },
}


def lookup(topic: str) -> Optional[dict[str, Any]]:
    """정적 LLM Wiki lookup.

    Args:
        topic: wiki topic 키

    Returns:
        wiki entry dict or None (없음)
    """
    if not topic or not topic.strip():
        return None
    entry = _WIKI.get(topic.strip().lower())
    if entry is None:
        return None
    return dict(entry)  # 사본 (mutation 방지)


def search_by_tags(tags: list[str]) -> list[dict[str, Any]]:
    """tags 기반 search (간이).

    Args:
        tags: 검색할 tag list

    Returns:
        하나 이상의 tag가 매칭되는 wiki entry list (사본).
    """
    if not tags:
        return []
    tag_set = {t.lower() for t in tags}
    matched: list[dict[str, Any]] = []
    for entry in _WIKI.values():
        entry_tags = {t.lower() for t in entry.get("tags", [])}
        if tag_set & entry_tags:
            matched.append(dict(entry))
    return matched


def list_topics() -> list[str]:
    """전체 topic list 반환."""
    return list(_WIKI.keys())


__all__ = ["lookup", "search_by_tags", "list_topics"]
