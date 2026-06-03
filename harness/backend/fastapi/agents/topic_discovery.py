"""Topic Discovery Agent — P-AUX-3 (Phase 18 Slice S1).

주제를 모르는 사용자를 LLM 동적 스무고개(Akinator식)로 좁혀 후보 주제를 발굴한다.
LLM 1개 / 2모드(ask·finalize) — prompt_registry P-AUX-3 (v1.0.0) 정합.

두 모드:
  - ask:
      지금까지의 Q&A 상태를 받아 **다음 적응형 질문 1개 + 선택지 카드 2~4개**를 생성한다.
      주제 공간이 충분히 좁혀졌거나 질문이 많으면 종료(done) 신호를 낸다.
      ★ history 길이 ≥ MAX_QUESTIONS 이면 LLM 호출 없이 즉시 done (N고개 상한 강제).
  - finalize:
      Q&A 상태를 종합해 **후보 주제 3개**(각 {topic, tone, target, format, why_fit})를 합성한다.

호출 흐름 (둘 다 stateless agent — state 전체를 매 호출 주입):
  ask:      state(dict) → [상한 미달 시] gpt-4o-mini 1회(JSON mode) → dict
            {"mode":"ask"|"done", "question": str|null, "options": [str](2~4)|null, "rationale": str}
  finalize: state(dict) → gpt-4o-mini 1회(JSON mode) → dict
            {"candidates":[{topic,tone,target,format,why_fit} ×3]}

state 스키마:
  {
    "history": [{"question": str, "options": [str], "answer": str}, ...],
    "max_questions": int?   # 선택 — 없으면 MAX_QUESTIONS(기본 8) 사용
  }

비고:
  - 모델 기본 = settings.openai_model_default (workhorse, gpt-4o-mini). 비용/지연 통제(제안서 §9).
  - 자유입력 안전성(Intent 재사용/llm_security)은 후속 슬라이스 — S1 은 agent 코어만.
  - 파싱 실패 → ValueError (intent.py 패턴 계승). graceful 정규화(options 2~4, candidate 5필드 보장).
"""

from __future__ import annotations

import json
import logging
from typing import Any

from openai import OpenAI, OpenAIError

from ..config import get_settings

logger = logging.getLogger(__name__)


# ─── 상수 ──────────────────────────────────────────────────────────────

# N고개 상한 (제안서 §2 — 기본 6~8, 최대 12). ask 의 history 길이가 이 값 이상이면
# LLM 호출 없이 강제 done — 질문 루프 비용/지연 + "겉돌아 안 좁혀짐" 방어.
MAX_QUESTIONS = 8

# 선택지 카드 개수 범위 (제안서 §3 — 카드 2~4개 + 자유입력 혼합).
MIN_OPTIONS = 2
MAX_OPTIONS = 4

# 후보 주제 개수 (제안서 §4 — 후보 3개 × 브랜딩 방향).
N_CANDIDATES = 3

# 후보 주제가 반드시 가지는 5 필드.
CANDIDATE_FIELDS = ("topic", "tone", "target", "format", "why_fit")


# ─── 시스템 프롬프트 (ask 모드) ───────────────────────────────────────

ASK_SYSTEM_PROMPT = """당신은 영상기획 AI 에이전트의 주제 발굴기(Akinator식 스무고개)이다.

지금까지의 Q&A 히스토리를 보고, 사용자의 **영상 주제를 좁히는 다음 질문 1개 + 선택지 카드 2~4개**를
생성한다. 직전 답변에 따라 적응적으로 분기한다(아키네이터 핵심).

종료 판단:
- 주제 공간이 충분히 좁혀졌거나, 질문이 이미 많으면 mode="done" 을 반환한다(질문/선택지 없이).
- 아직 좁혀야 하면 mode="ask" 로 다음 질문과 선택지를 반환한다.

질문/선택지 규칙:
- 질문은 1개, 한 줄로 명확하게. 한국어.
- 선택지는 **2~4개** (서로 충분히 다른 방향). 자유입력은 프론트가 별도로 제공하므로 선택지에 넣지 않는다.
- 선택지는 짧은 명사형/구절(카드 라벨). 광고적 과장 표현 금지.

응답 형식 (JSON 1개 객체만):
- 질문 계속: {"mode": "ask", "question": "다음 질문 한 줄", "options": ["선택지1", "선택지2", "선택지3"], "rationale": "왜 이 질문인지 한 줄"}
- 종료:     {"mode": "done", "question": null, "options": null, "rationale": "충분히 좁혀진 이유 한 줄"}

자연어 머리말/꼬리말 금지. JSON 객체 1개만 반환한다.
"""


# ─── 시스템 프롬프트 (finalize 모드) ──────────────────────────────────

