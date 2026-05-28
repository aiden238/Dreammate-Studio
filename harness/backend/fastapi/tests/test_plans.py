"""Phase 4 plans router smoke tests (Slice 1).

검증 항목 (acceptance.md A1 + A4):
  - POST /api/v1/plans/start → 201 + plan_id 발급
  - POST /api/v1/plans/{plan_id}/wizard/{step} → 200 + next_step hint
  - POST /api/v1/plans/{plan_id}/generate → 202 (Slice 1 skeleton)
  - GET /api/v1/plans/{plan_id} → 200 + PlanResource
  - 미발견 plan_id → 404 + ErrorEnvelope (INV-006)
  - Phase 1 endpoint X-API-Deprecation header (A4 회귀 0)
  - Phase 1 endpoint body 무변경 (A4 회귀 0)
"""

from __future__ import annotations

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


# ─── POST /plans/{plan_id}/generate (Slice 1 skeleton) ────────────────

def test_plans_generate_skeleton_returns_202() -> None:
    """Phase 4 Slice 1: skeleton 202 Accepted (Slice 2에서 본격)."""
    start = client.post("/api/v1/plans/start", json={}).json()
    plan_id = start["plan_id"]
    r = client.post(f"/api/v1/plans/{plan_id}/generate", json={})
    assert r.status_code == 202
    data = r.json()
    assert data["ok"] is True
    assert data["data"]["plan_id"] == plan_id
    assert data["data"]["status"] == "accepted"


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
