"""Cross-provider Judge rescore — Claude(Anthropic)로 10 plan 재채점 (연구 스크립트).

목적 (research only, production code 0 변경):
  OpenAI 가 생성한 10 기획안을 **다른 provider(Claude/Anthropic)** 로 재채점하여,
  기존 gpt-4o critic(A0=calibration OFF / A1=calibration ON) 및 사람(rater A) 점수와
  비교한다. 가설: cross-provider judge 가 self-review 편향을 깨고 genericness 를 더
  잡아 verdict(approve→revise/reject)를 사람 쪽으로 뒤집는가 ("88점 함정" 차단).

재사용:
  - backend critic 의 DIRECTOR_SYSTEM_PROMPT / DIMENSIONS_DIRECTOR / _derive_verdict
    (cases meta output_mode=director → A0/A1 와 동일한 10차원 축으로 채점).
  - AnthropicAdapter + registry.get_model("claude-sonnet") (cross_validation.py 와 같은
    gateway seam: registry→adapter). cross_validation alias 는 Gemini 이고 alias 표에
    Sonnet 항목이 없어(plan_secondary→claude-haiku 만), judge=상위 모델 위해 registry KEY 직접 사용.
  - 10 raw dim → 5 rubric 축 매핑은 A0/A1 키와 동일 (content_quality / safety / brand_fit /
    actionability_depth / differentiation). safety 는 critic 10차원에 없어 5.0 상수(A0/A1 동일).

실 LLM(Anthropic) 호출. PYTHONIOENCODING=utf-8. 실패/malformed 1회 재시도 + 기록.
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

# ── Windows 콘솔 utf-8 + 백엔드 import 경로 ───────────────────────────────
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
except Exception:  # noqa: BLE001
    pass

HARNESS = Path(__file__).resolve().parents[1]          # .../harness
BACKEND = HARNESS / "backend" / "fastapi"
sys.path.insert(0, str(HARNESS))                        # `backend.fastapi.*` 패키지 import (상대 import 정합)

# .env 로드 (verify_llm_keys.py 패턴 — ANTHROPIC_API_KEY) ──────────────────
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

# critic 프롬프트/차원/verdict 재사용 (backend 직접 import) ───────────────────
from backend.fastapi.agents.critic import (  # noqa: E402
    DIMENSIONS_DIRECTOR,
    DIRECTOR_SYSTEM_PROMPT,
    _derive_verdict,
)
from backend.fastapi.config import get_settings  # noqa: E402
from backend.fastapi.llm import registry  # noqa: E402
from backend.fastapi.llm.providers.anthropic_adapter import AnthropicAdapter  # noqa: E402
from backend.fastapi.llm.types import LLMMessage, LLMRequest  # noqa: E402

# ── 데이터 경로 ───────────────────────────────────────────────────────────
HR = HARNESS / "eval" / "human_review"
CASES_PATH = HR / "2026-06-15-calib-ab-cases.json"
OUT_PATH = HR / "2026-06-15-calib-ab-claude.json"

# Claude judge = 강한 모델(Sonnet). 'claude-sonnet' 은 registry KEY (alias 표엔 Sonnet→없음;
#   plan_secondary→claude-haiku 만 존재). cross_validation.py 와 동일한 gateway seam(registry→
#   adapter)을 쓰되, alias 계층만 우회해 registry key 로 직접 강한 모델을 고른다 (judge = 상위 모델).
JUDGE_REGISTRY_KEY = "claude-sonnet"   # → settings.anthropic_model_sonnet (claude-sonnet-4-6)
JUDGE_TEMPERATURE = 0.1   # 평가 일관성 (0~0.2)
JUDGE_MAX_TOKENS = 2000   # director 10차원 scores+reasons+suggestions

# 10 raw dim → 5 rubric 축 매핑 (A0/A1 키와 byte-identical 산식).
#   content_quality      = avg(intent_fit, message_clarity, structure, hook_strength)
#   actionability_depth  = avg(feasibility, depth_actionability, retention_design)
#   brand_fit            = avg(brand_consistency, target_clarity)
#   differentiation      = differentiation (raw)
#   safety               = 5.0 상수 (critic 10차원에 없음 — A0/A1 동일 default)
RUBRIC_MAP: dict[str, tuple[str, ...]] = {
    "content_quality": ("intent_fit", "message_clarity", "structure", "hook_strength"),
    "actionability_depth": ("feasibility", "depth_actionability", "retention_design"),
    "brand_fit": ("brand_consistency", "target_clarity"),
    "differentiation": ("differentiation",),
}
SAFETY_CONST = 5.0


def _rubric_5(raw: dict[str, int]) -> dict[str, float]:
    out: dict[str, float] = {"safety": SAFETY_CONST}
    for axis, dims in RUBRIC_MAP.items():
        vals = [float(raw[d]) for d in dims]
        out[axis] = round(sum(vals) / len(vals), 4)
    return out


def _parse_scores(text: str) -> dict[str, int]:
    """Claude JSON 응답 → 10차원 정수 scores (critic run_critic 검증 로직 정합)."""
    parsed = json.loads(text)
    scores = parsed.get("scores")
    if not isinstance(scores, dict):
        raise ValueError("scores 객체 없음")
    missing = [k for k in DIMENSIONS_DIRECTOR if k not in scores]
    if missing:
        raise ValueError(f"scores 누락 차원: {missing}")
    norm: dict[str, int] = {}
    for k in DIMENSIONS_DIRECTOR:
        norm[k] = max(0, min(5, int(round(float(scores[k])))))
    return norm


def _judge_one(adapter: AnthropicAdapter, model_id: str, api_key: str, plan: dict
               ) -> tuple[dict[str, int], str]:
    """단일 plan Claude 채점 → (raw 10dim scores, raw_text).

    AnthropicAdapter 직접 호출(gateway seam) — json_mode=True 면 adapter 가 system 에
    JSON 지시 + 응답 코드펜스 제거(_strip_json_fences, A11 malformed 방어)까지 수행.
    """
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
    return _parse_scores(text), text


def main() -> int:
    cases = json.load(open(CASES_PATH, encoding="utf-8"))["cases"]
    settings = get_settings()
    model = registry.get_model(JUDGE_REGISTRY_KEY)
    model_id = model["model_id"]
    api_key = settings.anthropic_api_key
    if not api_key:
        print("ANTHROPIC_API_KEY 미설정 — 중단", file=sys.stderr)
        return 2
    adapter = AnthropicAdapter()

    print("=== Cross-provider Judge rescore (Claude/Anthropic) ===")
    print(f".env: {_loaded or '(미발견)'}")
    print(f"judge: registry={JUDGE_REGISTRY_KEY} model={model_id} provider={model['provider']}")
    print(f"temp={JUDGE_TEMPERATURE} | mode=director(10dim)")
    print(f"cases: {CASES_PATH}\n")

    results: list[dict] = []
    failures: list[dict] = []

    for c in cases:
        cid = c["case_id"]
        plan = dict(c["plan"])
        plan.setdefault("plan_id", cid)
        raw_scores = None
        raw_text = ""
        last_err = ""
        for attempt in (1, 2):  # 1회 재시도
            try:
                raw_scores, raw_text = _judge_one(adapter, model_id, api_key, plan)
                break
            except Exception as e:  # noqa: BLE001
                last_err = f"{type(e).__name__}: {str(e)[:160]}"
                print(f"[{cid}] attempt {attempt} 실패: {last_err}")
                time.sleep(1.0)

        if raw_scores is None:
            failures.append({"case_id": cid, "error": last_err, "raw": raw_text[:400]})
            print(f"[{cid}] FAILED (2 attempts)\n")
            continue

        avg, verdict = _derive_verdict(raw_scores, dimensions=DIMENSIONS_DIRECTOR)
        rubric5 = _rubric_5(raw_scores)
        results.append(
            {
                "case_id": cid,
                "kind": c.get("kind"),
                "A2_claude": {
                    "overall_score_avg": round(avg, 4),  # 10 raw dim 평균 (A0/A1 동일 산식)
                    "verdict": verdict,
                    "dimensions": rubric5,                # 5 rubric 축 0~5 (A0/A1 동일 매핑)
                    "raw_scores": raw_scores,             # 10차원 critic 0~5
                    "depth_axis_0_1": round(raw_scores["depth_actionability"] / 5.0, 4),
                },
            }
        )
        print(f"[{cid}] {c.get('kind'):8} overall={avg:.3f} verdict={verdict}")

    out = {
        "meta": {
            "date": "2026-06-21",
            "judge": "claude (anthropic, cross-provider)",
            "judge_registry_key": JUDGE_REGISTRY_KEY,
            "model_id": model_id,
            "model_id_note": "registry claude-sonnet → settings.anthropic_model_sonnet",
            "temperature": JUDGE_TEMPERATURE,
            "output_mode": "director",
            "n": len(results),
            "failures": len(failures),
            "rubric_map": {k: list(v) for k, v in RUBRIC_MAP.items()},
            "safety_const": SAFETY_CONST,
        },
        "cases": results,
        "failures": failures,
    }
    OUT_PATH.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n저장: {OUT_PATH}  (ok={len(results)}, fail={len(failures)})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
