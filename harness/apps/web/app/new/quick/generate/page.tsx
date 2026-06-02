"use client";

/**
 * Quick Mode Step 4 (Generate) page.
 *
 * Phase 3 Slice 4: setTimeout mock(buildMockPlan).
 * ★ Phase 14 S2 (위저드 실연결): mock 제거 → 실 백엔드 생성.
 *   수집 입력(step1 prompt / step2 answer / step3 direction)을
 *   startPlan() → wizardStep×3(quick.initial/clarify/direction) → generateMultiPlan()
 *   으로 보내고, 성공 시 /plan/{plan_id} 로 이동 (GET /plans/{id} read).
 *   rich 출력은 백엔드 rich_output_enabled gated 를 자동 상속(별도 배선 0).
 *   ProgressStepper 는 실 generate await(30~60s) 동안 낙관적으로 진행 표시 → 완료 시 navigate.
 *   ★ 랜딩 `/` 경로 무관(behavior-preserving). per-step 실 LLM 카드 = NG1(PARKED PKM/RAG).
 *
 * 참조:
 *   - apps/web/lib/api.ts (startPlan / wizardStep / generateMultiPlan)
 *   - apps/web/app/plan/[plan_id]/page.tsx (목적지 — 백엔드 envelope read + rich PlanCard)
 *   - backend/fastapi/orchestration/moa_orchestrator.py (Phase 14 S1 wizard_data 조립)
 */

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import ProgressStepper, {
  type StepperState,
} from "@/components/ProgressStepper";
import {
  loadQuickStep,
  type QuickStep1State,
  type QuickStep2State,
  type QuickStep3State,
} from "@/lib/quick_state";
import { startPlan, wizardStep, generateMultiPlan } from "@/lib/api";

const STEP_SEQUENCE: StepperState[] = [
  "intent",
  "rag",
  "planning",
  "critic",
  "complete",
];

// 실 generate(30~60s) 동안 cosmetic 진행 (critic 직전까지만 — complete 는 실제 완료 시).
const OPTIMISTIC_INTERVAL_MS = 4000;

export default function QuickStep4Page() {
  const router = useRouter();
  const [stepIdx, setStepIdx] = useState<number>(0);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const startedRef = useRef<boolean>(false);

  useEffect(() => {
    if (startedRef.current) return; // StrictMode 이중 실행 방지
    startedRef.current = true;

    const step3 = loadQuickStep<QuickStep3State>(3);
    if (!step3?.direction?.text) {
      // Step 3(방향 승인) 없이 직접 진입 → 처음으로
      router.replace("/new/quick");
      return;
    }
    const step1 = loadQuickStep<QuickStep1State>(1);
    const step2 = loadQuickStep<QuickStep2State>(2);
    const directionText = step3.editedText?.trim() || step3.direction.text;

    let cancelled = false;
    let timer: ReturnType<typeof setInterval> | undefined;

    async function run(): Promise<void> {
      let idx = 1;
      setStepIdx(idx);
      timer = setInterval(() => {
        idx = Math.min(idx + 1, STEP_SEQUENCE.length - 2); // critic 까지만
        if (!cancelled) setStepIdx(idx);
      }, OPTIMISTIC_INTERVAL_MS);

      try {
        const { plan_id } = await startPlan();
        await wizardStep(plan_id, "quick.initial", {
          user_input: step1?.initialPrompt ?? undefined,
        });
        await wizardStep(plan_id, "quick.clarify", {
          user_input: step2?.followUpAnswer ?? undefined,
          extra: step2?.skipped ? { skipped: true } : {},
        });
        await wizardStep(plan_id, "quick.direction", {
          user_input: directionText,
        });
        const result = await generateMultiPlan(plan_id);
        if (cancelled) return;
        if (timer) clearInterval(timer);
        if (result.ok) {
          setStepIdx(STEP_SEQUENCE.length - 1); // complete
          router.push(`/plan/${encodeURIComponent(plan_id)}`);
        } else {
          setErrorMsg(result.userMessage);
        }
      } catch (e) {
        if (cancelled) return;
        if (timer) clearInterval(timer);
        setErrorMsg(
          e instanceof Error
            ? e.message
            : "기획안 생성 중 오류가 발생했어요. 다시 시도해주세요.",
        );
      }
    }

    void run();

    return () => {
      cancelled = true;
      if (timer) clearInterval(timer);
    };
  }, [router]);

  const currentStep: StepperState = STEP_SEQUENCE[stepIdx] ?? "idle";

  return (
    <main className="min-h-screen bg-bg-default flex flex-col">
      <header className="border-b border-border-default px-4 py-3 sticky top-0 bg-bg-default z-10">
        <div className="max-w-2xl mx-auto flex items-center justify-between">
          <button
            type="button"
            className="text-text-muted text-sm font-medium hover:text-text-default transition-colors duration-fast"
            onClick={() => router.back()}
            aria-label="뒤로 가기"
          >
            {"←"} back
          </button>
          <div className="text-text-muted text-sm font-medium">Quick · 4</div>
          <div className="w-12" aria-hidden="true" />
        </div>
      </header>

      <section className="px-4 py-6 max-w-2xl mx-auto w-full">
        <h1 className="text-3xl font-bold text-text-default mb-2">
          {errorMsg ? "생성 실패" : "기획안 생성 중"}
        </h1>
        <p className="text-sm text-text-muted">
          {errorMsg
            ? "잠시 후 다시 시도하거나 처음부터 다시 만들어주세요."
            : "AI가 영상기획안 3개를 만들고 있어요. (30~60초)"}
        </p>
      </section>

      {!errorMsg && (
        <section className="px-4 max-w-2xl mx-auto w-full">
          <ProgressStepper currentStep={currentStep} />
        </section>
      )}

      {errorMsg && (
        <section className="px-4 py-6 max-w-2xl mx-auto w-full">
          <div
            role="alert"
            className="rounded-md border border-border-default bg-bg-subtle px-4 py-3 text-sm text-text-default"
          >
            {errorMsg}
          </div>
          <div className="mt-4 flex flex-col gap-3">
            <button
              type="button"
              onClick={() => window.location.reload()}
              className="w-full py-3 rounded-md font-semibold text-text-inverse bg-primary hover:bg-primary-hover active:bg-primary-pressed transition-colors duration-fast"
              aria-label="다시 시도"
            >
              다시 시도 ↻
            </button>
            <button
              type="button"
              onClick={() => router.push("/new/quick")}
              className="w-full py-3 rounded-md font-medium text-text-muted bg-bg-default border border-border-default hover:bg-bg-subtle transition-colors duration-fast"
              aria-label="처음으로"
            >
              처음으로
            </button>
          </div>
        </section>
      )}
    </main>
  );
}
