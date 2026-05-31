"""Phase 10 Slice 1 — MVP end-to-end 통합 테스트 (behavior-preserving, mock-deterministic).

★ 본 파일은 **신규 추가 only**. 기존 endpoint / agent / orchestrator / repo / test 코드는
  0 수정. 기존 339 test 가 개별 검증한 piece 들을 **하나의 사용자 여정으로 chaining** 하여
  연결성(piece 간 데이터 전달) + Envelope/응답 schema 정합 + graceful 을 관찰한다.

검증하는 MVP 전체 흐름 (CLAUDE.md "핵심 흐름" 정합):
  입력 → 의도 분석 → 3안 생성(Critic verdict canonical 0~1 + revise) → 결과 조회
       → 선택(option index) → 피드백(reason PII 마스킹) → SSE progress 단계

두 경로:
  - Quick mode 경로  : plans/start(quick.initial) → wizard(quick.*) → generate(3-plan)
                        → GET → select → feedback → SSE progress
  - Discovery mode 경로: plans/start(step1) → wizard(step1..) → 동일 체인 (분기 차이 관찰)

★ 기존 흐름 관찰만 — 새 코드 경로 추가 X.
  외부 의존(LLM/RAG/Supabase)은 기존 conftest fixture (routers.plans namespace mock) 재사용.
  select/feedback in-memory store 는 test_plans_feedback_api 패턴대로 _reset_for_test 로 격리.

참조 (변경 금지):
  - tests/conftest.py (mock_plans_pipeline_ok / mock_intent_block_plans / _RAG_SEEDS)
  - tests/test_e2e_slice1.py (Quick `/api/v1/generate` 단일 plan 흐름)
  - tests/test_moa_orchestrator.py (generate_plan 3-plan + ProgressSink 순서)
  - tests/test_plans_feedback_api.py (select/feedback API + PII 마스킹)
  - tests/test_sse_integration.py (progress_store 실 stage stream)
  - routers/{generate,plans,sse}.py (실제 endpoint 시그니처/응답)
"""

from __future__ import annotations

import json

import pytest
from fastapi.testclient import TestClient

from backend.fastapi.main import app
from backend.fastapi.orchestration import progress_store
from backend.fastapi.orchestration.progress_sink import StoreProgressSink
from backend.fastapi.routers import plans as plans_router

client = TestClient(app)


# ─── fixtures (격리) ───────────────────────────────────────────────────


@pytest.fixture(autouse=True)
def _reset_stores() -> None:
    """각 통합 시나리오 전 select / feedback in-memory store + progress_store 초기화.

    test_plans_feedback_api.py / test_sse_integration.py 의 격리 패턴 재사용.
    기존 store 자체는 수정하지 않고 _reset_for_test (기존 public test helper) 만 호출.
    """
    plans_router._selection_repo._reset_for_test()
    plans_router._feedback_repo._reset_for_test()
    progress_store._reset_for_test()
    yield
    plans_router._selection_repo._reset_for_test()
    plans_router._feedback_repo._reset_for_test()
    progress_store._reset_for_test()


def _start_plan(initial_input: str = "유튜브 쇼츠 기획해줘") -> str:
    """plans/start 로 신규 plan_id 발급 (체인 시작점)."""
    r = client.post("/api/v1/plans/start", json={"user_input": initial_input})
    assert r.status_code == 201, r.text
    return r.json()["plan_id"]


# ─── 1. Quick mode 전체 체인 ──────────────────────────────────────────


