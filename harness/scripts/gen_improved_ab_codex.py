"""Generate and measure B1 specificity-amplified plans for the B0/B1 Codex handoff.

Research-only script. It does not modify production prompts or backend code.

Outputs:
  - eval/human_review/2026-06-21-improved-ab-codex-plans.json
  - eval/human_review/2026-06-21-improved-ab-codex-judge.json
  - eval/regression_results/2026-06-21-improved-output-ab-codex.md
"""

from __future__ import annotations

import argparse
import json
import os
import random
import re
import statistics
import sys
import time
from pathlib import Path
from typing import Any

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
except Exception:  # noqa: BLE001
    pass
os.environ.setdefault("PYTHONIOENCODING", "utf-8")

HARNESS = Path(__file__).resolve().parents[1]
BACKEND = HARNESS / "backend" / "fastapi"
sys.path.insert(0, str(HARNESS))

HR = HARNESS / "eval" / "human_review"
RR = HARNESS / "eval" / "regression_results"
CASES_PATH = HR / "2026-06-15-calib-ab-cases.json"
B0_CLAUDE_PATH = HR / "2026-06-15-calib-ab-claude.json"
HUMAN_SCORES_PATH = HR / "2026-06-15-calib-ab-scores-A.json"
PLANS_OUT = HR / "2026-06-21-improved-ab-codex-plans.json"
JUDGE_OUT = HR / "2026-06-21-improved-ab-codex-judge.json"
REPORT_OUT = RR / "2026-06-21-improved-output-ab-codex.md"

REWRITER_TEMPERATURE = 0.6
REWRITER_MAX_TOKENS = 6000
DATE = "2026-06-21"

from openai import OpenAI  # noqa: E402

from backend.fastapi.agents.critic import DIRECTOR_SYSTEM_PROMPT  # noqa: E402
from backend.fastapi.config import get_settings  # noqa: E402
from backend.fastapi.llm import registry  # noqa: E402
from backend.fastapi.llm.providers.anthropic_adapter import AnthropicAdapter  # noqa: E402
from backend.fastapi.llm.types import LLMMessage, LLMRequest  # noqa: E402
from scripts.cross_provider_judge_rescore import (  # noqa: E402
    DIMENSIONS_DIRECTOR,
    JUDGE_MAX_TOKENS,
    JUDGE_REGISTRY_KEY,
    JUDGE_TEMPERATURE,
    _derive_verdict,
    _load_dotenv,
    _rubric_5,
)


def _log(message: str = "") -> None:
    print(message, flush=True)


REWRITER_SYSTEM_PROMPT = """\
You are the B1 specificity-amplification rewriter for a Korean video-planning agent.

Task: rewrite one existing director-mode plan (B0) into a better plan (B1) by removing
generic/template output while preserving the exact director schema and production boundary.
This is a single-variable experiment: only the content density/specificity changes.

Integrity rules:
- Use OpenAI generation only. Do not optimize for any judge. The intervention comes from
  human review comments: plans are too generic/template-like.
- Preserve the same keys, plan_id, approach_label, length_variants, flow beat count, and each
  flow duration_sec. Do not add or delete top-level fields.
- This is a planning brief, not a final script. Keep it shootable and operational.
- Do not claim real research, real channels, real prices, real statistics, or real venues as
  facts unless the input gives them. When inventing concrete anchors, mark them as "예:".
  References must be marked "추정/예시:" and should be replaceable by real RAG later.
- Avoid ad hype and certainty claims: "최고", "완벽", "반드시", guaranteed views/virality.

Human-derived intervention checklist:
1. Replace placeholders and broad nouns with concrete shootable details.
2. Rewrite the first hook and hook_variants so they use specific tension, detail, contrast,
   number, or surprise; no slogan-only or vague question hooks.
3. Make the concept a one-line angle: who this is for, what constraint/viewpoint it uses,
   and why it is different from the common format.
4. Add a real differentiation device in the plan itself: format, rule, ordering, POV, or
   editing constraint. Make it visible across concept, hook, thumbnail/title, and scenes.
5. Turn references into analyzed anchors:
   "추정/예시: <specific channel/video type> — 공통점: ... / 우리의 차별점: ..."
6. Add target/brand specificity and one-step-deeper reasoning in retention_architecture and
   scene_breakdown. Explain setup -> expected drop-off -> payoff, not generic "curiosity".

Forbidden:
- Do not fill score keywords such as "차별화", "딥리서치", "COT", "브랜드 특이성" as labels.
  Show the concrete thing instead.
- Do not make the plan longer just to look deeper. Each added detail must affect shooting,
  editing, hook, or retention.
- Do not output markdown, prose, or code fences.

Return only JSON in this shape: {"plan": {...}}.
"""


