"""Phase 5 Slice 3 — JWT 검증 middleware.

security-review §T1 정합:
- httpOnly cookie 우선 (sb_access_token)
- Authorization Bearer fallback (Phase 5+ API client 호환용)

정책:
- 모든 경로에 대해 토큰 존재 시 검증을 시도하고 request.state.user 에 주입한다.
- 토큰 없거나 검증 실패 시 request.state.user = None (pass-through).
- 인증 강제는 endpoint level 에서 (예: /auth/me 는 user None 이면 401).
- anonymous endpoint (/api/v1/generate, /api/v1/plans/start, /api/v1/auth/login) 는
  자연스럽게 pass-through (검사 없음).
"""

from __future__ import annotations

import logging
from typing import Any, Awaitable, Callable, Optional

from fastapi import Request

logger = logging.getLogger(__name__)


async def auth_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Any]],
) -> Any:
    """JWT 검증 + request.state.user 주입.

    토큰 추출 우선순위:
      1) httpOnly cookie `sb_access_token` (security-review §T1 권장)
      2) Authorization: Bearer <token> (fallback)

    검증 실패는 graceful — request.state.user 만 None 으로 유지.
    """
    token = _extract_token(request)
    user: Optional[dict[str, Any]] = None
    if token:
        user = _verify_jwt(token)
    # state 는 항상 한 번 set (downstream get 안전)
    request.state.user = user

    response = await call_next(request)
    return response


# ─── helpers ───────────────────────────────────────────────────────────


def _extract_token(request: Request) -> Optional[str]:
    """cookie 우선, Authorization Bearer fallback."""
    cookie_token = request.cookies.get("sb_access_token")
    if cookie_token:
        return cookie_token
    auth_header = request.headers.get("authorization", "")
    if auth_header.lower().startswith("bearer "):
        return auth_header[7:].strip() or None
    return None


def _verify_jwt(token: str) -> Optional[dict[str, Any]]:
    """Supabase JWT 검증. graceful — 실패 시 None.

    - dev_auth_mock 활성 + token == "mock-token" 인 경우 mock user 반환.
    - 실 Supabase client 존재 시 client.auth.get_user(token) 호출.
    - client 없음 / 호출 실패 -> None.
    """
    # 지연 import — config 변화에 따라 매 호출 settings 조회
    from backend.fastapi.config import get_settings
    from backend.fastapi.db.client import get_supabase

    settings = get_settings()
    if getattr(settings, "dev_auth_mock", False) and token == "mock-token":
        return {"user_id": "mock-user-1", "email": "mock@example.com"}

    client = get_supabase()
    if client is None:
        return None

    try:
        user_resp = client.auth.get_user(token)
    except Exception as exc:  # noqa: BLE001
        logger.warning("jwt_verify_failed: %s", exc.__class__.__name__)
        return None

    user_obj = getattr(user_resp, "user", None)
    if user_obj is None:
        return None
    return {
        "user_id": str(getattr(user_obj, "id", "")),
        "email": str(getattr(user_obj, "email", "") or ""),
    }


__all__ = ["auth_middleware"]
