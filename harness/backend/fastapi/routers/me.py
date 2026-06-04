"""Phase 19 Slice S1 — /me/* 네임스페이스 라우터 (2nd-brain 집계).

`GET /api/v1/me/pkm-graph` — 인증 사용자의 **개인 PKM + 브랜드 PKM + 4계층(user/brand)** 을
read-only 로 집계해 {nodes, edges, summary} 그래프로 반환한다. S2(모바일 카드) / S3(데스크톱
react-flow 그래프) 시각화가 이 한 API 를 공유한다.

★ 신규 테이블 0 (읽기 전용 집계) — 기존 pkm_entries / brand_memory_entries / brands 를
  PkmRepo / BrandMemoryRepo / BrandRepo 로 읽어 그래프 구조로 변환만 한다.
★ RLS/격리: 오직 요청 auth_user_id(및 그가 소유한 brand)의 데이터만. 교차 사용자 노출 0
  (service-key repo 를 쓰더라도 항상 authed user id 로 필터). 익명(None) → 빈 그래프 graceful.
★ graceful: 어떤 repo 실패도 raise 금지 — 그 부분만 비고 절대 500 내지 않는다 (부분 집계).
★ DI seam: pkm_repo / brand_repo / brand_memory_repo 를 주입 가능 (default 는 get_supabase()
  로 구성된 모듈 싱글톤). 실 Supabase 없이 in-memory repo 로 단위 테스트한다.

참조:
  - meta/proposals/2026-06-04_2nd-brain-visualization-design.md §1 (도식화 대상)
  - backend/fastapi/routers/plans.py (_auth_user_id 패턴 + repo 싱글톤 패턴)
"""

from __future__ import annotations

import logging
from typing import Any, Optional

from fastapi import APIRouter, HTTPException, Request

