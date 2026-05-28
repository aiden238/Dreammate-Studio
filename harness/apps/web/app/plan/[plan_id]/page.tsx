"use client";

/**
 * Phase 4 Slice 3 — Multi-plan 결과 페이지 (`/plan/[plan_id]`)
 *
 * 정합:
 *   - work_plan.md Slice 3: 3-plan 표시 + 1 선택 (PlanCard × 3 단순 세로 스택)
 *   - acceptance.md A5 (Phase 3 회귀 0), A6 (3-plan 표시 + 1 선택)
 *   - non_goals.md: PlanCard 4-layer 재정의 절대 X (D3 Phase 5+)
 *   - 사용자 결정 6-a: **PlanCard.tsx 무수정 import 만** ★
 *   - design.md §13 (Output Display Rules), §22 (Generation Progress)
 *   - api_contract.md §8: GET /plans/{id} → envelope null 이면 POST /generate 호출
 *
 * 핵심 원칙:
 *   - PlanCard × N 단순 반복 (PlanComparisonCard 본격은 Phase 5+ — D4 deferred)
 *   - 카드 클릭 → selected_plan_id state + sessionStorage 저장
 *   - Loading / Error 상태 (Phase 1 ErrorCard 재사용)
 *   - Phase 1 `/plan` 페이지 (sessionStorage envelope) 와 분리된 라우트
 */

