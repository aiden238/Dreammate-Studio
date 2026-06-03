"""Phase 18 Slice S2 — branding session endpoint 테스트 (topic_discovery 배선).

검증 항목:
  POST /plans/{id}/branding/next:
    1. 첫 호출(답변 없음) → mode=ask + question + 2~4 options + step=1.
    2. 답변(answer) 동반 → 직전 질문에 answer 기록 + 다음 질문(step 증가).
    3. selected_option 동반 → 직전 질문에 selected_option 기록 (카드 우선).
    4. mode=done passthrough (agent 가 done 반환 시).
    5. 미발견 plan_id → 404 INV-006.
    6. graceful — agent 가 예외 → 500 아님, mode=done 안전 응답.
  POST /plans/{id}/branding/finalize:
    7. 후보 3개(5필드) 반환 + wizard_data.branding.candidates 저장.
    8. 미발견 plan_id → 404.
    9. graceful — agent 예외 → 500 아님, 빈 candidates.

★ mock — run_topic_discovery_ask / finalize 를 monkeypatch (실 LLM 호출 0, CI-safe).
   router 가 모듈 네임스페이스로 import 하므로 plans_router 의 심볼을 패치한다.
TestClient + plans/start 로 plan_id 생성.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from backend.fastapi.main import app
from backend.fastapi.routers import plans as plans_router

client = TestClient(app)


# ─── fixtures ──────────────────────────────────────────────────────────


def _new_plan_id() -> str:
    """plans/start 로 신규 plan_id 발급."""
    r = client.post("/api/v1/plans/start", json={"user_input": None})
    assert r.status_code == 201
    return r.json()["plan_id"]


def _patch_ask(monkeypatch, fn) -> None:
    monkeypatch.setattr(plans_router, "run_topic_discovery_ask", fn)


def _patch_finalize(monkeypatch, fn) -> None:
    monkeypatch.setattr(plans_router, "run_topic_discovery_finalize", fn)


# ─── POST /plans/{id}/branding/next ──────────────────────────────────


def test_branding_next_first_call_returns_ask(monkeypatch) -> None:
    """첫 호출(답변 없음) → mode=ask + question + 2~4 options + step=1."""
    def fake_ask(state, *, client=None, model=None):
        # 첫 호출이므로 history 는 비어 있어야 한다 (pending 추가 전).
        assert state["history"] == []
        return {
            "mode": "ask",
            "question": "어떤 분야의 영상을 만들고 싶나요?",
            "options": ["요리", "여행", "운동"],
            "rationale": "분야부터 좁힌다",
        }

    _patch_ask(monkeypatch, fake_ask)
    plan_id = _new_plan_id()
    r = client.post(f"/api/v1/plans/{plan_id}/branding/next", json={})
    assert r.status_code == 200
    data = r.json()
    assert data["mode"] == "ask"
    assert data["question"] == "어떤 분야의 영상을 만들고 싶나요?"
    assert 2 <= len(data["options"]) <= 4
    assert data["step"] == 1
    assert data["max_questions"] == plans_router.BRANDING_MAX_QUESTIONS


def test_branding_next_records_answer_and_advances(monkeypatch) -> None:
    """답변 동반 → 직전 질문에 answer 기록 + 다음 질문(step 증가)."""
    calls = {"n": 0}

    def fake_ask(state, *, client=None, model=None):
        calls["n"] += 1
        if calls["n"] == 1:
            return {"mode": "ask", "question": "Q1", "options": ["a", "b"], "rationale": ""}
        # 2번째 호출 — 직전 pending 항목에 answer 가 기록되어 들어와야 한다.
        assert state["history"][-1]["answer"] == "요리"
        return {"mode": "ask", "question": "Q2", "options": ["c", "d", "e"], "rationale": ""}

    _patch_ask(monkeypatch, fake_ask)
    plan_id = _new_plan_id()

    r1 = client.post(f"/api/v1/plans/{plan_id}/branding/next", json={})
    assert r1.json()["step"] == 1

    r2 = client.post(
        f"/api/v1/plans/{plan_id}/branding/next", json={"answer": "요리"}
    )
    assert r2.status_code == 200
    data = r2.json()
    assert data["mode"] == "ask"
    assert data["question"] == "Q2"
    assert data["step"] == 2


def test_branding_next_selected_option_recorded(monkeypatch) -> None:
    """selected_option 동반 → 카드 선택이 answer 로 기록 (카드 우선)."""
    calls = {"n": 0}

    def fake_ask(state, *, client=None, model=None):
        calls["n"] += 1
        if calls["n"] == 1:
            return {"mode": "ask", "question": "Q1", "options": ["요리", "여행"], "rationale": ""}
        # selected_option 이 answer 보다 우선 채택되어야 한다.
        assert state["history"][-1]["answer"] == "여행"
        return {"mode": "done", "question": None, "options": None, "rationale": ""}

    _patch_ask(monkeypatch, fake_ask)
    plan_id = _new_plan_id()
    client.post(f"/api/v1/plans/{plan_id}/branding/next", json={})
    r = client.post(
        f"/api/v1/plans/{plan_id}/branding/next",
        json={"selected_option": "여행", "answer": "무시될값"},
    )
    assert r.status_code == 200
    assert r.json()["mode"] == "done"


def test_branding_next_done_passthrough(monkeypatch) -> None:
    """agent 가 done 반환 → mode=done + question/options None + 새 질문 추가 없음."""
    def fake_ask(state, *, client=None, model=None):
        return {"mode": "done", "question": None, "options": None, "rationale": "충분"}

    _patch_ask(monkeypatch, fake_ask)
    plan_id = _new_plan_id()
    r = client.post(f"/api/v1/plans/{plan_id}/branding/next", json={})
    assert r.status_code == 200
    data = r.json()
    assert data["mode"] == "done"
    assert data["question"] is None
    assert data["options"] is None
    assert data["step"] == 0  # done — history 에 새 질문 추가 안 함


def test_branding_next_unknown_plan_404(monkeypatch) -> None:
    """미발견 plan_id → 404 INV-006 (agent 호출 전 차단)."""
    def fake_ask(state, *, client=None, model=None):  # pragma: no cover — 호출되면 안 됨
        raise AssertionError("agent should not be called for unknown plan")

    _patch_ask(monkeypatch, fake_ask)
    r = client.post("/api/v1/plans/not-a-real-id/branding/next", json={})
    assert r.status_code == 404
    assert r.json()["error"]["code"] == "INV-006"


def test_branding_next_graceful_on_agent_error(monkeypatch) -> None:
    """agent 예외 → 500 아님, mode=done 안전 응답 (plan 흐름 차단 0)."""
    def fake_ask(state, *, client=None, model=None):
        raise ValueError("LLM 파싱 실패")

    _patch_ask(monkeypatch, fake_ask)
    plan_id = _new_plan_id()
    r = client.post(f"/api/v1/plans/{plan_id}/branding/next", json={})
    assert r.status_code == 200
    data = r.json()
    assert data["mode"] == "done"
    assert data["step"] == 0


# ─── POST /plans/{id}/branding/finalize ──────────────────────────────


def test_branding_finalize_returns_and_stores_candidates(monkeypatch) -> None:
    """후보 3개(5필드) 반환 + wizard_data.branding.candidates 저장."""
    cands = [
        {
            "topic": f"주제{i}",
            "tone": f"톤{i}",
            "target": f"타깃{i}",
            "format": f"포맷{i}",
            "why_fit": f"이유{i}",
        }
        for i in range(3)
    ]

    def fake_finalize(state, *, client=None, model=None):
        return {"candidates": cands}

    _patch_finalize(monkeypatch, fake_finalize)
    plan_id = _new_plan_id()
    r = client.post(f"/api/v1/plans/{plan_id}/branding/finalize")
    assert r.status_code == 200
    data = r.json()
    assert len(data["candidates"]) == 3
    for c in data["candidates"]:
        assert set(c.keys()) == {"topic", "tone", "target", "format", "why_fit"}
    # 상태 저장 확인 (in-memory _plan_store).
    stored = plans_router._plan_store[plan_id]["wizard_data"]["branding"]["candidates"]
    assert len(stored) == 3


def test_branding_finalize_unknown_plan_404(monkeypatch) -> None:
    """미발견 plan_id → 404 INV-006."""
    def fake_finalize(state, *, client=None, model=None):  # pragma: no cover
        raise AssertionError("agent should not be called for unknown plan")

    _patch_finalize(monkeypatch, fake_finalize)
    r = client.post("/api/v1/plans/not-a-real-id/branding/finalize")
    assert r.status_code == 404
    assert r.json()["error"]["code"] == "INV-006"


def test_branding_finalize_graceful_on_agent_error(monkeypatch) -> None:
    """finalize agent 예외 → 500 아님, 빈 candidates."""
    def fake_finalize(state, *, client=None, model=None):
        raise ValueError("LLM 파싱 실패")

    _patch_finalize(monkeypatch, fake_finalize)
    plan_id = _new_plan_id()
    r = client.post(f"/api/v1/plans/{plan_id}/branding/finalize")
    assert r.status_code == 200
    assert r.json()["candidates"] == []


# ─── 통합 흐름 + OpenAPI 노출 ─────────────────────────────────────────


def test_branding_next_then_finalize_flow(monkeypatch) -> None:
    """ask 1회 → answer → finalize 까지 누적 history 가 finalize state 로 전달됨."""
    def fake_ask(state, *, client=None, model=None):
        return {"mode": "ask", "question": "Q1", "options": ["a", "b"], "rationale": ""}

    seen = {}

    def fake_finalize(state, *, client=None, model=None):
        seen["history"] = state["history"]
        return {
            "candidates": [
                {"topic": "t", "tone": "x", "target": "y", "format": "z", "why_fit": "w"}
            ]
        }

    _patch_ask(monkeypatch, fake_ask)
    _patch_finalize(monkeypatch, fake_finalize)
    plan_id = _new_plan_id()
    client.post(f"/api/v1/plans/{plan_id}/branding/next", json={})
    client.post(f"/api/v1/plans/{plan_id}/branding/next", json={"answer": "a"})
    r = client.post(f"/api/v1/plans/{plan_id}/branding/finalize")
    assert r.status_code == 200
    # finalize 가 받은 history 에 답변이 누적되어 있어야 한다.
    assert seen["history"][0]["answer"] == "a"


def test_branding_endpoints_in_openapi() -> None:
    """Phase 18 branding endpoint 가 OpenAPI 문서에 노출."""
    r = client.get("/openapi.json")
    assert r.status_code == 200
    paths = r.json().get("paths", {})
    assert "/api/v1/plans/{plan_id}/branding/next" in paths
    assert "/api/v1/plans/{plan_id}/branding/finalize" in paths
