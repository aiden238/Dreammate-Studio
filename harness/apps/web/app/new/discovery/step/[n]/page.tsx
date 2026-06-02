/**
 * Phase 3 Slice 3 — Discovery Step 2~7 dynamic route (`/new/discovery/step/[n]`).
 *
 * n=2~7 통합 페이지. Step 1은 별도 파일 (Slice 2 산출물 보존).
 * - n=2,3,4: BrandDirectionCard 패턴 (Slice 2 재사용)
 * - n=5: ToneChipsForm (form 변형)
 * - n=6: DirectionApprovalCard variant=verbose
 * - n=7: ProgressStepper (4단계) + PlanCard (Phase 1 재사용, mock)
 * - 그 외: notFound()
 *
 * Phase 4 진입 시 실 API 통합 (현재 mock 데이터).
 *
 * 참조:
 *   - apps/web/discovery_flow.md §2~§7
 *   - apps/web/component_map.md (Routes ↔ Components 매핑 표)
 *   - apps/web/wireframes/direction_approval.md
 */

'use client';

import { useEffect, useRef, useState } from 'react';
import { useParams, useRouter, notFound } from 'next/navigation';
import { CardGrid5 } from '@/components/discovery/CardGrid5';
import type { BrandDirectionCardData } from '@/components/discovery/BrandDirectionCard';
import { ToneChipsForm } from '@/components/discovery/ToneChipsForm';
import { DirectionApprovalCard } from '@/components/common/DirectionApprovalCard';
import ProgressStepper, {
  type StepperState,
} from '@/components/ProgressStepper';
import { startPlan, wizardStep, generateMultiPlan } from '@/lib/api';
import {
  loadDiscoveryStep,
  saveDiscoveryStep,
  loadDiscoveryStep1,
  type DiscoveryStep2State,
  type DiscoveryStep3State,
  type DiscoveryStep4State,
  type DiscoveryStep5State,
  type DiscoveryStep6State,
  type DiscoveryStep6Direction,
} from '@/lib/discovery_state';

// ─── Mock data (Slice 3: Phase 4 실 API 통합 전 mock) ─────────────────

