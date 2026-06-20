#!/usr/bin/env python3
"""analyze_blind_ab.py — Critic calibration A/B (A0 vs A1) blind 채점 분석.

Phase 27 측정 그라운딩 — critic_calibration_enabled(critic.py "88점 함정" 보정)의
A0(보정 OFF, 낙관편향) vs A1(보정 ON, anti-optimism + 핵심차원 게이트)을 **사람 blind
채점**으로 검증한다. critic 점수가 사람 평균과 얼마나 괴리하는지(특히 false-approve),
그리고 A1 이 **얕은(SHALLOW) plan 에서만** 점수를 낮췄는지(과교정 가드)를 정량화한다.

설계 불변 (blind 분리):
  - 채점자는 cases[].{case_id,kind,input,plan} 만 본다. hidden A0/A1 critic 점수는
    `…-calib-ab-key.json` 으로 분리되어 채점자가 절대 못 본다. 본 스크립트는 채점 **완료 후**
    key.json(critic) + rater export 2개를 합쳐 분석만 한다 (production code 0 변경).
  - 의존성: scipy 있으면 사용, 없으면 numpy/pure-python fallback(κ·Wilcoxon·McNemar·r 직접 수식).
    LLM 0, network 0, deterministic.

스케일 약속:
  - 사람 차원 점수 = 0~5 (rubric §2.1~2.5). human_avg = rubric_dims 산술평균(0~5).
  - critic overall = 0~5 (critic.overall_score_avg). 사람과 직접 비교(동일 0~5 축).
  - depth_actionability = 별도 0~1 축 (human_avg 에 미포함 — §2.6).

사용:
  python scripts/analyze_blind_ab.py \\
      --key  eval/human_review/2026-06-15-calib-ab-key.json \\
      --rater eval/human_review/<rater1-export>.json \\
      --rater eval/human_review/<rater2-export>.json \\
      [--out eval/regression_results/2026-06-15-critic-calib-ab.md] \\
      [--approve-threshold 3.5] [--human-pass 3.0]

rater export JSON 스키마 (채점 HTML "export" 산출 — 본 스크립트가 읽는 형식):
  {
    "rater_id": "R1",                       # 채점자 식별 (익명 코드)
    "scores": {
      "<case_id>": {
        "dimensions": { "<dim>": <0~5>, ... },   # rubric_dims 중 채점한 것
        "overall": <0~5>,                        # (선택) 없으면 dimensions 평균으로 산출
        "depth_actionability": <0~1>,            # (선택) 별도 축
        "verdict": "approve|revise|reject"       # (선택) 사람 판정 — verdict 일치율용
      }, ...
    }
  }
  · case_id 누락 / dim 누락은 graceful skip (해당 케이스·차원만 제외, N 감소로 처리).
  · 두 rater 의 case 교집합에서만 사람평균/일치도 계산.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from collections import OrderedDict
from datetime import date
from pathlib import Path
from typing import Any

# ─── scipy 우선, 없으면 fallback ──────────────────────────────────────
try:  # pragma: no cover - 환경 의존
    from scipy import stats as _scipy_stats  # type: ignore
    _HAVE_SCIPY = True
except Exception:  # noqa: BLE001
    _scipy_stats = None
    _HAVE_SCIPY = False

DATE = "2026-06-15"
ARMS = ("A0", "A1")
# rubric_dims (cases meta 의 rubric_dims 와 동일 순서). human_avg = 이 5축 평균(0~5).
DEFAULT_RUBRIC_DIMS = (
    "content_quality",
    "safety",
    "brand_fit",
    "actionability_depth",
    "differentiation",
)
# critic approve 임계 (critic.py: avg ≥ 3.5). 사전동결 — 변경 시 리포트에 명기.
DEFAULT_APPROVE_THRESHOLD = 3.5
# 사람 평균 "합격선"(0~5). human_avg < 이 값 = 사람이 보기엔 미달 → false-approve 판정 기준.
DEFAULT_HUMAN_PASS = 3.0


# ══════════════════════════════════════════════════════════════════════
# 통계 헬퍼 (scipy 없으면 순수 python/numpy 수식 직접 구현)
# ══════════════════════════════════════════════════════════════════════

def _mean(xs: list[float]) -> float | None:
    return sum(xs) / len(xs) if xs else None


def _round(x: float | None, n: int = 3) -> float | None:
    return round(x, n) if isinstance(x, (int, float)) else None


def pearson_r(xs: list[float], ys: list[float]) -> float | None:
    """Pearson 상관계수. n<2 또는 분산 0 이면 None."""
    n = len(xs)
    if n < 2 or n != len(ys):
        return None
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    syy = sum((y - my) ** 2 for y in ys)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    if sxx <= 0 or syy <= 0:
        return None
    return sxy / math.sqrt(sxx * syy)


def cohen_weighted_kappa(
    a: list[float], b: list[float], *, k_min: int, k_max: int
) -> dict[str, Any]:
    """Cohen's quadratic weighted κ — 정수 등급(반올림) 2 rater 일치도.

    0~5 실수 점수는 가장 가까운 정수 등급으로 반올림해 (k_max-k_min+1)×… 혼동행렬을 만든다.
    quadratic weight w_ij = 1 - (i-j)^2 / (K-1)^2. scipy 미사용(직접 수식 — 결과 동일).

    Returns: {"kappa": float|None, "n": int, "note": str}. n<2 또는 단일 등급이면 None+주의.
    """
    pairs = [
        (int(round(x)), int(round(y)))
        for x, y in zip(a, b)
        if isinstance(x, (int, float)) and isinstance(y, (int, float))
    ]
    n = len(pairs)
    if n < 2:
        return {"kappa": None, "n": n, "note": "n<2 — κ 계산 불가"}
    cats = list(range(k_min, k_max + 1))
    K = len(cats)
    idx = {c: i for i, c in enumerate(cats)}
    # 등급 범위 밖 clip (방어).
    def _ci(v: int) -> int:
        return idx.get(min(max(v, k_min), k_max), 0)

    obs = [[0.0] * K for _ in range(K)]
    for x, y in pairs:
        obs[_ci(x)][_ci(y)] += 1.0
    # 주변 분포.
    row = [sum(obs[i]) for i in range(K)]
    col = [sum(obs[i][j] for i in range(K)) for j in range(K)]
    # quadratic weights (0=완전일치 → w=1, 멀수록 ↓).
    denom_w = (K - 1) ** 2 if K > 1 else 1
    w = [[1.0 - ((i - j) ** 2) / denom_w for j in range(K)] for i in range(K)]
    po = sum(w[i][j] * obs[i][j] for i in range(K) for j in range(K)) / n
    pe = sum(w[i][j] * (row[i] * col[j] / n) for i in range(K) for j in range(K)) / n
    if abs(1.0 - pe) < 1e-12:
        # 모든 질량이 한 등급 → 기대일치=관측일치 → κ 정의 불가.
        return {
            "kappa": None,
            "n": n,
            "note": "분산 0(단일 등급 집중) — κ 정의 불가, raw 일치율 참조",
        }
    kappa = (po - pe) / (1.0 - pe)
    return {"kappa": kappa, "n": n, "note": ""}


def icc_2_1(rater_a: list[float], rater_b: list[float]) -> float | None:
    """ICC(2,1) two-way random, single rater, absolute agreement (보조 일치도).

    연속 점수(0~5 실수)에 적합. 2 rater × n target one-way ANOVA 분해로 산출한다.
    N 작으면 점추정만(신뢰구간 미산출). 분산 0 등 정의불가면 None.
    """
    pairs = [
        (x, y)
        for x, y in zip(rater_a, rater_b)
        if isinstance(x, (int, float)) and isinstance(y, (int, float))
    ]
    n = len(pairs)
    k = 2
    if n < 2:
        return None
    grand = sum(x + y for x, y in pairs) / (n * k)
    # row(target) means, col(rater) means.
    row_means = [(x + y) / k for x, y in pairs]
    col_means = [
        sum(x for x, _ in pairs) / n,
        sum(y for _, y in pairs) / n,
    ]
    ss_rows = k * sum((rm - grand) ** 2 for rm in row_means)
    ss_cols = n * sum((cm - grand) ** 2 for cm in col_means)
    ss_total = sum((v - grand) ** 2 for x, y in pairs for v in (x, y))
    ss_err = ss_total - ss_rows - ss_cols
    ms_rows = ss_rows / (n - 1)
    ms_cols = ss_cols / (k - 1)
    ms_err = ss_err / ((n - 1) * (k - 1)) if (n - 1) * (k - 1) > 0 else 0.0
    denom = ms_rows + (k - 1) * ms_err + (k / n) * (ms_cols - ms_err)
    if abs(denom) < 1e-12:
        return None
    return (ms_rows - ms_err) / denom


def wilcoxon_signed_rank(a: list[float], b: list[float]) -> dict[str, Any]:
    """Paired Wilcoxon signed-rank (A0 vs A1). scipy 있으면 사용, 없으면 정규근사 fallback.

    Returns: {"W": float|None, "p": float|None, "n_nonzero": int, "method": str, "note": str}.
    N 작으면 정규근사 p 는 참고용(연속성 보정 적용). zero-diff 는 제외.
    """
    diffs = [
        x - y
        for x, y in zip(a, b)
        if isinstance(x, (int, float)) and isinstance(y, (int, float))
    ]
    nonzero = [d for d in diffs if abs(d) > 1e-12]
    n = len(nonzero)
    if n < 1:
        return {"W": None, "p": None, "n_nonzero": 0, "method": "none",
                "note": "차이 0 — 검정 불가"}
    if _HAVE_SCIPY and n >= 1:
        try:  # pragma: no cover - 환경 의존
            res = _scipy_stats.wilcoxon(
                [x for x, y in zip(a, b)
                 if isinstance(x, (int, float)) and isinstance(y, (int, float))],
                [y for x, y in zip(a, b)
                 if isinstance(x, (int, float)) and isinstance(y, (int, float))],
                zero_method="wilcox", correction=True, mode="auto",
            )
            return {"W": float(res.statistic), "p": float(res.pvalue),
                    "n_nonzero": n, "method": "scipy", "note": ""}
        except Exception:  # noqa: BLE001 — fallback 으로 진행
            pass
    # ── pure-python: signed-rank + 정규근사 ──
    ranks = _rank_abs(nonzero)
    w_plus = sum(r for d, r in zip(nonzero, ranks) if d > 0)
    w_minus = sum(r for d, r in zip(nonzero, ranks) if d < 0)
    W = min(w_plus, w_minus)
    mean_w = n * (n + 1) / 4.0
    var_w = n * (n + 1) * (2 * n + 1) / 24.0
    if var_w <= 0:
        return {"W": float(W), "p": None, "n_nonzero": n, "method": "exact_small",
                "note": "분산 0 — p 미산출"}
    z = (W - mean_w + 0.5) / math.sqrt(var_w)  # 연속성 보정
    p = 2.0 * _norm_sf(abs(z))
    return {"W": float(W), "p": float(min(1.0, p)), "n_nonzero": n,
            "method": "normal_approx", "note": "N 소표본 — 정규근사 p 는 참고용"}


def _rank_abs(values: list[float]) -> list[float]:
    """|값| 오름차순 평균순위(동점=평균 rank). signed-rank 용."""
    order = sorted(range(len(values)), key=lambda i: abs(values[i]))
    ranks = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and abs(values[order[j + 1]]) == abs(values[order[i]]):
            j += 1
        avg_rank = (i + 1 + j + 1) / 2.0  # 1-based 평균
        for t in range(i, j + 1):
            ranks[order[t]] = avg_rank
        i = j + 1
    return ranks


def mcnemar(b: int, c: int) -> dict[str, Any]:
    """McNemar (paired binary) — approve 비율 변화. b,c = 불일치 쌍 수.

    b = A0 approve & A1 not, c = A0 not & A1 approve. 연속성 보정 χ²(df=1).
    N 작으면 binomial exact p 도 함께 산출. {"chi2","p_chi2","p_exact","b","c","note"}.
    """
    nd = b + c
    if nd == 0:
        return {"chi2": None, "p_chi2": None, "p_exact": None, "b": b, "c": c,
                "note": "불일치 쌍 0 — approve 패턴 동일"}
    chi2 = (abs(b - c) - 1) ** 2 / nd  # Yates 연속성 보정
    p_chi2 = _chi2_sf_df1(chi2)
    # exact binomial two-sided (p=0.5).
    k = min(b, c)
    p_exact = min(
        1.0,
        2.0 * sum(_binom(nd, i) for i in range(0, k + 1)) / (2.0 ** nd),
    )
    if _HAVE_SCIPY:  # pragma: no cover - 환경 의존
        try:
            from scipy.stats import binomtest  # type: ignore
            p_exact = float(binomtest(k, nd, 0.5).pvalue)
        except Exception:  # noqa: BLE001
            pass
    return {"chi2": chi2, "p_chi2": p_chi2, "p_exact": p_exact, "b": b, "c": c,
            "note": "N 소표본 — exact p 우선 참조"}


def _binom(n: int, k: int) -> float:
    return math.comb(n, k)


def _norm_sf(z: float) -> float:
    """표준정규 상측확률 P(Z>z) = 0.5*erfc(z/√2)."""
    return 0.5 * math.erfc(z / math.sqrt(2.0))


def _chi2_sf_df1(x: float) -> float:
    """χ²(df=1) 상측확률 = 2*P(Z>√x) = erfc(√(x/2))."""
    if x <= 0:
        return 1.0
    return math.erfc(math.sqrt(x / 2.0))


# ══════════════════════════════════════════════════════════════════════
# 로딩 / 병합
# ══════════════════════════════════════════════════════════════════════

def _load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def _human_overall(case_scores: dict[str, Any], dims: tuple[str, ...]) -> float | None:
    """한 rater 의 한 케이스 overall(0~5) — explicit overall 우선, 없으면 dim 평균."""
    ov = case_scores.get("overall")
    if isinstance(ov, (int, float)):
        return float(ov)
    d = case_scores.get("dimensions") or {}
    vals = [float(d[k]) for k in dims if isinstance(d.get(k), (int, float))]
    return _mean(vals)


def _critic_overall(arm_block: dict[str, Any]) -> float | None:
    """hidden arm block 의 critic overall(0~5). overall_score_avg 우선."""
    for k in ("overall_score_avg", "overall", "overall_score"):
        v = arm_block.get(k)
        if isinstance(v, (int, float)):
            # overall_score(0~1)면 0~5 로 환산.
            return float(v) * 5.0 if k == "overall_score" and v <= 1.0 else float(v)
    return None


def _critic_approve(
    arm_block: dict[str, Any], overall_0_5: float | None, threshold: float
) -> bool:
    """critic approve 여부 — verdict=='approve' 또는 overall_0_5 ≥ 임계 (둘 중 하나)."""
    v = str(arm_block.get("verdict", "")).strip().lower()
    if v == "approve":
        return True
    if v in ("revise", "reject"):
        return False
    return overall_0_5 is not None and overall_0_5 >= threshold


# ══════════════════════════════════════════════════════════════════════
# 분석 코어
# ══════════════════════════════════════════════════════════════════════

def analyze(
    key: dict[str, Any],
    raters: list[dict[str, Any]],
    *,
    dims: tuple[str, ...],
    approve_threshold: float,
    human_pass: float,
) -> dict[str, Any]:
    """key(critic A0/A1) + rater export 2개 → 분석 결과 dict.

    교집합 케이스(양 rater + key 모두 존재)만 사용. 케이스별 사람평균 = 2 rater human_overall 평균.
    """
    cases = key.get("cases", [])
    key_by_id: "OrderedDict[str, dict[str, Any]]" = OrderedDict()
    for c in cases:
        cid = c.get("case_id")
        if cid:
            key_by_id[cid] = c

    if len(raters) < 2:
        raise SystemExit("rater export 2개가 필요합니다 (--rater 두 번).")
    r1 = (raters[0].get("scores") or {})
    r2 = (raters[1].get("scores") or {})
    r1_id = raters[0].get("rater_id", "R1")
    r2_id = raters[1].get("rater_id", "R2")

    # 교집합 case_id (key + 두 rater 모두 채점).
    common = [cid for cid in key_by_id if cid in r1 and cid in r2]

    per_case: list[dict[str, Any]] = []
    # inter-rater 누적(차원별 + overall).
    rater_pairs_overall: tuple[list[float], list[float]] = ([], [])
    rater_pairs_by_dim: dict[str, tuple[list[float], list[float]]] = {
        d: ([], []) for d in dims
    }

    for cid in common:
        kc = key_by_id[cid]
        kind = kc.get("kind", "normal")
        s1, s2 = r1[cid], r2[cid]
        ov1 = _human_overall(s1, dims)
        ov2 = _human_overall(s2, dims)
        if ov1 is not None and ov2 is not None:
            rater_pairs_overall[0].append(ov1)
            rater_pairs_overall[1].append(ov2)
        human_avg = _mean([v for v in (ov1, ov2) if v is not None])

        # 차원별 사람평균 + inter-rater 누적.
        dim_human: dict[str, float | None] = {}
        d1, d2 = (s1.get("dimensions") or {}), (s2.get("dimensions") or {})
        for d in dims:
            v1, v2 = d1.get(d), d2.get(d)
            if isinstance(v1, (int, float)) and isinstance(v2, (int, float)):
                rater_pairs_by_dim[d][0].append(float(v1))
                rater_pairs_by_dim[d][1].append(float(v2))
            dvals = [float(v) for v in (v1, v2) if isinstance(v, (int, float))]
            dim_human[d] = _mean(dvals)

        # depth(0~1) 별도 축 평균.
        dvals01 = [
            float(s.get("depth_actionability"))
            for s in (s1, s2)
            if isinstance(s.get("depth_actionability"), (int, float))
        ]
        depth_human = _mean(dvals01)

        # 사람 verdict(있으면) 다수결/일치 — 두 rater verdict.
        hv = [str(s.get("verdict", "")).strip().lower() for s in (s1, s2)]
        hv = [v for v in hv if v in ("approve", "revise", "reject")]

        # critic A0/A1.
        hidden = kc.get("hidden", {})
        arm_info: dict[str, Any] = {}
        for arm in ARMS:
            blk = hidden.get(arm, {}) if isinstance(hidden, dict) else {}
            cov = _critic_overall(blk)
            arm_info[arm] = {
                "critic_overall": cov,
                "verdict": str(blk.get("verdict", "")).strip().lower() or None,
                "approve": _critic_approve(blk, cov, approve_threshold),
                "abs_gap": (abs(cov - human_avg)
                            if cov is not None and human_avg is not None else None),
            }

        per_case.append({
            "case_id": cid,
            "kind": kind,
            "human_avg": human_avg,
            "human_overall_per_rater": {r1_id: ov1, r2_id: ov2},
            "dim_human": dim_human,
            "depth_human": depth_human,
            "human_verdicts": hv,
            "arms": arm_info,
        })

    # ── inter-rater 일치도 ──
    inter = {
        "overall": {
            "kappa_weighted": cohen_weighted_kappa(
                *rater_pairs_overall, k_min=0, k_max=5),
            "icc_2_1": icc_2_1(*rater_pairs_overall),
            "pearson_r": pearson_r(*rater_pairs_overall),
            "exact_agree_pct": _exact_agree(*rater_pairs_overall),
            "n": len(rater_pairs_overall[0]),
        },
        "by_dim": {
            d: {
                "kappa_weighted": cohen_weighted_kappa(
                    *rater_pairs_by_dim[d], k_min=0, k_max=5),
                "n": len(rater_pairs_by_dim[d][0]),
            }
            for d in dims
        },
        "rater_ids": [r1_id, r2_id],
    }

    # ── arm별 종합 지표 ──
    arm_summary = {arm: _arm_metrics(per_case, arm, human_pass) for arm in ARMS}

    # ── 통계: paired Wilcoxon(critic overall), McNemar(approve) ──
    a0_overall = [c["arms"]["A0"]["critic_overall"] for c in per_case]
    a1_overall = [c["arms"]["A1"]["critic_overall"] for c in per_case]
    paired = [
        (x, y) for x, y in zip(a0_overall, a1_overall)
        if isinstance(x, (int, float)) and isinstance(y, (int, float))
    ]
    wil = wilcoxon_signed_rank([x for x, _ in paired], [y for _, y in paired])

    # McNemar on approve (A0 vs A1).
    b = sum(1 for c in per_case
            if c["arms"]["A0"]["approve"] and not c["arms"]["A1"]["approve"])
    cc = sum(1 for c in per_case
             if not c["arms"]["A0"]["approve"] and c["arms"]["A1"]["approve"])
    mcn = mcnemar(b, cc)

    # ── SHALLOW vs GS 분해 ──
    decomp = _decompose_shallow_gs(per_case)

    return {
        "dims": list(dims),
        "approve_threshold": approve_threshold,
        "human_pass": human_pass,
        "n_common": len(common),
        "n_total_key": len(key_by_id),
        "per_case": per_case,
        "inter_rater": inter,
        "arm_summary": arm_summary,
        "wilcoxon": wil,
        "mcnemar": mcn,
        "decompose": decomp,
        "have_scipy": _HAVE_SCIPY,
        "rater_ids": [r1_id, r2_id],
    }


def _exact_agree(a: list[float], b: list[float]) -> float | None:
    """정수등급 반올림 후 완전일치 비율(보조). N=0 이면 None."""
    pairs = [(round(x), round(y)) for x, y in zip(a, b)]
    if not pairs:
        return None
    return sum(1 for x, y in pairs if x == y) / len(pairs)


def _arm_metrics(
    per_case: list[dict[str, Any]], arm: str, human_pass: float
) -> dict[str, Any]:
    """한 arm 의 종합 지표: false-approve율 / mean|gap| / Pearson r / verdict 일치율."""
    critic_ov, human_ov = [], []
    abs_gaps = []
    fa_num = fa_den = 0          # false-approve: critic approve & human_avg < pass
    verdict_match = verdict_n = 0
    for c in per_case:
        a = c["arms"][arm]
        cov, hav = a["critic_overall"], c["human_avg"]
        if isinstance(cov, (int, float)) and isinstance(hav, (int, float)):
            critic_ov.append(cov)
            human_ov.append(hav)
            abs_gaps.append(abs(cov - hav))
        # false-approve.
        if a["approve"] and isinstance(hav, (int, float)):
            fa_den += 1
            if hav < human_pass:
                fa_num += 1
        # verdict 일치 (critic verdict vs 사람 다수결 verdict).
        hv = c["human_verdicts"]
        if a["verdict"] and hv:
            human_major = _majority(hv)
            verdict_n += 1
            if human_major == a["verdict"]:
                verdict_match += 1
    return {
        "n_scored": len(critic_ov),
        "false_approve_rate": (fa_num / fa_den) if fa_den else None,
        "false_approve_num": fa_num,
        "false_approve_den": fa_den,
        "mean_abs_gap": _mean(abs_gaps),
        "pearson_r": pearson_r(critic_ov, human_ov),
        "verdict_agree_rate": (verdict_match / verdict_n) if verdict_n else None,
        "verdict_agree_num": verdict_match,
        "verdict_agree_den": verdict_n,
        "critic_overall_mean": _mean(critic_ov),
        "human_avg_mean": _mean(human_ov),
        "approve_rate": (
            sum(1 for c in per_case if c["arms"][arm]["approve"]) / len(per_case)
            if per_case else None
        ),
    }


def _majority(verdicts: list[str]) -> str | None:
    """2 rater verdict 다수결 — 동률이면 더 보수적(reject>revise>approve)."""
    if not verdicts:
        return None
    counts = {v: verdicts.count(v) for v in set(verdicts)}
    top = max(counts.values())
    tied = [v for v, n in counts.items() if n == top]
    order = {"reject": 0, "revise": 1, "approve": 2}
    return sorted(tied, key=lambda v: order.get(v, 3))[0]


def _decompose_shallow_gs(per_case: list[dict[str, Any]]) -> dict[str, Any]:
    """SHALLOW vs GS(normal) 분해 — A1 이 얕은셋만 낮췄나(낙관편향↓ / 과교정 가드).

    핵심 질문:
      (1) 얕은셋(SHALLOW): A1 critic_overall 이 A0 보다 낮은가? (낙관편향 보정 작동)
          그리고 A1 이 사람평균(낮을 것)에 더 가까운가? (false-approve 감소)
      (2) 정상셋(GS): A1 이 A0 대비 점수를 **거의 안 낮췄나**? (과교정 가드 — 정상까지 깎으면 실패)
    """
    out: dict[str, Any] = {}
    for label, pred in (
        ("shallow", lambda k: k == "shallow"),
        ("normal", lambda k: k != "shallow"),
    ):
        subset = [c for c in per_case if pred(c["kind"])]
        a0 = [c["arms"]["A0"]["critic_overall"] for c in subset]
        a1 = [c["arms"]["A1"]["critic_overall"] for c in subset]
        ha = [c["human_avg"] for c in subset]
        deltas = [
            (y - x) for x, y in zip(a0, a1)
            if isinstance(x, (int, float)) and isinstance(y, (int, float))
        ]
        gap_a0 = _mean([
            abs(x - h) for x, h in zip(a0, ha)
            if isinstance(x, (int, float)) and isinstance(h, (int, float))
        ])
        gap_a1 = _mean([
            abs(y - h) for y, h in zip(a1, ha)
            if isinstance(y, (int, float)) and isinstance(h, (int, float))
        ])
        out[label] = {
            "n": len(subset),
            "case_ids": [c["case_id"] for c in subset],
            "a0_mean": _mean([x for x in a0 if isinstance(x, (int, float))]),
            "a1_mean": _mean([y for y in a1 if isinstance(y, (int, float))]),
            "human_avg_mean": _mean([h for h in ha if isinstance(h, (int, float))]),
            "mean_delta_a1_minus_a0": _mean(deltas),
            "mean_abs_gap_a0": gap_a0,
            "mean_abs_gap_a1": gap_a1,
            "fa_a0": _fa_count(subset, "A0"),
            "fa_a1": _fa_count(subset, "A1"),
        }
    return out


def _fa_count(subset: list[dict[str, Any]], arm: str) -> dict[str, int]:
    """subset 내 arm 의 (approve & human_avg<3) 카운트 — 분해표용."""
    num = den = 0
    for c in subset:
        a = c["arms"][arm]
        hav = c["human_avg"]
        if a["approve"] and isinstance(hav, (int, float)):
            den += 1
            if hav < DEFAULT_HUMAN_PASS:
                num += 1
    return {"num": num, "den": den}


# ══════════════════════════════════════════════════════════════════════
# 리포트 (6 섹션)
# ══════════════════════════════════════════════════════════════════════

def _fmt(x: float | None, n: int = 3) -> str:
    return f"{x:.{n}f}" if isinstance(x, (int, float)) else "—"


def _fmt_pct(x: float | None) -> str:
    return f"{x * 100:.0f}%" if isinstance(x, (int, float)) else "—"


def render_report(res: dict[str, Any]) -> str:
    dims = res["dims"]
    thr = res["approve_threshold"]
    hp = res["human_pass"]
    L: list[str] = []
    a = L.append

    a("# Critic Calibration A/B (A0 보정OFF vs A1 보정ON) — blind 채점 분석")
    a("")
    a(f"> 날짜: {DATE} | N={res['n_common']} 케이스(교집합) / key {res['n_total_key']} "
      f"| 채점자 2명 ({', '.join(res['rater_ids'])}) blind")
    a(f"> critic_calibration_enabled A0(OFF, 낙관편향) vs A1(ON, anti-optimism + 핵심차원 게이트)")
    a(f"> 통계엔진: {'scipy' if res['have_scipy'] else 'numpy/pure-python fallback'} "
      f"(κ·Wilcoxon·McNemar·r 직접 수식) | LLM 0 · network 0")
    a("")

    # ── 1. 설정 ──
    a("## 1. 설정")
    a("")
    a(f"- **arms**: A0 = critic_calibration OFF (전수 approve 낙관편향), "
      f"A1 = ON (엄격 채점 프롬프트 + 핵심차원 < calibration_min 시 approve→revise 강등).")
    a(f"- **사람 채점**: rubric 5차원(0~5) → human_avg = 산술평균(0~5). "
      f"depth_actionability 는 별도 0~1 축(human_avg 미포함).")
    a(f"- **차원**: {', '.join(dims)}")
    a(f"- **blind 분리**: 채점 HTML 에는 case_id/kind/input/plan 만 임베드. "
      f"hidden A0/A1 critic 점수는 key.json 으로 분리(채점자 미열람, devtools 포함).")
    a(f"- **케이스 구성**: SHALLOW(얕은 plan — 낙관편향 트랩) vs GS(정상 plan — 과교정 가드).")
    a("")

    # ── 2. 통제 (사전동결 임계) ──
    a("## 2. 통제 — 사전동결 임계 (plotter식)")
    a("")
    a("> 분석 **전** 동결. 데이터 보고 임계를 바꾸지 않는다 (사후 합리화 차단).")
    a("")
    a("| 항목 | 동결값 | 출처/근거 |")
    a("|---|---|---|")
    a(f"| critic approve 임계 | overall ≥ **{thr}** (0~5) | critic.py `_derive_verdict` "
      f"(avg ≥ 3.5 AND 모든 점수 ≥ 2) |")
    a(f"| 사람 합격선(human_pass) | human_avg ≥ **{hp}** (0~5) | rubric §2.5 "
      f"\"3점=일부 불만 가능\" 미만 = 미달 |")
    a(f"| false-approve 정의 | critic approve & human_avg < {hp} | 낙관편향의 직접 측정 |")
    a("| κ weight | quadratic (0~5 정수등급 반올림) | Cohen weighted κ 표준 |")
    a("| Wilcoxon | paired, zero 제외, 연속성 보정 | A0 vs A1 critic overall |")
    a("| McNemar | Yates 보정 χ² + binomial exact | approve 비율 변화 |")
    a("| N 소표본 처리 | 점추정 + 방향성 위주, p 는 참고 | N=10 |")
    a("")

    # ── 3. 결과표 ──
    a("## 3. 결과표")
    a("")
    a("### 3.1 케이스별 (사람평균 = 2 rater 평균)")
    a("")
    a("| case_id | kind | human_avg | depth(0~1) | A0 critic | A0 |A0 gap| | A1 critic | A1 |A1 gap| |")
    a("|---|---|---|---|---|---|---|---|")
    for c in res["per_case"]:
        a0, a1 = c["arms"]["A0"], c["arms"]["A1"]
        a(f"| {c['case_id']} | {c['kind']} | {_fmt(c['human_avg'],2)} | "
          f"{_fmt(c['depth_human'],2)} | {_fmt(a0['critic_overall'],2)} | "
          f"{_fmt(a0['abs_gap'],2)} | {_fmt(a1['critic_overall'],2)} | "
          f"{_fmt(a1['abs_gap'],2)} |")
    a("")
    a("### 3.2 차원별 사람평균 (2 rater 평균)")
    a("")
    header = "| case_id | " + " | ".join(dims) + " |"
    a(header)
    a("|" + "---|" * (len(dims) + 1))
    for c in res["per_case"]:
        cells = " | ".join(_fmt(c["dim_human"].get(d), 2) for d in dims)
        a(f"| {c['case_id']} | {cells} |")
    a("")
    a("### 3.3 arm별 종합 지표")
    a("")
    a("| 지표 | A0 (보정OFF) | A1 (보정ON) | 방향 |")
    a("|---|---|---|---|")
    s0, s1 = res["arm_summary"]["A0"], res["arm_summary"]["A1"]
    a(f"| **false-approve율** | {_fmt_pct(s0['false_approve_rate'])} "
      f"({s0['false_approve_num']}/{s0['false_approve_den']}) | "
      f"{_fmt_pct(s1['false_approve_rate'])} "
      f"({s1['false_approve_num']}/{s1['false_approve_den']}) | "
      f"{_arrow_lower_better(s0['false_approve_rate'], s1['false_approve_rate'])} |")
    a(f"| **mean(\\|critic−human\\|)** | {_fmt(s0['mean_abs_gap'])} | "
      f"{_fmt(s1['mean_abs_gap'])} | "
      f"{_arrow_lower_better(s0['mean_abs_gap'], s1['mean_abs_gap'])} |")
    a(f"| **Pearson r (critic vs human)** | {_fmt(s0['pearson_r'])} | "
      f"{_fmt(s1['pearson_r'])} | "
      f"{_arrow_higher_better(s0['pearson_r'], s1['pearson_r'])} |")
    a(f"| **verdict 일치율** | {_fmt_pct(s0['verdict_agree_rate'])} "
      f"({s0['verdict_agree_num']}/{s0['verdict_agree_den']}) | "
      f"{_fmt_pct(s1['verdict_agree_rate'])} "
      f"({s1['verdict_agree_num']}/{s1['verdict_agree_den']}) | "
      f"{_arrow_higher_better(s0['verdict_agree_rate'], s1['verdict_agree_rate'])} |")
    a(f"| critic overall mean | {_fmt(s0['critic_overall_mean'])} | "
      f"{_fmt(s1['critic_overall_mean'])} | — |")
    a(f"| approve 비율 | {_fmt_pct(s0['approve_rate'])} | "
      f"{_fmt_pct(s1['approve_rate'])} | — |")
    a(f"| (참조) 사람평균 mean | {_fmt(s0['human_avg_mean'])} | "
      f"{_fmt(s1['human_avg_mean'])} | — |")
    a("")
    a("### 3.4 inter-rater 일치도")
    a("")
    ir = res["inter_rater"]
    ov = ir["overall"]
    kp = ov["kappa_weighted"]
    a(f"- **overall (0~5)**: weighted κ = **{_fmt(kp['kappa'])}** "
      f"(n={kp['n']}{'; ' + kp['note'] if kp['note'] else ''}) | "
      f"ICC(2,1) = {_fmt(ov['icc_2_1'])} | Pearson r = {_fmt(ov['pearson_r'])} | "
      f"완전일치 = {_fmt_pct(ov['exact_agree_pct'])}")
    a(f"- κ 해석 기준: <0 불일치 / 0~.2 slight / .21~.4 fair / .41~.6 moderate / "
      f".61~.8 substantial / >.8 almost perfect (Landis–Koch). "
      f"★ N={ov['n']} 소표본 — 점추정, 신뢰구간 넓음(주의).")
    a("")
    a("| 차원 | weighted κ | n |")
    a("|---|---|---|")
    for d in dims:
        dk = ir["by_dim"][d]["kappa_weighted"]
        a(f"| {d} | {_fmt(dk['kappa'])}"
          f"{' ⚠' + dk['note'] if dk['note'] else ''} | {dk['n']} |")
    a("")

    # ── 4. 통계 ──
    a("## 4. 통계 (N=10 소표본 — 방향성 위주, 유의성은 참고)")
    a("")
    wil = res["wilcoxon"]
    a(f"- **paired Wilcoxon** (A0 vs A1 critic overall): W = {_fmt(wil['W'],1)}, "
      f"p = {_fmt(wil['p'])} (n_nonzero={wil['n_nonzero']}, {wil['method']})"
      f"{' — ' + wil['note'] if wil['note'] else ''}")
    mcn = res["mcnemar"]
    a(f"- **McNemar** (approve 비율 A0→A1): b(A0✓·A1✗)={mcn['b']}, "
      f"c(A0✗·A1✓)={mcn['c']}, χ²(Yates)={_fmt(mcn['chi2'],3)}, "
      f"p_χ²={_fmt(mcn['p_chi2'])}, p_exact={_fmt(mcn['p_exact'])}"
      f"{' — ' + mcn['note'] if mcn['note'] else ''}")
    a("")
    a("> 해석 가드: N=10 에서 p 값은 검정력이 낮다. **점추정(false-approve율 차·gap 차)과 "
      "방향성**을 1차 근거로, p 는 보조 신호로만 읽는다.")
    a("")

    # ── 5. 핵심 발견 · 메커니즘 분해 ──
    a("## 5. 핵심 발견 · 메커니즘 분해 (SHALLOW vs GS)")
    a("")
    dc = res["decompose"]
    sh, no = dc["shallow"], dc["normal"]
    a("| 분해축 | n | A0 mean | A1 mean | Δ(A1−A0) | gap A0 | gap A1 | FA A0 | FA A1 |")
    a("|---|---|---|---|---|---|---|---|---|")
    a(f"| **SHALLOW(얕음)** | {sh['n']} | {_fmt(sh['a0_mean'],2)} | "
      f"{_fmt(sh['a1_mean'],2)} | {_fmt(sh['mean_delta_a1_minus_a0'],2)} | "
      f"{_fmt(sh['mean_abs_gap_a0'],2)} | {_fmt(sh['mean_abs_gap_a1'],2)} | "
      f"{sh['fa_a0']['num']}/{sh['fa_a0']['den']} | "
      f"{sh['fa_a1']['num']}/{sh['fa_a1']['den']} |")
    a(f"| **GS(정상)** | {no['n']} | {_fmt(no['a0_mean'],2)} | "
      f"{_fmt(no['a1_mean'],2)} | {_fmt(no['mean_delta_a1_minus_a0'],2)} | "
      f"{_fmt(no['mean_abs_gap_a0'],2)} | {_fmt(no['mean_abs_gap_a1'],2)} | "
      f"{no['fa_a0']['num']}/{no['fa_a0']['den']} | "
      f"{no['fa_a1']['num']}/{no['fa_a1']['den']} |")
    a("")
    a("**메커니즘 판독 (2 가설):**")
    a("")
    a(f"- (1) **낙관편향↓ (얕은셋 작동)**: A1 이 SHALLOW 에서 점수를 낮췄나? "
      f"Δ(A1−A0)={_fmt(sh['mean_delta_a1_minus_a0'],2)} → "
      f"{_verdict_lower(sh['mean_delta_a1_minus_a0'])}. "
      f"사람괴리 gap: {_fmt(sh['mean_abs_gap_a0'],2)}→{_fmt(sh['mean_abs_gap_a1'],2)} "
      f"({_verdict_gap(sh['mean_abs_gap_a0'], sh['mean_abs_gap_a1'])}).")
    a(f"- (2) **과교정 가드 (정상셋 보존)**: A1 이 GS 에서 점수를 안 낮췄나? "
      f"Δ(A1−A0)={_fmt(no['mean_delta_a1_minus_a0'],2)} → "
      f"{_verdict_guard(no['mean_delta_a1_minus_a0'])}.")
    a("")
    a("> 이상적 패턴: **SHALLOW Δ < 0 (낮춤) & GS Δ ≈ 0 (보존)** → calibration 이 "
      "얕은 plan 만 선택적으로 깎아 false-approve 를 줄이고 정상 plan 은 해치지 않음.")
    a("")

    # ── 6. 판정 · 한계 ──
    a("## 6. 판정 · 한계")
    a("")
    a("**판정 (사전동결 기준 자동 평가):**")
    a("")
    for line in _verdict_lines(res):
        a(f"- {line}")
    a("")
    a("**한계:**")
    a("")
    a(f"- N={res['n_common']} 소표본 — κ/ICC/p 모두 신뢰구간 넓음. 방향성 신호로 해석.")
    a("- 채점자 2명 — inter-rater 는 점추정. 3명+ 시 재측정 권장.")
    a("- SHALLOW/GS 분해 셀당 표본 작음 — 셀별 통계검정 비실시(기술통계만).")
    a("- critic overall(0~5)과 human_avg(0~5)는 동일 축 가정 — rubric 차원 정의 차이는 "
      "절대 gap 에 일부 반영될 수 있음(상대비교 A0 vs A1 은 통제됨).")
    a("- blind 무결성은 key 분리에 의존 — 채점 HTML 빌드 시 hidden 미임베드 별도 검증 필요.")
    a("")
    return "\n".join(L)


def _arrow_lower_better(a: float | None, b: float | None) -> str:
    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        return "—"
    if b < a:
        return "✅ A1↓ (개선)"
    if b > a:
        return "⚠ A1↑ (악화)"
    return "= 동일"


def _arrow_higher_better(a: float | None, b: float | None) -> str:
    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        return "—"
    if b > a:
        return "✅ A1↑ (개선)"
    if b < a:
        return "⚠ A1↓ (악화)"
    return "= 동일"


def _verdict_lower(delta: float | None) -> str:
    if not isinstance(delta, (int, float)):
        return "데이터 부족"
    if delta < -0.1:
        return "✅ 낮춤(낙관편향 보정 작동)"
    if delta > 0.1:
        return "⚠ 오히려 높임"
    return "≈ 변화 미미"


def _verdict_gap(g0: float | None, g1: float | None) -> str:
    if not isinstance(g0, (int, float)) or not isinstance(g1, (int, float)):
        return "데이터 부족"
    return "괴리↓ 개선" if g1 < g0 else ("괴리↑ 악화" if g1 > g0 else "동일")


def _verdict_guard(delta: float | None) -> str:
    if not isinstance(delta, (int, float)):
        return "데이터 부족"
    if abs(delta) <= 0.15:
        return "✅ 보존(과교정 없음)"
    if delta < 0:
        return "⚠ 정상셋도 깎음(과교정 의심)"
    return "정상셋 상승"


def _verdict_lines(res: dict[str, Any]) -> list[str]:
    """사전동결 기준 자동 판정 라인."""
    lines: list[str] = []
    s0, s1 = res["arm_summary"]["A0"], res["arm_summary"]["A1"]
    dc = res["decompose"]
    sh, no = dc["shallow"], dc["normal"]

    # false-approve.
    fa0, fa1 = s0["false_approve_rate"], s1["false_approve_rate"]
    if isinstance(fa0, (int, float)) and isinstance(fa1, (int, float)):
        if fa1 < fa0:
            lines.append(f"**false-approve ↓**: {_fmt_pct(fa0)} → {_fmt_pct(fa1)} "
                         f"— A1 calibration 이 낙관편향을 줄였다 (1차 목표 달성).")
        elif fa1 > fa0:
            lines.append(f"⚠ **false-approve ↑**: {_fmt_pct(fa0)} → {_fmt_pct(fa1)} "
                         f"— A1 이 오히려 잘못 승인 증가(역효과, 재검토).")
        else:
            lines.append(f"false-approve 동일 ({_fmt_pct(fa0)}) — A1 효과 미검출.")
    else:
        lines.append("false-approve 비교 불가(approve 케이스 부족).")

    # gap.
    g0, g1 = s0["mean_abs_gap"], s1["mean_abs_gap"]
    if isinstance(g0, (int, float)) and isinstance(g1, (int, float)):
        lines.append(f"**critic↔human 괴리** mean|gap|: {_fmt(g0)} → {_fmt(g1)} "
                     f"({'개선' if g1 < g0 else '악화' if g1 > g0 else '동일'}).")

    # 메커니즘 종합 판정.
    sd = sh["mean_delta_a1_minus_a0"]
    nd = no["mean_delta_a1_minus_a0"]
    if isinstance(sd, (int, float)) and isinstance(nd, (int, float)):
        if sd < -0.1 and abs(nd) <= 0.15:
            lines.append("**메커니즘 ✅ 선택적 보정 확인**: 얕은셋만 낮추고(낙관편향↓) "
                         "정상셋은 보존(과교정 가드 통과) → calibration ON 활성 권고.")
        elif sd < -0.1 and nd < -0.15:
            lines.append("⚠ **과교정 의심**: 얕은셋도 정상셋도 함께 깎음 — "
                         "핵심차원 게이트가 정상 plan 까지 강등. calibration_min 재튜닝 필요.")
        elif sd >= -0.1:
            lines.append("⚠ **낙관편향 미보정**: 얕은셋에서 A1 이 점수를 의미있게 "
                         "낮추지 못함 — 보정 강도/프롬프트 재설계 필요.")

    # inter-rater 신뢰.
    kp = res["inter_rater"]["overall"]["kappa_weighted"]["kappa"]
    if isinstance(kp, (int, float)):
        if kp >= 0.6:
            lines.append(f"inter-rater κ={_fmt(kp)} (substantial+) — 사람 채점 신뢰 가능.")
        elif kp >= 0.4:
            lines.append(f"inter-rater κ={_fmt(kp)} (moderate) — 사람 채점 보통, 주의.")
        else:
            lines.append(f"⚠ inter-rater κ={_fmt(kp)} (낮음) — 사람평균 신뢰도 제한, "
                         f"rubric 명확화/3rd rater 필요.")
    return lines


# ══════════════════════════════════════════════════════════════════════
# CLI
# ══════════════════════════════════════════════════════════════════════

def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description="Critic calibration A/B (A0 vs A1) blind 채점 분석 — "
                    "false-approve·괴리·일치도·SHALLOW/GS 분해 리포트 생성.")
    p.add_argument("--key", required=True, type=Path,
                   help="hidden A0/A1 critic 점수 key.json (cases[].hidden 포함).")
    p.add_argument("--rater", action="append", default=[], type=Path,
                   help="채점자 export JSON (2회 지정 — rater 2명).")
    p.add_argument("--out", type=Path, default=None,
                   help="리포트 출력 경로(.md). 미지정 → stdout.")
    p.add_argument("--approve-threshold", type=float,
                   default=DEFAULT_APPROVE_THRESHOLD,
                   help=f"critic approve overall 임계 0~5 (기본 {DEFAULT_APPROVE_THRESHOLD}).")
    p.add_argument("--human-pass", type=float, default=DEFAULT_HUMAN_PASS,
                   help=f"사람 합격선 human_avg 0~5 (기본 {DEFAULT_HUMAN_PASS}).")
    p.add_argument("--json-out", type=Path, default=None,
                   help="(선택) 분석 결과 raw JSON 도 저장.")
    args = p.parse_args(argv)

    if len(args.rater) < 2:
        p.error("--rater 를 2번 지정하세요 (채점자 2명 export).")

    key = _load_json(args.key)
    raters = [_load_json(r) for r in args.rater]

    meta = key.get("meta", {}) if isinstance(key, dict) else {}
    dims = tuple(meta.get("rubric_dims") or DEFAULT_RUBRIC_DIMS)

    res = analyze(
        key, raters,
        dims=dims,
        approve_threshold=args.approve_threshold,
        human_pass=args.human_pass,
    )
    report = render_report(res)

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(report, encoding="utf-8")
        print(f"[analyze_blind_ab] 리포트 작성: {args.out}", file=sys.stderr)
    else:
        print(report)

    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(
            json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[analyze_blind_ab] raw JSON: {args.json_out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
