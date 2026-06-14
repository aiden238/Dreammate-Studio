/**
 * Phase 3 Slice 3 — ToneChipsForm (Discovery Step 5, form 변형 — 5-card 예외)
 *
 * U2-7 결정 (2026-05-27): 다중선택 chip 8개 + skip 패턴 채택, 슬라이더 X.
 *
 * 참조:
 *   - apps/web/discovery_flow.md §5 (Tone & Style form 변형)
 *   - apps/web/component_map.md §ToneChipsForm (placeholder — Slice 3 진입 시 4-layer)
 *   - apps/web/design_system/tokens.md (chip color / radius)
 *   - docs/contracts/output_schema.md §7 tone_card form
 *
 * a11y: role=group + 명시 aria-label, chip role=checkbox + aria-checked
 *       (frontend_design_contract.md §5).
 */

'use client';

import { type FC } from 'react';

/** 8 chips — discovery_flow.md §5.1 6~10개 범위 내 chosen */
export const TONE_CHIPS = [
  'warm',
  'professional',
  'casual',
  'energetic',
  'sincere',
  'humorous',
  'informative',
  'friendly',
] as const;

export type ToneChip = (typeof TONE_CHIPS)[number];

export interface ToneChipsFormProps {
  selectedTones: string[];
  onChange: (tones: string[]) => void;
  onSkip?: () => void;
  /** default 4 — discovery_flow.md §5.1 (1~4개 선택) */
  maxSelections?: number;
  ariaLabel?: string;
}

export const ToneChipsForm: FC<ToneChipsFormProps> = ({
  selectedTones,
  onChange,
  onSkip,
  maxSelections = 4,
  ariaLabel = '톤 선택 (다중선택)',
}) => {
  const toggleChip = (chip: string) => {
    if (selectedTones.includes(chip)) {
      onChange(selectedTones.filter((c) => c !== chip));
    } else if (selectedTones.length < maxSelections) {
      onChange([...selectedTones, chip]);
    }
  };

  const atMax = selectedTones.length >= maxSelections;

  return (
    <div
      role="group"
      aria-label={ariaLabel}
      className="w-full max-w-2xl mx-auto px-4 py-2"
    >
      <div className="text-sm text-text-muted mb-3">
        영상의 톤을 1~{maxSelections}개 선택해주세요.
      </div>

      <div className="flex flex-wrap gap-2 mb-3">
        {TONE_CHIPS.map((chip) => {
          const isSelected = selectedTones.includes(chip);
          const isDisabled = !isSelected && atMax;
          return (
            <button
              key={chip}
              type="button"
              role="checkbox"
              aria-checked={isSelected}
              aria-label={chip}
              disabled={isDisabled}
              onClick={() => toggleChip(chip)}
              className={`inline-flex min-h-[44px] items-center gap-1.5 px-4 py-2 rounded-full border text-sm transition-colors duration-fast focus:outline-none focus:border-border-focus focus:border-2 ${
                isSelected
                  ? 'bg-primary text-text-inverse border-primary shadow-[0_8px_22px_-14px_rgba(86,55,36,0.5)]'
                  : isDisabled
                    ? 'bg-bg-subtle text-text-placeholder border-border-subtle cursor-not-allowed'
                    : 'bg-surface text-text-default border-border-default hover:border-primary-300 hover:bg-primary-50/50'
              }`}
            >
              {isSelected && (
                <span aria-hidden="true" className="text-xs font-bold">
                  {'✓'}
                </span>
              )}
              {chip}
            </button>
          );
        })}
      </div>

      <div
        className="text-xs text-text-muted mb-4"
        aria-live="polite"
        aria-label={`선택된 톤 ${selectedTones.length}개 (최대 ${maxSelections}개)`}
      >
        선택됨: {selectedTones.length} / {maxSelections}
      </div>

      {onSkip && (
        <button
          type="button"
          onClick={onSkip}
          className="text-sm text-text-muted underline hover:text-text-default transition-colors duration-fast"
          aria-label="톤 건너뛰기 (AI에게 위임)"
        >
          톤 건너뛰기 (AI에게 위임)
        </button>
      )}
    </div>
  );
};