const MOCK_CARDS_BY_STEP: Record<2 | 3 | 4, BrandDirectionCardData[]> = {
  2: [
    {
      card_id: 'domain-a',
      kind: 'ai_suggestion',
      name: '재테크',
      description: '돈 관리, 투자, 자산 형성 콘텐츠',
      fit_situation: '30대 직장인 / 자영업자',
      pros: '높은 검색량',
      cautions: '규제 표현 주의',
      confidence: 0.82,
    },
    {
      card_id: 'domain-b',
      kind: 'ai_suggestion',
      name: '건강',
      description: '신체 / 정신 건강 정보',
      fit_situation: '40대~60대 / 모든 연령',
      pros: '꾸준한 수요',
      cautions: '의료 정보 검증 필수',
      confidence: 0.74,
    },
    {
      card_id: 'domain-c',
      kind: 'ai_suggestion',
      name: '라이프스타일',
      description: '일상 / 취미 / 자기계발',
      fit_situation: '20대~30대',
      pros: '광범위한 타깃',
      cautions: '경쟁 심함',
      confidence: 0.7,
    },
    {
      card_id: 'domain-d',
      kind: 'ai_suggestion',
      name: '기술 / IT',
      description: '디지털 도구, 소프트웨어, AI',
      fit_situation: '얼리어답터 / 직장인',
      pros: '전문성 가시화',
      cautions: '진입 장벽 (전문 지식)',
      confidence: 0.68,
    },
  ],
  3: [
    {
      card_id: 'series-a',
      kind: 'ai_suggestion',
      name: '30초 쇼츠',
      description: '짧고 임팩트 있는 단일 포인트',
      fit_situation: '바이럴 / 첫 발견',
      pros: '소비 부담 ↓',
      cautions: '깊이 제한',
      confidence: 0.83,
    },
    {
      card_id: 'series-b',
      kind: 'ai_suggestion',
      name: '1분 정보',
      description: '핵심 정리 + 출처',
      fit_situation: '검색 유입 / 재시청',
      pros: '검색 노출 좋음',
      cautions: '편집 시간 ↑',
      confidence: 0.78,
    },
    {
      card_id: 'series-c',
      kind: 'ai_suggestion',
      name: '인터뷰',
      description: '전문가 / 사용자 대담',
      fit_situation: '신뢰 형성 / 다양성',
      pros: '신뢰도 ↑',
      cautions: '섭외 비용',
      confidence: 0.65,
    },
    {
      card_id: 'series-d',
      kind: 'ai_suggestion',
      name: '리뷰',
      description: '실 사용 검증 / 비교',
      fit_situation: '구매 결정 단계',
      pros: '전환율 ↑',
      cautions: '광고 표시 의무',
      confidence: 0.72,
    },
  ],
  4: [
    {
      card_id: 'target-a',
      kind: 'ai_suggestion',
      name: '30대 직장인',
      description: '바쁘지만 자기계발 의지 ↑',
      fit_situation: '재테크 / 건강 / 시간관리',
      pros: '구매력 ↑',
      cautions: '시간 ↓',
      confidence: 0.85,
    },
    {
      card_id: 'target-b',
      kind: 'ai_suggestion',
      name: '20대 학생',
      description: '취업 준비 / 경험 축적',
      fit_situation: '학습 / 경력 / 트렌드',
      pros: 'SNS 활성',
      cautions: '구매력 ↓',
      confidence: 0.7,
    },
    {
      card_id: 'target-c',
      kind: 'ai_suggestion',
      name: '자영업자',
      description: '시간 효율 + 매출 직결 필요',
      fit_situation: '비즈니스 / 절세 / 마케팅',
      pros: '명확한 니즈',
      cautions: '경쟁 심함',
      confidence: 0.68,
    },
    {
      card_id: 'target-d',
      kind: 'ai_suggestion',
      name: '주부',
      description: '가족 / 생활 정보 / 절약',
      fit_situation: '생활 / 육아 / 살림',
      pros: '꾸준한 시청',
      cautions: '구매 결정 시간 ↑',
      confidence: 0.65,
    },
  ],
};

const USER_INPUT_SLOT_BY_STEP: Record<2 | 3 | 4, BrandDirectionCardData> = {
  2: {
    card_id: 'domain-user-input',
    kind: 'user_direct_input',
    name: '직접 입력',
    description: '도메인을 직접 입력해주세요',
  },
  3: {
    card_id: 'series-user-input',
    kind: 'user_direct_input',
    name: '직접 입력',
    description: '시리즈 형식을 직접 입력해주세요',
  },
  4: {
    card_id: 'target-user-input',
    kind: 'user_direct_input',
    name: '직접 입력',
    description: '타깃을 직접 입력해주세요',
  },
};

const TITLE_BY_STEP: Record<2 | 3 | 4 | 5 | 6 | 7, { h1: string; sub: string }> =
  {
    2: {
      h1: '도메인을 선택하세요',
      sub: '어떤 분야의 콘텐츠인가요?',
    },
    3: {
      h1: '시리즈 형식을 선택하세요',
      sub: '영상 길이와 포맷을 정해주세요.',
    },
    4: {
      h1: '타깃을 선택하세요',
      sub: '누구에게 보여주고 싶은 영상인가요?',
    },
    5: {
      h1: '톤을 선택하세요',
      sub: '여러 톤을 동시에 선택할 수 있어요.',
    },
    6: {
      h1: '기획 방향을 확인해주세요',
      sub: 'AI가 정리한 한 줄 방향',
    },
    7: {
      h1: '기획안을 생성 중이에요',
      sub: '30~60초 정도 걸려요.',
    },
  };

// ─── Page Header (모든 step 공통) ─────────────────────────────────────

function WizardHeader({
  n,
  onBack,
}: {
  n: number;
  onBack: () => void;
}) {
  return (
    <header className="border-b border-border-default px-4 py-3 sticky top-0 bg-bg-default z-10">
      <div className="max-w-2xl mx-auto flex items-center justify-between">
        <button
          type="button"
          className="text-text-muted text-sm font-medium hover:text-text-default transition-colors duration-fast"
          onClick={onBack}
          aria-label="뒤로 가기"
        >
          ← back
        </button>
        <div
          className="text-text-muted text-sm font-medium"
          aria-current="step"
        >
          {n} / 7
        </div>
        <div className="w-12" aria-hidden="true" />
      </div>
    </header>
  );
}

