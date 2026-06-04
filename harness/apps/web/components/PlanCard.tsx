/**
 * Phase 1 Slice 7 — 기획안 카드 (단일 plan 표시)
 *
 * 참조: component_map.md "PlanOptionCard" (3개 비교 카드는 Phase 3에서)
 *       design.md §13 (Output Display Rules)
 *       output_schema.md §8.1 (Plan)
 *
 * Slice 7 보강:
 *   - approach_label 배지 색상 (narrative/informational/empathy/experiment/review/other)
 *   - flow 의 duration_sec 합계 표시
 *
 * 비교/선택/거절 액션은 Phase 3 (Discovery + 3-plan 비교) 에서.
 */

import type { ApproachLabel, Plan } from "@/lib/types";

const APPROACH_LABEL_KO: Record<ApproachLabel, string> = {
  narrative: "서사형",
  informational: "정보 전달형",
  empathy: "공감형",
  experiment: "실험형",
  review: "리뷰형",
  other: "기타",
};

/**
 * approach 유형별 톤. (color-only 분기 금지 원칙은 텍스트가 함께 있어 OK.)
 */
const APPROACH_BADGE_CLASS: Record<ApproachLabel, string> = {
  narrative: "bg-info-50 text-info-700",
  informational: "bg-neutral-100 text-neutral-700",
  empathy: "bg-primary-50 text-primary-700",
  experiment: "bg-warning-50 text-warning-700",
  review: "bg-success-50 text-success-700",
  other: "bg-neutral-100 text-neutral-700",
};

export interface PlanCardProps {
  plan: Plan;
}

