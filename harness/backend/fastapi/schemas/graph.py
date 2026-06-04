"""Phase 19 Slice S1 — 2nd-brain PKM 그래프 집계 응답 스키마.

`GET /api/v1/me/pkm-graph` 가 사용자의 **개인 PKM + 브랜드 PKM + 4계층(user/brand)** 을
도식화 가능한 {nodes, edges} 그래프 구조로 반환한다. 신규 테이블 0 — 기존 pkm_entries /
brand_memory_entries / brands 를 읽어 집계하는 read-only 레이어.

★ 설계 출처: meta/proposals/2026-06-04_2nd-brain-visualization-design.md §1 (도식화 대상).
  노드 = User/Brand/PKM entries, 엣지 = 소유(owns)/보유(has_*) 관계. is_user_locked = 🔒 강조.
★ 카드/리스트(S2 모바일) · 그래프(S3 데스크톱) 양쪽이 동일 구조를 소비한다 (제안서 §2).
"""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field


class PkmGraphNode(BaseModel):
    """그래프 노드 1개 — user / brand / pkm(개인 또는 브랜드 scope).

    id 는 type 접두어로 네임스페이스를 구분한다 (충돌 0):
      - "user:<auth_user_id>"  (type=user, 루트 1개)
      - "brand:<brand_id>"     (type=brand)
      - "domain:<domain_id>"   (type=domain, Phase 21 4계층 depth)
      - "series:<series_id>"   (type=series, Phase 21 4계층 depth)
      - "video:<video_id>"     (type=video, Phase 26 4계층 최하단)
      - "pkm:<entry_id>"       (type=pkm, scope=personal)
      - "bm:<entry_id>"        (type=pkm, scope=brand)
      - "source:<plan_id>"     (type=source, Phase 21 provenance — 브랜드 PKM 출처)
    """

    id: str = Field(description="네임스페이스 접두어 포함 노드 id (예: 'pkm:<uuid>').")
    type: Literal["user", "brand", "domain", "series", "video", "pkm", "source"] = Field(
        description="노드 종류.",
    )
    label: str = Field(description="화면 표시용 라벨 (PKM 은 content 요약).")
    scope: Optional[Literal["personal", "brand"]] = Field(
        default=None, description="PKM 노드의 scope (개인/브랜드). 비-PKM 은 None.",
    )
    entry_type: Optional[str] = Field(
        default=None,
        description="PKM 노드의 entry_type (preferred_tone 등). 비-PKM 은 None.",
    )
    locked: Optional[bool] = Field(
        default=None,
        description="PKM 노드의 is_user_locked (🔒). 비-PKM 은 None.",
    )


class PkmGraphEdge(BaseModel):
    """그래프 엣지 1개 — source 노드 → target 노드 관계.

    kind: owns(user→brand) / has_personal(user→개인 pkm) / has_brand_pkm(brand→브랜드 pkm) /
          has_domain(brand→domain) / has_series(domain→series) / has_video(series→video) /
          sourced_from(브랜드 pkm→출처).
    """

    source: str = Field(description="출발 노드 id.")
    target: str = Field(description="도착 노드 id.")
    kind: Literal[
        "owns",
        "has_personal",
        "has_brand_pkm",
        "has_domain",
        "has_series",
        "has_video",
        "sourced_from",
    ] = Field(
        description="관계 종류.",
    )


class PkmGraphSummary(BaseModel):
    """집계 요약 카운트 (UX 표시 + 빈 그래프 판별용)."""

    personal: int = Field(default=0, description="개인 PKM entry 수.")
    brand: int = Field(default=0, description="브랜드 PKM entry 수 (전 brand 합).")
    brands: int = Field(default=0, description="사용자 소유 brand 수.")
    # Phase 21 S1 — 4계층 depth + provenance (default 0 → graceful/backward-compat:
    # domain/series/source 가 없으면 Phase 19 와 동일한 0 카운트).
    domains: int = Field(default=0, description="domain 노드 수 (전 brand 합, Phase 21).")
    series: int = Field(default=0, description="series 노드 수 (전 domain 합, Phase 21).")
    sources: int = Field(
        default=0, description="고유 출처(plan) 노드 수 — 브랜드 PKM provenance (Phase 21).",
    )
    # Phase 26 S1 — 4계층 최하단 video (default 0 → graceful/backward-compat:
    # video 가 없으면 Phase 24 와 동일한 0 카운트).
    videos: int = Field(default=0, description="video 노드 수 (전 series 합, Phase 26).")


