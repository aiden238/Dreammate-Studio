"""Phase 7 Slice 2 — 5단계 transition logic (ADR-026).

5단계: pending → filtered → evaluated → approved → promoted
hybrid 승인 (evaluated → approved): 자동 ≥ 0.8 / 수동 0.6~0.8.
promotion_history: append-only (DB layer + application 양쪽 강제).

References:
  - docs/decisions/phase_7_promotion_logic.md (ADR-026)
  - docs/contracts/rag_data_contract.md §18.3 + §18.4
  - knowledge/rag/promotion_rule.md
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal, Optional

KnowledgeStage = Literal[
    "pending", "filtered", "evaluated", "approved", "promoted"
]

# Transition 순서 (ADR-026 §1)
_STAGE_ORDER: list[KnowledgeStage] = [
    "pending",
    "filtered",
    "evaluated",
    "approved",
    "promoted",
]

# 자동 임계 (ADR-026 §1.3 hybrid)
AUTO_APPROVE_THRESHOLD = 0.8
EVAL_PASS_THRESHOLD = 0.6


def promotion_history_entry(
    from_stage: KnowledgeStage,
    to_stage: KnowledgeStage,
    *,
    reason: Optional[str] = None,
    scores: Optional[dict[str, float]] = None,
    overall_score: Optional[float] = None,
    method: Optional[str] = None,
    threshold: Optional[float] = None,
) -> dict[str, Any]:
    """promotion_history append entry 생성 (ADR-026 §2 schema 정합).

    Returns:
        dict (JSON-serializable):
          - from: str (stage)
          - to: str (stage)
          - at: str (ISO8601 UTC)
          - reason / scores / overall / method / threshold (optional)
    """
    entry: dict[str, Any] = {
        "from": from_stage,
        "to": to_stage,
        "at": datetime.now(timezone.utc).isoformat(),
    }
    if reason is not None:
        entry["reason"] = reason
    if scores is not None:
        entry["scores"] = scores
    if overall_score is not None:
        entry["overall"] = overall_score
    if method is not None:
        entry["method"] = method
    if threshold is not None:
        entry["threshold"] = threshold
    return entry


def _can_transition(
    from_stage: KnowledgeStage, to_stage: KnowledgeStage
) -> bool:
    """transition 순서 검증 (ADR-026 §1 강제)."""
    try:
        from_idx = _STAGE_ORDER.index(from_stage)
        to_idx = _STAGE_ORDER.index(to_stage)
        return to_idx == from_idx + 1
    except ValueError:
        return False


def transition(
    item: dict[str, Any],
    target_stage: KnowledgeStage,
    *,
    scores: Optional[dict[str, float]] = None,
    overall_score: Optional[float] = None,
    reason: Optional[str] = None,
    method: Optional[str] = None,
) -> dict[str, Any]:
    """item을 target_stage로 transition + promotion_history append.

    Args:
        item: candidate_knowledge row dict (stage + promotion_history 필드)
        target_stage: 목표 stage (다음 단계만 허용 — 순서 강제)
        scores: eval_rubric 점수 dict (filtered → evaluated 시 권장)
        overall_score: 종합 점수
            - filtered → evaluated 시 권장 (이력 기록)
            - evaluated → approved 시 필수 (hybrid 분기 판정)
        reason: transition 사유
        method: 'auto' or 'manual' (evaluated → approved 시 — 미지정 시 자동 판정)

    Returns:
        갱신된 item dict (원본 mutated — stage + promotion_history).

    Raises:
        ValueError:
          - 잘못된 transition 순서 (out-of-order)
          - evaluated → approved 시 overall_score 누락
          - overall_score가 EVAL_PASS_THRESHOLD (0.6) 미만
    """
    current_stage: KnowledgeStage = item.get("stage", "pending")
    if not _can_transition(current_stage, target_stage):
        raise ValueError(
            f"Invalid transition: {current_stage} → {target_stage}. "
            f"Allowed order: {' → '.join(_STAGE_ORDER)}"
        )

    threshold: Optional[float] = None

    # Hybrid 승인 로직 (evaluated → approved, ADR-026 §1.3)
    if target_stage == "approved" and method is None:
        if overall_score is None:
            raise ValueError(
                "overall_score required for evaluated → approved transition"
            )
        if overall_score >= AUTO_APPROVE_THRESHOLD:
            method = "auto"
            threshold = AUTO_APPROVE_THRESHOLD
        elif overall_score >= EVAL_PASS_THRESHOLD:
            method = "manual"
            threshold = EVAL_PASS_THRESHOLD
        else:
            raise ValueError(
                f"overall_score {overall_score} below threshold "
                f"{EVAL_PASS_THRESHOLD}. Cannot transition to approved."
            )

    entry = promotion_history_entry(
        current_stage,
        target_stage,
        reason=reason,
        scores=scores,
        overall_score=overall_score,
        method=method,
        threshold=threshold,
    )

    item["stage"] = target_stage
    history = item.get("promotion_history", [])
    if not isinstance(history, list):
        # graceful: malformed history → reset (append-only 정신은 신규 생성에만 적용)
        history = []
    history.append(entry)
    item["promotion_history"] = history
    return item
