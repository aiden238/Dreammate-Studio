/**
 * Phase 3 Slice 2 — BrandDirectionCard (Discovery 카드 패턴 baseline)
 *
 * 4-layer chosen variant=`current` (Stacked vertical 5-card) 구현.
 * variant prop 자리만 두고 alt (horizontal_swipe / grid_2x3)는 Phase 4+ 또는
 * 사용자 결정 시 채움.
 *
 * 참조:
 *   - apps/web/design_system/component_contract.md §3 (4-layer 예시)
 *   - apps/web/component_map.md §BrandDirectionCard (Behavior / Layout / Visual / Wireframe)
 *   - apps/web/design_system/tokens.md (Visual layer 토큰 참조)
 *   - apps/web/wireframes/step1_brand.md
 *   - docs/contracts/output_schema.md §3 P-001 brand_direction_cards.cards[i]
 *
 * a11y: role=radio + aria-checked + aria-label (frontend_design_contract.md §5.3)
 *
 * Phase 30 Slice 4 — 시각 리스킨(ChoiceCard, orange × beige 종이).
 *   기능(role/aria-checked/onSelect/onKeyDown/onUserInputChange) 전부 보존.
 *   표현 계층만: 크림 surface + 웜 보더 + 선택 시 주황 보더·옅은 앰버 배경 + 체크 아이콘.
 *   참조: design_reference/VISUAL_CONTRACT.md §6(선택 카드), reference/discovery.html(.choice-card).
 */

'use client';

import { type FC } from 'react';

export type BrandDirectionCardVariant =
  | 'current'
  | 'horizontal_swipe'
  | 'grid_2x3';

export interface BrandDirectionCardData {
  card_id: string;
  kind: 'ai_suggestion' | 'user_direct_input';
  name: string;
  description: string;
  fit_situation?: string;
  pros?: string;
  cautions?: string;
  confidence?: number;
}

export interface BrandDirectionCardProps {
  card: BrandDirectionCardData;
  selected: boolean;
  onSelect: (card_id: string) => void;
  /** user_direct_input 모드일 때만 사용 */
  onUserInputChange?: (text: string) => void;
  /**
   * chosen=current 만 구현. horizontal_swipe / grid_2x3 는 prop 자리만
   * (Phase 4+ 또는 사용자 결정 시 채움 — component_map.md §BrandDirectionCard variants).
   */
  variant?: BrandDirectionCardVariant;
}

export const BrandDirectionCard: FC<BrandDirectionCardProps> = ({
  card,
  selected,
  onSelect,
  onUserInputChange,
  variant = 'current',
}) => {
  // TODO(Phase 4+): variant === 'horizontal_swipe' / 'grid_2x3' 분기 추가
  // 현재는 current variant만 구현. alt variants는 prop 자리만 (component_map.md variants yaml).
  if (variant !== 'current') {
    // fallback to current
  }

  // user_direct_input 모드: textarea 카드
  if (card.kind === 'user_direct_input') {
    return (
      <div
        role="radio"
        tabIndex={0}
        aria-label={card.name}
        aria-checked={selected}
        className={`relative w-full min-h-[44px] p-4 rounded-2xl border transition-all duration-fast focus-within:outline-none ${
          selected
            ? 'border-primary border-2 bg-primary-50 shadow-[0_10px_30px_-18px_rgba(86,55,36,0.35)]'
            : 'bg-surface border-border-default focus-within:border-border-focus focus-within:border-2 hover:border-primary-300'
        }`}
        onClick={() => onSelect(card.card_id)}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            onSelect(card.card_id);
          }
        }}
      >
        {selected && (
          <span
            aria-hidden="true"
            className="absolute right-3.5 top-3.5 inline-flex h-5 w-5 items-center justify-center rounded-full bg-primary text-text-inverse text-xs font-bold"
          >
            {'✓'}
          </span>
        )}
        <div className="font-display text-text-default font-bold text-lg mb-3">
          {'✎'} {card.name}
        </div>
        <textarea
          className="w-full p-3 border border-border-default rounded-xl text-sm text-text-default placeholder:text-text-placeholder bg-surface focus:outline-none focus:border-border-focus focus:border-2 resize-none"
          placeholder={card.description || '직접 브랜드 방향을 입력해주세요...'}
          rows={3}
          aria-label="브랜드 방향 직접 입력"
          onChange={(e) => onUserInputChange?.(e.target.value)}
          onFocus={() => onSelect(card.card_id)}
        />
      </div>
    );
  }

  // ai_suggestion 카드
  const filled = typeof card.confidence === 'number'
    ? Math.round(card.confidence * 5)
    : 0;

  return (
    <button
      type="button"
      role="radio"
      aria-checked={selected}
      aria-label={card.name}
      onClick={() => onSelect(card.card_id)}
      className={`relative w-full min-h-[44px] text-left p-4 rounded-2xl border transition-all duration-fast focus:outline-none focus:border-border-focus focus:border-2 motion-safe:hover:-translate-y-0.5 ${
        selected
          ? 'border-primary border-2 bg-primary-50 shadow-[0_10px_30px_-18px_rgba(86,55,36,0.35)]'
          : 'bg-surface border-border-default hover:border-primary-300 hover:bg-primary-50/40'
      }`}
    >
      <div className="flex items-center gap-2 mb-2 pr-7">
        {selected && (
          <span
            aria-hidden="true"
            className="absolute right-3.5 top-3.5 inline-flex items-center justify-center w-5 h-5 rounded-full bg-primary text-text-inverse text-xs font-bold"
          >
            {'✓'}
          </span>
        )}
        <div className="font-display font-bold text-lg text-text-default">
          {card.name}
        </div>
      </div>
      <div className="text-base text-text-default mb-3 leading-normal">
        {card.description}
      </div>
      {(card.fit_situation || card.pros || card.cautions) && (
        <div className="space-y-1 border-t border-border-subtle pt-3">
          {card.fit_situation && (
            <div className="text-sm text-text-muted">
              <span className="font-medium">Fit</span> {card.fit_situation}
            </div>
          )}
          {card.pros && (
            <div className="text-sm text-text-muted">
              <span className="font-medium">Pros</span> {card.pros}
            </div>
          )}
          {card.cautions && (
            <div className="text-sm text-text-muted">
              <span className="font-medium">{'⚠'} Cautions</span>{' '}
              {card.cautions}
            </div>
          )}
        </div>
      )}
      {typeof card.confidence === 'number' && (
        <div className="mt-3 text-xs text-text-muted flex items-center gap-2">
          <span aria-hidden="true">
            <span className="text-primary">{'●'.repeat(filled)}</span>
            <span className="text-border-default">
              {'○'.repeat(5 - filled)}
            </span>
          </span>
          <span>confidence {card.confidence.toFixed(2)}</span>
        </div>
      )}
    </button>
  );
};
