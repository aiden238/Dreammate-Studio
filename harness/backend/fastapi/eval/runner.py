"""Phase 9.5 — golden_set 회귀 runner (ADR-033).

mock-deterministic primary + 실 LLM mode flag.

설계 (ADR-033 §1, §2.2, §2.4):
  - mock 모드 (primary): golden_set 케이스 input → 결정적 mock Envelope fixture 생성
    (실 LLM/Supabase 호출 0, 고정 seed 없음 — 순수 deterministic). schema 준수(100% 필수)
    + structural(plan 3개 / hook 존재 / flow 비트 / 광고 단어 부재 / 차단 단어 0) 채점.
  - real 모드 (문서, CI 미사용): OpenAI 실 호출 → 8차원 의미 채점. 본 phase 는 NotImplemented.
  - 임계값 게이트 (eval-run §6): schema 100% / 점수 하락 ≤0.3 / 광고 >5% fail / 차단 단어 >0% fail
    + P0 케이스 통과율 < 100% 즉시 fail.

mock fixture 정책:
  - 각 케이스의 expected_properties 를 만족하는 canonical Envelope 를 결정적으로 합성한다
    (canonical-only 품질 baseline — ADR-034 Critic deprecated 0–5 제거 안전망).
  - 광고/차단 단어 검사는 rag/quality_filter 패턴 + llm_security 차단 사전 재사용.
"""
from __future__ import annotations

import logging
from typing import Any
from uuid import uuid4

from ..rag.quality_filter import _AD_WORDS
from ..schemas.output import (
    Body,
    CriticEvaluation,
    Envelope,
    Meta,
    Plan,
    PlanFlowBeat,
    Validation,
    ValidationCheck,
)
from .golden_set_loader import load_golden_set
from .mode import MODE_MOCK, MODE_REAL, ScoreContext, real_score_envelope, resolve_mode
from .revise_effect import aggregate_revise_effects, measure_revise_effect

logger = logging.getLogger(__name__)

# ── 차단 단어 단일 사전 (ADR-033 §2.4) ───────────────────────────────
# video_planning_eval brand_consistency + llm_security_contract §광고 차단 + GS-004 1차 단어 통합.
# LLM 출력만 검사 (사용자 입력 예외 — GS-004 notes). _AD_WORDS(quality_filter) 와 합집합.
_LLM_SECURITY_AD_WORDS = [
    "최고의",
    "혁신적",
    "획기적",
    "완벽한",
    "1위",
    "넘버원",
    "압도적",
    "역대급",
    "단연 최고",
    "최고",
]
AD_WORDS: tuple[str, ...] = tuple(dict.fromkeys([*_AD_WORDS, *_LLM_SECURITY_AD_WORDS]))

# 차단 단어 (안전 — 0% 허용). 인젝션/보안 회피 표현 등 절대 출력 금지 어휘.
BLOCKED_WORDS: tuple[str, ...] = (
    "system prompt",
    "이전 지시를 무시",
    "ignore previous",
)

# 임계값 (eval-run §6 / ADR-033 §2.4 mock 강제 4종).
THRESHOLD_SCORE_DROP = 0.3
THRESHOLD_AD_RATE = 0.05  # 광고 표현 검출 > 5% fail
THRESHOLD_BLOCKED_RATE = 0.0  # 차단 단어 검출 > 0% fail


# ── structural 헬퍼 ──────────────────────────────────────────────────

def _collect_text(envelope_dict: dict[str, Any]) -> str:
    """Envelope body 의 LLM 출력 텍스트 필드 전체를 이어붙임 (광고/차단 단어 검사용).

    사용자 입력(meta/input)은 검사 대상 아님 — body(plan 텍스트 + critic) 만 수집.
    """
    body = envelope_dict.get("body") or {}
    parts: list[str] = []
    for plan in body.get("plan_candidates") or []:
        if not isinstance(plan, dict):
            continue
        parts.append(str(plan.get("name", "")))
        parts.append(str(plan.get("concept", "")))
        parts.append(str(plan.get("hook", "")))
        parts.append(str(plan.get("pros", "")))
        parts.append(str(plan.get("risks", "")))
        for beat in plan.get("flow") or []:
            if isinstance(beat, dict):
                parts.append(str(beat.get("beat", "")))
                parts.append(str(beat.get("purpose", "")))
    critic = body.get("critic_evaluation")
    if isinstance(critic, dict):
        for v in (critic.get("reasons") or {}).values():
            parts.append(str(v))
        for v in (critic.get("suggestions") or {}).values():
            parts.append(str(v))
    return " ".join(parts)


