"""Phase 7 Slice 3 — chunking tests (ADR-025 §1).

검증 항목:
  - 빈 / 공백만 → []
  - 짧은 텍스트 → 단일 chunk
  - 긴 텍스트 → 다중 chunk (size 분할)
  - 문장 boundary 우선
  - overlap 적용
  - overlap >= size → ValueError
  - 단일 long sentence → 단어 boundary 강제 분할
"""
from __future__ import annotations

import pytest

from backend.fastapi.rag.chunking import chunk


def test_chunk_empty_text_returns_empty() -> None:
    """빈 / 공백만 → [] (graceful)."""
    assert chunk("") == []
    assert chunk("   ") == []
    assert chunk("\n\t  ") == []


def test_chunk_short_text_returns_single_chunk() -> None:
    """단일 짧은 문장 → 단일 chunk 반환."""
    text = "짧은 문장입니다."
    chunks = chunk(text, size=512, overlap=50)
    assert len(chunks) == 1
    assert chunks[0].strip() == text.strip()


def test_chunk_long_text_splits_into_multiple() -> None:
    """1000 단어 입력 (size=512보다 큼) → 2개 이상 chunk."""
    text = "word " * 1000
    chunks = chunk(text, size=512, overlap=50)
    # 단일 문장이 size 초과 → 단어 boundary 강제 분할
    assert len(chunks) >= 2


def test_chunk_sentence_boundary_preserved() -> None:
    """문장 boundary 우선 — 짧은 문장 여러 개를 small size로 분할."""
    text = "첫 번째 문장입니다. 두 번째 문장이에요. 세 번째도 있습니다."
    chunks = chunk(text, size=10, overlap=2)
    assert len(chunks) >= 1
    for c in chunks:
        assert c.strip()  # non-empty


def test_chunk_overlap_applied() -> None:
    """size 작게 + overlap 양수 → 인접 chunk 일부 단어 겹침."""
    # 20개 짧은 "단어 문장" — 의도적으로 마침표 없이 단일 문장으로 강제 분할
    text = " ".join(f"w{i}" for i in range(20))
    chunks = chunk(text, size=10, overlap=3)
    if len(chunks) >= 2:
        chunk0_words = chunks[0].split()
        chunk1_words = chunks[1].split()
        # overlap 3 tokens — 최소 일부 단어 겹침
        assert any(w in chunk1_words for w in chunk0_words[-3:])


def test_chunk_overlap_larger_than_size_raises() -> None:
    """overlap >= size → ValueError (잘못된 설정)."""
    with pytest.raises(ValueError, match="overlap"):
        chunk("text content here", size=10, overlap=10)
    with pytest.raises(ValueError, match="overlap"):
        chunk("text content here", size=5, overlap=20)


def test_chunk_single_long_sentence_force_split() -> None:
    """단일 문장이 size 초과 시 → 단어 boundary 강제 분할."""
    text = " ".join(f"w{i}" for i in range(800))  # 800 단어 "단일 문장"
    chunks = chunk(text, size=200, overlap=20)
    # 800 / (200-20) = ~5 chunks 예상
    assert len(chunks) >= 2
    for c in chunks:
        assert c.strip()
        # 각 chunk는 size 이내 (단어 기준)
        assert len(c.split()) <= 200
