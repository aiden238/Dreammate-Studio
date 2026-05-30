"""Phase 8 Slice 3 — SSE progress_store 브릿지 통합 (ADR-028).

검증 범위:
  1. progress_store record/read/clear roundtrip + maxlen cap.
  2. StoreProgressSink.emit → progress_store 기록 / NullProgressSink 무기록.
  3. sse.py 가 store populated 시 실 stage stream / store empty 시 mock fallback.

기존 test_sse.py(4 케이스) 는 수정 0 — graceful fallback 이 mock 동작 보존.
"""
from __future__ import annotations

import json

import pytest
from fastapi.testclient import TestClient

from backend.fastapi.main import app
from backend.fastapi.orchestration import progress_store
from backend.fastapi.orchestration.progress_sink import NullProgressSink, StoreProgressSink


@pytest.fixture(autouse=True)
def _reset_store():
    progress_store._reset_for_test()
    yield
    progress_store._reset_for_test()


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


# ─── 1. progress_store record/read/clear/maxlen ───────────────────────


def test_progress_store_record_read_roundtrip() -> None:
    progress_store.record("p1", {"type": "progress", "stage": "intent", "step": 1})
    progress_store.record("p1", {"type": "complete", "stage": "complete", "step": 4})
    evs = progress_store.read("p1")
    assert len(evs) == 2 and evs[-1]["type"] == "complete"


def test_progress_store_maxlen_cap() -> None:
    for i in range(100):
        progress_store.record("p1", {"type": "progress", "step": i})
    assert len(progress_store.read("p1")) <= 64


def test_progress_store_clear() -> None:
    progress_store.record("p1", {"type": "progress"})
    progress_store.clear("p1")
    assert progress_store.read("p1") == []


# ─── 2. ProgressSink 연동 ─────────────────────────────────────────────


def test_store_progress_sink_emits_to_store() -> None:
    sink = StoreProgressSink("p2")
    sink.emit("intent", step=1, message="의도 분석 중...")
    sink.emit("complete", step=4, message="완료")
    evs = progress_store.read("p2")
    assert evs[0]["stage"] == "intent" and evs[-1]["type"] == "complete"


def test_null_sink_records_nothing() -> None:
    sink = NullProgressSink()
    sink.emit("intent", step=1)
    # NullSink 는 store 미기록
    assert progress_store.read("anything") == []


# ─── 3. sse.py 브릿지 ─────────────────────────────────────────────────


def test_sse_reads_store_when_populated(client: TestClient) -> None:
    # store 에 실 stage 미리 기록 → SSE 가 그대로 stream
    for st, step in [("intent", 1), ("rag", 2), ("planning", 3), ("critic", 4)]:
        progress_store.record("p3", {"type": "progress", "stage": st, "step": step, "plan_id": "p3"})
    progress_store.record("p3", {"type": "complete", "stage": "complete", "step": 4, "plan_id": "p3"})
    resp = client.get("/api/v1/plans/p3/progress")
    assert resp.status_code == 200
    events = [json.loads(l[5:]) for l in resp.text.split("\n\n") if l.startswith("data:")]
    stages = [e.get("stage") for e in events if e.get("type") == "progress"]
    assert stages == ["intent", "rag", "planning", "critic"]
    assert events[-1]["type"] == "complete"


def test_sse_graceful_fallback_when_store_empty(client: TestClient) -> None:
    # store 비어있음 → 기존 mock 4단계 fallback (test_sse 보존 동작과 동일)
    resp = client.get("/api/v1/plans/empty-plan/progress")
    assert resp.status_code == 200
    events = [json.loads(l[5:]) for l in resp.text.split("\n\n") if l.startswith("data:")]
    progress_events = [e for e in events if e.get("type") == "progress"]
    assert len(progress_events) == 4  # mock 4단계
    assert events[-1]["type"] == "complete"
