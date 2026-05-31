"""brand_memory_extractor — P-AUX-2 (Phase 10 Slice S2).

Phase 9 (ADR-031) 가 준비한 brand_memory 적재 인프라(candidate_knowledge pending 적재 +
BrandMemoryRepo 수동 CRUD)를 실제 추출 agent 로 활성화한다. 누적된 feedback_events
(like/dislike/reject/regenerate + reason) + selected_plans(선택 패턴)을 분석하여
Brand Memory 후보(proposed_entries)를 추출한다.

설계 결정 — heuristic (규칙 기반, LLM 미사용):
  - ADR-031 §P-AUX-2 규칙은 결정적(deterministic)이다:
      · 1회성 결정       → confidence ≤ 0.3
      · 2회 이상 반복     → confidence ≥ 0.7
      · 명시 선호(reason) → confidence ≥ 0.9
      · 기존 Brand Memory 충돌 항목 우선 제외 + 별도 표시 / 최대 5개
  - 위 규칙은 빈도 집계 + reason 유무로 충분히 구현 가능 → LLM 호출 0 (비용 0, 결정적).
  - 따라서 PROMPT_VERSION/prompt_registry 활성 prompt 등록 불필요 (registry P-AUX-2 명세는
    LLM 활성화 시점 SoT 로 보존 — heuristic 구현은 그 규칙을 코드로 반영).

★ graceful (P-GRACEFUL-001):
  - 입력 부족(빈 feedback/selection) / 추출 실패 → 빈 proposed_entries 반환 (예외 전파 X).
  - BrandMemoryRepo 저장 실패해도 graceful (raise 0 — 호출자/응답 차단 0).

★ PII 마스킹 (Phase 9 security-review T5 계승):
  - reason / source_evidence 등 자유 텍스트는 feedback_repo.mask_pii 재사용(단일 출처)으로
    이메일/전화/주민/카드 → [masked]. import 실패 시 graceful 통과.
  - 단, 호출자(feedback endpoint)는 이미 저장 전 마스킹된 reason(row)을 전달하므로 이중 방어.

★ agent 격리 (agent_io_contract §1.2):
  - orchestrator/standalone callable. 다른 agent(critic/intent/planning/rewriter) 직접 호출 0.
  - BrandMemoryRepo(준비용 repo)만 선택적으로 주입받아 후보 영속화 (graceful).

References:
  - docs/decisions/phase_9_brand_memory_prep.md (ADR-031 — P-AUX-2 설계 명세 + 적재 경로)
  - ai_system/prompts/prompt_registry.md P-AUX-2 (명세 SoT — confidence 규칙)
  - docs/contracts/agent_io_contract.md §7 Memory Extractor (입출력 + §7.5 결과 처리)
  - docs/contracts/db_schema.md §6 brand_memory_entries (entry_type 5종)
  - backend/fastapi/db/repositories/brand_memory_repo.py (BrandMemoryRepo — 적재 대상)
  - backend/fastapi/db/repositories/feedback_repo.py (mask_pii — PII 마스킹 단일 출처)
"""

from __future__ import annotations

import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)

# ─── 메타 (registry P-AUX-2 미러 — heuristic 구현이므로 LLM PROMPT_VERSION 미부여) ───
PROMPT_ID = "P-AUX-2"
# heuristic (LLM 미사용) — registry P-AUX-2 v1.0.0 명세의 confidence 규칙을 코드로 반영.
# LLM 활성화 시점에 prompt_registry semver 부여 (prompt-version-review). 현 구현은 IMPL_KIND 로 표기.
IMPL_KIND = "heuristic"

# entry_type enum (db_schema §6 brand_memory_entries / ADR-031).
ENTRY_PREFERRED_TONE = "preferred_tone"
ENTRY_AVOID_PHRASE = "avoid_phrase"
ENTRY_PREFERRED_PHRASE = "preferred_phrase"
ENTRY_SUCCESS_PATTERN = "success_pattern"
ENTRY_REJECTION_PATTERN = "rejection_pattern"

