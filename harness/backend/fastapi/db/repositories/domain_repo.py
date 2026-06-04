"""Phase 21 Slice S1 — DomainRepo (graceful domains read wrapper, 4계층 depth).

4계층 데이터 모델(User → Brand → **Domain** → Series → Video)의 Domain 계층을 read-only 로
나열한다. Phase 19 `/me/pkm-graph` 가 User→Brand 까지만 펼치던 것을 Domain→Series 까지
깊이 확장(additive)하기 위한 anchor. Supabase 사용 가능 시 PostgreSQL(domains),
아니면 in-memory dict 로 graceful fallback.

★ read-only — 본 slice 는 list_for_brand 만 (생성/수정 X). pkm-graph 집계 전용.
★ additive/graceful: domain 0 이거나 어떤 실패도 raise 금지 → 빈 리스트. 그러면 pkm-graph
  builder 가 Phase 19 와 byte-identical 그래프를 낸다 (깊이 노드 0).

설계 원칙 (BrandRepo 패턴 계승):
  1. graceful — 어떤 실패도 raise 금지, in-memory fallback / [] 반환 (P-GRACEFUL-001).
  2. 비동기 인터페이스 (BrandRepo / BrandMemoryRepo 와 호환).
  3. RLS 격리는 domains→brands→auth_user_id 체인이 강제 — 본 repo 는 brand_id keyed 라
     호출자(pkm-graph)가 이미 소유 검증된 brand_id 만 넘긴다 (교차 노출 0).

참조:
  - db/migrations/0001_init.sql §2 domains (id / brand_id NOT NULL / name NOT NULL / …)
  - backend/fastapi/db/repositories/brand_repo.py (graceful 패턴 복제 모델)
"""

from __future__ import annotations

import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)


