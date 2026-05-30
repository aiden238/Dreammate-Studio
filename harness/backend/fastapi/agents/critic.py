"""Critic Agent — P-007 (Phase 1 Slice 3).

생성된 plan 1개에 대해 8차원 0~5점 평가를 수행한다 (output_schema.md §9 정합).
Phase 1: 평가만 (approve / revise / reject 판정 반환). revise 호출 없음.
Phase 4+: Critic의 revise 판정 시 Rewriter(P-008) 자동 호출, 최대 2 round.

호출 흐름:
  plan(dict) → gpt-4o 1회 호출 (JSON mode) → dict 반환 (output_schema §9.1)

failure_cases FC-001~005 시드 패턴 (eval/failure_cases.md) 을 차단하도록 system
prompt 구성:
  FC-001 후킹 약함        → hook_strength ≤ 2
  FC-002 타겟 모호        → target_clarity ≤ 2
  FC-003 실행 불가능      → feasibility ≤ 2
  FC-004 광고적 표현      → brand_consistency ≤ 2 + blocking_issues
  FC-005 hallucination    → message_clarity ≤ 2 + blocking_issues
"""

from __future__ import annotations

import json
import logging
from typing import Any

from openai import OpenAI, OpenAIError

from ..config import get_settings

logger = logging.getLogger(__name__)


# ─── 시스템 프롬프트 (Critic only) ─────────────────────────────────────

SYSTEM_PROMPT = """당신은 영상기획 AI 에이전트의 품질 평가자(Critic)이다.

입력으로 plan 1개(JSON)가 주어진다. 다음 8차원에 대해 각각 0~5 정수 점수를 부여하고,
짧은 reason(1~2줄)과 suggestion(1줄)을 작성한다.

8 평가 차원:
  1. intent_fit          : 사용자 요청의 의도와 plan이 부합하는가
  2. target_clarity      : 시청자 페르소나가 구체적인가 (광범위 = 낮은 점수)
  3. hook_strength       : 첫 3초 후크가 스크롤을 멈추게 하는가
                           ("안녕하세요", "오늘은 ~에 대해" 형 = 1~2점)
  4. message_clarity     : 핵심 메시지가 한 줄로 정리되는가, 사실 정확한가
                           (검증 불가능한 통계 = 낮은 점수)
  5. structure           : flow 비트 구성이 도입-전개-마무리로 자연스러운가
  6. feasibility         : 1인/스마트폰/저예산으로 촬영·편집 실행 가능한가
                           (드론·8K·고예산 가정 = 낮은 점수)
  7. brand_consistency   : 광고적 과장 표현 없는가
                           ("혁신적", "최고의", "완벽한", "최선의", "최첨단",
                            "획기적", "1위", "압도적" = 즉시 1점)
  8. differentiation     : 흔한 패턴이 아닌, 차별화된 접근인가

판정 규칙 (overall_verdict):
  - approve: avg ≥ 3.5 AND 모든 점수 ≥ 2
  - revise:  2.5 ≤ avg < 3.5  OR  1~2개 점수가 < 2
  - reject:  avg < 2.5  OR  3개 이상 점수가 < 2

blocking_issues:
  - 광고적 과장 표현 발견 시 단어를 명시
  - 검증 불가능한 통계 발견 시 해당 문장 명시
  - 1인 운영자 가정 위반 시 명시
  - 최대 3개

응답 형식 (JSON 1개 객체만, 자연어 머리말/꼬리말 금지):
{
  "scores": {
    "intent_fit": 0-5,
    "target_clarity": 0-5,
    "hook_strength": 0-5,
    "message_clarity": 0-5,
    "structure": 0-5,
    "feasibility": 0-5,
    "brand_consistency": 0-5,
    "differentiation": 0-5
  },
  "reasons": {
    "intent_fit": "...",
    "target_clarity": "...",
    "hook_strength": "...",
    "message_clarity": "...",
    "structure": "...",
    "feasibility": "...",
    "brand_consistency": "...",
    "differentiation": "..."
  },
  "suggestions": {
    "intent_fit": "...",
    "target_clarity": "...",
    "hook_strength": "...",
    "message_clarity": "...",
    "structure": "...",
    "feasibility": "...",
    "brand_consistency": "...",
    "differentiation": "..."
  },
  "overall_verdict": "approve | revise | reject",
  "blocking_issues": ["..."]
}

8개 키는 반드시 모두 채운다. overall_score_avg와 revise_round는 서버에서 채우므로
생략 가능하다. plan 안의 plan_id는 응답에서 사용하지 않는다 (서버가 주입).
"""


