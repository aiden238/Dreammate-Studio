# Phase 3 — Scope

> 작업 범위 명시. Scope 밖은 non_goals + 후속 Phase 이관.

---

## In Scope (Slice별)

### Slice 1: Foundation
- `apps/web/tailwind.config.ts` (tokens 매핑)
- `apps/web/app/globals.css` (CSS variables)
- `apps/web/lib/design_tokens.ts` (TS 상수 export)
- `docs/decisions/phase_3_tailwind_tokens_mapping.md` (ADR-012)

### Slice 2: Thin Vertical (Discovery Step 1)
- `apps/web/components/discovery/BrandDirectionCard.tsx` (chosen variant)
- `apps/web/components/discovery/CardGrid5.tsx` (chosen variant)
- `apps/web/app/new/discovery/step/1/page.tsx`
- `apps/web/lib/state/wizard.ts` (session storage, Step 1 propagation)
- `apps/web/lib/discovery_state.ts` (Discovery 흐름 state)
- **검증**: `npm run dev` → http://localhost:3000/new/discovery/step/1 → 카드 5장 + 선택 동작

### Slice 3: Discovery 확장 (Step 2~7)
- `apps/web/app/new/discovery/step/[n]/page.tsx` (dynamic route 또는 개별)
- `apps/web/components/discovery/ToneChipsForm.tsx` (Step 5 form)
- `apps/web/components/common/DirectionApprovalCard.tsx` (Step 6, verbose)
- discovery_state.ts 확장 (Step 1 → 7 propagation)
- Step 7 generate 호출 (Phase 1 endpoint mock OR 단일 호출)

### Slice 4: Quick Mode (Slice 3와 병렬)
- `apps/web/components/quick/QuickInputCard.tsx`
- `apps/web/app/new/quick/page.tsx` (Step 1)
- `apps/web/app/new/quick/clarify/page.tsx` (Step 2)
- `apps/web/app/new/quick/direction/page.tsx` (Step 3, DirectionApprovalCard minimal)
- `apps/web/app/new/quick/generate/page.tsx` (Step 4)
- `apps/web/lib/quick_state.ts`

### Slice 5: Middleware + Mode Branching
- `apps/web/lib/mode_branching.ts` (yaml → TS)
- `apps/web/app/new/page.tsx` (진입점, redirect)
- (선택) `apps/web/middleware.ts`
- `docs/decisions/phase_3_mode_branching_middleware.md` (ADR-013)

### Slice 6: 통합 + 회고 + archive
- `scripts/audit_page_component.ps1` (D5)
- `scripts/smoke_test_phase_3.ps1`
- `eval/qa_reports/phase-3-final_2026-05-28.md`
- `meta/retrospectives/phase-3.md`
- `phases/active → archive/phase-3-pwa-impl/` 이동
- PROJECT_STATE / PHASE_REGISTRY / 00_START_HERE / README 갱신

---

## 범위 경계

```
Phase 3 포함                              Phase 3 미포함
─────────────────────────────────         ─────────────────────────────────
Next.js .tsx 코드 작성                    Phase 2 spec 변경
4-layer chosen variant 구현               모든 variants 구현 (alt는 prop 자리)
Tailwind tokens 매핑                      design.md / design_handoff 수정
Discovery 7-step + Quick 4-step routes    Phase 5 Auth / Phase 9 피드백
Mode Branching middleware                 Phase 4 SSE / multi-step endpoint
audit_page_component.ps1 (D5)              audit 자동 도구 확장
smoke test Phase 3 추가                   Lighthouse / Playwright e2e
component_map.md (read-only 절대)         component_map.md 수정 (조정 4번)
PlanCard 4-layer 정합 (Phase 4 이관)      D3 deferred
```

---

## 예상 파일 변경 목록

```
신규 (~25 개):
  apps/web/
    lib/  : 4 파일 (design_tokens / mode_branching / state/wizard / discovery_state / quick_state)
    app/new/ : 6 파일 (page + discovery/step/[n] + quick/{page,clarify,direction,generate})
    components/  : 5 파일 (discovery/BrandDirectionCard / CardGrid5 / ToneChipsForm + common/DirectionApprovalCard + quick/QuickInputCard)
  scripts/  : 2 파일 (audit_page_component / smoke_test_phase_3)
  docs/decisions/  : 2 ADR (012 / 013)
  phases/active/phase-3-pwa-impl/  : 9 entry files
  eval/qa_reports/  : 8 reports
  meta/  : handoff + retrospective + proposals

수정:
  apps/web/tailwind.config.ts
  apps/web/app/layout.tsx
  apps/web/app/globals.css
  PROJECT_STATE / PHASE_REGISTRY / 00_START_HERE / README

명시 무수정 (조정 4번):
  apps/web/component_map.md  ← read-only 절대 보장. deviation 발견 시 deviation_log만.
  apps/web/page_map.md       ← read-only (Phase 2 결과)
  apps/web/design_handoff.md ← read-only
  apps/web/design_system/*   ← read-only
  apps/web/*flow.md, *branching.md, direction_approval.md, wireframes/* ← read-only
  apps/web/design.md         ← read-only
```

---

## 완료 기준 요약

전체 acceptance는 `acceptance.md` A1~A10 참조.

핵심:
- pytest 62/62 회귀 0
- next build / tsc / lint 0 errors
- audit_naming 0 drift + audit_page_component 0 drift (Slice 6 신규)
- 변경성 시뮬레이션 5/5 회귀 PASS (Phase 2 결과 보존)
- Thin Vertical (Slice 2) 브라우저 동작 확인
