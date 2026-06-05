"""HIP-007 S2 — golden_set eval 정식 트리거 entrypoint (mock 기본 + real opt-in).

배경 (meta/audits/2026-06-05.md §D / HIP-007): 실 LLM 회귀가 1회성(mock + Phase 23 1회
baseline)이고 **반복 가능한 정식 경로가 없었다**. 본 모듈이 한 명령 entrypoint 를 제공한다:
  - mock (default): 결정적, CI per-commit 가능, 비용 0 → regression_results 기록.
  - real (--real, opt-in): build_real_llm_caller() 주입 + 키 존재 시에만 실 LLM 채점.
    키 부재 → resolve_mode graceful mock fallback (실 호출 0). 운영 야간 배치용 (NG2).

CLI:
  python -m backend.fastapi.eval.run_eval --trigger hip007-s2 [--real] [--baseline 0.8]
"""

from __future__ import annotations

import logging
from typing import Any, Callable

from .mode import ScoreContext
from .report import write_report
from .runner import run_golden_set_eval

logger = logging.getLogger(__name__)


def build_real_llm_caller() -> Callable[[dict[str, Any]], dict[str, Any]]:
    """real 모드 채점 caller — 기존 파이프라인(run_planning ×3 + run_critic)으로 case→Envelope dict.

    ★ 실 LLM 호출은 반환된 caller 가 invoke 될 때만 발생(키 존재 + resolve_mode=real).
    CI/test 는 키가 없어 resolve_mode 가 mock 으로 fallback → 본 caller 미호출(실 호출 0).
    """

    def _caller(case: dict[str, Any]) -> dict[str, Any]:  # pragma: no cover — 실 LLM(키 필요)
        from ..agents.critic import normalize_to_canonical, run_critic
        from ..agents.planning import _APPROACH_HINTS, run_planning
        from ..schemas.output import (
            Body,
            CriticEvaluation,
            Envelope,
            Meta,
            Plan,
            Validation,
            ValidationCheck,
        )

        user_input = str(case.get("input", ""))
        case_id = str(case.get("id", "GS"))
        plans: list[Plan] = []
        verdicts: list[dict[str, Any]] = []
        for i in range(len(_APPROACH_HINTS)):
            parsed = run_planning(user_input)
            plan_dict = dict(parsed.get("plan") or {})
            plan_dict.setdefault("plan_id", f"{case_id}-plan-{i}")
            plan_dict.setdefault("option_index", i)
            plan = Plan.model_validate(plan_dict)
            plans.append(plan)
            verdicts.append(normalize_to_canonical(run_critic(plan.model_dump())))

        rep = verdicts[0] if verdicts else {}
        critic = CriticEvaluation(
            overall_score=rep.get("overall_score") or 0.0,
            dimensions=rep.get("dimensions") or {},
            overall_verdict=rep.get("overall_verdict") or "approve",
            blocking_issues=rep.get("blocking_issues") or [],
            revise_round=0,
        )
        envelope = Envelope(
            meta=Meta(
                request_id=f"{case_id}-real",
                prompt_id="P-006",
                prompt_version="v1.0.0",
                model="real-llm",
                generated_at="2026-06-05T00:00:00Z",
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
                checks=[ValidationCheck(name="real_eval", status="ok")],
                warnings=[],
            ),
        )
        return envelope.model_dump(mode="json")

    return _caller


def run_and_report(
    *,
    mode: str = "mock",
    trigger: str = "eval-run",
    out_dir: str | None = None,
    baseline_score: float | None = None,
    include_revise_effect: bool = True,
) -> tuple[dict[str, Any], str]:
    """golden_set eval 실행 + regression_results 기록 (한 명령).

    Returns:
        (result, report_path). result["mode"] 는 실효 모드(real 요청이 키 부재로 fallback 시 "mock").
    """
    ctx = ScoreContext(
        requested_mode=mode,
        llm_caller=build_real_llm_caller() if mode == "real" else None,
    )
    result = run_golden_set_eval(
        mode=mode,
        baseline_score=baseline_score,
        include_revise_effect=include_revise_effect,
        ctx=ctx,
    )
    path = write_report(result, trigger=trigger, out_dir=out_dir)
    logger.info(
        "eval done: requested=%s effective=%s gate=%s path=%s",
        mode,
        result["mode"],
        result["gate"]["passed"],
        path,
    )
    return result, path


if __name__ == "__main__":  # pragma: no cover
    import argparse

    parser = argparse.ArgumentParser(description="golden_set eval 정식 트리거 (HIP-007 S2)")
    parser.add_argument(
        "--real", action="store_true", help="real LLM 모드 (키 필요, 없으면 mock fallback)"
    )
    parser.add_argument("--trigger", default="eval-run", help="리포트 파일명 prefix")
    parser.add_argument("--baseline", type=float, default=None, help="점수 하락 게이트용 baseline")
    args = parser.parse_args()
    res, out_path = run_and_report(
        mode="real" if args.real else "mock",
        trigger=args.trigger,
        baseline_score=args.baseline,
    )
    verdict = "pass" if res["gate"]["passed"] else "fail"
    print(f"mode={res['mode']} gate={verdict} -> {out_path}")
