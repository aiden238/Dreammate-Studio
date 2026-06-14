"use client";

/**
 * Phase 30 Slice 5 — BrainReflectedBanner (★ PlanCard 외부 wrapper, 표현 계층 전용)
 *
 * 정합:
 *   - design_reference/COMPONENT_MAPPING.md §6: PlanResultPageContent ▸ BrainReflectedBanner
 *   - Phase 29 S5 "내 brain 반영" 신호(에이전트 느낌) — 기능/표시 조건 보존.
 *   - design_reference/VISUAL_CONTRACT.md §6(일반 패널) — 옅은 주황 강조(20% 한도 내 안내 배너).
 *
 * 원칙:
 *   - 표시 여부·count 는 page.tsx 의 brainReflected state 가 결정(여기는 표현 계층만).
 *   - count===null 이면 렌더 안 함(graceful — 미로그인/무PKM/실패).
 */

export interface BrainReflectedBannerProps {
  /** null 이면 미표시. 숫자면 반영된 brain 선호 개수. */
  count: number | null;
}

export default function BrainReflectedBanner({
  count,
}: BrainReflectedBannerProps) {
  if (count === null) return null;
  return (
    <div className="flex items-center gap-2 rounded-xl border border-primary-200 bg-primary-50 px-3 py-2 text-sm text-primary-700">
      <span aria-hidden>🧠</span>
      <span>내 brain의 선호 {count}개를 반영해 만들었어요.</span>
    </div>
  );
}
