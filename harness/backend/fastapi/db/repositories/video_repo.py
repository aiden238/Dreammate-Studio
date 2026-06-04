"""Phase 26 Slice S1 — VideoProjectRepo (graceful video CRUD wrapper, 4계층 최하단).

4계층 데이터 모델(User → Brand → Domain → Series → **Video**)의 Video 계층을 CRUD 한다.
Phase 21/22/24 의 DomainRepo/SeriesRepo 를 한 단계 아래로 그대로 복제한 것 — series 아래의
video_projects 행을 나열/생성/수정/삭제한다. Supabase 사용 가능 시 PostgreSQL(video_projects),
아니면 in-memory dict 로 graceful fallback.

★ additive/graceful: video 0 이거나 어떤 실패도 raise 금지 → 빈 리스트/None/False. 그러면
  pkm-graph builder 가 Phase 24 와 byte-identical 그래프를 낸다 (video 노드 0).
★ SeriesRepo 와의 차이:
  - in-memory store 가 series_id keyed (1:N) — series 아래의 video 들.
  - 테이블이 "video_projects", name 필드가 `title` (not `name`).
  - video_projects.auth_user_id 가 NOT NULL → create 시 auth_user_id 를 받아 INSERT 한다.
    (SeriesRepo 에는 없는 인자 — 라우터가 인증 사용자 id 를 넘긴다.)
★ LEGACY 주의: db/repositories/video_project.py(insert_video_project, ADR-023 deprecated)와는
  별개의 신규 repo 다 (legacy 미접촉).

설계 원칙 (SeriesRepo/BrandRepo 패턴 계승):
  1. graceful — 어떤 실패도 raise 금지, in-memory fallback / [] / None / False 반환 (P-GRACEFUL-001).
  2. 비동기 인터페이스 (SeriesRepo / DomainRepo 와 호환).
  3. RLS 격리는 video_projects→series→domains→brands→auth_user_id 체인이 강제 — 본 repo 는
     series_id keyed 라 호출자(라우터)가 이미 소유 검증된 series_id 만 넘긴다 (교차 노출 0).

참조:
  - db/migrations/0001_init.sql §4 video_projects (id / series_id FK / auth_user_id NOT NULL /
    title NOT NULL / status default 'draft' / …)
  - backend/fastapi/db/repositories/series_repo.py (CRUD 패턴 복제 모델, 한 단계 위)
"""

from __future__ import annotations

import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)