class PkmGraphResponse(BaseModel):
    """GET /api/v1/me/pkm-graph 응답 — {nodes, edges, summary}.

    익명/무데이터 → 빈 nodes/edges + summary 전부 0 (graceful, 200).
    """

    nodes: list[PkmGraphNode] = Field(default_factory=list)
    edges: list[PkmGraphEdge] = Field(default_factory=list)
    summary: PkmGraphSummary = Field(default_factory=PkmGraphSummary)


# ─── Phase 19 Slice S4 — PKM 큐레이션(잠금/편집) 요청·응답 스키마 ─────────


class MePkmPatchRequest(BaseModel):
    """PATCH /api/v1/me/pkm/{node_id} 요청 — content 편집 / locked 토글 (부분 갱신).

    둘 다 선택(Optional) — content 만, locked 만, 혹은 둘 다 보낼 수 있다.
    아무 필드도 없으면 변경 없음(현재 노드 반환, no-op).
    """

    content: Optional[str] = Field(
        default=None, description="새 PKM content (None 이면 미변경).",
    )
    locked: Optional[bool] = Field(
        default=None,
        description="새 is_user_locked 상태 — 🔒 사용자 고정 토글 (None 이면 미변경).",
    )


class MePkmMutationResponse(BaseModel):
    """PATCH / DELETE /api/v1/me/pkm/{node_id} 응답.

    PATCH 성공 시 갱신된 node 를 동봉(프론트 즉시 반영 보조). DELETE 는 node 생략.
    소유/존재 검증 실패는 endpoint 가 404 로 응답 (이 모델 미반환).
    """

    ok: bool = Field(description="동작 성공 여부.")
    node: Optional[PkmGraphNode] = Field(
        default=None, description="PATCH 시 갱신된 PKM 노드 (DELETE 는 None).",
    )


# ─── Phase 22 Slice S1 — 구조 생성(Domain/Series) 요청·응답 스키마 ──────
#
# 4계층(User→Brand→Domain→Series) 의 Domain/Series 를 사용자가 직접 생성한다.
# 생성된 행은 Phase 21 /me/pkm-graph 집계가 자동으로 깊이 노드로 펼친다 (집계 변경 0).
# ★ 소유: domain 은 본인 brand 아래, series 는 본인 domain 아래만 — 라우터가 검증(교차 → 404).


class MeDomainCreateRequest(BaseModel):
    """POST /api/v1/me/domains 요청 — 소유 brand 아래 domain 1개 생성.

    name 은 비어 있으면 안 됨(min_length=1) → 빈 이름은 422 (Pydantic 검증).
    """

    brand_id: str = Field(description="domain 을 붙일 소유 brand id.")
    name: str = Field(min_length=1, description="domain 이름 (비어 있으면 422).")


class MeDomainNode(BaseModel):
    """생성된 domain 의 식별 필드 (응답 동봉)."""

    id: str = Field(description="생성된 domain id.")
    brand_id: str = Field(description="소속 brand id.")
    name: str = Field(description="domain 이름.")


class MeDomainCreateResponse(BaseModel):
    """POST /api/v1/me/domains 응답 — {ok, domain}.

    소유/검증 실패는 endpoint 가 401/404/422 로 응답 (이 모델 미반환).
    """

    ok: bool = Field(description="생성 성공 여부.")
    domain: MeDomainNode = Field(description="생성된 domain.")


class MeSeriesCreateRequest(BaseModel):
    """POST /api/v1/me/series 요청 — 소유 domain 아래 series 1개 생성.

    name 은 비어 있으면 안 됨(min_length=1) → 빈 이름은 422 (Pydantic 검증).
    """

    domain_id: str = Field(description="series 를 붙일 소유 domain id.")
    name: str = Field(min_length=1, description="series 이름 (비어 있으면 422).")


class MeSeriesNode(BaseModel):
    """생성된 series 의 식별 필드 (응답 동봉)."""

    id: str = Field(description="생성된 series id.")
    domain_id: str = Field(description="소속 domain id.")
    name: str = Field(description="series 이름.")


class MeSeriesCreateResponse(BaseModel):
    """POST /api/v1/me/series 응답 — {ok, series}."""

    ok: bool = Field(description="생성 성공 여부.")
    series: MeSeriesNode = Field(description="생성된 series.")


