"""Phase 5 Slice 2 — PlansRepo (graceful CRUD wrapper).

Supabase 사용 가능 시 PostgreSQL 영속화, 아니면 in-memory dict 로 graceful fallback.

설계 원칙:
  1. Phase 1 graceful 정책 계승 — 실패 시 raise 금지, in-memory fallback.
  2. routers/plans.py 의 기존 `_plan_store: dict` 와 호환 (instance 주입).
  3. 비동기 인터페이스 (Phase 5 Slice 4 SSE Progress 와 호환).
  4. RLS 강제는 Slice 4 ADR-021 에서 활성화 (본 Slice 는 baseline).

참조:
  - docs/contracts/db_schema.md §plans (Phase 5 Slice 2 본문)
  - docs/decisions/phase_5_supabase_adoption.md (ADR-020 §Implementation impact)
  - meta/validations/2026-05-29_phase-5-pre-entry_self.md §V5, §V6
"""

from __future__ import annotations

import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)


class PlansRepo:
    """Plans CRUD repository — graceful Supabase or in-memory.

    Usage:
        from backend.fastapi.db import PlansRepo, get_supabase

        repo = PlansRepo(supabase_client=get_supabase(), in_memory_store=_plan_store)
        plan = await repo.get("plan-uuid")
        await repo.create("plan-uuid", {"mode": "discovery"})
        await repo.update("plan-uuid", {"status": "generated"})
        await repo.delete("plan-uuid")
    """

    def __init__(
        self,
        supabase_client: Optional[Any] = None,
        in_memory_store: Optional[dict[str, dict[str, Any]]] = None,
    ) -> None:
        self.client = supabase_client
        self.store: dict[str, dict[str, Any]] = (
            in_memory_store if in_memory_store is not None else {}
        )

    # ─── helpers ─────────────────────────────────────────────────────

    def _use_supabase(self) -> bool:
        return self.client is not None

    # ─── CRUD ────────────────────────────────────────────────────────

    async def get(self, plan_id: str) -> Optional[dict[str, Any]]:
        """Get plan by id. Supabase 실패 시 in-memory fallback."""
        if self._use_supabase():
            try:
                resp = (
                    self.client.table("plans")  # type: ignore[union-attr]
                    .select("*")
                    .eq("id", plan_id)
                    .maybe_single()
                    .execute()
                )
                if resp and getattr(resp, "data", None):
                    return resp.data
            except Exception as exc:
                logger.warning(
                    "plans_get_failed: %s — falling back to in-memory",
                    exc.__class__.__name__,
                )
        return self.store.get(plan_id)

    async def create(
        self, plan_id: str, payload: dict[str, Any]
    ) -> dict[str, Any]:
        """Create plan. Supabase 실패 시 in-memory 저장 (graceful)."""
        if self._use_supabase():
            try:
                resp = (
                    self.client.table("plans")  # type: ignore[union-attr]
                    .insert({**payload, "id": plan_id})
                    .execute()
                )
                if resp and getattr(resp, "data", None):
                    return resp.data[0]
            except Exception as exc:
                logger.warning(
                    "plans_create_failed: %s — falling back to in-memory",
                    exc.__class__.__name__,
                )
        # graceful in-memory fallback
        self.store[plan_id] = dict(payload)
        return self.store[plan_id]

    async def update(
        self, plan_id: str, patch: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
        """Patch plan. Supabase 실패 또는 plan_id 없음 시 in-memory fallback."""
        if self._use_supabase():
            try:
                resp = (
                    self.client.table("plans")  # type: ignore[union-attr]
                    .update(patch)
                    .eq("id", plan_id)
                    .execute()
                )
                if resp and getattr(resp, "data", None):
                    return resp.data[0]
            except Exception as exc:
                logger.warning(
                    "plans_update_failed: %s — falling back to in-memory",
                    exc.__class__.__name__,
                )
        if plan_id in self.store:
            self.store[plan_id].update(patch)
            return self.store[plan_id]
        return None

    async def delete(self, plan_id: str) -> bool:
        """Delete plan. Supabase 실패 시 in-memory fallback. Returns True if deleted."""
        if self._use_supabase():
            try:
                self.client.table("plans").delete().eq("id", plan_id).execute()  # type: ignore[union-attr]
                # Supabase delete 는 항상 True (RLS 통과 + row 미존재도 200).
                # in-memory 도 같이 정리.
                existed = self.store.pop(plan_id, None) is not None
                return existed or True
            except Exception as exc:
                logger.warning(
                    "plans_delete_failed: %s — falling back to in-memory",
                    exc.__class__.__name__,
                )
        return self.store.pop(plan_id, None) is not None


__all__ = ["PlansRepo"]
