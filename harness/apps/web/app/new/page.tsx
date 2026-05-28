/**
 * Phase 3 Slice 5 — /new 진입점 (mode branching redirect).
 *
 * 사용자 컨텍스트 검사 → Discovery / Discovery from Step 3 / Quick 으로 redirect.
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
 * URL query override 지원:
 *   - /new?new=true   → user_new_project (Discovery 강제)
 *   - /new?quick=true → user_quick_force (Brand 있을 때만, 현재 mock에서는 fallthrough)
 *
 * Suspense 경계: useSearchParams() Next.js 14 SSG 제약 — Suspense wrap 필수 (csr-bailout 회피).
 */

'use client';

import { Suspense, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { resolveMode, getMockUserContext } from '@/lib/mode_branching';

function NewEntryInner() {
  const router = useRouter();
  const searchParams = useSearchParams();

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
    router.replace(result.redirectPath);
  }, [router, searchParams]);

  return <LoadingPlaceholder />;
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
