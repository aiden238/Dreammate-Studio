"""Phase 19 Slice S4 — PKM 큐레이션(잠금/편집/삭제) 엔드포인트 테스트 (mock, CI-safe).

대상:
  - PATCH /api/v1/me/pkm/{node_id}  (content 편집 / locked 토글)
  - DELETE /api/v1/me/pkm/{node_id} (삭제)
  분기: 'pkm:<id>' 개인(PkmRepo, auth_user_id 격리) / 'bm:<id>' 브랜드(소유 brand 검증 후 BrandMemoryRepo).

검증 축:
  1. PATCH locked 토글 (개인 + 브랜드) → is_user_locked 변경.
  2. PATCH content (개인 + 브랜드) → content 변경.
  3. DELETE (개인 + 브랜드) → 제거.
  4. RLS — user A 가 user B 의 pkm/bm 수정·삭제 시도 → 404 (미소유), B 데이터 불변.
  5. 익명 → 401. unknown node_id → 404. graceful(repo raise) → 404, 500 X.

★ mock — 실 Supabase 0 (in-memory repos). DI seam(_curate_pkm_patch/_curate_pkm_delete)으로
   직접 호출하거나, TestClient + dev_auth_mock 쿠키로 HTTP 경로(401 검증)를 탄다.
"""

from __future__ import annotations

from typing import Any

import pytest
from fastapi.testclient import TestClient

from backend.fastapi import config as _config_module
from backend.fastapi.db import BrandMemoryRepo, BrandRepo, PkmRepo
from backend.fastapi.db import client as _db_client_module
from backend.fastapi.main import app
from backend.fastapi.routers import me as me_router
from backend.fastapi.routers.me import _curate_pkm_delete, _curate_pkm_patch
from backend.fastapi.schemas.graph import MePkmPatchRequest


# ─── helpers ──────────────────────────────────────────────────────────


async def _seed_personal(repo: PkmRepo, auth_user_id: str, entry_id: str, content: str,
                         *, locked: bool = False) -> str:
    """개인 PKM entry 를 명시 id 로 시드(실 Supabase row 모사). node_id 반환."""
    await repo.add_entry(auth_user_id, "preferred_tone", content, is_user_locked=locked)
    # add_entry 는 in-memory id 미설정 → 방금 추가한 행에 id 부여 (Supabase row 모사).
    repo.store[auth_user_id][-1]["id"] = entry_id
    return f"pkm:{entry_id}"


async def _seed_brand(
    brand_repo: BrandRepo, bm_repo: BrandMemoryRepo,
    auth_user_id: str, entry_id: str, content: str, *, locked: bool = False,
) -> tuple[str, str]:
    """소유 brand 1 + 브랜드 PKM entry 시드. (node_id, brand_id) 반환.

    ★ 실 Supabase row 모사 — brand_memory_entries PK 는 **entry_id**(0005), `id` 컬럼 없음.
    (구 버전은 `["id"]` 를 주입해 live schema(entry_id) 회귀를 못 잡았다 — CODEX 발견, 2026-06-22.)
    """
    brand_id = await brand_repo.get_or_create_default(auth_user_id, name="내 브랜드")
    assert brand_id
    await bm_repo.add_entry(brand_id, "preferred_tone", content)
    row = bm_repo.store[brand_id][-1]
    row["entry_id"] = entry_id  # 실 PK 컬럼 — repo 가 read 시 entry_id→id 미러
    row.pop("id", None)         # 실 DB 행엔 id 없음
    row["is_user_locked"] = locked
    return f"bm:{entry_id}", brand_id


# ─── 1. PATCH locked 토글 (개인 + 브랜드) ──────────────────────────────


@pytest.mark.asyncio
async def test_patch_personal_lock_toggle() -> None:
    """개인 PKM locked 토글 → is_user_locked 변경, node.locked 반영."""
    uid = "user-A"
    pkm_repo = PkmRepo()
    node_id = await _seed_personal(pkm_repo, uid, "p1", "담백한 톤", locked=False)

    resp = await _curate_pkm_patch(
        node_id, MePkmPatchRequest(locked=True), uid,
        pkm_repo=pkm_repo, brand_repo=BrandRepo(), brand_memory_repo=BrandMemoryRepo(),
    )
    assert resp.ok is True
    assert resp.node is not None
    assert resp.node.locked is True
    assert pkm_repo.store[uid][0]["is_user_locked"] is True


