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
 * Phase 30 Slice 3 — 시각 리스킨 (orange × beige 종이 워크스페이스).
 *   기능(핸들러/상태/API 호출/route href)은 전부 보존. 표현 계층만 변경:
 *     - 중앙 Hero(Paperlogy 제목 + 핵심구 웜 그라데이션)
 *     - 따뜻한 prompt panel(큰 입력 + 📎 첨부)
 *     - 4 상황 시작카드(웜 종이 카드)
 *     - 주황 primary CTA(기획안 만들기)
 *   참조: design_reference/VISUAL_CONTRACT.md, COMPONENT_MAPPING.md §4,
 *         reference/index.html (시각 기준 — 정적 HTML 미복제).
 *
 * Discovery Wizard, Quick Mode 는 Phase 3 에서 추가.
 */

import { FormEvent, useRef, useState } from "react";
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
// Phase 30 S3 — 웜 종이 시작카드용 kicker 라벨 추가(시각 전용, route/문구 불변).
const SITUATIONS: {
  label: string;
  hint: string;
  href: string;
  kicker: string;
}[] = [
  {
    label: "아이디어는 있는데 정리가 안 됐어요",
    hint: "질문을 따라가며 방향을 좁혀드려요",
    href: "/new/discovery/step/1",
    kicker: "01 · Discovery",
  },
  {
    label: "브랜드 방향부터 잡고 싶어요",
    hint: "사람들이 나를 어떻게 기억하면 좋을지부터",
    href: "/new/branding",
    kicker: "02 · Branding",
  },
  {
    label: "SNS 콘텐츠로 반응을 보고 싶어요",
    hint: "어디에 올려 반응을 볼지 같이 정해요",
    href: "/new/branding?goal=sns_validation",
    kicker: "03 · Validation",
  },
  {
    label: "바로 영상기획안을 만들고 싶어요",
    hint: "짧게 입력하면 3개를 만들어 비교",
    href: "/new/quick",
    kicker: "04 · Quick Plan",
  },
];

