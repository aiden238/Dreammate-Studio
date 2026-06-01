"""Cross-validation (교차검증) — Phase 11 A안 Slice 2 (제안서 §7 / §18.A).

표준 Critic(OpenAI gpt-4o) 평가를 **다른 family 모델(Gemini)**로 1회 독립 교차검증하여
단일 모델 self-bias 를 줄인다. multi-llm-validation Skill 정신과 정합(생성=mini, 검증=gpt-4o,
교차검증=Gemini).

★★ behavior-preserving / gated default-off:
  - 본 모듈은 **순수 함수**다. 어디에도 자동 연결되지 않는다(orchestrator/agents/routers 미변경).
  - 활성 게이트는 config `cross_validation_enabled`(default False). 호출측이 이 flag 로
    cross_validate 호출 여부를 결정한다(본 모듈은 flag 를 강제하지 않음 — 호출 책임 분리).
  - Gemini 실패(키없음/503/빈출력/JSON 파싱 실패)는 **예외 전파 없이** graceful
    CrossCheck(available=False, error=...) 로 흡수한다 → 기존 파이프라인 무영향.

흐름:
  cross_validate(plan_text) → gateway.complete("cross_validation", ...) [Gemini, JSON mode]
    → CrossCheck(overall_score 0–1 + dimensions + verdict + comment)  (Critic 과 동형)
  compare(openai_critic_canonical, cross) → 두 평가 비교 dict
    (agreement / score_delta / divergent_dimensions / recommendation)

★ Critic canonical 동형: Critic 의 normalize_to_canonical 산출(overall_score 0–1 + dimensions
  0–1, ADR-018/029)과 같은 축. 비교(compare)가 같은 스케일에서 이루어진다.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from typing import Any

from .errors import LLMError

logger = logging.getLogger(__name__)

# Critic 8 차원 (agents/critic.py DIMENSIONS 와 동형 — 교차검증도 같은 축으로 평가).
CROSS_DIMENSIONS: tuple[str, ...] = (
    "intent_fit",
    "target_clarity",
    "hook_strength",
    "message_clarity",
    "structure",
    "feasibility",
    "brand_consistency",
    "differentiation",
)

# compare 합의 임계: 두 overall_score(0–1) 차이가 이 값 이하면 합의(consensus).
AGREEMENT_THRESHOLD = 0.2
# divergent_dimensions: 차원별 점수 차이가 이 값 초과면 불일치 차원으로 기록.
DIMENSION_DIVERGENCE_THRESHOLD = 0.3


# ─── 교차검증 system prompt (Gemini, JSON mode, Critic 동형 출력) ─────────

CROSS_SYSTEM_PROMPT = """당신은 영상기획안을 독립적으로 교차검증하는 품질 평가자다.

입력으로 영상기획안(plan) 1개가 주어진다. 다른 평가자의 결과를 모른 채, 아래 8개 차원을
각각 0.0~1.0 실수로 채점하라(1.0 = 완벽, 0.0 = 매우 미흡).

8 평가 차원:
  intent_fit         : 사용자 요청 의도와 plan 이 부합하는가
  target_clarity     : 시청자 페르소나가 구체적인가
  hook_strength      : 첫 3초 후크가 스크롤을 멈추게 하는가
  message_clarity    : 핵심 메시지가 한 줄로 정리되며 사실 정확한가
  structure          : 도입-전개-마무리 flow 가 자연스러운가
  feasibility        : 1인/스마트폰/저예산으로 실행 가능한가
  brand_consistency  : 광고적 과장 표현이 없는가
  differentiation    : 흔한 패턴이 아닌 차별화된 접근인가

응답 형식 (JSON 1개 객체만, 자연어 머리말/꼬리말 금지):
{
  "overall_score": 0.0,
  "dimensions": {
    "intent_fit": 0.0, "target_clarity": 0.0, "hook_strength": 0.0,
    "message_clarity": 0.0, "structure": 0.0, "feasibility": 0.0,
    "brand_consistency": 0.0, "differentiation": 0.0
  },
  "verdict": "approve | revise | reject",
  "comment": "한두 줄 총평"
}

