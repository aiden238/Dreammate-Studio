"""Rewriter Agent (P-008) — Phase 4.5 Slice 2 + Phase 6 Slice 2 (ADR-019).

Critic verdict가 `revise`일 때 plan의 weakness를 반영하여 plan을 1회 개선한다.

설계 원칙:
- 인라인 prompt (NG8: Phase 7+ 정식 prompt 카탈로그 등록 전까지)
- graceful: LLM 실패 시 원본 plan을 반환 + ``_rewriter_warning`` 마커 추가
- retry 0 (Phase 4.5 1차 — Critic revise loop 자체가 최대 2회 시도하므로 단일 호출 retry 불필요)
- Planning agent (P-006) 의 sync OpenAI 패턴과 호환: async 함수지만 OpenAI client는
  AsyncOpenAI 또는 호환 mock 사용. 테스트는 client를 주입한다.

Phase 6 Slice 2 강화 (ADR-019, P-008 v1.0.0 → v1.1.0):
- `RewriterInput` / `RewriterOutput` Pydantic 모델 도입 (typing 검증 + frontend type mirror용 export).
- 기존 dict 반환 패턴은 호환 유지 (routers/plans.py 변경 X — 회귀 0).
- graceful failure 정책 명시: LLM 실패 / non-dict 응답 → 원본 plan + `_rewriter_warning` 마커.

호출 흐름:
  plan(dict) + critic_verdict(dict) → gpt-4o-mini async 호출 (JSON mode)
  → 개선된 plan dict 반환 (원본 키 구조 유지)
"""
from __future__ import annotations

import json
import logging
from typing import Any

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


# ─── Phase 6 Slice 2: Pydantic 모델 (ADR-019, P-008 v1.1.0) ──────────

class RewriterInput(BaseModel):
    """Rewriter 입력 envelope (Phase 6 ADR-019, agent_io_contract §6 v1.1.0).

    기존 `run_rewriter(plan, critic_verdict, ...)` 호출 패턴은 호환 유지.
    이 모델은 typing 검증 + frontend type mirror 용도 (실 함수는 dict 인자 그대로 받음).
    """

    plan: dict[str, Any] = Field(..., description="원본 plan dict (P-006 구조)")
    critic_verdict: dict[str, Any] = Field(
        ...,
        description="Critic 평가 결과 dict (overall_verdict / blocking_issues / suggestions 등)",
    )
    model: str = Field(default="gpt-4o-mini", description="사용할 LLM 모델명")


class RewriterOutput(BaseModel):
    """Rewriter 출력 envelope (Phase 6 ADR-019, agent_io_contract §6 v1.1.0).

    실제 `run_rewriter` 는 dict 반환을 유지 (routers/plans.py 호환). 이 모델은 typing
    검증 + frontend type mirror 용도.

    Fields:
      - revised_plan: dict[str, Any] — 개선된 plan (P-006 구조 + revised meta keys).
      - _rewriter_model: Optional[str] — 사용된 LLM 모델 (메타 마커).
      - _rewriter_warning: Optional[str] — graceful 실패 시 마커 ("rewriter_failed: <ErrorClass>").
    """

    revised_plan: dict[str, Any] = Field(..., description="개선된 plan dict")
    rewriter_model: str | None = Field(
        default=None,
        alias="_rewriter_model",
        description="사용된 LLM 모델 (메타 마커).",
    )
    rewriter_warning: str | None = Field(
        default=None,
        alias="_rewriter_warning",
        description=(
            "graceful 실패 시 마커. 'rewriter_failed: <ErrorClass>' 형식. "
            "이 마커가 있으면 revised_plan 은 원본 plan 과 동일 (LLM 호출 실패)."
        ),
    )

    model_config = {"populate_by_name": True}


# ─── 시스템 프롬프트 (Rewriter only, 인라인 — NG7) ────────────────────