# ─── Phase 24 Slice S1 — 구조 편집/삭제(Domain/Series EDIT+DELETE) 스키마 ──
#
# Phase 22 의 CREATE 와 대칭으로 4계층 Domain/Series 의 rename + 삭제를 제공한다.
# 편집/삭제된 행은 Phase 21 /me/pkm-graph 집계가 자동 반영(graph builder 불변).
# ★ 소유: domain 은 본인 brand 아래, series 는 본인 domain 아래만 — 라우터가 검증(교차 → 404).
# ★ 응답: 편집은 Phase 22 의 {ok, domain|series} 재사용, 삭제는 {ok, deleted} (MeMutationResponse).


class MeDomainUpdateRequest(BaseModel):
    """PATCH /api/v1/me/domains/{domain_id} 요청 — domain rename.

    name 은 비어 있으면 안 됨(min_length=1) → 빈 이름은 422 (Pydantic 검증).
    """

    name: str = Field(min_length=1, description="새 domain 이름 (비어 있으면 422).")


class MeSeriesUpdateRequest(BaseModel):
    """PATCH /api/v1/me/series/{series_id} 요청 — series rename.

    name 은 비어 있으면 안 됨(min_length=1) → 빈 이름은 422 (Pydantic 검증).
    """

    name: str = Field(min_length=1, description="새 series 이름 (비어 있으면 422).")


class MeMutationResponse(BaseModel):
    """DELETE /api/v1/me/domains|series|videos/{id} 응답 — {ok, deleted}.

    소유/존재 검증 실패는 endpoint 가 404 로 응답 (이 모델 미반환).
    """

    ok: bool = Field(description="동작 성공 여부.")
    deleted: bool = Field(default=True, description="대상 삭제 완료 여부.")


# ─── Phase 26 Slice S1 — Video CRUD (4계층 최하단 Video 계층) 스키마 ─────
#
# 4계층(User→Brand→Domain→Series→Video) 의 최하단 Video 를 사용자가 직접 CRUD 한다.
# 생성/편집/삭제된 행은 Phase 21 /me/pkm-graph 집계가 series→video 깊이 노드로 자동 반영.
# ★ 소유: video 는 본인 series(→domain→brand) 아래만 — 라우터가 검증(교차 → 404).
# ★ name 필드가 `title` (video_projects 스키마 — Domain/Series 의 `name` 과 다름).


class MeVideoCreateRequest(BaseModel):
    """POST /api/v1/me/videos 요청 — 소유 series 아래 video 1개 생성.

    title 은 비어 있으면 안 됨(min_length=1) → 빈 title 은 422 (Pydantic 검증).
    """

    series_id: str = Field(description="video 를 붙일 소유 series id.")
    title: str = Field(min_length=1, description="video 제목 (비어 있으면 422).")


class MeVideoUpdateRequest(BaseModel):
    """PATCH /api/v1/me/videos/{video_id} 요청 — video 제목 변경.

    title 은 비어 있으면 안 됨(min_length=1) → 빈 title 은 422 (Pydantic 검증).
    """

    title: str = Field(min_length=1, description="새 video 제목 (비어 있으면 422).")


class MeVideoNode(BaseModel):
    """생성/편집된 video 의 식별 필드 (응답 동봉)."""

    id: str = Field(description="생성된 video id.")
    series_id: str = Field(description="소속 series id.")
    title: str = Field(description="video 제목.")


class MeVideoCreateResponse(BaseModel):
    """POST / PATCH /api/v1/me/videos 응답 — {ok, video}.

    소유/검증 실패는 endpoint 가 401/404/422 로 응답 (이 모델 미반환).
    """

    ok: bool = Field(description="동작 성공 여부.")
    video: MeVideoNode = Field(description="생성/편집된 video.")


__all__ = [
    "PkmGraphNode",
    "PkmGraphEdge",
    "PkmGraphSummary",
    "PkmGraphResponse",
    "MePkmPatchRequest",
    "MePkmMutationResponse",
    "MeDomainCreateRequest",
    "MeDomainNode",
    "MeDomainCreateResponse",
    "MeSeriesCreateRequest",
    "MeSeriesNode",
    "MeSeriesCreateResponse",
    "MeDomainUpdateRequest",
    "MeSeriesUpdateRequest",
    "MeMutationResponse",
    "MeVideoCreateRequest",
    "MeVideoUpdateRequest",
    "MeVideoNode",
    "MeVideoCreateResponse",
]
