# Phase 3 — Work Plan (Slice 1~6)

> 작성: 2026-05-28
> 원칙: Thin Vertical Flow (Slice 2 = 한 페이지 통째 작동), Phase 2 spec read-only

---

## Slice 1 — Foundation (Tailwind tokens 매핑)

**목표**: tokens.md를 Tailwind theme.extend로 매핑. CSS variables. 시나리오 1 (token 변경) 1 파일 swap 보장.

### 산출물
- `apps/web/tailwind.config.ts` 갱신 (theme.extend.colors / fontSize / spacing / borderRadius / screens / transitionDuration)
- `apps/web/app/globals.css` (CSS custom properties)
- `apps/web/lib/design_tokens.ts` (TS 상수 export — 컴포넌트 import용)
- `apps/web/app/layout.tsx` 갱신 (globals.css import 확인)
- `docs/decisions/phase_3_tailwind_tokens_mapping.md` (ADR-012)
- `eval/qa_reports/phase-3-slice-1_2026-05-28.md`

### Acceptance
- next build 0 errors
- tsc --noEmit 0 errors
- hardcoded 색 0건 (literal hex grep)
- audit_naming 0 drift

### 추정: 2~3h

### Commit
```
phase-3(slice-1): Foundation — Tailwind tokens 매핑 + design_tokens.ts
```

---

## Slice 2 — Thin Vertical: Discovery Step 1 end-to-end ★ Phase 3 핵심

**목표**: Slice 1 위에 Discovery Step 1 한 페이지 통째 작동. `npm run dev` → http://localhost:3000/new/discovery/step/1 → 카드 5장 + 선택.

### 산출물
- `apps/web/components/discovery/BrandDirectionCard.tsx` (4-layer chosen variant + variant prop 자리)
- `apps/web/components/discovery/CardGrid5.tsx` (4-layer chosen variant)
- `apps/web/app/new/discovery/step/1/page.tsx` (single page route)
- `apps/web/lib/state/wizard.ts` (session storage state machine baseline)
- `apps/web/lib/discovery_state.ts` (Discovery 흐름 — Step 1 → next 자리)
- (선택) 단위 테스트: components/__tests__/BrandDirectionCard.test.tsx + CardGrid5.test.tsx (smoke level 1~2 케이스)
- `eval/qa_reports/phase-3-slice-2_2026-05-28.md`

### Acceptance ★ 핵심
- next build 0 errors
- `npm run dev` 후 http://localhost:3000/new/discovery/step/1 접근 가능
- 카드 5장 (AI 4 + user_input 1) 표시
- 카드 선택 시 selected state 변화
- Visual = tokens 참조 (literal 색 0건)
- session storage state 작동
- **component_map.md 0줄 수정** (조정 4번)

### 추정: 3~4h

### Commit
```
phase-3(slice-2): Thin Vertical — Discovery Step 1 (BrandDirectionCard + CardGrid5 end-to-end)
```

---

## Slice 3 — Discovery 확장 (Step 2~7) — Slice 4와 병렬

**목표**: Slice 2 패턴을 Step 2~7로 복제. Step 5는 ToneChipsForm 예외, Step 6는 DirectionApprovalCard, Step 7은 Phase 1 PlanCard 재사용.

### 산출물
- `apps/web/app/new/discovery/step/[n]/page.tsx` (dynamic route, n=1~7 통합)
   - 또는 step/1, step/2 개별 파일 (n=1은 Slice 2 산출물 활용)
- `apps/web/components/discovery/ToneChipsForm.tsx` (Step 5, 다중선택 chip 8개 + skip)
- `apps/web/components/common/DirectionApprovalCard.tsx` (Step 6, verbose variant)
- discovery_state.ts 확장 (Step 1~7 propagation)
- Step 7 generate (Phase 1 endpoint 호출 또는 mock)
- `eval/qa_reports/phase-3-slice-3_2026-05-28.md`

### Acceptance
- /new/discovery/step/2~7 라우팅 동작
- ToneChipsForm 다중선택 chip
- DirectionApprovalCard verbose
- back navigation + state 보존
- next build / tsc / lint 0 errors
- **component_map.md 0줄 수정**

### 추정: 3~4h

### Commit
```
phase-3(slice-3): Discovery Step 2~7 + ToneChipsForm + DirectionApprovalCard (verbose)
```

---

## Slice 4 — Quick Mode 4-step (Slice 3와 병렬)

**목표**: Quick 흐름 4-step routes + QuickInputCard 분기.

### 산출물
- `apps/web/components/quick/QuickInputCard.tsx` (initial_prompt / follow_up_question 분기)
- `apps/web/app/new/quick/page.tsx` (Step 1)
- `apps/web/app/new/quick/clarify/page.tsx` (Step 2)
- `apps/web/app/new/quick/direction/page.tsx` (Step 3, DirectionApprovalCard minimal — Slice 3 컴포넌트 재사용)
- `apps/web/app/new/quick/generate/page.tsx` (Step 4)
- `apps/web/lib/quick_state.ts`
- `eval/qa_reports/phase-3-slice-4_2026-05-28.md`

