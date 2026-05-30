"""Phase 9 Slice 2 — SelectionRepo / FeedbackRepo / BrandMemoryRepo graceful CRUD + reason PII 마스킹.

테스트 시나리오 (additive — 기존 baseline 회귀 0):
  SelectionRepo:
    1. in-memory select + get round-trip
    2. Supabase mock select (selected_plans insert)
    3. Supabase 실패 → in-memory fallback (graceful)
    4. option_index 0/1/2 보존
    5. get nonexistent → None
  FeedbackRepo:
    6. in-memory record + list_for_plan round-trip
    7. event_type like/dislike/reject/regenerate 보존
    8. ★ reason PII 마스킹 (이메일/전화 → [masked]) — security-review T1
    9. Supabase 실패 → in-memory fallback (graceful)
  BrandMemoryRepo (준비):
    10. in-memory add_entry + list_for_brand round-trip
    11. Supabase 실패 → in-memory fallback (graceful)

참조:
  - docs/decisions/phase_9_feedback_selection.md (ADR-030 §Verification)
  - docs/decisions/phase_9_brand_memory_prep.md (ADR-031 §Verification)
  - meta/security_reviews/2026-05-29_phase-9-feedback-pii.md (T1 reason PII 마스킹)
  - backend/fastapi/tests/test_db.py (PlansRepo graceful 패턴 + mock 모델)
"""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

import pytest

from backend.fastapi.db.repositories.brand_memory_repo import BrandMemoryRepo
from backend.fastapi.db.repositories.feedback_repo import FeedbackRepo, mask_pii
from backend.fastapi.db.repositories.selection_repo import SelectionRepo


# ─── fixtures (autouse _reset 패턴) ────────────────────────────────────


@pytest.fixture
def selection_repo() -> SelectionRepo:
    repo = SelectionRepo(supabase_client=None, in_memory_store={})
    repo._reset_for_test()
    return repo


@pytest.fixture
def feedback_repo() -> FeedbackRepo:
    repo = FeedbackRepo(supabase_client=None, in_memory_store={})
    repo._reset_for_test()
    return repo


@pytest.fixture
def brand_memory_repo() -> BrandMemoryRepo:
    repo = BrandMemoryRepo(supabase_client=None, in_memory_store={})
    repo._reset_for_test()
    return repo


# ─── SelectionRepo ─────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_selection_in_memory_select_and_get(selection_repo: SelectionRepo) -> None:
    """Supabase 없을 때 in-memory dict 로 select + get round-trip."""
    row = await selection_repo.select(
        "plan-1", 1, auth_user_id="user-a", selection_reason="이 안이 톤이 맞아요"
    )
    assert row["plan_id"] == "plan-1"
    assert row["selected_option_index"] == 1
    assert row["selection_reason"] == "이 안이 톤이 맞아요"

    fetched = await selection_repo.get("plan-1")
    assert fetched is not None
    assert fetched["selected_option_index"] == 1


@pytest.mark.asyncio
async def test_selection_supabase_mock_select() -> None:
    """Supabase mock select — selected_plans insert round-trip."""
    mock_client = MagicMock()
    mock_resp = MagicMock()
    mock_resp.data = [
        {"id": "sel-1", "plan_id": "plan-2", "selected_option_index": 2}
    ]
    mock_client.table.return_value.insert.return_value.execute.return_value = mock_resp

    repo = SelectionRepo(supabase_client=mock_client, in_memory_store={})
    row = await repo.select("plan-2", 2)
    assert row["id"] == "sel-1"
    assert row["selected_option_index"] == 2
    # in-memory mirror 로 get 일관성
    fetched = await repo.get("plan-2")
    assert fetched is not None


@pytest.mark.asyncio
async def test_selection_supabase_failure_falls_back_to_in_memory() -> None:
    """graceful: Supabase 실패 → in-memory 저장 (raise 0, 사용자 차단 0)."""
    mock_client = MagicMock()
    mock_client.table.return_value.insert.return_value.execute.side_effect = (
        RuntimeError("simulated network failure")
    )
    store: dict[str, dict[str, Any]] = {}
    repo = SelectionRepo(supabase_client=mock_client, in_memory_store=store)
    row = await repo.select("plan-3", 0)
    assert row["selected_option_index"] == 0
    assert "plan-3" in store


@pytest.mark.asyncio
async def test_selection_option_index_boundaries(selection_repo: SelectionRepo) -> None:
    """option_index 0/1/2 모두 정상 저장 (DB check 0–2 정합 — repo 레벨은 값 보존)."""
    for idx in (0, 1, 2):
        row = await selection_repo.select(f"plan-idx-{idx}", idx)
        assert row["selected_option_index"] == idx


@pytest.mark.asyncio
async def test_selection_get_nonexistent_returns_none(selection_repo: SelectionRepo) -> None:
    """존재하지 않는 plan_id 조회 시 None (graceful)."""
    assert await selection_repo.get("nope") is None


