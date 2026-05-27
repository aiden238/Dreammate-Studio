# Phase 2 — Assumptions (phase-start v1.2.0 §6 4점검)

> 작성일: 2026-05-27
> Skill: phase-start v1.2.0 §6 (Assumptions / Simplest Slice / Surgical Scope / Verification)
> 적용: Phase 2 PWA 설계

---

## 1. Assumptions

### 1.1 확정 가정

| # | 가정 | 근거 |
|---|---|---|
| A1 | Phase 0/1 archive (design.md / page_map / component_map / PlanCard) baseline 가용 | `phases/archive/phase-0/1/` |
| A2 | tokens / 4-layer / variants 패턴이 over-engineering 위험 있음 | GPT 회고 + meta/proposals P1~P4 |
| A3 | Phase 2는 **spec only** — 코드 변경 0 | Phase 2 scope.md |
| A4 | Phase 3가 Phase 2 spec 100% 따라가게 작성 | dependencies.md / handoff.md |
| A5 | Phase 4 multi-step endpoint migration은 Phase 4에서 — Phase 2는 spec 형식만 | api_contract.md §8 |
| A6 | **audit_naming.ps1 0 drift** (Phase 2 진입 시점, 2026-05-27) | scripts/audit_naming.ps1 실행 결과 (v1.2.0 §6.1 cross-reference 점검 통과) |
| A7 | Sub-agent 폴더 분리 병렬 패턴 (P-FOLDER-PARALLEL-001) 채택 | meta/patterns.md |
| A8 | Variants Bank 적용은 3개 컴포넌트만 (BrandDirectionCard / CardGrid5 / DirectionApprovalCard) | 본 plan §변경 가능성 보증 메커니즘 |
| A9 | 4-layer 강제는 4개 컴포넌트만 (위 3 + QuickInputCard) | 본 plan |
| A10 | Discovery Step 2~7은 Step 1 template 재사용 (4줄 명세) | scope.md |

### 1.2 불확실 항목 (검증 필요)

| ID | 항목 | 검증 방법 | 미검증 시 영향 |
|---|---|---|---|
| U2-1 | Discovery 7단계가 사용자에게 자연스러운지 | Slice 6 사용자 manual 리뷰 | 단계 수 조정 / merge 검토 |
| U2-2 | 카드 5장 360px 한 화면 적합성 | Slice 2 wireframe + manual visual | 가로 스와이프 variants 활성화 |
| U2-3 | Mode 자동 분기 임계값 추가 필요한지 | Slice 4 + Phase 9 피드백 | branching yaml 보강 |
| U2-4 | Direction Approval 편집 vs 재생성 비율 | Phase 4 실 사용자 데이터 | minimal vs verbose variant 활성화 |
| U2-5 | Phase 1 → Phase 4 endpoint 어댑터 비용 | Phase 3 진입 시 | adapter layer spec 추가 |
| U2-6 | Variants 중 어떤 게 실 사용자에게 효과적 | Phase 9 피드백 | chosen variant 재선택 |
| U2-7 | Step 5 Tone form 패턴의 구체 형식 (슬라이더/다중선택/textarea) | Slice 3 dispatch 시 결정 | Slice 3 ADR로 기록 |
| U2-8 | design-review Skill 절차 부재 발견 가능성 | Slice 6 첫 사용 시 | P-X retrospective proposal 등록 |

**검증 결과 기록**: `eval/regression_results/phase-2-uncertainty-*.md` (필요 시) 또는 Slice별 QA report.

### 1.3 Contract cross-reference 점검 (v1.2.0 §6.1)

```
[2026-05-27] scripts/audit_naming.ps1 실행
결과:
  plan_candidates   PASS   0 drift
  video_projects    PASS   0 drift
  critic_evaluation PASS   0 drift
  rag_references    PASS   0 drift

→ Phase 1 CC-001 적용 + P1~P4 Skill 갱신 결과 유지됨.
→ Phase 2 진입 baseline OK.
```

---

## 2. Simplest Slice (3회 압축)

```
1차 답: Design system + Discovery 7단계 + Quick + Mode branching + 통합 + 검증 (6 Slices)
2차 답: Foundation(Slice 1) + Brand card template(Slice 2)만 (baseline 정립)
3차 답: BrandDirectionCard 1개 컴포넌트의 Behavior layer 명세 + tokens.md 시드 (5 카테고리)
```

**최종 Slice 1 baseline**:
- `apps/web/design_system/tokens.md` (6 카테고리)
- `apps/web/design_system/component_contract.md` (4-layer template + BrandDirectionCard 예시 1개)
- `apps/web/design_system/variant_format.md` (yaml schema)
- `apps/web/design_system/replaceability_score.md` (L/M/H)
- ADR-010 + ADR-011

→ Slice 1 정립 = 후속 5 Slices의 작업 비용 결정.

---

## 3. Surgical Scope

### 3.1 editable

