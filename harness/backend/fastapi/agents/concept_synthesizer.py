"""Phase 28 S3 — 컨셉 수렴기 (개인 PKM 신호 더미 → '내 컨셉' 표면화).

누적된 개인 PKM(pkm_entries, scope=personal)은 정확한 개별 신호이지만 그대로는
(a) 모순 공존 (b) confidence 평탄 → 중요도 미분화 (c) 종합/수렴 부재 라는 한계가 있다.
본 합성기는 1회 LLM 호출로 신호 더미를 다음으로 압축한다:
  - concept   : 사용자의 핵심 컨셉 한 줄 (반복·고신뢰 신호 종합)
  - pillars   : 핵심 기둥 2~4개 (정체성 축 — 중요도 분화)
  - conflicts : 서로 모순되는 신호 쌍 + 해소 제안 (모순 해소)

★ read-time: 영속하지 않는다 (NG12 계승 — 자동 쓰기 0).
★ graceful: key 없음 / 엔트리 없음 / 실패 / 파싱 실패 → enabled=False 빈 결과.
★ 중요도 분화: confidence/locked/반복(동일 content 재등장)을 LLM 입력에 함께 제공.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Optional

from openai import OpenAI, OpenAIError

from ..config import get_settings

logger = logging.getLogger(__name__)

# 합성 입력 상한 — 고신뢰 우선 정렬 후 상위 N개만 (토큰/비용 가드).
MAX_INPUT_ENTRIES = 24

CONCEPT_SYSTEM_PROMPT = """당신은 사용자의 영상기획 2nd brain의 '컨셉 수렴기'다.
누적된 개인 PKM 신호(선호 톤/문구, 지양 표현, 성공 패턴)를 종합해 사용자가
'쓸수록 드러나는 자기만의 컨셉'을 표면화한다. 영상을 제작하지 않는다.

각 신호는 [entry_type] content (conf=신뢰도, 🔒=사용자고정) 형식으로 주어진다.
신뢰도가 높거나 🔒(고정)이거나 반복된 신호일수록 더 핵심으로 취급한다.

반드시 JSON 으로만 답한다:
{
  "concept": "이 사람의 핵심 컨셉을 한 문장으로 (구체적·고유하게)",
  "pillars": [
    {"label": "정체성 축 이름(짧게)", "detail": "이 축을 뒷받침하는 신호 종합 한 줄"}
  ],
  "conflicts": [
    {"a": "신호 A", "b": "신호 A와 모순되는 신호 B", "note": "왜 모순인지 + 어느 쪽을 택할지 한 줄 제안"}
  ]
}
규칙:
- pillars 2~4개: 반복·고신뢰 신호를 묶은 핵심 축만 (지엽적 신호는 버린다).
- conflicts: 실제로 서로 어긋나는 쌍만(없으면 빈 배열). 추측·억지 모순 금지.
- 일반론·뻔한 말 금지. 이 사람만의 구체성을 살린다."""


def _entry_line(e: dict[str, Any]) -> str:
    et = str(e.get("entry_type", "?"))
    content = str(e.get("content", "")).strip()
    conf = float(e.get("confidence") or 0.5)
    lock = " 🔒" if e.get("is_user_locked") else ""
    return f"[{et}] {content} (conf={conf:.2f}{lock})"


def synthesize_concept(
    pkm_entries: list[dict[str, Any]],
    *,
    client: Optional[Any] = None,
    model: Optional[str] = None,
) -> dict[str, Any]:
    """개인 PKM 리스트 → {"enabled", "concept", "pillars", "conflicts", "based_on"}.

    graceful: entries 0 / key 없음 / 실패 → enabled=False 빈 결과(호출 0 또는 흐름 차단 X).
    """
    empty = {"enabled": False, "concept": "", "pillars": [], "conflicts": [], "based_on": 0}
    entries = [e for e in (pkm_entries or []) if str(e.get("content", "")).strip()]
    if not entries:
        return empty

    settings = get_settings()
    if not settings.openai_api_key:
        return empty
    _client = client or OpenAI(api_key=settings.openai_api_key)
    _model = model or settings.openai_model_default

    # 중요도 분화: 신뢰도 desc 정렬 후 상위 N개만 합성 입력으로 (locked 는 신뢰도 무관 우선).
    ranked = sorted(
        entries,
        key=lambda e: (bool(e.get("is_user_locked")), float(e.get("confidence") or 0.5)),
        reverse=True,
    )[:MAX_INPUT_ENTRIES]
    signal_block = "\n".join(_entry_line(e) for e in ranked)

    logger.info("concept synthesize start model=%s entries=%d", _model, len(ranked))
    try:
        resp = _client.chat.completions.create(
            model=_model,
            messages=[
                {"role": "system", "content": CONCEPT_SYSTEM_PROMPT},
                {"role": "user", "content": f"개인 PKM 신호:\n{signal_block}\n\nJSON으로만 종합해줘."},
            ],
            response_format={"type": "json_object"},
            temperature=0.4,
            max_tokens=700,
        )
    except OpenAIError as exc:  # graceful
        logger.warning("concept synthesize OpenAI 실패: %s (graceful)", exc.__class__.__name__)
        return empty
    except Exception as exc:  # noqa: BLE001 — 흐름 차단 금지
        logger.warning("concept synthesize 실패: %s (graceful)", exc.__class__.__name__)
        return empty

    raw = resp.choices[0].message.content or "{}"
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        logger.warning("concept synthesize JSON 파싱 실패 (graceful)")
        return empty

    concept = str(parsed.get("concept", "")).strip()
    pillars: list[dict[str, str]] = []
    for p in parsed.get("pillars") or []:
        if not isinstance(p, dict):
            continue
        label = str(p.get("label", "")).strip()
        if not label:
            continue
        pillars.append({"label": label, "detail": str(p.get("detail", "")).strip()})
    conflicts: list[dict[str, str]] = []
    for cf in parsed.get("conflicts") or []:
        if not isinstance(cf, dict):
            continue
        a = str(cf.get("a", "")).strip()
        b = str(cf.get("b", "")).strip()
        if not (a and b):
            continue
        conflicts.append({"a": a, "b": b, "note": str(cf.get("note", "")).strip()})

    logger.info(
        "concept synthesize done concept=%dchars pillars=%d conflicts=%d",
        len(concept), len(pillars), len(conflicts),
    )
    return {
        "enabled": True,
        "concept": concept,
        "pillars": pillars[:4],
        "conflicts": conflicts[:5],
        "based_on": len(entries),
    }


__all__ = ["synthesize_concept"]
