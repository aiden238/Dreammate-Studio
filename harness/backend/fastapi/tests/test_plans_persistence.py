"""HIP-008 S3 plan envelope 영속 (_persist_plan_envelope) — 단위 (hermetic, mock supabase).

검증:
  - OFF(plans_repo_enabled=False, default) → no-op(False) + supabase 미접근 = in-memory only byte-identical
  - ON + mock supabase(update 행 존재) → update 경로(영속 시도 True)
  - ON + update 행 없음 → create(upsert) 경로
  - ON + supabase raise → graceful(raise 0, PlansRepo in-memory fallback)
참조: meta/audits/2026-06-05.md §B (HIP-008), meta/improvement_roadmap_hip006-010.md (008-S3).
"""

from __future__ import annotations

from unittest.mock import MagicMock

from backend.fastapi.config import Settings
from backend.fastapi.orchestration import moa_orchestrator as moa


def _entry() -> dict:
    return {"envelope": {"k": 1}, "status": "generated", "updated_at": "2026-06-05T00:00:00Z"}


def _mock_supabase(*, update_data, insert_data=None) -> MagicMock:
    sb = MagicMock()
    tbl = sb.table.return_value
    tbl.update.return_value.eq.return_value.execute.return_value = MagicMock(data=update_data)
    tbl.insert.return_value.execute.return_value = MagicMock(data=insert_data or [])
    return sb


async def test_persist_off_is_noop() -> None:
    sb = MagicMock()
    ok = await moa._persist_plan_envelope(
        "p1", _entry(), settings=Settings(plans_repo_enabled=False), supabase=sb
    )
    assert ok is False
    sb.table.assert_not_called()  # OFF = supabase 미접근 (byte-identical)


async def test_persist_on_update_existing_row() -> None:
    sb = _mock_supabase(update_data=[{"id": "p1", "status": "generated"}])
    ok = await moa._persist_plan_envelope(
        "p1", _entry(), settings=Settings(plans_repo_enabled=True), supabase=sb
    )
    assert ok is True
    assert sb.table.return_value.update.called
    assert not sb.table.return_value.insert.called  # 행 존재 → create 미호출


async def test_persist_on_upsert_creates_when_no_row() -> None:
    sb = _mock_supabase(update_data=[], insert_data=[{"id": "p1"}])  # update 0행 → create
    ok = await moa._persist_plan_envelope(
        "p1", _entry(), settings=Settings(plans_repo_enabled=True), supabase=sb
    )
    assert ok is True
    assert sb.table.return_value.insert.called  # upsert create 경로


async def test_persist_graceful_on_supabase_raise() -> None:
    sb = MagicMock()
    sb.table.side_effect = RuntimeError("db down")
    # raise 가 전파되지 않아야 한다 (PlansRepo in-memory fallback + 헬퍼 try/except)
    ok = await moa._persist_plan_envelope(
        "p1", _entry(), settings=Settings(plans_repo_enabled=True), supabase=sb
    )
    assert ok is True  # 시도됨, graceful 처리 — 생성 흐름 차단 0
