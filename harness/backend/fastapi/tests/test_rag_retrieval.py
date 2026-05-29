"""Phase 7 Slice 3 — retrieval tests (pgvector mock, ADR-025 §3).

검증 항목:
  - 정상 호출 → top_k 결과
  - 빈 query → []
  - Supabase 미설정 → [] (graceful)
  - embedding 실패 → [] (graceful)
  - RPC 실패 → [] (graceful)
  - dedupe by content
"""
from __future__ import annotations

from typing import Any, Optional
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.fastapi.rag.retrieval import search


# ─── helpers ─────────────────────────────────────────────────────────


class _FakeEmbeddingClient:
    """AsyncOpenAI client mock — embeddings.create 흉내 (embed() 통과용)."""

    def __init__(
        self,
        vec: Optional[list[float]] = None,
        raise_exc: Optional[BaseException] = None,
    ) -> None:
        self.embeddings = MagicMock()
        outer_vec = vec
        outer_exc = raise_exc

        async def _create(**kwargs: Any) -> Any:
            if outer_exc is not None:
                raise outer_exc
            mock_resp = MagicMock()
            mock_data = MagicMock()
            mock_data.embedding = (
                outer_vec if outer_vec is not None else [0.1] * 1536
            )
            mock_resp.data = [mock_data]
            return mock_resp

        self.embeddings.create = AsyncMock(side_effect=_create)


class _FakeSupabaseClient:
    """Supabase client mock — rpc().execute() 흉내."""

    def __init__(
        self,
        rpc_results: Optional[list[dict[str, Any]]] = None,
        rpc_exc: Optional[BaseException] = None,
    ) -> None:
        self.rpc_results = rpc_results or []
        self.rpc_exc = rpc_exc
        self.last_rpc_name: Optional[str] = None
        self.last_rpc_params: Optional[dict[str, Any]] = None

    def rpc(self, name: str, params: dict[str, Any]) -> Any:
        self.last_rpc_name = name
        self.last_rpc_params = params
        outer = self

        class _Caller:
            def execute(self) -> Any:
                if outer.rpc_exc is not None:
                    raise outer.rpc_exc
                mock_resp = MagicMock()
                mock_resp.data = outer.rpc_results
                return mock_resp

        return _Caller()


# ─── 기본 동작 ────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_search_returns_top_k_results() -> None:
    """정상 RPC 응답 → top_k 결과 반환."""
    emb_client = _FakeEmbeddingClient()
    sb_client = _FakeSupabaseClient(
        rpc_results=[
            {"id": "1", "content": "영상기획 가이드", "similarity": 0.9},
            {"id": "2", "content": "타겟 분석", "similarity": 0.85},
            {"id": "3", "content": "후크 가이드", "similarity": 0.75},
        ]
    )
    results = await search(
        "영상기획",
        top_k=3,
        threshold=0.7,
        embedding_client=emb_client,
        supabase_client=sb_client,
    )
    assert len(results) == 3
    assert sb_client.last_rpc_name == "match_approved_knowledge"
    assert sb_client.last_rpc_params is not None
    assert sb_client.last_rpc_params["match_count"] == 3
    assert sb_client.last_rpc_params["match_threshold"] == 0.7


@pytest.mark.asyncio
async def test_search_empty_query_returns_empty() -> None:
    """빈 / 공백만 query → [] (embed 호출 X)."""
    assert await search("") == []
    assert await search("   ") == []


# ─── Graceful 실패 ───────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_search_supabase_unavailable_graceful() -> None:
    """Supabase None → 빈 list + warning (env 미설정 fallback)."""
    emb_client = _FakeEmbeddingClient()
    # supabase_client 인자 미주입 → get_supabase() 호출 → env 없으면 None
    results = await search(
        "영상기획",
        embedding_client=emb_client,
        # supabase_client 미주입 — runtime은 get_supabase() 호출
    )
    # 테스트 환경에서 Supabase env 미설정 → None → 빈 list
    assert results == []


@pytest.mark.asyncio
async def test_search_embedding_failure_graceful() -> None:
    """embedding 실패 → 빈 list (RPC 호출 X)."""
    fail_client = _FakeEmbeddingClient(
        raise_exc=RuntimeError("openai outage")
    )
    sb_client = _FakeSupabaseClient(
        rpc_results=[{"id": "1", "content": "x", "similarity": 0.9}]
    )
    results = await search(
        "영상기획",
        embedding_client=fail_client,
        supabase_client=sb_client,
    )
    assert results == []
    # embedding 실패 시 RPC 호출이 발생하지 않아야 함
    assert sb_client.last_rpc_name is None


@pytest.mark.asyncio
async def test_search_rpc_failure_graceful() -> None:
    """Supabase RPC 예외 → 빈 list (graceful)."""
    emb_client = _FakeEmbeddingClient()
    sb_client = _FakeSupabaseClient(rpc_exc=RuntimeError("rpc network"))
    results = await search(
        "영상기획",
        embedding_client=emb_client,
        supabase_client=sb_client,
    )
    assert results == []


# ─── dedupe ──────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_search_dedupe_by_content() -> None:
    """동일 content 중복 제거 (ADR-025 §3 dedupe)."""
    emb_client = _FakeEmbeddingClient()
    sb_client = _FakeSupabaseClient(
        rpc_results=[
            {"id": "1", "content": "동일 텍스트", "similarity": 0.9},
            {"id": "2", "content": "동일 텍스트", "similarity": 0.85},
            {"id": "3", "content": "다른 텍스트", "similarity": 0.75},
        ]
    )
    results = await search(
        "query",
        top_k=10,
        embedding_client=emb_client,
        supabase_client=sb_client,
    )
    assert len(results) == 2  # dedupe 적용
    contents = [r["content"] for r in results]
    assert "동일 텍스트" in contents
    assert "다른 텍스트" in contents


# ─── brand_id 격리 ───────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_search_brand_id_passed_to_rpc() -> None:
    """brand_id 인자 → RPC params에 filter_brand_id 전달 (ADR-025 §3 isolation)."""
    emb_client = _FakeEmbeddingClient()
    sb_client = _FakeSupabaseClient(rpc_results=[])
    await search(
        "영상기획",
        brand_id="brand-xyz",
        auth_user_id="user-1",
        embedding_client=emb_client,
        supabase_client=sb_client,
    )
    assert sb_client.last_rpc_params is not None
    assert sb_client.last_rpc_params.get("filter_brand_id") == "brand-xyz"
    assert sb_client.last_rpc_params.get("filter_auth_user_id") == "user-1"
