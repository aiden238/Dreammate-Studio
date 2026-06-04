"""Phase 26 Slice S1 — Video CRUD(/me/videos) 엔드포인트 + pkm-graph 깊이 테스트 (mock, CI-safe).

대상 (Phase 22/24 Domain/Series CRUD 를 한 단계 아래 series→video 로 복제, 4계층 완성):
  - POST   /api/v1/me/videos               {series_id, title} → 본인 series 아래 video 생성.
  - PATCH  /api/v1/me/videos/{video_id}     {title}           → 본인 video 제목 변경.
  - DELETE /api/v1/me/videos/{video_id}                       → video 삭제.

검증 축:
  1. 소유 series 아래 video 생성 → ok + video.id, VideoProjectRepo.list_for_series 즉시 반영 +
     /me/pkm-graph 가 video 노드 + has_video 엣지 + summary.videos 자동 반영(Phase 21 집계 불변).
  2. PATCH title / DELETE video → 반영 (list + graph).
  3. ★ RLS — 다른 user 의 series 아래 video 생성 / 다른 user 의 video 편집·삭제 → 404 (대상 불변).
  4. 익명(토큰 없음) HTTP → 401.
  5. 빈 title → 422 (Pydantic min_length).
  6. graceful — repo create None/raise / update None / delete False/raise → unhandled 500 없음
     (create 503, update/delete 404 controlled).
  7. ★ graceful/byte-identical — brand+domain+series 있으나 video 0 → graph 가 Phase 24 와
     동일(video 노드/has_video 엣지 0, summary.videos==0).

★ mock — 실 Supabase 0 (in-memory repos). DI seam(_create_video/_update_video/_delete_video)으로
   직접 호출하거나, TestClient + dev_auth_mock 쿠키로 HTTP 경로(401/422/200)를 탄다.
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
    VideoProjectRepo,
)
from backend.fastapi.db import client as _db_client_module
from backend.fastapi.main import app
from backend.fastapi.routers import me as me_router
from backend.fastapi.routers.me import (
    _aggregate_pkm_graph,
    _create_video,
    _delete_video,
    _update_video,
)
from backend.fastapi.schemas.graph import (
    MeVideoCreateRequest,
    MeVideoUpdateRequest,
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
    """소유 brand 1 + domain 1 시드 → (brand_id, domain_id) 반환."""
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


async def _seed_video(
    brand_repo: BrandRepo,
    domain_repo: DomainRepo,
    series_repo: SeriesRepo,
    video_repo: VideoProjectRepo,
    auth_user_id: str,
) -> tuple[str, str, str, str]:
    """소유 brand 1 + domain 1 + series 1 + video 1 시드 → (brand, domain, series, video) 반환."""
    brand_id, domain_id, series_id = await _seed_series(
        brand_repo, domain_repo, series_repo, auth_user_id,
    )
    row = await video_repo.create(series_id, "내 영상", auth_user_id)
    assert row and row.get("id")
    return brand_id, domain_id, series_id, str(row["id"])


# ─── 1. 소유 series 아래 video 생성 → ok + list + graph 반영 ───────────


@pytest.mark.asyncio
async def test_create_video_under_owned_series() -> None:
    """소유 series 아래 video 생성 → ok, id 있음, list_for_series 즉시 포함."""
    uid = "user-A"
    brand_repo, domain_repo, series_repo, video_repo = (
        BrandRepo(), DomainRepo(), SeriesRepo(), VideoProjectRepo(),
    )
    _, _domain_id, series_id = await _seed_series(brand_repo, domain_repo, series_repo, uid)

    resp = await _create_video(
        MeVideoCreateRequest(series_id=series_id, title="오프닝 영상"), uid,
        brand_repo=brand_repo, domain_repo=domain_repo,
        series_repo=series_repo, video_repo=video_repo,
    )
    assert resp.ok is True
    assert resp.video.id
    assert resp.video.series_id == series_id
    assert resp.video.title == "오프닝 영상"

    # ★ VideoProjectRepo.list_for_series 즉시 반영.
    videos = await video_repo.list_for_series(series_id)
    assert any(v.get("id") == resp.video.id for v in videos)
    assert any(v.get("title") == "오프닝 영상" for v in videos)
    # ★ auth_user_id 가 row 에 동봉 (video_projects.auth_user_id NOT NULL).
    assert any(v.get("auth_user_id") == uid for v in videos)


@pytest.mark.asyncio
async def test_created_video_appears_in_pkm_graph() -> None:
    """brand→domain→series→video 생성 후 /me/pkm-graph 가 video 노드 + has_video 엣지 자동 반영.

    ★ Phase 21 집계를 전혀 변경하지 않고도 생성된 video 행이 graph 에 펼쳐짐을 확인.
    """
    uid = "user-A"
    pkm_repo = PkmRepo()
    brand_repo, domain_repo, series_repo, video_repo = (
        BrandRepo(), DomainRepo(), SeriesRepo(), VideoProjectRepo(),
    )
    brand_memory_repo = BrandMemoryRepo()

    _, _domain_id, series_id = await _seed_series(brand_repo, domain_repo, series_repo, uid)
    v = await _create_video(
        MeVideoCreateRequest(series_id=series_id, title="주간 리뷰 1화"), uid,
        brand_repo=brand_repo, domain_repo=domain_repo,
        series_repo=series_repo, video_repo=video_repo,
    )

    graph = await _aggregate_pkm_graph(
        uid,
        pkm_repo=pkm_repo,
        brand_repo=brand_repo,
        brand_memory_repo=brand_memory_repo,
        domain_repo=domain_repo,
        series_repo=series_repo,
        video_repo=video_repo,
    )

    node_ids = {n.id for n in graph.nodes}
    assert f"series:{series_id}" in node_ids
    assert f"video:{v.video.id}" in node_ids
    # video 노드 라벨 = title 패스스루.
    video_nodes = [n for n in graph.nodes if n.type == "video"]
    assert len(video_nodes) == 1
    assert video_nodes[0].label == "주간 리뷰 1화"
    # 엣지 — series → video (has_video).
    has_video = [e for e in graph.edges if e.kind == "has_video"]
    assert len(has_video) == 1
    assert has_video[0].source == f"series:{series_id}"
    assert has_video[0].target == f"video:{v.video.id}"
    # summary.videos 카운트.
    assert graph.summary.videos == 1


# ─── 2. PATCH title / DELETE video → 반영 ─────────────────────────────


@pytest.mark.asyncio
async def test_update_video_under_owned_series() -> None:
    """소유 video 제목 변경 → ok, title 변경, list_for_series 즉시 반영."""
    uid = "user-A"
    brand_repo, domain_repo, series_repo, video_repo = (
        BrandRepo(), DomainRepo(), SeriesRepo(), VideoProjectRepo(),
    )
    _, _domain_id, series_id, video_id = await _seed_video(
        brand_repo, domain_repo, series_repo, video_repo, uid,
    )

    resp = await _update_video(
        video_id, MeVideoUpdateRequest(title="오프닝 영상(수정)"), uid,
        brand_repo=brand_repo, domain_repo=domain_repo,
        series_repo=series_repo, video_repo=video_repo,
    )
    assert resp.ok is True
    assert resp.video.id == video_id
    assert resp.video.title == "오프닝 영상(수정)"

    videos = await video_repo.list_for_series(series_id)
    assert any(v.get("id") == video_id and v.get("title") == "오프닝 영상(수정)" for v in videos)


@pytest.mark.asyncio
async def test_delete_video_under_owned_series() -> None:
    """소유 video 삭제 → ok, list_for_series 에서 제거."""
    uid = "user-A"
    brand_repo, domain_repo, series_repo, video_repo = (
        BrandRepo(), DomainRepo(), SeriesRepo(), VideoProjectRepo(),
    )
    _, _domain_id, series_id, video_id = await _seed_video(
        brand_repo, domain_repo, series_repo, video_repo, uid,
    )

    resp = await _delete_video(
        video_id, uid,
        brand_repo=brand_repo, domain_repo=domain_repo,
        series_repo=series_repo, video_repo=video_repo,
    )
    assert resp.ok is True
    assert resp.deleted is True
    assert await video_repo.list_for_series(series_id) == []
    # in-memory store 전체에 그 video_id 가 남지 않음.
    assert all(
        v.get("id") != video_id
        for rows in video_repo.store.values()
        for v in rows
    )


# ─── 3. ★ RLS — 다른 user 의 series/video CRUD → 404 (대상 불변) ───────


@pytest.mark.asyncio
async def test_create_video_under_not_owned_series_404() -> None:
    """user A 가 user B 소유 series 아래 video 생성 시도 → 404, B series 에 video 0."""
    brand_repo, domain_repo, series_repo, video_repo = (
        BrandRepo(), DomainRepo(), SeriesRepo(), VideoProjectRepo(),
    )
    _, _b_domain, b_series = await _seed_series(brand_repo, domain_repo, series_repo, "user-B")

    with pytest.raises(Exception) as exc_info:
        await _create_video(
            MeVideoCreateRequest(series_id=b_series, title="침투 영상"), "user-A",
            brand_repo=brand_repo, domain_repo=domain_repo,
            series_repo=series_repo, video_repo=video_repo,
        )
    assert getattr(exc_info.value, "status_code", None) == 404
    # ★ B series 아래 video 생성 0.
    assert await video_repo.list_for_series(b_series) == []


@pytest.mark.asyncio
async def test_create_video_under_nonexistent_series_404() -> None:
    """존재하지 않는 series_id 아래 video → 404 (소유 검증 실패)."""
    brand_repo, domain_repo, series_repo, video_repo = (
        BrandRepo(), DomainRepo(), SeriesRepo(), VideoProjectRepo(),
    )
    await _seed_brand(brand_repo, "user-A")  # A 는 brand 만 (series 없음).

    with pytest.raises(Exception) as exc_info:
        await _create_video(
            MeVideoCreateRequest(series_id="nope-series", title="유령 영상"), "user-A",
            brand_repo=brand_repo, domain_repo=domain_repo,
            series_repo=series_repo, video_repo=video_repo,
        )
    assert getattr(exc_info.value, "status_code", None) == 404


@pytest.mark.asyncio
async def test_update_other_users_video_404_target_unchanged() -> None:
    """user A 가 user B 소유 video 제목 변경 시도 → 404, B video title 불변."""
    brand_repo, domain_repo, series_repo, video_repo = (
        BrandRepo(), DomainRepo(), SeriesRepo(), VideoProjectRepo(),
    )
    _, _b_domain, b_series, b_video = await _seed_video(
        brand_repo, domain_repo, series_repo, video_repo, "user-B",
    )

    with pytest.raises(Exception) as exc_info:
        await _update_video(
            b_video, MeVideoUpdateRequest(title="침투(수정)"), "user-A",
            brand_repo=brand_repo, domain_repo=domain_repo,
            series_repo=series_repo, video_repo=video_repo,
        )
    assert getattr(exc_info.value, "status_code", None) == 404
    videos = await video_repo.list_for_series(b_series)
    assert any(v.get("id") == b_video and v.get("title") == "내 영상" for v in videos)


@pytest.mark.asyncio
async def test_delete_other_users_video_404_target_unchanged() -> None:
    """user A 가 user B 소유 video 삭제 시도 → 404, B video 존속."""
    brand_repo, domain_repo, series_repo, video_repo = (
        BrandRepo(), DomainRepo(), SeriesRepo(), VideoProjectRepo(),
    )
    _, _b_domain, b_series, b_video = await _seed_video(
        brand_repo, domain_repo, series_repo, video_repo, "user-B",
    )

    with pytest.raises(Exception) as exc_info:
        await _delete_video(
            b_video, "user-A",
            brand_repo=brand_repo, domain_repo=domain_repo,
            series_repo=series_repo, video_repo=video_repo,
        )
    assert getattr(exc_info.value, "status_code", None) == 404
    assert any(v.get("id") == b_video for v in await video_repo.list_for_series(b_series))


# ─── 4. 익명 HTTP → 401 ───────────────────────────────────────────────


def test_create_video_anonymous_returns_401() -> None:
    """토큰 없음(익명) POST /me/videos → 401."""
    client = TestClient(app)
    r = client.post("/api/v1/me/videos", json={"series_id": "s1", "title": "x"})
    assert r.status_code == 401


def test_update_video_anonymous_returns_401() -> None:
    """토큰 없음(익명) PATCH /me/videos/{id} → 401."""
    client = TestClient(app)
    r = client.patch("/api/v1/me/videos/v1", json={"title": "x"})
    assert r.status_code == 401


def test_delete_video_anonymous_returns_401() -> None:
    """토큰 없음(익명) DELETE /me/videos/{id} → 401."""
    client = TestClient(app)
    r = client.delete("/api/v1/me/videos/v1")
    assert r.status_code == 401


# ─── 5. 빈 title → 422 (Pydantic min_length) ─────────────────────────


def test_create_video_empty_title_422() -> None:
    """빈 title → 422 (인증 무관 — Pydantic 검증이 먼저)."""
    client = TestClient(app)
    r = client.post("/api/v1/me/videos", json={"series_id": "s1", "title": ""})
    assert r.status_code == 422


def test_update_video_empty_title_422(monkeypatch: pytest.MonkeyPatch) -> None:
    """빈 title → 422 (Pydantic 검증). dev_auth_mock 쿠키로 인증 통과 후 본문 검증."""
    _config_module.get_settings.cache_clear()
    settings = _config_module.get_settings()
    monkeypatch.setattr(settings, "dev_auth_mock", True, raising=False)
    monkeypatch.setattr(_db_client_module, "get_supabase", lambda: None)
    monkeypatch.setattr("backend.fastapi.routers.auth.get_supabase", lambda: None)

    client = TestClient(app)
    client.cookies.set("sb_access_token", "mock-token")
    r = client.patch("/api/v1/me/videos/v1", json={"title": ""})
    assert r.status_code == 422


# ─── 6. graceful — repo None / False / raise → unhandled 500 없음 ─────


@pytest.mark.asyncio
async def test_create_video_repo_none_no_unhandled_500() -> None:
    """video_repo.create 가 None 반환 → unhandled 500 아님, 503 controlled."""
    uid = "user-A"
    brand_repo, domain_repo, series_repo = BrandRepo(), DomainRepo(), SeriesRepo()
    _, _domain_id, series_id = await _seed_series(brand_repo, domain_repo, series_repo, uid)

    class _NoneVideoRepo:
        async def create(self, *a: Any, **k: Any) -> Any:
            return None

    with pytest.raises(Exception) as exc_info:
        await _create_video(
            MeVideoCreateRequest(series_id=series_id, title="실패 영상"), uid,
            brand_repo=brand_repo, domain_repo=domain_repo,
            series_repo=series_repo, video_repo=_NoneVideoRepo(),  # type: ignore[arg-type]
        )
    assert getattr(exc_info.value, "status_code", None) == 503


@pytest.mark.asyncio
async def test_create_video_repo_raise_no_unhandled_500() -> None:
    """video_repo.create 가 raise → endpoint 안전(503), unhandled 500 없음."""
    uid = "user-A"
    brand_repo, domain_repo, series_repo = BrandRepo(), DomainRepo(), SeriesRepo()
    _, _domain_id, series_id = await _seed_series(brand_repo, domain_repo, series_repo, uid)

    class _BoomVideoRepo:
        async def create(self, *a: Any, **k: Any) -> Any:
            raise RuntimeError("videos down")

    with pytest.raises(Exception) as exc_info:
        await _create_video(
            MeVideoCreateRequest(series_id=series_id, title="폭발 영상"), uid,
            brand_repo=brand_repo, domain_repo=domain_repo,
            series_repo=series_repo, video_repo=_BoomVideoRepo(),  # type: ignore[arg-type]
        )
    assert getattr(exc_info.value, "status_code", None) == 503


@pytest.mark.asyncio
async def test_update_video_repo_none_no_unhandled_500() -> None:
    """video_repo.update_title 이 None 반환(미존재) → unhandled 500 아님, 404 controlled."""
    uid = "user-A"
    brand_repo, domain_repo, series_repo, video_repo = (
        BrandRepo(), DomainRepo(), SeriesRepo(), VideoProjectRepo(),
    )
    _, _domain_id, _series_id, video_id = await _seed_video(
        brand_repo, domain_repo, series_repo, video_repo, uid,
    )

    class _NoneUpdateVideoRepo(VideoProjectRepo):
        async def update_title(self, *a: Any, **k: Any) -> Any:
            return None

    none_repo = _NoneUpdateVideoRepo(in_memory_store=video_repo.store)

    with pytest.raises(Exception) as exc_info:
        await _update_video(
            video_id, MeVideoUpdateRequest(title="실패"), uid,
            brand_repo=brand_repo, domain_repo=domain_repo,
            series_repo=series_repo, video_repo=none_repo,
        )
    assert getattr(exc_info.value, "status_code", None) == 404


@pytest.mark.asyncio
async def test_delete_video_repo_raise_no_unhandled_500() -> None:
    """video_repo.delete 가 raise → endpoint 안전(404), unhandled 500 없음."""
    uid = "user-A"
    brand_repo, domain_repo, series_repo, video_repo = (
        BrandRepo(), DomainRepo(), SeriesRepo(), VideoProjectRepo(),
    )
    _, _domain_id, _series_id, video_id = await _seed_video(
        brand_repo, domain_repo, series_repo, video_repo, uid,
    )

    class _BoomDeleteVideoRepo(VideoProjectRepo):
        async def delete(self, *a: Any, **k: Any) -> Any:
            raise RuntimeError("videos down")

    boom_repo = _BoomDeleteVideoRepo(in_memory_store=video_repo.store)

    with pytest.raises(Exception) as exc_info:
        await _delete_video(
            video_id, uid,
            brand_repo=brand_repo, domain_repo=domain_repo,
            series_repo=series_repo, video_repo=boom_repo,
        )
    assert getattr(exc_info.value, "status_code", None) == 404


# ─── 7. ★ graceful/byte-identical — video 0 → Phase 24 동일 graph ─────


@pytest.mark.asyncio
async def test_pkm_graph_no_video_is_phase24_identical() -> None:
    """brand+domain+series 있으나 video 0 → video 노드/has_video 엣지 0, summary.videos==0.

    ★ Phase 24 graph 와 byte-identical (video_repo 미주입 default 빈 store 와 동일 결과).
    """
    uid = "user-A"
    pkm_repo = PkmRepo()
    brand_repo, domain_repo, series_repo, video_repo = (
        BrandRepo(), DomainRepo(), SeriesRepo(), VideoProjectRepo(),
    )
    brand_memory_repo = BrandMemoryRepo()
    await _seed_series(brand_repo, domain_repo, series_repo, uid)

    # video_repo 주입(빈 store) — 결과는 Phase 24 와 동일해야.
    resp_with = await _aggregate_pkm_graph(
        uid,
        pkm_repo=pkm_repo,
        brand_repo=brand_repo,
        brand_memory_repo=brand_memory_repo,
        domain_repo=domain_repo,
        series_repo=series_repo,
        video_repo=video_repo,
    )

    types = {n.type for n in resp_with.nodes}
    kinds = {e.kind for e in resp_with.edges}
    # ★ video 노드/has_video 엣지 0.
    assert "video" not in types
    assert "has_video" not in kinds
    assert resp_with.summary.videos == 0
    # domain/series 깊이는 그대로(Phase 24 동일).
    assert resp_with.summary.domains == 1
    assert resp_with.summary.series == 1


@pytest.mark.asyncio
async def test_pkm_graph_default_video_repo_no_video() -> None:
    """video_repo 미주입(모듈 싱글톤 default, 빈 store) → video 0 (graceful)."""
    uid = "user-A"
    pkm_repo = PkmRepo()
    brand_repo, domain_repo, series_repo = BrandRepo(), DomainRepo(), SeriesRepo()
    brand_memory_repo = BrandMemoryRepo()
    await _seed_series(brand_repo, domain_repo, series_repo, uid)

    # video_repo 인자를 아예 안 넘김 → 모듈 _video_repo (빈 store) 사용.
    resp = await _aggregate_pkm_graph(
        uid,
        pkm_repo=pkm_repo,
        brand_repo=brand_repo,
        brand_memory_repo=brand_memory_repo,
        domain_repo=domain_repo,
        series_repo=series_repo,
    )
    assert resp.summary.videos == 0
    assert not any(n.type == "video" for n in resp.nodes)


@pytest.mark.asyncio
async def test_pkm_graph_graceful_on_video_repo_error() -> None:
    """video repo 가 raise → 500 아님, brand/domain/series 정상, video 만 빔 (graceful)."""
    uid = "user-A"
    pkm_repo = PkmRepo()
    brand_repo, domain_repo, series_repo = BrandRepo(), DomainRepo(), SeriesRepo()
    brand_memory_repo = BrandMemoryRepo()
    await _seed_series(brand_repo, domain_repo, series_repo, uid)

    class _BoomVideoRepo:
        async def list_for_series(self, *a: Any, **k: Any) -> list[dict[str, Any]]:
            raise RuntimeError("videos down")

    resp = await _aggregate_pkm_graph(
        uid,
        pkm_repo=pkm_repo,
        brand_repo=brand_repo,
        brand_memory_repo=brand_memory_repo,
        domain_repo=domain_repo,
        series_repo=series_repo,
        video_repo=_BoomVideoRepo(),  # type: ignore[arg-type]
    )
    # domain/series 정상, video 0 (graceful).
    assert resp.summary.domains == 1
    assert resp.summary.series == 1
    assert resp.summary.videos == 0
    assert not any(n.type == "video" for n in resp.nodes)


# ─── 8. RLS — 다른 series 의 video 미포함 (graph 격리) ────────────────


@pytest.mark.asyncio
async def test_pkm_graph_video_rls_other_series_excluded() -> None:
    """A 의 series video 만 — 다른 user(B) 의 video 는 어떤 노드/엣지에도 0."""
    pkm_repo = PkmRepo()
    brand_repo, domain_repo, series_repo, video_repo = (
        BrandRepo(), DomainRepo(), SeriesRepo(), VideoProjectRepo(),
    )
    brand_memory_repo = BrandMemoryRepo()

    _, _a_domain, a_series = await _seed_series(brand_repo, domain_repo, series_repo, "user-A")
    _, _b_domain, b_series = await _seed_series(brand_repo, domain_repo, series_repo, "user-B")
    await video_repo.create(a_series, "A 영상", "user-A")
    await video_repo.create(b_series, "B 영상(노출 금지)", "user-B")

    resp = await _aggregate_pkm_graph(
        "user-A",
        pkm_repo=pkm_repo,
        brand_repo=brand_repo,
        brand_memory_repo=brand_memory_repo,
        domain_repo=domain_repo,
        series_repo=series_repo,
        video_repo=video_repo,
    )

    labels = [n.label for n in resp.nodes]
    video_nodes = [n for n in resp.nodes if n.type == "video"]
    # A 의 video 1개만.
    assert len(video_nodes) == 1
    assert video_nodes[0].label == "A 영상"
    # ★ B 의 video 노출 0.
    assert all("노출 금지" not in label for label in labels)
    assert resp.summary.videos == 1


# ─── 9. HTTP end-to-end (dev_auth_mock 쿠키) — 생성/삭제 wired ─────────


def test_create_video_http_authed_200(monkeypatch: pytest.MonkeyPatch) -> None:
    """dev_auth_mock + mock-token 쿠키 → mock-user-1 의 소유 series 아래 video 생성 200."""
    _config_module.get_settings.cache_clear()
    settings = _config_module.get_settings()
    monkeypatch.setattr(settings, "dev_auth_mock", True, raising=False)
    monkeypatch.setattr(_db_client_module, "get_supabase", lambda: None)
    monkeypatch.setattr("backend.fastapi.routers.auth.get_supabase", lambda: None)

    import asyncio

    brand_repo, domain_repo, series_repo, video_repo = (
        BrandRepo(), DomainRepo(), SeriesRepo(), VideoProjectRepo(),
    )
    _, _domain_id, series_id = asyncio.run(
        _seed_series(brand_repo, domain_repo, series_repo, "mock-user-1"),
    )
    monkeypatch.setattr(me_router, "_brand_repo", brand_repo)
    monkeypatch.setattr(me_router, "_domain_repo", domain_repo)
    monkeypatch.setattr(me_router, "_series_repo", series_repo)
    monkeypatch.setattr(me_router, "_video_repo", video_repo)

    client = TestClient(app)
    client.cookies.set("sb_access_token", "mock-token")
    r = client.post("/api/v1/me/videos", json={"series_id": series_id, "title": "HTTP 영상"})
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert data["video"]["id"]
    assert data["video"]["title"] == "HTTP 영상"
    # 생성 반영.
    assert asyncio.run(video_repo.list_for_series(series_id))


def test_delete_video_http_cross_user_404(monkeypatch: pytest.MonkeyPatch) -> None:
    """dev_auth_mock → mock-user-1 이 타인 video 삭제 시도 → 404 (HTTP wired)."""
    _config_module.get_settings.cache_clear()
    settings = _config_module.get_settings()
    monkeypatch.setattr(settings, "dev_auth_mock", True, raising=False)
    monkeypatch.setattr(_db_client_module, "get_supabase", lambda: None)
    monkeypatch.setattr("backend.fastapi.routers.auth.get_supabase", lambda: None)

    import asyncio

    brand_repo, domain_repo, series_repo, video_repo = (
        BrandRepo(), DomainRepo(), SeriesRepo(), VideoProjectRepo(),
    )
    _, _o_domain, o_series, o_video = asyncio.run(
        _seed_video(brand_repo, domain_repo, series_repo, video_repo, "other-user"),
    )
    monkeypatch.setattr(me_router, "_brand_repo", brand_repo)
    monkeypatch.setattr(me_router, "_domain_repo", domain_repo)
    monkeypatch.setattr(me_router, "_series_repo", series_repo)
    monkeypatch.setattr(me_router, "_video_repo", video_repo)

    client = TestClient(app)
    client.cookies.set("sb_access_token", "mock-token")
    r = client.delete(f"/api/v1/me/videos/{o_video}")
    assert r.status_code == 404
    # ★ 타인 video 존속.
    assert any(v.get("id") == o_video for v in asyncio.run(video_repo.list_for_series(o_series)))


def test_video_crud_endpoints_in_openapi() -> None:
    """Phase 26 S1 POST /me/videos, PATCH/DELETE /me/videos/{id} 가 OpenAPI 문서에 노출."""
    client = TestClient(app)
    r = client.get("/openapi.json")
    assert r.status_code == 200
    paths = r.json().get("paths", {})
    assert "post" in paths.get("/api/v1/me/videos", {})
    assert "patch" in paths.get("/api/v1/me/videos/{video_id}", {})
    assert "delete" in paths.get("/api/v1/me/videos/{video_id}", {})
