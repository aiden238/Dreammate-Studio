"""Planning Agent — P-006 (Phase 1 Slice 2).

승인된 영상기획 요청에 대해 단일 plan_candidate를 생성한다.
Phase 1 deviation: contract는 plans 3개, 본 Phase는 1개만 (validation.warnings로 추적).

호출 흐름:
  user_input(str) → gpt-4o-mini 1회 호출 (JSON mode) → dict 반환
  {"plan": {name, concept, hook, flow[...], pros, risks, approach_label}}
"""

from __future__ import annotations

import json
import logging
from typing import Any

from openai import OpenAI, OpenAIError

from ..config import get_settings

logger = logging.getLogger(__name__)


# ─── 시스템 프롬프트 (Planning only) ──────────────────────────────────

SYSTEM_PROMPT = """당신은 영상기획 AI 에이전트의 기획안 생성기이다.

사용자의 영상기획 요청을 받아 영상기획안 1개를 JSON으로 반환한다.
(Phase 1 임시 — 정식은 3개 다양한 접근.)

반환 형식 (JSON 1개 객체만):
{
  "plan": {
    "name": "10~16자 이내 기획안 이름",
    "concept": "1~2줄 콘셉트",
    "hook": "20~60자 영상 첫 3초 후크",
    "flow": [
      {"beat_index": 0, "beat": "도입 비트 설명", "duration_sec": 3, "purpose": "관심 유발"},
      {"beat_index": 1, "beat": "전개 비트 설명", "duration_sec": 15, "purpose": "핵심 메시지"},
      {"beat_index": 2, "beat": "마무리 비트 설명", "duration_sec": 12, "purpose": "CTA"}
    ],
    "pros": "이 기획안의 장점 1줄",
    "risks": "주의해야 할 위험 1줄",
    "approach_label": "narrative | informational | empathy | experiment | review | other 중 1개"
  }
}

규칙:
- 자연어 머리말/꼬리말 금지 (JSON 객체만 반환)
- "혁신적", "최고의", "완벽한", "최선의", "최첨단" 같은 광고 표현 사용 금지
- 사실관계 검증 불가능한 통계 인용 금지
- flow는 최소 2개, 최대 8개 비트
- 각 비트의 duration_sec 합이 영상 길이에 부합
- 후킹은 광고 카피처럼 작성하지 말 것
"""


# ─── 호출 함수 ────────────────────────────────────────────────────────

def run_planning(
    user_input: str,
    *,
    client: OpenAI | None = None,
    model: str | None = None,
) -> dict[str, Any]:
    """Planning 생성 LLM 호출.

    Args:
        user_input: 사용자 요청 텍스트 (Intent 통과 후).
        client: OpenAI 클라이언트 (테스트 시 mock 주입).
        model: 사용 모델 (기본은 settings.openai_model_default).

    Returns:
        dict:
          - plan (dict): output_schema §8.1 Plan body (단일 plan, Phase 1 deviation)

    Raises:
        OpenAIError: API 호출 실패.
        ValueError: JSON 파싱 실패 또는 plan 필드 누락.
    """
    settings = get_settings()
    _client = client or OpenAI(api_key=settings.openai_api_key)
    _model = model or settings.openai_model_default

    logger.info("planning call start model=%s input_len=%d", _model, len(user_input))

    try:
        response = _client.chat.completions.create(
            model=_model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_input},
            ],
            response_format={"type": "json_object"},
            temperature=0.7,  # 다양성 (agent_io_contract §4.4)
            max_tokens=1500,
        )
    except OpenAIError:
        logger.exception("Planning OpenAI API 호출 실패")
        raise

    raw_content = response.choices[0].message.content or "{}"
    logger.debug("planning raw response: %s", raw_content[:200])

    try:
        parsed: dict[str, Any] = json.loads(raw_content)
    except json.JSONDecodeError as e:
        raise ValueError(f"Planning LLM 응답 JSON 파싱 실패: {e}") from e

    if "plan" not in parsed:
        raise ValueError("Planning LLM 응답에 plan 필드 없음")

    return parsed


# ─── 메타 ────────────────────────────────────────────────────────────

PROMPT_ID = "P-006"
PROMPT_VERSION = "v1.0.0"