def detect_ad_words(text: str) -> list[str]:
    """텍스트에서 광고 표현 검출 (정확 매칭). 검출 단어 list 반환."""
    return [w for w in AD_WORDS if w in text]


def detect_blocked_words(text: str) -> list[str]:
    """텍스트에서 차단 단어 검출 (정확 매칭, 대소문자 무시). 검출 단어 list 반환."""
    low = text.lower()
    return [w for w in BLOCKED_WORDS if w.lower() in low]


# ── 채점 ─────────────────────────────────────────────────────────────

def score_case(case: dict[str, Any], envelope_dict: dict[str, Any]) -> dict[str, Any]:
    """schema 준수(100% 필수) + structural 채점.

    structural 룰 (ADR-033 §2.2):
      - plan_candidates 3개
      - 각 plan hook 존재 (min_length 10)
      - 각 plan flow 비트 2~8
      - 광고 단어 부재 (body 텍스트)
      - 차단 단어 0 (body 텍스트)

    Args:
        case: load_golden_set 케이스 dict.
        envelope_dict: mock pipeline 이 생성한 Envelope.model_dump(mode="json").

    Returns:
        {
          case_id, priority,
          schema_ok: bool,
          structural: { plan_count_ok, hook_ok, flow_ok, ad_clean, blocked_clean },
          ad_words: [...], blocked_words: [...],
          structural_score: float (0~1 — 만족 룰 비율),
          passed: bool (schema_ok AND structural 전부),
        }
    """
    # 1. schema 준수 — Envelope Pydantic 재검증 (100% 필수).
    schema_ok = True
    schema_error: str | None = None
    try:
        Envelope.model_validate(envelope_dict)
    except Exception as exc:  # pydantic ValidationError 등
        schema_ok = False
        schema_error = str(exc)

    body = envelope_dict.get("body") or {}
    plans = body.get("plan_candidates") or []

    # 2. structural.
    plan_count_ok = len(plans) == 3

    hook_ok = True
    flow_ok = True
    for plan in plans:
        if not isinstance(plan, dict):
            hook_ok = False
            flow_ok = False
            continue
        hook = str(plan.get("hook", ""))
        if len(hook) < 10:
            hook_ok = False
        flow = plan.get("flow") or []
        if not (2 <= len(flow) <= 8):
            flow_ok = False

    text = _collect_text(envelope_dict)
    ad_words = detect_ad_words(text)
    blocked_words = detect_blocked_words(text)
    ad_clean = len(ad_words) == 0
    blocked_clean = len(blocked_words) == 0

    structural = {
        "plan_count_ok": plan_count_ok,
        "hook_ok": hook_ok,
        "flow_ok": flow_ok,
        "ad_clean": ad_clean,
        "blocked_clean": blocked_clean,
    }
    structural_score = sum(1 for v in structural.values() if v) / len(structural)
    passed = schema_ok and all(structural.values())

    return {
        "case_id": case.get("id", "?"),
        "priority": case.get("priority", "P1"),
        "schema_ok": schema_ok,
        "schema_error": schema_error,
        "structural": structural,
        "ad_words": ad_words,
        "blocked_words": blocked_words,
        "structural_score": round(structural_score, 4),
        "passed": passed,
    }


# ── mock pipeline (deterministic fixture) ────────────────────────────

