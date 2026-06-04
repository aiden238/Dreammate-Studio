"""Phase 21 Slice S1 — /me/pkm-graph 4계층 depth + provenance(source) 테스트 (mock, CI-safe).

검증 축:
  1. 4계층 — brand → domain → series 시드(DomainRepo/SeriesRepo 주입) → domain/series 노드 +
     has_domain/has_series 엣지 + summary.domains/series 카운트.
  2. provenance — 브랜드 PKM 에 source_plan_id 시드 → source: 노드 + sourced_from 엣지 + dedup.
  3. ★ graceful/byte-identical — brand+pkm 있고 domain/series/source 0 → user/brand/pkm 노드 +
     owns/has_personal/has_brand_pkm 엣지만 (깊이/출처 노드·엣지 0). summary.domains==series==sources==0.
     = Phase 19 동일.
  4. RLS — 다른 brand/user 의 domain 은 미포함.
  5. 익명 → 빈 그래프 (unchanged).

★ mock — 실 Supabase 0 (in-memory repos). DI seam(domain_repo/series_repo 포함)으로
   _aggregate_pkm_graph 를 직접 호출 (test_pkm_graph.py 패턴 계승).
"""

from __future__ import annotations

from typing import Any

import pytest

from backend.fastapi.db import (
    BrandMemoryRepo,
    BrandRepo,
    DomainRepo,
    PkmRepo,
    SeriesRepo,
)
from backend.fastapi.routers.me import _aggregate_pkm_graph


# ─── helpers ──────────────────────────────────────────────────────────


async def _seed_base(
    auth_user_id: str,
) -> tuple[PkmRepo, BrandRepo, BrandMemoryRepo, str]:
    """개인 pkm 1 + brand 1 + 브랜드 pkm 1 (출처 없음) 을 시드 — Phase 19 동등 base."""
    pkm_repo = PkmRepo()
    brand_repo = BrandRepo()
    brand_memory_repo = BrandMemoryRepo()

    await pkm_repo.add_entry(auth_user_id, "preferred_tone", "담백한 톤")
    brand_id = await brand_repo.get_or_create_default(auth_user_id, name="내 브랜드")
    assert brand_id
    await brand_memory_repo.add_entry(brand_id, "preferred_tone", "브랜드 톤")

    return pkm_repo, brand_repo, brand_memory_repo, brand_id


# ─── 1. 4계층 depth — domain/series 노드 + 엣지 + summary ──────────────


@pytest.mark.asyncio
async def test_pkm_graph_4layer_depth_domain_series() -> None:
    """brand → domain 2 → (domain1 에 series 2) → domain/series 노드 + has_domain/has_series."""
    uid = "user-A"
    pkm_repo, brand_repo, brand_memory_repo, brand_id = await _seed_base(uid)

    # domain 2개 (in-memory store 는 brand_id keyed).
    domain_repo = DomainRepo()
    domain_repo.store[brand_id] = [
        {"id": "dom-1", "brand_id": brand_id, "name": "도메인 1"},
        {"id": "dom-2", "brand_id": brand_id, "name": "도메인 2"},
    ]
    # series — domain_id keyed. dom-1 에 2개, dom-2 에 0개.
    series_repo = SeriesRepo()
    series_repo.store["dom-1"] = [
        {"id": "ser-1", "domain_id": "dom-1", "name": "시리즈 1"},
        {"id": "ser-2", "domain_id": "dom-1", "name": "시리즈 2"},
    ]

    resp = await _aggregate_pkm_graph(
        uid,
        pkm_repo=pkm_repo,
        brand_repo=brand_repo,
        brand_memory_repo=brand_memory_repo,
        domain_repo=domain_repo,
        series_repo=series_repo,
    )

    by_type: dict[str, list[Any]] = {}
    for n in resp.nodes:
        by_type.setdefault(n.type, []).append(n)

    # domain 2 + series 2 노드.
    assert len(by_type.get("domain", [])) == 2
    assert len(by_type.get("series", [])) == 2
    assert {n.id for n in by_type["domain"]} == {"domain:dom-1", "domain:dom-2"}
    assert {n.id for n in by_type["series"]} == {"series:ser-1", "series:ser-2"}
    # label 패스스루.
    assert {n.label for n in by_type["domain"]} == {"도메인 1", "도메인 2"}

    # 엣지 — has_domain 2 (brand → domain), has_series 2 (dom-1 → series).
    has_domain = [e for e in resp.edges if e.kind == "has_domain"]
    has_series = [e for e in resp.edges if e.kind == "has_series"]
    assert len(has_domain) == 2
    assert len(has_series) == 2
    assert all(e.source == f"brand:{brand_id}" for e in has_domain)
    assert all(e.target in {"domain:dom-1", "domain:dom-2"} for e in has_domain)
    assert all(e.source == "domain:dom-1" for e in has_series)
    assert all(e.target in {"series:ser-1", "series:ser-2"} for e in has_series)

    # summary 신규 카운트.
    assert resp.summary.domains == 2
    assert resp.summary.series == 2
    # 기존 카운트 그대로 (additive).
    assert resp.summary.personal == 1
    assert resp.summary.brands == 1
    assert resp.summary.brand == 1
    assert resp.summary.sources == 0


