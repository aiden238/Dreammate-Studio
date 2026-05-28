/**
 * Phase 3 Slice 2 — CardGrid5 (Discovery 5-card 배치 컨테이너)
 *
 * 4-layer chosen variant=`current` (Vertical stack 1-col 5-row).
 * BrandDirectionCard 5개 (4 AI suggestions + 1 user_direct_input) 배치.
 * alt_horizontal_swipe variant는 prop 자리만 (Phase 4+ A/B 검토).
 *
 * 참조:
 *   - apps/web/component_map.md §CardGrid5
 *   - apps/web/wireframes/step1_brand.md (1열 5행 stack)
 *   - apps/web/design_system/tokens.md (space.3 gap, space.4 padding)
 *
 * a11y: role=radiogroup + aria-label (frontend_design_contract.md §5.3)
 */

'use client';

import { type FC } from 'react';
import {
  BrandDirectionCard,
  type BrandDirectionCardData,
} from './BrandDirectionCard';

export type CardGrid5Variant = 'current' | 'horizontal_swipe';

export interface CardGrid5Props {
  /** 4 AI suggestions */
  cards: BrandDirectionCardData[];
  /** 1 user_direct_input (5번째 슬롯) */
  userInputSlot: BrandDirectionCardData;
  /** 선택된 카드 id (단일 선택, controlled) */
  selectedCardId: string | null;
  onSelect: (card_id: string) => void;
  onUserInputChange: (text: string) => void;
  ariaLabel?: string;
  /**
   * chosen=current 만 구현. alt_horizontal_swipe 는 prop 자리만
   * (component_map.md §CardGrid5 variants yaml — Phase 9 A/B 테스트).
   */
  variant?: CardGrid5Variant;
}

export const CardGrid5: FC<CardGrid5Props> = ({
  cards,
  userInputSlot,
  selectedCardId,
  onSelect,
  onUserInputChange,
  ariaLabel = '5장 카드 중 1장 선택',
  variant = 'current',
}) => {
  // TODO(Phase 9): variant === 'horizontal_swipe' carousel 구현
  // 현재는 current variant (vertical stack)만 구현.
  if (variant !== 'current') {
    // fallback to current
  }

  const allCards: BrandDirectionCardData[] = [...cards, userInputSlot];

  return (
    <div
      role="radiogroup"
      aria-label={ariaLabel}
      className="flex flex-col gap-3 px-4 w-full max-w-2xl mx-auto"
    >
      {allCards.map((card) => (
        <BrandDirectionCard
          key={card.card_id}
          card={card}
          selected={selectedCardId === card.card_id}
          onSelect={onSelect}
          onUserInputChange={
            card.kind === 'user_direct_input' ? onUserInputChange : undefined
          }
        />
      ))}
    </div>
  );
};