overall_score 는 8 차원의 산술평균(0.0~1.0)이다. verdict 는 approve(≥0.7) /
revise(0.5~0.7) / reject(<0.5) 기준을 따른다. 모든 차원 키를 반드시 채운다.
"""


# ─── CrossCheck dataclass (교차검증 결과, canonical 동형) ────────────────

@dataclass(frozen=True)
class CrossCheck:
    """Gemini 교차검증 결과 (Critic canonical 과 동형).

    Attributes:
        available: 교차검증 성공 여부. False 면 Gemini 실패(키없음/503/빈출력/파싱실패)로
                   graceful 흡수된 상태 → error 에 사유. 호출측은 이 경우 교차검증을 무시한다.
        model_id: 실제 호출된 Gemini concrete model_id (없으면 "").
        overall_score: 전체 점수 0.0~1.0 (Critic overall_score 와 같은 축).
        dimensions: 차원별 0.0~1.0 점수 (Critic dimensions 와 같은 축).
        verdict: "approve" | "revise" | "reject" (없으면 "").
        comment: 총평 (없으면 "").
        error: available=False 일 때 실패 사유.
        raw: Gemini 원본 응답 텍스트 (디버깅용).
    """

    available: bool = True
    model_id: str = ""
    overall_score: float | None = None
    dimensions: dict[str, float] = field(default_factory=dict)
    verdict: str = ""
    comment: str = ""
    error: str = ""
    raw: str = ""


def _clamp01(x: Any) -> float | None:
    """0.0~1.0 으로 clamp (변환 불가 시 None). bool 은 점수가 아니므로 제외."""
    if isinstance(x, bool):
        return None
    try:
        v = float(x)
    except (TypeError, ValueError):
        return None
    return max(0.0, min(1.0, v))


def _parse_cross_payload(text: str) -> tuple[float | None, dict[str, float], str, str]:
    """Gemini JSON 응답 텍스트 → (overall_score, dimensions, verdict, comment).

    Raises:
        ValueError: JSON 파싱 실패 또는 dimensions 부재(graceful 흡수는 cross_validate 책임).
    """
    parsed = json.loads(text)
    if not isinstance(parsed, dict):
        raise ValueError("cross-validation 응답이 JSON 객체가 아님")

    raw_dims = parsed.get("dimensions")
    dimensions: dict[str, float] = {}
    if isinstance(raw_dims, dict):
        for k in CROSS_DIMENSIONS:
            c = _clamp01(raw_dims.get(k))
            if c is not None:
                dimensions[k] = c

    overall = _clamp01(parsed.get("overall_score"))
    if overall is None and dimensions:
        # overall 누락 시 dimensions 평균으로 보정 (Critic normalize 정신).
        overall = sum(dimensions.values()) / len(dimensions)

    if overall is None and not dimensions:
        raise ValueError("cross-validation 응답에 overall_score / dimensions 모두 없음")

    verdict = str(parsed.get("verdict", "")).strip().lower()
    if verdict not in {"approve", "revise", "reject"}:
        verdict = ""
    comment = str(parsed.get("comment", ""))
    return overall, dimensions, verdict, comment


def cross_validate(
    plan_text: str,
    *,
    gateway: Any = None,
    tier: str = "free",
    mode: str = "standard",
    adapter: Any = None,
    client: Any = None,
) -> CrossCheck:
    """plan 을 cross_validation alias(→ Gemini)로 독립 교차검증한다.

    ★ graceful: Gemini 실패(키없음 LLMError / 503 / 빈출력 / JSON 파싱 실패)는 예외를
    전파하지 않고 CrossCheck(available=False, error=...) 로 흡수한다. 호출측 파이프라인은
    교차검증 없이 정상 진행(behavior-preserving).

    Args:
        plan_text: 평가 대상 plan (JSON 문자열 또는 자연어 요약).
        gateway: LLMGateway DI (None 이면 get_gateway() 싱글톤). 테스트가 mock 주입.
        tier / mode: alias 해석 축 (A안 cross_validation 은 mode 무관 → gemini-cross).
        adapter / client: gateway.complete 로 전달되는 provider DI (테스트 mock 주입 → 실 API 0).

    Returns:
        CrossCheck (성공 시 available=True + 점수, 실패 시 available=False + error).
    """
    gw = gateway
    if gw is None:
        from .gateway import get_gateway  # 지연 import (순환 방지)

        gw = get_gateway()

    messages = [
        {"role": "system", "content": CROSS_SYSTEM_PROMPT},
        {
            "role": "user",
            "content": "다음 영상기획안을 8차원으로 교차검증해줘:\n\n" + str(plan_text),
        },
    ]

    try:
        resp = gw.complete(
            "cross_validation",
            messages,
            tier=tier,
            mode=mode,
            temperature=0.2,  # 평가 일관성 (Critic 과 동일 기조).
            json_mode=True,
            adapter=adapter,
            client=client,
        )
    except LLMError as e:
        # 키없음/503-소진/provider 실패 → graceful 흡수.
        logger.info("cross_validate graceful skip (LLMError): %s", e)
        return CrossCheck(available=False, error=f"gemini 호출 실패: {e}")
    except Exception as e:  # 예기치 못한 실패도 파이프라인 보호 위해 graceful.
        logger.warning("cross_validate graceful skip (예외): %s", e)
        return CrossCheck(available=False, error=f"교차검증 예외: {e}")

    text = (resp.text or "").strip()
    if not text:
        # thinking 모델 출력 0 등 → graceful.
        logger.info("cross_validate graceful skip — 빈 출력 model=%s", resp.model_id)
        return CrossCheck(available=False, model_id=resp.model_id, error="빈 출력(empty)")

    try:
        overall, dimensions, verdict, comment = _parse_cross_payload(text)
    except (ValueError, json.JSONDecodeError) as e:
        logger.info("cross_validate graceful skip — JSON 파싱 실패: %s", e)
        return CrossCheck(
            available=False, model_id=resp.model_id, error=f"파싱 실패: {e}", raw=text
        )

    logger.info(
        "cross_validate ok model=%s overall=%s verdict=%s",
        resp.model_id, overall, verdict,
    )
    return CrossCheck(
        available=True,
        model_id=resp.model_id,
        overall_score=overall,
        dimensions=dimensions,
        verdict=verdict,
        comment=comment,
        raw=text,
    )


def _critic_overall(critic_canonical: dict[str, Any]) -> float | None:
    """Critic canonical dict 에서 overall_score(0–1) 추출 (없으면 dimensions 평균)."""
    o = _clamp01(critic_canonical.get("overall_score"))
    if o is not None:
        return o
    dims = critic_canonical.get("dimensions")
    if isinstance(dims, dict) and dims:
        vals = [c for c in (_clamp01(v) for v in dims.values()) if c is not None]
        if vals:
            return sum(vals) / len(vals)
    return None


def compare(openai_critic_canonical: dict[str, Any], cross: CrossCheck) -> dict[str, Any]:
    """OpenAI Critic 평가와 Gemini 교차검증을 비교한다.

    두 평가가 같은 축(overall_score 0–1, dimensions 0–1)이므로 직접 비교 가능.

    Args:
        openai_critic_canonical: Critic canonical dict(overall_score / dimensions, 0–1).
        cross: cross_validate 산출 CrossCheck.

    Returns:
        dict:
          - available (bool): 교차검증 사용 가능 여부(cross.available).
          - agreement (bool): 두 overall_score 차이 ≤ AGREEMENT_THRESHOLD.
          - openai_score (float|None) / gemini_score (float|None)
          - score_delta (float|None): |openai - gemini|.
          - divergent_dimensions (list[str]): 차원별 차이가 임계 초과인 차원명.
          - recommendation (str): "consensus" | "human_review_needed" | "cross_unavailable".

        cross.available=False 면 recommendation="cross_unavailable" + agreement=False.
    """
    if not cross.available:
        return {
            "available": False,
            "agreement": False,
            "openai_score": _critic_overall(openai_critic_canonical),
            "gemini_score": None,
            "score_delta": None,
            "divergent_dimensions": [],
            "recommendation": "cross_unavailable",
            "error": cross.error,
        }

    openai_score = _critic_overall(openai_critic_canonical)
    gemini_score = cross.overall_score

    if openai_score is None or gemini_score is None:
        # 점수 비교 불가 → 보수적으로 human review.
        return {
            "available": True,
            "agreement": False,
            "openai_score": openai_score,
            "gemini_score": gemini_score,
            "score_delta": None,
            "divergent_dimensions": [],
            "recommendation": "human_review_needed",
        }

    score_delta = abs(openai_score - gemini_score)
    # round 으로 부동소수 경계 오차 흡수 (예: |0.8-0.6| == 0.2000…07 → 0.2 로 정규화).
    agreement = round(score_delta, 4) <= AGREEMENT_THRESHOLD

    divergent = _divergent_dimensions(
        openai_critic_canonical.get("dimensions"), cross.dimensions
    )

    recommendation = "consensus" if agreement else "human_review_needed"

    return {
        "available": True,
        "agreement": agreement,
        "openai_score": openai_score,
        "gemini_score": gemini_score,
        "score_delta": round(score_delta, 4),
        "divergent_dimensions": divergent,
        "recommendation": recommendation,
    }


def _divergent_dimensions(
    openai_dims: Any, gemini_dims: dict[str, float]
) -> list[str]:
    """차원별 점수 차이가 임계 초과인 차원명 목록 (정렬). 한쪽이라도 없으면 skip."""
    if not isinstance(openai_dims, dict) or not gemini_dims:
        return []
    out: list[str] = []
    for k in CROSS_DIMENSIONS:
        a = _clamp01(openai_dims.get(k))
        b = _clamp01(gemini_dims.get(k))
        if a is None or b is None:
            continue
        if abs(a - b) > DIMENSION_DIVERGENCE_THRESHOLD:
            out.append(k)
    return out
