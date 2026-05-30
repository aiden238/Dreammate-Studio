"""Phase 9 Slice 2 — SelectionRepo (graceful CRUD wrapper).

plan 선택 영속화. Supabase 사용 가능 시 PostgreSQL(selected_plans), 아니면 in-memory dict 로 graceful fallback.

설계 원칙 (Phase 5 PlansRepo 패턴 계승):
  1. Phase 1 graceful 정책 계승 — 실패 시 raise 금지, in-memory fallback (P-GRACEFUL-001).
  2. 실 plans 테이블 정합 (ADR-030) — plan_id (→ plans.id) + selected_option_index (0–2, plan_candidates JSONB 배열 인덱스).
  3. 비동기 인터페이스 (PlansRepo 와 호환).
  4. RLS 강제는 0005_feedback_selection.sql 의 실 Supabase 에서만 (in-memory fallback 시 미적용 — security-review T3).

참조:
  - docs/contracts/db_schema.md §4.3 selected_plans (Phase 9 실 구현)
  - docs/decisions/phase_9_feedback_selection.md (ADR-030 §1 selected_plans + §3 SelectionRepo graceful)
  - backend/fastapi/db/repositories/plans_repo.py (graceful 패턴 복제 모델)
"""

from __future__ import annotations

import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)


class SelectionRepo:
    """selected_plans CRUD repository — graceful Supabase or in-memory.

    Usage:
        from backend.fastapi.db import SelectionRepo, get_supabase

        repo = SelectionRepo(supabase_client=get_supabase())
        await repo.select("plan-uuid", 1, selection_reason="이 안이 톤이 맞아요")
        row = await repo.get("plan-uuid")
    """

    def __init__(
        self,
        supabase_client: Optional[Any] = None,
        in_memory_store: Optional[dict[str, dict[str, Any]]] = None,
    ) -> None:
        self.client = supabase_client
        # key = plan_id, value = selection row (plan 당 최신 선택 1건 — selected_plans 1:1)
        self.store: dict[str, dict[str, Any]] = (
            in_memory_store if in_memory_store is not None else {}
        )

    # ─── helpers ─────────────────────────────────────────────────────

    def _use_supabase(self) -> bool:
        return self.client is not None

    # ─── operations ──────────────────────────────────────────────────

    async def select(
        self,
        plan_id: str,
        selected_option_index: int,
        *,
        auth_user_id: Optional[str] = None,
        selection_reason: Optional[str] = None,
    ) -> dict[str, Any]:
        """Record plan 선택. Supabase 실패 시 in-memory fallback (graceful).

        Args:
            plan_id: 선택 대상 plan (→ plans.id).
            selected_option_index: 선택한 candidate index (0–2, plan_candidates 배열 인덱스).
            auth_user_id: RLS 정합 (anon 시 None).
            selection_reason: 사용자 선택 사유 (호출자가 PII 마스킹 후 전달 권장 — T1).

        Returns:
            저장된 selection row dict.
        """
        payload: dict[str, Any] = {
            "plan_id": plan_id,
            "auth_user_id": auth_user_id,
            "selected_option_index": selected_option_index,
            "selection_reason": selection_reason,
        }

        if self._use_supabase():
            try:
                resp = (
                    self.client.table("selected_plans")  # type: ignore[union-attr]
                    .insert(payload)
                    .execute()
                )
                if resp and getattr(resp, "data", None):
                    row = resp.data[0]
                    self.store[plan_id] = row  # in-memory mirror (조회 일관성)
                    return row
            except Exception as exc:
                logger.warning(
                    "selection_select_failed: %s — falling back to in-memory",
                    exc.__class__.__name__,
                )
        # graceful in-memory fallback
        self.store[plan_id] = dict(payload)
        return self.store[plan_id]

    async def get(self, plan_id: str) -> Optional[dict[str, Any]]:
        """Get 선택 row by plan_id. Supabase 실패 시 in-memory fallback."""
        if self._use_supabase():
            try:
                resp = (
                    self.client.table("selected_plans")  # type: ignore[union-attr]
                    .select("*")
                    .eq("plan_id", plan_id)
                    .maybe_single()
                    .execute()
                )
                if resp and getattr(resp, "data", None):
                    return resp.data
            except Exception as exc:
                logger.warning(
                    "selection_get_failed: %s — falling back to in-memory",
                    exc.__class__.__name__,
                )
        return self.store.get(plan_id)

    def _reset_for_test(self) -> None:
        """테스트용 in-memory store 초기화 (Phase 5 _reset 패턴)."""
        self.store.clear()


__all__ = ["SelectionRepo"]
