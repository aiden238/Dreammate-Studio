# Phase 4.5 — Scope

> 작업 범위. 이 문서는 Slice 분할의 기준이며, scope 밖 작업은 자동 거부.

## 포함 (In-Scope)

### 백엔드 (backend/fastapi/)

| 파일 | 작업 유형 | 비고 |
|---|---|---|
| `agents/rewriter.py` | **신규** | P-008 Rewriter agent, 인라인 prompt (Phase 6+ prompt_registry 정식화 전) |
| `agents/critic.py` | **수정** | (선택) `select_best_plan_index()` 추가 — Z-X3 |
| `routers/plans.py` | **수정** | `/plans/{plan_id}/generate`에 revise loop + best-plan 통합 |
| `schemas/output.py` | **수정** | `revise_history: list[dict]`, `recommended_plan_index: Optional[int]` 추가 |
| `config.py` | **수정** | (선택) `critic_max_revise: int = 2` 환경 변수화 |
| `tests/test_rewriter.py` | **신규** | revise 0/1/2회 + 실패 + best-plan 0/1/2 + tie-break |
| `tests/test_plans.py` | **수정** | `/plans/{plan_id}/generate` revise loop 통합 케이스 |

### 프론트엔드 (apps/web/)

| 파일 | 작업 유형 | 비고 |
|---|---|---|
| `app/plan/[plan_id]/page.tsx` | **수정** | wrapper UI 추가 — `recommended_plan_index === idx`일 때 `<div class="ring-2 ring-emerald-500">` |
| `lib/types.ts` | **수정** | `MultiPlanEnvelope.recommended_plan_index?: number`, `Body.revise_history?: list` |
| `lib/api.ts` | **수정 X** | 기존 `generateMultiPlan()` 응답 구조 그대로 활용 |
| `components/plan/PlanCard.tsx` | **수정 절대 금지** | **5연속 0줄 유지** (사용자 결정 6-a 계승) |
| `apps/web/component_map.md` | **수정 절대 금지** | **16연속 0줄 유지** |

### 메타 / 도구 (meta + scripts + .claude/skills/)

| 파일 | 작업 유형 | 비고 |
|---|---|---|
| `meta/validations/2026-05-28_phase-4.5-pre-entry_self.md` | **신규** | M1 self-validation (Claude Code) |
| `meta/validations/2026-05-28_phase-4.5-pre-entry_external.md` | **신규** | M2 외부 검증 placeholder |
| `.claude/skills/phase-complete/SKILL.md` | **수정** | v1.1.0 → v1.2.0 §1.6 변경성 시뮬 자동 게이트 (P-X2) |
| `scripts/scenario_simulation.ps1` | **신규** | 변경성 시뮬 시나리오 1~5 자동 walkthrough |
| `scripts/smoke_test_phase_4_5.ps1` | **신규** | 9/9 (Phase 4 8/8 + revise 1개) |
| `docs/decisions/phase_4_5_critic_revise.md` | **신규** | ADR-016 — Critic revise loop 결정 |
| `docs/decisions/phase_4_5_best_plan_selection.md` | **신규** | ADR-017 — Z-X3 best-plan logic 결정 |

### 회고 / 상태

| 파일 | 작업 유형 |
|---|---|
| `meta/retrospectives/phase-4.5.md` | **신규** |
| `meta/patterns.md` | **수정** (P-X1-EFFECT-001 update 13연속 + P-X2-EFFECT-001 신규) |
| `meta/skill_usage_log.md` | **수정** (multi-llm-validation formal 1 + phase-complete v1.2.0) |
| `PROJECT_STATE.md` | **수정** (phase_4_5_* 필드 + next_phase_status) |
| `PHASE_REGISTRY.md` | **수정** (Phase 4.5 row 추가) |
| `00_START_HERE.md` | **수정** |
| `README.md` (root + harness) | **수정** |

## 예상 파일 변경 수

- **신규**: ~12 (rewriter.py + tests + 2 validations + scenario_sim + smoke_test + 2 ADR + 회고 + 2 frontend types/wrapper 일부)
- **수정**: ~10 (routers/plans.py + schemas/output.py + frontend page.tsx + types.ts + SKILL.md + patterns + skill_usage + 4 state docs)
- **금지 (0줄 유지)**: 2 (PlanCard.tsx + component_map.md)
- **예상 LOC**: ~+600 신규 / ~+150 수정 (backend ~+450 / frontend ~+50 / docs ~+250)

## 제외 (Out-of-Scope) → `non_goals.md` 참조

DB 영속화 / Supabase Auth / RLS / SSE / PlanCard 4-layer 정합 / prompt_registry 정식화 / revise 효과 eval / multi-provider client factory (Z-X2 Phase 21+).
