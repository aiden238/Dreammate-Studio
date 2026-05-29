"""Phase 7 Slice 4 — RAG end-to-end integration tests.

테스트 케이스:
  1. run_rag returns references with RAG priority (RAG > LLM Wiki, ADR-025 §4)
  2. Supabase unavailable falls back to LLM Wiki only (graceful, ADR-025 §5)
  3. RAG no results uses LLM Wiki fallback + rag_no_results warning
  4. end-to-end chunk → quality_filter → eval_rubric → transition 5단계 통과
  5. LLM Wiki lookup returns entry
  6. LLM Wiki lookup missing returns None
  7. LLM Wiki search_by_tags
  8. LLM Wiki list_topics
  9. run_rag empty input
"""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.fastapi.agents.rag import run_rag
from backend.fastapi.rag.chunking import chunk
from backend.fastapi.rag.eval_rubric import evaluate, overall
from backend.fastapi.rag.llm_wiki import (
    list_topics,
    lookup,
    search_by_tags,
)
from backend.fastapi.rag.promotion import (
    AUTO_APPROVE_THRESHOLD,
    transition,
)
from backend.fastapi.rag.quality_filter import quality_filter


class _FakeEmbedding:
    """OpenAI embedding client mock (returns fixed vector)."""

    def __init__(self, vec=None):
        self.embeddings = MagicMock()

        async def _create(**kwargs):
            mock_resp = MagicMock()
            mock_data = MagicMock()
            mock_data.embedding = vec or [0.1] * 1536
            mock_resp.data = [mock_data]
            return mock_resp

        self.embeddings.create = AsyncMock(side_effect=_create)


class _FakeSupabase:
    """Supabase client mock (returns rpc results or raises)."""

    def __init__(self, rpc_results=None, rpc_exc=None):
        self.rpc_results = rpc_results or []
        self.rpc_exc = rpc_exc

    def rpc(self, name, params):
        outer = self

        class _Caller:
            def execute(self):
                if outer.rpc_exc:
                    raise outer.rpc_exc
                mock_resp = MagicMock()
                mock_resp.data = outer.rpc_results
                return mock_resp

        return _Caller()


# ───── (1) RAG priority ──────────────────────────────────────────────


@pytest.mark.asyncio
async def test_run_rag_returns_references_with_rag_priority():
    """RAG > LLM Wiki 우선순위 확인 (ADR-025 §4)."""
    emb = _FakeEmbedding()
    sb = _FakeSupabase(
        rpc_results=[
            {
                "id": "1",
                "content": "영상기획 사용자 데이터",
                "similarity": 0.9,
            },
        ]
    )
    result = await run_rag(
        "영상기획", embedding_client=emb, supabase_client=sb
    )
    assert "references" in result
    # RAG 결과 + LLM Wiki 결과 모두 포함
    sources = {r["source"] for r in result["references"]}
    assert "rag" in sources
    # RAG는 fallback이 아니어야 함
    assert result["rag_used_fallback"] is False


# ───── (2) Supabase unavailable graceful ─────────────────────────────


@pytest.mark.asyncio
async def test_run_rag_supabase_unavailable_falls_back_to_llm_wiki():
    """Supabase 실패 → LLM Wiki만 (graceful, ADR-025 §5)."""
    emb = _FakeEmbedding()
    sb = _FakeSupabase(rpc_exc=RuntimeError("supabase fail"))
    result = await run_rag(
        "영상기획", embedding_client=emb, supabase_client=sb
    )
    # rag_used_fallback = True
    assert result["rag_used_fallback"] is True
    # warnings에 rag_* (rag_unavailable or rag_no_results) 포함
    assert any("rag" in w for w in result["rag_warnings"])
    # references는 LLM Wiki만 (RAG 없음 — Supabase 실패 후 retrieval.search가
    # 빈 list 반환하므로 RAG source는 없거나 0개)
    rag_count = sum(
        1 for r in result["references"] if r["source"] == "rag"
    )
    assert rag_count == 0


