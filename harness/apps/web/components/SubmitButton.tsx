"use client";

/**
 * Phase 1 Slice 6 — 입력 페이지 제출 버튼
 *
 * frontend_design_contract.md §2.1 / §3.3 (44px+ 터치 타겟, primary CTA) 부분 적용.
 * 본격적인 토큰 alias / shadcn wrap 은 Slice 7+ / Phase 2 에서.
 */

import type { ButtonHTMLAttributes, ReactNode } from "react";

export interface SubmitButtonProps
  extends ButtonHTMLAttributes<HTMLButtonElement> {
  isLoading?: boolean;
  loadingLabel?: string;
  children: ReactNode;
}

export default function SubmitButton({
  isLoading = false,
  loadingLabel = "생성 중...",
  children,
  disabled,
  className,
  ...rest
}: SubmitButtonProps) {
  const merged = [
    "inline-flex items-center justify-center",
    "w-full sm:w-auto",
    "min-h-[44px] px-6 py-3",
    "rounded-md font-semibold text-base",
    "bg-primary-500 text-white",
    "hover:bg-primary-600 active:bg-primary-700",
    "disabled:bg-neutral-300 disabled:text-neutral-500 disabled:cursor-not-allowed",
    "focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary-500",
    "transition-colors duration-150",
    className ?? "",
  ].join(" ");

  return (
    <button
      type="submit"
      disabled={disabled || isLoading}
      aria-busy={isLoading || undefined}
      className={merged}
      {...rest}
    >
      {isLoading ? loadingLabel : children}
    </button>
  );
}