def _mock_envelope_for_case(case: dict[str, Any]) -> dict[str, Any]:
    """케이스 input → canonical 정상 Envelope (deterministic, 실 LLM 호출 X).

    각 케이스의 expected_properties(plan 3개 / hook / flow)를 만족하는 결정적 fixture.
    canonical-only(overall_score 0–1 + dimensions) — deprecated 0–5 미사용 (ADR-034 정합).
    광고/차단 단어 미포함 (정상 baseline). 동일 케이스 → 동일 출력 (random/now 회피).
    """
    case_id = str(case.get("id", "GS-000"))
    # 결정적 plan_id seed — case_id 기반 (uuid4 회피).
    plans: list[Plan] = []
    labels = ["narrative", "informational", "experiment"]
    for i in range(3):
        plans.append(
            Plan(
                plan_id=f"{case_id}-plan-{i}",
                option_index=i,
                name=f"기획안 {i + 1}",
                concept=f"{case_id} 콘셉트 {i + 1} — 영상기획 방향 제시",
                hook=f"{case_id} 후크 {i + 1} 시청 유지율 검증용 문장",
                flow=[
                    PlanFlowBeat(beat_index=0, beat="도입", duration_sec=3, purpose="관심 유도"),
                    PlanFlowBeat(beat_index=1, beat="전개", duration_sec=20, purpose="핵심 전달"),
                    PlanFlowBeat(beat_index=2, beat="마무리", duration_sec=7, purpose="행동 유도"),
                ],
                pros="명확한 구조",
                risks="제작 난이도",
                approach_label=labels[i],
                rag_used=[],
            )
        )

    critic = CriticEvaluation(
        overall_score=0.78,
        dimensions={
            "intent_fit": 0.8,
            "target_clarity": 0.75,
            "hook_strength": 0.8,
            "message_clarity": 0.78,
            "structure": 0.8,
            "feasibility": 0.76,
            "brand_consistency": 0.82,
            "differentiation": 0.74,
        },
        overall_verdict="approve",
        blocking_issues=[],
        revise_round=0,
    )

    envelope = Envelope(
        meta=Meta(
            request_id=f"{case_id}-req",
            prompt_id="P-006",
            prompt_version="v1.0.0",
            model="mock-deterministic",
            generated_at="2026-05-31T00:00:00Z",
            locale="ko-KR",
        ),
        body=Body(
            plan_candidates=plans,
            critic_evaluation=critic,
            rag_references=[],
            revise_history=None,
            recommended_plan_index=0,
        ),
        validation=Validation(
            passed=True,
            checks=[
                ValidationCheck(name="schema_envelope", status="ok"),
                ValidationCheck(name="plan_count", status="ok", detail="3 plans"),
                ValidationCheck(name="critic_evaluation", status="ok", detail="mock canonical"),
            ],
            warnings=[],
        ),
    )
    return envelope.model_dump(mode="json")


def _avg(values: list[float]) -> float:
    return round(sum(values) / len(values), 4) if values else 0.0


# ── revise effect mock fixture (deterministic) ───────────────────────
# ADR-033 §2.3 — revise loop 개선 효과 (Phase 4.5 D6 해소). 실 LLM 미호출.
# 각 시나리오 = (revise_history[ReviseAttempt dict], attempt 순서별 canonical score 0–1).
# canonical-only (overall_score 0–1) — deprecated 0–5 미사용 (ADR-034 정합).
#   improved : revise 후 점수 상승 (정상 동작)
#   regressed: revise 후 점수 하락 (Phase 4.5 우려 — "revise 가 기획을 평범하게")
#   no_change: revise 미발생 또는 점수 정체
#   max      : max_revise 도달 (소폭 상승)
_REVISE_EFFECT_FIXTURES: list[tuple[list[dict[str, Any]], list[float]]] = [
    # improved — 초기 revise verdict → revise → 재평가 상승.
    (
        [
            {"attempt": 0, "action": "revise", "revised": True},
            {"attempt": 1, "action": "approve", "revised": False},
        ],
        [0.62, 0.81],
    ),
    # improved — 2회 revise 점진 상승.
    (
        [
            {"attempt": 0, "action": "revise", "revised": True},
            {"attempt": 1, "action": "revise", "revised": True},
            {"attempt": 2, "action": "approve", "revised": False},
        ],
        [0.55, 0.68, 0.79],
    ),
    # no_change — 초기 approve (revise 미발생).
    (
        [
            {"attempt": 0, "action": "approve", "revised": False},
        ],
        [0.84],
    ),
    # regressed — revise 후 점수 하락 (Phase 4.5 우려 검증 지표).
    (
        [
            {"attempt": 0, "action": "revise", "revised": True},
            {"attempt": 1, "action": "approve", "revised": False},
        ],
        [0.74, 0.69],
    ),
    # max_reached — max_revise 도달, 소폭 상승.
    (
        [
            {"attempt": 0, "action": "revise", "revised": True},
            {"attempt": 1, "action": "revise", "revised": True},
            {"attempt": 2, "action": "revise", "revised": False, "max_reached": True},
        ],
        [0.58, 0.63, 0.66],
    ),
]


