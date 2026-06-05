"""HIP-006 S2 — cost-review reader/aggregator.

HIP-006 S1 발신기(agent_io_log.py)가 쌓은 agent_io 텔레메트리 JSONL 을 읽어
비용/토큰/실패/latency 를 집계하고 eval/cost_snapshots/{date}.md 형식 스냅샷을 렌더한다.
→ "데이터원 부재로 cost-review 동결"(meta/audits/2026-06-05.md §3) 의 소비측 해소.

graceful: 없는 파일/깨진 줄은 건너뛴다(raise 0). 순수 함수 — 부작용은 build_cost_snapshot 의
out_path 쓰기뿐(미지정 시 쓰기 0). cost-review Skill 이 본 모듈을 호출해 스냅샷을 만든다.
"""

from __future__ import annotations

import json
import logging
import os
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any

from ..config import get_settings

logger = logging.getLogger(__name__)


def load_agent_io_records(path: str) -> list[dict[str, Any]]:
    """JSONL → record list. 없는 파일/깨진 줄은 graceful skip (raise 0)."""
    records: list[dict[str, Any]] = []
    if not path or not os.path.exists(path):
        return records
    try:
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except (ValueError, TypeError):
                    continue  # 깨진 줄 skip
                if isinstance(rec, dict):
                    records.append(rec)
    except OSError as exc:
        logger.debug("cost_report load 실패 (graceful): %s", exc)
    return records


def aggregate_agent_io(records: list[dict[str, Any]]) -> dict[str, Any]:
    """record list → 집계 dict (totals + by_model + by_agent)."""
    by_model: dict[str, dict[str, float]] = defaultdict(
        lambda: {"calls": 0, "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0}
    )
    by_agent: dict[str, dict[str, float]] = defaultdict(
        lambda: {"calls": 0, "cost_usd": 0.0}
    )
    total_in = total_out = 0
    total_cost = 0.0
    cost_known = cost_unknown = 0
    success = failure = 0
    latencies: list[int] = []

    for r in records:
        model = str(r.get("model", "?"))
        agent = str(r.get("agent_name", "?"))
        in_tok = int(r.get("input_tokens") or 0)
        out_tok = int(r.get("output_tokens") or 0)
        total_in += in_tok
        total_out += out_tok
        by_model[model]["calls"] += 1
        by_model[model]["input_tokens"] += in_tok
        by_model[model]["output_tokens"] += out_tok
        by_agent[agent]["calls"] += 1

        cost = r.get("cost_usd", None)
        if cost is not None:
            try:
                c = float(cost)
            except (ValueError, TypeError):
                cost_unknown += 1
            else:
                total_cost += c
                by_model[model]["cost_usd"] += c
                by_agent[agent]["cost_usd"] += c
                cost_known += 1
        else:
            cost_unknown += 1

        if r.get("success", True):
            success += 1
        else:
            failure += 1

        lat = r.get("latency_ms", None)
        if isinstance(lat, (int, float)):
            latencies.append(int(lat))

    return {
        "total_calls": len(records),
        "success_calls": success,
        "failure_calls": failure,
        "total_input_tokens": total_in,
        "total_output_tokens": total_out,
        "total_tokens": total_in + total_out,
        "total_cost_usd": round(total_cost, 6),
        "cost_known_calls": cost_known,
        "cost_unknown_calls": cost_unknown,
        "avg_latency_ms": (
            round(sum(latencies) / len(latencies), 1) if latencies else None
        ),
        "max_latency_ms": max(latencies) if latencies else None,
        "by_model": {m: dict(v) for m, v in by_model.items()},
        "by_agent": {a: dict(v) for a, v in by_agent.items()},
    }


def render_cost_markdown(
    agg: dict[str, Any], *, source_path: str = "", generated_at: str = ""
) -> str:
    """집계 dict → eval/cost_snapshots 스냅샷 markdown."""
    lines = [
        f"# Cost Snapshot — {generated_at}",
        "",
        f"> source: `{source_path}` · records: {agg['total_calls']}",
        "> HIP-006 cost-review (observability/cost_report.py) — agent_io 텔레메트리 집계.",
        "",
        "## 요약",
        f"- 호출: {agg['total_calls']} (성공 {agg['success_calls']} / 실패 {agg['failure_calls']})",
        f"- 토큰: in {agg['total_input_tokens']} / out {agg['total_output_tokens']} / total {agg['total_tokens']}",
        f"- 비용(추정): ${agg['total_cost_usd']} (known {agg['cost_known_calls']} / unknown {agg['cost_unknown_calls']} calls)",
        f"- latency: avg {agg['avg_latency_ms']} ms / max {agg['max_latency_ms']} ms",
        "",
        "## 모델별",
        "| model | calls | in_tok | out_tok | cost_usd |",
        "|---|---|---|---|---|",
    ]
    for m, v in sorted(agg["by_model"].items()):
        lines.append(
            f"| {m} | {v['calls']} | {v['input_tokens']} | {v['output_tokens']} | {round(v['cost_usd'], 6)} |"
        )
    lines += ["", "## agent별", "| agent | calls | cost_usd |", "|---|---|---|"]
    for a, v in sorted(agg["by_agent"].items()):
        lines.append(f"| {a} | {v['calls']} | {round(v['cost_usd'], 6)} |")
    lines.append("")
    return "\n".join(lines)


def build_cost_snapshot(
    jsonl_path: str | None = None,
    out_path: str | None = None,
    generated_at: str | None = None,
) -> dict[str, Any]:
    """텔레메트리 → 집계 + 스냅샷 markdown. out_path 지정 시 파일 기록.

    jsonl_path 미지정 시 settings.agent_io_log_path 사용 (HIP-006 발신기 기본 경로).
    Returns: {"aggregate", "markdown", "source", "out_path"}.
    """
    path = jsonl_path or getattr(
        get_settings(), "agent_io_log_path", "logs/telemetry/agent_io.jsonl"
    )
    records = load_agent_io_records(path)
    agg = aggregate_agent_io(records)
    stamp = generated_at or datetime.now(timezone.utc).isoformat()
    md = render_cost_markdown(agg, source_path=path, generated_at=stamp)
    if out_path:
        parent = os.path.dirname(out_path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as fh:
            fh.write(md)
    return {"aggregate": agg, "markdown": md, "source": path, "out_path": out_path}


if __name__ == "__main__":  # pragma: no cover
    import sys

    _jsonl = sys.argv[1] if len(sys.argv) > 1 else None
    _out = sys.argv[2] if len(sys.argv) > 2 else None
    _res = build_cost_snapshot(jsonl_path=_jsonl, out_path=_out)
    print(_res["markdown"])
