/**
 * Phase 3 Slice 4 — Quick Mode Step 1 (initial prompt) page.
 *
 * 흐름: 짧은 프롬프트 입력 → /new/quick/clarify (Step 2, follow-up 필요 시)
 *                       → /new/quick/direction (Step 3, follow-up 불필요 시)
 *
 * 참조:
 *   - apps/web/quick_flow.md §1
 *   - apps/web/page_map.md /new/quick
 *   - apps/web/wireframes/quick_short.md Step 1
 *
 * Slice 4 단독: needs_clarification 판정 mock (initialPrompt.length < 20 → clarify 진입).
 * Phase 4+: POST /api/v1/quick/start (output_schema §7) 실 호출로 교체.
 */

'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { QuickInputCard } from '@/components/quick/QuickInputCard';
import {
  saveQuickStep,
  loadQuickStep,
  type QuickStep1State,
} from '@/lib/quick_state';

const MAX_LEN = 300;

export default function QuickStep1Page() {
  const router = useRouter();
  const [prompt, setPrompt] = useState<string>('');

  // session storage에서 이전 state 복원 (back navigation 시 보존)
  useEffect(() => {
    const saved = loadQuickStep<QuickStep1State>(1);
    if (saved?.initialPrompt) {
      setPrompt(saved.initialPrompt);
    }
  }, []);

  const handleNext = () => {
    const trimmed = prompt.trim();
    if (!trimmed) return;
    const state: QuickStep1State = { initialPrompt: trimmed };
    saveQuickStep<QuickStep1State>(1, state);

    // Slice 4 mock 판정:
    //   < 20자 → 정보 부족 가능성 ↑ → clarify 진입
    //   ≥ 20자 → 충분 → direction 바로 진입
    // Phase 4 실 endpoint에서 AI 판정 결과로 교체.
    if (trimmed.length < 20) {
      router.push('/new/quick/clarify');
    } else {
      router.push('/new/quick/direction');
    }
  };

  const ctaDisabled = prompt.trim().length === 0 || prompt.length > MAX_LEN;

  return (
    <main className="min-h-screen bg-bg-default flex flex-col">
      {/* Header (BreadcrumbBrandPath placeholder — Phase 4+ 실 컨텍스트 합류) */}
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
          <div className="text-text-muted text-sm font-medium">Quick</div>
          <div className="w-12" aria-hidden="true" />
        </div>
      </header>

      {/* Title section */}
      <section className="px-4 py-6 max-w-2xl mx-auto w-full">
        <p className="text-xs text-text-muted mb-2" aria-label="현재 컨텍스트">
          Brand A · Series B
        </p>
        <h1 className="text-3xl font-bold text-text-default mb-2">
          이번엔 어떤 영상을?
        </h1>
        <p className="text-sm text-text-muted">
          짧게 의도만 입력하면 돼요.
        </p>
      </section>

      {/* Input */}
      <section className="flex-1 pb-32">
        <QuickInputCard
          mode="initial_prompt"
          value={prompt}
          onChange={setPrompt}
          maxLength={MAX_LEN}
        />
      </section>

      {/* Sticky bottom CTA */}
      <footer className="fixed bottom-0 left-0 right-0 border-t border-border-default bg-bg-default px-4 py-3 safe-area">
        <div className="max-w-2xl mx-auto">
          <button
            type="button"
            disabled={ctaDisabled}
            onClick={handleNext}
            className="w-full py-3 rounded-md font-semibold text-text-inverse bg-primary hover:bg-primary-hover active:bg-primary-pressed disabled:bg-primary-disabled disabled:cursor-not-allowed transition-colors duration-fast"
            aria-label="다음 단계로 진행"
          >
            {ctaDisabled ? '의도를 입력해주세요' : '다음 ▶'}
          </button>
        </div>
      </footer>
    </main>
  );
}
