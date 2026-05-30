# Phase 9 — Scope

## 포함 (In-Scope)

### Backend — DB / Repo (신규)

| 파일 | 작업 |
|---|---|
| `backend/fastapi/db/migrations/0005_feedback_selection.sql` | **신규** — selected_plans + feedback_events + discovery_choices + brand_memory_entries (실 `plans` 테이블 정합: option_index 0–2, plan_candidates JSONB 참조) + RLS (Phase 5 패턴) |
| `backend/fastapi/db/repositories/selection_repo.py` | **신규** — SelectionRepo (graceful, PlansRepo 패턴) — select/get |
| `backend/fastapi/db/repositories/feedback_repo.py` | **신규** — FeedbackRepo (graceful) — record/list |
| `backend/fastapi/db/__init__.py` | **수정** — SelectionRepo / FeedbackRepo export |

### Backend — Router / Orchestrator

| 파일 | 작업 |
|---|---|
| `backend/fastapi/routers/plans.py` | **수정** — POST /plans/{id}/select + POST /plans/{id}/feedback + GET /plans/{id}/feedback (thin adapter, repo 호출) |
| `backend/fastapi/orchestration/moa_orchestrator.py` | **수정** — critic step에 `normalize_to_canonical` wiring (verdict → canonical 0–1, deprecated 0–5 병행) |
| `backend/fastapi/schemas/plans.py` | **수정** — SelectRequest / FeedbackRequest / SelectionResponse / FeedbackResponse Pydantic |

### Backend — Brand Memory 준비 (agent 미구현)

| 파일 | 작업 |
|---|---|
| `backend/fastapi/db/repositories/brand_memory_repo.py` | **신규** — BrandMemoryRepo (graceful) — entry CRUD (수동/준비용, 자동 추출 X) |
| `backend/fastapi/rag/feedback_to_candidate.py` | **신규 (선택)** — feedback → candidate_knowledge(source_kind='user_feedback') 적재 경로 준비 (Phase 7 candidate 연결) |

### Frontend (wrapper — PlanCard·component_map 무수정 ★)

| 파일 | 작업 |
|---|---|
| `apps/web/app/plan/[plan_id]/page.tsx` | **수정** — 선택 버튼 + 반려 이유 입력 UI inline wrapper (PlanCard 외부) |
| `apps/web/lib/api.ts` | **수정** — selectPlan / sendFeedback fetch (credentials include) |
| `apps/web/lib/types.ts` | **수정** — SelectRequest/Response + FeedbackRequest/Response type |
| `apps/web/components/plan/PlanCard.tsx` | **수정 절대 금지** ★ |
| `apps/web/component_map.md` | **수정 절대 금지** ★ (신규 component 등록 X — page.tsx inline) |

### Tests

| 파일 | 작업 |
|---|---|
| `tests/test_selection_feedback.py` | **신규** — selection_repo + feedback_repo graceful CRUD |
| `tests/test_plans_feedback_api.py` | **신규** — select/feedback endpoint |
| `tests/test_critic_canonical_wiring.py` | **신규** — normalize wiring (critic_evaluation canonical 0–1 저장) |
| `tests/test_brand_memory_prep.py` | **신규** — brand_memory_repo + feedback→candidate 적재 경로 |
| 모든 baseline tests | **수정 X** (normalize wiring은 의도된 critic_evaluation delta만 — Phase 8 Slice 4 패턴) |

### Contracts / ADRs / Meta / Scripts

| 파일 | 작업 |
|---|---|
| `docs/contracts/db_schema.md` | **수정** (contract-change) — feedback/selection 실 plans 테이블 정합 + brand_memory prep |
| `docs/decisions/phase_9_feedback_selection.md` | **신규** — ADR-030 |
| `docs/decisions/phase_9_brand_memory_prep.md` | **신규** — ADR-031 (P-AUX-2 설계, 활성화 Phase 10+) |
| `docs/decisions/phase_9_critic_canonical_wiring.md` | **신규** — ADR-032 (normalize wiring) |
| `meta/validations/2026-05-29_phase-9-pre-entry_self.md` + external | **신규** |
| `meta/security_reviews/2026-05-29_phase-9-feedback-pii.md` | **신규** (M2 — 두 번째 정식) |
| `scripts/smoke_test_phase_9.ps1` | **신규** — 15 체크 |
| `scripts/scenario_simulation.ps1` | **수정** — v5 (S21~S25 추가) |
| `meta/retrospectives/phase-9.md` / `patterns.md` / `skill_usage_log.md` | **수정/신규** |
| `PROJECT_STATE / PHASE_REGISTRY / 00_START_HERE / README` | **수정** |

## 예상 파일 변경 수
- **신규**: ~18 (migration + repo 3 + feedback_to_candidate + tests 4 + ADR 3 + validations 2 + security_review + smoke + retrospective)
- **수정**: ~12 (plans.py + orchestrator + schemas/plans + db __init__ + frontend 3 + db_schema + scenario_sim + patterns + skill_usage + state docs)
- **금지 (0줄)**: 2 (PlanCard.tsx, component_map.md)

## 제외 → `non_goals.md`
