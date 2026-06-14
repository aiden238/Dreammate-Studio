"use client";

/**
 * Phase 30 Slice 6 — FinalBriefPanel (★ PlanCard 외부 wrapper, 표현 계층 전용)
 *
 * 정합:
 *   - design_reference/COMPONENT_MAPPING.md §6: PlanResultPageContent ▸ (선택완료 결과 표현)
 *   - design_reference/reference/final-output.html: 좌측 섹션 내비 + 기획요약(paper/book) 레이아웃 차용
 *   - design_reference/VISUAL_CONTRACT.md §6(서적 카드: 아이보리 종이 + Paperlogy 제목 + 본문 가독성)
 *
 * ★ 제품 경계 = 영상기획 **브리프**(제작 아님):
 *   - 선택완료(savedSelectedIndex)된 plan 의 **현 output_schema 가 실제 제공하는 필드만** 표시.
 *   - 브리프 슬롯(기획요약/흐름구성)은 실데이터가 있을 때만 노출.
 *   - reference 의 '대본/촬영체크리스트/업로드문구'(=제작 산출물)는 schema 에 없음
 *     → 하드코딩/목업 절대 금지. "준비중(영상 제작 단계)"로 graceful 안내만.
 *
 * 원칙:
 *   - PlanCard.tsx 무수정 — 본 컴포넌트는 page.tsx 의 선택완료 결과 표현 표현 계층만 교체.
 *   - 기능 0 변경: 다음 행동 CTA(Brain/새 영상/준비중)는 page.tsx 가 children(actions)으로 주입.
 *   - 섹션 내비는 aria-current + 색 외 라벨, role 보존, 44px 터치, focus-visible.
 *   - 주황 20% 제한: 활성 섹션/진행 표시에만 옅은 주황, 본문은 웜 paper/surface 그대로.
 */

import { useId, useMemo, useState } from "react";

import type { Plan } from "@/lib/types";

const APPROACH_LABEL_KO: Record<string, string> = {
  narrative: "내러티브",
  informational: "정보 전달",
  empathy: "공감",
  experiment: "실험",
  review: "리뷰",
  other: "기타",
};

export interface FinalBriefPanelProps {
  /** 선택 저장(savedSelectedIndex)된 기획안. 브리프 깊이의 실데이터 출처. */
  plan: Plan;
  /** page.tsx 가 주입하는 다음 행동 CTA(Brain/새 영상/준비중) — 기능 무변경. */
  actions?: React.ReactNode;
}

/** 한 섹션의 메타. available=false 이면 내비에 "준비중"으로 비활성 표시. */
interface BriefSection {
  key: string;
  label: string;
  /** 실데이터 존재 여부 — false 면 제작 단계 슬롯(준비중). */
  available: boolean;
}

export default function FinalBriefPanel({ plan, actions }: FinalBriefPanelProps) {
  const headingId = useId();

  // ── 브리프 깊이: 실제 schema 필드 유무 판정 (목업 금지 — 있는 것만 true) ──
  const hasBrief = Boolean(
    plan.concept || plan.hook || plan.target_audience || plan.tone || plan.cta,
  );
  const flowBeats = plan.flow ?? [];
  const hasFlow = flowBeats.length > 0;

  // 제작 단계 산출물(대본/촬영체크리스트/업로드문구)은 현 schema 에 없음 → 준비중.
  const sections: BriefSection[] = useMemo(
    () => [
      { key: "brief", label: "기획 요약", available: hasBrief },
      { key: "flow", label: "흐름 구성", available: hasFlow },
      // ↓ 영상 제작 단계 산출물 — schema 미제공(준비중, 하드코딩 금지)
      { key: "script", label: "최종 대본", available: false },
      { key: "shoot", label: "촬영 체크리스트", available: false },
      { key: "upload", label: "업로드 문구", available: false },
    ],
    [hasBrief, hasFlow],
  );

  const firstAvailable =
    sections.find((s) => s.available)?.key ?? sections[0].key;
  const [activeKey, setActiveKey] = useState<string>(firstAvailable);

  // 활성 섹션이 비가용이면(데이터 전무) brief 로 폴백 — 항상 무언가 보이게.
  const active =
    sections.find((s) => s.key === activeKey && s.available) ??
    sections.find((s) => s.available) ??
    null;

  return (
    <section
      aria-labelledby={headingId}
      className="flex flex-col gap-4 border-t border-border-default pt-5"
    >
      <header className="flex flex-col gap-1">
        <p className="text-xs font-semibold uppercase tracking-wider text-primary-600">
          Final Brief
        </p>
        <h2
          id={headingId}
          className="font-display text-base font-bold text-text-default"
        >
          선택한 방향을 영상기획 브리프로 정리했어요 🧠
        </h2>
        <p className="text-sm text-text-muted">
          이 방향이 내 brain에 쌓였어요. 브리프를 확인하고 다음 행동으로
          이어가세요.
        </p>
      </header>

      {/* 좌측 섹션 내비 + 우측 종이 본문 (final-output.html output-layout 차용) */}
      <div className="grid grid-cols-1 gap-4 desktop:grid-cols-[200px_minmax(0,1fr)]">
        {/* 섹션 내비 — 데이터 있는 섹션만 활성, 제작 슬롯은 "준비중" 비활성 */}
        <nav
          aria-label="브리프 섹션"
          className="flex flex-row flex-wrap gap-1 desktop:flex-col desktop:sticky desktop:top-6 desktop:self-start"
        >
          {sections.map((s) => {
            const isActive = active?.key === s.key;
            if (!s.available) {
              return (
                <span
                  key={s.key}
                  aria-disabled="true"
                  className="inline-flex min-h-[44px] items-center justify-between gap-2 rounded-lg px-3 py-2 text-left text-sm text-text-placeholder"
                >
                  <span>{s.label}</span>
                  <span className="text-xs">준비중</span>
                </span>
              );
            }
            return (
              <button
                key={s.key}
                type="button"
                aria-current={isActive ? "true" : undefined}
                onClick={() => setActiveKey(s.key)}
                className={`inline-flex min-h-[44px] items-center gap-2 rounded-lg px-3 py-2 text-left text-sm font-medium transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary-500 ${
                  isActive
                    ? "bg-primary-50 text-primary-700"
                    : "text-text-muted hover:bg-primary-50/60"
                }`}
              >
                {isActive && <span aria-hidden>▸</span>}
                <span>{s.label}</span>
              </button>
            );
          })}
        </nav>

        {/* 종이 본문 — 활성 섹션의 실데이터만 렌더 */}
        <article className="rounded-2xl border border-border-default bg-surface p-5 shadow-sm">
          {active?.key === "brief" && (
            <BriefBody plan={plan} />
          )}
          {active?.key === "flow" && <FlowBody beats={flowBeats} />}
          {!active && (
            <p className="text-sm text-text-muted">
              아직 표시할 브리프 내용이 없어요.
            </p>
          )}

          {/* 제작 단계 안내 — 산출물 하드코딩 대신 graceful 경계 안내 */}
          <p className="mt-5 border-t border-border-default pt-3 text-xs text-text-placeholder">
            대본·촬영 체크리스트·업로드 문구 등 영상 제작 단계 산출물은 준비중이에요.
            지금은 영상기획 브리프까지 제공해요.
          </p>
        </article>
      </div>

      {/* 다음 행동 CTA — page.tsx 가 주입(기능 무변경) */}
      {actions}
    </section>
  );
}

