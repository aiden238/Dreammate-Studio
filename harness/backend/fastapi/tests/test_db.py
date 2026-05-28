"""Phase 1 Slice 5 — DB persistence + graceful failure 검증.

테스트 시나리오:
  1. env 미설정 → get_supabase_client() == None → status="skipped_no_db"
  2. client init 자체가 예외 → None → skipped_no_db (graceful)
  3. video_projects insert 예외 → status="failed_db_error", project_id=None
  4. video_projects 성공 + plan_candidates insert 예외 → 부분 실패 분기
  5. 정상 경로 → status="saved", project_id + plan_candidate_ids 채움
  6. raw_llm_json 에 plan + critic + rag_references 통합 저장 검증
  7. router e2e: DB 실패 시도 HTTP 200 유지 (사용자 차단 0건)
"""

from __future__ import annotations

from typing import Any

import pytest
from fastapi.testclient import TestClient

from backend.fastapi.db import save_video_planning
from backend.fastapi.db.supabase_client import get_supabase_client
from backend.fastapi.db.types import PersistenceResult
from backend.fastapi.main import app


client = TestClient(app)


# ─── Fake Supabase client (테이블/insert/execute 체이닝 모사) ──────────

class _FakeExecuteResult:
    def __init__(self, data: list[dict[str, Any]] | None) -> None:
        self.data = data


class _FakeInsert:
    def __init__(self, table_name: str, row: dict[str, Any], scenarios: dict[str, Any]) -> None:
        self.table_name = table_name
        self.row = row
        self.scenarios = scenarios

    def execute(self) -> _FakeExecuteResult:
        behavior = self.scenarios.get(self.table_name, "ok")
        if behavior == "raise":
            raise RuntimeError(f"simulated {self.table_name} insert failure")
        if behavior == "empty":
            return _FakeExecuteResult(data=[])
        # ok — 가짜 id 부여
        fake_id = f"fake-{self.table_name}-id"
        return _FakeExecuteResult(data=[{**self.row, "id": fake_id}])


class _FakeTable:
    def __init__(self, name: str, scenarios: dict[str, Any], log: list[dict[str, Any]]) -> None:
        self.name = name
        self.scenarios = scenarios
        self.log = log

    def insert(self, row: dict[str, Any]) -> _FakeInsert:
        # 호출 로그 (raw_llm_json 등 검증용)
        self.log.append({"table": self.name, "row": row})
        return _FakeInsert(self.name, row, self.scenarios)


class _FakeSupabaseClient:
    def __init__(self, scenarios: dict[str, Any] | None = None) -> None:
        self.scenarios = scenarios or {}
        self.log: list[dict[str, Any]] = []

    def table(self, name: str) -> _FakeTable:
        return _FakeTable(name, self.scenarios, self.log)


# ─── 1. get_supabase_client: env 미설정 시 None ────────────────────────

def test_get_client_returns_none_when_env_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    """SUPABASE_URL / SUPABASE_ANON_KEY 미설정 시 None 반환."""
    monkeypatch.setenv("SUPABASE_URL", "")
    monkeypatch.setenv("SUPABASE_ANON_KEY", "")
    from backend.fastapi.config import get_settings

    get_settings.cache_clear()

    client_obj = get_supabase_client()
    assert client_obj is None


def test_get_client_returns_none_when_only_url_set(monkeypatch: pytest.MonkeyPatch) -> None:
    """절반만 설정되어도 None (둘 다 필요)."""
    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("SUPABASE_ANON_KEY", "")
    from backend.fastapi.config import get_settings

    get_settings.cache_clear()

    assert get_supabase_client() is None


# ─── 2. save_video_planning: skip 분기 ────────────────────────────────

def test_save_skipped_when_no_client(monkeypatch: pytest.MonkeyPatch) -> None:
    """get_supabase_client() == None → status="skipped_no_db", project_id=None."""

    def fake_no_client() -> None:
        return None

    monkeypatch.setattr(
        "backend.fastapi.db.get_supabase_client", fake_no_client
    )

    result = save_video_planning(
        request_id="req-1",
        input_text="유튜브 첫 영상",
        locale="ko-KR",
        plan_dict={"name": "테스트", "option_index": 0},
        critic_dict=None,
        rag_refs=[],
    )

    assert isinstance(result, PersistenceResult)
    assert result.status == "skipped_no_db"
    assert result.project_id is None
    assert result.plan_candidate_ids == []
    assert result.error_reason is None


# ─── 3. save_video_planning: client.table 예외 흡수 ───────────────────

