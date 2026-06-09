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
import time
from typing import Any

from openai import OpenAI, OpenAIError

from ..config import get_settings
from ..observability.agent_io_log import log_agent_io, usage_tokens

logger = logging.getLogger(__name__)


# ─── 시스템 프롬프트 (Intent only) ─────────────────────────────────────

SYSTEM_PROMPT = """당신은 영상기획 AI 에이전트의 의도 분류기이다.

★ 이 앱은 "영상기획 도구"다. 사용자가 입력칸에 적는 것은 대개 **만들 영상의 주제·아이디어**다.
따라서 "영상/쇼츠/유튜브" 같은 말이 없어도, 콘텐츠 주제면 **영상 아이디어로 간주해 기본 수용한다.**

판정 원칙:
- 기본값 = 수용(intent_ok=true). "이 주제로 영상을 만든다"로 해석 가능하면 수용.
- ★ 애매하면 수용한다 (사용자가 영상 주제로 적었다고 가정).
- 단순히 "정보성 주제"라는 이유로 거부하지 않는다 — 정보형/팁/리뷰 영상도 영상기획이다.

허용 (intent_ok=true):
- 유튜브/쇼츠/릴스/틱톡 영상 기획, 브랜드/홍보 영상, 후크/흐름/타겟/톤 설정
- ★ 주제만 적은 경우도 수용: "대학생활 팁", "자취 요리", "재테크 기초", "여행 브이로그",
  "운동 루틴", "제품 리뷰", "공부법" 등 — 전부 영상으로 만들 수 있는 콘텐츠 주제다.

거부 (intent_ok=false) — 영상과 **명백히 무관**한 것만:
- 날씨/시간/길찾기 등 개인비서 질의 ("오늘 날씨 어때")
- 코딩/디버깅/수학 풀이 등 작업 대행 ("이 코드 고쳐줘", "번역해줘")
- 잡담·인사 ("안녕", "심심해")

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

    _t0 = time.perf_counter()
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

    # ★ Phase 27 A8: 기본 경로 텔레메트리 (gated default-off + graceful).
    _i_in, _i_out = usage_tokens(getattr(response, "usage", None))
    log_agent_io(
        agent_name="intent",
        prompt_id=PROMPT_ID,
        prompt_version=PROMPT_VERSION,
        model=_model,
        input_tokens=_i_in,
        output_tokens=_i_out,
        latency_ms=int((time.perf_counter() - _t0) * 1000),
        success=True,
    )

    return parsed


# ─── 메타 ────────────────────────────────────────────────────────────

PROMPT_ID = "P-001"
# Phase 16: v1.0.0 → v1.1.0 (prompt-version-review, CC-021) — Intent 완화.
# 콘텐츠 토픽 기본 수용(애매하면 수용) + 명백한 도메인 밖(날씨/코딩/잡담)만 거부.
# 오반려(맨 토픽을 정보질문으로 차단) 해소. output schema 불변(intent_ok/reason).
PROMPT_VERSION = "v1.1.0"
