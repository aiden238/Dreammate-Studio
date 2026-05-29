"""Phase 7 Slice 3 — embedding tests (mock, ADR-025 §2).

검증 항목:
  - 정상 호출 → 1536 dim list
  - 빈 / 공백만 → None
  - 예외 → None (graceful)
  - empty data → None (graceful)
  - embed_many 혼합 결과
"""
from __future__ import annotations

from typing import Any, Optional
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.fastapi.rag.embedding import embed, embed_many


class _FakeEmbeddingClient:
    """AsyncOpenAI client mock — embeddings.create 흉내."""

    def __init__(
        self,
        vec: Optional[list[float]] = None,
        raise_exc: Optional[BaseException] = None,
        empty_data: bool = False,
    ) -> None:
        self.embeddings = MagicMock()
        outer_vec = vec
        outer_exc = raise_exc
        outer_empty = empty_data

        async def _create(**kwargs: Any) -> Any:
            if outer_exc is not None:
                raise outer_exc
            mock_resp = MagicMock()
            if outer_empty:
                mock_resp.data = []
                return mock_resp
            mock_data = MagicMock()
            mock_data.embedding = (
                outer_vec if outer_vec is not None else [0.1] * 1536
            )
            mock_resp.data = [mock_data]
            return mock_resp

        self.embeddings.create = AsyncMock(side_effect=_create)


# ─── 기본 동작 ────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_embed_returns_1536_dim_vector() -> None:
    """정상 응답 → 1536 dim list."""
    client = _FakeEmbeddingClient(vec=[0.5] * 1536)
    result = await embed("영상기획 가이드", client=client)
    assert isinstance(result, list)
    assert len(result) == 1536
    assert result[0] == 0.5


@pytest.mark.asyncio
async def test_embed_empty_text_returns_none() -> None:
    """빈 / 공백만 → None (API 호출 X)."""
    client = _FakeEmbeddingClient()
    assert await embed("", client=client) is None
    assert await embed("   ", client=client) is None
    assert await embed("\n\t", client=client) is None


# ─── Graceful 실패 ───────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_embed_failure_returns_none_graceful() -> None:
    """API 예외 → None + warning (graceful)."""
    client = _FakeEmbeddingClient(raise_exc=RuntimeError("network outage"))
    result = await embed("영상기획 가이드", client=client)
    assert result is None


@pytest.mark.asyncio
async def test_embed_empty_data_returns_none() -> None:
    """응답 data 비어 있음 → None."""
    client = _FakeEmbeddingClient(empty_data=True)
    result = await embed("영상기획", client=client)
    assert result is None


# ─── embed_many ──────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_embed_many_handles_mixed_results() -> None:
    """다중 입력 중 빈 텍스트는 None, 나머지는 vector."""
    client = _FakeEmbeddingClient(vec=[0.3] * 1536)
    results = await embed_many(["text1", "", "text3"], client=client)
    assert len(results) == 3
    assert results[0] is not None
    assert len(results[0]) == 1536  # type: ignore[arg-type]
    assert results[1] is None
    assert results[2] is not None
    assert len(results[2]) == 1536  # type: ignore[arg-type]
