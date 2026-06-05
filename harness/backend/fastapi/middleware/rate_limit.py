"""Phase 27 S3 — 최소 rate limiter (B-7).

gated default-off. ON 시 핵심 비용 endpoint(generation)를 신원(user-우선, 없으면 IP) 기준
fixed-window 로 제한 → free tier 비용 무제한·brute force 방어.

★ 최소 구현 한계(U-2): in-memory fixed-window(단일 프로세스). 멀티-프로세스/분산은
  rate_limit_policy.md §4(Redis sliding window) 운영 단계 후속.
★ behavior-preserving: enforce_rate_limit 는 rate_limit_enabled=False(default) 면 즉시 no-op
  → 기존 응답 byte-identical. 두 generation endpoint 가 동일 identity 카운터 공유(우회 방지).
★ 정책 정합: rate_limit_policy.md §3.2 free generate 행(2/분 burst, 5/일 cost cap).
"""

from __future__ import annotations

import time

from fastapi import Request
from fastapi.responses import JSONResponse

# (window_name, seconds, limit) — 정책 §3.2 free generation.
_WINDOWS: tuple[tuple[str, int, int], ...] = (
    ("minute", 60, 2),       # burst 방어
    ("day", 86_400, 5),      # 일일 cost cap (free 의 binding 한도)
)

# {(identity, window_name): (window_start_epoch, count)} — 프로세스 로컬.
_COUNTERS: dict[tuple[str, str], tuple[int, int]] = {}


class RateLimitExceeded(Exception):
    """rate limit 초과 — main.py 핸들러가 429 ErrorEnvelope 로 변환."""

    def __init__(self, window: str, limit: int, retry_after: int) -> None:
        self.window = window
        self.limit = limit
        self.retry_after = max(1, retry_after)
        super().__init__(f"rate limit exceeded ({window}: {limit})")


def _identity(request: Request) -> str:
    """신원 키: 인증 user_id 우선(request.state.user dict), 없으면 client IP."""
    user = getattr(request.state, "user", None)
    if isinstance(user, dict):
        uid = user.get("user_id")
        if uid:
            return f"user:{uid}"
    client = request.client
    return f"ip:{client.host if client else 'unknown'}"


def _check_and_consume(identity: str, now: int) -> None:
    """모든 window 통과 시 카운트 +1. 하나라도 초과면 RateLimitExceeded(차단 요청은 미소비)."""
    # 1) 전 window 초과 검사 (차단되는 요청은 카운트하지 않는다).
    for name, seconds, limit in _WINDOWS:
        start, count = _COUNTERS.get((identity, name), (0, 0))
        cur_start = now - (now % seconds)
        if start != cur_start:
            count = 0
        if count >= limit:
            raise RateLimitExceeded(name, limit, (cur_start + seconds) - now)
    # 2) 전부 통과 → 전 window 증가.
    for name, seconds, _limit in _WINDOWS:
        start, count = _COUNTERS.get((identity, name), (0, 0))
        cur_start = now - (now % seconds)
        if start != cur_start:
            count = 0
        _COUNTERS[(identity, name)] = (cur_start, count + 1)


async def enforce_rate_limit(request: Request) -> None:
    """FastAPI 의존성 — 비용 endpoint(generation)에 부착. gated default-off.

    OFF(rate_limit_enabled=False, default) → 즉시 return (no-op, byte-identical).
    ON → 신원 기준 fixed-window 검사, 초과 시 RateLimitExceeded(→429).
    """
    from ..config import get_settings  # 지연 import (config 의존만, 순환 회피)

    settings = get_settings()
    if not getattr(settings, "rate_limit_enabled", False):
        return
    _check_and_consume(_identity(request), int(time.time()))


def rate_limit_error_response(exc: RateLimitExceeded) -> JSONResponse:
    """RateLimitExceeded → 429 ErrorEnvelope + X-RateLimit-*/Retry-After 헤더."""
    from ..schemas.output import ErrorBody, ErrorEnvelope, ErrorMeta  # 지연 import

    env = ErrorEnvelope(
        error=ErrorBody(
            code="E-RL-001",
            message=str(exc),
            user_message="요청이 너무 많아요. 잠시 후 다시 시도해 주세요.",
            retry_allowed=True,
        ),
        meta=ErrorMeta.make(),
    )
    headers = {
        "Retry-After": str(exc.retry_after),
        "X-RateLimit-Limit": str(exc.limit),
        "X-RateLimit-Remaining": "0",
        "X-RateLimit-Reset": str(int(time.time()) + exc.retry_after),
    }
    return JSONResponse(status_code=429, content=env.model_dump(), headers=headers)


def reset_counters() -> None:
    """테스트 전용 — 카운터 초기화."""
    _COUNTERS.clear()
