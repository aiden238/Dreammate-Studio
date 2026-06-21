"use client";

/**
 * Phase 34 S2 — 대화형 follow-up 입력 (결과 카드 이후 계속 이어가기).
 *
 * 결과 카드를 보고 1개를 선택한 뒤 "저장 = 끝"이던 막다른 길을, 프롬프트로 계속 이어갈 수
 * 있게 한다. 선택한 카드(컨텍스트)를 바탕으로 추가 요청을 보내면 새 기획안 묶음이 아래에 쌓인다.
 *
 * ★ 표현 계층 전용 — PlanCard.tsx 무수정 정신 계승. 상위(page.tsx)가 generate 재호출 + 스레드 누적.
 */

import { useCallback, useState } from "react";

export interface FollowUpComposerProps {
  /** 제출 콜백 — 입력 텍스트를 받아 generate 재호출 (상위 책임). */
  onSubmit: (text: string) => void;
  /** generate 진행 중 (중복 제출 방지 + 로딩 표시). */
  busy: boolean;
  /** 현재 선택된 카드 라벨(있으면 "이 카드 기반" 컨텍스트 안내). */
  selectedLabel?: string | null;
  /** 에러 메시지(있으면 표시). */
  error?: string | null;
}

const HINTS = [
  "2번을 더 짧게(30초)",
  "다른 후크로 다시",
  "더 위트있는 톤으로",
  "이 방향으로 다른 컨셉도",
];

export default function FollowUpComposer({
  onSubmit,
  busy,
  selectedLabel,
  error,
}: FollowUpComposerProps) {
  const [text, setText] = useState("");

  const submit = useCallback(() => {
    const t = text.trim();
    if (!t || busy) return;
    onSubmit(t);
    setText("");
  }, [text, busy, onSubmit]);

  return (
    <section
      aria-label="이어서 요청하기"
      className="flex flex-col gap-2 rounded-xl border border-primary-200 bg-primary-50/60 p-3 sm:p-4"
    >
      <div className="flex items-center justify-between gap-2">
        <h3 className="font-display text-sm font-semibold text-text-default">
          💬 이어서 요청하기
        </h3>
        {selectedLabel ? (
          <span className="text-xs text-primary-700 truncate max-w-[60%]">
            기준: <span className="font-medium">{selectedLabel}</span>
          </span>
        ) : (
          <span className="text-xs text-text-muted">
            카드를 고르면 그 방향으로 이어가요
          </span>
        )}
      </div>

      <div className="flex items-end gap-2">
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={(e) => {
            // Cmd/Ctrl+Enter 로 제출 (Enter 는 줄바꿈 보존)
            if ((e.metaKey || e.ctrlKey) && e.key === "Enter") {
              e.preventDefault();
              submit();
            }
          }}
          disabled={busy}
          rows={2}
          placeholder="수정·추가 요청을 입력하세요 (예: 더 짧게 / 다른 후크 / 다른 컨셉)"
          className="flex-1 resize-none rounded-lg border border-border-default bg-surface px-3 py-2 text-sm text-text-default placeholder:text-text-placeholder focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-1 focus-visible:outline-primary-500 disabled:opacity-60"
          aria-label="추가 요청 입력"
        />
        <button
          type="button"
          onClick={submit}
          disabled={busy || text.trim().length === 0}
          aria-label="이어서 요청 전송"
          className={`shrink-0 min-h-[44px] px-4 rounded-lg text-sm font-semibold transition-colors ${
            busy || text.trim().length === 0
              ? "bg-neutral-200 text-text-muted cursor-not-allowed"
              : "bg-primary-500 text-white hover:bg-primary-600 active:bg-primary-700"
          }`}
        >
          {busy ? "생성 중…" : "이어가기"}
        </button>
      </div>

      {/* 빠른 입력 칩 */}
      <div className="flex flex-wrap gap-1.5">
        {HINTS.map((h) => (
          <button
            key={h}
            type="button"
            disabled={busy}
            onClick={() => setText(h)}
            className="rounded-full border border-primary-200 bg-surface px-2.5 py-1 text-xs text-primary-700 hover:bg-primary-100 disabled:opacity-50"
          >
            {h}
          </button>
        ))}
      </div>

      {error && (
        <p
          role="alert"
          className="rounded-md bg-error-50 border border-error-200 px-3 py-2 text-xs text-error-700"
        >
          {error}
        </p>
      )}
    </section>
  );
}
