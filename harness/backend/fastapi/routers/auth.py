"""Phase 5 Slice 3 — Auth endpoints (login / me / logout).

Supabase Auth 통합:
- POST /api/v1/auth/login: email + password -> session (JWT 는 httpOnly cookie 로 저장)
- GET  /api/v1/auth/me:    현재 user (cookie 또는 Bearer)
- POST /api/v1/auth/logout: cookie clear + Supabase signOut

graceful: Supabase 미설정 시 503 (또는 dev_auth_mock=True 일 때만 mock user 허용).

security-review §T1 권장:
- JWT 는 httpOnly + Secure + SameSite=Strict cookie 로만 저장
- sessionStorage / localStorage 미사용 (frontend 에서 직접 접근 불가)
- refresh token 별도 cookie, 30 일
"""

from __future__ import annotations

import logging
from typing import Any, Optional

import re

from fastapi import APIRouter, HTTPException, Request, Response
from pydantic import BaseModel, Field, field_validator

from backend.fastapi.config import get_settings
from backend.fastapi.db.client import get_supabase

# Phase 5 Slice 3: EmailStr 의존 (email-validator) 미사용.
# 외부 패키지 추가 회피 + Slice 2/4 회귀 0 위해 자체 정규식.
# RFC 5322 단순화 — 실제 검증은 Supabase Auth 가 다시 수행.
_EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$")

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


# ─── Schemas ───────────────────────────────────────────────────────────


class LoginRequest(BaseModel):
    """POST /api/v1/auth/login 요청 페이로드.

    email: 단순 정규식 검증 (RFC 5322 단순화). EmailStr 는 email-validator
    런타임 의존성 추가가 필요해 회피. Supabase Auth 가 다시 검증한다.
    """

    email: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=1, max_length=256)

    @field_validator("email")
    @classmethod
    def _validate_email(cls, v: str) -> str:
        if not _EMAIL_RE.match(v):
            raise ValueError("invalid_email")
        return v


class AuthSession(BaseModel):
    """공통 세션 응답.

    access_token / refresh_token 은 응답 body 에 절대 노출 안 함
    (security-review §T1: httpOnly cookie 만 사용).
    """

    user_id: str
    email: str


class LogoutResponse(BaseModel):
    status: str = "logged_out"


# ─── Cookie helpers ────────────────────────────────────────────────────


_ACCESS_COOKIE = "sb_access_token"
_REFRESH_COOKIE = "sb_refresh_token"
_ACCESS_MAX_AGE = 3600  # 1 hour (Supabase 기본)
_REFRESH_MAX_AGE = 30 * 24 * 3600  # 30 days


def _set_session_cookies(
    response: Response,
    access_token: str,
    refresh_token: Optional[str] = None,
    *,
    secure: bool = True,
) -> None:
    """security-review §T1: httpOnly + Secure + SameSite=Strict."""
    response.set_cookie(
        key=_ACCESS_COOKIE,
        value=access_token,
        httponly=True,
        secure=secure,
        samesite="strict",
        max_age=_ACCESS_MAX_AGE,
        path="/",
    )
    if refresh_token:
        response.set_cookie(
            key=_REFRESH_COOKIE,
            value=refresh_token,
            httponly=True,
            secure=secure,
            samesite="strict",
            max_age=_REFRESH_MAX_AGE,
            path="/",
        )


def _clear_session_cookies(response: Response) -> None:
    response.delete_cookie(_ACCESS_COOKIE, path="/")
    response.delete_cookie(_REFRESH_COOKIE, path="/")


# ─── Endpoints ─────────────────────────────────────────────────────────


