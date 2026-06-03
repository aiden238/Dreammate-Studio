"""Phase 17 가-S1 — 신원(auth_user_id) plumbing 라우터 패스스루 테스트.

auth_middleware 가 request.state.user 에 주입한 신원이 라우터를 거쳐
orchestration.generate_plan() 의 auth_user_id 인자로 전달되는지 검증한다.

검증 축:
  - 인증(dev_auth_mock + mock-token cookie) → auth_user_id="mock-user-1" 패스스루.
  - 익명(토큰 없음) → auth_user_id=None (기존 경로 byte-identical, 회귀 0).
  - Phase 1 sync /generate 도 신원 관측(로깅) 후 200 동작 불변.

★ 본 슬라이스는 plumbing only — generate_plan 을 mock 하여 kwarg 만 확인한다
(brand_memory 로드/주입은 가-S2).

신원 source 는 cookie/JWT(auth_middleware) — request body/schema 불변(contract 무변경).
"""

from __future__ import annotations

import logging
from typing import Any

import pytest
from fastapi.testclient import TestClient

from backend.fastapi import config as _config_module
from backend.fastapi.db import client as _db_client_module
from backend.fastapi.main import app
from backend.fastapi.schemas.output import (
    Body,
    Envelope,
    Meta,
    Plan,
    PlanFlowBeat,
    Validation,
    ValidationCheck,
)


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def _set_dev_auth_mock(monkeypatch: pytest.MonkeyPatch, enabled: bool) -> None:
    """settings.dev_auth_mock 토글 + lru_cache 무효화 (test_auth 패턴 동일)."""
    _config_module.get_settings.cache_clear()
    settings = _config_module.get_settings()
    monkeypatch.setattr(settings, "dev_auth_mock", enabled, raising=False)


def _force_no_supabase(monkeypatch: pytest.MonkeyPatch) -> None:
    """get_supabase() -> None 강제 (middleware 가 mock-token 분기 타도록)."""
    monkeypatch.setattr(_db_client_module, "get_supabase", lambda: None)
    monkeypatch.setattr("backend.fastapi.routers.auth.get_supabase", lambda: None)


def _minimal_envelope() -> Envelope:
    """generate_plan mock 이 반환할 최소 Envelope (라우터 200 경로 통과용)."""
    return Envelope(
        meta=Meta.make(
            prompt_id="P-006",
            prompt_version="1.0.0",
            model="gpt-4o-mini",
            locale="ko-KR",
            request_id="req-test",
            project_id=None,
        ),
        body=Body(
            plan_candidates=[
                Plan(
                    plan_id="p-test",
                    option_index=0,
                    name="기획안",
                    concept="콘셉트",
                    hook="후크 — 최소 10자 이상 확보용 문장",
                    flow=[
                        PlanFlowBeat(beat_index=0, beat="도입", duration_sec=3, purpose="관심"),
                        PlanFlowBeat(beat_index=1, beat="마무리", duration_sec=5, purpose="CTA"),
                    ],
                )
            ],
            critic_evaluation=None,
            rag_references=[],
        ),
        validation=Validation(
            passed=True,
            checks=[ValidationCheck(name="schema_envelope", status="ok")],
            warnings=[],
        ),
    )


# ─── 1. 인증 → auth_user_id 패스스루 ──────────────────────────────────


