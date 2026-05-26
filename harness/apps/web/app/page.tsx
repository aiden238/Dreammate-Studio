"use client";

/**
 * Phase 1 Slice 6 — 입력 페이지 (`/`)
 *
 * 정합:
 *   - work_plan.md Slice 6: 텍스트 입력 + 제출만 (Wizard / Quick Mode 미포함)
 *   - acceptance.md A5: 입력 페이지 렌더링, 제출 후 /plan 이동
 *   - design.md §16 (모바일 우선) / §19 (44px+ 터치 타겟)
 *
 * Discovery Wizard 카드 5장, Generation Stepper, Intent Warning Box 등은
 * Slice 7+ (Polish) 또는 Phase 3 (Discovery / Quick Mode 분리) 에서 추가한다.
 */

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";

import SubmitButton from "@/components/SubmitButton";
import { generate } from "@/lib/api";

const SESSION_STORAGE_KEY = "dreammate.slice6.plan";
const MAX_INPUT_LENGTH = 2000;

export default function HomePage() {
  const router = useRouter();
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const trimmed = input.trim();
    if (!trimmed) {
      setError("어떤 영상을 기획하실지 한 줄이라도 적어주세요.");
      return;
    }

    setError(null);
    setIsLoading(true);

    try {
      const result = await generate({ input: trimmed, locale: "ko-KR" });
      if (result.ok) {
        // sessionStorage에 응답 저장 후 /plan 으로 라우팅 (Slice 6 단순화)
        if (typeof window !== "undefined") {
          window.sessionStorage.setItem(
            SESSION_STORAGE_KEY,
            JSON.stringify(result.envelope),
          );
        }
        router.push("/plan");
        return;
      }

      // 에러: 422 (Intent 차단 / 입력 검증) / 5xx / 네트워크 등 통합 표시
      setError(result.userMessage);
    } catch (unexpected) {
      const message =
        unexpected instanceof Error ? unexpected.message : String(unexpected);
      setError(`예상치 못한 오류가 발생했어요. (${message})`);
    } finally {
      setIsLoading(false);
    }
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

      <form
        onSubmit={handleSubmit}
        className="flex flex-col gap-4"
        aria-describedby={error ? "submit-error" : undefined}
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

        {error && (
          <div
            id="submit-error"
            role="alert"
            className="rounded-md border border-error-500 bg-error-50 px-3 py-2 text-sm text-error-700"
          >
            {error}
          </div>
        )}

        <SubmitButton isLoading={isLoading}>기획안 만들기</SubmitButton>
      </form>

      <footer className="mt-4 text-xs text-neutral-500 leading-relaxed">
        <p>
          Phase 1 MVP — 단일 기획안 1개를 보여드려요. 카드 3개 비교, Discovery
          Wizard, Quick Mode 는 후속 Phase 에서 추가됩니다.
        </p>
      </footer>
    </main>
  );
}
