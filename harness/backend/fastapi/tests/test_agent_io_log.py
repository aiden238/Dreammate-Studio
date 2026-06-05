"""HIP-006 agent_io 텔레메트리 발신기 — 단위 + gateway 통합 (hermetic, 실 API 0).

검증:
  - gated default-off: 비활성 시 미기록(False) + 파일 미생성 (behavior-preserving)
  - enabled: JSONL 1행 + db_schema §7.1 정합 필드 + cost 추정
  - graceful: 잘못된 경로라도 raise 안 함(False)
  - estimate_cost_usd: 등록 모델 계산 / 미등록 None
  - gateway.complete 통합: alias→agent_name, provider/model/tokens/latency 기록
참조: meta/audits/2026-06-05.md (HIP-006), docs/contracts/db_schema.md §7.1.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from unittest.mock import MagicMock

import pytest

from backend.fastapi.config import Settings
from backend.fastapi.llm.gateway import LLMGateway
from backend.fastapi.llm.types import LLMResponse, LLMUsage
from backend.fastapi.observability import agent_io_log as aio


@dataclass
class _FakeSettings:
    agent_io_log_enabled: bool
    agent_io_log_path: str


def _patch(monkeypatch, enabled: bool, path) -> None:
    monkeypatch.setattr(aio, "get_settings", lambda: _FakeSettings(enabled, str(path)))


def test_disabled_is_noop(tmp_path, monkeypatch) -> None:
    p = tmp_path / "agent_io.jsonl"
    _patch(monkeypatch, False, p)
    assert aio.log_agent_io(agent_name="planning", model="gpt-4o-mini") is False
    assert not p.exists()


def test_enabled_writes_one_record(tmp_path, monkeypatch) -> None:
    p = tmp_path / "nested" / "agent_io.jsonl"
    _patch(monkeypatch, True, p)
    ok = aio.log_agent_io(
        agent_name="critic",
        provider="openai",
        model="gpt-4o",
        input_tokens=100,
        output_tokens=50,
        latency_ms=1234,
        success=True,
    )
    assert ok is True
    lines = p.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    rec = json.loads(lines[0])
    assert rec["agent_name"] == "critic"
    assert rec["model"] == "gpt-4o"
    assert rec["input_tokens"] == 100
    assert rec["output_tokens"] == 50
    assert rec["total_tokens"] == 150
    assert rec["success"] is True
    assert rec["latency_ms"] == 1234
    assert rec["ts"]  # timestamp 존재
    assert rec["cost_usd"] == pytest.approx((100 * 2.5 + 50 * 10) / 1_000_000, rel=1e-6)


def test_graceful_never_raises(monkeypatch) -> None:
    # null byte 경로 → open/makedirs 실패해도 raise 하지 않고 False
    _patch(monkeypatch, True, "\x00bad/path/x.jsonl")
    assert aio.log_agent_io(agent_name="x", model="m") is False


def test_estimate_cost_known_and_unknown() -> None:
    assert aio.estimate_cost_usd("gpt-4o-mini", 1_000_000, 0) == pytest.approx(0.15)
    assert aio.estimate_cost_usd("gemini-3.5-flash", 0, 1_000_000) == pytest.approx(9.0)
    assert aio.estimate_cost_usd("unknown-model", 100, 100) is None


def test_gateway_complete_emits_record(tmp_path, monkeypatch) -> None:
    p = tmp_path / "agent_io.jsonl"
    _patch(monkeypatch, True, p)
    resp = LLMResponse(
        text="{}",
        model_id="gpt-4o-mini",
        alias="planning",
        usage=LLMUsage(prompt_tokens=12, completion_tokens=8),
    )
    adapter = MagicMock()
    adapter.complete.return_value = resp
    out = LLMGateway().complete(
        "planning", [{"role": "user", "content": "hi"}], adapter=adapter
    )
    assert out.text == "{}"
    rec = json.loads(p.read_text(encoding="utf-8").strip())
    assert rec["agent_name"] == "planning"
    assert rec["provider"] == "openai"
    assert rec["model"] == "gpt-4o-mini"
    assert rec["input_tokens"] == 12
    assert rec["output_tokens"] == 8
    assert rec["latency_ms"] is not None and rec["latency_ms"] >= 0
    assert rec["success"] is True


# ─── HIP-006 S3 — usage_tokens / DB 적재 / 기본 경로(critic) 계측 ──────

def test_usage_tokens_defensive() -> None:
    class _U:
        prompt_tokens = 12
        completion_tokens = 8

    assert aio.usage_tokens(_U()) == (12, 8)
    assert aio.usage_tokens(None) == (0, 0)
    assert aio.usage_tokens(MagicMock()) == (0, 0)  # MagicMock attrs → 0 (방어적)


def test_db_write_when_to_db_enabled(tmp_path, monkeypatch) -> None:
    s = Settings(
        agent_io_log_enabled=True,
        agent_io_log_to_db=True,
        agent_io_log_path=str(tmp_path / "a.jsonl"),
    )
    monkeypatch.setattr(aio, "get_settings", lambda: s)
    mock_client = MagicMock()
    monkeypatch.setattr("backend.fastapi.db.get_supabase", lambda: mock_client)
    ok = aio.log_agent_io(
        agent_name="critic", prompt_id="P-007", prompt_version="v1.1.0",
        model="gpt-4o", input_tokens=10, output_tokens=5,
    )
    assert ok is True
    mock_client.table.assert_called_with("agent_io_logs")
    assert mock_client.table.return_value.insert.called


def test_db_write_skipped_when_to_db_off(tmp_path, monkeypatch) -> None:
    s = Settings(
        agent_io_log_enabled=True,
        agent_io_log_to_db=False,
        agent_io_log_path=str(tmp_path / "a.jsonl"),
    )
    monkeypatch.setattr(aio, "get_settings", lambda: s)
    mock_client = MagicMock()
    monkeypatch.setattr("backend.fastapi.db.get_supabase", lambda: mock_client)
    aio.log_agent_io(agent_name="x", model="m")
    assert not mock_client.table.called  # to_db OFF → DB 미접근 (JSONL 만)


def test_run_critic_emits_telemetry(tmp_path, monkeypatch) -> None:
    """HIP-006 S3: 기본 경로(critic, gateway 미경유)도 텔레메트리 기록."""
    from backend.fastapi.agents import critic as critic_mod
    from backend.fastapi.agents.critic import DIMENSIONS, run_critic

    s = Settings(agent_io_log_enabled=True, agent_io_log_path=str(tmp_path / "c.jsonl"))
    monkeypatch.setattr(aio, "get_settings", lambda: s)  # 발신기 활성
    monkeypatch.setattr(critic_mod, "get_settings", lambda: Settings())  # critic 기본(calibration off)
    payload = json.dumps(
        {
            "scores": {k: 4 for k in DIMENSIONS},
            "reasons": {},
            "suggestions": {},
            "overall_verdict": "approve",
            "blocking_issues": [],
        },
        ensure_ascii=False,
    )
    client = MagicMock()
    msg = MagicMock()
    msg.content = payload
    choice = MagicMock()
    choice.message = msg
    resp = MagicMock()
    resp.choices = [choice]
    client.chat.completions.create.return_value = resp

    run_critic({"plan_id": "p"}, client=client)
    rec = json.loads((tmp_path / "c.jsonl").read_text(encoding="utf-8").strip())
    assert rec["agent_name"] == "critic"
    assert rec["prompt_id"] == "P-007"
