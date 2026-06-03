"""Planning Agent — P-006 (Phase 1 Slice 2 + Slice 4 RAG context + Phase 4 Slice 2 3-plan parallel).

승인된 영상기획 요청에 대해 plan_candidate(s)를 생성한다.

Phase 1 (run_planning): 1 plan (deviation from contract 3 plans).
Phase 4 Slice 2 (run_planning_parallel_3): 3 plans parallel (asyncio.gather) + multi-model interface.
  - 사용자 결정 4-b: 3 parallel async call + 향후 모델 추가 가능 구조.
  - approach_label 분기 (narrative + informational + experiment) — 각 호출마다 다른 hint.
  - parallel error graceful (retry 1회 → fallback dict).
  - approach_label unique 강제 (중복 시 fallback label 사용).

호출 흐름:
  Phase 1: user_input(str) → gpt-4o-mini 1회 호출 (JSON mode) → dict 반환
           {"plan": {name, concept, hook, flow[...], pros, risks, approach_label}}
  Phase 4: user_input(str) → 3 parallel gpt-4o-mini async 호출 → list[dict] 반환 (length 3)

Slice 4 (Phase 1) 추가:
  - run_planning(user_input, rag_context=[...]) — RAG 참고 자료를 시스템 프롬프트에 주입.
  - rag_context=None 또는 빈 배열이면 Slice 2 동작과 동일 (backward compat).
"""

from __future__ import annotations

import asyncio
import copy
import json
import logging
from typing import Any, Sequence

from openai import OpenAI, OpenAIError

from ..config import effective_output_mode, get_settings

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


# ─── Phase 13 S2 (P-006 v1.1.0): rich SYSTEM_PROMPT ──────────────────
# ★ gated/additive: 기존 compact SYSTEM_PROMPT(v1.0.0)는 보존(flag OFF 경로).
#   본 rich 프롬프트는 rich_output_enabled=True(S3 wiring) 경로에서만 사용된다.
#   S2 는 이 상수/헬퍼를 제공·검증만 하고, 어느 곳에서도 호출하지 않는다(behavior-preserving).
#   출력은 compact 와 동일한 {"plan": {...}} envelope + S1 의 rich Optional 슬롯(전부 선택).
#   ★ 제품 경계: 확장본도 "기획 브리프"(촬영·편집 가이드)이지 완성 대본/영상 제작이 아니다.
RICH_SYSTEM_PROMPT = """당신은 영상기획 AI 에이전트의 기획안 생성기이다.

사용자의 영상기획 요청을 받아 **상세 영상기획 브리프** 1개를 JSON으로 반환한다.
이것은 "기획 브리프"(촬영·편집 가이드)이지 완성 대본·영상 제작물이 아니다.

반환 형식 (JSON 1개 객체만):
{
  "plan": {
    "name": "10~16자 이내 기획안 이름",
    "concept": "1~2줄 콘셉트",
    "hook": "20~60자 영상 첫 3초 후크",
    "hook_variants": ["대안 후크 1", "대안 후크 2"],
    "target_audience": "타깃 시청자 (예: 자취 2~3년차 20대)",
    "tone": "톤·무드 (예: 담백하고 솔직한)",
    "flow": [
      {
        "beat_index": 0,
        "beat": "비트 라벨/설명",
        "duration_sec": 3,
        "purpose": "이 비트의 목적",
        "visual": "화면/구도/연출 묘사 (카메라·앵글 등 beat 보다 구체적)",
        "dialogue": "내레이션/대사 (있으면)",
        "caption": "자막 텍스트 (있으면)"
      }
    ],
    "shots": ["B-roll/추가 샷 아이디어 1", "샷 2"],
    "thumbnail": "썸네일 컨셉 (문구 + 비주얼 방향)",
    "title_candidates": ["제목 후보 1", "제목 후보 2", "제목 후보 3"],
    "cta": "영상 마무리 Call-to-action",
    "references": ["참고할 만한 유형/사례 (그대로 복제 금지)"],
    "length_variants": ["30초 컷 요약", "60초 컷 요약"],
    "pros": "이 기획안의 장점 1줄",
    "risks": "주의해야 할 위험 1줄",
    "approach_label": "narrative | informational | empathy | experiment | review | other 중 1개"
  }
}

규칙:
- 자연어 머리말/꼬리말 금지 (JSON 객체만 반환)
- "혁신적", "최고의", "완벽한", "최선의", "최첨단" 같은 광고 표현 사용 금지
- 사실관계 검증 불가능한 통계 인용 금지
- flow는 최소 2개, 최대 8개 비트, 각 비트의 duration_sec 합이 영상 길이에 부합
- 각 비트에 visual(화면)·dialogue(대사)·caption(자막)을 가능한 한 채운다 (해당 없으면 생략 가능)
- hook_variants 는 최대 2개, title_candidates 는 3~5개, references 는 최대 5개
- 후킹·제목·CTA는 광고 카피처럼 과장하지 말 것
- 완성 대본 전체를 쓰지 말 것 — 어디까지나 촬영·편집을 위한 "브리프" 수준
"""


