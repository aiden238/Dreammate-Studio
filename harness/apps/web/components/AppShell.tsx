"use client";

/**
 * AppShell — Phase 27 S2(B-2) 지속 네비게이션 → Phase 30 S2 리브랜딩(이중 내비)
 *
 * 정합:
 *   - apps/web/component_map.md: AppShell (모바일 하단 탭바 + 데스크톱 좌측 사이드바)
 *   - design.md §16 (모바일 우선), 44px+ 터치 타겟.
 *   - 도달성(B-2): 모든 페이지에서 홈·새 기획·내 brain 이동 가능.
 *   - design_reference/VISUAL_CONTRACT.md §5 / COMPONENT_MAPPING.md §3 (이중 내비):
 *       데스크톱(≥1024px) = Primary Rail(72–76px) + Secondary Sidebar(220–260px),
 *       모바일(<1024px) = 기존 하단 탭바 그대로 유지.
 *
 * Phase 30 S2 — 표현 계층만 변경:
 *   - 기능(라우팅 href·active 판정·HIDDEN_PREFIXES·aria-current·safe-area)은 100% 보존.
 *   - 데스크톱 이중 내비는 lg(≥1024px)에서만 표시(fixed, 문서 흐름 비침습),
 *     모바일 하단 탭바는 lg에서 숨김 — 한 화면에 둘 중 하나만 노출.
 *   - 색: rail #573A2A 계열(rail / rail-text 토큰), 사이드바 = 베이지 표면(neutral-50).
 *     주황은 active 표시에만 제한적으로 사용(VISUAL_CONTRACT §3).
 */

import Link from "next/link";
import { usePathname } from "next/navigation";

type Tab = {
  href: string;
  label: string;
  icon: string;
  ariaLabel: string;
};

// 모바일 하단 탭 — 기존 그대로(도달성 핵심 3개). 변경 금지.
const TABS: Tab[] = [
  { href: "/", label: "홈", icon: "🏠", ariaLabel: "홈 — 빠른 기획" },
  { href: "/new", label: "새 기획", icon: "✏️", ariaLabel: "새 기획 — 마법사/주제발굴" },
  { href: "/brain", label: "내 brain", icon: "🧠", ariaLabel: "내 brain — 지식 구조/PKM" },
];

// 데스크톱 Primary Rail — VISUAL_CONTRACT §5(홈·기획·브랜드·결과·Brain).
// href 는 모두 실재 라우트만 사용(신규 라우트 0). 활성 판정은 isActive 공유.
type RailItem = {
  href: string;
  label: string;
  icon: string;
  ariaLabel: string;
  // 이 영역(Primary)으로 묶이는 경로 prefix들 — active 표시 + Secondary 영역 선택용.
  match: string[];
};

const RAIL_ITEMS: RailItem[] = [
  { href: "/", label: "홈", icon: "🏠", ariaLabel: "홈 — 빠른 기획", match: ["/"] },
  {
    href: "/new",
    label: "기획",
    icon: "✏️",
    ariaLabel: "기획 — 마법사/주제발굴",
    match: ["/new"],
  },
  {
    href: "/new/branding",
    label: "브랜드",
    icon: "🎨",
    ariaLabel: "브랜드 — 브랜드 방향 찾기",
    match: ["/new/branding"],
  },
  {
    href: "/plan",
    label: "결과",
    icon: "📄",
    ariaLabel: "결과 — 생성된 기획안",
    match: ["/plan"],
  },
  {
    href: "/brain",
    label: "Brain",
    icon: "🧠",
    ariaLabel: "내 brain — 지식 구조/PKM",
    match: ["/brain"],
  },
];

// 영역별 Secondary Sidebar 하위 메뉴 — 실재 라우트만(목업 데이터 하드코딩 아님).
type SideLink = { href: string; label: string };
type SideSection = {
  // 어떤 Primary 영역에 속하는지(rail item href 기준)
  area: string;
  title: string;
  links: SideLink[];
};

const SIDE_SECTIONS: SideSection[] = [
  {
    area: "/new",
    title: "기획 시작",
    links: [
      { href: "/new", label: "기획 방식 고르기" },
      { href: "/new/quick", label: "바로 기획안 만들기" },
      { href: "/new/discovery/step/1", label: "주제 발굴부터" },
    ],
  },
  {
    area: "/new/branding",
    title: "브랜드 방향",
    links: [{ href: "/new/branding", label: "브랜드 방향 찾기" }],
  },
  {
    area: "/plan",
    title: "결과물",
    links: [{ href: "/plan", label: "기획안 결과" }],
  },
  {
    area: "/brain",
    title: "내 Brain",
    links: [{ href: "/brain", label: "지식 구조 보기" }],
  },
];

// 숨길 경로 — 집중 플로우(자체 고정 하단 CTA 보유) + 인증 풀스크린.
//   홈(/) · 내 brain(/brain) = 목적지라 네비 유지.
const HIDDEN_PREFIXES = ["/login", "/new", "/plan"];

/**
 * 이 경로에서 AppShell(좌측 이중 내비 + 모바일 하단 탭)이 숨겨지는가.
 * layout.tsx 의 본문 여백(데스크톱 pl-320 / 모바일 pb-20)을 shell 가시성과 **연동**하기 위해 export.
 * (숨김 경로에서 여백을 그대로 두면 사이드바 없이 빈 좌측 320px → 콘텐츠가 우측으로 치우침.)
 */
export function isShellHidden(pathname: string): boolean {
  return HIDDEN_PREFIXES.some(
    (p) => pathname === p || pathname.startsWith(p + "/"),
  );
}

function matchesPrefix(pathname: string, prefix: string): boolean {
  if (prefix === "/") return pathname === "/";
  return pathname === prefix || pathname.startsWith(prefix + "/");
}

