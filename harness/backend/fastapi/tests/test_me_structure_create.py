"""Phase 22 Slice S1 — 구조 생성(Domain/Series CREATE) 엔드포인트 테스트 (mock, CI-safe).

대상:
  - POST /api/v1/me/domains  {brand_id, name}  → 본인 brand 아래 domain 생성.
  - POST /api/v1/me/series   {domain_id, name} → 본인 domain 아래 series 생성.

검증 축:
  1. 소유 brand 아래 domain 생성 → ok + domain.id, DomainRepo.list_for_brand 에 즉시 반영.
  2. 소유 domain 아래 series 생성 → ok + series.id, SeriesRepo.list_for_domain 에 즉시 반영.
  3. ★ RLS — 다른 user 의 brand 아래 domain 생성 → 404; 미소유 domain 아래 series → 404.
  4. 익명(토큰 없음) HTTP → 401.
  5. 빈 name → 422 (Pydantic min_length).
  6. graceful — repo.create 가 None / raise → unhandled 500 없음 (503 controlled).
  7. end-to-end — brand→domain→series 생성 후 /me/pkm-graph 가 깊이 노드 자동 반영(Phase 21).

★ mock — 실 Supabase 0 (in-memory repos). DI seam(_create_domain/_create_series)으로 직접
   호출하거나, TestClient + dev_auth_mock 쿠키로 HTTP 경로(401/422/200)를 탄다.
"""

from __future__ import annotations

from typing import Any

import pytest
from fastapi.testclient import TestClient

from backend.fastapi import config as _config_module
from backend.fastapi.db import (
    BrandMemoryRepo,
    BrandRepo,
    DomainRepo,
    PkmRepo,
    SeriesRepo,
)
from backend.fastapi.db import client as _db_client_module
from backend.fastapi.main import app
from backend.fastapi.routers import me as me_router
from backend.fastapi.routers.me import (
    _aggregate_pkm_graph,
    _create_domain,
    _create_series,
)
from backend.fastapi.schemas.graph import (
    MeDomainCreateRequest,
    MeSeriesCreateRequest,
)


# ─── helpers ──────────────────────────────────────────────────────────


async def _seed_brand(brand_repo: BrandRepo, auth_user_id: str) -> str:
    """소유 brand 1개 시드 → brand_id 반환."""
    brand_id = await brand_repo.get_or_create_default(auth_user_id, name="내 브랜드")
    assert brand_id
    return brand_id


async def _seed_domain(
    brand_repo: BrandRepo, domain_repo: DomainRepo, auth_user_id: str,
) -> tuple[str, str]:
    """소유 brand 1 + 그 아래 domain 1 시드 → (brand_id, domain_id) 반환."""
    brand_id = await _seed_brand(brand_repo, auth_user_id)
    row = await domain_repo.create(brand_id, "내 도메인")
    assert row and row.get("id")
    return brand_id, str(row["id"])


# ─── 1. 소유 brand 아래 domain 생성 → ok + list 반영 ──────────────────


@pytest.mark.asyncio
async def test_create_domain_under_owned_brand() -> None:
    """소유 brand 아래 domain 생성 → ok, id 있음, list_for_brand 즉시 포함."""
    uid = "user-A"
    brand_repo, domain_repo = BrandRepo(), DomainRepo()
    brand_id = await _seed_brand(brand_repo, uid)

    resp = await _create_domain(
        MeDomainCreateRequest(brand_id=brand_id, name="브이로그"), uid,
        brand_repo=brand_repo, domain_repo=domain_repo,
    )
    assert resp.ok is True
    assert resp.domain.id
    assert resp.domain.brand_id == brand_id
    assert resp.domain.name == "브이로그"

    # ★ DomainRepo.list_for_brand 즉시 반영.
    domains = await domain_repo.list_for_brand(brand_id)
    assert any(d.get("id") == resp.domain.id for d in domains)
    assert any(d.get("name") == "브이로그" for d in domains)


# ─── 2. 소유 domain 아래 series 생성 → ok + list 반영 ─────────────────


