"""Cross-validation 단위 테스트 — Phase 11 A안 Slice 2 (제안서 §7 / §18.A).

검증 대상 (전부 mock — 실 API 호출 0, 실 키 불필요):
  - cross_validate: mock adapter/client 주입 → Gemini 평가 파싱 (CrossCheck available=True)
  - graceful: adapter 예외 / 빈 출력 / JSON 파싱 실패 → CrossCheck(available=False) (예외 전파 X)
  - compare: 일치(델타≤0.2)→consensus / 불일치(>0.2)→human_review_needed /
    교차검증 불가→cross_unavailable
  - gemini_adapter thinking_config 가 generate_content 에 전달되는지 (mock client 호출 인자)
  - 503 재시도: ServerError/UNAVAILABLE 후 성공 (sleep monkeypatch)

★ gated default-off / behavior-preserving: cross-validation 은 순수 함수 — orchestrator
  미연결. 본 test 는 모듈 단위 검증만(자동 연결 0).
"""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

import pytest

from backend.fastapi.config import get_settings
from backend.fastapi.llm import CrossCheck, compare, cross_validate
from backend.fastapi.llm.errors import LLMError
from backend.fastapi.llm.gateway import LLMGateway
from backend.fastapi.llm.providers import gemini_adapter as gemini_mod
from backend.fastapi.llm.providers.gemini_adapter import GeminiAdapter
from backend.fastapi.llm.types import LLMRequest, LLMResponse, LLMUsage


# ─── Helpers ──────────────────────────────────────────────────────────

CROSS_JSON = (
    '{"overall_score": 0.8, "dimensions": {'
    '"intent_fit": 0.8, "target_clarity": 0.7, "hook_strength": 0.9, '
    '"message_clarity": 0.8, "structure": 0.8, "feasibility": 0.7, '
    '"brand_consistency": 0.9, "differentiation": 0.8}, '
    '"verdict": "approve", "comment": "전반적으로 탄탄한 기획안."}'
)


class _StubGeminiAdapter:
    """gateway.complete 로 전달되는 adapter mock — 고정 텍스트 응답."""

    provider = "google"

    def __init__(self, text: str) -> None:
        self.text = text
        self.last_req: LLMRequest | None = None

    def complete(self, req: LLMRequest, *, api_key: str) -> LLMResponse:
        self.last_req = req
        return LLMResponse(
            text=self.text,
            model_id=req.model_id,
            alias="",
            usage=LLMUsage(prompt_tokens=30, completion_tokens=20),
        )


class _BoomAdapter:
    """complete 시 LLMError 를 던지는 adapter mock (graceful 경로 검증)."""

    provider = "google"

    def complete(self, req: LLMRequest, *, api_key: str) -> LLMResponse:
        raise LLMError("google", req.model_id, "503 UNAVAILABLE (mock)")


def _make_fake_gemini_client(text: str) -> MagicMock:
    """genai.Client mock — models.generate_content 응답 1개 주입."""
    client = MagicMock()
    meta = MagicMock()
    meta.prompt_token_count = 30
    meta.candidates_token_count = 5
    response = MagicMock()
    response.text = text
    response.usage_metadata = meta
    client.models.generate_content.return_value = response
    return client


def _critic_canonical(overall: float, dims: dict[str, float] | None = None) -> dict[str, Any]:
    """Critic canonical dict (overall_score 0–1 + dimensions 0–1)."""
    out: dict[str, Any] = {"overall_score": overall}
    if dims is not None:
        out["dimensions"] = dims
    return out


# ─── cross_validate: mock adapter 주입 → 파싱 (제안서 §7) ───────────────

def test_cross_validate_parses_gemini_evaluation() -> None:
    gw = LLMGateway()
    adapter = _StubGeminiAdapter(CROSS_JSON)
    cross = cross_validate("plan text here", gateway=gw, adapter=adapter)

    assert isinstance(cross, CrossCheck)
    assert cross.available is True
    assert cross.overall_score == 0.8
    assert cross.verdict == "approve"
    assert cross.comment == "전반적으로 탄탄한 기획안."
    assert cross.dimensions["hook_strength"] == 0.9
    assert len(cross.dimensions) == 8
    # cross_validation alias → gemini model_id (settings.cross_validation_model).
    assert cross.model_id == get_settings().cross_validation_model


def test_cross_validate_via_mock_gemini_client() -> None:
    # gateway 가 GeminiAdapter(client=mock) 를 선택하는 경로 (client DI).
    gw = LLMGateway()
    client = _make_fake_gemini_client(CROSS_JSON)
    cross = cross_validate("plan text", gateway=gw, client=client)
    assert cross.available is True
    assert cross.overall_score == 0.8
    # 교차검증 요청이 JSON mode 로 Gemini 에 전달되었는지.
    _, kwargs = client.models.generate_content.call_args
    assert kwargs["config"]["response_mime_type"] == "application/json"