@router.post("/login", response_model=AuthSession)
async def login(payload: LoginRequest, response: Response) -> AuthSession:
    """이메일 + 비밀번호로 로그인. 성공 시 httpOnly cookie 발급."""
    settings = get_settings()
    client = get_supabase()

    # graceful: Supabase 미설정 + dev_auth_mock 활성 -> mock user
    if client is None:
        if getattr(settings, "dev_auth_mock", False):
            mock_session = AuthSession(
                user_id="mock-user-1",
                email=str(payload.email),
            )
            # dev mode: secure=False 허용 (HTTP 로컬 환경)
            _set_session_cookies(
                response,
                access_token="mock-token",
                refresh_token=None,
                secure=False,
            )
            return mock_session
        raise HTTPException(status_code=503, detail="auth_unavailable")

    try:
        result = client.auth.sign_in_with_password(
            {"email": str(payload.email), "password": payload.password},
        )
    except Exception as exc:
        logger.warning("login_failed: %s", exc.__class__.__name__)
        raise HTTPException(status_code=401, detail="invalid_credentials")

    user = getattr(result, "user", None)
    session = getattr(result, "session", None)
    if user is None or session is None:
        raise HTTPException(status_code=401, detail="invalid_credentials")

    access_token = getattr(session, "access_token", None)
    refresh_token = getattr(session, "refresh_token", None)
    if not access_token:
        raise HTTPException(status_code=401, detail="invalid_credentials")

    # ★ Phase 27 fix: secure 쿠키는 HTTPS 에서만 저장된다. 로컬 개발(HTTP localhost)에서는
    #   secure=True 면 브라우저가 쿠키를 버려 로그인이 사실상 실패 → app_env=development 면 False.
    _set_session_cookies(
        response,
        access_token=access_token,
        refresh_token=refresh_token,
        secure=(settings.app_env != "development"),
    )
    return AuthSession(
        user_id=str(getattr(user, "id", "")),
        email=str(getattr(user, "email", "") or ""),
    )


@router.post("/signup", response_model=AuthSession)
async def signup(payload: LoginRequest, response: Response) -> AuthSession:
    """이메일 + 비밀번호로 회원가입 후 자동 로그인 (httpOnly cookie 발급).

    ★ MVP: admin create_user(email_confirm=True)로 즉시 가입(이메일 인증 단계 생략) → 자동 로그인.
      production 은 실 이메일 인증 흐름 권장(보안). 본 엔드포인트는 1차 MVP 실사용/로컬 테스트용.
    """
    settings = get_settings()
    client = get_supabase()
    if client is None:
        if getattr(settings, "dev_auth_mock", False):
            _set_session_cookies(
                response, access_token="mock-token", refresh_token=None, secure=False
            )
            return AuthSession(user_id="mock-user-1", email=str(payload.email))
        raise HTTPException(status_code=503, detail="auth_unavailable")

    # 1) 계정 생성 (auto-confirm). 이미 있으면 409.
    try:
        client.auth.admin.create_user(
            {
                "email": str(payload.email),
                "password": payload.password,
                "email_confirm": True,
            }
        )
    except Exception as exc:  # noqa: BLE001
        msg = str(exc).lower()
        if any(t in msg for t in ("already", "registered", "exist")):
            raise HTTPException(status_code=409, detail="email_already_registered")
        logger.warning("signup_failed: %s", exc.__class__.__name__)
        raise HTTPException(status_code=400, detail="signup_failed")

    # 2) 자동 로그인 (세션 토큰 발급).
    try:
        result = client.auth.sign_in_with_password(
            {"email": str(payload.email), "password": payload.password}
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("signup_login_failed: %s", exc.__class__.__name__)
        raise HTTPException(status_code=401, detail="signup_login_failed")

    user = getattr(result, "user", None)
    session = getattr(result, "session", None)
    access_token = getattr(session, "access_token", None) if session else None
    if user is None or not access_token:
        raise HTTPException(status_code=401, detail="signup_login_failed")

    _set_session_cookies(
        response,
        access_token=access_token,
        refresh_token=getattr(session, "refresh_token", None),
        secure=(settings.app_env != "development"),
    )
    return AuthSession(
        user_id=str(getattr(user, "id", "")),
        email=str(getattr(user, "email", "") or ""),
    )


@router.get("/me", response_model=AuthSession)
async def get_me(request: Request) -> AuthSession:
    """현재 인증된 user 반환. auth_middleware 가 request.state.user 주입."""
    user: Optional[dict[str, Any]] = getattr(request.state, "user", None)
    if user is None:
        raise HTTPException(status_code=401, detail="unauthenticated")
    return AuthSession(
        user_id=str(user.get("user_id", "")),
        email=str(user.get("email", "") or ""),
    )


@router.post("/logout", response_model=LogoutResponse)
async def logout(response: Response) -> LogoutResponse:
    """cookie clear + (가능 시) Supabase signOut."""
    client = get_supabase()
    if client is not None:
        try:
            client.auth.sign_out()
        except Exception as exc:  # noqa: BLE001
            # graceful: signOut 실패해도 cookie 는 clear
            logger.info("supabase_signout_skipped: %s", exc.__class__.__name__)
    _clear_session_cookies(response)
    return LogoutResponse(status="logged_out")


__all__ = ["router", "LoginRequest", "AuthSession", "LogoutResponse"]