import { useCallback, useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";

import AuthGuard from "@/components/AuthGuard"; // Phase 5 Slice 3 — 외부 wrapper (PlanCard 무수정 유지)
import ErrorCard from "@/components/ErrorCard";
import PlanCard from "@/components/PlanCard"; // ★ 무수정 import (사용자 결정 6-a)
import ProgressStepper from "@/components/ProgressStepper";
import { generateMultiPlan, getPlan } from "@/lib/api";
import type {
  CriticEvaluation,
  CriticVerdict,
  ErrorEnvelope,
  MultiPlanEnvelope,
  Plan,
  RAGReference,
} from "@/lib/types";
import { isEnvelope } from "@/lib/types";

const SESSION_KEY_PREFIX = "dreammate.phase4.plan.selected";

const VERDICT_LABEL: Record<CriticVerdict, string> = {
  approve: "승인",
  revise: "보완 필요",
  reject: "재시도 권장",
};

const VERDICT_CLASS: Record<CriticVerdict, string> = {
  approve: "bg-success-50 text-success-700",
  revise: "bg-warning-50 text-warning-700",
  reject: "bg-error-50 text-error-700",
};

/**
 * Phase 5 Slice 3 — AuthGuard 외부 wrapper.
 * 기존 PlanResultPage 컴포넌트 로직은 PlanResultPageContent 로 이동.
 * PlanCard.tsx + component_map.md 무수정 정신 계승 (외부에서만 wrap).
 */
export default function PlanResultPage() {
  return (
    <AuthGuard>
      <PlanResultPageContent />
    </AuthGuard>
  );
}

function PlanResultPageContent() {
  const params = useParams<{ plan_id: string }>();
  const router = useRouter();
  const planId = String(params?.plan_id ?? "");

  const [loading, setLoading] = useState(true);
  const [envelope, setEnvelope] = useState<MultiPlanEnvelope | null>(null);
  const [error, setError] = useState<ErrorEnvelope | null>(null);
  const [selectedPlanId, setSelectedPlanId] = useState<string | null>(null);

  // sessionStorage 에서 이전 선택 복원
  useEffect(() => {
    if (typeof window === "undefined" || !planId) return;
    try {
      const saved = window.sessionStorage.getItem(
        `${SESSION_KEY_PREFIX}.${planId}`,
      );
      if (saved) setSelectedPlanId(saved);
    } catch {
      // ignore (private mode / sessionStorage 비활성 등)
    }
  }, [planId]);

  const load = useCallback(async () => {
    if (!planId) {
      setLoading(false);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      // 1. plan resource 조회 (이미 생성됐다면 그대로 표시)
      const resource = await getPlan(planId);
      if (resource.envelope && isEnvelope(resource.envelope)) {
        setEnvelope(resource.envelope as MultiPlanEnvelope);
        setLoading(false);
        return;
      }

      // 2. envelope 미생성 시 POST /generate 호출
      const result = await generateMultiPlan(planId);
      if (result.ok) {
        setEnvelope(result.envelope);
      } else {
        setError(result.error);
      }
    } catch (e) {
      const message = e instanceof Error ? e.message : "unknown";
      setError({
        ok: false,
        error: {
          code: "NET-000",
          message,
          user_message:
            "서버와 통신할 수 없어요. 잠시 후 다시 시도해주세요.",
          retry_allowed: true,
        },
      });
    } finally {
      setLoading(false);
    }
  }, [planId]);

  useEffect(() => {
    void load();
  }, [load]);

  const handleSelect = useCallback(
    (clickedPlanId: string) => {
      setSelectedPlanId(clickedPlanId);
      if (typeof window !== "undefined") {
        try {
          window.sessionStorage.setItem(
            `${SESSION_KEY_PREFIX}.${planId}`,
            clickedPlanId,
          );
        } catch {
          // ignore
        }
      }
    },
    [planId],
  );

  const handleHome = useCallback(() => {
    router.push("/");
  }, [router]);

  // ── Loading 상태 (Phase 1 ProgressStepper 재사용) ──────────────────
  if (loading) {
    return (
      <main
        className="mx-auto w-full max-w-2xl px-4 py-8 flex flex-col items-center justify-center gap-4 min-h-[60vh]"
        aria-busy
      >
        <ProgressStepper currentStep="planning" />
        <p className="text-sm text-neutral-500">
          AI가 기획안 3개를 만들고 있어요 (약 30~60초 소요)
        </p>
      </main>
    );
  }

  // ── Error 상태 (Phase 1 ErrorCard 재사용) ──────────────────────────
  if (error) {
    return (
      <main className="mx-auto w-full max-w-2xl px-4 py-6 sm:py-10 flex flex-col gap-6">
        <ErrorCard error={error} onRetry={load} onHome={handleHome} />
      </main>
    );
  }

  // ── Envelope 없음 (방어) ───────────────────────────────────────────
  if (!envelope || !envelope.body.plan_candidates?.length) {
    return (
      <main className="mx-auto w-full max-w-2xl px-4 py-8 flex flex-col gap-4 items-center text-center">
        <h1 className="text-xl font-bold text-neutral-900">기획안 없음</h1>
        <p className="text-sm text-neutral-600">
          생성된 기획안이 없어요. 처음으로 돌아가 다시 시도해주세요.
        </p>
        <button
          type="button"
          onClick={handleHome}
          className="inline-flex items-center justify-center min-h-[44px] px-4 py-2 rounded-md bg-primary-500 text-white text-sm font-semibold hover:bg-primary-600"
        >
          처음으로
        </button>
      </main>
    );
  }

  const plans: Plan[] = envelope.body.plan_candidates;
  const critic: CriticEvaluation | null | undefined =
    envelope.body.critic_evaluation;
  const ragRefs: RAGReference[] = envelope.body.rag_references ?? [];
  const projectId = envelope.meta.project_id ?? null;
  const warnings = envelope.validation.warnings ?? [];
  // Phase 4.5 Slice 3 (Z-X3): Critic 8-dim 기준 best-plan index. null 시 highlight 없음.
  const recommendedIdx: number | null =
    typeof envelope.body.recommended_plan_index === "number"
      ? envelope.body.recommended_plan_index
      : null;

  return (
    <main className="mx-auto w-full max-w-2xl px-4 py-6 sm:py-10 pb-32 flex flex-col gap-6">
      {/* Header */}
      <header className="flex flex-col gap-2">
        <p className="text-xs font-semibold tracking-wider uppercase text-primary-600">
          기획안 {plans.length}개
        </p>
        <h1 className="text-xl sm:text-2xl font-bold text-neutral-900">
          AI가 만든 영상 기획안 {plans.length}개
        </h1>
        <p className="text-sm text-neutral-600">
          마음에 드는 기획안을 선택하세요.
        </p>
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
                <span aria-hidden>○</span> 임시 결과
              </span>
            )}
          </span>
        </p>
      </header>

      {/* Critic 점수 + RAG 참조 */}
      {critic && (
        <section
          aria-label="품질 평가"
          className={`rounded-md px-3 py-2 ${VERDICT_CLASS[critic.overall_verdict]}`}
        >
          <p className="text-sm font-semibold">
            품질 점수 {critic.overall_score_avg.toFixed(1)} / 5 ·{" "}
            {VERDICT_LABEL[critic.overall_verdict]}
            {critic.revise_round > 0 && (
              <span className="ml-1 text-xs">
                (개선 {critic.revise_round}회)
              </span>
            )}
          </p>
          {critic.blocking_issues.length > 0 && (
            <ul className="mt-1 list-disc list-inside text-xs">
              {critic.blocking_issues.map((issue, idx) => (
                <li key={idx}>{issue}</li>
              ))}
            </ul>
          )}
        </section>
      )}

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

      {/* 3-plan 세로 스택 (★ PlanCard 무수정 + 단순 반복) */}
      <section
        aria-label="기획안 후보 목록"
        role="radiogroup"
        className="flex flex-col gap-4"
      >
        {plans.map((plan, i) => {
          const isSelected = selectedPlanId === plan.plan_id;
          const isRecommended = recommendedIdx === i;
          // selected 우선순위: 선택됨 시 primary ring, 그렇지 않고 추천일 때 emerald ring.
          const ringClass = isSelected
            ? "ring-2 ring-primary-500 ring-offset-2"
            : isRecommended
              ? "ring-2 ring-emerald-500 ring-offset-2"
              : "ring-0 hover:ring-1 hover:ring-neutral-300";
          return (
            <div
              key={plan.plan_id}
              role="radio"
              aria-checked={isSelected}
              aria-label={`기획안 ${i + 1} / ${plans.length} — ${plan.name}${
                isRecommended ? " (AI 추천)" : ""
              }`}
              data-recommended={isRecommended ? "true" : "false"}
              tabIndex={0}
              onClick={() => handleSelect(plan.plan_id)}
              onKeyDown={(e) => {
                if (e.key === "Enter" || e.key === " ") {
                  e.preventDefault();
                  handleSelect(plan.plan_id);
                }
              }}
              className={`relative cursor-pointer rounded-lg transition-shadow ${ringClass} focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary-500`}
            >
              {/* Phase 4.5 Slice 3 (Z-X3): AI 추천 badge — wrapper 에만 추가 (PlanCard 무수정). */}
              {isRecommended && !isSelected && (
                <span
                  aria-hidden
                  className="absolute -top-2 left-3 z-10 inline-flex items-center rounded-full bg-emerald-500 px-2 py-0.5 text-xs font-semibold text-white shadow"
                >
                  AI 추천
                </span>
              )}
              <div className="flex items-center gap-2 mb-2 px-1">
                <span className="text-xs font-medium text-neutral-500">
                  옵션 {i + 1} / {plans.length}
                </span>
                {isSelected && (
                  <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-primary-500 text-white">
                    선택됨
                  </span>
                )}
              </div>
              <PlanCard plan={plan} />
            </div>
          );
        })}
      </section>

      {/* Warnings (개발자 정보) */}
      {warnings.length > 0 && (
        <details className="rounded-md border border-neutral-200 bg-neutral-100 px-3 py-2 text-xs text-neutral-600">
          <summary className="font-semibold cursor-pointer">
            개발자 정보 ({warnings.length} warnings)
          </summary>
          <ul className="mt-1 ml-4 list-disc">
            {warnings.map((w) => (
              <li key={w}>{w}</li>
            ))}
          </ul>
        </details>
      )}

      {/* Bottom CTA (fixed) */}
      <footer className="fixed bottom-0 left-0 right-0 border-t border-neutral-200 bg-white p-4 z-10">
        <div className="mx-auto w-full max-w-2xl">
          <button
            type="button"
            disabled={!selectedPlanId}
            onClick={() => {
              const sel = plans.find((p) => p.plan_id === selectedPlanId);
              // Phase 4 Slice 3: 단순 alert. Phase 5+ Feedback 흐름에서 본격화.
              window.alert(
                `선택: ${sel?.name ?? selectedPlanId}\n` +
                  `(Phase 5+에서 저장 / 피드백 흐름 추가)`,
              );
            }}
            aria-label="선택 확정"
            className={`w-full min-h-[44px] px-4 py-3 rounded-md text-sm font-semibold transition-colors ${
              selectedPlanId
                ? "bg-primary-500 text-white hover:bg-primary-600 active:bg-primary-700 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary-500"
                : "bg-neutral-200 text-neutral-500 cursor-not-allowed"
            }`}
          >
            {selectedPlanId ? "이 기획안으로 진행" : "카드를 선택하세요"}
          </button>
        </div>
      </footer>
    </main>
  );
}
