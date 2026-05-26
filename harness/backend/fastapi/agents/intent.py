"""Intent Agent — P-001 (Phase 1 Slice 2).

영상기획 요청인지 단순 분류한다. 영상기획 외 요청 (날씨, 잡담, 일반 코딩,
정보 검색, 광고 등) 은 차단한다.

호출 흐름:
  user_input(str) → gpt-4o-mini 1회 호출 (JSON mode) → dict 반환
  {"intent_ok": bool, "reason": str?, "category": "video_planning"?}

Note (prompt_registry mapping):
  본 Phase 1 구현은 인텐트 분류 1회 호출이라는 단일 책임을 가진다. 사용자 task
  spec 상 PROMPT_ID = "P-001" 로 둔다 (Phase 1 임시 매핑). 실제 prompt_registry의
  P-AUX-1(intent_filter) 정합은 Phase 2+ Discovery/Quick UX 도입 시 통합 예정.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from openai import OpenAI, OpenAIError

from ..config import get_settings

logger = logging.getLogger(__name__)


# ─── 시스템 프롬프트 (Intent only) ─────────────────────────────────────

SYSTEM_PROMPT = """당신은 영상기획 AI 에이전트의 의도 분류기이다.

판정 대상:
- 사용자의 입력이 "영상기획" 요청인지 여부.

허용 (intent_ok=true) 예시:
- 유튜브, 쇼츠, 릴스, 틱톡 등 영상 기획 요청
- 브랜드 영상, 홍보 영상, 채널 콘셉트 기획
- 영상의 후크 / 흐름 / 타겟 / 톤 설정 요청

거부 (intent_ok=false) 예시:
- 날씨, 시간 등 일상 정보 질문
- 일반 코딩, 디버깅 도움
- 잡담, 가벼운 대화
- 단순 정보 검색 (위키 / 뉴스 등)
- 광고 카피, SEO 키워드 등 영상기획과 직접 무관한 요청

응답 형식 (JSON 1개 객체만):
- 허용: {"intent_ok": true, "category": "video_planning"}
- 거부: {"intent_ok": false, "reason": "거부 사유 한 줄"}

자연어 머리말/꼬리말 금지. JSON 객체 1개만 반환한다.
"""


# ─── 호출 함수 ────────────────────────────────────────────────────────

def run_intent(
    user_input: str,
    *,
    client: OpenAI | None = None,
    model: str | None = None,
) -> dict[str, Any]:
    """Intent 분류 LLM 호출.

    Args:
        user_input: 사용자 요청 텍스트.
        client: OpenAI 클라이언트 (테스트 시 mock 주입).
        model: 사용 모델 (기본은 settings.openai_model_default).

    Returns:
        dict:
          - intent_ok (bool): 영상기획 요청 여부
          - reason (str): intent_ok=False 시 거부 사유
          - category (str): intent_ok=True 시 "video_planning"

    Raises:
        OpenAIError: API 호출 실패.
        ValueError: JSON 파싱 실패 또는 intent_ok 필드 누락.
    """
    settings = get_settings()
    _client = client or OpenAI(api_key=settings.openai_api_key)
    _model = model or settings.openai_model_default

    logger.info("intent call start model=%s input_len=%d", _model, len(user_input))

    try:
        response = _client.chat.completions.create(
            model=_model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_input},
            ],
            response_format={"type": "json_object"},
            temperature=0.3,  # 분류 일관성 (agent_io_contract §3.4)
            max_tokens=200,
        )
    except OpenAIError:
        logger.exception("Intent OpenAI API 호출 실패")
        raise

    raw_content = response.choices[0].message.content or "{}"
    logger.debug("intent raw response: %s", raw_content[:200])

    try:
        parsed: dict[str, Any] = json.loads(raw_content)
    except json.JSONDecodeError as e:
        raise ValueError(f"Intent LLM 응답 JSON 파싱 실패: {e}") from e

    if "intent_ok" not in parsed:
        raise ValueError("Intent LLM 응답에 intent_ok 필드 없음")

    return parsed


# ─── 메타 ────────────────────────────────────────────────────────────

PROMPT_ID = "P-001"
PROMPT_VERSION = "v1.0.0"