VALID_ENTRY_TYPES = {
    ENTRY_PREFERRED_TONE,
    ENTRY_AVOID_PHRASE,
    ENTRY_PREFERRED_PHRASE,
    ENTRY_SUCCESS_PATTERN,
    ENTRY_REJECTION_PATTERN,
}

# confidence 규칙 (ADR-031 §P-AUX-2 / registry P-AUX-2 §System).
CONFIDENCE_ONE_OFF = 0.3        # 1회성 결정 ≤ 0.3
CONFIDENCE_REPEATED = 0.7       # 2회 이상 반복 ≥ 0.7
CONFIDENCE_EXPLICIT = 0.9       # 명시 선호(reason 동반) ≥ 0.9
REPEAT_THRESHOLD = 2            # "2회 이상 반복" 기준
MAX_PROPOSED_ENTRIES = 5        # 최대 5개

# 긍정 신호(success_pattern) vs 부정 신호(rejection_pattern) event_type 분류.
_POSITIVE_EVENTS = {"like", "select"}
_NEGATIVE_EVENTS = {"dislike", "reject", "regenerate"}


def _mask(text: Optional[str]) -> Optional[str]:
    """feedback_repo.mask_pii 재사용 (단일 출처 — security-review T5).

    import 실패 시(테스트 격리 등) 원본 통과 — 호출자가 이미 마스킹한 reason 을
    전달하므로 이중 방어 중 하나 (graceful).
    """
    if not text:
        return text
    try:
        from ..db.repositories.feedback_repo import mask_pii

        return mask_pii(text)
    except Exception:  # pragma: no cover — defensive (graceful)
        return text


def _existing_index(current_brand_memory: Optional[list[dict[str, Any]]]) -> set[tuple[str, str]]:
    """기존 Brand Memory entry 의 (entry_type, content) 집합 — 충돌 검사용.

    content 는 공백 정규화 후 비교 (사소한 차이 무시).
    """
    index: set[tuple[str, str]] = set()
    if not current_brand_memory:
        return index
    for entry in current_brand_memory:
        if not isinstance(entry, dict):
            continue
        et = str(entry.get("entry_type") or "").strip()
        content = " ".join(str(entry.get("content") or "").split())
        if et and content:
            index.add((et, content))
    return index


def _event_type(event: dict[str, Any]) -> str:
    """feedback/selection event 에서 event_type 추출.

    feedback_events 는 'event_type', selected_plans 는 선택 이벤트로 'select' 매핑.
    """
    et = event.get("event_type")
    if et:
        return str(et).strip().lower()
    # selected_plans row (selected_option_index 보유) → select 이벤트로 간주
    if "selected_option_index" in event:
        return "select"
    return ""


def _reason(event: dict[str, Any]) -> Optional[str]:
    """event 에서 자유 입력 사유 추출 (feedback=reason / selection=selection_reason)."""
    return event.get("reason") or event.get("selection_reason")


def _scale_confidence(count: int, has_explicit_reason: bool) -> float:
    """빈도 + 명시 사유 유무로 confidence 산출 (ADR-031 규칙).

    - 명시 선호(reason 동반) → 0.9 (최우선)
    - 2회 이상 반복          → 0.7
    - 1회성                  → 0.3
    """
    if has_explicit_reason:
        return CONFIDENCE_EXPLICIT
    if count >= REPEAT_THRESHOLD:
        return CONFIDENCE_REPEATED
    return CONFIDENCE_ONE_OFF


