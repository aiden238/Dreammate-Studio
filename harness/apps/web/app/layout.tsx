import type { Metadata, Viewport } from "next";
import "./globals.css";

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
  themeColor: "#6366F1",
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
        {children}
      </body>
    </html>
  );
}