@pytest.mark.asyncio
async def test_patch_brand_lock_toggle() -> None:
    """브랜드 PKM locked 토글 → 소유 검증 통과 + is_user_locked 변경."""
    uid = "user-A"
    brand_repo, bm_repo = BrandRepo(), BrandMemoryRepo()
    node_id, brand_id = await _seed_brand(brand_repo, bm_repo, uid, "b1", "브랜드 톤")

    resp = await _curate_pkm_patch(
        node_id, MePkmPatchRequest(locked=True), uid,
        pkm_repo=PkmRepo(), brand_repo=brand_repo, brand_memory_repo=bm_repo,
    )
    assert resp.ok is True
    assert resp.node is not None
    assert resp.node.locked is True
    assert bm_repo.store[brand_id][0]["is_user_locked"] is True


# ─── 2. PATCH content (개인 + 브랜드) ──────────────────────────────────


@pytest.mark.asyncio
async def test_patch_personal_content() -> None:
    """개인 PKM content 편집 → content 변경, node.label 반영."""
    uid = "user-A"
    pkm_repo = PkmRepo()
    node_id = await _seed_personal(pkm_repo, uid, "p1", "이전 내용")

    resp = await _curate_pkm_patch(
        node_id, MePkmPatchRequest(content="새 내용"), uid,
        pkm_repo=pkm_repo, brand_repo=BrandRepo(), brand_memory_repo=BrandMemoryRepo(),
    )
    assert resp.ok is True
    assert resp.node is not None
    assert resp.node.label == "새 내용"
    assert pkm_repo.store[uid][0]["content"] == "새 내용"


@pytest.mark.asyncio
async def test_patch_brand_content() -> None:
    """브랜드 PKM content 편집 → content 변경."""
    uid = "user-A"
    brand_repo, bm_repo = BrandRepo(), BrandMemoryRepo()
    node_id, brand_id = await _seed_brand(brand_repo, bm_repo, uid, "b1", "이전 브랜드 내용")

    resp = await _curate_pkm_patch(
        node_id, MePkmPatchRequest(content="새 브랜드 내용"), uid,
        pkm_repo=PkmRepo(), brand_repo=brand_repo, brand_memory_repo=bm_repo,
    )
    assert resp.ok is True
    assert resp.node is not None
    assert resp.node.label == "새 브랜드 내용"
    assert bm_repo.store[brand_id][0]["content"] == "새 브랜드 내용"


# ─── 3. DELETE (개인 + 브랜드) ─────────────────────────────────────────


@pytest.mark.asyncio
async def test_delete_personal() -> None:
    """개인 PKM 삭제 → store 에서 제거."""
    uid = "user-A"
    pkm_repo = PkmRepo()
    node_id = await _seed_personal(pkm_repo, uid, "p1", "삭제 대상")

    resp = await _curate_pkm_delete(
        node_id, uid,
        pkm_repo=pkm_repo, brand_repo=BrandRepo(), brand_memory_repo=BrandMemoryRepo(),
    )
    assert resp.ok is True
    assert pkm_repo.store.get(uid, []) == []


@pytest.mark.asyncio
async def test_delete_brand() -> None:
    """브랜드 PKM 삭제 → 소유 검증 통과 + store 에서 제거."""
    uid = "user-A"
    brand_repo, bm_repo = BrandRepo(), BrandMemoryRepo()
    node_id, brand_id = await _seed_brand(brand_repo, bm_repo, uid, "b1", "삭제 대상")

    resp = await _curate_pkm_delete(
        node_id, uid,
        pkm_repo=PkmRepo(), brand_repo=brand_repo, brand_memory_repo=bm_repo,
    )
    assert resp.ok is True
    assert bm_repo.store.get(brand_id, []) == []


# ─── 4. RLS — A 가 B 의 데이터 수정·삭제 시도 → 404, B 불변 ──────────────


@pytest.mark.asyncio
async def test_patch_personal_cross_user_blocked() -> None:
    """user A 가 user B 의 개인 PKM 수정 시도 → 404, B 데이터 불변."""
    pkm_repo = PkmRepo()
    # B 의 entry (id=b-secret). A 가 그 node_id 로 수정 시도.
    await _seed_personal(pkm_repo, "user-B", "b-secret", "B 의 비밀 톤", locked=False)

    with pytest.raises(Exception) as exc_info:
        await _curate_pkm_patch(
            "pkm:b-secret", MePkmPatchRequest(content="해킹 시도"), "user-A",
            pkm_repo=pkm_repo, brand_repo=BrandRepo(), brand_memory_repo=BrandMemoryRepo(),
        )
    assert getattr(exc_info.value, "status_code", None) == 404
    # ★ B 데이터 불변.
    assert pkm_repo.store["user-B"][0]["content"] == "B 의 비밀 톤"


