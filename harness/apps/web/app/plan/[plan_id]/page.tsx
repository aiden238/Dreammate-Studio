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
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";

import AuthGuard from "@/components/AuthGuard"; // Phase 5 Slice 3 — 외부 wrapper (PlanCard 무수정 유지)
import ErrorCard from "@/components/ErrorCard";
import PlanCard from "@/components/PlanCard"; // ★ 무수정 import (사용자 결정 6-a)
import ProgressStepper from "@/components/ProgressStepper";
// Phase 30 Slice 5 — PlanCard 외부 wrapper(표현 계층 전용). PlanCard.tsx 무수정.
//   COMPONENT_MAPPING §6 권장 구조: PlanComparisonGrid ▸ PlanOptionFrame ▸ PlanCard
//   + PlanFeedbackControls + BrandMemoryAside + BrainReflectedBanner.
import BrainReflectedBanner from "@/components/plan/BrainReflectedBanner";
import BrandMemoryAside from "@/components/plan/BrandMemoryAside";
import PlanComparisonGrid from "@/components/plan/PlanComparisonGrid";
import PlanFeedbackControls from "@/components/plan/PlanFeedbackControls";
import PlanOptionFrame from "@/components/plan/PlanOptionFrame";
import {
  generateMultiPlan,
  getPkmGraph,
  getPlan,
  selectPlan,
  sendFeedback,
} from "@/lib/api";
import { subscribeToPlanProgress, type ProgressEvent } from "@/lib/sse";
import type {
  CriticEvaluation,
  ErrorEnvelope,
  FeedbackEventType,
  MultiPlanEnvelope,
  Plan,
  RAGReference,
} from "@/lib/types";
import { isEnvelope } from "@/lib/types";

