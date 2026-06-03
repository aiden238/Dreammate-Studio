"""Intent Agent (P-001) 단위 테스트 — Phase 1 Slice 2.

검증 대상:
  - run_intent() 가 OpenAI 클라이언트 mock으로 동작
  - 영상기획 요청 → intent_ok=True, category="video_planning"
  - 영상기획 외 요청 (날씨 / 잡담) → intent_ok=False, reason 존재
  - JSON 파싱 실패 → ValueError
  - intent_ok 필드 누락 → ValueError
"""

from __future__ import annotations

import json
from typing import Any
from unittest.mock import MagicMock

import pytest

from backend.fastapi.agents.intent import (
    PROMPT_ID,
    PROMPT_VERSION,
    SYSTEM_PROMPT,
    run_intent,
)


# ─── Helpers ──────────────────────────────────────────────────────────

def _make_fake_client(content: str) -> MagicMock:
    """OpenAI client mock — chat.completions.create 응답 1개 주입."""
    client = MagicMock()
    msg = MagicMock()
    msg.content = content
    choice = MagicMock()
    choice.message = msg
    response = MagicMock()
    response.choices = [choice]
    client.chat.completions.create.return_value = response
    return client


# ─── 메타 ─────────────────────────────────────────────────────────────

def test_intent_prompt_meta() -> None:
    """P-001 / v1.1.0 매핑 확인 (Phase 16 — Intent 완화, CC-021)."""
    assert PROMPT_ID == "P-001"
    assert PROMPT_VERSION == "v1.1.0"


def test_intent_prompt_leniency_framing() -> None:
    """Phase 16: 프롬프트가 '콘텐츠 토픽 기본 수용 + 애매하면 수용' 완화 framing 을 담는다.

    오반려(맨 토픽을 정보질문으로 차단) 회귀 방지 — 프롬프트 텍스트 가드.
    (실 분류 동작은 run_intent live 검증; 단위 테스트는 client mock 이라 framing 만 가드.)
    """
    assert "기본 수용" in SYSTEM_PROMPT
    assert "애매하면 수용" in SYSTEM_PROMPT
    # 정보성 주제 거부 금지 명시 (false-positive 원인 차단)
    assert "정보성 주제" in SYSTEM_PROMPT and "거부하지 않는다" in SYSTEM_PROMPT
    # 도메인 밖(날씨/코딩/잡담)은 여전히 거부 framing 유지
    assert "날씨" in SYSTEM_PROMPT and "코딩" in SYSTEM_PROMPT


# ─── 영상기획 통과 ────────────────────────────────────────────────────

def test_intent_allows_video_planning_request() -> None:
    """유튜브 채널 첫 영상 기획 요청 → intent_ok=True."""
    client = _make_fake_client(
        json.dumps({"intent_ok": True, "category": "video_planning"})
    )
    result = run_intent("유튜브 채널 첫 영상 기획해줘", client=client, model="gpt-4o-mini")
    assert result["intent_ok"] is True
    assert result["category"] == "video_planning"


def test_intent_allows_shorts_request() -> None:
    """쇼츠 콘셉트 요청도 통과."""
    client = _make_fake_client(
        json.dumps({"intent_ok": True, "category": "video_planning"})
    )
    result = run_intent("30초 재테크 쇼츠 기획", client=client, model="gpt-4o-mini")
    assert result["intent_ok"] is True


# ─── 거부 케이스 ──────────────────────────────────────────────────────

def test_intent_blocks_weather_query() -> None:
    """날씨 질문 → intent_ok=False (GS-003 유사 케이스)."""
    client = _make_fake_client(
        json.dumps({"intent_ok": False, "reason": "영상기획과 무관한 날씨 질의"})
    )
    result = run_intent("오늘 서울 날씨 알려줘", client=client, model="gpt-4o-mini")
    assert result["intent_ok"] is False
    assert "reason" in result and result["reason"]


def test_intent_blocks_smalltalk() -> None:
    """잡담 / 점심 추천 → intent_ok=False (GS-003 사례)."""
    client = _make_fake_client(
        json.dumps({"intent_ok": False, "reason": "잡담 / 일상 추천 요청"})
    )
    result = run_intent("오늘 점심 뭐 먹지? 추천해줘", client=client, model="gpt-4o-mini")
    assert result["intent_ok"] is False
    assert result["reason"]


def test_intent_blocks_coding_help() -> None:
    """일반 코딩 도움 요청 → intent_ok=False."""
    client = _make_fake_client(
        json.dumps({"intent_ok": False, "reason": "일반 코딩 도움 요청"})
    )
    result = run_intent(
        "파이썬 리스트 정렬 어떻게 해?", client=client, model="gpt-4o-mini"
    )
    assert result["intent_ok"] is False


# ─── 오류 케이스 ──────────────────────────────────────────────────────

def test_intent_raises_on_invalid_json() -> None:
    """LLM이 깨진 JSON을 반환 → ValueError."""
    client = _make_fake_client("not a json")
    with pytest.raises(ValueError, match="JSON 파싱 실패"):
        run_intent("input", client=client, model="gpt-4o-mini")


def test_intent_raises_on_missing_intent_ok() -> None:
    """intent_ok 필드 누락 → ValueError."""
    client = _make_fake_client(json.dumps({"category": "video_planning"}))
    with pytest.raises(ValueError, match="intent_ok"):
        run_intent("input", client=client, model="gpt-4o-mini")
