"""Phase 9.5 — regression_results 출력 (eval-run §5 형식).

run_golden_set_eval 결과 → eval/regression_results/{trigger}_{타임스탬프}.md.
eval-run §5 형식: 요약 점수표 + 케이스별 결과 + 임계값 점검 + 결정.

타임스탬프는 인자로 주입 가능 (테스트 결정성 — datetime.now 회피).
trigger 명만 주면 파일명은 `{trigger}.md` (고정).
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# eval/regression_results 기본 위치 (harness 루트 기준).
#   본 파일: harness/backend/fastapi/eval/report.py → parents[3]=harness
_REPO_ROOT = Path(__file__).resolve().parents[3]


def render_report(result: dict[str, Any], *, trigger: str) -> str:
    """run_golden_set_eval 결과 → eval-run §5 형식 markdown 문자열.

    Args:
        result: run_golden_set_eval 반환 dict ({mode, cases, summary, gate}).
        trigger: 트리거 식별자 (phase-9.5_baseline / phase-complete / ...).

    Returns:
        markdown 문자열.
    """
    summary = result.get("summary", {})
    gate = result.get("gate", {})
    cases = result.get("cases", [])
    mode = result.get("mode", "mock")

    verdict = "pass" if gate.get("passed") else "fail"

    lines: list[str] = []
    lines.append(f"# Eval Run: {trigger}")
    lines.append("")
    lines.append(f"- 트리거: {trigger}")
    lines.append(f"- 모드: {mode} (mock-deterministic — 실 LLM 미호출, 비용 0)")
    lines.append(f"- 케이스 수: {summary.get('total', 0)}")
    lines.append("- 비교 대상: canonical-only baseline (ADR-033 / ADR-034 안전망)")
    lines.append("")

    # ── 요약 점수표 ──
    lines.append("## 요약 점수")
    lines.append("")
    lines.append("| 지표 | 값 |")
    lines.append("|---|---|")
    lines.append(f"| schema 준수율 | {_pct(summary.get('schema_rate'))} |")
    lines.append(f"| 케이스 통과율 | {_pct(summary.get('pass_rate'))} |")
    lines.append(f"| structural 평균 | {summary.get('structural_avg')} |")
    lines.append(f"| 광고 표현 검출율 | {_pct(summary.get('ad_rate'))} |")
    lines.append(f"| 차단 단어 검출율 | {_pct(summary.get('blocked_rate'))} |")
    lines.append(f"| P0 통과율 ({summary.get('p0_total', 0)} 케이스) | {_pct(summary.get('p0_pass_rate'))} |")
    if summary.get("baseline_score") is not None:
        lines.append(f"| baseline 점수 | {summary.get('baseline_score')} |")
    lines.append("")

    # ── 케이스별 결과 ──
    lines.append("## 케이스별 결과")
    lines.append("")
    lines.append("| case_id | priority | schema | structural | 광고 | 차단 | 결과 |")
    lines.append("|---|---|---|---|---|---|---|")
    for c in cases:
        ad = ", ".join(c.get("ad_words", [])) or "-"
        blocked = ", ".join(c.get("blocked_words", [])) or "-"
        result_mark = "pass" if c.get("passed") else "fail"
        lines.append(
            f"| {c.get('case_id')} | {c.get('priority')} | "
            f"{'ok' if c.get('schema_ok') else 'FAIL'} | "
            f"{c.get('structural_score')} | {ad} | {blocked} | {result_mark} |"
        )
    lines.append("")

    # ── 임계값 점검 ──
    lines.append("## 임계값 점검 (eval-run §6)")
    lines.append("")
    lines.append(f"- schema 준수율 < 100%: {_gate_mark(summary.get('schema_rate', 0.0) >= 1.0)}")
    lines.append(f"- 광고 표현 검출 > 5%: {_gate_mark(summary.get('ad_rate', 0.0) <= 0.05)}")
    lines.append(f"- 차단 단어 검출 > 0%: {_gate_mark(summary.get('blocked_rate', 0.0) <= 0.0)}")
    lines.append(f"- P0 통과율 < 100%: {_gate_mark(summary.get('p0_pass_rate', 1.0) >= 1.0)}")
    lines.append("")
    if gate.get("violations"):
        lines.append("### 위반 항목")
        lines.append("")
        for v in gate["violations"]:
            lines.append(f"- {v}")
        lines.append("")

    # ── 결정 ──
    lines.append("## 결정")
    lines.append("")
    lines.append(f"{verdict}")
    lines.append("")
    lines.append("## 후속 액션")
    lines.append("")
    if verdict == "pass":
        lines.append(
            "- canonical-only 품질 baseline 확정 (Slice 4 Critic deprecated 0–5 제거 검증 기준)."
        )
    else:
        lines.append("- 위반 항목 분석 → bug-triage / 수정 후 재실행.")
    lines.append("")

    return "\n".join(lines)


def write_report(
    result: dict[str, Any],
    *,
    trigger: str,
    out_dir: str | None = None,
) -> str:
    """eval-run §5 형식 리포트를 eval/regression_results/{trigger}.md 로 출력.

    Args:
        result: run_golden_set_eval 반환 dict.
        trigger: 트리거 식별자 (파일명 prefix, 타임스탬프 없이 고정 — 테스트 결정성).
        out_dir: 출력 디렉토리 (None → eval/regression_results).

    Returns:
        생성된 파일 절대 경로 (str).
    """
    target_dir = Path(out_dir) if out_dir else _REPO_ROOT / "eval" / "regression_results"
    target_dir.mkdir(parents=True, exist_ok=True)

    content = render_report(result, trigger=trigger)
    out_path = target_dir / f"{trigger}.md"
    out_path.write_text(content, encoding="utf-8")
    logger.info("eval report 생성: %s", out_path)
    return str(out_path)


def _pct(value: float | None) -> str:
    if value is None:
        return "-"
    return f"{round(value * 100, 1)}%"


def _gate_mark(ok: bool) -> str:
    return "PASS" if ok else "FAIL"
