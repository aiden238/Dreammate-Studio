"""Phase 31 S3 — golden_set RAG ON/OFF 품질측정 (RAG가 plan 품질을 올리나).

검증된 cross-provider Claude judge 로 RAG grounding 의 생성 품질 기여를 bounded 측정.
project-2 교훈(Temp 유실) 따라 **커밋 재현 스크립트**. RAG 검색은 6ba1aaf 라이브 검증분 재사용.

축:
  - 검색: RAG_EMBEDDING_PROVIDER=gemini, retrieval.search @0.7 (approved_knowledge 8건).
  - 생성: OpenAI gpt-4o-mini, director 프롬프트(v1.2.1).
    ON  = 검색 청크를 '참고자료(RAG)' 로 user 프롬프트에 주입.
    OFF = 주입 없음(동일 입력).
  - 채점: _judge_one (Claude claude-sonnet, 10차원). 비교: overall Δ.

비용: 쿼리수 × {ON,OFF} × (검색 + 생성 + 채점). ★ 시크릿 출력 0.
실행: python scripts/phase31_rag_onoff.py   (rootdir harness/)
"""
from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
except Exception:
    pass

HARNESS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HARNESS))

ENV = HARNESS / "backend" / "fastapi" / ".env"


def _load_env() -> None:
    for line in ENV.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip())
    os.environ["RAG_EMBEDDING_PROVIDER"] = "gemini"  # 검색측 Gemini(라이브 검증분)


_load_env()

from scripts.cross_provider_judge_rescore import _judge_one  # noqa: E402
from backend.fastapi.agents.planning import DIRECTOR_SYSTEM_PROMPT  # noqa: E402
from backend.fastapi.agents.critic import DIMENSIONS_DIRECTOR  # noqa: E402
from backend.fastapi.llm import registry  # noqa: E402
from backend.fastapi.llm.providers.anthropic_adapter import AnthropicAdapter  # noqa: E402
from backend.fastapi.rag import retrieval  # noqa: E402

# 시드 8건 주제 매칭 — RAG 가 실제 청크를 줄 수 있는 쿼리
QUERIES = [
    ("브이로그", "일상 브이로그 영상 기획안 — 무음 자동재생 환경에서 후크를 살리고 싶어"),
    ("리뷰", "제품 언박싱 리뷰 숏폼 기획안 — 진정성 있게 보이고 싶어"),
]


async def _retrieve(q: str) -> list[str]:
    hits = await retrieval.search(q, top_k=3, threshold=0.7)
    return [str(h.get("content", "")).strip() for h in hits if h.get("content")]


def _mean10(scores: dict) -> float:
    return round(sum(scores[d] for d in DIMENSIONS_DIRECTOR) / len(DIMENSIONS_DIRECTOR), 3)


def _gen(client, user_input: str, rag_chunks: list[str]) -> dict:
    ctx = ""
    if rag_chunks:
        joined = "\n".join(f"- {c}" for c in rag_chunks)
        ctx = f"\n\n참고자료(RAG, 복제 금지·맥락 반영):\n{joined}"
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": DIRECTOR_SYSTEM_PROMPT},
            {"role": "user", "content": f"한 줄 기획 방향: {user_input}{ctx}"},
        ],
        response_format={"type": "json_object"},
        temperature=0.6,
        max_tokens=8000,  # director plan 절단 방지(gpt-4o-mini max 16k)
    )
    obj = json.loads(resp.choices[0].message.content or "{}")
    return obj.get("plan", obj)


async def main() -> int:
    from openai import OpenAI

    oai = OpenAI()
    model = registry.get_model("claude-sonnet")
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        print("[FATAL] ANTHROPIC_API_KEY 없음")
        return 2
    adapter = AnthropicAdapter()

    print("=== Phase 31 S3 — RAG ON/OFF 품질 (Claude judge) ===")
    results = []
    for qid, ui in QUERIES:
        chunks = await _retrieve(ui)
        print(f"  [{qid}] 검색 청크 {len(chunks)}건")
        scores_by = {}
        for cond, ch in (("OFF", []), ("ON", chunks)):
            try:
                plan = _gen(oai, ui, ch)
                sc, _ = _judge_one(adapter, model["model_id"], api_key, plan)
                m = _mean10(sc)
                scores_by[cond] = m
                print(f"     {cond:3}: overall(10d)={m}")
            except Exception as exc:
                scores_by[cond] = None
                print(f"     {cond:3}: [ERR {exc.__class__.__name__}: {str(exc)[:80]}]")
        results.append((qid, len(chunks), scores_by))

    print("\n=== Δ (ON - OFF) ===")
    for qid, nch, sb in results:
        off, on = sb.get("OFF"), sb.get("ON")
        if isinstance(off, float) and isinstance(on, float):
            print(f"  {qid:8} (청크 {nch}): {off} -> {on}  Δ={round(on - off, 3):+}")
        else:
            print(f"  {qid:8}: 측정 불가")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