def test_save_handles_video_projects_insert_exception(monkeypatch: pytest.MonkeyPatch) -> None:
    """video_projects insert 가 raise → status="failed_db_error", project_id=None."""
    fake_client = _FakeSupabaseClient(scenarios={"video_projects": "raise"})
    monkeypatch.setattr(
        "backend.fastapi.db.get_supabase_client", lambda: fake_client
    )

    result = save_video_planning(
        request_id="req-2",
        input_text="건강한 식단 쇼츠",
        locale="ko-KR",
        plan_dict={"name": "테스트", "option_index": 0},
        critic_dict=None,
        rag_refs=[],
    )

    assert result.status == "failed_db_error"
    assert result.project_id is None
    assert result.plan_candidate_ids == []
    assert result.error_reason == "video_projects_insert_failed"


def test_save_handles_plan_candidates_insert_exception(monkeypatch: pytest.MonkeyPatch) -> None:
    """video_projects 성공 + plan_candidates raise → 부분 실패 (project_id 반환, status fail)."""
    fake_client = _FakeSupabaseClient(scenarios={"plan_candidates": "raise"})
    monkeypatch.setattr(
        "backend.fastapi.db.get_supabase_client", lambda: fake_client
    )

    result = save_video_planning(
        request_id="req-3",
        input_text="요리 채널",
        locale="ko-KR",
        plan_dict={"name": "테스트", "option_index": 0, "approach_label": "narrative"},
        critic_dict={"overall_verdict": "approve"},
        rag_refs=[],
    )

    assert result.status == "failed_db_error"
    # video_projects 는 저장됐으므로 project_id 는 채워질 수 있음 (부분 성공 추적)
    assert result.project_id == "fake-video_projects-id"
    assert result.plan_candidate_ids == []
    assert result.error_reason == "plan_candidates_insert_failed"


# ─── 4. save_video_planning: 정상 경로 ────────────────────────────────

def test_save_success_returns_ids(monkeypatch: pytest.MonkeyPatch) -> None:
    """모든 insert 성공 → status="saved", project_id + plan_candidate_ids 채움."""
    fake_client = _FakeSupabaseClient(scenarios={})  # 모두 ok
    monkeypatch.setattr(
        "backend.fastapi.db.get_supabase_client", lambda: fake_client
    )

    result = save_video_planning(
        request_id="req-4",
        input_text="첫 영상 기획",
        locale="ko-KR",
        plan_dict={
            "name": "첫 영상",
            "option_index": 0,
            "concept": "초보 유튜버 안내",
            "hook": "구독자 0명에서 시작한 채널이 첫 영상으로 한 일",
            "approach_label": "narrative",
        },
        critic_dict={"overall_verdict": "approve", "overall_score_avg": 3.9},
        rag_refs=[{"source_id": "seed-001", "title": "유튜브 후크"}],
    )

    assert result.status == "saved"
    assert result.project_id == "fake-video_projects-id"
    assert result.plan_candidate_ids == ["fake-plan_candidates-id"]
    assert result.error_reason is None


def test_raw_llm_json_includes_plan_critic_and_rag(monkeypatch: pytest.MonkeyPatch) -> None:
    """plan_candidates.raw_llm_json 에 plan / critic_evaluation / rag_references 통합 저장."""
    fake_client = _FakeSupabaseClient(scenarios={})
    monkeypatch.setattr(
        "backend.fastapi.db.get_supabase_client", lambda: fake_client
    )

    save_video_planning(
        request_id="req-5",
        input_text="테스트 입력",
        locale="ko-KR",
        plan_dict={"name": "테스트", "option_index": 0, "approach_label": "informational"},
        critic_dict={"overall_verdict": "approve", "scores": {"hook_strength": 4}},
        rag_refs=[
            {"source_id": "seed-001", "title": "후크 작성법", "similarity": 0.85},
            {"source_id": "seed-002", "title": "쇼츠 구조", "similarity": 0.78},
        ],
    )

    # video_projects + plan_candidates 두 번의 insert 호출 발생
    assert len(fake_client.log) == 2
    plan_insert = fake_client.log[1]
    assert plan_insert["table"] == "plan_candidates"

    raw = plan_insert["row"]["raw_llm_json"]
    assert "plan" in raw
    assert "critic_evaluation" in raw
    assert "rag_references" in raw
    assert raw["plan"]["name"] == "테스트"
    assert raw["critic_evaluation"]["overall_verdict"] == "approve"
    assert len(raw["rag_references"]) == 2
    assert raw["rag_references"][0]["source_id"] == "seed-001"


def test_save_handles_empty_insert_response(monkeypatch: pytest.MonkeyPatch) -> None:
    """insert 응답이 빈 데이터인 경우에도 graceful → failed_db_error."""
    fake_client = _FakeSupabaseClient(scenarios={"video_projects": "empty"})
    monkeypatch.setattr(
        "backend.fastapi.db.get_supabase_client", lambda: fake_client
    )

    result = save_video_planning(
        request_id="req-6",
        input_text="테스트",
        locale="ko-KR",
        plan_dict={"name": "테스트", "option_index": 0},
        critic_dict=None,
        rag_refs=[],
    )

    assert result.status == "failed_db_error"
    assert result.project_id is None