// ─── n=2,3,4: BrandDirectionCard 패턴 (Slice 2 재사용) ─────────────────

function BrandCardStep({ n }: { n: 2 | 3 | 4 }) {
  const router = useRouter();
  const cards = MOCK_CARDS_BY_STEP[n];
  const userInputSlot = USER_INPUT_SLOT_BY_STEP[n];
  const { h1, sub } = TITLE_BY_STEP[n];

  const [selectedCardId, setSelectedCardId] = useState<string | null>(null);
  const [userInputText, setUserInputText] = useState<string>('');

  useEffect(() => {
    const saved = loadDiscoveryStep(n);
    if (saved) {
      setSelectedCardId(saved.selectedCardId);
      setUserInputText(saved.userInputText ?? '');
    }
  }, [n]);

  const handleSelect = (card_id: string) => {
    setSelectedCardId(card_id);
  };

  const handleUserInputChange = (text: string) => {
    setUserInputText(text);
    setSelectedCardId(userInputSlot.card_id);
  };

  const handleNext = () => {
    if (!selectedCardId) return;
    const state: DiscoveryStep2State | DiscoveryStep3State | DiscoveryStep4State = {
      selectedCardId,
      userInputText:
        selectedCardId === userInputSlot.card_id ? userInputText : undefined,
    };
    saveDiscoveryStep(n, state);
    router.push(`/new/discovery/step/${n + 1}`);
  };

  const ctaDisabled =
    !selectedCardId ||
    (selectedCardId === userInputSlot.card_id && userInputText.trim() === '');

  return (
    <main className="min-h-screen bg-bg-default flex flex-col">
      <WizardHeader n={n} onBack={() => router.back()} />
      <section className="px-4 py-6 max-w-2xl mx-auto w-full">
        <h1 className="text-3xl font-bold text-text-default mb-2">{h1}</h1>
        <p className="text-sm text-text-muted">{sub}</p>
      </section>
      <section className="flex-1 pb-32">
        <CardGrid5
          cards={cards}
          userInputSlot={userInputSlot}
          selectedCardId={selectedCardId}
          onSelect={handleSelect}
          onUserInputChange={handleUserInputChange}
          ariaLabel={h1}
        />
      </section>
      <footer className="fixed bottom-0 left-0 right-0 border-t border-border-default bg-bg-default px-4 py-3 safe-area">
        <div className="max-w-2xl mx-auto">
          <button
            type="button"
            disabled={ctaDisabled}
            onClick={handleNext}
            className="w-full py-3 rounded-md font-semibold text-text-inverse bg-primary hover:bg-primary-hover active:bg-primary-pressed disabled:bg-primary-disabled disabled:cursor-not-allowed transition-colors duration-fast"
            aria-label="다음 단계로 진행"
          >
            {ctaDisabled ? '카드를 선택해주세요' : '다음 단계로 ▶'}
          </button>
        </div>
      </footer>
    </main>
  );
}

// ─── n=5: ToneChipsForm (form 변형) ───────────────────────────────────

