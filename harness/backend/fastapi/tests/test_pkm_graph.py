"""Phase 19 Slice S1 — GET /api/v1/me/pkm-graph 집계 엔드포인트 테스트 (mock, CI-safe).

검증 축:
  1. authed + 주입 in-memory repos(개인 pkm 2 + brand 1 + 브랜드 pkm 2) →
     user 노드 1 + 개인 pkm 2 + brand 1 + 브랜드 pkm 2 노드 + 올바른 엣지 + summary.
     locked 플래그 패스스루.
  2. 익명(request.state.user 없음) → 빈 {nodes, edges} 200 (graceful).
  3. RLS 격리 — 두 user 시드, A 로 요청 → A 노드만 (B 0).
  4. graceful — repo 가 raise → 엔드포인트 여전히 200, 그 부분만 빔.

★ mock — 실 Supabase 0 (in-memory repos). DI seam(pkm_repo/brand_repo/brand_memory_repo)으로
   엔드포인트 함수를 직접 호출하거나(주입), TestClient + dev_auth_mock 쿠키로 HTTP 경로를 탄다
   (test_identity_plumbing / test_branding_endpoint 패턴).
"""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any, Optional

import pytest
from fastapi.testclient import TestClient

from backend.fastapi import config as _config_module
from backend.fastapi.db import BrandMemoryRepo, BrandRepo, PkmRepo
from backend.fastapi.db import client as _db_client_module
from backend.fastapi.main import app
from backend.fastapi.routers import me as me_router
from backend.fastapi.routers.me import _aggregate_pkm_graph, get_pkm_graph


# ─── helpers ──────────────────────────────────────────────────────────


def _request_with_user(auth_user_id: Optional[str]) -> Any:
    """get_pkm_graph 가 읽는 request.state.user 만 흉내내는 최소 Request 대역.

    auth_middleware 가 주입하는 형식({"user_id": ...})을 그대로 모사. None 이면 익명.
    """
    user = {"user_id": auth_user_id} if auth_user_id else None
    return SimpleNamespace(state=SimpleNamespace(user=user))


async def _seed_repos(
    auth_user_id: str,
) -> tuple[PkmRepo, BrandRepo, BrandMemoryRepo, str]:
    """개인 pkm 2(1개 locked) + brand 1 + 브랜드 pkm 2 를 in-memory repo 에 시드."""
    pkm_repo = PkmRepo()
    brand_repo = BrandRepo()
    brand_memory_repo = BrandMemoryRepo()

    await pkm_repo.add_entry(
        auth_user_id, "preferred_tone", "담백한 톤", is_user_locked=True,
    )
    await pkm_repo.add_entry(auth_user_id, "avoid_phrase", "과장 표현")

    brand_id = await brand_repo.get_or_create_default(auth_user_id, name="내 브랜드")
    assert brand_id

    await brand_memory_repo.add_entry(brand_id, "preferred_tone", "브랜드 톤")
    await brand_memory_repo.add_entry(brand_id, "preferred_phrase", "선호 표현")

    return pkm_repo, brand_repo, brand_memory_repo, brand_id


# ─── 1. authed + 주입 repos → 전체 집계 + 엣지 + summary + locked ───────


