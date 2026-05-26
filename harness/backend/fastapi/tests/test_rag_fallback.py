"""Phase 1 Slice 4 — RAG Lite + graceful fallback 검증.

검증 항목:
  1. env 미설정 (db_url="")            → fallback(env_missing) + references==[]
  2. pgvector 연결 오류 (connect raise) → fallback(pgvector_unreachable)
  3. fallback() 직접 호출               → references==[], used_fallback=True
  4. router 통합 (rag fallback 시)      → HTTP 200 + body.rag_references==[]
  5. router 통합 (rag OK 시)            → body.rag_references 길이==2

→ 핵심 acceptance: 사용자 요청은 RAG 실패와 무관하게 절대 차단되지 않는다.
"""

from __future__ import annotations

from typing import Any

import pytest
from fastapi.testclient import TestClient

from backend.fastapi.main import app
from backend.fastapi.rag.fallback import fallback
from backend.fastapi.rag.retriever import run_rag_retrieval
from backend.fastapi.rag.types import RAGReference, RetrievalResult


client = TestClient(app)


# ─── 1. env 미설정 → fallback(env_missing) ──────────────────────────────

def test_retrieval_env_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    """database_url과 pgvector_database_url 모두 빈 문자열이면 즉시 fallback."""
    # _env_setup이 OPENAI_API_KEY를 설정해두지만 PGVECTOR_* 는 기본값(빈 문자열).
    # get_settings는 fixture에서 cache_clear 되므로 환경변수 미설정 == default 적용.
    monkeypatch.delenv("PGVECTOR_DATABASE_URL", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    from backend.fastapi.config import get_settings

    get_settings.cache_clear()

    result = run_rag_retrieval("유튜브 첫 영상 기획")

    assert isinstance(result, RetrievalResult)
    assert result.used_fallback is True
    assert result.fallback_reason == "env_missing"
    assert result.references == []


# ─── 2. pgvector 연결 오류 → fallback(pgvector_unreachable) ──────────────

def test_retrieval_connection_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """psycopg.connect 가 raise → fallback(pgvector_unreachable)."""
    # DB URL은 있다고 가정 (그래야 connect 시도 분기로 진입)
    monkeypatch.setenv("PGVECTOR_DATABASE_URL", "postgresql://x:y@nohost:5432/db")
    from backend.fastapi.config import get_settings

    get_settings.cache_clear()

    # psycopg.connect 가 즉시 raise 하도록 monkeypatch.
    import backend.fastapi.rag.retriever as retriever_mod

    class _FakePsycopg:
        @staticmethod
        def connect(*args: Any, **kwargs: Any) -> Any:
            raise ConnectionError("simulated pgvector down")

    monkeypatch.setattr(retriever_mod, "psycopg", _FakePsycopg)
    # embedding을 우회: query_error로 빠지지 않게 fake embedding 반환.
    monkeypatch.setattr(
        retriever_mod, "_embed_query", lambda q: [0.0] * 1536
    )

    result = run_rag_retrieval("유튜브 첫 영상 기획")

    assert result.used_fallback is True
    assert result.fallback_reason == "pgvector_unreachable"
    assert result.references == []


# ─── 3. fallback() 직접 호출 ───────────────────────────────────────────

def test_fallback_returns_empty_references() -> None:
    """fallback() 헬퍼 단독 호출 시 references=[] + used_fallback=True."""
    result = fallback("env_missing")

    assert result.references == []
    assert result.used_fallback is True
    assert result.fallback_reason == "env_missing"


def test_fallback_default_reason() -> None:
    """fallback() 인자 생략 시 기본 사유 pgvector_unreachable."""
    result = fallback()

    assert result.used_fallback is True
    assert result.fallback_reason == "pgvector_unreachable"


# ─── 4. router + rag fallback → HTTP 200 + 빈 references ─────────────────

def test_router_with_rag_fallback_returns_200(
    mock_intent_ok: Any,
    mock_rag_fallback: Any,
    mock_planning_ok: Any,
    mock_critic_ok: Any,
) -> None:
    """RAG fallback 시에도 사용자 요청은 200으로 정상 처리."""
    response = client.post(
        "/api/v1/generate",
        json={"input": "유튜브 첫 영상 기획해줘"},
    )
    assert response.status_code == 200

    data = response.json()
    # body.rag_references 는 빈 배열
    assert data["body"]["rag_references"] == []
    # validation.checks 에 rag_retrieval status="warn"
    checks = data["validation"]["checks"]
    rag_check = next((c for c in checks if c["name"] == "rag_retrieval"), None)
    assert rag_check is not None
    assert rag_check["status"] == "warn"
    assert "fallback=True" in (rag_check["detail"] or "")
    # plan.rag_used 도 빈 배열
    assert data["body"]["plans"][0]["rag_used"] == []


# ─── 5. router + rag OK → references 채워짐 ────────────────────────────

def test_router_with_rag_ok_returns_references(
    mock_intent_ok: Any,
    mock_rag_ok: Any,
    mock_planning_ok: Any,
    mock_critic_ok: Any,
) -> None:
    """RAG가 2개 reference 반환 → body.rag_references 길이==2 + plan.rag_used 채움."""
    response = client.post(
        "/api/v1/generate",
        json={"input": "쇼츠 콘텐츠 기획"},
    )
    assert response.status_code == 200

    data = response.json()
    refs = data["body"]["rag_references"]
    assert len(refs) == 2

    # 각 reference 필드 검증 (RAGReference schema 정합)
    for r in refs:
        assert r["source_id"]
        assert r["title"]
        assert r["snippet"]
        assert 0.0 <= r["similarity"] <= 1.0

    # validation.checks rag_retrieval status="ok"
    checks = data["validation"]["checks"]
    rag_check = next((c for c in checks if c["name"] == "rag_retrieval"), None)
    assert rag_check is not None
    assert rag_check["status"] == "ok"
    assert "references=2" in (rag_check["detail"] or "")
    assert "fallback=False" in (rag_check["detail"] or "")

    # plan.rag_used 도 2개 (router가 references 요약하여 주입)
    plan_rag_used = data["body"]["plans"][0]["rag_used"]
    assert len(plan_rag_used) == 2
    assert plan_rag_used[0]["source_id"] == "seed-001"
    assert plan_rag_used[1]["source_id"] == "seed-002"


# ─── 6. RetrievalResult Pydantic 검증 (보조) ────────────────────────────

def test_retrieval_result_validates_similarity_range() -> None:
    """RAGReference.similarity는 0.0~1.0 범위만 허용."""
    with pytest.raises(Exception):
        RAGReference(
            source_id="x",
            title="t",
            snippet="s",
            similarity=1.5,  # out of range
        )


def test_retrieval_result_snippet_max_length() -> None:
    """RAGReference.snippet은 300자 제한."""
    with pytest.raises(Exception):
        RAGReference(
            source_id="x",
            title="t",
            snippet="가" * 301,
            similarity=0.8,
        )