function Step5Tone() {
  const router = useRouter();
  const { h1, sub } = TITLE_BY_STEP[5];
  const [selectedTones, setSelectedTones] = useState<string[]>([]);
  const [skipped, setSkipped] = useState(false);

  useEffect(() => {
    const saved = loadDiscoveryStep(5);
    if (saved) {
      setSelectedTones(saved.selectedTones);
      setSkipped(saved.skipped ?? false);
    }
  }, []);

  const handleNext = () => {
    const state: DiscoveryStep5State = { selectedTones, skipped: false };
    saveDiscoveryStep(5, state);
    router.push('/new/discovery/step/6');
  };

  const handleSkip = () => {
    const state: DiscoveryStep5State = { selectedTones: [], skipped: true };
    saveDiscoveryStep(5, state);
    setSkipped(true);
    router.push('/new/discovery/step/6');
  };

  const ctaDisabled = selectedTones.length === 0;

  return (
    <main className="min-h-screen bg-bg-default flex flex-col">
      <WizardHeader n={5} onBack={() => router.back()} />
      <section className="px-4 py-6 max-w-2xl mx-auto w-full">
        <h1 className="text-3xl font-bold text-text-default mb-2">{h1}</h1>
        <p className="text-sm text-text-muted">{sub}</p>
      </section>
      <section className="flex-1 pb-32">
        <ToneChipsForm
          selectedTones={selectedTones}
          onChange={setSelectedTones}
          onSkip={handleSkip}
          maxSelections={4}
          ariaLabel="톤 선택 (다중선택, 최대 4개)"
        />
        {skipped && (
          <div
            className="text-xs text-text-muted mt-2 px-4 max-w-2xl mx-auto"
            aria-live="polite"
          >
            톤 건너뛰기 선택됨 — AI가 자동으로 결정합니다.
          </div>
        )}
      </section>
      <footer className="fixed bottom-0 left-0 right-0 border-t border-border-default bg-bg-default px-4 py-3 safe-area">
        <div className="max-w-2xl mx-auto">
          <button
            type="button"
            disabled={ctaDisabled}
            onClick={handleNext}
            className="w-full py-3 rounded-md font-semibold text-text-inverse bg-primary hover:bg-primary-hover active:bg-primary-pressed disabled:bg-primary-disabled disabled:cursor-not-allowed transition-colors duration-fast"
            aria-label="다음 단계로 진행"
          >
            {ctaDisabled ? '톤을 선택해주세요' : '다음 단계로 ▶'}
          </button>
        </div>
      </footer>
    </main>
  );
}

// ─── n=6: DirectionApprovalCard verbose ──────────────────────────────

/**
 * Step 1~5 sessionStorage state를 요약해 mock 한 줄 방향 + reasons 생성.
 * Phase 4 진입 시 P-005 endpoint 호출로 교체 (현재는 mock 본문 + 실 reasons).
 */
function buildMockDirection(reviseCount: number): DiscoveryStep6Direction {
  // sessionStorage에 저장된 Step 1~5 선택값을 reasons로 합성
  const reasons: Array<{ step: string; value: string }> = [];

  if (typeof window !== 'undefined') {
    const s1 = loadDiscoveryStep1();
    if (s1?.selectedCardId) {
      reasons.push({
        step: 'Step 1 Brand',
        value: s1.userInputText ?? s1.selectedCardId,
      });
    }
    const s2 = loadDiscoveryStep(2);
    if (s2?.selectedCardId) {
      reasons.push({
        step: 'Step 2 Domain',
        value: s2.userInputText ?? s2.selectedCardId,
      });
    }
    const s3 = loadDiscoveryStep(3);
    if (s3?.selectedCardId) {
      reasons.push({
        step: 'Step 3 Series',
        value: s3.userInputText ?? s3.selectedCardId,
      });
    }
    const s4 = loadDiscoveryStep(4);
    if (s4?.selectedCardId) {
      reasons.push({
        step: 'Step 4 Target',
        value: s4.userInputText ?? s4.selectedCardId,
      });
    }
    const s5 = loadDiscoveryStep(5);
    if (s5) {
      if (s5.skipped) {
        reasons.push({ step: 'Step 5 Tone', value: '건너뛰기 (AI 위임)' });
      } else if (s5.selectedTones.length > 0) {
        reasons.push({
          step: 'Step 5 Tone',
          value: s5.selectedTones.join(' / '),
        });
      }
    }
  }

  // 재생성 시 mock 변형 (Phase 4에서 실 P-005 응답으로 교체)
  const variations = [
    '30대 직장인을 위한 짧고 유머러스한 재테크 쇼츠',
    '바쁜 직장인이 1분 만에 이해하는 핵심 재테크 팁',
    '진솔한 톤으로 풀어내는 30대 자산 형성 가이드',
  ];
  const text = variations[reviseCount % variations.length];

  return { text, reasons, revise_count: reviseCount };
}

