"""Intent + Planning 통합 LLM 호출 (Slice 1 임시).

Slice 2에서 intent.py / planning.py로 분리 예정.
prompt_id = "P-PHASE1-COMBINED" (api_contract / prompt_registry에는 미등록,
Phase 1 임시 ID — Slice 2에서 P-001 + P-006으로 정합).

호출 흐름:
  input(str) → gpt-4o-mini 1회 호출 (JSON mode) → dict 반환
"""

from __future__ import annotations

import json
import logging
from typing import Any

from openai import OpenAI, OpenAIError

from ..config import get_settings

logger = logging.getLogger(__name__)


# ─── 시스템 프롬프트 (Slice 1 임시 통합) ──────────────────────────────

SYSTEM_PROMPT = """당신은 영상기획 AI 에이전트다.

규칙:
1. 영상기획과 무관한 요청 (예: 날씨, 잡담, 코딩 도움 등) 은 거부한다.
   거부 시 JSON: {"intent_ok": false, "reason": "영상기획 외 요청"}

2. 영상기획 요청이면 기획안 1개를 JSON으로 반환한다.
   반환 형식:
   {
     "intent_ok": true,
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

금지:
- "혁신적", "최고의", "완벽한", "최선의", "최첨단" 같은 광고 표현 사용 금지
- 자연어 머리말/꼬리말 금지 (JSON 객체만 반환)
- 사실관계 검증 불가능한 통계 인용 금지

응답은 반드시 JSON 1개 객체로만 한다.
"""


# ─── 호출 함수 ────────────────────────────────────────────────────────

def run_intent_planning(
    user_input: str,
    *,
    client: OpenAI | None = None,
    model: str | None = None,
) -> dict[str, Any]:
    """Intent + Planning 통합 LLM 호출.

    Args:
        user_input: 사용자 요청 텍스트.
        client: OpenAI 클라이언트 (테스트 시 mock 주입).
        model: 사용 모델 (기본은 settings.openai_model_default).

    Returns:
        LLM 응답 dict. 키:
          - intent_ok (bool)
          - reason (str, intent_ok=False일 때)
          - plan (dict, intent_ok=True일 때)

    Raises:
        OpenAIError: API 호출 실패.
        ValueError: JSON 파싱 실패.
    """
    settings = get_settings()
    _client = client or OpenAI(api_key=settings.openai_api_key)
    _model = model or settings.openai_model_default

    logger.info("intent_planning call start model=%s input_len=%d", _model, len(user_input))

    try:
        response = _client.chat.completions.create(
            model=_model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_input},
            ],
            response_format={"type": "json_object"},
            temperature=0.7,
            max_tokens=1500,
        )
    except OpenAIError:
        logger.exception("OpenAI API 호출 실패")
        raise

    raw_content = response.choices[0].message.content or "{}"
    logger.debug("intent_planning raw response: %s", raw_content[:200])

    try:
        parsed: dict[str, Any] = json.loads(raw_content)
    except json.JSONDecodeError as e:
        raise ValueError(f"LLM 응답 JSON 파싱 실패: {e}") from e

    if "intent_ok" not in parsed:
        raise ValueError("LLM 응답에 intent_ok 필드 없음")

    return parsed


# ─── 메타 ────────────────────────────────────────────────────────────

PROMPT_ID = "P-PHASE1-COMBINED"
PROMPT_VERSION = "v0.1.0"  # Phase 1 Slice 1 임시
