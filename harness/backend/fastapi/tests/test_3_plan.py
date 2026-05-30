"""Phase 4 Slice 2 — 3-plan parallel generation + multi-model interface tests.

acceptance.md A2 + A3 + A4 매핑:
  - A2: plans length 3 + approach_label unique + multi-model 인터페이스
  - A3: Critic verdict 노출 (revise loop 없음 — Phase 4.5+ deferred)
  - A4: Phase 1 endpoint 회귀 0 (1-plan + X-API-Deprecation header 유지)

핵심 검증:
  1. 3-plan length === 3
  2. approach_label set === 3 (모두 unique)
  3. validation.warnings에서 phase_1_single_plan 동적 제거
  4. validation.warnings에 phase_4_no_revise_loop 추가
  5. Phase 1 endpoint 여전히 1-plan 반환 (회귀 0)
  6. multi-model validation.check 노출
  7. parallel error graceful — 1개 실패 시 fallback dict (length 3 보장)
  8. Critic evaluation 8 scores 정상 노출
"""

from __future__ import annotations

from typing import Any

import pytest
from fastapi.testclient import TestClient

from backend.fastapi.main import app

client = TestClient(app)


# ─── 1. 3-plan length === 3 ───────────────────────────────────────────

def test_3_plan_length_is_3(mock_plans_pipeline_ok) -> None:
    """Phase 4 endpoint → body.plan_candidates length 3."""
    start = client.post(
        "/api/v1/plans/start", json={"user_input": "유튜브 쇼츠 만들기"}
    ).json()
    plan_id = start["plan_id"]

    r = client.post(f"/api/v1/plans/{plan_id}/generate", json={})
    assert r.status_code == 200, r.text
    data = r.json()
    assert "body" in data
    assert "plan_candidates" in data["body"]
    assert len(data["body"]["plan_candidates"]) == 3


# ─── 2. approach_label unique ─────────────────────────────────────────

def test_approach_label_unique(mock_plans_pipeline_ok) -> None:
    """3개 plan의 approach_label set === 3 (모두 unique)."""
    start = client.post(
        "/api/v1/plans/start", json={"user_input": "테스트"}
    ).json()
    plan_id = start["plan_id"]
    r = client.post(f"/api/v1/plans/{plan_id}/generate", json={})
    assert r.status_code == 200
    labels = [p["approach_label"] for p in r.json()["body"]["plan_candidates"]]
    assert len(set(labels)) == 3, f"approach_label not unique: {labels}"


# ─── 3. validation.warnings: phase_1_single_plan 제거 ─────────────────

def test_warnings_phase_1_single_plan_removed(mock_plans_pipeline_ok) -> None:
    """plans length 3일 때 validation.warnings에서 phase_1_single_plan 제거."""
    start = client.post(
        "/api/v1/plans/start", json={"user_input": "테스트"}
    ).json()
    plan_id = start["plan_id"]
    r = client.post(f"/api/v1/plans/{plan_id}/generate", json={})
    assert r.status_code == 200
    warnings = r.json()["validation"]["warnings"]
    assert "phase_1_single_plan" not in warnings


# ─── 4. validation.warnings: phase_4_no_revise_loop (Phase 4.5 Slice 2 갱신) ────

def test_warnings_phase_4_no_revise_loop_present(mock_plans_pipeline_ok) -> None:
    """Phase 4.5 Slice 2 갱신: critic approve 일 때도 revise loop 자체는 동작했으므로
    `phase_4_no_revise_loop` warning 은 제거된다.

    이전 (Phase 4 baseline): revise loop 미동작 → phase_4_no_revise_loop 포함.
    현재 (Phase 4.5 Slice 2): plan 별 critic+revise loop 실행 (approve 면 attempt 0 만)
    → revise_history 가 채워지고 warning 제거.
    """
    start = client.post(
        "/api/v1/plans/start", json={"user_input": "테스트"}
    ).json()
    plan_id = start["plan_id"]
    r = client.post(f"/api/v1/plans/{plan_id}/generate", json={})
    warnings = r.json()["validation"]["warnings"]
    assert "phase_4_no_revise_loop" not in warnings
    # Phase 4.5 Slice 2: revise_history 가 body 에 노출됨.
    assert r.json()["body"]["revise_history"] is not None


# ─── 5. Phase 1 endpoint 회귀 0 — 여전히 1-plan ───────────────────────

def test_phase_1_endpoint_still_1_plan(mock_pipeline_ok) -> None:
    """Phase 1 endpoint /api/v1/generate 여전히 1-plan 반환 (회귀 0)."""
    r = client.post("/api/v1/generate", json={"input": "유튜브 쇼츠"})
    assert r.status_code == 200
    data = r.json()
    assert len(data["body"]["plan_candidates"]) == 1
    # Phase 1 endpoint는 여전히 phase_1_single_plan warning 유지.
    assert "phase_1_single_plan" in data["validation"]["warnings"]


# ─── 6. Critic evaluation 8 scores 노출 ───────────────────────────────