/** 기획 요약 본문 — 있는 필드만 렌더(목업 금지). */
function BriefBody({ plan }: { plan: Plan }) {
  const approachKo = APPROACH_LABEL_KO[plan.approach_label] ?? null;
  const rows: { label: string; value: string }[] = [];
  if (plan.concept) rows.push({ label: "컨셉", value: plan.concept });
  if (plan.target_audience)
    rows.push({ label: "타깃", value: plan.target_audience });
  if (plan.tone) rows.push({ label: "톤·무드", value: plan.tone });
  if (approachLabelVisible(approachKo, plan.approach_label))
    rows.push({ label: "접근", value: approachKo as string });
  if (plan.cta) rows.push({ label: "행동 유도", value: plan.cta });

  return (
    <div className="flex flex-col gap-3">
      <p className="text-xs font-semibold uppercase tracking-wider text-text-placeholder">
        Project Brief
      </p>
      <h3 className="font-display text-xl font-bold text-text-default">
        {plan.name}
      </h3>

      {plan.hook && (
        <p className="rounded-xl bg-bg-subtle px-4 py-3 font-editorial text-base leading-relaxed text-text-default">
          “{plan.hook}”
        </p>
      )}

      {rows.length > 0 && (
        <dl className="flex flex-col divide-y divide-border-default">
          {rows.map((r) => (
            <div key={r.label} className="flex flex-col gap-1 py-2.5">
              <dt className="text-xs text-text-muted">{r.label}</dt>
              <dd className="text-sm leading-relaxed text-text-default">
                {r.value}
              </dd>
            </div>
          ))}
        </dl>
      )}

      {!plan.hook && rows.length === 0 && (
        <p className="text-sm text-text-muted">
          요약할 기획 정보가 아직 없어요.
        </p>
      )}
    </div>
  );
}

/** 흐름 구성 본문 — flow 비트의 실데이터(beat/purpose/duration)만 렌더. */
function FlowBody({ beats }: { beats: Plan["flow"] }) {
  return (
    <div className="flex flex-col gap-3">
      <p className="text-xs font-semibold uppercase tracking-wider text-text-placeholder">
        Story Flow
      </p>
      <h3 className="font-display text-xl font-bold text-text-default">
        흐름 구성
      </h3>
      <ol className="flex flex-col gap-2">
        {beats.map((b, i) => (
          <li
            key={b.beat_index ?? i}
            className="grid grid-cols-[64px_minmax(0,1fr)] gap-3 border-b border-border-default pb-2.5 last:border-b-0"
          >
            <span className="font-display text-sm font-semibold text-text-muted tabular-nums">
              {typeof b.duration_sec === "number" ? `${b.duration_sec}초` : `#${i + 1}`}
            </span>
            <div className="flex flex-col gap-0.5">
              <span className="text-sm font-medium text-text-default">
                {b.beat}
              </span>
              {b.purpose && (
                <span className="text-xs text-text-muted">{b.purpose}</span>
              )}
              {b.visual && (
                <span className="text-xs text-text-placeholder">
                  화면: {b.visual}
                </span>
              )}
              {b.dialogue && (
                <span className="font-editorial text-xs text-text-muted">
                  “{b.dialogue}”
                </span>
              )}
              {b.caption && (
                <span className="text-xs text-text-placeholder">
                  자막: {b.caption}
                </span>
              )}
            </div>
          </li>
        ))}
      </ol>
    </div>
  );
}

/** approach_label 이 의미있는 한국어로 매핑됐고 "기타"가 아닐 때만 표시. */
function approachLabelVisible(
  approachKo: string | null,
  raw: string,
): boolean {
  return Boolean(approachKo) && raw !== "other";
}
