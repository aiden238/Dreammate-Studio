"""Phase 5 Slice 4 — SSE Progress event schema (security-review §T4).

검증 범위:
  1. /api/v1/plans/{plan_id}/progress 가 text/event-stream 응답.
  2. 4 progress + 1 complete = 5 이벤트 생성.
  3. event schema: {type, step, name?, message, plan_id, ...}.
  4. ALLOWED_ORIGINS 외 origin 은 403 차단.

multi_slice_plan.md §Slice 4 작업 단위 (4): 3+ 케이스. 본 파일은 4 케이스.
"""

from __future__ import annotations

import json

import pytest
from fastapi.testclient import TestClient

from backend.fastapi.main import app
from backend.fastapi.routers import sse as sse_module


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


# ─── 1. text/event-stream content-type ─────────────────────────────────


def test_sse_progress_returns_event_stream_content_type(client: TestClient) -> None:
    """/plans/{plan_id}/progress 가 text/event-stream content-type 반환."""
    resp = client.get("/api/v1/plans/test-plan/progress")
    assert resp.status_code == 200, resp.text
    content_type = resp.headers.get("content-type", "")
    assert "text/event-stream" in content_type


# ─── 2. 4 progress + 1 complete 이벤트 생성 ────────────────────────────


def test_sse_progress_emits_4_steps_plus_complete(client: TestClient) -> None:
    """4 progress + 1 complete = 5 이벤트."""
    resp = client.get("/api/v1/plans/test-plan/progress")
    text = resp.text
    # SSE 표준 포맷: 각 이벤트는 "data: {...}\n\n" 으로 끝남.
    events = [
        chunk
        for chunk in text.split("\n\n")
        if chunk.strip().startswith("data:")
    ]
    assert len(events) == 5, f"expected 5 events, got {len(events)}: {events}"


# ─── 3. event schema 검증 ──────────────────────────────────────────────


def test_sse_progress_event_schema_matches_contract(client: TestClient) -> None:
    """첫 이벤트 = progress/step=1/name=intent, 마지막 = complete."""
    resp = client.get("/api/v1/plans/test-plan/progress")
    parsed: list[dict] = []
    for chunk in resp.text.split("\n\n"):
        if not chunk.strip().startswith("data:"):
            continue
        payload = json.loads(chunk.strip()[len("data:"):].strip())
        parsed.append(payload)

    assert len(parsed) == 5
    # 첫 이벤트
    first = parsed[0]
    assert first["type"] == "progress"
    assert first["step"] == 1
    assert first["name"] == "intent"
    assert first["plan_id"] == "test-plan"
    assert "duration_estimate_sec" in first
    # 중간 단계 이름 검증
    names = [e.get("name") for e in parsed[:4]]
    assert names == ["intent", "rag", "planning", "critic"]
    # 마지막 = complete
    last = parsed[-1]
    assert last["type"] == "complete"
    assert last["step"] == 4
    assert last["plan_id"] == "test-plan"


# ─── 4. Origin 검증 — ALLOWED_ORIGINS 외 → 403 ────────────────────────


def test_sse_origin_disallowed_returns_403(
    client: TestClient, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """ALLOWED_ORIGINS 외 origin 헤더 → 403 origin_not_allowed."""
    # ALLOWED_ORIGINS 를 빈 set 으로 override → 모든 origin 차단 (no-origin 은 허용 유지)
    monkeypatch.setattr(sse_module, "ALLOWED_ORIGINS", set())

    resp = client.get(
        "/api/v1/plans/test-plan/progress",
        headers={"origin": "https://malicious.example.com"},
    )
    assert resp.status_code == 403
    assert resp.json()["detail"] == "origin_not_allowed"
