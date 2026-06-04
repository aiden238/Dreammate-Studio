"""Phase 24 Slice S1 — 구조 편집/삭제(Domain/Series EDIT+DELETE) 엔드포인트 테스트 (mock, CI-safe).

대상 (Phase 22 CREATE 와 대칭, /brain 4계층 CRUD 완성):
  - PATCH  /api/v1/me/domains/{domain_id}  {name}  → 본인 brand 아래 domain rename.
  - DELETE /api/v1/me/domains/{domain_id}          → domain 삭제 + 그 아래 series 캐스케이드.
  - PATCH  /api/v1/me/series/{series_id}   {name}  → 본인 domain 아래 series rename.
  - DELETE /api/v1/me/series/{series_id}           → series 삭제.

검증 축:
  1. 소유 domain rename → name 변경, DomainRepo.list_for_brand 즉시 반영.
  2. 소유 domain 삭제 → list_for_brand 에서 사라짐 AND 그 아래 series 도 캐스케이드 삭제(in-memory).
  3. 소유 series rename/삭제 → SeriesRepo.list_for_domain 즉시 반영.
  4. ★ RLS — 다른 user 의 domain/series 편집·삭제 → 404 (대상 불변).
  5. 익명(토큰 없음) HTTP → 401.
  6. 빈 name → 422 (Pydantic min_length).
  7. graceful — repo update None / delete False / raise → unhandled 500 없음 (404 controlled).

★ mock — 실 Supabase 0 (in-memory repos). DI seam(_update_*/_delete_*)으로 직접 호출하거나,
   TestClient + dev_auth_mock 쿠키로 HTTP 경로(401/422)를 탄다.
"""

from __future__ import annotations

from typing import Any

import pytest
from fastapi.testclient import TestClient

