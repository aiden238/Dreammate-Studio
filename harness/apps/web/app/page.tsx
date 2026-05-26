"use client";

/**
 * Phase 1 Slice 7 — 입력 페이지 (`/`)
 *
 * 정합:
 *   - work_plan.md Slice 7: ProgressStepper + ErrorCard + PWA manifest
 *   - acceptance.md A5: 입력 페이지 렌더링, 제출 후 /plan 이동
 *   - acceptance.md A2: 비관련 입력 → INV-001 ErrorCard 노출
 *   - design.md §16 (모바일 우선), §19 (44px+ 터치 타겟), §20 (Error UX)
 *
 * Slice 6 대비 변경점:
 *   - inline 1줄 에러 → ErrorCard 컴포넌트 (코드별 메시지/액션)
 *   - "생성 중..." 텍스트 → ProgressStepper (4단계 시각화)
 *   - 에러 페이로드는 /plan 으로 넘기지 않고 입력 페이지에 인라인 표시 (즉시 재입력 가능)
 *
 * Discovery Wizard, Quick Mode 는 Phase 3 에서 추가.
 */

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";

import ErrorCard from "@/components/ErrorCard";
import ProgressStepper, {
  type StepperState,
} from "@/components/ProgressStepper";
import SubmitButton from "@/components/SubmitButton";
import { generate } from "@/lib/api";
import { toDisplayErrorFromCode, type DisplayError } from "@/lib/errors";

const SESSION_STORAGE_KEY = "dreammate.slice6.plan";
const MAX_INPUT_LENGTH = 2000;

export default function HomePage() {
  const router = useRouter();
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [stepperState, setStepperState] = useState<StepperState>("idle");
  const [displayError, setDisplayError] = useState<DisplayError | null>(null);
  const [inputWarning, setInputWarning] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const trimmed = input.trim();
    if (!trimmed) {
      setInputWarning("어떤 영상을 기획하실지 한 줄이라도 적어주세요.");
      return;
    }

    setInputWarning(null);
    setDisplayError(null);
    setIsLoading(true);
    // Phase 1 백엔드는 동기라 실제 단계 콜백이 없다 → planning 단계로 고정 표시.
    // Phase 4+ SSE 가 들어오면 단계별 setStepperState 호출하면 됨.
    setStepperState("planning");

    try {
      const result = await generate({ input: trimmed, locale: "ko-KR" });
      if (result.ok) {
        setStepperState("complete");
        if (typeof window !== "undefined") {
          window.sessionStorage.setItem(
            SESSION_STORAGE_KEY,
            JSON.stringify(result.envelope),
          );
          window.sessionStorage.removeItem(`${SESSION_STORAGE_KEY}.error`);
        }
        router.push("/plan");
        return;
      }

      // 에러 표시. plan/page.tsx 로 넘기지 않고 입력 페이지에 직접 표시
      // → 사용자가 즉시 재입력 가능.
      setDisplayError(
        toDisplayErrorFromCode(
          result.errorCode,
          result.userMessage,
          (result.error.error as { request_id?: string }).request_id,
          result.retryAllowed,
        ),
      );
      setStepperState("idle");
    } catch (unexpected) {
      const message =
        unexpected instanceof Error ? unexpected.message : String(unexpected);
      setDisplayError(
        toDisplayErrorFromCode("UNK-001", `예상치 못한 오류: ${message}`),
      );
      setStepperState("idle");
    } finally {
      setIsLoading(false);
    }
  }

  function handleRetry() {
    setDisplayError(null);
    // 사용자가 텍스트를 그대로 두고 다시 시도 가능하도록 input 은 보존.
  }

  function handleGoHome() {
    setDisplayError(null);
    setInput("");
  }

  return (
    <main className="mx-auto w-full max-w-2xl px-4 py-8 sm:py-12 flex flex-col gap-6">
      <header className="flex flex-col gap-2">
        <p className="text-xs font-semibold tracking-wider uppercase text-primary-600">
          Dreammate Studio
        </p>
        <h1 className="text-2xl sm:text-3xl font-bold text-neutral-900 leading-tight">
          영상기획 AI 에이전트
        </h1>
        <p className="text-sm sm:text-base text-neutral-600 leading-relaxed">
          어떤 영상을 만들지 한 줄로 적어주세요. AI가 기획안 카드로 정리해
          드릴게요.
        </p>
      </header>

      {/* 에러 카드 (입력 위에 노출 → 사용자가 입력 수정 후 재시도) */}
      {displayError && (
        <ErrorCard
          error={displayError}
          onRetry={displayError.canRetry ? handleRetry : undefined}
          onHome={displayError.canGoHome ? handleGoHome : undefined}
        />
      )}

      <form
        onSubmit={handleSubmit}
        className="flex flex-col gap-4"
        aria-describedby={inputWarning ? "input-warning" : undefined}
      >
        <label
          htmlFor="idea-input"
          className="text-sm font-medium text-neutral-900"
        >
          영상 아이디어
        </label>
        <textarea
          id="idea-input"
          name="idea"
          required
          maxLength={MAX_INPUT_LENGTH}
          rows={5}
          placeholder="어떤 영상을 기획하시나요?"
          value={input}
          onChange={(event) => setInput(event.target.value)}
          disabled={isLoading}
          className="w-full rounded-md border border-neutral-200 bg-neutral-0 px-3 py-3 text-base text-neutral-900 placeholder-neutral-400 leading-relaxed focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-1 focus-visible:outline-primary-500 disabled:bg-neutral-100 disabled:text-neutral-500"
        />
        <div className="flex items-center justify-between text-xs text-neutral-500">
          <span aria-live="polite">
            {input.length} / {MAX_INPUT_LENGTH}자
          </span>
        </div>

        {inputWarning && (
          <div
            id="input-warning"
            role="alert"
            className="rounded-md border border-warning-500 bg-warning-50 px-3 py-2 text-sm text-warning-700"
          >
            {inputWarning}
          </div>
        )}

        <SubmitButton isLoading={isLoading}>기획안 만들기</SubmitButton>
      </form>

      {/* 진행 stepper — 제출 중일 때만 노출 */}
      {isLoading && (
        <ProgressStepper currentStep={stepperState} />
      )}

      <footer className="mt-4 text-xs text-neutral-500 leading-relaxed">
        <p>
          Phase 1 MVP — 단일 기획안 1개를 보여드려요. 카드 3개 비교, Discovery
          Wizard, Quick Mode 는 후속 Phase 에서 추가됩니다.
        </p>
      </footer>
    </main>
  );
}