from ..db import (
    BrandMemoryRepo,
    BrandRepo,
    DomainRepo,
    PkmRepo,
    SeriesRepo,
    VideoProjectRepo,
    get_supabase,
)
from ..schemas.graph import (
    MeDomainCreateRequest,
    MeDomainCreateResponse,
    MeDomainNode,
    MeDomainUpdateRequest,
    MeMutationResponse,
    MePkmMutationResponse,
    MePkmPatchRequest,
    MeSeriesCreateRequest,
    MeSeriesCreateResponse,
    MeSeriesNode,
    MeSeriesUpdateRequest,
    MeVideoCreateRequest,
    MeVideoCreateResponse,
    MeVideoNode,
    MeVideoUpdateRequest,
    PkmGraphEdge,
    PkmGraphNode,
    PkmGraphResponse,
    PkmGraphSummary,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/me", tags=["me"])


# ─── 모듈 repo 싱글톤 (plans.py 패턴 — graceful Supabase or in-memory) ──
# Supabase 사용 가능 시 PostgreSQL(서비스 키 → RLS 우회), 아니면 각 repo 의 in-memory fallback.
# 본 엔드포인트는 read-only — 항상 authed user id 로 필터하므로 service-key 여도 교차 노출 0.
_pkm_repo: PkmRepo = PkmRepo(supabase_client=get_supabase(), in_memory_store={})
_brand_repo: BrandRepo = BrandRepo(supabase_client=get_supabase(), in_memory_store={})
_brand_memory_repo: BrandMemoryRepo = BrandMemoryRepo(
    supabase_client=get_supabase(), in_memory_store={},
)
# Phase 21 S1 — 4계층 depth (Domain/Series) repo 싱글톤 (graceful, 동일 DI seam).
_domain_repo: DomainRepo = DomainRepo(supabase_client=get_supabase(), in_memory_store={})
_series_repo: SeriesRepo = SeriesRepo(supabase_client=get_supabase(), in_memory_store={})
# Phase 26 S1 — 4계층 최하단 (Video) repo 싱글톤 (graceful, 동일 DI seam).
_video_repo: VideoProjectRepo = VideoProjectRepo(
    supabase_client=get_supabase(), in_memory_store={},
)

# PKM 노드 라벨 요약 상한 (content 가 길면 잘라 표시 — 노드 가독성).
_LABEL_MAX = 60

# 브랜드 PKM 출처(source) 노드 라벨 접두 (Phase 21 provenance — 짧은 plan id 동봉).
_SOURCE_LABEL_PREFIX = "기획안 출처"


# ─── helpers ──────────────────────────────────────────────────────────


def _auth_user_id(request: Request) -> Optional[str]:
    """request.state.user (auth_middleware 주입) 에서 user_id 추출. anon 시 None.

    plans.py::_auth_user_id 와 동일 규약 (단일 source-of-truth 는 cookie/JWT).
    """
    user = getattr(request.state, "user", None)
    if isinstance(user, dict):
        uid = user.get("user_id")
        return str(uid) if uid else None
    return None


def _summarize(content: Any) -> str:
    """PKM content 를 노드 라벨용으로 요약 (None/긴 문자열 graceful 처리)."""
    text = str(content or "").strip()
    if len(text) > _LABEL_MAX:
        return text[: _LABEL_MAX - 1] + "…"
    return text


def _pkm_node(
    row: dict[str, Any], *, id_prefix: str, scope: str,
) -> PkmGraphNode:
    """pkm_entries / brand_memory_entries row → PkmGraphNode 변환 (공통).

    id 는 row 의 'id'(영속) 우선, 없으면(in-memory fallback row) entry_type+content 로
    결정적 대체 — 동일 row 는 동일 id (그래프 안정성).
    """
    raw_id = row.get("id")
    node_id = str(raw_id) if raw_id else f"{row.get('entry_type')}:{row.get('content')}"
    return PkmGraphNode(
        id=f"{id_prefix}:{node_id}",
        type="pkm",
        scope=scope,  # type: ignore[arg-type]
        entry_type=row.get("entry_type"),
        label=_summarize(row.get("content")),
        locked=bool(row.get("is_user_locked", False)),
    )


# ─── GET /api/v1/me/pkm-graph ─────────────────────────────────────────


@router.get(
    "/pkm-graph",
    response_model=PkmGraphResponse,
    summary="2nd-brain PKM 그래프 집계 (Phase 19 Slice S1)",
    description=(
        "인증 사용자의 개인 PKM(pkm_entries, scope=personal) + 소유 브랜드(brands) + "
        "브랜드 PKM(brand_memory_entries)을 {nodes, edges, summary} 그래프로 집계 반환한다 "
        "(read-only, 신규 테이블 0). 루트 user 노드 아래 개인 PKM(has_personal) 과 "
        "brand(owns) → 브랜드 PKM(has_brand_pkm) 을 펼친다. is_user_locked → node.locked(🔒). "
        "★ RLS/격리: 본인 auth_user_id/소유 brand 의 데이터만 (교차 노출 0). "
        "익명/무데이터 → 빈 그래프 graceful(200). 어떤 repo 실패도 그 부분만 비고 500 없음."
    ),
)
async def get_pkm_graph(request: Request) -> PkmGraphResponse:
    """HTTP route — request 에서 신원 추출 후 집계 함수에 위임 (thin handler).

    ★ DI seam 은 _aggregate_pkm_graph 에 둔다 (FastAPI 가 repo 인자를 request/response 필드로
      해석하지 않도록 route 시그니처는 request only).
    """
    return await _aggregate_pkm_graph(_auth_user_id(request))


async def _aggregate_pkm_graph(
    auth_user_id: Optional[str],
    *,
    pkm_repo: Optional[PkmRepo] = None,
    brand_repo: Optional[BrandRepo] = None,
    brand_memory_repo: Optional[BrandMemoryRepo] = None,
    domain_repo: Optional[DomainRepo] = None,
    series_repo: Optional[SeriesRepo] = None,
    video_repo: Optional[VideoProjectRepo] = None,
) -> PkmGraphResponse:
    """auth_user_id 기준으로 PKM 그래프를 집계한다 (graceful, RLS 격리).

    ★ DI seam: repo 인자 미전달 시 모듈 싱글톤 사용 (default 운영 경로). 테스트는 in-memory repo 주입.
    ★ Phase 21 S1 (additive): brand 아래로 Domain→Series 깊이(domain_repo/series_repo) +
      브랜드 PKM 출처(source_plan_id) provenance 를 펼친다. domain/series/source 가 없으면
      Phase 19 와 byte-identical (깊이/출처 노드·엣지 0, summary 신규 카운트 0).
    ★ Phase 26 S1 (additive): series 아래로 Video(video_repo) 깊이를 한 단계 더 펼친다.
      video 가 없으면 Phase 24 와 byte-identical (video 노드·엣지 0, summary.videos 0).
    """
    # 익명 → 빈 그래프 (graceful 200, 노출 0).
    if not auth_user_id:
        return PkmGraphResponse()

    pkm_repo = pkm_repo if pkm_repo is not None else _pkm_repo
    brand_repo = brand_repo if brand_repo is not None else _brand_repo
    brand_memory_repo = (
        brand_memory_repo if brand_memory_repo is not None else _brand_memory_repo
    )
    domain_repo = domain_repo if domain_repo is not None else _domain_repo
    series_repo = series_repo if series_repo is not None else _series_repo
    video_repo = video_repo if video_repo is not None else _video_repo

    nodes: list[PkmGraphNode] = []
    edges: list[PkmGraphEdge] = []
    # Phase 21 — 깊이/출처 카운트 (graceful: 데이터 없으면 0 유지 = Phase 19 동일).
    domain_count = 0
    series_count = 0
    video_count = 0  # Phase 26 — video 노드 수 (graceful: 데이터 없으면 0 = Phase 24 동일).
    source_ids: set[str] = set()  # 출처(plan) 노드 dedup — bm 여럿이 같은 plan 출처일 수 있음.

    # 0. 루트 user 노드 (4계층의 정점 — domains/series 깊이는 S5).
    user_node_id = f"user:{auth_user_id}"
    nodes.append(PkmGraphNode(id=user_node_id, type="user", label="나"))

    # 1. 개인 PKM (scope=personal) — user → pkm (has_personal).
    personal_count = 0
    try:
        personal_entries = await pkm_repo.list_for_user(auth_user_id, scope="personal")
    except Exception as exc:  # graceful — 이 부분만 비우고 진행 (500 금지).
        logger.warning("pkm_graph personal_list_failed: %s (graceful)", exc.__class__.__name__)
        personal_entries = []
    for row in personal_entries:
        if not isinstance(row, dict):
            continue
        node = _pkm_node(row, id_prefix="pkm", scope="personal")
        nodes.append(node)
        edges.append(PkmGraphEdge(source=user_node_id, target=node.id, kind="has_personal"))
        personal_count += 1

    # 2. 소유 brands — user → brand (owns) + 각 brand 의 브랜드 PKM.
    brand_count = 0
    brand_pkm_count = 0
    try:
        brands = await brand_repo.list_for_user(auth_user_id)
    except Exception as exc:  # graceful — brand 집계 실패 시 brand/브랜드 PKM 전체 skip.
        logger.warning("pkm_graph brand_list_failed: %s (graceful)", exc.__class__.__name__)
        brands = []
    for brand in brands:
        if not isinstance(brand, dict):
            continue
        brand_id = brand.get("id")
        if not brand_id:
            continue  # id 없는 row(비정상) → skip.
        brand_node_id = f"brand:{brand_id}"
        nodes.append(
            PkmGraphNode(
                id=brand_node_id,
                type="brand",
                label=_summarize(brand.get("name")) or "브랜드",
            )
        )
        edges.append(PkmGraphEdge(source=user_node_id, target=brand_node_id, kind="owns"))
        brand_count += 1

        # 2a. (Phase 21 additive) 4계층 depth — brand → domain (has_domain) → series (has_series).
        # ★ graceful: domain/series repo 실패 → 그 brand 의 깊이만 비우고 진행 (500 금지).
        # ★ byte-identical: domain 0 → 이 블록은 노드/엣지 0 추가 (Phase 19 동일).
        try:
            domains = await domain_repo.list_for_brand(str(brand_id))
        except Exception as exc:
            logger.warning(
                "pkm_graph domain_list_failed: %s brand_id=%s (graceful)",
                exc.__class__.__name__, brand_id,
            )
            domains = []
        for domain in domains:
            if not isinstance(domain, dict):
                continue
            domain_id = domain.get("id")
            if not domain_id:
                continue  # id 없는 row(비정상) → skip.
            domain_node_id = f"domain:{domain_id}"
            nodes.append(
                PkmGraphNode(
                    id=domain_node_id,
                    type="domain",
                    label=_summarize(domain.get("name")) or "도메인",
                )
            )
            edges.append(
                PkmGraphEdge(source=brand_node_id, target=domain_node_id, kind="has_domain")
            )
            domain_count += 1

            # domain → series (has_series). domain 단위로 graceful.
            try:
                series_rows = await series_repo.list_for_domain(str(domain_id))
            except Exception as exc:
                logger.warning(
                    "pkm_graph series_list_failed: %s domain_id=%s (graceful)",
                    exc.__class__.__name__, domain_id,
                )
                series_rows = []
            for series_row in series_rows:
                if not isinstance(series_row, dict):
                    continue
                series_id = series_row.get("id")
                if not series_id:
                    continue
                series_node_id = f"series:{series_id}"
                nodes.append(
                    PkmGraphNode(
                        id=series_node_id,
                        type="series",
                        label=_summarize(series_row.get("name")) or "시리즈",
                    )
                )
                edges.append(
                    PkmGraphEdge(
                        source=domain_node_id, target=series_node_id, kind="has_series",
                    )
                )
                series_count += 1

                # (Phase 26 additive) series → video (has_video). series 단위로 graceful.
                # ★ byte-identical: video 0 → 이 블록은 노드/엣지 0 추가 (Phase 24 동일).
                try:
                    video_rows = await video_repo.list_for_series(str(series_id))
                except Exception as exc:
                    logger.warning(
                        "pkm_graph video_list_failed: %s series_id=%s (graceful)",
                        exc.__class__.__name__, series_id,
                    )
                    video_rows = []
                for video_row in video_rows:
                    if not isinstance(video_row, dict):
                        continue
                    video_id = video_row.get("id")
                    if not video_id:
                        continue
                    video_node_id = f"video:{video_id}"
                    nodes.append(
                        PkmGraphNode(
                            id=video_node_id,
                            type="video",
                            label=_summarize(video_row.get("title")) or "영상",
                        )
                    )
                    edges.append(
                        PkmGraphEdge(
                            source=series_node_id, target=video_node_id, kind="has_video",
                        )
                    )
                    video_count += 1

        # 2b. 브랜드 PKM — brand → bm (has_brand_pkm). brand 단위로 graceful.
        try:
            bm_entries = await brand_memory_repo.list_for_brand(str(brand_id))
        except Exception as exc:  # graceful — 해당 brand 의 PKM 만 비우고 다음 brand 진행.
            logger.warning(
                "pkm_graph brand_memory_list_failed: %s brand_id=%s (graceful)",
                exc.__class__.__name__, brand_id,
            )
            bm_entries = []
        for row in bm_entries:
            if not isinstance(row, dict):
                continue
            node = _pkm_node(row, id_prefix="bm", scope="brand")
            nodes.append(node)
            edges.append(
                PkmGraphEdge(source=brand_node_id, target=node.id, kind="has_brand_pkm")
            )
            brand_pkm_count += 1

            # 2c. (Phase 21 additive) provenance — 브랜드 PKM 에 source_plan_id 가 있으면
            # 출처(source) 노드 + bm → source (sourced_from) 엣지. plan_id 로 dedup.
            # ★ byte-identical: source_plan_id 없음/빈 값 → 노드/엣지 0 (Phase 19 동일).
            plan_id = row.get("source_plan_id")
            if plan_id:
                plan_id_str = str(plan_id)
                source_node_id = f"source:{plan_id_str}"
                if plan_id_str not in source_ids:
                    source_ids.add(plan_id_str)
                    nodes.append(
                        PkmGraphNode(
                            id=source_node_id,
                            type="source",
                            label=f"{_SOURCE_LABEL_PREFIX} {plan_id_str[:8]}".strip(),
                        )
                    )
                edges.append(
                    PkmGraphEdge(source=node.id, target=source_node_id, kind="sourced_from")
                )

    logger.info(
        "pkm_graph aggregated auth_user_id=%s personal=%d brands=%d brand_pkm=%d "
        "domains=%d series=%d videos=%d sources=%d",
        auth_user_id, personal_count, brand_count, brand_pkm_count,
        domain_count, series_count, video_count, len(source_ids),
    )
    return PkmGraphResponse(
        nodes=nodes,
        edges=edges,
        summary=PkmGraphSummary(
            personal=personal_count,
            brand=brand_pkm_count,
            brands=brand_count,
            domains=domain_count,
            series=series_count,
            videos=video_count,
            sources=len(source_ids),
        ),
    )


# ─── PKM 큐레이션 (Phase 19 Slice S4 — 잠금/편집/삭제) ─────────────────
#
# node_id 네임스페이스(S1)로 대상 분기:
#   - "pkm:<id>" → 개인 PKM (pkm_entries, auth_user_id 격리) — PkmRepo.
#   - "bm:<id>"  → 브랜드 PKM (brand_memory_entries) — 소유 brand 검증 후 BrandMemoryRepo.
# 익명 → 401. 미존재/미소유 → 404. 어떤 repo 실패도 안전(None/False → 404). 교차 사용자 변경/삭제 0.


def _require_auth_user_id(request: Request) -> str:
    """authed uid 추출 — 익명이면 401 (큐레이션은 본인 데이터에만 허용)."""
    uid = _auth_user_id(request)
    if not uid:
        raise HTTPException(status_code=401, detail="unauthenticated")
    return uid


def _split_node_id(node_id: str) -> tuple[str, str]:
    """node_id 를 (prefix, raw_id) 로 분해. 'pkm:<id>' → ('pkm', '<id>').

    raw_id 자체가 ':' 를 포함할 수 있어(in-memory fallback id) 첫 ':' 만 기준 분할.
    """
    prefix, sep, raw = node_id.partition(":")
    if not sep:
        return ("", node_id)
    return (prefix, raw)


async def _owns_brand_entry(
    raw_id: str,
    *,
    auth_user_id: str,
    brand_repo: BrandRepo,
    brand_memory_repo: BrandMemoryRepo,
) -> bool:
    """브랜드 PKM entry(raw_id)가 uid 소유 brand 에 속하는지 검증 (RLS).

    uid 의 brand 들을 나열 → 각 brand 의 brand_memory entry id 에 raw_id 가 있으면 True.
    어떤 repo 실패도 graceful — 검증 실패(미소유 처리) → False (500 금지).
    """
    try:
        brands = await brand_repo.list_for_user(auth_user_id)
    except Exception as exc:
        logger.warning("pkm_curate brand_list_failed: %s (graceful)", exc.__class__.__name__)
        return False
    for brand in brands:
        if not isinstance(brand, dict):
            continue
        brand_id = brand.get("id")
        if not brand_id:
            continue
        try:
            entries = await brand_memory_repo.list_for_brand(str(brand_id))
        except Exception as exc:
            logger.warning(
                "pkm_curate brand_memory_list_failed: %s (graceful)", exc.__class__.__name__,
            )
            continue
        for row in entries:
            if isinstance(row, dict) and str(row.get("id")) == str(raw_id):
                return True
    return False


@router.patch(
    "/pkm/{node_id}",
    response_model=MePkmMutationResponse,
    summary="PKM 큐레이션 — content 편집 / 잠금 토글 (Phase 19 Slice S4)",
    description=(
        "node_id('pkm:<id>' 개인 / 'bm:<id>' 브랜드)로 분기해 content/locked 를 부분 갱신한다. "
        "개인은 auth_user_id 격리, 브랜드는 소유 brand 검증 후 갱신. "
        "익명 → 401. 미존재/미소유 → 404. 교차 사용자 변경 0."
    ),
)
async def patch_pkm_node(
    node_id: str, body: MePkmPatchRequest, request: Request,
) -> MePkmMutationResponse:
    """PKM 노드 1개 부분 갱신 (thin handler — 신원 추출 후 위임)."""
    uid = _require_auth_user_id(request)
    return await _curate_pkm_patch(node_id, body, uid)


@router.delete(
    "/pkm/{node_id}",
    response_model=MePkmMutationResponse,
    summary="PKM 큐레이션 — 삭제 (Phase 19 Slice S4)",
    description=(
        "node_id('pkm:<id>' 개인 / 'bm:<id>' 브랜드)로 분기해 PKM entry 를 삭제한다. "
        "개인은 auth_user_id 격리, 브랜드는 소유 brand 검증 후 삭제. "
        "익명 → 401. 미존재/미소유 → 404. 교차 사용자 삭제 0."
    ),
)
async def delete_pkm_node(node_id: str, request: Request) -> MePkmMutationResponse:
    """PKM 노드 1개 삭제 (thin handler — 신원 추출 후 위임)."""
    uid = _require_auth_user_id(request)
    return await _curate_pkm_delete(node_id, uid)


async def _curate_pkm_patch(
    node_id: str,
    body: MePkmPatchRequest,
    auth_user_id: str,
    *,
    pkm_repo: Optional[PkmRepo] = None,
    brand_repo: Optional[BrandRepo] = None,
    brand_memory_repo: Optional[BrandMemoryRepo] = None,
) -> MePkmMutationResponse:
    """PATCH 구현 — node_id prefix 분기 + 소유 검증 + 부분 갱신 (DI seam for tests)."""
    pkm_repo = pkm_repo if pkm_repo is not None else _pkm_repo
    brand_repo = brand_repo if brand_repo is not None else _brand_repo
    brand_memory_repo = (
        brand_memory_repo if brand_memory_repo is not None else _brand_memory_repo
    )

    prefix, raw_id = _split_node_id(node_id)

    if prefix == "pkm":
        # 개인 PKM — PkmRepo 가 auth_user_id 격리로 소유 강제.
        # ★ graceful: repo 가 (예기치 못하게) raise 해도 500 금지 → 404 안전 매핑.
        try:
            updated = await pkm_repo.update_entry(
                raw_id,
                auth_user_id=auth_user_id,
                content=body.content,
                is_user_locked=body.locked,
            )
        except Exception as exc:
            logger.warning("pkm_patch_failed: %s (graceful 404)", exc.__class__.__name__)
            updated = None
        if updated is None:
            raise HTTPException(status_code=404, detail="pkm_not_found")
        return MePkmMutationResponse(
            ok=True, node=_pkm_node(updated, id_prefix="pkm", scope="personal"),
        )

    if prefix == "bm":
        # 브랜드 PKM — 먼저 소유 brand 검증 (미소유 → 404).
        owned = await _owns_brand_entry(
            raw_id,
            auth_user_id=auth_user_id,
            brand_repo=brand_repo,
            brand_memory_repo=brand_memory_repo,
        )
        if not owned:
            raise HTTPException(status_code=404, detail="brand_pkm_not_found")
        try:
            updated = await brand_memory_repo.update_entry(
                raw_id, content=body.content, is_user_locked=body.locked,
            )
        except Exception as exc:
            logger.warning("bm_patch_failed: %s (graceful 404)", exc.__class__.__name__)
            updated = None
        if updated is None:
            raise HTTPException(status_code=404, detail="brand_pkm_not_found")
        return MePkmMutationResponse(
            ok=True, node=_pkm_node(updated, id_prefix="bm", scope="brand"),
        )

    # 알 수 없는 네임스페이스(user:/brand:/기타) → 큐레이션 대상 아님.
    raise HTTPException(status_code=404, detail="not_a_pkm_node")


async def _curate_pkm_delete(
    node_id: str,
    auth_user_id: str,
    *,
    pkm_repo: Optional[PkmRepo] = None,
    brand_repo: Optional[BrandRepo] = None,
    brand_memory_repo: Optional[BrandMemoryRepo] = None,
) -> MePkmMutationResponse:
    """DELETE 구현 — node_id prefix 분기 + 소유 검증 + 삭제 (DI seam for tests)."""
    pkm_repo = pkm_repo if pkm_repo is not None else _pkm_repo
    brand_repo = brand_repo if brand_repo is not None else _brand_repo
    brand_memory_repo = (
        brand_memory_repo if brand_memory_repo is not None else _brand_memory_repo
    )

    prefix, raw_id = _split_node_id(node_id)

    if prefix == "pkm":
        # ★ graceful: repo raise → 500 금지, 404 안전 매핑.
        try:
            ok = await pkm_repo.delete_entry(raw_id, auth_user_id=auth_user_id)
        except Exception as exc:
            logger.warning("pkm_delete_failed: %s (graceful 404)", exc.__class__.__name__)
            ok = False
        if not ok:
            raise HTTPException(status_code=404, detail="pkm_not_found")
        return MePkmMutationResponse(ok=True)

    if prefix == "bm":
        owned = await _owns_brand_entry(
            raw_id,
            auth_user_id=auth_user_id,
            brand_repo=brand_repo,
            brand_memory_repo=brand_memory_repo,
        )
        if not owned:
            raise HTTPException(status_code=404, detail="brand_pkm_not_found")
        try:
            ok = await brand_memory_repo.delete_entry(raw_id)
        except Exception as exc:
            logger.warning("bm_delete_failed: %s (graceful 404)", exc.__class__.__name__)
            ok = False
        if not ok:
            raise HTTPException(status_code=404, detail="brand_pkm_not_found")
        return MePkmMutationResponse(ok=True)

    raise HTTPException(status_code=404, detail="not_a_pkm_node")


# ─── 구조 생성 (Phase 22 Slice S1 — Domain/Series CREATE) ─────────────
#
# 사용자가 4계층(User→Brand→Domain→Series) 의 Domain/Series 를 직접 만든다.
# 생성 즉시 Phase 21 /me/pkm-graph 가 깊이 노드로 자동 반영(집계 변경 0).
#   POST /api/v1/me/domains  {brand_id, name}  → 본인 brand 아래 domain.
#   POST /api/v1/me/series   {domain_id, name} → 본인 domain 아래 series.
# 익명 → 401. 빈 name → 422 (Pydantic). 미소유 brand/domain → 404 (curation 과 동일 의미론).
# 어떤 repo 실패도 안전 — 생성 None → 503(일시 실패), 절대 unhandled 500 / 교차 생성 0.


async def _owns_brand(
    brand_id: str,
    *,
    auth_user_id: str,
    brand_repo: BrandRepo,
) -> bool:
    """brand_id 가 uid 소유 brand 목록에 있는지 검증 (RLS). graceful 실패 → False (미소유 처리)."""
    try:
        brands = await brand_repo.list_for_user(auth_user_id)
    except Exception as exc:
        logger.warning("structure brand_list_failed: %s (graceful)", exc.__class__.__name__)
        return False
    for brand in brands:
        if isinstance(brand, dict) and str(brand.get("id")) == str(brand_id):
            return True
    return False


async def _owns_domain(
    domain_id: str,
    *,
    auth_user_id: str,
    brand_repo: BrandRepo,
    domain_repo: DomainRepo,
) -> bool:
    """domain_id 가 uid 소유 brand 들의 domain 에 속하는지 검증 (RLS).

    uid 의 brand 나열 → 각 brand 의 domain 나열 → domain_id 있으면 True.
    어떤 repo 실패도 graceful — 미소유 처리(False), 500 금지.
    """
    try:
        brands = await brand_repo.list_for_user(auth_user_id)
    except Exception as exc:
        logger.warning("structure brand_list_failed: %s (graceful)", exc.__class__.__name__)
        return False
    for brand in brands:
        if not isinstance(brand, dict):
            continue
        brand_id = brand.get("id")
        if not brand_id:
            continue
        try:
            domains = await domain_repo.list_for_brand(str(brand_id))
        except Exception as exc:
            logger.warning(
                "structure domain_list_failed: %s (graceful)", exc.__class__.__name__,
            )
            continue
        for domain in domains:
            if isinstance(domain, dict) and str(domain.get("id")) == str(domain_id):
                return True
    return False


@router.post(
    "/domains",
    response_model=MeDomainCreateResponse,
    summary="구조 생성 — 소유 brand 아래 domain 생성 (Phase 22 Slice S1)",
    description=(
        "본인 소유 brand(brand_id) 아래 domain 1개를 생성한다. 생성 즉시 /me/pkm-graph 가 "
        "깊이 노드로 자동 반영(집계 변경 0). 익명 → 401. 빈 name → 422. 미소유 brand → 404 "
        "(교차 사용자 생성 0). repo 일시 실패 → 503 (unhandled 500 없음)."
    ),
)
async def create_domain(
    body: MeDomainCreateRequest, request: Request,
) -> MeDomainCreateResponse:
    """domain 1개 생성 (thin handler — 신원 추출 후 위임)."""
    uid = _require_auth_user_id(request)
    return await _create_domain(body, uid)


@router.post(
    "/series",
    response_model=MeSeriesCreateResponse,
    summary="구조 생성 — 소유 domain 아래 series 생성 (Phase 22 Slice S1)",
    description=(
        "본인 소유 domain(domain_id) 아래 series 1개를 생성한다. 생성 즉시 /me/pkm-graph 가 "
        "깊이 노드로 자동 반영(집계 변경 0). 익명 → 401. 빈 name → 422. 미소유 domain → 404 "
        "(교차 사용자 생성 0). repo 일시 실패 → 503 (unhandled 500 없음)."
    ),
)
async def create_series(
    body: MeSeriesCreateRequest, request: Request,
) -> MeSeriesCreateResponse:
    """series 1개 생성 (thin handler — 신원 추출 후 위임)."""
    uid = _require_auth_user_id(request)
    return await _create_series(body, uid)


async def _create_domain(
    body: MeDomainCreateRequest,
    auth_user_id: str,
    *,
    brand_repo: Optional[BrandRepo] = None,
    domain_repo: Optional[DomainRepo] = None,
) -> MeDomainCreateResponse:
    """POST /me/domains 구현 — 소유 검증 + 생성 (DI seam for tests).

    소유 brand 아니면 404. 생성 None(일시 repo 실패) → 503 (graceful, unhandled 500 금지).
    """
    brand_repo = brand_repo if brand_repo is not None else _brand_repo
    domain_repo = domain_repo if domain_repo is not None else _domain_repo

    # 소유 brand 검증 — 미소유/미존재 → 404 (curation 과 동일, 403 아님).
    if not await _owns_brand(body.brand_id, auth_user_id=auth_user_id, brand_repo=brand_repo):
        raise HTTPException(status_code=404, detail="brand_not_found")

    # ★ graceful: repo.create 가 (예기치 못하게) raise 해도 unhandled 500 금지 → None 처리.
    try:
        row = await domain_repo.create(body.brand_id, body.name)
    except Exception as exc:
        logger.warning("domain_create_failed: %s (graceful 503)", exc.__class__.__name__)
        row = None
    if not row or not row.get("id"):
        # 검증/소유는 통과했으나 저장 일시 실패 → 503 (재시도 가능), 500 누출 0.
        raise HTTPException(status_code=503, detail="domain_create_unavailable")

    return MeDomainCreateResponse(
        ok=True,
        domain=MeDomainNode(
            id=str(row["id"]),
            brand_id=str(row.get("brand_id", body.brand_id)),
            name=str(row.get("name", body.name)),
        ),
    )


async def _create_series(
    body: MeSeriesCreateRequest,
    auth_user_id: str,
    *,
    brand_repo: Optional[BrandRepo] = None,
    domain_repo: Optional[DomainRepo] = None,
    series_repo: Optional[SeriesRepo] = None,
) -> MeSeriesCreateResponse:
    """POST /me/series 구현 — 소유 검증 + 생성 (DI seam for tests).

    소유 domain 아니면 404. 생성 None(일시 repo 실패) → 503 (graceful, unhandled 500 금지).
    """
    brand_repo = brand_repo if brand_repo is not None else _brand_repo
    domain_repo = domain_repo if domain_repo is not None else _domain_repo
    series_repo = series_repo if series_repo is not None else _series_repo

    # 소유 domain 검증 (uid brand → domain 체인) — 미소유/미존재 → 404.
    if not await _owns_domain(
        body.domain_id,
        auth_user_id=auth_user_id,
        brand_repo=brand_repo,
        domain_repo=domain_repo,
    ):
        raise HTTPException(status_code=404, detail="domain_not_found")

    try:
        row = await series_repo.create(body.domain_id, body.name)
    except Exception as exc:
        logger.warning("series_create_failed: %s (graceful 503)", exc.__class__.__name__)
        row = None
    if not row or not row.get("id"):
        raise HTTPException(status_code=503, detail="series_create_unavailable")

    return MeSeriesCreateResponse(
        ok=True,
        series=MeSeriesNode(
            id=str(row["id"]),
            domain_id=str(row.get("domain_id", body.domain_id)),
            name=str(row.get("name", body.name)),
        ),
    )


# ─── 구조 편집/삭제 (Phase 24 Slice S1 — Domain/Series EDIT+DELETE) ────
#
# Phase 22 CREATE 와 대칭으로 4계층 Domain/Series 를 rename + 삭제한다 (/brain 4계층 CRUD 완성).
# 편집/삭제 즉시 Phase 21 /me/pkm-graph 가 자동 반영(graph builder 불변).
#   PATCH  /api/v1/me/domains/{domain_id}  {name}  → 본인 brand 아래 domain rename.
#   DELETE /api/v1/me/domains/{domain_id}          → domain 삭제 + 그 아래 series 캐스케이드.
#   PATCH  /api/v1/me/series/{series_id}   {name}  → 본인 domain 아래 series rename.
#   DELETE /api/v1/me/series/{series_id}           → series 삭제.
# 익명 → 401. 빈 name → 422 (Pydantic). 미소유 domain/series → 404 (curation/create 와 동일 의미론).
# 어떤 repo 실패도 안전 — update None / delete False → 404 (controlled), unhandled 500 / 교차 변경 0.


async def _owns_series(
    series_id: str,
    *,
    auth_user_id: str,
    brand_repo: BrandRepo,
    domain_repo: DomainRepo,
    series_repo: SeriesRepo,
) -> bool:
    """series_id 가 uid 소유 brand→domain 아래 series 에 속하는지 검증 (RLS).

    uid 의 brand 나열 → 각 brand 의 domain 나열 → 각 domain 의 series 나열 → series_id 있으면 True.
    어떤 repo 실패도 graceful — 미소유 처리(False), 500 금지.
    """
    try:
        brands = await brand_repo.list_for_user(auth_user_id)
    except Exception as exc:
        logger.warning("structure brand_list_failed: %s (graceful)", exc.__class__.__name__)
        return False
    for brand in brands:
        if not isinstance(brand, dict):
            continue
        brand_id = brand.get("id")
        if not brand_id:
            continue
        try:
            domains = await domain_repo.list_for_brand(str(brand_id))
        except Exception as exc:
            logger.warning(
                "structure domain_list_failed: %s (graceful)", exc.__class__.__name__,
            )
            continue
        for domain in domains:
            if not isinstance(domain, dict):
                continue
            domain_id = domain.get("id")
            if not domain_id:
                continue
            try:
                series_rows = await series_repo.list_for_domain(str(domain_id))
            except Exception as exc:
                logger.warning(
                    "structure series_list_failed: %s (graceful)", exc.__class__.__name__,
                )
                continue
            for series_row in series_rows:
                if isinstance(series_row, dict) and str(series_row.get("id")) == str(series_id):
                    return True
    return False


@router.patch(
    "/domains/{domain_id}",
    response_model=MeDomainCreateResponse,
    summary="구조 편집 — 소유 domain rename (Phase 24 Slice S1)",
    description=(
        "본인 소유 domain(domain_id)의 name 을 변경한다. 변경 즉시 /me/pkm-graph 가 자동 반영. "
        "익명 → 401. 빈 name → 422. 미소유/미존재 domain → 404 (교차 사용자 변경 0). "
        "repo 일시 실패(None) → 404 (controlled, unhandled 500 없음)."
    ),
)
async def update_domain(
    domain_id: str, body: MeDomainUpdateRequest, request: Request,
) -> MeDomainCreateResponse:
    """domain 1개 rename (thin handler — 신원 추출 후 위임)."""
    uid = _require_auth_user_id(request)
    return await _update_domain(domain_id, body, uid)


@router.delete(
    "/domains/{domain_id}",
    response_model=MeMutationResponse,
    summary="구조 삭제 — 소유 domain 삭제 + series 캐스케이드 (Phase 24 Slice S1)",
    description=(
        "본인 소유 domain(domain_id)을 삭제한다. 그 아래 series 도 함께 삭제(Supabase FK 캐스케이드 / "
        "in-memory 라우터 캐스케이드). 삭제 즉시 /me/pkm-graph 가 자동 반영. "
        "익명 → 401. 미소유/미존재 domain → 404 (교차 사용자 삭제 0)."
    ),
)
async def delete_domain(domain_id: str, request: Request) -> MeMutationResponse:
    """domain 1개 삭제 (thin handler — 신원 추출 후 위임)."""
    uid = _require_auth_user_id(request)
    return await _delete_domain(domain_id, uid)


@router.patch(
    "/series/{series_id}",
    response_model=MeSeriesCreateResponse,
    summary="구조 편집 — 소유 series rename (Phase 24 Slice S1)",
    description=(
        "본인 소유 series(series_id)의 name 을 변경한다. 변경 즉시 /me/pkm-graph 가 자동 반영. "
        "익명 → 401. 빈 name → 422. 미소유/미존재 series → 404 (교차 사용자 변경 0). "
        "repo 일시 실패(None) → 404 (controlled, unhandled 500 없음)."
    ),
)
async def update_series(
    series_id: str, body: MeSeriesUpdateRequest, request: Request,
) -> MeSeriesCreateResponse:
    """series 1개 rename (thin handler — 신원 추출 후 위임)."""
    uid = _require_auth_user_id(request)
    return await _update_series(series_id, body, uid)


@router.delete(
    "/series/{series_id}",
    response_model=MeMutationResponse,
    summary="구조 삭제 — 소유 series 삭제 (Phase 24 Slice S1)",
    description=(
        "본인 소유 series(series_id)를 삭제한다. 삭제 즉시 /me/pkm-graph 가 자동 반영. "
        "익명 → 401. 미소유/미존재 series → 404 (교차 사용자 삭제 0)."
    ),
)
async def delete_series(series_id: str, request: Request) -> MeMutationResponse:
    """series 1개 삭제 (thin handler — 신원 추출 후 위임)."""
    uid = _require_auth_user_id(request)
    return await _delete_series(series_id, uid)


async def _update_domain(
    domain_id: str,
    body: MeDomainUpdateRequest,
    auth_user_id: str,
    *,
    brand_repo: Optional[BrandRepo] = None,
    domain_repo: Optional[DomainRepo] = None,
) -> MeDomainCreateResponse:
    """PATCH /me/domains/{id} 구현 — 소유 검증 + rename (DI seam for tests).

    소유 domain 아니면 404. update None(미존재/일시 실패) → 404 (graceful, unhandled 500 금지).
    """
    brand_repo = brand_repo if brand_repo is not None else _brand_repo
    domain_repo = domain_repo if domain_repo is not None else _domain_repo

    # 소유 domain 검증 (uid brand → domain 체인) — 미소유/미존재 → 404.
    if not await _owns_domain(
        domain_id, auth_user_id=auth_user_id, brand_repo=brand_repo, domain_repo=domain_repo,
    ):
        raise HTTPException(status_code=404, detail="domain_not_found")

    # ★ graceful: repo.update_name 이 (예기치 못하게) raise 해도 unhandled 500 금지 → None 처리.
    try:
        row = await domain_repo.update_name(domain_id, body.name)
    except Exception as exc:
        logger.warning("domain_update_failed: %s (graceful 404)", exc.__class__.__name__)
        row = None
    if not row or not row.get("id"):
        raise HTTPException(status_code=404, detail="domain_not_found")

    return MeDomainCreateResponse(
        ok=True,
        domain=MeDomainNode(
            id=str(row["id"]),
            brand_id=str(row.get("brand_id", "")),
            name=str(row.get("name", body.name)),
        ),
    )


async def _delete_domain(
    domain_id: str,
    auth_user_id: str,
    *,
    brand_repo: Optional[BrandRepo] = None,
    domain_repo: Optional[DomainRepo] = None,
    series_repo: Optional[SeriesRepo] = None,
) -> MeMutationResponse:
    """DELETE /me/domains/{id} 구현 — 소유 검증 + 삭제 + series 캐스케이드 (DI seam for tests).

    소유 domain 아니면 404. delete False(미존재/일시 실패) → 404 (graceful, unhandled 500 금지).
    ★ in-memory 캐스케이드: domain 아래 series 를 list_for_domain 으로 찾아 각각 SeriesRepo.delete.
      Supabase 는 series.domain_id ON DELETE CASCADE 가 자동 처리하지만, in-memory store 의
      series 가 부모 없이 남지 않도록 라우터가 명시 캐스케이드한다 (graceful, 실패해도 진행).
    """
    brand_repo = brand_repo if brand_repo is not None else _brand_repo
    domain_repo = domain_repo if domain_repo is not None else _domain_repo
    series_repo = series_repo if series_repo is not None else _series_repo

    if not await _owns_domain(
        domain_id, auth_user_id=auth_user_id, brand_repo=brand_repo, domain_repo=domain_repo,
    ):
        raise HTTPException(status_code=404, detail="domain_not_found")

    # 캐스케이드 대상 series 를 삭제 전에 수집 (domain 삭제 후엔 부모 키로 조회 불가할 수 있음).
    try:
        child_series = await series_repo.list_for_domain(domain_id)
    except Exception as exc:
        logger.warning("domain_delete_series_list_failed: %s (graceful)", exc.__class__.__name__)
        child_series = []

    try:
        ok = await domain_repo.delete(domain_id)
    except Exception as exc:
        logger.warning("domain_delete_failed: %s (graceful 404)", exc.__class__.__name__)
        ok = False
    if not ok:
        raise HTTPException(status_code=404, detail="domain_not_found")

    # ★ in-memory 캐스케이드 — 각 자식 series 삭제 (graceful: 개별 실패는 무시하고 계속).
    for series_row in child_series:
        if not isinstance(series_row, dict):
            continue
        series_id = series_row.get("id")
        if not series_id:
            continue
        try:
            await series_repo.delete(str(series_id))
        except Exception as exc:
            logger.warning(
                "domain_delete_series_cascade_failed: %s (graceful)", exc.__class__.__name__,
            )

    return MeMutationResponse(ok=True, deleted=True)


async def _update_series(
    series_id: str,
    body: MeSeriesUpdateRequest,
    auth_user_id: str,
    *,
    brand_repo: Optional[BrandRepo] = None,
    domain_repo: Optional[DomainRepo] = None,
    series_repo: Optional[SeriesRepo] = None,
) -> MeSeriesCreateResponse:
    """PATCH /me/series/{id} 구현 — 소유 검증 + rename (DI seam for tests).

    소유 series 아니면 404. update None(미존재/일시 실패) → 404 (graceful, unhandled 500 금지).
    """
    brand_repo = brand_repo if brand_repo is not None else _brand_repo
    domain_repo = domain_repo if domain_repo is not None else _domain_repo
    series_repo = series_repo if series_repo is not None else _series_repo

    if not await _owns_series(
        series_id,
        auth_user_id=auth_user_id,
        brand_repo=brand_repo,
        domain_repo=domain_repo,
        series_repo=series_repo,
    ):
        raise HTTPException(status_code=404, detail="series_not_found")

    try:
        row = await series_repo.update_name(series_id, body.name)
    except Exception as exc:
        logger.warning("series_update_failed: %s (graceful 404)", exc.__class__.__name__)
        row = None
    if not row or not row.get("id"):
        raise HTTPException(status_code=404, detail="series_not_found")

    return MeSeriesCreateResponse(
        ok=True,
        series=MeSeriesNode(
            id=str(row["id"]),
            domain_id=str(row.get("domain_id", "")),
            name=str(row.get("name", body.name)),
        ),
    )


async def _delete_series(
    series_id: str,
    auth_user_id: str,
    *,
    brand_repo: Optional[BrandRepo] = None,
    domain_repo: Optional[DomainRepo] = None,
    series_repo: Optional[SeriesRepo] = None,
) -> MeMutationResponse:
    """DELETE /me/series/{id} 구현 — 소유 검증 + 삭제 (DI seam for tests).

    소유 series 아니면 404. delete False(미존재/일시 실패) → 404 (graceful, unhandled 500 금지).
    """
    brand_repo = brand_repo if brand_repo is not None else _brand_repo
    domain_repo = domain_repo if domain_repo is not None else _domain_repo
    series_repo = series_repo if series_repo is not None else _series_repo

    if not await _owns_series(
        series_id,
        auth_user_id=auth_user_id,
        brand_repo=brand_repo,
        domain_repo=domain_repo,
        series_repo=series_repo,
    ):
        raise HTTPException(status_code=404, detail="series_not_found")

    try:
        ok = await series_repo.delete(series_id)
    except Exception as exc:
        logger.warning("series_delete_failed: %s (graceful 404)", exc.__class__.__name__)
        ok = False
    if not ok:
        raise HTTPException(status_code=404, detail="series_not_found")

    return MeMutationResponse(ok=True, deleted=True)


# ─── Video CRUD (Phase 26 Slice S1 — 4계층 최하단 Video CREATE+EDIT+DELETE) ──
#
# Phase 22/24 의 Domain/Series CRUD 를 한 단계 아래(series→video)로 그대로 복제한다.
# 생성/편집/삭제 즉시 Phase 21 /me/pkm-graph 가 series→video 깊이 노드로 자동 반영(graph builder 불변).
#   POST   /api/v1/me/videos               {series_id, title} → 본인 series 아래 video 생성.
#   PATCH  /api/v1/me/videos/{video_id}     {title}           → 본인 video 제목 변경.
#   DELETE /api/v1/me/videos/{video_id}                       → video 삭제.
# 익명 → 401. 빈 title → 422 (Pydantic). 미소유 series/video → 404 (curation/create 와 동일 의미론).
# 어떤 repo 실패도 안전 — create None → 503(일시 실패) / update None·delete False → 404 (controlled).
# unhandled 500 / 교차 사용자 생성·변경·삭제 0.


async def _owns_video(
    video_id: str,
    *,
    auth_user_id: str,
    brand_repo: BrandRepo,
    domain_repo: DomainRepo,
    series_repo: SeriesRepo,
    video_repo: VideoProjectRepo,
) -> bool:
    """video_id 가 uid 소유 brand→domain→series 아래 video 에 속하는지 검증 (RLS, 4-hop).

    uid 의 brand 나열 → 각 brand 의 domain → 각 domain 의 series → 각 series 의 video 나열 →
    video_id 있으면 True. 어떤 repo 실패도 graceful — 미소유 처리(False), 500 금지.
    """
    try:
        brands = await brand_repo.list_for_user(auth_user_id)
    except Exception as exc:
        logger.warning("structure brand_list_failed: %s (graceful)", exc.__class__.__name__)
        return False
    for brand in brands:
        if not isinstance(brand, dict):
            continue
        brand_id = brand.get("id")
        if not brand_id:
            continue
        try:
            domains = await domain_repo.list_for_brand(str(brand_id))
        except Exception as exc:
            logger.warning(
                "structure domain_list_failed: %s (graceful)", exc.__class__.__name__,
            )
            continue
        for domain in domains:
            if not isinstance(domain, dict):
                continue
            domain_id = domain.get("id")
            if not domain_id:
                continue
            try:
                series_rows = await series_repo.list_for_domain(str(domain_id))
            except Exception as exc:
                logger.warning(
                    "structure series_list_failed: %s (graceful)", exc.__class__.__name__,
                )
                continue
            for series_row in series_rows:
                if not isinstance(series_row, dict):
                    continue
                series_id = series_row.get("id")
                if not series_id:
                    continue
                try:
                    video_rows = await video_repo.list_for_series(str(series_id))
                except Exception as exc:
                    logger.warning(
                        "structure video_list_failed: %s (graceful)", exc.__class__.__name__,
                    )
                    continue
                for video_row in video_rows:
                    if isinstance(video_row, dict) and str(video_row.get("id")) == str(video_id):
                        return True
    return False


@router.post(
    "/videos",
    response_model=MeVideoCreateResponse,
    summary="구조 생성 — 소유 series 아래 video 생성 (Phase 26 Slice S1)",
    description=(
        "본인 소유 series(series_id) 아래 video 1개를 생성한다. 생성 즉시 /me/pkm-graph 가 "
        "series→video 깊이 노드로 자동 반영(집계 변경 0). 익명 → 401. 빈 title → 422. "
        "미소유 series → 404 (교차 사용자 생성 0). repo 일시 실패 → 503 (unhandled 500 없음)."
    ),
)
async def create_video(
    body: MeVideoCreateRequest, request: Request,
) -> MeVideoCreateResponse:
    """video 1개 생성 (thin handler — 신원 추출 후 위임)."""
    uid = _require_auth_user_id(request)
    return await _create_video(body, uid)


@router.patch(
    "/videos/{video_id}",
    response_model=MeVideoCreateResponse,
    summary="구조 편집 — 소유 video 제목 변경 (Phase 26 Slice S1)",
    description=(
        "본인 소유 video(video_id)의 title 을 변경한다. 변경 즉시 /me/pkm-graph 가 자동 반영. "
        "익명 → 401. 빈 title → 422. 미소유/미존재 video → 404 (교차 사용자 변경 0). "
        "repo 일시 실패(None) → 404 (controlled, unhandled 500 없음)."
    ),
)
async def update_video(
    video_id: str, body: MeVideoUpdateRequest, request: Request,
) -> MeVideoCreateResponse:
    """video 1개 제목 변경 (thin handler — 신원 추출 후 위임)."""
    uid = _require_auth_user_id(request)
    return await _update_video(video_id, body, uid)


@router.delete(
    "/videos/{video_id}",
    response_model=MeMutationResponse,
    summary="구조 삭제 — 소유 video 삭제 (Phase 26 Slice S1)",
    description=(
        "본인 소유 video(video_id)를 삭제한다. 삭제 즉시 /me/pkm-graph 가 자동 반영. "
        "익명 → 401. 미소유/미존재 video → 404 (교차 사용자 삭제 0)."
    ),
)
async def delete_video(video_id: str, request: Request) -> MeMutationResponse:
    """video 1개 삭제 (thin handler — 신원 추출 후 위임)."""
    uid = _require_auth_user_id(request)
    return await _delete_video(video_id, uid)


async def _create_video(
    body: MeVideoCreateRequest,
    auth_user_id: str,
    *,
    brand_repo: Optional[BrandRepo] = None,
    domain_repo: Optional[DomainRepo] = None,
    series_repo: Optional[SeriesRepo] = None,
    video_repo: Optional[VideoProjectRepo] = None,
) -> MeVideoCreateResponse:
    """POST /me/videos 구현 — 소유 검증 + 생성 (DI seam for tests).

    소유 series 아니면 404. 생성 None(일시 repo 실패) → 503 (graceful, unhandled 500 금지).
    ★ video_projects.auth_user_id NOT NULL → 인증 사용자 id 를 create 에 넘긴다.
    """
    brand_repo = brand_repo if brand_repo is not None else _brand_repo
    domain_repo = domain_repo if domain_repo is not None else _domain_repo
    series_repo = series_repo if series_repo is not None else _series_repo
    video_repo = video_repo if video_repo is not None else _video_repo

    # 소유 series 검증 (uid brand → domain → series 체인) — 미소유/미존재 → 404.
    if not await _owns_series(
        body.series_id,
        auth_user_id=auth_user_id,
        brand_repo=brand_repo,
        domain_repo=domain_repo,
        series_repo=series_repo,
    ):
        raise HTTPException(status_code=404, detail="series_not_found")

    try:
        row = await video_repo.create(body.series_id, body.title, auth_user_id)
    except Exception as exc:
        logger.warning("video_create_failed: %s (graceful 503)", exc.__class__.__name__)
        row = None
    if not row or not row.get("id"):
        raise HTTPException(status_code=503, detail="video_create_unavailable")

    return MeVideoCreateResponse(
        ok=True,
        video=MeVideoNode(
            id=str(row["id"]),
            series_id=str(row.get("series_id", body.series_id)),
            title=str(row.get("title", body.title)),
        ),
    )


async def _update_video(
    video_id: str,
    body: MeVideoUpdateRequest,
    auth_user_id: str,
    *,
    brand_repo: Optional[BrandRepo] = None,
    domain_repo: Optional[DomainRepo] = None,
    series_repo: Optional[SeriesRepo] = None,
    video_repo: Optional[VideoProjectRepo] = None,
) -> MeVideoCreateResponse:
    """PATCH /me/videos/{id} 구현 — 소유 검증 + 제목 변경 (DI seam for tests).

    소유 video 아니면 404. update None(미존재/일시 실패) → 404 (graceful, unhandled 500 금지).
    """
    brand_repo = brand_repo if brand_repo is not None else _brand_repo
    domain_repo = domain_repo if domain_repo is not None else _domain_repo
    series_repo = series_repo if series_repo is not None else _series_repo
    video_repo = video_repo if video_repo is not None else _video_repo

    if not await _owns_video(
        video_id,
        auth_user_id=auth_user_id,
        brand_repo=brand_repo,
        domain_repo=domain_repo,
        series_repo=series_repo,
        video_repo=video_repo,
    ):
        raise HTTPException(status_code=404, detail="video_not_found")

    try:
        row = await video_repo.update_title(video_id, body.title)
    except Exception as exc:
        logger.warning("video_update_failed: %s (graceful 404)", exc.__class__.__name__)
        row = None
    if not row or not row.get("id"):
        raise HTTPException(status_code=404, detail="video_not_found")

    return MeVideoCreateResponse(
        ok=True,
        video=MeVideoNode(
            id=str(row["id"]),
            series_id=str(row.get("series_id", "")),
            title=str(row.get("title", body.title)),
        ),
    )


async def _delete_video(
    video_id: str,
    auth_user_id: str,
    *,
    brand_repo: Optional[BrandRepo] = None,
    domain_repo: Optional[DomainRepo] = None,
    series_repo: Optional[SeriesRepo] = None,
    video_repo: Optional[VideoProjectRepo] = None,
) -> MeMutationResponse:
    """DELETE /me/videos/{id} 구현 — 소유 검증 + 삭제 (DI seam for tests).

    소유 video 아니면 404. delete False(미존재/일시 실패) → 404 (graceful, unhandled 500 금지).
    """
    brand_repo = brand_repo if brand_repo is not None else _brand_repo
    domain_repo = domain_repo if domain_repo is not None else _domain_repo
    series_repo = series_repo if series_repo is not None else _series_repo
    video_repo = video_repo if video_repo is not None else _video_repo

    if not await _owns_video(
        video_id,
        auth_user_id=auth_user_id,
        brand_repo=brand_repo,
        domain_repo=domain_repo,
        series_repo=series_repo,
        video_repo=video_repo,
    ):
        raise HTTPException(status_code=404, detail="video_not_found")

    try:
        ok = await video_repo.delete(video_id)
    except Exception as exc:
        logger.warning("video_delete_failed: %s (graceful 404)", exc.__class__.__name__)
        ok = False
    if not ok:
        raise HTTPException(status_code=404, detail="video_not_found")

    return MeMutationResponse(ok=True, deleted=True)


__all__ = [
    "router",
    "get_pkm_graph",
    "patch_pkm_node",
    "delete_pkm_node",
    "create_domain",
    "create_series",
    "update_domain",
    "delete_domain",
    "update_series",
    "delete_series",
    "create_video",
    "update_video",
    "delete_video",
]