FINALIZE_SYSTEM_PROMPT = """당신은 영상기획 AI 에이전트의 주제 발굴기(Akinator식 스무고개)이다.

지금까지의 Q&A 히스토리를 종합해 사용자에게 맞는 **후보 영상 주제 3개**를 합성한다.
각 후보는 주제와 함께 브랜딩 방향(톤/타깃/포맷/왜 맞는지)을 갖는다.

각 후보 필드:
- topic:   주제 한 줄 (구체적, 광고 과장 금지)
- tone:    톤 한 줄 (예: "담백하고 솔직한 동네 가게 톤")
- target:  타깃 한 줄 (예: "동네 카페를 좋아하는 커피 애호가")
- format:  포맷 한 줄 (예: "정보형 30초 쇼츠")
- why_fit: 이 후보가 사용자에게 맞는 이유 한 줄 (Q&A 답변 근거를 반영)

규칙:
- 후보 3개는 서로 충분히 다른 접근으로 만든다.
- 모든 필드를 한국어로 채운다. 빈 값 금지.
- 광고적 과장 표현 금지.

응답 형식 (JSON 1개 객체만):
{"candidates": [
  {"topic": "...", "tone": "...", "target": "...", "format": "...", "why_fit": "..."},
  {"topic": "...", "tone": "...", "target": "...", "format": "...", "why_fit": "..."},
  {"topic": "...", "tone": "...", "target": "...", "format": "...", "why_fit": "..."}
]}

자연어 머리말/꼬리말 금지. JSON 객체 1개만 반환한다.
"""


# ─── 내부 헬퍼 ────────────────────────────────────────────────────────

def _resolve_cap(state: dict[str, Any]) -> int:
    """state.max_questions 를 정규화한 N고개 상한 반환 (없거나 비정상이면 MAX_QUESTIONS)."""
    raw = state.get("max_questions")
    if isinstance(raw, int) and raw > 0:
        return raw
    return MAX_QUESTIONS


def _history_text(state: dict[str, Any]) -> str:
    """state.history 를 LLM user prompt 용 텍스트로 직렬화 (graceful — 비정상 항목 skip)."""
    history = state.get("history")
    if not isinstance(history, list) or not history:
        return "(아직 답변 없음 — 첫 질문을 생성한다.)"
    lines: list[str] = []
    for i, turn in enumerate(history, start=1):
        if not isinstance(turn, dict):
            continue
        q = turn.get("question", "")
        a = turn.get("answer", "")
        lines.append(f"Q{i}. {q}\nA{i}. {a}")
    return "\n".join(lines) if lines else "(아직 답변 없음 — 첫 질문을 생성한다.)"


def _normalize_options(raw: Any) -> list[str]:
    """선택지를 2~4개 문자열 리스트로 정규화.

    - 비문자열/빈 문자열 제거.
    - MAX_OPTIONS(4) 초과 시 앞에서부터 truncate.
    (MIN_OPTIONS 미만 보충은 LLM 책임 — 부족하면 그대로 두고 호출측이 판단.)
    """
    if not isinstance(raw, list):
        return []
    cleaned = [str(o).strip() for o in raw if isinstance(o, str) and str(o).strip()]
    if len(cleaned) > MAX_OPTIONS:
        cleaned = cleaned[:MAX_OPTIONS]
    return cleaned


def _normalize_candidate(raw: Any) -> dict[str, str]:
    """후보 1개를 5필드 보장 dict 로 정규화 (누락 필드는 빈 문자열로 graceful 채움)."""
    src = raw if isinstance(raw, dict) else {}
    out: dict[str, str] = {}
    for field in CANDIDATE_FIELDS:
        val = src.get(field, "")
        out[field] = str(val).strip() if val is not None else ""
    return out


# ─── 호출 함수 (ask 모드) ─────────────────────────────────────────────

