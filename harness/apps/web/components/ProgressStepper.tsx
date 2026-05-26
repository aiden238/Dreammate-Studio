"use client";

/**
 * Phase 1 Slice 7 — 4단계 생성 진행 스텝퍼
 *
 * 참조:
 *   - apps/web/design.md §22 (4-stage Generation Progress Stepper)
 *   - docs/contracts/error_response_contract.md §7 (단계별 에러 표시)
 *   - apps/web/component_map.md "GenerationProgressStepper"
 *
 * Phase 1 백엔드는 단일 동기 호출 (≈30~60s) 이므로 실제 SSE/폴링이 없다.
 * → 시각 단서 (현재 활성 단계 + 진행 캡션) 만 제공해서 사용자가
 *   "응답이 끊긴 게 아니라 처리 중" 임을 인지하게 한다.
 *
 * Phase 4+ SSE 가 들어오면 step 매핑만 외부에서 주입받으면 된다.
 */

import type { ReactNode } from "react";

export type Step = "intent" | "rag" | "planning" | "critic";
export type StepperState = "idle" | Step | "complete";
export type StepStatus = "pending" | "active" | "done" | "error";

export interface ProgressStepperProps {
  /**
   * 현재 단계. "idle" 은 시작 전, "complete" 는 모두 완료.
   * Phase 1 동안 동기 호출이므로 보통 "planning" 으로 고정해두고
   * 응답 받으면 "complete" 로 전환한다.
   */
  currentStep: StepperState;
  /**
   * 에러 발생 시 어떤 단계에서 멈췄는지 표시. errorAtStep 이 주어지면
   * 해당 단계는 "error" (✗ 빨강), 이전 단계는 "done", 이후는 "pending".
   */
  errorAtStep?: Step;
}

interface StepDef {
  key: Step;
  index: number;
  label: string;
  caption: string;
}

const STEPS: StepDef[] = [
  { key: "intent", index: 1, label: "의도 확인", caption: "입력을 이해하는 중" },
  { key: "rag", index: 2, label: "자료 검색", caption: "참고 자료를 찾는 중" },
  { key: "planning", index: 3, label: "기획안 생성", caption: "기획안을 만드는 중" },
  { key: "critic", index: 4, label: "품질 평가", caption: "결과를 점검하는 중" },
];

function getStepStatus(
  step: Step,
  current: StepperState,
  errorAtStep?: Step,
): StepStatus {
  // 에러 케이스 우선
  if (errorAtStep) {
    if (step === errorAtStep) return "error";
    const errIdx = STEPS.findIndex((s) => s.key === errorAtStep);
    const stepIdx = STEPS.findIndex((s) => s.key === step);
    if (stepIdx < errIdx) return "done";
    return "pending";
  }

  if (current === "idle") return "pending";
  if (current === "complete") return "done";

  const currentIdx = STEPS.findIndex((s) => s.key === current);
  const stepIdx = STEPS.findIndex((s) => s.key === step);
  if (stepIdx < currentIdx) return "done";
  if (stepIdx === currentIdx) return "active";
  return "pending";
}

function getActiveCaption(
  current: StepperState,
  errorAtStep?: Step,
): string {
  if (errorAtStep) {
    const def = STEPS.find((s) => s.key === errorAtStep);
    return def ? `${def.label} 단계에서 문제가 생겼어요` : "문제가 생겼어요";
  }
  if (current === "idle") return "준비 중";
  if (current === "complete") return "완료";
  const def = STEPS.find((s) => s.key === current);
  return def?.caption ?? "처리 중";
}

// ─── 시각 토큰 ─────────────────────────────────────────────────────────

interface CircleClasses {
  base: string;
  inner: ReactNode;
}

