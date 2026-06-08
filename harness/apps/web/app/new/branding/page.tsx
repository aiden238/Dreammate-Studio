"use client";

/**
 * Phase 18 Slice S3 — Branding (주제 추천 / 스무고개) 페이지.
 *
 * "무엇을 찍을지 모르겠는" 사용자를 위한 콜드스타트 해소 흐름 (design.md §2-1).
 * LLM 동적 스무고개(Akinator식)로 좁혀 후보 영상 주제 3개를 발굴 → 택1 → 기존 3안 생성.
 *
 * 흐름:
 *   mount(★ StrictMode-safe startedRef 가드)
 *     → startPlan("(브랜딩 세션)") → plan_id 보관 → brandingNext(plan_id, {}) → 첫 질문
 *   Q&A loop:
 *     선택 카드(2~4개) 클릭 → brandingNext({selected_option})
 *     자유 입력 제출      → brandingNext({answer})
 *     mode==="ask" 동안 반복 (진행바 step/max_questions)
 *   done:
 *     brandingFinalize(plan_id) → 후보 주제 3개 카드
 *   pick(택1) — Phase 18 S4:
 *     brandingSelect(planId, candidate)  ★ FIRST (best-effort)
 *       → backend 가 SAME plan 의 initial_input 을 택1 주제로 설정(planning 연결) +
 *         gated+authed 일 때 브랜딩 방향을 brand_memory 로 시드(발굴→축적→주입 P17 루프)
 *     → generateMultiPlan(planId)  ★ SAME plan 재사용 (startPlan 재호출 X — initial_input 이 이미 주제)
 *     → router.push('/plan/'+planId)
 *     ★ select 실패 → 여전히 generate 로 진행(seed 는 부가 단계, 흐름 차단 0). 단, select 가 주제를
 *       설정하므로 select 가 네트워크로 실패하면 initial_input 미설정 → fallback 으로 그때 startPlan(topic).
 *
 * ★ StrictMode (P-STRICTMODE-ONESHOT-001, meta/retrospectives/phase-14.md):
 *   mount 1회-실행 effect 는 `startedRef` 가드로만 중복 실행을 막는다.
 *   `cancelled` 플래그(cleanup 에서 set)는 쓰지 않는다 — dev 이중 invoke 시 첫 cleanup 이
 *   유일한 run 의 side-effect(질문 표시)를 취소하는 데드락을 유발하기 때문.
 *
 * 참조:
 *   - apps/web/app/new/quick/generate/page.tsx (★ startedRef 패턴 원형 + 에러 UI)
 *   - apps/web/lib/api.ts (startPlan / brandingNext / brandingFinalize / generateMultiPlan)
 *   - apps/web/components/discovery/BrandDirectionCard.tsx (선택 카드 UX 일관)
 *   - apps/web/design.md §2 (콜드스타트 / 카드 단위 / 모바일 한 손 / 제작 기능 미포함)
 *
 * Phase 18 S4: 택1 시 brandingSelect 로 planning 연결 + brand_memory 시드(gated+authed, best-effort).
 *   e2e 라이브 = S5.
 */

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import {
  startPlan,
  brandingNext,
  brandingFinalize,
  brandingSelect,
  generateMultiPlan,
} from "@/lib/api";
import type { BrandingCandidate } from "@/lib/types";

type Phase = "loading" | "qa" | "finalizing" | "candidates" | "generating";

const FREE_TEXT_MAX = 200;