# ─── 5. Router e2e: DB 실패 시도 200 응답 ──────────────────────────────

def test_router_returns_200_even_when_db_fails(
    mock_intent_ok, mock_rag_fallback, mock_planning_ok, mock_critic_ok, mock_db_save_fail
) -> None:
    """DB 저장 실패 시도 HTTP 200 + meta.project_id=None + db_persistence status=warn.

    Phase 1 핵심 acceptance: DB 실패는 절대 사용자를 차단하지 않는다.
    """
    response = client.post(
        "/api/v1/generate",
        json={"input": "유튜브 첫 영상"},
    )

    assert response.status_code == 200, f"DB 실패 시 사용자 차단 (HTTP {response.status_code})"
    data = response.json()

    # meta.project_id 는 None (저장 실패)
    assert data["meta"]["project_id"] is None

    # validation.checks.db_persistence status=warn
    checks = data["validation"]["checks"]
    db_check = next((c for c in checks if c["name"] == "db_persistence"), None)
    assert db_check is not None, "db_persistence check가 validation에 노출되어야 함"
    assert db_check["status"] == "warn"
    assert "failed_db_error" in db_check["detail"]


# ─── Phase 5 Slice 2 — Supabase client (Protocol-based) + PlansRepo CRUD ──
#
# multi_slice_plan.md §Slice 2 작업 단위 (9): test_db.py — Supabase client mock + plans_repo CRUD 5+ 케이스.
# graceful 정책 검증:
#   - env 미설정 → get_supabase() == None → in-memory fallback
#   - Supabase 실패 → in-memory fallback (회귀 0)
#   - revise_history JSONB round-trip (Phase 4.5 ADR-016 + Phase 6 ReviseAttempt)
#   - canonical critic_evaluation JSONB round-trip (Phase 6 ADR-018)

from unittest.mock import MagicMock

from backend.fastapi.db.client import get_supabase
from backend.fastapi.db.repositories.plans_repo import PlansRepo


# ─── P5S2-1. get_supabase: env 미설정 시 None (graceful) ───────────────


