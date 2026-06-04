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
      - "pkm:<entry_id>"       (type=pkm, scope=personal)
      - "bm:<entry_id>"        (type=pkm, scope=brand)
    """

    id: str = Field(description="네임스페이스 접두어 포함 노드 id (예: 'pkm:<uuid>').")
    type: Literal["user", "brand", "pkm"] = Field(description="노드 종류.")
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

    kind: owns(user→brand) / has_personal(user→개인 pkm) / has_brand_pkm(brand→브랜드 pkm).
    """

    source: str = Field(description="출발 노드 id.")
    target: str = Field(description="도착 노드 id.")
    kind: Literal["owns", "has_personal", "has_brand_pkm"] = Field(
        description="관계 종류.",
    )


class PkmGraphSummary(BaseModel):
    """집계 요약 카운트 (UX 표시 + 빈 그래프 판별용)."""

    personal: int = Field(default=0, description="개인 PKM entry 수.")
    brand: int = Field(default=0, description="브랜드 PKM entry 수 (전 brand 합).")
    brands: int = Field(default=0, description="사용자 소유 brand 수.")


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


__all__ = [
    "PkmGraphNode",
    "PkmGraphEdge",
    "PkmGraphSummary",
    "PkmGraphResponse",
    "MePkmPatchRequest",
    "MePkmMutationResponse",
]