export default function BrandingPage() {
  const router = useRouter();
  const startedRef = useRef<boolean>(false);

  // plan_id 는 effect/handler 양쪽에서 참조 — ref 로 보관(렌더 무관, 안정 식별자).
  const planIdRef = useRef<string | null>(null);

  const [phase, setPhase] = useState<Phase>("loading");
  const [question, setQuestion] = useState<string | null>(null);
  const [options, setOptions] = useState<string[]>([]);
  const [step, setStep] = useState<number>(0);
  const [maxQuestions, setMaxQuestions] = useState<number>(0);
  const [freeText, setFreeText] = useState<string>("");
  const [candidates, setCandidates] = useState<BrandingCandidate[]>([]);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  // 답변 전송/생성 중 입력 잠금 (중복 호출 방지).
  const [busy, setBusy] = useState<boolean>(false);
  // Phase 29 — 상황 버튼 목표(?goal). SNS 등 목표별 질문 프레이밍 + 인트로 배너.
  const [goalLabel, setGoalLabel] = useState<string | null>(null);

  // ── mount: plan 시작 + 첫 질문 (★ startedRef 가드, cancelled 플래그 미사용) ──
  useEffect(() => {
    if (startedRef.current) return; // StrictMode 이중 실행 방지
    startedRef.current = true;

    async function bootstrap(): Promise<void> {
      try {
        // Phase 29 — ?goal(상황 버튼) 읽어 첫 호출에 전달 → 질문 프레이밍 분기.
        const goal =
          new URLSearchParams(window.location.search).get("goal") || undefined;
        const labels: Record<string, string> = {
          sns_validation: "SNS에서 반응을 볼 콘텐츠 방향을 같이 찾아요",
          organize: "막연한 아이디어를 질문으로 정리해 드려요",
        };
        if (goal && labels[goal]) setGoalLabel(labels[goal]);
        const { plan_id } = await startPlan("(브랜딩 세션)");
        planIdRef.current = plan_id;
        const res = await brandingNext(plan_id, goal ? { goal } : {});
        applyNext(res);
      } catch (e) {
        setErrorMsg(friendlyError(e));
      }
    }

    void bootstrap();
    // cleanup 없음 — 타이머/구독 없고, navigation 같은 핵심 side-effect 를 막지 않는다.
    // ★ 의도된 mount 1회-실행 (startedRef 가드). applyNext 를 deps 에 넣지 않는다 —
    //   재실행이 목적이 아니라 1회 부트스트랩이므로 (P-STRICTMODE-ONESHOT-001).
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // brandingNext 응답을 화면 상태로 반영. mode==="done" 이면 finalize 로 진행.
  function applyNext(res: {
    mode: "ask" | "done";
    question: string | null;
    options: string[] | null;
    step: number;
    max_questions: number;
  }): void {
    setStep(res.step);
    setMaxQuestions(res.max_questions);
    if (res.mode === "done") {
      void runFinalize();
      return;
    }
    setQuestion(res.question);
    setOptions(Array.isArray(res.options) ? res.options : []);
    setFreeText("");
    setPhase("qa");
  }

  // 답변(카드 선택 또는 자유입력) 전송 → 다음 질문.
  async function submitAnswer(body: {
    selected_option?: string;
    answer?: string;
  }): Promise<void> {
    const planId = planIdRef.current;
    if (!planId || busy) return;
    setBusy(true);
    setErrorMsg(null);
    try {
      const res = await brandingNext(planId, body);
      applyNext(res);
    } catch (e) {
      setErrorMsg(friendlyError(e));
    } finally {
      setBusy(false);
    }
  }

  async function runFinalize(): Promise<void> {
    const planId = planIdRef.current;
    if (!planId) return;
    setPhase("finalizing");
    setErrorMsg(null);
    try {
      const res = await brandingFinalize(planId);
      const list = Array.isArray(res.candidates) ? res.candidates : [];
      if (list.length === 0) {
        setErrorMsg(
          "후보 주제를 만들지 못했어요. 처음부터 다시 시도해주세요.",
        );
        return;
      }
      setCandidates(list);
      setPhase("candidates");
    } catch (e) {
      setErrorMsg(friendlyError(e));
    }
  }

  // 후보 주제 택1 (Phase 18 S4):
  //   1) brandingSelect(SAME plan, candidate) — backend 가 initial_input 을 택1 주제로 설정(planning
  //      연결) + gated+authed 일 때 브랜딩 방향을 brand_memory 시드. ★ best-effort (실패해도 진행).
  //   2) 성공 시 SAME plan 재사용해 generateMultiPlan (initial_input 이 이미 주제 → startPlan 불필요).
  //   3) select 가 네트워크로 실패하면 initial_input 미설정 → fallback 으로 startPlan(topic) 후 generate.
  async function pickCandidate(candidate: BrandingCandidate): Promise<void> {
    if (busy) return;
    setBusy(true);
    setErrorMsg(null);
    setPhase("generating");
    try {
      // SAME branding plan 재사용 (mount 에서 보관한 planIdRef). select 가 그 plan 에 주제를 설정한다.
      let targetPlanId = planIdRef.current;
      let selected = false;
      if (targetPlanId) {
        try {
          await brandingSelect(targetPlanId, {
            topic: candidate.topic,
            tone: candidate.tone,
            target: candidate.target,
            format: candidate.format,
          });
          selected = true; // initial_input 이 SAME plan 에 설정됨 → 그대로 generate.
        } catch {
          // ★ select 실패(네트워크/404 등) → seed 는 부가 단계이므로 흐름 차단 X.
          //   단, initial_input 이 설정 안 됐으므로 아래 fallback 으로 새 plan 을 주제로 생성한다.
          selected = false;
        }
      }
      // fallback — select 누락/실패 시 택1 주제로 새 plan 생성 (기존 S3 경로 보존).
      if (!targetPlanId || !selected) {
        const started = await startPlan(candidate.topic);
        targetPlanId = started.plan_id;
      }

      const result = await generateMultiPlan(targetPlanId);
      if (result.ok) {
        router.push(`/plan/${encodeURIComponent(targetPlanId)}`);
      } else {
        setErrorMsg(result.userMessage);
        setPhase("candidates");
        setBusy(false);
      }
    } catch (e) {
      setErrorMsg(friendlyError(e));
      setPhase("candidates");
      setBusy(false);
    }
  }

  const freeTextOver = freeText.length > FREE_TEXT_MAX;
  const freeTextDisabled = busy || freeText.trim().length === 0 || freeTextOver;
  const headerStep =
    maxQuestions > 0 ? `질문 ${Math.min(step, maxQuestions)} / ${maxQuestions}` : "준비 중";

  return (
    <main className="min-h-screen bg-bg-default flex flex-col">
      {/* Header */}
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
          <div className="text-text-muted text-sm font-medium">주제 추천</div>
          <div className="w-12" aria-hidden="true" />
        </div>
      </header>

      {/* 진행바 (Q&A 단계에서만) */}
      {(phase === "qa" || phase === "finalizing") && maxQuestions > 0 && (
        <div className="px-4 pt-4 max-w-2xl mx-auto w-full">
          <div className="flex items-center justify-between text-xs text-text-muted mb-1">
            <span aria-live="polite">{headerStep}</span>
          </div>
          <div
            className="h-1.5 w-full rounded-full bg-bg-subtle overflow-hidden"
            role="progressbar"
            aria-valuemin={0}
            aria-valuemax={maxQuestions}
            aria-valuenow={Math.min(step, maxQuestions)}
            aria-label="스무고개 진행도"
          >
            <div
              className="h-full bg-primary transition-all duration-fast"
              style={{
                width: `${Math.min(100, (Math.min(step, maxQuestions) / maxQuestions) * 100)}%`,
              }}
            />
          </div>
        </div>
      )}

      {/* Title */}
      <section className="px-4 py-6 max-w-2xl mx-auto w-full">
        <h1 className="text-3xl font-bold text-text-default mb-2">
          {phase === "candidates"
            ? "이런 주제는 어때요?"
            : phase === "generating"
              ? "기획안 생성 중"
              : "무엇을 찍을지 같이 찾아봐요"}
        </h1>
        <p className="text-sm text-text-muted">
          {phase === "loading" && "첫 질문을 준비하고 있어요…"}
          {phase === "qa" &&
            "몇 가지 질문에 답하면 AI가 어울리는 주제를 골라드려요."}
          {phase === "finalizing" && "답변을 모아 주제를 좁히고 있어요…"}
          {phase === "candidates" &&
            "마음에 드는 주제를 하나 고르면 기획안 3개를 만들어드려요."}
          {phase === "generating" &&
            "고른 주제로 영상기획안 3개를 만들고 있어요. (30~60초)"}
        </p>
        {/* Phase 29 — 상황 버튼 목표 인트로 (예: SNS 반응) → 질문이 그 목표로 분기됨 */}
        {goalLabel && (phase === "qa" || phase === "loading") && (
          <div className="mt-3 rounded-md border border-primary-200 bg-primary-50 px-3 py-2 text-sm text-primary-700">
            🎯 {goalLabel}
          </div>
        )}
      </section>

      {/* 에러 */}
      {errorMsg && (
        <section className="px-4 pb-4 max-w-2xl mx-auto w-full">
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
              aria-label="처음부터 다시 시도"
            >
              처음부터 다시 ↻
            </button>
            <button
              type="button"
              onClick={() => router.push("/new")}
              className="w-full py-3 rounded-md font-medium text-text-muted bg-bg-default border border-border-default hover:bg-bg-subtle transition-colors duration-fast"
              aria-label="다른 방법으로 시작"
            >
              다른 방법으로 시작
            </button>
          </div>
        </section>
      )}

      {/* 로딩 / 생성 중 스피너 */}
      {!errorMsg &&
        (phase === "loading" ||
          phase === "finalizing" ||
          phase === "generating") && (
          <section className="flex-1 flex items-center justify-center px-4 py-10">
            <div
              className="w-8 h-8 border-2 border-border-default border-t-primary rounded-full animate-spin"
              aria-label="처리 중"
              role="status"
            />
          </section>
        )}

      {/* Q&A — 선택 카드 + 자유 입력 */}
      {!errorMsg && phase === "qa" && (
        <section className="flex-1 px-4 pb-10 max-w-2xl mx-auto w-full">
          {question && (
            <h2
              aria-live="polite"
              className="text-text-default font-semibold text-lg mb-4 leading-normal"
            >
              Q. {question}
            </h2>
          )}

          {/* 선택지 카드 (2~4개) */}
          {options.length > 0 && (
            <div
              role="group"
              aria-label="선택지 카드"
              className="flex flex-col gap-3 mb-6"
            >
              {options.map((opt, i) => (
                <button
                  key={`${i}-${opt}`}
                  type="button"
                  disabled={busy}
                  onClick={() => void submitAnswer({ selected_option: opt })}
                  className="w-full text-left p-4 rounded-lg border border-border-default bg-surface text-base text-text-default leading-normal transition-all duration-fast hover:bg-bg-subtle hover:scale-[1.01] focus:outline-none focus:border-border-focus focus:border-2 disabled:opacity-50 disabled:cursor-not-allowed"
                  aria-label={`선택: ${opt}`}
                >
                  {opt}
                </button>
              ))}
            </div>
          )}

          {/* 자유 입력 (기타 / 직접 입력) */}
          <div className="bg-surface border border-border-default rounded-md p-3 focus-within:border-border-focus focus-within:border-2 transition-colors duration-fast">
            <label
              htmlFor="branding-free-text"
              className="block text-sm font-medium text-text-muted mb-2"
            >
              기타 / 직접 입력
            </label>
            <textarea
              id="branding-free-text"
              value={freeText}
              onChange={(e) => setFreeText(e.target.value)}
              placeholder="예: 위 보기에 없어요. 직접 적을게요."
              rows={3}
              disabled={busy}
              aria-label="직접 답변 입력"
              aria-multiline="true"
              aria-invalid={freeTextOver ? true : undefined}
              className="w-full text-text-default placeholder:text-text-placeholder bg-transparent border-none outline-none resize-none text-base disabled:opacity-50"
            />
            <div
              aria-live="polite"
              className={`text-xs text-right mt-1 ${
                freeTextOver ? "text-text-danger font-medium" : "text-text-muted"
              }`}
            >
              {freeText.length} / {FREE_TEXT_MAX}
            </div>
          </div>
          <button
            type="button"
            disabled={freeTextDisabled}
            onClick={() => void submitAnswer({ answer: freeText.trim() })}
            className="mt-3 w-full py-3 rounded-md font-semibold text-text-inverse bg-primary hover:bg-primary-hover active:bg-primary-pressed disabled:bg-primary-disabled disabled:cursor-not-allowed transition-colors duration-fast"
            aria-label="직접 입력한 답변으로 진행"
          >
            {busy ? "처리 중…" : "이 답변으로 진행 ▶"}
          </button>
        </section>
      )}

      {/* 후보 주제 카드 (택1) */}
      {!errorMsg && phase === "candidates" && (
        <section className="flex-1 px-4 pb-10 max-w-2xl mx-auto w-full">
          <div
            role="group"
            aria-label="후보 주제 카드"
            className="flex flex-col gap-4"
          >
            {candidates.map((c, i) => (
              <button
                key={`${i}-${c.topic}`}
                type="button"
                disabled={busy}
                onClick={() => void pickCandidate(c)}
                className="w-full text-left p-4 rounded-lg border border-border-default bg-surface transition-all duration-fast hover:bg-bg-subtle hover:scale-[1.01] focus:outline-none focus:border-border-focus focus:border-2 disabled:opacity-50 disabled:cursor-not-allowed"
                aria-label={`주제 선택: ${c.topic}`}
              >
                <div className="font-semibold text-lg text-text-default mb-2 leading-normal">
                  {c.topic}
                </div>
                <div className="flex flex-wrap gap-2 mb-3">
                  {c.tone && (
                    <span className="text-xs px-2 py-0.5 rounded-full bg-bg-subtle text-text-muted">
                      톤 · {c.tone}
                    </span>
                  )}
                  {c.target && (
                    <span className="text-xs px-2 py-0.5 rounded-full bg-bg-subtle text-text-muted">
                      타깃 · {c.target}
                    </span>
                  )}
                  {c.format && (
                    <span className="text-xs px-2 py-0.5 rounded-full bg-bg-subtle text-text-muted">
                      포맷 · {c.format}
                    </span>
                  )}
                </div>
                {c.why_fit && (
                  <div className="text-sm text-text-muted leading-normal border-t border-border-subtle pt-3">
                    {c.why_fit}
                  </div>
                )}
              </button>
            ))}
          </div>
        </section>
      )}
    </main>
  );
}

function friendlyError(e: unknown): string {
  if (e instanceof Error && e.message) {
    if (e.message.startsWith("branding_") || e.message.startsWith("startPlan")) {
      return "주제를 찾는 중 문제가 생겼어요. 잠시 후 다시 시도해주세요.";
    }
    return e.message;
  }
  return "문제가 생겼어요. 잠시 후 다시 시도해주세요.";
}
