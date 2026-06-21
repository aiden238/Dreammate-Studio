"""RAG Gemini 채택 — 재현 가능 측정 프로브 (2026-06-21, project-2 잔여 2c-measure).

project-2(2026-06-09~10)가 Temp/(gitignored)에서 했던 rag_gemini_adopt / rag_embed_measure
를 **커밋 스크립트로 재작성**(같은 유실 방지). 실 Gemini 임베딩 + Supabase RPC 호출.

무엇을 측정하나:
  1. approved_knowledge 코퍼스 상태 (total / promoted+active = 검색 대상).
  2. RAG_EMBEDDING_PROVIDER=gemini 로 3개 ko 쿼리(시드 8건 주제 매칭) retrieval.search()
     @ threshold 0.7 과 0.4 — hit 수 + top similarity + 매칭 tag.

비용: Gemini embedContent 3~6콜(미미) + Supabase RPC. ★ 시크릿 출력 0 (키명/SET 여부만).

실행:  python scripts/rag_gemini_probe.py     (rootdir = harness/, .env = backend/fastapi/.env)
"""
from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

# Windows 콘솔(cp949)에서도 ko/기호 출력 깨짐·크래시 방지
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
except Exception:
    pass

HARNESS = Path(__file__).resolve().parents[1]
ENV_PATH = HARNESS / "backend" / "fastapi" / ".env"


def _load_env() -> None:
    """backend/fastapi/.env → os.environ (Settings 가 os.environ 우선 채택)."""
    if not ENV_PATH.exists():
        print(f"[FATAL] .env 없음: {ENV_PATH}")
        sys.exit(2)
    for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        os.environ.setdefault(k.strip(), v.strip())
    # ★ 측정 핵심: 임베딩 provider 를 gemini 로 override (default openai).
    os.environ["RAG_EMBEDDING_PROVIDER"] = "gemini"


# 시드 8건(2026-06-10_candidate-ready.md) 주제 매칭 ko 쿼리
QUERIES = [
    ("무음후크/브이로그", "릴스 브이로그 무음 자동재생일 때 첫 1초 후크를 어떻게 설계해야 해?"),
    ("챌린지/CTA", "틱톡 챌린지 영상에서 핵심 동작은 어떻게 보여주고 따라찍기 CTA는 언제 넣어?"),
    ("리뷰/언박싱", "유튜브 쇼츠 언박싱 리뷰에서 후크랑 단점 언급은 어떻게 구성해?"),
]


async def main() -> None:
    _load_env()
    # env 세팅 후 import (Settings 캐시가 gemini 로 고정되도록)
    sys.path.insert(0, str(HARNESS))
    from backend.fastapi.config import get_settings
    from backend.fastapi.db.client import get_supabase
    from backend.fastapi.rag import retrieval

    s = get_settings()
    print("=== 환경 (시크릿 미출력) ===")
    for name in ("google_api_key", "supabase_url"):
        val = getattr(s, name, "") or ""
        print(f"  {name}: {'[SET]' if val else '[MISSING]'}")
    print(f"  rag_embedding_provider: {getattr(s, 'rag_embedding_provider', '?')}")
    print(f"  rag_embedding_gemini_model: {getattr(s, 'rag_embedding_gemini_model', '?')}")
    print(f"  rag_embedding_dim: {getattr(s, 'rag_embedding_dim', '?')}")
    print(f"  rag_threshold(default): {getattr(s, 'rag_threshold', '?')}")

    # 1) 코퍼스 상태
    print("\n=== 코퍼스 (approved_knowledge) ===")
    sb = get_supabase()
    if sb is None:
        print("  [WARN] supabase unconfigured — retrieval graceful empty")
    else:
        try:
            total = sb.table("approved_knowledge").select("id", count="exact").execute()
            print(f"  total rows: {getattr(total, 'count', '?')}")
            # status/is_active 분포는 Python 집계(서버측 필터 컬럼 차이 회피)
            rows = sb.table("approved_knowledge").select("*").execute()
            data = getattr(rows, "data", None) or []
            from collections import Counter

            st = Counter(str((r or {}).get("status")) for r in data)
            act = sum(1 for r in data if (r or {}).get("is_active") in (True, "true", 1))
            cols = sorted(data[0].keys()) if data else []
            print(f"  status 분포: {dict(st)}")
            print(f"  is_active=true: {act}/{len(data)}")
            print(f"  컬럼: {cols}")
        except Exception as exc:
            print(f"  [WARN] 코퍼스 조회: {exc.__class__.__name__}: {str(exc)[:120]}")

    # 2) Gemini 검색 @0.7 / @0.4
    for thr in (0.7, 0.4):
        print(f"\n=== retrieval.search @ threshold {thr} (Gemini 임베딩) ===")
        for label, q in QUERIES:
            try:
                hits = await retrieval.search(q, top_k=5, threshold=thr)
            except Exception as exc:
                print(f"  {label}: [ERR {exc.__class__.__name__}]")
                continue
            if not hits:
                print(f"  {label}: 0 hits")
                continue
            tops = []
            for h in hits[:3]:
                sim = h.get("similarity")
                tag = (h.get("metadata") or {}).get("tag", "?")
                sim_s = f"{sim:.3f}" if isinstance(sim, (int, float)) else "?"
                tops.append(f"{sim_s}({tag})")
            print(f"  {label}: {len(hits)} hits -- top: {', '.join(tops)}")


if __name__ == "__main__":
    asyncio.run(main())