### Acceptance
- /new/quick + clarify + direction + generate 라우팅 동작
- QuickInputCard 두 mode 분기
- DirectionApprovalCard minimal variant
- next build / tsc / lint 0 errors
- **component_map.md 0줄 수정**

### 추정: 2~3h

### Commit
```
phase-3(slice-4): Quick Mode 4-step routes + QuickInputCard
```

### Slice 3 ∥ Slice 4 충돌 회피
- Slice 3 영역: `app/new/discovery/`, `components/discovery/{ToneChipsForm}`, `components/common/DirectionApprovalCard`, `lib/discovery_state.ts`
- Slice 4 영역: `app/new/quick/`, `components/quick/QuickInputCard`, `lib/quick_state.ts`
- 공유: DirectionApprovalCard는 Slice 3에서 작성, Slice 4는 import만 (variant prop=minimal)
- Slice 4 sub-agent prompt에 "DirectionApprovalCard 신규 작성 금지, Slice 3 산출물 import only" 명시

---

## Slice 5 — Middleware + Mode Branching

**목표**: mode_branching.yaml → TS 변환 + /new 진입점 redirect.

### 산출물
- `apps/web/lib/mode_branching.ts` (4 branching_rules + 3 override_rules → 함수)
- `apps/web/app/new/page.tsx` (진입점, 사용자 컨텍스트 검사 → redirect)
- (선택) `apps/web/middleware.ts` — ADR-013에서 결정 (기본: page.tsx redirect)
- `docs/decisions/phase_3_mode_branching_middleware.md` (ADR-013)
- `eval/qa_reports/phase-3-slice-5_2026-05-28.md`

### Acceptance
- `/new` 접근 시 4 branching_rules + 3 override_rules 모두 동작
- next build / tsc / lint 0 errors
- session storage state 보존 검증
- **component_map.md 0줄 수정**

### 추정: 2~3h

### Commit
```
phase-3(slice-5): Mode Branching middleware (/new redirect) + ADR-013
```

---

## Slice 6 — 통합 + audit + smoke + retrospective + archive

**목표**: Phase 3 종료. audit_page_component (D5) + smoke test + 변경성 시뮬 회귀 + 회고 + archive.

### 산출물
- `scripts/audit_page_component.ps1` (NEW, D5)
- `scripts/smoke_test_phase_3.ps1` (NEW)
- `eval/qa_reports/phase-3-final_2026-05-28.md`
- `meta/retrospectives/phase-3.md` (회고 — P-X1 효과 측정 + deviation 분석)
- `meta/proposals/2026-05-28_phase-3-retrospective-proposals.md` (Y-X 있다면)
- `phases/active/phase-3-pwa-impl/closing_notes.md`
- `phases/active → archive/phase-3-pwa-impl/` 이동
- PROJECT_STATE / PHASE_REGISTRY / 00_START_HERE / README 갱신

### Acceptance (A1~A10 종합)
- A1~A10 모두 PASS
- 변경성 시뮬레이션 5/5 회귀 PASS
- pytest 62/62 회귀 0
- next build / tsc / lint 0 errors
- audit_naming + audit_page_component 모두 0 drift
- **component_map.md 0줄 수정** (전체 Phase 3에서)
- D3 Phase 4 이관 명시 (closing_notes)

### 추정: 2~3h

### Commit
```
phase-3(slice-6): final QA + audit_page_component + smoke + retrospective + archive
```

---

## 전체 추정

| Slice | 시간 | 누적 |
|---|---|---|
| 1 Foundation | 2~3h | 2~3h |
| 2 Thin Vertical ★ | 3~4h | 5~7h |
| 3 Discovery 확장 | 3~4h | 8~11h |
| 4 Quick Mode | 2~3h | 10~14h |
| 5 Middleware | 2~3h | 12~17h |
| 6 통합 + 회고 | 2~3h | 14~20h |

**Phase 3 총**: 14~20h (P-X1 pre-entry 0.5h 별도)

---

## Slice 진입 규칙

```
1. 이전 Slice acceptance 모두 통과 확인
2. audit_naming 0 drift 확인
3. pytest 62/62 PASS 확인
4. component_map.md / page_map.md / design_handoff.md 0줄 수정 확인 (git log)
5. 다음 Slice acceptance 재확인
6. (Wave 3 병렬) 충돌 영역 sub-section 분리 명시 + P-X1 §SELF-VERIFICATION 의무
7. Sub-agent dispatch 또는 main session
8. 완료 시: audit + git commit + main session diff 검증
```

---

## scope creep 경고

다음 발견 시 즉시 중단 + 사용자 알림:
- component_map.md 수정 (조정 4번 위반 — critical)
- design_handoff.md / page_map.md / design_system/* 수정
- 4-layer 4개 외 컴포넌트 신규 4-layer 작성
- variants alt 구현 (chosen만 가능, alt는 prop 자리만)
- PlanCard 4-layer 정합 시도 (D3 Phase 4)
- audit script 외 자동화 도구 추가
- backend/ 수정

---

## 변경 이력

- 2026-05-28: Slice 1~6 최초 작성 (Thin Vertical 채택, 조정 4 반영)
