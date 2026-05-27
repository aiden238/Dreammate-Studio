# Phase 2 — Work Plan (Slice 1~6)

> phase-start v1.2.0 §6.2 Simplest Slice 기반 분해
> 작성일: 2026-05-27
> 원칙: 변경 가능성 우선 (over-engineering 회피)

---

## Slice 개요

```
Slice 1 → Slice 2 → Slice 3 || Slice 4 → Slice 5 → Slice 6
  Foundation  Brand template   Direction  Quick    통합 +    검증
                                Approval   Mode   handoff
                                + Disc 2~7 + Branch
```

각 Slice 완료 = 1 commit + audit_naming PASS + 다음 Slice 진입 권한.

---

## Slice 1 — Design System Foundation ★ 가장 중요

**목표**: 4-layer + Variants Bank + Replaceability 형식 정립. 후속 Slice가 이 baseline 재사용.

### 산출물 (4 + 2)
- `apps/web/design_system/tokens.md` (6 카테고리: color / typography / spacing / radius / breakpoint / motion)
- `apps/web/design_system/component_contract.md` (4-layer template + BrandDirectionCard 예시 1개)
- `apps/web/design_system/variant_format.md` (yaml schema + 예시)
- `apps/web/design_system/replaceability_score.md` (L/M/H 정책 + 예시)
- `docs/decisions/phase_2_design_layered_minimal.md` (ADR-010)
- `docs/decisions/phase_2_variants_3_components.md` (ADR-011)

### Acceptance
- 4 design_system 파일 작성
- ADR-010 + ADR-011
- BrandDirectionCard 4-layer 예시 (component_contract.md 안에 포함)
- audit_naming 0 drift

### 추정 시간: 2~3h

### Commit message
```
phase-2(slice-1): design system foundation (tokens + 4-layer + variants + replaceability)
```

---

## Slice 2 — Discovery Step 1 (Brand) + 5-card Template

**목표**: Slice 1 정립한 4-layer + variants 형식으로 Brand card + 5-card 패턴 적용. 후속 Slice 재사용 baseline.

### 산출물
- `apps/web/discovery_flow.md` §0 (개요) + §1 (Step 1 Brand 상세)
- `apps/web/wireframes/step1_brand.md` (ASCII art, 360px 적합)
- `apps/web/component_map.md` 갱신:
  - `BrandDirectionCard` 4-layer (Behavior / Layout / Visual / Wireframe) + variants 3개 (current / horizontal_swipe / grid_2x3) + replaceability M
  - `CardGrid5` 4-layer + variants 2~3개 + replaceability M

### Acceptance
- discovery_flow.md §0 + §1 작성
- wireframes/step1_brand.md ASCII art
- 2 컴포넌트 4-layer + variants
- audit_naming 0 drift

### 추정 시간: 2~3h

### Commit message
```
phase-2(slice-2): Discovery Step 1 + BrandDirectionCard 4-layer template
```

---

## Slice 3 — Direction Approval Pattern (격상) + Discovery Step 2~7

**목표**: 양 모드 공통 핵심 UX인 Direction Approval을 별도 spec으로 격상. Discovery Step 2~7은 Step 1 template 재사용으로 간략 명세.

### 산출물
- `apps/web/direction_approval.md` (NEW)
- `apps/web/wireframes/direction_approval.md`
- `apps/web/component_map.md` 갱신:
  - `DirectionApprovalCard` 4-layer + variants 2개 (minimal / verbose) + replaceability M
- `apps/web/discovery_flow.md` §2 ~ §7 (각 4줄 명세):
  - §2 Step 2 Domain: P-002 / BrandDirectionCard 재사용 / 입력: Brand 선택 / 다음: Step 3
  - §3 Step 3 Series: P-003 / BrandDirectionCard 재사용 / ...
  - §4 Step 4 Target: P-004 / ...
  - §5 Step 5 Tone: P-004 / **form 패턴 변형 (5-card 예외)** / 슬라이더 또는 다중선택 / 다음: Step 6
  - §6 Step 6 Direction Summary: P-005 / **DirectionApprovalCard 사용** (direction_approval.md 참조) / 입력: Step 1~5 종합 / 다음: Step 7
  - §7 Step 7 Generate: P-006 / progress stepper 4단계 / 입력: Direction 승인 / 다음: /plan 결과 페이지

### Acceptance
- direction_approval.md + wireframe + 컴포넌트 4-layer + variants
- discovery_flow.md §2 ~ §7 6개 section 4줄 명세
- Step 5 form 변형 명시
- Step 6 DirectionApprovalCard cross-reference
- audit_naming 0 drift

### 추정 시간: 2~3h

### Commit message
```
phase-2(slice-3): Direction Approval pattern (격상) + Discovery Step 2~7 간략
```

---

## Slice 4 — Quick Mode + Mode Branching

**목표**: 짧은 프롬프트 flow + Discovery vs Quick 자동 분기 규칙 yaml.