from backend.fastapi import config as _config_module
from backend.fastapi.db import (
    BrandRepo,
    DomainRepo,
    SeriesRepo,
)
from backend.fastapi.db import client as _db_client_module
from backend.fastapi.main import app
from backend.fastapi.routers import me as me_router
from backend.fastapi.routers.me import (
    _delete_domain,
    _delete_series,
    _update_domain,
    _update_series,
)
from backend.fastapi.schemas.graph import (
    MeDomainUpdateRequest,
    MeSeriesUpdateRequest,
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


async def _seed_series(
    brand_repo: BrandRepo,
    domain_repo: DomainRepo,
    series_repo: SeriesRepo,
    auth_user_id: str,
) -> tuple[str, str, str]:
    """소유 brand 1 + domain 1 + series 1 시드 → (brand_id, domain_id, series_id) 반환."""
    brand_id, domain_id = await _seed_domain(brand_repo, domain_repo, auth_user_id)
    row = await series_repo.create(domain_id, "내 시리즈")
    assert row and row.get("id")
    return brand_id, domain_id, str(row["id"])


# ─── 1. 소유 domain rename → name 변경 + list 반영 ────────────────────


@pytest.mark.asyncio
async def test_update_domain_under_owned_brand() -> None:
    """소유 domain rename → ok, name 변경, list_for_brand 즉시 반영."""
    uid = "user-A"
    brand_repo, domain_repo = BrandRepo(), DomainRepo()
    brand_id, domain_id = await _seed_domain(brand_repo, domain_repo, uid)

    resp = await _update_domain(
        domain_id, MeDomainUpdateRequest(name="브이로그(수정)"), uid,
        brand_repo=brand_repo, domain_repo=domain_repo,
    )
    assert resp.ok is True
    assert resp.domain.id == domain_id
    assert resp.domain.name == "브이로그(수정)"

    domains = await domain_repo.list_for_brand(brand_id)
    assert any(d.get("id") == domain_id and d.get("name") == "브이로그(수정)" for d in domains)


# ─── 2. 소유 domain 삭제 → 사라짐 + series 캐스케이드 ─────────────────


@pytest.mark.asyncio
async def test_delete_domain_removes_it_and_cascades_series() -> None:
    """소유 domain 삭제 → list_for_brand 에서 제거 AND 그 아래 series 캐스케이드 삭제(in-memory)."""
    uid = "user-A"
    brand_repo, domain_repo, series_repo = BrandRepo(), DomainRepo(), SeriesRepo()
    brand_id, domain_id, series_id = await _seed_series(
        brand_repo, domain_repo, series_repo, uid,
    )
    # 사전 상태 — domain 1, 그 아래 series 1.
    assert any(d.get("id") == domain_id for d in await domain_repo.list_for_brand(brand_id))
    assert any(s.get("id") == series_id for s in await series_repo.list_for_domain(domain_id))

    resp = await _delete_domain(
        domain_id, uid,
        brand_repo=brand_repo, domain_repo=domain_repo, series_repo=series_repo,
    )
    assert resp.ok is True
    assert resp.deleted is True

    # ★ domain 제거.
    assert all(d.get("id") != domain_id for d in await domain_repo.list_for_brand(brand_id))
    # ★ series 캐스케이드 삭제 — domain 아래 series 0.
    assert await series_repo.list_for_domain(domain_id) == []
    # in-memory store 전체에 그 series_id 가 남지 않음.
    assert all(
        s.get("id") != series_id
        for rows in series_repo.store.values()
        for s in rows
    )


# ─── 3. 소유 series rename/삭제 → list 반영 ───────────────────────────


@pytest.mark.asyncio
async def test_update_series_under_owned_domain() -> None:
    """소유 series rename → ok, name 변경, list_for_domain 즉시 반영."""
    uid = "user-A"
    brand_repo, domain_repo, series_repo = BrandRepo(), DomainRepo(), SeriesRepo()
    _, domain_id, series_id = await _seed_series(brand_repo, domain_repo, series_repo, uid)

    resp = await _update_series(
        series_id, MeSeriesUpdateRequest(name="주간 리뷰(수정)"), uid,
        brand_repo=brand_repo, domain_repo=domain_repo, series_repo=series_repo,
    )
    assert resp.ok is True
    assert resp.series.id == series_id
    assert resp.series.name == "주간 리뷰(수정)"

    series = await series_repo.list_for_domain(domain_id)
    assert any(s.get("id") == series_id and s.get("name") == "주간 리뷰(수정)" for s in series)


@pytest.mark.asyncio
async def test_delete_series_under_owned_domain() -> None:
    """소유 series 삭제 → ok, list_for_domain 에서 제거."""
    uid = "user-A"
    brand_repo, domain_repo, series_repo = BrandRepo(), DomainRepo(), SeriesRepo()
    _, domain_id, series_id = await _seed_series(brand_repo, domain_repo, series_repo, uid)

    resp = await _delete_series(
        series_id, uid,
        brand_repo=brand_repo, domain_repo=domain_repo, series_repo=series_repo,
    )
    assert resp.ok is True
    assert resp.deleted is True
    assert await series_repo.list_for_domain(domain_id) == []


# ─── 4. ★ RLS — 다른 user 의 domain/series 편집·삭제 → 404 (대상 불변) ──


@pytest.mark.asyncio
async def test_update_other_users_domain_404_target_unchanged() -> None:
    """user A 가 user B 소유 domain rename 시도 → 404, B domain name 불변."""
    brand_repo, domain_repo = BrandRepo(), DomainRepo()
    b_brand, b_domain = await _seed_domain(brand_repo, domain_repo, "user-B")

    with pytest.raises(Exception) as exc_info:
        await _update_domain(
            b_domain, MeDomainUpdateRequest(name="침투(수정)"), "user-A",
            brand_repo=brand_repo, domain_repo=domain_repo,
        )
    assert getattr(exc_info.value, "status_code", None) == 404
    # ★ B domain 불변.
    domains = await domain_repo.list_for_brand(b_brand)
    assert any(d.get("id") == b_domain and d.get("name") == "내 도메인" for d in domains)


@pytest.mark.asyncio
async def test_delete_other_users_domain_404_target_unchanged() -> None:
    """user A 가 user B 소유 domain 삭제 시도 → 404, B domain 존속."""
    brand_repo, domain_repo, series_repo = BrandRepo(), DomainRepo(), SeriesRepo()
    b_brand, b_domain = await _seed_domain(brand_repo, domain_repo, "user-B")

    with pytest.raises(Exception) as exc_info:
        await _delete_domain(
            b_domain, "user-A",
            brand_repo=brand_repo, domain_repo=domain_repo, series_repo=series_repo,
        )
    assert getattr(exc_info.value, "status_code", None) == 404
    # ★ B domain 존속.
    assert any(d.get("id") == b_domain for d in await domain_repo.list_for_brand(b_brand))


@pytest.mark.asyncio
async def test_update_other_users_series_404_target_unchanged() -> None:
    """user A 가 user B 소유 series rename 시도 → 404, B series name 불변."""
    brand_repo, domain_repo, series_repo = BrandRepo(), DomainRepo(), SeriesRepo()
    _, b_domain, b_series = await _seed_series(brand_repo, domain_repo, series_repo, "user-B")

    with pytest.raises(Exception) as exc_info:
        await _update_series(
            b_series, MeSeriesUpdateRequest(name="침투(수정)"), "user-A",
            brand_repo=brand_repo, domain_repo=domain_repo, series_repo=series_repo,
        )
    assert getattr(exc_info.value, "status_code", None) == 404
    series = await series_repo.list_for_domain(b_domain)
    assert any(s.get("id") == b_series and s.get("name") == "내 시리즈" for s in series)


@pytest.mark.asyncio
async def test_delete_other_users_series_404_target_unchanged() -> None:
    """user A 가 user B 소유 series 삭제 시도 → 404, B series 존속."""
    brand_repo, domain_repo, series_repo = BrandRepo(), DomainRepo(), SeriesRepo()
    _, b_domain, b_series = await _seed_series(brand_repo, domain_repo, series_repo, "user-B")

    with pytest.raises(Exception) as exc_info:
        await _delete_series(
            b_series, "user-A",
            brand_repo=brand_repo, domain_repo=domain_repo, series_repo=series_repo,
        )
    assert getattr(exc_info.value, "status_code", None) == 404
    assert any(s.get("id") == b_series for s in await series_repo.list_for_domain(b_domain))


# ─── 5. 익명 HTTP → 401 ───────────────────────────────────────────────


def test_update_domain_anonymous_returns_401() -> None:
    """토큰 없음(익명) PATCH /me/domains/{id} → 401."""
    client = TestClient(app)
    r = client.patch("/api/v1/me/domains/d1", json={"name": "x"})
    assert r.status_code == 401


def test_delete_domain_anonymous_returns_401() -> None:
    """토큰 없음(익명) DELETE /me/domains/{id} → 401."""
    client = TestClient(app)
    r = client.delete("/api/v1/me/domains/d1")
    assert r.status_code == 401


def test_update_series_anonymous_returns_401() -> None:
    """토큰 없음(익명) PATCH /me/series/{id} → 401."""
    client = TestClient(app)
    r = client.patch("/api/v1/me/series/s1", json={"name": "x"})
    assert r.status_code == 401


def test_delete_series_anonymous_returns_401() -> None:
    """토큰 없음(익명) DELETE /me/series/{id} → 401."""
    client = TestClient(app)
    r = client.delete("/api/v1/me/series/s1")
    assert r.status_code == 401


# ─── 6. 빈 name → 422 (Pydantic min_length) ──────────────────────────


def test_update_domain_empty_name_422(monkeypatch: pytest.MonkeyPatch) -> None:
    """빈 name → 422 (Pydantic 검증). dev_auth_mock 쿠키로 인증 통과 후 본문 검증."""
    _config_module.get_settings.cache_clear()
    settings = _config_module.get_settings()
    monkeypatch.setattr(settings, "dev_auth_mock", True, raising=False)
    monkeypatch.setattr(_db_client_module, "get_supabase", lambda: None)
    monkeypatch.setattr("backend.fastapi.routers.auth.get_supabase", lambda: None)

    client = TestClient(app)
    client.cookies.set("sb_access_token", "mock-token")
    r = client.patch("/api/v1/me/domains/d1", json={"name": ""})
    assert r.status_code == 422


def test_update_series_empty_name_422(monkeypatch: pytest.MonkeyPatch) -> None:
    """빈 name → 422."""
    _config_module.get_settings.cache_clear()
    settings = _config_module.get_settings()
    monkeypatch.setattr(settings, "dev_auth_mock", True, raising=False)
    monkeypatch.setattr(_db_client_module, "get_supabase", lambda: None)
    monkeypatch.setattr("backend.fastapi.routers.auth.get_supabase", lambda: None)

    client = TestClient(app)
    client.cookies.set("sb_access_token", "mock-token")
    r = client.patch("/api/v1/me/series/s1", json={"name": ""})
    assert r.status_code == 422


# ─── 7. graceful — repo None / False / raise → unhandled 500 없음 ─────


@pytest.mark.asyncio
async def test_update_domain_repo_none_no_unhandled_500() -> None:
    """domain_repo.update_name 이 None 반환(미존재) → unhandled 500 아님, 404 controlled."""
    uid = "user-A"
    brand_repo, domain_repo = BrandRepo(), DomainRepo()
    _, domain_id = await _seed_domain(brand_repo, domain_repo, uid)

    class _NoneUpdateDomainRepo(DomainRepo):
        async def update_name(self, *a: Any, **k: Any) -> Any:
            return None

    none_repo = _NoneUpdateDomainRepo(in_memory_store=domain_repo.store)

    with pytest.raises(Exception) as exc_info:
        await _update_domain(
            domain_id, MeDomainUpdateRequest(name="실패"), uid,
            brand_repo=brand_repo, domain_repo=none_repo,
        )
    assert getattr(exc_info.value, "status_code", None) == 404


@pytest.mark.asyncio
async def test_update_domain_repo_raise_no_unhandled_500() -> None:
    """domain_repo.update_name 이 raise → endpoint 안전(404), unhandled 500 없음."""
    uid = "user-A"
    brand_repo, domain_repo = BrandRepo(), DomainRepo()
    _, domain_id = await _seed_domain(brand_repo, domain_repo, uid)

    class _BoomUpdateDomainRepo(DomainRepo):
        async def update_name(self, *a: Any, **k: Any) -> Any:
            raise RuntimeError("domains down")

    boom_repo = _BoomUpdateDomainRepo(in_memory_store=domain_repo.store)

    with pytest.raises(Exception) as exc_info:
        await _update_domain(
            domain_id, MeDomainUpdateRequest(name="폭발"), uid,
            brand_repo=brand_repo, domain_repo=boom_repo,
        )
    assert getattr(exc_info.value, "status_code", None) == 404


@pytest.mark.asyncio
async def test_delete_domain_repo_false_no_unhandled_500() -> None:
    """domain_repo.delete 가 False 반환 → unhandled 500 아님, 404 controlled."""
    uid = "user-A"
    brand_repo, domain_repo, series_repo = BrandRepo(), DomainRepo(), SeriesRepo()
    _, domain_id = await _seed_domain(brand_repo, domain_repo, uid)

    class _FalseDeleteDomainRepo(DomainRepo):
        async def delete(self, *a: Any, **k: Any) -> Any:
            return False

    false_repo = _FalseDeleteDomainRepo(in_memory_store=domain_repo.store)

    with pytest.raises(Exception) as exc_info:
        await _delete_domain(
            domain_id, uid,
            brand_repo=brand_repo, domain_repo=false_repo, series_repo=series_repo,
        )
    assert getattr(exc_info.value, "status_code", None) == 404


@pytest.mark.asyncio
async def test_delete_series_repo_raise_no_unhandled_500() -> None:
    """series_repo.delete 가 raise → endpoint 안전(404), unhandled 500 없음."""
    uid = "user-A"
    brand_repo, domain_repo, series_repo = BrandRepo(), DomainRepo(), SeriesRepo()
    _, _domain_id, series_id = await _seed_series(brand_repo, domain_repo, series_repo, uid)

    class _BoomDeleteSeriesRepo(SeriesRepo):
        async def delete(self, *a: Any, **k: Any) -> Any:
            raise RuntimeError("series down")

    boom_repo = _BoomDeleteSeriesRepo(in_memory_store=series_repo.store)

    with pytest.raises(Exception) as exc_info:
        await _delete_series(
            series_id, uid,
            brand_repo=brand_repo, domain_repo=domain_repo, series_repo=boom_repo,
        )
    assert getattr(exc_info.value, "status_code", None) == 404


# ─── 8. HTTP end-to-end (dev_auth_mock 쿠키) — PATCH/DELETE wired ──────


def test_update_domain_http_authed_200(monkeypatch: pytest.MonkeyPatch) -> None:
    """dev_auth_mock + mock-token 쿠키 → mock-user-1 의 소유 domain rename 200."""
    _config_module.get_settings.cache_clear()
    settings = _config_module.get_settings()
    monkeypatch.setattr(settings, "dev_auth_mock", True, raising=False)
    monkeypatch.setattr(_db_client_module, "get_supabase", lambda: None)
    monkeypatch.setattr("backend.fastapi.routers.auth.get_supabase", lambda: None)

    import asyncio

    brand_repo, domain_repo = BrandRepo(), DomainRepo()
    _, domain_id = asyncio.run(_seed_domain(brand_repo, domain_repo, "mock-user-1"))
    monkeypatch.setattr(me_router, "_brand_repo", brand_repo)
    monkeypatch.setattr(me_router, "_domain_repo", domain_repo)

    client = TestClient(app)
    client.cookies.set("sb_access_token", "mock-token")
    r = client.patch(f"/api/v1/me/domains/{domain_id}", json={"name": "HTTP 수정"})
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert data["domain"]["name"] == "HTTP 수정"


def test_delete_domain_http_cross_user_404(monkeypatch: pytest.MonkeyPatch) -> None:
    """dev_auth_mock → mock-user-1 이 타인 domain 삭제 시도 → 404 (HTTP wired)."""
    _config_module.get_settings.cache_clear()
    settings = _config_module.get_settings()
    monkeypatch.setattr(settings, "dev_auth_mock", True, raising=False)
    monkeypatch.setattr(_db_client_module, "get_supabase", lambda: None)
    monkeypatch.setattr("backend.fastapi.routers.auth.get_supabase", lambda: None)

    import asyncio

    brand_repo, domain_repo, series_repo = BrandRepo(), DomainRepo(), SeriesRepo()
    other_brand, other_domain = asyncio.run(_seed_domain(brand_repo, domain_repo, "other-user"))
    monkeypatch.setattr(me_router, "_brand_repo", brand_repo)
    monkeypatch.setattr(me_router, "_domain_repo", domain_repo)
    monkeypatch.setattr(me_router, "_series_repo", series_repo)

    client = TestClient(app)
    client.cookies.set("sb_access_token", "mock-token")
    r = client.delete(f"/api/v1/me/domains/{other_domain}")
    assert r.status_code == 404
    # ★ 타인 domain 존속.
    assert any(d.get("id") == other_domain for d in asyncio.run(domain_repo.list_for_brand(other_brand)))


def test_structure_crud_endpoints_in_openapi() -> None:
    """Phase 24 S1 PATCH/DELETE /me/domains/{id}, /me/series/{id} 가 OpenAPI 문서에 노출."""
    client = TestClient(app)
    r = client.get("/openapi.json")
    assert r.status_code == 200
    paths = r.json().get("paths", {})
    assert "patch" in paths.get("/api/v1/me/domains/{domain_id}", {})
    assert "delete" in paths.get("/api/v1/me/domains/{domain_id}", {})
    assert "patch" in paths.get("/api/v1/me/series/{series_id}", {})
    assert "delete" in paths.get("/api/v1/me/series/{series_id}", {})
