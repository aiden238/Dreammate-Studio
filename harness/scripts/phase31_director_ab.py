"""Phase 31 S2 — P-006 director v1.2.0 vs v1.2.1 A/B (prompt-version-review 확인 측정).

검증된 cross-provider Claude judge 로 생성 프롬프트 개선(특이성+정직가드)의 회귀 비퇴행을
bounded 라이브 확인. project-2 교훈(Temp 유실) 따라 **커밋 재현 스크립트**.

축:
  - 생성: OpenAI gpt-4o-mini, director 프롬프트 OLD(v1.2.0, 재구성) vs NEW(v1.2.1, 현행).
  - 채점: scripts/cross_provider_judge_rescore._judge_one (Claude claude-sonnet, 10차원).
  - 비교: overall(10dim 평균) Δ + 정직 라벨('추정/예시:') 준수 + 슬롯 과확장 여부.

비용: 2케이스 × {old,new} × (생성 1 + 채점 1) = 8 LLM 콜. ★ 시크릿 출력 0.
실행: python scripts/phase31_director_ab.py   (rootdir harness/)
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

# 재사용: judge 헬퍼 + dotenv (cross_provider_judge_rescore 는 import 시 main 미실행=guarded)
from scripts.cross_provider_judge_rescore import (  # noqa: E402
    JUDGE_REGISTRY_KEY,
    _judge_one,
    _load_dotenv,
)
from backend.fastapi.agents.planning import DIRECTOR_SYSTEM_PROMPT as GEN_NEW  # noqa: E402
from backend.fastapi.agents.critic import DIMENSIONS_DIRECTOR  # noqa: E402
from backend.fastapi.llm import registry  # noqa: E402
from backend.fastapi.llm.providers.anthropic_adapter import AnthropicAdapter  # noqa: E402

# OLD(v1.2.0) = NEW 에서 v1.2.1 추가 블록 제거(재구성)
_MARK = "\n\n[P-006 v1.2.1"
GEN_OLD = GEN_NEW.split(_MARK)[0]
assert len(GEN_OLD) < len(GEN_NEW), "v1.2.1 블록 분리 실패 — 프롬프트 마커 확인"

CASES = [
    ("normal", "대학생 창업 동아리 신입 모집 영상 — 동아리의 실제 프로젝트와 분위기를 보여주고 싶어"),
    ("shallow", "맛집 영상 만들고 싶어"),
]


def _gen_plan(client, prompt: str, user_input: str) -> dict:
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": f"한 줄 기획 방향: {user_input}"},
        ],
        response_format={"type": "json_object"},
        temperature=0.6,
        max_tokens=8000,  # director plan(rich 12 + director 3슬롯)은 매우 큼 — 절단 방지(gpt-4o-mini max 16k)
    )
    raw = resp.choices[0].message.content or "{}"
    obj = json.loads(raw)
    return obj.get("plan", obj)


def _mean10(scores: dict) -> float:
    return round(sum(scores[d] for d in DIMENSIONS_DIRECTOR) / len(DIMENSIONS_DIRECTOR), 3)


def _honesty(plan: dict) -> tuple[int, int]:
    """(라벨된 추정 수, 잠재 단정 레퍼런스 수) — 정직 가드 준수 신호."""
    refs = plan.get("references") or []
    refs = [str(r) for r in refs if str(r).strip()]
    labeled = sum(1 for r in refs if "추정" in r or "예시" in r)
    # why_this_works 도 점검
    why_labeled = 0
    for sc in plan.get("scene_breakdown") or []:
        w = str((sc or {}).get("why_this_works", ""))
        if "추정" in w or "예시" in w:
            why_labeled += 1
    return labeled + why_labeled, len(refs)


def main() -> int:
    _load_dotenv()
    from openai import OpenAI

    oai = OpenAI()
    model = registry.get_model(JUDGE_REGISTRY_KEY)
    import os

    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        print("[FATAL] ANTHROPIC_API_KEY 없음")
        return 2
    adapter = AnthropicAdapter()

    print("=== Phase 31 S2 — director v1.2.0 vs v1.2.1 (Claude judge) ===")
    rows = []
    for cid, ui in CASES:
        for ver, prompt in (("v1.2.0", GEN_OLD), ("v1.2.1", GEN_NEW)):
            try:
                plan = _gen_plan(oai, prompt, ui)
                scores, _ = _judge_one(adapter, model["model_id"], api_key, plan)
                m = _mean10(scores)
                labeled, n_refs = _honesty(plan)
                rows.append((cid, ver, m, labeled, n_refs))
                print(f"  {cid:8} {ver}: overall(10d)={m}  정직라벨={labeled} / refs={n_refs}")
            except Exception as exc:
                rows.append((cid, ver, None, None, None))
                print(f"  {cid:8} {ver}: [ERR {exc.__class__.__name__}: {str(exc)[:80]}]")

    print("\n=== Δ (v1.2.1 - v1.2.0) ===")
    for cid, _ in CASES:
        old = next((r[2] for r in rows if r[0] == cid and r[1] == "v1.2.0"), None)
        new = next((r[2] for r in rows if r[0] == cid and r[1] == "v1.2.1"), None)
        if isinstance(old, float) and isinstance(new, float):
            print(f"  {cid:8}: {old} -> {new}  Δ={round(new - old, 3):+}")
        else:
            print(f"  {cid:8}: 측정 불가(생성/채점 실패)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