### 산출물
- `apps/web/quick_flow.md`
  - 짧은 프롬프트 입력 → 부족 정보 1~2 질문 → DirectionApprovalCard → Generate
  - direction_approval.md cross-reference
- `apps/web/mode_branching.md` (yaml)
  - branching_rules 배열 (최소 3 condition)
  - override 규칙 ("user 명시 'new project'")
- `apps/web/wireframes/quick_short.md`
- `apps/web/component_map.md` 갱신:
  - `QuickInputCard` 4-layer + variants는 current만 + replaceability L

### Acceptance
- 3 파일 + 1 컴포넌트
- mode_branching yaml format 정합
- audit_naming 0 drift

### 추정 시간: 2~3h

### Commit message
```
phase-2(slice-4): Quick Mode + Mode Branching yaml
```

---

## Slice 5 — page_map / component_map 통합 + Design Handoff (★ Phase 2 핵심)

**목표**: 모든 Slice 통합 + Phase 2의 가장 중요한 산출물인 design_handoff.md 작성.

### 산출물
- `apps/web/page_map.md` 통합 갱신:
  - 모든 routes: `/` (Phase 1) / `/discovery/step/{1..7}` / `/quick` / `/plan` / 기타 placeholder
  - 각 route가 사용하는 컴포넌트 명시
- `apps/web/component_map.md` 통합 갱신:
  - 4-layer 4개 컴포넌트 (Slice 1~4 종합)
  - 기타 minimal entries (PlanCard / ErrorCard / ProgressStepper / SubmitButton — Phase 1 기존)
  - `PlanComparisonCard` Phase 4 placeholder 1줄
  - Replaceability 통합 매트릭스
- `apps/web/design_handoff.md` (NEW, ★ 핵심):
  - 변경 시나리오 5개 매핑표
  - Replaceability 종합 표
  - Phase 3 진입 시 variants 선택 절차
  - Phase 4+ 디자인 갱신 시 영향 범위 예측
- `apps/web/wireframes/plan_comparison_placeholder.md` (1줄 placeholder)

### Acceptance
- page_map / component_map 통합 정합
- design_handoff.md 5 시나리오 매핑표
- audit_naming 0 drift
- manual checklist: page ↔ component 정합 (모든 page의 컴포넌트가 component_map에 존재)

### 추정 시간: 2~3h

### Commit message
```
phase-2(slice-5): page_map + component_map 통합 + design_handoff (변경 가이드)
```

---

## Slice 6 — design-review + retrospective + archive

**목표**: 최종 검증 + 회고 + archive 이동.

### 산출물
- `eval/qa_reports/phase-2-final_2026-05-27.md`:
  - qa-check v1.2.0 11 카테고리
  - Simplicity Check 5/5
  - **변경성 시뮬레이션 5개** (assumptions.md §4.3)
  - design-review Skill 결과
- `meta/retrospectives/phase-2.md`:
  - 4점검 결과 + U2-X 검증
  - 잘된/안 된/배운/근본 원인
  - 개선 제안 (있다면)
- `phases/active/phase-2-pwa-design/closing_notes.md`
- `phases/active → archive/phase-2-pwa-design/` 이동
- PROJECT_STATE / PHASE_REGISTRY 갱신 (Phase 2 done, Phase 3 active next)

### Acceptance
- qa-check 11 카테고리 통과 (Critical 0)
- 변경성 시뮬레이션 5/5 PASS
- design-review Skill 결과 첨부
- retrospective 작성
- archive 이동 완료

### 추정 시간: 1~2h

### Commit message
```
phase-2(slice-6): final QA + design-review + retrospective + archive
```

---

## 전체 추정

| Slice | 시간 | 누적 |
|---|---|---|
| 1 | 2~3h | 2~3h |
| 2 | 2~3h | 4~6h |
| 3 | 2~3h | 6~9h |
| 4 | 2~3h | 8~12h |
| 5 | 2~3h | 10~15h |
| 6 | 1~2h | 11~17h |

**Phase 2 총 추정**: 11~17h (Phase 1의 약 60% 수준)

---

## Slice 진입 규칙

```
1. 이전 Slice acceptance 모두 통과 확인
2. audit_naming 0 drift 확인
3. 다음 Slice의 산출물 / acceptance 재확인
4. (병렬 Slice 3 + 4) 충돌 영역 (component_map) sub-section 분리 명시
5. Sub-agent dispatch 또는 main session 작업
6. 완료 시:
   - audit_naming
   - manual checklist (Slice별)
   - git commit (Slice 단위)
   - PROJECT_STATE 갱신
```

---

## scope creep 경고

다음 발견 시 즉시 중단:
- assumptions.md §3.2 read-only 파일 수정 필요성
- non_goals.md 항목 spec 작성 유혹 (Plan 비교 카드, audit script 등)
- 4-layer 4개 초과 컴포넌트
- Variants Bank 3개 초과
- Step 2~7 wireframe 상세 (간략 4줄로 충분)

→ 사용자에게 알림 + 결정 요청.

---

## 변경 이력

- 2026-05-27: Slice 1~6 최초 작성 (Simplest Slice 도출 결과)
