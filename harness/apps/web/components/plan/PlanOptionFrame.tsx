"use client";

/**
 * Phase 30 Slice 5 — PlanOptionFrame (★ PlanCard 외부 wrapper, 표현 계층 전용)
 *
 * 정합:
 *   - design_reference/COMPONENT_MAPPING.md §6: PlanComparisonGrid ▸ PlanOptionFrame ▸ PlanCard
 *   - design_reference/VISUAL_CONTRACT.md §6(선택 카드: 주황 테두리 + 옅은 앰버 + 체크/라벨)
 *   - reference/workspace.html `.plan-card.selected`(주황 outline) 시각 의도
 *
 * 원칙:
 *   - PlanCard.tsx 무수정 — children 으로 받아 외곽 frame 만 입힘.
 *   - 기능 0 변경: radio role/aria-checked/tabIndex/onSelect/onKeyDown 은 page.tsx 의 값을 그대로 받음.
 *   - 선택을 색만으로 표현하지 않음 → "선택됨"/"AI 추천" 텍스트 배지 + 체크 아이콘 병행.
 *   - 주황 20% 제한: 주황은 선택 테두리/배지에만, 카드 본문은 PlanCard(웜 surface) 그대로.
 */

import type { ReactNode } from "react";

export interface PlanOptionFrameProps {
  optionIndex: number;
  total: number;
  /** PlanCard 의 plan.name — aria-label 구성용(표시는 PlanCard 내부가 담당). */
  planName: string;
  selected: boolean;
  recommended: boolean;
  onSelect: () => void;
  /** ★ 기존 PlanCard (무수정) */
  children: ReactNode;
  /** PlanFeedbackControls 등 카드 하단 액션 슬롯 */
  footer?: ReactNode;
}

export default function PlanOptionFrame({
  optionIndex: i,
  total,
  planName,
  selected,
  recommended,
  onSelect,
  children,
  footer,
}: PlanOptionFrameProps) {
  // 선택 우선: 선택 시 주황 ring + 옅은 앰버. 미선택·추천 시 success ring(주황과 구분).
  const stateClass = selected
    ? "ring-2 ring-primary-500 ring-offset-2 ring-offset-bg-default bg-primary-50/50"
    : recommended
      ? "ring-2 ring-success-500 ring-offset-2 ring-offset-bg-default"
      : "ring-1 ring-border-default hover:ring-primary-300";

  return (
    <div
      role="radio"
      aria-checked={selected}
      aria-label={`기획안 ${i + 1} / ${total} — ${planName}${
        recommended ? " (AI 추천)" : ""
      }`}
      data-recommended={recommended ? "true" : "false"}
      tabIndex={0}
      onClick={onSelect}
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          onSelect();
        }
      }}
      className={`relative flex h-full cursor-pointer flex-col rounded-2xl p-2 transition-shadow ${stateClass} focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary-500`}
    >
      {/* AI 추천 badge — wrapper 에만(PlanCard 무수정). 선택 시엔 선택 배지가 우선. */}
      {recommended && !selected && (
        <span
          className="absolute -top-2 left-4 z-10 inline-flex items-center gap-1 rounded-full bg-success-500 px-2 py-0.5 text-xs font-semibold text-white shadow"
        >
          <span aria-hidden>★</span> AI 추천
        </span>
      )}

      {/* 옵션 라벨 + 선택 상태(색 외 텍스트/체크 표시) */}
      <div className="mb-2 flex items-center gap-2 px-1 pt-1">
        <span className="text-xs font-medium text-text-muted">
          옵션 {i + 1} / {total}
        </span>
        {selected && (
          <span className="inline-flex items-center gap-1 rounded-full bg-primary-500 px-2 py-0.5 text-xs font-semibold text-white">
            <span aria-hidden>✓</span> 선택됨
          </span>
        )}
      </div>

      {/* ★ 기존 PlanCard (무수정) */}
      <div className="min-w-0">{children}</div>

      {footer}
    </div>
  );
}
