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
  CriticVerdict,
  ErrorEnvelope,
  FeedbackEventType,
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
        <p className="text-sm text-neutral-500 text-center leading-relaxed">
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
        {/* Phase 29 S5 — "내 brain 반영" 신호 (에이전트 느낌: 쓸수록 내 브랜드를 학습) */}
        {brainReflected !== null && (
          <div className="rounded-md border border-primary-200 bg-primary-50 px-3 py-2 text-sm text-primary-700">
            🧠 내 brain의 선호 {brainReflected}개를 반영해 만들었어요.
          </div>
        )}
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

      {/* Phase 5 Slice 4 — SSE Progress (PlanCard 외부 wrapper, ADR-022) */}
      {progress && progress.type === "progress" && (
        <section
          aria-label="생성 진행 상황"
          aria-live="polite"
          className="rounded-lg bg-primary-50 border border-primary-200 px-3 py-2 text-sm text-primary-900"
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

      {/* Critic 점수 + RAG 참조 */}
      {critic && (
        <section
          aria-label="품질 평가"
          className={`rounded-md px-3 py-2 ${VERDICT_CLASS[critic.overall_verdict]}`}
        >
          <p className="text-sm font-semibold">
            {/* Phase 9.5 Slice 4 (ADR-034): backend deprecated 0–5(overall_score_avg) 제거.
                canonical overall_score(0–1) 를 % 로 표시 (PlanCard 무수정 — page.tsx inline wrapper).
                canonical 미존재(graceful skip) 시 품질 점수 라벨 숨김, verdict 만 노출. */}
            {typeof critic.overall_score === "number" && (
              <>품질 점수 {Math.round(critic.overall_score * 100)}점 / 100 · </>
            )}
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

              {/* Phase 9 Slice 5 — 선택/반려 피드백 UI (★ PlanCard 외부 wrapper inline, ADR-030).
                  신규 component 안 만듦 → component_map.md 0줄. PlanCard.tsx 0줄.
                  wrapper 의 radio onClick 버블링 차단 위해 각 액션 stopPropagation. */}
              <div
                className="mt-3 px-1 flex flex-col gap-2"
                onClick={(e) => e.stopPropagation()}
                onKeyDown={(e) => e.stopPropagation()}
              >
                <div className="flex flex-wrap items-center gap-2">
                  <button
                    type="button"
                    disabled={selectBusy}
                    onClick={() => void handleConfirmSelect(i)}
                    aria-label={`옵션 ${i + 1} 이 안 선택`}
                    className={`inline-flex items-center justify-center min-h-[40px] px-3 py-2 rounded-md text-sm font-semibold transition-colors ${
                      savedSelectedIndex === i
                        ? "bg-primary-600 text-white"
                        : "bg-primary-500 text-white hover:bg-primary-600 active:bg-primary-700"
                    } disabled:opacity-50 disabled:cursor-not-allowed focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary-500`}
                  >
                    {savedSelectedIndex === i ? "선택 저장됨" : "이 안 선택"}
                  </button>

                  <button
                    type="button"
                    aria-pressed={feedbackByIndex[i] === "like"}
                    aria-label={`옵션 ${i + 1} 좋아요`}
                    onClick={() => void handleFeedback(i, "like")}
                    className={`inline-flex items-center justify-center min-h-[40px] px-3 py-2 rounded-md text-sm font-medium border transition-colors ${
                      feedbackByIndex[i] === "like"
                        ? "border-success-500 bg-success-50 text-success-700"
                        : "border-neutral-300 text-neutral-700 hover:bg-neutral-100"
                    } focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary-500`}
                  >
                    <span aria-hidden>👍</span>
                    <span className="ml-1">좋아요</span>
                  </button>

                  <button
                    type="button"
                    aria-pressed={feedbackByIndex[i] === "dislike"}
                    aria-label={`옵션 ${i + 1} 별로예요`}
                    onClick={() => void handleFeedback(i, "dislike")}
                    className={`inline-flex items-center justify-center min-h-[40px] px-3 py-2 rounded-md text-sm font-medium border transition-colors ${
                      feedbackByIndex[i] === "dislike"
                        ? "border-warning-500 bg-warning-50 text-warning-700"
                        : "border-neutral-300 text-neutral-700 hover:bg-neutral-100"
                    } focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary-500`}
                  >
                    <span aria-hidden>👎</span>
                    <span className="ml-1">별로예요</span>
                  </button>

                  <button
                    type="button"
                    aria-expanded={rejectOpenIndex === i}
                    aria-label={`옵션 ${i + 1} 반려 이유 입력`}
                    onClick={() => handleToggleReject(i)}
                    className={`inline-flex items-center justify-center min-h-[40px] px-3 py-2 rounded-md text-sm font-medium border transition-colors ${
                      feedbackByIndex[i] === "reject"
                        ? "border-error-500 bg-error-50 text-error-700"
                        : "border-neutral-300 text-neutral-700 hover:bg-neutral-100"
                    } focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary-500`}
                  >
                    {feedbackByIndex[i] === "reject" ? "반려됨" : "반려"}
                  </button>
                </div>

                {/* 반려 이유 입력 (inline textarea — 해당 카드에서만 노출) */}
                {rejectOpenIndex === i && (
                  <div className="flex flex-col gap-2 rounded-md border border-neutral-200 bg-neutral-50 p-3">
                    <label
                      htmlFor={`reject-reason-${i}`}
                      className="text-xs font-semibold text-neutral-700"
                    >
                      반려 이유 (선택 입력)
                    </label>
                    <textarea
                      id={`reject-reason-${i}`}
                      value={rejectReason}
                      onChange={(e) => setRejectReason(e.target.value)}
                      maxLength={2000}
                      rows={3}
                      placeholder="이 기획안이 맞지 않은 이유를 적어주세요 (선택)"
                      className="w-full rounded-md border border-neutral-300 px-2 py-1.5 text-sm text-neutral-900 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-1 focus-visible:outline-primary-500"
                    />
                    <div className="flex items-center gap-2">
                      <button
                        type="button"
                        onClick={() => void handleSubmitReject(i)}
                        className="inline-flex items-center justify-center min-h-[40px] px-3 py-2 rounded-md bg-error-500 text-white text-sm font-semibold hover:bg-error-600 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-error-500"
                      >
                        반려 제출
                      </button>
                      <button
                        type="button"
                        onClick={() => handleToggleReject(i)}
                        className="inline-flex items-center justify-center min-h-[40px] px-3 py-2 rounded-md border border-neutral-300 text-neutral-700 text-sm font-medium hover:bg-neutral-100"
                      >
                        취소
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </section>

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

      {/* Phase 29 S4 — 선택 저장 후 다음 행동 (브리프 §17 작업4: Brain CTA → "내 생각이 쌓인다" 락인) */}
      {savedSelectedIndex !== null && (
        <section className="flex flex-col gap-2 border-t border-neutral-200 pt-5">
          <h2 className="text-sm font-semibold text-neutral-900">
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
            className="flex items-center justify-between gap-3 min-h-[44px] rounded-lg border border-neutral-200 px-4 py-3 text-sm font-medium text-neutral-900 hover:bg-neutral-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-1 focus-visible:outline-primary-500"
          >
            <span>✏️ 같은 방향으로 새 영상 만들기</span>
            <span aria-hidden>›</span>
          </Link>
          <button
            type="button"
            disabled
            aria-disabled="true"
            className="flex items-center justify-between gap-3 min-h-[44px] rounded-lg border border-neutral-200 px-4 py-3 text-sm font-medium text-neutral-400 cursor-not-allowed"
          >
            <span>📱 이 기획안으로 SNS 콘텐츠 만들기</span>
            <span className="text-xs">준비중</span>
          </button>
        </section>
      )}

      {/* Bottom CTA (fixed) */}
      <footer className="fixed bottom-0 left-0 right-0 border-t border-neutral-200 bg-white p-4 z-10">
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
                : "bg-neutral-200 text-neutral-500 cursor-not-allowed"
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