function circleClassesFor(status: StepStatus, index: number): CircleClasses {
  switch (status) {
    case "done":
      return {
        base: "bg-success-500 text-white border-success-500",
        inner: (
          <svg
            aria-hidden="true"
            viewBox="0 0 16 16"
            className="w-4 h-4"
            fill="none"
            stroke="currentColor"
            strokeWidth="2.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <polyline points="3 8 7 12 13 4" />
          </svg>
        ),
      };
    case "active":
      return {
        base:
          "bg-primary-500 text-white border-primary-500 motion-safe:animate-pulse",
        inner: <span className="text-xs font-bold">{index}</span>,
      };
    case "error":
      return {
        base: "bg-error-500 text-white border-error-500",
        inner: (
          <svg
            aria-hidden="true"
            viewBox="0 0 16 16"
            className="w-4 h-4"
            fill="none"
            stroke="currentColor"
            strokeWidth="2.5"
            strokeLinecap="round"
          >
            <line x1="4" y1="4" x2="12" y2="12" />
            <line x1="12" y1="4" x2="4" y2="12" />
          </svg>
        ),
      };
    case "pending":
    default:
      return {
        base: "bg-neutral-100 text-neutral-500 border-neutral-200",
        inner: <span className="text-xs font-semibold">{index}</span>,
      };
  }
}

function lineClassFor(rightStatus: StepStatus): string {
  if (rightStatus === "done") return "bg-success-500";
  if (rightStatus === "active") return "bg-primary-300";
  if (rightStatus === "error") return "bg-error-500";
  return "bg-neutral-200";
}

// ─── 컴포넌트 ──────────────────────────────────────────────────────────

export default function ProgressStepper({
  currentStep,
  errorAtStep,
}: ProgressStepperProps) {
  const ariaLabel = errorAtStep
    ? `진행 중 ${errorAtStep} 단계에서 오류 발생`
    : currentStep === "complete"
      ? "모든 단계 완료"
      : "기획안 생성 진행 상황";

  return (
    <section
      aria-label={ariaLabel}
      aria-live="polite"
      className="flex flex-col gap-3 rounded-md border border-neutral-200 bg-neutral-0 p-4"
    >
      <ol className="flex items-center justify-between gap-1">
        {STEPS.map((step, idx) => {
          const status = getStepStatus(step.key, currentStep, errorAtStep);
          const { base, inner } = circleClassesFor(status, step.index);
          const isLast = idx === STEPS.length - 1;
          // 라인은 "현재 step → 다음 step" 사이의 상태 = 다음 step 의 상태로 색칠
          const nextStatus = isLast
            ? null
            : getStepStatus(STEPS[idx + 1].key, currentStep, errorAtStep);

          return (
            <li
              key={step.key}
              className="flex-1 flex items-center min-w-0"
              aria-current={status === "active" ? "step" : undefined}
            >
              {/* circle + label */}
              <div className="flex flex-col items-center gap-1 min-w-0">
                <div
                  className={[
                    "w-7 h-7 rounded-full border-2 flex items-center justify-center transition-colors",
                    base,
                  ].join(" ")}
                  aria-hidden="true"
                >
                  {inner}
                </div>
                <span
                  className={[
                    "text-[10px] sm:text-xs font-medium leading-none text-center",
                    status === "active"
                      ? "text-primary-700"
                      : status === "done"
                        ? "text-success-700"
                        : status === "error"
                          ? "text-error-700"
                          : "text-neutral-500",
                  ].join(" ")}
                >
                  {step.label}
                </span>
              </div>
              {/* connector line */}
              {!isLast && nextStatus && (
                <div
                  className={[
                    "flex-1 h-0.5 mx-1 sm:mx-2 -mt-4 rounded transition-colors",
                    lineClassFor(nextStatus),
                  ].join(" ")}
                  aria-hidden="true"
                />
              )}
            </li>
          );
        })}
      </ol>

      <p
        className={[
          "text-xs sm:text-sm leading-relaxed",
          errorAtStep
            ? "text-error-700"
            : currentStep === "complete"
              ? "text-success-700"
              : "text-neutral-600",
        ].join(" ")}
      >
        {getActiveCaption(currentStep, errorAtStep)}
      </p>
    </section>
  );
}
