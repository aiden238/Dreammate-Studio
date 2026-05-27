"""Phase 1 Slice 1 + Slice 2 + Slice 3 + Slice 4 + Slice 5 — end-to-end 검증.

검증 항목 (assumptions.md §4.1 매핑):
  A1. /api/v1/generate 응답 HTTP 200 + envelope 구조
  A6. output_schema v1.0 준수 (meta / body / validation)
  + health endpoint 동작
  + Intent 차단 시 422 + INV-001 ErrorEnvelope (Slice 2)
  + 입력 검증 (빈 문자열 / 너무 긴 문자열 차단)
  + Critic 평가 결과가 body.critic_evaluation에 포함 (Slice 3)
  + validation.warnings에서 phase_1_no_critic 제거 (Slice 3)
  + body.rag_references 필드 활성화 + fallback graceful (Slice 4)
  + validation.warnings에서 phase_1_no_rag 제거 (Slice 4)
  + meta.project_id 노출 + DB 실패 시 graceful 200 (Slice 5)
  + validation.checks에 db_persistence 추가 (Slice 5)
"""

from __future__ import annotations

from fastapi.testclient import TestClient

from backend.fastapi.main import app


client = TestClient(app)


# ─── A1. /api/v1/generate 200 응답 ────────────────────────────────────

def test_generate_returns_200_with_envelope(mock_pipeline_ok) -> None:
    """정상 입력 → HTTP 200 + envelope 구조."""
    response = client.post(
        "/api/v1/generate",
        json={"input": "유튜브 채널 첫 영상 기획해줘"},
    )

    assert response.status_code == 200
    data = response.json()

    # envelope 3섹션 모두 존재
    assert "meta" in data
    assert "body" in data
    assert "validation" in data


# ─── A6. output_schema v1.0 준수 ──────────────────────────────────────

def test_generate_meta_fields(mock_pipeline_ok) -> None:
    """meta 필수 필드 확인 (output_schema.md §2)."""
    response = client.post(
        "/api/v1/generate",
        json={"input": "30대 직장인 대상 재테크 쇼츠 기획해줘"},
    )
    data = response.json()

    meta = data["meta"]
    assert meta["schema_version"] == "1.0.0"
    assert meta["prompt_id"].startswith("P-")
    assert meta["model"]
    assert "request_id" in meta
    assert "generated_at" in meta
    assert meta["locale"] == "ko-KR"


def test_generate_body_plans_phase1_single(mock_pipeline_ok) -> None:
    """Phase 1 body.plan_candidates 길이 1 (deviation from contract 3)."""
    response = client.post(
        "/api/v1/generate",
        json={"input": "초보 요리 쇼츠 채널 첫 영상"},
    )
    data = response.json()

    plan_candidates = data["body"]["plan_candidates"]
    assert len(plan_candidates) == 1, "Phase 1 Slice 1은 plan_candidates 1개만 반환"

    plan = plan_candidates[0]
    assert plan["plan_id"]
    assert plan["option_index"] == 0
    assert plan["name"]
    assert plan["hook"]
    assert isinstance(plan["flow"], list)
    assert len(plan["flow"]) >= 2
    assert plan["approach_label"] in [
        "narrative",
        "informational",
        "empathy",
        "experiment",
        "review",
        "other",
    ]


def test_generate_validation_warnings_phase1(mock_pipeline_ok) -> None:
    """Phase 1 deviation은 validation.warnings에 명시.

    Slice 3: Critic 활성화 → `phase_1_no_critic` 제거됨.
    Slice 4: RAG 활성화 → `phase_1_no_rag` 제거됨.
    남는 deviation 경고는 `phase_1_single_plan` (3 vs 1) 만.
    """
    response = client.post(
        "/api/v1/generate",
        json={"input": "쇼츠 콘텐츠 기획"},
    )
    data = response.json()

    validation = data["validation"]
    assert validation["passed"] is True

    warnings = validation["warnings"]
    assert "phase_1_single_plan" in warnings
    assert "phase_1_no_rag" not in warnings, (
        "Slice 4에서 RAG가 활성화되었으므로 phase_1_no_rag 경고가 사라져야 함"
    )
    assert "phase_1_no_critic" not in warnings, (
        "Slice 3에서 Critic이 활성화되었으므로 phase_1_no_critic 경고가 사라져야 함"
    )


# ─── Critic 평가 (Slice 3) ────────────────────────────────────────────

