"""Planning Agent (P-006) 단위 테스트 — Phase 1 Slice 2.

검증 대상:
  - run_planning() 가 OpenAI 클라이언트 mock으로 동작
  - 정상 응답 → plan dict 반환 + Plan Pydantic 모델 검증 통과
  - 응답 schema 준수 (name / hook / flow / approach_label 등)
  - plan 필드 누락 → ValueError
  - JSON 파싱 실패 → ValueError
"""

from __future__ import annotations

import json
from typing import Any
from unittest.mock import MagicMock

import pytest

from backend.fastapi.agents.planning import (
    PROMPT_ID,
    PROMPT_VERSION,
    run_planning,
)
from backend.fastapi.schemas.output import Plan, PlanFlowBeat


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


_VALID_PLAN_RESPONSE: dict[str, Any] = {
    "plan": {
        "name": "첫 영상 시작하기",
        "concept": "초보 유튜버를 위한 채널 첫 영상 콘셉트",
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
    }
}


# ─── 메타 ─────────────────────────────────────────────────────────────

def test_planning_prompt_meta() -> None:
    """P-006 / v1.0.0 매핑 확인."""
    assert PROMPT_ID == "P-006"
    assert PROMPT_VERSION == "v1.0.0"


# ─── 정상 plan 생성 ───────────────────────────────────────────────────

def test_planning_returns_plan_dict() -> None:
    """LLM 정상 응답 → plan dict 반환."""
    client = _make_fake_client(json.dumps(_VALID_PLAN_RESPONSE))
    result = run_planning(
        "유튜브 채널 첫 영상 기획해줘", client=client, model="gpt-4o-mini"
    )
    assert "plan" in result
    plan = result["plan"]
    assert plan["name"] == "첫 영상 시작하기"
    assert plan["approach_label"] == "narrative"
    assert isinstance(plan["flow"], list)
    assert len(plan["flow"]) == 3


# ─── Plan schema 준수 (Pydantic 검증) ────────────────────────────────

def test_planning_output_passes_pydantic_schema() -> None:
    """LLM 응답이 output_schema Plan 모델로 검증 통과."""
    client = _make_fake_client(json.dumps(_VALID_PLAN_RESPONSE))
    result = run_planning("쇼츠 기획", client=client, model="gpt-4o-mini")
    plan_raw = result["plan"]

    # Plan 모델 직렬화 시도 (router에서 동일 흐름)
    plan = Plan(
        plan_id="11111111-1111-1111-1111-111111111111",
        option_index=0,
        name=plan_raw["name"],
        concept=plan_raw["concept"],
        hook=plan_raw["hook"],
        flow=[
            PlanFlowBeat(**b)
            for b in plan_raw["flow"]
        ],
        pros=plan_raw["pros"],
        risks=plan_raw["risks"],
        approach_label=plan_raw["approach_label"],
        rag_used=[],
    )
    assert plan.name == "첫 영상 시작하기"
    assert plan.approach_label == "narrative"
    assert len(plan.flow) == 3
    assert plan.flow[0].duration_sec == 3


# ─── 오류 케이스 ──────────────────────────────────────────────────────

def test_planning_raises_on_invalid_json() -> None:
    """깨진 JSON → ValueError."""
    client = _make_fake_client("not a json")
    with pytest.raises(ValueError, match="JSON 파싱 실패"):
        run_planning("input", client=client, model="gpt-4o-mini")


def test_planning_raises_on_missing_plan_field() -> None:
    """plan 필드 누락 → ValueError."""
    client = _make_fake_client(json.dumps({"intent_ok": True}))
    with pytest.raises(ValueError, match="plan"):
        run_planning("input", client=client, model="gpt-4o-mini")
