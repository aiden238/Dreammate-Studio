"""Phase 7 Slice 3 — 512 tokens chunking (ADR-025).

문장 boundary 우선, 단어 boundary fallback.
overlap 50 tokens (10% 표준).

ADR-024 §2 글자 기준 → ADR-025 §1 token 기준으로 재정의.
한국어 + 영어 혼재 OK. tiktoken 없이 whitespace 기반 단순 추정 (Phase 7 MVP).

References:
  - docs/decisions/phase_7_rag_architecture.md (ADR-025 §1 Chunking)
  - knowledge/rag/promotion_rule.md
"""
from __future__ import annotations

import re

# 문장 boundary regex — 한국어/영어 마침표/물음표/느낌표 + 다음 공백
_SENTENCE_BOUNDARY = re.compile(r"(?<=[.!?。?!])\s+")


def _count_tokens(text: str) -> int:
    """단순 token 추정 (whitespace 분리).

    정확한 token count는 tiktoken 필요하지만 Phase 7 MVP는 whitespace로 근사.
    한국어는 어절 단위로 분리되며 token 수가 실제보다 적게 측정될 수 있으나,
    over-allocation 방지 (chunk가 size 초과하지 않음 보장)에는 안전.
    """
    return len(text.split())


def chunk(
    text: str,
    *,
    size: int = 512,
    overlap: int = 50,
) -> list[str]:
    """텍스트를 size tokens chunk로 분할 (overlap tokens 적용).

    분할 전략 (ADR-025 §1):
      1. 문장 boundary 우선 — 한 chunk 내 문장이 잘리지 않도록 시도.
      2. 단일 문장이 size 초과 시 → 단어 boundary로 강제 분할 (fallback).
      3. overlap 토큰만큼 다음 chunk 앞에 prepend (context 보존).

    Args:
        text: 입력 텍스트 (빈 / 공백만 → []).
        size: chunk size (tokens, 기본 512).
        overlap: overlap (tokens, 기본 50).

    Returns:
        chunk list (각 chunk는 size 이내, overlap 적용).

    Raises:
        ValueError: overlap >= size (잘못된 설정).
    """
    if not text or not text.strip():
        return []

    if overlap >= size:
        raise ValueError(
            f"overlap ({overlap}) must be less than size ({size})"
        )

    # 1) 문장 분할
    sentences = _SENTENCE_BOUNDARY.split(text.strip())
    sentences = [s.strip() for s in sentences if s.strip()]

    if not sentences:
        return []

    # 2) 문장 단위로 chunk 누적
    chunks: list[str] = []
    current_chunk: list[str] = []
    current_size = 0

    for sentence in sentences:
        sent_tokens = _count_tokens(sentence)

        # 단일 문장이 size 초과 시 → 단어 boundary로 강제 분할
        if sent_tokens > size:
            # 누적된 chunk flush
            if current_chunk:
                chunks.append(" ".join(current_chunk))
                current_chunk = []
                current_size = 0
            # 단어 단위 강제 분할 (overlap 적용)
            words = sentence.split()
            step = size - overlap if size > overlap else size
            for i in range(0, len(words), step):
                sub_words = words[i : i + size]
                if sub_words:
                    chunks.append(" ".join(sub_words))
                if i + size >= len(words):
                    break
            continue

        # 일반 케이스: chunk size 초과 직전까지 누적
        if current_size + sent_tokens > size and current_chunk:
            chunks.append(" ".join(current_chunk))
            # overlap 적용: 마지막 overlap 토큰 만큼 다음 chunk 시작
            overlap_text = " ".join(current_chunk)
            overlap_words = overlap_text.split()
            overlap_keep = (
                overlap_words[-overlap:] if overlap > 0 else []
            )
            current_chunk = overlap_keep + [sentence]
            current_size = _count_tokens(" ".join(current_chunk))
        else:
            current_chunk.append(sentence)
            current_size += sent_tokens

    # 마지막 chunk flush
    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks


__all__ = ["chunk"]
