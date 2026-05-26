import type { Metadata, Viewport } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Dreammate Studio — 영상기획 AI 에이전트",
  description:
    "막연한 아이디어를 검증 가능한 영상기획 카드로 만들어주는 AI 에이전트. Phase 1 MVP.",
  manifest: "/manifest.json",
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 5,
  themeColor: "#6366F1",
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
