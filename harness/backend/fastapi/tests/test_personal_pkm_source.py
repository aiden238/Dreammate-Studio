"""Phase 26 S2 — 개인 PKM 출처(provenance) — source_plan_id → graph sourced_from 엣지 테스트.

브랜드 PKM(brand_memory_entries)은 이미 source_plan_id + /me/pkm-graph 의 source 노드/sourced_from
엣지(Phase 21)를 가진다. 본 슬라이스는 그 **개인 scope 대칭** 을 추가한다:
  - PkmRepo.add_entry 가 source_plan_id 를 받아 row/list 에 보존.
  - 추출 hook 이 confidence≥0.9 후보를 적재할 때 source_plan_id = plan_id 기록.
  - /me/pkm-graph 가 개인 PKM 의 source_plan_id → source: 노드 + (pkm→source) sourced_from 엣지
    (브랜드 PKM 과 동일 로직·공유 dedup → 같은 plan 출처면 source 노드 1개).

검증 축:
  1. repo — add_entry(source_plan_id=...) → row 에 보존 + list_for_user 가 반환.
  2. hook — flag ON + 명시 사유 피드백 → 적재된 개인 PKM 의 source_plan_id == plan_id.
  3. graph — 개인 PKM 에 source_plan_id → source 노드 + sourced_from 엣지(개인 pkm→source) +
     같은 plan_id 브랜드 PKM 과 dedup(노드 1개, summary.sources 합산).
  4. ★ graceful/byte-identical — source_plan_id 없는 개인 PKM → source 노드/엣지 0 (이전과 동일).

★ mock — 실 Supabase 0 (in-memory repos). DI seam 으로 _aggregate_pkm_graph /
  _run_personal_pkm_extract_hook 를 직접 호출 (test_pkm_graph_depth / test_personal_pkm_extract_wiring 패턴).
"""

from __future__ import annotations

import pytest

from backend.fastapi.config import get_settings
from backend.fastapi.db import BrandMemoryRepo, BrandRepo, DomainRepo, PkmRepo, SeriesRepo
from backend.fastapi.db.repositories.feedback_repo import FeedbackRepo
from backend.fastapi.db.repositories.selection_repo import SelectionRepo
from backend.fastapi.routers.me import _aggregate_pkm_graph
from backend.fastapi.routers.plans import _run_personal_pkm_extract_hook


# ─── 1. repo — add_entry(source_plan_id) round-trip ────────────────────


@pytest.mark.asyncio
async def test_add_entry_persists_source_plan_id() -> None:
    """★ add_entry(source_plan_id=...) → row 에 보존 + list_for_user 가 반환."""
    repo = PkmRepo()
    row = await repo.add_entry(
        "u-1", "preferred_tone", "출처 있는 톤", source_plan_id="plan-abc-123",
    )
    assert row["source_plan_id"] == "plan-abc-123"

    entries = await repo.list_for_user("u-1", scope="personal")
    assert len(entries) == 1
    assert entries[0]["source_plan_id"] == "plan-abc-123"


@pytest.mark.asyncio
async def test_add_entry_source_plan_id_defaults_none() -> None:
    """★ source_plan_id 미전달(기존 호출자) → None (byte-identical, 출처 미기록)."""
    repo = PkmRepo()
    row = await repo.add_entry("u-1", "preferred_tone", "출처 없는 톤")
    assert row["source_plan_id"] is None


# ─── 2. hook — 적재된 개인 PKM 이 source_plan_id == plan_id 기록 ─────────


def _set_extract_flag(monkeypatch: pytest.MonkeyPatch, enabled: bool) -> None:
    """settings.personal_pkm_extract_enabled 토글 + lru_cache 무효화 (wiring 테스트 패턴)."""
    monkeypatch.setenv("PERSONAL_PKM_EXTRACT_ENABLED", "true" if enabled else "false")
    get_settings.cache_clear()
    assert get_settings().personal_pkm_extract_enabled is enabled