function Step6Direction() {
  const router = useRouter();
  const { h1, sub } = TITLE_BY_STEP[6];
  const [direction, setDirection] = useState<DiscoveryStep6Direction>(() =>
    buildMockDirection(0),
  );

  useEffect(() => {
    const saved = loadDiscoveryStep(6);
    if (saved) {
      setDirection(saved.direction);
    } else {
      // 최초 진입 시 sessionStorage 기반 reasons 합성
      setDirection(buildMockDirection(0));
    }
  }, []);

  const handleApprove = () => {
    const state: DiscoveryStep6State = { direction, approved: true };
    saveDiscoveryStep(6, state);
    router.push('/new/discovery/step/7');
  };

  const handleEditAndApprove = (editedText: string) => {
    const next: DiscoveryStep6Direction = { ...direction, text: editedText };
    const state: DiscoveryStep6State = {
      direction: next,
      approved: true,
      editedText,
    };
    saveDiscoveryStep(6, state);
    router.push('/new/discovery/step/7');
  };

  const handleRegenerate = () => {
    // direction_approval.md §4.2: revise_count ≤ 2 권장
    const next = buildMockDirection((direction.revise_count ?? 0) + 1);
    setDirection(next);
    const state: DiscoveryStep6State = { direction: next };
    saveDiscoveryStep(6, state);
  };

  return (
    <main className="min-h-screen bg-bg-default flex flex-col">
      <WizardHeader n={6} onBack={() => router.back()} />
      <section className="px-4 py-6 max-w-2xl mx-auto w-full">
        <h1 className="text-3xl font-bold text-text-default mb-2">{h1}</h1>
        <p className="text-sm text-text-muted">{sub}</p>
      </section>
      <section className="flex-1 pb-8">
        <DirectionApprovalCard
          direction={direction}
          variant="verbose"
          onApprove={handleApprove}
          onEditAndApprove={handleEditAndApprove}
          onRegenerate={handleRegenerate}
          ariaLabel="기획 방향 승인 (Discovery Step 6)"
        />
      </section>
    </main>
  );
}

// ─── n=7: Generate (★ Phase 14 S3 — 백엔드 실연결) ───────────────────
//
// Phase 3 Slice 3: mock stepper(setInterval) → router.push('/plan') (랜딩, 데이터 없음).
// Phase 14 S3: Step 1~6 수집 입력 → startPlan() → wizardStep×6(step1~step6) →
//   generateMultiPlan() → router.push('/plan/[plan_id]') (GET /plans/{id} read, rich gated 상속).
//   ProgressStepper 는 실 generate await(30~60s) 동안 낙관적 진행 → 완료 시 navigate.
//   중간 카드(step2~4)·톤(step5)·방향(step6)은 입력수집 UX 유지 — per-step 실 LLM 카드 = NG1(PARKED).

