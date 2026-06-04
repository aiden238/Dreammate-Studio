"""Phase 25 Slice S1 — 브랜딩 택1 → domain/series auto-seed (wizard↔4계층 link) 테스트.

브랜딩 세션을 완료하고 후보를 택1(/branding/select)하면, gated+authed 일 때 그 주제→domain /
포맷→series 를 사용자 기본 brand 아래 auto-create 한다. 그러면 브랜딩 흐름만으로 /brain 4계층
(Phase 21/22 graph)이 자동으로 채워진다. ★ _seed_branding_pkm 와 동일 게이트/신원/graceful (새 flag 없음).

검증 축:
  - flag ON + 신원 → domain(name==topic) + series(name==format) auto-create, (domain_id, series_id) non-null.
  - ★ 멱등 — 동일 주제 재택1 → domain 1개만(중복 0), get_or_create 가 기존 row 재사용.
  - gated — flag OFF → 생성 0, (None, None), BrandRepo 미호출 (no surprise write). ★ HTTP 응답 byte-identical
    (domain_id/series_id null) — 기존 branding-select 동작 불변.
  - 익명(auth_user_id None) → 생성 0, (None, None), 에러 0.
  - graceful — repo 실패 → 500 0, 응답은 그대로 (domain_id/series_id null).
  - repo unit — DomainRepo/SeriesRepo.get_or_create 멱등 (2회 동일 name → 1 row).

★ DI seam: _auto_create_domain_series 에 brand_repo/domain_repo/series_repo 인자 주입 → 실 Supabase
  없이 end-to-end 배선 입증 (test_branding_select 의 _seed_branding_pkm 패턴). ADD only (회귀 0).
"""

from __future__ import annotations

from typing import Any

import pytest
from fastapi.testclient import TestClient

from backend.fastapi import config as _config_module
from backend.fastapi.config import get_settings
from backend.fastapi.db import client as _db_client_module
from backend.fastapi.db.repositories.brand_repo import BrandRepo
from backend.fastapi.db.repositories.domain_repo import DomainRepo
from backend.fastapi.db.repositories.series_repo import SeriesRepo
from backend.fastapi.main import app
from backend.fastapi.routers import plans as plans_router
from backend.fastapi.routers.plans import _auto_create_domain_series
from backend.fastapi.schemas.plans import BrandingSelectRequest

client = TestClient(app)


# ─── helpers ──────────────────────────────────────────────────────────


def _set_seed_flag(monkeypatch: pytest.MonkeyPatch, enabled: bool) -> None:
    """settings.branding_pkm_seed_enabled 토글 + lru_cache 무효화 (동일 게이트, 새 flag 없음)."""
    monkeypatch.setenv("BRANDING_PKM_SEED_ENABLED", "true" if enabled else "false")
    get_settings.cache_clear()
    assert get_settings().branding_pkm_seed_enabled is enabled


class _ForbiddenBrandRepo:
    """get_or_create_default 호출 시 즉시 실패 (no surprise write 보장 — flag OFF/anon)."""

    async def get_or_create_default(self, *args: Any, **kwargs: Any) -> str:  # pragma: no cover
        raise AssertionError("BrandRepo.get_or_create_default must NOT be called (flag OFF/anon)")


def _fresh_repos() -> tuple[BrandRepo, DomainRepo, SeriesRepo]:
    return (
        BrandRepo(supabase_client=None, in_memory_store={}),
        DomainRepo(supabase_client=None, in_memory_store={}),
        SeriesRepo(supabase_client=None, in_memory_store={}),
    )


def _candidate(**over: Any) -> BrandingSelectRequest:
    base = {
        "topic": "30대 직장인 점심 도시락 브이로그",
        "tone": "친근하고 담백한 톤",
        "target": "30대 직장인",
        "format": "60초 세로 쇼츠",
    }
    base.update(over)
    return BrandingSelectRequest(**base)


def _new_plan_id() -> str:
    r = client.post("/api/v1/plans/start", json={"user_input": None})
    assert r.status_code == 201
    return r.json()["plan_id"]


# ─── 1. flag ON + 신원 → domain(topic) + series(format) auto-create ─────


