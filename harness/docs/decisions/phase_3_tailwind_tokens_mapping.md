# ADR-012: Phase 3 Tailwind Tokens Mapping

> Status: accepted (Phase 3 Slice 1, 2026-05-28)
> Author: Phase 3 Slice 1 sub-agent
> Related: ADR-010 (4-layer minimal), ADR-011 (Variants 3 components)

---

## Context

Phase 2 `design_handoff.md` §1 시나리오 1: "tokens.md 색 변경 → 영향 파일 ≤ 1 (replaceability L)".
Phase 3에서는 이를 코드로 구현해야 한다. tokens.md 1줄 수정 시
전체 페이지/컴포넌트가 자동 반영되어야 한다.

추가 제약:
- Phase 1 baseline (Tailwind 14, Next.js 14, TypeScript 5) 보존
- Phase 1 컴포넌트(PlanCard, ErrorCard, ProgressStepper, SubmitButton)
  회귀 0 (기존 `bg-neutral-50` / `text-neutral-900` 등 scale 토큰 직접 참조)
- 추가 런타임 비용 회피 (CSS-in-JS 등 도입 X)
- Visual layer 4-layer 컴포넌트 (`component_contract.md` §1)에서
  literal hex 색 0건 강제

---

## Decision

**Tailwind `theme.extend` + CSS custom properties + TS 상수 export** 3-layer 조합.

```
apps/web/design_system/tokens.md       (원천 spec, markdown)
                ↓ (수동 동기, replaceability L)
apps/web/app/globals.css :root         (CSS custom properties — 실 값 정의)
                ↓ (var(--*) 참조)
apps/web/tailwind.config.ts            (theme.extend.colors / fontSize / etc)
                ↓ (Tailwind utility 생성)
apps/web/components/*.tsx              (className="bg-primary text-text-default")

apps/web/lib/design_tokens.ts          (TS 상수 — motion ms / breakpoint px 등
                                        Tailwind 미지원 동적 값 import)
```

- **tailwind.config.ts** `theme.extend`의 각 토큰을 `var(--*)` 참조로 정의
- **globals.css** `:root` 블록에서 실 값 정의 (1곳)
- **design_tokens.ts** TS 상수 export (motion duration ms 숫자, breakpoint px 숫자)
- Visual layer에서 항상 토큰 alias 통해서만 사용 (literal `#6366F1` 금지)

---

## Alternatives

### A. Tailwind theme에 literal 값 hardcoding
- 거부 — 시나리오 1 1 파일 swap 불가능 (tailwind.config.ts + 컴포넌트 className 양쪽 변경 필요)

### B. CSS variables only (Tailwind 제거)
- 거부 — Phase 1 baseline에서 Tailwind 14 활용 + 기존 컴포넌트가 utility class에 의존

### C. Styled-components / Emotion (CSS-in-JS)
- 거부 — 런타임 비용 / SSR 복잡도 / Phase 1 baseline 대비 추가 dep

### D. Tailwind extend + CSS variables (채택)
- 1 파일 swap 보장 (globals.css :root 블록 1곳)
- Tailwind utility 활용 (`bg-primary`, `text-text-default`)
- TS 상수 import도 가능 (motion duration 등)
- 추가 dep 없음

---

## Consequences

### 긍정
- **시나리오 1 PASS**: globals.css :root 1 블록 수정 → 모든 컴포넌트 자동 반영
- **Tailwind utility 자동 참조**: `bg-primary` / `text-text-default` / `rounded-lg` 등
  Tailwind 빌드 시 var(--*) 그대로 출력
- **TS 상수 import 가능**: `import { TOKENS } from "@/lib/design_tokens"`로
  motion ms, breakpoint px 등 동적 값 활용
- **Phase 1 호환**: Phase 1 컴포넌트의 `bg-neutral-50` / `text-neutral-900` 등
  scale 토큰 그대로 보존 (tailwind.config.ts에 legacy scale 유지)
- **prefers-reduced-motion 자동 적용**: globals.css의 글로벌 미디어 쿼리가
  모든 transition duration을 instant로 강제

### 부정
- **4개 파일 동기 부담**: tokens.md / globals.css / tailwind.config.ts / design_tokens.ts
  모두 일관 유지 필요 → Phase 3 Slice 6 audit_page_component.ps1 (D5)에서
  drift 검출 자동화로 완화 예정
- **Tailwind 빌드 시 var(--*) 참조 처리**: JIT 모드에서 var는 그대로
  CSS output에 포함 — Tailwind 4 호환 issue 없음 (3.4.6 기준)

### 중립
- dark mode (Phase 11+): tokens.md TBD → globals.css에 `@media (prefers-color-scheme: dark)`
  자리 placeholder로 두고 본격 활성 시 :root 블록만 추가

---

## Verification

### 자동 검증
- `npm run build` (next build) 0 errors
- `npx tsc --noEmit` 0 errors
- `npx next lint` 0 warnings (Phase 3 Slice 1 신규 파일만 적용)
- grep literal hex 색 (`apps/web/components/discovery/`, `apps/web/components/common/`,
  `apps/web/components/quick/`, `apps/web/app/new/`) → 0 건 강제
  - 단, `apps/web/components/{PlanCard,ErrorCard,ProgressStepper,SubmitButton}.tsx`
    는 Phase 1 baseline (Phase 4 D3 이관) — 검사 제외

### 수동 검증 (Slice 6 변경성 시뮬레이션)
- 시나리오 1: globals.css `--color-primary` 1줄 변경 → 영향 파일 ≤ 1 확인
- Tailwind utility 자동 반영 확인 (`bg-primary` 클래스가 새 색으로 렌더링)
- TS 상수도 동시 갱신 필요 (design_tokens.ts) — 동기 절차 명시

---

## Related

- ADR-010: `docs/decisions/phase_2_design_layered_minimal.md` (4-layer minimal)
- ADR-011: `docs/decisions/phase_2_variants_3_components.md` (Variants 3 components)
- `apps/web/design_system/tokens.md` (Phase 2 원천)
- `apps/web/design_system/component_contract.md` §1 Visual layer (literal hex 금지)
- `apps/web/design_handoff.md` §1 시나리오 1
- `frontend_design_contract.md` §2 (디자인 토큰 contract)

---

## 변경 이력

- 2026-05-28: ADR-012 최초 작성 (Phase 3 Slice 1)
