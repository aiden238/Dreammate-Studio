"""Phase 18 Slice S4 — 브랜딩 후보 택1 → planning 연결 + brand_memory 시드 테스트.

발굴(P18 branding)한 후보를 택1(/branding/select)하면 (1) plan_entry.initial_input 을 그 주제로
설정해 후속 generate 가 받게 하고(planning 연결), (2) gated+authed 일 때 그 브랜딩 방향
(tone/target/format)을 사용자 brand_memory 로 시드한다(축적 — P17 주입 루프가 다음 generate 부터 읽음).

검증 축:
  - flag ON + 신원 + 주입 in-memory repos → tone→preferred_tone, target/format→preferred_phrase 가
    auto-create 된 brand 에 confidence 0.9 로 적재 (seeded == N). selected/initial_input 저장.
  - flag OFF(default) → BrandRepo 미호출(no surprise write), seed 0, 그래도 selected/initial_input 저장.
  - 익명(auth_user_id None) → seed 0, BrandRepo 미호출.
  - dedup — 동일 후보 재택1 → 중복 적재 0 (seeded 0).
  - 404 — 미발견 plan_id → INV-006.
  - graceful — seed hook 이 예외를 던져도 select endpoint 200 (차단 0).

★ DI seam: _seed_branding_pkm 에 brand_repo / brand_memory_repo 인자 주입 → 실 Supabase 없이
  end-to-end 시드 배선 입증 (test_brand_memory_extract_wiring 패턴). ADD only (회귀 0).
"""

from __future__ import annotations

from typing import Any

import pytest
from fastapi.testclient import TestClient

from backend.fastapi.config import get_settings
from backend.fastapi.db.repositories.brand_memory_repo import BrandMemoryRepo
from backend.fastapi.db.repositories.brand_repo import BrandRepo
from backend.fastapi.main import app
from backend.fastapi.routers import plans as plans_router
from backend.fastapi.routers.plans import _seed_branding_pkm
from backend.fastapi.schemas.plans import BrandingSelectRequest

client = TestClient(app)


# ─── helpers ──────────────────────────────────────────────────────────


def _set_seed_flag(monkeypatch: pytest.MonkeyPatch, enabled: bool) -> None:
    """settings.branding_pkm_seed_enabled 토글 + lru_cache 무효화 (다-S5 패턴 동일)."""
    monkeypatch.setenv("BRANDING_PKM_SEED_ENABLED", "true" if enabled else "false")
    get_settings.cache_clear()
    assert get_settings().branding_pkm_seed_enabled is enabled


class _ForbiddenBrandRepo:
    """get_or_create_default 호출 시 즉시 실패 (no surprise write 보장 — 다-S5 패턴)."""

    async def get_or_create_default(self, *args: Any, **kwargs: Any) -> str:  # pragma: no cover
        raise AssertionError("BrandRepo.get_or_create_default must NOT be called (flag OFF/anon)")

    async def get_default_brand_id(self, *args: Any, **kwargs: Any) -> str:  # pragma: no cover
        raise AssertionError("BrandRepo.get_default_brand_id must NOT be called (flag OFF/anon)")


