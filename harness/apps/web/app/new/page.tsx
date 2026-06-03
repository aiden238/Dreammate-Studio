/**
 * Phase 3 Slice 5 — /new 진입점 (mode branching).
 *
 * 사용자 컨텍스트 검사 → Discovery / Discovery from Step 3 / Quick 으로 안내.
 * mode_branching.md §0.1 분기 흐름 1:1 정합.
 *
 * 참조:
 *   - apps/web/mode_branching.md (Phase 2 yaml spec, read-only)
 *   - apps/web/lib/mode_branching.ts (Slice 5 TS 변환)
 *   - apps/web/page_map.md /new entry
 *   - docs/decisions/phase_3_mode_branching_middleware.md (ADR-013, page redirect over middleware)
 *
 * Phase 3 (현재): mock UserContext (brandsCount=0 → rule_new_user → /new/discovery/step/1).
 * Phase 5: Supabase Auth 도입 시 mock 제거 + getUserContext() 실 fetch (서버 컴포넌트 가능).
 *
 * URL query override 지원 (★ 기존 진입 계약 보존 — 즉시 redirect):
 *   - /new?new=true   → user_new_project (Discovery 강제, 즉시 이동)
 *   - /new?quick=true → user_quick_force (Brand 있을 때만; mock 에선 fallthrough → 추천 카드)
 *
 * Phase 18 S3 (additive): override 가 없으면 mode-selection 카드 화면을 보여준다.
 *   - 추천 모드(resolveMode 결과)를 강조 + Quick/Discovery 진입 + 신규 "주제 추천받기" 카드.
 *   - override 진입(?new/?quick)은 기존처럼 즉시 redirect (behavior-preserving).
 *
 * Suspense 경계: useSearchParams() Next.js 14 SSG 제약 — Suspense wrap 필수 (csr-bailout 회피).
 */

'use client';

import { Suspense, useEffect, useMemo, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import {
  resolveMode,
  getMockUserContext,
  type BranchingResult,
} from '@/lib/mode_branching';

function NewEntryInner() {
  const router = useRouter();
  const searchParams = useSearchParams();
  // override(?new/?quick) 진입은 기존처럼 즉시 redirect → 카드 화면 깜빡임 방지.
  const hasOverride =
    searchParams?.get('new') === 'true' || searchParams?.get('quick') === 'true';
  const [resolved, setResolved] = useState<BranchingResult | null>(null);

  useEffect(() => {
    // searchParams는 ReadonlyURLSearchParams (Next.js 14) — URLSearchParams 호환.
    const ctx = getMockUserContext(
      searchParams ? new URLSearchParams(searchParams.toString()) : undefined,
    );
    const result = resolveMode(ctx);
    // 분기 결과 로그 (Phase 4+ 관측성 시 structured log로 교체)
    // eslint-disable-next-line no-console
    console.info(
      '[mode_branching]',
      result.rule_id,
      '→',
      result.redirectPath,
      result.rationale,
    );
    if (hasOverride) {
      // override 진입 — 기존 계약 보존: 즉시 redirect.
      router.replace(result.redirectPath);
      return;
    }
    // override 없음 — mode-selection 카드 화면 노출 (추천 강조).
    setResolved(result);
  }, [router, searchParams, hasOverride]);

  if (hasOverride || !resolved) {
    return <LoadingPlaceholder />;
  }
  return <ModeSelection router={router} recommended={resolved} />;
}

interface ModeOption {
  key: 'quick' | 'discovery' | 'branding';
  title: string;
  desc: string;
  href: string;
  recommendedFor: BranchingResult['mode'][];
}

const MODE_OPTIONS: ModeOption[] = [
  {
    key: 'quick',
    title: '빠르게 한 편',
    desc: '의도만 한 줄 적으면 바로 기획안 3개를 만들어요.',
    href: '/new/quick',
    recommendedFor: ['quick'],
  },
  {
    key: 'discovery',
    title: '차근차근 만들기',
    desc: '브랜드·타깃부터 단계별로 함께 정리해요. (처음이라면 추천)',
    href: '/new/discovery/step/1',
    recommendedFor: ['discovery', 'discovery_from_step3'],
  },
  {
    key: 'branding',
    title: '주제 추천받기 / 모르겠어요',
    desc: '무엇을 찍을지 막막하면 몇 가지 질문으로 주제를 같이 찾아드려요.',
    href: '/new/branding',
    recommendedFor: [],
  },
];

function ModeSelection({
  router,
  recommended,
}: {
  router: ReturnType<typeof useRouter>;
  recommended: BranchingResult;
}) {
  const options = useMemo(() => MODE_OPTIONS, []);
  return (
    <main className="min-h-screen bg-bg-default flex flex-col">
      <header className="border-b border-border-default px-4 py-3 sticky top-0 bg-bg-default z-10">
        <div className="max-w-2xl mx-auto flex items-center justify-between">
          <button
            type="button"
            className="text-text-muted text-sm font-medium hover:text-text-default transition-colors duration-fast"
            onClick={() => router.back()}
            aria-label="뒤로 가기"
          >
            {'←'} back
          </button>
          <div className="text-text-muted text-sm font-medium">새 영상기획</div>
          <div className="w-12" aria-hidden="true" />
        </div>
      </header>

      <section className="px-4 py-6 max-w-2xl mx-auto w-full">
        <h1 className="text-3xl font-bold text-text-default mb-2">
          어떻게 시작할까요?
        </h1>
        <p className="text-sm text-text-muted">
          마음에 드는 방식을 골라주세요. 언제든 바꿀 수 있어요.
        </p>
      </section>

      <section className="flex-1 px-4 pb-10 max-w-2xl mx-auto w-full">
        <div
          role="group"
          aria-label="시작 방식 선택"
          className="flex flex-col gap-3"
        >
          {options.map((opt) => {
            const isRecommended = opt.recommendedFor.includes(recommended.mode);
            return (
              <button
                key={opt.key}
                type="button"
                onClick={() => router.push(opt.href)}
                className={`w-full text-left p-4 rounded-lg border transition-all duration-fast hover:bg-bg-subtle hover:scale-[1.01] focus:outline-none focus:border-border-focus focus:border-2 ${
                  isRecommended
                    ? 'bg-bg-subtle border-primary border-2'
                    : 'bg-surface border-border-default'
                }`}
                aria-label={`${opt.title}${isRecommended ? ' (추천)' : ''}`}
              >
                <div className="flex items-center gap-2 mb-1">
                  <span className="font-semibold text-lg text-text-default">
                    {opt.title}
                  </span>
                  {isRecommended && (
                    <span className="text-xs px-2 py-0.5 rounded-full bg-primary text-text-inverse font-medium">
                      추천
                    </span>
                  )}
                </div>
                <div className="text-sm text-text-muted leading-normal">
                  {opt.desc}
                </div>
              </button>
            );
          })}
        </div>
      </section>
    </main>
  );
}

function LoadingPlaceholder() {
  return (
    <main className="min-h-screen bg-bg-default flex items-center justify-center px-4">
      <div className="text-center">
        <div
          className="inline-block w-8 h-8 border-2 border-border-default border-t-primary rounded-full animate-spin mb-4"
          aria-hidden="true"
        />
        <div className="text-text-default text-sm font-medium">
          기획 준비 중...
        </div>
        <div className="mt-2 text-xs text-text-muted">
          사용자 컨텍스트 분석 후 적절한 흐름으로 안내합니다
        </div>
      </div>
    </main>
  );
}

export default function NewEntryPage() {
  return (
    <Suspense fallback={<LoadingPlaceholder />}>
      <NewEntryInner />
    </Suspense>
  );
}