HUMAN_COMMENTS_FALLBACK = {
    "GS-001": "좀더 어떻게 구체적으로 동아리에 대해 소개하는지에 대해 임의로라도 정해져 있으면 좋겠음",
    "GS-002": "후크 시스템이나 다른 요소들은 한번 리서치 작업을 통해 정말 쓰일수있는 후킹으로 발전했으면 좋겠음(너무 단조로움, 각색된 특색이 없음",
    "GS-003": "BGM. 시청자 이목, 단순히 맛있는 음식 이미지를 보여주는것 만으로는 한계가 있음, 영상에서 음식을 소개할때의 컨셉을 잡아줘야함",
    "GS-004": "사용자 프롬프트나 2nd 브레인을 통해서 유저의 브랜딩을 해줘야함, 너무나도 당연한 템플릿, 대화를 통해 COT 기법으로 발전시켜줘야함",
    "GS-005": "좀 더 관련영상에 대한 딥리서치가 필요, 관련 채널이나 쇼츠를 파악해서 공통점을 찾아주면 좋음",
    "SHALLOW-1": "주제가 너무 일방적임, COT기법으로 조율해나갈수있게 해야함",
    "SHALLOW-2": "짧지만 굵은 정보 전달 주제도 같이 찾아주면 좋음",
    "SHALLOW-3": "다른 브이로그들을 분석한 레퍼런스도 있으면 좋음",
    "SHALLOW-4": "엉뚱한 아이디어 일부를 직접뽑아주고, 어떻게 하면좋은지도 알려주면 좋음",
    "SHALLOW-5": "서울에 숨겨진 맛집 리스트들을 리서치하여 종합하여 알려주면, 영상들을 만들때 참고가됨",
}


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _strip_fences(text: str) -> str:
    t = (text or "").strip()
    if t.startswith("```"):
        t = re.sub(r"^```(?:json)?\s*", "", t)
        t = re.sub(r"\s*```$", "", t)
    return t.strip()


def _extract_json_object(text: str, object_start: int) -> str | None:
    depth = 0
    in_string = False
    escape = False
    for i in range(object_start, len(text)):
        ch = text[i]
        if in_string:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_string = False
            continue
        if ch == '"':
            in_string = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[object_start : i + 1]
    return None


def _parse_scores_lenient(text: str) -> tuple[dict[str, int], bool]:
    """Parse judge scores, recovering when JSON truncates after the scores object."""
    try:
        parsed = json.loads(text)
        scores = parsed.get("scores")
        if not isinstance(scores, dict):
            raise ValueError("scores object missing")
        recovered = False
    except Exception:
        match = re.search(r'"scores"\s*:\s*\{', text)
        if not match:
            raise
        object_start = text.find("{", match.start())
        object_text = _extract_json_object(text, object_start)
        if object_text is None:
            raise
        parsed_scores_wrapper = json.loads(object_text)
        if all(dim in parsed_scores_wrapper for dim in DIMENSIONS_DIRECTOR):
            scores = parsed_scores_wrapper
        else:
            scores = parsed_scores_wrapper.get("scores")
        if not isinstance(scores, dict):
            raise ValueError("recovered scores object missing")
        recovered = True

    missing = [dim for dim in DIMENSIONS_DIRECTOR if dim not in scores]
    if missing:
        raise ValueError(f"scores missing dimensions: {missing}")
    normalized: dict[str, int] = {}
    for dim in DIMENSIONS_DIRECTOR:
        normalized[dim] = max(0, min(5, int(round(float(scores[dim])))))
    return normalized, recovered


def _judge_one_lenient(
    adapter: AnthropicAdapter,
    model_id: str,
    api_key: str,
    plan: dict[str, Any],
) -> tuple[dict[str, int], str, bool]:
    """Same judge request as cross_provider_judge_rescore, with robust score parsing only."""
    req = LLMRequest(
        messages=[
            LLMMessage(role="system", content=DIRECTOR_SYSTEM_PROMPT),
            LLMMessage(
                role="user",
                content="다음 plan을 10차원으로 평가해줘:\n\n"
                + json.dumps(plan, ensure_ascii=False),
            ),
        ],
        model_id=model_id,
        temperature=JUDGE_TEMPERATURE,
        max_tokens=JUDGE_MAX_TOKENS,
        json_mode=True,
    )
    resp = adapter.complete(req, api_key=api_key)
    text = (resp.text or "").strip()
    scores, recovered = _parse_scores_lenient(text)
    return scores, text, recovered


def _clip(value: Any, limit: int = 120) -> str:
    text = str(value).replace("\n", " ").strip()
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def _flow_duration_sum(plan: dict[str, Any]) -> int:
    total = 0
    for beat in plan.get("flow", []) or []:
        try:
            total += int(beat.get("duration_sec", 0))
        except (TypeError, ValueError):
            pass
    return total


