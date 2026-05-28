/**
 * Phase 3 Slice 4 — QuickInputCard (Quick Mode 입력, mode 분기)
 *
 * 두 mode 공유 컴포넌트:
 *   - initial_prompt    : Step 1 짧은 프롬프트 입력 (max 300자, textarea rows=4)
 *   - follow_up_question: Step 2 부족 정보 질문 답변 (max 200자, textarea rows=3, skip CTA)
 *
 * 참조:
 *   - apps/web/component_map.md §QuickInputCard (4-layer, current variant)
 *   - apps/web/quick_flow.md §1, §2
 *   - apps/web/wireframes/quick_short.md Step 1/2
 *   - apps/web/design_system/tokens.md
 *   - docs/contracts/frontend_design_contract.md §5 (a11y)
 *
 * Visual: tokens 참조 (literal hex 0건). var(--color-*) alias만 사용.
 * a11y: role="region" + aria-label + textarea aria-multiline + aria-live char count.
 */

'use client';

import { type FC } from 'react';

export type QuickInputCardMode = 'initial_prompt' | 'follow_up_question';

export interface QuickInputCardProps {
  mode: QuickInputCardMode;
  /** follow_up_question 모드일 때만 표시 */
  question?: string;
  placeholder?: string;
  /** default: initial_prompt=300, follow_up_question=200 (quick_flow.md §1.4 / §2.4) */
  maxLength?: number;
  value: string;
  onChange: (text: string) => void;
  /** follow_up_question 모드의 secondary CTA (이대로 진행 / AI에게 위임) */
  onSkip?: () => void;
  ariaLabel?: string;
}

export const QuickInputCard: FC<QuickInputCardProps> = ({
  mode,
  question,
  placeholder,
  maxLength,
  value,
  onChange,
  onSkip,
  ariaLabel,
}) => {
  const effectiveMaxLength =
    maxLength ?? (mode === 'initial_prompt' ? 300 : 200);
  const overLimit = value.length > effectiveMaxLength;

  const defaultPlaceholder =
    mode === 'initial_prompt'
      ? '예: 다른 스타일로 한 편 더'
      : '답변을 입력하세요';

  const defaultAriaLabel =
    ariaLabel ??
    (mode === 'initial_prompt' ? '짧은 프롬프트 입력' : 'AI 부족 정보 질문');

  return (
    <section
      role="region"
      aria-label={defaultAriaLabel}
      className="w-full max-w-2xl mx-auto px-4 py-2"
    >
      {mode === 'follow_up_question' && question && (
        <h2
          aria-live="polite"
          className="text-text-default font-semibold text-lg mb-3 leading-normal"
        >
          Q. {question}
        </h2>
      )}

      <div
        className="bg-surface border border-border-default rounded-md p-3 focus-within:border-border-focus focus-within:border-2 transition-colors duration-fast"
      >
        <textarea
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder ?? defaultPlaceholder}
          rows={mode === 'initial_prompt' ? 4 : 3}
          aria-label={mode === 'initial_prompt' ? '이번 영상 의도' : '부족 정보 답변'}
          aria-multiline="true"
          aria-invalid={overLimit ? true : undefined}
          className="w-full text-text-default placeholder:text-text-placeholder bg-transparent border-none outline-none resize-none text-base"
        />
        <div
          aria-live="polite"
          className={`text-xs text-right mt-1 ${
            overLimit ? 'text-text-danger font-medium' : 'text-text-muted'
          }`}
        >
          {value.length} / {effectiveMaxLength}
        </div>
      </div>

      {mode === 'follow_up_question' && onSkip && (
        <button
          type="button"
          onClick={onSkip}
          className="mt-3 text-sm text-text-muted underline hover:text-text-default transition-colors duration-fast"
          aria-label="답변 건너뛰고 진행"
        >
          답변 건너뛰기 (AI에게 위임) ▷
        </button>
      )}
    </section>
  );
};

export default QuickInputCard;
