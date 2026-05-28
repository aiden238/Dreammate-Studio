"use client";

/**
 * Phase 5 Slice 3 — AuthGuard wrapper.
 *
 * 사용 패턴 (PlanCard 무수정 정신 계승):
 *   export default function Page() {
 *     return (
 *       <AuthGuard>
 *         <PageContent />
 *       </AuthGuard>
 *     );
 *   }
 *
 * 동작:
 *   - mount 시 GET /auth/me 호출
 *   - 인증됨 → children 렌더
 *   - 미인증 → /login 으로 router.push + fallback (또는 null)
 *
 * 참조:
 *   - harness/apps/web/lib/auth.ts (getCurrentUser)
 *   - harness/meta/security_reviews/2026-05-29_phase-5-auth-rls.md §T1
 */

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { getCurrentUser } from "@/lib/auth";
import type { AuthSession } from "@/lib/types";

interface AuthGuardProps {
  children: React.ReactNode;
  /** 미인증 상태에서 redirect 직전 잠시 보일 fallback. 기본값 null. */
  fallback?: React.ReactNode;
  /** redirect target. 기본값 "/login". */
  redirectTo?: string;
}

export default function AuthGuard({
  children,
  fallback = null,
  redirectTo = "/login",
}: AuthGuardProps) {
  const [session, setSession] = useState<AuthSession | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    let mounted = true;
    void getCurrentUser().then((s) => {
      if (!mounted) return;
      setSession(s);
      setLoading(false);
      if (!s) {
        router.push(redirectTo);
      }
    });
    return () => {
      mounted = false;
    };
  }, [router, redirectTo]);

  if (loading) {
    return (
      <div
        className="p-8 text-center text-sm text-neutral-500"
        aria-busy
        aria-live="polite"
      >
        인증 확인 중...
      </div>
    );
  }

  if (!session) {
    return <>{fallback}</>;
  }

  return <>{children}</>;
}