def test_phase_5_get_supabase_no_env_returns_none(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """SUPABASE_URL / SUPABASE_ANON_KEY 미설정 시 None (Phase 5 graceful)."""
    monkeypatch.setenv("SUPABASE_URL", "")
    monkeypatch.setenv("SUPABASE_ANON_KEY", "")
    from backend.fastapi.config import get_settings

    get_settings.cache_clear()

    client_obj = get_supabase()
    assert client_obj is None


# ─── P5S2-2. PlansRepo in-memory create + get ─────────────────────────


@pytest.mark.asyncio
async def test_phase_5_plans_repo_in_memory_create_get() -> None:
    """Supabase 없을 때 in-memory dict 로 CRUD round-trip."""
    repo = PlansRepo(supabase_client=None, in_memory_store={})
    result = await repo.create("plan-1", {"mode": "discovery", "status": "draft"})
    assert result["mode"] == "discovery"
    assert result["status"] == "draft"

    fetched = await repo.get("plan-1")
    assert fetched is not None
    assert fetched["mode"] == "discovery"


# ─── P5S2-3. PlansRepo in-memory update ────────────────────────────────


@pytest.mark.asyncio
async def test_phase_5_plans_repo_in_memory_update() -> None:
    """update 시 기존 dict patch 적용."""
    store: dict[str, dict[str, Any]] = {
        "plan-1": {"mode": "discovery", "status": "draft"},
    }
    repo = PlansRepo(supabase_client=None, in_memory_store=store)
    updated = await repo.update("plan-1", {"status": "generated"})
    assert updated is not None
    assert updated["status"] == "generated"
    assert updated["mode"] == "discovery"  # 기존 값 보존


# ─── P5S2-4. PlansRepo in-memory delete ────────────────────────────────


@pytest.mark.asyncio
async def test_phase_5_plans_repo_in_memory_delete() -> None:
    """delete 후 store 에서 제거."""
    store: dict[str, dict[str, Any]] = {
        "plan-1": {"mode": "discovery"},
    }
    repo = PlansRepo(supabase_client=None, in_memory_store=store)
    deleted = await repo.delete("plan-1")
    assert deleted is True
    assert "plan-1" not in store


# ─── P5S2-5. PlansRepo Supabase mock — revise_history JSONB round-trip ──


@pytest.mark.asyncio
async def test_phase_5_plans_repo_supabase_create_with_revise_history() -> None:
    """Phase 4.5 revise_history JSONB round-trip via Supabase mock.

    multi_slice_plan.md §V5: revise_history JSONB 영속화 검증.
    Phase 4.5 ADR-016 (list[list[dict]]) + Phase 6 ReviseAttempt typing 호환.
    """
    revise_payload = [
        [
            {"attempt": 0, "action": "revise", "revised": True},
            {"attempt": 1, "action": "approve", "revised": False},
        ],
        [{"attempt": 0, "action": "approve", "revised": False}],
        [{"attempt": 0, "action": "approve", "revised": False}],
    ]

    mock_client = MagicMock()
    mock_resp = MagicMock()
    mock_resp.data = [
        {
            "id": "plan-1",
            "mode": "discovery",
            "revise_history": revise_payload,
        }
    ]
    mock_client.table.return_value.insert.return_value.execute.return_value = mock_resp

    repo = PlansRepo(supabase_client=mock_client, in_memory_store={})
    result = await repo.create(
        "plan-1",
        {
            "mode": "discovery",
            "revise_history": revise_payload,
        },
    )
    assert "revise_history" in result
    assert result["revise_history"] == revise_payload
    # plan별 attempt list 구조 보존 확인
    assert len(result["revise_history"]) == 3
    assert result["revise_history"][0][0]["action"] == "revise"


# ─── P5S2-6. PlansRepo Supabase 실패 시 in-memory fallback (graceful) ──


@pytest.mark.asyncio
async def test_phase_5_plans_repo_supabase_failure_falls_back_to_in_memory() -> None:
    """graceful: Supabase 실패 → in-memory 저장 (사용자 차단 0건).

    multi_slice_plan.md §Slice 2: graceful fallback 정책 검증.
    """
    mock_client = MagicMock()
    mock_client.table.return_value.insert.return_value.execute.side_effect = (
        RuntimeError("simulated network failure")
    )

    store: dict[str, dict[str, Any]] = {}
    repo = PlansRepo(supabase_client=mock_client, in_memory_store=store)
    result = await repo.create("plan-1", {"mode": "discovery"})
    # in-memory fallback PASS
    assert result["mode"] == "discovery"
    assert "plan-1" in store


# ─── P5S2-7. PlansRepo Supabase mock — canonical critic_evaluation 호환 ──


@pytest.mark.asyncio
async def test_phase_5_plans_repo_supabase_canonical_critic_round_trip() -> None:
    """Phase 6 canonical Critic verdict JSONB round-trip via Supabase mock.

    multi_slice_plan.md §V6: canonical (overall_score + dimensions) DB 호환 검증.
    Phase 6 ADR-018 정합.
    """
    canonical_critic = {
        "overall_score": 0.85,
        "overall_verdict": "approve",
        "dimensions": {
            "intent_fit": 0.9,
            "target_clarity": 0.8,
            "hook_strength": 0.85,
            "message_clarity": 0.85,
            "structure": 0.8,
            "feasibility": 0.9,
            "brand_consistency": 1.0,
            "differentiation": 0.7,
        },
    }

    mock_client = MagicMock()
    mock_resp = MagicMock()
    mock_resp.data = [
        {
            "id": "plan-2",
            "mode": "discovery",
            "critic_evaluation": canonical_critic,
            "recommended_plan_index": 0,
        }
    ]
    mock_client.table.return_value.insert.return_value.execute.return_value = mock_resp

    repo = PlansRepo(supabase_client=mock_client, in_memory_store={})
    result = await repo.create(
        "plan-2",
        {
            "mode": "discovery",
            "critic_evaluation": canonical_critic,
            "recommended_plan_index": 0,
        },
    )
    assert result["critic_evaluation"]["overall_score"] == 0.85
    assert result["critic_evaluation"]["overall_verdict"] == "approve"
    assert len(result["critic_evaluation"]["dimensions"]) == 8
    assert result["recommended_plan_index"] == 0


# ─── P5S2-8. PlansRepo get nonexistent → None ──────────────────────────


@pytest.mark.asyncio
async def test_phase_5_plans_repo_get_nonexistent_returns_none() -> None:
    """존재하지 않는 plan_id 조회 시 None (graceful)."""
    repo = PlansRepo(supabase_client=None, in_memory_store={})
    result = await repo.get("nonexistent-plan-id")
    assert result is None


# ─── P5S2-9. PlansRepo update nonexistent → None ───────────────────────


@pytest.mark.asyncio
async def test_phase_5_plans_repo_update_nonexistent_returns_none() -> None:
    """존재하지 않는 plan_id update 시 None (graceful, raise X)."""
    repo = PlansRepo(supabase_client=None, in_memory_store={})
    result = await repo.update("nonexistent-plan-id", {"status": "finalized"})
    assert result is None