function Step7Generate() {
  const router = useRouter();
  const { h1, sub } = TITLE_BY_STEP[7];
  const [currentStep, setCurrentStep] = useState<StepperState>('idle');
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const startedRef = useRef<boolean>(false);

  useEffect(() => {
    if (startedRef.current) return; // StrictMode 이중 실행 방지
    startedRef.current = true;

    const SEQ: StepperState[] = [
      'intent',
      'rag',
      'planning',
      'critic',
      'complete',
    ];
    // ★ cancelled 플래그 미사용 (StrictMode dev cleanup 이 유일 run 을 취소해
    //   navigation 막는 버그 방지). startedRef 로 1회 실행, cleanup 은 timer 만 정리.
    let timer: ReturnType<typeof setInterval> | undefined;

    async function run(): Promise<void> {
      const s1 = loadDiscoveryStep1();
      const s2 = loadDiscoveryStep(2);
      const s3 = loadDiscoveryStep(3);
      const s4 = loadDiscoveryStep(4);
      const s5 = loadDiscoveryStep(5);
      const s6 = loadDiscoveryStep(6);
      const directionText = s6?.editedText?.trim() || s6?.direction?.text;
      if (!directionText) {
        // Step 6(방향 승인) 없이 직접 진입 → 처음으로
        router.replace('/new/discovery/step/1');
        return;
      }

      let idx = 1;
      setCurrentStep(SEQ[idx]);
      timer = setInterval(() => {
        idx = Math.min(idx + 1, SEQ.length - 2); // critic 까지만
        setCurrentStep(SEQ[idx]);
      }, 4000);

      try {
        const { plan_id } = await startPlan();
        await wizardStep(plan_id, 'step1', {
          selected_card_id: s1?.selectedCardId ?? undefined,
          user_input: s1?.userInputText ?? undefined,
        });
        await wizardStep(plan_id, 'step2', {
          selected_card_id: s2?.selectedCardId ?? undefined,
          user_input: s2?.userInputText ?? undefined,
        });
        await wizardStep(plan_id, 'step3', {
          selected_card_id: s3?.selectedCardId ?? undefined,
          user_input: s3?.userInputText ?? undefined,
        });
        await wizardStep(plan_id, 'step4', {
          selected_card_id: s4?.selectedCardId ?? undefined,
          user_input: s4?.userInputText ?? undefined,
        });
        await wizardStep(plan_id, 'step5', {
          user_input:
            s5 && !s5.skipped && s5.selectedTones.length > 0
              ? s5.selectedTones.join(' / ')
              : undefined,
          extra: s5?.skipped ? { skipped: true } : {},
        });
        await wizardStep(plan_id, 'step6', { user_input: directionText });
        const result = await generateMultiPlan(plan_id);
        if (timer) clearInterval(timer);
        if (result.ok) {
          setCurrentStep('complete');
          router.push(`/plan/${encodeURIComponent(plan_id)}`);
        } else {
          setErrorMsg(result.userMessage);
        }
      } catch (e) {
        if (timer) clearInterval(timer);
        setErrorMsg(
          e instanceof Error
            ? e.message
            : '기획안 생성 중 오류가 발생했어요. 다시 시도해주세요.',
        );
      }
    }

    void run();

    return () => {
      if (timer) clearInterval(timer);
    };
  }, [router]);

  return (
    <main className="min-h-screen bg-bg-default flex flex-col">
      <WizardHeader n={7} onBack={() => router.back()} />
      <section className="px-4 py-6 max-w-2xl mx-auto w-full">
        <h1 className="text-3xl font-bold text-text-default mb-2">
          {errorMsg ? '생성 실패' : h1}
        </h1>
        <p className="text-sm text-text-muted">
          {errorMsg
            ? '잠시 후 다시 시도하거나 처음부터 다시 만들어주세요.'
            : sub}
        </p>
      </section>
      <section className="flex-1 px-4 max-w-2xl mx-auto w-full">
        {!errorMsg && <ProgressStepper currentStep={currentStep} />}
        {errorMsg && (
          <>
            <div
              role="alert"
              className="rounded-md border border-border-default bg-bg-subtle px-4 py-3 text-sm text-text-default"
            >
              {errorMsg}
            </div>
            <div className="mt-4 flex flex-col gap-3">
              <button
                type="button"
                onClick={() => window.location.reload()}
                className="w-full py-3 rounded-md font-semibold text-text-inverse bg-primary hover:bg-primary-hover active:bg-primary-pressed transition-colors duration-fast"
                aria-label="다시 시도"
              >
                다시 시도 ↻
              </button>
              <button
                type="button"
                onClick={() => router.push('/new/discovery/step/1')}
                className="w-full py-3 rounded-md font-medium text-text-muted bg-bg-default border border-border-default hover:bg-bg-subtle transition-colors duration-fast"
                aria-label="처음으로"
              >
                처음으로
              </button>
            </div>
          </>
        )}
      </section>
    </main>
  );
}

// ─── Root page (dynamic route dispatcher) ────────────────────────────

export default function DiscoveryStepDynamicPage() {
  const params = useParams<{ n: string }>();
  const n = Number(params?.n);

  if (n === 2 || n === 3 || n === 4) {
    return <BrandCardStep n={n} />;
  }
  if (n === 5) {
    return <Step5Tone />;
  }
  if (n === 6) {
    return <Step6Direction />;
  }
  if (n === 7) {
    return <Step7Generate />;
  }

  // n=1은 별도 page.tsx (Slice 2 산출물) — dynamic route에 도달했다면 invalid
  notFound();
}
