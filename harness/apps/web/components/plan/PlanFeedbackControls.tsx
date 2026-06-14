"use client";

/**
 * Phase 30 Slice 5 — PlanFeedbackControls (★ PlanCard 외부 wrapper, 표현 계층 전용)
 *
 * 정합:
 *   - design_reference/COMPONENT_MAPPING.md §6: PlanResultPageContent ▸ PlanFeedbackControls
 *   - design_reference/VISUAL_CONTRACT.md §6(선택 카드)·§7(CTA)·§3(주황 20% 제한)
 *   - reference/workspace.html `.plan-actions`(선택·수정·거절) 시각 의도
 *
 * 원칙:
 *   - 기능 0 변경: page.tsx 의 핸들러(onConfirmSelect/onFeedback/onToggleReject/onSubmitReject)·
 *     상태(savedSelectedIndex/feedbackByIndex/rejectOpenIndex/rejectReason/selectBusy)를 그대로 prop 으로 받음.
 *   - ADR-030 의 액션·낙관적 UI·에러 경로는 page.tsx 에 그대로 둠(여기는 표현 계층만).
 *   - PlanCard.tsx 무수정 — 본 컴포넌트는 PlanCard 외부에서만 렌더.
 *   - 색상-외-상태표시(텍스트/aria-pressed/aria-expanded) 유지, 44px 터치 영역, focus-visible.
 *
 * 시각:
 *   - 평가 점수(있을 때만): 종이 위 score-row(라벨 + 막대 + 수치) — workspace.html `.score-row/.score-bar`.
 *   - 액션 버튼: 주황 primary(이 안 선택) + 웜 보더 secondary(좋아요/별로예요/반려).
 */

import type { FeedbackEventType } from "@/lib/types";

export interface PlanFeedbackControlsProps {
  optionIndex: number;
  // 상태(page.tsx 소유 — 표시용으로만 전달)
  savedSelectedIndex: number | null;
  selectBusy: boolean;
  feedback: FeedbackEventType | undefined;
  rejectOpen: boolean;
  rejectReason: string;
  // 핸들러(page.tsx 소유 — 기능 0 변경)
  onConfirmSelect: (optionIndex: number) => void;
  onFeedback: (optionIndex: number, eventType: FeedbackEventType) => void;
  onToggleReject: (optionIndex: number) => void;
  onSubmitReject: (optionIndex: number) => void;
  onRejectReasonChange: (value: string) => void;
}

const ACTION_BTN =
  "inline-flex items-center justify-center min-h-[44px] px-3 py-2 rounded-md text-sm font-medium border transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary-500";

export default function PlanFeedbackControls({
  optionIndex: i,
  savedSelectedIndex,
  selectBusy,
  feedback,
  rejectOpen,
  rejectReason,
  onConfirmSelect,
  onFeedback,
  onToggleReject,
  onSubmitReject,
  onRejectReasonChange,
}: PlanFeedbackControlsProps) {
  // wrapper(radio) onClick/keydown 버블링 차단 — 액션이 카드 선택을 트리거하지 않도록.
  return (
    <div
      className="mt-3 flex flex-col gap-2"
      onClick={(e) => e.stopPropagation()}
      onKeyDown={(e) => e.stopPropagation()}
    >
      <div className="flex flex-wrap items-center gap-2">
        <button
          type="button"
          disabled={selectBusy}
          onClick={() => onConfirmSelect(i)}
          aria-label={`옵션 ${i + 1} 이 안 선택`}
          className={`inline-flex items-center justify-center min-h-[44px] px-3 py-2 rounded-md text-sm font-semibold transition-colors ${
            savedSelectedIndex === i
              ? "bg-primary-600 text-white"
              : "bg-primary-500 text-white hover:bg-primary-600 active:bg-primary-700"
          } disabled:opacity-50 disabled:cursor-not-allowed focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary-500`}
        >
          {savedSelectedIndex === i ? "선택 저장됨" : "이 안 선택"}
        </button>

        <button
          type="button"
          aria-pressed={feedback === "like"}
          aria-label={`옵션 ${i + 1} 좋아요`}
          onClick={() => onFeedback(i, "like")}
          className={`${ACTION_BTN} ${
            feedback === "like"
              ? "border-success-500 bg-success-50 text-success-700"
              : "border-neutral-300 text-neutral-700 hover:bg-primary-50/60"
          }`}
        >
          <span aria-hidden>👍</span>
          <span className="ml-1">좋아요</span>
        </button>

        <button
          type="button"
          aria-pressed={feedback === "dislike"}
          aria-label={`옵션 ${i + 1} 별로예요`}
          onClick={() => onFeedback(i, "dislike")}
          className={`${ACTION_BTN} ${
            feedback === "dislike"
              ? "border-warning-500 bg-warning-50 text-warning-700"
              : "border-neutral-300 text-neutral-700 hover:bg-primary-50/60"
          }`}
        >
          <span aria-hidden>👎</span>
          <span className="ml-1">별로예요</span>
        </button>

        <button
          type="button"
          aria-expanded={rejectOpen}
          aria-label={`옵션 ${i + 1} 반려 이유 입력`}
          onClick={() => onToggleReject(i)}
          className={`${ACTION_BTN} ${
            feedback === "reject"
              ? "border-error-500 bg-error-50 text-error-700"
              : "border-neutral-300 text-neutral-700 hover:bg-primary-50/60"
          }`}
        >
          {feedback === "reject" ? "반려됨" : "반려"}
        </button>
      </div>

      {/* 반려 이유 입력 (inline textarea — 해당 카드에서만 노출) */}
      {rejectOpen && (
        <div className="flex flex-col gap-2 rounded-md border border-border-default bg-surface px-3 py-3">
          <label
            htmlFor={`reject-reason-${i}`}
            className="text-xs font-semibold text-text-default"
          >
            반려 이유 (선택 입력)
          </label>
          <textarea
            id={`reject-reason-${i}`}
            value={rejectReason}
            onChange={(e) => onRejectReasonChange(e.target.value)}
            maxLength={2000}
            rows={3}
            placeholder="이 기획안이 맞지 않은 이유를 적어주세요 (선택)"
            className="w-full rounded-md border border-border-default bg-neutral-0 px-2 py-1.5 text-sm text-text-default placeholder:text-text-placeholder focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-1 focus-visible:outline-primary-500"
          />
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => onSubmitReject(i)}
              className="inline-flex items-center justify-center min-h-[44px] px-3 py-2 rounded-md bg-error-500 text-white text-sm font-semibold hover:bg-error-700 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-error-500"
            >
              반려 제출
            </button>
            <button
              type="button"
              onClick={() => onToggleReject(i)}
              className="inline-flex items-center justify-center min-h-[44px] px-3 py-2 rounded-md border border-border-default text-text-default text-sm font-medium hover:bg-primary-50/60"
            >
              취소
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