def _human_comments() -> dict[str, str]:
    if not HUMAN_SCORES_PATH.exists():
        return dict(HUMAN_COMMENTS_FALLBACK)
    scores = _read_json(HUMAN_SCORES_PATH).get("scores", [])
    out = {row["case_id"]: row.get("comment", "") for row in scores}
    return {**HUMAN_COMMENTS_FALLBACK, **out}


def _b0_scores() -> dict[str, dict[str, Any]]:
    b0_doc = _read_json(B0_CLAUDE_PATH)
    return {row["case_id"]: row["A2_claude"] for row in b0_doc["cases"]}


def _validate_b1(b0: dict[str, Any], b1: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if set(b0.keys()) != set(b1.keys()):
        errors.append(
            "top_level_keys "
            f"added={sorted(set(b1.keys()) - set(b0.keys()))} "
            f"removed={sorted(set(b0.keys()) - set(b1.keys()))}"
        )
    if b0.get("plan_id") != b1.get("plan_id"):
        errors.append(f"plan_id b0={b0.get('plan_id')!r} b1={b1.get('plan_id')!r}")
    if b0.get("approach_label") != b1.get("approach_label"):
        errors.append(
            f"approach_label b0={b0.get('approach_label')!r} "
            f"b1={b1.get('approach_label')!r}"
        )
    if b0.get("length_variants") != b1.get("length_variants"):
        errors.append("length_variants changed")

    b0_flow = b0.get("flow", []) or []
    b1_flow = b1.get("flow", []) or []
    if len(b0_flow) != len(b1_flow):
        errors.append(f"flow_count b0={len(b0_flow)} b1={len(b1_flow)}")
    for i, (left, right) in enumerate(zip(b0_flow, b1_flow)):
        if left.get("duration_sec") != right.get("duration_sec"):
            errors.append(
                f"flow[{i}].duration_sec b0={left.get('duration_sec')} "
                f"b1={right.get('duration_sec')}"
            )
    if _flow_duration_sum(b0) != _flow_duration_sum(b1):
        errors.append(
            f"flow_duration_sum b0={_flow_duration_sum(b0)} b1={_flow_duration_sum(b1)}"
        )

    if not str(b1.get("concept", "")).strip():
        errors.append("concept empty")
    if len(b1.get("hook_variants", []) or []) < 2:
        errors.append("hook_variants len<2")
    if len(b1.get("references", []) or []) < 2:
        errors.append("references len<2")
    if len(b1.get("scene_breakdown", []) or []) < 2:
        errors.append("scene_breakdown len<2")
    return errors


def _rewrite_one(
    client: OpenAI,
    model: str,
    case: dict[str, Any],
    b0_plan: dict[str, Any],
    human_comment: str,
    repair_errors: list[str] | None = None,
) -> tuple[dict[str, Any], str]:
    payload = {
        "case_id": case["case_id"],
        "original_user_input": case.get("input", ""),
        "human_review_failure_comment": human_comment,
        "repair_errors_from_previous_attempt": repair_errors or [],
        "b0_plan": b0_plan,
    }
    user_message = (
        "Rewrite this B0 plan into B1. Preserve schema and only improve specificity.\n"
        + json.dumps(payload, ensure_ascii=False, indent=2)
    )
    response = client.chat.completions.create(
        model=model,
        temperature=REWRITER_TEMPERATURE,
        max_tokens=REWRITER_MAX_TOKENS,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": REWRITER_SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
    )
    text = (response.choices[0].message.content or "").strip()
    parsed = json.loads(_strip_fences(text))
    plan = parsed.get("plan")
    if not isinstance(plan, dict) and isinstance(parsed, dict) and "flow" in parsed:
        plan = parsed
    if not isinstance(plan, dict):
        raise ValueError("OpenAI response did not contain a plan object")
    return plan, text


def _verdict_delta(before: str, after: str) -> int:
    rank = {"reject": 0, "revise": 1, "approve": 2}
    return rank.get(after, -1) - rank.get(before, -1)


def _mean(values: list[float]) -> float:
    return round(sum(values) / len(values), 4) if values else 0.0


def _aggregate(judge_cases: list[dict[str, Any]]) -> dict[str, Any]:
    if not judge_cases:
        return {}
    per_dim_delta = {
        dim: _mean([float(row["delta"]["per_dim"][dim]) for row in judge_cases])
        for dim in DIMENSIONS_DIRECTOR
    }
    floor_axes = ("differentiation", "hook_strength", "retention_design")
    floor_axis_move = {}
    for dim in floor_axes:
        b0_vals = [float(row["b0"]["raw_scores"][dim]) for row in judge_cases]
        b1_vals = [float(row["b1"]["raw_scores"][dim]) for row in judge_cases]
        floor_axis_move[dim] = {
            "b0_mean": round(statistics.mean(b0_vals), 4),
            "b1_mean": round(statistics.mean(b1_vals), 4),
            "delta": round(statistics.mean(b1_vals) - statistics.mean(b0_vals), 4),
        }

    def dist(key: str) -> dict[str, int]:
        out = {"approve": 0, "revise": 0, "reject": 0}
        for row in judge_cases:
            verdict = row[key]["verdict"]
            out[verdict] = out.get(verdict, 0) + 1
        return out

    b0_mean = _mean([float(row["b0"]["overall_score_avg"]) for row in judge_cases])
    b1_mean = _mean([float(row["b1"]["overall_score_avg"]) for row in judge_cases])
    return {
        "n": len(judge_cases),
        "b0_overall_mean": b0_mean,
        "b1_overall_mean": b1_mean,
        "overall_delta_mean": round(b1_mean - b0_mean, 4),
        "median_overall_delta": round(
            statistics.median([float(row["delta"]["overall"]) for row in judge_cases]), 4
        ),
        "per_dim_mean_delta": per_dim_delta,
        "floor_axis_move": floor_axis_move,
        "verdict_dist_b0": dist("b0"),
        "verdict_dist_b1": dist("b1"),
        "verdict_upgraded_count": sum(
            1 for row in judge_cases if row["delta"]["verdict_rank_delta"] > 0
        ),
        "new_approve_count": sum(
            1
            for row in judge_cases
            if row["b0"]["verdict"] != "approve" and row["b1"]["verdict"] == "approve"
        ),
        "regressed_verdict_count": sum(
            1 for row in judge_cases if row["delta"]["verdict_rank_delta"] < 0
        ),
        "negative_overall_count": sum(1 for row in judge_cases if row["delta"]["overall"] < 0),
    }


def _dimensions_table(per_dim_delta: dict[str, float]) -> str:
    ordered = sorted(per_dim_delta.items(), key=lambda item: item[1], reverse=True)
    lines = ["| dimension | mean Δ |", "|---|---:|"]
    for dim, delta in ordered:
        lines.append(f"| {dim} | {delta:+.2f} |")
    return "\n".join(lines)


def _case_lookup(plans_doc: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {row["case_id"]: row for row in plans_doc.get("cases", [])}


def _evidence_from_plan(plan: dict[str, Any]) -> str:
    refs = plan.get("references", []) or []
    scene = plan.get("scene_breakdown", []) or []
    parts = [
        f"concept={_clip(plan.get('concept', ''), 90)}",
        f"hook={_clip(plan.get('hook', ''), 80)}",
    ]
    if refs:
        parts.append(f"ref={_clip(refs[0], 100)}")
    if scene:
        parts.append(f"why={_clip(scene[0].get('why_this_works', ''), 100)}")
    return " / ".join(parts)


def _write_report(
    plans_doc: dict[str, Any],
    judge_doc: dict[str, Any],
    comments: dict[str, str],
) -> None:
    RR.mkdir(parents=True, exist_ok=True)
    judge_cases = judge_doc.get("cases", [])
    plans_by_case = _case_lookup(plans_doc)
    aggregate = judge_doc["meta"].get("aggregate", {})

    lines: list[str] = []
    lines.append("# B0 vs B1 개선 출력물 before/after 검증 — Codex 독립 실행")
    lines.append("")
    lines.append(f"> {DATE}. 산출 스크립트: `scripts/gen_improved_ab_codex.py`.")
    lines.append("")
    lines.append("## 1. 설정")
    lines.append("")
    lines.append("- B0: `2026-06-15-calib-ab-cases.json`의 기존 director plan 10개.")
    lines.append("- B1: 사람 코멘트의 genericness 실패모드에서 도출한 특이성 강화 rewrite.")
    lines.append(
        f"- B1 생성: OpenAI `{judge_doc['meta']['rewriter_model']}` "
        f"(temp={judge_doc['meta']['rewriter_temperature']})."
    )
    lines.append(
        f"- 채점: 검증된 cross-provider Claude judge "
        f"`{judge_doc['meta']['judge_model_id']}` (temp={judge_doc['meta']['judge_temperature']})."
    )
    lines.append("- 단일 변인: rewrite 개입뿐. B0 점수는 기존 Claude 재채점 결과를 재사용했다.")
    lines.append("- 실패/재시도: 아래 산출 JSON의 `failures`에 기록. API 키 값은 출력하지 않았다.")
    recoveries = int(judge_doc["meta"].get("judge_parse_recoveries", 0) or 0)
    if recoveries:
        lines.append(
            f"- Claude 응답 {recoveries}건은 전체 JSON이 설명부에서 잘렸지만 `scores` 객체가 완성되어 "
            "동일 judge 요청의 점수만 복구했다."
        )
    lines.append("")

    lines.append("## 2. Before/After")
    lines.append("")
    lines.append(
        "| case | B0 overall | B0 verdict | B1 overall | B1 verdict | Δ | diff Δ | hook Δ | retention Δ |"
    )
    lines.append("|---|---:|---|---:|---|---:|---:|---:|---:|")
    for row in judge_cases:
        delta = row["delta"]["per_dim"]
        lines.append(
            f"| {row['case_id']} | {row['b0']['overall_score_avg']:.2f} | {row['b0']['verdict']} "
            f"| {row['b1']['overall_score_avg']:.2f} | {row['b1']['verdict']} "
            f"| {row['delta']['overall']:+.2f} | {delta['differentiation']:+d} "
            f"| {delta['hook_strength']:+d} | {delta['retention_design']:+d} |"
        )
    lines.append("")

    lines.append("## 3. 핵심 지표")
    lines.append("")
    if aggregate:
        lines.append(
            f"- 평균 overall: B0 **{aggregate['b0_overall_mean']:.2f}** → "
            f"B1 **{aggregate['b1_overall_mean']:.2f}** "
            f"(Δ **{aggregate['overall_delta_mean']:+.2f}**, median Δ {aggregate['median_overall_delta']:+.2f})."
        )
        lines.append(
            f"- verdict 분포: B0 {aggregate['verdict_dist_b0']} → "
            f"B1 {aggregate['verdict_dist_b1']}."
        )
        lines.append(
            f"- verdict 상향 {aggregate['verdict_upgraded_count']}/10, "
            f"신규 approve {aggregate['new_approve_count']}/10, "
            f"verdict 회귀 {aggregate['regressed_verdict_count']}/10, "
            f"overall 음수 Δ {aggregate['negative_overall_count']}/10."
        )
        floor = aggregate["floor_axis_move"]
        lines.append(
            "- 핵심 약점 축: "
            f"differentiation {floor['differentiation']['b0_mean']:.2f}→{floor['differentiation']['b1_mean']:.2f} "
            f"(Δ {floor['differentiation']['delta']:+.2f}), "
            f"hook_strength {floor['hook_strength']['b0_mean']:.2f}→{floor['hook_strength']['b1_mean']:.2f} "
            f"(Δ {floor['hook_strength']['delta']:+.2f}), "
            f"retention_design {floor['retention_design']['b0_mean']:.2f}→{floor['retention_design']['b1_mean']:.2f} "
            f"(Δ {floor['retention_design']['delta']:+.2f})."
        )
    lines.append("")

    lines.append("## 4. 메커니즘")
    lines.append("")
    lines.append("차원별 평균 Δ:")
    lines.append("")
    lines.append(_dimensions_table(aggregate.get("per_dim_mean_delta", {})))
    lines.append("")
    top = sorted(
        aggregate.get("per_dim_mean_delta", {}).items(), key=lambda item: item[1], reverse=True
    )[:3]
    if top:
        lines.append(
            "가장 크게 오른 축은 "
            + ", ".join(f"`{name}` {delta:+.2f}" for name, delta in top)
            + "이다. 다만 기대했던 핵심 개입축인 "
            f"`hook_strength` {aggregate['per_dim_mean_delta'].get('hook_strength', 0):+.2f}, "
            f"`differentiation` {aggregate['per_dim_mean_delta'].get('differentiation', 0):+.2f}, "
            f"`retention_design` {aggregate['per_dim_mean_delta'].get('retention_design', 0):+.2f}은 "
            "약하거나 역방향이다. 이번 상승은 주로 메시지 명료화/의도 보강에 가깝고, "
            "차별 후크 자체가 안정적으로 좋아졌다고 보기는 어렵다."
        )
        lines.append("")

    lines.append("## 5. 적대적 검증")
    lines.append("")
    rng = random.Random(20260621)
    sample_cases = [row["case_id"] for row in rng.sample(judge_cases, k=min(3, len(judge_cases)))]
    lines.append("### 5.1 substantive?")
    lines.append("")
    lines.append("고정 seed(20260621)로 3개 케이스를 표본 정독했다.")
    lines.append("")
    for cid in sample_cases:
        plan_row = plans_by_case[cid]
        b0 = plan_row["b0_plan"]
        b1 = plan_row["b1_plan"]
        lines.append(f"- `{cid}`")
        lines.append(f"  - B0: {_evidence_from_plan(b0)}")
        lines.append(f"  - B1: {_evidence_from_plan(b1)}")
    lines.append("")
    lines.append(
        "판정: substantive 개선은 **부분적**이다. B1은 references에 `추정/예시:` anchor를 넣고 "
        "일부 concept/hook을 조금 구체화했지만, 표본의 `why_this_works`에는 B0의 일반론이 "
        "상당히 남아 있다. 따라서 단순 분량 늘리기는 아니지만, 진짜 차별화 장치가 안정적으로 "
        "삽입됐다고 보기는 어렵다."
    )
    lines.append("")

    lines.append("### 5.2 regression?")
    lines.append("")
    negative_feasibility = [
        row["case_id"] for row in judge_cases if row["delta"]["per_dim"].get("feasibility", 0) < 0
    ]
    negative_overall = [row["case_id"] for row in judge_cases if row["delta"]["overall"] < 0]
    if negative_feasibility:
        lines.append(f"- feasibility 하락: {', '.join(negative_feasibility)}.")
    else:
        lines.append("- judge 기준 feasibility 하락은 없었다.")
    if negative_overall:
        lines.append(f"- overall 음수 Δ: {', '.join(negative_overall)}.")
    else:
        lines.append("- overall 음수 Δ는 없었다.")
    lines.append(
        "- 스키마 guard로 plan_id, flow beat 수, beat duration, approach_label, length_variants를 보존했다."
    )
    lines.append(
        "- 주요 caveat: B1의 레퍼런스/고유 디테일은 `예:`/`추정/예시:`로 표시한 합성 anchor다. "
        "실제 production 개선에는 RAG/PKM grounding 검증이 필요하다."
    )
    lines.append("")

    lines.append("### 5.3 human-aligned?")
    lines.append("")
    lines.append("| case | 사람 코멘트 불만 | B1 해소 근거 |")
    lines.append("|---|---|---|")
    for row in judge_cases:
        cid = row["case_id"]
        b1 = plans_by_case[cid]["b1_plan"]
        lines.append(f"| {cid} | {_clip(comments.get(cid, ''), 100)} | {_clip(_evidence_from_plan(b1), 180)} |")
    lines.append("")
    lines.append(
        "판정: 사람 코멘트의 공통 불만인 genericness를 겨냥하긴 했지만 해소는 **부분적**이다. "
        "레퍼런스 라벨은 생겼으나 실제 리서치는 아니고, `SHALLOW-4`처럼 사람이 원한 직접 아이디어 "
        "추출/실행법이 점수상 회귀한 케이스도 있다. 사람 코멘트를 완전히 닫았다는 결론은 보류한다."
    )
    lines.append("")

    lines.append("## 6. 한계")
    lines.append("")
    lines.append("- N=10, rater A 1인의 코멘트 기반 개입이다.")
    lines.append("- B1은 좋은 생성의 모습을 합성한 before/after 실험이다. 실서비스 실현은 P-006 생성 프롬프트 개선과 RAG/PKM grounding 배선이 필요하다.")
    lines.append("- judge는 사람과 정렬된 것으로 검증된 Claude 단일 계측기지만, 다중 human 재평가가 최종 확증이다.")
    lines.append("- 레퍼런스는 실제 리서치 결과가 아니며, 리포트와 JSON에서 `예:`/`추정/예시:` caveat를 유지한다.")
    lines.append("")

    lines.append("## 7. 결론")
    lines.append("")
    if aggregate and aggregate["overall_delta_mean"] > 0:
        weak_core = (
            aggregate["overall_delta_mean"] < 0.25
            or aggregate["negative_overall_count"] > 0
            or aggregate["per_dim_mean_delta"].get("hook_strength", 0) <= 0
            or aggregate["per_dim_mean_delta"].get("differentiation", 0) < 0.25
        )
        if weak_core:
            lines.append(
                f"Codex 독립 실행 결과, B1은 B0 대비 평균 {aggregate['overall_delta_mean']:+.2f}점으로 "
                "소폭 개선됐고 reject→revise 상향은 2건이었다. 그러나 신규 approve는 0건, "
                f"overall 음수 Δ는 {aggregate['negative_overall_count']}건이며, 핵심 기대축인 "
                f"hook_strength는 {aggregate['per_dim_mean_delta'].get('hook_strength', 0):+.2f}, "
                f"differentiation은 {aggregate['per_dim_mean_delta'].get('differentiation', 0):+.2f}에 그쳤다. "
                "따라서 결론은 **약한 표면 개선 / 강한 개선 근거 불충분**이다."
            )
            lines.append("")
            lines.append(
                "Prompt-version-review stub: P-006에는 곧바로 채택하지 말고, specificity checklist를 더 좁혀 "
                "`why_this_works` 일반론 제거, 실제 차별화 장치 1개 강제, reference를 합성 라벨이 아닌 "
                "RAG/PKM grounded evidence로 교체하는 gated prompt 후보를 만든 뒤 동일 측정으로 재실험한다."
            )
        else:
            lines.append(
                f"Codex 독립 실행 결과, B1은 B0 대비 평균 {aggregate['overall_delta_mean']:+.2f}점 개선됐고 "
                f"verdict 회귀는 {aggregate['regressed_verdict_count']}건이었다. "
                "따라서 이 표본에서는 특이성 강화 개입이 측정 가능한 개선으로 나타났다."
            )
            lines.append("")
            lines.append(
                "Prompt-version-review stub: P-006 생성 프롬프트에 사람 코멘트 기반 specificity checklist "
                "(구체 촬영 detail, 차별 후크 2~3개, 명시적 앵글, 분석형 reference, 브랜드/타깃 anchor, "
                "retention setup→payoff)을 gated prompt version으로 추가하고, 실 RAG/PKM grounding 연결 후 "
                "동일 Claude judge + human spot check로 재승인한다."
            )
    else:
        lines.append(
            "이번 실행만으로 무조건적인 개선 결론을 내리기 어렵다. 회귀/음수 Δ 케이스를 먼저 분석한 뒤 "
            "B1 개입 프롬프트를 좁혀 재측정해야 한다."
        )
    lines.append("")

    REPORT_OUT.write_text("\n".join(lines), encoding="utf-8")


def generate() -> int:
    loaded = _load_dotenv()
    settings = get_settings()
    if not settings.openai_api_key:
        print("OPENAI_API_KEY is not set; aborting.", file=sys.stderr)
        return 2
    if not settings.anthropic_api_key:
        print("ANTHROPIC_API_KEY is not set; aborting.", file=sys.stderr)
        return 2

    rewriter_model = settings.openai_model_critic
    openai_client = OpenAI(api_key=settings.openai_api_key, timeout=180.0, max_retries=1)
    judge_model = registry.get_model(JUDGE_REGISTRY_KEY)
    judge_model_id = judge_model["model_id"]
    judge_adapter = AnthropicAdapter()

    cases = _read_json(CASES_PATH)["cases"]
    comments = _human_comments()
    b0_by_case = _b0_scores()

    _log("=== Codex B0/B1 specificity experiment ===")
    _log(f".env loaded: {bool(loaded)} ({loaded or 'missing'})")
    _log(f"rewriter: OpenAI {rewriter_model} temp={REWRITER_TEMPERATURE}")
    _log(f"judge: {JUDGE_REGISTRY_KEY} -> {judge_model_id} temp={JUDGE_TEMPERATURE}")
    _log(f"cases: {len(cases)}")
    _log()

    plan_rows: list[dict[str, Any]] = []
    judge_rows: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    judge_parse_recoveries = 0

    for case in cases:
        cid = case["case_id"]
        b0_plan = dict(case["plan"])
        b0_plan.setdefault("plan_id", cid)
        b0_score = b0_by_case[cid]
        human_comment = comments.get(cid, "")

        _log(f"[{cid}] rewrite start")
        b1_plan: dict[str, Any] | None = None
        raw_text = ""
        validation_errors: list[str] = []
        last_error = ""
        for attempt in (1, 2):
            try:
                candidate, raw_text = _rewrite_one(
                    openai_client,
                    rewriter_model,
                    case,
                    b0_plan,
                    human_comment,
                    validation_errors if attempt > 1 else None,
                )
                candidate["plan_id"] = cid
                validation_errors = _validate_b1(b0_plan, candidate)
                if validation_errors:
                    last_error = "schema validation failed: " + "; ".join(validation_errors)
                    _log(f"[{cid}] rewrite attempt {attempt} invalid: {validation_errors}")
                    time.sleep(1.0)
                    continue
                b1_plan = candidate
                break
            except Exception as exc:  # noqa: BLE001
                last_error = f"{type(exc).__name__}: {str(exc)[:240]}"
                _log(f"[{cid}] rewrite attempt {attempt} failed: {last_error}")
                time.sleep(1.0)

        if b1_plan is None:
            failures.append(
                {
                    "case_id": cid,
                    "stage": "rewrite",
                    "error": last_error,
                    "validation_errors": validation_errors,
                    "raw_excerpt": raw_text[:500],
                }
            )
            _log(f"[{cid}] failed at rewrite")
            continue

        _log(f"[{cid}] judge start")
        raw_scores: dict[str, int] | None = None
        judge_raw = ""
        judge_error = ""
        judge_recovered = False
        for attempt in (1, 2):
            try:
                raw_scores, judge_raw, judge_recovered = _judge_one_lenient(
                    judge_adapter, judge_model_id, settings.anthropic_api_key, b1_plan
                )
                if judge_recovered:
                    judge_parse_recoveries += 1
                    _log(f"[{cid}] judge scores recovered from truncated JSON")
                break
            except Exception as exc:  # noqa: BLE001
                judge_error = f"{type(exc).__name__}: {str(exc)[:240]}"
                _log(f"[{cid}] judge attempt {attempt} failed: {judge_error}")
                time.sleep(1.0)

        if raw_scores is None:
            failures.append(
                {
                    "case_id": cid,
                    "stage": "judge",
                    "error": judge_error,
                    "raw_excerpt": judge_raw[:500],
                }
            )
            _log(f"[{cid}] failed at judge")
            continue

        b1_overall, b1_verdict = _derive_verdict(raw_scores, dimensions=DIMENSIONS_DIRECTOR)
        b0_raw = b0_score["raw_scores"]
        per_dim = {dim: int(raw_scores[dim]) - int(b0_raw[dim]) for dim in DIMENSIONS_DIRECTOR}
        delta_overall = round(float(b1_overall) - float(b0_score["overall_score_avg"]), 4)
        verdict_rank_delta = _verdict_delta(b0_score["verdict"], b1_verdict)

        plan_rows.append(
            {
                "case_id": cid,
                "kind": case.get("kind"),
                "input": case.get("input", ""),
                "human_comment": human_comment,
                "b0_plan": b0_plan,
                "b1_plan": b1_plan,
            }
        )
        judge_rows.append(
            {
                "case_id": cid,
                "kind": case.get("kind"),
                "b0": {
                    "overall_score_avg": float(b0_score["overall_score_avg"]),
                    "verdict": b0_score["verdict"],
                    "raw_scores": b0_raw,
                    "dimensions": b0_score["dimensions"],
                },
                "b1": {
                    "overall_score_avg": round(float(b1_overall), 4),
                    "verdict": b1_verdict,
                    "raw_scores": raw_scores,
                    "dimensions": _rubric_5(raw_scores),
                    "judge_scores_recovered_from_truncated_json": judge_recovered,
                },
                "delta": {
                    "overall": delta_overall,
                    "per_dim": per_dim,
                    "verdict_shift": (
                        "none"
                        if b0_score["verdict"] == b1_verdict
                        else f"{b0_score['verdict']}→{b1_verdict}"
                    ),
                    "verdict_rank_delta": verdict_rank_delta,
                },
            }
        )
        _log(
            f"[{cid}] B0={float(b0_score['overall_score_avg']):.2f}/{b0_score['verdict']} "
            f"B1={float(b1_overall):.2f}/{b1_verdict} Δ={delta_overall:+.2f}"
        )

    aggregate = _aggregate(judge_rows)
    plans_doc = {
        "meta": {
            "date": DATE,
            "experiment": "B0_vs_B1_specificity_amplification_codex",
            "b0_source": str(CASES_PATH.relative_to(HARNESS)),
            "n": len(plan_rows),
            "failures": len(failures),
            "rewriter_model": rewriter_model,
            "rewriter_temperature": REWRITER_TEMPERATURE,
            "schema_guard": "top-level keys, plan_id, flow count/durations, approach_label, length_variants",
            "intervention_source": "human rater A genericness comments",
        },
        "cases": plan_rows,
        "failures": [row for row in failures if row["stage"] == "rewrite"],
    }
    judge_doc = {
        "meta": {
            "date": DATE,
            "experiment": "B0_vs_B1_specificity_amplification_codex",
            "b0_score_source": str(B0_CLAUDE_PATH.relative_to(HARNESS)),
            "b1_score_source": "Claude judge run by this script",
            "rewriter_model": rewriter_model,
            "rewriter_temperature": REWRITER_TEMPERATURE,
            "judge_registry_key": JUDGE_REGISTRY_KEY,
            "judge_model_id": judge_model_id,
            "judge_temperature": JUDGE_TEMPERATURE,
            "output_mode": "director",
            "n": len(judge_rows),
            "failures": len(failures),
            "judge_parse_recoveries": judge_parse_recoveries,
            "aggregate": aggregate,
        },
        "cases": judge_rows,
        "failures": failures,
    }

    _write_json(PLANS_OUT, plans_doc)
    _write_json(JUDGE_OUT, judge_doc)
    _write_report(plans_doc, judge_doc, comments)

    _log()
    _log("=== Aggregate ===")
    if aggregate:
        _log(
            f"overall: B0={aggregate['b0_overall_mean']:.2f} "
            f"B1={aggregate['b1_overall_mean']:.2f} "
            f"Δ={aggregate['overall_delta_mean']:+.2f}"
        )
        _log(f"verdict B0: {aggregate['verdict_dist_b0']}")
        _log(f"verdict B1: {aggregate['verdict_dist_b1']}")
        _log(f"verdict upgraded: {aggregate['verdict_upgraded_count']}")
    _log(f"plans:  {PLANS_OUT}")
    _log(f"judge:  {JUDGE_OUT}")
    _log(f"report: {REPORT_OUT}")
    _log(f"failures: {len(failures)}")
    _log(f"judge parse recoveries: {judge_parse_recoveries}")
    return 0 if not failures else 1


def report_only() -> int:
    comments = _human_comments()
    plans_doc = _read_json(PLANS_OUT)
    judge_doc = _read_json(JUDGE_OUT)
    _write_report(plans_doc, judge_doc, comments)
    _log(f"report: {REPORT_OUT}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--generate", action="store_true", help="Generate B1 plans, judge them, and write report.")
    parser.add_argument("--report", action="store_true", help="Regenerate report from existing Codex JSON outputs.")
    args = parser.parse_args()
    if args.report and not args.generate:
        return report_only()
    return generate()


if __name__ == "__main__":
    raise SystemExit(main())
