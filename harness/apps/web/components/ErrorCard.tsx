"use client";

/**
 * Phase 1 Slice 7 — 사용자용 오류 카드
 *
 * 참조:
 *   - docs/contracts/error_response_contract.md §5 (user_message), §6 (user_action),
 *                                                 §11.2 (절대 금지 — 영문 message 노출)
 *   - apps/web/design.md §20 (Error UX 원칙)
 *   - apps/web/component_map.md "ErrorCard"
 *
 * 동작:
 *   - error.code 를 lib/errors.ts 의 RULES 로 매핑 → title / fallback body 결정
 *   - server 가 명시한 user_message 가 있으면 우선 사용 (광고적 표현 / 영문 기술 메시지 차단은 backend 책임)
 *   - 동시에 표시되는 액션 최대 2개 (error_response_contract.md §6 우선순위)
 */

import type { ErrorEnvelope } from "@/lib/types";
import { toDisplayError, type DisplayError } from "@/lib/errors";

export interface ErrorCardProps {
  /**
   * ErrorEnvelope (lib/api.ts 가 정규화한 객체) 또는 미리 변환된 DisplayError.
   * sessionStorage 에서 복원하는 경로 (plan/page.tsx) 와 직접 호출 경로 (page.tsx) 양쪽 지원.
   */
  error: ErrorEnvelope | DisplayError;
  /**
   * "다시 시도" 클릭 시. canRetry === true 일 때만 노출.
   */
  onRetry?: () => void;
  /**
   * "처음으로" 클릭 시. canGoHome === true 일 때만 노출.
   */
  onHome?: () => void;
}

function isDisplayError(
  value: ErrorEnvelope | DisplayError,
): value is DisplayError {
  return (
    "title" in value && "body" in value && typeof value.title === "string"
  );
}

export default function ErrorCard({ error, onRetry, onHome }: ErrorCardProps) {
  const display: DisplayError = isDisplayError(error)
    ? error
    : toDisplayError(error);

  return (
    <section
      role="alert"
      aria-live="assertive"
      className="rounded-lg border border-error-500 bg-error-50 p-4 sm:p-6 flex flex-col gap-3"
    >
      <header className="flex items-start gap-3">
        {/* 경고 아이콘 — 색상에만 의존하지 않도록 추가 (design.md §19) */}
        <span
          aria-hidden="true"
          className="flex-shrink-0 inline-flex items-center justify-center w-8 h-8 rounded-full bg-error-500 text-white text-base font-bold"
        >
          !
        </span>
        <div className="flex-1 min-w-0">
          <h2 className="text-base sm:text-lg font-bold text-error-700 leading-snug">
            {display.title}
          </h2>
        </div>
      </header>

      <p className="text-sm sm:text-base text-neutral-800 leading-relaxed">
        {display.body}
      </p>

      {(display.requestId || display.code) && (
        <p className="text-[11px] text-neutral-500 leading-relaxed">
          <span className="font-mono">code: {display.code}</span>
          {display.requestId && (
            <>
              {" · "}
              <span className="font-mono">
                request_id: {display.requestId}
              </span>
            </>
          )}
        </p>
      )}

      {/* 액션 버튼 영역 — 최대 2개, 모바일 우선 stacked / sm 이상 inline */}
      <div className="mt-1 flex flex-col sm:flex-row gap-2">
        {display.canRetry && onRetry && (
          <button
            type="button"
            onClick={onRetry}
            className="inline-flex items-center justify-center min-h-[44px] px-4 py-2 rounded-md bg-primary-500 text-white text-sm font-semibold hover:bg-primary-600 active:bg-primary-700 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary-500"
          >
            다시 시도
          </button>
        )}
        {display.canGoHome && onHome && (
          <button
            type="button"
            onClick={onHome}
            className="inline-flex items-center justify-center min-h-[44px] px-4 py-2 rounded-md bg-neutral-0 text-neutral-700 border border-neutral-300 text-sm font-semibold hover:bg-neutral-100 active:bg-neutral-200 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-neutral-400"
          >
            처음으로
          </button>
        )}
      </div>
    </section>
  );
}