def test_quick_mode_full_chain(mock_plans_pipeline_ok) -> None:
    """Quick mode end-to-end: start → wizard(quick.*) → generate(3-plan)
    → GET(envelope) → select(option) → feedback → 각 단계 산출이 다음 입력으로 전달.

    이 케이스가 MVP 핵심 흐름 전체를 하나로 연결한다 (연결성 backbone).
    """
    # (1) 입력 → plan_id 발급
    plan_id = _start_plan("30대 직장인 대상 재테크 쇼츠 기획해줘")

    # (2) Quick wizard 진행 — next_step hint 가 quick.* 체인으로 이어지는지
    r_w1 = client.post(
        f"/api/v1/plans/{plan_id}/wizard/quick.initial",
        json={"user_input": "재테크 입문"},
    )
    assert r_w1.status_code == 200
    assert r_w1.json()["next_step"] == "quick.clarify"

    r_w2 = client.post(
        f"/api/v1/plans/{plan_id}/wizard/quick.clarify",
        json={"user_input": "타겟은 30대 직장인"},
    )
    assert r_w2.json()["next_step"] == "quick.direction"

    r_w3 = client.post(
        f"/api/v1/plans/{plan_id}/wizard/quick.direction",
        json={"user_input": "한 줄 방향 승인"},
    )
    # 한 줄 방향 승인 다음은 generate (CLAUDE.md "한 줄 기획 방향 승인" → 생성)
    assert r_w3.json()["next_step"] == "generate"

    # (3) 3안 생성 — Intent → RAG → 3-plan parallel → Critic → DB save → Envelope
    r_gen = client.post(f"/api/v1/plans/{plan_id}/generate", json={})
    assert r_gen.status_code == 200, r_gen.text
    env = r_gen.json()

    # Envelope 3섹션 정합
    assert set(["meta", "body", "validation"]).issubset(env.keys())
    plan_candidates = env["body"]["plan_candidates"]
    assert len(plan_candidates) == 3, "Phase 4+ MOA: 3안 생성"

    # Critic verdict canonical 0~1 (Phase 9.5 ADR-034) — deprecated 0–5 제거 관찰
    critic = env["body"]["critic_evaluation"]
    assert critic is not None
    assert "scores" not in critic and "overall_score_avg" not in critic
    assert 0.0 <= critic["overall_score"] <= 1.0
    for v in critic["dimensions"].values():
        assert 0.0 <= v <= 1.0
    assert critic["overall_verdict"] in ("approve", "revise", "reject")
    # revise_round 필드 존재 (revise 흐름 연결 — approve 케이스는 0)
    assert critic["revise_round"] == 0

    # DB save 산출이 meta.project_id 로 전달 (save_video_planning → Meta)
    assert env["meta"]["project_id"] == "fake-project-uuid"

    # (4) GET 으로 generated envelope 가 그대로 조회되는지 (생성 산출 → 저장 → 조회 연결)
    r_get = client.get(f"/api/v1/plans/{plan_id}")
    assert r_get.status_code == 200
    resource = r_get.json()
    assert resource["status"] == "generated"
    assert resource["envelope"] is not None
    got_candidates = resource["envelope"]["body"]["plan_candidates"]
    assert len(got_candidates) == 3
    # generate 응답의 plan_id 가 GET envelope 에 그대로 보존 (연결성)
    assert got_candidates[0]["plan_id"] == plan_candidates[0]["plan_id"]

    # (5) 선택 — option_index 가 plan_candidates 배열 인덱스로 전달
    chosen_idx = 1
    r_sel = client.post(
        f"/api/v1/plans/{plan_id}/select",
        json={"selected_option_index": chosen_idx, "selection_reason": "톤이 맞아요"},
    )
    assert r_sel.status_code == 200
    sel = r_sel.json()
    assert sel["plan_id"] == plan_id
    assert sel["selected_option_index"] == chosen_idx
    assert sel["selected_at"]

    # select 후 status 가 "selected" 로 전이 (상태 머신 연결)
    r_get2 = client.get(f"/api/v1/plans/{plan_id}")
    assert r_get2.json()["status"] == "selected"

    # (6) 피드백 — 선택한 option 에 대한 like 기록 → list 로 round-trip
    r_fb = client.post(
        f"/api/v1/plans/{plan_id}/feedback",
        json={"event_type": "like", "option_index": chosen_idx},
    )
    assert r_fb.status_code == 200
    assert r_fb.json()["event_type"] == "like"
    assert r_fb.json()["option_index"] == chosen_idx

    r_fb_list = client.get(f"/api/v1/plans/{plan_id}/feedback")
    assert r_fb_list.status_code == 200
    events = r_fb_list.json()["events"]
    assert len(events) == 1
    assert events[0]["event_type"] == "like"


