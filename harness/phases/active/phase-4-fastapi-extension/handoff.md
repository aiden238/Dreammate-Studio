# Phase 4 — Handoff

> 진행 중 컨텍스트 + Phase 4 → 다음 phase 이관 정보.

---

## 현재 진행 상황

```yaml
status: active
started: 2026-05-28
last_updated: 2026-05-28
completed_slices: []
in_progress: [Slice 1 Foundation]
blocked_by: []
next_action: "Wave 1 Slice 1 sub-agent dispatch — Foundation contract endpoints"
```

---

## Phase 4 → 다음 phase 이관 (Slice 4 retrospective에서 사용자 선택)

### 인수 항목 (deferred 명세)

| ID | 항목 | 권장 다음 phase |
|---|---|---|
| **D6** | Critic revise loop + Rewriter (P-008) | Phase 4.5 mini-phase 또는 Phase 6 |
| **D7** | SSE Progress streaming | Phase 5 (Auth/RLS와 함께) |
| **D8** | PlanComparisonCard 본격 4-layer | Phase 5+ |
| **D3** (Phase 3 인수 유지) | PlanCard 4-layer 재정의 | Phase 5+ (D4와 함께) |
| **D4** (Phase 3 인수 유지) | PlanComparisonCard 상세 | Phase 5+ |
| **D2** (Phase 3 인수 유지) | QuickInputCard alt variants | Phase 9 사용자 데이터 후 |
| **Phase 1 endpoint 제거** | 사용자 결정 5-a | Phase 8+ (마이그 완료 후) |

### 다음 phase 선택지 (Slice 4 retrospective + closing_notes에서 사용자 결정)

```
옵션 A: Phase 4.5 mini-phase
  - Critic revise loop + Rewriter (P-008)
  - 추정 시간: 8~12h
  - 다음 → Phase 5

옵션 B: Phase 5 DB/Auth (Critic revise는 Phase 6+)
  - Supabase Auth + RLS
  - SSE Progress (D7) 동시 처리 가능
  - 추정 시간: 15~20h
  - Critic revise는 Phase 6에 통합

옵션 C: 다른 우선순위 (Phase 6+, Phase 9 등)
  - 사용자 시점에서 우선순위 재평가
```

→ Slice 4 sub-agent가 retrospective에 위 3 옵션 명시 + 사용자가 결정.

---

## context-compact 시 보존 필수 항목

다음 세션 진입 시 반드시 로드:

```
1. PROJECT_STATE.md
2. phases/active/phase-4-fastapi-extension/goals.md
3. phases/active/phase-4-fastapi-extension/assumptions.md  ← 4점검 결과
4. phases/active/phase-4-fastapi-extension/work_plan.md    ← Slice 1~4
5. phases/active/phase-4-fastapi-extension/multi_slice_plan.md
6. docs/contracts/api_contract.md §8
7. docs/contracts/output_schema.md §8 (P-006) + §9 (P-007)
8. phases/archive/phase-3-pwa-impl/closing_notes.md (frontend baseline)
```

---

## 진행 트래킹

```yaml
phase_4_progress:
  current_wave: 1
  current_slice: 1
  total_slices: 4
  total_waves: 4
  completed_slices: []
  estimated_hours_total: 7-11
  estimated_hours_elapsed: 0
  blockers: []
  next_action: "Wave 1 Slice 1 — Foundation contract endpoints sub-agent dispatch"
  p_x1_streak_target: 4  # Slice 1~4 모두 §SELF-VERIFICATION PASS
  component_map_zero_lines_target: 4  # 11+ 연속 보존
  last_updated: 2026-05-28
```

---

## 미해결 결정 사항 (Slice 진행 중 결정)

| 항목 | 옵션 | 결정 시점 |
|---|---|---|
| `openai_models_for_3plan` default 값 | `["gpt-4o-mini"] × 3` vs `["gpt-4o-mini", "gpt-4o-mini", "gpt-4o"]` | Slice 2 dispatch 전 — 권장: 모두 gpt-4o-mini (cost 효율, 사용자 데이터 후 mix) |
| Phase 1 frontend `/plan` Phase 4 자동 redirect 여부 | 자동 redirect / 수동 안내만 | Slice 3 진입 시 결정 |
| component_map.md 갱신 필요성 (PlanComparisonCard placeholder) | contract-change Skill 발동 / Phase 5+로 미룸 | Slice 3/4에서 결정 |
| 다음 phase (사용자 결정 3-c) | A / B / C | **Slice 4 retrospective에서** |

각 결정은 발생 시점에 work_plan.md 또는 ADR로 기록.

---

## 위험 요소 (Phase 4 진행 중 모니터링)

| # | 위험 | 모니터링 | 임계값 |
|---|---|---|---|
| R1 | Phase 1 endpoint 회귀 | 매 Slice pytest 62/62 | 1 fail 즉시 alert |
| R2 | 3-plan approach_label 중복 | Slice 2 retry 1회 후 검증 | 3개 모두 unique 강제 |
| R3 | LLM cost (3 parallel) | Slice 2 측정 (예상: $0.001~0.005/호출) | $10/day 초과 시 alert |
| R4 | PlanCard × 3 360px 가독성 | Slice 3 manual | 가로 스크롤 발생 시 fail |
| R5 | component_map.md drift 충동 | 매 Slice §SELF-VERIFICATION | 1줄이라도 수정 시 즉시 revert |
| R6 | P-AGENT-SCOPE-001 재발 | 매 Slice git diff | 1건이라도 발견 시 fail |

---

## 관련 문서

- 진입 점검 보고서: `eval/qa_reports/phase-4-entry-check_2026-05-28.md`
- Phase 4 폴더: `phases/active/phase-4-fastapi-extension/`
- 강화된 Skill: phase-start v1.3.0 (P-X1) / qa-check v1.2.0 / phase-complete v1.1.0 / harness-audit v1.1.0
- Phase 3 인수 항목: `phases/archive/phase-3-pwa-impl/closing_notes.md`
- 회고 패턴: `meta/patterns.md` P-DRIFT-001 / P-SLICE-001 / P-GRACEFUL-001 / P-FOLDER-PARALLEL-001 / P-AGENT-SCOPE-001 (Mitigated) / P-X1-EFFECT-001 / P-THIN-VERTICAL-001 / P-DESIGN-LAYERED-001

---

## 종료

다음 작업:
1. PROJECT_STATE / PHASE_REGISTRY Phase 4 active 갱신
2. 진입 commit + push
3. **Wave 1 Slice 1 sub-agent dispatch** (Foundation contract endpoints)
4. 이후 Wave 2 (Slice 2 Thin Vertical) → Wave 3 (Slice 3 Frontend) → Wave 4 (Slice 4 Final)
5. **Slice 4 retrospective에서 다음 phase (A/B/C) 결정**