export default function PlanCard({ plan }: PlanCardProps) {
  const totalDurationSec = plan.flow.reduce(
    (sum, beat) => sum + (beat.duration_sec ?? 0),
    0,
  );
  const totalMin = Math.floor(totalDurationSec / 60);
  const totalSec = totalDurationSec % 60;
  const totalDurationLabel =
    totalMin > 0
      ? `${totalMin}분 ${totalSec}초`
      : `${totalDurationSec}초`;

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
          className={`inline-flex items-center rounded-sm text-xs font-medium px-2 py-1 ${APPROACH_BADGE_CLASS[plan.approach_label]}`}
          aria-label={`접근 방식: ${APPROACH_LABEL_KO[plan.approach_label]}`}
        >
          {APPROACH_LABEL_KO[plan.approach_label]}
        </span>
      </header>

      {/* Concept */}
      <p className="text-sm sm:text-base text-neutral-700 leading-relaxed">
        {plan.concept}
      </p>

      {/* rich: 타깃·톤 메타 (값 있을 때만 — 읽기 전용 텍스트) */}
      {(plan.target_audience || plan.tone) && (
        <p
          className="text-xs text-neutral-500 -mt-1 flex flex-wrap gap-x-2 gap-y-1"
          aria-label="타깃과 톤"
        >
          {plan.target_audience && (
            <span>
              <span className="font-semibold text-neutral-600">타깃</span>{" "}
              {plan.target_audience}
            </span>
          )}
          {plan.target_audience && plan.tone && (
            <span aria-hidden="true">·</span>
          )}
          {plan.tone && (
            <span>
              <span className="font-semibold text-neutral-600">톤</span>{" "}
              {plan.tone}
            </span>
          )}
        </p>
      )}

      {/* Hook (강조 박스) */}
      <section
        className="rounded-md border-l-4 border-primary-500 bg-primary-50 px-3 py-3"
        aria-label="후킹 문장"
      >
        <p className="text-xs font-semibold text-primary-700 mb-1">후킹</p>
        <p className="text-base sm:text-lg text-neutral-900 leading-relaxed">
          {plan.hook}
        </p>
      </section>

      {/* rich: 대안 후크 (값 있을 때만 — 읽기 전용 텍스트) */}
      {plan.hook_variants && plan.hook_variants.length > 0 && (
        <section aria-label="다른 후크 후보">
          <h3 className="text-xs font-semibold text-neutral-900 mb-2">
            다른 후크
          </h3>
          <ul className="flex flex-col gap-2">
            {plan.hook_variants.map((variant, i) => (
              <li
                key={i}
                className="rounded-md border border-neutral-200 bg-neutral-50 px-3 py-2 text-sm text-neutral-700 leading-relaxed"
              >
                {variant}
              </li>
            ))}
          </ul>
        </section>
      )}

      {/* Flow (numbered list) */}
      <section aria-label="영상 흐름">
        <div className="flex items-baseline justify-between gap-2 mb-2">
          <h3 className="text-sm font-semibold text-neutral-900">영상 흐름</h3>
          <span
            className="text-xs text-neutral-500"
            aria-label={`총 길이 ${totalDurationLabel}`}
          >
            총 {totalDurationLabel} · {plan.flow.length}개 비트
          </span>
        </div>
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
                <p className="text-xs text-neutral-600 mt-1">{beat.purpose}</p>
                {/* rich: beat 상세 (값 있을 때만 — 화면/대사/자막 읽기 전용) */}
                {(beat.visual || beat.dialogue || beat.caption) && (
                  <dl className="mt-2 flex flex-col gap-1 border-t border-neutral-200 pt-2">
                    {beat.visual && (
                      <div className="flex gap-2 text-xs">
                        <dt className="flex-shrink-0 font-semibold text-neutral-500">
                          화면
                        </dt>
                        <dd className="text-neutral-700 leading-relaxed">
                          {beat.visual}
                        </dd>
                      </div>
                    )}
                    {beat.dialogue && (
                      <div className="flex gap-2 text-xs">
                        <dt className="flex-shrink-0 font-semibold text-neutral-500">
                          대사
                        </dt>
                        <dd className="text-neutral-700 leading-relaxed">
                          {beat.dialogue}
                        </dd>
                      </div>
                    )}
                    {beat.caption && (
                      <div className="flex gap-2 text-xs">
                        <dt className="flex-shrink-0 font-semibold text-neutral-500">
                          자막
                        </dt>
                        <dd className="text-neutral-700 leading-relaxed">
                          {beat.caption}
                        </dd>
                      </div>
                    )}
                  </dl>
                )}
              </div>
            </li>
          ))}
        </ol>
      </section>

      {/* rich: 촬영 샷 / B-roll (값 있을 때만 — 읽기 전용 가이드 텍스트) */}
      {plan.shots && plan.shots.length > 0 && (
        <section aria-label="촬영 샷">
          <h3 className="text-sm font-semibold text-neutral-900 mb-2">
            촬영 샷
          </h3>
          <ul className="flex flex-col gap-1.5 list-disc pl-5">
            {plan.shots.map((shot, i) => (
              <li
                key={i}
                className="text-sm text-neutral-700 leading-relaxed"
              >
                {shot}
              </li>
            ))}
          </ul>
        </section>
      )}

      {/* rich: 썸네일 / 제목 후보 (값 있을 때만 — 읽기 전용 텍스트) */}
      {(plan.thumbnail ||
        (plan.title_candidates && plan.title_candidates.length > 0)) && (
        <section
          className="rounded-md border border-neutral-200 bg-neutral-50 px-3 py-3 flex flex-col gap-3"
          aria-label="썸네일과 제목 후보"
        >
          {plan.thumbnail && (
            <div>
              <h3 className="text-xs font-semibold text-neutral-900 mb-1">
                썸네일
              </h3>
              <p className="text-sm text-neutral-700 leading-relaxed">
                {plan.thumbnail}
              </p>
            </div>
          )}
          {plan.title_candidates && plan.title_candidates.length > 0 && (
            <div>
              <h3 className="text-xs font-semibold text-neutral-900 mb-1">
                제목 후보
              </h3>
              <ul className="flex flex-col gap-1 list-disc pl-5">
                {plan.title_candidates.map((title, i) => (
                  <li
                    key={i}
                    className="text-sm text-neutral-700 leading-relaxed"
                  >
                    {title}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </section>
      )}

      {/* rich: CTA (값 있을 때만 — 읽기 전용 텍스트) */}
      {plan.cta && (
        <section
          className="rounded-md border-l-4 border-neutral-300 bg-neutral-50 px-3 py-2"
          aria-label="콜 투 액션"
        >
          <h3 className="text-xs font-semibold text-neutral-600 mb-1">CTA</h3>
          <p className="text-sm text-neutral-700 leading-relaxed">{plan.cta}</p>
        </section>
      )}

      {/* rich: 참고 스타일 / 레퍼런스 (값 있을 때만 — 읽기 전용 텍스트) */}
      {plan.references && plan.references.length > 0 && (
        <section aria-label="참고 스타일">
          <h3 className="text-sm font-semibold text-neutral-900 mb-2">
            참고 스타일
          </h3>
          <ul className="flex flex-col gap-1.5 list-disc pl-5">
            {plan.references.map((ref, i) => (
              <li
                key={i}
                className="text-sm text-neutral-700 leading-relaxed"
              >
                {ref}
              </li>
            ))}
          </ul>
        </section>
      )}

      {/* rich: 길이 변형 (값 있을 때만 — 읽기 전용 텍스트) */}
      {plan.length_variants && plan.length_variants.length > 0 && (
        <section aria-label="길이 변형">
          <h3 className="text-sm font-semibold text-neutral-900 mb-2">
            길이 변형
          </h3>
          <ul className="flex flex-wrap gap-2">
            {plan.length_variants.map((variant, i) => (
              <li
                key={i}
                className="inline-flex items-center rounded-sm bg-neutral-100 text-neutral-700 text-xs font-medium px-2 py-1"
              >
                {variant}
              </li>
            ))}
          </ul>
        </section>
      )}

      {/* director: 후크 시스템 (값 있을 때만 — Phase 15) */}
      {plan.hook_system && plan.hook_system.length > 0 && (
        <section aria-label="후크 시스템">
          <h3 className="text-sm font-semibold text-neutral-900 mb-2">
            후크 시스템 (첫 후크 + 재후크)
          </h3>
          <ul className="space-y-1.5">
            {plan.hook_system.map((h, i) => (
              <li
                key={i}
                className="text-sm text-neutral-700 leading-relaxed pl-3 border-l-2 border-neutral-200"
              >
                {h}
              </li>
            ))}
          </ul>
        </section>
      )}

      {/* director: 리텐션 설계 (값 있을 때만 — Phase 15) */}
      {plan.retention_architecture && (
        <section aria-label="리텐션 설계">
          <h3 className="text-sm font-semibold text-neutral-900 mb-2">
            리텐션 설계
          </h3>
          <p className="text-sm text-neutral-700 leading-relaxed">
            {plan.retention_architecture}
          </p>
        </section>
      )}

      {/* director: 씬 분해 (값 있을 때만 — Phase 15, 기획 브리프 수준) */}
      {plan.scene_breakdown && plan.scene_breakdown.length > 0 && (
        <section aria-label="씬 분해">
          <h3 className="text-sm font-semibold text-neutral-900 mb-2">
            씬 분해
          </h3>
          <ol className="space-y-2">
            {plan.scene_breakdown.map((scene, i) => (
              <li
                key={i}
                className="rounded-md bg-neutral-50 px-3 py-2 text-sm leading-relaxed"
              >
                <p className="font-medium text-neutral-900">
                  {i + 1}. {scene.scene_intent}
                </p>
                <p className="text-neutral-600 mt-0.5">
                  감정: {scene.viewer_emotion} · 리텐션: {scene.retention_device}
                </p>
                <p className="text-neutral-500 text-xs mt-0.5">
                  근거: {scene.why_this_works}
                </p>
                {scene.fallback_scene && (
                  <p className="text-neutral-500 text-xs mt-0.5">
                    대안: {scene.fallback_scene}
                  </p>
                )}
                {(scene.brand_signal || scene.commercial_signal) && (
                  <p className="text-neutral-500 text-xs mt-0.5">
                    {scene.brand_signal && <>브랜드: {scene.brand_signal}</>}
                    {scene.brand_signal && scene.commercial_signal && " · "}
                    {scene.commercial_signal && <>상업: {scene.commercial_signal}</>}
                  </p>
                )}
              </li>
            ))}
          </ol>
        </section>
      )}

      {/* commercial_viral: 상업·전략 슬롯 (값 있을 때만 — Phase 20) */}
      {(plan.market_context ||
        plan.audience_psychology ||
        plan.brand_positioning ||
        plan.commercial_conversion ||
        plan.platform_packaging ||
        plan.production_feasibility ||
        plan.measurement_plan) && (
        <section aria-label="상업·전략 브리프">
          <h3 className="text-sm font-semibold text-neutral-900 mb-2">
            상업·전략 브리프
          </h3>
          <dl className="space-y-1.5 text-sm">
            {(
              [
                ["시장 맥락", plan.market_context],
                ["시청자 심리", plan.audience_psychology],
                ["브랜드 포지셔닝", plan.brand_positioning],
                ["전환 설계", plan.commercial_conversion],
                ["플랫폼 패키징", plan.platform_packaging],
                ["제작 실현성", plan.production_feasibility],
                ["측정 계획", plan.measurement_plan],
              ] as const
            ).map(([label, value]) =>
              value ? (
                <div
                  key={label}
                  className="rounded-md bg-neutral-50 px-3 py-2"
                >
                  <dt className="text-xs font-medium text-neutral-500">
                    {label}
                  </dt>
                  <dd className="text-neutral-700 leading-relaxed mt-0.5">
                    {value}
                  </dd>
                </div>
              ) : null,
            )}
          </dl>
          <p className="text-neutral-400 text-xs mt-2">
            ※ 전략 기획 브리프 — 조회수·성과 보장이 아닌 패턴·근거 기반 제안.
            시장·심리는 실데이터 없으면 추정.
          </p>
        </section>
      )}

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
