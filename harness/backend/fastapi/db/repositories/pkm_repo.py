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
import re
from typing import Any, Optional

logger = logging.getLogger(__name__)

_VALID_ENTRY_TYPES = {
    "preferred_tone",
    "avoid_phrase",
    "preferred_phrase",
    "success_pattern",
    "rejection_pattern",
}

# ─── Phase 28 S2 — 강화/정리 상수 (스키마 변경 0, confidence 재활용) ──────────
REINFORCE_BOOST = 0.15   # 유사 재등장 시 confidence 증가폭 (반복 강화)
DECAY_FACTOR = 0.95      # 이번 패스에서 안 건드린 비-locked entry confidence 감쇠 (gentle)
PRUNE_FLOOR = 0.3        # 감쇠 후 이 미만이면 제거 (불필요 제거)
CONF_CAP = 1.0

# 추출기가 가끔 만드는 일반·무정보 후보 (불필요 — 저장 안 함).
_NOISE_SUBSTRINGS = (
    "반복 선호한 기획 패턴",
    "선호한 기획 패턴",
)


def _norm(s: str) -> str:
    return re.sub(r"\s+", "", (s or "").lower())


def _is_noise(content: str) -> bool:
    c = (content or "").strip()
    if len(c) < 5:
        return True
    return any(sub in c for sub in _NOISE_SUBSTRINGS)


def _content_similar(a: str, b: str) -> bool:
    """같은 entry_type 내 content 유사도(heuristic, LLM 0). 정규화 동일/포함 또는 토큰 Jaccard≥0.5."""
    na, nb = _norm(a), _norm(b)
    if not na or not nb:
        return False
    if na == nb or na in nb or nb in na:
        return True
    ta = set((a or "").lower().split())
    tb = set((b or "").lower().split())
    if not ta or not tb:
        return False
    return len(ta & tb) / len(ta | tb) >= 0.5


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

    # ─── Phase 28 S2 — 강화/정리 (반복 강화 + 불필요 제거, 스키마 변경 0) ──────

    async def _update_confidence(
        self, row: dict[str, Any], auth_user_id: str, new_conf: float
    ) -> None:
        """기존 entry 의 confidence 갱신 (Supabase: id+auth, in-memory: dict ref mutate). graceful."""
        rid = row.get("id")
        if self._use_supabase() and rid:
            try:
                self.client.table("pkm_entries").update(  # type: ignore[union-attr]
                    {"confidence": new_conf}
                ).eq("id", rid).eq("auth_user_id", auth_user_id).execute()
            except Exception as exc:  # pragma: no cover — graceful
                logger.warning("pkm_conf_update_failed: %s", exc.__class__.__name__)
        row["confidence"] = new_conf  # in-memory mirror / store ref

    async def consolidate_entry(
        self,
        auth_user_id: str,
        entry_type: str,
        content: str,
        *,
        scope: str = "personal",
        confidence: float = 0.5,
        source_plan_id: Optional[str] = None,
    ) -> Optional[tuple[str, str]]:
        """add_entry 의 강화-인지 버전 (반복 강화 + 중복/노이즈 제거).

        - 노이즈(일반·무정보) → 저장 안 함 (None 반환).
        - 같은 entry_type 에 유사 content 존재 → **강화**(confidence↑, dedup, insert 0) → ("reinforced", 기존content).
        - 신규 → add_entry insert → ("inserted", content).

        Returns: (action, canonical_content) 또는 None(노이즈 스킵).
        """
        if _is_noise(content):
            return None
        existing = await self.list_for_user(auth_user_id, scope=scope)
        for row in existing:
            if str(row.get("entry_type")) != str(entry_type):
                continue
            if _content_similar(content, str(row.get("content", ""))):
                cur = float(row.get("confidence") or 0.5)
                new_conf = round(min(CONF_CAP, max(cur, float(confidence)) + REINFORCE_BOOST), 4)
                await self._update_confidence(row, auth_user_id, new_conf)
                return ("reinforced", str(row.get("content", "")))
        await self.add_entry(
            auth_user_id, entry_type, content,
            scope=scope, confidence=confidence, source_plan_id=source_plan_id,
        )
        return ("inserted", content)

    async def decay_and_prune(
        self,
        auth_user_id: str,
        *,
        scope: str = "personal",
        protect: Optional[set[str]] = None,
        decay: float = DECAY_FACTOR,
        floor: float = PRUNE_FLOOR,
    ) -> tuple[int, int]:
        """이번 패스에서 강화/삽입 안 된(=protect 외) 비-locked entry 를 gentle decay,
        floor 미만은 삭제(불필요 제거). user_locked 는 절대 건드리지 않는다.

        Returns: (decayed, pruned).
        """
        protect_norm = {_norm(c) for c in (protect or set())}
        existing = await self.list_for_user(auth_user_id, scope=scope)
        decayed = pruned = 0
        for row in existing:
            if row.get("is_user_locked"):
                continue
            if _norm(str(row.get("content", ""))) in protect_norm:
                continue
            cur = float(row.get("confidence") or 0.5)
            new_conf = round(cur * decay, 4)
            if new_conf < floor:
                rid = row.get("id")
                if rid:
                    if await self.delete_entry(rid, auth_user_id=auth_user_id):
                        pruned += 1
                else:  # in-memory (id 없음)
                    try:
                        self.store.get(auth_user_id, []).remove(row)
                        pruned += 1
                    except ValueError:  # pragma: no cover
                        pass
            else:
                await self._update_confidence(row, auth_user_id, new_conf)
                decayed += 1
        return (decayed, pruned)

    def _reset_for_test(self) -> None:
        """테스트용 in-memory store 초기화 (BrandMemoryRepo._reset 패턴)."""
        self.store.clear()


__all__ = ["PkmRepo"]