def test_generate_includes_critic_evaluation(mock_pipeline_ok) -> None:
    """body.critic_evaluation 8 차원 + verdict 포함 (output_schema §9.1)."""
    response = client.post(
        "/api/v1/generate",
        json={"input": "초보 요리 쇼츠 채널 첫 영상 기획해줘"},
    )
    assert response.status_code == 200
    data = response.json()

    critic = data["body"].get("critic_evaluation")
    assert critic is not None, "Slice 3: body.critic_evaluation 필드 채워져야 함"

    # 8 차원 점수 모두 0~5 정수
    scores = critic["scores"]
    expected_dims = {
        "intent_fit",
        "target_clarity",
        "hook_strength",
        "message_clarity",
        "structure",
        "feasibility",
        "brand_consistency",
        "differentiation",
    }
    assert set(scores.keys()) == expected_dims
    for k, v in scores.items():
        assert isinstance(v, int)
        assert 0 <= v <= 5, f"{k} 점수가 0~5 범위 밖: {v}"

    # verdict는 enum
    assert critic["overall_verdict"] in ("approve", "revise", "reject")

    # plan_id echo back
    plan_id = data["body"]["plan_candidates"][0]["plan_id"]
    assert critic["target_plan_id"] == plan_id

    # Phase 1: revise_round 항상 0
    assert critic["revise_round"] == 0


def test_generate_critic_validation_check_present(mock_pipeline_ok) -> None:
    """validation.checks에 critic_evaluation 항목이 P-007@v1.0.0 detail로 노출."""
    response = client.post(
        "/api/v1/generate",
        json={"input": "유튜브 첫 영상"},
    )
    data = response.json()
    checks = data["validation"]["checks"]

    critic_check = next((c for c in checks if c["name"] == "critic_evaluation"), None)
    assert critic_check is not None
    assert critic_check["status"] == "ok"
    assert critic_check["detail"] == "P-007@v1.0.0"


def test_generate_critic_flagged_returns_revise_verdict(
    mock_intent_ok, mock_rag_fallback, mock_planning_ok, mock_critic_flagged, mock_db_save_ok
) -> None:
    """Critic이 약한 plan을 flag → verdict=revise, blocking_issues 채워짐.

    Phase 1: revise verdict여도 router는 정상 200 응답 (revise 호출 없음).
    Slice 5: DB save 도 동시 동작 (mock_db_save_ok 체이닝).
    """
    response = client.post(
        "/api/v1/generate",
        json={"input": "건강 관련 쇼츠"},
    )
    assert response.status_code == 200
    data = response.json()

    critic = data["body"]["critic_evaluation"]
    assert critic["overall_verdict"] == "revise"
    assert len(critic["blocking_issues"]) >= 1
    # FC-001/002 시드 패턴 — hook_strength, target_clarity가 미달
    assert critic["scores"]["hook_strength"] < 2
    assert critic["scores"]["target_clarity"] < 2


# ─── RAG references (Slice 4) ─────────────────────────────────────────

def test_generate_includes_rag_references(
    mock_intent_ok, mock_rag_ok, mock_planning_ok, mock_critic_ok, mock_db_save_ok
) -> None:
    """RAG 가 OK 경로일 때 body.rag_references 가 채워지고 validation.checks에 rag_retrieval ok."""
    response = client.post(
        "/api/v1/generate",
        json={"input": "건강한 식단 쇼츠 기획"},
    )
    assert response.status_code == 200
    data = response.json()

    refs = data["body"]["rag_references"]
    assert len(refs) == 2
    assert refs[0]["source_id"] == "seed-001"

    # validation.checks 에 rag_retrieval status=ok
    checks = data["validation"]["checks"]
    rag_check = next((c for c in checks if c["name"] == "rag_retrieval"), None)
    assert rag_check is not None
    assert rag_check["status"] == "ok"


def test_generate_with_rag_fallback(
    mock_intent_ok, mock_rag_fallback, mock_planning_ok, mock_critic_ok, mock_db_save_ok
) -> None:
    """RAG fallback 시 body.rag_references==[] + validation.checks.rag_retrieval status=warn."""
    response = client.post(
        "/api/v1/generate",
        json={"input": "유튜브 채널 첫 영상"},
    )
    assert response.status_code == 200
    data = response.json()

    assert data["body"]["rag_references"] == []

    checks = data["validation"]["checks"]
    rag_check = next((c for c in checks if c["name"] == "rag_retrieval"), None)
    assert rag_check is not None
    assert rag_check["status"] == "warn"


# ─── DB persistence (Slice 5) ─────────────────────────────────────────


def test_generate_includes_project_id(mock_pipeline_ok) -> None:
    """DB 저장 성공 시 meta.project_id 가 fake-project-uuid 로 노출된다."""
    response = client.post(
        "/api/v1/generate",
        json={"input": "유튜브 채널 첫 영상"},
    )
    assert response.status_code == 200
    data = response.json()

    assert data["meta"]["project_id"] == "fake-project-uuid"


