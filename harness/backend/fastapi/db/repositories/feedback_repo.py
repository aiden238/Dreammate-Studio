"""Phase 9 Slice 2 — FeedbackRepo (graceful CRUD wrapper) + reason PII 마스킹.

피드백(like/dislike/reject/regenerate) 영속화. Supabase 사용 가능 시 PostgreSQL(feedback_events),
아니면 in-memory dict 로 graceful fallback.

설계 원칙 (Phase 5 PlansRepo 패턴 계승):
  1. Phase 1 graceful 정책 계승 — 실패 시 raise 금지, in-memory fallback (P-GRACEFUL-001).
  2. 실 plans 테이블 정합 (ADR-030) — plan_id (→ plans.id) + event_type enum + option_index (null=plan 전체).
  3. ★ reason text 저장 전 PII 마스킹 (security-review T1/T2) — record() 시점, INSERT 직전.
     이메일/전화/주민/카드 패턴(quality_filter PII 패턴 재사용) → [masked].
  4. RLS 강제는 0005_feedback_selection.sql 의 실 Supabase 에서만 (security-review T3).

참조:
  - docs/contracts/db_schema.md §5.2 feedback_events (Phase 9 실 구현)
  - docs/decisions/phase_9_feedback_selection.md (ADR-030 §2 feedback_events + §3 FeedbackRepo graceful)
  - meta/security_reviews/2026-05-29_phase-9-feedback-pii.md (T1 저장 전 마스킹 — feedback_repo INSERT 직전)
  - backend/fastapi/rag/quality_filter.py (_PII_PATTERNS — 이메일/전화/주민/카드 재사용)
"""

from __future__ import annotations

import logging
import re
from typing import Any, Optional

logger = logging.getLogger(__name__)

_MASK_TOKEN = "[masked]"

# PII 마스킹 패턴 — quality_filter._PII_PATTERNS 와 동일 출처 (llm_security §3.2 직접 식별자).
# 순서: 카드(가장 긴 숫자열) → 주민 → 전화 → 이메일 — 부분 매칭 충돌 방지.
# 참조: backend/fastapi/rag/quality_filter.py §_PII_PATTERNS
_PII_MASK_PATTERNS = [
    re.compile(r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b"),          # 카드번호
    re.compile(r"\b\d{6}-[1-4]\d{6}\b"),                                 # 주민등록번호
    re.compile(r"\b\d{2,3}-\d{3,4}-\d{4}\b"),                            # 한국 전화번호
    re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),  # email
]

_VALID_EVENT_TYPES = {"like", "dislike", "reject", "regenerate"}


def mask_pii(text: Optional[str]) -> Optional[str]:
    """reason text 의 직접 식별자(이메일/전화/주민/카드) 를 [masked] 로 치환 (security-review T1/T2).

    저장 전 마스킹 (case B) — raw PII 가 DB 에 잔존하지 않도록 record() INSERT 직전 적용.
    None / 빈 문자열은 그대로 통과.
    """
    if not text:
        return text
    masked = text
    for pattern in _PII_MASK_PATTERNS:
        masked = pattern.sub(_MASK_TOKEN, masked)
    return masked


class FeedbackRepo:
    """feedback_events CRUD repository — graceful Supabase or in-memory.

    Usage:
        from backend.fastapi.db import FeedbackRepo, get_supabase

        repo = FeedbackRepo(supabase_client=get_supabase())
        await repo.record("plan-uuid", "like", option_index=0)
        events = await repo.list_for_plan("plan-uuid")
    """

    def __init__(
        self,
        supabase_client: Optional[Any] = None,
        in_memory_store: Optional[dict[str, list[dict[str, Any]]]] = None,
    ) -> None:
        self.client = supabase_client
        # key = plan_id, value = feedback events list (1:N)
        self.store: dict[str, list[dict[str, Any]]] = (
            in_memory_store if in_memory_store is not None else {}
        )

    # ─── helpers ─────────────────────────────────────────────────────

    def _use_supabase(self) -> bool:
        return self.client is not None

    # ─── operations ──────────────────────────────────────────────────

    async def record(
        self,
        plan_id: str,
        event_type: str,
        *,
        option_index: Optional[int] = None,
        reason: Optional[str] = None,
        auth_user_id: Optional[str] = None,
    ) -> dict[str, Any]:
        """Record 피드백. ★ reason PII 저장 전 마스킹 (T1). Supabase 실패 시 in-memory fallback.

        Args:
            plan_id: 피드백 대상 plan (→ plans.id).
            event_type: 'like' | 'dislike' | 'reject' | 'regenerate'.
            option_index: 특정 candidate 대상 (0–2). None = plan 전체.
            reason: 자유 입력 사유 — INSERT 직전 PII 마스킹 적용 (security-review T1/T2).
            auth_user_id: RLS 정합 (anon 시 None).

        Returns:
            저장된 feedback row dict (reason 은 마스킹된 값).
        """
        # ★ 저장 전 PII 마스킹 (security-review T1 — feedback_repo INSERT 직전)
        masked_reason = mask_pii(reason)

        payload: dict[str, Any] = {
            "plan_id": plan_id,
            "auth_user_id": auth_user_id,
            "option_index": option_index,
            "event_type": event_type,
            "reason": masked_reason,
        }

        if self._use_supabase():
            try:
                resp = (
                    self.client.table("feedback_events")  # type: ignore[union-attr]
                    .insert(payload)
                    .execute()
                )
                if resp and getattr(resp, "data", None):
                    row = resp.data[0]
                    self.store.setdefault(plan_id, []).append(row)  # in-memory mirror
                    return row
            except Exception as exc:
                logger.warning(
                    "feedback_record_failed: %s — falling back to in-memory",
                    exc.__class__.__name__,
                )
        # graceful in-memory fallback
        row = dict(payload)
        self.store.setdefault(plan_id, []).append(row)
        return row

    async def list_for_plan(self, plan_id: str) -> list[dict[str, Any]]:
        """List 해당 plan 의 피드백 events. Supabase 실패 시 in-memory fallback."""
        if self._use_supabase():
            try:
                resp = (
                    self.client.table("feedback_events")  # type: ignore[union-attr]
                    .select("*")
                    .eq("plan_id", plan_id)
                    .execute()
                )
                if resp and getattr(resp, "data", None) is not None:
                    return list(resp.data)
            except Exception as exc:
                logger.warning(
                    "feedback_list_failed: %s — falling back to in-memory",
                    exc.__class__.__name__,
                )
        return list(self.store.get(plan_id, []))

    def _reset_for_test(self) -> None:
        """테스트용 in-memory store 초기화 (Phase 5 _reset 패턴)."""
        self.store.clear()


__all__ = ["FeedbackRepo", "mask_pii"]
