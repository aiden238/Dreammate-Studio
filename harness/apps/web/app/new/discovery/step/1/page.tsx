/**
 * Phase 3 Slice 2 — Discovery Step 1 (Brand) page.
 *
 * Thin Vertical 검증 핵심 페이지. CardGrid5 + BrandDirectionCard×5 + sticky CTA.
 *
 * 참조:
 *   - apps/web/page_map.md §/new/discovery/step/1
 *   - apps/web/discovery_flow.md §1
 *   - apps/web/wireframes/step1_brand.md
 *   - docs/contracts/output_schema.md §3 P-001
 *
 * Slice 2 단독: mock 데이터 사용 (Slice 3+에서 실 API 호출 분기).
 * Slice 3: router.push('/new/discovery/step/2') 활성화.
 */

'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { CardGrid5 } from '@/components/discovery/CardGrid5';
import DiscoveryProgress from '@/components/discovery/DiscoveryProgress';
import type { BrandDirectionCardData } from '@/components/discovery/BrandDirectionCard';
import {
  saveDiscoveryStep1,
  loadDiscoveryStep1,
  type DiscoveryStep1State,
} from '@/lib/discovery_state';

// Phase 3 Slice 2: Phase 1 endpoint 통합 전 mock 데이터.
// Slice 3에서 P-001 brand_direction_cards 실 API fetch로 교체.
const MOCK_BRAND_CARDS: BrandDirectionCardData[] = [
  {
    card_id: 'brand-a',
    kind: 'ai_suggestion',
    name: '정보형 콘텐츠',
    description: '명확한 정보 전달 중심, 전문성 강조',
    fit_situation: '교육 / 튜토리얼 / 가이드',
    pros: '신뢰도 ↑, 검색 노출 좋음',
    cautions: '재미 요소 약함',
    confidence: 0.85,
  },
  {
    card_id: 'brand-b',
    kind: 'ai_suggestion',
    name: '스토리텔링',
    description: '경험과 이야기 중심, 감정 연결',
    fit_situation: '브랜드 소개 / 후기 / 변화 과정',
    pros: '몰입도 ↑, 공감 형성',
    cautions: '진입 장벽 (긴 호흡)',
    confidence: 0.72,
  },
  {
    card_id: 'brand-c',
    kind: 'ai_suggestion',
    name: '리뷰 / 비교',
    description: '실 사용 검증, 객관적 비교',
    fit_situation: '제품 / 서비스 평가',
    pros: '구매 결정 직접 영향',
    cautions: '광고 표현 차단 필수',
    confidence: 0.78,
  },
  {
    card_id: 'brand-d',
    kind: 'ai_suggestion',
    name: '엔터테인먼트',
    description: '재미와 흥미 위주, 가볍게 시청',
    fit_situation: '쇼츠 / 챌린지 / 일상',
    pros: '바이럴 가능성',
    cautions: '브랜드 정체성 약화 위험',
    confidence: 0.65,
  },
];

const USER_INPUT_SLOT: BrandDirectionCardData = {
  card_id: 'brand-user-input',
  kind: 'user_direct_input',
  name: '직접 입력',
  description: '어떻게 기억되면 좋을지 직접 적어주세요',
};

export default function DiscoveryStep1Page() {
  const router = useRouter();
  const [selectedCardId, setSelectedCardId] = useState<string | null>(null);
  const [userInputText, setUserInputText] = useState<string>('');

  // session storage에서 이전 state 복원 (back navigation 시 보존)
  useEffect(() => {
    const saved = loadDiscoveryStep1();
    if (saved) {
      setSelectedCardId(saved.selectedCardId);
      setUserInputText(saved.userInputText ?? '');
    }
  }, []);

  const handleSelect = (card_id: string) => {
    setSelectedCardId(card_id);
  };

  const handleUserInputChange = (text: string) => {
    setUserInputText(text);
    // textarea focus / change 시 user_direct_input 카드 자동 선택
    setSelectedCardId(USER_INPUT_SLOT.card_id);
  };

  const handleNext = () => {
    if (!selectedCardId) return;
    const state: DiscoveryStep1State = {
      selectedCardId,
      userInputText:
        selectedCardId === USER_INPUT_SLOT.card_id ? userInputText : undefined,
    };
    saveDiscoveryStep1(state);
    // Slice 3: Step 2 dynamic route 활성
    router.push('/new/discovery/step/2');
  };

  const ctaDisabled =
    !selectedCardId ||
    (selectedCardId === USER_INPUT_SLOT.card_id && userInputText.trim() === '');

  return (
    <main className="min-h-screen bg-bg-default flex flex-col">
      {/* Header (WizardStepHeader placeholder — Slice 3에서 컴포넌트화) */}
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
          <div className="text-text-muted text-sm font-medium">1 / 7</div>
          <div className="w-12" aria-hidden="true" />
        </div>
      </header>

      {/* Title section */}
      <section className="px-4 py-6 max-w-2xl mx-auto w-full">
        <h1 className="text-3xl font-bold text-text-default mb-2">
          어떤 느낌으로 기억되면 좋을까요?
        </h1>
        <p className="text-sm text-text-muted">
          사람들이 이걸 어떻게 기억하면 좋을지 골라요. 직접 적어도 돼요.
        </p>
        <div className="mt-4">
          <DiscoveryProgress currentStep={1} />
        </div>
      </section>

      {/* Cards (CardGrid5) */}
      <section className="flex-1 pb-32">
        <CardGrid5
          cards={MOCK_BRAND_CARDS}
          userInputSlot={USER_INPUT_SLOT}
          selectedCardId={selectedCardId}
          onSelect={handleSelect}
          onUserInputChange={handleUserInputChange}
          ariaLabel="브랜드 방향 선택"
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
            {ctaDisabled ? '카드를 선택해주세요' : '다음 단계로 ▶'}
          </button>
        </div>
      </footer>
    </main>
  );
}
