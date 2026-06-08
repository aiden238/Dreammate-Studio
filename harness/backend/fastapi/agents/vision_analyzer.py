"""Phase 29 A — 레퍼런스 이미지 분석기 (멀티모달 → 영상기획 키워드).

첨부 이미지(레퍼런스: 무드보드/경쟁 영상 썸네일/화면 캡처 등)를 gpt-4o-mini 비전으로
분석해 ① summary(생성 user_input 에 프리펜드 = 레퍼런스 반영, A1) ② keywords(PKM 적재, A2)를 만든다.

★ graceful: 이미지 0 / 실패 / 파싱 실패 → {summary:"", keywords:[]} (생성 흐름 절대 차단 X).
★ additive: 이미지 미첨부 시 호출 0 → 기존 동작 byte-identical.
★ 영상 제작 X — 레퍼런스를 '기획 관점'으로만 해석(제품 정체성 정합).
"""

from __future__ import annotations

import json
import logging
from typing import Any, Optional

from openai import OpenAI, OpenAIError

from ..config import get_settings

logger = logging.getLogger(__name__)

MAX_IMAGES = 4

# entry_type 은 pkm_entries enum 정합 (brand_memory_entries 와 동일 5종).
_VALID_ENTRY_TYPES = {
    "preferred_tone",
    "avoid_phrase",
    "preferred_phrase",
    "success_pattern",
    "rejection_pattern",
}

VISION_SYSTEM_PROMPT = """당신은 영상기획 AI 에이전트의 레퍼런스 분석기다.
사용자가 첨부한 이미지(무드보드 / 경쟁 영상 썸네일 / 화면 캡처 / 참고 사진 등)를
'영상기획 관점'으로 해석한다. 영상을 제작하지 않는다 — 톤·스타일·구성·메시지만 읽는다.
반드시 JSON 으로만 답한다:
{
  "summary": "이 레퍼런스의 톤·스타일·구성·분위기를 2~3문장으로",
  "keywords": [
    {"entry_type": "preferred_tone|preferred_phrase|avoid_phrase|success_pattern", "content": "기획에 쓸 구체적 한 줄"}
  ]
}
규칙: keywords 3~5개, 영상기획에 실제로 쓸 선호/스타일만. 일반론·무의미·이미지 묘사만 하기 금지."""


def analyze_references(
    images: list[str],
    *,
    client: Optional[Any] = None,
    model: Optional[str] = None,
) -> dict[str, Any]:
    """첨부 이미지 → {"summary": str, "keywords": [{entry_type, content}]}. graceful."""
    if not images:
        return {"summary": "", "keywords": []}

    settings = get_settings()
    if not settings.openai_api_key:
        return {"summary": "", "keywords": []}
    _client = client or OpenAI(api_key=settings.openai_api_key)
    _model = model or settings.openai_model_default  # gpt-4o-mini = 비전 지원

    content: list[dict[str, Any]] = [
        {"type": "text", "text": "이 레퍼런스를 영상기획 관점에서 분석해줘. JSON으로만."}
    ]
    for url in images[:MAX_IMAGES]:
        if isinstance(url, str) and url:
            content.append({"type": "image_url", "image_url": {"url": url}})

    logger.info("vision analyze start model=%s images=%d", _model, len(images))
    try:
        resp = _client.chat.completions.create(
            model=_model,
            messages=[
                {"role": "system", "content": VISION_SYSTEM_PROMPT},
                {"role": "user", "content": content},
            ],
            response_format={"type": "json_object"},
            temperature=0.3,
            max_tokens=600,
        )
    except OpenAIError as exc:  # graceful — 생성 흐름 차단 X
        logger.warning("vision analyze OpenAI 실패: %s (graceful)", exc.__class__.__name__)
        return {"summary": "", "keywords": []}
    except Exception as exc:  # noqa: BLE001 — 어떤 예외도 흐름 차단 금지
        logger.warning("vision analyze 실패: %s (graceful)", exc.__class__.__name__)
        return {"summary": "", "keywords": []}

    raw = resp.choices[0].message.content or "{}"
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        logger.warning("vision analyze JSON 파싱 실패 (graceful)")
        return {"summary": "", "keywords": []}

    summary = str(parsed.get("summary", "")).strip()
    raw_kws = parsed.get("keywords") or []
    keywords: list[dict[str, str]] = []
    for k in raw_kws:
        if not isinstance(k, dict):
            continue
        c = str(k.get("content", "")).strip()
        et = str(k.get("entry_type", "preferred_phrase"))
        if not c:
            continue
        if et not in _VALID_ENTRY_TYPES:
            et = "preferred_phrase"
        keywords.append({"entry_type": et, "content": c})

    logger.info("vision analyze done summary=%dchars keywords=%d", len(summary), len(keywords))
    return {"summary": summary, "keywords": keywords[:5]}


__all__ = ["analyze_references"]
