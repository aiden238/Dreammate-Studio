"""Phase 9 Slice 4 — Brand Memory 준비: feedback/selection → candidate_knowledge 적재 경로.

테스트 시나리오 (additive — 기존 baseline 회귀 0):
  build_candidate_from_feedback:
    1. source_kind / status='pending' / content 구성 (event_type 라벨 + option_index)
    2. ★ reason PII 마스킹 (이메일/전화 → [masked]) — security-review T5
    3. source_kind='user_choice' (select 이벤트) 지정
  enqueue_feedback_candidate:
    4. in-memory list 적재 + status='pending' 유지
    5. Supabase mock INSERT (candidate_knowledge) round-trip
    6. Supabase 실패 → in-memory fallback (graceful, raise 0)
    7. ★ pending 아닌 candidate 도 pending 으로 강제 (자동 승격 차단 — NG12)
  ★ 자동 승격 미호출 검증:
    8. enqueue 후 status='pending' 고정 (promotion.transition 미호출, promoted 미진입 — NG12)
  BrandMemoryRepo (Slice 2 보강):
    9. in-memory add_entry + list_for_brand round-trip (수동/준비용)

참조:
  - docs/decisions/phase_9_brand_memory_prep.md (ADR-031 §Implementation + §Non-activation)
  - docs/contracts/db_schema.md §7.2 candidate_knowledge (source_kind / status='pending')
  - meta/security_reviews/2026-05-29_phase-9-feedback-pii.md (T5 적재 PII 차단)
  - backend/fastapi/rag/feedback_to_candidate.py (적재 경로)
"""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

import pytest

from backend.fastapi.db.repositories.brand_memory_repo import BrandMemoryRepo
from backend.fastapi.rag.feedback_to_candidate import (
    PENDING_STATUS,
    SOURCE_KIND_CHOICE,
    SOURCE_KIND_FEEDBACK,
    build_candidate_from_feedback,
    enqueue_feedback_candidate,
)


# ─── build_candidate_from_feedback ─────────────────────────────────────


def test_build_candidate_source_kind_status_and_content() -> None:
    """source_kind 기본 user_feedback + status='pending' + content 구성 (event_type/option_index)."""
    candidate = build_candidate_from_feedback(
        "plan-1", "dislike", option_index=2
    )
    assert candidate["source_kind"] == SOURCE_KIND_FEEDBACK
    assert candidate["source_id"] == "plan-1"
    # ★ Phase 7 5단계 진입점 — pending (자동 승격 X, NG12)
    assert candidate["status"] == PENDING_STATUS
    assert candidate["metadata"]["event_type"] == "dislike"
    assert candidate["metadata"]["option_index"] == 2
    # content 에 option_index 반영
    assert "option_index=2" in candidate["content"]


def test_build_candidate_masks_pii_in_reason() -> None:
    """★ 적재 전 PII 마스킹 (security-review T5) — 이메일/전화 → [masked]."""
    candidate = build_candidate_from_feedback(
        "plan-pii",
        "reject",
        reason="연락처 010-1234-5678 또는 me@example.com 으로 주세요",
        option_index=1,
    )
    content = candidate["content"]
    assert "010-1234-5678" not in content
    assert "me@example.com" not in content
    assert "[masked]" in content


def test_build_candidate_source_kind_user_choice() -> None:
    """select 이벤트는 source_kind='user_choice' 로 적재 가능."""
    candidate = build_candidate_from_feedback(
        "plan-sel",
        "select",
        option_index=0,
        source_kind=SOURCE_KIND_CHOICE,
    )
    assert candidate["source_kind"] == SOURCE_KIND_CHOICE
    assert candidate["status"] == PENDING_STATUS


# ─── enqueue_feedback_candidate ────────────────────────────────────────


@pytest.mark.asyncio
async def test_enqueue_in_memory_appends_and_keeps_pending() -> None:
    """Supabase 없을 때 in-memory list 적재 + status='pending' 유지."""
    store: list[dict[str, Any]] = []
    candidate = build_candidate_from_feedback("plan-2", "like", option_index=0)
    row = await enqueue_feedback_candidate(candidate, in_memory_store=store)
    assert len(store) == 1
    assert row["status"] == PENDING_STATUS
    assert store[0]["source_kind"] == SOURCE_KIND_FEEDBACK


