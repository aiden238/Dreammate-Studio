"use client";

/**
 * Phase 22 Slice S2 — 구조 생성 인라인 입력 (Domain/Series CREATE).
 *
 * `/brain` "지식 구조(4계층)" 섹션에서 사용. brand 아래 "+ 도메인", domain 아래 "+ 시리즈"
 * 를 만드는 작은 controlled 입력 + 추가 버튼.
 *   - 자체 입력 state(value)를 가져 부모(page.tsx)의 map 관리 없이 controlled 가 보장됨
 *     (StrictMode one-shot 영향 없음 — user-triggered onChange/onSubmit).
 *   - 제출 시 부모가 넘긴 onSubmit(name) 을 await → 부모가 createDomain/createSeries + refetch 수행.
 *     성공하면 입력을 비우고, 실패하면 인라인 에러 메시지를 띄운다.
 *
 * 참조:
 *   - apps/web/app/brain/page.tsx (PkmChip 큐레이션 컨트롤과 동일 토큰/버튼 스타일)
 *   - apps/web/design.md §2 (카드 단위 / 모바일 한 손)
 */

import { useState } from "react";

interface StructureCreateInputProps {
  /** 입력 placeholder (예: "새 도메인 이름"). */
  placeholder: string;
  /** 추가 버튼 라벨 (예: "+ 도메인"). */
  buttonLabel: string;
  /** 접근성 라벨 (예: "도메인 추가"). */
  ariaLabel: string;
  /** 다른 곳에서 동작 중이라 잠시 비활성. */
  disabled?: boolean;
  /** 제출 — 이름을 받아 생성+refetch. 성공 resolve / 실패 reject. */
  onSubmit: (name: string) => Promise<void>;
}

export default function StructureCreateInput({
  placeholder,
  buttonLabel,
  ariaLabel,
  disabled = false,
  onSubmit,
}: StructureCreateInputProps) {
  const [value, setValue] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const trimmed = value.trim();
  const blocked = disabled || busy;
  const canSubmit = trimmed !== "" && !blocked;

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!canSubmit) return;
    setBusy(true);
    setError(null);
    try {
      await onSubmit(trimmed);
      setValue(""); // 성공 → 입력 비우기.
    } catch {
      setError("추가에 실패했어요. 잠시 후 다시 시도해주세요.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="mt-2">
      <div className="flex items-center gap-2">
        <input
          type="text"
          value={value}
          onChange={(e) => setValue(e.target.value)}
          placeholder={placeholder}
          disabled={blocked}
          aria-label={ariaLabel}
          className="flex-1 min-w-0 min-h-[44px] px-3 rounded-md border border-border-default bg-surface text-sm text-text-default placeholder:text-text-placeholder focus:outline-none focus:border-primary disabled:opacity-40 disabled:cursor-not-allowed transition-colors duration-fast"
        />
        <button
          type="submit"
          disabled={!canSubmit}
          aria-label={ariaLabel}
          className="shrink-0 inline-flex items-center gap-1 min-h-[44px] px-3 rounded-md text-sm font-semibold text-text-inverse bg-primary hover:bg-primary-hover active:bg-primary-pressed transition-colors duration-fast disabled:opacity-40 disabled:cursor-not-allowed"
        >
          {busy ? (
            <span
              className="w-4 h-4 border-2 border-text-inverse border-t-transparent rounded-full animate-spin"
              role="status"
              aria-label="추가 중"
            />
          ) : null}
          {buttonLabel}
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