# ─── FeedbackRepo ──────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_feedback_in_memory_record_and_list(feedback_repo: FeedbackRepo) -> None:
    """Supabase 없을 때 in-memory record + list_for_plan round-trip."""
    await feedback_repo.record("plan-1", "like", option_index=0)
    await feedback_repo.record("plan-1", "dislike", option_index=2, reason="좀 평범해요")
    events = await feedback_repo.list_for_plan("plan-1")
    assert len(events) == 2
    assert events[0]["event_type"] == "like"
    assert events[1]["event_type"] == "dislike"
    assert events[1]["option_index"] == 2


@pytest.mark.asyncio
async def test_feedback_event_types_preserved(feedback_repo: FeedbackRepo) -> None:
    """event_type like/dislike/reject/regenerate 모두 보존 (enum 정합)."""
    for et in ("like", "dislike", "reject", "regenerate"):
        await feedback_repo.record("plan-et", et)
    events = await feedback_repo.list_for_plan("plan-et")
    assert {e["event_type"] for e in events} == {"like", "dislike", "reject", "regenerate"}


@pytest.mark.asyncio
async def test_feedback_reason_pii_masked_on_record(feedback_repo: FeedbackRepo) -> None:
    """★ reason PII 저장 전 마스킹 (security-review T1) — 이메일/전화 → [masked]."""
    row = await feedback_repo.record(
        "plan-pii",
        "reject",
        reason="연락처 010-1234-5678 또는 me@example.com 으로 주세요",
    )
    assert "010-1234-5678" not in row["reason"]
    assert "me@example.com" not in row["reason"]
    assert "[masked]" in row["reason"]
    # 저장된 값(list)도 마스킹되어 있어야 함 (raw PII 잔존 0)
    events = await feedback_repo.list_for_plan("plan-pii")
    assert "010-1234-5678" not in events[0]["reason"]
    assert "me@example.com" not in events[0]["reason"]


def test_mask_pii_patterns() -> None:
    """mask_pii: 이메일/전화/주민/카드 마스킹 + None/빈 통과."""
    assert mask_pii(None) is None
    assert mask_pii("") == ""
    assert mask_pii("그냥 좋아요") == "그냥 좋아요"  # PII 없음 — 불변
    assert "[masked]" in mask_pii("주민 901201-1234567 노출")
    assert "[masked]" in mask_pii("카드 1234-5678-9012-3456")
    assert "[masked]" in mask_pii("전화 02-123-4567")
    assert "[masked]" in mask_pii("메일 a.b+c@sub.example.co.kr")


@pytest.mark.asyncio
async def test_feedback_supabase_failure_falls_back_to_in_memory() -> None:
    """graceful: Supabase 실패 → in-memory 저장 (raise 0)."""
    mock_client = MagicMock()
    mock_client.table.return_value.insert.return_value.execute.side_effect = (
        RuntimeError("simulated network failure")
    )
    store: dict[str, list[dict[str, Any]]] = {}
    repo = FeedbackRepo(supabase_client=mock_client, in_memory_store=store)
    row = await repo.record("plan-fb", "like")
    assert row["event_type"] == "like"
    assert "plan-fb" in store


# ─── BrandMemoryRepo (준비) ─────────────────────────────────────────────


@pytest.mark.asyncio
async def test_brand_memory_in_memory_add_and_list(brand_memory_repo: BrandMemoryRepo) -> None:
    """Supabase 없을 때 in-memory add_entry + list_for_brand round-trip (수동/준비용)."""
    await brand_memory_repo.add_entry("brand-1", "preferred_tone", "친근하고 담백한 톤")
    await brand_memory_repo.add_entry(
        "brand-1", "avoid_phrase", "과장 광고 표현", source_plan_id="plan-9", confidence=0.9
    )
    entries = await brand_memory_repo.list_for_brand("brand-1")
    assert len(entries) == 2
    assert entries[0]["entry_type"] == "preferred_tone"
    assert entries[1]["confidence"] == 0.9
    assert entries[1]["source_plan_id"] == "plan-9"
    # 준비용 — is_user_locked 기본 False
    assert entries[0]["is_user_locked"] is False


@pytest.mark.asyncio
async def test_brand_memory_supabase_failure_falls_back_to_in_memory() -> None:
    """graceful: Supabase 실패 → in-memory 저장 (raise 0)."""
    mock_client = MagicMock()
    mock_client.table.return_value.insert.return_value.execute.side_effect = (
        RuntimeError("simulated network failure")
    )
    store: dict[str, list[dict[str, Any]]] = {}
    repo = BrandMemoryRepo(supabase_client=mock_client, in_memory_store=store)
    row = await repo.add_entry("brand-x", "success_pattern", "후크 강함")
    assert row["entry_type"] == "success_pattern"
    assert "brand-x" in store
