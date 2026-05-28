# Phase 6 — Scope

## 포함 (In-Scope)

### Contracts (read + edit via contract-change Skill)

| 파일 | 작업 | 비고 |
|---|---|---|
| `docs/contracts/output_schema.md` | **수정** | Critic verdict canonical + revise_history + recommended_plan_index 정식 등록 |
| `docs/contracts/agent_io_contract.md` | **수정** | P-008 Rewriter agent schema 정식 등록 (semver만, prompt body 인라인 유지) |
| `docs/contracts/api_contract.md` | **수정** (Optional) | /plans/{plan_id}/generate 응답 구조 갱신 |

### Backend (backend/fastapi/)

| 파일 | 작업 |
|---|---|
| `agents/critic.py` | **수정** — CriticVerdict canonical 구조 (dimensions: dict[str, float] + overall_score: float) + select_best_plan_index fallback 축소 + deprecation note |
| `schemas/output.py` | **수정** — CriticEvaluation 모델 canonical 필드 명시 + revise_history typing 강화 (List[ReviseAttempt]) + ReviseAttempt 모델 신규 |
| `agents/rewriter.py` | **수정** (소폭) — RewriterInput / RewriterOutput Pydantic 모델 도입 (Phase 4.5 dict 반환 → Pydantic 모델) |
| `tests/test_critic.py` | **수정** — canonical 케이스 추가 + fallback deprecation warning 검증 |
| `tests/test_rewriter.py` | **수정** — Pydantic 모델 케이스 추가 |
| `tests/test_plans.py` | **수정 X** (회귀 검증만, baseline 유지) |
| `tests/test_schema_stress.py` | **신규** — best-plan tie / rewriter fail / revise max / dimension 부재 등 5~7 케이스 |

### Frontend (apps/web/)

| 파일 | 작업 |
|---|---|
| `lib/types.ts` | **수정** — CriticVerdict 모델 frontend mirror (dimensions: Record<string, number> + overall_score: number) + ReviseAttempt type + 모든 모델 backend schema 1:1 매핑 |
| `app/plan/[plan_id]/page.tsx` | **수정 X** (회귀 검증만) |
| `components/plan/PlanCard.tsx` | **수정 절대 금지** ★ — 10연속 0줄 |
| `component_map.md` | **수정 절대 금지** ★ — 20연속 0줄 |

### Meta / Scripts / Docs

| 파일 | 작업 |
|---|---|
| `meta/validations/2026-05-29_phase-6-pre-entry_self.md` | **신규** (M1, V1~V5) |
| `meta/validations/2026-05-29_phase-6-pre-entry_external.md` | **신규** (M2, placeholder) |
| `docs/decisions/phase_6_critic_canonical.md` | **신규** — ADR-018 |
| `docs/decisions/phase_6_rewriter_contract.md` | **신규** — ADR-019 |
| `scripts/schema_stress_test.ps1` | **신규** — pytest stress matrix + frontend tsc 정합 + import sanity |
| `scripts/smoke_test_phase_6.ps1` | **신규** — 10/10 (Phase 4.5 9 + schema stress 1) |
| `meta/retrospectives/phase-6.md` | **신규** |
| `meta/patterns.md` | **수정** (P-CRITIC-CANONICAL-001 신규 + P-X1-EFFECT-001 update 17연속) |
| `meta/skill_usage_log.md` | **수정** (contract-change +1 / multi-llm-validation formal +1) |
| `PROJECT_STATE.md` / `PHASE_REGISTRY.md` / `00_START_HERE.md` / `README.md` × 2 | **수정** |

## 예상 파일 변경 수

- **신규**: ~8 (2 validations + 2 ADR + 2 scripts + 회고 + tests/test_schema_stress)
- **수정**: ~10 (contracts × 2~3 + agents × 2 + schemas + types.ts + state docs × 5)
- **금지 (0줄)**: 2 (PlanCard.tsx, component_map.md)
- **예상 LOC**: ~+800 신규 / ~+200 수정 / ~−50 (fallback 축소)

## 제외 (Out-of-Scope) → `non_goals.md` 참조

Supabase / RLS / Auth / SSE / DB migration / PlanCard 수정 / prompt body / revise eval — 모두 Phase 5+ 이관.
