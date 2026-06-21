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
import uuid
from typing import Any, Optional

logger = logging.getLogger(__name__)

_VALID_ENTRY_TYPES = {
    "preferred_tone",
    "avoid_phrase",
    "preferred_phrase",
    "success_pattern",
    "rejection_pattern",
}


def _identity(row: dict[str, Any]) -> str:
    """행의 식별자 값 — 실 PK 는 entry_id(0005), 호출측 컨벤션은 id. 둘 다 허용."""
    return str(row.get("entry_id") or row.get("id") or "")


def _norm(row: dict[str, Any]) -> dict[str, Any]:
    """brand_memory_entries 행을 호출측('id') 컨벤션과 정합시킨다.

    ★ 실 DB PK 는 entry_id(`0005_feedback_selection.sql:62`)라 select/insert 응답은 entry_id 만
    가진다. me.py `_pkm_node`/`_brand_owns_entry` 등 호출측은 다른 PKM(pkm_entries=id)과 대칭으로
    row['id'] 를 읽으므로, entry_id → id 미러를 보장해 그래프 노드 id·소유검증·라운드트립이 깨지지
    않게 한다(스키마 quirk 를 repo 경계에 격리 — me.py 무변경).
    """
    if isinstance(row, dict) and row.get("id") is None and row.get("entry_id") is not None:
        row = {**row, "id": row["entry_id"]}
    return row


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
                    row = _norm(resp.data[0])  # entry_id → id 미러(호출측 컨벤션)
                    self.store.setdefault(brand_id, []).append(row)  # in-memory mirror
                    return row
            except Exception as exc:
                logger.warning(
                    "brand_memory_add_failed: %s — falling back to in-memory",
                    exc.__class__.__name__,
                )
        # graceful in-memory fallback — entry_id 생성(실 DB gen_random_uuid 대응)해 식별 가능하게.
        row = dict(payload)
        row["entry_id"] = str(uuid.uuid4())
        row = _norm(row)
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
                    return [_norm(r) for r in resp.data]  # entry_id → id 미러
            except Exception as exc:
                logger.warning(
                    "brand_memory_list_failed: %s — falling back to in-memory",
                    exc.__class__.__name__,
                )
        return [_norm(r) for r in self.store.get(brand_id, [])]

    # ─── 큐레이션 (Phase 19 Slice S4 — 수동 잠금/편집/삭제) ──────────────
    #
    # ★ 소유(brand→user) 검증은 endpoint 책임 — 본 repo 는 brand_id keyed 라 auth_user_id 를
    #   모른다. endpoint 가 BrandRepo 로 brand 소유를 확인한 뒤에만 아래 메서드를 호출한다.
    #   (in-memory store 는 brand_id 가 unique 하므로 entry_id 만으로 안전하게 분기 가능.)

    async def update_entry(
        self,
        entry_id: str,
        *,
        content: Optional[str] = None,
        is_user_locked: Optional[bool] = None,
    ) -> Optional[dict[str, Any]]:
        """브랜드 PKM entry 의 content / is_user_locked 부분 갱신. 미존재/실패 → None (graceful).

        ★ 소유 검증은 호출 endpoint 가 선행 (brand→auth_user_id). 변경 필드 없으면 현재 행 반환.
        """
        patch: dict[str, Any] = {}
        if content is not None:
            patch["content"] = content
        if is_user_locked is not None:
            patch["is_user_locked"] = is_user_locked

        # 변경 필드 없음 → no-op, 현재 행 조회 후 반환.
        if not patch:
            return self._find_in_memory(entry_id)

        if self._use_supabase():
            try:
                resp = (
                    self.client.table("brand_memory_entries")  # type: ignore[union-attr]
                    .update(patch)
                    .eq("entry_id", entry_id)  # ★ 실 PK 컬럼(0005) — 'id' 아님
                    .execute()
                )
                if resp and getattr(resp, "data", None):
                    return _norm(resp.data[0])
                return None
            except Exception as exc:
                logger.warning(
                    "brand_memory_update_failed: %s — graceful None",
                    exc.__class__.__name__,
                )
                return None

        # graceful in-memory fallback — 전 brand store 에서 entry_id(=노출 id) 일치 행 갱신.
        for rows in self.store.values():
            for row in rows:
                if _identity(row) == str(entry_id):
                    row.update(patch)
                    return _norm(row)
        return None

    async def delete_entry(self, entry_id: str) -> bool:
        """브랜드 PKM entry 삭제. 성공 True, 미존재/실패 False (graceful).

        ★ 소유 검증은 호출 endpoint 가 선행 (brand→auth_user_id).
        """
        if self._use_supabase():
            try:
                resp = (
                    self.client.table("brand_memory_entries")  # type: ignore[union-attr]
                    .delete()
                    .eq("entry_id", entry_id)  # ★ 실 PK 컬럼(0005) — 'id' 아님
                    .execute()
                )
                if resp and getattr(resp, "data", None):
                    return True
                return False
            except Exception as exc:
                logger.warning(
                    "brand_memory_delete_failed: %s — graceful False",
                    exc.__class__.__name__,
                )
                return False

        # graceful in-memory fallback — 전 brand store 에서 entry_id(=노출 id) 일치 행 제거.
        for rows in self.store.values():
            for i, row in enumerate(rows):
                if _identity(row) == str(entry_id):
                    rows.pop(i)
                    return True
        return False

    def _find_in_memory(self, entry_id: str) -> Optional[dict[str, Any]]:
        """in-memory store 전체에서 entry_id(=노출 id) 일치 행 검색 (no-op update 보조)."""
        for rows in self.store.values():
            for row in rows:
                if _identity(row) == str(entry_id):
                    return _norm(row)
        return None

    def _reset_for_test(self) -> None:
        """테스트용 in-memory store 초기화 (Phase 5 _reset 패턴)."""
        self.store.clear()


__all__ = ["BrandMemoryRepo"]