class DomainRepo:
    """domains read repository — graceful Supabase or in-memory (4계층 Domain 계층).

    Usage:
        from backend.fastapi.db import DomainRepo, get_supabase

        repo = DomainRepo(supabase_client=get_supabase())
        domains = await repo.list_for_brand("brand-uuid")  # [] if none / failure
    """

    def __init__(
        self,
        supabase_client: Optional[Any] = None,
        in_memory_store: Optional[dict[str, list[dict[str, Any]]]] = None,
    ) -> None:
        self.client = supabase_client
        # key = brand_id, value = domain rows list (1:N)
        self.store: dict[str, list[dict[str, Any]]] = (
            in_memory_store if in_memory_store is not None else {}
        )

    # ─── helpers ─────────────────────────────────────────────────────

    def _use_supabase(self) -> bool:
        return self.client is not None

    # ─── operations (read-only) ──────────────────────────────────────

    async def list_for_brand(self, brand_id: str) -> list[dict[str, Any]]:
        """List 해당 brand 의 domain row 전체. 없거나 실패하면 빈 리스트 (graceful).

        ★ Phase 21 S1 (pkm-graph 깊이): Brand → Domain 펼침. domain 0 → [] → 깊이 노드 0
          (Phase 19 byte-identical).
        ★ RLS/격리: 호출자가 이미 소유 검증된 brand_id 만 넘긴다 (domains→brands 체인).
        """
        if self._use_supabase():
            try:
                resp = (
                    self.client.table("domains")  # type: ignore[union-attr]
                    .select("*")
                    .eq("brand_id", brand_id)
                    .execute()
                )
                data = getattr(resp, "data", None)
                if data is not None:
                    return list(data)
            except Exception as exc:
                logger.warning(
                    "domain_list_for_brand_failed: %s — falling back to in-memory",
                    exc.__class__.__name__,
                )
        # graceful in-memory fallback — 본 brand 의 domain 만.
        return list(self.store.get(brand_id, []))

    # ─── operations (create — Phase 22 S1) ───────────────────────────

    async def create(self, brand_id: str, name: str) -> Optional[dict[str, Any]]:
        """brand 아래 domain row 1개 생성 후 그 row(dict, id 포함) 반환. 실패 시 None (graceful).

        ★ BrandRepo.get_or_create_default INSERT 패턴 계승 — Supabase insert → id /
          없으면 in-memory uuid4 fallback. 어떤 실패도 raise 금지 → None (호출자가 안전 매핑).
        ★ RLS/격리: 호출자(라우터)가 이미 소유 검증한 brand_id 만 넘긴다 (domains→brands 체인).
          0003_rls_policy.sql 의 domains owner-insert 도 교차 계정 INSERT 를 강제 차단.
        ★ in-memory mirror: Supabase 성공 시에도 store 에 append → list_for_brand 즉시 반영.
        """
        payload: dict[str, Any] = {"brand_id": brand_id, "name": name}

        if self._use_supabase():
            try:
                resp = (
                    self.client.table("domains")  # type: ignore[union-attr]
                    .insert(payload)
                    .execute()
                )
                if resp and getattr(resp, "data", None):
                    row = resp.data[0]
                    if row.get("id"):
                        self.store.setdefault(brand_id, []).append(row)  # in-memory mirror
                        return dict(row)
                # data 없음 / id 없음 → graceful None.
                logger.warning(
                    "domain_create_no_id brand_id=%s — graceful None", brand_id,
                )
                return None
            except Exception as exc:
                logger.warning(
                    "domain_create_failed: %s — graceful None",
                    exc.__class__.__name__,
                )
                return None

        # graceful in-memory fallback — uuid4 로 결정적 unique id.
        from uuid import uuid4

        row = dict(payload)
        row["id"] = str(uuid4())
        self.store.setdefault(brand_id, []).append(row)
        return dict(row)

    async def get_or_create(
        self, brand_id: str, name: str,
    ) -> Optional[dict[str, Any]]:
        """brand 아래 name 일치 domain 이 있으면 그 row 를, 없으면 새로 생성해 반환 (idempotent).

        ★ Phase 25 S1 (wizard↔4계층 link): 브랜딩 택1 주제 → domain auto-seed 용 멱등 anchor.
          동일 주제 재택1 → 기존 domain 재사용(중복 0). list_for_brand → name 비교 → 없으면 create.
        ★ graceful: 어떤 실패도 raise 금지 → None (호출자 hook 이 graceful 매핑).
        ★ RLS/격리: 호출자(라우터)가 이미 소유 검증한 brand_id 만 넘긴다 (domains→brands 체인).
        """
        try:
            existing = await self.list_for_brand(brand_id)
            for row in existing:
                if isinstance(row, dict) and str(row.get("name")) == str(name):
                    return dict(row)  # 동일 name domain 재사용 (멱등)
            return await self.create(brand_id, name)
        except Exception as exc:  # pragma: no cover — graceful (어떤 실패도 None)
            logger.warning(
                "domain_get_or_create_failed: %s — graceful None",
                exc.__class__.__name__,
            )
            return None

    # ─── operations (edit/delete — Phase 24 S1) ──────────────────────
    #
    # ★ 소유(domain→brand→user) 검증은 endpoint 책임 — 본 repo 는 brand_id keyed 라
    #   auth_user_id 를 모른다. endpoint 가 _owns_domain 으로 소유를 확인한 뒤에만 호출한다.
    #   (in-memory store 는 brand_id 별 list 라 domain_id 로 전 brand 를 가로질러 검색.)
    # ★ BrandMemoryRepo.update_entry/delete_entry 패턴 계승 — Supabase update/delete + id eq +
    #   in-memory list mutation + graceful (어떤 실패도 raise 금지 → None/False).

    async def update_name(
        self, domain_id: str, name: str,
    ) -> Optional[dict[str, Any]]:
        """domain 의 name 을 갱신 후 갱신된 row 반환. 미존재/실패 → None (graceful).

        ★ 소유 검증은 호출 endpoint 가 선행 (domain→brand→auth_user_id).
        ★ in-memory mirror: Supabase 성공 시에도 store 의 동일 row 를 갱신 → list_for_brand 즉시 반영.
        """
        patch: dict[str, Any] = {"name": name}

        if self._use_supabase():
            try:
                resp = (
                    self.client.table("domains")  # type: ignore[union-attr]
                    .update(patch)
                    .eq("id", domain_id)
                    .execute()
                )
                if resp and getattr(resp, "data", None):
                    row = resp.data[0]
                    self._mirror_update(domain_id, patch)  # in-memory mirror
                    return dict(row)
                return None
            except Exception as exc:
                logger.warning(
                    "domain_update_failed: %s — graceful None",
                    exc.__class__.__name__,
                )
                return None

        # graceful in-memory fallback — 전 brand store 에서 id 일치 domain 갱신.
        for rows in self.store.values():
            for row in rows:
                if str(row.get("id")) == str(domain_id):
                    row.update(patch)
                    return dict(row)
        return None

    async def delete(self, domain_id: str) -> bool:
        """domain 삭제. 성공 True, 미존재/실패 False (graceful).

        ★ 소유 검증은 호출 endpoint 가 선행 (domain→brand→auth_user_id).
        ★ series 캐스케이드: Supabase 는 series.domain_id ON DELETE CASCADE 가 자동 처리.
          in-memory 일관성은 라우터가 SeriesRepo 로 별도 캐스케이드한다 (repo 는 자기 store 만).
        """
        if self._use_supabase():
            try:
                resp = (
                    self.client.table("domains")  # type: ignore[union-attr]
                    .delete()
                    .eq("id", domain_id)
                    .execute()
                )
                ok = bool(resp and getattr(resp, "data", None))
                if ok:
                    self._mirror_delete(domain_id)  # in-memory mirror
                return ok
            except Exception as exc:
                logger.warning(
                    "domain_delete_failed: %s — graceful False",
                    exc.__class__.__name__,
                )
                return False

        # graceful in-memory fallback — 전 brand store 에서 id 일치 domain 제거.
        return self._mirror_delete(domain_id)

    def _mirror_update(self, domain_id: str, patch: dict[str, Any]) -> None:
        """in-memory store 에서 domain_id 일치 row 를 patch 로 갱신 (Supabase mirror 보조)."""
        for rows in self.store.values():
            for row in rows:
                if str(row.get("id")) == str(domain_id):
                    row.update(patch)
                    return

    def _mirror_delete(self, domain_id: str) -> bool:
        """in-memory store 에서 domain_id 일치 row 제거. 제거했으면 True (Supabase mirror 보조)."""
        for rows in self.store.values():
            for i, row in enumerate(rows):
                if str(row.get("id")) == str(domain_id):
                    rows.pop(i)
                    return True
        return False

    def _reset_for_test(self) -> None:
        """테스트용 in-memory store 초기화 (BrandRepo._reset 패턴)."""
        self.store.clear()


__all__ = ["DomainRepo"]
