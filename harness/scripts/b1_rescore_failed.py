"""B1 rescore 보강 — judge max_tokens 절단으로 실패한 case 만 재채점 후 병합 (research only).

문제: b1_specificity_rewrite.py 1차 실행에서 5개 case 가 judge 단계에서
  JSONDecodeError(Unterminated string, char~2600) 로 실패 — B1 plan 이 더 밀도가
  높아 Claude judge 의 reasons/suggestions JSON 이 JUDGE_MAX_TOKENS(2000) 를 넘겨
  절단된 것(측정 도구의 출력 버짓 한계이지 B1 품질 문제 아님).

해결(단일 변인 보존): 채점 '로직'(_parse_scores/_derive_verdict/_rubric_5/프롬프트/
  temp=0.1/registry claude-sonnet/AnthropicAdapter)은 byte-identical 그대로 두고,
  judge 출력 토큰 버짓만 4000 으로 올려 같은 judge 가 '완전한' JSON 을 내도록 한다.
  (B0 는 2000 으로 채점됐지만 B0 plan 이 짧아 절단 없이 파싱됨 — 동일 judge·동일 산식.)
  실패한 case 만 재채점 → 기존 결과 JSON 에 병합 + aggregate 재계산.
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
except Exception:  # noqa: BLE001
    pass
os.environ.setdefault("PYTHONIOENCODING", "utf-8")

HARNESS = Path(__file__).resolve().parents[1]
BACKEND = HARNESS / "backend" / "fastapi"
sys.path.insert(0, str(HARNESS))


def _load_dotenv() -> str | None:
    env_path = BACKEND / ".env"
    if not env_path.exists():
        return None
    with open(env_path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            v = v.strip().strip('"').strip("'")
            if v:
                os.environ[k.strip()] = v
    return str(env_path)


_loaded = _load_dotenv()

# 채점 로직·프롬프트·차원 byte-identical 재사용 (max_tokens 만 호출 시 상향) ──
from scripts.cross_provider_judge_rescore import (  # noqa: E402
    DIMENSIONS_DIRECTOR,
    DIRECTOR_SYSTEM_PROMPT,
    JUDGE_REGISTRY_KEY,
    JUDGE_TEMPERATURE,
    _derive_verdict,
    _parse_scores,
    _rubric_5,
)
from backend.fastapi.config import get_settings  # noqa: E402
from backend.fastapi.llm import registry  # noqa: E402
from backend.fastapi.llm.providers.anthropic_adapter import AnthropicAdapter  # noqa: E402
from backend.fastapi.llm.types import LLMMessage, LLMRequest  # noqa: E402

HR = HARNESS / "eval" / "human_review"
CASES_PATH = HR / "2026-06-15-calib-ab-cases.json"
B0_CLAUDE_PATH = HR / "2026-06-15-calib-ab-claude.json"
OUT_PATH = HR / "2026-06-21-b1-specificity-rescore.json"

JUDGE_MAX_TOKENS_HI = 4000   # ★ 절단 방지용 상향 (산식 무관 — 출력 버짓만)
FLOOR_AXES = ("differentiation", "hook_strength", "retention_design", "target_clarity")


def _judge_one_hi(adapter: AnthropicAdapter, model_id: str, api_key: str, plan: dict
                  ) -> tuple[dict[str, int], str]:
    """_judge_one 과 byte-identical (system/user/temp/json_mode/parse 동일) — max_tokens 만 4000."""
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
        max_tokens=JUDGE_MAX_TOKENS_HI,
        json_mode=True,
    )
    resp = adapter.complete(req, api_key=api_key)
    text = (resp.text or "").strip()
    return _parse_scores(text), text


def main() -> int:
    data = json.load(open(OUT_PATH, encoding="utf-8"))
    cases_src = {c["case_id"]: c for c in json.load(open(CASES_PATH, encoding="utf-8"))["cases"]}
    b0_scores = {c["case_id"]: c["A2_claude"]
                 for c in json.load(open(B0_CLAUDE_PATH, encoding="utf-8"))["cases"]}

    settings = get_settings()
    anthropic_key = settings.anthropic_api_key
    rewriter_model = data["meta"].get("rewriter_model", settings.openai_model_critic)
    judge_model = registry.get_model(JUDGE_REGISTRY_KEY)
    judge_model_id = judge_model["model_id"]
    adapter = AnthropicAdapter()

    # 실패 case 중 b1_judge 절단 실패만 골라 재채점 (b1_rewrite/스키마 실패는 별개로 둠).
    judge_failures = [f for f in data.get("failures", []) if f.get("stage") == "b1_judge"]
    other_failures = [f for f in data.get("failures", []) if f.get("stage") != "b1_judge"]
    failed_ids = [f["case_id"] for f in judge_failures]
    print(f"=== B1 rescore (judge truncation fix, max_tokens={JUDGE_MAX_TOKENS_HI}) ===")
    print(f".env: {_loaded}")
    print(f"judge: {JUDGE_REGISTRY_KEY} {judge_model_id} temp={JUDGE_TEMPERATURE}")
    print(f"재채점 대상(절단 실패): {failed_ids}\n")

    from openai import OpenAI  # noqa: E402
    client = OpenAI(api_key=settings.openai_api_key)

    # rewriter 재사용(동일 B1 plan 을 다시 생성해야 함 — 1차에서 plan 을 저장 안 했으므로 재생성)
    from scripts.b1_specificity_rewrite import _rewrite_one, _validate_b1  # noqa: E402

    still_failed: list[dict] = []
    recovered: list[dict] = []

    for cid in failed_ids:
        src = cases_src[cid]
        b0_plan = dict(src["plan"])
        b0_plan.setdefault("plan_id", cid)
        user_input = src.get("input", "")
        b0 = b0_scores[cid]

        # B1 재생성 (1차에서 plan 미저장 → 동일 rewriter 로 재생성, 스키마 검증 동일)
        b1_plan = None
        last_err = ""
        for attempt in (1, 2, 3):
            try:
                cand, _ = _rewrite_one(client, rewriter_model, user_input, b0_plan)
                cand["plan_id"] = cid
                v = _validate_b1(b0_plan, cand)
                if v:
                    last_err = "schema: " + "; ".join(v)
                    print(f"[{cid}] rewrite attempt {attempt} 스키마위반: {v}")
                    time.sleep(1.0)
                    continue
                b1_plan = cand
                break
            except Exception as e:  # noqa: BLE001
                last_err = f"{type(e).__name__}: {str(e)[:120]}"
                print(f"[{cid}] rewrite attempt {attempt} 실패: {last_err}")
                time.sleep(1.0)
        if b1_plan is None:
            still_failed.append({"case_id": cid, "stage": "b1_rewrite_retry", "error": last_err})
            print(f"[{cid}] rewrite 재생성 실패\n")
            continue

        # B1 재채점 (max_tokens 4000, 동일 judge/산식)
        scores = None
        jerr = ""
        for attempt in (1, 2):
            try:
                scores, _ = _judge_one_hi(adapter, judge_model_id, anthropic_key, b1_plan)
                break
            except Exception as e:  # noqa: BLE001
                jerr = f"{type(e).__name__}: {str(e)[:120]}"
                print(f"[{cid}] judge attempt {attempt} 실패: {jerr}")
                time.sleep(1.0)
        if scores is None:
            still_failed.append({"case_id": cid, "stage": "b1_judge_hi", "error": jerr})
            print(f"[{cid}] 재채점 실패\n")
            continue

        b1_avg, b1_verdict = _derive_verdict(scores, dimensions=DIMENSIONS_DIRECTOR)
        b1_rubric5 = _rubric_5(scores)
        b0_raw = b0["raw_scores"]
        per_dim = {d: int(scores[d]) - int(b0_raw[d]) for d in DIMENSIONS_DIRECTOR}
        overall_delta = round(b1_avg - float(b0["overall_score_avg"]), 4)
        verdict_shift = "none" if b0["verdict"] == b1_verdict else f"{b0['verdict']}→{b1_verdict}"
        recovered.append({
            "case_id": cid,
            "kind": src.get("kind"),
            "b0": {
                "overall_score_avg": b0["overall_score_avg"],
                "verdict": b0["verdict"],
                "raw_scores": b0_raw,
                "dimensions": b0["dimensions"],
            },
            "b1": {
                "overall_score_avg": round(b1_avg, 4),
                "verdict": b1_verdict,
                "raw_scores": scores,
                "dimensions": b1_rubric5,
                "plan": b1_plan,
            },
            "delta": {"per_dim": per_dim, "overall": overall_delta, "verdict_shift": verdict_shift},
            "judge_max_tokens": JUDGE_MAX_TOKENS_HI,
        })
        print(f"[{cid}] {src.get('kind'):8} B0={b0['overall_score_avg']:.2f} "
              f"B1={b1_avg:.2f} Δ={overall_delta:+.2f} | {b0['verdict']}→{b1_verdict}")

    # ── 병합 + aggregate 재계산 ──
    all_cases = list(data["cases"]) + recovered
    # case_id 정렬(원래 순서)
    order = [c["case_id"] for c in json.load(open(CASES_PATH, encoding="utf-8"))["cases"]]
    all_cases.sort(key=lambda c: order.index(c["case_id"]))

    n = len(all_cases)
    per_dim_mean = {d: round(sum(oc["delta"]["per_dim"][d] for oc in all_cases) / n, 4)
                    for d in DIMENSIONS_DIRECTOR}
    b0_overall_mean = round(sum(oc["b0"]["overall_score_avg"] for oc in all_cases) / n, 4)
    b1_overall_mean = round(sum(oc["b1"]["overall_score_avg"] for oc in all_cases) / n, 4)
    floor_move = {}
    for ax in FLOOR_AXES:
        b0m = round(sum(oc["b0"]["raw_scores"][ax] for oc in all_cases) / n, 4)
        b1m = round(sum(oc["b1"]["raw_scores"][ax] for oc in all_cases) / n, 4)
        floor_move[ax] = {"b0_mean": b0m, "b1_mean": b1m, "delta": round(b1m - b0m, 4)}

    def _dist(key: str) -> dict:
        d = {"approve": 0, "revise": 0, "reject": 0}
        for oc in all_cases:
            d[oc[key]["verdict"]] += 1
        return d
    rank = {"reject": 0, "revise": 1, "approve": 2}
    to_approve = sum(1 for oc in all_cases
                     if oc["b0"]["verdict"] != "approve" and oc["b1"]["verdict"] == "approve")
    reject_to_revise = sum(1 for oc in all_cases
                           if oc["b0"]["verdict"] == "reject" and oc["b1"]["verdict"] == "revise")
    verdict_upgraded = sum(1 for oc in all_cases
                           if rank[oc["b1"]["verdict"]] > rank[oc["b0"]["verdict"]])

    data["cases"] = all_cases
    data["failures"] = other_failures + still_failed
    data["meta"]["n"] = n
    data["meta"]["failures"] = len(data["failures"])
    data["meta"]["judge_max_tokens_default"] = 2000
    data["meta"]["judge_max_tokens_rescued"] = JUDGE_MAX_TOKENS_HI
    data["meta"]["rescued_note"] = (
        "5 case 가 1차에서 judge 출력 절단(max_tokens=2000)으로 실패 → 동일 judge·동일 산식, "
        "출력 버짓만 4000 으로 상향해 재채점(B1 plan 도 동일 rewriter 로 재생성)."
    )
    data["meta"]["aggregate"] = {
        "per_dim_mean_delta": per_dim_mean,
        "b0_overall_mean": b0_overall_mean,
        "b1_overall_mean": b1_overall_mean,
        "overall_delta_mean": round(b1_overall_mean - b0_overall_mean, 4),
        "floor_axes_move": floor_move,
        "verdict_dist_b0": _dist("b0"),
        "verdict_dist_b1": _dist("b1"),
        "to_approve_count": to_approve,
        "reject_to_revise_count": reject_to_revise,
        "verdict_upgraded_count": verdict_upgraded,
    }
    OUT_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    ag = data["meta"]["aggregate"]
    print("\n" + "=" * 64)
    print(f"MERGED AGGREGATE  n={n}  failures={len(data['failures'])}")
    print(f"  overall: B0={ag['b0_overall_mean']:.3f} → B1={ag['b1_overall_mean']:.3f} "
          f"(Δ={ag['overall_delta_mean']:+.3f})")
    for ax, mv in ag["floor_axes_move"].items():
        print(f"    {ax:18} {mv['b0_mean']:.2f} → {mv['b1_mean']:.2f}  (Δ={mv['delta']:+.2f})")
    print(f"  verdict B0: {ag['verdict_dist_b0']}")
    print(f"  verdict B1: {ag['verdict_dist_b1']}")
    print(f"  → approve 신규={ag['to_approve_count']}  reject→revise={ag['reject_to_revise_count']}  "
          f"verdict 상향={ag['verdict_upgraded_count']}")
    print("=" * 64)
    print(f"저장: {OUT_PATH}  (ok={n}, fail={len(data['failures'])})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