@pytest.mark.asyncio
async def test_pkm_graph_aggregates_nodes_edges_and_summary() -> None:
    """개인 pkm 2 + brand 1 + 브랜드 pkm 2 → 노드/엣지/summary + locked 패스스루."""
    uid = "user-A"
    pkm_repo, brand_repo, brand_memory_repo, brand_id = await _seed_repos(uid)

    resp = await _aggregate_pkm_graph(
        uid,
        pkm_repo=pkm_repo,
        brand_repo=brand_repo,
        brand_memory_repo=brand_memory_repo,
    )

    # 노드 카운트 — user 1 + 개인 pkm 2 + brand 1 + 브랜드 pkm 2 = 6.
    assert len(resp.nodes) == 6
    by_type: dict[str, list[Any]] = {}
    for n in resp.nodes:
        by_type.setdefault(n.type, []).append(n)
    assert len(by_type["user"]) == 1
    assert len(by_type["brand"]) == 1
    pkm_nodes = by_type["pkm"]
    assert len(pkm_nodes) == 4  # 개인 2 + 브랜드 2

    # user 루트 노드.
    user_node = by_type["user"][0]
    assert user_node.id == f"user:{uid}"
    assert user_node.label == "나"

    # 개인/브랜드 scope 분리.
    personal_nodes = [n for n in pkm_nodes if n.scope == "personal"]
    brand_pkm_nodes = [n for n in pkm_nodes if n.scope == "brand"]
    assert len(personal_nodes) == 2
    assert len(brand_pkm_nodes) == 2
    assert all(n.id.startswith("pkm:") for n in personal_nodes)
    assert all(n.id.startswith("bm:") for n in brand_pkm_nodes)

    # ★ locked 패스스루 — 개인 pkm 중 정확히 1개가 locked=True.
    assert sum(1 for n in personal_nodes if n.locked) == 1

    # 엣지 — owns 1 + has_personal 2 + has_brand_pkm 2.
    kinds = [e.kind for e in resp.edges]
    assert kinds.count("owns") == 1
    assert kinds.count("has_personal") == 2
    assert kinds.count("has_brand_pkm") == 2

    brand_node = by_type["brand"][0]
    assert brand_node.id == f"brand:{brand_id}"
    assert brand_node.label == "내 브랜드"
    # owns 엣지는 user → brand.
    owns = [e for e in resp.edges if e.kind == "owns"][0]
    assert owns.source == f"user:{uid}"
    assert owns.target == brand_node.id
    # has_brand_pkm 엣지는 brand → bm.
    for e in resp.edges:
        if e.kind == "has_brand_pkm":
            assert e.source == brand_node.id
            assert e.target.startswith("bm:")
        if e.kind == "has_personal":
            assert e.source == f"user:{uid}"
            assert e.target.startswith("pkm:")

    # summary 카운트.
    assert resp.summary.personal == 2
    assert resp.summary.brand == 2
    assert resp.summary.brands == 1


# ─── 2. 익명 → 빈 그래프 200 (HTTP 경로) ──────────────────────────────


def test_pkm_graph_anonymous_returns_empty() -> None:
    """토큰 없음(익명) → 빈 {nodes, edges} + summary 0, 200 (graceful)."""
    client = TestClient(app)
    r = client.get("/api/v1/me/pkm-graph")  # 쿠키 없음
    assert r.status_code == 200
    data = r.json()
    assert data["nodes"] == []
    assert data["edges"] == []
    assert data["summary"] == {
        "personal": 0, "brand": 0, "brands": 0,
        "domains": 0, "series": 0, "sources": 0,  # Phase 21 additive (graceful 0)
    }


@pytest.mark.asyncio
async def test_pkm_graph_anonymous_direct_empty() -> None:
    """직접 호출 — request.state.user None → 빈 그래프 (repo 미접근)."""
    resp = await get_pkm_graph(_request_with_user(None))
    assert resp.nodes == []
    assert resp.edges == []
    assert resp.summary.personal == 0


# ─── 3. RLS 격리 — A 요청은 A 데이터만 (B 0) ──────────────────────────


@pytest.mark.asyncio
async def test_pkm_graph_rls_isolation_no_cross_user() -> None:
    """두 user 시드, A 로 요청 → A 노드만 (B 의 어떤 데이터도 노출 0)."""
    # 같은 repo 인스턴스(공유 store)에 A/B 모두 시드 — 격리는 list 메서드가 보장.
    pkm_repo = PkmRepo()
    brand_repo = BrandRepo()
    brand_memory_repo = BrandMemoryRepo()

    await pkm_repo.add_entry("user-A", "preferred_tone", "A 의 톤")
    await pkm_repo.add_entry("user-B", "preferred_tone", "B 의 톤(노출 금지)")

    a_brand = await brand_repo.get_or_create_default("user-A", name="A 브랜드")
    b_brand = await brand_repo.get_or_create_default("user-B", name="B 브랜드")
    await brand_memory_repo.add_entry(a_brand, "preferred_tone", "A 브랜드 PKM")
    await brand_memory_repo.add_entry(b_brand, "preferred_tone", "B 브랜드 PKM(노출 금지)")

    resp = await _aggregate_pkm_graph(
        "user-A",
        pkm_repo=pkm_repo,
        brand_repo=brand_repo,
        brand_memory_repo=brand_memory_repo,
    )

    labels = [n.label for n in resp.nodes]
    # A 데이터만.
    assert "A 의 톤" in labels
    assert "A 브랜드" in labels
    assert "A 브랜드 PKM" in labels
    # ★ B 데이터는 어떤 노드/엣지에도 없음.
    blob = " ".join(labels)
    assert "노출 금지" not in blob
    assert "B 브랜드" not in labels
    # 노드: user 1 + 개인 1 + brand 1 + 브랜드 pkm 1 = 4.
    assert len(resp.nodes) == 4
    assert resp.summary.personal == 1
    assert resp.summary.brands == 1
    assert resp.summary.brand == 1
    # B brand 노드 id 가 엣지에 등장하지 않음.
    assert all(b_brand not in e.target and b_brand not in e.source for e in resp.edges)


