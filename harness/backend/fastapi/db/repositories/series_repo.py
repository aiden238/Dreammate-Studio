"""Phase 21 Slice S1 — SeriesRepo (graceful series read wrapper, 4계층 depth).

4계층 데이터 모델(User → Brand → Domain → **Series** → Video)의 Series 계층을 read-only 로
나열한다. Phase 19 `/me/pkm-graph` 깊이 확장(additive)의 최하단(Domain→Series). Supabase
사용 가능 시 PostgreSQL(series), 아니면 in-memory dict 로 graceful fallback.

★ read-only — 본 slice 는 list_for_domain 만 (생성/수정 X). pkm-graph 집계 전용.
★ additive/graceful: series 0 이거나 어떤 실패도 raise 금지 → 빈 리스트. 그러면 pkm-graph
  builder 가 Phase 19 와 byte-identical 그래프를 낸다 (깊이 노드 0).

설계 원칙 (BrandRepo 패턴 계승):
  1. graceful — 어떤 실패도 raise 금지, in-memory fallback / [] 반환 (P-GRACEFUL-001).
  2. 비동기 인터페이스 (BrandRepo / DomainRepo 와 호환).
  3. RLS 격리는 series→domains→brands→auth_user_id 체인이 강제 — 본 repo 는 domain_id keyed 라
     호출자(pkm-graph)가 이미 소유 검증된 brand 의 domain_id 만 넘긴다 (교차 노출 0).

참조:
  - db/migrations/0001_init.sql §3 series (id / domain_id NOT NULL / name NOT NULL / target / …)
  - backend/fastapi/db/repositories/brand_repo.py (graceful 패턴 복제 모델)
"""

from __future__ import annotations

import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)


class SeriesRepo:
    """series read repository — graceful Supabase or in-memory (4계층 Series 계층).

    Usage:
        from backend.fastapi.db import SeriesRepo, get_supabase

        repo = SeriesRepo(supabase_client=get_supabase())
        series = await repo.list_for_domain("domain-uuid")  # [] if none / failure
    """

    def __init__(
        self,
        supabase_client: Optional[Any] = None,
        in_memory_store: Optional[dict[str, list[dict[str, Any]]]] = None,
    ) -> None:
        self.client = supabase_client
        # key = domain_id, value = series rows list (1:N)
        self.store: dict[str, list[dict[str, Any]]] = (
            in_memory_store if in_memory_store is not None else {}
        )

    # ─── helpers ─────────────────────────────────────────────────────

    def _use_supabase(self) -> bool:
        return self.client is not None

    # ─── operations (read-only) ──────────────────────────────────────

    async def list_for_domain(self, domain_id: str) -> list[dict[str, Any]]:
        """List 해당 domain 의 series row 전체. 없거나 실패하면 빈 리스트 (graceful).

        ★ Phase 21 S1 (pkm-graph 깊이): Domain → Series 펼침. series 0 → [] → 깊이 노드 0
          (Phase 19 byte-identical).
        ★ RLS/격리: 호출자가 이미 소유 검증된 brand 의 domain_id 만 넘긴다 (series→domains 체인).
        """
        if self._use_supabase():
            try:
                resp = (
                    self.client.table("series")  # type: ignore[union-attr]
                    .select("*")
                    .eq("domain_id", domain_id)
                    .execute()
                )
                data = getattr(resp, "data", None)
                if data is not None:
                    return list(data)
            except Exception as exc:
                logger.warning(
                    "series_list_for_domain_failed: %s — falling back to in-memory",
                    exc.__class__.__name__,
                )
        # graceful in-memory fallback — 본 domain 의 series 만.
        return list(self.store.get(domain_id, []))

    # ─── operations (create — Phase 22 S1) ───────────────────────────

    async def create(self, domain_id: str, name: str) -> Optional[dict[str, Any]]:
        """domain 아래 series row 1개 생성 후 그 row(dict, id 포함) 반환. 실패 시 None (graceful).

        ★ BrandRepo.get_or_create_default INSERT 패턴 계승 — Supabase insert → id /
          없으면 in-memory uuid4 fallback. 어떤 실패도 raise 금지 → None (호출자가 안전 매핑).
        ★ RLS/격리: 호출자(라우터)가 이미 소유 검증한 domain_id 만 넘긴다 (series→domains→brands 체인).
          0003_rls_policy.sql 의 series owner-insert 도 교차 계정 INSERT 를 강제 차단.
        ★ in-memory mirror: Supabase 성공 시에도 store 에 append → list_for_domain 즉시 반영.
        """
        payload: dict[str, Any] = {"domain_id": domain_id, "name": name}

        if self._use_supabase():
            try:
                resp = (
                    self.client.table("series")  # type: ignore[union-attr]
                    .insert(payload)
                    .execute()
                )
                if resp and getattr(resp, "data", None):
                    row = resp.data[0]
                    if row.get("id"):
                        self.store.setdefault(domain_id, []).append(row)  # in-memory mirror
                        return dict(row)
                # data 없음 / id 없음 → graceful None.
                logger.warning(
                    "series_create_no_id domain_id=%s — graceful None", domain_id,
                )
                return None
            except Exception as exc:
                logger.warning(
                    "series_create_failed: %s — graceful None",
                    exc.__class__.__name__,
                )
                return None

        # graceful in-memory fallback — uuid4 로 결정적 unique id.
        from uuid import uuid4

        row = dict(payload)
        row["id"] = str(uuid4())
        self.store.setdefault(domain_id, []).append(row)
        return dict(row)

    def _reset_for_test(self) -> None:
        """테스트용 in-memory store 초기화 (BrandRepo._reset 패턴)."""
        self.store.clear()


__all__ = ["SeriesRepo"]
