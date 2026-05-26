"""pytest fixtures — OPENAI_API_KEY 없이도 테스트 통과시키기 위한 mock 주입.

Slice 2 변경:
  - mock_openai_intent_ok / mock_openai_intent_block (Slice 1 통합 호출용) 제거
  - mock_intent_ok / mock_intent_block / mock_planning_ok 분리
  - mock_pipeline_ok: 라우터 e2e용 (Intent allow + Planning success) 조합 fixture
"""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

import pytest


# ─── 환경변수 강제 주입 ────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def _env_setup(monkeypatch: pytest.MonkeyPatch) -> None:
    """모든 테스트에 더미 OPENAI_API_KEY 주입.

    실제 LLM 호출은 mock으로 차단되므로 키 자체는 사용되지 않는다.
    """
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-dummy")
    monkeypatch.setenv("APP_ENV", "development")
    # config.get_settings는 lru_cache이므로 cache 초기화 필요
    from backend.fastapi.config import get_settings

    get_settings.cache_clear()


# ─── Mock 응답 데이터 ──────────────────────────────────────────────────

_INTENT_OK_RESPONSE: dict[str, Any] = {
    "intent_ok": True,
    "category": "video_planning",
}

_INTENT_BLOCK_RESPONSE: dict[str, Any] = {
    "intent_ok": False,
    "reason": "영상기획과 무관한 요청 (날씨 질의)",
}

_PLANNING_OK_RESPONSE: dict[str, Any] = {
    "plan": {
        "name": "첫 영상 시작하기",
        "concept": "초보 유튜버를 위한 채널 첫 영상 콘셉트 안내",
        "hook": "구독자 0명에서 시작한 채널이 첫 영상으로 한 일",
        "flow": [
            {
                "beat_index": 0,
                "beat": "도입 — 시청자 공감",
                "duration_sec": 3,
                "purpose": "관심 유발",
            },
            {
                "beat_index": 1,
                "beat": "전개 — 채널 운영 동기",
                "duration_sec": 20,
                "purpose": "신뢰 형성",
            },
            {
                "beat_index": 2,
                "beat": "마무리 — 다음 영상 예고",
                "duration_sec": 7,
                "purpose": "재방문 유도",
            },
        ],
        "pros": "콜드스타트 시청자에게 친근",
        "risks": "후크가 약하면 이탈률 높음",
        "approach_label": "narrative",
    },
}


# ─── Intent 단독 mock ──────────────────────────────────────────────────

@pytest.fixture
def mock_intent_ok(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    """Intent Agent가 영상기획 통과를 반환하는 mock."""

    def fake_call(*args: Any, **kwargs: Any) -> dict[str, Any]:
        return dict(_INTENT_OK_RESPONSE)

    monkeypatch.setattr("backend.fastapi.routers.generate.run_intent", fake_call)
    return MagicMock()


@pytest.fixture
def mock_intent_block(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    """Intent Agent가 차단을 반환하는 mock."""

    def fake_call(*args: Any, **kwargs: Any) -> dict[str, Any]:
        return dict(_INTENT_BLOCK_RESPONSE)

    monkeypatch.setattr("backend.fastapi.routers.generate.run_intent", fake_call)
    return MagicMock()


# ─── Planning 단독 mock ────────────────────────────────────────────────

@pytest.fixture
def mock_planning_ok(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    """Planning Agent가 정상 plan을 반환하는 mock."""

    def fake_call(*args: Any, **kwargs: Any) -> dict[str, Any]:
        # deepcopy 효과를 위해 매 호출 새 dict
        import copy

        return copy.deepcopy(_PLANNING_OK_RESPONSE)

    monkeypatch.setattr("backend.fastapi.routers.generate.run_planning", fake_call)
    return MagicMock()


# ─── 파이프라인 (Intent allow + Planning success) 조합 fixture ─────────

@pytest.fixture
def mock_pipeline_ok(
    mock_intent_ok: MagicMock,
    mock_planning_ok: MagicMock,
) -> MagicMock:
    """e2e 정상 경로 fixture — router 응답 200 검증용."""
    return MagicMock()