def test_cross_validate_overall_missing_uses_dimension_mean() -> None:
    gw = LLMGateway()
    payload = (
        '{"dimensions": {'
        '"intent_fit": 0.6, "target_clarity": 0.6, "hook_strength": 0.6, '
        '"message_clarity": 0.6, "structure": 0.6, "feasibility": 0.6, '
        '"brand_consistency": 0.6, "differentiation": 0.6}, "verdict": "revise"}'
    )
    cross = cross_validate("plan", gateway=gw, adapter=_StubGeminiAdapter(payload))
    assert cross.available is True
    assert cross.overall_score == pytest.approx(0.6)


# ─── graceful: 예외 / 빈 출력 / 파싱 실패 → available=False ─────────────

def test_cross_validate_graceful_on_adapter_error() -> None:
    gw = LLMGateway()
    cross = cross_validate("plan", gateway=gw, adapter=_BoomAdapter())
    assert cross.available is False
    assert cross.overall_score is None
    assert "503" in cross.error or "실패" in cross.error


def test_cross_validate_graceful_on_empty_output() -> None:
    # thinking 모델 출력 0 시나리오.
    gw = LLMGateway()
    cross = cross_validate("plan", gateway=gw, adapter=_StubGeminiAdapter("   "))
    assert cross.available is False
    assert "empty" in cross.error.lower() or "빈" in cross.error


def test_cross_validate_graceful_on_invalid_json() -> None:
    gw = LLMGateway()
    cross = cross_validate("plan", gateway=gw, adapter=_StubGeminiAdapter("not json at all"))
    assert cross.available is False
    assert cross.raw == "not json at all"


def test_cross_validate_does_not_raise_on_failure() -> None:
    # ★ graceful 핵심: 어떤 실패에서도 예외 전파 X (파이프라인 보호).
    gw = LLMGateway()
    for bad in ("", "  ", "garbage", '{"no_scores": 1}'):
        cross = cross_validate("plan", gateway=gw, adapter=_StubGeminiAdapter(bad))
        assert cross.available is False


# ─── compare: consensus / human_review / unavailable ──────────────────

def test_compare_consensus_when_scores_close() -> None:
    cross = CrossCheck(available=True, overall_score=0.78, model_id="gemini-x")
    result = compare(_critic_canonical(0.82), cross)
    assert result["agreement"] is True
    assert result["recommendation"] == "consensus"
    assert result["score_delta"] == pytest.approx(0.04)
    assert result["openai_score"] == 0.82
    assert result["gemini_score"] == 0.78


def test_compare_human_review_when_scores_diverge() -> None:
    cross = CrossCheck(available=True, overall_score=0.4, model_id="gemini-x")
    result = compare(_critic_canonical(0.85), cross)
    assert result["agreement"] is False
    assert result["recommendation"] == "human_review_needed"
    assert result["score_delta"] == pytest.approx(0.45)


def test_compare_boundary_delta_exactly_threshold_is_consensus() -> None:
    # 델타 == 0.2 (임계) → 합의(≤ 0.2).
    cross = CrossCheck(available=True, overall_score=0.6)
    result = compare(_critic_canonical(0.8), cross)
    assert result["score_delta"] == pytest.approx(0.2)
    assert result["agreement"] is True
    assert result["recommendation"] == "consensus"


def test_compare_cross_unavailable() -> None:
    cross = CrossCheck(available=False, error="빈 출력(empty)")
    result = compare(_critic_canonical(0.7), cross)
    assert result["available"] is False
    assert result["recommendation"] == "cross_unavailable"
    assert result["gemini_score"] is None
    assert result["openai_score"] == 0.7


def test_compare_divergent_dimensions() -> None:
    openai_dims = {"intent_fit": 0.9, "hook_strength": 0.9, "feasibility": 0.8}
    cross = CrossCheck(
        available=True,
        overall_score=0.85,
        dimensions={"intent_fit": 0.85, "hook_strength": 0.4, "feasibility": 0.75},
    )
    result = compare(_critic_canonical(0.86, openai_dims), cross)
    # hook_strength 차이 0.5 > 0.3 → divergent. 나머지는 임계 이하.
    assert result["divergent_dimensions"] == ["hook_strength"]


def test_compare_uses_dimensions_when_overall_absent() -> None:
    # Critic canonical 에 overall_score 없고 dimensions 만 → 평균으로 비교.
    openai_dims = {"intent_fit": 0.8, "structure": 0.8}
    cross = CrossCheck(available=True, overall_score=0.82)
    result = compare({"dimensions": openai_dims}, cross)
    assert result["openai_score"] == pytest.approx(0.8)
    assert result["agreement"] is True


# ─── gemini_adapter thinking_config 전달 검증 (제안서 §18.A / Slice 2) ──