# ─── Phase 15 S2 (P-006 v1.2.0): director SYSTEM_PROMPT ──────────────
# ★ gated/additive: compact(v1.0.0)·rich(v1.1.0) 프롬프트 보존. director 는
#   output_mode=director(S3 wiring) 경로에서만 사용 — S2 는 상수/헬퍼 제공·검증만(런타임 미연결).
#   rich 12슬롯 + director 3슬롯(hook_system/retention_architecture/scene_breakdown). LLM-only.
#   ★ 제품 경계: scene_breakdown 은 "기획 의도/감정/리텐션 근거"이지 촬영 지시·완성 대본 아님.
DIRECTOR_SYSTEM_PROMPT = """당신은 영상기획 AI 에이전트의 기획안 생성기이다.

사용자의 영상기획 요청을 받아 **연출·리텐션까지 설계한 상세 기획 브리프** 1개를 JSON으로 반환한다.
이것은 "기획 브리프"(촬영·편집·연출 가이드)이지 완성 대본·영상 제작물이 아니다.

★★ 이 모드(director)의 핵심은 다음 3개 필드다 — rich 필드만 채우고 끝내지 말고 **반드시 모두 구체적으로 채운다**:
   - hook_system: 첫 후크 + 영상 중반 재후크(re-hook) 지점 (최소 2개 항목)
   - retention_architecture: 이탈 예상 구간 + 호기심 갭/페이싱 장치 (빈 문자열 금지)
   - scene_breakdown: 씬 2개 이상, 각 씬에 scene_intent/viewer_emotion/retention_device/why_this_works
   이 3개가 비면 director 출력으로 무효다.

반환 형식 (JSON 1개 객체만 — rich 12슬롯 + director 3슬롯):
{
  "plan": {
    "name": "10~16자 이내 기획안 이름",
    "concept": "1~2줄 콘셉트",
    "hook": "20~60자 영상 첫 3초 후크",
    "hook_variants": ["대안 후크 1", "대안 후크 2"],
    "target_audience": "타깃 시청자",
    "tone": "톤·무드",
    "flow": [
      {"beat_index": 0, "beat": "비트 라벨", "duration_sec": 3, "purpose": "목적",
       "visual": "화면/구도/연출", "dialogue": "내레이션/대사", "caption": "자막"}
    ],
    "shots": ["B-roll/추가 샷"],
    "thumbnail": "썸네일 컨셉",
    "title_candidates": ["제목 후보 (3~5)"],
    "cta": "마무리 Call-to-action",
    "references": ["참고 유형/사례 (복제 금지)"],
    "length_variants": ["30초 컷", "60초 컷"],

    "hook_system": ["첫 후크 설계", "영상 중반 재후크(re-hook) 지점 (예: @0:15)"],
    "retention_architecture": "리텐션 구조 — 이탈 예상 구간 + 호기심 갭/페이싱 장치 (1~2문단)",
    "scene_breakdown": [
      {
        "scene_intent": "이 씬의 기획 의도",
        "viewer_emotion": "시청자가 느끼길 의도하는 감정",
        "retention_device": "이탈 방지/호기심 유지 장치",
        "why_this_works": "작동 근거 (일반론 금지 — 패턴/맥락 기반)",
        "fallback_scene": "약할 때 대안 씬 (없으면 생략)"
      }
    ],

    "pros": "장점 1줄",
    "risks": "위험 1줄",
    "approach_label": "narrative | informational | empathy | experiment | review | other 중 1개"
  }
}

규칙:
- 자연어 머리말/꼬리말 금지 (JSON 객체만 반환)
- 광고 과장 표현("혁신적/최고의/완벽한/최선의/최첨단") + 조회수/바이럴 보장 표현 금지
- 사실관계 검증 불가능한 통계 인용 금지
- flow는 최소 2개~최대 8개, duration_sec 합이 영상 길이에 부합
- hook_system: 첫 후크 + 재후크 지점 설계 (단발 hook_variants 보다 상위 — 영상 흐름상 어디서 다시 잡을지)
- retention_architecture: 어디서 이탈이 예상되고 어떻게 막을지 구조적으로
- scene_breakdown: 각 씬의 의도/감정/리텐션장치/근거 (why_this_works 는 막연한 일반론 금지)
- ★ 완성 대본 전체 작성 금지 — scene_breakdown 도 "기획 의도/연출 방향"이지 대사 전문(全文)·촬영 지시가 아니다 (브리프 수준)
"""