@pytest.mark.asyncio
async def test_create_series_under_owned_domain() -> None:
    """소유 domain 아래 series 생성 → ok, id 있음, list_for_domain 즉시 포함."""
    uid = "user-A"
    brand_repo, domain_repo, series_repo = BrandRepo(), DomainRepo(), SeriesRepo()
    _, domain_id = await _seed_domain(brand_repo, domain_repo, uid)

    resp = await _create_series(
        MeSeriesCreateRequest(domain_id=domain_id, name="주간 리뷰"), uid,
        brand_repo=brand_repo, domain_repo=domain_repo, series_repo=series_repo,
    )
    assert resp.ok is True
    assert resp.series.id
    assert resp.series.domain_id == domain_id
    assert resp.series.name == "주간 리뷰"

    # ★ SeriesRepo.list_for_domain 즉시 반영.
    series = await series_repo.list_for_domain(domain_id)
    assert any(s.get("id") == resp.series.id for s in series)
    assert any(s.get("name") == "주간 리뷰" for s in series)


# ─── 3. ★ RLS — 다른 user 의 brand/domain 아래 생성 → 404 ─────────────


@pytest.mark.asyncio
async def test_create_domain_under_other_users_brand_404() -> None:
    """user A 가 user B 소유 brand 아래 domain 생성 시도 → 404, B brand 에 domain 0."""
    brand_repo, domain_repo = BrandRepo(), DomainRepo()
    b_brand = await _seed_brand(brand_repo, "user-B")

    with pytest.raises(Exception) as exc_info:
        await _create_domain(
            MeDomainCreateRequest(brand_id=b_brand, name="침투 도메인"), "user-A",
            brand_repo=brand_repo, domain_repo=domain_repo,
        )
    assert getattr(exc_info.value, "status_code", None) == 404
    # ★ B brand 아래 domain 생성 0.
    assert await domain_repo.list_for_brand(b_brand) == []


@pytest.mark.asyncio
async def test_create_series_under_not_owned_domain_404() -> None:
    """user A 가 user B 소유 domain 아래 series 생성 시도 → 404, B domain 에 series 0."""
    brand_repo, domain_repo, series_repo = BrandRepo(), DomainRepo(), SeriesRepo()
    _, b_domain = await _seed_domain(brand_repo, domain_repo, "user-B")

    with pytest.raises(Exception) as exc_info:
        await _create_series(
            MeSeriesCreateRequest(domain_id=b_domain, name="침투 시리즈"), "user-A",
            brand_repo=brand_repo, domain_repo=domain_repo, series_repo=series_repo,
        )
    assert getattr(exc_info.value, "status_code", None) == 404
    # ★ B domain 아래 series 생성 0.
    assert await series_repo.list_for_domain(b_domain) == []


@pytest.mark.asyncio
async def test_create_series_under_nonexistent_domain_404() -> None:
    """존재하지 않는 domain_id 아래 series → 404 (소유 검증 실패)."""
    brand_repo, domain_repo, series_repo = BrandRepo(), DomainRepo(), SeriesRepo()
    await _seed_brand(brand_repo, "user-A")  # A 는 brand 만 (domain 없음).

    with pytest.raises(Exception) as exc_info:
        await _create_series(
            MeSeriesCreateRequest(domain_id="nope-domain", name="유령 시리즈"), "user-A",
            brand_repo=brand_repo, domain_repo=domain_repo, series_repo=series_repo,
        )
    assert getattr(exc_info.value, "status_code", None) == 404


# ─── 4. 익명 HTTP → 401 ───────────────────────────────────────────────


def test_create_domain_anonymous_returns_401() -> None:
    """토큰 없음(익명) POST /me/domains → 401."""
    client = TestClient(app)
    r = client.post("/api/v1/me/domains", json={"brand_id": "b1", "name": "x"})
    assert r.status_code == 401


def test_create_series_anonymous_returns_401() -> None:
    """토큰 없음(익명) POST /me/series → 401."""
    client = TestClient(app)
    r = client.post("/api/v1/me/series", json={"domain_id": "d1", "name": "x"})
    assert r.status_code == 401