REWRITER_SYSTEM_PROMPT = """당신은 영상기획 AI 에이전트의 Rewriter입니다.
주어진 영상기획안(plan)과 Critic 평가(verdict)를 받아, verdict의 weakness 항목을 반영하여 plan을 1회 개선합니다.

규칙:
1. plan의 핵심 구조(name, concept, hook, flow, pros, risks, approach_label 등)는 유지하되 weakness 지적 사항만 보완한다.
2. 광고적 표현 금지 ("최고의", "혁신적인", "완벽한", "최선의", "최첨단", "획기적", "1위", "압도적").
3. 검증 불가능한 통계 인용 금지.
4. 출력은 입력 plan과 동일한 JSON 구조 (자연어 머리말/꼬리말 없이 JSON 객체만).
5. weakness 항목이 모호하면 가장 명확한 1~2개만 반영한다.
6. flow는 최소 2개, 최대 8개 비트.
"""


REWRITER_USER_TEMPLATE = """[원본 plan]
{plan_json}

[Critic verdict]
{verdict_json}

[지시]
verdict의 blocking_issues 와 suggestions 를 우선적으로 반영하여 plan을 개선한 JSON을 반환하세요.
JSON 객체만 출력하고 다른 설명은 포함하지 마세요.
"""


# ─── 호출 함수 ────────────────────────────────────────────────────────

async def run_rewriter(
    plan: dict[str, Any],
    critic_verdict: dict[str, Any],
    *,
    model: str = "gpt-4o-mini",
    client: Any | None = None,
) -> dict[str, Any]:
    """Critic verdict의 weakness 항목을 반영하여 plan을 1회 개선.

    Args:
        plan: 원본 plan dict (Plan.model_dump() 또는 raw plan dict).
        critic_verdict: Critic 평가 결과 dict (overall_verdict, blocking_issues, suggestions 등).
        model: 사용할 LLM 모델명 (기본 gpt-4o-mini).
        client: AsyncOpenAI 호환 client. None 이면 새로 생성 (테스트는 주입).

    Returns:
        개선된 plan dict. LLM 실패 또는 형식 오류 시 원본 plan을 반환하되
        ``_rewriter_warning`` 키 추가 (graceful 정책).
    """
    if client is None:
        # local import to avoid hard dependency at module import time
        from openai import AsyncOpenAI  # type: ignore

        client = AsyncOpenAI()

    user_prompt = REWRITER_USER_TEMPLATE.format(
        plan_json=json.dumps(plan, ensure_ascii=False, indent=2),
        verdict_json=json.dumps(critic_verdict, ensure_ascii=False, indent=2),
    )

    logger.info(
        "rewriter call start model=%s plan_keys=%d verdict_action=%s",
        model,
        len(plan),
        critic_verdict.get("overall_verdict") or critic_verdict.get("action"),
    )

    try:
        completion = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": REWRITER_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.4,
            max_tokens=1500,
        )
        content = completion.choices[0].message.content or "{}"
        revised = json.loads(content)
        if not isinstance(revised, dict):
            raise ValueError("Rewriter LLM returned non-object JSON")

        # 메타 보존 (원본 plan_id / option_index 유지 — 라우터가 schema 재구성 시 활용).
        for preserve_key in ("plan_id", "option_index"):
            if preserve_key in plan and preserve_key not in revised:
                revised[preserve_key] = plan[preserve_key]
        revised.setdefault("_rewriter_model", model)
        return revised
    except Exception as exc:  # graceful — LLM 실패 시 원본 보존
        logger.warning("rewriter_failed: %s", exc.__class__.__name__, exc_info=exc)
        fallback = dict(plan)
        fallback["_rewriter_warning"] = f"rewriter_failed: {exc.__class__.__name__}"
        return fallback


# ─── 메타 ────────────────────────────────────────────────────────────

PROMPT_ID = "P-008"
# Phase 6 ADR-019: v1.0.0 → v1.1.0 (Pydantic 모델 정식 등록 + graceful 정책 명시).
# semver: minor bump (breaking change 없음, dict 반환 호환 유지).
PROMPT_VERSION = "v1.1.0"