# ─── 평가 차원 메타 ────────────────────────────────────────────────────

DIMENSIONS: tuple[str, ...] = (
    "intent_fit",
    "target_clarity",
    "hook_strength",
    "message_clarity",
    "structure",
    "feasibility",
    "brand_consistency",
    "differentiation",
)


# ─── verdict 산출 (server-side 보정) ──────────────────────────────────

def _derive_verdict(scores: dict[str, int]) -> tuple[float, str]:
    """평균 + 미달 카운트로 verdict 산출 (output_schema §9.2).

    Returns:
        (overall_score_avg, verdict)
    """
    values = [int(scores.get(k, 0)) for k in DIMENSIONS]
    avg = sum(values) / len(values)
    below_2 = sum(1 for v in values if v < 2)

    if avg < 2.5 or below_2 >= 3:
        verdict = "reject"
    elif (2.5 <= avg < 3.5) or below_2 in (1, 2):
        verdict = "revise"
    else:  # avg >= 3.5 AND 모든 점수 ≥ 2
        verdict = "approve"
    return round(avg, 4), verdict


# ─── 호출 함수 ────────────────────────────────────────────────────────

def run_critic(
    plan: dict[str, Any],
    *,
    client: OpenAI | None = None,
    model: str | None = None,
) -> dict[str, Any]:
    """Critic 평가 LLM 호출.

    Args:
        plan: Planning agent가 생성한 plan dict (또는 Plan.model_dump()).
              plan_id 키가 있으면 target_plan_id로 echo back.
        client: OpenAI 클라이언트 (테스트 시 mock 주입).
        model: 사용 모델 (기본은 settings.openai_model_critic = gpt-4o).

    Returns:
        dict matching output_schema §9.1:
          - target_plan_id (str): plan["plan_id"] echo
          - scores (dict): 8 차원 0~5 정수
          - reasons (dict): 8 차원 1~2줄 사유
          - suggestions (dict): 8 차원 1줄 개선안
          - overall_score_avg (float): 8 점수 산술 평균
          - overall_verdict (str): "approve" | "revise" | "reject"
          - blocking_issues (list[str]): 0~3개
          - revise_round (int): Phase 1 항상 0

    Raises:
        OpenAIError: API 호출 실패.
        ValueError: JSON 파싱 실패 또는 scores 키 누락.
    """
    settings = get_settings()
    _client = client or OpenAI(api_key=settings.openai_api_key)
    _model = model or settings.openai_model_critic

    target_plan_id = str(plan.get("plan_id") or "")

    logger.info("critic call start model=%s plan_id=%s", _model, target_plan_id)

    try:
        response = _client.chat.completions.create(
            model=_model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": "다음 plan을 8차원으로 평가해줘:\n\n"
                    + json.dumps(plan, ensure_ascii=False),
                },
            ],
            response_format={"type": "json_object"},
            temperature=0.2,  # 평가 일관성 (agent_io_contract §5.4)
            max_tokens=1500,
        )
    except OpenAIError:
        logger.exception("Critic OpenAI API 호출 실패")
        raise

    raw_content = response.choices[0].message.content or "{}"
    logger.debug("critic raw response: %s", raw_content[:200])

    try:
        parsed: dict[str, Any] = json.loads(raw_content)
    except json.JSONDecodeError as e:
        raise ValueError(f"Critic LLM 응답 JSON 파싱 실패: {e}") from e

    scores = parsed.get("scores")
    if not isinstance(scores, dict):
        raise ValueError("Critic LLM 응답에 scores 객체 없음")
    missing = [k for k in DIMENSIONS if k not in scores]
    if missing:
        raise ValueError(f"Critic scores 누락 차원: {missing}")

    # 점수 정수화 + clamp 0~5 (LLM이 4.5 같은 실수를 줄 수도 있으므로)
    norm_scores: dict[str, int] = {}
    for k in DIMENSIONS:
        v = scores[k]
        try:
            iv = int(round(float(v)))
        except (TypeError, ValueError) as e:
            raise ValueError(f"Critic score 정수 변환 실패 ({k}): {v}") from e
        norm_scores[k] = max(0, min(5, iv))

    reasons = parsed.get("reasons") or {}
    suggestions = parsed.get("suggestions") or {}
    if not isinstance(reasons, dict) or not isinstance(suggestions, dict):
        raise ValueError("Critic reasons/suggestions 형식 불일치")

    # 키 보강: LLM이 빠뜨린 차원은 빈 문자열로 채움
    reasons = {k: str(reasons.get(k, "")) for k in DIMENSIONS}
    suggestions = {k: str(suggestions.get(k, "")) for k in DIMENSIONS}

    # server-side verdict 보정 (output_schema §9.2 규칙 강제)
    avg, derived_verdict = _derive_verdict(norm_scores)
    llm_verdict = str(parsed.get("overall_verdict", "")).strip().lower()
    if llm_verdict not in {"approve", "revise", "reject"}:
        llm_verdict = derived_verdict
    # 규칙 우선 (LLM이 점수와 모순되는 verdict 내면 규칙 채택)
    verdict = derived_verdict if llm_verdict != derived_verdict else llm_verdict

    blocking_raw = parsed.get("blocking_issues") or []
    if not isinstance(blocking_raw, list):
        blocking_raw = []
    blocking_issues = [str(b) for b in blocking_raw][:3]

    result: dict[str, Any] = {
        "target_plan_id": target_plan_id,
        "scores": norm_scores,
        "reasons": reasons,
        "suggestions": suggestions,
        "overall_score_avg": avg,
        "overall_verdict": verdict,
        "blocking_issues": blocking_issues,
        "revise_round": 0,  # Phase 1: 항상 0 (서버 관리)
    }

    logger.info(
        "critic ok plan_id=%s avg=%.2f verdict=%s",
        target_plan_id,
        avg,
        verdict,
    )
    return result


