"""Phase 9 Slice 2 — BrandMemoryRepo (graceful CRUD wrapper, 준비용).

Brand Memory entry 영속화 (수동/준비용). Supabase 사용 가능 시 PostgreSQL(brand_memory_entries),
아니면 in-memory dict 로 graceful fallback.

★ 준비만 (ADR-031 / NG1):
  - 본 repo 는 수동/준비용 entry CRUD (add_entry / list_for_brand) 만 제공.
  - 자동 추출 agent (P-AUX-2 brand_memory_extractor) 는 Phase 9 미구현 — Phase 10+ (MVP 운영 + 데이터 누적 후).
  - 자동 추출 로직 / orchestration 연결 / 호출 0 (NG1).

설계 원칙 (Phase 5 PlansRepo 패턴 계승):
  1. graceful — 실패 시 raise 금지, in-memory fallback (P-GRACEFUL-001).
  2. 비동기 인터페이스 (PlansRepo 와 호환).
  3. entry_type enum 5종 (preferred_tone / avoid_phrase / preferred_phrase / success_pattern / rejection_pattern).
  4. RLS 강제는 0005_feedback_selection.sql 의 실 Supabase 에서만 (brands 를 통한 user 격리).

참조:
  - docs/contracts/db_schema.md §6 brand_memory_entries
  - docs/decisions/phase_9_brand_memory_prep.md (ADR-031 — 준비만, agent 미구현 Phase 10+)
  - backend/fastapi/db/repositories/plans_repo.py (graceful 패턴 복제 모델)
"""

from __future__ import annotations

import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)

_VALID_ENTRY_TYPES = {
    "preferred_tone",
    "avoid_phrase",
    "preferred_phrase",
    "success_pattern",
    "rejection_pattern",
}


class BrandMemoryRepo:
    """brand_memory_entries CRUD repository — graceful Supabase or in-memory (준비용).

    Usage:
        from backend.fastapi.db import BrandMemoryRepo, get_supabase

        repo = BrandMemoryRepo(supabase_client=get_supabase())
        await repo.add_entry("brand-uuid", "preferred_tone", "친근하고 담백한 톤")
        entries = await repo.list_for_brand("brand-uuid")
    """

    def __init__(
        self,
        supabase_client: Optional[Any] = None,
        in_memory_store: Optional[dict[str, list[dict[str, Any]]]] = None,
    ) -> None:
        self.client = supabase_client
        # key = brand_id, value = entries list (1:N)
        self.store: dict[str, list[dict[str, Any]]] = (
            in_memory_store if in_memory_store is not None else {}
        )

    # ─── helpers ─────────────────────────────────────────────────────

    def _use_supabase(self) -> bool:
        return self.client is not None

    # ─── operations (수동/준비용 — 자동 추출 X) ───────────────────────

    async def add_entry(
        self,
        brand_id: str,
        entry_type: str,
        content: str,
        *,
        source_plan_id: Optional[str] = None,
        confidence: float = 0.5,
    ) -> dict[str, Any]:
        """Add Brand Memory entry (수동/준비용). Supabase 실패 시 in-memory fallback.

        Args:
            brand_id: 대상 brand (→ brands.id).
            entry_type: preferred_tone | avoid_phrase | preferred_phrase | success_pattern | rejection_pattern.
            content: entry 내용.
            source_plan_id: 출처 plan (→ plans.id, 선택).
            confidence: 0–1 신뢰도 (수동 시 기본 0.5).

        Returns:
            저장된 entry row dict.
        """
        payload: dict[str, Any] = {
            "brand_id": brand_id,
            "entry_type": entry_type,
            "content": content,
            "source_plan_id": source_plan_id,
            "confidence": confidence,
            "is_user_locked": False,
        }

        if self._use_supabase():
            try:
                resp = (
                    self.client.table("brand_memory_entries")  # type: ignore[union-attr]
                    .insert(payload)
                    .execute()
                )
                if resp and getattr(resp, "data", None):
                    row = resp.data[0]
                    self.store.setdefault(brand_id, []).append(row)  # in-memory mirror
                    return row
            except Exception as exc:
                logger.warning(
                    "brand_memory_add_failed: %s — falling back to in-memory",
                    exc.__class__.__name__,
                )
        # graceful in-memory fallback
        row = dict(payload)
        self.store.setdefault(brand_id, []).append(row)
        return row

    async def list_for_brand(self, brand_id: str) -> list[dict[str, Any]]:
        """List 해당 brand 의 entries. Supabase 실패 시 in-memory fallback."""
        if self._use_supabase():
            try:
                resp = (
                    self.client.table("brand_memory_entries")  # type: ignore[union-attr]
                    .select("*")
                    .eq("brand_id", brand_id)
                    .execute()
                )
                if resp and getattr(resp, "data", None) is not None:
                    return list(resp.data)
            except Exception as exc:
                logger.warning(
                    "brand_memory_list_failed: %s — falling back to in-memory",
                    exc.__class__.__name__,
                )
        return list(self.store.get(brand_id, []))

    def _reset_for_test(self) -> None:
        """테스트용 in-memory store 초기화 (Phase 5 _reset 패턴)."""
        self.store.clear()


__all__ = ["BrandMemoryRepo"]
