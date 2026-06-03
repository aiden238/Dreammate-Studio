"""Phase 17 가-S3 — BrandRepo (graceful brand foundation, default-brand get-or-create).

MVP 는 `brands` row 를 한 번도 생성하지 않아 4계층(User→Brand→…)이 schema-only 였다.
그 결과 brand_memory_entries(brand_id keyed)에 anchor 가 없어 가-S2 brand_memory 주입이
실 인증 사용자에게 한 번도 발화하지 못했다(항상 byte-identical). 본 repo 는 인증 사용자에게
**기본 브랜드**를 보장(get-or-create)하여 brand_memory 가 붙을 anchor 를 만든다 —
풀 브랜드 관리 UI 없이(후속 슬라이스).

설계 원칙 (BrandMemoryRepo 패턴 계승):
  1. graceful — 어떤 실패도 raise 금지, in-memory fallback / None 반환 (P-GRACEFUL-001).
  2. 비동기 인터페이스 (BrandMemoryRepo 와 호환).
  3. idempotent — get_or_create_default 는 항상 query-before-insert (2번째 default 생성 0).
  4. RLS 격리는 0003_rls_policy.sql 의 brands_owner_insert (auth_user_id = auth.uid()) 가 강제.
     본 repo 는 오직 요청 auth_user_id 만 다룸 — 교차 계정 접근 0.

참조:
  - db/migrations/0001_init.sql §1 brands (id / auth_user_id NOT NULL / name NOT NULL / …)
  - db/migrations/0003_rls_policy.sql §1 brands_owner_insert (RLS)
  - backend/fastapi/db/repositories/brand_memory_repo.py (graceful 패턴 복제 모델)
"""

from __future__ import annotations

import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)

# 기본 브랜드 이름 (사용자가 명시 브랜드를 만들기 전 anchor 용).
DEFAULT_BRAND_NAME = "기본 브랜드"


class BrandRepo:
    """brands get-or-create repository — graceful Supabase or in-memory.

    Usage:
        from backend.fastapi.db import BrandRepo, get_supabase

        repo = BrandRepo(supabase_client=get_supabase())
        brand_id = await repo.get_or_create_default("auth-user-uuid")  # idempotent
        existing = await repo.get_default_brand_id("auth-user-uuid")
    """

    def __init__(
        self,
        supabase_client: Optional[Any] = None,
        in_memory_store: Optional[dict[str, list[dict[str, Any]]]] = None,
    ) -> None:
        self.client = supabase_client
        # key = auth_user_id, value = brand rows list (1:N, 가장 최근이 마지막).
        self.store: dict[str, list[dict[str, Any]]] = (
            in_memory_store if in_memory_store is not None else {}
        )

    # ─── helpers ─────────────────────────────────────────────────────

    def _use_supabase(self) -> bool:
        return self.client is not None

    # ─── operations ──────────────────────────────────────────────────

    async def get_default_brand_id(self, auth_user_id: str) -> Optional[str]:
        """user 소유 brand id 반환(여러 개면 가장 최근). 없으면 None. 실패도 None (graceful)."""
        if self._use_supabase():
            try:
                resp = (
                    self.client.table("brands")  # type: ignore[union-attr]
                    .select("id")
                    .eq("auth_user_id", auth_user_id)
                    .order("created_at", desc=True)
                    .limit(1)
                    .execute()
                )
                data = getattr(resp, "data", None)
                if data:
                    bid = data[0].get("id")
                    return str(bid) if bid else None
                return None
            except Exception as exc:
                logger.warning(
                    "brand_get_default_failed: %s — falling back to in-memory",
                    exc.__class__.__name__,
                )
        # graceful in-memory fallback — 가장 최근(append 순서 마지막).
        rows = self.store.get(auth_user_id, [])
        if rows:
            bid = rows[-1].get("id")
            return str(bid) if bid else None
        return None

    async def get_or_create_default(
        self,
        auth_user_id: str,
        *,
        name: str = DEFAULT_BRAND_NAME,
    ) -> Optional[str]:
        """user 의 기본 brand id 반환 — 없으면 brands row 1개 생성 후 그 id 반환.

        ★ idempotent: 항상 query(get_default_brand_id) 먼저 → 있으면 그대로 반환(2번째 default
          생성 0). 없을 때만 INSERT.
        ★ graceful: 조회/생성 어떤 단계 실패도 raise 금지 → None 반환(호출자가 주입 skip).
        ★ PII/격리: 오직 요청 auth_user_id 의 brand 만 다룸. RLS(brands_owner_insert) 가 강제.

        Args:
            auth_user_id: 대상 사용자 (→ brands.auth_user_id, Supabase auth.users.id).
            name: 생성 시 brand 이름 (기본 "기본 브랜드").

        Returns:
            기존 또는 새로 생성된 brand id. 실패 시 None.
        """
        # 1. query-before-insert — 기존 brand 있으면 그대로 (idempotent).
        existing = await self.get_default_brand_id(auth_user_id)
        if existing:
            return existing

        # 2. 없으면 INSERT.
        payload: dict[str, Any] = {
            "auth_user_id": auth_user_id,
            "name": name,
        }

        if self._use_supabase():
            try:
                resp = (
                    self.client.table("brands")  # type: ignore[union-attr]
                    .insert(payload)
                    .execute()
                )
                if resp and getattr(resp, "data", None):
                    row = resp.data[0]
                    bid = row.get("id")
                    if bid:
                        self.store.setdefault(auth_user_id, []).append(row)  # in-memory mirror
                        return str(bid)
                # data 없음 / id 없음 → graceful None (주입 skip, 흐름 차단 0).
                logger.warning(
                    "brand_create_no_id auth_user_id=%s — graceful None", auth_user_id,
                )
                return None
            except Exception as exc:
                logger.warning(
                    "brand_create_failed: %s — graceful None (no injection)",
                    exc.__class__.__name__,
                )
                return None

        # graceful in-memory fallback — id 생성(테스트/오프라인). uuid4 로 결정적 unique.
        from uuid import uuid4

        bid = str(uuid4())
        row = dict(payload)
        row["id"] = bid
        self.store.setdefault(auth_user_id, []).append(row)
        return bid

    def _reset_for_test(self) -> None:
        """테스트용 in-memory store 초기화 (BrandMemoryRepo._reset 패턴)."""
        self.store.clear()


__all__ = ["BrandRepo", "DEFAULT_BRAND_NAME"]
