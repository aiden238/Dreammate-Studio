# Phase 3 — Acceptance Criteria

> 10 항목 모두 통과해야 Phase 3 완료.

---

## A1. Foundation (Slice 1)

```
체크:
  - apps/web/tailwind.config.ts에서 tokens.md 매핑 (theme.extend.colors / spacing / etc)
  - apps/web/lib/design_tokens.ts TS 상수 export
  - 시나리오 1 회귀: tokens.md 색 변경 시 1 파일 swap 보장
```

- [ ] tailwind.config.ts tokens 매핑
- [ ] design_tokens.ts 작성
- [ ] next build 0 errors
- [ ] hardcoded 색 0건 (literal hex grep)

---

## A2. Thin Vertical (Slice 2) ★ Phase 3 핵심

```
체크: Discovery Step 1 end-to-end 작동
방법: npm run dev → http://localhost:3000/new/discovery/step/1
기준:
  - 카드 5장 (AI 4 + user_input 1) 표시
  - 카드 선택 가능 (selected state)
  - SubmitButton 활성/비활성
  - tokens 참조 색 적용 (literal 색 0)
```

- [ ] BrandDirectionCard.tsx 작성 (4-layer chosen variant)
- [ ] CardGrid5.tsx 작성
- [ ] /new/discovery/step/1 페이지 동작
- [ ] session storage state machine 작동 (state/wizard.ts + discovery_state.ts)

---

## A3. Discovery 확장 (Slice 3)

```
체크: Discovery Step 2~7 모두 라우팅
기준:
  - Step 2~5: BrandDirectionCard 패턴 재사용
  - Step 5: ToneChipsForm (다중선택 chip 8개 + skip)
  - Step 6: DirectionApprovalCard (verbose)
  - Step 7: Generate (Phase 1 PlanCard 재사용)
```

- [ ] /new/discovery/step/[n] dynamic route 동작 (n=1~7)
- [ ] ToneChipsForm 다중선택
- [ ] DirectionApprovalCard verbose variant
- [ ] back navigation + state 보존

---

## A4. Quick Mode (Slice 4)

```
체크: Quick 4-step routes 모두 동작
기준:
  - /new/quick (initial prompt)
  - /new/quick/clarify (follow-up question)
  - /new/quick/direction (DirectionApprovalCard minimal)
  - /new/quick/generate (PlanCard)
```

- [ ] QuickInputCard 두 mode 분기 (initial_prompt / follow_up_question)
- [ ] 4 routes 라우팅
- [ ] DirectionApprovalCard minimal variant

---

## A5. Mode Branching (Slice 5)

```
체크: /new 진입 시 user 컨텍스트 분기
기준:
  - rule_new_user → /new/discovery/step/1
  - rule_brand_no_series → /new/discovery/step/3
  - rule_has_series → /new/quick
  - override "new project" → /new/discovery/step/1
```

- [ ] lib/mode_branching.ts (yaml → TS, 4 rules + 3 overrides)
- [ ] /new/page.tsx redirect 동작
- [ ] 4 branching_rules 모두 manual 검증

---

## A6. Phase 1 회귀 0

```
체크: Phase 1 / 와 /plan 페이지 회귀 0
기준:
  - PlanCard / ErrorCard / ProgressStepper / SubmitButton 보존
  - Phase 1 backend (POST /api/v1/generate) 정상 동작
```

- [ ] pytest 62/62 PASS (backend 회귀 0)
- [ ] / 페이지 (Phase 1) 동작
- [ ] /plan 페이지 (Phase 1) 동작

---

## A7. 빌드 검증

```
체크: next build / tsc / lint 0 errors
도구: npm run build / npx tsc --noEmit / npx next lint
```

- [ ] next build 0 errors
- [ ] tsc --noEmit 0 errors
- [ ] ESLint clean

---

## A8. audit 자동 도구

```
체크: 2 audit 도구 모두 0 drift
도구: audit_naming.ps1 (기존) + audit_page_component.ps1 (Slice 6 신규)
```

- [ ] audit_naming.ps1 0 drift
- [ ] audit_page_component.ps1 작성 + 0 drift
- [ ] page_map.md ↔ 실 routes 정합 (audit_page_component 자동)
- [ ] component_map.md ↔ 실 components 정합 (자동)

---

## A9. 변경성 시뮬레이션 5/5 회귀

```
체크: Phase 2 변경성 시뮬레이션 5/5가 Phase 3 코드에서도 동작
방법: manual walkthrough (Slice 6)
```

- [ ] 시나리오 1: tokens 색 변경 영향 ≤ 1 파일
- [ ] 시나리오 2: BrandDirectionCard variants swap ≤ 2 파일
- [ ] 시나리오 3: Discovery 7→5 단계 축소 ≤ 4 파일
- [ ] 시나리오 4: Direction Approval minimal→verbose ≤ 1 파일
- [ ] 시나리오 5: Quick mode 폐기 ≤ 5 파일

---

## A10. component_map.md read-only 보존 (조정 4번)

```
체크: Phase 3 commit history에서 component_map.md 0줄 수정
도구: git diff HEAD~N apps/web/component_map.md
```

- [ ] 모든 Slice 1~6 commit에서 component_map.md 미수정
- [ ] deviation 발견 시 deviations.md 기록만
- [ ] retrospective에서 deviation count 보고

---

## Done Definition

A1~A10 모두 통과 + git commit (Slice 1~6) + push + archive 이동.

## 이후 Phase

**Phase 4. FastAPI 기본 백엔드 구현 (확장)** — 3-plan 활성화 + Critic revise + SSE / multi-step endpoint.
+ D2/D3/D4 deferred 처리.
