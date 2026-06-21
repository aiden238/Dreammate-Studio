/**
 * Phase 3 Slice 4 — Quick Mode Step 3 (Direction Approval, minimal variant) page.
 *
 * 흐름: P-005 oneline_direction 표시 → 승인 → /new/quick/generate
 *                                  → 다시 생성 → revise_count++ + mock 재호출
 *                                  → 수정 → 인라인 편집 후 진행
 *
 * 참조:
 *   - apps/web/quick_flow.md §3 (양 모드 공통 — variant=minimal)
 *   - apps/web/direction_approval.md
 *   - apps/web/components/common/DirectionApprovalCard.tsx (Slice 3 산출물 — import only)
 *   - docs/contracts/output_schema.md §7 P-005 oneline_direction
 *
 * Slice 4 단독: direction.text는 sessionStorage Step 1 initialPrompt 기반 mock
 * (Phase 4+ POST /api/v1/quick/start → P-005 response로 교체).
 */

'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { DirectionApprovalCard } from '@/components/common/DirectionApprovalCard';
import { quickClarity } from '@/lib/clarity';
import {
  saveQuickStep,
  loadQuickStep,
  type QuickStep1State,
  type QuickStep2State,
  type QuickStep3State,
} from '@/lib/quick_state';

/**
 * Slice 4 mock direction 생성 (Step 1 initialPrompt 기반).
 * Phase 4+ P-005 oneline_direction 응답으로 교체.
 */
function buildMockDirectionText(initialPrompt: string | null): string {
  const base = initialPrompt?.trim() ?? '새 영상';
  return `${base.slice(0, 24)}을 주제로 짧은 정보형 영상 한 편`;
}

export default function QuickStep3Page() {
  const router = useRouter();
  const [directionText, setDirectionText] = useState<string>('');
  const [reviseCount, setReviseCount] = useState<number>(0);
  // Phase 34 S2 — 의도 명확도(확인 턴 배지). 입력 구체성+clarify 보강으로 결정적 산출.
  const [clarity, setClarity] = useState<number | undefined>(undefined);

  // mount 시 Step 1 initialPrompt 로딩 + 이전 Step 3 state 복원
  useEffect(() => {
    // 명확도: Step1 길이 + Step2(clarify) 응답 여부로 결정적 계산(LLM 무호출).
    const step1 = loadQuickStep<QuickStep1State>(1);
    const step2 = loadQuickStep<QuickStep2State>(2);
    const promptLen = (step1?.initialPrompt ?? '').trim().length;
    const clarified = Boolean(
      step2 && !step2.skipped && step2.followUpAnswer && step2.followUpAnswer.trim(),
    );

    const step3 = loadQuickStep<QuickStep3State>(3);
    if (step3?.direction?.text) {
      setDirectionText(step3.direction.text);
      setReviseCount(step3.direction.revise_count ?? 0);
      setClarity(
        step3.direction.clarity_score ??
          quickClarity({ promptLen, clarified, edited: Boolean(step3.editedText) }),
      );
      return;
    }
    setDirectionText(buildMockDirectionText(step1?.initialPrompt ?? null));
    setClarity(quickClarity({ promptLen, clarified }));
  }, []);

  const handleApprove = () => {
    const state: QuickStep3State = {
      direction: { text: directionText, revise_count: reviseCount, clarity_score: clarity },
      approved: true,
    };
    saveQuickStep<QuickStep3State>(3, state);
    router.push('/new/quick/generate');
  };

  const handleEditAndApprove = (edited: string) => {
    // 직접 다듬으면 의도 확정도↑ — edited 가중 반영.
    const step1 = loadQuickStep<QuickStep1State>(1);
    const step2 = loadQuickStep<QuickStep2State>(2);
    const promptLen = (step1?.initialPrompt ?? '').trim().length;
    const clarified = Boolean(
      step2 && !step2.skipped && step2.followUpAnswer && step2.followUpAnswer.trim(),
    );
    const editedClarity = quickClarity({ promptLen, clarified, edited: true });
    const state: QuickStep3State = {
      direction: { text: edited, revise_count: reviseCount, clarity_score: editedClarity },
      approved: true,
      editedText: edited,
    };
    saveQuickStep<QuickStep3State>(3, state);
    setDirectionText(edited);
    setClarity(editedClarity);
    router.push('/new/quick/generate');
  };

  const handleRegenerate = () => {
    // Slice 4 mock: 재생성은 동일 prompt + 약간 변형 (Phase 4+ P-005 재호출 교체)
    const next = reviseCount + 1;
    setReviseCount(next);
    const step1 = loadQuickStep<QuickStep1State>(1);
    const base = step1?.initialPrompt?.trim() ?? '새 영상';
    setDirectionText(
      `${base.slice(0, 24)}을 다룬 ${next === 1 ? '스토리텔링' : '리뷰형'} 영상 한 편`,
    );
  };

  if (!directionText) {
    return (
      <main className="min-h-screen bg-bg-default flex items-center justify-center">
        <p className="text-text-muted text-sm">방향을 준비 중...</p>
      </main>
    );
  }

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
          <div className="text-text-muted text-sm font-medium">Quick · 3</div>
          <div className="w-12" aria-hidden="true" />
        </div>
      </header>

      <section className="px-4 py-6 max-w-2xl mx-auto w-full">
        <h1 className="text-3xl font-bold text-text-default mb-2">
          이 방향, 어떠세요?
        </h1>
        <p className="text-sm text-text-muted">
          AI가 정리한 한 줄 방향을 확인하고 진행해주세요.
        </p>
      </section>

      <section className="flex-1 pb-12">
        <DirectionApprovalCard
          direction={{ text: directionText, revise_count: reviseCount, clarity_score: clarity }}
          variant="minimal"
          onApprove={handleApprove}
          onEditAndApprove={handleEditAndApprove}
          onRegenerate={handleRegenerate}
          ariaLabel="기획 방향 승인 (Quick Mode)"
        />
      </section>
    </main>
  );
}