def test_critic_evaluation_present(mock_plans_pipeline_ok) -> None:
    """body.critic_evaluation 노출 + canonical 8 차원 + verdict 정상.

    Phase 9.5 ADR-034: deprecated 0–5 scores 제거 → canonical dimensions(0–1) 검증.
    """
    start = client.post(
        "/api/v1/plans/start", json={"user_input": "테스트"}
    ).json()
    plan_id = start["plan_id"]
    r = client.post(f"/api/v1/plans/{plan_id}/generate", json={})
    body = r.json()["body"]
    assert body["critic_evaluation"] is not None
    critic = body["critic_evaluation"]
    # Phase 9.5 ADR-034: deprecated 0–5 필드 제거 → canonical dimensions 노출
    assert "scores" not in critic
    assert "dimensions" in critic
    # 8 차원 모두 존재
    expected_dims = {
        "intent_fit", "target_clarity", "hook_strength", "message_clarity",
        "structure", "feasibility", "brand_consistency", "differentiation",
    }
    assert set(critic["dimensions"].keys()) == expected_dims
    # verdict 노출 (Phase 4: revise loop 없음 → revise_round=0)
    assert critic["overall_verdict"] in {"approve", "revise", "reject"}
    assert critic["revise_round"] == 0


# ─── 7. multi-model validation.check 노출 ─────────────────────────────

def test_multi_model_validation_check(mock_plans_pipeline_ok) -> None:
    """multi-model 인터페이스가 validation.checks에 노출 (ADR-015 정합)."""
    start = client.post(
        "/api/v1/plans/start", json={"user_input": "테스트"}
    ).json()
    plan_id = start["plan_id"]
    r = client.post(f"/api/v1/plans/{plan_id}/generate", json={})
    checks = r.json()["validation"]["checks"]
    multi = next((c for c in checks if c["name"] == "multi_model"), None)
    assert multi is not None, "multi_model check 누락"
    assert multi["status"] == "ok"
    assert "models=" in (multi["detail"] or "")


# ─── 8. parallel error graceful — 1개 실패 시 fallback ────────────────

def test_parallel_partial_failure_graceful(
    mock_intent_ok_plans,
    mock_rag_fallback_plans,
    mock_critic_ok_plans,
    mock_db_save_ok_plans,
    monkeypatch,
) -> None:
    """1개 plan 실패 시 retry 후 fallback dict — length 3 보장.

    Phase 4 Slice 2 graceful 정책 (사용자 응답 차단 금지).
    """

    async def flaky_parallel(*args: Any, **kwargs: Any) -> list[dict[str, Any]]:
        # 2번째 plan은 fallback dict 형태 (router 단에서 schema fallback 적용).
        return [
            {
                "plan": {
                    "name": "P1",
                    "concept": "c1",
                    "hook": "후크 1번 — 시청 유지율 검증 hook",
                    "flow": [
                        {"beat_index": 0, "beat": "x", "duration_sec": 5, "purpose": "p"},
                        {"beat_index": 1, "beat": "y", "duration_sec": 10, "purpose": "q"},
                    ],
                    "pros": "",
                    "risks": "",
                    "approach_label": "narrative",
                }
            },
            {
                "plan": {
                    "name": "(생성 실패 2)",
                    "concept": "(LLM 응답 실패 — graceful fallback)",
                    "hook": "재시도 권장 — 잠시 후 다시 시도해주세요",
                    "flow": [
                        {"beat_index": 0, "beat": "—", "duration_sec": 1, "purpose": "—"},
                        {"beat_index": 1, "beat": "—", "duration_sec": 1, "purpose": "—"},
                    ],
                    "pros": "",
                    "risks": "graceful fallback (Phase 4 Slice 2)",
                    "approach_label": "other",
                }
            },
            {
                "plan": {
                    "name": "P3",
                    "concept": "c3",
                    "hook": "후크 3번 — 실험적 비교 hook",
                    "flow": [
                        {"beat_index": 0, "beat": "x", "duration_sec": 5, "purpose": "p"},
                        {"beat_index": 1, "beat": "y", "duration_sec": 10, "purpose": "q"},
                    ],
                    "pros": "",
                    "risks": "",
                    "approach_label": "experiment",
                }
            },
        ]

    monkeypatch.setattr(
        "backend.fastapi.routers.plans.run_planning_parallel_3", flaky_parallel,
    )

    start = client.post(
        "/api/v1/plans/start", json={"user_input": "테스트"}
    ).json()
    plan_id = start["plan_id"]
    r = client.post(f"/api/v1/plans/{plan_id}/generate", json={})
    assert r.status_code == 200
    data = r.json()
    # graceful — 3개 모두 보장 (fallback dict 포함)
    assert len(data["body"]["plan_candidates"]) == 3


# ─── 9. GET /plans/{plan_id} 에서 envelope 조회 가능 ──────────────────

