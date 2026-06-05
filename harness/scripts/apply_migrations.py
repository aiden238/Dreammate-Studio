#!/usr/bin/env python3
"""Phase 27 S4 — Supabase/Postgres migration 적용 (B-4 · M-1).

0001~0008 마이그레이션을 순서대로 적용한다. match_approved_knowledge RPC(0008) 포함.
모든 마이그레이션은 멱등(IF NOT EXISTS / OR REPLACE / IF EXISTS) → 재실행 안전.

사용:
  python scripts/apply_migrations.py --list      # (오프라인) 적용 순서·크기 출력
  python scripts/apply_migrations.py --apply     # psql + DATABASE_URL 로 순서 적용
  python scripts/apply_migrations.py --verify     # 핵심 객체(RPC/테이블) 존재 확인

전제 (--apply / --verify):
  - 환경변수 DATABASE_URL (또는 backend/fastapi/.env 의 DATABASE_URL) = Supabase Postgres
    연결 문자열 (예: postgresql://postgres:...@db.xxxx.supabase.co:5432/postgres).
  - psql CLI 설치 (Supabase 표준). 미설치 시 Supabase SQL Editor 로 각 파일을 순서대로 실행.
  - ★ 키/URL 은 backend/fastapi/.env (.gitignore) 에만. 코드/커밋/로그 평문 금지.

★ Phase 27 범위 = 스크립트/절차 제공까지. 실제 운영 DB 적용은 ops(사용자 인프라).
"""

from __future__ import annotations

import argparse
import glob
import os
import subprocess
import sys
from pathlib import Path
from shutil import which

# Windows 콘솔(cp949)에서 한글/em-dash 출력 안전화.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
    except Exception:
        pass

REPO = Path(__file__).resolve().parents[1]
MIG_DIR = REPO / "backend" / "fastapi" / "db" / "migrations"

# 적용 후 존재해야 하는 핵심 객체 (B-4 RPC + 4계층/PKM 테이블).
VERIFY_SQL = (
    "SELECT "
    "EXISTS(SELECT 1 FROM pg_proc WHERE proname='match_approved_knowledge') AS rpc_match_approved_knowledge, "
    "to_regclass('public.plans')                IS NOT NULL AS table_plans, "
    "to_regclass('public.brands')               IS NOT NULL AS table_brands, "
    "to_regclass('public.pkm_entries')          IS NOT NULL AS table_pkm_entries, "
    "to_regclass('public.brand_memory_entries') IS NOT NULL AS table_brand_memory_entries;"
)


def migrations() -> list[Path]:
    """4자리 prefix 마이그레이션만 정렬 (legacy 3자리 001_init.sql 제외)."""
    files = sorted(glob.glob(str(MIG_DIR / "[0-9][0-9][0-9][0-9]_*.sql")))
    return [Path(f) for f in files]


def load_database_url() -> str:
    url = os.environ.get("DATABASE_URL", "").strip()
    if url:
        return url
    env = REPO / "backend" / "fastapi" / ".env"
    if env.exists():
        for line in env.read_text(encoding="utf-8").splitlines():
            s = line.strip()
            if s.startswith("DATABASE_URL="):
                return s.split("=", 1)[1].strip().strip('"').strip("'")
    return ""


def cmd_list() -> int:
    migs = migrations()
    if not migs:
        print(f"✗ 마이그레이션 없음: {MIG_DIR}", file=sys.stderr)
        return 1
    print(f"적용 순서 ({len(migs)} migrations) — {MIG_DIR}")
    for i, m in enumerate(migs, 1):
        print(f"  {i:>2}. {m.name}  ({m.stat().st_size} bytes)")
    print("\n전부 멱등(IF NOT EXISTS / OR REPLACE) → 재실행 안전.")
    print("적용: python scripts/apply_migrations.py --apply")
    return 0


def _backend():
    """적용 백엔드 선택: psql(우선) → psycopg2(폴백). (name, module|None) 반환."""
    if which("psql") is not None:
        return ("psql", None)
    try:
        import psycopg2  # type: ignore

        return ("psycopg2", psycopg2)
    except ImportError:
        return (None, None)


def _resolve() -> tuple[str, str, object] | None:
    """(url, backend, module) 또는 None(전제 미충족)."""
    url = load_database_url()
    if not url:
        print("✗ DATABASE_URL 미설정 (env 또는 backend/fastapi/.env).", file=sys.stderr)
        return None
    name, mod = _backend()
    if name is None:
        print(
            "✗ psql 미설치 + psycopg2 미설치. 택1: (a) pip install psycopg2-binary "
            "(b) psql 설치 (c) Supabase SQL Editor 로 0001~0008 순서 실행.",
            file=sys.stderr,
        )
        return None
    return (url, name, mod)


def _apply_file(name: str, mod: object, url: str, path: Path) -> bool:
    if name == "psql":
        return (
            subprocess.run(["psql", url, "-v", "ON_ERROR_STOP=1", "-f", str(path)]).returncode
            == 0
        )
    # psycopg2 — 파일 전체를 한 트랜잭션으로 (dollar-quoted 함수 본문 안전).
    conn = mod.connect(url)  # type: ignore[attr-defined]
    try:
        conn.autocommit = False
        with conn.cursor() as cur:
            cur.execute(path.read_text(encoding="utf-8"))
        conn.commit()
        return True
    except Exception as e:  # noqa: BLE001 — 어떤 DB 에러든 중단 + 보고
        conn.rollback()
        print(f"  ✗ {type(e).__name__}: {str(e).splitlines()[0]}", file=sys.stderr)
        return False
    finally:
        conn.close()


def cmd_apply() -> int:
    r = _resolve()
    if r is None:
        return 2
    url, name, mod = r
    print(f"(백엔드: {name})")
    for m in migrations():
        print(f"→ 적용: {m.name}")
        if not _apply_file(name, mod, url, m):
            print(f"✗ 실패: {m.name} — 중단.", file=sys.stderr)
            return 4
    print("✓ 전체 마이그레이션 적용 완료.")
    return cmd_verify()


def cmd_verify() -> int:
    r = _resolve()
    if r is None:
        return 2
    url, name, mod = r
    print("→ 핵심 객체 검증 (RPC + 테이블):")
    if name == "psql":
        return (
            0
            if subprocess.run(
                ["psql", url, "-v", "ON_ERROR_STOP=1", "-t", "-A", "-c", VERIFY_SQL]
            ).returncode
            == 0
            else 5
        )
    conn = mod.connect(url)  # type: ignore[attr-defined]
    try:
        with conn.cursor() as cur:
            cur.execute(VERIFY_SQL)
            row = cur.fetchone()
            cols = [d[0] for d in cur.description]
        for c, v in zip(cols, row):
            mark = "✓" if v else "✗"
            print(f"  {mark} {c:32} = {v}")
        return 0 if all(row) else 5
    except Exception as e:  # noqa: BLE001
        print(f"  ✗ {type(e).__name__}: {str(e).splitlines()[0]}", file=sys.stderr)
        return 5
    finally:
        conn.close()


def main() -> int:
    p = argparse.ArgumentParser(description="Dreammate migration apply (Phase 27 S4)")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--list", action="store_true", help="적용 순서 출력 (오프라인)")
    g.add_argument("--apply", action="store_true", help="psql + DATABASE_URL 로 순서 적용")
    g.add_argument("--verify", action="store_true", help="핵심 객체 존재 확인")
    a = p.parse_args()
    if a.list:
        return cmd_list()
    if a.apply:
        return cmd_apply()
    return cmd_verify()


if __name__ == "__main__":
    raise SystemExit(main())