# ─── 4. graceful — repo raise → 200, 그 부분만 빔 ─────────────────────


@pytest.mark.asyncio
async def test_pkm_graph_graceful_on_personal_repo_error() -> None:
    """개인 PKM repo 가 raise → 500 아님, 개인 부분만 빔 (brand 는 정상 집계)."""
    uid = "user-A"
    _, brand_repo, brand_memory_repo, _ = await _seed_repos(uid)

    class _BoomPkmRepo:
        async def list_for_user(self, *a: Any, **k: Any) -> list[dict[str, Any]]:
            raise RuntimeError("pkm down")

    resp = await _aggregate_pkm_graph(
        uid,
        pkm_repo=_BoomPkmRepo(),  # type: ignore[arg-type]
        brand_repo=brand_repo,
        brand_memory_repo=brand_memory_repo,
    )

    # 개인 PKM 0 (실패), 그러나 user + brand + 브랜드 pkm 은 정상.
    assert resp.summary.personal == 0
    assert resp.summary.brands == 1
    assert resp.summary.brand == 2
    assert not any(n.scope == "personal" for n in resp.nodes)
    assert any(n.type == "brand" for n in resp.nodes)


@pytest.mark.asyncio
async def test_pkm_graph_graceful_on_brand_repo_error() -> None:
    """brand repo 가 raise → 500 아님, 개인 PKM 은 정상, brand/브랜드 PKM 전체 빔."""
    uid = "user-A"
    pkm_repo, _, brand_memory_repo, _ = await _seed_repos(uid)

    class _BoomBrandRepo:
        async def list_for_user(self, *a: Any, **k: Any) -> list[dict[str, Any]]:
            raise RuntimeError("brand down")

    resp = await _aggregate_pkm_graph(
        uid,
        pkm_repo=pkm_repo,
        brand_repo=_BoomBrandRepo(),  # type: ignore[arg-type]
        brand_memory_repo=brand_memory_repo,
    )

    assert resp.summary.personal == 2  # 개인은 정상
    assert resp.summary.brands == 0  # brand 집계 실패 → 0
    assert resp.summary.brand == 0  # 브랜드 PKM 도 0 (brand anchor 없음)
    assert not any(n.type == "brand" for n in resp.nodes)


# ─── 5. HTTP 경로 (dev_auth_mock 쿠키) — 모듈 repo 주입 ───────────────


def test_pkm_graph_http_authed_path(monkeypatch: pytest.MonkeyPatch) -> None:
    """dev_auth_mock + mock-token 쿠키 → mock-user-1 로 집계 (HTTP end-to-end wired)."""
    # dev_auth_mock 활성 + supabase None 강제 (middleware mock-token 분기).
    _config_module.get_settings.cache_clear()
    settings = _config_module.get_settings()
    monkeypatch.setattr(settings, "dev_auth_mock", True, raising=False)
    monkeypatch.setattr(_db_client_module, "get_supabase", lambda: None)
    monkeypatch.setattr("backend.fastapi.routers.auth.get_supabase", lambda: None)

    import asyncio

    # mock-user-1 에 시드된 in-memory repos 를 모듈 싱글톤에 주입.
    pkm_repo, brand_repo, brand_memory_repo, _ = asyncio.run(_seed_repos("mock-user-1"))
    monkeypatch.setattr(me_router, "_pkm_repo", pkm_repo)
    monkeypatch.setattr(me_router, "_brand_repo", brand_repo)
    monkeypatch.setattr(me_router, "_brand_memory_repo", brand_memory_repo)

    client = TestClient(app)
    client.cookies.set("sb_access_token", "mock-token")
    r = client.get("/api/v1/me/pkm-graph")
    assert r.status_code == 200
    data = r.json()
    assert data["summary"] == {
        "personal": 2, "brand": 2, "brands": 1,
        "domains": 0, "series": 0, "sources": 0,  # Phase 21 additive (graceful 0 — no depth seeded)
    }
    assert len(data["nodes"]) == 6
    assert any(n["type"] == "user" and n["id"] == "user:mock-user-1" for n in data["nodes"])


def test_pkm_graph_in_openapi() -> None:
    """Phase 19 endpoint 가 OpenAPI 문서에 노출."""
    client = TestClient(app)
    r = client.get("/openapi.json")
    assert r.status_code == 200
    paths = r.json().get("paths", {})
    assert "/api/v1/me/pkm-graph" in paths