# ─── 2. provenance — source 노드 + sourced_from 엣지 + dedup ───────────


@pytest.mark.asyncio
async def test_pkm_graph_source_edge_provenance() -> None:
    """브랜드 PKM 2개가 같은 source_plan_id → source 노드 1개(dedup) + sourced_from 엣지 2."""
    uid = "user-A"
    pkm_repo = PkmRepo()
    brand_repo = BrandRepo()
    brand_memory_repo = BrandMemoryRepo()

    brand_id = await brand_repo.get_or_create_default(uid, name="내 브랜드")
    assert brand_id
    # 같은 plan 출처 2개 + 출처 없는 1개.
    await brand_memory_repo.add_entry(
        brand_id, "preferred_tone", "출처 있는 톤 A", source_plan_id="plan-xyz-123456",
    )
    await brand_memory_repo.add_entry(
        brand_id, "preferred_phrase", "출처 있는 표현 B", source_plan_id="plan-xyz-123456",
    )
    await brand_memory_repo.add_entry(brand_id, "avoid_phrase", "출처 없는 entry")

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

    # source 노드 1개 (dedup), sourced_from 엣지 2개 (bm 2개 → 같은 source).
    assert len(source_nodes) == 1
    assert source_nodes[0].id == "source:plan-xyz-123456"
    assert len(sourced_from) == 2
    assert all(e.target == "source:plan-xyz-123456" for e in sourced_from)
    assert all(e.source.startswith("bm:") for e in sourced_from)

    assert resp.summary.sources == 1


# ─── 3. ★ graceful/byte-identical — depth/source 0 → Phase 19 동일 ────


@pytest.mark.asyncio
async def test_pkm_graph_no_depth_is_phase19_identical() -> None:
    """brand+pkm 있으나 domain/series/source 0 → user/brand/pkm 노드 + owns/has_* 엣지만."""
    uid = "user-A"
    pkm_repo, brand_repo, brand_memory_repo, _ = await _seed_base(uid)

    resp = await _aggregate_pkm_graph(
        uid,
        pkm_repo=pkm_repo,
        brand_repo=brand_repo,
        brand_memory_repo=brand_memory_repo,
        domain_repo=DomainRepo(),  # 빈 store
        series_repo=SeriesRepo(),  # 빈 store
    )

    types = {n.type for n in resp.nodes}
    kinds = {e.kind for e in resp.edges}

    # ★ Phase 19 노드 종류만 — domain/series/source 노드 0.
    assert types == {"user", "brand", "pkm"}
    assert "domain" not in types
    assert "series" not in types
    assert "source" not in types
    # ★ Phase 19 엣지 종류만 — has_domain/has_series/sourced_from 0.
    assert kinds <= {"owns", "has_personal", "has_brand_pkm"}
    assert "has_domain" not in kinds
    assert "has_series" not in kinds
    assert "sourced_from" not in kinds

    # 노드: user 1 + 개인 pkm 1 + brand 1 + 브랜드 pkm 1 = 4 (Phase 19 동일).
    assert len(resp.nodes) == 4

    # ★ 신규 summary 카운트 전부 0 (graceful/backward-compat).
    assert resp.summary.domains == 0
    assert resp.summary.series == 0
    assert resp.summary.sources == 0


@pytest.mark.asyncio
async def test_pkm_graph_default_repos_no_depth() -> None:
    """domain_repo/series_repo 미주입(모듈 싱글톤 default, 빈 store) → 깊이 0 (graceful)."""
    uid = "user-A"
    pkm_repo, brand_repo, brand_memory_repo, _ = await _seed_base(uid)

    # domain_repo/series_repo 인자를 아예 안 넘김 → 모듈 _domain_repo/_series_repo (빈 store) 사용.
    resp = await _aggregate_pkm_graph(
        uid,
        pkm_repo=pkm_repo,
        brand_repo=brand_repo,
        brand_memory_repo=brand_memory_repo,
    )

    assert resp.summary.domains == 0
    assert resp.summary.series == 0
    assert resp.summary.sources == 0
    assert not any(n.type in {"domain", "series", "source"} for n in resp.nodes)


