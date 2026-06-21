/**
 * Phase 3 Slice 3 — DirectionApprovalCard (양 모드 공통)
 *
 * Discovery Step 6 (variant=verbose, chosen) + Quick Mode (variant=minimal).
 * 4-layer chosen = verbose. minimal은 Quick Mode가 prop으로 전달.
 *
 * 참조:
 *   - apps/web/component_map.md §DirectionApprovalCard (4-layer + 2 variants)
 *   - apps/web/direction_approval.md (양 모드 공통 spec)
 *   - apps/web/wireframes/direction_approval.md
 *   - apps/web/design_system/tokens.md
 *   - docs/contracts/output_schema.md §7 P-005 oneline_direction
 *
 * a11y: role=region + 명시 aria-label, textarea aria-multiline,
 *       버튼 role=button + 명시 aria-label (frontend_design_contract.md §5).
 */

'use client';

import { useEffect, useState, type FC } from 'react';

export type DirectionApprovalCardVariant = 'verbose' | 'minimal';

export interface DirectionReason {
  step: string;
  value: string;
}

export interface DirectionApprovalCardDirection {
  text: string;
  reasons?: DirectionReason[];
  revise_count?: number;
  /**
   * Phase 34 S2 (cross-project 수렴) — 의도 명확도 0~1 (plotter 확인 턴 clarity_score 흡수).
   * 있으면 "이렇게 이해했어요 — 맞나요?" 확인 라인 + 명확도 배지를 표면화(가산적, 없으면 종전 동일).
   */
  clarity_score?: number;
}

export interface DirectionApprovalCardProps {
  direction: DirectionApprovalCardDirection;
  /** default 'verbose' (Discovery 권장) */
  variant?: DirectionApprovalCardVariant;
  onApprove: () => void;
  onEditAndApprove?: (edited_text: string) => void;
  onRegenerate: () => void;
  ariaLabel?: string;
}

const MAX_LEN = 70;