def test_plans_generate_passes_auth_user_id(
    client: TestClient, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """dev_auth_mock + mock-token cookie → generate_plan(auth_user_id="mock-user-1")."""
    _set_dev_auth_mock(monkeypatch, True)
    _force_no_supabase(monkeypatch)

    captured: dict[str, Any] = {}

    async def fake_generate_plan(plan_id, plan_entry, req, **kwargs):
        captured["auth_user_id"] = kwargs.get("auth_user_id")
        captured["kwargs"] = kwargs
        # 라우터가 stored envelope(plan_entry["envelope"])를 200 으로 반환하므로 채워둠.
        plan_entry["envelope"] = {"ok": True, "data": {"mock": True}}
        return _minimal_envelope()

    monkeypatch.setattr(
        "backend.fastapi.routers.plans.generate_plan", fake_generate_plan,
    )

    start = client.post("/api/v1/plans/start", json={"user_input": "유튜브 쇼츠"}).json()
    plan_id = start["plan_id"]

    # 인증 쿠키는 client 인스턴스에 설정 (per-request cookies 는 deprecated).
    client.cookies.set("sb_access_token", "mock-token")
    r = client.post(f"/api/v1/plans/{plan_id}/generate", json={})
    assert r.status_code == 200
    # ★ 신원이 라우터 → generate_plan kwarg 로 전달됨.
    assert captured["auth_user_id"] == "mock-user-1"


# ─── 2. 익명 → auth_user_id=None (byte-identical) ─────────────────────


def test_plans_generate_anonymous_passes_none(
    client: TestClient, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """토큰 없음(익명) → generate_plan(auth_user_id=None) — 기존 경로 그대로."""
    _set_dev_auth_mock(monkeypatch, True)
    _force_no_supabase(monkeypatch)

    captured: dict[str, Any] = {}

    async def fake_generate_plan(plan_id, plan_entry, req, **kwargs):
        captured["auth_user_id"] = kwargs.get("auth_user_id")
        plan_entry["envelope"] = {"ok": True, "data": {"mock": True}}
        return _minimal_envelope()

    monkeypatch.setattr(
        "backend.fastapi.routers.plans.generate_plan", fake_generate_plan,
    )

    start = client.post("/api/v1/plans/start", json={"user_input": "유튜브 쇼츠"}).json()
    plan_id = start["plan_id"]

    r = client.post(f"/api/v1/plans/{plan_id}/generate", json={})  # 쿠키 없음
    assert r.status_code == 200
    # ★ 익명 — None 전달 (anon byte-identical).
    assert captured["auth_user_id"] is None


# ─── 3. Phase 1 sync /generate 신원 관측 (동작 불변) ──────────────────


def test_sync_generate_observes_identity_and_unchanged(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Phase 1 /generate: 인증 시 신원 로깅 관측 + 200 동작 불변 (주입 0).

    generate.py 는 orchestrator 비경유 — 신원은 로깅만, Envelope/출력 무영향.
    """
    _set_dev_auth_mock(monkeypatch, True)
    _force_no_supabase(monkeypatch)

    # 파이프라인 mock (generate.py namespace) — LLM 실호출 없이 200.
    monkeypatch.setattr(
        "backend.fastapi.routers.generate.run_intent",
        lambda *a, **k: {"intent_ok": True, "category": "video_planning"},
    )
    from backend.fastapi.rag.types import RetrievalResult

    monkeypatch.setattr(
        "backend.fastapi.routers.generate.run_rag_retrieval",
        lambda *a, **k: RetrievalResult(references=[], used_fallback=True, fallback_reason=None),
    )
    monkeypatch.setattr(
        "backend.fastapi.routers.generate.run_planning",
        lambda *a, **k: {
            "plan": {
                "name": "기획안",
                "concept": "콘셉트",
                "hook": "후크 — 최소 10자 이상 확보용 문장",
                "flow": [
                    {"beat_index": 0, "beat": "도입", "duration_sec": 3, "purpose": "관심"},
                    {"beat_index": 1, "beat": "마무리", "duration_sec": 5, "purpose": "CTA"},
                ],
                "pros": "장점",
                "risks": "위험",
                "approach_label": "informational",
            }
        },
    )
    monkeypatch.setattr(
        "backend.fastapi.routers.generate.run_critic",
        lambda plan, *a, **k: {
            "target_plan_id": str(plan.get("plan_id") or ""),
            "scores": {
                "intent_fit": 4, "target_clarity": 4, "hook_strength": 4,
                "message_clarity": 4, "structure": 4, "feasibility": 4,
                "brand_consistency": 4, "differentiation": 4,
            },
            "reasons": {}, "suggestions": {},
            "overall_score_avg": 4.0, "overall_verdict": "approve",
            "blocking_issues": [], "revise_round": 0,
        },
    )
    from backend.fastapi.db.types import PersistenceResult

    monkeypatch.setattr(
        "backend.fastapi.routers.generate.save_video_planning",
        lambda **k: PersistenceResult(
            status="saved", project_id=None, plan_candidate_ids=[], error_reason=None,
        ),
    )

    client.cookies.set("sb_access_token", "mock-token")
    with caplog.at_level(logging.INFO, logger="backend.fastapi.routers.generate"):
        r = client.post(
            "/api/v1/generate",
            json={"input": "유튜브 쇼츠 만들기"},
        )
    assert r.status_code == 200
    # ★ 신원이 sync endpoint 에서 관측(로깅)됨 — anon 아님.
    assert "auth_user_id=mock-user-1" in caplog.text
