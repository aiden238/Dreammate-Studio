# Phase 3 — Handoff

> 진행 중 컨텍스트 + Phase 4 이관. 종료 시 closing_notes.md로 보강 + archive.

---

## 현재 진행 상황

```yaml
status: active
started: 2026-05-28
last_updated: 2026-05-28
completed_slices: []
in_progress: []
blocked_by: []
next_action: "Wave 1 Slice 1 sub-agent dispatch — Foundation (Tailwind tokens 매핑)"
```

---

## Phase 3 → Phase 4 이관 사항

### 이관 데이터

Phase 3 완료 시 Phase 4에 넘기는 것:
- 실 .tsx 컴포넌트 4개 (BrandDirectionCard / CardGrid5 / DirectionApprovalCard / QuickInputCard) + ToneChipsForm
- /new/* routes (Discovery 7-step + Quick 4-step)
- /new/page.tsx (Mode Branching middleware)
- lib/ (design_tokens / mode_branching / state machines)
- Phase 2 spec 100% 충실 (drift는 deviation_log에 기록)
- scripts/audit_page_component.ps1 (D5)
- scripts/smoke_test_phase_3.ps1

### Phase 4 해결할 잔여 (D2/D3/D4)

| ID | 항목 | 진입 시점 |
|---|---|---|
| D2 | QuickInputCard alt variants | Phase 4 실 사용자 데이터 발생 시 |
| D3 | PlanCard 4-layer 정합 | Phase 4 3-plan 활성화 시 PlanComparisonCard와 함께 |
| D4 | PlanComparisonCard 상세 spec | Phase 4 진입 시 (api_contract §8.3 multi-step endpoint 활성화) |

---

## context-compact 시 보존 필수

다음 세션 진입 시 반드시 로드:
```
1. PROJECT_STATE.md
2. phases/active/phase-3-pwa-impl/goals.md
3. phases/active/phase-3-pwa-impl/assumptions.md  ← 4점검 결과
4. phases/active/phase-3-pwa-impl/work_plan.md
5. phases/active/phase-3-pwa-impl/multi_slice_plan.md
6. apps/web/design_handoff.md (Phase 2 baseline)
7. apps/web/component_map.md (Phase 2 baseline, read-only)
8. .claude/skills/phase-start/SKILL.md (v1.3.0, P-X1 §SELF-VERIFICATION 참조)
```

---

## 진행 트래킹

```yaml
phase_3_progress:
  current_wave: 1
  current_slice: 1
  total_slices: 6
  total_waves: 5
  completed_slices: []
  estimated_hours_total: 14.5-21
  estimated_hours_elapsed: 0.5  # P-X1 pre-entry
  blockers: []
  next_action: "Wave 1 Slice 1 — Foundation (Tailwind config + tokens.md 매핑)"
  last_updated: 2026-05-28
  deviation_count: 0  # 조정 4번 추적 (component_map drift)
```

---

## 미해결 결정 (Slice 진행 중)

| 항목 | 옵션 | 결정 시점 |
|---|---|---|
| ToneChipsForm chip 개수 (U3-5) | 6 / 8 / 10 | Slice 3 dispatch 전 (기본 8) |
| Step 7 generate UX | Phase 1 endpoint 직접 호출 / mock 모드 | Slice 3 진입 시 (기본 Phase 1 endpoint 직접) |
| /new middleware vs page.tsx redirect | middleware.ts / page.tsx (Phase 5 Auth와 통합?) | Slice 5 진입 시 (기본 page.tsx redirect — ADR-013) |
| Slice 2 unit test 작성 여부 | yes (smoke level) / no (e2e만) | Slice 2 진입 시 (기본 yes, 컴포넌트당 1~2 케이스) |

---

## 위험 모니터링

| # | 위험 | 임계값 | 완화 |
|---|---|---|---|
| R1 | spec ↔ 코드 drift (component_map vs 실 코드) | drift 1건 이상 | sub-agent prompt에 design_handoff 매핑 명시 + Slice 6 변경성 시뮬 회귀 |
| R2 | sub-agent forbidden 침범 재발 | 1건이라도 | **P-X1 §SELF-VERIFICATION 의무 + main session 후속 검증** |
| R3 | hardcoded 색 발생 (tokens 매핑 누락) | 1건이라도 | Slice 6 grep + audit_page_component |
| R4 | component_map.md 수정 발생 (조정 4번 위반) | **0건 강제** | sub-agent prompt에 read-only 절대 명시 + main session diff 검증 |
| R5 | Phase 1 endpoint 1-plan vs Discovery 7-step UX mismatch | Slice 3 진입 시 | Phase 4 multi-step migration 어댑터 명시 |
| R6 | Step 5 ToneChipsForm UX 불확실 | Slice 3 manual | 8 chips + skip 버튼 기본 |
| R7 | session storage state machine 충돌 | Slice 4/5 manual | wizard.discovery.* / wizard.quick.* prefix 분리 |

---

## 관련 문서

- 진입 점검 보고서: `eval/qa_reports/phase-3-entry-check_2026-05-28.md`
- 4 조정 결정: 사용자 지시 ("Phase 3 진입은 OK. 단, 아래 4개를 조정한 뒤 진입.")
- P-X1 변경 로그: `docs/contract_changes/2026-05-28-px1-sub-agent-self-verification.md`
- Phase 2 archive: `phases/archive/phase-2-pwa-design/`
- 회고 패턴: `meta/patterns.md` (P-DRIFT-001 / P-SLICE-001 / P-GRACEFUL-001 / P-FOLDER-PARALLEL-001 / P-AGENT-SCOPE-001 / P-DESIGN-LAYERED-001)

---

## 종료

다음 작업:
1. PROJECT_STATE / PHASE_REGISTRY Phase 3 active 갱신
2. 진입 commit + push
3. **Wave 1 Slice 1 sub-agent dispatch** (Foundation)
4. 이후 Wave 2 (Thin Vertical) → Wave 3 병렬 (Discovery 확장 ∥ Quick) → Wave 4 (Middleware) → Wave 5 (통합 + 회고)
