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
import Link from "next/link";
import { useRouter } from "next/navigation";

import ErrorCard from "@/components/ErrorCard";
import ProgressStepper, {
  type StepperState,
} from "@/components/ProgressStepper";
import SubmitButton from "@/components/SubmitButton";
import { startPlan } from "@/lib/api";
import { toDisplayErrorFromCode, type DisplayError } from "@/lib/errors";

const MAX_INPUT_LENGTH = 2000;

// Phase 29 S1 — 4가지 "상황" 진입 (기능명이 아니라 사용자 상황). 전부 기존 route 재사용.
//   브리프 §6: 첫 화면 버튼은 전문용어(브랜드/도메인/마케팅) 대신 상황 문장.
const SITUATIONS: { label: string; hint: string; href: string }[] = [
  {
    label: "아이디어는 있는데 정리가 안 됐어요",
    hint: "질문을 따라가며 방향을 좁혀드려요",
    href: "/new/discovery/step/1",
  },
  {
    label: "브랜드 방향부터 잡고 싶어요",
    hint: "사람들이 나를 어떻게 기억하면 좋을지부터",
    href: "/new/branding",
  },
  {
    label: "SNS 콘텐츠로 반응을 보고 싶어요",
    hint: "어디에 올려 반응을 볼지 같이 정해요",
    href: "/new/branding?goal=sns_validation",
  },
  {
    label: "바로 영상기획안을 만들고 싶어요",
    hint: "짧게 입력하면 3개를 만들어 비교",
    href: "/new/quick",
  },
];

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
    setStepperState("planning");

    try {
      // ★ Phase 28 S1: 홈도 plans 흐름을 탄다 — startPlan(입력) → /plan/[id].
      //   /plan/[id] 가 generateMultiPlan(credentials 포함=auth) + 영속(plans) + 피드백 UI 를 제공
      //   → 어느 경로로 써도 저장되고 피드백→학습(PKM)으로 이어진다(2nd brain 루프).
      //   (기존 레거시 /generate 단발 = 저장 실패 + 학습 미연결 막다른 길 제거.)
      const { plan_id } = await startPlan(trimmed, "ko-KR");
      setStepperState("complete");
      router.push(`/plan/${plan_id}`);
      return;
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
        <div className="flex items-center justify-between gap-2">
          <p className="text-xs font-semibold tracking-wider uppercase text-primary-600">
            Dreammate Studio
          </p>
          {/* Phase 19 S2 — 2nd brain (PKM) 진입 (additive nav entry). */}
          <Link
            href="/brain"
            className="inline-flex items-center gap-1 min-h-[44px] px-3 rounded-md text-sm font-medium text-primary-600 hover:bg-primary-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-1 focus-visible:outline-primary-500"
            aria-label="내 2nd brain 열기"
          >
            <span aria-hidden>🧠</span> 내 brain
          </Link>
        </div>
        <h1 className="text-2xl sm:text-3xl font-bold text-neutral-900 leading-tight">
          막막한 아이디어를,
          <br />
          실행 가능한 영상기획으로.
        </h1>
        <p className="text-sm sm:text-base text-neutral-600 leading-relaxed">
          브랜드 방향부터 SNS 콘텐츠, 영상기획안까지 — 질문을 따라가며 같이
          정리해 드려요.
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
          지금 만들고 싶은 아이디어를 편하게 적어보세요
        </label>
        <textarea
          id="idea-input"
          name="idea"
          required
          maxLength={MAX_INPUT_LENGTH}
          rows={5}
          placeholder="예: 창업동아리 활동을 쇼츠로 만들고 싶어요"
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

      {/* Phase 29 S1 — 4가지 상황 버튼 (기능명 X, 사용자 상황 O). 기존 route 재사용. */}
      <section
        aria-labelledby="situation-heading"
        className="flex flex-col gap-3 border-t border-neutral-200 pt-6"
      >
        <h2 id="situation-heading" className="text-sm font-semibold text-neutral-900">
          아직 막막하다면, 상황에 맞게 시작해요
        </h2>
        {SITUATIONS.map((s) => (
          <Link
            key={s.href}
            href={s.href}
            className="flex items-center justify-between gap-3 min-h-[44px] rounded-lg border border-neutral-200 px-4 py-3 text-left transition-colors hover:border-primary-400 hover:bg-primary-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-1 focus-visible:outline-primary-500"
            aria-label={s.label}
          >
            <span className="flex flex-col gap-0.5">
              <span className="text-sm font-medium text-neutral-900">{s.label}</span>
              <span className="text-xs text-neutral-600">{s.hint}</span>
            </span>
            <span aria-hidden className="text-neutral-400">›</span>
          </Link>
        ))}
      </section>

      {/* 흐름 표시 — 무엇을 향해 가는지 (브리프 §5.3) */}
      <div className="flex flex-wrap items-center justify-center gap-x-2 gap-y-1 text-xs text-neutral-400">
        {["아이디어", "기억될 이미지", "SNS 콘텐츠", "영상기획안"].map((step, i) => (
          <span key={step} className="flex items-center gap-2">
            {i > 0 && <span aria-hidden>→</span>}
            <span>{step}</span>
          </span>
        ))}
      </div>

      <footer className="mt-2 text-xs text-neutral-500 leading-relaxed">
        <p>
          한 줄만 적어도 기획안 3개를 만들어 비교해 드려요. 로그인하면 피드백이
          내 brain에 쌓여 다음 기획에 반영됩니다(쓸수록 내 브랜드를 학습).
        </p>
      </footer>
    </main>
  );
}
