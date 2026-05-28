"use client";

/**
 * Phase 3 Slice 4 — Quick Mode Step 4 (Generate) page.
 *
 * 흐름: ProgressStepper 4단계 (Intent → RAG → Plan → Critic) → PlanCard 표시
 *
 * 참조:
 *   - apps/web/quick_flow.md §4 (Discovery Step 7과 동일 컴포넌트 / endpoint)
 *   - apps/web/components/ProgressStepper.tsx (Phase 1 기존, import only)
 *   - apps/web/components/PlanCard.tsx (Phase 1 기존, import only)
 *   - docs/contracts/output_schema.md §8 P-006 plan_candidates
 *
 * Slice 4 단독: ProgressStepper의 4단계는 setTimeout으로 단계별 progress mock
 * (Phase 4+ SSE/실 endpoint 호출로 교체).
 */

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import ProgressStepper, {
  type StepperState,
} from "@/components/ProgressStepper";
import PlanCard from "@/components/PlanCard";
import type { Plan } from "@/lib/types";
import {
  saveQuickStep,
  loadQuickStep,
  type QuickStep1State,
  type QuickStep3State,
  type QuickStep4State,
} from "@/lib/quick_state";

/**
 * Slice 4 mock PlanCard 데이터 (Phase 1 PlanCard props 호환).
 * Phase 4+ POST /api/v1/quick/generate 응답 Envelope.body.plans[0] 으로 교체.
 */
function buildMockPlan(directionText: string, prompt: string | null): Plan {
  return {
    plan_id: "quick-mock-plan-001",
    option_index: 0,
    name: "Quick Mode Mock 기획안",
    concept: `${directionText} 기반으로 시청자가 30초 안에 핵심 메시지를 잡을 수 있도록 구성한 정보형 영상.`,
    hook: `${prompt?.slice(0, 30) ?? "이번 영상"}, 30초만 봐도 핵심을 잡는 법`,
    flow: [
      {
        beat_index: 0,
        beat: "오프닝 후킹",
        duration_sec: 5,
        purpose: "시청자 관심 즉시 확보",
      },
      {
        beat_index: 1,
        beat: "핵심 메시지 전달",
        duration_sec: 15,
        purpose: "한 줄 방향의 본문",
      },
      {
        beat_index: 2,
        beat: "근거 / 사례",
        duration_sec: 8,
        purpose: "신뢰도 보강",
      },
      {
        beat_index: 3,
        beat: "마무리 CTA",
        duration_sec: 5,
        purpose: "다음 행동 유도",
      },
    ],
    pros: "짧고 명확. 모바일 시청자 적합.",
    risks: "정보 밀도 높음 — 자막 필요.",
    approach_label: "informational",
    rag_used: [],
  };
}

const STEP_SEQUENCE: StepperState[] = [
  "intent",
  "rag",
  "planning",
  "critic",
  "complete",
];

const STEP_INTERVAL_MS = 600; // mock 진행 속도 (총 ~2.4s)

export default function QuickStep4Page() {
  const router = useRouter();
  const [stepIdx, setStepIdx] = useState<number>(0);
  const [plan, setPlan] = useState<Plan | null>(null);

  useEffect(() => {
    // Step 3 진입 전 직접 URL 접근 차단 (mock): direction state 없으면 Step 1로 복귀
    const step3 = loadQuickStep<QuickStep3State>(3);
    if (!step3?.direction?.text) {
      router.replace("/new/quick");
      return;
    }
    const directionText = step3.direction.text;

    let cancelled = false;
    let timer: ReturnType<typeof setTimeout>;

    function tick(idx: number) {
      if (cancelled) return;
      setStepIdx(idx);
      if (idx >= STEP_SEQUENCE.length - 1) {
        // complete — mock plan 생성 + sessionStorage 저장
        const step1 = loadQuickStep<QuickStep1State>(1);
        const built = buildMockPlan(
          directionText,
          step1?.initialPrompt ?? null,
        );
        setPlan(built);
        const state: QuickStep4State = {
          generatedAt: new Date().toISOString(),
          envelope: { mock: true, plan: built },
        };
        saveQuickStep<QuickStep4State>(4, state);
        return;
      }
      timer = setTimeout(() => tick(idx + 1), STEP_INTERVAL_MS);
    }

    timer = setTimeout(() => tick(1), STEP_INTERVAL_MS);

    return () => {
      cancelled = true;
      if (timer) clearTimeout(timer);
    };
  }, [router]);

  const currentStep = STEP_SEQUENCE[stepIdx] ?? "idle";

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
          기획안 생성 중
        </h1>
        <p className="text-sm text-text-muted">
          AI가 4단계로 영상기획을 만들고 있어요. (30~60초)
        </p>
      </section>

      <section className="px-4 max-w-2xl mx-auto w-full">
        <ProgressStepper currentStep={currentStep} />
      </section>

      {plan && (
        <section className="px-4 py-6 max-w-2xl mx-auto w-full">
          <PlanCard plan={plan} />
        </section>
      )}

      {plan && (
        <footer className="px-4 py-6 max-w-2xl mx-auto w-full">
          <button
            type="button"
            onClick={() => router.push("/new/quick")}
            className="w-full py-3 rounded-md font-medium text-text-muted bg-bg-default border border-border-default hover:bg-bg-subtle transition-colors duration-fast"
            aria-label="처음으로"
          >
            처음으로 ↻
          </button>
        </footer>
      )}
    </main>
  );
}
