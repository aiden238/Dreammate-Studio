"use client";

/**
 * Phase 1 Slice 6 — 결과 페이지 (`/plan`)
 *
 * 정합:
 *   - work_plan.md Slice 6: PlanCard 1개 표시
 *   - acceptance.md A5: 제출 후 /plan 이동 + 결과 표시
 *   - design.md §13 (Output Display Rules — 단일 카드 단순 노출)
 *
 * Slice 6 단순화: sessionStorage 로 응답 인계. URL 파라미터 / route handler 인계는
 * Slice 7+ 또는 Phase 3 에서 검토. 새로고침 시 sessionStorage 가 유지되므로 OK,
 * 다른 탭 / 직접 URL 진입 시 "기획안 없음" 안내.
 */

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import PlanCard from "@/components/PlanCard";
import type { Envelope } from "@/lib/types";
import { isEnvelope } from "@/lib/types";

const SESSION_STORAGE_KEY = "dreammate.slice6.plan";

export default function PlanPage() {
  const router = useRouter();
  const [envelope, setEnvelope] = useState<Envelope | null>(null);
  const [hydrated, setHydrated] = useState(false);

  useEffect(() => {
    if (typeof window === "undefined") return;
    const raw = window.sessionStorage.getItem(SESSION_STORAGE_KEY);
    if (!raw) {
      setHydrated(true);
      return;
    }
    try {
      const parsed = JSON.parse(raw);
      if (isEnvelope(parsed)) {
        setEnvelope(parsed);
      }
    } catch {
      // 손상된 sessionStorage 항목 → 무시 (empty state)
    }
    setHydrated(true);
  }, []);

  function handleRestart() {
    if (typeof window !== "undefined") {
      window.sessionStorage.removeItem(SESSION_STORAGE_KEY);
    }
    router.push("/");
  }

  if (!hydrated) {
    // SSR / 첫 hydration 사이의 깜빡임 최소화
    return (
      <main className="mx-auto w-full max-w-2xl px-4 py-8" aria-busy>
        <p className="text-sm text-neutral-500">불러오는 중...</p>
      </main>
    );
  }

  if (!envelope) {
    return (
      <main className="mx-auto w-full max-w-2xl px-4 py-8 flex flex-col gap-4">
        <h1 className="text-xl font-bold text-neutral-900">기획안 없음</h1>
        <p className="text-sm text-neutral-600 leading-relaxed">
          아직 생성된 기획안이 없어요. 입력 페이지로 돌아가 새로 만들어 주세요.
        </p>
        <Link
          href="/"
          className="inline-flex items-center justify-center self-start min-h-[44px] px-4 py-2 rounded-md bg-primary-500 text-white text-sm font-semibold hover:bg-primary-600 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary-500"
        >
          입력 페이지로
        </Link>
      </main>
    );
  }

  const plan = envelope.body.plans[0];
  const warnings = envelope.validation.warnings ?? [];

  return (
    <main className="mx-auto w-full max-w-2xl px-4 py-6 sm:py-10 flex flex-col gap-6">
      <header className="flex flex-col gap-2">
        <p className="text-xs font-semibold tracking-wider uppercase text-primary-600">
          기획안
        </p>
        <h1 className="text-xl sm:text-2xl font-bold text-neutral-900">
          AI가 정리한 영상 기획안
        </h1>
        <p className="text-xs text-neutral-500">
          request_id: <span className="font-mono">{envelope.meta.request_id}</span>
        </p>
      </header>

      {plan ? (
        <PlanCard plan={plan} />
      ) : (
        <div
          role="alert"
          className="rounded-md border border-warning-500 bg-warning-50 px-3 py-2 text-sm text-warning-700"
        >
          응답에 기획안 카드가 포함되지 않았어요.
        </div>
      )}

      {warnings.length > 0 && (
        <section
          aria-label="응답 경고"
          className="rounded-md border border-neutral-200 bg-neutral-100 px-3 py-2 text-xs text-neutral-600"
        >
          <p className="font-semibold mb-1">참고</p>
          <ul className="list-disc list-inside flex flex-col gap-1">
            {warnings.map((w) => (
              <li key={w}>{w}</li>
            ))}
          </ul>
        </section>
      )}

      <footer className="mt-2 flex flex-col sm:flex-row gap-3">
        <button
          type="button"
          onClick={handleRestart}
          className="inline-flex items-center justify-center min-h-[44px] px-4 py-2 rounded-md bg-primary-500 text-white text-sm font-semibold hover:bg-primary-600 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary-500"
        >
          다시 만들기
        </button>
      </footer>
    </main>
  );
}
