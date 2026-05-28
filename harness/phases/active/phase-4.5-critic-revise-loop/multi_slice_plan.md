# Phase 4.5 — Multi-Slice Plan

> Slice 4개 모두 sub-agent dispatch (사용자 결정)
> Wave 4개 (모두 sequential — mini-phase scope)

---

## Wave 구조

```
Wave 1 (sub-agent A): Slice 1 [Pre-Entry — validations + P-X2 + entry commit]
  ↓ (main verify)
Wave 2 (sub-agent B): Slice 2 [Rewriter agent + Revise Loop]
  ↓ (main verify)
Wave 3 (sub-agent C): Slice 3 [Best-Plan Selection + Frontend wrapper]
  ↓ (main verify)
Wave 4 (sub-agent D): Slice 4 [Close — qa-check final + design-review + 회고 + state docs]
```

병렬화 불가:
- Slice 2 결과(revise_history 구조)에 Slice 3 의존
- Slice 1 산출물(scenario_simulation.ps1)을 Slice 4가 사용
- Slice 4 회고는 Slice 1~3 결과 누적 후 가능

---

## Slice 1 — Pre-Entry (Wave 1, sub-agent A)

### 작업 단위
1. `meta/validations/2026-05-28_phase-4.5-pre-entry_self.md` 작성 (Claude Code 자가 검증, 지침 참조)
2. `meta/validations/2026-05-28_phase-4.5-pre-entry_external.md` 작성 (외부 검증 placeholder 형식)
3. P-X2 채택:
   - `.claude/skills/phase-complete/SKILL.md` v1.1.0 → v1.2.0 (§1.6 추가)
   - `scripts/scenario_simulation.ps1` 신규 작성
4. `meta/skill_usage_log.md` 갱신 (multi-llm-validation formal 1 추가)
5. **acceptance entry commit**: "feat(phase-4.5): Slice 1 entry — validations self + P-X2 채택 + scenario_simulation.ps1"

### 영향 파일 (4 신규 + 2 수정)
- 신규: 2 validations + scenario_simulation.ps1 + (선택 추가 entry 산출물)
- 수정: phase-complete SKILL.md + skill_usage_log.md

### 시간: 3~4h

