# Phase 2 — Multi-Slice Execution Plan (Wave 1~5)

> 작성: 2026-05-27 (Phase 2 진입 시)
> 방식: sub-agent 분산 (context 관리 + 병렬 가능 시 병렬)
> 원칙: 폴더/파일 분리로 충돌 0 (P-FOLDER-PARALLEL-001)

---

## 1. 의존성 그래프

```
Slice 1 (Foundation) ─→ Slice 2 (Brand template)
                              ↓
                ┌─────────────┴─────────────┐
            Slice 3                       Slice 4
        (Direction +              (Quick + Mode
         Discovery 2~7)            Branching)
                ↓                         ↓
                └─────────────┬─────────────┘
                       Slice 5 (통합 + handoff)
                              ↓
                       Slice 6 (검증 + archive)
```

---

## 2. Wave 분할

### Wave 1 — 순차 (1 sub-agent)
- **A: Slice 1** — Design System Foundation (baseline)

### Wave 2 — 순차 (1 sub-agent)
- **B: Slice 2** — Brand card + 5-card template (Slice 1 사용)

### Wave 3 — 병렬 (2 sub-agents)
- **C: Slice 3** — Direction Approval + Discovery Step 2~7
- **D: Slice 4** — Quick Mode + Mode Branching

폴더/파일 분리:
- Slice 3 → `direction_approval.md` + `discovery_flow.md §2~§7` + component_map의 `DirectionApprovalCard`
- Slice 4 → `quick_flow.md` + `mode_branching.md` + component_map의 `QuickInputCard`

→ 분리 sub-section 명시로 component_map 동시 수정 회피.

### Wave 4 — 순차 (1 sub-agent)
- **E: Slice 5** — page_map / component_map 통합 + design_handoff.md

Slice 3/4의 component_map sub-section을 머지 + 종합 매트릭스 작성.

### Wave 5 — 순차 (1 sub-agent)
- **F: Slice 6** — design-review + retrospective + archive

총 sub-agent dispatch: **6**

---

## 3. 충돌 분석 매트릭스

| Wave | Slices | 변경 영역 | 충돌 위험 | 완화 |
|---|---|---|---|---|
| 1 | 1 | design_system/* (NEW), ADR 2개 | — (baseline) | — |
| 2 | 2 | discovery_flow §0+§1 + wireframes/step1 + component_map (2 컴포넌트) | — (단독) | — |
| 3 | 3 + 4 | (3): direction_approval / discovery_flow §2~§7 / component_map §DirectionApprovalCard ∥ (4): quick_flow / mode_branching / component_map §QuickInputCard | 0 (별도 sub-section) | sub-agent 프롬프트에 component_map 자기 sub-section만 명시 |
| 4 | 5 | page_map / component_map (통합) / design_handoff (NEW) | Slice 2~4 모두 끝난 후 sequential | — |
| 5 | 6 | eval / meta / phases/archive | 단일 sub-agent | — |

---

## 4. Sub-Agent 공통 절차

각 sub-agent 4-Phase 절차 수행:

```
Phase A. 컨텍스트 로딩 (필요한 design_system + 이전 Slice 산출물만 — Surgical Scope)
Phase B. 파일 생성 (4-layer + variants + replaceability 형식 준수)
Phase C. 정적 검증:
  - audit_naming 0 drift
  - manual grep (4-layer / variants / replaceability 존재 확인)
Phase D. 하네스 기록 + commit + push:
  - eval/qa_reports/phase-2-slice-{N}_{date}.md
  - git commit + push
```

---

## 5. Slice별 sub-agent prompt 핵심

### Slice 1 (Wave 1, 단독)
- editable: `apps/web/design_system/*` + ADR 2개
- forbidden: 다른 모든 영역 (apps/web/components, backend, phases/archive 등)
- baseline: 없음 (foundation 정립)
- acceptance: 4 파일 + 2 ADR + audit_naming PASS

### Slice 2 (Wave 2, 단독)
- editable: discovery_flow.md (§0+§1), wireframes/step1_brand.md, component_map.md (BrandDirectionCard + CardGrid5만)
- baseline: Slice 1 산출물
- acceptance: 4-layer + variants + audit_naming PASS

### Slice 3 (Wave 3, 병렬 A)
- editable: direction_approval.md, wireframes/direction_approval.md, discovery_flow.md §2~§7, component_map.md §DirectionApprovalCard만
- 명시 제약: "Slice 4 sub-agent가 동시에 quick_flow / mode_branching / QuickInputCard 작업 중. component_map의 다른 컴포넌트 sub-section 건드리지 말 것."
- baseline: Slice 1 + Slice 2

### Slice 4 (Wave 3, 병렬 B)
- editable: quick_flow.md, mode_branching.md, wireframes/quick_short.md, component_map.md §QuickInputCard만
- 명시 제약: "Slice 3 sub-agent가 동시에 direction_approval / Discovery 2~7 / DirectionApprovalCard 작업 중. component_map의 다른 컴포넌트 sub-section 건드리지 말 것."
- baseline: Slice 1 + Slice 2

### Slice 5 (Wave 4, 단독)
- editable: page_map.md, component_map.md (통합 갱신), design_handoff.md, wireframes/plan_comparison_placeholder.md
- baseline: Slice 1~4 종합
- acceptance: page ↔ component 정합 + design_handoff 5 시나리오 매핑표

### Slice 6 (Wave 5, 단독)
- editable: eval/qa_reports/phase-2-final, meta/retrospectives/phase-2, phases/active → archive 이동, PROJECT_STATE / PHASE_REGISTRY 갱신
- Skill 호출: design-review + qa-check + meta-retrospective + phase-complete

---

## 6. 안전 장치

### 6.1 Wave 내 sub-agent들이 동일 파일 수정 방지

- Wave 3: Slice 3 + Slice 4 → 각각 다른 핵심 파일 (direction_approval vs quick_flow) + component_map은 sub-section 분리

### 6.2 PROJECT_STATE / PHASE_REGISTRY 충돌 회피

- 모든 sub-agent에 PROJECT_STATE/PHASE_REGISTRY 수정 금지 명시
- main session이 Wave 완료 시 일괄 갱신 (또는 Slice 6 sub-agent만 수정)

### 6.3 git push 경쟁

- 각 sub-agent commit + push 자체 수행
- 병렬 push 시 한쪽 실패하면 → `git pull --rebase origin main` + 재push

---

## 7. 진행 트래킹

```yaml
phase_2_multi_slice_progress:
  wave_1:
    status: pending
    sub_agents: [A_slice_1]
  wave_2:
    status: pending
    sub_agents: [B_slice_2]
  wave_3:
    status: pending
    sub_agents: [C_slice_3, D_slice_4]
  wave_4:
    status: pending
    sub_agents: [E_slice_5]
  wave_5:
    status: pending
    sub_agents: [F_slice_6]
```

각 Wave 완료 시 본 파일 + PROJECT_STATE 갱신.

---

## 8. 종료 조건 (Phase 2 완료)

- Slice 1~6 commit + push
- audit_naming 0 drift
- design_handoff.md 5 시나리오 walkthrough PASS
- qa-check v1.2.0 11 카테고리 통과
- meta/retrospectives/phase-2.md 작성
- archive 이동

---

## 9. 변경 이력

- 2026-05-27: 최초 작성 (Phase 2 진입 시, Wave 1~5 분할)
