"use client";

/**
 * Phase 30 Slice 5 — BrandMemoryAside (★ PlanCard 외부 wrapper, 표현 계층 전용)
 *
 * 정합:
 *   - design_reference/COMPONENT_MAPPING.md §6: PlanResultPageContent ▸ BrandMemoryAside
 *   - design_reference/VISUAL_CONTRACT.md §6(일반 패널: 크림 surface + 웜 보더)
 *   - reference/workspace.html `.memory-panel`(평가 점수 score-row/score-bar + 참고자료 status)
 *
 * 원칙:
 *   - 목업 하드코딩 금지 — envelope 의 실데이터(critic.dimensions·overall_score·verdict, rag_references)만 표시.
 *   - 데이터 없으면 graceful 빈상태/숨김(기존 page.tsx 의 critic·rag 표시 조건과 동일 의미 보존).
 *   - 점수 막대는 색 외 수치(%) 텍스트 병행 — 색상-외-상태표시.
 *   - 데스크톱 우측 sticky aside, 모바일은 본문 아래로 흐름(부모 grid 가 1열로 전환).
 */

import type {
  CriticEvaluation,
  CriticVerdict,
  RAGReference,
} from "@/lib/types";

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

// 8 차원 canonical key → 한국어 라벨 (lib/types CriticScores 키 기준).
// 미정의 key 는 key 그대로 노출(graceful) — backend 차원 확장 대비.
const DIMENSION_LABEL_KO: Record<string, string> = {
  intent_fit: "의도 적합성",
  target_clarity: "타깃 명료성",
  hook_strength: "후킹 강도",
  message_clarity: "메시지 명료성",
  structure: "구조",
  feasibility: "실행 가능성",
  brand_consistency: "브랜드 일관성",
  differentiation: "차별성",
};

export interface BrandMemoryAsideProps {
  critic: CriticEvaluation | null | undefined;
  ragRefs: RAGReference[];
}

export default function BrandMemoryAside({
  critic,
  ragRefs,
}: BrandMemoryAsideProps) {
  const dimensions = critic?.dimensions ?? null;
  const dimEntries = dimensions ? Object.entries(dimensions) : [];

  return (
    <aside
      aria-label="Brand Memory"
      className="flex flex-col gap-4 rounded-2xl border border-border-default bg-surface p-4 shadow-sm desktop:sticky desktop:top-6 desktop:self-start"
    >
      <header className="flex items-center justify-between gap-2">
        <h2 className="font-display text-base font-bold text-text-default">
          Brand Memory
        </h2>
        {critic && (
          <span
            className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-semibold ${VERDICT_CLASS[critic.overall_verdict]}`}
          >
            <span aria-hidden>●</span>
            {VERDICT_LABEL[critic.overall_verdict]}
          </span>
        )}
      </header>

      {/* 종합 품질 점수 (canonical overall_score 0–1 → %) */}
      {critic && typeof critic.overall_score === "number" && (
        <div className="rounded-xl bg-bg-subtle px-3 py-2">
          <p className="text-xs text-text-muted">종합 품질</p>
          <p className="font-display text-2xl font-bold text-text-default">
            {Math.round(critic.overall_score * 100)}
            <span className="ml-0.5 text-sm font-medium text-text-muted">
              / 100
            </span>
          </p>
          {critic.revise_round > 0 && (
            <p className="text-xs text-text-muted">
              개선 {critic.revise_round}회 반영됨
            </p>
          )}
        </div>
      )}

      {/* 차원별 점수 (실데이터 — workspace.html score-row/score-bar 의도) */}
      {dimEntries.length > 0 && (
        <section aria-label="차원별 평가 점수" className="flex flex-col gap-2">
          <h3 className="text-xs font-semibold uppercase tracking-wider text-text-placeholder">
            차원별 점수
          </h3>
          <ul className="flex flex-col gap-2">
            {dimEntries.map(([key, value]) => {
              const pct = Math.max(
                0,
                Math.min(100, Math.round(value * 100)),
              );
              return (
                <li key={key} className="flex flex-col gap-1">
                  <div className="flex items-baseline justify-between gap-2">
                    <span className="text-xs text-text-muted">
                      {DIMENSION_LABEL_KO[key] ?? key}
                    </span>
                    <span className="text-xs font-semibold text-text-default tabular-nums">
                      {pct}
                    </span>
                  </div>
                  <div
                    className="h-1.5 w-full overflow-hidden rounded-full bg-bg-deep"
                    role="meter"
                    aria-valuenow={pct}
                    aria-valuemin={0}
                    aria-valuemax={100}
                    aria-label={`${DIMENSION_LABEL_KO[key] ?? key} ${pct}점`}
                  >
                    <span
                      className="block h-full rounded-full bg-primary-500"
                      style={{ width: `${pct}%` }}
                    />
                  </div>
                </li>
              );
            })}
          </ul>
        </section>
      )}

      {/* Critic blocking issues (있을 때만 — 기존 page.tsx 표시 의미 보존) */}
      {critic && critic.blocking_issues.length > 0 && (
        <section aria-label="개선 필요 항목">
          <h3 className="text-xs font-semibold uppercase tracking-wider text-text-placeholder">
            개선 필요
          </h3>
          <ul className="mt-1 list-disc list-inside text-xs text-text-muted">
            {critic.blocking_issues.map((issue, idx) => (
              <li key={idx}>{issue}</li>
            ))}
          </ul>
        </section>
      )}

      {/* 참고 자료 (rag_references 개수 — workspace.html status 라인 의도) */}
      <section
        aria-label="참고 자료"
        className="flex items-center gap-2 border-t border-border-default pt-3 text-xs text-text-muted"
      >
        <span aria-hidden>📚</span>
        <span>
          {ragRefs.length > 0
            ? `참고 자료 ${ragRefs.length}개를 활용했어요`
            : "참고 자료 없이 생성했어요"}
        </span>
      </section>
    </aside>
  );
}
