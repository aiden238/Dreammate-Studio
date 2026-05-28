import type { Config } from "tailwindcss";

/**
 * Tailwind config — Phase 3 Slice 1 (Foundation, 2026-05-28)
 *
 * design_system/tokens.md 1:1 매핑. theme.extend의 모든 토큰은 CSS variable 참조
 * (var(--color-*) 등). 실 값은 globals.css :root 블록에서 정의.
 *
 * 시나리오 1 (design_handoff.md §1): tokens.md 1줄 변경 → globals.css 1 블록 변경
 * → Tailwind utility 자동 반영. 영향 파일 ≤ 1 보장.
 *
 * Phase 1 호환: primary scale (50~900) / neutral scale / semantic scale은
 * 토큰 alias 도입 후에도 유지 (Phase 1 컴포넌트 회귀 보호).
 *
 * 참조: docs/decisions/phase_3_tailwind_tokens_mapping.md (ADR-012)
 */
const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // ── Phase 3 Slice 1 — design_system/tokens.md 1:1 매핑 ──
        // Primary (CTA, 선택, 활성)
        primary: {
          DEFAULT: "var(--color-primary)",
          hover: "var(--color-primary-hover)",
          pressed: "var(--color-primary-pressed)",
          disabled: "var(--color-primary-disabled)",
          // Phase 1 호환 scale (Phase 1 컴포넌트 회귀 보호)
          50: "#EEF2FF",
          100: "#E0E7FF",
          200: "#C7D2FE",
          300: "#A5B4FC",
          400: "#818CF8",
          500: "#6366F1",
          600: "#4F46E5",
          700: "#4338CA",
          800: "#3730A3",
          900: "#312E81",
        },
        accent: "var(--color-accent)",
        "bg-default": "var(--color-bg-default)",
        "bg-subtle": "var(--color-bg-subtle)",
        "bg-overlay": "var(--color-bg-overlay)",
        surface: "var(--color-surface)",
        "text-default": "var(--color-text-default)",
        "text-muted": "var(--color-text-muted)",
        "text-placeholder": "var(--color-text-placeholder)",
        "text-inverse": "var(--color-text-inverse)",
        "text-danger": "var(--color-text-danger)",
        "text-success": "var(--color-text-success)",
        "border-default": "var(--color-border-default)",
        "border-subtle": "var(--color-border-subtle)",
        "border-focus": "var(--color-border-focus)",
        "state-success": "var(--color-state-success)",
        "state-warning": "var(--color-state-warning)",
        "state-error": "var(--color-state-error)",
        "state-info": "var(--color-state-info)",
        // ── Phase 1 호환 (neutral / warning / error / success / info) ──
        // Phase 1 컴포넌트 (PlanCard, ErrorCard 등)가 직접 참조 — 보존.
        neutral: {
          0: "#FFFFFF",
          50: "#FAFAFA",
          100: "#F5F5F5",
          200: "#E5E5E5",
          300: "#D4D4D4",
          400: "#A3A3A3",
          500: "#737373",
          600: "#525252",
          700: "#404040",
          800: "#262626",
          900: "#171717",
        },
        warning: {
          50: "#FFFBEB",
          500: "#F59E0B",
          700: "#B45309",
        },
        error: {
          50: "#FEF2F2",
          500: "#EF4444",
          700: "#B91C1C",
        },
        success: {
          50: "#F0FDF4",
          500: "#22C55E",
          700: "#15803D",
        },
        info: {
          50: "#EFF6FF",
          500: "#3B82F6",
          700: "#1D4ED8",
        },
      },
      fontFamily: {
        sans: "var(--font-family-sans)",
        mono: "var(--font-family-mono)",
      },
      fontSize: {
        xs: "var(--font-size-xs)",
        sm: "var(--font-size-sm)",
        base: "var(--font-size-base)",
        lg: "var(--font-size-lg)",
        xl: "var(--font-size-xl)",
        "2xl": "var(--font-size-2xl)",
        "3xl": "var(--font-size-3xl)",
      },
      fontWeight: {
        regular: "var(--font-weight-regular)",
        medium: "var(--font-weight-medium)",
        semibold: "var(--font-weight-semibold)",
        bold: "var(--font-weight-bold)",
      },
      lineHeight: {
        tight: "var(--font-lh-tight)",
        normal: "var(--font-lh-normal)",
        relaxed: "var(--font-lh-relaxed)",
      },
      spacing: {
        // 0 / 1 / 2 / 3 / 4 / 5 / 6 / 8 / 10 / 12 / 16 (tokens.md §3.1)
        // Tailwind default 0~16 키는 유지하면서 CSS variable 참조로 alias.
        token0: "var(--space-0)",
        token1: "var(--space-1)",
        token2: "var(--space-2)",
        token3: "var(--space-3)",
        token4: "var(--space-4)",
        token5: "var(--space-5)",
        token6: "var(--space-6)",
        token8: "var(--space-8)",
        token10: "var(--space-10)",
        token12: "var(--space-12)",
        token16: "var(--space-16)",
      },
      borderRadius: {
        none: "var(--radius-none)",
        sm: "var(--radius-sm)",
        md: "var(--radius-md)",
        lg: "var(--radius-lg)",
        xl: "var(--radius-xl)",
        "2xl": "var(--radius-2xl)",
        full: "var(--radius-full)",
      },
      screens: {
        // tokens.md §5.1 — mobile-first min-width
        "mobile-md": "390px",
        sm: "480px",
        // tablet 768 / desktop 1024 / desktop-lg 1440은 Tailwind default와
        // 정합 (md=768, lg=1024, 2xl=1440 ≈). 명시 매핑은 아래 alias로 추가.
        tablet: "768px",
        desktop: "1024px",
        "desktop-lg": "1440px",
      },
      transitionDuration: {
        instant: "var(--motion-instant)",
        fast: "var(--motion-fast)",
        base: "var(--motion-base)",
        normal: "var(--motion-normal)",
        slow: "var(--motion-slow)",
      },
      transitionTimingFunction: {
        "ease-out-token": "var(--motion-ease-out)",
        "ease-in-out-token": "var(--motion-ease-in-out)",
        spring: "var(--motion-spring)",
      },
    },
  },
  plugins: [],
};

export default config;
