"""Phase 9 Slice 4 — feedback/selection → candidate_knowledge 적재 경로 (ADR-031).

Brand Memory 후보 추출 준비. P-AUX-2 brand_memory_extractor agent 는 미구현 (Phase 10+ — NG1).
본 모듈은 데이터 누적 인프라(candidate_knowledge pending 적재)만 제공한다.

적재 경계 (ADR-031 / NG12):
  - 적재는 candidate_knowledge status='pending' 까지만 — Phase 7 5단계 파이프라인 진입점.
  - 자동 승격(pending → filtered → ... → promoted) 절대 호출 X (rag.promotion.transition 미호출).
    승격은 rag-update Skill 5단계 절차 필요 (Phase 11+ 두 번째 트리거).
  - 적재 전 PII 마스킹 (security-review T5) — feedback_repo.mask_pii 재사용 (단일 출처).

graceful (P-GRACEFUL-001): Supabase 사용 가능 시 candidate_knowledge INSERT,
  실패/미설정 시 in-memory list fallback (raise 0).

References:
  - docs/decisions/phase_9_brand_memory_prep.md (ADR-031 — 적재 경로 + P-AUX-2 설계 명세)
  - docs/contracts/db_schema.md §7.2 candidate_knowledge (source_kind / status='pending')
  - backend/fastapi/rag/promotion.py (Phase 7 5단계 — 본 모듈은 import/호출 0, pending 진입점만 정합)
  - backend/fastapi/db/repositories/feedback_repo.py (mask_pii — 저장 전 마스킹 재사용)
  - meta/security_reviews/2026-05-29_phase-9-feedback-pii.md (T5 적재 PII 차단)
"""

from __future__ import annotations

import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)

# candidate_knowledge.source_kind enum (db_schema §7.2) — Phase 9 적재 경로가 사용하는 2종.
SOURCE_KIND_FEEDBACK = "user_feedback"
SOURCE_KIND_CHOICE = "user_choice"

# 적재는 항상 pending — Phase 7 5단계 진입점 (자동 승격 X, NG12).
PENDING_STATUS = "pending"

# event_type 별 사람이 읽을 수 있는 content prefix (한국어).
_EVENT_LABELS = {
    "like": "사용자가 선호한 기획안",
    "dislike": "사용자가 선호하지 않은 기획안",
    "reject": "사용자가 반려한 기획안",
    "regenerate": "사용자가 재생성을 요청한 기획안",
    "select": "사용자가 선택한 기획안",
}


def _mask(text: Optional[str]) -> Optional[str]:
    """feedback_repo.mask_pii 재사용 (단일 출처 — security-review T5).

    import 실패 시(테스트 격리 등) 원본 통과 — 단, 호출자(feedback endpoint)는
    이미 저장 전 마스킹(T1)을 거친 reason 을 전달하므로 이중 방어 중 하나.
    """
    if not text:
        return text
    try:
        from backend.fastapi.db.repositories.feedback_repo import mask_pii

        return mask_pii(text)
    except Exception:  # pragma: no cover — defensive (graceful)
        return text


def _compose_content(
    event_type: str,
    reason: Optional[str],
    option_index: Optional[int],
) -> str:
    """event_type + option_index + reason 으로 candidate content 문자열 구성."""
    label = _EVENT_LABELS.get(event_type, f"사용자 이벤트({event_type})")
    parts = [label]
    if option_index is not None:
        parts.append(f"(option_index={option_index})")
    if reason:
        parts.append(f"— 사유: {reason}")
    return " ".join(parts)


def build_candidate_from_feedback(
    plan_id: str,
    event_type: str,
    *,
    reason: Optional[str] = None,
    option_index: Optional[int] = None,
    source_kind: str = SOURCE_KIND_FEEDBACK,
) -> dict[str, Any]:
    """feedback/selection → candidate_knowledge pending dict (적재 준비, 저장 X).

    Args:
        plan_id: 출처 plan (→ candidate.source_id, PII 삭제 요청 시 역추적 — T5).
        event_type: 'like' | 'dislike' | 'reject' | 'regenerate' | 'select'.
            reject/dislike 신호도 rejection_pattern 후보로 적재 가능 (단 pending).
        reason: 자유 입력 사유 — 적재 전 PII 마스킹 적용 (T5).
        option_index: 특정 candidate 대상 (0–2). None = plan 전체.
        source_kind: 'user_feedback' (기본) | 'user_choice' (선택 이벤트).

    Returns:
        candidate_knowledge row dict (status='pending' 고정 — 자동 승격 X, NG12).
        DB 저장은 enqueue_feedback_candidate() 가 담당.
    """
    content = _compose_content(event_type, reason, option_index)
    # ★ 적재 전 PII 마스킹 (security-review T5 — content 진입 전)
    masked = _mask(content)
    return {
        "source_kind": source_kind,
        "source_id": plan_id,
        "content": masked,
        "status": PENDING_STATUS,  # Phase 7 5단계 진입점 — 자동 승격 X (NG12)
        "metadata": {
            "event_type": event_type,
            "option_index": option_index,
        },
    }


async def enqueue_feedback_candidate(
    candidate: dict[str, Any],
    *,
    supabase_client: Optional[Any] = None,
    in_memory_store: Optional[list[dict[str, Any]]] = None,
) -> dict[str, Any]:
    """candidate_knowledge pending 적재 (graceful — Supabase or in-memory).

    ★ 자동 승격 X (NG12): status='pending' 고정으로 INSERT 만. promotion.transition 미호출.
    승격(pending → ... → promoted)은 rag-update Skill 5단계 절차 (Phase 11+).

    Args:
        candidate: build_candidate_from_feedback() 산출 dict (status='pending' 권장).
        supabase_client: Supabase client. None 이면 in-memory fallback.
        in_memory_store: graceful fallback list (Supabase 실패/미설정 시 append).

    Returns:
        적재된 candidate row dict (status 는 'pending' 유지 — 승격 X).
    """
    # 방어: status 가 어떤 경로로든 pending 이 아니면 pending 으로 강제 (자동 승격 차단, NG12).
    if candidate.get("status") != PENDING_STATUS:
        candidate = {**candidate, "status": PENDING_STATUS}

    if supabase_client is not None:
        try:
            resp = (
                supabase_client.table("candidate_knowledge")
                .insert(candidate)
                .execute()
            )
            if resp and getattr(resp, "data", None):
                row = resp.data[0]
                if in_memory_store is not None:
                    in_memory_store.append(row)  # in-memory mirror
                return row
        except Exception as exc:
            logger.warning(
                "candidate_enqueue_failed: %s — falling back to in-memory",
                exc.__class__.__name__,
            )

    # graceful in-memory fallback
    row = dict(candidate)
    if in_memory_store is not None:
        in_memory_store.append(row)
    return row


__all__ = [
    "build_candidate_from_feedback",
    "enqueue_feedback_candidate",
    "SOURCE_KIND_FEEDBACK",
    "SOURCE_KIND_CHOICE",
    "PENDING_STATUS",
]
