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

    def _reset_for_test(self) -> None:
        """테스트용 in-memory store 초기화 (BrandRepo._reset 패턴)."""
        self.store.clear()


__all__ = ["DomainRepo"]
