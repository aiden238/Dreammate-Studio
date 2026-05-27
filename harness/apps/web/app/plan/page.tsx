"use client";

/**
 * Phase 1 Slice 7 — 결과 페이지 (`/plan`)
 *
 * 정합:
 *   - work_plan.md Slice 7: ErrorCard, Critic 점수 / RAG 참조 / project_id 표시
 *   - acceptance.md A5: 제출 후 /plan 이동 + 결과 표시
 *   - design.md §13 (Output Display Rules — 단일 카드 + 메타정보)
 *   - error_response_contract.md §11.1 (클라이언트 처리)
 *
 * Slice 6 대비 변경점:
 *   - 일반적인 에러는 `/` 에서 표시하지만, sessionStorage 로 넘어온 error 가 있으면 ErrorCard 노출
 *   - PlanCard 위에 Critic 점수 배지 / blocking_issues / RAG 참조 수 / project_id 상태 표시
 */

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import ErrorCard from "@/components/ErrorCard";
import PlanCard from "@/components/PlanCard";
import type {
  CriticEvaluation,
  CriticVerdict,
  Envelope,
  RAGReference,
} from "@/lib/types";
import { isEnvelope } from "@/lib/types";

const SESSION_STORAGE_KEY = "dreammate.slice6.plan";
const SESSION_ERROR_KEY = "dreammate.slice6.plan.error";

const VERDICT_LABEL: Record<CriticVerdict, string> = {
  approve: "승인",
  revise: "보완 필요",
  reject: "재시도 권장",
};

const VERDICT_CLASS: Record<CriticVerdict, string> = {
  approve: "bg-success-50 text-success-700 border-success-500",
  revise: "bg-warning-50 text-warning-700 border-warning-500",
  reject: "bg-error-50 text-error-700 border-error-500",
};

export default function PlanPage() {
  const router = useRouter();
  const [envelope, setEnvelope] = useState<Envelope | null>(null);
  const [storedError, setStoredError] = useState<{
    code: string;
    user_message?: string;
    request_id?: string;
    retry_allowed?: boolean;
  } | null>(null);
  const [hydrated, setHydrated] = useState(false);

  useEffect(() => {
    if (typeof window === "undefined") return;

    // 에러 우선 확인 (Slice 7: 일부 흐름에서 /plan 로 에러 동반 진입 가능)
    const errRaw = window.sessionStorage.getItem(SESSION_ERROR_KEY);
    if (errRaw) {
      try {
        const parsed = JSON.parse(errRaw);
        if (parsed && typeof parsed === "object" && "code" in parsed) {
          setStoredError(parsed);
          setHydrated(true);
          return;
        }
      } catch {
        // ignore
      }
    }

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
      window.sessionStorage.removeItem(SESSION_ERROR_KEY);
    }
    router.push("/");
  }

  if (!hydrated) {
    return (
      <main className="mx-auto w-full max-w-2xl px-4 py-8" aria-busy>
        <p className="text-sm text-neutral-500">불러오는 중...</p>
      </main>
    );
  }

  // ── 에러 페이로드 노출 ─────────────────────────────────────────────
  if (storedError) {
    return (
      <main className="mx-auto w-full max-w-2xl px-4 py-6 sm:py-10 flex flex-col gap-6">
        <ErrorCard
          error={{
            ok: false,
            error: {
              code: storedError.code,
              message: storedError.code,
              user_message: storedError.user_message,
              retry_allowed: storedError.retry_allowed,
              request_id: storedError.request_id,
            },
          }}
          onRetry={handleRestart}
          onHome={handleRestart}
        />
      </main>
    );
  }

  // ── envelope 비어있음 (직접 URL 진입 등) ──────────────────────────
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

  const plan = envelope.body.plan_candidates[0];
  const warnings = envelope.validation.warnings ?? [];
  const critic: CriticEvaluation | null | undefined =
    envelope.body.critic_evaluation;
  const ragRefs: RAGReference[] = envelope.body.rag_references ?? [];
  const projectId = envelope.meta.project_id ?? null;

  return (
    <main className="mx-auto w-full max-w-2xl px-4 py-6 sm:py-10 flex flex-col gap-6">
      <header className="flex flex-col gap-2">
        <p className="text-xs font-semibold tracking-wider uppercase text-primary-600">
          기획안
        </p>
        <h1 className="text-xl sm:text-2xl font-bold text-neutral-900">
          AI가 정리한 영상 기획안
        </h1>
        <p className="text-xs text-neutral-500 flex flex-wrap gap-x-3 gap-y-1">
          <span>
            request_id:{" "}
            <span className="font-mono">{envelope.meta.request_id}</span>
          </span>
          <span>
            {projectId ? (
              <span className="inline-flex items-center gap-1 text-success-700">
                <span aria-hidden>●</span> 저장됨
              </span>
            ) : (
              <span className="inline-flex items-center gap-1 text-neutral-500">
                <span aria-hidden>○</span> 임시 결과 (저장 안 됨)
              </span>
            )}
          </span>
        </p>
      </header>

      {/* Critic 점수 + blocking issues */}
      {critic && (
        <section
          aria-label="품질 평가"
          className={`rounded-md border px-3 py-3 ${VERDICT_CLASS[critic.overall_verdict]}`}
        >
          <div className="flex items-baseline justify-between gap-2 flex-wrap">
            <p className="text-sm font-semibold">
              품질 점수 {critic.overall_score_avg.toFixed(1)} / 5
            </p>
            <span className="text-xs font-medium">
              {VERDICT_LABEL[critic.overall_verdict]}
              {critic.revise_round > 0 && (
                <> · 개선 {critic.revise_round}회</>
              )}
            </span>
          </div>
          {critic.blocking_issues.length > 0 && (
            <ul className="mt-2 list-disc list-inside flex flex-col gap-1 text-xs">
              {critic.blocking_issues.map((issue, idx) => (
                <li key={idx}>{issue}</li>
              ))}
            </ul>
          )}
        </section>
      )}

      {/* RAG 참조 수 */}
      <section
        aria-label="참고 자료"
        className="text-xs text-neutral-600 flex items-center gap-2"
      >
        <span aria-hidden>📚</span>
        <span>
          {ragRefs.length > 0
            ? `참고 자료 ${ragRefs.length}개를 활용했어요`
            : "참고 자료 없이 생성했어요"}
        </span>
      </section>

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
