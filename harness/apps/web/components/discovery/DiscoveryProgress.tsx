"use client";

/**
 * Phase 29 S3 — 아키네이터 진행 요약 (브리프 §7.4).
 *
 * "왜 이 질문에 답하고 있지?"를 줄이기 위해, 정리 중인 차원(기억느낌→주제→시리즈→누구에게→톤)을
 * 칩으로 보여주고 완료(✓)·현재 단계를 표시한다. sessionStorage 는 client-only 이므로
 * mount 후(useEffect) 읽는다(SSR 안전).
 */

import { useEffect, useState } from "react";

import { loadDiscoveryStep1, loadDiscoveryStep } from "@/lib/discovery_state";

const DIMS: { n: number; label: string }[] = [
  { n: 1, label: "기억 느낌" },
  { n: 2, label: "주제 영역" },
  { n: 3, label: "시리즈" },
  { n: 4, label: "누구에게" },
  { n: 5, label: "톤" },
];

function isDone(n: number): boolean {
  try {
    if (n === 1) return !!loadDiscoveryStep1()?.selectedCardId;
    if (n === 5) {
      const s = loadDiscoveryStep(5);
      return !!(s && ((s.selectedTones && s.selectedTones.length > 0) || s.skipped));
    }
    const s = loadDiscoveryStep(n as 2 | 3 | 4);
    return !!s?.selectedCardId;
  } catch {
    return false;
  }
}

export default function DiscoveryProgress({ currentStep }: { currentStep: number }) {
  const [doneMap, setDoneMap] = useState<Record<number, boolean>>({});

  useEffect(() => {
    const m: Record<number, boolean> = {};
    for (const d of DIMS) m[d.n] = isDone(d.n);
    setDoneMap(m);
  }, [currentStep]);

  return (
    <div
      aria-label="정리 진행 상황"
      className="flex flex-wrap items-center gap-1.5 text-xs text-text-muted"
    >
      <span className="font-medium">정리 중</span>
      {DIMS.map((d) => {
        const done = doneMap[d.n];
        const current = d.n === currentStep;
        return (
          <span
            key={d.n}
            className={[
              "rounded-full px-2 py-0.5",
              current
                ? "bg-primary-100 text-primary-700 font-semibold"
                : done
                  ? "bg-success-50 text-success-700"
                  : "bg-neutral-100 text-neutral-400",
            ].join(" ")}
          >
            {done && !current ? "✓ " : ""}
            {d.label}
          </span>
        );
      })}
    </div>
  );
}
