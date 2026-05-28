"""Phase 4 plans router smoke tests (Slice 1) + Phase 4.5 Slice 2 revise loop.

검증 항목 (acceptance.md A1 + A4 + Phase 4.5 A2/A3):
  - POST /api/v1/plans/start → 201 + plan_id 발급
  - POST /api/v1/plans/{plan_id}/wizard/{step} → 200 + next_step hint
  - POST /api/v1/plans/{plan_id}/generate → 202 (Slice 1 skeleton)
  - GET /api/v1/plans/{plan_id} → 200 + PlanResource
  - 미발견 plan_id → 404 + ErrorEnvelope (INV-006)
  - Phase 1 endpoint X-API-Deprecation header (A4 회귀 0)
  - Phase 1 endpoint body 무변경 (A4 회귀 0)
  - [Phase 4.5 Slice 2] revise_history 응답 포함 + 최대 2회 차단 + approve no-revise
"""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from backend.fastapi.main import app

client = TestClient(app)


# ─── POST /plans/start ────────────────────────────────────────────────

def test_plans_start_creates_plan_id() -> None:
    """신규 plan_id 발급 + 201 + locale echo."""
    r = client.post("/api/v1/plans/start", json={"locale": "ko-KR"})
    assert r.status_code == 201
    data = r.json()
    assert data["plan_id"]
    assert data["locale"] == "ko-KR"
    assert "created_at" in data


def test_plans_start_default_locale() -> None:
    """locale 미지정 시 ko-KR 기본값."""
    r = client.post("/api/v1/plans/start", json={})
    assert r.status_code == 201
    assert r.json()["locale"] == "ko-KR"


# ─── GET /plans/{plan_id} (미발견 → 404) ──────────────────────────────

def test_plans_get_unknown_returns_404_inv006() -> None:
    """미발견 plan_id → 404 + ErrorEnvelope (INV-006)."""
    r = client.get("/api/v1/plans/not-a-real-id")
    assert r.status_code == 404
    body = r.json()
    assert body["ok"] is False
    assert body["error"]["code"] == "INV-006"
    assert body["error"]["retry_allowed"] is False
    assert "request_id" in body["meta"]


def test_plans_wizard_step_unknown_plan_404() -> None:
    """존재하지 않는 plan_id에 wizard 호출 → 404 INV-006."""
    r = client.post(
        "/api/v1/plans/not-a-real-id/wizard/step1",
        json={"selected_card_id": "x"},
    )
    assert r.status_code == 404
    assert r.json()["error"]["code"] == "INV-006"


def test_plans_generate_unknown_plan_404() -> None:
    """존재하지 않는 plan_id에 generate 호출 → 404 INV-006."""
    r = client.post("/api/v1/plans/not-a-real-id/generate", json={})
    assert r.status_code == 404
    assert r.json()["error"]["code"] == "INV-006"


# ─── POST /plans/{plan_id}/wizard/{step} ──────────────────────────────

