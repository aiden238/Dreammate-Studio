import type { Metadata, Viewport } from "next";
import "./globals.css";
import AppShell from "@/components/AppShell";
import MainFrame from "@/components/MainFrame";

/**
 * Phase 1 Slice 7 — root layout
 *
 * frontend_design_contract.md §6.1: manifest + theme_color + viewport
 * apps/web/design.md §16: 모바일 우선
 */
export const metadata: Metadata = {
  title: "Dreammate Studio — 영상기획 AI 에이전트",
  description:
    "막연한 아이디어를 검증 가능한 영상기획 카드로 만들어주는 AI 에이전트. Phase 1 MVP.",
  manifest: "/manifest.json",
  applicationName: "Dreammate Studio",
  appleWebApp: {
    capable: true,
    statusBarStyle: "default",
    title: "Dreammate",
  },
  icons: {
    icon: [
      { url: "/icons/icon-192.svg", type: "image/svg+xml" },
    ],
    apple: [{ url: "/icons/icon-192.svg" }],
  },
  formatDetection: {
    telephone: false,
  },
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 5,
  // Phase 30 S8 QA — PWA 브라우저 크롬 색을 새 팔레트(orange primary)로 정정.
  //   legacy indigo(#6366F1) 잔재 제거. 출처: globals.css --color-primary / VISUAL_CONTRACT §2.
  themeColor: "#F47B20",
  colorScheme: "light",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ko">
      <body className="min-h-screen bg-neutral-50 text-neutral-900 safe-area">
        {/* 지속 네비(AppShell)가 본문을 가리지 않도록 여백 확보 — 단, shell 이 실제 보이는
            경로에서만(MainFrame 이 isShellHidden 로 연동). 숨김 경로(/login·/new·/plan)는 여백 0
            → 콘텐츠 전체폭 중앙 정렬(우측 치우침 해소). 모바일=하단 탭바(pb-20)/데스크톱=좌측 내비(320px). */}
        <MainFrame>{children}</MainFrame>
        <AppShell />
      </body>
    </html>
  );
}
