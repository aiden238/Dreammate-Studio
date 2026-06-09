#!/usr/bin/env python3
"""check_boundaries.py — 프로젝트(L1 런타임) ↔ 지침(L2 하네스) 경계 게이트.

경계 정의: harness/BOUNDARIES.md / 정책: harness/meta/factory/factory_contract.md 규칙1.
이동 없는 명시적 경계 표시의 '기계 강제' 절반(나머지 절반 = .github/CODEOWNERS 가시성).

동작:
  - 기본(advisory): staged diff를 분류·보고하고 경고만 한다(exit 0). 기존 워크플로 0 변경.
  - --strict: 경계 위반 시 exit 1 (pre-commit hook / CI 연결용).
  - 파일 목록을 인자로 주면 그걸 검사(git 없이 테스트 가능).

위반(WARN/strict FAIL) 규칙:
  1) [governance] 한 변경집합이 L2 계약(docs/contracts/**)과 L1 런타임을 동시에 수정
     → 계약 격리 위반(contract-change는 별도 커밋이어야 함).
  2) [factory_contract 규칙1] meta/factory/** 변경과 L1 런타임 변경이 한 집합에 공존
     → 메타-하네스는 L1 read-only여야 함.
경고(항상 advisory):
  3) L1 런타임(backend/fastapi·apps/web·migrations) 변경 가시화.

의존성 0(stdlib만). Windows/Unix 공통(git이 forward-slash 경로 반환).
"""
from __future__ import annotations

import subprocess
import sys

# Windows cp949 등에서도 한글/em-dash 출력 안전(pre-commit/CI 콘솔 무관).
try:
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
except Exception:  # pragma: no cover
    pass

# repo-root 상대 경로(forward slash) 접두사. harness/ 는 repo 루트의 하위.
L1_RUNTIME = (
    "harness/backend/fastapi/",
    "harness/apps/web/",
    "harness/packages/",
)
L1_MIGRATIONS = ("harness/backend/fastapi/db/migrations/",)
L2_CONTRACTS = ("harness/docs/contracts/", "harness/.claude/skills/")
L2_META_FACTORY = ("harness/meta/factory/",)


def _staged_files() -> list[str]:
    try:
        out = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            capture_output=True, text=True, check=True,
        ).stdout
    except Exception:
        return []
    return [ln.strip() for ln in out.splitlines() if ln.strip()]


def _has(files: list[str], prefixes: tuple[str, ...]) -> list[str]:
    return [f for f in files if any(f.startswith(p) for p in prefixes)]


def check(files: list[str]) -> tuple[list[str], list[str]]:
    """returns (violations, warnings)."""
    l1 = _has(files, L1_RUNTIME + L1_MIGRATIONS)
    contracts = _has(files, L2_CONTRACTS)
    factory = _has(files, L2_META_FACTORY)

    violations: list[str] = []
    warnings: list[str] = []

    if l1 and contracts:
        violations.append(
            "[계약 격리] 한 변경집합이 L1 런타임과 L2 계약(docs/contracts·skills)을 동시 수정. "
            "contract-change는 별도 커밋으로 분리하라. "
            f"(런타임 {len(l1)}개 / 계약 {len(contracts)}개)"
        )
    if l1 and factory:
        violations.append(
            "[factory_contract 규칙1 위반] meta/factory/** 변경이 L1 런타임 변경과 공존 — "
            "메타-하네스는 L1 read-only여야 한다."
        )
    if l1:
        warnings.append(
            f"[가시화] L1 Product Runtime {len(l1)}개 변경: " + ", ".join(l1[:8])
            + (" ..." if len(l1) > 8 else "")
        )
    return violations, warnings


def main(argv: list[str]) -> int:
    strict = "--strict" in argv
    files = [a for a in argv if not a.startswith("--")]
    if not files:
        files = _staged_files()
    if not files:
        print("check_boundaries: 검사할 파일 없음(staged 0).")
        return 0

    violations, warnings = check(files)
    for w in warnings:
        print("WARN  " + w)
    for v in violations:
        print("VIOLATION  " + v)

    if violations and strict:
        print(f"\n경계 위반 {len(violations)}건 — strict 모드 실패. BOUNDARIES.md 참조.")
        return 1
    if violations:
        print(f"\n경계 위반 {len(violations)}건(advisory). --strict면 차단. BOUNDARIES.md 참조.")
    else:
        print("경계 OK.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