@pytest.mark.asyncio
async def test_enqueue_supabase_mock_insert() -> None:
    """Supabase mock — candidate_knowledge insert round-trip."""
    mock_client = MagicMock()
    mock_resp = MagicMock()
    mock_resp.data = [
        {"candidate_id": "cand-1", "source_kind": "user_feedback", "status": "pending"}
    ]
    mock_client.table.return_value.insert.return_value.execute.return_value = mock_resp

    store: list[dict[str, Any]] = []
    candidate = build_candidate_from_feedback("plan-3", "reject")
    row = await enqueue_feedback_candidate(
        candidate, supabase_client=mock_client, in_memory_store=store
    )
    assert row["candidate_id"] == "cand-1"
    assert row["status"] == PENDING_STATUS
    # candidate_knowledge 테이블 대상 insert
    mock_client.table.assert_called_with("candidate_knowledge")
    # in-memory mirror
    assert len(store) == 1


@pytest.mark.asyncio
async def test_enqueue_supabase_failure_falls_back_to_in_memory() -> None:
    """graceful: Supabase 실패 → in-memory 적재 (raise 0, 사용자 차단 0)."""
    mock_client = MagicMock()
    mock_client.table.return_value.insert.return_value.execute.side_effect = (
        RuntimeError("simulated network failure")
    )
    store: list[dict[str, Any]] = []
    candidate = build_candidate_from_feedback("plan-4", "regenerate")
    row = await enqueue_feedback_candidate(
        candidate, supabase_client=mock_client, in_memory_store=store
    )
    assert row["status"] == PENDING_STATUS
    assert len(store) == 1


@pytest.mark.asyncio
async def test_enqueue_forces_pending_status() -> None:
    """★ pending 아닌 candidate 도 pending 으로 강제 (자동 승격 차단 — NG12)."""
    store: list[dict[str, Any]] = []
    # 외부에서 status 를 promoted 로 조작해도 enqueue 가 pending 으로 reset
    tampered = build_candidate_from_feedback("plan-5", "like")
    tampered["status"] = "promoted"
    row = await enqueue_feedback_candidate(tampered, in_memory_store=store)
    assert row["status"] == PENDING_STATUS
    assert store[0]["status"] == PENDING_STATUS


# ─── ★ 자동 승격 미호출 검증 (NG12) ─────────────────────────────────────


@pytest.mark.asyncio
async def test_no_auto_promotion_status_stays_pending(monkeypatch) -> None:
    """★ 적재 경로는 rag.promotion.transition 을 절대 호출하지 않는다 (NG12).

    feedback → candidate 적재 후 status 는 pending 고정 (promoted 미진입).
    promotion.transition 을 호출하면 즉시 실패하도록 monkeypatch — 호출 0 보장.
    """
    import backend.fastapi.rag.promotion as promotion_mod

    def _forbidden(*args: Any, **kwargs: Any) -> Any:  # pragma: no cover
        raise AssertionError(
            "promotion.transition must NOT be called in feedback adsorption path (NG12)"
        )

    monkeypatch.setattr(promotion_mod, "transition", _forbidden)

    store: list[dict[str, Any]] = []
    for et in ("like", "dislike", "reject", "regenerate"):
        candidate = build_candidate_from_feedback("plan-ng12", et)
        row = await enqueue_feedback_candidate(candidate, in_memory_store=store)
        # pending 고정 — 어떤 단계도 진행되지 않음
        assert row["status"] == PENDING_STATUS
    # 적재된 모든 후보가 pending (promoted/approved/filtered 미진입)
    assert all(c["status"] == PENDING_STATUS for c in store)


# ─── BrandMemoryRepo (Slice 2 보강 — 수동/준비용) ───────────────────────


@pytest.mark.asyncio
async def test_brand_memory_repo_add_and_list_prep() -> None:
    """BrandMemoryRepo add_entry/list — 수동/준비용 (자동 추출 X, NG1)."""
    repo = BrandMemoryRepo(supabase_client=None, in_memory_store={})
    repo._reset_for_test()
    await repo.add_entry("brand-1", "rejection_pattern", "과장된 후크 회피", confidence=0.7)
    entries = await repo.list_for_brand("brand-1")
    assert len(entries) == 1
    assert entries[0]["entry_type"] == "rejection_pattern"
    # 준비용 — 자동 추출 아님 (수동 입력, is_user_locked 기본 False)
    assert entries[0]["is_user_locked"] is False