# ─── 4. RLS — 다른 brand 의 domain 미포함 ─────────────────────────────


@pytest.mark.asyncio
async def test_pkm_graph_depth_rls_other_brand_excluded() -> None:
    """A 의 brand domain 만 — 다른 brand(B) 의 domain 은 어떤 노드/엣지에도 0."""
    pkm_repo = PkmRepo()
    brand_repo = BrandRepo()
    brand_memory_repo = BrandMemoryRepo()

    a_brand = await brand_repo.get_or_create_default("user-A", name="A 브랜드")
    b_brand = await brand_repo.get_or_create_default("user-B", name="B 브랜드")
    assert a_brand and b_brand

    domain_repo = DomainRepo()
    # A brand 에 domain 1개, B brand 에 domain 1개(노출 금지).
    domain_repo.store[a_brand] = [{"id": "dom-A", "brand_id": a_brand, "name": "A 도메인"}]
    domain_repo.store[b_brand] = [
        {"id": "dom-B", "brand_id": b_brand, "name": "B 도메인(노출 금지)"},
    ]
    series_repo = SeriesRepo()
    series_repo.store["dom-A"] = [{"id": "ser-A", "domain_id": "dom-A", "name": "A 시리즈"}]
    series_repo.store["dom-B"] = [
        {"id": "ser-B", "domain_id": "dom-B", "name": "B 시리즈(노출 금지)"},
    ]

    resp = await _aggregate_pkm_graph(
        "user-A",
        pkm_repo=pkm_repo,
        brand_repo=brand_repo,
        brand_memory_repo=brand_memory_repo,
        domain_repo=domain_repo,
        series_repo=series_repo,
    )

    node_ids = {n.id for n in resp.nodes}
    labels = [n.label for n in resp.nodes]

    # A 의 깊이만.
    assert "domain:dom-A" in node_ids
    assert "series:ser-A" in node_ids
    # ★ B 의 domain/series 는 노출 0.
    assert "domain:dom-B" not in node_ids
    assert "series:ser-B" not in node_ids
    assert all("노출 금지" not in label for label in labels)
    # 엣지에도 B id 등장 0.
    assert all("dom-B" not in e.target and "dom-B" not in e.source for e in resp.edges)
    assert all("ser-B" not in e.target and "ser-B" not in e.source for e in resp.edges)

    assert resp.summary.domains == 1
    assert resp.summary.series == 1


# ─── 5. graceful — depth repo raise → 500 아님, 깊이만 빔 ──────────────


@pytest.mark.asyncio
async def test_pkm_graph_graceful_on_domain_repo_error() -> None:
    """domain repo 가 raise → 500 아님, brand/pkm 정상, 깊이/series 만 빔."""
    uid = "user-A"
    pkm_repo, brand_repo, brand_memory_repo, _ = await _seed_base(uid)

    class _BoomDomainRepo:
        async def list_for_brand(self, *a: Any, **k: Any) -> list[dict[str, Any]]:
            raise RuntimeError("domains down")

    resp = await _aggregate_pkm_graph(
        uid,
        pkm_repo=pkm_repo,
        brand_repo=brand_repo,
        brand_memory_repo=brand_memory_repo,
        domain_repo=_BoomDomainRepo(),  # type: ignore[arg-type]
        series_repo=SeriesRepo(),
    )

    # brand/개인 PKM 정상, 깊이 0 (graceful).
    assert resp.summary.brands == 1
    assert resp.summary.personal == 1
    assert resp.summary.domains == 0
    assert resp.summary.series == 0
    assert not any(n.type in {"domain", "series"} for n in resp.nodes)


# ─── 6. 익명 → 빈 그래프 (unchanged) ──────────────────────────────────


@pytest.mark.asyncio
async def test_pkm_graph_anonymous_still_empty() -> None:
    """auth_user_id None → 빈 그래프 (Phase 21 확장 후에도 unchanged)."""
    resp = await _aggregate_pkm_graph(None)
    assert resp.nodes == []
    assert resp.edges == []
    assert resp.summary.domains == 0
    assert resp.summary.series == 0
    assert resp.summary.sources == 0