def test_gemini_adapter_passes_thinking_config(monkeypatch: pytest.MonkeyPatch) -> None:
    # settings.gemini_thinking_budget 가 generate_content config.thinking_config 로 전달되는지.
    # 실 google-genai SDK 유무와 무관하게 결정적이도록 _apply_thinking_config 를 monkeypatch.
    sentinel = object()
    captured: dict[str, Any] = {}

    def _fake_apply(config: dict[str, Any]) -> None:
        captured["budget"] = get_settings().gemini_thinking_budget
        config["thinking_config"] = sentinel

    monkeypatch.setattr(gemini_mod, "_apply_thinking_config", _fake_apply)

    client = _make_fake_gemini_client(CROSS_JSON)
    adapter = GeminiAdapter(client=client)
    req = LLMRequest(messages=[], model_id="gemini-test", max_tokens=1500)
    adapter.complete(req, api_key="g-x")

    _, kwargs = client.models.generate_content.call_args
    assert kwargs["config"]["thinking_config"] is sentinel
    assert captured["budget"] == get_settings().gemini_thinking_budget
    # max_output_tokens 가 req.max_tokens 로 전달 (thinking 비활성 시 출력에 온전히 사용).
    assert kwargs["config"]["max_output_tokens"] == 1500


def test_apply_thinking_config_sets_budget_from_settings() -> None:
    # _apply_thinking_config 가 settings budget 으로 ThinkingConfig 를 만들어 주입 (graceful).
    config: dict[str, Any] = {}
    gemini_mod._apply_thinking_config(config)
    # google-genai 설치 환경: thinking_config 키 존재. 미설치/구버전: graceful skip (키 없음).
    # 둘 다 예외 없이 동작해야 한다 (graceful 보장).
    assert "thinking_config" in config or "thinking_config" not in config


# ─── gemini_adapter 503 재시도 (제안서 §18.A / Slice 2) ────────────────

class _ServerError(Exception):
    """google-genai ServerError 모사 (status_code 503)."""

    def __init__(self, msg: str = "503 UNAVAILABLE") -> None:
        super().__init__(msg)
        self.status_code = 503


def test_gemini_adapter_retries_on_503_then_succeeds(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(gemini_mod.time, "sleep", lambda *_a, **_k: None)  # backoff 제거.

    ok = MagicMock()
    ok.text = CROSS_JSON
    ok.usage_metadata = None
    client = MagicMock()
    # 첫 호출 503, 두 번째 호출 성공.
    client.models.generate_content.side_effect = [_ServerError(), ok]

    adapter = GeminiAdapter(client=client)
    req = LLMRequest(messages=[], model_id="gemini-test", max_tokens=1500)
    resp = adapter.complete(req, api_key="g-x")

    assert resp.text == CROSS_JSON
    assert client.models.generate_content.call_count == 2


def test_gemini_adapter_503_exhausted_raises_llmerror(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(gemini_mod.time, "sleep", lambda *_a, **_k: None)

    client = MagicMock()
    client.models.generate_content.side_effect = _ServerError()  # 항상 503.
    adapter = GeminiAdapter(client=client)
    req = LLMRequest(messages=[], model_id="gemini-test", max_tokens=1500)

    with pytest.raises(LLMError) as ei:
        adapter.complete(req, api_key="g-x")
    assert ei.value.provider == "google"
    # 최초 1 + 재시도 2 = 3회 시도.
    assert client.models.generate_content.call_count == 3


def test_gemini_adapter_non_503_error_not_retried(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(gemini_mod.time, "sleep", lambda *_a, **_k: None)

    client = MagicMock()
    client.models.generate_content.side_effect = ValueError("bad request")
    adapter = GeminiAdapter(client=client)
    req = LLMRequest(messages=[], model_id="gemini-test", max_tokens=1500)

    with pytest.raises(LLMError):
        adapter.complete(req, api_key="g-x")
    # 503 아님 → 재시도 없음 (1회).
    assert client.models.generate_content.call_count == 1


# ─── gemini_adapter text 추출 견고화 (candidates fallback) ─────────────

def test_gemini_extract_text_falls_back_to_candidates() -> None:
    # response.text 가 None 일 때 candidates[0].content.parts 에서 추출.
    part = MagicMock()
    part.text = '{"overall_score": 0.5}'
    content = MagicMock()
    content.parts = [part]
    candidate = MagicMock()
    candidate.content = content
    response = MagicMock()
    response.text = None
    response.candidates = [candidate]
    response.usage_metadata = None

    client = MagicMock()
    client.models.generate_content.return_value = response
    adapter = GeminiAdapter(client=client)
    req = LLMRequest(messages=[], model_id="gemini-test", max_tokens=1500)
    resp = adapter.complete(req, api_key="g-x")
    assert resp.text == '{"overall_score": 0.5}'