def test_generate_includes_db_persistence_check_ok(mock_pipeline_ok) -> None:
    """validation.checks 에 db_persistence status=ok + detail 에 project_id 포함."""
    response = client.post(
        "/api/v1/generate",
        json={"input": "유튜브 채널 첫 영상"},
    )
    data = response.json()
    checks = data["validation"]["checks"]

    db_check = next((c for c in checks if c["name"] == "db_persistence"), None)
    assert db_check is not None, "Slice 5: db_persistence check 가 노출되어야 함"
    assert db_check["status"] == "ok"
    assert "saved" in db_check["detail"]
    assert "fake-project-uuid" in db_check["detail"]


def test_generate_db_failure_still_returns_200(
    mock_intent_ok, mock_rag_fallback, mock_planning_ok, mock_critic_ok, mock_db_save_fail
) -> None:
    """DB 저장 실패 시 — HTTP 200 + meta.project_id=null + db_persistence status=warn.

    Phase 1 핵심 acceptance: DB 실패는 절대 사용자를 차단하지 않는다.
    """
    response = client.post(
        "/api/v1/generate",
        json={"input": "유튜브 채널 첫 영상"},
    )

    assert response.status_code == 200, "DB 실패 시도 사용자 응답은 정상 200 유지"
    data = response.json()

    assert data["meta"]["project_id"] is None

    checks = data["validation"]["checks"]
    db_check = next((c for c in checks if c["name"] == "db_persistence"), None)
    assert db_check is not None
    assert db_check["status"] == "warn"
    assert "failed_db_error" in db_check["detail"]


def test_generate_db_skipped_still_returns_200(
    mock_intent_ok, mock_rag_fallback, mock_planning_ok, mock_critic_ok, mock_db_save_skipped
) -> None:
    """Supabase env 미설정 (skipped_no_db) 시도 HTTP 200 유지.

    개발 환경에서 .env에 SUPABASE_URL 없이도 정상 동작 보장 (graceful skip).
    """
    response = client.post(
        "/api/v1/generate",
        json={"input": "유튜브 채널 첫 영상"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["meta"]["project_id"] is None

    checks = data["validation"]["checks"]
    db_check = next((c for c in checks if c["name"] == "db_persistence"), None)
    assert db_check is not None
    assert db_check["status"] == "warn"
    assert "skipped_no_db" in db_check["detail"]


# ─── Intent 차단 (Slice 2 INV-001 ErrorEnvelope) ──────────────────────

def test_generate_intent_block_returns_422_envelope(mock_intent_block) -> None:
    """영상기획 외 요청 → 422 + INV-001 ErrorEnvelope (Slice 2 정식 응답)."""
    response = client.post(
        "/api/v1/generate",
        json={"input": "오늘 서울 날씨 알려줘"},
    )

    assert response.status_code == 422
    body = response.json()

    # ErrorEnvelope 정합 (error_response_contract.md §1)
    assert body["ok"] is False
    assert "error" in body
    assert "meta" in body

    err = body["error"]
    assert err["code"] == "INV-001"
    assert isinstance(err["message"], str) and err["message"]
    assert isinstance(err["user_message"], str) and err["user_message"]
    assert err["retry_allowed"] is False

    meta = body["meta"]
    assert "request_id" in meta and meta["request_id"]
    assert "generated_at" in meta and meta["generated_at"]


# ─── 입력 검증 ────────────────────────────────────────────────────────

def test_generate_rejects_empty_input() -> None:
    """빈 input → 422 (Pydantic 검증)."""
    response = client.post(
        "/api/v1/generate",
        json={"input": ""},
    )
    assert response.status_code == 422


def test_generate_rejects_oversize_input() -> None:
    """2000자 초과 input → 422 (Pydantic 검증)."""
    response = client.post(
        "/api/v1/generate",
        json={"input": "a" * 2001},
    )
    assert response.status_code == 422


def test_generate_default_locale() -> None:
    """locale 미지정 시 ko-KR 기본값."""
    # 실제 LLM 호출 없이 Pydantic 모델 검증만
    from backend.fastapi.schemas.input import GenerateRequest

    req = GenerateRequest(input="테스트 입력")
    assert req.locale == "ko-KR"


# ─── Health ───────────────────────────────────────────────────────────

def test_health_endpoint() -> None:
    """uvicorn 부트 후 헬스체크."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["phase"] == "1"


# ─── OpenAPI 문서 노출 ────────────────────────────────────────────────

def test_openapi_docs_available() -> None:
    """FastAPI 자동 OpenAPI 문서가 노출되는지."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    spec = response.json()
    paths = spec.get("paths", {})
    assert "/api/v1/generate" in paths
    assert "/health" in paths