# ─── Phase 8 Slice 4: conservative adapter (ADR-029) ─────────────────

def _is_num(x: Any) -> bool:
    """float 변환 가능 여부 (bool 제외 — bool 은 점수가 아님)."""
    if isinstance(x, bool):
        return False
    try:
        float(x)
    except (TypeError, ValueError):
        return False
    return True


def normalize_to_canonical(verdict: dict[str, Any]) -> dict[str, Any]:
    """P-007 conservative adapter (Slice 4 ADR-029): 0–5 scores → 0–1 canonical.

    LLM-facing P-007 prompt 는 0–5 정수 8 dims 유지. 본 helper 는 code-side 정규화:
      dimensions[dim] = scores[dim] / 5.0  (0–1 clamp)
      overall_score   = overall_score_avg / 5.0  (또는 scores 평균/5.0)
    기존 0–5 deprecated 필드(scores / overall_score_avg)는 병행 유지 → 회귀 0
    (run_critic 파이프라인 출력 의미 불변 — 본 helper 는 additive 코드 유틸이며
    run_critic 반환에 강제 주입하지 않는다).

    Phase 6 CriticEvaluation canonical(overall_score + dimensions, ADR-018) 와 정합.
    이미 canonical(overall_score 또는 dimensions)이 있으면 그 값을 우선 보존한다.

    Args:
        verdict: run_critic 산출 dict (또는 0–5 형식 verdict dict).

    Returns:
        입력 사본 + canonical 필드(dimensions / overall_score) 추가. scores 가 없거나
        비어 있으면 입력을 그대로 반환 (비파괴 사본).
    """
    out = dict(verdict)  # 비파괴 (사본)
    scores = verdict.get("scores")
    if isinstance(scores, dict) and scores:
        dims: dict[str, float] = {}
        for k, v in scores.items():
            if not _is_num(v):
                continue
            dims[k] = max(0.0, min(1.0, float(v) / 5.0))
        if dims:
            # 기존 canonical dimensions 가 있으면 보존, 없으면 정규화 결과 주입.
            out.setdefault("dimensions", dims)
            if out.get("overall_score") is None:
                avg5 = verdict.get("overall_score_avg")
                if avg5 is None or not _is_num(avg5):
                    vals = [float(x) for x in scores.values() if _is_num(x)]
                    avg5 = sum(vals) / len(vals) if vals else None
                if avg5 is not None and _is_num(avg5):
                    out["overall_score"] = max(0.0, min(1.0, float(avg5) / 5.0))
    return out