def _fresh_repos() -> tuple[BrandRepo, BrandMemoryRepo]:
    return (
        BrandRepo(supabase_client=None, in_memory_store={}),
        BrandMemoryRepo(supabase_client=None, in_memory_store={}),
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


# ─── 1. flag ON + 신원 → 시드 (tone/target/format 매핑 + confidence 0.9) ──


@pytest.mark.asyncio
async def test_seed_on_persists_branding_direction(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """★ flag ON + authed → tone→preferred_tone, target/format→preferred_phrase 가 0.9 로 적재."""
    _set_seed_flag(monkeypatch, True)
    brand, mem = _fresh_repos()

    seeded = await _seed_branding_pkm(
        "plan-1", "u-1", _candidate(),
        brand_repo=brand, brand_memory_repo=mem,
    )
    assert seeded == 3  # tone + target + format

    brand_id = await brand.get_default_brand_id("u-1")
    assert brand_id is not None
    entries = await mem.list_for_brand(brand_id)
    assert len(entries) == 3
    # 전부 명시 택1 = 고신뢰 0.9.
    assert all(float(e["confidence"]) == 0.9 for e in entries)
    by_type = {(e["entry_type"], e["content"]) for e in entries}
    assert ("preferred_tone", "친근하고 담백한 톤") in by_type
    assert ("preferred_phrase", "타깃 시청자: 30대 직장인") in by_type
    assert ("preferred_phrase", "선호 포맷: 60초 세로 쇼츠") in by_type
    # source_plan_id 가 plan 으로 기록됨.
    assert all(e.get("source_plan_id") == "plan-1" for e in entries)


@pytest.mark.asyncio
async def test_seed_on_tone_only_seeds_one(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """tone 만 있고 target/format 비면 1건만 시드 (빈 값 skip)."""
    _set_seed_flag(monkeypatch, True)
    brand, mem = _fresh_repos()

    seeded = await _seed_branding_pkm(
        "plan-t", "u-t", _candidate(tone="유쾌한 톤", target=None, format="  "),
        brand_repo=brand, brand_memory_repo=mem,
    )
    assert seeded == 1
    brand_id = await brand.get_default_brand_id("u-t")
    entries = await mem.list_for_brand(brand_id)
    assert len(entries) == 1
    assert entries[0]["entry_type"] == "preferred_tone"


# ─── 2. flag OFF → no brand, no seed (no surprise write) ────────────────


@pytest.mark.asyncio
async def test_seed_off_no_call_no_write(monkeypatch: pytest.MonkeyPatch) -> None:
    """★ flag OFF(default) → BrandRepo 미호출, brand_memory 쓰기 0, seeded 0."""
    _set_seed_flag(monkeypatch, False)
    _, mem = _fresh_repos()

    seeded = await _seed_branding_pkm(
        "plan-2", "u-2", _candidate(),
        brand_repo=_ForbiddenBrandRepo(), brand_memory_repo=mem,
    )
    assert seeded == 0
    assert mem.store == {}


# ─── 3. 익명 → no seed ──────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_seed_anonymous_no_call_no_write(monkeypatch: pytest.MonkeyPatch) -> None:
    """★ flag ON 이어도 익명(auth_user_id None) → BrandRepo 미호출, 쓰기 0."""
    _set_seed_flag(monkeypatch, True)
    _, mem = _fresh_repos()

    seeded = await _seed_branding_pkm(
        "plan-3", None, _candidate(),
        brand_repo=_ForbiddenBrandRepo(), brand_memory_repo=mem,
    )
    assert seeded == 0
    assert mem.store == {}


# ─── 4. dedup — 동일 후보 재택1 → 중복 적재 0 ──────────────────────────


@pytest.mark.asyncio
async def test_seed_dedup_on_reselect(monkeypatch: pytest.MonkeyPatch) -> None:
    """★ 동일 후보 재택1 → 동일 (entry_type, content) dedup → 두 번째 seeded 0."""
    _set_seed_flag(monkeypatch, True)
    brand, mem = _fresh_repos()

    first = await _seed_branding_pkm(
        "plan-4", "u-4", _candidate(),
        brand_repo=brand, brand_memory_repo=mem,
    )
    second = await _seed_branding_pkm(
        "plan-4", "u-4", _candidate(),
        brand_repo=brand, brand_memory_repo=mem,
    )
    assert first == 3
    assert second == 0  # 전부 dedup

    brand_id = await brand.get_default_brand_id("u-4")
    entries = await mem.list_for_brand(brand_id)
    assert len(entries) == 3  # 중복 없이 3건만


# ─── 5. HTTP e2e — selected/initial_input 저장 (시드 유무 무관) ─────────


def test_select_stores_selected_and_initial_input_when_off(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """★ flag OFF → seed 0 이지만 selected/initial_input 은 항상 저장 (planning 연결, byte-identical)."""
    _set_seed_flag(monkeypatch, False)
    plan_id = _new_plan_id()

    r = client.post(
        f"/api/v1/plans/{plan_id}/branding/select",
        json={
            "topic": "주제 X",
            "tone": "톤 X",
            "target": "타깃 X",
            "format": "포맷 X",
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True
    assert body["seeded"] == 0  # OFF → 시드 0

    # planning 연결 — initial_input + selected 저장 확인.
    entry = plans_router._plan_store[plan_id]
    assert entry["initial_input"] == "주제 X"
    selected = entry["wizard_data"]["branding"]["selected"]
    assert selected["topic"] == "주제 X"
    assert selected["tone"] == "톤 X"


def test_select_unknown_plan_404() -> None:
    """미발견 plan_id → 404 INV-006."""
    r = client.post(
        "/api/v1/plans/not-a-real-id/branding/select",
        json={"topic": "x"},
    )
    assert r.status_code == 404
    assert r.json()["error"]["code"] == "INV-006"


def test_select_graceful_when_seed_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    """★ seed hook 이 예외를 던져도 select endpoint 는 200 (graceful, 차단 0)."""
    _set_seed_flag(monkeypatch, True)

    async def boom(*args: Any, **kwargs: Any) -> int:
        raise RuntimeError("simulated seed failure")

    monkeypatch.setattr(plans_router, "_seed_branding_pkm", boom)

    plan_id = _new_plan_id()
    r = client.post(
        f"/api/v1/plans/{plan_id}/branding/select",
        json={"topic": "주제 Y", "tone": "톤 Y"},
    )
    # ★ 시드 실패가 select 저장을 차단하지 않음 — 200 + selected/initial_input 저장.
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True
    assert body["seeded"] == 0  # 예외 → 응답상 0
    assert plans_router._plan_store[plan_id]["initial_input"] == "주제 Y"


def test_select_endpoint_in_openapi() -> None:
    """Phase 18 S4 branding/select endpoint 가 OpenAPI 문서에 노출."""
    r = client.get("/openapi.json")
    assert r.status_code == 200
    paths = r.json().get("paths", {})
    assert "/api/v1/plans/{plan_id}/branding/select" in paths