### Sub-agent prompt 핵심
- editable: 위 6 파일 + entry 디렉토리 산출물
- **forbidden**: PlanCard.tsx, component_map.md, agents/*, routers/*, schemas/*, page.tsx, types.ts (Slice 2/3 영역)
- P-X1 §SELF-VERIFICATION 의무

---

## Slice 2 — Rewriter + Revise Loop (Wave 2, sub-agent B)

### 작업 단위
1. `backend/fastapi/agents/rewriter.py` 신규
   - `async def run_rewriter(plan, critic_verdict, *, model, client) -> dict`
   - 인라인 prompt + retry 0 (graceful: 실패 시 원본 plan 반환 + warning)
2. `backend/fastapi/routers/plans.py` 수정 — `/plans/{plan_id}/generate`에 revise loop 통합:
   ```python
   revise_history = []
   for attempt in range(critic_max_revise):  # 기본 2
       verdict = await run_critic(plan, ...)
       revise_history.append({"verdict": verdict, "revision_count": attempt})
       if verdict["action"] != "revise":
           break
       plan = await run_rewriter(plan, verdict, ...)
   ```
3. `backend/fastapi/schemas/output.py` 수정 — `Body.revise_history: Optional[list[dict]] = None`
4. `backend/fastapi/config.py` 수정 — `critic_max_revise: int = 2` (env override)
5. `backend/tests/test_rewriter.py` 신규 (5~7 케이스: 기본 revise / 실패 graceful / approve 즉시 / 2회 revise / loop max 차단)
6. `backend/tests/test_plans.py` 수정 (revise loop 통합 케이스 2~3 추가)
7. `docs/decisions/phase_4_5_critic_revise.md` 신규 — ADR-016
8. **acceptance commit**: "feat(phase-4.5): Slice 2 — Rewriter agent + Critic revise loop (max 2)"

### 영향 파일 (4 신규 + 4 수정)

### 시간: 5~6h

### Sub-agent prompt 핵심
- editable: 위 8 파일
- **forbidden**: PlanCard.tsx, component_map.md, page.tsx (Slice 3 영역), 모든 frontend 코드 (단 types.ts 수정 X — Slice 3 통합)
- 의존: Slice 1 산출물 (scenario_simulation.ps1 사용 X — Slice 4에서 사용)
- P-X1 §SELF-VERIFICATION 의무

---

## Slice 3 — Best-Plan + Frontend Wrapper (Wave 3, sub-agent C)

### 작업 단위
1. `backend/fastapi/agents/critic.py` 수정 — `def select_best_plan_index(verdicts: list[dict]) -> int`
   - 8-dim 평균 점수 + tie-breaking은 plan_index 작은 쪽
2. `backend/fastapi/routers/plans.py` 수정 — best-plan 통합:
   ```python
   recommended_idx = select_best_plan_index([v for p, v in plan_verdicts])
   body["recommended_plan_index"] = recommended_idx
   ```
3. `backend/fastapi/schemas/output.py` 수정 — `Body.recommended_plan_index: Optional[int] = None`
4. `backend/tests/test_critic.py` 수정 (3~4 케이스: idx 0 / 1 / 2 / tie-break)
5. `apps/web/lib/types.ts` 수정 — `MultiPlanEnvelope.recommended_plan_index?: number`, `Body.revise_history?: ReviseEntry[]`
6. `apps/web/app/plan/[plan_id]/page.tsx` 수정 — wrapper UI:
   ```tsx
   <div className={recommendedIdx === idx ? "ring-2 ring-emerald-500 rounded-lg" : ""}>
     <PlanCard plan={plan} />
   </div>
   ```
7. `docs/decisions/phase_4_5_best_plan_selection.md` 신규 — ADR-017
8. **acceptance commit**: "feat(phase-4.5): Slice 3 — best-plan selection + frontend wrapper highlight"

### 영향 파일 (2 신규 + 5 수정)

### 시간: 3~4h

### Sub-agent prompt 핵심
- editable: 위 7 파일
- **forbidden**: PlanCard.tsx ★ (절대 — 5연속 0줄 baseline), component_map.md ★, agents/rewriter.py (Slice 2 영역)
- 의존: Slice 2 결과 (revise_history 구조, critic verdict 구조)
- P-X1 §SELF-VERIFICATION 의무 + **PlanCard.tsx 사후 git diff --stat 0줄 명시 확인**

---

## Slice 4 — Close (Wave 4, sub-agent D)

### 작업 단위
1. `qa-check` v1.2.0 final 호출 (11 카테고리, 7 PASS / 4 skip 목표)
2. `scripts/audit_naming.ps1` + `scripts/audit_page_component.ps1` final 호출 (0 drift)
3. `scripts/scenario_simulation.ps1` final 호출 — **P-X2 첫 자동 게이트 트리거**
4. `scripts/smoke_test_phase_4_5.ps1` 신규 + 실행 (9/9 PASS)
5. `design-review` Skill 호출 — impl §B (PlanCard 무수정 정합 검증)
6. `meta-retrospective` Skill 호출 → `meta/retrospectives/phase-4.5.md` 작성
7. `meta/patterns.md` 갱신 (P-X1-EFFECT-001 update 13연속 + P-X2-EFFECT-001 신규)
8. `phase-complete` Skill v1.2.0 호출 (P-X2 자동 게이트 동작 검증)
9. archive 이동: `phases/active/phase-4.5-*` → `phases/archive/phase-4.5-critic-revise-loop/`
10. state docs 갱신: PROJECT_STATE / PHASE_REGISTRY / 00_START_HERE / README × 2
11. **closing_notes.md** 작성 (다음 phase 옵션 명시)
12. **acceptance final commit**: "feat(phase-4.5): Slice 4 — Phase 4.5 close (smoke 9/9 + P-X2 자동 게이트 첫 작동)"

### 영향 파일 (3 신규 + 7 수정 + archive 이동)

### 시간: 1~2h

### Sub-agent prompt 핵심
- editable: 회고 + patterns + state docs + smoke_test_phase_4_5.ps1 + closing_notes
- **forbidden**: 코드 (agents/*, routers/*, schemas/*, components/*, page.tsx) — 모두 Slice 1~3 완료 후 수정 0
- 의존: Slice 1~3 완료
- P-X1 §SELF-VERIFICATION 의무

---

## 충돌 분석 매트릭스 (Slice × 영향 영역)

| Slice | backend/agents | backend/routers | backend/schemas | backend/tests | frontend/page | frontend/types | meta/* | scripts | docs/decisions | state docs |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ validations + skill_usage | ✅ scenario_sim | ❌ | ❌ |
| 2 | ✅ rewriter + critic | ✅ revise loop | ✅ revise_history | ✅ rewriter + plans | ❌ | ❌ | ❌ | ❌ | ✅ ADR-016 | ❌ |
| 3 | ✅ critic (best-plan) | ✅ best-plan 통합 | ✅ recommended_plan_index | ✅ critic | ✅ wrapper | ✅ Optional 필드 | ❌ | ❌ | ✅ ADR-017 | ❌ |
| 4 | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ retrospective + patterns | ✅ smoke_test_phase_4_5 | ❌ | ✅ PROJECT_STATE etc |

**Slice 2 vs Slice 3 backend 중첩** (critic.py + routers/plans.py + schemas/output.py):
- Slice 2: revise loop integration → critic.py read-only (verdict 구조 그대로 사용)
- Slice 3: critic.py에 select_best_plan_index() **함수 추가** (Slice 2의 revise 결과 verdict list를 입력)
- Slice 2 commit 후 Slice 3 진입 → **sequential 보장 시 충돌 0**

**routers/plans.py 2회 수정 (Slice 2 + Slice 3)**: 별도 함수 block 추가 방식 → merge conflict 0.

---

## 누적 P-X1 streak 목표

| Phase | Slice 수 | P-X1 PASS |
|---|---|---|
| Phase 3 | 5 (Slice 1~5, Slice 6 main) | 5 |
| Phase 4 | 4 (Slice 1~3 sub, Slice 4 main) | 4 |
| Phase 4.5 | 4 (Slice 1~4 모두 sub) | **4** |
| **누적** | — | **13** |

13연속 PASS → P-AGENT-SCOPE-001 mitigation 누적 입증 강화.

---

## 시간 추정 요약

| Slice | 시간 | 누적 |
|---|---|---|
| 1 | 3~4h | 3~4h |
| 2 | 5~6h | 8~10h |
| 3 | 3~4h | 11~14h |
| 4 | 1~2h | **12~16h** |

원안 8~12h + Z-X3(+2~3h) + P-X2(+1~2h) + validations(+1h) = 12~18h → 압축 12~16h.
