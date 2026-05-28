# Phase 4 — Multi-Slice Execution Plan (4 Waves, all sequential)

> 작성: 2026-05-28 (Phase 4 진입)
> 방식: sub-agent 분산 (context 관리). 모두 sequential (사용자 결정 2-a).

---

## 1. 의존성 그래프

```
Slice 1 (Foundation) → Slice 2 (Thin Vertical 3-plan) → Slice 3 (Frontend) → Slice 4 (Final)
```

전부 직선 — 병렬 미채택 사유:
- Phase 4 scope 작음 (7~11h, Phase 3의 50%)
- backend (Slice 2) → frontend (Slice 3) 의존
- P-AGENT-SCOPE-001 재발 방지 (Phase 3 5연속 PASS 유지)

---

## 2. Wave 분할 (4 sequential)

### Wave 1
- **A: Slice 1** — Foundation contract endpoints

### Wave 2
- **B: Slice 2** — Thin Vertical 3-plan (multi-model 가능)

### Wave 3
- **C: Slice 3** — Frontend 3-plan minimal

### Wave 4
- **D: Slice 4** — Final + Archive + 다음 phase 옵션 명시

총 sub-agent dispatch: **4** (Phase 1/2/3 6 dispatch 대비 ▼33%).

---

## 3. 충돌 분석 매트릭스

| Wave | Slice | 변경 영역 | 충돌 위험 |
|---|---|---|---|
| 1 | 1 | backend/fastapi/{routers/plans, schemas/plans, routers/generate(header), main, tests/test_plans} + ADR-014 | — |
| 2 | 2 | backend/fastapi/{agents/planning, schemas/output, routers/plans, config, tests/test_3_plan} + ADR-015 | — (Slice 1 baseline 사용) |
| 3 | 3 | apps/web/{app/plan/[plan_id], app/plan/page (선택), lib/api, lib/types} | — (Slice 2 응답 구조 사용) |
| 4 | 4 | scripts/smoke + eval/qa_reports + meta/{retrospective, proposals, patterns, skill_usage} + archive + 상태 파일 | 단일 |

→ Sequential이라 race 0.

---

## 4. Sub-Agent 공통 절차 (4-Phase)

각 sub-agent:

```
Phase A. 컨텍스트 로딩 (Surgical Scope — 필요한 것만)
Phase B. 파일 생성 / 수정
Phase C. 정적 검증:
  - audit_naming 0 drift
  - pytest 62 + 신규 (회귀 0)
  - next build / tsc / lint (Slice 3+)
  - audit_page_component (Slice 3+)
Phase D. 하네스 기록 + §SELF-VERIFICATION (P-X1) + commit + push
```

---

## 5. §SELF-VERIFICATION (P-X1) 의무 절차 (모든 sub-agent)

```bash
# 작업 완료 직전
git status
git diff --stat HEAD
```

**필수 확인**:
- editable 외 forbidden 0건
- **`component_map.md` 0줄 수정** ★ (11+ 연속 보존 — 조정 4번)
- **`apps/web/components/PlanCard.tsx` 0줄 수정** ★ (사용자 결정 6-a)
- Phase 2 spec (page_map / design_handoff / design_system / *flow / wireframes / direction_approval / design.md) 0줄
- Phase 3 baseline (apps/web/app/new/*, components/discovery/*, common/*, quick/*, lib/* Phase 3 산출물) 0줄
- Phase 1 endpoint `/api/v1/generate` 실 동작 영향 0 (header만 추가 OK)

**판정**:
- 모두 PASS → 정상 commit
- 1건이라도 fail → 즉시 revert 후 재시도 또는 deviations.md 기록

---

## 6. main session 후속 검증 (Wave 종료 시 의무)

```bash
git log -1 --stat
git diff HEAD~1 HEAD --stat -- \
  harness/apps/web/component_map.md \
  harness/apps/web/components/PlanCard.tsx \
  harness/apps/web/page_map.md \
  harness/apps/web/design_handoff.md \
  harness/apps/web/design_system/ \
  harness/apps/web/discovery_flow.md \
  harness/apps/web/quick_flow.md \
  harness/apps/web/mode_branching.md \
  harness/apps/web/direction_approval.md \
  harness/apps/web/design.md \
  harness/apps/web/wireframes/
```

→ 모두 empty (0줄) 확인 후 Wave 종료 / 다음 Wave 진입.

---

## 7. 진행 트래킹

```yaml
phase_4_multi_slice_progress:
  wave_1:
    status: pending
    sub_agents: [A_slice_1]
    estimated_hours: 2-3
  wave_2:
    status: pending
    sub_agents: [B_slice_2]
    estimated_hours: 2-3
  wave_3:
    status: pending
    sub_agents: [C_slice_3]
    estimated_hours: 2-3
  wave_4:
    status: pending
    sub_agents: [D_slice_4]
    estimated_hours: 1-2

  p_x1_streak_target: 4  # Slice 1~4 모두 PASS
  component_map_zero_lines_target: 4  # 11+ 연속 보존
  plan_card_zero_lines_target: 4  # PlanCard 무수정 (사용자 결정 6-a)
```

각 Wave 완료 시 갱신.

---

## 8. 종료 조건 (Phase 4 완료)

- Slice 1~4 commit + push
- A1~A10 모두 PASS
- audit_naming + audit_page_component 0 drift
- pytest 회귀 0 + next build 0 errors
- §SELF-VERIFICATION 4/4 PASS
- component_map.md 11+ 연속 0줄
- PlanCard.tsx 0줄 수정 (Phase 4 전체)
- 변경성 시뮬 5/5 회귀
- **다음 phase 옵션 (A/B/C) closing_notes + retrospective 명시**
- archive 이동

---

## 9. 다음 phase 결정 (사용자 결정 3-c)

Slice 4 sub-agent가 retrospective + closing_notes에 다음 3 옵션 제시:

```
옵션 A: Phase 4.5 mini-phase
  - Critic revise loop + Rewriter (P-008)
  - 추정: 8~12h
  - 효과: failure_cases FC revise → approve 검증

옵션 B: Phase 5 DB/Auth (Critic revise는 Phase 6+ 통합)
  - Supabase Auth + RLS
  - SSE Progress (D7) 동시 처리 가능
  - 추정: 15~20h

옵션 C: 다른 우선순위
  - 사용자 시점에서 재평가
```

→ 사용자가 Slice 4 종료 직후 결정.

---

## 10. 변경 이력

- 2026-05-28: 최초 작성 (Phase 4 진입, GPT 검토 채택)
