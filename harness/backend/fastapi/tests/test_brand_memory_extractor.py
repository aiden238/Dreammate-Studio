"""Phase 10 Slice S2 — brand_memory_extractor (P-AUX-2, heuristic) 테스트.

테스트 시나리오 (additive — 기존 351 baseline 회귀 0, mock-deterministic):
  추출 로직:
    1. 부정 신호(dislike/reject) → rejection_pattern 후보 + confidence 규칙 (2회+ → 0.7)
    2. 긍정 신호(like/select) → success_pattern 후보
    3. 명시 사유(reason) 동반 → confidence 0.9 (명시 선호) + avoid/preferred_phrase 후보
    4. 1회성 결정 → confidence 0.3
    5. selected_plans(선택 이벤트) 도 입력으로 소비 (select → success_pattern)
    6. 최대 5개 제한 (MAX_PROPOSED_ENTRIES)
  graceful:
    7. 빈/None 입력 → 빈 proposed_entries (예외 0)
    8. 잘못된(non-dict) 입력 항목 skip (graceful)
  PII 마스킹:
    9. reason 의 이메일/전화 → [masked] (source_evidence/content 어디에도 raw PII 0)
  충돌 검사:
    10. 기존 Brand Memory 와 (entry_type, content) 일치 → conflicts 로 분리 (proposed 제외)
  repo 영속화 (mock):
    11. run_brand_memory_extractor persist=True + repo mock → confidence ≥ 0.9 만 add_entry
    12. repo.add_entry 실패해도 graceful (예외 0, persisted 누락만)

참조:
  - docs/decisions/phase_9_brand_memory_prep.md (ADR-031 §P-AUX-2 confidence 규칙)
  - backend/fastapi/agents/brand_memory_extractor.py
  - backend/fastapi/db/repositories/brand_memory_repo.py (BrandMemoryRepo)
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.fastapi.agents.brand_memory_extractor import (
    CONFIDENCE_EXPLICIT,
    CONFIDENCE_ONE_OFF,
    CONFIDENCE_REPEATED,
    ENTRY_AVOID_PHRASE,
    ENTRY_PREFERRED_PHRASE,
    ENTRY_REJECTION_PATTERN,
    ENTRY_SUCCESS_PATTERN,
    MAX_PROPOSED_ENTRIES,
    extract_brand_memory_candidates,
    run_brand_memory_extractor,
)
from backend.fastapi.db.repositories.brand_memory_repo import BrandMemoryRepo


def _entries_by_type(result: dict[str, Any], entry_type: str) -> list[dict[str, Any]]:
    return [e for e in result["proposed_entries"] if e["entry_type"] == entry_type]


# ─── 추출 로직 ──────────────────────────────────────────────────────────


def test_repeated_negative_yields_rejection_pattern_confidence_07() -> None:
    """부정 신호 2회 반복(reason 없음) → rejection_pattern + confidence 0.7."""
    feedback = [
        {"event_type": "dislike", "option_index": 0},
        {"event_type": "reject", "option_index": 1},
    ]
    result = extract_brand_memory_candidates(feedback)
    rej = _entries_by_type(result, ENTRY_REJECTION_PATTERN)
    assert len(rej) == 1
    # 2회 이상 반복 → 0.7 (명시 사유 없음)
    assert rej[0]["confidence"] == CONFIDENCE_REPEATED


def test_positive_signal_yields_success_pattern() -> None:
    """긍정 신호(like) → success_pattern 후보."""
    feedback = [{"event_type": "like", "option_index": 0}]
    result = extract_brand_memory_candidates(feedback)
    succ = _entries_by_type(result, ENTRY_SUCCESS_PATTERN)
    assert len(succ) == 1


def test_explicit_reason_yields_confidence_09_and_avoid_phrase() -> None:
    """명시 사유 동반 부정 신호 → confidence 0.9 + avoid_phrase 후보."""
    feedback = [
        {"event_type": "reject", "option_index": 0, "reason": "광고 같은 과장 표현 싫어요"},
    ]
    result = extract_brand_memory_candidates(feedback)
    # rejection_pattern 은 명시 사유로 confidence 0.9
    rej = _entries_by_type(result, ENTRY_REJECTION_PATTERN)
    assert rej and rej[0]["confidence"] == CONFIDENCE_EXPLICIT
    # avoid_phrase 후보가 사유로부터 생성
    avoid = _entries_by_type(result, ENTRY_AVOID_PHRASE)
    assert avoid and "과장 표현" in avoid[0]["content"]


def test_one_off_decision_confidence_03() -> None:
    """1회성 결정(reason 없음, 단일) → confidence 0.3."""
    result = extract_brand_memory_candidates([{"event_type": "dislike"}])
    rej = _entries_by_type(result, ENTRY_REJECTION_PATTERN)
    assert rej and rej[0]["confidence"] == CONFIDENCE_ONE_OFF


def test_selected_plans_consumed_as_select_event() -> None:
    """selected_plans(선택 이벤트) 도 입력 — select → success_pattern."""
    selections = [
        {"selected_option_index": 1, "selection_reason": "이 톤이 좋아요"},
        {"selected_option_index": 0},
    ]
    result = extract_brand_memory_candidates(None, selections)
    succ = _entries_by_type(result, ENTRY_SUCCESS_PATTERN)
    assert succ  # 선택 패턴 누적
    # selection_reason → preferred_phrase 후보
    pref = _entries_by_type(result, ENTRY_PREFERRED_PHRASE)
    assert pref and "톤이 좋아요" in pref[0]["content"]


def test_max_five_proposed_entries() -> None:
    """최대 5개 제한 — 서로 다른 사유 다수여도 proposed_entries ≤ 5."""
    feedback = [
        {"event_type": "reject", "reason": f"사유{i} 회피 요소"} for i in range(10)
    ]
    result = extract_brand_memory_candidates(feedback)
    assert len(result["proposed_entries"]) <= MAX_PROPOSED_ENTRIES


# ─── graceful ───────────────────────────────────────────────────────────


def test_empty_input_returns_empty_no_raise() -> None:
    """빈/None 입력 → 빈 proposed_entries (예외 전파 0 — graceful)."""
    assert extract_brand_memory_candidates(None, None)["proposed_entries"] == []
    assert extract_brand_memory_candidates([], [])["proposed_entries"] == []


def test_non_dict_items_are_skipped_gracefully() -> None:
    """잘못된(non-dict) 입력 항목은 skip — 예외 0."""
    feedback = ["not-a-dict", None, {"event_type": "like"}]  # type: ignore[list-item]
    result = extract_brand_memory_candidates(feedback)  # type: ignore[arg-type]
    # 유효한 like 1건만 반영 (success_pattern)
    assert _entries_by_type(result, ENTRY_SUCCESS_PATTERN)


# ─── PII 마스킹 ─────────────────────────────────────────────────────────


def test_pii_in_reason_is_masked_everywhere() -> None:
    """★ reason 의 이메일/전화 → [masked] (content/source_evidence 어디에도 raw PII 0)."""
    feedback = [
        {
            "event_type": "dislike",
            "reason": "연락처 010-1234-5678 또는 me@example.com 으로 알려주세요",
        }
    ]
    result = extract_brand_memory_candidates(feedback)
    blob = repr(result)
    assert "010-1234-5678" not in blob
    assert "me@example.com" not in blob
    assert "[masked]" in blob


# ─── 충돌 검사 ──────────────────────────────────────────────────────────


def test_conflict_with_existing_brand_memory_is_separated() -> None:
    """기존 Brand Memory 와 (entry_type, content) 일치 → conflicts 분리 (proposed 제외)."""
    feedback = [{"event_type": "dislike"}, {"event_type": "reject"}]
    # 먼저 충돌 없는 추출로 content 확인
    base = extract_brand_memory_candidates(feedback)
    rej = _entries_by_type(base, ENTRY_REJECTION_PATTERN)[0]
    existing = [{"entry_type": rej["entry_type"], "content": rej["content"]}]

    result = extract_brand_memory_candidates(
        feedback, current_brand_memory=existing
    )
    # proposed 에서는 제외, conflicts 에 별도 표시
    assert not _entries_by_type(result, ENTRY_REJECTION_PATTERN)
    assert any(
        c["entry_type"] == ENTRY_REJECTION_PATTERN
        and c.get("conflicts_with_existing") is True
        for c in result["conflicts"]
    )


# ─── repo 영속화 (mock) ─────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_run_persists_only_high_confidence_with_mock_repo() -> None:
    """persist=True + repo mock → confidence ≥ 0.9(명시 선호)만 add_entry (agent_io §7.5)."""
    repo = MagicMock()
    repo.add_entry = AsyncMock(return_value={"entry_type": "avoid_phrase", "ok": True})

    feedback = [
        {"event_type": "reject", "reason": "과장 광고 표현 회피"},  # confidence 0.9
        {"event_type": "dislike"},  # confidence 0.3 (영속화 제외)
    ]
    result = await run_brand_memory_extractor(
        feedback, brand_id="brand-1", repo=repo, persist=True,
    )
    # 0.9 후보만 영속화 (0.3 은 제외)
    assert repo.add_entry.await_count >= 1
    for call in repo.add_entry.await_args_list:
        # add_entry(brand_id, entry_type, content, confidence=...)
        assert call.kwargs.get("confidence", 0.0) >= CONFIDENCE_EXPLICIT
    assert "persisted" in result


@pytest.mark.asyncio
async def test_run_persist_repo_failure_is_graceful() -> None:
    """repo.add_entry 실패해도 graceful (예외 0, persisted 비어도 추출 결과 보존)."""
    repo = MagicMock()
    repo.add_entry = AsyncMock(side_effect=RuntimeError("simulated db failure"))

    feedback = [{"event_type": "reject", "reason": "과장 광고 표현 회피"}]
    # 예외 전파 0
    result = await run_brand_memory_extractor(
        feedback, brand_id="brand-1", repo=repo, persist=True,
    )
    assert result["proposed_entries"]  # 추출 자체는 성공
    assert result["persisted"] == []  # 저장은 실패 → 빈 리스트 (graceful)


@pytest.mark.asyncio
async def test_run_persists_to_real_in_memory_brand_memory_repo() -> None:
    """BrandMemoryRepo(in-memory) round-trip — 추출 후보가 실제 repo 에 적재."""
    repo = BrandMemoryRepo(supabase_client=None, in_memory_store={})
    repo._reset_for_test()
    feedback = [{"event_type": "reject", "reason": "과장 광고 표현 회피"}]
    result = await run_brand_memory_extractor(
        feedback, brand_id="brand-rt", repo=repo, persist=True,
    )
    assert result["persisted"]
    entries = await repo.list_for_brand("brand-rt")
    assert len(entries) >= 1


@pytest.mark.asyncio
async def test_run_without_repo_skips_persist() -> None:
    """repo 미제공/persist=False → 추출만 (persisted 키 없음, 예외 0)."""
    feedback = [{"event_type": "like"}]
    result = await run_brand_memory_extractor(feedback)
    assert "proposed_entries" in result
    assert "persisted" not in result