const SESSION_KEY_PREFIX = "dreammate.phase4.plan.selected";

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
  // Phase 5 Slice 4 — SSE Progress 상태 (D7). PlanCard 무수정 정신 계승:
  // 본 state 와 UI 는 PlanCard 외부 wrapper 에만 영향.
  const [progress, setProgress] = useState<ProgressEvent | null>(null);
  // Phase 29 S5 — "내 brain 반영" 신호. 로그인 + PKM(개인/브랜드)>0 이면 realuse 주입이 적용됨.
  const [brainReflected, setBrainReflected] = useState<number | null>(null);

  // Phase 9 Slice 5 — 선택/반려 피드백 상태 (ADR-030). PlanCard 무수정 정신 계승:
  // 본 state 와 UI 는 모두 PlanCard 외부 wrapper (page.tsx inline) 에만 영향.
  //   - savedSelectedIndex: backend /select 저장 완료된 option_index (null = 미저장).
  //   - selectBusy: /select 호출 중 (버튼 중복 클릭 방지).
  //   - feedbackByIndex: option_index → 마지막으로 전송한 피드백 event_type (UI 표시용).
  //   - rejectOpenIndex: 반려 이유 textarea 가 열린 카드 index (null = 모두 닫힘).
  //   - rejectReason: 반려 이유 입력값 (열린 카드 전용 — 닫힐 때 초기화).
  //   - actionError: 선택/피드백 호출 실패 시 사용자 표시 메시지.
  const [savedSelectedIndex, setSavedSelectedIndex] = useState<number | null>(
    null,
  );
  const [selectBusy, setSelectBusy] = useState(false);
  const [feedbackByIndex, setFeedbackByIndex] = useState<
    Record<number, FeedbackEventType>
  >({});
  const [rejectOpenIndex, setRejectOpenIndex] = useState<number | null>(null);
  const [rejectReason, setRejectReason] = useState("");
  const [actionError, setActionError] = useState<string | null>(null);

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

  // Phase 29 S5 — 생성 후 "내 brain 반영" 신호: 로그인 + PKM(개인/브랜드)>0 이면
  //   realuse 주입 경로상 이번 기획에 반영됨. 미로그인/무PKM/실패 → 표시 안 함(graceful).
  useEffect(() => {
    if (loading) return;
    let alive = true;
    getPkmGraph()
      .then((g) => {
        if (!alive) return;
        const count = (g.summary.personal ?? 0) + (g.summary.brand ?? 0);
        if (count > 0) setBrainReflected(count);
      })
      .catch(() => {
        /* 미로그인/실패 → 배너 미표시 (graceful) */
      });
    return () => {
      alive = false;
    };
  }, [loading]);

  // Phase 5 Slice 4 — SSE Progress 구독 (ADR-022).
  // PlanCard.tsx 무수정 유지: progress UI 는 본 컴포넌트 상단 외부 wrapper 에만 렌더.
  useEffect(() => {
    if (!planId) return;
    if (typeof window === "undefined") return; // SSR 안전
    const sub = subscribeToPlanProgress(planId, (event) => {
      setProgress(event);
    });
    return () => {
      sub.close();
    };
  }, [planId]);

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

  // Phase 9 Slice 5 — backend /select 저장 (ADR-030). PlanCard 외부 wrapper inline.
  //   - optionIndex 는 plan_candidates 배열 인덱스 (0–2) = SelectPlanRequest.selected_option_index.
  //   - 성공 시 savedSelectedIndex 갱신 (선택 저장 표시). 실패 시 actionError 표시 (graceful).
  const handleConfirmSelect = useCallback(
    async (optionIndex: number, reason?: string | null) => {
      if (!planId) return;
      setSelectBusy(true);
      setActionError(null);
      try {
        const resp = await selectPlan(planId, {
          selected_option_index: optionIndex,
          selection_reason: reason ?? null,
        });
        setSavedSelectedIndex(resp.selected_option_index);
      } catch {
        setActionError(
          "선택을 저장하지 못했어요. 잠시 후 다시 시도해주세요.",
        );
      } finally {
        setSelectBusy(false);
      }
    },
    [planId],
  );

  // Phase 9 Slice 5 — like / dislike 피드백 (ADR-030). PlanCard 외부 wrapper inline.
  const handleFeedback = useCallback(
    async (optionIndex: number, eventType: FeedbackEventType) => {
      if (!planId) return;
      setActionError(null);
      // 낙관적 UI: 즉시 표시, 실패 시 롤백.
      setFeedbackByIndex((prev) => ({ ...prev, [optionIndex]: eventType }));
      try {
        await sendFeedback(planId, {
          event_type: eventType,
          option_index: optionIndex,
        });
      } catch {
        setFeedbackByIndex((prev) => {
          const next = { ...prev };
          delete next[optionIndex];
          return next;
        });
        setActionError(
          "피드백을 저장하지 못했어요. 잠시 후 다시 시도해주세요.",
        );
      }
    },
    [planId],
  );

  // Phase 9 Slice 5 — 반려 이유 제출 (event_type="reject"). PlanCard 외부 wrapper inline.
  const handleSubmitReject = useCallback(
    async (optionIndex: number) => {
      if (!planId) return;
      const reason = rejectReason.trim();
      setActionError(null);
      try {
        await sendFeedback(planId, {
          event_type: "reject",
          option_index: optionIndex,
          reason: reason.length > 0 ? reason : null,
        });
        setFeedbackByIndex((prev) => ({ ...prev, [optionIndex]: "reject" }));
        setRejectOpenIndex(null);
        setRejectReason("");
      } catch {
        setActionError(
          "반려를 저장하지 못했어요. 잠시 후 다시 시도해주세요.",
        );
      }
    },
    [planId, rejectReason],
  );

  // 반려 이유 textarea 토글 (열기/닫기). 닫을 때 입력값 초기화.
  const handleToggleReject = useCallback((optionIndex: number) => {
    setRejectOpenIndex((prev) => {
      const next = prev === optionIndex ? null : optionIndex;
      if (next === null) setRejectReason("");
      return next;
    });
  }, []);

  // ── Loading 상태 (Phase 1 ProgressStepper 재사용) ──────────────────
  if (loading) {
    return (
      <main
        className="mx-auto w-full max-w-2xl px-4 py-8 flex flex-col items-center justify-center gap-4 min-h-[60vh]"
        aria-busy
      >
        <ProgressStepper currentStep="planning" />
        <p className="text-sm text-text-muted text-center leading-relaxed">
          AI 기획 파트너가 내 brain의 방향을 확인하고
          <br />
          기획안 3개를 작성하고 있어요 (약 30~60초)
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
        <h1 className="font-display text-xl font-bold text-text-default">
          기획안 없음
        </h1>
        <p className="text-sm text-text-muted">
          생성된 기획안이 없어요. 처음으로 돌아가 다시 시도해주세요.
        </p>
        <button
          type="button"
          onClick={handleHome}
          className="inline-flex items-center justify-center min-h-[44px] px-4 py-2 rounded-md bg-primary-500 text-white text-sm font-semibold hover:bg-primary-600 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary-500"
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
    <main className="mx-auto w-full max-w-6xl px-4 py-6 sm:py-10 pb-32 flex flex-col gap-6">
      {/* Header */}
      <header className="flex flex-col gap-2">
        <p className="text-xs font-semibold tracking-wider uppercase text-primary-600">
          기획안 {plans.length}개
        </p>
        <h1 className="font-display text-xl sm:text-2xl font-bold text-text-default">
          AI가 만든 영상 기획안 {plans.length}개
        </h1>
        <p className="text-sm text-text-muted">
          서로 다른 접근을 같은 기준으로 비교하고, 마음에 드는 기획안을
          선택하세요.
        </p>
        {/* Phase 29 S5 / Phase 30 S5 — "내 brain 반영" 신호 (BrainReflectedBanner wrapper) */}
        <BrainReflectedBanner count={brainReflected} />
        <p className="text-xs text-text-muted flex flex-wrap gap-x-3 gap-y-1">
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
              <span className="inline-flex items-center gap-1 text-text-muted">
                <span aria-hidden>○</span> 임시 결과
              </span>
            )}
          </span>
        </p>
      </header>

      {/* Phase 5 Slice 4 — SSE Progress (PlanCard 외부 wrapper, ADR-022) */}
      {progress && progress.type === "progress" && (
        <section
          aria-label="생성 진행 상황"
          aria-live="polite"
          className="rounded-xl bg-primary-50 border border-primary-200 px-3 py-2 text-sm text-primary-700"
        >
          <p className="font-semibold">
            단계 {progress.step} / 4 — {progress.name ?? ""}
          </p>
          <p className="mt-1 text-xs">{progress.message}</p>
          {typeof progress.duration_estimate_sec === "number" && (
            <p className="mt-0.5 text-xs text-primary-700">
              예상 {progress.duration_estimate_sec}초
            </p>
          )}
        </section>
      )}

      {/* 데스크톱 2열(비교 그리드 + Brand Memory aside) / 모바일 1열(VISUAL_CONTRACT §5) */}
      <div className="grid grid-cols-1 gap-5 desktop:grid-cols-[minmax(0,1fr)_300px]">
        {/* 좌: 3열 비교 그리드 (★ PlanComparisonGrid ▸ PlanOptionFrame ▸ PlanCard 무수정) */}
        <PlanComparisonGrid label="기획안 후보 목록">
          {plans.map((plan, i) => {
            const isSelected = selectedPlanId === plan.plan_id;
            const isRecommended = recommendedIdx === i;
            return (
              <PlanOptionFrame
                key={plan.plan_id}
                optionIndex={i}
                total={plans.length}
                planName={plan.name}
                selected={isSelected}
                recommended={isRecommended}
                onSelect={() => handleSelect(plan.plan_id)}
                footer={
                  <PlanFeedbackControls
                    optionIndex={i}
                    savedSelectedIndex={savedSelectedIndex}
                    selectBusy={selectBusy}
                    feedback={feedbackByIndex[i]}
                    rejectOpen={rejectOpenIndex === i}
                    rejectReason={rejectReason}
                    onConfirmSelect={(idx) => void handleConfirmSelect(idx)}
                    onFeedback={(idx, et) => void handleFeedback(idx, et)}
                    onToggleReject={handleToggleReject}
                    onSubmitReject={(idx) => void handleSubmitReject(idx)}
                    onRejectReasonChange={setRejectReason}
                  />
                }
              >
                {/* ★ PlanCard 무수정 import */}
                <PlanCard plan={plan} />
              </PlanOptionFrame>
            );
          })}
        </PlanComparisonGrid>

        {/* 우: Brand Memory aside — 기존 critic·rag 데이터 표시 (목업 아님) */}
        <BrandMemoryAside critic={critic} ragRefs={ragRefs} />
      </div>

      {/* Phase 9 Slice 5 — 선택/피드백 호출 실패 표시 (PlanCard 외부 wrapper) */}
      {actionError && (
        <p
          role="alert"
          className="rounded-md bg-error-50 border border-error-200 px-3 py-2 text-sm text-error-700"
        >
          {actionError}
        </p>
      )}

      {/* Warnings (개발자 정보) */}
      {warnings.length > 0 && (
        <details className="rounded-md border border-border-default bg-bg-subtle px-3 py-2 text-xs text-text-muted">
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

      {/* Phase 29 S4 — 선택 저장 후 다음 행동 (브리프 §17 작업4: Brain CTA → "내 생각이 쌓인다" 락인) */}
      {savedSelectedIndex !== null && (
        <section className="flex flex-col gap-2 border-t border-border-default pt-5">
          <h2 className="font-display text-sm font-semibold text-text-default">
            선택을 저장했어요 — 이 방향이 내 brain에 쌓였어요 🧠
          </h2>
          <Link
            href="/brain"
            className="flex items-center justify-between gap-3 min-h-[44px] rounded-lg border border-primary-300 bg-primary-50 px-4 py-3 text-sm font-medium text-primary-700 hover:bg-primary-100 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-1 focus-visible:outline-primary-500"
          >
            <span>🧠 내 brain에서 보기</span>
            <span aria-hidden>›</span>
          </Link>
          <Link
            href="/"
            className="flex items-center justify-between gap-3 min-h-[44px] rounded-lg border border-border-default bg-surface px-4 py-3 text-sm font-medium text-text-default hover:bg-primary-50/60 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-1 focus-visible:outline-primary-500"
          >
            <span>✏️ 같은 방향으로 새 영상 만들기</span>
            <span aria-hidden>›</span>
          </Link>
          <button
            type="button"
            disabled
            aria-disabled="true"
            className="flex items-center justify-between gap-3 min-h-[44px] rounded-lg border border-border-default px-4 py-3 text-sm font-medium text-text-placeholder cursor-not-allowed"
          >
            <span>📱 이 기획안으로 SNS 콘텐츠 만들기</span>
            <span className="text-xs">준비중</span>
          </button>
        </section>
      )}

      {/* Bottom CTA (fixed) */}
      <footer className="fixed bottom-0 left-0 right-0 border-t border-border-default bg-surface p-4 z-10">
        <div className="mx-auto w-full max-w-2xl">
          <button
            type="button"
            disabled={!selectedPlanId || selectBusy}
            onClick={() => {
              // Phase 9 Slice 5 (ADR-030): backend /select 저장 (PlanCard 외부 wrapper).
              // 로컬 선택된 plan_id → plan_candidates 배열 인덱스(0–2) 매핑 후 저장.
              const idx = plans.findIndex((p) => p.plan_id === selectedPlanId);
              if (idx >= 0) {
                void handleConfirmSelect(idx);
              }
            }}
            aria-label="선택 확정"
            className={`w-full min-h-[44px] px-4 py-3 rounded-md text-sm font-semibold transition-colors ${
              selectedPlanId && !selectBusy
                ? "bg-primary-500 text-white hover:bg-primary-600 active:bg-primary-700 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary-500"
                : "bg-neutral-200 text-text-muted cursor-not-allowed"
            }`}
          >
            {!selectedPlanId
              ? "카드를 선택하세요"
              : selectBusy
                ? "저장 중…"
                : savedSelectedIndex !== null &&
                    plans[savedSelectedIndex]?.plan_id === selectedPlanId
                  ? "선택 저장됨"
                  : "이 기획안으로 진행"}
          </button>
        </div>
      </footer>
    </main>
  );
}