def extract_brand_memory_candidates(
    feedback_events: Optional[list[dict[str, Any]]] = None,
    selected_plans: Optional[list[dict[str, Any]]] = None,
    *,
    current_brand_memory: Optional[list[dict[str, Any]]] = None,
) -> dict[str, Any]:
    """feedback_events + selected_plans → Brand Memory 후보 추출 (heuristic, graceful).

    Args:
        feedback_events: feedback_events row list
            (각 dict: event_type / option_index / reason ...). None/빈 → graceful.
        selected_plans: selected_plans row list
            (각 dict: selected_option_index / selection_reason ...). None/빈 → graceful.
        current_brand_memory: 기존 brand_memory_entries row list
            (충돌 검사용 — (entry_type, content) 일치 항목은 제외 + 별도 표시).

    Returns:
        dict (registry P-AUX-2 output schema 정합):
          {
            "proposed_entries": [
              { entry_type, content, confidence (0–1), source_evidence }
            ],                                  # 최대 5개
            "conflicts": [ { ...entry..., "conflicts_with_existing": True } ],
            "impl_kind": "heuristic",
          }
        입력 부족/추출 실패 시 proposed_entries=[] (예외 전파 X — graceful).
    """
    try:
        events: list[dict[str, Any]] = [
            e for e in (feedback_events or []) if isinstance(e, dict)
        ]
        selections: list[dict[str, Any]] = [
            s for s in (selected_plans or []) if isinstance(s, dict)
        ]
        existing = _existing_index(current_brand_memory)

        # ── 신호 집계 (entry_type 별 빈도 + 명시 사유 수집) ──────────────
        # key = (entry_type, normalized_content), value = {count, reasons}
        agg: dict[tuple[str, str], dict[str, Any]] = {}

        def _accumulate(entry_type: str, content: str, reason: Optional[str]) -> None:
            content = " ".join(str(content).split())
            if not content:
                return
            key = (entry_type, content)
            slot = agg.setdefault(key, {"count": 0, "reasons": []})
            slot["count"] += 1
            masked_reason = _mask(reason)
            if masked_reason:
                slot["reasons"].append(masked_reason)

        for ev in events + selections:
            et = _event_type(ev)
            if not et:
                continue
            reason = _reason(ev)
            if et in _POSITIVE_EVENTS:
                # 긍정 신호 → success_pattern (명시 사유 있으면 preferred_phrase 도)
                label = "선택" if et == "select" else "선호"
                _accumulate(
                    ENTRY_SUCCESS_PATTERN,
                    f"사용자가 반복 {label}한 기획 패턴",
                    reason,
                )
                masked_reason = _mask(reason)
                if masked_reason:
                    _accumulate(ENTRY_PREFERRED_PHRASE, masked_reason, reason)
            elif et in _NEGATIVE_EVENTS:
                # 부정 신호 → rejection_pattern (명시 사유 있으면 avoid_phrase 도)
                _accumulate(
                    ENTRY_REJECTION_PATTERN,
                    "사용자가 반복 회피한 기획 패턴",
                    reason,
                )
                masked_reason = _mask(reason)
                if masked_reason:
                    _accumulate(ENTRY_AVOID_PHRASE, masked_reason, reason)

        # ── 후보 생성 (confidence 산출 + 충돌 분리) ──────────────────────
        proposed: list[dict[str, Any]] = []
        conflicts: list[dict[str, Any]] = []
        for (entry_type, content), slot in agg.items():
            count = int(slot["count"])
            reasons: list[str] = slot["reasons"]
            has_explicit = bool(reasons)
            confidence = _scale_confidence(count, has_explicit)
            # source_evidence — 마스킹된 사유 또는 빈도 요약 (PII 0).
            if reasons:
                source_evidence = "; ".join(reasons[:3])
            else:
                source_evidence = f"{count}건의 동일 신호 누적"

            entry = {
                "entry_type": entry_type,
                "content": content,
                "confidence": round(confidence, 2),
                "source_evidence": source_evidence,
            }
            if (entry_type, content) in existing:
                # 기존 Brand Memory 충돌 → 우선 제외 + 별도 표시 (ADR-031)
                conflicts.append({**entry, "conflicts_with_existing": True})
            else:
                proposed.append(entry)

        # ── 정렬(confidence 내림차순 → 결정적 tie-break) + 최대 5개 ──────
        proposed.sort(key=lambda e: (-e["confidence"], e["entry_type"], e["content"]))
        proposed = proposed[:MAX_PROPOSED_ENTRIES]

        logger.info(
            "brand_memory_extract ok proposed=%d conflicts=%d (events=%d selections=%d)",
            len(proposed), len(conflicts), len(events), len(selections),
        )
        return {
            "proposed_entries": proposed,
            "conflicts": conflicts,
            "impl_kind": IMPL_KIND,
        }
    except Exception as exc:  # pragma: no cover — graceful (추출 실패해도 차단 0)
        logger.warning(
            "brand_memory_extract_failed: %s — returning empty (graceful)",
            exc.__class__.__name__,
        )
        return {"proposed_entries": [], "conflicts": [], "impl_kind": IMPL_KIND}


