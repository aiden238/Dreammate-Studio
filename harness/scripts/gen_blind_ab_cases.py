"""Critic calibration A/B (HIP-007) blind 케이스 생성 스크립트.

목적
====
사람 blind 채점용 A/B 데이터를 생성한다. 10케이스(정상 5 + 얕은 5) 각각에 대해:
  1. 입력 1개 → 실 LLM 으로 기획안 3안 생성 (run_planning_parallel_3) →
     critic 으로 채점해 추천 1안(recommended_index)을 plan 으로 고정.
  2. 같은 plan 을 critic 으로 **2번** 채점:
       A0 = calibration OFF (critic_calibration_enabled=False)
       A1 = calibration ON  (critic_calibration_enabled=True)
     → A0/A1 의 overall_score_avg · verdict · dimensions 캡처.
  3. 출력 2파일 분리(blind):
       eval/human_review/2026-06-15-calib-ab-cases.json — case_id/kind/input/plan + hidden(A0/A1)
       eval/human_review/2026-06-15-calib-ab-key.json   — case_id + hidden(A0/A1) 만 (정답키)
     ★ 최종 채점 HTML 은 cases[].{case_id,kind,input,plan} 만 임베드하고 hidden 은 절대
       포함하지 않는다 — 이 스크립트는 데이터 산출만 하며, hidden 을 cases 와 key 양쪽에 두되
       채점 HTML 빌더가 cases 에서 hidden 을 strip 하도록 한다(이 파일의 책임 밖).

A0/A1 토글 방식 (critic.py 실제 구조 기준)
==========================================
critic.run_critic() 는 settings 인자를 받지 않고 내부에서 get_settings() 를 호출해
`critic_calibration_enabled` (+ effective_output_mode 별 CALIBRATION_KEY_DIMS) 를 읽는다.
따라서 토글은 **환경변수 override + get_settings.cache_clear()** 로 한다:
    os.environ["CRITIC_CALIBRATION_ENABLED"] = "false"|"true"
    get_settings.cache_clear()
    run_critic(plan, client=...)
calibration ON 시 (1) anti-optimism 프리앰블이 system prompt 에 붙고
(2) _derive_verdict 의 핵심 차원 게이트(approve→revise 강등)가 적용된다.

★ output_mode 고정: critic 의 차원 집합/calibration key dims 는 effective_output_mode 에
  의존한다. .env 의 APP_PROFILE=realuse 는 output_mode=director 를 함의하므로, 본 스크립트는
  재현성을 위해 OUTPUT_MODE 를 명시 고정한다(기본 director — depth_actionability +
  retention_design 이 calibration key dims 이라 "88점 함정" 토글이 가장 선명).

비용 가드
=========
--smoke (기본) 는 1케이스만 실행한다 (실 LLM: 기획 3안 1배치 + critic 채점 소수).
전체 10케이스 실행(--generate)은 본 스크립트도 지원하나, 본 단계(스크립트 작성+smoke)에서는
호출하지 않는다 (Generate 단계가 수행).

사용
====
  cd harness && python scripts/gen_blind_ab_cases.py            # smoke (1케이스)
  cd harness && python scripts/gen_blind_ab_cases.py --generate # 전체 10케이스 (Generate 단계 전용)
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any

# ── stdout utf-8 강제 (Windows cp949 콘솔 방어) ──────────────────────────
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
except Exception:  # noqa: BLE001
    pass

# ── 경로 ────────────────────────────────────────────────────────────────
# 본 파일: harness/scripts/gen_blind_ab_cases.py → parents[1] = harness 루트.
HARNESS_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = HARNESS_ROOT / "backend" / "fastapi"
OUT_DIR = HARNESS_ROOT / "eval" / "human_review"
DATE = "2026-06-15"
CASES_PATH = OUT_DIR / f"{DATE}-calib-ab-cases.json"
KEY_PATH = OUT_DIR / f"{DATE}-calib-ab-key.json"

# backend 패키지(`backend.fastapi.*`) import 를 위해 harness 루트를 sys.path 에.
if str(HARNESS_ROOT) not in sys.path:
    sys.path.insert(0, str(HARNESS_ROOT))


# ── .env 로더 (verify_llm_keys.py 패턴 재사용 — 의존성 0) ──────────────────
def load_dotenv() -> str | None:
    """harness/backend/fastapi/.env 를 os.environ 으로 로드 (.env 값 우선)."""
    candidates = [
        BACKEND_DIR / ".env",
        HARNESS_ROOT / ".env",
        Path(".env"),
    ]
    for path in candidates:
        if path.exists():
            with open(path, encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    key, val = line.split("=", 1)
                    val = val.strip().strip('"').strip("'")
                    if val:
                        os.environ[key.strip()] = val
            return str(path)
    return None


# ── 케이스 입력 정의 ──────────────────────────────────────────────────────
# 얕은 5케이스: 의도적 빈약 입력 (88점 함정 유발 — calibration ON 시 강등 기대).
SHALLOW_INPUTS: list[str] = [
    "유튜브 영상 하나 만들고 싶어",
    "30초 쇼츠",
    "브이로그",
    "재밌는 콘텐츠 아무거나",
    "맛집 소개 영상",
]

# 정상 5케이스: golden_set 에서 서로 다른 도메인 입력 5개 선택 (loader 우선, 폴백 내장).
# golden_set 의 user_message 중 placeholder("(...)" 류)는 제외하고 실제 도메인 입력만 채택.
_NORMAL_FALLBACK_INPUTS: list[str] = [
    "대학생 창업동아리 운영하면서 영상 만들고 싶어요",
    "동아리 신입 모집 영상 30초로 만들고 싶어",
    "자취 요리 브이로그를 정보형으로 만들고 싶어",
    "재테크 기초를 알려주는 60초 정보형 영상",
    "반려견 산책 일상을 담은 감성 브이로그",
]

# rubric 5축(스키마 meta.rubric_dims) — critic 8/9/10 차원을 사람 채점 5축으로 매핑.
RUBRIC_DIMS = [
    "content_quality",
    "safety",
    "brand_fit",
    "actionability_depth",
    "differentiation",
]
DEPTH_AXIS = "depth_actionability(0~1 별도축)"

# critic 차원 → rubric 5축 매핑 (집계용 — 평균으로 5축 환산).
#   critic dims: intent_fit/target_clarity/hook_strength/message_clarity/structure/
#                feasibility/brand_consistency/differentiation[/depth_actionability/retention_design]
_RUBRIC_FROM_CRITIC: dict[str, tuple[str, ...]] = {
    "content_quality": ("intent_fit", "message_clarity", "structure", "hook_strength"),
    "safety": ("brand_consistency",),
    "brand_fit": ("target_clarity", "brand_consistency"),
    "actionability_depth": ("feasibility", "depth_actionability", "retention_design"),
    "differentiation": ("differentiation",),
}


def _select_normal_inputs() -> list[str]:
    """golden_set 에서 서로 다른 도메인 실입력 5개 선택 (폴백 내장)."""
    try:
        from backend.fastapi.eval.golden_set_loader import load_golden_set

        cases = load_golden_set()
    except Exception:  # noqa: BLE001 — loader 실패 시 폴백
        cases = []

    picked: list[str] = []
    seen: set[str] = set()
    for c in cases:
        inp = c.get("input") or {}
        msg = inp.get("user_message") if isinstance(inp, dict) else None
        if not isinstance(msg, str):
            continue
        msg = msg.strip()
        # placeholder/컨텍스트성 입력 배제 ("(...)" 로 시작) + 너무 짧은 입력 배제.
        if not msg or msg.startswith("(") or len(msg) < 8:
            continue
        if msg in seen:
            continue
        seen.add(msg)
        picked.append(msg)
        if len(picked) >= 5:
            break

    # 부족분은 폴백으로 채움 (정상 5케이스 보장).
    for fb in _NORMAL_FALLBACK_INPUTS:
        if len(picked) >= 5:
            break
        if fb not in seen:
            seen.add(fb)
            picked.append(fb)
    return picked[:5]


# ── critic 토글 호출 ──────────────────────────────────────────────────────
def _score_with_calibration(plan_body: dict[str, Any], *, enabled: bool, client: Any) -> dict[str, Any]:
    """calibration 토글(env override + cache_clear) 후 run_critic 1회.

    critic.run_critic 는 get_settings() 를 내부 호출하므로, 환경변수로 calibration 을 켜고
    캐시를 비운 뒤 호출해야 토글이 반영된다. output_mode 도 동일 메커니즘으로 고정 유지된다.
    """
    from backend.fastapi.agents.critic import run_critic
    from backend.fastapi.config import get_settings

    os.environ["CRITIC_CALIBRATION_ENABLED"] = "true" if enabled else "false"
    get_settings.cache_clear()  # type: ignore[attr-defined]
    verdict = run_critic(plan_body, client=client)
    return verdict


def _to_arm_record(verdict: dict[str, Any]) -> dict[str, Any]:
    """critic verdict → hidden arm 레코드 (overall/verdict/dimensions + rubric 5축 + depth 별도축)."""
    scores: dict[str, Any] = verdict.get("scores") or {}
    # rubric 5축 환산 (0~5).
    rubric: dict[str, float] = {}
    for dim, sources in _RUBRIC_FROM_CRITIC.items():
        vals = [float(scores[s]) for s in sources if s in scores]
        rubric[dim] = round(sum(vals) / len(vals), 4) if vals else None  # type: ignore[assignment]
    # depth 별도축 (0~1) — depth_actionability 가 있으면 /5, 없으면 None.
    depth_raw = scores.get("depth_actionability")
    depth_0_1 = round(float(depth_raw) / 5.0, 4) if isinstance(depth_raw, (int, float)) else None
    return {
        "overall_score_avg": verdict.get("overall_score_avg"),
        "verdict": verdict.get("overall_verdict"),
        "dimensions": rubric,           # 스키마 meta.rubric_dims 5축 (0~5)
        "raw_scores": scores,           # critic 원 차원 (8/9/10) — 투명성/디버그
        "depth_axis_0_1": depth_0_1,    # depth_actionability 별도축 (0~1)
    }


# ── 케이스 1개 생성 ───────────────────────────────────────────────────────
async def _build_one_case(
    case_id: str,
    kind: str,
    user_input: str,
    *,
    client: Any,
) -> dict[str, Any]:
    """입력 1개 → 기획 3안 생성 → 추천 1안 plan 고정 → A0/A1 채점 → 케이스 dict."""
    from backend.fastapi.agents.critic import select_best_plan_index
    from backend.fastapi.agents.planning import run_planning_parallel_3
    from backend.fastapi.config import get_settings

    # 추천 선택용 채점은 default(파일·env 의 calibration 상태)로 — A0/A1 토글과 무관.
    #   (calibration 비활성으로 명시 고정 → 추천 선택은 보정 전 점수 기준, 결정적.)
    os.environ["CRITIC_CALIBRATION_ENABLED"] = "false"
    get_settings.cache_clear()  # type: ignore[attr-defined]

    plans = await run_planning_parallel_3(user_input, rag_context=[], client=client)

    # 각 안 채점 → recommended_index (canonical 기반 best-plan).
    from backend.fastapi.agents.critic import normalize_to_canonical, run_critic

    bodies: list[dict[str, Any]] = []
    verdicts: list[dict[str, Any]] = []
    for env in plans:
        body = env.get("plan", {}) if isinstance(env, dict) else {}
        bodies.append(body)
        verdicts.append(normalize_to_canonical(run_critic(body, client=client)))

    rec_idx = select_best_plan_index(verdicts)
    if rec_idx is None or not (0 <= rec_idx < len(bodies)):
        rec_idx = 0
    plan = bodies[rec_idx]

    # 같은 plan 을 A0(OFF)/A1(ON) 으로 각각 채점.
    a0 = _score_with_calibration(plan, enabled=False, client=client)
    a1 = _score_with_calibration(plan, enabled=True, client=client)

    return {
        "case_id": case_id,
        "kind": kind,
        "input": user_input,
        "plan": plan,
        "hidden": {
            "A0": _to_arm_record(a0),
            "A1": _to_arm_record(a1),
        },
    }


# ── 빌드 엔트리 ───────────────────────────────────────────────────────────
def _make_client() -> Any:
    from openai import OpenAI

    key = os.environ.get("OPENAI_API_KEY", "")
    if not key:
        raise RuntimeError("OPENAI_API_KEY 미설정 (.env 또는 환경변수 확인)")
    return OpenAI(api_key=key)


async def _build_all(*, smoke: bool) -> dict[str, Any]:
    """smoke=True → 1케이스(첫 정상 1건). smoke=False → 정상5+얕은5 전체."""
    client = _make_client()
    normal_inputs = _select_normal_inputs()

    cases: list[dict[str, Any]] = []
    if smoke:
        # 비용 가드: 정상 1케이스만 (A0≠A1 토글·스키마 검증 목적).
        cases.append(
            await _build_one_case("GS-001", "normal", normal_inputs[0], client=client)
        )
    else:
        for i, inp in enumerate(normal_inputs, start=1):
            cases.append(
                await _build_one_case(f"GS-{i:03d}", "normal", inp, client=client)
            )
        for i, inp in enumerate(SHALLOW_INPUTS, start=1):
            cases.append(
                await _build_one_case(f"SHALLOW-{i}", "shallow", inp, client=client)
            )

    meta = {
        "date": DATE,
        "n": len(cases),
        "arms": ["A0", "A1"],
        "rubric_dims": RUBRIC_DIMS,
        "depth_axis": DEPTH_AXIS,
        "output_mode": os.environ.get("OUTPUT_MODE", "director"),
        "toggle": "env CRITIC_CALIBRATION_ENABLED + get_settings.cache_clear()",
        "smoke": smoke,
    }
    return {"meta": meta, "cases": cases}


def _write_outputs(payload: dict[str, Any]) -> None:
    """cases(plan 포함 전체) + key(hidden 분리) 2파일 기록.

    blind 원칙: 채점 HTML 은 cases[].{case_id,kind,input,plan} 만 임베드한다. hidden 은
    cases 파일에도 두되(전체 데이터 산출물), 정답키는 key 파일로 별도 분리해 채점자가
    devtools 로도 못 보게 한다(채점 HTML 빌더가 cases 에서 hidden 을 strip).
    """
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    # cases: plan 포함 전체 (hidden 포함 — Generate 단계 산출물).
    CASES_PATH.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    # key: case_id + hidden 만 (정답키 분리).
    key_payload = {
        "meta": payload["meta"],
        "cases": [
            {"case_id": c["case_id"], "kind": c["kind"], "hidden": c["hidden"]}
            for c in payload["cases"]
        ],
    }
    KEY_PATH.write_text(
        json.dumps(key_payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Critic calibration A/B blind 케이스 생성")
    parser.add_argument(
        "--generate",
        action="store_true",
        help="전체 10케이스 생성 (정상5+얕은5). 미지정 시 smoke(1케이스).",
    )
    parser.add_argument(
        "--output-mode",
        default="director",
        choices=["compact", "rich", "director", "commercial_viral"],
        help="critic/planning output_mode 고정 (default director — depth+retention key dims).",
    )
    parser.add_argument(
        "--no-write",
        action="store_true",
        help="파일 기록 생략 (smoke 검증만 — stdout 요약).",
    )
    args = parser.parse_args()

    loaded = load_dotenv()
    # ★ output_mode 고정 (재현성). APP_PROFILE=realuse 의 director 함의를 명시 override.
    os.environ["OUTPUT_MODE"] = args.output_mode
    # realuse 프로파일이 다른 flag 를 끌어들이지 않도록 프로파일은 default 로 중립화
    #   (critic/planning 토글만 본 스크립트가 통제 — output_mode 는 위에서 명시 고정).
    os.environ["APP_PROFILE"] = "default"

    smoke = not args.generate
    print("=== Critic calibration A/B 케이스 생성 ===")
    print(f".env: {loaded or '(미발견 — 환경변수만)'}")
    print(f"mode: {'SMOKE(1케이스)' if smoke else 'GENERATE(10케이스)'} | output_mode={args.output_mode}")
    print(f"toggle: CRITIC_CALIBRATION_ENABLED env + get_settings.cache_clear()\n")

    payload = asyncio.run(_build_all(smoke=smoke))

    # 콘솔 요약 (A0/A1 점수 예시 — 키 평문 미노출).
    for c in payload["cases"]:
        a0, a1 = c["hidden"]["A0"], c["hidden"]["A1"]
        print(
            f"[{c['case_id']:10}] {c['kind']:7} | "
            f"A0 avg={a0['overall_score_avg']} verdict={a0['verdict']} depth01={a0['depth_axis_0_1']} | "
            f"A1 avg={a1['overall_score_avg']} verdict={a1['verdict']} depth01={a1['depth_axis_0_1']}"
        )
        toggled = (a0["verdict"] != a1["verdict"]) or (
            a0["overall_score_avg"] != a1["overall_score_avg"]
        )
        print(f"             toggle A0≠A1: {'YES' if toggled else 'NO (동일 — 점수/판정 변화 없음)'}")

    if not args.no_write:
        _write_outputs(payload)
        print(f"\ncases → {CASES_PATH}")
        print(f"key   → {KEY_PATH}")
    else:
        print("\n(--no-write: 파일 기록 생략)")

    # smoke 성공 판정: 1케이스의 A0/A1 가 모두 캡처됐고 스키마(verdict/overall/dimensions) 존재.
    ok = bool(payload["cases"]) and all(
        c["hidden"]["A0"].get("verdict") and c["hidden"]["A1"].get("verdict")
        and c["hidden"]["A0"].get("dimensions") and c["hidden"]["A1"].get("dimensions")
        for c in payload["cases"]
    )
    print(f"\nsmoke 통과(A0/A1 캡처+스키마): {'OK' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
