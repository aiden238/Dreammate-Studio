#!/usr/bin/env python3
"""skill_usage_report.py — 코드 기반 Skill 사용 집계 (측정 접지선, Phase 27 A8).

stale 수동 `meta/skill_usage_log.md`(5/31 이후 미갱신)를 대체한다 — 세션 트랜스크립트의
실제 Skill tool 호출을 deterministic 하게 집계하고 INDEX 정책(미트리거=폐기후보 /
한 세션 3회+=자동화후보)을 적용한다. `cost_report.py`(agent_io 소비)와 동형:
데이터원(트랜스크립트) → 집계 → 마크다운. 기록+소비를 한 묶음으로 코드화.

의존성 0(stdlib), graceful(없는 경로/깨진 줄 skip), LLM 0.

사용:
  python scripts/skill_usage_report.py [transcript_dir] [out_path]
  transcript_dir 미지정 → git 루트로부터 ~/.claude/projects/<encoded> 자동 추론.
  out_path 미지정 → stdout.

★ 한계: Skill 'tool 호출'만 집계. SKILL.md 본문 주입(절차추종)·산출물(ADR/회고) 기반
  사용은 미반영 → '폐기후보'는 tool 미호출이지 dead 확정 아님(보수 해석, 워크플로 감사 정합).
"""
from __future__ import annotations

import glob
import json
import os
import string
import subprocess
import sys
from collections import Counter, defaultdict

_KEEP = set(string.ascii_letters + string.digits)


def repo_root() -> str:
    """repo 루트 = 이 파일(<repo>/harness/scripts/skill_usage_report.py)의 3 level up.

    ★ 결정론적 — git 서브프로세스 회피(Windows cp949 가 한글 경로 stdout 을 못 읽어
    fallback 되던 버그 차단). git 루트와 동일(harness 상위 = CCD projects 인코딩 기준 cwd).
    """
    here = os.path.abspath(__file__)
    root = os.path.dirname(os.path.dirname(os.path.dirname(here)))
    # 안전망: 구조가 다르면 git(utf-8) 시도 → 그래도 실패 시 cwd.
    if os.path.isdir(os.path.join(root, "harness")) or os.path.isdir(os.path.join(root, ".git")):
        return root
    try:
        return subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, check=True,
            encoding="utf-8", errors="replace",
        ).stdout.strip()
    except Exception:
        return os.getcwd()


def ascii_encode(path: str) -> str:
    """CCD projects 디렉토리 인코딩: 비 [A-Za-z0-9] 문자를 '-' 로 (한글·공백·슬래시 포함)."""
    return "".join(c if c in _KEEP else "-" for c in path)


def find_transcript_dir(arg: str | None) -> str:
    if arg and os.path.isdir(arg):
        return arg
    base = os.path.join(os.path.expanduser("~"), ".claude", "projects")
    cand = os.path.join(base, ascii_encode(repo_root()))
    if os.path.isdir(cand):
        return cand
    name = os.path.basename(repo_root()).split("_")[0] or "Dreammate"
    for d in glob.glob(os.path.join(base, f"*{name}*")):
        if os.path.isdir(d):
            return d
    return cand  # 없으면 graceful empty


def defined_skills() -> list[str]:
    """.claude/skills/*/ 디렉토리명 = 정의된 skill 목록 (repo 기준, deterministic)."""
    for root in (os.getcwd(), os.path.join(os.getcwd(), "harness"),
                 os.path.join(repo_root(), "harness")):
        p = os.path.join(root, ".claude", "skills")
        if os.path.isdir(p):
            return sorted(
                d for d in os.listdir(p)
                if os.path.isdir(os.path.join(p, d)) and not d.startswith(".")
            )
    return []


def collect(transcript_dir: str):
    total: Counter = Counter()
    per_session_max: dict[str, int] = defaultdict(int)
    sessions = 0
    for fn in glob.glob(os.path.join(transcript_dir, "*.jsonl")):
        sessions += 1
        sess: Counter = Counter()
        try:
            with open(fn, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        o = json.loads(line)
                    except Exception:
                        continue
                    if o.get("type") != "assistant":
                        continue
                    c = o.get("message", {}).get("content")
                    if not isinstance(c, list):
                        continue
                    for part in c:
                        if (isinstance(part, dict) and part.get("type") == "tool_use"
                                and part.get("name") == "Skill"):
                            s = (part.get("input", {}) or {}).get("skill", "?")
                            sess[s] += 1
        except Exception:
            continue
        for s, n in sess.items():
            total[s] += n
            per_session_max[s] = max(per_session_max[s], n)
    return total, per_session_max, sessions


def render(defined, total, per_session_max, sessions, transcript_dir) -> str:
    used = [s for s in defined if total.get(s, 0) > 0]
    dead = [s for s in defined if total.get(s, 0) == 0]
    auto = [s for s in defined if per_session_max.get(s, 0) >= 3]
    unknown = [s for s in total if s not in defined]
    L = [
        "# Skill Usage Report (code-generated, Phase 27 A8)",
        "",
        f"> source: `{transcript_dir}` · sessions: {sessions} · 정의 skill: {len(defined)} · tool 호출된: {len(used)}",
        "> 생성: `scripts/skill_usage_report.py` (deterministic, LLM 0). 정책: 미트리거=폐기후보 / 3회+세션=자동화후보.",
        "",
        "## 호출 집계 (Skill tool 기준, total 내림차순)",
        "| skill | total calls | max/세션 | 자동화후보(≥3) |",
        "|---|---|---|---|",
    ]
    for s in sorted(defined, key=lambda x: -total.get(x, 0)):
        n = total.get(s, 0)
        m = per_session_max.get(s, 0)
        L.append(f"| {s} | {n} | {m} | {'★' if m >= 3 else ''} |")
    L += [
        "",
        f"## 폐기후보 (Skill tool 호출 0건) — {len(dead)}개",
        (", ".join(dead) if dead else "(없음)"),
        "",
        f"## 자동화후보 (한 세션 3회+) — {len(auto)}개",
        (", ".join(auto) if auto else "(없음)"),
    ]
    if unknown:
        L += ["", "## ⚠️ 정의 외 호출(이름 불일치/폐기됨)",
              ", ".join(f"{s}({total[s]})" for s in unknown)]
    L += ["",
          "> ★ 한계: Skill 'tool 호출'만 집계. SKILL.md 본문 주입(절차추종)·산출물(ADR/회고)"
          " 기반 사용은 미반영 → '폐기후보'는 tool 미호출이지 dead 확정 아님(보수 해석)."]
    return "\n".join(L)


def main(argv: list[str]) -> int:
    transcript_dir = find_transcript_dir(argv[0] if argv else None)
    out_path = argv[1] if len(argv) > 1 else None
    defined = defined_skills()
    total, psm, sessions = collect(transcript_dir)
    md = render(defined, total, psm, sessions, transcript_dir)
    if out_path:
        os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(md)
        print(f"written: {out_path} ({sessions} sessions, {sum(total.values())} skill calls, "
              f"{len(defined)} defined)")
    else:
        print(md)
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    except Exception:
        pass
    raise SystemExit(main(sys.argv[1:]))
