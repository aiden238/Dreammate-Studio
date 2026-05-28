/**
 * Phase 3 Slice 4 — Quick Mode Step 2 (follow-up question) page.
 *
 * 흐름: 부족 정보 1~2 질문 답변 → /new/quick/direction
 *      또는 skip → /new/quick/direction (missing_info 자동 기록)
 *
 * 참조:
 *   - apps/web/quick_flow.md §2
 *   - apps/web/wireframes/quick_short.md Step 2
 *   - docs/contracts/output_schema.md §7.2 missing_info Quick Mode 0~2개
 *
 * Slice 4 단독: question은 mock (Phase 4+ POST /api/v1/quick/start 응답
 * clarify_questions로 동적 교체).
 */

'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { QuickInputCard } from '@/components/quick/QuickInputCard';
import {
  saveQuickStep,
  loadQuickStep,
  type QuickStep2State,
} from '@/lib/quick_state';

const MAX_LEN = 200;

// Slice 4 mock 질문 (Phase 4+ AI 판정 결과로 교체)
// quick_flow.md §2.3 검사 항목 첫 번째: target 없음
const MOCK_QUESTION = '어떤 분께 보여드릴 영상인가요?';

export default function QuickStep2Page() {
  const router = useRouter();
  const [answer, setAnswer] = useState<string>('');

  useEffect(() => {
    const saved = loadQuickStep<QuickStep2State>(2);
    if (saved?.followUpAnswer) {
      setAnswer(saved.followUpAnswer);
    }
  }, []);

  const handleSubmit = () => {
    const trimmed = answer.trim();
    if (!trimmed) return;
    const state: QuickStep2State = { followUpAnswer: trimmed, skipped: false };
    saveQuickStep<QuickStep2State>(2, state);
    router.push('/new/quick/direction');
  };

  const handleSkip = () => {
    const state: QuickStep2State = { skipped: true };
    saveQuickStep<QuickStep2State>(2, state);
    router.push('/new/quick/direction');
  };

  const ctaDisabled = answer.trim().length === 0 || answer.length > MAX_LEN;

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
          <div className="text-text-muted text-sm font-medium">Quick · 2</div>
          <div className="w-12" aria-hidden="true" />
        </div>
      </header>

      <section className="px-4 py-6 max-w-2xl mx-auto w-full">
        <h1 className="text-3xl font-bold text-text-default mb-2">
          한 가지만 더!
        </h1>
        <p className="text-sm text-text-muted">
          AI가 영상 만들기 전 확인해요.
        </p>
      </section>

      <section className="flex-1 pb-40">
        <QuickInputCard
          mode="follow_up_question"
          question={MOCK_QUESTION}
          value={answer}
          onChange={setAnswer}
          onSkip={handleSkip}
          maxLength={MAX_LEN}
          placeholder="예: 20대 대학생"
        />
      </section>

      <footer className="fixed bottom-0 left-0 right-0 border-t border-border-default bg-bg-default px-4 py-3 safe-area">
        <div className="max-w-2xl mx-auto flex flex-col gap-3">
          <button
            type="button"
            onClick={handleSkip}
            className="w-full py-3 rounded-md font-medium text-text-muted bg-bg-default border border-border-default hover:bg-bg-subtle transition-colors duration-fast"
            aria-label="이대로 진행 (skip)"
          >
            이대로 진행 (skip) ▷
          </button>
          <button
            type="button"
            disabled={ctaDisabled}
            onClick={handleSubmit}
            className="w-full py-3 rounded-md font-semibold text-text-inverse bg-primary hover:bg-primary-hover active:bg-primary-pressed disabled:bg-primary-disabled disabled:cursor-not-allowed transition-colors duration-fast"
            aria-label="답변 후 진행"
          >
            {ctaDisabled ? '답변을 입력해주세요' : '답변 후 진행 ▶'}
          </button>
        </div>
      </footer>
    </main>
  );
}
