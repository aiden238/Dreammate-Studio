"""pytest fixtures — OPENAI_API_KEY 없이도 테스트 통과시키기 위한 mock 주입."""

from __future__ import annotations

import os
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


# ─── OpenAI client mock ────────────────────────────────────────────────

@pytest.fixture
def mock_openai_intent_ok(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    """LLM이 영상기획 정상 응답을 반환하는 mock."""

    def fake_call(*args: Any, **kwargs: Any) -> dict[str, Any]:
        return {
            "intent_ok": True,
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

    monkeypatch.setattr(
        "backend.fastapi.routers.generate.run_intent_planning",
        fake_call,
    )
    return MagicMock()


@pytest.fixture
def mock_openai_intent_block(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    """LLM이 Intent 차단 응답을 반환하는 mock."""

    def fake_call(*args: Any, **kwargs: Any) -> dict[str, Any]:
        return {
            "intent_ok": False,
            "reason": "영상기획과 무관한 요청 (날씨 질의)",
        }

    monkeypatch.setattr(
        "backend.fastapi.routers.generate.run_intent_planning",
        fake_call,
    )
    return MagicMock()