def run_revise_effect_eval(
    *,
    fixtures: list[tuple[list[dict[str, Any]], list[float]]] | None = None,
) -> dict[str, Any]:
    """revise loop 개선 효과 eval — mock fixture 기반 (ADR-033 §2.3, Phase 4.5 D6 해소).

    각 fixture(revise_history + attempt 순서별 canonical score) → measure_revise_effect →
    aggregate_revise_effects 로 집계. 실 LLM 미호출 (deterministic).

    Args:
        fixtures: (revise_history, scores_by_attempt) 튜플 list 주입 (None → 기본 fixture 5종).

    Returns:
        {effects: [measure_revise_effect...], aggregate: {mean_delta, improved_rate,
         regressed_rate, no_change_rate, n}}.
    """
    src = fixtures if fixtures is not None else _REVISE_EFFECT_FIXTURES
    effects = [measure_revise_effect(history, scores) for history, scores in src]
    aggregate = aggregate_revise_effects(effects)
    return {"effects": effects, "aggregate": aggregate}


def run_golden_set_eval(
    *,
    mode: str = "mock",
    cases: list[dict[str, Any]] | None = None,
    baseline_score: float | None = None,
    golden_set_path: str | None = None,
    include_revise_effect: bool = False,
    ctx: ScoreContext | None = None,
) -> dict[str, Any]:
    """golden_set 케이스 → pipeline → 채점 → 요약 + 임계값 게이트.

    ★ default mode="mock" — Phase 9.5 mock-deterministic 경로 불변 (behavior-preserving).
    mode="real" 은 **capability** (Phase 10 S3 wire, ADR-033 §1):
      - ctx.llm_caller 주입 + 실 LLM 키(OPENAI/ANTHROPIC) 존재 시에만 real 경로 활성 (opt-in).
      - 키/caller 부재 시 mock 으로 graceful fallback (예외 X) → CI/test 실 호출 0.
      - real 경로는 주입된 caller 가 case → 채점 envelope 합성 (운영 배치 구현). 본 모듈은
        실 client 를 import 하지 않으며 default caller 가 없어 단독 실 호출 불가.

    Args:
        mode: "mock" (deterministic primary) | "real" (실 LLM capability — opt-in).
        cases: 케이스 list 주입 (None → load_golden_set).
        baseline_score: 직전 baseline 평균 canonical 점수 (점수 하락 게이트용, None → 게이트 skip).
        golden_set_path: golden_set.md 경로 (None → 기본).
        include_revise_effect: True → revise effect eval(ADR-033 §2.3) 집계를 result/summary 에 포함.
        ctx: real 모드 컨텍스트 (llm_caller / 환경변수 주입). None → mock 전용.

    Returns:
        {mode, cases: [score_case...], summary: {...}, gate: {passed, violations}}.
        mode 키는 **실효 모드** (real 요청이 graceful fallback 되면 "mock").
        include_revise_effect=True 시 result["revise_effect"](effects + aggregate) 추가 +
        summary["revise_effect"](mean_delta / improved_rate / regressed_rate) 추가.
    """
    # 모드 결정 — requested mode 를 ctx 와 합쳐 실효 모드 산출 (graceful fallback 포함).
    score_ctx = ctx or ScoreContext()
    if score_ctx.requested_mode is None:
        score_ctx = ScoreContext(
            requested_mode=mode,
            llm_caller=score_ctx.llm_caller,
            env=score_ctx.env,
        )
    effective_mode = resolve_mode(score_ctx)  # "mock" | "real" (ValueError on 미지원)

    if cases is None:
        cases = load_golden_set(golden_set_path)

    scored: list[dict[str, Any]] = []
    for case in cases:
        if effective_mode == MODE_REAL:  # pragma: no cover — opt-in 운영 배치 (CI 미실행)
            # capability 경로: 주입된 llm_caller 로 실 LLM 채점 envelope 생성.
            envelope_dict = real_score_envelope(case, score_ctx)
        else:
            envelope_dict = _mock_envelope_for_case(case)
        scored.append(score_case(case, envelope_dict))

    total = len(scored)
    schema_ok_n = sum(1 for s in scored if s["schema_ok"])
    passed_n = sum(1 for s in scored if s["passed"])
    ad_hits = sum(1 for s in scored if s["ad_words"])
    blocked_hits = sum(1 for s in scored if s["blocked_words"])

    p0 = [s for s in scored if s["priority"] == "P0"]
    p0_pass_n = sum(1 for s in p0 if s["passed"])

    # canonical 평균 점수 (structural_score 평균 — mock baseline 대리).
    structural_avg = _avg([s["structural_score"] for s in scored])

    summary = {
        "total": total,
        "schema_rate": round(schema_ok_n / total, 4) if total else 0.0,
        "pass_rate": round(passed_n / total, 4) if total else 0.0,
        "structural_avg": structural_avg,
        "ad_rate": round(ad_hits / total, 4) if total else 0.0,
        "blocked_rate": round(blocked_hits / total, 4) if total else 0.0,
        "p0_total": len(p0),
        "p0_pass_rate": round(p0_pass_n / len(p0), 4) if p0 else 1.0,
        "baseline_score": baseline_score,
    }

    result: dict[str, Any] = {
        "mode": effective_mode,  # 실효 모드 (real 요청이 fallback 되면 "mock").
        "cases": scored,
        "summary": summary,
        "gate": None,  # placeholder — revise effect 반영 후 채운다.
    }

    # revise effect 통합 (ADR-033 §2.3, Phase 4.5 D6) — opt-in.
    if include_revise_effect:
        revise = run_revise_effect_eval()
        result["revise_effect"] = revise
        summary["revise_effect"] = revise["aggregate"]

    result["gate"] = check_thresholds(summary)
    return result


