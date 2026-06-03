"""Phase 17 다-S3 — PkmRepo (graceful 개인 PKM CRUD) 테스트.

검증 축 (BrandMemoryRepo 테스트 패턴 계승):
  - in-memory: add_entry → list_for_user round-trip + per-user 격리 (교차 계정 0).
  - scope 필터: scope='personal' 만 반환 (series 혼재 시 분리).
  - Supabase 실패 → graceful in-memory fallback (raise 0).
"""

from __future__ import annotations

from typing import Any

import pytest

from backend.fastapi.db import PkmRepo


# ─── 1. in-memory round-trip + per-user 격리 ───────────────────────────


@pytest.mark.asyncio
async def test_add_and_list_in_memory() -> None:
    """add_entry → list_for_user round-trip (Supabase 없이 in-memory)."""
    repo = PkmRepo()
    row = await repo.add_entry("u-1", "preferred_tone", "담백한 톤")

    assert row["auth_user_id"] == "u-1"
    assert row["entry_type"] == "preferred_tone"
    assert row["content"] == "담백한 톤"
    assert row["scope"] == "personal"
    assert row["is_user_locked"] is False
    assert row["confidence"] == 0.5

    entries = await repo.list_for_user("u-1")
    assert len(entries) == 1
    assert entries[0]["content"] == "담백한 톤"


@pytest.mark.asyncio
async def test_per_user_isolation() -> None:
    """★ per-user 격리 — 한 user 의 entry 는 다른 user list 에 절대 노출 X."""
    repo = PkmRepo()
    await repo.add_entry("u-1", "preferred_tone", "u1 톤")
    await repo.add_entry("u-2", "preferred_tone", "u2 톤")

    u1 = await repo.list_for_user("u-1")
    u2 = await repo.list_for_user("u-2")

    assert [e["content"] for e in u1] == ["u1 톤"]
    assert [e["content"] for e in u2] == ["u2 톤"]
    # 미존재 user → 빈 리스트 (graceful).
    assert await repo.list_for_user("u-none") == []


@pytest.mark.asyncio
async def test_scope_filter_separates_personal_and_series() -> None:
    """list_for_user(scope=...) 는 해당 scope 만 반환 (personal/series 분리)."""
    repo = PkmRepo()
    await repo.add_entry("u-1", "preferred_tone", "personal 톤", scope="personal")
    await repo.add_entry("u-1", "success_pattern", "series 포맷", scope="series")

    personal = await repo.list_for_user("u-1", scope="personal")
    series = await repo.list_for_user("u-1", scope="series")

    assert [e["content"] for e in personal] == ["personal 톤"]
    assert [e["content"] for e in series] == ["series 포맷"]


@pytest.mark.asyncio
async def test_user_locked_and_confidence_passthrough() -> None:
    """is_user_locked / confidence 인자가 그대로 저장됨 (설계 §6.2 user_locked)."""
    repo = PkmRepo()
    row = await repo.add_entry(
        "u-1", "preferred_phrase", "고정 표현", confidence=0.95, is_user_locked=True,
    )
    assert row["is_user_locked"] is True
    assert row["confidence"] == 0.95


# ─── 2. Supabase 실패 → graceful fallback ──────────────────────────────


class _RaisingClient:
    """모든 table().insert/select 가 예외를 던지는 fake Supabase client."""

    def table(self, _name: str) -> Any:
        raise RuntimeError("supabase down")


@pytest.mark.asyncio
async def test_supabase_failure_graceful_fallback() -> None:
    """Supabase 호출 실패 → raise 0, in-memory fallback 으로 동작."""
    repo = PkmRepo(supabase_client=_RaisingClient())

    # add_entry: insert 실패해도 in-memory 에 적재 (graceful).
    row = await repo.add_entry("u-1", "avoid_phrase", "금지어")
    assert row["content"] == "금지어"

    # list_for_user: select 실패해도 in-memory mirror 반환 (graceful).
    entries = await repo.list_for_user("u-1")
    assert len(entries) == 1
    assert entries[0]["content"] == "금지어"
