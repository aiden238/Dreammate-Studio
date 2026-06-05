"""Phase 27 S3 — 최소 rate limiter (B-7) 검증.

보장:
  1. OFF (default) → 비용 endpoint 무제한 통과 (byte-identical, no-op).
  2. ON → 신원별 fixed-window 초과 시 429 + E-RL-001 + Retry-After/X-RateLimit-* 헤더.
  3. minute/day 두 window 동작 + 신원(user/IP) 분리 + 차단 요청 미소비.
"""

from types import SimpleNamespace

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from backend.fastapi.config import get_settings
from backend.fastapi.middleware.rate_limit import (
    RateLimitExceeded,
    _check_and_consume,
    _identity,
    enforce_rate_limit,
    rate_limit_error_response,
    reset_counters,
)


@pytest.fixture(autouse=True)
def _clean(monkeypatch):
    """각 테스트 전후 카운터 + settings 캐시 초기화."""
    monkeypatch.delenv("RATE_LIMIT_ENABLED", raising=False)
    reset_counters()
    get_settings.cache_clear()
    yield
    reset_counters()
    get_settings.cache_clear()


def _make_app() -> FastAPI:
    app = FastAPI()
    app.add_exception_handler(
        RateLimitExceeded, lambda request, exc: rate_limit_error_response(exc)
    )

    @app.post("/cost", dependencies=[Depends(enforce_rate_limit)])
    async def _cost() -> dict:
        return {"ok": True}

    return app


# ── 통합: OFF = no-op ──────────────────────────────────────────────────
def test_off_is_noop():
    """rate_limit_enabled 미설정(default False) → 많은 요청 전부 200."""
    client = TestClient(_make_app())
    for _ in range(10):
        assert client.post("/cost").status_code == 200


# ── 통합: ON = minute 한도 초과 시 429 ──────────────────────────────────
def test_on_blocks_after_minute_limit(monkeypatch):
    monkeypatch.setenv("RATE_LIMIT_ENABLED", "true")
    get_settings.cache_clear()
    client = TestClient(_make_app())

    assert client.post("/cost").status_code == 200  # 1
    assert client.post("/cost").status_code == 200  # 2
    blocked = client.post("/cost")  # 3 → minute(2) 초과
    assert blocked.status_code == 429
    body = blocked.json()
    assert body["ok"] is False
    assert body["error"]["code"] == "E-RL-001"
    assert body["error"]["retry_allowed"] is True
    assert "Retry-After" in blocked.headers
    assert blocked.headers["X-RateLimit-Limit"] == "2"
    assert blocked.headers["X-RateLimit-Remaining"] == "0"


# ── 단위: 신원 키 (user 우선 / IP fallback) ─────────────────────────────
def test_identity_user_vs_ip():
    user_req = SimpleNamespace(
        state=SimpleNamespace(user={"user_id": "u-123"}),
        client=SimpleNamespace(host="1.2.3.4"),
    )
    anon_req = SimpleNamespace(
        state=SimpleNamespace(user=None),
        client=SimpleNamespace(host="1.2.3.4"),
    )
    assert _identity(user_req) == "user:u-123"
    assert _identity(anon_req) == "ip:1.2.3.4"


# ── 단위: minute + day 두 window 동작 (결정적 now) ──────────────────────
def test_check_and_consume_minute_and_day():
    reset_counters()
    now = 1_000_000  # 고정

    _check_and_consume("id1", now)  # minute=1 day=1
    _check_and_consume("id1", now)  # minute=2 day=2
    with pytest.raises(RateLimitExceeded) as ei:
        _check_and_consume("id1", now)  # minute(2) 초과 → 차단(미소비)
    assert ei.value.window == "minute"

    _check_and_consume("id1", now + 61)  # 새 minute: day=3
    _check_and_consume("id1", now + 61)  # day=4
    _check_and_consume("id1", now + 122)  # 또 새 minute: day=5
    with pytest.raises(RateLimitExceeded) as ei2:
        _check_and_consume("id1", now + 183)  # minute OK but day(5) 초과
    assert ei2.value.window == "day"


# ── 단위: 신원 분리 (서로 다른 identity 는 카운터 독립) ─────────────────
def test_separate_identities_independent():
    reset_counters()
    now = 2_000_000
    _check_and_consume("a", now)
    _check_and_consume("a", now)
    # a 는 minute 초과 상태이나 b 는 영향 없음.
    _check_and_consume("b", now)
    _check_and_consume("b", now)
    with pytest.raises(RateLimitExceeded):
        _check_and_consume("b", now)