# ─── 2. Discovery mode 전체 체인 ──────────────────────────────────────


def test_discovery_mode_full_chain(mock_plans_pipeline_ok) -> None:
    """Discovery mode end-to-end: start → wizard(step1..step7 분기) → generate
    → select → feedback. Quick 과 동일 백엔드 체인을 타되 wizard 분기만 다름 (분기 차이 관찰).
    """
    plan_id = _start_plan("영상 채널을 처음 시작하는데 뭘 만들지 모르겠어요")

    # Discovery 7-step 분기 — step1 → step2 next_step hint 확인 (Quick 분기와 차이)
    r_s1 = client.post(
        f"/api/v1/plans/{plan_id}/wizard/step1",
        json={"selected_card_id": "card-brand-intro"},
    )
    assert r_s1.status_code == 200
    assert r_s1.json()["next_step"] == "step2", "Discovery 분기: step1 다음은 step2 (Quick 와 차이)"
    assert r_s1.json()["step"] == "step1"

    # step7 (마지막) → generate hint
    r_s7 = client.post(
        f"/api/v1/plans/{plan_id}/wizard/step7",
        json={"user_input": "30대 직장인 대상, 친근한 톤"},
    )
    assert r_s7.json()["next_step"] == "generate"

    # 동일 generate 체인 (Discovery 도 동일 orchestrator 경유)
    r_gen = client.post(f"/api/v1/plans/{plan_id}/generate", json={})
    assert r_gen.status_code == 200
    env = r_gen.json()
    assert len(env["body"]["plan_candidates"]) == 3

    # select → feedback 체인 (Quick 과 동일하게 연결)
    r_sel = client.post(
        f"/api/v1/plans/{plan_id}/select",
        json={"selected_option_index": 0},
    )
    assert r_sel.status_code == 200

    r_fb = client.post(
        f"/api/v1/plans/{plan_id}/feedback",
        json={"event_type": "dislike", "option_index": 0, "reason": "조금 평범해요"},
    )
    assert r_fb.status_code == 200
    assert r_fb.json()["event_type"] == "dislike"


# ─── 3. revise 흐름 연결 (Critic verdict=revise → revise_history) ─────