export const DirectionApprovalCard: FC<DirectionApprovalCardProps> = ({
  direction,
  variant = 'verbose',
  onApprove,
  onEditAndApprove,
  onRegenerate,
  ariaLabel = '기획 방향 승인',
}) => {
  const [editMode, setEditMode] = useState(false);
  const [editedText, setEditedText] = useState(direction.text);

  // direction prop 변경 (재생성) 시 buffer 동기
  useEffect(() => {
    setEditedText(direction.text);
    setEditMode(false);
  }, [direction.text]);

  const overLimit = editedText.length > MAX_LEN;
  // Phase 34 S2 — 명확도 배지(plotter 확인 턴 흡수). null이면 종전 카드와 byte-동일.
  const clarity = direction.clarity_score;
  const showClarity = typeof clarity === 'number';
  const clarityStrong = showClarity && (clarity as number) >= 0.6;
  const showReasons =
    variant === 'verbose' &&
    Array.isArray(direction.reasons) &&
    direction.reasons.length > 0;

  const handlePrimaryClick = () => {
    if (editMode) {
      if (onEditAndApprove && !overLimit) {
        onEditAndApprove(editedText);
      }
    } else {
      onApprove();
    }
  };

  const handleKeyDownTextarea = (
    e: React.KeyboardEvent<HTMLTextAreaElement>,
  ) => {
    if (e.key === 'Escape') {
      e.preventDefault();
      setEditMode(false);
      setEditedText(direction.text);
    }
  };

  return (
    <section
      role="region"
      aria-label={ariaLabel}
      className="w-full max-w-2xl mx-auto px-4 py-2"
    >
      {/* Phase 34 S2 — 확인 턴 라인 + 명확도 배지 (plotter 흡수). clarity_score 있을 때만. */}
      {showClarity && (
        <div className="flex items-center gap-2 mb-3">
          <span aria-hidden="true" className="text-primary">
            ✓
          </span>
          <p className="text-sm font-medium text-text-default">
            이렇게 이해했어요 — 맞나요?
          </p>
          <span
            aria-label={`명확도 ${Math.round((clarity as number) * 100)}퍼센트`}
            className={`ml-auto rounded-full px-2 py-0.5 text-xs font-semibold ${
              clarityStrong
                ? 'bg-primary text-text-inverse'
                : 'bg-bg-subtle text-text-muted border border-border-default'
            }`}
          >
            명확도 {Math.round((clarity as number) * 100)}%
          </span>
        </div>
      )}

      {/* 한 줄 방향 카드 */}
      <div
        role="region"
        aria-label="AI 생성 기획 방향"
        className="bg-bg-subtle rounded-lg p-4 border border-border-default mb-4"
      >
        {editMode ? (
          <>
            <textarea
              value={editedText}
              onChange={(e) => setEditedText(e.target.value)}
              onKeyDown={handleKeyDownTextarea}
              rows={3}
              aria-label="기획 방향 편집"
              aria-multiline="true"
              aria-invalid={overLimit ? true : undefined}
              className={`w-full p-3 rounded-md text-text-default bg-surface focus:outline-none transition-colors duration-fast resize-none ${
                overLimit
                  ? 'border-2 border-state-error'
                  : 'border border-border-default focus:border-border-focus focus:border-2'
              }`}
              placeholder="기획 방향을 편집해주세요"
            />
            <div className="mt-2 flex items-center justify-between text-sm">
              <span
                aria-live="polite"
                className={overLimit ? 'text-text-danger font-medium' : 'text-text-muted'}
              >
                글자수: {editedText.length} / {MAX_LEN}
              </span>
              <button
                type="button"
                onClick={() => {
                  setEditMode(false);
                  setEditedText(direction.text);
                }}
                className="text-text-muted hover:text-text-default transition-colors duration-fast"
                aria-label="편집 취소"
              >
                ✗ 취소
              </button>
            </div>
          </>
        ) : (
          <div className="flex items-start justify-between gap-3">
            <p className="text-text-default font-medium text-xl leading-normal flex-1">
              &ldquo;{direction.text}&rdquo;
            </p>
            <button
              type="button"
              onClick={() => setEditMode(true)}
              className="flex-shrink-0 text-text-muted hover:text-primary transition-colors duration-fast"
              aria-label="편집"
            >
              ✎
            </button>
          </div>
        )}
      </div>

      {/* Reasons (verbose only) */}
      {showReasons && (
        <div className="border-t border-border-subtle pt-4 mb-4">
          <div className="text-sm font-medium text-text-default mb-2">
            이유:
          </div>
          <ul className="space-y-1">
            {direction.reasons!.map((r, i) => (
              <li
                key={`${r.step}-${i}`}
                className="text-sm text-text-muted leading-normal"
              >
                <span aria-hidden="true">• </span>
                <span className="font-medium">{r.step}:</span> {r.value}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Buttons */}
      <div className="flex flex-col gap-3">
        <button
          type="button"
          onClick={handlePrimaryClick}
          disabled={editMode && overLimit}
          className="w-full py-3 rounded-md font-semibold text-text-inverse bg-primary hover:bg-primary-hover active:bg-primary-pressed disabled:bg-primary-disabled disabled:cursor-not-allowed transition-colors duration-fast"
          aria-label={editMode ? '수정 후 진행' : '이대로 진행'}
        >
          {editMode ? '수정 후 진행 ▶' : '이대로 진행 ▶'}
        </button>
        <button
          type="button"
          onClick={onRegenerate}
          className="w-full py-2 rounded-md text-text-muted hover:text-primary underline transition-colors duration-fast"
          aria-label="다시 생성"
        >
          ↻ 다시 생성
          {typeof direction.revise_count === 'number' && direction.revise_count > 0 && (
            <span className="ml-2 text-xs">({direction.revise_count}회)</span>
          )}
        </button>
      </div>
    </section>
  );
};