@pytest.mark.asyncio
async def test_auto_create_on_seeds_domain_and_series(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """★ flag ON + authed → domain(name==topic) + series(name==format) 생성, id 둘 다 non-null."""
    _set_seed_flag(monkeypatch, True)
    brand, domain_repo, series_repo = _fresh_repos()

    domain_id, series_id = await _auto_create_domain_series(
        "plan-1", "u-1", _candidate(),
        brand_repo=brand, domain_repo=domain_repo, series_repo=series_repo,
    )
    assert domain_id is not None
    assert series_id is not None

    brand_id = await brand.get_default_brand_id("u-1")
    assert brand_id is not None
    domains = await domain_repo.list_for_brand(brand_id)
    assert len(domains) == 1
    assert domains[0]["name"] == "30대 직장인 점심 도시락 브이로그"  # topic → domain name
    assert str(domains[0]["id"]) == domain_id

    series = await series_repo.list_for_domain(domain_id)
    assert len(series) == 1
    assert series[0]["name"] == "60초 세로 쇼츠"  # format → series name
    assert str(series[0]["id"]) == series_id


@pytest.mark.asyncio
async def test_auto_create_default_series_name_when_format_blank(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """format 비면 기본 시리즈 이름으로 series 생성 (domain 은 항상 topic)."""
    _set_seed_flag(monkeypatch, True)
    brand, domain_repo, series_repo = _fresh_repos()

    domain_id, series_id = await _auto_create_domain_series(
        "plan-f", "u-f", _candidate(format="  "),
        brand_repo=brand, domain_repo=domain_repo, series_repo=series_repo,
    )
    assert domain_id is not None
    assert series_id is not None
    series = await series_repo.list_for_domain(domain_id)
    assert series[0]["name"] == "기본 시리즈"


# ─── 2. ★ 멱등 — 동일 주제 재택1 → domain/series 중복 0 ─────────────────


@pytest.mark.asyncio
async def test_auto_create_idempotent_on_reselect(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """★ 동일 주제 재택1 → get_or_create 가 기존 row 재사용 → domain/series 각 1개만 (중복 0)."""
    _set_seed_flag(monkeypatch, True)
    brand, domain_repo, series_repo = _fresh_repos()

    first = await _auto_create_domain_series(
        "plan-2", "u-2", _candidate(),
        brand_repo=brand, domain_repo=domain_repo, series_repo=series_repo,
    )
    second = await _auto_create_domain_series(
        "plan-2", "u-2", _candidate(),
        brand_repo=brand, domain_repo=domain_repo, series_repo=series_repo,
    )
    # 동일 (topic, format) → 동일 domain/series id 재사용.
    assert first == second
    assert first[0] is not None and first[1] is not None

    brand_id = await brand.get_default_brand_id("u-2")
    domains = await domain_repo.list_for_brand(brand_id)
    assert len(domains) == 1  # ★ 중복 0
    series = await series_repo.list_for_domain(first[0])
    assert len(series) == 1  # ★ 중복 0


# ─── 3. gated — flag OFF → 생성 0, BrandRepo 미호출 (no surprise write) ──


@pytest.mark.asyncio
async def test_auto_create_off_no_call_no_write(monkeypatch: pytest.MonkeyPatch) -> None:
    """★ flag OFF(default) → BrandRepo 미호출, domain/series 생성 0, (None, None)."""
    _set_seed_flag(monkeypatch, False)
    _, domain_repo, series_repo = _fresh_repos()

    result = await _auto_create_domain_series(
        "plan-3", "u-3", _candidate(),
        brand_repo=_ForbiddenBrandRepo(), domain_repo=domain_repo, series_repo=series_repo,
    )
    assert result == (None, None)
    assert domain_repo.store == {}
    assert series_repo.store == {}


# ─── 4. 익명 → 생성 0, BrandRepo 미호출 ─────────────────────────────────


@pytest.mark.asyncio
async def test_auto_create_anonymous_no_call_no_write(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """★ flag ON 이어도 익명(auth_user_id None) → BrandRepo 미호출, 생성 0, (None, None)."""
    _set_seed_flag(monkeypatch, True)
    _, domain_repo, series_repo = _fresh_repos()

    result = await _auto_create_domain_series(
        "plan-4", None, _candidate(),
        brand_repo=_ForbiddenBrandRepo(), domain_repo=domain_repo, series_repo=series_repo,
    )
    assert result == (None, None)
    assert domain_repo.store == {}
    assert series_repo.store == {}


# ─── 5. graceful — repo 실패 → raise 0, 확보분(None)만 반환 ──────────────


@pytest.mark.asyncio
async def test_auto_create_graceful_when_brand_raises(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """★ brand 해결이 예외를 던져도 hook 은 raise 0 → (None, None) (graceful)."""
    _set_seed_flag(monkeypatch, True)
    _, domain_repo, series_repo = _fresh_repos()

    class _BoomBrandRepo:
        async def get_or_create_default(self, *a: Any, **k: Any) -> str:
            raise RuntimeError("simulated brand failure")

    result = await _auto_create_domain_series(
        "plan-5", "u-5", _candidate(),
        brand_repo=_BoomBrandRepo(), domain_repo=domain_repo, series_repo=series_repo,
    )
    assert result == (None, None)


@pytest.mark.asyncio
async def test_auto_create_partial_when_series_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """★ domain 은 생성됐는데 series 생성이 실패 → (domain_id, None) (확보분만, raise 0)."""
    _set_seed_flag(monkeypatch, True)
    brand, domain_repo, _ = _fresh_repos()

    class _BoomSeriesRepo:
        async def get_or_create(self, *a: Any, **k: Any) -> None:
            raise RuntimeError("simulated series failure")

    domain_id, series_id = await _auto_create_domain_series(
        "plan-6", "u-6", _candidate(),
        brand_repo=brand, domain_repo=domain_repo, series_repo=_BoomSeriesRepo(),
    )
    assert domain_id is not None  # domain 은 생성됨
    assert series_id is None  # series 는 실패 → None (graceful)


# ─── 6. HTTP e2e — flag OFF → byte-identical (domain_id/series_id null) ──


def test_select_http_off_byte_identical(monkeypatch: pytest.MonkeyPatch) -> None:
    """★ flag OFF → 기존 동작 불변: ok/seeded 그대로, domain_id/series_id null (additive)."""
    _set_seed_flag(monkeypatch, False)
    plan_id = _new_plan_id()

    r = client.post(
        f"/api/v1/plans/{plan_id}/branding/select",
        json={"topic": "주제 X", "tone": "톤 X", "target": "타깃 X", "format": "포맷 X"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True
    assert body["seeded"] == 0  # OFF → 시드 0 (기존 불변)
    assert body["domain_id"] is None  # OFF → 4계층 생성 0
    assert body["series_id"] is None
    # planning 연결(initial_input/selected)은 항상 저장 — 기존 동작 불변.
    entry = plans_router._plan_store[plan_id]
    assert entry["initial_input"] == "주제 X"


def test_select_http_anonymous_no_4layer(monkeypatch: pytest.MonkeyPatch) -> None:
    """★ flag ON 이지만 익명(쿠키 없음) → domain_id/series_id null, 200, 에러 0."""
    _set_seed_flag(monkeypatch, True)
    plan_id = _new_plan_id()

    anon = TestClient(app)  # 쿠키 없음 → request.state.user None
    r = anon.post(
        f"/api/v1/plans/{plan_id}/branding/select",
        json={"topic": "익명 주제", "format": "포맷"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True
    assert body["domain_id"] is None
    assert body["series_id"] is None


def test_select_http_authed_creates_4layer(monkeypatch: pytest.MonkeyPatch) -> None:
    """★ dev_auth_mock + mock-token 쿠키 + flag ON → mock-user-1 brand 아래 domain/series 생성 (e2e)."""
    _set_seed_flag(monkeypatch, True)
    _config_module.get_settings.cache_clear()
    settings = _config_module.get_settings()
    monkeypatch.setattr(settings, "dev_auth_mock", True, raising=False)
    monkeypatch.setattr(_db_client_module, "get_supabase", lambda: None)
    monkeypatch.setattr("backend.fastapi.routers.auth.get_supabase", lambda: None)

    # in-memory 모듈 싱글톤 주입 (hermetic — 실 Supabase 미접근).
    brand, domain_repo, series_repo = _fresh_repos()
    monkeypatch.setattr(plans_router, "_brand_repo", brand)
    monkeypatch.setattr(plans_router, "_domain_repo", domain_repo)
    monkeypatch.setattr(plans_router, "_series_repo", series_repo)

    authed = TestClient(app)
    authed.cookies.set("sb_access_token", "mock-token")
    plan_id = _new_plan_id()
    r = authed.post(
        f"/api/v1/plans/{plan_id}/branding/select",
        json={"topic": "인증 주제", "format": "30초 릴스"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True
    assert body["domain_id"] is not None
    assert body["series_id"] is not None

    # mock-user-1 brand 아래 domain(name==topic) + series(name==format) 실제 생성 확인.
    brand_id = await_default(brand, "mock-user-1")
    domains = run_async(domain_repo.list_for_brand(brand_id))
    assert any(d["name"] == "인증 주제" for d in domains)
    series = run_async(series_repo.list_for_domain(body["domain_id"]))
    assert any(s["name"] == "30초 릴스" for s in series)


def test_select_http_authed_idempotent(monkeypatch: pytest.MonkeyPatch) -> None:
    """★ 동일 주제 두 번 택1(인증) → domain 1개만 (HTTP e2e 멱등 — 중복 0)."""
    _set_seed_flag(monkeypatch, True)
    _config_module.get_settings.cache_clear()
    settings = _config_module.get_settings()
    monkeypatch.setattr(settings, "dev_auth_mock", True, raising=False)
    monkeypatch.setattr(_db_client_module, "get_supabase", lambda: None)
    monkeypatch.setattr("backend.fastapi.routers.auth.get_supabase", lambda: None)

    brand, domain_repo, series_repo = _fresh_repos()
    monkeypatch.setattr(plans_router, "_brand_repo", brand)
    monkeypatch.setattr(plans_router, "_domain_repo", domain_repo)
    monkeypatch.setattr(plans_router, "_series_repo", series_repo)

    authed = TestClient(app)
    authed.cookies.set("sb_access_token", "mock-token")

    for _ in range(2):
        plan_id = _new_plan_id()  # 새 plan 이라도 동일 (brand, topic) → 동일 domain.
        r = authed.post(
            f"/api/v1/plans/{plan_id}/branding/select",
            json={"topic": "반복 주제", "format": "60초"},
        )
        assert r.status_code == 200

    brand_id = await_default(brand, "mock-user-1")
    domains = run_async(domain_repo.list_for_brand(brand_id))
    matching = [d for d in domains if d["name"] == "반복 주제"]
    assert len(matching) == 1  # ★ 두 번 택1 해도 domain 1개


def test_select_http_graceful_when_hook_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    """★ 4계층 hook 이 예외를 던져도 select endpoint 는 200 (graceful, domain_id/series_id null)."""
    _set_seed_flag(monkeypatch, True)

    async def boom(*args: Any, **kwargs: Any) -> tuple[None, None]:
        raise RuntimeError("simulated 4layer failure")

    monkeypatch.setattr(plans_router, "_auto_create_domain_series", boom)

    plan_id = _new_plan_id()
    r = client.post(
        f"/api/v1/plans/{plan_id}/branding/select",
        json={"topic": "주제 G", "format": "포맷 G"},
    )
    assert r.status_code == 200  # ★ hook 실패가 select 를 차단하지 않음
    body = r.json()
    assert body["ok"] is True
    assert body["domain_id"] is None
    assert body["series_id"] is None


# ─── 7. repo unit — get_or_create 멱등 (2회 동일 name → 1 row) ──────────


@pytest.mark.asyncio
async def test_domain_repo_get_or_create_idempotent() -> None:
    """★ DomainRepo.get_or_create — 동일 (brand, name) 2회 → 동일 row 1개 (중복 0)."""
    repo = DomainRepo(supabase_client=None, in_memory_store={})
    first = await repo.get_or_create("brand-x", "도메인 A")
    second = await repo.get_or_create("brand-x", "도메인 A")
    assert first is not None and second is not None
    assert first["id"] == second["id"]  # 기존 row 재사용
    assert len(await repo.list_for_brand("brand-x")) == 1  # ★ 1 row

    # 다른 name → 별도 row.
    other = await repo.get_or_create("brand-x", "도메인 B")
    assert other is not None and other["id"] != first["id"]
    assert len(await repo.list_for_brand("brand-x")) == 2


@pytest.mark.asyncio
async def test_series_repo_get_or_create_idempotent() -> None:
    """★ SeriesRepo.get_or_create — 동일 (domain, name) 2회 → 동일 row 1개 (중복 0)."""
    repo = SeriesRepo(supabase_client=None, in_memory_store={})
    first = await repo.get_or_create("domain-x", "시리즈 A")
    second = await repo.get_or_create("domain-x", "시리즈 A")
    assert first is not None and second is not None
    assert first["id"] == second["id"]  # 기존 row 재사용
    assert len(await repo.list_for_domain("domain-x")) == 1  # ★ 1 row


# ─── helpers (sync wrappers for HTTP e2e 검증) ──────────────────────────


def run_async(coro: Any) -> Any:
    """동기 테스트에서 async repo 메서드 검증용 (asyncio.run 래퍼)."""
    import asyncio

    return asyncio.run(coro)


def await_default(brand: BrandRepo, uid: str) -> str:
    """brand.get_default_brand_id(uid) 동기 검증 헬퍼."""
    bid = run_async(brand.get_default_brand_id(uid))
    assert bid is not None
    return bid
