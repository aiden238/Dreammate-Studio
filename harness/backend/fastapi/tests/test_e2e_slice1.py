"""Phase 1 Slice 1 — end-to-end 검증.

검증 항목 (assumptions.md §4.1 매핑):
  A1. /api/v1/generate 응답 HTTP 200 + envelope 구조
  A6. output_schema v1.0 준수 (meta / body / validation)
  + health endpoint 동작
  + Intent 차단 시 422 (Slice 2에서 정식 ErrorEnvelope로 교체)
  + 입력 검증 (빈 문자열 / 너무 긴 문자열 차단)
"""

from __future__ import annotations

from fastapi.testclient import TestClient

from backend.fastapi.main import app


client = TestClient(app)


# ─── A1. /api/v1/generate 200 응답 ────────────────────────────────────

def test_generate_returns_200_with_envelope(mock_openai_intent_ok) -> None:
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

def test_generate_meta_fields(mock_openai_intent_ok) -> None:
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


def test_generate_body_plans_phase1_single(mock_openai_intent_ok) -> None:
    """Phase 1 body.plans 길이 1 (deviation from contract 3)."""
    response = client.post(
        "/api/v1/generate",
        json={"input": "초보 요리 쇼츠 채널 첫 영상"},
    )
    data = response.json()

    plans = data["body"]["plans"]
    assert len(plans) == 1, "Phase 1 Slice 1은 plans 1개만 반환"

    plan = plans[0]
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


def test_generate_validation_warnings_phase1(mock_openai_intent_ok) -> None:
    """Phase 1 deviation은 validation.warnings에 명시."""
    response = client.post(
        "/api/v1/generate",
        json={"input": "쇼츠 콘텐츠 기획"},
    )
    data = response.json()

    validation = data["validation"]
    assert validation["passed"] is True

    warnings = validation["warnings"]
    assert "phase_1_single_plan" in warnings
    assert "phase_1_no_rag" in warnings
    assert "phase_1_no_critic" in warnings


# ─── Intent 차단 (Slice 2 전 임시 응답) ───────────────────────────────

def test_generate_intent_block_returns_422(mock_openai_intent_block) -> None:
    """영상기획 외 요청 → 422 (Slice 2에서 ErrorEnvelope로 교체 예정)."""
    response = client.post(
        "/api/v1/generate",
        json={"input": "오늘 서울 날씨 알려줘"},
    )

    assert response.status_code == 422
    body = response.json()
    assert body["detail"]["code"] == "INV-001"


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
    assert data["slice"] == "1"


# ─── OpenAPI 문서 노출 ────────────────────────────────────────────────

def test_openapi_docs_available() -> None:
    """FastAPI 자동 OpenAPI 문서가 노출되는지."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    spec = response.json()
    paths = spec.get("paths", {})
    assert "/api/v1/generate" in paths
    assert "/health" in paths
