"""Topic Discovery Agent (P-AUX-3) 단위 테스트 — Phase 18 Slice S1.

검증 대상 (mock LLM, CI-safe — 실 API 호출 0):
  - ask: 유효 JSON → question + options(2~4) 파싱.
  - ask: options 5개 반환 → 4개로 truncate.
  - ask: done 신호 → mode="done", question/options None.
  - ask cap: history 길이 ≥ MAX_QUESTIONS → LLM 미호출 + mode="done".
  - finalize: candidates 3개, 각 {topic,tone,target,format,why_fit} 존재.
  - finalize: 후보 필드 누락 → graceful (5필드 보장, 빈 문자열).
  - 파싱 실패(깨진 JSON) → ValueError (ask / finalize).
  - mode/candidates 필드 누락 → ValueError.
  - meta: PROMPT_ID/PROMPT_VERSION 단언.
"""

from __future__ import annotations

import json
from unittest.mock import MagicMock

import pytest

from backend.fastapi.agents.topic_discovery import (
    CANDIDATE_FIELDS,
    MAX_QUESTIONS,
    PROMPT_ID,
    PROMPT_VERSION,
    run_topic_discovery_ask,
    run_topic_discovery_finalize,
)


# ─── Helpers (intent.py _make_fake_client 패턴 재사용) ─────────────────

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

def test_topic_discovery_prompt_meta() -> None:
    """P-AUX-3 / v1.0.0 매핑 확인 (Phase 18 S1 신규)."""
    assert PROMPT_ID == "P-AUX-3"
    assert PROMPT_VERSION == "v1.0.0"


# ─── ask: 다음 질문 + 선택지 ──────────────────────────────────────────

def test_ask_returns_question_and_options() -> None:
    """유효 JSON → mode=ask, question + options(2~4) 파싱."""
    client = _make_fake_client(
        json.dumps(
            {
                "mode": "ask",
                "question": "어떤 분야의 영상을 만들고 싶나요?",
                "options": ["일상/브이로그", "정보/교육", "리뷰/하울"],
                "rationale": "주제 대분류부터 좁힌다",
            }
        )
    )
    result = run_topic_discovery_ask({"history": []}, client=client, model="gpt-4o-mini")
    assert result["mode"] == "ask"
    assert result["question"]
    assert isinstance(result["options"], list)
    assert 2 <= len(result["options"]) <= 4
    assert result["options"] == ["일상/브이로그", "정보/교육", "리뷰/하울"]


def test_ask_truncates_options_to_four() -> None:
    """options 5개 반환 → 앞 4개로 truncate (MAX_OPTIONS)."""
    client = _make_fake_client(
        json.dumps(
            {
                "mode": "ask",
                "question": "톤은 어떤 쪽인가요?",
                "options": ["A", "B", "C", "D", "E"],
                "rationale": "톤을 좁힌다",
            }
        )
    )
    result = run_topic_discovery_ask({"history": []}, client=client, model="gpt-4o-mini")
    assert result["options"] == ["A", "B", "C", "D"]
    assert len(result["options"]) == 4


def test_ask_done_signal() -> None:
    """LLM 이 종료 신호 → mode=done, question/options None."""
    client = _make_fake_client(
        json.dumps(
            {
                "mode": "done",
                "question": None,
                "options": None,
                "rationale": "주제가 충분히 좁혀졌다",
            }
        )
    )
    result = run_topic_discovery_ask(
        {"history": [{"question": "q", "options": [], "answer": "a"}]},
        client=client,
        model="gpt-4o-mini",
    )
    assert result["mode"] == "done"
    assert result["question"] is None
    assert result["options"] is None


# ─── ask cap: N고개 상한 강제 ─────────────────────────────────────────

