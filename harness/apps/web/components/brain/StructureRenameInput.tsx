"use client";

/**
 * Phase 24 Slice S2 — 구조 인라인 rename (Domain/Series EDIT).
 *
 * `/brain` "지식 구조(4계층)" 섹션에서 사용. 도메인/시리즈 행의 ✏️ 를 누르면 그 자리에서
 * 현재 이름이 채워진 controlled 입력으로 바뀌고, 저장(✓)하면 부모가 넘긴 onSubmit(name) 을
 * await → 부모가 updateDomain/updateSeries + refetch 수행. 취소(✕)하면 원래 이름으로 복귀.
 *   - 자체 입력 state(value, 현재 이름으로 초기화)를 가져 부모의 map 관리 없이 controlled 보장.
 *   - 성공 시 부모가 표시 모드로 되돌린다(onDone). 실패하면 인라인 에러 + 편집 모드 유지.
 *   - StructureCreateInput 과 동일한 토큰/버튼/에러 스타일(일관 UX).
 *
 * 참조:
 *   - apps/web/components/brain/StructureCreateInput.tsx (controlled 입력 + 토큰 원형)
 *   - apps/web/app/brain/page.tsx (PkmChip 큐레이션 ✏️/🗑 와 동일 톤)
 *   - apps/web/design.md §2 (카드 단위 / 모바일 한 손 / 44px 탭 타깃)
 */

import { useState } from "react";

interface StructureRenameInputProps {
  /** 현재 이름 — 입력 초기값(prefill). */
  initialValue: string;
  /** 접근성 라벨 (예: "도메인 이름 수정"). */
  ariaLabel: string;
  /** 다른 곳에서 동작 중이라 잠시 비활성. */
  disabled?: boolean;
  /** 저장 — 새 이름을 받아 update+refetch. 성공 resolve / 실패 reject. */
  onSubmit: (name: string) => Promise<void>;
  /** 편집 종료(저장 성공 또는 취소) — 부모가 표시 모드로 복귀. */
  onDone: () => void;
}

export default function StructureRenameInput({
  initialValue,
  ariaLabel,
  disabled = false,
  onSubmit,
  onDone,
}: StructureRenameInputProps) {
  const [value, setValue] = useState(initialValue);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const trimmed = value.trim();
  const blocked = disabled || busy;
  // 빈 값/무변경은 저장 불가 (무변경은 취소와 동일 효과).
  const canSubmit = trimmed !== "" && trimmed !== initialValue && !blocked;

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!canSubmit) return;
    setBusy(true);
    setError(null);
    try {
      await onSubmit(trimmed);
      onDone(); // 성공 → 표시 모드로 복귀.
    } catch {
      setError("수정에 실패했어요. 잠시 후 다시 시도해주세요.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="w-full">
      <div className="flex items-center gap-2">
        <input
          type="text"
          value={value}
          onChange={(e) => setValue(e.target.value)}
          disabled={blocked}
          aria-label={ariaLabel}
          // eslint-disable-next-line jsx-a11y/no-autofocus
          autoFocus
          className="flex-1 min-w-0 min-h-[44px] px-3 rounded-md border border-border-default bg-surface text-sm text-text-default placeholder:text-text-placeholder focus:outline-none focus:border-primary disabled:opacity-40 disabled:cursor-not-allowed transition-colors duration-fast"
        />
        <button
          type="submit"
          disabled={!canSubmit}
          aria-label="저장"
          title="저장"
          className="shrink-0 inline-flex items-center justify-center min-h-[44px] px-3 rounded-md text-sm font-semibold text-text-inverse bg-primary hover:bg-primary-hover active:bg-primary-pressed transition-colors duration-fast disabled:opacity-40 disabled:cursor-not-allowed"
        >
          {busy ? (
            <span
              className="w-4 h-4 border-2 border-text-inverse border-t-transparent rounded-full animate-spin"
              role="status"
              aria-label="저장 중"
            />
          ) : (
            "저장"
          )}
        </button>
        <button
          type="button"
          onClick={onDone}
          disabled={blocked}
          aria-label="취소"
          title="취소"
          className="shrink-0 inline-flex items-center justify-center min-h-[44px] px-3 rounded-md text-sm font-medium text-text-muted hover:text-text-default hover:bg-bg-subtle transition-colors duration-fast disabled:opacity-40 disabled:cursor-not-allowed"
        >
          취소
        </button>
      </div>
      {error ? (
        <p role="alert" className="mt-1 text-xs text-text-danger">
          {error}
        </p>
      ) : null}
    </form>
  );
}