export default function HomePage() {
  const router = useRouter();
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [stepperState, setStepperState] = useState<StepperState>("idle");
  const [displayError, setDisplayError] = useState<DisplayError | null>(null);
  const [inputWarning, setInputWarning] = useState<string | null>(null);
  // Phase 29 A — 멀티모달 레퍼런스(이미지) 첨부 (base64 data URL, 최대 4장).
  const [images, setImages] = useState<string[]>([]);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  function handleFiles(files: FileList | null) {
    if (!files) return;
    const room = 4 - images.length;
    Array.from(files)
      .slice(0, Math.max(0, room))
      .forEach((f) => {
        if (!f.type.startsWith("image/")) return;
        if (f.size > 5 * 1024 * 1024) {
          setInputWarning("이미지는 5MB 이하만 첨부할 수 있어요.");
          return;
        }
        const reader = new FileReader();
        reader.onload = () => {
          const url = reader.result;
          if (typeof url === "string") {
            setImages((prev) => (prev.length >= 4 ? prev : [...prev, url]));
          }
        };
        reader.readAsDataURL(f);
      });
  }

  function removeImage(i: number) {
    setImages((prev) => prev.filter((_, idx) => idx !== i));
  }

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
      const { plan_id } = await startPlan(
        trimmed,
        "ko-KR",
        images.length > 0 ? images : undefined, // Phase 29 A — 첨부 레퍼런스 전달
      );
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
    <main className="mx-auto w-full max-w-2xl px-4 py-10 sm:py-16 flex flex-col gap-8">
      {/* ── Hero — 중앙 정렬, Paperlogy 제목 + 핵심구 웜 그라데이션 ── */}
      <header className="flex flex-col items-center gap-3 text-center">
        <div className="flex w-full items-center justify-between gap-2">
          <p className="text-[11px] font-bold tracking-[0.12em] uppercase text-primary-600">
            Guided Video Planning
          </p>
          {/* Phase 19 S2 — 2nd brain (PKM) 진입 (additive nav entry). */}
          <Link
            href="/brain"
            className="inline-flex items-center gap-1 min-h-[44px] px-3 rounded-xl text-sm font-medium text-primary-700 hover:bg-primary-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-1 focus-visible:outline-primary-500"
            aria-label="내 2nd brain 열기"
          >
            <span aria-hidden>🧠</span> 내 brain
          </Link>
        </div>
        <h1 className="font-display text-3xl sm:text-[2.6rem] font-extrabold text-neutral-900 leading-[1.18] tracking-tight text-balance">
          막연한 아이디어를,
          <br />
          <span className="bg-gradient-to-r from-primary-300 via-primary-500 to-primary-700 bg-clip-text text-transparent">
            기억되는 영상 기획
          </span>
          으로.
        </h1>
        <p className="max-w-md text-sm sm:text-base text-neutral-600 leading-relaxed">
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
          className="text-sm font-medium text-neutral-700"
        >
          지금 만들고 싶은 아이디어를 편하게 적어보세요
        </label>
        {/* Phase 30 S3 — 따뜻한 프롬프트 패널(크림 surface + 웜 보더 + 옅은 그림자) + 멀티모달 첨부 */}
        <div className="rounded-2xl border border-neutral-200 bg-neutral-50 shadow-[0_10px_30px_-18px_rgba(86,55,36,0.35)] transition-colors focus-within:border-primary-400 focus-within:ring-2 focus-within:ring-primary-100">
          <textarea
            id="idea-input"
            name="idea"
            required
            maxLength={MAX_INPUT_LENGTH}
            rows={4}
            placeholder="예: 창업동아리 활동을 쇼츠로 만들고 싶어요"
            value={input}
            onChange={(event) => setInput(event.target.value)}
            disabled={isLoading}
            className="w-full resize-none rounded-2xl border-0 bg-transparent px-4 pt-4 pb-1 text-base text-neutral-900 placeholder-neutral-400 leading-relaxed outline-none disabled:text-neutral-500"
          />
          {images.length > 0 && (
            <div className="flex flex-wrap gap-2 px-3 pb-1">
              {images.map((src, i) => (
                <div key={i} className="relative">
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img
                    src={src}
                    alt={`레퍼런스 ${i + 1}`}
                    className="h-14 w-14 rounded-lg border border-neutral-200 object-cover"
                  />
                  <button
                    type="button"
                    onClick={() => removeImage(i)}
                    aria-label={`레퍼런스 ${i + 1} 제거`}
                    className="absolute -right-1.5 -top-1.5 flex h-4 w-4 items-center justify-center rounded-full bg-neutral-800 text-[10px] leading-none text-neutral-0"
                  >
                    ×
                  </button>
                </div>
              ))}
            </div>
          )}
          <div className="flex items-center justify-between px-3 pb-2.5 pt-1">
            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              disabled={isLoading || images.length >= 4}
              title="레퍼런스 이미지 첨부 (무드보드·참고 영상 캡처 등, 최대 4장)"
              className="inline-flex items-center gap-1 rounded-lg px-2 py-1 text-xs text-neutral-500 transition-colors hover:bg-primary-50 hover:text-primary-700 disabled:cursor-not-allowed disabled:text-neutral-300"
            >
              <span aria-hidden>📎</span> 레퍼런스 첨부
              {images.length > 0 ? ` (${images.length}/4)` : ""}
            </button>
            <span aria-live="polite" className="text-xs text-neutral-400">
              {input.length} / {MAX_INPUT_LENGTH}
            </span>
          </div>
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            multiple
            className="hidden"
            onChange={(e) => {
              handleFiles(e.target.files);
              e.target.value = "";
            }}
          />
        </div>

        {inputWarning && (
          <div
            id="input-warning"
            role="alert"
            className="rounded-lg border border-warning-500 bg-warning-50 px-3 py-2 text-sm text-warning-700"
          >
            {inputWarning}
          </div>
        )}

        <SubmitButton isLoading={isLoading}>기획안 만들기</SubmitButton>
      </form>

      {/* 진행 stepper — 제출 중일 때만 노출 */}
      {isLoading && <ProgressStepper currentStep={stepperState} />}

      {/* Phase 30 S3 — 4가지 상황 = 웜 종이 시작카드 (기능명 X, 사용자 상황 O). 기존 route 재사용. */}
      <section
        aria-labelledby="situation-heading"
        className="flex flex-col gap-4 border-t border-neutral-200 pt-8"
      >
        <h2
          id="situation-heading"
          className="font-display text-lg font-bold text-neutral-900 tracking-tight"
        >
          아직 막막하다면, 상황에 맞게 시작해요
        </h2>
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
          {SITUATIONS.map((s) => (
            <Link
              key={s.href}
              href={s.href}
              className="group relative flex min-h-[44px] flex-col gap-2 overflow-hidden rounded-2xl border border-neutral-200 bg-neutral-50 p-4 text-left transition-colors hover:border-primary-400 hover:bg-primary-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-1 focus-visible:outline-primary-500"
              aria-label={s.label}
            >
              {/* 종이 위 옅은 주황 광원 (장식, 약하게 — VISUAL_CONTRACT §6 서적 카드) */}
              <span
                aria-hidden
                className="pointer-events-none absolute -right-8 -bottom-10 h-28 w-28 rounded-full bg-primary-100/60 blur-2xl"
              />
              <span className="relative text-[11px] font-bold uppercase tracking-[0.08em] text-primary-600">
                {s.kicker}
              </span>
              <span className="relative flex flex-col gap-1">
                <span className="font-display text-base font-bold text-neutral-900 leading-snug">
                  {s.label}
                </span>
                <span className="text-xs text-neutral-600 leading-relaxed">
                  {s.hint}
                </span>
              </span>
              <span
                aria-hidden
                className="relative mt-1 inline-flex items-center text-xs font-semibold text-primary-700"
              >
                시작하기
                <span className="ml-1 transition-transform group-hover:translate-x-0.5">
                  →
                </span>
              </span>
            </Link>
          ))}
        </div>
      </section>

      {/* 흐름 표시 — 무엇을 향해 가는지 (브리프 §5.3) */}
      <div className="flex flex-wrap items-center justify-center gap-x-2 gap-y-1 text-xs text-neutral-400">
        {["아이디어", "기억될 이미지", "SNS 콘텐츠", "영상기획안"].map(
          (step, i) => (
            <span key={step} className="flex items-center gap-2">
              {i > 0 && (
                <span aria-hidden className="text-primary-300">
                  →
                </span>
              )}
              <span>{step}</span>
            </span>
          ),
        )}
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