def check_thresholds(summary: dict[str, Any]) -> dict[str, Any]:
    """eval-run §6 임계값 게이트.

    - schema 준수율 < 100% → fail
    - 광고 표현 검출 > 5% → fail
    - 차단 단어 검출 > 0% → fail
    - P0 케이스 통과율 < 100% → fail (즉시 차단)
    - 평균 점수 하락 > 0.3 (baseline_score 제공 시) → fail

    Returns:
        {passed: bool, violations: [str, ...]}.
    """
    violations: list[str] = []

    if summary.get("schema_rate", 0.0) < 1.0:
        violations.append(
            f"schema_rate {summary.get('schema_rate')} < 1.0 (100% 필수)"
        )
    if summary.get("ad_rate", 0.0) > THRESHOLD_AD_RATE:
        violations.append(
            f"ad_rate {summary.get('ad_rate')} > {THRESHOLD_AD_RATE} (광고 표현 검출)"
        )
    if summary.get("blocked_rate", 0.0) > THRESHOLD_BLOCKED_RATE:
        violations.append(
            f"blocked_rate {summary.get('blocked_rate')} > {THRESHOLD_BLOCKED_RATE} (차단 단어 검출)"
        )
    if summary.get("p0_pass_rate", 1.0) < 1.0:
        violations.append(
            f"p0_pass_rate {summary.get('p0_pass_rate')} < 1.0 (P0 즉시 차단)"
        )

    baseline = summary.get("baseline_score")
    if baseline is not None:
        drop = baseline - summary.get("structural_avg", 0.0)
        if drop > THRESHOLD_SCORE_DROP:
            violations.append(
                f"점수 하락 {round(drop, 4)} > {THRESHOLD_SCORE_DROP} (baseline {baseline})"
            )

    return {"passed": len(violations) == 0, "violations": violations}
