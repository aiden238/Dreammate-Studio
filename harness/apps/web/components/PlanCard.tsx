/**
 * Phase 1 Slice 6 — 기획안 카드 (단일 plan 표시)
 *
 * 참조: component_map.md "PlanOptionCard" (3개 비교 카드는 Phase 3에서)
 *       design.md §13 (Output Display Rules)
 *       output_schema.md §8.1 (Plan)
 *
 * Slice 6 단순화: 비교/선택/거절 액션 없음. 단일 카드 표시만.
 * Slice 7+ 에서 RegenerateButton / SavePlanButton 등 추가.
 */

import type { Plan } from "@/lib/types";

const APPROACH_LABEL_KO: Record<Plan["approach_label"], string> = {
  narrative: "서사형",
  informational: "정보 전달형",
  empathy: "공감형",
  experiment: "실험형",
  review: "리뷰형",
  other: "기타",
};

export interface PlanCardProps {
  plan: Plan;
}

export default function PlanCard({ plan }: PlanCardProps) {
  return (
    <article
      className="rounded-lg border border-neutral-200 bg-neutral-0 shadow-sm p-4 sm:p-6 flex flex-col gap-4"
      aria-labelledby={`plan-${plan.plan_id}-title`}
    >
      {/* Header: name + approach badge */}
      <header className="flex items-start justify-between gap-3 flex-wrap">
        <h2
          id={`plan-${plan.plan_id}-title`}
          className="text-lg sm:text-xl font-bold text-neutral-900 leading-snug"
        >
          {plan.name}
        </h2>
        <span
          className="inline-flex items-center rounded-sm bg-primary-50 text-primary-700 text-xs font-medium px-2 py-1"
          aria-label={`접근 방식: ${APPROACH_LABEL_KO[plan.approach_label]}`}
        >
          {APPROACH_LABEL_KO[plan.approach_label]}
        </span>
      </header>

      {/* Concept */}
      <p className="text-sm sm:text-base text-neutral-700 leading-relaxed">
        {plan.concept}
      </p>

      {/* Hook (강조 박스) */}
      <section
        className="rounded-md border-l-4 border-primary-500 bg-primary-50 px-3 py-3"
        aria-label="후킹 문장"
      >
        <p className="text-xs font-semibold text-primary-700 mb-1">
          후킹
        </p>
        <p className="text-base sm:text-lg text-neutral-900 leading-relaxed">
          {plan.hook}
        </p>
      </section>

      {/* Flow (numbered list) */}
      <section aria-label="영상 흐름">
        <h3 className="text-sm font-semibold text-neutral-900 mb-2">
          영상 흐름
        </h3>
        <ol className="flex flex-col gap-2">
          {plan.flow.map((beat) => (
            <li
              key={beat.beat_index}
              className="flex gap-3 rounded-md border border-neutral-200 bg-neutral-50 px-3 py-2"
            >
              <span className="flex-shrink-0 inline-flex items-center justify-center w-6 h-6 rounded-full bg-primary-500 text-white text-xs font-bold">
                {beat.beat_index + 1}
              </span>
              <div className="flex-1 min-w-0">
                <div className="flex items-baseline justify-between gap-2 flex-wrap">
                  <p className="text-sm font-medium text-neutral-900">
                    {beat.beat}
                  </p>
                  <span className="text-xs text-neutral-500 flex-shrink-0">
                    {beat.duration_sec}초
                  </span>
                </div>
                <p className="text-xs text-neutral-600 mt-1">
                  {beat.purpose}
                </p>
              </div>
            </li>
          ))}
        </ol>
      </section>

      {/* Pros / Risks */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {plan.pros && (
          <section
            className="rounded-md bg-success-50 px-3 py-2"
            aria-label="장점"
          >
            <h3 className="text-xs font-semibold text-success-700 mb-1">
              장점
            </h3>
            <p className="text-sm text-neutral-700 leading-relaxed">
              {plan.pros}
            </p>
          </section>
        )}
        {plan.risks && (
          <section
            className="rounded-md bg-warning-50 px-3 py-2"
            aria-label="리스크"
          >
            <h3 className="text-xs font-semibold text-warning-700 mb-1">
              리스크
            </h3>
            <p className="text-sm text-neutral-700 leading-relaxed">
              {plan.risks}
            </p>
          </section>
        )}
      </div>
    </article>
  );
}