def test_ask_cap_forces_done_without_llm_call() -> None:
    """history 길이 ≥ MAX_QUESTIONS → LLM 미호출 + mode=done (상한 강제)."""
    client = _make_fake_client("이건 호출되면 안 되는 응답")
    history = [
        {"question": f"q{i}", "options": [], "answer": f"a{i}"}
        for i in range(MAX_QUESTIONS)
    ]
    result = run_topic_discovery_ask({"history": history}, client=client, model="gpt-4o-mini")
    assert result["mode"] == "done"
    assert result["question"] is None
    assert result["options"] is None
    # ★ 상한 도달 시 LLM 호출 0 (비용/루프 방어).
    client.chat.completions.create.assert_not_called()


def test_ask_cap_respects_custom_max_questions() -> None:
    """state.max_questions override → 그 값 이상이면 done (LLM 미호출)."""
    client = _make_fake_client("호출되면 안 됨")
    history = [{"question": "q1", "options": [], "answer": "a1"}]
    result = run_topic_discovery_ask(
        {"history": history, "max_questions": 1}, client=client, model="gpt-4o-mini"
    )
    assert result["mode"] == "done"
    client.chat.completions.create.assert_not_called()


# ─── finalize: 후보 3개 × 브랜딩 방향 ─────────────────────────────────

def test_finalize_returns_three_candidates_with_fields() -> None:
    """mock → candidates 3개, 각 {topic,tone,target,format,why_fit} 존재."""
    cands = [
        {
            "topic": f"주제 {i}",
            "tone": f"톤 {i}",
            "target": f"타깃 {i}",
            "format": f"정보형 30초 쇼츠 {i}",
            "why_fit": f"이유 {i}",
        }
        for i in range(3)
    ]
    client = _make_fake_client(json.dumps({"candidates": cands}))
    result = run_topic_discovery_finalize(
        {"history": [{"question": "q", "options": [], "answer": "a"}]},
        client=client,
        model="gpt-4o-mini",
    )
    assert len(result["candidates"]) == 3
    for c in result["candidates"]:
        for field in CANDIDATE_FIELDS:
            assert field in c
            assert c[field]


def test_finalize_graceful_fills_missing_fields() -> None:
    """후보 일부 필드 누락 → 5필드 보장 (graceful, 누락은 빈 문자열)."""
    client = _make_fake_client(
        json.dumps({"candidates": [{"topic": "동네 카페 비하인드"}]})
    )
    result = run_topic_discovery_finalize({"history": []}, client=client, model="gpt-4o-mini")
    assert len(result["candidates"]) == 1
    c = result["candidates"][0]
    for field in CANDIDATE_FIELDS:
        assert field in c  # 5필드 모두 존재
    assert c["topic"] == "동네 카페 비하인드"
    assert c["tone"] == ""  # 누락 → 빈 문자열


# ─── 오류 케이스 ──────────────────────────────────────────────────────

def test_ask_raises_on_invalid_json() -> None:
    """ask: LLM 이 깨진 JSON 반환 → ValueError."""
    client = _make_fake_client("not a json")
    with pytest.raises(ValueError, match="JSON 파싱 실패"):
        run_topic_discovery_ask({"history": []}, client=client, model="gpt-4o-mini")


def test_ask_raises_on_missing_mode() -> None:
    """ask: mode 필드 누락 → ValueError."""
    client = _make_fake_client(json.dumps({"question": "q", "options": ["a", "b"]}))
    with pytest.raises(ValueError, match="mode"):
        run_topic_discovery_ask({"history": []}, client=client, model="gpt-4o-mini")


def test_finalize_raises_on_invalid_json() -> None:
    """finalize: LLM 이 깨진 JSON 반환 → ValueError."""
    client = _make_fake_client("{broken")
    with pytest.raises(ValueError, match="JSON 파싱 실패"):
        run_topic_discovery_finalize({"history": []}, client=client, model="gpt-4o-mini")


def test_finalize_raises_on_missing_candidates() -> None:
    """finalize: candidates 필드 누락 → ValueError."""
    client = _make_fake_client(json.dumps({"foo": "bar"}))
    with pytest.raises(ValueError, match="candidates"):
        run_topic_discovery_finalize({"history": []}, client=client, model="gpt-4o-mini")