def test_plans_wizard_step_accepted_discovery() -> None:
    """Discovery step1 → step2 next_step hint."""
    start = client.post("/api/v1/plans/start", json={}).json()
    plan_id = start["plan_id"]
    r = client.post(
        f"/api/v1/plans/{plan_id}/wizard/step1",
        json={"selected_card_id": "brand-a"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["plan_id"] == plan_id
    assert data["step"] == "step1"
    assert data["accepted"] is True
    assert data["next_step"] == "step2"


def test_plans_wizard_step7_next_is_generate() -> None:
    """Discovery step7 → next_step=generate (terminal)."""
    start = client.post("/api/v1/plans/start", json={}).json()
    plan_id = start["plan_id"]
    r = client.post(
        f"/api/v1/plans/{plan_id}/wizard/step7",
        json={"user_input": "최종 입력"},
    )
    assert r.status_code == 200
    assert r.json()["next_step"] == "generate"


def test_plans_wizard_step_quick_chain() -> None:
    """Quick mode chain — quick.initial → quick.clarify hint."""
    start = client.post("/api/v1/plans/start", json={}).json()
    plan_id = start["plan_id"]
    r = client.post(
        f"/api/v1/plans/{plan_id}/wizard/quick.initial",
        json={"user_input": "쇼츠 만들고 싶어"},
    )
    assert r.status_code == 200
    assert r.json()["next_step"] == "quick.clarify"


# ─── POST /plans/{plan_id}/generate (Slice 2 본격 — 200 Envelope) ─────

def test_plans_generate_returns_200_envelope(
    mock_intent_ok_plans,
    mock_rag_fallback_plans,
    mock_planning_parallel_3_ok,
    mock_critic_ok_plans,
    mock_db_save_ok_plans,
) -> None:
    """Phase 4 Slice 2: skeleton 202 → 본격 200 Envelope (3-plan).

    Slice 1 (이전): skeleton 202 + {"ok": True, "data": {"status": "accepted"}}.
    Slice 2 (현재): 본격 — Intent → RAG → 3-plan parallel → Critic → DB → Envelope 200.
    """
    start = client.post(
        "/api/v1/plans/start", json={"user_input": "유튜브 쇼츠"}
    ).json()
    plan_id = start["plan_id"]
    r = client.post(f"/api/v1/plans/{plan_id}/generate", json={})
    assert r.status_code == 200
    data = r.json()
    # Slice 2 본격: Envelope 구조 (meta / body / validation)
    assert "meta" in data
    assert "body" in data
    assert "validation" in data
    # 3-plan 본격 활성 (Slice 2 acceptance A2)
    assert len(data["body"]["plan_candidates"]) == 3


# ─── GET /plans/{plan_id} (정상) ──────────────────────────────────────

def test_plans_get_after_start_returns_plan_resource() -> None:
    """plans/start 직후 GET → status=created + envelope=None."""
    start = client.post("/api/v1/plans/start", json={}).json()
    plan_id = start["plan_id"]
    r = client.get(f"/api/v1/plans/{plan_id}")
    assert r.status_code == 200
    data = r.json()
    assert data["plan_id"] == plan_id
    assert data["status"] == "created"
    assert data["envelope"] is None  # Slice 2에서 채움


def test_plans_get_after_wizard_status_in_progress() -> None:
    """wizard step 진행 후 GET → status=wizard_in_progress."""
    start = client.post("/api/v1/plans/start", json={}).json()
    plan_id = start["plan_id"]
    client.post(
        f"/api/v1/plans/{plan_id}/wizard/step1",
        json={"selected_card_id": "x"},
    )
    r = client.get(f"/api/v1/plans/{plan_id}")
    assert r.status_code == 200
    assert r.json()["status"] == "wizard_in_progress"


# ─── Phase 1 endpoint 회귀 0 (acceptance A4) ──────────────────────────

def test_phase_1_generate_has_deprecation_header(mock_pipeline_ok) -> None:
    """Phase 1 endpoint X-API-Deprecation header 노출 (ADR-014, 실 동작 무변경)."""
    r = client.post(
        "/api/v1/generate",
        json={"input": "유튜브 쇼츠 만들기"},
    )
    assert r.status_code == 200  # Phase 1 동작 무변경
    assert "X-API-Deprecation" in r.headers
    assert "Phase 4" in r.headers["X-API-Deprecation"]
    # 새 contract endpoint 안내 포함
    assert "/plans/" in r.headers["X-API-Deprecation"]


def test_phase_1_generate_body_unchanged(mock_pipeline_ok) -> None:
    """Phase 1 endpoint response body 정합 — plan_candidates length 1 (Phase 1 호환)."""
    r = client.post(
        "/api/v1/generate",
        json={"input": "유튜브 쇼츠 만들기"},
    )
    assert r.status_code == 200
    data = r.json()
    # Phase 1 envelope 구조 그대로
    assert "meta" in data
    assert "body" in data
    assert "validation" in data
    assert "plan_candidates" in data["body"]
    # Phase 1은 1개만 (Slice 2에서 3개로 활성)
    assert len(data["body"]["plan_candidates"]) == 1


def test_phase_1_generate_intent_block_has_deprecation_header(mock_intent_block) -> None:
    """Phase 1 endpoint error path도 X-API-Deprecation header 노출 (422 INV-001)."""
    r = client.post(
        "/api/v1/generate",
        json={"input": "오늘 서울 날씨 알려줘"},
    )
    assert r.status_code == 422  # Phase 1 동작 무변경
    assert "X-API-Deprecation" in r.headers
    body = r.json()
    assert body["error"]["code"] == "INV-001"  # Phase 1 error 코드 그대로


# ─── Phase 4.5 Slice 2 — Critic revise loop 통합 케이스 ──────────────


def _build_revise_verdict(plan: dict[str, Any]) -> dict[str, Any]:
    """revise verdict — overall_verdict 강제."""
    target_id = str(plan.get("plan_id") or "")
    scores = {
        "intent_fit": 3, "target_clarity": 1, "hook_strength": 1,
        "message_clarity": 3, "structure": 3, "feasibility": 3,
        "brand_consistency": 4, "differentiation": 2,
    }
    return {
        "target_plan_id": target_id,
        "scores": scores,
        "reasons": {k: "—" for k in scores},
        "suggestions": {k: "—" for k in scores},
        "overall_score_avg": round(sum(scores.values()) / len(scores), 4),
        "overall_verdict": "revise",
        "blocking_issues": ["hook 약함"],
        "revise_round": 0,
    }


def _build_approve_verdict(plan: dict[str, Any]) -> dict[str, Any]:
    """approve verdict."""
    target_id = str(plan.get("plan_id") or "")
    scores = {
        "intent_fit": 4, "target_clarity": 4, "hook_strength": 4,
        "message_clarity": 4, "structure": 4, "feasibility": 4,
        "brand_consistency": 5, "differentiation": 4,
    }
    return {
        "target_plan_id": target_id,
        "scores": scores,
        "reasons": {k: "—" for k in scores},
        "suggestions": {k: "—" for k in scores},
        "overall_score_avg": round(sum(scores.values()) / len(scores), 4),
        "overall_verdict": "approve",
        "blocking_issues": [],
        "revise_round": 0,
    }


@pytest.fixture
def mock_critic_always_revise_plans(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    """routers.plans.run_critic → 항상 revise (revise loop max 차단 테스트용)."""

    def fake(plan: dict[str, Any], *args: Any, **kwargs: Any) -> dict[str, Any]:
        return _build_revise_verdict(plan)

    monkeypatch.setattr("backend.fastapi.routers.plans.run_critic", fake)
    return MagicMock()


@pytest.fixture
def mock_rewriter_ok_plans(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    """routers.plans.run_rewriter → 입력 plan을 그대로 반환 (revise 시도는 카운트됨)."""

    async def fake(
        plan: dict[str, Any], verdict: dict[str, Any], **kwargs: Any,
    ) -> dict[str, Any]:
        out = dict(plan)
        out["_rewriter_model"] = "gpt-4o-mini"
        # name 갱신 → revise 가 실제 일어났음을 추적 가능
        out["name"] = f"개선-{out.get('name', 'x')}"[:20]
        return out

    monkeypatch.setattr("backend.fastapi.routers.plans.run_rewriter", fake)
    return MagicMock()


def test_revise_history_present_in_response(
    mock_intent_ok_plans,
    mock_rag_fallback_plans,
    mock_planning_parallel_3_ok,
    mock_critic_ok_plans,  # approve — revise 시도 0
    mock_db_save_ok_plans,
) -> None:
    """Phase 4.5 A3: 응답 Body 에 revise_history 키 존재 + plans_count 일치.

    Critic approve verdict → revise attempt 0회. revise_history 는
    plan별 [{"attempt": 0, "action": "approve", "revised": False}] 1개 entry.
    """
    start = client.post(
        "/api/v1/plans/start", json={"user_input": "유튜브 쇼츠"},
    ).json()
    plan_id = start["plan_id"]
    r = client.post(f"/api/v1/plans/{plan_id}/generate", json={})
    assert r.status_code == 200
    body = r.json()["body"]
    assert "revise_history" in body
    histories = body["revise_history"]
    assert histories is not None
    # plans_count 와 outer list 길이 일치
    assert len(histories) == len(body["plan_candidates"])
    # 각 plan 의 첫 attempt 는 approve (revise 안 일어남)
    for h in histories:
        assert isinstance(h, list)
        assert len(h) >= 1
        assert h[0]["attempt"] == 0
        assert h[0]["action"] == "approve"
        assert h[0]["revised"] is False


def test_revise_loop_max_2_blocks_third_revise(
    mock_intent_ok_plans,
    mock_rag_fallback_plans,
    mock_planning_parallel_3_ok,
    mock_critic_always_revise_plans,
    mock_rewriter_ok_plans,
    mock_db_save_ok_plans,
) -> None:
    """Phase 4.5 A2: Critic이 항상 revise를 반환해도 revise 횟수 ≤ 2 (max 차단).

    settings.critic_max_revise = 2 (기본).
    revise_history per plan 길이 = 3 (attempt 0 / 1 / 2). attempt 2 에서 max_reached=True.
    """
    start = client.post(
        "/api/v1/plans/start", json={"user_input": "유튜브 쇼츠"},
    ).json()
    plan_id = start["plan_id"]
    r = client.post(f"/api/v1/plans/{plan_id}/generate", json={})
    assert r.status_code == 200
    histories = r.json()["body"]["revise_history"]
    assert histories is not None
    for h in histories:
        # 3 attempts: 0,1,2 (max_revise=2 + 초기 attempt 1 = 총 3 entries)
        assert len(h) == 3, f"expected 3 attempts, got {len(h)}: {h}"
        # 마지막 attempt 는 max_reached
        assert h[-1].get("max_reached") is True
        # 마지막 attempt 는 revise 시도하지 않음
        assert h[-1]["revised"] is False
        # 처음 2개 attempt (0, 1) 은 revised=True (revise 실행됨)
        assert h[0]["revised"] is True
        assert h[1]["revised"] is True
        # 모든 attempt 의 action 은 'revise'
        for entry in h:
            assert entry["action"] == "revise"


def test_critic_approve_no_revise(
    mock_intent_ok_plans,
    mock_rag_fallback_plans,
    mock_planning_parallel_3_ok,
    mock_critic_ok_plans,  # 첫 critic approve
    mock_db_save_ok_plans,
) -> None:
    """Phase 4.5: 첫 critic 이 approve 면 revise 시도 0 + history 길이 1."""
    start = client.post(
        "/api/v1/plans/start", json={"user_input": "유튜브 쇼츠"},
    ).json()
    plan_id = start["plan_id"]
    r = client.post(f"/api/v1/plans/{plan_id}/generate", json={})
    assert r.status_code == 200
    histories = r.json()["body"]["revise_history"]
    assert histories is not None
    for h in histories:
        assert len(h) == 1  # attempt 0 만 (approve 즉시 종료)
        assert h[0]["action"] == "approve"
        assert h[0]["revised"] is False
        # max_reached 키 없음 (revise 시도 안 함)
        assert "max_reached" not in h[0]


# ─── OpenAPI 노출 확인 ────────────────────────────────────────────────

def test_phase_4_endpoints_in_openapi_spec() -> None:
    """Phase 4 4 endpoints가 OpenAPI 문서에 노출."""
    r = client.get("/openapi.json")
    assert r.status_code == 200
    paths = r.json().get("paths", {})
    assert "/api/v1/plans/start" in paths
    assert "/api/v1/plans/{plan_id}/wizard/{step}" in paths
    assert "/api/v1/plans/{plan_id}/generate" in paths
    assert "/api/v1/plans/{plan_id}" in paths
    # Phase 1 endpoint 공존 보존
    assert "/api/v1/generate" in paths