class VideoProjectRepo:
    """video_projects CRUD repository — graceful Supabase or in-memory (4계층 Video 계층).

    Usage:
        from backend.fastapi.db import VideoProjectRepo, get_supabase

        repo = VideoProjectRepo(supabase_client=get_supabase())
        videos = await repo.list_for_series("series-uuid")  # [] if none / failure
    """

    def __init__(
        self,
        supabase_client: Optional[Any] = None,
        in_memory_store: Optional[dict[str, list[dict[str, Any]]]] = None,
    ) -> None:
        self.client = supabase_client
        # key = series_id, value = video_projects rows list (1:N)
        self.store: dict[str, list[dict[str, Any]]] = (
            in_memory_store if in_memory_store is not None else {}
        )

    # ─── helpers ─────────────────────────────────────────────────────

    def _use_supabase(self) -> bool:
        return self.client is not None

    # ─── operations (read-only) ──────────────────────────────────────

    async def list_for_series(self, series_id: str) -> list[dict[str, Any]]:
        """List 해당 series 의 video_projects row 전체. 없거나 실패하면 빈 리스트 (graceful).

        ★ Phase 26 S1 (pkm-graph 깊이): Series → Video 펼침. video 0 → [] → 깊이 노드 0
          (Phase 24 byte-identical).
        ★ RLS/격리: 호출자가 이미 소유 검증된 series_id 만 넘긴다 (video_projects→series 체인).
        """
        if self._use_supabase():
            try:
                resp = (
                    self.client.table("video_projects")  # type: ignore[union-attr]
                    .select("*")
                    .eq("series_id", series_id)
                    .execute()
                )
                data = getattr(resp, "data", None)
                if data is not None:
                    return list(data)
            except Exception as exc:
                logger.warning(
                    "video_list_for_series_failed: %s — falling back to in-memory",
                    exc.__class__.__name__,
                )
        # graceful in-memory fallback — 본 series 의 video 만.
        return list(self.store.get(series_id, []))

    # ─── operations (create — Phase 26 S1) ───────────────────────────

    async def create(
        self, series_id: str, title: str, auth_user_id: str,
    ) -> Optional[dict[str, Any]]:
        """series 아래 video_projects row 1개 생성 후 그 row(dict, id 포함) 반환. 실패 시 None (graceful).

        ★ SeriesRepo.create 패턴 계승 — Supabase insert → id / 없으면 in-memory uuid4 fallback.
          어떤 실패도 raise 금지 → None (호출자가 안전 매핑).
        ★ video_projects.auth_user_id 는 NOT NULL → 인증 사용자 id 를 payload 에 동봉한다
          (SeriesRepo 에는 없는 인자 — series 는 domain→brand 체인으로만 소유가 강제됨).
        ★ RLS/격리: 호출자(라우터)가 이미 소유 검증한 series_id 만 넘긴다 (video_projects→series→
          domains→brands 체인).
        ★ in-memory mirror: Supabase 성공 시에도 store 에 append → list_for_series 즉시 반영.
        """
        payload: dict[str, Any] = {
            "series_id": series_id,
            "title": title,
            "auth_user_id": auth_user_id,
        }

        if self._use_supabase():
            try:
                resp = (
                    self.client.table("video_projects")  # type: ignore[union-attr]
                    .insert(payload)
                    .execute()
                )
                if resp and getattr(resp, "data", None):
                    row = resp.data[0]
                    if row.get("id"):
                        self.store.setdefault(series_id, []).append(row)  # in-memory mirror
                        return dict(row)
                # data 없음 / id 없음 → graceful None.
                logger.warning(
                    "video_create_no_id series_id=%s — graceful None", series_id,
                )
                return None
            except Exception as exc:
                logger.warning(
                    "video_create_failed: %s — graceful None",
                    exc.__class__.__name__,
                )
                return None

        # graceful in-memory fallback — uuid4 로 결정적 unique id.
        from uuid import uuid4

        row = dict(payload)
        row["id"] = str(uuid4())
        self.store.setdefault(series_id, []).append(row)
        return dict(row)

    async def get_or_create(
        self, series_id: str, title: str, auth_user_id: str,
    ) -> Optional[dict[str, Any]]:
        """series 아래 title 일치 video 가 있으면 그 row 를, 없으면 새로 생성해 반환 (idempotent).

        ★ SeriesRepo.get_or_create 패턴 계승 — list_for_series → title 비교 → 없으면 create.
          동일 (series, title) 재택1 → 기존 video 재사용(중복 0).
        ★ graceful: 어떤 실패도 raise 금지 → None (호출자 hook 이 graceful 매핑).
        ★ RLS/격리: 호출자(라우터)가 이미 소유 검증한 series_id 만 넘긴다 (video_projects→series 체인).
        """
        try:
            existing = await self.list_for_series(series_id)
            for row in existing:
                if isinstance(row, dict) and str(row.get("title")) == str(title):
                    return dict(row)  # 동일 title video 재사용 (멱등)
            return await self.create(series_id, title, auth_user_id)
        except Exception as exc:  # pragma: no cover — graceful (어떤 실패도 None)
            logger.warning(
                "video_get_or_create_failed: %s — graceful None",
                exc.__class__.__name__,
            )
            return None

    # ─── operations (edit/delete — Phase 26 S1) ──────────────────────
    #
    # ★ 소유(video→series→domain→brand→user) 검증은 endpoint 책임 — 본 repo 는 series_id keyed 라
    #   auth_user_id 를 모른다. endpoint 가 _owns_video 로 소유를 확인한 뒤에만 호출한다.
    #   (in-memory store 는 series_id 별 list 라 video_id 로 전 series 를 가로질러 검색.)
    # ★ SeriesRepo.update_name/delete 패턴 계승 — Supabase update/delete + id eq +
    #   in-memory list mutation + graceful (어떤 실패도 raise 금지 → None/False).

    async def update_title(
        self, video_id: str, title: str,
    ) -> Optional[dict[str, Any]]:
        """video 의 title 을 갱신 후 갱신된 row 반환. 미존재/실패 → None (graceful).

        ★ 소유 검증은 호출 endpoint 가 선행 (video→series→domain→brand→auth_user_id).
        ★ in-memory mirror: Supabase 성공 시에도 store 의 동일 row 를 갱신 → list_for_series 즉시 반영.
        """
        patch: dict[str, Any] = {"title": title}

        if self._use_supabase():
            try:
                resp = (
                    self.client.table("video_projects")  # type: ignore[union-attr]
                    .update(patch)
                    .eq("id", video_id)
                    .execute()
                )
                if resp and getattr(resp, "data", None):
                    row = resp.data[0]
                    self._mirror_update(video_id, patch)  # in-memory mirror
                    return dict(row)
                return None
            except Exception as exc:
                logger.warning(
                    "video_update_failed: %s — graceful None",
                    exc.__class__.__name__,
                )
                return None

        # graceful in-memory fallback — 전 series store 에서 id 일치 video 갱신.
        for rows in self.store.values():
            for row in rows:
                if str(row.get("id")) == str(video_id):
                    row.update(patch)
                    return dict(row)
        return None

    async def delete(self, video_id: str) -> bool:
        """video 삭제. 성공 True, 미존재/실패 False (graceful).

        ★ 소유 검증은 호출 endpoint 가 선행 (video→series→domain→brand→auth_user_id).
        ★ series 삭제 시 캐스케이드(in-memory): 라우터가 각 video 마다 본 delete 를 호출한다.
        """
        if self._use_supabase():
            try:
                resp = (
                    self.client.table("video_projects")  # type: ignore[union-attr]
                    .delete()
                    .eq("id", video_id)
                    .execute()
                )
                ok = bool(resp and getattr(resp, "data", None))
                if ok:
                    self._mirror_delete(video_id)  # in-memory mirror
                return ok
            except Exception as exc:
                logger.warning(
                    "video_delete_failed: %s — graceful False",
                    exc.__class__.__name__,
                )
                return False

        # graceful in-memory fallback — 전 series store 에서 id 일치 video 제거.
        return self._mirror_delete(video_id)

    def _mirror_update(self, video_id: str, patch: dict[str, Any]) -> None:
        """in-memory store 에서 video_id 일치 row 를 patch 로 갱신 (Supabase mirror 보조)."""
        for rows in self.store.values():
            for row in rows:
                if str(row.get("id")) == str(video_id):
                    row.update(patch)
                    return

    def _mirror_delete(self, video_id: str) -> bool:
        """in-memory store 에서 video_id 일치 row 제거. 제거했으면 True (Supabase mirror 보조)."""
        for rows in self.store.values():
            for i, row in enumerate(rows):
                if str(row.get("id")) == str(video_id):
                    rows.pop(i)
                    return True
        return False

    def _reset_for_test(self) -> None:
        """테스트용 in-memory store 초기화 (SeriesRepo._reset_for_test 패턴)."""
        self.store.clear()


__all__ = ["VideoProjectRepo"]
