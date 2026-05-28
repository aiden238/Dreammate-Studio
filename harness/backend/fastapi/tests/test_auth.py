"""Phase 5 Slice 3 — Auth endpoints + JWT middleware tests.

검증 범위:
- /api/v1/auth/login: mock mode (Supabase None + dev_auth_mock=True)
- /api/v1/auth/login: no supabase + no mock -> 503
- /api/v1/auth/login: 422 (Pydantic 이메일 검증)
- /api/v1/auth/me: 인증 없으면 401
- /api/v1/auth/me: mock cookie 있으면 200
- /api/v1/auth/me: Authorization Bearer fallback
- /api/v1/auth/logout: cookie clear

security-review §T1 검증:
- 응답 cookie 에 httponly + samesite=strict 속성 확인.
"""

from __future__ import annotations

from typing import Any

import pytest
from fastapi.testclient import TestClient

from backend.fastapi import config as _config_module
from backend.fastapi.db import client as _db_client_module
from backend.fastapi.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def _set_dev_auth_mock(monkeypatch: pytest.MonkeyPatch, enabled: bool) -> None:
    """settings.dev_auth_mock 을 토글하고 lru_cache 무효화."""
    _config_module.get_settings.cache_clear()
    settings = _config_module.get_settings()
    monkeypatch.setattr(settings, "dev_auth_mock", enabled, raising=False)


def _force_no_supabase(monkeypatch: pytest.MonkeyPatch) -> None:
    """get_supabase() -> None 강제."""
    monkeypatch.setattr(_db_client_module, "get_supabase", lambda: None)
    # routers/auth + middleware/auth_middleware 가 import 한 별칭도 차단
    monkeypatch.setattr(
        "backend.fastapi.routers.auth.get_supabase", lambda: None,
    )


# ─── /auth/login ────────────────────────────────────────────────────────


def test_login_mock_mode_returns_session(
    client: TestClient, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """dev_auth_mock=True + Supabase None -> mock session + httpOnly cookie."""
    _set_dev_auth_mock(monkeypatch, True)
    _force_no_supabase(monkeypatch)

    resp = client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "pwd"},
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["user_id"] == "mock-user-1"
    assert data["email"] == "test@example.com"
    # security-review §T1: access_token 응답 body 미노출
    assert "access_token" not in data
    # httpOnly cookie 발급 확인
    assert "sb_access_token" in resp.cookies
    # Set-Cookie header attribute 확인 (httponly + samesite=strict)
    set_cookie_headers = resp.headers.get_list("set-cookie") if hasattr(
        resp.headers, "get_list",
    ) else [resp.headers.get("set-cookie", "")]
    joined = " ".join(set_cookie_headers).lower()
    assert "httponly" in joined
    assert "samesite=strict" in joined


def test_login_no_supabase_no_mock_returns_503(
    client: TestClient, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """dev_auth_mock=False + Supabase None -> 503 auth_unavailable."""
    _set_dev_auth_mock(monkeypatch, False)
    _force_no_supabase(monkeypatch)

    resp = client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "pwd"},
    )
    assert resp.status_code == 503
    assert resp.json()["detail"] == "auth_unavailable"


def test_login_invalid_email_returns_422(client: TestClient) -> None:
    """Pydantic EmailStr 검증."""
    resp = client.post(
        "/api/v1/auth/login",
        json={"email": "not_an_email", "password": "pwd"},
    )
    assert resp.status_code == 422


# ─── /auth/me ───────────────────────────────────────────────────────────


def test_me_unauthenticated_returns_401(
    client: TestClient, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """토큰 없음 -> 401 unauthenticated."""
    _set_dev_auth_mock(monkeypatch, True)
    _force_no_supabase(monkeypatch)

    resp = client.get("/api/v1/auth/me")
    assert resp.status_code == 401
    assert resp.json()["detail"] == "unauthenticated"


def test_me_with_mock_cookie_returns_user(
    client: TestClient, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """dev_auth_mock + mock-token cookie -> 200 mock user."""
    _set_dev_auth_mock(monkeypatch, True)
    _force_no_supabase(monkeypatch)

    resp = client.get(
        "/api/v1/auth/me",
        cookies={"sb_access_token": "mock-token"},
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["user_id"] == "mock-user-1"
    assert data["email"] == "mock@example.com"


def test_me_with_bearer_fallback_returns_user(
    client: TestClient, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Authorization Bearer fallback (cookie 없을 때)."""
    _set_dev_auth_mock(monkeypatch, True)
    _force_no_supabase(monkeypatch)

    resp = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer mock-token"},
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["user_id"] == "mock-user-1"


def test_me_invalid_token_returns_401(
    client: TestClient, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """알 수 없는 토큰 + Supabase None -> 401 (middleware 가 user=None 주입)."""
    _set_dev_auth_mock(monkeypatch, True)
    _force_no_supabase(monkeypatch)

    resp = client.get(
        "/api/v1/auth/me",
        cookies={"sb_access_token": "garbage-token"},
    )
    assert resp.status_code == 401


# ─── /auth/logout ───────────────────────────────────────────────────────


def test_logout_clears_cookie(
    client: TestClient, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """logout -> 200 + cookie delete."""
    _force_no_supabase(monkeypatch)

    resp = client.post("/api/v1/auth/logout")
    assert resp.status_code == 200
    assert resp.json()["status"] == "logged_out"
    # delete_cookie 는 max-age=0 또는 expires past 로 Set-Cookie 발급
    set_cookie = " ".join(
        resp.headers.get_list("set-cookie")
        if hasattr(resp.headers, "get_list")
        else [resp.headers.get("set-cookie", "")],
    ).lower()
    assert "sb_access_token" in set_cookie


# ─── Real Supabase client mock (sign_in_with_password) ─────────────────


class _FakeUser:
    id = "real-user-uuid-1"
    email = "real@example.com"


class _FakeSession:
    access_token = "real-access-token"
    refresh_token = "real-refresh-token"


class _FakeAuthResult:
    user = _FakeUser()
    session = _FakeSession()


class _FakeAuth:
    def sign_in_with_password(self, _payload: dict[str, Any]) -> _FakeAuthResult:
        return _FakeAuthResult()

    def sign_out(self) -> None:
        return None

    def get_user(self, token: str) -> Any:
        class _Resp:
            user = _FakeUser()

        return _Resp() if token == "real-access-token" else None


class _FakeSupabase:
    def __init__(self) -> None:
        self.auth = _FakeAuth()

    def table(self, _name: str) -> Any:
        return None


def test_login_real_supabase_path_sets_cookies(
    client: TestClient, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Supabase client 존재 시 sign_in_with_password 경로 검증."""
    fake = _FakeSupabase()
    monkeypatch.setattr(
        "backend.fastapi.routers.auth.get_supabase", lambda: fake,
    )

    resp = client.post(
        "/api/v1/auth/login",
        json={"email": "real@example.com", "password": "pwd"},
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["user_id"] == "real-user-uuid-1"
    assert data["email"] == "real@example.com"
    # security-review §T1: access_token 응답 body 미노출
    assert "access_token" not in data
    # access + refresh 두 cookie 모두 발급
    set_cookie = " ".join(
        resp.headers.get_list("set-cookie")
        if hasattr(resp.headers, "get_list")
        else [resp.headers.get("set-cookie", "")],
    ).lower()
    assert "sb_access_token=real-access-token" in set_cookie
    assert "sb_refresh_token=real-refresh-token" in set_cookie
