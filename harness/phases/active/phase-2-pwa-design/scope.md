# Phase 2 — Scope

> Phase 2의 작업 범위. Scope 밖 요청은 non_goals 확인 + 후속 Phase로 이관.

---

## In Scope

### 1. Design System Foundation (Slice 1)

| 항목 | 위치 |
|---|---|
| tokens (6 카테고리) | `apps/web/design_system/tokens.md` |
| 4-layer template + 예시 1개 | `apps/web/design_system/component_contract.md` |
| Variants Bank yaml format | `apps/web/design_system/variant_format.md` |
| Replaceability L/M/H 정책 | `apps/web/design_system/replaceability_score.md` |
| ADR-010 (4-layer 채택) | `docs/decisions/phase_2_design_layered_minimal.md` |
| ADR-011 (Variants 3개 한정) | `docs/decisions/phase_2_variants_3_components.md` |

### 2. Discovery Step 1 + 5-card Pattern (Slice 2)

| 항목 | 위치 |
|---|---|
| Discovery flow 개요 + Step 1 상세 | `apps/web/discovery_flow.md` §0, §1 |
| Step 1 wireframe (ASCII) | `apps/web/wireframes/step1_brand.md` |
| BrandDirectionCard (4-layer + 3 variants) | `apps/web/component_map.md` 추가 |
| CardGrid5 (4-layer + 3 variants) | `apps/web/component_map.md` 추가 |

### 3. Direction Approval Pattern (Slice 3 — 격상)

| 항목 | 위치 |
|---|---|
| Direction Approval 독립 spec | `apps/web/direction_approval.md` |
| Direction Approval wireframe | `apps/web/wireframes/direction_approval.md` |
| DirectionApprovalCard (4-layer + 2 variants minimal/verbose) | `apps/web/component_map.md` 추가 |
| Discovery Step 2~7 간략 명세 (4줄 패턴 명세) | `apps/web/discovery_flow.md` §2~§7 |

### 4. Quick Mode + Mode Branching (Slice 4)

| 항목 | 위치 |
|---|---|
| Quick Mode short flow | `apps/web/quick_flow.md` |
| Mode 자동 분기 yaml | `apps/web/mode_branching.md` |
| Quick wireframe | `apps/web/wireframes/quick_short.md` |
| QuickInputCard (4-layer, variants는 current만) | `apps/web/component_map.md` 추가 |

### 5. 통합 + Design Handoff (Slice 5)

| 항목 | 위치 |
|---|---|
| 전체 page routes | `apps/web/page_map.md` 통합 갱신 |
| 모든 컴포넌트 목록 + 4-layer 강제 4개 / 나머지 minimal | `apps/web/component_map.md` 통합 갱신 |
| 변경 시나리오 매핑표 | `apps/web/design_handoff.md` (NEW, **핵심**) |
| Plan 비교 카드 placeholder | `apps/web/component_map.md` 1줄 추가 (Phase 4 deferred) |

### 6. 검증 + 회고 (Slice 6)

| 항목 | 위치 |
|---|---|
| design-review Skill 실행 | manual |
| qa-check v1.2.0 (11 카테고리) | `eval/qa_reports/phase-2-final_2026-05-27.md` |
| 변경성 시뮬레이션 (5개) | 위 qa_report § 변경성 Eval |
| 회고 | `meta/retrospectives/phase-2.md` |
| archive 이동 | `phases/active → phases/archive/phase-2-pwa-design/` |

---

## 범위 경계

```
Phase 2 포함                              Phase 2 미포함
─────────────────────────────────         ─────────────────────────────────
*.md spec 파일 작성                        Next.js *.tsx 코드
4-layer (4개 컴포넌트만)                   4-layer (모든 컴포넌트)
Variants Bank (3개 컴포넌트)               Variants Bank (전체)
Discovery Step 1 상세                      Discovery Step 2~7 wireframe 상세
Direction Approval 상세                    Plan 비교 카드 상세 (Phase 4)
Quick Mode flow                            실제 컴포넌트 구현 (Phase 3)
mode_branching.md (yaml)                  audit_page_component.ps1 (Phase 3+)
design_handoff.md                          다국어 / 접근성 본격 (Phase 11+)
manual checklist + audit_naming (기존)     자동 정합성 도구 추가
```

---

## 예상 파일 변경 목록 (산출 추정)

```
신규 파일 (~22 개):
  apps/web/design_system/
    tokens.md
    component_contract.md
    variant_format.md
    replaceability_score.md
  apps/web/discovery_flow.md
  apps/web/quick_flow.md
  apps/web/mode_branching.md
  apps/web/direction_approval.md
  apps/web/design_handoff.md
  apps/web/wireframes/
    step1_brand.md
    direction_approval.md
    quick_short.md
    plan_comparison_placeholder.md
  docs/decisions/
    phase_2_design_layered_minimal.md (ADR-010)
    phase_2_variants_3_components.md (ADR-011)
  phases/active/phase-2-pwa-design/ (9 entry files — 이미 작성 중)
  eval/qa_reports/phase-2-{entry-check, slice-1~6, final}.md (8 files)
  meta/handoffs/2026-05-27_phase-2-entry.md
  meta/retrospectives/phase-2.md

수정 파일:
  apps/web/page_map.md (통합 갱신)
  apps/web/component_map.md (통합 갱신 — 4 핵심 컴포넌트 4-layer + 기타 minimal)
  apps/web/design.md (보강 only)
  docs/contracts/frontend_design_contract.md (보강 only)
  PROJECT_STATE.md / PHASE_REGISTRY.md
```

---

## 완료 기준 요약

전체 완료 기준은 `acceptance.md` 참조.  
핵심: **design_handoff.md의 변경 시나리오 5개가 실제 파일 매핑과 일치** + **4-layer 4개 컴포넌트 모두 작성** + **audit_naming 0 drift**.