function isActive(pathname: string, href: string): boolean {
  return matchesPrefix(pathname, href);
}

// Primary Rail active — 가장 구체적인(긴) match prefix 가 이기도록 선택.
function activeRailHref(pathname: string): string | null {
  let best: { href: string; len: number } | null = null;
  for (const item of RAIL_ITEMS) {
    for (const m of item.match) {
      if (matchesPrefix(pathname, m) && (!best || m.length > best.len)) {
        best = { href: item.href, len: m.length };
      }
    }
  }
  return best?.href ?? null;
}

function DesktopPrimaryRail({ pathname }: { pathname: string }) {
  const activeHref = activeRailHref(pathname);
  return (
    <nav
      aria-label="주요 영역"
      className="fixed inset-y-0 left-0 z-40 hidden w-[76px] flex-col items-center gap-1 border-r border-border-default bg-rail px-2 py-4 desktop:flex"
      style={{ paddingBottom: "max(1rem, env(safe-area-inset-bottom))" }}
    >
      <span
        aria-hidden
        className="mb-3 grid h-10 w-10 place-items-center rounded-xl bg-primary-500 font-display text-lg font-bold text-text-inverse"
      >
        D
      </span>
      <ul className="flex w-full flex-col items-stretch gap-1">
        {RAIL_ITEMS.map((item) => {
          const active = activeHref === item.href;
          return (
            <li key={item.href}>
              <Link
                href={item.href}
                aria-current={active ? "page" : undefined}
                aria-label={item.ariaLabel}
                className={[
                  "flex min-h-[54px] flex-col items-center justify-center gap-1 rounded-xl px-1 py-2 text-[10px] font-medium transition-colors",
                  "focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-[-2px] focus-visible:outline-primary-300",
                  active
                    ? "bg-primary-500/20 text-rail-text ring-1 ring-inset ring-primary-400/40"
                    : "text-[#C9B9AC] hover:bg-[rgba(229,215,204,0.10)] hover:text-rail-text",
                ].join(" ")}
              >
                <span aria-hidden className="text-lg leading-none">
                  {item.icon}
                </span>
                <span>{item.label}</span>
              </Link>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}

function DesktopContextSidebar({ pathname }: { pathname: string }) {
  const activeHref = activeRailHref(pathname);
  const section =
    SIDE_SECTIONS.find((s) => s.area === activeHref) ?? null;

  return (
    <aside
      aria-label="현재 영역 메뉴"
      className="fixed inset-y-0 left-[76px] z-30 hidden w-[244px] flex-col gap-5 overflow-y-auto border-r border-border-default bg-neutral-50/95 px-4 py-5 backdrop-blur desktop:flex"
      style={{ paddingBottom: "max(1.25rem, env(safe-area-inset-bottom))" }}
    >
      <div className="font-display text-lg font-bold text-text-default">
        Workspace
      </div>

      {/* 현재 영역 하위 메뉴 — 실재 라우트만 */}
      {section && (
        <nav aria-label={section.title} className="flex flex-col gap-1">
          <p className="px-2 pb-1 text-[11px] font-bold uppercase tracking-wider text-text-placeholder">
            {section.title}
          </p>
          {section.links.map((link) => {
            const active = isActive(pathname, link.href);
            return (
              <Link
                key={link.href}
                href={link.href}
                aria-current={active ? "page" : undefined}
                className={[
                  "flex min-h-[42px] items-center gap-2 rounded-lg px-3 text-sm transition-colors",
                  "focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-[-2px] focus-visible:outline-primary-500",
                  active
                    ? "bg-primary-50 font-semibold text-primary-700 ring-1 ring-inset ring-primary-200"
                    : "text-text-muted hover:bg-primary-50/60 hover:text-text-default",
                ].join(" ")}
              >
                {active && (
                  <span
                    aria-hidden
                    className="h-4 w-1 rounded-full bg-primary-500"
                  />
                )}
                <span>{link.label}</span>
              </Link>
            );
          })}
        </nav>
      )}

      {/* 현재 프로젝트 / 브랜드 — placeholder(기존 데이터 범위 내, 목업 하드코딩 아님) */}
      <section
        aria-label="현재 프로젝트"
        className="rounded-md border border-border-default bg-surface px-3 py-3"
      >
        <p className="font-display text-sm font-bold text-text-default">
          현재 프로젝트
        </p>
        <p className="mt-1 text-xs leading-relaxed text-text-muted">
          진행 중인 기획을 선택하면 여기에 표시됩니다.
        </p>
      </section>

      {/* Brand Memory 요약 — placeholder(실데이터 연결 전 빈 상태) */}
      <section
        aria-label="Brand Memory 요약"
        className="rounded-md border border-border-default bg-surface px-3 py-3"
      >
        <p className="font-display text-sm font-bold text-text-default">
          Brand Memory
        </p>
        <p className="mt-1 text-xs leading-relaxed text-text-muted">
          피드백이 쌓이면 브랜드 톤·선호 구조 요약이 여기에 모입니다.
        </p>
      </section>
    </aside>
  );
}

function MobileBottomNav({ pathname }: { pathname: string }) {
  return (
    <nav
      aria-label="주요 메뉴"
      className="fixed inset-x-0 bottom-0 z-40 border-t border-neutral-200 bg-neutral-0/95 backdrop-blur desktop:hidden"
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

export default function AppShell() {
  const pathname = usePathname() ?? "/";

  if (isShellHidden(pathname)) {
    return null;
  }

  return (
    <>
      <DesktopPrimaryRail pathname={pathname} />
      <DesktopContextSidebar pathname={pathname} />
      <MobileBottomNav pathname={pathname} />
    </>
  );
}
