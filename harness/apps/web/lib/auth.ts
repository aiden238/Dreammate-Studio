/**
 * Phase 5 Slice 3 — Supabase Auth helpers (cookie-based).
 *
 * security-review §T1 정합:
 *   - JWT 는 backend httpOnly cookie 로만 관리 (sb_access_token / sb_refresh_token).
 *   - 본 모듈은 토큰을 직접 read/set 하지 않는다. fetch 인터페이스만 제공.
 *   - `credentials: "include"` 로 cookie 자동 전송.
 *
 * 참조:
 *   - harness/backend/fastapi/routers/auth.py (login / me / logout)
 *   - harness/meta/security_reviews/2026-05-29_phase-5-auth-rls.md §T1
 */

import { API_BASE_URL } from "./api";
import type { AuthSession } from "./types";

export type { AuthSession };

/**
 * POST /api/v1/auth/login
 * 성공 시 backend 가 httpOnly cookie 발급. 응답 body 에는 토큰 없음.
 *
 * 실패 시 throw — login page 에서 사용자 메시지로 변환.
 */
export async function login(
  email: string,
  password: string,
): Promise<AuthSession> {
  const url = `${API_BASE_URL}/api/v1/auth/login`;
  const resp = await fetch(url, {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
    },
    body: JSON.stringify({ email, password }),
  });
  if (!resp.ok) {
    throw new Error(`login_failed: HTTP ${resp.status}`);
  }
  return (await resp.json()) as AuthSession;
}

/**
 * POST /api/v1/auth/signup
 * 회원가입 후 자동 로그인. 성공 시 backend 가 httpOnly cookie 발급.
 * 실패 시 throw (409=이미 가입됨 등) — signup page 에서 메시지 변환.
 */
export async function signup(
  email: string,
  password: string,
): Promise<AuthSession> {
  const url = `${API_BASE_URL}/api/v1/auth/signup`;
  const resp = await fetch(url, {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
    },
    body: JSON.stringify({ email, password }),
  });
  if (!resp.ok) {
    throw new Error(`signup_failed: HTTP ${resp.status}`);
  }
  return (await resp.json()) as AuthSession;
}

/**
 * GET /api/v1/auth/me
 * 현재 user 조회. 미인증 (401) / 네트워크 실패 / 알 수 없는 응답 시 null 반환.
 */
export async function getCurrentUser(): Promise<AuthSession | null> {
  try {
    const url = `${API_BASE_URL}/api/v1/auth/me`;
    const resp = await fetch(url, {
      method: "GET",
      credentials: "include",
      headers: { Accept: "application/json" },
    });
    if (resp.status === 401) return null;
    if (!resp.ok) return null;
    return (await resp.json()) as AuthSession;
  } catch {
    return null;
  }
}

/**
 * POST /api/v1/auth/logout
 * cookie clear. 실패해도 무시 (frontend 상태만 비움).
 */
export async function logout(): Promise<void> {
  try {
    const url = `${API_BASE_URL}/api/v1/auth/logout`;
    await fetch(url, {
      method: "POST",
      credentials: "include",
    });
  } catch {
    // graceful: 네트워크 실패해도 frontend 는 로그아웃 상태로 진입.
  }
}
