"""Phase 9 Slice 3 — select / feedback API endpoint 테스트 (ADR-030).

검증 항목:
  POST /plans/{id}/select:
    1. selected_option_index 0–2 + reason → 200 + SelectPlanResponse
    2. option_index 범위 밖(3) → 422 (Pydantic ge/le)
    3. 미발견 plan_id → 404 INV-006
    4. select 후 GET /plans/{id} status="selected"
  POST /plans/{id}/feedback:
    5. 4 event_type (like/dislike/reject/regenerate) → 200
    6. event_type enum 밖 → 422
    7. option_index 범위 밖 → 422
    8. 미발견 plan_id → 404
    9. reason PII (이메일) → 저장 시 마스킹 (GET 으로 확인)
  GET /plans/{id}/feedback:
    10. 기록된 feedback events 목록 반환
    11. 미발견 plan_id → 404

thin adapter — repo 호출 (graceful in-memory). TestClient + plans/start 로 plan_id 생성.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from backend.fastapi.main import app
from backend.fastapi.routers import plans as plans_router

client = TestClient(app)


# ─── fixtures ──────────────────────────────────────────────────────────


@pytest.fixture(autouse=True)
def _reset_repos() -> None:
    """각 테스트 전 select / feedback in-memory store 초기화 (격리)."""
    plans_router._selection_repo._reset_for_test()
    plans_router._feedback_repo._reset_for_test()


def _new_plan_id() -> str:
    """plans/start 로 신규 plan_id 발급."""
    r = client.post("/api/v1/plans/start", json={"user_input": "유튜브 쇼츠"})
    assert r.status_code == 201
    return r.json()["plan_id"]


# ─── POST /plans/{id}/select ──────────────────────────────────────────


def test_select_returns_200_with_response() -> None:
    """selected_option_index 0–2 + reason → 200 + SelectPlanResponse."""
    plan_id = _new_plan_id()
    r = client.post(
        f"/api/v1/plans/{plan_id}/select",
        json={"selected_option_index": 1, "selection_reason": "이 안이 톤이 맞아요"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["plan_id"] == plan_id
    assert data["selected_option_index"] == 1
    assert data["selection_reason"] == "이 안이 톤이 맞아요"
    assert data["selected_at"]


def test_select_option_index_0_and_2_valid() -> None:
    """경계값 0 / 2 모두 허용."""
    for idx in (0, 2):
        plan_id = _new_plan_id()
        r = client.post(
            f"/api/v1/plans/{plan_id}/select",
            json={"selected_option_index": idx},
        )
        assert r.status_code == 200
        assert r.json()["selected_option_index"] == idx


def test_select_option_index_out_of_range_422() -> None:
    """selected_option_index 3 (>2) → 422 (Pydantic le)."""
    plan_id = _new_plan_id()
    r = client.post(
        f"/api/v1/plans/{plan_id}/select",
        json={"selected_option_index": 3},
    )
    assert r.status_code == 422


def test_select_option_index_negative_422() -> None:
    """selected_option_index -1 (<0) → 422 (Pydantic ge)."""
    plan_id = _new_plan_id()
    r = client.post(
        f"/api/v1/plans/{plan_id}/select",
        json={"selected_option_index": -1},
    )
    assert r.status_code == 422


def test_select_unknown_plan_404() -> None:
    """미발견 plan_id → 404 INV-006."""
    r = client.post(
        "/api/v1/plans/not-a-real-id/select",
        json={"selected_option_index": 0},
    )
    assert r.status_code == 404
    assert r.json()["error"]["code"] == "INV-006"


def test_select_updates_plan_status() -> None:
    """select 후 GET /plans/{id} status="selected"."""
    plan_id = _new_plan_id()
    client.post(
        f"/api/v1/plans/{plan_id}/select",
        json={"selected_option_index": 0},
    )
    r = client.get(f"/api/v1/plans/{plan_id}")
    assert r.status_code == 200
    assert r.json()["status"] == "selected"


# ─── POST /plans/{id}/feedback ────────────────────────────────────────


@pytest.mark.parametrize("event_type", ["like", "dislike", "reject", "regenerate"])
def test_feedback_all_event_types_200(event_type: str) -> None:
    """4 event_type 모두 → 200 + FeedbackResponse."""
    plan_id = _new_plan_id()
    r = client.post(
        f"/api/v1/plans/{plan_id}/feedback",
        json={"event_type": event_type, "option_index": 0},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["plan_id"] == plan_id
    assert data["event_type"] == event_type
    assert data["option_index"] == 0
    assert data["recorded_at"]


def test_feedback_option_index_none_allowed() -> None:
    """option_index 미지정 (plan 전체 대상) → 200 + null."""
    plan_id = _new_plan_id()
    r = client.post(
        f"/api/v1/plans/{plan_id}/feedback",
        json={"event_type": "like"},
    )
    assert r.status_code == 200
    assert r.json()["option_index"] is None


def test_feedback_invalid_event_type_422() -> None:
    """event_type enum 밖 → 422 (Pydantic Literal)."""
    plan_id = _new_plan_id()
    r = client.post(
        f"/api/v1/plans/{plan_id}/feedback",
        json={"event_type": "love"},
    )
    assert r.status_code == 422


def test_feedback_option_index_out_of_range_422() -> None:
    """option_index 5 (>2) → 422."""
    plan_id = _new_plan_id()
    r = client.post(
        f"/api/v1/plans/{plan_id}/feedback",
        json={"event_type": "like", "option_index": 5},
    )
    assert r.status_code == 422


def test_feedback_unknown_plan_404() -> None:
    """미발견 plan_id → 404 INV-006."""
    r = client.post(
        "/api/v1/plans/not-a-real-id/feedback",
        json={"event_type": "like"},
    )
    assert r.status_code == 404
    assert r.json()["error"]["code"] == "INV-006"


def test_feedback_reason_pii_masked() -> None:
    """reason 의 PII(이메일) 는 저장 전 마스킹 → GET 으로 [masked] 확인 (security-review T1)."""
    plan_id = _new_plan_id()
    client.post(
        f"/api/v1/plans/{plan_id}/feedback",
        json={"event_type": "dislike", "reason": "연락주세요 me@example.com"},
    )
    r = client.get(f"/api/v1/plans/{plan_id}/feedback")
    assert r.status_code == 200
    events = r.json()["events"]
    assert len(events) == 1
    assert "me@example.com" not in events[0]["reason"]
    assert "[masked]" in events[0]["reason"]


# ─── GET /plans/{id}/feedback ─────────────────────────────────────────


def test_feedback_list_returns_recorded_events() -> None:
    """기록된 feedback events 목록 반환 (1:N)."""
    plan_id = _new_plan_id()
    client.post(
        f"/api/v1/plans/{plan_id}/feedback",
        json={"event_type": "like", "option_index": 0},
    )
    client.post(
        f"/api/v1/plans/{plan_id}/feedback",
        json={"event_type": "reject", "option_index": 1, "reason": "톤이 안 맞아요"},
    )
    r = client.get(f"/api/v1/plans/{plan_id}/feedback")
    assert r.status_code == 200
    data = r.json()
    assert data["plan_id"] == plan_id
    assert len(data["events"]) == 2
    event_types = {e["event_type"] for e in data["events"]}
    assert event_types == {"like", "reject"}


def test_feedback_list_unknown_plan_404() -> None:
    """미발견 plan_id → 404 INV-006."""
    r = client.get("/api/v1/plans/not-a-real-id/feedback")
    assert r.status_code == 404
    assert r.json()["error"]["code"] == "INV-006"


def test_feedback_list_empty_when_no_feedback() -> None:
    """피드백 없는 plan → 빈 events list."""
    plan_id = _new_plan_id()
    r = client.get(f"/api/v1/plans/{plan_id}/feedback")
    assert r.status_code == 200
    assert r.json()["events"] == []


# ─── OpenAPI 노출 ──────────────────────────────────────────────────────


def test_phase_9_endpoints_in_openapi() -> None:
    """Phase 9 select/feedback endpoint 가 OpenAPI 문서에 노출."""
    r = client.get("/openapi.json")
    assert r.status_code == 200
    paths = r.json().get("paths", {})
    assert "/api/v1/plans/{plan_id}/select" in paths
    assert "/api/v1/plans/{plan_id}/feedback" in paths
