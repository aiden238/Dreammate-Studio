"use client";

/**
 * Phase 34 S2 (cross-project 수렴) — 단일 대화형 기획 페이지 (`/new/flow`)
 *
 * plotter의 "한 화면 대화 흐름"(입력 → 확인 → 카드 → 이어가기)을 Dreammate에 흡수.
 * 단, 라우트를 넘나드는 기존 위저드(/new/quick/* · /plan/[id])는 **무변경**으로 두고,
 * 이 페이지는 **추가 라우트**로 공존한다(테스트 후 아니면 폐기만 — 기존 흐름 무손상, 가역).
 *
 * ★ 디자인 보존: orange×beige 카드 화면을 그대로 — 결과 단계는 기존 카드 페이지(/plan/[id])와
 *   **동일 컴포넌트·동일 상호작용**(PlanComparisonGrid ▸ PlanOptionFrame ▸ PlanCard +
 *   PlanFeedbackControls + BrandMemoryAside + BrainReflectedBanner + 저장/임시 상태칩 +
 *   고정 하단 "이 기획안으로 진행" CTA + 선택완료 FinalBriefPanel)을 재현한다.
 *   확인 턴은 DirectionApprovalCard(명확도 배지 포함), 이어가기는 FollowUpComposer 재사용.
 *
 * 흐름(한 화면, 대화식 누적):
 *   intent  — 의도 입력(QuickInputCard)
 *   confirm — "이렇게 이해했어요 — 맞나요?" + 명확도 + 보정 (DirectionApprovalCard)
 *   generating — 낙관적 ProgressStepper (startPlan→wizardStep×3→generateMultiPlan, 30~60s)
 *   result  — 기획안 카드 3개(선택·저장·피드백) + 이어서 요청하기(스레드 누적) + 선택완료 브리프
 *
 * 백엔드: 기존 위저드 API 그대로(startPlan/wizardStep/generateMultiPlan/selectPlan/sendFeedback).
 *   목 모드 없음 → generate 단계는 :8000 필요(확인 턴까지는 클라이언트라 키 없이도 동작).
 *
 * 인증: 전체 AuthGuard 미적용 — 의도 입력은 기존 위저드 입력처럼 익명 친화로 둔다(로그인 강제 X).
 *   select/feedback/getPkmGraph는 익명이면 백엔드가 graceful(401→actionError·배너 미표시)로 흡수.
 */

import { useCallback, useEffect, useRef, useState } from "react";
import Link from "next/link";

import BrainReflectedBanner from "@/components/plan/BrainReflectedBanner";
import BrandMemoryAside from "@/components/plan/BrandMemoryAside";
import FinalBriefPanel from "@/components/plan/FinalBriefPanel";
import FollowUpComposer from "@/components/plan/FollowUpComposer";
import PlanComparisonGrid from "@/components/plan/PlanComparisonGrid";
import PlanFeedbackControls from "@/components/plan/PlanFeedbackControls";
import PlanOptionFrame from "@/components/plan/PlanOptionFrame";
import PlanCard from "@/components/PlanCard"; // ★ 무수정 import (디자인 보존)
import ProgressStepper, { type StepperState } from "@/components/ProgressStepper";
import { DirectionApprovalCard } from "@/components/common/DirectionApprovalCard";
import { QuickInputCard } from "@/components/quick/QuickInputCard";
import { quickClarity } from "@/lib/clarity";
import {
  generate,
  generateMultiPlan,
  getPkmGraph,
  selectPlan,
  sendFeedback,
  startPlan,
  wizardStep,
} from "@/lib/api";
import type {
  CriticEvaluation,
  FeedbackEventType,
  MultiPlanEnvelope,
  Plan,
  RAGReference,
} from "@/lib/types";

type Phase = "intent" | "confirm" | "generating" | "result";

interface FlowDirection {
  text: string;
  clarity_score: number;
  revise_count: number;
}

const STEP_SEQUENCE: StepperState[] = [
  "intent",
  "rag",
  "planning",
  "critic",
  "complete",
];
const OPTIMISTIC_INTERVAL_MS = 4000;

/** Quick 위저드의 mock 방향 합성과 동일 — Phase 4+ P-005 실응답으로 교체 가능. */
function buildDirectionText(prompt: string, reviseCount: number): string {
  const base = prompt.trim().slice(0, 24) || "새 영상";
  if (reviseCount === 0) return `${base}을 주제로 짧은 정보형 영상 한 편`;
  const variations = ["스토리텔링", "리뷰형", "비교형"];
  return `${base}을 다룬 ${variations[(reviseCount - 1) % variations.length]} 영상 한 편`;
}

