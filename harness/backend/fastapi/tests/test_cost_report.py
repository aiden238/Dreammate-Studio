"""HIP-006 S2 cost-review reader/aggregator — 단위 테스트 (hermetic).

검증: JSONL 로드(깨진 줄/없는 파일 graceful) / 집계(totals·by_model·by_agent·latency·
cost known·unknown) / markdown 렌더 / build_cost_snapshot 파일 기록 + settings 기본 경로.
참조: meta/audits/2026-06-05.md (HIP-006), meta/improvement_roadmap_hip006-010.md (006-S2).
"""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from backend.fastapi.observability import cost_report as cr


@dataclass
class _FakeSettings:
    agent_io_log_path: str


def test_load_skips_bad_and_missing(tmp_path) -> None:
    p = tmp_path / "a.jsonl"
    p.write_text(
        '{"model":"gpt-4o-mini","agent_name":"planning"}\n'
        "NOT JSON\n"
        "\n"
        '{"model":"gpt-4o","agent_name":"critic"}\n',
        encoding="utf-8",
    )
    recs = cr.load_agent_io_records(str(p))
    assert len(recs) == 2  # 깨진 줄 + 빈 줄 skip
    assert cr.load_agent_io_records(str(tmp_path / "missing.jsonl")) == []


def test_aggregate_totals_and_breakdown() -> None:
    records = [
        {"model": "gpt-4o-mini", "agent_name": "planning", "input_tokens": 100, "output_tokens": 50, "cost_usd": 0.001, "latency_ms": 200, "success": True},
        {"model": "gpt-4o-mini", "agent_name": "planning", "input_tokens": 200, "output_tokens": 100, "cost_usd": 0.002, "latency_ms": 400, "success": True},
        {"model": "gpt-4o", "agent_name": "critic", "input_tokens": 300, "output_tokens": 150, "cost_usd": None, "latency_ms": None, "success": False},
    ]
    agg = cr.aggregate_agent_io(records)
    assert agg["total_calls"] == 3
    assert agg["success_calls"] == 2
    assert agg["failure_calls"] == 1
    assert agg["total_input_tokens"] == 600
    assert agg["total_output_tokens"] == 300
    assert agg["total_tokens"] == 900
    assert agg["total_cost_usd"] == pytest.approx(0.003)
    assert agg["cost_known_calls"] == 2
    assert agg["cost_unknown_calls"] == 1
    assert agg["by_model"]["gpt-4o-mini"]["calls"] == 2
    assert agg["by_model"]["gpt-4o-mini"]["cost_usd"] == pytest.approx(0.003)
    assert agg["by_agent"]["critic"]["calls"] == 1
    assert agg["avg_latency_ms"] == pytest.approx(300.0)  # (200+400)/2, None 제외
    assert agg["max_latency_ms"] == 400


def test_render_markdown_contains_key_numbers() -> None:
    agg = cr.aggregate_agent_io(
        [{"model": "gpt-4o", "agent_name": "critic", "input_tokens": 10, "output_tokens": 5, "cost_usd": 0.01, "latency_ms": 100, "success": True}]
    )
    md = cr.render_cost_markdown(agg, source_path="x.jsonl", generated_at="2026-06-05T00:00:00Z")
    assert "Cost Snapshot" in md
    assert "gpt-4o" in md
    assert "critic" in md
    assert "0.01" in md


def test_build_snapshot_writes_file(tmp_path) -> None:
    src = tmp_path / "agent_io.jsonl"
    src.write_text(
        '{"model":"gpt-4o-mini","agent_name":"planning","input_tokens":100,"output_tokens":50,"cost_usd":0.001,"latency_ms":200,"success":true}\n',
        encoding="utf-8",
    )
    out = tmp_path / "snap" / "cost.md"
    res = cr.build_cost_snapshot(jsonl_path=str(src), out_path=str(out), generated_at="2026-06-05T00:00:00Z")
    assert res["aggregate"]["total_calls"] == 1
    assert out.exists()
    assert "Cost Snapshot" in out.read_text(encoding="utf-8")


def test_build_snapshot_uses_settings_path_when_none(tmp_path, monkeypatch) -> None:
    src = tmp_path / "agent_io.jsonl"
    src.write_text("", encoding="utf-8")
    monkeypatch.setattr(cr, "get_settings", lambda: _FakeSettings(str(src)))
    res = cr.build_cost_snapshot(generated_at="2026-06-05T00:00:00Z")  # jsonl_path None → settings
    assert res["source"] == str(src)
    assert res["aggregate"]["total_calls"] == 0