@pytest.mark.asyncio
async def test_extract_hook_records_source_plan_id(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """★ flag ON + 명시 사유 피드백 → 적재된 개인 PKM 의 source_plan_id == plan_id."""
    _set_extract_flag(monkeypatch, True)
    fb = FeedbackRepo(supabase_client=None, in_memory_store={})
    sel = SelectionRepo(supabase_client=None, in_memory_store={})
    pkm = PkmRepo(supabase_client=None, in_memory_store={})

    # 명시 사유 동반 부정 신호 → confidence 0.9 (명시 선호) → 영속화 대상.
    await fb.record("plan-src-1", "dislike", reason="너무 과장된 톤은 피해주세요")

    await _run_personal_pkm_extract_hook(
        "plan-src-1", "u-src",
        feedback_repo=fb, selection_repo=sel, pkm_repo=pkm,
    )

    entries = await pkm.list_for_user("u-src", scope="personal")
    assert len(entries) >= 1
    # ★ 적재된 모든 개인 PKM 이 추출 출처 plan_id 를 기록.
    assert all(e["source_plan_id"] == "plan-src-1" for e in entries)


# ─── 3. graph — 개인 PKM source 노드 + sourced_from 엣지 + 브랜드 dedup ──


@pytest.mark.asyncio
async def test_pkm_graph_personal_source_edge() -> None:
    """개인 PKM 에 source_plan_id → source: 노드 + (개인 pkm→source) sourced_from 엣지."""
    uid = "user-A"
    pkm_repo = PkmRepo()
    brand_repo = BrandRepo()
    brand_memory_repo = BrandMemoryRepo()

    await pkm_repo.add_entry(
        uid, "preferred_tone", "출처 있는 개인 톤", source_plan_id="plan-personal-1",
    )

    resp = await _aggregate_pkm_graph(
        uid,
        pkm_repo=pkm_repo,
        brand_repo=brand_repo,
        brand_memory_repo=brand_memory_repo,
        domain_repo=DomainRepo(),
        series_repo=SeriesRepo(),
    )

    source_nodes = [n for n in resp.nodes if n.type == "source"]
    sourced_from = [e for e in resp.edges if e.kind == "sourced_from"]

    assert len(source_nodes) == 1
    assert source_nodes[0].id == "source:plan-personal-1"
    assert len(sourced_from) == 1
    # ★ 엣지 출발은 개인 pkm 노드(pkm: 접두), 도착은 source 노드.
    assert sourced_from[0].source.startswith("pkm:")
    assert sourced_from[0].target == "source:plan-personal-1"
    assert resp.summary.sources == 1


@pytest.mark.asyncio
async def test_pkm_graph_personal_and_brand_source_dedup() -> None:
    """★ 개인 PKM + 브랜드 PKM 이 같은 plan 출처 → source 노드 1개(dedup) + sourced_from 엣지 2.

    summary.sources 가 개인·브랜드 출처를 함께(공유 source_ids) 카운트.
    """
    uid = "user-A"
    pkm_repo = PkmRepo()
    brand_repo = BrandRepo()
    brand_memory_repo = BrandMemoryRepo()

    shared_plan = "plan-shared-9999"
    # 개인 + 브랜드 PKM 둘 다 같은 plan 출처.
    await pkm_repo.add_entry(
        uid, "preferred_tone", "개인 톤", source_plan_id=shared_plan,
    )
    brand_id = await brand_repo.get_or_create_default(uid, name="내 브랜드")
    assert brand_id
    await brand_memory_repo.add_entry(
        brand_id, "preferred_phrase", "브랜드 표현", source_plan_id=shared_plan,
    )

    resp = await _aggregate_pkm_graph(
        uid,
        pkm_repo=pkm_repo,
        brand_repo=brand_repo,
        brand_memory_repo=brand_memory_repo,
        domain_repo=DomainRepo(),
        series_repo=SeriesRepo(),
    )

    source_nodes = [n for n in resp.nodes if n.type == "source"]
    sourced_from = [e for e in resp.edges if e.kind == "sourced_from"]

    # ★ source 노드 1개 (개인+브랜드 dedup), sourced_from 엣지 2개 (개인 pkm + 브랜드 bm).
    assert len(source_nodes) == 1
    assert source_nodes[0].id == f"source:{shared_plan}"
    assert len(sourced_from) == 2
    assert all(e.target == f"source:{shared_plan}" for e in sourced_from)
    # 한 엣지는 개인(pkm:), 한 엣지는 브랜드(bm:) 에서 출발.
    sources = {e.source.split(":")[0] for e in sourced_from}
    assert sources == {"pkm", "bm"}
    # summary.sources 는 공유 dedup → 1 (개인·브랜드 합산이되 같은 plan 이라 1).
    assert resp.summary.sources == 1


# ─── 4. ★ graceful/byte-identical — 출처 없는 개인 PKM → source 0 ────────


@pytest.mark.asyncio
async def test_pkm_graph_personal_no_source_is_identical() -> None:
    """★ source_plan_id 없는 개인 PKM → source 노드/엣지 0 (이전과 byte-identical)."""
    uid = "user-A"
    pkm_repo = PkmRepo()
    brand_repo = BrandRepo()
    brand_memory_repo = BrandMemoryRepo()

    # 출처 없는 개인 PKM (source_plan_id 미전달).
    await pkm_repo.add_entry(uid, "preferred_tone", "출처 없는 개인 톤")

    resp = await _aggregate_pkm_graph(
        uid,
        pkm_repo=pkm_repo,
        brand_repo=brand_repo,
        brand_memory_repo=brand_memory_repo,
        domain_repo=DomainRepo(),
        series_repo=SeriesRepo(),
    )

    types = {n.type for n in resp.nodes}
    kinds = {e.kind for e in resp.edges}

    # ★ source 노드/엣지 0 — user + 개인 pkm 만.
    assert "source" not in types
    assert "sourced_from" not in kinds
    # 노드: user 1 + 개인 pkm 1 = 2 (출처/brand 없음).
    assert len(resp.nodes) == 2
    assert resp.summary.sources == 0
    assert resp.summary.personal == 1