export default function NewFlowPage() {
  const [phase, setPhase] = useState<Phase>("intent");
  const [prompt, setPrompt] = useState("");
  const [direction, setDirection] = useState<FlowDirection | null>(null);
  const [planId, setPlanId] = useState<string | null>(null);
  const [envelope, setEnvelope] = useState<MultiPlanEnvelope | null>(null);
  const [selectedPlanId, setSelectedPlanId] = useState<string | null>(null);
  const [brainReflected, setBrainReflected] = useState<number | null>(null);
  const [stepIdx, setStepIdx] = useState(0);
  const [error, setError] = useState<string | null>(null);

  // 선택/피드백 상태 (ADR-030, /plan/[id]와 동일 — 결과 카드 상호작용).
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

  // 이어가기 스레드(결과 카드 후 추가 프롬프트로 새 묶음 누적).
  const [followUps, setFollowUps] = useState<
    { input: string; envelope: MultiPlanEnvelope }[]
  >([]);
  const [followUpBusy, setFollowUpBusy] = useState(false);
  const [followUpError, setFollowUpError] = useState<string | null>(null);

  const timerRef = useRef<ReturnType<typeof setInterval> | undefined>(undefined);
  const runningRef = useRef(false); // 이중 제출 가드

  const clearTimer = useCallback(() => {
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = undefined;
    }
  }, []);

  // 언마운트 시 타이머 정리(누수·stale setState 방지).
  useEffect(() => clearTimer, [clearTimer]);

  // 홈(/)에서 ?prompt= 로 넘어온 의도 계승 → 바로 확인 턴으로 (단일 흐름 진입점).
  useEffect(() => {
    if (typeof window === "undefined") return;
    const p = (new URLSearchParams(window.location.search).get("prompt") ?? "").trim();
    if (!p) return;
    setPrompt(p);
    setDirection({
      text: buildDirectionText(p, 0),
      clarity_score: quickClarity({ promptLen: p.length, clarified: false }),
      revise_count: 0,
    });
    setPhase("confirm");
  }, []);

  // ── intent → confirm: 의도 제출 시 mock 방향 + 명확도 계산(클라이언트, 무비용) ──
  const handleIntentSubmit = useCallback(() => {
    const text = prompt.trim();
    if (text.length === 0) return;
    setError(null);
    setDirection({
      text: buildDirectionText(text, 0),
      clarity_score: quickClarity({ promptLen: text.length, clarified: false }),
      revise_count: 0,
    });
    setPhase("confirm");
  }, [prompt]);

  // ── 확인 턴: 다시 생성(방향 재합성) ──
  const handleRegenerate = useCallback(() => {
    setDirection((prev) => {
      const nextCount = (prev?.revise_count ?? 0) + 1;
      return {
        text: buildDirectionText(prompt, nextCount),
        clarity_score: quickClarity({
          promptLen: prompt.trim().length,
          clarified: false,
        }),
        revise_count: nextCount,
      };
    });
  }, [prompt]);

  // ── confirm → generating → result: 기존 위저드 API로 3-plan 생성 ──
  const runGenerate = useCallback(
    async (directionText: string) => {
      if (runningRef.current) return; // 이중 제출 가드
      runningRef.current = true;
      setPhase("generating");
      setError(null);
      setStepIdx(1);
      clearTimer();
      timerRef.current = setInterval(() => {
        setStepIdx((i) => Math.min(i + 1, STEP_SEQUENCE.length - 2));
      }, OPTIMISTIC_INTERVAL_MS);

      try {
        const started = await startPlan(prompt);
        setPlanId(started.plan_id);
        await wizardStep(started.plan_id, "quick.initial", {
          user_input: prompt,
        });
        await wizardStep(started.plan_id, "quick.clarify", {
          extra: { skipped: true },
        });
        await wizardStep(started.plan_id, "quick.direction", {
          user_input: directionText,
        });
        const result = await generateMultiPlan(started.plan_id);
        clearTimer();
        if (result.ok) {
          setEnvelope(result.envelope);
          setStepIdx(STEP_SEQUENCE.length - 1);
          setPhase("result");
          if (typeof window !== "undefined") {
            window.setTimeout(
              () => window.scrollTo({ top: 0, behavior: "smooth" }),
              60,
            );
          }
          // "내 brain 반영" 신호(로그인+PKM>0) — 익명/실패는 graceful 미표시.
          getPkmGraph()
            .then((g) => {
              const count =
                (g.summary.personal ?? 0) + (g.summary.brand ?? 0);
              if (count > 0) setBrainReflected(count);
            })
            .catch(() => {});
        } else {
          setError(result.userMessage);
          setStepIdx(0);
          setPhase("confirm");
        }
      } catch (e) {
        clearTimer();
        setError(
          e instanceof Error
            ? e.message
            : "기획안 생성 중 오류가 발생했어요. 다시 시도해주세요.",
        );
        setStepIdx(0);
        setPhase("confirm");
      } finally {
        runningRef.current = false;
      }
    },
    [prompt, clearTimer],
  );

  // ── 카드 선택(로컬 표시) ──
  const handleSelect = useCallback((id: string) => {
    setSelectedPlanId(id);
  }, []);

  // ── 선택 저장 (backend /select, ADR-030) ──
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
        setActionError("선택을 저장하지 못했어요. 잠시 후 다시 시도해주세요.");
      } finally {
        setSelectBusy(false);
      }
    },
    [planId],
  );

  // ── like/dislike 피드백 (낙관적, 실패 시 롤백) ──
  const handleFeedback = useCallback(
    async (optionIndex: number, eventType: FeedbackEventType) => {
      if (!planId) return;
      setActionError(null);
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
        setActionError("피드백을 저장하지 못했어요. 잠시 후 다시 시도해주세요.");
      }
    },
    [planId],
  );

  // ── 반려 이유 제출 ──
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
        setActionError("반려를 저장하지 못했어요. 잠시 후 다시 시도해주세요.");
      }
    },
    [planId, rejectReason],
  );

  const handleToggleReject = useCallback((optionIndex: number) => {
    setRejectOpenIndex((prev) => {
      const next = prev === optionIndex ? null : optionIndex;
      if (next === null) setRejectReason("");
      return next;
    });
  }, []);

  // ── 이어가기: 선택 카드 방향을 이어 generate 재호출 → 스레드 누적 ──
  const handleFollowUp = useCallback(
    async (text: string) => {
      setFollowUpBusy(true);
      setFollowUpError(null);
      const allPlans: Plan[] = [
        ...(envelope?.body.plan_candidates ?? []),
        ...followUps.flatMap((f) => f.envelope.body.plan_candidates ?? []),
      ];
      const sel = allPlans.find((p) => p.plan_id === selectedPlanId);
      const contextual = sel
        ? `이전 기획안 "${sel.name}" (콘셉트: ${sel.concept})의 방향을 이어서, 다음 요청을 반영해줘: ${text}`
        : text;
      try {
        const result = await generate({ input: contextual });
        if (result.ok) {
          setFollowUps((prev) => [
            ...prev,
            { input: text, envelope: result.envelope as MultiPlanEnvelope },
          ]);
          if (typeof window !== "undefined") {
            window.setTimeout(
              () =>
                window.scrollTo({
                  top: document.body.scrollHeight,
                  behavior: "smooth",
                }),
              80,
            );
          }
        } else {
          setFollowUpError(
            result.userMessage ?? "이어서 생성하지 못했어요. 다시 시도해주세요.",
          );
        }
      } catch {
        setFollowUpError("이어서 생성하지 못했어요. 다시 시도해주세요.");
      } finally {
        setFollowUpBusy(false);
      }
    },
    [envelope, followUps, selectedPlanId],
  );

  const plans: Plan[] = envelope?.body.plan_candidates ?? [];
  const critic: CriticEvaluation | null | undefined =
    envelope?.body.critic_evaluation;
  const ragRefs: RAGReference[] = envelope?.body.rag_references ?? [];
  const projectId = envelope?.meta.project_id ?? null;
  const warnings = envelope?.validation.warnings ?? [];
  const recommendedIdx: number | null =
    typeof envelope?.body.recommended_plan_index === "number"
      ? envelope.body.recommended_plan_index
      : null;
  const selectedPlan: Plan | undefined = [
    ...plans,
    ...followUps.flatMap((f) => f.envelope.body.plan_candidates ?? []),
  ].find((p) => p.plan_id === selectedPlanId);

  const currentStep: StepperState = STEP_SEQUENCE[stepIdx] ?? "idle";
  const submitted = phase !== "intent";
  const isResult = phase === "result" && envelope && plans.length > 0;

  return (
    <main className="mx-auto w-full max-w-6xl px-4 py-6 sm:py-10 pb-32 flex flex-col gap-6">
      {/* 페이지 헤더 */}
      <header className="flex flex-col gap-1">
        <p className="text-xs font-semibold tracking-wider uppercase text-primary-600">
          새 영상 기획
        </p>
        <h1 className="font-display text-xl sm:text-2xl font-bold text-text-default">
          한 화면에서 기획 완성하기
        </h1>
        <p className="text-sm text-text-muted">
          의도를 적으면 → 이해를 확인하고 → 기획안 3개를 만들고 → 이어서 계속
          다듬을 수 있어요.
        </p>
      </header>

      {/* 1) 내 요청 요약 칩 (제출 후 유지 — 대화식) */}
      {submitted && (
        <section
          aria-label="내 요청"
          className="rounded-xl border-l-4 border-primary-500 border-y border-r border-border-default bg-bg-subtle px-4 py-3"
        >
          <p className="text-xs font-semibold text-text-muted mb-0.5">
            내 요청
          </p>
          <p className="text-sm text-text-default">{prompt}</p>
        </section>
      )}

      {/* 2) 의도 입력 (intent) */}
      {phase === "intent" && (
        <section className="flex flex-col gap-4">
          <QuickInputCard
            mode="initial_prompt"
            value={prompt}
            onChange={setPrompt}
            placeholder="예: 30대 직장인을 위한 재테크 정보 쇼츠, 유머러스하게 1분"
            ariaLabel="이번 영상 의도"
          />
          <div className="px-4">
            <button
              type="button"
              onClick={handleIntentSubmit}
              disabled={prompt.trim().length === 0}
              className={`w-full min-h-[44px] px-4 py-3 rounded-md text-sm font-semibold transition-colors ${
                prompt.trim().length > 0
                  ? "bg-primary-500 text-white hover:bg-primary-600 active:bg-primary-700 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary-500"
                  : "bg-neutral-200 text-text-muted cursor-not-allowed"
              }`}
              aria-label="이해 확인으로"
            >
              다음 — 이해 확인 ▶
            </button>
          </div>
        </section>
      )}

      {/* 3) 확인 턴 (confirm) — 명확도 배지 포함 */}
      {phase === "confirm" && direction && (
        <section className="flex flex-col gap-2">
          {error && (
            <p
              role="alert"
              aria-live="assertive"
              className="mx-4 rounded-md bg-error-50 border border-error-200 px-3 py-2 text-sm text-error-700"
            >
              {error}
            </p>
          )}
          <DirectionApprovalCard
            direction={direction}
            variant="minimal"
            onApprove={() => void runGenerate(direction.text)}
            onEditAndApprove={(edited) => {
              setDirection((prev) =>
                prev
                  ? {
                      ...prev,
                      text: edited,
                      clarity_score: quickClarity({
                        promptLen: prompt.trim().length,
                        clarified: false,
                        edited: true,
                      }),
                    }
                  : prev,
              );
              void runGenerate(edited);
            }}
            onRegenerate={handleRegenerate}
            ariaLabel="기획 방향 확인 (단일 흐름)"
          />
        </section>
      )}

      {/* 4) 생성 중 (generating) — 낙관적 진행 */}
      {phase === "generating" && (
        <section
          aria-live="polite"
          className="flex flex-col items-center gap-4 py-6"
        >
          {direction && (
            <p className="text-sm text-text-muted text-center">
              방향: <span className="text-text-default">{direction.text}</span>
            </p>
          )}
          <ProgressStepper currentStep={currentStep} />
          <p className="text-sm text-text-muted text-center leading-relaxed">
            AI가 영상기획안 3개를 만들고 있어요 (약 30~60초)
          </p>
        </section>
      )}

      {/* 5) 결과 (result) — ★ /plan/[id]와 동일 디자인·상호작용 재현 */}
      {isResult && envelope && (
        <>
          <section className="flex flex-col gap-2">
            <p className="text-xs font-semibold tracking-wider uppercase text-primary-600">
              기획안 {plans.length}개
            </p>
            <h2 className="font-display text-xl sm:text-2xl font-bold text-text-default">
              AI가 만든 영상 기획안 {plans.length}개
            </h2>
            <p className="text-sm text-text-muted">
              서로 다른 접근을 같은 기준으로 비교하고, 마음에 드는 기획안을
              선택하세요.
            </p>
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
          </section>

          <div className="grid grid-cols-1 gap-5 desktop:grid-cols-[minmax(0,1fr)_300px]">
            <PlanComparisonGrid label="기획안 후보 목록">
              {plans.map((plan, i) => (
                <PlanOptionFrame
                  key={plan.plan_id}
                  optionIndex={i}
                  total={plans.length}
                  planName={plan.name}
                  selected={selectedPlanId === plan.plan_id}
                  recommended={recommendedIdx === i}
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
                  <PlanCard plan={plan} />
                </PlanOptionFrame>
              ))}
            </PlanComparisonGrid>
            <BrandMemoryAside critic={critic} ragRefs={ragRefs} />
          </div>

          {actionError && (
            <p
              role="alert"
              aria-live="assertive"
              className="rounded-md bg-error-50 border border-error-200 px-3 py-2 text-sm text-error-700"
            >
              {actionError}
            </p>
          )}

          {/* 이어진 기획 스레드 (선택만 — /plan/[id] follow-up과 동일) */}
          {followUps.map((fu, fi) => {
            const fuPlans = fu.envelope.body.plan_candidates ?? [];
            return (
              <section
                key={`fu-${fi}`}
                aria-label={`이어진 기획 ${fi + 1}`}
                className="flex flex-col gap-3 border-t border-border-default pt-5"
              >
                <p className="text-sm text-text-muted">
                  💬 이어서:{" "}
                  <span className="font-medium text-text-default">
                    &ldquo;{fu.input}&rdquo;
                  </span>
                </p>
                <PlanComparisonGrid label={`이어진 기획안 ${fi + 1}`}>
                  {fuPlans.map((plan, i) => (
                    <PlanOptionFrame
                      key={plan.plan_id}
                      optionIndex={i}
                      total={fuPlans.length}
                      planName={plan.name}
                      selected={selectedPlanId === plan.plan_id}
                      recommended={false}
                      onSelect={() => handleSelect(plan.plan_id)}
                    >
                      <PlanCard plan={plan} />
                    </PlanOptionFrame>
                  ))}
                </PlanComparisonGrid>
              </section>
            );
          })}

          {/* 이어서 요청하기 (막다른길 제거) */}
          <FollowUpComposer
            onSubmit={(t) => void handleFollowUp(t)}
            busy={followUpBusy}
            selectedLabel={selectedPlan?.name ?? null}
            error={followUpError}
          />

          {/* 개발자 정보(warnings) — /plan/[id] 패리티 */}
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

          {/* 선택 저장 후 — 영상기획 브리프 + 다음 행동 CTA (/plan/[id] 패리티) */}
          {savedSelectedIndex !== null && plans[savedSelectedIndex] && (
            <FinalBriefPanel
              plan={plans[savedSelectedIndex]}
              actions={
                <div className="flex flex-col gap-2">
                  <h3 className="font-display text-sm font-semibold text-text-default">
                    다음 행동
                  </h3>
                  <Link
                    href="/brain"
                    className="flex items-center justify-between gap-3 min-h-[44px] rounded-lg border border-primary-300 bg-primary-50 px-4 py-3 text-sm font-medium text-primary-700 hover:bg-primary-100 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-1 focus-visible:outline-primary-500"
                  >
                    <span>🧠 내 brain에서 보기</span>
                    <span aria-hidden>›</span>
                  </Link>
                  <Link
                    href="/new/flow"
                    className="flex items-center justify-between gap-3 min-h-[44px] rounded-lg border border-border-default bg-surface px-4 py-3 text-sm font-medium text-text-default hover:bg-primary-50/60 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-1 focus-visible:outline-primary-500"
                  >
                    <span>✏️ 새 영상 기획 시작</span>
                    <span aria-hidden>›</span>
                  </Link>
                </div>
              }
            />
          )}
        </>
      )}

      {/* 하단 고정 CTA — 결과 단계에서만(선택 저장 확정, /plan/[id] 패리티) */}
      {isResult && (
        <footer className="fixed bottom-0 left-0 right-0 border-t border-border-default bg-surface p-4 z-10">
          <div className="mx-auto w-full max-w-2xl">
            <button
              type="button"
              disabled={!selectedPlanId || selectBusy}
              onClick={() => {
                const idx = plans.findIndex((p) => p.plan_id === selectedPlanId);
                if (idx >= 0) void handleConfirmSelect(idx);
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
      )}
    </main>
  );
}
