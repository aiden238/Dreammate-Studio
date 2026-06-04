"""Phase 17 다-S3 — PkmRepo (graceful 개인 PKM CRUD wrapper).

개인(계정) 단위 PKM entry 영속화 — auth_user_id 로 격리되는 brand-독립(User 계층) 메모리.
Supabase 사용 가능 시 PostgreSQL(pkm_entries), 아니면 in-memory dict 로 graceful fallback.

★ 설계 출처: meta/proposals/2026-06-03_pkm-rag-orchestrator-design.md §8.2 (pkm_entries) +
  §2/§6.2 (우선순위: user_locked/personal > brand). 본 slice 는 scope='personal' 만 다룬다
  (series 는 후속). 자동 추출/승격 X — 수동/준비용 CRUD 만 (NG12 계승).

설계 원칙 (BrandMemoryRepo 패턴 계승):
  1. graceful — 어떤 실패도 raise 금지, in-memory fallback (P-GRACEFUL-001).
  2. 비동기 인터페이스 (BrandMemoryRepo / BrandRepo 와 호환).
  3. entry_type enum 5종 (preferred_tone / avoid_phrase / preferred_phrase / success_pattern / rejection_pattern) — brand_memory_entries 정합.
  4. RLS 격리는 0006_pkm_entries.sql 의 pkm_entries_user_isolation (auth_user_id = auth.uid()) 가 강제.
     본 repo 는 오직 요청 auth_user_id 만 다룸 — 교차 계정 접근 0.

참조:
  - db/migrations/0006_pkm_entries.sql (pkm_entries 스키마 + RLS)
  - backend/fastapi/db/repositories/brand_memory_repo.py (graceful 패턴 복제 모델)
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


class PkmRepo:
    """pkm_entries CRUD repository — graceful Supabase or in-memory (개인 PKM).

    Usage:
        from backend.fastapi.db import PkmRepo, get_supabase

        repo = PkmRepo(supabase_client=get_supabase())
        await repo.add_entry("auth-user-uuid", "preferred_tone", "담백하고 군더더기 없는 톤")
        entries = await repo.list_for_user("auth-user-uuid")  # scope='personal'
    """

    def __init__(
        self,
        supabase_client: Optional[Any] = None,
        in_memory_store: Optional[dict[str, list[dict[str, Any]]]] = None,
    ) -> None:
        self.client = supabase_client
        # key = auth_user_id, value = entries list (1:N)
        self.store: dict[str, list[dict[str, Any]]] = (
            in_memory_store if in_memory_store is not None else {}
        )

    # ─── helpers ─────────────────────────────────────────────────────

    def _use_supabase(self) -> bool:
        return self.client is not None

    # ─── operations (수동/준비용 — 자동 추출 X, NG12) ─────────────────

    async def add_entry(
        self,
        auth_user_id: str,
        entry_type: str,
        content: str,
        *,
        scope: str = "personal",
        confidence: float = 0.5,
        is_user_locked: bool = False,
        source_plan_id: Optional[str] = None,
    ) -> dict[str, Any]:
        """Add 개인 PKM entry. Supabase 실패 시 in-memory fallback (graceful).

        Args:
            auth_user_id: 대상 사용자 (→ pkm_entries.auth_user_id, Supabase auth.users.id).
            entry_type: preferred_tone | avoid_phrase | preferred_phrase | success_pattern | rejection_pattern.
            content: entry 내용.
            scope: 'personal' (this slice) | 'series' (후속). 기본 'personal'.
            confidence: 0–1 신뢰도 (수동 시 기본 0.5).
            is_user_locked: ★ user_locked 최우선 (설계 §6.2). 기본 False.
            source_plan_id: 출처 plan (→ plans.id, 선택 — Phase 26 S2 provenance).
                기본 None → 미전달(기존 호출자) 시 출처 미기록 = byte-identical
                (brand_memory_repo.add_entry source_plan_id 미러).

        Returns:
            저장된 entry row dict.
        """
        payload: dict[str, Any] = {
            "scope": scope,
            "auth_user_id": auth_user_id,
            "entry_type": entry_type,
            "content": content,
            "confidence": confidence,
            "is_user_locked": is_user_locked,
            "source_plan_id": source_plan_id,
        }

        if self._use_supabase():
            try:
                resp = (
                    self.client.table("pkm_entries")  # type: ignore[union-attr]
                    .insert(payload)
                    .execute()
                )
                if resp and getattr(resp, "data", None):
                    row = resp.data[0]
                    self.store.setdefault(auth_user_id, []).append(row)  # in-memory mirror
                    return row
            except Exception as exc:
                logger.warning(
                    "pkm_add_failed: %s — falling back to in-memory",
                    exc.__class__.__name__,
                )
        # graceful in-memory fallback
        row = dict(payload)
        self.store.setdefault(auth_user_id, []).append(row)
        return row

    async def list_for_user(
        self,
        auth_user_id: str,
        *,
        scope: str = "personal",
    ) -> list[dict[str, Any]]:
        """List 해당 user 의 PKM entries (scope 필터). Supabase 실패 시 in-memory fallback.

        ★ PII/격리: 오직 요청 auth_user_id 의 entry 만 반환(RLS 격리 데이터). 교차 계정 접근 0.
        """
        if self._use_supabase():
            try:
                resp = (
                    self.client.table("pkm_entries")  # type: ignore[union-attr]
                    .select("*")
                    .eq("auth_user_id", auth_user_id)
                    .eq("scope", scope)
                    .execute()
                )
                if resp and getattr(resp, "data", None) is not None:
                    return list(resp.data)
            except Exception as exc:
                logger.warning(
                    "pkm_list_failed: %s — falling back to in-memory",
                    exc.__class__.__name__,
                )
        # in-memory fallback — 본인 user + scope 일치만 (격리).
        return [
            row
            for row in self.store.get(auth_user_id, [])
            if row.get("scope", "personal") == scope
        ]

    # ─── 큐레이션 (Phase 19 Slice S4 — 수동 잠금/편집/삭제) ──────────────

    async def update_entry(
        self,
        entry_id: str,
        *,
        auth_user_id: str,
        content: Optional[str] = None,
        is_user_locked: Optional[bool] = None,
    ) -> Optional[dict[str, Any]]:
        """개인 PKM entry 의 content / is_user_locked 를 부분 갱신 (RLS 격리).

        ★ RLS/격리: id 일치 + **auth_user_id 일치** 행만 갱신 (교차 계정 수정 0). 미소유/미존재 →
          None. Supabase 는 .eq("auth_user_id") 로 강제, in-memory 는 본인 store 만 순회.
        ★ graceful: 어떤 실패도 raise 금지 → None (호출자가 404 로 매핑). 변경 필드 없으면 현재 행 반환.

        Args:
            entry_id: 대상 pkm_entries.id.
            auth_user_id: 요청 사용자 (소유 검증 키).
            content: 새 content (None 이면 미변경).
            is_user_locked: 새 잠금 상태 (None 이면 미변경).

        Returns:
            갱신된 entry row dict, 미소유/미존재/실패 시 None.
        """
        patch: dict[str, Any] = {}
        if content is not None:
            patch["content"] = content
        if is_user_locked is not None:
            patch["is_user_locked"] = is_user_locked

        # 변경 필드 없음 → 소유 검증 겸 현재 행 조회 후 반환 (no-op, 격리 유지).
        if not patch:
            for row in await self.list_for_user(auth_user_id):
                if str(row.get("id")) == str(entry_id):
                    return row
            return None

        if self._use_supabase():
            try:
                resp = (
                    self.client.table("pkm_entries")  # type: ignore[union-attr]
                    .update(patch)
                    .eq("id", entry_id)
                    .eq("auth_user_id", auth_user_id)  # ★ RLS 소유 강제
                    .execute()
                )
                if resp and getattr(resp, "data", None):
                    return resp.data[0]
                # 0 rows updated → 미소유 또는 미존재.
                return None
            except Exception as exc:
                logger.warning(
                    "pkm_update_failed: %s — graceful None",
                    exc.__class__.__name__,
                )
                return None

        # graceful in-memory fallback — 본인 store 의 id 일치 행만 (격리).
        for row in self.store.get(auth_user_id, []):
            if str(row.get("id")) == str(entry_id):
                row.update(patch)
                return row
        return None

    async def delete_entry(
        self,
        entry_id: str,
        *,
        auth_user_id: str,
    ) -> bool:
        """개인 PKM entry 삭제 (RLS 격리). 성공 True, 미소유/미존재/실패 False (graceful).

        ★ RLS/격리: id + auth_user_id 일치 행만 삭제 (교차 계정 삭제 0).
        """
        if self._use_supabase():
            try:
                resp = (
                    self.client.table("pkm_entries")  # type: ignore[union-attr]
                    .delete()
                    .eq("id", entry_id)
                    .eq("auth_user_id", auth_user_id)  # ★ RLS 소유 강제
                    .execute()
                )
                if resp and getattr(resp, "data", None):
                    return True
                return False
            except Exception as exc:
                logger.warning(
                    "pkm_delete_failed: %s — graceful False",
                    exc.__class__.__name__,
                )
                return False

        # graceful in-memory fallback — 본인 store 에서만 제거 (격리).
        rows = self.store.get(auth_user_id, [])
        for i, row in enumerate(rows):
            if str(row.get("id")) == str(entry_id):
                rows.pop(i)
                return True
        return False

    def _reset_for_test(self) -> None:
        """테스트용 in-memory store 초기화 (BrandMemoryRepo._reset 패턴)."""
        self.store.clear()


__all__ = ["PkmRepo"]
