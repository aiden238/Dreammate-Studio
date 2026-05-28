/**
 * Phase 3 Slice 1 — design_system/tokens.md TS 상수 export.
 *
 * 컴포넌트 코드에서 import해서 사용 (Tailwind utility로 표현하기 어려운
 * 동적 값 — motion duration ms 숫자, breakpoint px 숫자 등).
 *
 * 변경 시 4개 파일 모두 동기 필요:
 *   1. apps/web/design_system/tokens.md (원천 spec)
 *   2. apps/web/app/globals.css (CSS custom properties)
 *   3. apps/web/tailwind.config.ts (theme.extend alias)
 *   4. apps/web/lib/design_tokens.ts (본 파일)
 *
 * 시나리오 1 (design_handoff.md §1, replaceability L): 색/폰트/spacing 변경 시
 * tokens.md 1줄 + 본 4 파일 한 블록씩 swap → 전체 자동 반영.
 *
 * 참조:
 *   - apps/web/design_system/tokens.md
 *   - docs/decisions/phase_3_tailwind_tokens_mapping.md (ADR-012)
 *
 * 사용:
 *   import { TOKENS } from "@/lib/design_tokens";
 *   const ms = TOKENS.motion.fast; // 150
 */

export const TOKENS = {
  /** Color — tokens.md §1 (semantic, not literal) */
  color: {
    // Primary
    primary: "#6366F1",
    primaryHover: "#4F46E5",
    primaryPressed: "#4338CA",
    primaryDisabled: "#A5B4FC",
    // Accent
    accent: "#06B6D4",
    // Background / Surface
    bgDefault: "#FAFAFA",
    bgSubtle: "#F5F5F5",
    bgOverlay: "rgba(0, 0, 0, 0.5)",
    surface: "#FFFFFF",
    // Text
    textDefault: "#171717",
    textMuted: "#525252",
    textPlaceholder: "#A3A3A3",
    textInverse: "#FFFFFF",
    textDanger: "#B91C1C",
    textSuccess: "#15803D",
    // Border
    borderDefault: "#E5E5E5",
    borderSubtle: "#F5F5F5",
    borderFocus: "#6366F1",
    // State
    stateSuccess: "#22C55E",
    stateWarning: "#F59E0B",
    stateError: "#EF4444",
    stateInfo: "#3B82F6",
  },

  /** Typography — tokens.md §2 */
  font: {
    familySans:
      '"Pretendard Variable", "Pretendard", -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif',
    familyMono: '"JetBrains Mono", "Menlo", "Consolas", monospace',
    sizeXs: "0.75rem",
    sizeSm: "0.875rem",
    sizeBase: "0.9375rem",
    sizeLg: "1.0625rem",
    sizeXl: "1.125rem",
    size2xl: "1.25rem",
    size3xl: "1.5rem",
    weightRegular: 400,
    weightMedium: 500,
    weightSemibold: 600,
    weightBold: 700,
    lhTight: 1.2,
    lhNormal: 1.4,
    lhRelaxed: 1.5,
  },

  /** Spacing (4px base) — tokens.md §3 */
  spacing: {
    s0: "0",
    s1: "0.25rem",
    s2: "0.5rem",
    s3: "0.75rem",
    s4: "1rem",
    s5: "1.25rem",
    s6: "1.5rem",
    s8: "2rem",
    s10: "2.5rem",
    s12: "3rem",
    s16: "4rem",
  },

  /** Radius — tokens.md §4 */
  radius: {
    none: "0",
    sm: "0.25rem",
    md: "0.5rem",
    lg: "0.75rem",
    xl: "1rem",
    "2xl": "1.5rem",
    full: "9999px",
  },

  /** Breakpoint (mobile-first, px 숫자) — tokens.md §5 */
  breakpoint: {
    mobile: 360,
    mobileMd: 390,
    sm: 480,
    tablet: 768,
    desktop: 1024,
    desktopLg: 1440,
  },

  /** Motion (ms 숫자) — tokens.md §6 */
  motion: {
    instant: 0,
    fast: 150,
    base: 250,
    normal: 300,
    slow: 400,
    easeOut: "cubic-bezier(0, 0, 0.2, 1)",
    easeInOut: "cubic-bezier(0.4, 0, 0.2, 1)",
    spring: "cubic-bezier(0.34, 1.56, 0.64, 1)",
  },
} as const;

export type TokensColor = keyof typeof TOKENS.color;
export type TokensFont = keyof typeof TOKENS.font;
export type TokensSpacing = keyof typeof TOKENS.spacing;
export type TokensRadius = keyof typeof TOKENS.radius;
export type TokensBreakpoint = keyof typeof TOKENS.breakpoint;
export type TokensMotion = keyof typeof TOKENS.motion;
