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
    run_planning_multi_provider_3,
)
from backend.fastapi.llm.types import LLMResponse
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


# ─── Phase 11 B안 S2b-2a: run_planning_multi_provider_3 (gateway 기반) ─

def _plan_json(label: str) -> str:
    """slot 별 valid {"plan": {...}} JSON 문자열 (approach_label 다양화)."""
    return json.dumps(
        {
            "plan": {
                "name": f"plan-{label}",
                "concept": f"{label} 콘셉트",
                "hook": f"{label} 후크 — 첫 3초 시선 고정",
                "flow": [
                    {"beat_index": 0, "beat": "도입", "duration_sec": 3, "purpose": "관심"},
                    {"beat_index": 1, "beat": "전개", "duration_sec": 15, "purpose": "메시지"},
                ],
                "pros": "장점 1줄",
                "risks": "위험 1줄",
                "approach_label": label,
            }
        }
    )


class _FakeGateway:
    """alias 별로 서로 다른 LLMResponse 를 반환하는 fake gateway.

    complete(alias, messages, **kw) → LLMResponse(text=valid plan JSON, model_id=alias 별 상이).
    raise_on: 이 alias 호출 시 항상 예외 (retry 도 실패하도록).
    """

    def __init__(self, raise_on: str | None = None) -> None:
        self.raise_on = raise_on
        self.calls: list[str] = []
        # alias → (approach_label, model_id)
        self._map = {
            "plan_primary": ("narrative", "gpt-4o-mini"),
            "plan_secondary": ("informational", "claude-haiku-4-5"),
            "plan_tertiary": ("experiment", "gemini-3-flash"),
        }

    def complete(self, alias: str, messages: Any, **kwargs: Any) -> LLMResponse:
        self.calls.append(alias)
        if alias == self.raise_on:
            raise RuntimeError(f"fake gateway 강제 실패: {alias}")
        label, model_id = self._map[alias]
        return LLMResponse(text=_plan_json(label), model_id=model_id, alias=alias)


@pytest.mark.asyncio
async def test_multi_provider_3_returns_length_3_unique_labels() -> None:
    """fake gateway 주입 → length 3 + 각 {"plan": {...}} shape + approach_label unique."""
    gw = _FakeGateway()
    results = await run_planning_multi_provider_3("유튜브 쇼츠 기획", gateway=gw)

    assert len(results) == 3
    for r in results:
        assert "plan" in r
        assert isinstance(r["plan"], dict)
        # 내부 _model_id 누수 없음 (pop 되어야 함).
        assert "_model_id" not in r
    labels = [r["plan"]["approach_label"] for r in results]
    assert len(set(labels)) == 3, f"approach_label not unique: {labels}"
    # 3 alias 모두 정확히 1회씩 호출.
    assert set(gw.calls) == {"plan_primary", "plan_secondary", "plan_tertiary"}


@pytest.mark.asyncio
async def test_multi_provider_3_slot_failure_fallback_keeps_length_3() -> None:
    """한 슬롯 gateway.complete 예외 → retry 후에도 예외 → fallback 으로 대체, length 3 유지."""
    gw = _FakeGateway(raise_on="plan_secondary")
    results = await run_planning_multi_provider_3("테스트", gateway=gw)

    assert len(results) == 3
    # 실패 슬롯(secondary, index 1)은 fallback dict 로 대체.
    fallback = results[1]
    assert "plan" in fallback
    assert "graceful fallback" in fallback["plan"]["risks"]
    # plan_secondary 는 최초 1회 + retry 1회 = 2회 호출.
    assert gw.calls.count("plan_secondary") == 2


@pytest.mark.asyncio
async def test_multi_provider_3_clean_json_parses() -> None:
    """gateway 가 펜스 없는 clean JSON 을 주면(S2b-1 adapter 처리 전제) 파싱 성공."""
    gw = _FakeGateway()
    results = await run_planning_multi_provider_3("clean json 테스트", gateway=gw)
    assert len(results) == 3
    # primary slot 의 plan 이 정상 파싱되어 name 노출.
    assert results[0]["plan"]["name"] == "plan-narrative"


@pytest.mark.asyncio
async def test_multi_provider_3_with_rag_context() -> None:
    """rag_context 주입 시에도 정상 동작 (length 3)."""
    gw = _FakeGateway()
    rag = [{"title": "참고1", "snippet": "검증된 패턴 스니펫"}]
    results = await run_planning_multi_provider_3(
        "rag 주입 테스트", rag_context=rag, gateway=gw
    )
    assert len(results) == 3
    assert all("plan" in r for r in results)
