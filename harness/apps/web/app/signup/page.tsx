"use client";

/**
 * Phase 27 — Signup page (회원가입 → 자동 로그인).
 *
 * 정합:
 *   - lib/auth.ts: signup(email, password) — backend admin create + auto-login (httpOnly cookie)
 *   - design.md: mobile-first / 한 줄 form / 44px tap target
 *
 * 흐름: email + password 입력 → POST /auth/signup → 성공(자동 로그인) 시 router.push("/")
 */

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

import { signup } from "@/lib/auth";

export default function SignupPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const router = useRouter();

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    if (password.length < 6) {
      setError("비밀번호는 6자 이상이어야 해요.");
      return;
    }
    setSubmitting(true);
    try {
      await signup(email, password);
      router.push("/");
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err);
      if (msg.includes("409")) {
        setError("이미 가입된 이메일이에요. 로그인해 주세요.");
      } else {
        setError("회원가입 실패: 잠시 후 다시 시도해 주세요.");
      }
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-sm flex-col justify-center px-6 py-10">
      <header className="mb-6 flex flex-col gap-1">
        <h1 className="text-2xl font-bold text-neutral-900">회원가입</h1>
        <p className="text-sm text-neutral-600">
          이메일과 비밀번호로 계정을 만들면 바로 시작할 수 있어요.
        </p>
      </header>

      <form onSubmit={onSubmit} className="flex flex-col gap-4" noValidate>
        <div className="flex flex-col gap-1">
          <label htmlFor="email" className="text-sm font-medium text-neutral-800">
            이메일
          </label>
          <input
            id="email"
            type="email"
            autoComplete="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="min-h-[44px] w-full rounded-md border border-neutral-300 bg-white px-3 py-2 text-sm text-neutral-900 outline-none focus-visible:border-primary-500 focus-visible:ring-2 focus-visible:ring-primary-200"
            aria-required="true"
            aria-invalid={error ? "true" : "false"}
          />
        </div>

        <div className="flex flex-col gap-1">
          <label htmlFor="password" className="text-sm font-medium text-neutral-800">
            비밀번호 (6자 이상)
          </label>
          <input
            id="password"
            type="password"
            autoComplete="new-password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="min-h-[44px] w-full rounded-md border border-neutral-300 bg-white px-3 py-2 text-sm text-neutral-900 outline-none focus-visible:border-primary-500 focus-visible:ring-2 focus-visible:ring-primary-200"
            aria-required="true"
            aria-invalid={error ? "true" : "false"}
          />
        </div>

        {error && (
          <div
            role="alert"
            className="rounded-md bg-error-50 px-3 py-2 text-sm text-error-700"
          >
            {error}
          </div>
        )}

        <button
          type="submit"
          disabled={submitting || !email || !password}
          className={`mt-2 inline-flex min-h-[44px] w-full items-center justify-center rounded-md px-4 py-3 text-sm font-semibold transition-colors ${
            submitting || !email || !password
              ? "bg-neutral-200 text-neutral-500 cursor-not-allowed"
              : "bg-primary-500 text-white hover:bg-primary-600 active:bg-primary-700 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary-500"
          }`}
        >
          {submitting ? "처리 중..." : "회원가입하고 시작하기"}
        </button>
      </form>

      <p className="mt-6 text-center text-sm text-neutral-600">
        이미 계정이 있으신가요?{" "}
        <Link href="/login" className="font-medium text-primary-600 hover:underline">
          로그인
        </Link>
      </p>
    </main>
  );
}