# ─── Phase 4.5 Slice 3: Best-plan selection (Z-X3) ────────────────────
# ─── Phase 6 Slice 2: canonical 우선순위 (ADR-018) ─────────────────────
# ─── Phase 9.5 Slice 4: deprecated 0–5 fallback 제거 (ADR-034) ─────────

def select_best_plan_index(verdicts: list[dict[str, Any]]) -> int | None:
    """Critic verdict list 에서 가장 좋은 plan 의 index 를 반환 (Z-X3 / ADR-018).

    Phase 4.5 Slice 3 — 3 plan 동등 노출 부담 완화. recommended_plan_index 로
    frontend wrapper(`/plan/[plan_id]/page.tsx`) highlight 에 사용. PlanCard.tsx
    무수정 정책 유지 (사용자 결정 6-a 계승).

    Phase 6 (ADR-018) canonical 우선순위 — Phase 9.5 (ADR-034) deprecated 0–5 fallback 제거 완료:
      1. `overall_score` (float [0.0~1.0]) — canonical
      2. `dimensions` (dict[str, float]) 평균 — canonical fallback

      Phase 9 wiring (ADR-032) 으로 critic_evaluation 에 canonical 항상 populated →
      deprecated 0–5 fallback(overall_score_avg / scores / eight_dim_scores) 은 dead code 였고,
      Phase 9.5 Slice 4 (ADR-034) 에서 완전 제거되었다 (canonical 두 경로만 소비, 없으면 None).
      LLM-facing 0–5(run_critic)는 normalize_to_canonical 가 0–1 로 변환하므로 본 함수에는
      canonical 만 도달한다 (P-007 prompt contract 불변).

    Args:
        verdicts: plan별 verdict dict list.
                  None 또는 invalid 항목은 skip.

    Returns:
        best plan index (0-based, `plan_candidates` 순서와 동일).
        모든 verdict 가 invalid 거나 list 가 비면 None.

    Tie-breaking:
        동점 시 plan_index 가 더 작은 쪽 (deterministic — 동일 입력 동일 출력).
    """
    if not verdicts:
        return None

    def _score(v: Any) -> float | None:
        if not isinstance(v, dict):
            return None
        # Phase 6 canonical (ADR-018): overall_score (float, 0~1)
        if v.get("overall_score") is not None:
            try:
                return float(v["overall_score"])
            except (TypeError, ValueError):
                pass
        # Phase 6 canonical (ADR-018): dimensions dict 평균 (float, 0~1)
        dims_canonical = v.get("dimensions")
        if isinstance(dims_canonical, dict) and dims_canonical:
            try:
                vals = [float(x) for x in dims_canonical.values() if x is not None]
                if vals:
                    return sum(vals) / len(vals)
            except (TypeError, ValueError):
                pass
        # Phase 9.5 (ADR-034): deprecated 0–5 fallback(overall_score_avg / scores /
        # eight_dim_scores) 제거됨. canonical(overall_score / dimensions) 없으면 None.
        return None

    best_idx: int | None = None
    best_score: float | None = None
    for i, v in enumerate(verdicts):
        s = _score(v)
        if s is None:
            continue
        if best_score is None or s > best_score:
            best_score = s
            best_idx = i
        # tie: best_idx already lower index → 유지 (deterministic)
    return best_idx


# ─── 메타 ────────────────────────────────────────────────────────────

PROMPT_ID = "P-007"
# Phase 8 ADR-029: v1.0.0 → v1.1.0 — code-side 0–5↔0–1 conservative adapter
# (normalize_to_canonical) 추가. LLM-facing prompt(0–5) 불변, run_critic 출력 의미 불변
# (helper additive, 미강제 주입 → 회귀 0). semver minor (output schema 미변경).
PROMPT_VERSION = "v1.1.0"