@pytest.mark.asyncio
async def test_delete_personal_cross_user_blocked() -> None:
    """user A 가 user B 의 개인 PKM 삭제 시도 → 404, B 데이터 불변."""
    pkm_repo = PkmRepo()
    await _seed_personal(pkm_repo, "user-B", "b-secret", "B 의 비밀 톤")

    with pytest.raises(Exception) as exc_info:
        await _curate_pkm_delete(
            "pkm:b-secret", "user-A",
            pkm_repo=pkm_repo, brand_repo=BrandRepo(), brand_memory_repo=BrandMemoryRepo(),
        )
    assert getattr(exc_info.value, "status_code", None) == 404
    assert len(pkm_repo.store["user-B"]) == 1  # 불변


@pytest.mark.asyncio
async def test_patch_brand_cross_user_blocked() -> None:
    """user A 가 user B 소유 브랜드 PKM 수정 시도 → 404 (미소유), B 데이터 불변."""
    brand_repo, bm_repo = BrandRepo(), BrandMemoryRepo()
    # B 의 brand + 브랜드 PKM (id=b-secret). A 는 자기 brand 없음.
    _, b_brand = await _seed_brand(brand_repo, bm_repo, "user-B", "b-secret", "B 브랜드 비밀")

    with pytest.raises(Exception) as exc_info:
        await _curate_pkm_patch(
            "bm:b-secret", MePkmPatchRequest(content="해킹 시도"), "user-A",
            pkm_repo=PkmRepo(), brand_repo=brand_repo, brand_memory_repo=bm_repo,
        )
    assert getattr(exc_info.value, "status_code", None) == 404
    # ★ B 브랜드 PKM 불변.
    assert bm_repo.store[b_brand][0]["content"] == "B 브랜드 비밀"


@pytest.mark.asyncio
async def test_delete_brand_cross_user_blocked() -> None:
    """user A 가 user B 소유 브랜드 PKM 삭제 시도 → 404, B 데이터 불변."""
    brand_repo, bm_repo = BrandRepo(), BrandMemoryRepo()
    _, b_brand = await _seed_brand(brand_repo, bm_repo, "user-B", "b-secret", "B 브랜드 비밀")

    with pytest.raises(Exception) as exc_info:
        await _curate_pkm_delete(
            "bm:b-secret", "user-A",
            pkm_repo=PkmRepo(), brand_repo=brand_repo, brand_memory_repo=bm_repo,
        )
    assert getattr(exc_info.value, "status_code", None) == 404
    assert len(bm_repo.store[b_brand]) == 1  # 불변


# ─── 5. unknown node_id / non-pkm prefix → 404 ────────────────────────


@pytest.mark.asyncio
async def test_patch_unknown_node_404() -> None:
    """존재하지 않는 개인 PKM id → 404."""
    with pytest.raises(Exception) as exc_info:
        await _curate_pkm_patch(
            "pkm:nope", MePkmPatchRequest(locked=True), "user-A",
            pkm_repo=PkmRepo(), brand_repo=BrandRepo(), brand_memory_repo=BrandMemoryRepo(),
        )
    assert getattr(exc_info.value, "status_code", None) == 404


@pytest.mark.asyncio
async def test_patch_non_pkm_prefix_404() -> None:
    """user:/brand: 등 큐레이션 대상 아닌 네임스페이스 → 404."""
    for nid in ("user:user-A", "brand:b1", "weird"):
        with pytest.raises(Exception) as exc_info:
            await _curate_pkm_patch(
                nid, MePkmPatchRequest(locked=True), "user-A",
                pkm_repo=PkmRepo(), brand_repo=BrandRepo(), brand_memory_repo=BrandMemoryRepo(),
            )
        assert getattr(exc_info.value, "status_code", None) == 404


@pytest.mark.asyncio
async def test_delete_unknown_node_404() -> None:
    """존재하지 않는 브랜드 PKM id → 404 (소유 검증 실패)."""
    with pytest.raises(Exception) as exc_info:
        await _curate_pkm_delete(
            "bm:nope", "user-A",
            pkm_repo=PkmRepo(), brand_repo=BrandRepo(), brand_memory_repo=BrandMemoryRepo(),
        )
    assert getattr(exc_info.value, "status_code", None) == 404