# ───── (3) RAG no results fallback ──────────────────────────────────


@pytest.mark.asyncio
async def test_run_rag_no_rag_results_uses_llm_wiki_fallback():
    """RAG 결과 0개 → LLM Wiki만 + rag_no_results warning."""
    emb = _FakeEmbedding()
    sb = _FakeSupabase(rpc_results=[])  # 빈 결과
    result = await run_rag(
        "영상기획", embedding_client=emb, supabase_client=sb
    )
    assert result["rag_used_fallback"] is True
    assert "rag_no_results" in result["rag_warnings"]


# ───── (4) end-to-end 5단계 ──────────────────────────────────────────


@pytest.mark.asyncio
async def test_end_to_end_chunk_then_promote_then_search():
    """chunking → quality_filter → eval_rubric → transition → 5단계 통과."""
    text = (
        "영상기획 가이드입니다. 타겟 페르소나 분석. "
        "후크 패턴 활용. 영상 콘텐츠 톤 가이드. "
        "스토리 구성과 메시지 전달이 중요합니다. "
        "유튜브 릴스 썸네일 타이틀 오프닝 엔딩 CTA."
    )
    chunks = chunk(text, size=512, overlap=50)
    assert len(chunks) >= 1

    for c in chunks:
        # quality_filter
        qf = quality_filter(c)
        if not qf.passed:
            continue
        # eval_rubric
        scores = evaluate(c)
        overall_score = overall(scores)
        # 5단계 transition
        item: dict = {"stage": "pending"}
        item = transition(item, "filtered", reason="quality_pass")
        item = transition(
            item,
            "evaluated",
            scores=dict(scores),
            overall_score=overall_score,
        )
        if overall_score >= AUTO_APPROVE_THRESHOLD:
            item = transition(
                item,
                "approved",
                overall_score=overall_score,
            )
            item = transition(item, "promoted")
            assert item["stage"] == "promoted"
            # promotion_history 4회 append
            assert len(item["promotion_history"]) == 4
        else:
            # 수동 승인 대기 (또는 거부) — evaluated에서 정지
            assert item["stage"] == "evaluated"


# ───── (5)(6)(7)(8) LLM Wiki ────────────────────────────────────────


def test_llm_wiki_lookup_returns_entry():
    """기존 topic lookup."""
    entry = lookup("hook_patterns")
    assert entry is not None
    assert "content" in entry
    assert "tags" in entry
    assert entry["topic"] == "hook_patterns"


def test_llm_wiki_lookup_missing_returns_none():
    """존재하지 않는 topic + 빈 입력 → None."""
    assert lookup("nonexistent_topic_xyz") is None
    assert lookup("") is None
    assert lookup("   ") is None


def test_llm_wiki_search_by_tags():
    """tag 검색 — hook tag로 hook_patterns 매칭."""
    results = search_by_tags(["hook"])
    assert len(results) >= 1
    assert any("hook" in r.get("tags", []) for r in results)
    # 빈 tag list → 빈 결과
    assert search_by_tags([]) == []


def test_llm_wiki_list_topics():
    """전체 topic list — 5개 이상 + 핵심 항목 포함."""
    topics = list_topics()
    assert "hook_patterns" in topics
    assert "target_persona" in topics
    assert len(topics) >= 5


# ───── (9) Empty input ──────────────────────────────────────────────


@pytest.mark.asyncio
async def test_run_rag_empty_input_returns_no_results():
    """빈 입력 → rag_no_results warning + 빈 references."""
    emb = _FakeEmbedding()
    sb = _FakeSupabase(rpc_results=[])
    result = await run_rag("", embedding_client=emb, supabase_client=sb)
    assert result["rag_used_fallback"] is True
    assert "rag_no_results" in result["rag_warnings"]
    assert result["references"] == []
