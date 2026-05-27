# Phase 2 — Goals

> Phase: 2 / design.md 기반 PWA 설계 (Discovery + Quick 분기)
> Status: active
> Started: 2026-05-27

---

## 핵심 목표

**PWA 화면 구현 (Phase 3) 전에, 변경 가능한 프론트 설계 기준을 만든다.**

Phase 2는 **구현이 아닌 설계 phase**. Next.js 컴포넌트 코드 작성은 Phase 3.

### 본질 정의

| 종전 접근 | Phase 2 접근 |
|---|---|
| "디자인을 확정한다" | "**디자인의 변경 가능성을 코드보다 먼저 보장한다**" |
| 단일 진실 = 화면 명세 | 단일 진실 = **컴포넌트 contract + 변경 절차** |
| Phase 3에서 spec 그대로 따름 | Phase 3 진입 시 variants 선택 + tokens.md 한 번에 swap 가능 |

### 세부 목표

#### G1. Design System Foundation (변경 가능성 기반)
- `apps/web/design_system/tokens.md` — color / typography / spacing / radius / breakpoint / motion
- `apps/web/design_system/component_contract.md` — 4-layer template (Behavior / Layout / Visual / Wireframe)
- `apps/web/design_system/variant_format.md` — Variants Bank yaml format
- `apps/web/design_system/replaceability_score.md` — L/M/H 단순 정책

#### G2. 4-layer + Variants 핵심 컴포넌트
- **4-layer 강제 (4개)**: BrandDirectionCard / CardGrid5 / DirectionApprovalCard / QuickInputCard
- **Variants Bank (3개)**: BrandDirectionCard / CardGrid5 / DirectionApprovalCard

#### G3. Discovery Wizard 7단계 + Quick Mode + Mode Branching
- Step 1 (Brand) 상세 + Step 2~7 패턴 반복 명세
- Direction Approval 카드 (양 모드 공통, 핵심 UX) **별도 Slice 격상**
- Quick Mode short flow + 분기 규칙 yaml

#### G4. page_map / component_map 통합 + Design Handoff
- 전체 page routes 명세
- 모든 컴포넌트 4-layer 또는 minimal entry
- **design_handoff.md** — "변경 요청 → 수정 파일 매핑표" (Phase 2의 가장 중요한 산출물)

#### G5. Phase 3 진입 인수 명확화
- Phase 3 sub-agent가 막힘없이 코드 작성 가능한 spec 완성도
- "Phase 2에서 안 한 것"이 Phase 3 deferred 목록에 명시적으로 인수

---

## 우선순위

```
G1 (Foundation) > G2 (4개 핵심) > G4 (handoff) > G3 (Discovery/Quick) > G5 (deferred 명시)
```

G1이 baseline — 후속 Slice는 G1 정립된 format 재사용.

---

## 비-목표 (non_goals.md 참조)

- Next.js 코드 작성 (Phase 3)
- 모든 컴포넌트 4-layer 강제
- Plan 비교 카드 상세 spec (Phase 4)
- audit_page_component.ps1 자동 도구 (Phase 3 이후)
- Discovery 7단계 모든 wireframe 상세
- 다국어 / 접근성 본격 적용 (Phase 11+)

---

## 관련 문서

- `scope.md` — Slice별 작업 범위
- `acceptance.md` — 완료 기준 (10개)
- `assumptions.md` — phase-start v1.2.0 §6 4점검 결과
- `work_plan.md` — Slice 1~6 분해
- `multi_slice_plan.md` — Wave 1~5 분할
- `handoff.md` — Phase 2 → Phase 3 이관
- `apps/web/design.md` (Phase 0) — 핵심 UX 규칙 (참조용, 보강 대상)
- `docs/contracts/frontend_design_contract.md` (Phase 0) — 디자인 contract (참조용)
- `meta/proposals/2026-05-26_phase-1-retrospective-proposals.md` — P1~P4 적용 완료 (Phase 2 진입 baseline)
