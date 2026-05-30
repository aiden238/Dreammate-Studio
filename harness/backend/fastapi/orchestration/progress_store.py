"""Phase 8 — in-memory progress store (ADR-028).

SSE Progress 브릿지. orchestrator(StoreProgressSink)가 record, sse.py가 read.
graceful + maxlen(메모리 누수 방지, U6). 동기 single-process (별도 worker 없음, ADR-028).
"""
from __future__ import annotations

from collections import OrderedDict
from typing import Any

_MAX_PLANS = 256       # LRU 상한 (메모리 누수 방지)
_MAX_EVENTS = 64       # plan 당 이벤트 상한

_store: "OrderedDict[str, list[dict[str, Any]]]" = OrderedDict()


def record(plan_id: str, event: dict[str, Any]) -> None:
    """plan_id 의 progress 이벤트 append (graceful, maxlen cap)."""
    if not plan_id:
        return
    events = _store.get(plan_id)
    if events is None:
        events = []
        _store[plan_id] = events
        _store.move_to_end(plan_id)
        while len(_store) > _MAX_PLANS:
            _store.popitem(last=False)  # 가장 오래된 plan 제거
    events.append(event)
    if len(events) > _MAX_EVENTS:
        del events[: len(events) - _MAX_EVENTS]


def read(plan_id: str) -> list[dict[str, Any]]:
    """plan_id 의 progress 이벤트 스냅샷 (graceful — 없으면 빈 list)."""
    if not plan_id:
        return []
    return list(_store.get(plan_id, []))


def clear(plan_id: str) -> None:
    """plan_id 이벤트 제거 (complete 후 cleanup)."""
    _store.pop(plan_id, None)


def _reset_for_test() -> None:
    """테스트 격리용."""
    _store.clear()
