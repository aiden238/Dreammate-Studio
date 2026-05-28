"""Phase 5 Slice 4 — RLS 정책 검증 (security-review §T2).

본 테스트는 PostgreSQL 위 실제 RLS 정책 자체를 자동 검증하지 않는다
(Supabase 실 환경에서 SQL 적용 후 manual 검증). 대신 다음을 검증한다:

  1. PlansRepo 가 Supabase mock 의 결과를 그대로 반환 — RLS 차단 시
     Supabase 가 빈 응답(data=None)을 돌려주면 repo 도 None 반환 (graceful).
  2. 0003_rls_policy.sql 파일 존재 + 핵심 정책 구문 포함.
  3. anonymous endpoint (Phase 1 /generate) 와 authenticated endpoint 분리가
     db_schema.md 에 문서화됨 (정책 ↔ 문서 drift 차단).

multi_slice_plan.md §Slice 4 작업 단위 (3): 3+ 케이스. 본 파일은 4 케이스.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest

from backend.fastapi.db.repositories.plans_repo import PlansRepo


# ─── 1. RLS 차단 시도 — 다른 user plan 조회 → None ─────────────────────


@pytest.mark.asyncio
async def test_rls_other_user_plan_blocked_via_supabase_mock() -> None:
    """다른 user 의 plan 조회 시 Supabase RLS 가 차단 → repo.get None 반환.

    실 Supabase 동작: RLS 정책이 0 row 반환 → resp.data = None.
    PlansRepo.get 은 `if resp and getattr(resp, "data", None)` 조건에서
    falsy 처리 → in-memory fallback (빈 store) → None.
    """
    mock_client = MagicMock()
    mock_resp = MagicMock()
    mock_resp.data = None  # RLS 차단 = 빈 결과
    mock_client.table.return_value.select.return_value.eq.return_value.maybe_single.return_value.execute.return_value = mock_resp

    repo = PlansRepo(supabase_client=mock_client, in_memory_store={})
    result = await repo.get("other-user-plan-id")
    assert result is None


# ─── 2. 본인 plan 은 RLS 통과 → dict 반환 ──────────────────────────────


@pytest.mark.asyncio
async def test_rls_own_plan_accessible_via_supabase_mock() -> None:
    """본인 plan 은 RLS 통과 → resp.data 의 dict 그대로 반환."""
    own_plan = {
        "id": "own-plan-id",
        "auth_user_id": "user-1",
        "mode": "discovery",
        "status": "draft",
    }
    mock_client = MagicMock()
    mock_resp = MagicMock()
    mock_resp.data = own_plan
    mock_client.table.return_value.select.return_value.eq.return_value.maybe_single.return_value.execute.return_value = mock_resp

    repo = PlansRepo(supabase_client=mock_client, in_memory_store={})
    result = await repo.get("own-plan-id")
    assert result is not None
    assert result["auth_user_id"] == "user-1"
    assert result["mode"] == "discovery"


# ─── 3. 0003_rls_policy.sql 핵심 구문 검증 ─────────────────────────────


def test_rls_policy_sql_file_exists_with_core_clauses() -> None:
    """0003_rls_policy.sql 파일 + plans/brands/domains/series/video_projects RLS 활성화."""
    sql_path = (
        Path(__file__).resolve().parents[1]
        / "db" / "migrations" / "0003_rls_policy.sql"
    )
    assert sql_path.exists(), f"missing: {sql_path}"

    content = sql_path.read_text(encoding="utf-8")
    # RLS 활성화 5개 테이블
    assert "ALTER TABLE plans" in content and "ENABLE ROW LEVEL SECURITY" in content
    assert "ALTER TABLE brands" in content
    assert "ALTER TABLE domains" in content
    assert "ALTER TABLE series" in content
    assert "ALTER TABLE video_projects" in content
    # auth.uid() 핵심 사용
    assert "auth.uid()" in content
    # plans 정책에 auth_user_id 직접 검증
    assert "plans_authenticated" in content
    assert "auth_user_id" in content


# ─── 4. anonymous endpoint 분리 문서화 검증 (drift 차단) ───────────────


def test_rls_anonymous_endpoint_separation_documented() -> None:
    """db_schema.md 가 anonymous endpoint 와 authenticated endpoint 분리를 명시.

    drift 차단: SQL 정책이 변경되어도 db_schema.md 가 동시 갱신되어야 함.
    """
    # tests/ → backend/fastapi/ → backend/ → harness/ → docs/contracts/db_schema.md
    schema_path = (
        Path(__file__).resolve().parents[3] / "docs" / "contracts" / "db_schema.md"
    )
    assert schema_path.exists(), f"missing: {schema_path}"

    content = schema_path.read_text(encoding="utf-8")
    # RLS 섹션 존재
    assert "RLS" in content or "Row Level Security" in content
    # anonymous endpoint 분리 명시
    assert ("anonymous endpoint" in content) or ("anon role" in content)
    # /generate (Phase 1) 또는 /plans/start anon 분리 명시
    assert ("/api/v1/generate" in content) or ("/plans/start" in content)