# ─── 5. 빈 name → 422 (Pydantic min_length) ──────────────────────────


def test_create_domain_empty_name_422() -> None:
    """빈 name → 422 (인증 무관 — Pydantic 검증이 먼저)."""
    client = TestClient(app)
    r = client.post("/api/v1/me/domains", json={"brand_id": "b1", "name": ""})
    assert r.status_code == 422


def test_create_series_empty_name_422() -> None:
    """빈 name → 422."""
    client = TestClient(app)
    r = client.post("/api/v1/me/series", json={"domain_id": "d1", "name": ""})
    assert r.status_code == 422


# ─── 6. graceful — repo.create None / raise → unhandled 500 없음 ──────


@pytest.mark.asyncio
async def test_create_domain_repo_none_no_unhandled_500() -> None:
    """domain_repo.create 가 None 반환 → unhandled 500 아님, 503 controlled."""

    class _NoneDomainRepo:
        async def create(self, *a: Any, **k: Any) -> Any:
            return None

    uid = "user-A"
    brand_repo = BrandRepo()
    brand_id = await _seed_brand(brand_repo, uid)

    with pytest.raises(Exception) as exc_info:
        await _create_domain(
            MeDomainCreateRequest(brand_id=brand_id, name="실패 도메인"), uid,
            brand_repo=brand_repo, domain_repo=_NoneDomainRepo(),  # type: ignore[arg-type]
        )
    # ★ unhandled 500 이 아니라 controlled 503.
    assert getattr(exc_info.value, "status_code", None) == 503


@pytest.mark.asyncio
async def test_create_domain_repo_raise_no_unhandled_500() -> None:
    """domain_repo.create 가 raise → endpoint 안전(503), unhandled 500 없음."""

    class _BoomDomainRepo:
        async def create(self, *a: Any, **k: Any) -> Any:
            raise RuntimeError("domains down")

    uid = "user-A"
    brand_repo = BrandRepo()
    brand_id = await _seed_brand(brand_repo, uid)

    with pytest.raises(Exception) as exc_info:
        await _create_domain(
            MeDomainCreateRequest(brand_id=brand_id, name="폭발 도메인"), uid,
            brand_repo=brand_repo, domain_repo=_BoomDomainRepo(),  # type: ignore[arg-type]
        )
    assert getattr(exc_info.value, "status_code", None) == 503


@pytest.mark.asyncio
async def test_create_series_repo_raise_no_unhandled_500() -> None:
    """series_repo.create 가 raise → endpoint 안전(503), unhandled 500 없음."""

    class _BoomSeriesRepo:
        async def create(self, *a: Any, **k: Any) -> Any:
            raise RuntimeError("series down")

    uid = "user-A"
    brand_repo, domain_repo = BrandRepo(), DomainRepo()
    _, domain_id = await _seed_domain(brand_repo, domain_repo, uid)

    with pytest.raises(Exception) as exc_info:
        await _create_series(
            MeSeriesCreateRequest(domain_id=domain_id, name="폭발 시리즈"), uid,
            brand_repo=brand_repo, domain_repo=domain_repo,
            series_repo=_BoomSeriesRepo(),  # type: ignore[arg-type]
        )
    assert getattr(exc_info.value, "status_code", None) == 503


# ─── 7. end-to-end — 생성 후 /me/pkm-graph 깊이 노드 자동 반영 ─────────


