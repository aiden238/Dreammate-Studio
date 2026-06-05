"use client";

/**
 * AppShell — Phase 27 S2 (B-2 잔여): 지속 네비게이션
 *
 * 정합:
 *   - apps/web/component_map.md: AppShell (모바일 하단 탭바 + 데스크톱 좌측 사이드바)
 *     → S2 최소 구현 = 하단 탭바(전 폭). 데스크톱 좌측 사이드바 full 은 후속(deferred).
 *   - design.md §16 (모바일 우선), 44px+ 터치 타겟.
 *   - 도달성(B-2): 홈에서만이 아니라 "모든 페이지"에서 홈·새 기획·내 brain 이동 가능.
 *
 * HIP-008 S4 는 홈(`/`)에 진입 카드를 추가했고, 본 컴포넌트는 그 진입을 전 페이지 지속 네비로 확장한다.
 * 로그인 화면에서는 숨긴다(인증 흐름 방해 방지).
 */

import Link from "next/link";
import { usePathname } from "next/navigation";

type Tab = {
  href: string;
  label: string;
  icon: string;
  ariaLabel: string;
};

const TABS: Tab[] = [
  { href: "/", label: "홈", icon: "🏠", ariaLabel: "홈 — 빠른 기획" },
  { href: "/new", label: "새 기획", icon: "✏️", ariaLabel: "새 기획 — 마법사/주제발굴" },
  { href: "/brain", label: "내 brain", icon: "🧠", ariaLabel: "내 brain — 지식 구조/PKM" },
];

// 숨길 경로 (인증 등 풀스크린 흐름).
const HIDDEN_PREFIXES = ["/login"];

function isActive(pathname: string, href: string): boolean {
  if (href === "/") return pathname === "/";
  return pathname === href || pathname.startsWith(href + "/");
}

export default function AppShell() {
  const pathname = usePathname() ?? "/";

  if (HIDDEN_PREFIXES.some((p) => pathname === p || pathname.startsWith(p + "/"))) {
    return null;
  }

  return (
    <nav
      aria-label="주요 메뉴"
      className="fixed inset-x-0 bottom-0 z-40 border-t border-neutral-200 bg-neutral-0/95 backdrop-blur"
      style={{ paddingBottom: "env(safe-area-inset-bottom)" }}
    >
      <ul className="mx-auto flex max-w-2xl items-stretch justify-around">
        {TABS.map((tab) => {
          const active = isActive(pathname, tab.href);
          return (
            <li key={tab.href} className="flex-1">
              <Link
                href={tab.href}
                aria-current={active ? "page" : undefined}
                aria-label={tab.ariaLabel}
                className={[
                  "flex min-h-[56px] flex-col items-center justify-center gap-0.5 px-2 py-1 text-xs font-medium transition-colors",
                  "focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-[-2px] focus-visible:outline-primary-500",
                  active
                    ? "text-primary-600"
                    : "text-neutral-500 hover:text-neutral-900 hover:bg-neutral-50",
                ].join(" ")}
              >
                <span aria-hidden className="text-lg leading-none">
                  {tab.icon}
                </span>
                <span>{tab.label}</span>
              </Link>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}