def test_plans_get_returns_envelope_after_generate(mock_plans_pipeline_ok) -> None:
    """generate 후 GET /plans/{plan_id} → envelope 필드 채워짐 (3-plan)."""
    start = client.post(
        "/api/v1/plans/start", json={"user_input": "테스트"}
    ).json()
    plan_id = start["plan_id"]
    client.post(f"/api/v1/plans/{plan_id}/generate", json={})

    r = client.get(f"/api/v1/plans/{plan_id}")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "generated"
    envelope = data["envelope"]
    assert envelope is not None
    assert len(envelope["body"]["plan_candidates"]) == 3


# ─── 10. Intent 차단 → 422 INV-001 ─────────────────────────────────────

def test_plans_generate_intent_block_returns_422(
    mock_intent_block_plans,
    mock_rag_fallback_plans,
    mock_critic_ok_plans,
    mock_db_save_ok_plans,
) -> None:
    """Intent 차단 시 422 + INV-001 (Phase 1 endpoint와 동일 정책)."""
    start = client.post(
        "/api/v1/plans/start", json={"user_input": "오늘 서울 날씨 알려줘"}
    ).json()
    plan_id = start["plan_id"]
    r = client.post(f"/api/v1/plans/{plan_id}/generate", json={})
    assert r.status_code == 422
    body = r.json()
    assert body["ok"] is False
    assert body["error"]["code"] == "INV-001"
    assert body["error"]["retry_allowed"] is False


# ─── 11. config: openai_models_for_3plan_list 검증 ────────────────────

def test_settings_openai_models_for_3plan_list_default() -> None:
    """기본 settings에서 openai_models_for_3plan_list가 정확히 3개 반환."""
    from backend.fastapi.config import get_settings

    settings = get_settings()
    models = settings.openai_models_for_3plan_list
    assert len(models) == 3, f"expected 3 models, got {len(models)}"
    # 기본값은 모두 gpt-4o-mini
    assert all(m == "gpt-4o-mini" for m in models)


def test_settings_openai_models_for_3plan_list_padding(monkeypatch) -> None:
    """env에 1개만 지정 시 default로 padding하여 길이 3 보장."""
    monkeypatch.setenv("OPENAI_MODELS_FOR_3PLAN", "gpt-4o")
    from backend.fastapi.config import get_settings

    get_settings.cache_clear()
    settings = get_settings()
    models = settings.openai_models_for_3plan_list
    assert len(models) == 3
    # 첫 모델은 env 지정값, 나머지는 첫 모델로 padding
    assert models == ["gpt-4o", "gpt-4o", "gpt-4o"]


def test_settings_openai_models_for_3plan_list_multi(monkeypatch) -> None:
    """env에 3개 모두 지정 시 그대로 반영 (multi-model 인터페이스)."""
    monkeypatch.setenv(
        "OPENAI_MODELS_FOR_3PLAN", "gpt-4o-mini,gpt-4o,gpt-4o-mini"
    )
    from backend.fastapi.config import get_settings

    get_settings.cache_clear()
    settings = get_settings()
    models = settings.openai_models_for_3plan_list
    assert models == ["gpt-4o-mini", "gpt-4o", "gpt-4o-mini"]


# ─── 12. compute_validation_warnings_phase4 helper 단위 테스트 ───────

def test_compute_validation_warnings_phase4_3_plans_critic_rag() -> None:
    """plans=3 + critic_present + rag ok → only phase_4_no_revise_loop."""
    from backend.fastapi.schemas.output import compute_validation_warnings_phase4

    warnings = compute_validation_warnings_phase4(
        plans_count=3,
        rag_used_fallback=False,
        critic_present=True,
        has_revise_loop=False,
    )
    assert "phase_1_single_plan" not in warnings
    assert "phase_1_no_rag" not in warnings
    assert "phase_1_no_critic" not in warnings
    assert "phase_4_no_revise_loop" in warnings


def test_compute_validation_warnings_phase4_phase1_endpoint_signature() -> None:
    """Phase 1 endpoint 형태 (plans=1) → phase_1_single_plan 유지, no revise warning 미추가."""
    from backend.fastapi.schemas.output import compute_validation_warnings_phase4

    warnings = compute_validation_warnings_phase4(
        plans_count=1,
        rag_used_fallback=True,
        critic_present=True,
        has_revise_loop=False,
    )
    assert "phase_1_single_plan" in warnings
    assert "phase_1_no_rag" in warnings
    # plans_count == 1 일 때는 phase_4_no_revise_loop 미추가 (Phase 1 endpoint baseline)
    assert "phase_4_no_revise_loop" not in warnings


# ─── 13. multi-model: models 파라미터 분기 가능 (인터페이스 검증) ─────

@pytest.mark.asyncio
async def test_run_planning_parallel_3_models_param_validation() -> None:
    """models 파라미터가 3개가 아닐 때 ValueError (multi-model 인터페이스 검증)."""
    from backend.fastapi.agents.planning import run_planning_parallel_3

    with pytest.raises(ValueError, match="Expected 3 models"):
        await run_planning_parallel_3(
            "유튜브 쇼츠", models=["gpt-4o-mini", "gpt-4o-mini"],
        )
