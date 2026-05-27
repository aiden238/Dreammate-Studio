# Phase 2 — Handoff

> 진행 중 컨텍스트 + Phase 3 이관 정보. 종료 시 closing_notes.md로 보강 후 archive.

---

## 현재 진행 상황

```yaml
status: active
started: 2026-05-27
last_updated: 2026-05-27
completed_slices: []
in_progress: []
blocked_by: []
next_action: "Wave 1 — Slice 1 Design System Foundation sub-agent dispatch"
```

---

## Phase 2 → Phase 3 이관 사항

### 이관 데이터

Phase 2 완료 시 Phase 3에 넘기는 것:

- `apps/web/design_system/` (4 파일 + 2 ADR) — tokens / 4-layer template / variants format / replaceability
- `apps/web/discovery_flow.md` (§0 + §1 상세 + §2~§7 간략)
- `apps/web/quick_flow.md`
- `apps/web/mode_branching.md` (yaml)
- `apps/web/direction_approval.md`
- `apps/web/page_map.md` (통합 갱신)
- `apps/web/component_map.md` (4-layer 4개 + 기타)
- `apps/web/design_handoff.md` (변경 가이드)
- `apps/web/wireframes/` (step1 / direction_approval / quick_short / plan_comparison_placeholder)
- `eval/qa_reports/phase-2-final_2026-05-27.md`
- `meta/retrospectives/phase-2.md`

### Phase 3에서 해결할 잔여 (deferred 5)

| ID | 항목 | 처리 시점 |
|---|---|---|
| D1 | Step 2~7 wireframe 상세 | Phase 3 진입 시 template 적용으로 자동 도출 |
| D2 | QuickInputCard variants 추가 | Phase 3 구현 중 alt 발생 시 |
| D3 | PlanCard 4-layer 정합 | Phase 3 코드 작성 후 회고 정합 |
| D4 | PlanComparisonCard 상세 | Phase 4 (3-plan 활성화 시) |
| D5 | audit_page_component.ps1 | Phase 3 실 파일 생긴 후 작성 |

---

## context-compact 시 보존 필수 항목

다음 세션 진입 시 반드시 로드:

```
1. PROJECT_STATE.md
2. phases/active/phase-2-pwa-design/goals.md
3. phases/active/phase-2-pwa-design/assumptions.md  ← 4점검 결과
4. phases/active/phase-2-pwa-design/work_plan.md    ← 다음 작업 단위
5. phases/active/phase-2-pwa-design/multi_slice_plan.md ← Wave 분할
6. apps/web/design.md (Phase 0)
7. apps/web/design_system/component_contract.md (Slice 1 완료 후)
```

위 7개만 로드해도 Phase 2 작업 재개 가능.

---

## 진행 트래킹

```yaml
phase_2_progress:
  current_wave: 1
  current_slice: 1
  total_slices: 6
  completed_slices: []
  estimated_hours_total: 11-17
  estimated_hours_elapsed: 0
  blockers: []
  next_action: "Wave 1 Slice 1 — Design System Foundation 작성 (tokens + 4-layer template + variant format + replaceability)"
  last_updated: 2026-05-27
```

---

## 미해결 결정 사항 (Slice 진행 중 결정 필요)

| 항목 | 옵션 | 결정 시점 |
|---|---|---|
| Step 5 Tone form 패턴 구체 형식 | 슬라이더 / 다중선택 / textarea | Slice 3 진입 시 |
| Direction Approval verbose variant의 "이유 표시" 형식 | bullet / paragraph / table | Slice 3 진입 시 |
| Mode branching의 "user 명시 override" 버튼 위치 | header / footer / fab | Slice 4 진입 시 |
| design_handoff.md 변경 시나리오 5개 외 추가? | 6번째 시나리오? | Slice 5 진입 시 |
| Wave 3 병렬 sub-agent의 component_map 동시 수정 방지 | sub-section 분리 / lock 정책 | Wave 3 dispatch 직전 |

각 결정은 발생 시점에 work_plan.md에 기록 또는 ADR 추가.

---

## 위험 요소 (Phase 2 진행 중 모니터링)

| # | 위험 | 모니터링 방법 | 임계값 |
|---|---|---|---|
| R1 | scope creep (모든 컴포넌트에 4-layer 유혹) | 매 Slice 종료 시 4-layer 대상 컴포넌트 수 확인 | 4개 초과 시 alert |
| R2 | over-engineering (Variants 추가) | 매 Slice 종료 시 variants 작성된 컴포넌트 수 확인 | 3개 초과 시 alert |
| R3 | design-review Skill 절차 부재 | Slice 6에서 첫 사용 시 발견 가능 | P-X proposal 등록 |
| R4 | Discovery Step 2~7이 너무 간략해서 Phase 3 진입 시 정보 부족 | Slice 3 종료 시 사용자 manual 리뷰 | 4줄 명세로 충분한지 결정 |
| R5 | Step 5 Tone form 패턴 미해결 | Slice 3 dispatch 전 결정 | sub-agent에 명시 |
| R6 | Wave 3 병렬 sub-agent의 component_map 충돌 | Wave 3 dispatch 시 sub-section 명시 | manual review |

---

## 관련 문서

- 진입 점검 보고서: `eval/qa_reports/phase-2-entry-check_2026-05-27.md`
- 4-layer + Variants 결정 ADR: Slice 1에서 ADR-010 / ADR-011 작성
- Phase 2 폴더: `phases/active/phase-2-pwa-design/`
- Phase 1 archive: `phases/archive/phase-1-mvp-basic-flow/`
- 회고 P1~P4: `meta/proposals/2026-05-26_phase-1-retrospective-proposals.md` (accepted_all)

---

## 종료

다음 작업 진행 시:
1. 본 handoff 참조해 Phase 2 컨텍스트 재구성
2. `work_plan.md` Slice 1부터 진입
3. 각 Slice 완료 시 본 파일 `phase_2_progress` 블록 갱신
4. Phase 2 완료 시 `meta-retrospective` Skill로 회고 → `meta/retrospectives/phase-2.md`
5. `phase-complete` v1.1.0 절차 (Skill SKILL.md §1.5 자동 smoke test도 호출 — Phase 2는 코드 무변경이라 manual checklist만으로 대체 가능)