async def run_brand_memory_extractor(
    feedback_events: Optional[list[dict[str, Any]]] = None,
    selected_plans: Optional[list[dict[str, Any]]] = None,
    *,
    brand_id: Optional[str] = None,
    current_brand_memory: Optional[list[dict[str, Any]]] = None,
    repo: Optional[Any] = None,
    persist: bool = False,
    persist_min_confidence: float = CONFIDENCE_EXPLICIT,
) -> dict[str, Any]:
    """standalone/orchestrator callable — 추출 + (선택) 후보 영속화 (graceful).

    Args:
        feedback_events / selected_plans / current_brand_memory: extract 입력.
        brand_id: 영속화 대상 brand (persist=True + repo 제공 시 필요).
        repo: BrandMemoryRepo (graceful — None 이면 영속화 skip).
        persist: True + repo + brand_id 모두 있을 때만 후보 add_entry.
            ★ 자동 INSERT 는 confidence ≥ persist_min_confidence(기본 0.9, 명시 선호)만 —
            agent_io_contract §7.5 (confidence ≥ 0.9 자동 INSERT) 정합. 나머지는 제안만(pending UX).
        persist_min_confidence: 자동 영속화 임계 (기본 0.9).

    Returns:
        extract_brand_memory_candidates 결과 + (persist 시) "persisted" 리스트 추가.
        어떤 단계 실패해도 graceful — 예외 전파 0, 부가 결과만 누락.
    """
    result = extract_brand_memory_candidates(
        feedback_events,
        selected_plans,
        current_brand_memory=current_brand_memory,
    )

    if not (persist and repo is not None and brand_id):
        return result

    persisted: list[dict[str, Any]] = []
    for entry in result.get("proposed_entries", []):
        if float(entry.get("confidence", 0.0)) < persist_min_confidence:
            continue
        try:
            row = await repo.add_entry(
                brand_id,
                entry["entry_type"],
                entry["content"],
                confidence=float(entry["confidence"]),
            )
            persisted.append(row)
        except Exception as exc:  # pragma: no cover — graceful (저장 실패 무시)
            logger.warning(
                "brand_memory_persist_failed: %s entry_type=%s (graceful)",
                exc.__class__.__name__, entry.get("entry_type"),
            )
    result["persisted"] = persisted
    return result


__all__ = [
    "extract_brand_memory_candidates",
    "run_brand_memory_extractor",
    "PROMPT_ID",
    "IMPL_KIND",
    "VALID_ENTRY_TYPES",
    "ENTRY_PREFERRED_TONE",
    "ENTRY_AVOID_PHRASE",
    "ENTRY_PREFERRED_PHRASE",
    "ENTRY_SUCCESS_PATTERN",
    "ENTRY_REJECTION_PATTERN",
    "CONFIDENCE_ONE_OFF",
    "CONFIDENCE_REPEATED",
    "CONFIDENCE_EXPLICIT",
    "MAX_PROPOSED_ENTRIES",
]
