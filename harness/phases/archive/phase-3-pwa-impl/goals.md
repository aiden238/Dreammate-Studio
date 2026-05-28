# Phase 3 — Goals

> Phase: 3 / Next.js PWA 기본 UI 구현 (Discovery + Quick 분기)
> Status: active
> Started: 2026-05-28
> 조정 후 진입 (4 조정 사항 적용)

---

## 핵심 목표

**Phase 2 design spec을 실 Next.js 코드로 변환** — 새 디자인 결정 0건. 모든 결정은 Phase 2 design_handoff.md / component_map.md / design_system/* 에서.

### 4 조정 사항 (사용자 결정, 2026-05-28)

1. **P-X1 선적용** ✅ — phase-start v1.3.0 (pre-entry commit `3d0b0fb`)
2. **Thin Vertical Flow** — Slice 2를 "Discovery Step 1 end-to-end"로 재정의 (한 페이지 통째 작동 → 패턴 확장)
3. **PlanCard 4-layer 정합 Phase 4 이관** — D3 deferred, Slice 6에서 처리 안 함
4. **component_map.md read-only 절대 보장** — deviation 발견 시 deviation_log + proposal만, 직접 수정 금지

### 세부 목표

#### G1. Foundation
- Tailwind config + tokens.md 1:1 매핑
- `apps/web/lib/design_tokens.ts` (TS 상수)
- 시나리오 1 (token 변경) 1 파일 swap 보장

#### G2. Thin Vertical (Phase 3의 가장 중요한 검증)
- Discovery Step 1 (Brand) end-to-end 작동
- BrandDirectionCard + CardGrid5 (chosen variant)
- `/new/discovery/step/1/page.tsx` 라우트
- `npm run dev` 후 브라우저에서 카드 5장 표시 + 선택 가능

#### G3. Vertical 확장
- Discovery Step 2~7 (Step 1 패턴 재사용)
- Step 5 ToneChipsForm (다중선택 chip)
- Step 6 DirectionApprovalCard (verbose)
- Step 7 Generate (Phase 1 PlanCard 재사용)

#### G4. Quick Mode 흐름
- QuickInputCard (initial + follow_up_question 분기)
- 4-step routes
- DirectionApprovalCard minimal variant

#### G5. Mode Branching
- `lib/mode_branching.ts` (yaml → TS)
- `/new/page.tsx` 진입 라우팅
- 4 branching_rules + 3 override_rules

#### G6. 통합 + 검증
- `audit_page_component.ps1` (D5 deferred 처리)
- `smoke_test_phase_3.ps1`
- 변경성 시뮬레이션 5/5 회귀 PASS
- retrospective + archive

---

## 우선순위

```
G1 (Foundation) > G2 (Thin Vertical 검증) > G5 (Branching) > G3 (Discovery 확장) ∥ G4 (Quick) > G6 (통합)
```

G2가 가장 중요 — Phase 2 spec → 코드 변환의 "검증" 단계. 여기서 패턴이 작동하면 G3/G4는 단순 복제.

---

## 비-목표

- 모든 spec 결정 변경 (Phase 2 read-only)
- component_map.md 수정 (조정 4번)
- PlanCard 4-layer 정합 (조정 3번, Phase 4)
- PlanComparisonCard 상세 (Phase 4)
- 모든 컴포넌트 variants 구현 (chosen만, 나머지 variant prop 자리)
- Phase 5 Auth / Phase 9 피드백 / Phase 11+ i18n

---

## 관련 문서

- `scope.md` — Slice별 범위
- `acceptance.md` — A1~A10 완료 기준
- `assumptions.md` — phase-start v1.3.0 §6 4점검 결과
- `work_plan.md` — Slice 1~6 분해
- `multi_slice_plan.md` — Wave 1~5
- `handoff.md` — Phase 3 → Phase 4 이관
- `apps/web/design_handoff.md` (Phase 2) — 변경 가이드 baseline
- `apps/web/component_map.md` (Phase 2, read-only) — 단일 진실 소스