# ─── 6. graceful — repo raise → 404, 500 X ────────────────────────────


@pytest.mark.asyncio
async def test_patch_graceful_on_repo_error() -> None:
    """PkmRepo.update_entry 가 raise → 엔드포인트는 안전(404), 500 없음."""

    class _BoomPkmRepo:
        async def update_entry(self, *a: Any, **k: Any) -> Any:
            raise RuntimeError("pkm down")

    with pytest.raises(Exception) as exc_info:
        await _curate_pkm_patch(
            "pkm:p1", MePkmPatchRequest(locked=True), "user-A",
            pkm_repo=_BoomPkmRepo(),  # type: ignore[arg-type]
            brand_repo=BrandRepo(), brand_memory_repo=BrandMemoryRepo(),
        )
    # update_entry 자체는 graceful(None) 이어야 하지만 여기선 raise 대역 — 안전 매핑 확인.
    assert getattr(exc_info.value, "status_code", None) == 404


@pytest.mark.asyncio
async def test_patch_brand_graceful_on_brand_list_error() -> None:
    """소유 검증용 brand_repo 가 raise → 미소유 처리(404), 500 없음."""

    class _BoomBrandRepo:
        async def list_for_user(self, *a: Any, **k: Any) -> Any:
            raise RuntimeError("brand down")

    with pytest.raises(Exception) as exc_info:
        await _curate_pkm_patch(
            "bm:b1", MePkmPatchRequest(locked=True), "user-A",
            pkm_repo=PkmRepo(),
            brand_repo=_BoomBrandRepo(),  # type: ignore[arg-type]
            brand_memory_repo=BrandMemoryRepo(),
        )
    assert getattr(exc_info.value, "status_code", None) == 404


# ─── 7. HTTP 경로 — 익명 → 401 ────────────────────────────────────────


def test_patch_anonymous_returns_401() -> None:
    """토큰 없음(익명) PATCH → 401."""
    client = TestClient(app)
    r = client.patch("/api/v1/me/pkm/pkm:p1", json={"locked": True})
    assert r.status_code == 401


def test_delete_anonymous_returns_401() -> None:
    """토큰 없음(익명) DELETE → 401."""
    client = TestClient(app)
    r = client.delete("/api/v1/me/pkm/pkm:p1")
    assert r.status_code == 401


# ─── 8. HTTP 경로 (dev_auth_mock 쿠키) — end-to-end PATCH 잠금 ─────────


def test_patch_http_authed_lock_toggle(monkeypatch: pytest.MonkeyPatch) -> None:
    """dev_auth_mock + mock-token 쿠키 → mock-user-1 의 개인 PKM 잠금 토글 (HTTP wired)."""
    _config_module.get_settings.cache_clear()
    settings = _config_module.get_settings()
    monkeypatch.setattr(settings, "dev_auth_mock", True, raising=False)
    monkeypatch.setattr(_db_client_module, "get_supabase", lambda: None)
    monkeypatch.setattr("backend.fastapi.routers.auth.get_supabase", lambda: None)

    import asyncio

    pkm_repo = PkmRepo()
    asyncio.run(_seed_personal(pkm_repo, "mock-user-1", "p1", "토글 대상", locked=False))
    monkeypatch.setattr(me_router, "_pkm_repo", pkm_repo)
    monkeypatch.setattr(me_router, "_brand_repo", BrandRepo())
    monkeypatch.setattr(me_router, "_brand_memory_repo", BrandMemoryRepo())

    client = TestClient(app)
    client.cookies.set("sb_access_token", "mock-token")
    r = client.patch("/api/v1/me/pkm/pkm:p1", json={"locked": True})
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert data["node"]["locked"] is True
    assert pkm_repo.store["mock-user-1"][0]["is_user_locked"] is True


def test_pkm_curation_endpoints_in_openapi() -> None:
    """Phase 19 S4 PATCH/DELETE 가 OpenAPI 문서에 노출."""
    client = TestClient(app)
    r = client.get("/openapi.json")
    assert r.status_code == 200
    path_item = r.json().get("paths", {}).get("/api/v1/me/pkm/{node_id}", {})
    assert "patch" in path_item
    assert "delete" in path_item