def test_chain_critic_revise_verdict_flows_to_envelope(
    mock_intent_ok_plans,
    mock_rag_fallback_plans,
    mock_planning_parallel_3_ok,
    mock_db_save_ok_plans,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Critic 이 revise verdict → orchestrator revise loop 가 engage 되고 그 결과가
    Envelope(body.revise_history / validation.warnings) 로 전달되는지 연결 관찰.

    Critic 만 revise 로 교체 (다른 piece 는 기존 ok mock 재사용). Rewriter 는 기존
    routers.plans.run_rewriter 가 graceful 처리하므로 실 연결만 관찰.
    """
    from typing import Any

    def _critic_revise(plan: dict[str, Any], *a: Any, **k: Any) -> dict[str, Any]:
        # FC-001/002 시드 패턴 — 0–5 의 1점 → normalize 후 0.2 (< 0.4).
        scores = {
            "intent_fit": 3, "target_clarity": 1, "hook_strength": 1, "message_clarity": 3,
            "structure": 3, "feasibility": 3, "brand_consistency": 4, "differentiation": 2,
        }
        return {
            "target_plan_id": str(plan.get("plan_id") or ""),
            "scores": scores,
            "reasons": {key: "—" for key in scores},
            "suggestions": {key: "—" for key in scores},
            "overall_score_avg": round(sum(scores.values()) / len(scores), 4),
            "overall_verdict": "revise",
            "blocking_issues": ["타겟 좁히기", "hook 재작성"],
            "revise_round": 0,
        }

    monkeypatch.setattr("backend.fastapi.routers.plans.run_critic", _critic_revise)

    plan_id = _start_plan("건강 관련 쇼츠")
    r_gen = client.post(f"/api/v1/plans/{plan_id}/generate", json={})
    assert r_gen.status_code == 200, r_gen.text
    env = r_gen.json()

    critic = env["body"]["critic_evaluation"]
    assert critic["overall_verdict"] == "revise"
    assert len(critic["blocking_issues"]) >= 1
    # canonical 변환 후에도 약한 차원이 0.4 미만으로 전달됐는지 (verdict 연결성)
    assert critic["dimensions"]["hook_strength"] < 0.4
    assert critic["dimensions"]["target_clarity"] < 0.4

    # revise loop engage → revise_history 가 plan 별로 채워져 Envelope 로 전달
    revise_history = env["body"]["revise_history"]
    assert revise_history is not None
    assert len(revise_history) == 3  # plan 3개 각각 attempt log


# ─── 4. RAG references 가 plan.rag_used 로 전달 (연결성) ───────────────


def test_chain_rag_references_flow_to_plan(
    mock_intent_ok_plans,
    mock_rag_ok_plans,
    mock_planning_parallel_3_ok,
    mock_critic_ok_plans,
    mock_db_save_ok_plans,
) -> None:
    """RAG OK 경로일 때 retriever 산출(references)이 body.rag_references + plan.rag_used
    양쪽으로 전달되고 validation.checks.rag_retrieval status=ok 로 연결되는지 관찰.
    """
    plan_id = _start_plan("건강한 식단 쇼츠 기획")
    r_gen = client.post(f"/api/v1/plans/{plan_id}/generate", json={})
    assert r_gen.status_code == 200
    env = r_gen.json()

    # retriever 의 2개 seed 가 body.rag_references 로 전달
    refs = env["body"]["rag_references"]
    assert len(refs) == 2
    assert refs[0]["source_id"] == "seed-001"

    # 동일 references 가 각 plan.rag_used 로도 주입 (Planning 입력으로 전달된 흔적)
    for plan in env["body"]["plan_candidates"]:
        used = plan["rag_used"]
        assert len(used) == 2
        assert {u["source_id"] for u in used} == {"seed-001", "seed-002"}

    # validation.checks.rag_retrieval status=ok
    checks = {c["name"]: c for c in env["validation"]["checks"]}
    assert checks["rag_retrieval"]["status"] == "ok"


# ─── 5. SSE progress 단계 연결 (StoreProgressSink → progress_store → SSE) ──


def test_chain_sse_progress_stages(mock_plans_pipeline_ok) -> None:
    """generate 가 StoreProgressSink 로 기록한 stage 이벤트를 SSE endpoint 가 그대로 stream.

    실 generate 호출(TestClient) 이 progress_store 에 [intent, rag, planning, critic, complete]
    를 남기고, GET /progress 가 그 stage 들을 순서대로 반환하는지 (단계 연결성).
    """
    plan_id = _start_plan("쇼츠 콘텐츠 기획")

    r_gen = client.post(f"/api/v1/plans/{plan_id}/generate", json={})
    assert r_gen.status_code == 200

    # generate 동안 StoreProgressSink 가 실 stage 를 store 에 기록했어야 함
    snapshot = progress_store.read(plan_id)
    assert snapshot, "generate 후 progress_store 에 stage 이벤트가 기록돼야 함"
    recorded_stages = [e.get("stage") for e in snapshot if e.get("type") == "progress"]
    assert recorded_stages == ["intent", "rag", "planning", "critic"]
    assert snapshot[-1]["type"] == "complete"

    # SSE endpoint 가 그 store 를 read 하여 동일 stage 순서로 stream
    resp = client.get(f"/api/v1/plans/{plan_id}/progress")
    assert resp.status_code == 200
    events = [json.loads(l[5:]) for l in resp.text.split("\n\n") if l.startswith("data:")]
    sse_stages = [e.get("stage") for e in events if e.get("type") == "progress"]
    assert sse_stages == ["intent", "rag", "planning", "critic"]
    assert events[-1]["type"] == "complete"


# ─── 6. Quick `/api/v1/generate` (Phase 1 단일-plan 경로) 연결 ─────────


def test_chain_phase1_generate_single_plan(mock_pipeline_ok) -> None:
    """Phase 1 Quick endpoint `/api/v1/generate` 도 동일 MVP 핵심 흐름(Intent → RAG →
    Planning → Critic → DB save)을 단일-plan 으로 연결한다 (legacy quick 경로 회귀 관찰).

    Phase 4 plans 경로(3-plan)와 공존 — 두 경로 모두 동일 Envelope schema 로 수렴하는지 관찰.
    """
    r = client.post("/api/v1/generate", json={"input": "유튜브 채널 첫 영상 기획해줘"})
    assert r.status_code == 200
    env = r.json()

    assert set(["meta", "body", "validation"]).issubset(env.keys())
    # Phase 1 deviation: 단일 plan
    assert len(env["body"]["plan_candidates"]) == 1
    # 동일 canonical Critic schema 로 수렴
    critic = env["body"]["critic_evaluation"]
    assert 0.0 <= critic["overall_score"] <= 1.0
    assert critic["overall_verdict"] in ("approve", "revise", "reject")
    # DB save 산출 연결
    assert env["meta"]["project_id"] == "fake-project-uuid"


# ─── 7. graceful — DB 실패해도 전체 체인이 끊기지 않음 ────────────────


def test_chain_db_failure_does_not_break_chain(
    mock_intent_ok_plans,
    mock_rag_fallback_plans,
    mock_planning_parallel_3_ok,
    mock_critic_ok_plans,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """DB save 실패(failed_db_error) 시도 generate 200 + project_id=null + 이후 select/feedback
    체인이 정상 동작하는지 (graceful — DB 실패가 사용자 여정을 차단하지 않음).
    """
    from typing import Any

    from backend.fastapi.db.types import PersistenceResult

    def _save_fail(**kwargs: Any) -> PersistenceResult:
        return PersistenceResult(
            status="failed_db_error", project_id=None,
            plan_candidate_ids=[], error_reason="connection_refused",
        )

    monkeypatch.setattr("backend.fastapi.routers.plans.save_video_planning", _save_fail)

    plan_id = _start_plan("유튜브 채널 첫 영상")
    r_gen = client.post(f"/api/v1/plans/{plan_id}/generate", json={})
    assert r_gen.status_code == 200, "DB 실패여도 사용자 응답은 200 유지 (graceful)"
    env = r_gen.json()
    assert env["meta"]["project_id"] is None
    checks = {c["name"]: c for c in env["validation"]["checks"]}
    assert checks["db_persistence"]["status"] == "warn"

    # DB 실패 후에도 select/feedback (in-memory graceful) 가 정상 연결
    r_sel = client.post(
        f"/api/v1/plans/{plan_id}/select", json={"selected_option_index": 0},
    )
    assert r_sel.status_code == 200
    r_fb = client.post(
        f"/api/v1/plans/{plan_id}/feedback", json={"event_type": "regenerate"},
    )
    assert r_fb.status_code == 200


# ─── 8. graceful — Intent 차단 시 체인 진입 자체가 막힘 (422) ──────────


def test_chain_intent_block_halts_chain(mock_intent_block_plans) -> None:
    """영상기획 외 요청 → generate 단계에서 INV-001 / 422 로 체인이 안전 차단되고
    이후 단계(plan_candidates) 산출이 없는지 관찰 (Intent gate 연결).
    """
    plan_id = _start_plan("오늘 서울 날씨 알려줘")
    r_gen = client.post(f"/api/v1/plans/{plan_id}/generate", json={})

    assert r_gen.status_code == 422
    body = r_gen.json()
    assert body["ok"] is False
    assert body["error"]["code"] == "INV-001"
    assert body["error"]["retry_allowed"] is False

    # 차단됐으므로 GET 시 envelope 미생성 (status 가 generated 로 전이되지 않음)
    r_get = client.get(f"/api/v1/plans/{plan_id}")
    assert r_get.status_code == 200
    assert r_get.json()["status"] != "generated"
    assert r_get.json()["envelope"] is None


# ─── 9. graceful — 미발견 plan_id 는 각 단계에서 404 INV-006 ──────────


def test_chain_unknown_plan_id_404_at_each_step() -> None:
    """체인 중간 단계들이 미발견 plan_id 에 대해 일관되게 404 INV-006 을 반환하는지
    (연결 전제: 잘못된 plan_id 로는 다음 단계로 진행 불가).
    """
    ghost = "not-a-real-plan-id"

    r_gen = client.post(f"/api/v1/plans/{ghost}/generate", json={})
    assert r_gen.status_code == 404
    assert r_gen.json()["error"]["code"] == "INV-006"

    r_sel = client.post(f"/api/v1/plans/{ghost}/select", json={"selected_option_index": 0})
    assert r_sel.status_code == 404

    r_fb = client.post(f"/api/v1/plans/{ghost}/feedback", json={"event_type": "like"})
    assert r_fb.status_code == 404

    r_get = client.get(f"/api/v1/plans/{ghost}")
    assert r_get.status_code == 404


# ─── 10. feedback reason PII 마스킹이 체인 끝에서 보존 ────────────────


def test_chain_feedback_reason_pii_masked(mock_plans_pipeline_ok) -> None:
    """체인 마지막 feedback 단계에서 자유 입력 reason 의 PII(이메일/전화)가 저장 전
    마스킹되어 GET 으로 [masked] 만 노출되는지 (security-review T1 연결 관찰).
    """
    plan_id = _start_plan("유튜브 채널 첫 영상")
    client.post(f"/api/v1/plans/{plan_id}/generate", json={})
    client.post(f"/api/v1/plans/{plan_id}/select", json={"selected_option_index": 0})

    client.post(
        f"/api/v1/plans/{plan_id}/feedback",
        json={
            "event_type": "reject",
            "reason": "연락처 010-1234-5678 또는 me@example.com 으로 주세요",
        },
    )
    r_list = client.get(f"/api/v1/plans/{plan_id}/feedback")
    assert r_list.status_code == 200
    events = r_list.json()["events"]
    assert len(events) == 1
    reason = events[0]["reason"]
    assert "010-1234-5678" not in reason
    assert "me@example.com" not in reason
    assert "[masked]" in reason


# ─── 11. 선택한 option_index 경계값(0/1/2) 전 구간 연결 ────────────────


def test_chain_select_option_index_boundaries(mock_plans_pipeline_ok) -> None:
    """3-plan 생성 후 0/1/2 각 option 을 선택하는 전체 체인이 정상 연결되는지
    (selected_option_index 가 plan_candidates 인덱스 범위와 정합).
    """
    for idx in (0, 1, 2):
        plan_id = _start_plan(f"쇼츠 기획 옵션 {idx}")
        r_gen = client.post(f"/api/v1/plans/{plan_id}/generate", json={})
        assert r_gen.status_code == 200
        assert len(r_gen.json()["body"]["plan_candidates"]) == 3

        r_sel = client.post(
            f"/api/v1/plans/{plan_id}/select",
            json={"selected_option_index": idx},
        )
        assert r_sel.status_code == 200
        assert r_sel.json()["selected_option_index"] == idx


# ─── 12. validation.checks 7개 순서가 체인 산출에 보존 ────────────────


def test_chain_validation_checks_order_preserved(mock_plans_pipeline_ok) -> None:
    """3-plan generate 결과 Envelope 의 validation.checks 7개 순서가 보존되는지
    (orchestrator 조립 산출 → HTTP 응답까지 byte-level 정합 관찰).
    """
    plan_id = _start_plan("쇼츠 콘텐츠 기획")
    r_gen = client.post(f"/api/v1/plans/{plan_id}/generate", json={})
    assert r_gen.status_code == 200
    checks = [c["name"] for c in r_gen.json()["validation"]["checks"]]
    assert checks == [
        "schema_envelope", "intent_filter", "rag_retrieval", "plan_count",
        "critic_evaluation", "db_persistence", "multi_model",
    ]
