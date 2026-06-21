"""Phase 33 S2 — 결정적 게이트 ∘ cross-provider judge 직교 합산 측정 (재사용 데이터, LLM 0).

연구 arc 원래 후속(calib-ab-preliminary.md:43): "결정적 깊이 게이트 + cross-provider judge를
같은 10 plan + 같은 사람 점수에 대본다." 게이트는 결정론(비-LLM)이라 기존 데이터 재사용으로
신규 콜 0. cross-provider judge 결과(calib-ab-claude.json)·사람 점수(scores-A.json) 재사용.

측정: 같은 10케이스(director plan)에서
  - in-provider critic(A0): approve 10/10 (false-approve 10/10 — 사람 전수 <3).
  - 결정적 pacing 게이트(단독): payoff bloat 검출 → approve 강등. 몇 건 차단?
  - cross-provider judge(단독): false-approve 몇 건?
  - 게이트 ∘ judge: 둘 다 놓쳐야 false-approve 잔존.
→ 직교성(게이트=구조 / judge=점수) + 게이트의 무-LLM 차단 커버리지.

실행: python scripts/phase33_gate_judge_measure.py  (rootdir harness/)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
except Exception:
    pass

HARNESS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HARNESS))
HR = HARNESS / "eval" / "human_review"

from backend.fastapi.agents.critic import _pacing_gate_issue  # noqa: E402
from backend.fastapi.config import Settings  # noqa: E402

_GATE_ON = Settings(critic_pacing_gate_enabled=True)
_HUMAN_DIMS = ("content_quality", "brand_fit", "actionability_depth", "differentiation")
FALSE_APPROVE_HUMAN = 3.0  # 사전동결(preliminary.md): human_avg < 3.0 + approve = false-approve


def _load(name: str):
    return json.load(open(HR / name, encoding="utf-8"))


def main() -> int:
    cases = _load("2026-06-15-calib-ab-cases.json")["cases"]
    claude = {c["case_id"]: c for c in _load("2026-06-15-calib-ab-claude.json")["cases"]}
    human = {s["case_id"]: s for s in _load("2026-06-15-calib-ab-scores-A.json")["scores"]}

    rows = []
    for c in cases:
        cid = c["case_id"]
        plan = c.get("plan", {})
        h = human.get(cid, {})
        hvals = [float(h[d]) for d in _HUMAN_DIMS if isinstance(h.get(d), (int, float))]
        human_avg = round(sum(hvals) / len(hvals), 2) if hvals else None
        gate = _pacing_gate_issue(plan, _GATE_ON)  # None=정상 / str=bloat 차단
        cj = (claude.get(cid, {}).get("A2_claude") or {})
        judge_verdict = str(cj.get("verdict") or cj.get("overall_verdict") or "?").lower()
        rows.append({
            "cid": cid, "kind": c.get("kind"), "human": human_avg,
            "gate_fires": gate is not None, "judge": judge_verdict,
        })

    def low(r):  # 사람 기준 나쁜 plan (false-approve 대상)
        return r["human"] is not None and r["human"] < FALSE_APPROVE_HUMAN

    print("=== Phase 33 S2 — 게이트 ∘ cross-provider judge (10케이스, LLM 0) ===\n")
    print(f"{'case':10}{'kind':9}{'human':>6}  {'A0(in)':8}{'gate':6}{'judge':8}")
    for r in rows:
        a0 = "approve"  # A0 in-provider = 전수 approve (preliminary.md)
        g = "차단" if r["gate_fires"] else "-"
        print(f"{r['cid']:10}{str(r['kind']):9}{str(r['human']):>6}  {a0:8}{g:6}{r['judge']:8}")

    n = len(rows)
    bad = [r for r in rows if low(r)]
    # false-approve = approve 인데 사람<3
    fa_in = len(bad)  # in-provider 전수 approve → 전부 false-approve
    fa_gate = sum(1 for r in bad if not r["gate_fires"])  # 게이트가 놓친 것(차단 못 한 것)
    fa_judge = sum(1 for r in bad if r["judge"] == "approve")  # judge가 approve 한 것
    fa_combo = sum(1 for r in bad if (not r["gate_fires"]) and r["judge"] == "approve")
    gate_catch = sum(1 for r in bad if r["gate_fires"])

    print(f"\n=== 요약 (사람 기준 나쁜 plan {len(bad)}/{n}) ===")
    print(f"  in-provider critic(A0)  false-approve: {fa_in}/{len(bad)}  (전수 approve)")
    print(f"  결정적 게이트 단독       false-approve: {fa_gate}/{len(bad)}  (게이트가 {gate_catch}건 무-LLM 차단)")
    print(f"  cross-provider judge 단독 false-approve: {fa_judge}/{len(bad)}")
    print(f"  게이트 ∘ judge           false-approve: {fa_combo}/{len(bad)}")
    print("\n=== 직교성 ===")
    print(f"  게이트 차단(구조/pacing): {[r['cid'] for r in bad if r['gate_fires']] or '없음'}")
    print(f"  judge만 차단(점수 낙관):  {[r['cid'] for r in bad if (not r['gate_fires']) and r['judge']!='approve'] }")
    print(f"  → 게이트={gate_catch}건 결정론 차단(무-LLM), judge가 나머지 + 전체 닫음. 두 층 직교(구조 vs 점수).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
