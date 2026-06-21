"use client";

/**
 * MainFrame — 본문 여백을 AppShell 가시성과 연동 (Phase 34 S2 레이아웃 정렬 fix).
 *
 * 문제: layout.tsx 가 본문에 항상 `desktop:pl-[320px]`(좌측 이중 내비 폭) + `pb-20`(모바일 하단 탭)
 *       을 줬는데, AppShell 은 집중 플로우/인증 경로(/login·/new·/plan)에서 null 을 반환한다.
 *       → 그 경로들에서 사이드바는 없는데 좌측 320px 빈 패딩만 남아 콘텐츠가 우측으로 치우쳤다(PC).
 *
 * 해결: 같은 isShellHidden(pathname) 판정으로, shell 이 보일 때만 여백을 준다.
 *       숨김 경로 → 여백 0 → 콘텐츠가 전체 폭 기준 중앙 정렬(치우침 해소). 모바일도 불필요한 하단 여백 제거.
 *
 * 표현 계층 전용 — 라우팅/네비 기능 무변경(판정 로직은 AppShell 과 단일 출처 공유).
 */

import { usePathname } from "next/navigation";

import { isShellHidden } from "@/components/AppShell";

export default function MainFrame({ children }: { children: React.ReactNode }) {
  const pathname = usePathname() ?? "/";
  const hidden = isShellHidden(pathname);
  return (
    <div className={hidden ? "" : "pb-20 desktop:pb-0 desktop:pl-[320px]"}>
      {children}
    </div>
  );
}