# ─── 호출 함수 ────────────────────────────────────────────────────────

def _format_rag_context(rag_context: Sequence[Any]) -> str:
    """RAG references → 시스템 프롬프트용 "참고 자료" 섹션 문자열.

    RAGReference Pydantic model 또는 dict 둘 다 허용 (backward compat).
    빈 입력은 빈 문자열 반환 (호출자가 system prompt 합성 분기에 사용).
    """
    if not rag_context:
        return ""

    lines: list[str] = ["", "참고 자료 (출처가 검증된 영상기획 패턴):"]
    for i, ref in enumerate(rag_context, start=1):
        if hasattr(ref, "model_dump"):
            ref_dict: dict[str, Any] = ref.model_dump()
        elif isinstance(ref, dict):
            ref_dict = ref
        else:
            continue

        title = str(ref_dict.get("title") or "(제목 없음)")
        snippet = str(ref_dict.get("snippet") or "")[:300]
        lines.append(f"[{i}] {title}\n    {snippet}")

    lines.append(
        "이 참고 자료는 영상기획 패턴 학습용이다. 그대로 복제하지 말고 "
        "사용자 요청에 맞게 새 plan을 생성한다."
    )
    return "\n".join(lines)


def run_planning(
    user_input: str,
    *,
    rag_context: Sequence[Any] | None = None,
    client: OpenAI | None = None,
    model: str | None = None,
) -> dict[str, Any]:
    """Planning 생성 LLM 호출.

    Args:
        user_input: 사용자 요청 텍스트 (Intent 통과 후).
        rag_context: RAGReference 모델 또는 dict 의 시퀀스 (선택, Slice 4 추가).
                     비어있거나 None이면 Slice 2 동작과 동일 (backward compat).
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

    rag_block = _format_rag_context(rag_context or [])
    # Phase 15 S3 (gated): output_mode 별 프롬프트 (compact/rich/director). ★ compact/rich byte-identical
    #   (effective_output_mode 가 rich_output_enabled=True→"rich" 매핑 — Phase 13/14 동작 보존).
    _mode = effective_output_mode(settings)
    base = (
        DIRECTOR_SYSTEM_PROMPT
        if _mode == "director"
        else RICH_SYSTEM_PROMPT
        if _mode == "rich"
        else SYSTEM_PROMPT
    )
    system_prompt = base + (("\n" + rag_block) if rag_block else "")

    logger.info(
        "planning call start model=%s input_len=%d rag_refs=%d",
        _model,
        len(user_input),
        len(rag_context or []),
    )

    try:
        response = _client.chat.completions.create(
            model=_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input},
            ],
            response_format={"type": "json_object"},
            temperature=0.7,  # 다양성 (agent_io_contract §4.4)
            # Phase 15 S6: director 출력(rich 12 + director 3 + scene 리스트)은 커서 1500 절단 →
            #   director 슬롯(뒤쪽) 누락. director 만 상향(compact/rich 1500 불변 = byte-identical).
            max_tokens=3500 if _mode == "director" else 1500,
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


# ─── Phase 4 Slice 2: 3-plan parallel + multi-model 인터페이스 ────────

# approach_label hint per parallel call.
# 3 plans 각각 다른 접근으로 작성되도록 system prompt에 hint 주입 (사용자 결정 4-b).
_APPROACH_HINTS: tuple[str, ...] = (
    "narrative — 스토리텔링 중심, 감정 연결",
    "informational — 명확한 정보 전달, 전문성 강조",
    "experiment — 실험적 / 비교 / 챌린지 / 새 접근",
)

# Phase 4 Slice 2 메타 (P-006 동일, parallel 3-call extension).
PARALLEL_3_PROMPT_ID = "P-006"
PARALLEL_3_PROMPT_VERSION = "v1.0.0"


def _build_system_prompt_with_hint(approach_hint: str) -> str:
    """기존 SYSTEM_PROMPT (1-plan용)에 approach_hint 추가.

    Phase 4 Slice 2: parallel 3 호출 시 각 plan이 다른 approach_label 갖도록 hint 추가.
    """
    addendum = (
        f"\n\n[Phase 4 Slice 2 approach hint — 이 plan은 다음 방향으로 작성]:\n"
        f"{approach_hint}\n"
        f"\napproach_label 필드에 위 hint에 맞는 값을 정확히 선택하세요 "
        f"(narrative / informational / empathy / experiment / review / other)."
    )
    return SYSTEM_PROMPT + addendum


def _build_rich_system_prompt_with_hint(approach_hint: str) -> str:
    """Phase 13 S2: rich SYSTEM_PROMPT(v1.1.0)에 approach_hint 추가.

    _build_system_prompt_with_hint 의 rich 대응 — 3-plan 다양성(슬롯별 hint)을
    rich 프롬프트에 주입한다. ★ rich_output_enabled=True(S3 wiring) 경로 전용.
    S2 는 capability 만 제공 — 호출은 S3.
    """
    addendum = (
        f"\n\n[approach hint — 이 plan은 다음 방향으로 작성]:\n"
        f"{approach_hint}\n"
        f"\napproach_label 필드에 위 hint에 맞는 값을 정확히 선택하세요 "
        f"(narrative / informational / empathy / experiment / review / other)."
    )
    return RICH_SYSTEM_PROMPT + addendum


def _build_director_system_prompt_with_hint(approach_hint: str) -> str:
    """Phase 15 S2: director SYSTEM_PROMPT(v1.2.0)에 approach_hint 추가.

    _build_rich_system_prompt_with_hint 의 director 대응. ★ output_mode=director(S3) 경로 전용.
    S2 는 capability 만 제공 — 호출은 S3.
    """
    addendum = (
        f"\n\n[approach hint — 이 plan은 다음 방향으로 작성]:\n"
        f"{approach_hint}\n"
        f"\napproach_label 필드에 위 hint에 맞는 값을 정확히 선택하세요 "
        f"(narrative / informational / empathy / experiment / review / other)."
    )
    return DIRECTOR_SYSTEM_PROMPT + addendum


async def _run_planning_single(
    user_input: str,
    *,
    rag_context: Sequence[Any] | None = None,
    model: str,
    approach_hint: str,
    client: OpenAI | None = None,
) -> dict[str, Any]:
    """Single planning call with custom model + approach hint (async).

    Phase 4 Slice 2 (multi-model 인터페이스):
      - OpenAI 동기 client를 thread pool에서 실행 (asyncio 호환 + 기존 코드 호환).
      - approach_hint를 system prompt에 추가 → 3개 plan의 다양성 확보.

    Raises:
        OpenAIError / ValueError / JSONDecodeError (호출자가 graceful 처리).
    """
    settings = get_settings()
    _client = client or OpenAI(api_key=settings.openai_api_key)

    rag_block = _format_rag_context(rag_context or [])
    # Phase 15 S3 (gated): output_mode 별 hint 프롬프트 (compact/rich/director). compact/rich byte-identical.
    _mode = effective_output_mode(settings)
    base_prompt = (
        _build_director_system_prompt_with_hint(approach_hint)
        if _mode == "director"
        else _build_rich_system_prompt_with_hint(approach_hint)
        if _mode == "rich"
        else _build_system_prompt_with_hint(approach_hint)
    )
    system_prompt = base_prompt + (("\n" + rag_block) if rag_block else "")

    logger.info(
        "planning(parallel) call start model=%s input_len=%d rag_refs=%d hint=%s",
        model,
        len(user_input),
        len(rag_context or []),
        approach_hint.split(" ", 1)[0],
    )

    def _sync_call() -> dict[str, Any]:
        response = _client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input},
            ],
            response_format={"type": "json_object"},
            temperature=0.8,  # 약간 높여 다양성 확보 (3 parallel)
            max_tokens=1500,
        )
        raw = response.choices[0].message.content or "{}"
        parsed = json.loads(raw)
        if "plan" not in parsed:
            raise ValueError("Planning(parallel) response missing 'plan' key")
        return parsed

    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _sync_call)


def _fallback_plan_dict(index: int) -> dict[str, Any]:
    """graceful fallback plan — retry 실패 시에도 length 3 보장.

    Phase 4 Slice 2: parallel error graceful 정책 (사용자 응답 차단 금지).
    """
    return {
        "plan": {
            "name": f"(생성 실패 {index + 1})",
            "concept": "(LLM 응답 실패 — graceful fallback)",
            "hook": "재시도 권장 — 잠시 후 다시 시도해주세요",
            "flow": [
                {
                    "beat_index": 0,
                    "beat": "—",
                    "duration_sec": 1,
                    "purpose": "—",
                },
                {
                    "beat_index": 1,
                    "beat": "—",
                    "duration_sec": 1,
                    "purpose": "—",
                },
            ],
            "pros": "",
            "risks": "graceful fallback (Phase 4 Slice 2)",
            "approach_label": "other",
        }
    }


def _enforce_unique_approach_labels(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """3개 plan의 approach_label이 unique하도록 강제 (중복 시 fallback label 사용).

    Phase 4 Slice 2 (사용자 결정 4-b): unique 보장.
    강한 정합은 Phase 5+ prompt 개선에서 (현재는 fallback label 적용).
    """
    if len(results) < 3:
        return results

    fallback_pool: list[str] = [
        "narrative", "informational", "experiment", "empathy", "review", "other",
    ]
    seen: set[str] = set()
    for i, r in enumerate(results):
        plan = r.get("plan", {}) if isinstance(r, dict) else {}
        label = plan.get("approach_label", "other")
        if label in seen:
            for candidate in fallback_pool:
                if candidate not in seen:
                    plan["approach_label"] = candidate
                    label = candidate
                    break
        seen.add(label)
    return results


async def run_planning_parallel_3(
    user_input: str,
    *,
    rag_context: Sequence[Any] | None = None,
    models: list[str] | None = None,
    client: OpenAI | None = None,
) -> list[dict[str, Any]]:
    """Phase 4 Slice 2 — 3 parallel async planning calls with multi-model interface.

    사용자 결정 4-b 반영:
      - 3 parallel (asyncio.gather)
      - models: list[str] of 3 (default config.openai_models_for_3plan_list)
      - 향후 multi-provider 확장 가능 (Anthropic / Google 등 Phase 21+).

    Args:
        user_input: 사용자 입력 텍스트 (Intent 통과 후).
        rag_context: RAGReference 또는 dict 시퀀스 (Slice 4 호환). None 또는 빈 배열 허용.
        models: 3개 모델 list (None이면 settings.openai_models_for_3plan_list 사용).
        client: OpenAI client (테스트 mock 주입).

    Returns:
        list of 3 planning dicts. 각 dict은 {"plan": {...}} 형식.
        파싱 실패 시 graceful fallback dict 포함 (length 3 보장).

    Raises:
        ValueError: 모델 list가 3개가 아닐 때 (settings padding/truncating으로 통상 raise X).
    """
    settings = get_settings()
    _models = models if models is not None else settings.openai_models_for_3plan_list
    if len(_models) != 3:
        raise ValueError(f"Expected 3 models, got {len(_models)}")

    rag_context_list = list(rag_context or [])

    # 3 parallel async calls.
    tasks = [
        _run_planning_single(
            user_input,
            rag_context=rag_context_list,
            model=_models[i],
            approach_hint=_APPROACH_HINTS[i],
            client=client,
        )
        for i in range(3)
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)

    # 일부 실패 시 retry 1회 (parallel error graceful).
    final_results: list[dict[str, Any]] = []
    for i, r in enumerate(results):
        if isinstance(r, BaseException):
            logger.warning(
                "planning %d/3 failed (%s), retrying once", i + 1, type(r).__name__,
            )
            try:
                retry = await _run_planning_single(
                    user_input,
                    rag_context=rag_context_list,
                    model=_models[i],
                    approach_hint=_APPROACH_HINTS[i],
                    client=client,
                )
                final_results.append(retry)
            except Exception as e2:
                logger.warning(
                    "planning %d/3 retry also failed: %s — using fallback dict",
                    i + 1,
                    e2,
                )
                final_results.append(_fallback_plan_dict(i))
        else:
            # deepcopy 효과 (호출자가 mutate 해도 다른 결과에 영향 없도록).
            final_results.append(copy.deepcopy(r))

    # approach_label unique 강제 (사용자 결정 4-b).
    final_results = _enforce_unique_approach_labels(final_results)

    return final_results


# ─── Phase 11 B안 Slice S2b-2a: 3-provider 다양성 (gateway 기반, additive) ─

# 3-plan 다양성 alias 슬롯 (제안서 §18.B / aliases.py).
#   슬롯 i ↔ _APPROACH_HINTS[i] 1:1 (run_planning_parallel_3 와 동일 매핑).
#   plan_primary→GPT(gpt-4o-mini) / plan_secondary→Claude(haiku) / plan_tertiary→Gemini(flash).
_MULTI_PROVIDER_PLAN_ALIASES: tuple[str, ...] = (
    "plan_primary",
    "plan_secondary",
    "plan_tertiary",
)


async def _run_planning_single_via_gateway(
    user_input: str,
    *,
    rag_context_list: list[Any],
    alias: str,
    approach_hint: str,
    gateway: Any,
) -> dict[str, Any]:
    """gateway alias 기반 단일 planning 호출 (async). 슬롯 1개 = alias 1회 호출.

    Phase 11 B안 S2b-2a:
      - system prompt 합성은 _run_planning_single 과 동일(_build_system_prompt_with_hint +
        _format_rag_context block).
      - messages 는 LLMMessage(role/content) 시퀀스 (cross_validation.py 동작 본뜸).
      - gateway.complete 는 sync → run_in_executor 로 async 화 (gather 병렬 전제).
      - resp.text → json.loads → "plan" 키 필수(없으면 ValueError) → {"plan": {...}}.

    Raises:
        Exception: gateway/파싱 실패 (호출자가 retry/fallback graceful 처리).
    """
    from ..llm.types import LLMMessage  # 지연 import (provider-neutral 타입)

    rag_block = _format_rag_context(rag_context_list)
    # Phase 13 S3 (gated, 일관성): rich_output_enabled ON 이면 rich hint 프롬프트.
    #   ★ multi_provider 는 별 게이트(multi_provider_plans_enabled, default OFF)라
    #     이 함수는 통상 호출되지 않는다 — settings 는 late get_settings() 로 조회.
    _mode = effective_output_mode(get_settings())
    if _mode == "director":
        base_prompt = _build_director_system_prompt_with_hint(approach_hint)
    elif _mode == "rich":
        base_prompt = _build_rich_system_prompt_with_hint(approach_hint)
    else:
        base_prompt = _build_system_prompt_with_hint(approach_hint)
    system_prompt = base_prompt + (("\n" + rag_block) if rag_block else "")

    messages = [
        LLMMessage(role="system", content=system_prompt),
        LLMMessage(role="user", content=user_input),
    ]

    logger.info(
        "planning(multi-provider) call start alias=%s input_len=%d rag_refs=%d hint=%s",
        alias,
        len(user_input),
        len(rag_context_list),
        approach_hint.split(" ", 1)[0],
    )

    def _sync_call() -> Any:
        return gateway.complete(
            alias,
            messages,
            temperature=0.8,  # 다양성 (3 슬롯 — run_planning_parallel_3 와 동일 기조)
            max_tokens=1500,
            json_mode=True,
        )

    loop = asyncio.get_event_loop()
    resp = await loop.run_in_executor(None, _sync_call)

    raw = (resp.text or "").strip()
    parsed = json.loads(raw)
    if "plan" not in parsed:
        raise ValueError("Planning(multi-provider) response missing 'plan' key")
    return {"plan": parsed["plan"], "_model_id": resp.model_id}


async def run_planning_multi_provider_3(
    user_input: str,
    *,
    rag_context: Sequence[Any] | None = None,
    gateway: Any = None,
) -> list[dict[str, Any]]:
    """Phase 11 B안 §18.B — gateway 기반 3-provider 다양성 3-plan 생성 (gated, additive).

    ★★ behavior-preserving: 본 함수는 **신설**이며 아직 **아무 곳에서도 호출되지 않는다**
    (orchestrator 분기는 후속 S2b-2b). config `multi_provider_plans_enabled`(default OFF)
    가 활성 게이트 — 호출측이 결정한다(본 함수는 flag 강제 X). 기존 OpenAI 3-call 경로
    (run_planning_parallel_3)는 무변경.

    3안을 서로 다른 provider 로 생성하여 단일-provider 편향을 줄인다:
      plan_primary   → GPT(gpt-4o-mini)   [슬롯0: narrative hint]
      plan_secondary → Claude(haiku)      [슬롯1: informational hint]
      plan_tertiary  → Gemini(flash)      [슬롯2: experiment hint]
    슬롯 i 는 _APPROACH_HINTS[i] 와 1:1 (run_planning_parallel_3 와 동일 hint 매핑).

    Args:
        user_input: 사용자 입력 텍스트 (Intent 통과 후).
        rag_context: RAGReference 또는 dict 시퀀스 (Slice 4 호환). None/빈 배열 허용.
        gateway: LLMGateway DI (None 이면 get_gateway() 싱글톤). 테스트가 fake 주입.

    Returns:
        list of 3 planning dicts. 각 dict 은 {"plan": {...}} 형식 (length 3 보장).
        슬롯 실패(예외) 시 retry 1회 → 또 실패 시 _fallback_plan_dict(i) 로 대체.

    Note:
        graceful — run_planning_parallel_3 의 retry/fallback 로직을 그대로 본뜬다.
        응답 파싱은 clean JSON 가정(S2b-1 이 adapter 단에서 Claude 펜스 제거 처리).
    """
    gw = gateway
    if gw is None:
        from ..llm.gateway import get_gateway  # 지연 import (순환 방지)

        gw = get_gateway()

    rag_context_list = list(rag_context or [])

    # 3 슬롯 병렬 호출 (run_planning_parallel_3 패턴).
    tasks = [
        _run_planning_single_via_gateway(
            user_input,
            rag_context_list=rag_context_list,
            alias=_MULTI_PROVIDER_PLAN_ALIASES[i],
            approach_hint=_APPROACH_HINTS[i],
            gateway=gw,
        )
        for i in range(3)
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)

    # 슬롯별 관측 로깅 + 일부 실패 시 retry 1회 → fallback (graceful, length 3 보장).
    final_results: list[dict[str, Any]] = []
    for i, r in enumerate(results):
        alias = _MULTI_PROVIDER_PLAN_ALIASES[i]
        if isinstance(r, BaseException):
            logger.warning(
                "planning(multi-provider) slot=%d alias=%s failed (%s), retrying once",
                i, alias, type(r).__name__,
            )
            try:
                retry = await _run_planning_single_via_gateway(
                    user_input,
                    rag_context_list=rag_context_list,
                    alias=alias,
                    approach_hint=_APPROACH_HINTS[i],
                    gateway=gw,
                )
                model_id = retry.pop("_model_id", "")
                logger.info(
                    "planning(multi-provider) slot=%d alias=%s model=%s ok (retry)",
                    i, alias, model_id,
                )
                final_results.append(retry)
            except Exception as e2:
                logger.warning(
                    "planning(multi-provider) slot=%d alias=%s retry also failed: %s "
                    "— using fallback dict",
                    i, alias, e2,
                )
                final_results.append(_fallback_plan_dict(i))
        else:
            model_id = r.pop("_model_id", "") if isinstance(r, dict) else ""
            logger.info(
                "planning(multi-provider) slot=%d alias=%s model=%s ok",
                i, alias, model_id,
            )
            final_results.append(copy.deepcopy(r))

    # approach_label unique 강제 (run_planning_parallel_3 와 동일).
    final_results = _enforce_unique_approach_labels(final_results)

    return final_results


# ─── 메타 ────────────────────────────────────────────────────────────

PROMPT_ID = "P-006"
PROMPT_VERSION = "v1.0.0"  # compact (active, flag OFF 경로 — rich_output_enabled=False default)

# Phase 13 S2: rich 변형 version. rich_output_enabled=True(S3) 경로에서 사용.
# meta.prompt_version 분기(compact v1.0.0 / rich v1.1.0)는 S3 gated wiring 에서.
RICH_PROMPT_VERSION = "v1.1.0"

# Phase 15 S2: director 변형 version. output_mode=director(S3) 경로에서 사용.
# meta.prompt_version 분기(compact v1.0.0 / rich v1.1.0 / director v1.2.0)는 S3 gated wiring.
DIRECTOR_PROMPT_VERSION = "v1.2.0"
