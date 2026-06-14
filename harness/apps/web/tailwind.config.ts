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
          // Phase 30 S1 de-risk — legacy scale을 앰버~테라코타 웜 팔레트로 재매핑.
          // 앱 전반 primary-N00 직접 사용분이 자동 리컬러됨(기능 0 변화).
          // 출처: apps/web/design_reference/DESIGN_TOKENS.css.
          50: "#FFF6E8",
          100: "#FFE9C4",
          200: "#FFD68B",
          300: "#FFBF57",
          400: "#FF9A2F",
          500: "#F47B20",
          600: "#E96818",
          700: "#D94C1A",
          800: "#AD3817",
          900: "#7C2915",
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
        // Phase 30 S1 — 데스크톱 Primary Rail / 서적 카드용 (VISUAL_CONTRACT §2·§5).
        rail: "var(--color-rail)",
        "rail-text": "var(--color-rail-text)",
        // ── Phase 30 S1 de-risk — legacy scale 웜 재매핑 ──
        // PlanCard / ErrorCard / ProgressStepper 등이 neutral-N00 / status-N00을
        // 직접 참조 — 보존하되 값만 아이보리~짙은브라운 웜그레이로 교체해 자동 리컬러.
        // 출처: apps/web/design_reference/DESIGN_TOKENS.css + VISUAL_CONTRACT §2.
        neutral: {
          0: "#FFFFFF",
          50: "#FFFAF4",
          100: "#F5EFE6",
          200: "#EEE3D5",
          300: "#DDCDBD",
          400: "#A08E82",
          500: "#78685F",
          600: "#65544B",
          700: "#4D3D35",
          800: "#3F3029",
          900: "#352A24",
        },
        // warning=앰버, error=적갈색 — primary 주황과 시각적으로 구분(VISUAL_CONTRACT §8 / COMPONENT_MAPPING §8).
        warning: {
          50: "#FCF1DC",
          500: "#E0991C",
          700: "#9C6A12",
        },
        error: {
          50: "#F7E6E0",
          500: "#C2452A",
          700: "#8F2E1B",
        },
        success: {
          50: "#EAF1E0",
          500: "#5C8A3A",
          700: "#3F6326",
        },
        info: {
          50: "#E6EDF5",
          500: "#4A6FA5",
          700: "#34507A",
        },
      },
      fontFamily: {
        // Phase 30 S1 — VISUAL_CONTRACT §4 폰트 역할(fallback 체인만, 폰트파일/deps 추가 없음).
        sans: "var(--font-family-sans)", // UI·본문 (SUIT/Pretendard)
        display: "var(--font-family-display)", // Hero·제목 (Paperlogy)
        editorial: "var(--font-family-editorial)", // 대본·긴 인용 (Noto Serif KR)
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
