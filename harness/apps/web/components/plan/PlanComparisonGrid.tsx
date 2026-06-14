"use client";

/**
 * Phase 30 Slice 5 — PlanComparisonGrid (★ PlanCard 외부 wrapper, 표현 계층 전용)
 *
 * 정합:
 *   - design_reference/COMPONENT_MAPPING.md §6: PlanComparisonGrid ▸ PlanOptionFrame ▸ PlanCard
 *   - design_reference/VISUAL_CONTRACT.md §5(데스크톱 다열 / 모바일 1열)
 *   - reference/workspace.html `.plan-grid`(데스크톱 3열, 모바일 1열)
 *
 * 원칙:
 *   - 기능 0 변경: role="radiogroup" + 카드 단위 radio 는 기존 page.tsx 의미 그대로.
 *   - 데스크톱(≥1024px) 3열 비교, 모바일 1열 — 한 화면 한 행동(모바일) / 같은 기준 비교(데스크톱).
 *   - 본 컴포넌트는 레이아웃 컨테이너만 — 카드 내용·선택 상태는 children(PlanOptionFrame) 책임.
 */

import type { ReactNode } from "react";

export interface PlanComparisonGridProps {
  /** 비교 그룹 라벨(aria-label) */
  label: string;
  children: ReactNode;
}

export default function PlanComparisonGrid({
  label,
  children,
}: PlanComparisonGridProps) {
  return (
    <section
      aria-label={label}
      role="radiogroup"
      className="grid grid-cols-1 items-stretch gap-4 desktop:grid-cols-3"
    >
      {children}
    </section>
  );
}