def run_topic_discovery_ask(
    state: dict[str, Any],
    *,
    client: OpenAI | None = None,
    model: str | None = None,
) -> dict[str, Any]:
    """주제 발굴 — 다음 질문 1개 + 선택지 2~4개 (또는 done 신호).

    ★ N고개 상한 강제: state.history 길이가 상한(state.max_questions 또는 MAX_QUESTIONS)
      이상이면 LLM 호출 없이 즉시 {"mode": "done", ...} 를 반환한다 (비용/루프 방어).

    Args:
        state: {"history": [{"question","options","answer"}...], "max_questions": int?}.
        client: OpenAI 클라이언트 (테스트 시 mock 주입).
        model: 사용 모델 (기본은 settings.openai_model_default — workhorse).

    Returns:
        dict:
          - mode (str): "ask" | "done"
          - question (str|None): mode="ask" 시 다음 질문
          - options (list[str]|None): mode="ask" 시 선택지 2~4개
          - rationale (str): 질문/종료 사유 한 줄

    Raises:
        OpenAIError: API 호출 실패.
        ValueError: JSON 파싱 실패 또는 mode 필드 누락.
    """
    history = state.get("history") if isinstance(state.get("history"), list) else []
    cap = _resolve_cap(state)

    # ── N고개 상한 강제 (LLM 호출 없이 즉시 done) ──
    if len(history) >= cap:
        logger.info("topic_discovery ask cap reached: history=%d cap=%d", len(history), cap)
        return {
            "mode": "done",
            "question": None,
            "options": None,
            "rationale": f"질문 상한({cap}고개)에 도달해 주제 발굴을 마칩니다.",
        }

    settings = get_settings()
    _client = client or OpenAI(api_key=settings.openai_api_key)
    _model = model or settings.openai_model_default

    user_prompt = (
        f"지금까지의 Q&A:\n{_history_text(state)}\n\n"
        f"(현재 질문 수: {len(history)} / 상한: {cap})\n"
        "위를 바탕으로 다음 질문 1개 + 선택지 2~4개를 만들거나, 충분하면 종료해줘. JSON으로만."
    )

    logger.info("topic_discovery ask start model=%s history=%d", _model, len(history))

    try:
        response = _client.chat.completions.create(
            model=_model,
            messages=[
                {"role": "system", "content": ASK_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.3,  # 적응형 분기 일관성 (비결정성 방어 — 제안서 §9)
            max_tokens=400,
        )
    except OpenAIError:
        logger.exception("topic_discovery ask OpenAI API 호출 실패")
        raise

    raw_content = response.choices[0].message.content or "{}"
    logger.debug("topic_discovery ask raw response: %s", raw_content[:300])

    try:
        parsed: dict[str, Any] = json.loads(raw_content)
    except json.JSONDecodeError as e:
        raise ValueError(f"topic_discovery ask LLM 응답 JSON 파싱 실패: {e}") from e

    if "mode" not in parsed:
        raise ValueError("topic_discovery ask LLM 응답에 mode 필드 없음")

    mode = parsed.get("mode")
    rationale = str(parsed.get("rationale", "") or "")

    if mode == "done":
        return {"mode": "done", "question": None, "options": None, "rationale": rationale}

    # mode == "ask" (또는 그 외 → ask 로 취급하되 정규화).
    options = _normalize_options(parsed.get("options"))
    question = parsed.get("question")
    return {
        "mode": "ask",
        "question": str(question).strip() if question else None,
        "options": options,
        "rationale": rationale,
    }


# ─── 호출 함수 (finalize 모드) ────────────────────────────────────────

def run_topic_discovery_finalize(
    state: dict[str, Any],
    *,
    client: OpenAI | None = None,
    model: str | None = None,
) -> dict[str, Any]:
    """주제 발굴 종합 — 후보 주제 3개(각 {topic,tone,target,format,why_fit}) 합성.

    Args:
        state: {"history": [{"question","options","answer"}...]}.
        client: OpenAI 클라이언트 (테스트 시 mock 주입).
        model: 사용 모델 (기본은 settings.openai_model_default — workhorse).

    Returns:
        dict:
          - candidates (list[dict]): 각 {topic, tone, target, format, why_fit} 5필드 보장.
            (LLM 이 3개 미만/초과 반환해도 graceful — 5필드는 항상 채워짐.)

    Raises:
        OpenAIError: API 호출 실패.
        ValueError: JSON 파싱 실패 또는 candidates 필드 누락.
    """
    settings = get_settings()
    _client = client or OpenAI(api_key=settings.openai_api_key)
    _model = model or settings.openai_model_default

    user_prompt = (
        f"지금까지의 Q&A:\n{_history_text(state)}\n\n"
        f"위를 종합해 후보 영상 주제 {N_CANDIDATES}개(각 topic/tone/target/format/why_fit)를 만들어줘. JSON으로만."
    )

    logger.info("topic_discovery finalize start model=%s", _model)

    try:
        response = _client.chat.completions.create(
            model=_model,
            messages=[
                {"role": "system", "content": FINALIZE_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.4,  # 후보 다양성 (제안서 §4 — 서로 다른 3개)
            max_tokens=900,
        )
    except OpenAIError:
        logger.exception("topic_discovery finalize OpenAI API 호출 실패")
        raise

    raw_content = response.choices[0].message.content or "{}"
    logger.debug("topic_discovery finalize raw response: %s", raw_content[:400])

    try:
        parsed: dict[str, Any] = json.loads(raw_content)
    except json.JSONDecodeError as e:
        raise ValueError(f"topic_discovery finalize LLM 응답 JSON 파싱 실패: {e}") from e

    if "candidates" not in parsed:
        raise ValueError("topic_discovery finalize LLM 응답에 candidates 필드 없음")

    raw_candidates = parsed.get("candidates")
    if not isinstance(raw_candidates, list):
        raise ValueError("topic_discovery finalize candidates 가 리스트가 아님")

    # 각 후보를 5필드 보장 dict 로 정규화 (graceful — 누락 필드 빈 문자열).
    candidates = [_normalize_candidate(c) for c in raw_candidates]
    return {"candidates": candidates}


# ─── 메타 ────────────────────────────────────────────────────────────

# prompt_registry.md §10 P-AUX-3 (topic_discovery) 정합 — 단일 출처 SoT.
# Phase 18 S1 신규 (additive). ask/finalize 2모드 공유 1 prompt_id.
PROMPT_ID = "P-AUX-3"
PROMPT_VERSION = "v1.0.0"

# 구현 종류 / 모델 메타 (다른 agent 메타와 일관 — 문서·디버그용).
IMPL_KIND = "llm"
DEFAULT_MODEL_SETTING = "openai_model_default"  # workhorse (gpt-4o-mini)