```
apps/web/
  design.md                    (보강 only)
  page_map.md                  (통합 갱신)
  component_map.md             (통합 갱신, 4-layer 4개 + 기타 minimal)
  discovery_flow.md            (NEW, §0~§7)
  quick_flow.md                (NEW)
  mode_branching.md            (NEW, yaml)
  direction_approval.md        (NEW)
  design_handoff.md            (NEW, ★ 핵심)
  design_system/               (NEW 폴더)
    tokens.md
    component_contract.md
    variant_format.md
    replaceability_score.md
  wireframes/                  (NEW 폴더)
    step1_brand.md
    direction_approval.md
    quick_short.md
    plan_comparison_placeholder.md (1줄)

phases/active/phase-2-pwa-design/  (이미 작성)
  goals / scope / non_goals / acceptance / dependencies / handoff / assumptions
  work_plan / multi_slice_plan (다음 작성)

docs/decisions/
  phase_2_design_layered_minimal.md  (ADR-010, NEW)
  phase_2_variants_3_components.md   (ADR-011, NEW)

docs/contracts/
  frontend_design_contract.md   (보강 only — 새 컴포넌트 카탈로그)

eval/qa_reports/phase-2-*.md
meta/handoffs/2026-05-27_phase-2-entry.md
```

### 3.2 read-only

```
docs/contracts/ (frontend_design_contract 제외)
backend/        ← Phase 2 = frontend only
apps/web/app/   ← Phase 3 영역
apps/web/components/ ← Phase 3 영역 (현 PlanCard / ErrorCard / ProgressStepper / SubmitButton 보존)
apps/web/lib/   ← Phase 3 영역
ai_system/, knowledge/, product/, meta/ (handoffs / retrospectives 외)
eval/golden_set.md, failure_cases.md, INDEX.md
.claude/skills/  ← Skill 정의 read-only (필요 시 contract-change)
```

### 3.3 forbidden

```
phases/archive/  ← Phase 0/1
phases/planned/phase_3~30  ← 미래 영역
backend/spring/, apps/mobile/, packages/  ← Phase 21+
```

### 3.4 위반 감지

editable 외 파일 수정 필요성 시 → 작업 중단, 사용자에게 알림. scope creep 신호.

---

## 4. Verification (검증 체계)

### 4.1 자동 (Phase 2 범위)

| 검증 항목 | 도구 | Slice |
|---|---|---|
| audit_naming 0 drift | scripts/audit_naming.ps1 | 매 Slice 종료 |
| 4-layer 존재 grep | `grep -c "## Behavior\|## Layout\|## Visual\|## Wireframe" component_map.md` ≥ 16 | Slice 6 |
| Variants yaml 존재 grep | `grep -c "variants:" component_map.md` ≥ 3 | Slice 6 |
| Replaceability score 부여 grep | `grep -c "replaceability: [LMH]" component_map.md` | Slice 6 |

### 4.2 수동

| 검증 항목 | 방법 | Slice |
|---|---|---|
| design-review Skill | design.md vs 새 spec 일관성 | Slice 6 |
| Wireframe 360px 적합성 | 사용자 manual visual | Slice 2 / Slice 6 |
| 7-step 흐름 자연스러움 | 사용자 walkthrough | Slice 6 |
| design_handoff.md 매핑 정합 | 사용자 변경 시나리오 5개 walkthrough | Slice 5 / Slice 6 |

### 4.3 변경성 시뮬레이션 5개 (Slice 6 manual)

```
시나리오 1: "tokens.md 색 변경" → 영향 파일 ≤ 1 확인
시나리오 2: "BrandDirectionCard variants swap" → 영향 파일 ≤ 2 확인
시나리오 3: "Discovery 7→5 단계 축소" → 영향 파일 ≤ 4 확인
시나리오 4: "Direction Approval minimal→verbose swap" → 영향 파일 ≤ 1 확인
시나리오 5: "Quick mode 폐기" → 영향 파일 ≤ 5 확인
```

→ design_handoff.md 매핑표와 일치하면 PASS.

### 4.4 acceptance 매핑

A1~A10 (acceptance.md) → 각 Slice별 점검 표 (qa_reports에 기록).

---

## 5. 4점검 요약

| 점검 | 결과 요지 |
|---|---|
| Assumptions | 확정 10개 + 불확실 8개 (U2-1~8) + Contract cross-reference 0 drift |
| Simplest Slice | Slice 1 Design System Foundation (tokens + 4-layer template + variant format + replaceability) |
| Surgical Scope | editable 22+ 파일 / read-only 광범위 / forbidden 명확 |
| Verification | 자동 4개 + 수동 4개 + 변경성 시뮬레이션 5개 |

---

## 6. 다음 단계

1. `work_plan.md` 작성 (Slice 1~6 detail)
2. `multi_slice_plan.md` 작성 (Wave 1~5 분할)
3. `meta/handoffs/2026-05-27_phase-2-entry.md` 작성
4. `eval/qa_reports/phase-2-entry-check_2026-05-27.md` 작성
5. PROJECT_STATE.md 갱신 (Phase 2 active)
6. 진입 commit + push
7. **Wave 1 Slice 1 sub-agent dispatch**

---

## 7. 변경 이력

- 2026-05-27: Phase 2 진입 4점검 작성 (phase-start v1.2.0 §6 적용)
