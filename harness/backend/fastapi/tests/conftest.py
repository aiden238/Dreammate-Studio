"""pytest fixtures — OPENAI_API_KEY 없이도 테스트 통과시키기 위한 mock 주입.

Slice 2 변경:
  - mock_openai_intent_ok / mock_openai_intent_block (Slice 1 통합 호출용) 제거
  - mock_intent_ok / mock_intent_block / mock_planning_ok 분리
  - mock_pipeline_ok: 라우터 e2e용 (Intent allow + Planning success) 조합 fixture

Slice 3 변경:
  - mock_critic_ok / mock_critic_flagged 추가 (P-007 Critic Agent)
  - mock_pipeline_ok가 critic도 포함하도록 확장
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


# Critic의 router fake는 target_plan_id를 plan dict로부터 가져오도록 한다.
# (run_critic은 plan dict를 첫 인자로 받으므로 router fake에서도 동일 시그니처 모방)

_CRITIC_OK_SCORES: dict[str, int] = {
    "intent_fit": 4,
    "target_clarity": 3,
    "hook_strength": 4,
    "message_clarity": 4,
    "structure": 4,
    "feasibility": 4,
    "brand_consistency": 5,
    "differentiation": 3,
}


def _make_critic_ok_payload(plan: dict[str, Any]) -> dict[str, Any]:
    """approve verdict의 critic 결과 (router용)."""
    target_id = str(plan.get("plan_id") or "")
    scores = dict(_CRITIC_OK_SCORES)
    avg = round(sum(scores.values()) / len(scores), 4)
    return {
        "target_plan_id": target_id,
        "scores": scores,
        "reasons": {k: "양호" for k in scores},
        "suggestions": {k: "추가 다듬기 권장" for k in scores},
        "overall_score_avg": avg,
        "overall_verdict": "approve",
        "blocking_issues": [],
        "revise_round": 0,
    }


_CRITIC_FLAGGED_SCORES: dict[str, int] = {
    "intent_fit": 3,
    "target_clarity": 1,  # FC-002 풍 (타겟 모호)
    "hook_strength": 1,  # FC-001 풍 (인사 hook)
    "message_clarity": 3,
    "structure": 3,
    "feasibility": 3,
    "brand_consistency": 4,
    "differentiation": 2,
}


def _make_critic_flagged_payload(plan: dict[str, Any]) -> dict[str, Any]:
    """revise verdict (2개 차원 < 2) — FC-001/002 시드 패턴 모방."""
    target_id = str(plan.get("plan_id") or "")
    scores = dict(_CRITIC_FLAGGED_SCORES)
    avg = round(sum(scores.values()) / len(scores), 4)
    return {
        "target_plan_id": target_id,
        "scores": scores,
        "reasons": {
            "intent_fit": "의도와 일치",
            "target_clarity": "타겟이 광범위 — 1명으로 좁혀야 함",
            "hook_strength": "'안녕하세요' 형 hook = 스크롤 유발",
            "message_clarity": "메시지 한 줄 정리 미흡",
            "structure": "도입-전개-마무리 자연스러움",
            "feasibility": "1인 스마트폰 가능",
            "brand_consistency": "광고 표현 없음",
            "differentiation": "흔한 접근",
        },
        "suggestions": {
            "intent_fit": "그대로 유지",
            "target_clarity": "예: '30대 후반 야근 사무직' 으로 축소",
            "hook_strength": "질문형 / 충격적 사실 hook 권장",
            "message_clarity": "한 줄 메시지 정의 추가",
            "structure": "비트별 시간 분배 재검토",
            "feasibility": "추가 변경 불요",
            "brand_consistency": "유지",
            "differentiation": "독자적 관점 추가",
        },
        "overall_score_avg": avg,
        "overall_verdict": "revise",
        "blocking_issues": ["타겟 페르소나 1명으로 축소 필요", "hook 재작성 필요"],
        "revise_round": 0,
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


# ─── Critic 단독 mock (Slice 3) ────────────────────────────────────────

@pytest.fixture
def mock_critic_ok(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    """Critic Agent가 approve verdict + 8 차원 정상 점수를 반환하는 mock."""

    def fake_call(plan: dict[str, Any], *args: Any, **kwargs: Any) -> dict[str, Any]:
        return _make_critic_ok_payload(plan)

    monkeypatch.setattr("backend.fastapi.routers.generate.run_critic", fake_call)
    return MagicMock()


@pytest.fixture
def mock_critic_flagged(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    """Critic Agent가 revise verdict (FC-001/002 시드 패턴 모방) 을 반환하는 mock."""

    def fake_call(plan: dict[str, Any], *args: Any, **kwargs: Any) -> dict[str, Any]:
        return _make_critic_flagged_payload(plan)

    monkeypatch.setattr("backend.fastapi.routers.generate.run_critic", fake_call)
    return MagicMock()


# ─── 파이프라인 (Intent allow + Planning success + Critic approve) ─────

@pytest.fixture
def mock_pipeline_ok(
    mock_intent_ok: MagicMock,
    mock_planning_ok: MagicMock,
    mock_critic_ok: MagicMock,
) -> MagicMock:
    """e2e 정상 경로 fixture — router 응답 200 검증용 (Slice 3: Critic 포함)."""
    return MagicMock()
