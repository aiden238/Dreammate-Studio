# Phase 2 — Acceptance Criteria

> 10개 항목 모두 통과해야 Phase 2 완료. 미달 시 phase-complete 차단.

---

## A1. Design System Foundation 완성

```
체크: apps/web/design_system/ 폴더에 4 파일 + 2 ADR 존재
기준:
  - tokens.md: 6 카테고리 (color/typography/spacing/radius/breakpoint/motion)
  - component_contract.md: 4-layer template + 예시 1개 (BrandDirectionCard)
  - variant_format.md: yaml schema + 예시
  - replaceability_score.md: L/M/H 정책 + 예시
  - docs/decisions/phase_2_design_layered_minimal.md (ADR-010)
  - docs/decisions/phase_2_variants_3_components.md (ADR-011)
```

- [ ] 4 파일 + 2 ADR 존재
- [ ] tokens.md 6 카테고리 모두 작성

---

## A2. 4-layer 핵심 컴포넌트 4개 완성

```
체크: component_map.md에 다음 4개 컴포넌트가 4-layer 모두 작성됨
대상:
  1. BrandDirectionCard
  2. CardGrid5
  3. DirectionApprovalCard
  4. QuickInputCard
4-layer:
  - ## Behavior (props, state, events)
  - ## Layout (배치, breakpoint)
  - ## Visual (tokens 참조)
  - ## Wireframe (ASCII 또는 ref to wireframes/)
```

- [ ] 4개 컴포넌트 × 4-layer = 16 sections
- [ ] grep `"## Behavior\|## Layout\|## Visual\|## Wireframe" apps/web/component_map.md` 16+ 매치

---

## A3. Variants Bank 3개 컴포넌트 완성

```
체크: 다음 3개 컴포넌트에 variants yaml block 존재
대상:
  1. BrandDirectionCard: current + alt 2개 (horizontal_swipe / grid_2x3)
  2. CardGrid5: current + alt 1~2개
  3. DirectionApprovalCard: minimal + verbose
각 variant:
  - id
  - name
  - layout
  - tradeoff_pros / tradeoff_cons
```

- [ ] 3 컴포넌트 × variants yaml block
- [ ] 각 컴포넌트 minimum 2 variants

---

## A4. Discovery Step 1 상세 + Step 2~7 간략 명세

```
체크: apps/web/discovery_flow.md 작성
기준:
  - §0 개요 (7단계 흐름 도식)
  - §1 Step 1 Brand 상세 (4-layer 컴포넌트 사용)
  - §2~§7 각 4줄 명세 (prompt_id / pattern / 입력 / 다음 단계)
  - Step 5 Tone form 패턴 변형 명시
  - wireframes/step1_brand.md 존재
```

- [ ] discovery_flow.md §0 + §1 + §2~§7 (8 sections)
- [ ] wireframes/step1_brand.md ASCII art
- [ ] Step 5 Tone 예외 명시 (5-card → form 변형)

---

## A5. Direction Approval Pattern 독립 spec

```
체크: apps/web/direction_approval.md 존재 + Discovery flow / Quick flow 모두 cross-reference
기준:
  - Behavior: 텍스트 + 편집 textarea + 3 버튼
  - Layout: mobile 360px
  - Visual: tokens 참조
  - Wireframe: wireframes/direction_approval.md
  - Variants: minimal / verbose
  - Discovery Step 6과 Quick mode 모두 본 컴포넌트 사용 명시
```

- [ ] direction_approval.md 작성
- [ ] discovery_flow.md §6에서 DirectionApprovalCard 참조 명시
- [ ] quick_flow.md에서 DirectionApprovalCard 참조 명시

---

## A6. Quick Mode + Mode Branching

```
체크:
  - apps/web/quick_flow.md 작성 (짧은 프롬프트 → 부족 정보 질문 → Direction Approval → Generate)
  - apps/web/mode_branching.md 작성 (yaml 분기 트리)
  - wireframes/quick_short.md
기준:
  - mode_branching yaml: branching_rules 배열 + override 규칙
  - 최소 3개 branching condition (no_brand / brand_no_series / has_series)
```

- [ ] quick_flow.md
- [ ] mode_branching.md (yaml format)
- [ ] wireframes/quick_short.md

---

## A7. page_map + component_map 통합 갱신

```
체크: 통합 갱신 후 정합성
기준:
  - page_map.md: 모든 routes (/discovery/step/{n} / /quick / /plan / 기타) 명세
  - component_map.md: 4-layer 4개 + 기타 minimal (이름 + 의존성 + Phase 진입 시점)
  - PlanComparisonCard: Phase 4 placeholder 1줄
```

- [ ] page_map.md 갱신
- [ ] component_map.md 갱신
- [ ] 모든 page가 사용하는 컴포넌트가 component_map에 존재 (manual checklist)

---

## A8. Design Handoff 가이드 (Phase 2 핵심 산출물)

```
체크: apps/web/design_handoff.md 작성
기준:
  - 변경 시나리오 5개 매핑표 (예: "색 변경" → tokens.md / "Discovery 단계 변경" → ...)
  - Replaceability 통합 매트릭스
  - Phase 3 진입 시 variants 선택 절차
  - Phase 4+ 디자인 갱신 시 영향 범위 예측
```

- [ ] design_handoff.md 작성
- [ ] 변경 시나리오 5개 명시
- [ ] 매핑표 vs 실제 파일 정합 (manual walkthrough)

---

## A9. 변경성 시뮬레이션 5개 통과 (Slice 6)

```
체크: design_handoff.md의 5 시나리오를 manual walkthrough
시나리오:
  1. "tokens.md 색 변경" → 영향 파일 ≤ 1
  2. "BrandDirectionCard variants swap" → 영향 파일 ≤ 2
  3. "Discovery 7→5 단계 축소" → 영향 파일 ≤ 4
  4. "Direction Approval minimal→verbose swap" → 영향 파일 ≤ 1
  5. "Quick mode 폐기" → 영향 파일 ≤ 5
```

- [ ] 5 시나리오 walkthrough 결과 기록 (eval/qa_reports/phase-2-final §변경성 Eval)
- [ ] 모두 영향 범위 정합 PASS

---

## A10. audit_naming 0 drift + Skill 절차 통과

```
체크: 자동 + Skill 검증
기준:
  - scripts/audit_naming.ps1 0 drift (Slice별 + 최종)
  - design-review Skill (Slice 6) 실행 + 결과 첨부
  - qa-check v1.2.0 11 카테고리 통과 (3+ partial 허용, critical 0)
  - Phase 2 retrospective (meta/retrospectives/phase-2.md)
```

- [ ] audit_naming PASS (최종)
- [ ] design-review Skill 결과
- [ ] qa-check 11 카테고리 통과
- [ ] retrospective 작성

---

## Done Definition

위 A1~A10 모두 통과 + git commit (Slice 1~6) + push 완료 + archive 이동.

## 이후 Phase

**Phase 3. Next.js PWA UI 구현** — Phase 2 spec 기반 실 코드 작성.
