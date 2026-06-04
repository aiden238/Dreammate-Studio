"use client";

/**
 * Phase 19 Slice S3 — useMediaQuery 훅 (SSR-safe).
 *
 * window.matchMedia 를 구독해 현재 viewport 가 query 에 매치하는지 boolean 으로 반환.
 *   - `/brain` 데스크톱 분기(`(min-width: 1024px)`)에 사용 → 데스크톱일 때만 그래프 lazy-load.
 *   - SSR / 초기 렌더에서는 false 로 시작(서버엔 window 없음). 마운트 후 실제 값 동기화.
 *     → 데스크톱 그래프(react-flow)는 클라이언트 마운트 이후에만 트리거되므로 모바일 번들 미포함.
 *   - change 이벤트 구독 + cleanup (리사이즈/회전 시 토글 반영).
 *
 * 참조: apps/web/app/brain/page.tsx (S3 반응형 분기)
 */

import { useEffect, useState } from "react";

export function useMediaQuery(query: string): boolean {
  const [matches, setMatches] = useState(false);

  useEffect(() => {
    if (typeof window === "undefined" || !window.matchMedia) return;
    const mql = window.matchMedia(query);
    // 마운트 직후 현재 값 동기화 (SSR false → 실제 값).
    setMatches(mql.matches);
    const onChange = (e: MediaQueryListEvent) => setMatches(e.matches);
    mql.addEventListener("change", onChange);
    return () => mql.removeEventListener("change", onChange);
  }, [query]);

  return matches;
}