@pytest.mark.asyncio
async def test_created_structure_appears_in_pkm_graph() -> None:
    """brand→domain→series 생성 후 같은 repo 로 /me/pkm-graph 집계 → 깊이 노드 자동 반영.

    ★ Phase 21 집계를 전혀 변경하지 않고도 생성된 행이 graph 에 펼쳐짐을 확인.
    """
    uid = "user-A"
    pkm_repo = PkmRepo()
    brand_repo, domain_repo, series_repo = BrandRepo(), DomainRepo(), SeriesRepo()
    brand_memory_repo = BrandMemoryRepo()

    brand_id = await _seed_brand(brand_repo, uid)
    d = await _create_domain(
        MeDomainCreateRequest(brand_id=brand_id, name="브이로그"), uid,
        brand_repo=brand_repo, domain_repo=domain_repo,
    )
    s = await _create_series(
        MeSeriesCreateRequest(domain_id=d.domain.id, name="주간 리뷰"), uid,
        brand_repo=brand_repo, domain_repo=domain_repo, series_repo=series_repo,
    )

    graph = await _aggregate_pkm_graph(
        uid,
        pkm_repo=pkm_repo,
        brand_repo=brand_repo,
        brand_memory_repo=brand_memory_repo,
        domain_repo=domain_repo,
        series_repo=series_repo,
    )

    node_ids = {n.id for n in graph.nodes}
    assert f"domain:{d.domain.id}" in node_ids
    assert f"series:{s.series.id}" in node_ids
    assert graph.summary.domains == 1
    assert graph.summary.series == 1
    # 엣지 — brand → domain (has_domain), domain → series (has_series).
    kinds = {e.kind for e in graph.edges}
    assert "has_domain" in kinds
    assert "has_series" in kinds


# ─── 8. HTTP end-to-end (dev_auth_mock 쿠키) — 생성 200 ───────────────


def test_create_domain_http_authed_200(monkeypatch: pytest.MonkeyPatch) -> None:
    """dev_auth_mock + mock-token 쿠키 → mock-user-1 의 소유 brand 아래 domain 생성 200."""
    _config_module.get_settings.cache_clear()
    settings = _config_module.get_settings()
    monkeypatch.setattr(settings, "dev_auth_mock", True, raising=False)
    monkeypatch.setattr(_db_client_module, "get_supabase", lambda: None)
    monkeypatch.setattr("backend.fastapi.routers.auth.get_supabase", lambda: None)

    import asyncio

    brand_repo, domain_repo = BrandRepo(), DomainRepo()
    brand_id = asyncio.run(_seed_brand(brand_repo, "mock-user-1"))
    monkeypatch.setattr(me_router, "_brand_repo", brand_repo)
    monkeypatch.setattr(me_router, "_domain_repo", domain_repo)

    client = TestClient(app)
    client.cookies.set("sb_access_token", "mock-token")
    r = client.post("/api/v1/me/domains", json={"brand_id": brand_id, "name": "HTTP 도메인"})
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert data["domain"]["id"]
    assert data["domain"]["name"] == "HTTP 도메인"
    # 생성 반영.
    assert asyncio.run(domain_repo.list_for_brand(brand_id))


def test_create_domain_http_cross_user_404(monkeypatch: pytest.MonkeyPatch) -> None:
    """dev_auth_mock → mock-user-1 이 타인 brand 아래 domain 생성 시도 → 404 (HTTP wired)."""
    _config_module.get_settings.cache_clear()
    settings = _config_module.get_settings()
    monkeypatch.setattr(settings, "dev_auth_mock", True, raising=False)
    monkeypatch.setattr(_db_client_module, "get_supabase", lambda: None)
    monkeypatch.setattr("backend.fastapi.routers.auth.get_supabase", lambda: None)

    import asyncio

    brand_repo, domain_repo = BrandRepo(), DomainRepo()
    other_brand = asyncio.run(_seed_brand(brand_repo, "other-user"))
    monkeypatch.setattr(me_router, "_brand_repo", brand_repo)
    monkeypatch.setattr(me_router, "_domain_repo", domain_repo)

    client = TestClient(app)
    client.cookies.set("sb_access_token", "mock-token")
    r = client.post("/api/v1/me/domains", json={"brand_id": other_brand, "name": "침투"})
    assert r.status_code == 404
    assert asyncio.run(domain_repo.list_for_brand(other_brand)) == []


def test_structure_create_endpoints_in_openapi() -> None:
    """Phase 22 S1 POST /me/domains, /me/series 가 OpenAPI 문서에 노출."""
    client = TestClient(app)
    r = client.get("/openapi.json")
    assert r.status_code == 200
    paths = r.json().get("paths", {})
    assert "post" in paths.get("/api/v1/me/domains", {})
    assert "post" in paths.get("/api/v1/me/series", {})
