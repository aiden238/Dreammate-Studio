# Phase 5 — Scope

## 포함 (In-Scope)

### Contracts (read + edit via contract-change Skill)

| 파일 | 작업 |
|---|---|
| `docs/contracts/db_schema.md` | **신규** — 4계층 + plans + users 테이블 정의 |
| `docs/contracts/api_contract.md` | **수정** — /auth/login + /auth/me + SSE /plans/{plan_id}/progress 엔드포인트 |
| `docs/contracts/llm_security_contract.md` | **수정** (선택) — JWT + RLS 정책 명시 |
| `docs/contracts/rate_limit_policy.md` | **수정** (선택) — 사용자별 quota |

### Backend (backend/fastapi/)

| 파일 | 작업 |
|---|---|
| `db/__init__.py` + `db/client.py` | **신규** — Supabase client + connection pool |
| `db/migrations/0001_init.sql` | **신규** — brands, domains, series, video_projects, users 4계층 + plans |
| `db/migrations/0002_phase_4_5_revise_history.sql` | **신규** — revise_history + recommended_plan_index 컬럼 |
| `db/repositories/plans_repo.py` | **신규** — _plan_store dict → DB 영속화 (CRUD) |
| `routers/auth.py` | **신규** — /auth/login + /auth/me + /auth/logout |
| `routers/plans.py` | **수정** — _plan_store → plans_repo 호환 (graceful fallback 유지) |
| `routers/sse.py` | **신규** — SSE Progress /plans/{plan_id}/progress |
| `middleware/auth_middleware.py` | **신규** — JWT 검증 |
| `config.py` | **수정** — Supabase URL/Anon Key + SSE 활성 플래그 |
| `tests/test_db.py` | **신규** — Supabase client 연결 (mock) + plans_repo CRUD |
| `tests/test_auth.py` | **신규** — JWT 검증 + /auth/login 통합 |
| `tests/test_rls.py` | **신규** — 다른 user plan 접근 차단 |
| `tests/test_sse.py` | **신규** — SSE event schema + 4단계 progress |

### Frontend (apps/web/)

| 파일 | 작업 |
|---|---|
| `app/login/page.tsx` | **신규** — Supabase Auth login page |
| `components/AuthGuard.tsx` | **신규** — 인증 wrapper |
| `lib/auth.ts` | **신규** — Supabase JS client + session 관리 |
| `lib/sse.ts` | **신규** — SSE listener |
| `app/plan/[plan_id]/page.tsx` | **수정** — Progress UI 통합 (SSE) + AuthGuard |
| `lib/types.ts` | **수정** — SSEProgressEvent + AuthSession types |
| `components/plan/PlanCard.tsx` | **수정 절대 금지** ★ — 13연속 0줄 |
| `component_map.md` | **수정 절대 금지** ★ — 23연속 0줄 |

### Meta / Scripts / Docs

| 파일 | 작업 |
|---|---|
| `meta/validations/2026-05-29_phase-5-pre-entry_self.md` | **신규** (M1) |
| `meta/validations/2026-05-29_phase-5-pre-entry_external.md` | **신규** (M1) |
| `meta/security_reviews/2026-05-29_phase-5-auth-rls.md` | **신규** (M2, security-review Skill 결과) |
| `scripts/scenario_simulation.ps1` | **수정** — v2 (DB/Auth용 5 시나리오) |
| `scripts/smoke_test_phase_5.ps1` | **신규** — 12 체크 (Phase 6 10 + DB + RLS) |
| `docs/decisions/phase_5_supabase_adoption.md` | **신규** — ADR-020 |
| `docs/decisions/phase_5_rls_policy.md` | **신규** — ADR-021 |
| `docs/decisions/phase_5_sse_progress.md` | **신규** — ADR-022 |
| `meta/retrospectives/phase-5.md` | **신규** |
| `meta/patterns.md` | **수정** — P-RLS-001 + P-SSE-001 신규 + P-X1-EFFECT-001 update (22연속) |
| `meta/skill_usage_log.md` | **수정** — security-review 첫 정식 + contract-change 본격 두 번째 |
| `PROJECT_STATE.md` / `PHASE_REGISTRY.md` / `00_START_HERE.md` / `README.md` × 2 | **수정** |

## 예상 파일 변경 수

- **신규**: ~28 (backend DB layer + auth + SSE + tests + frontend auth + ADR × 3 + meta + scripts)
- **수정**: ~10 (state docs + contract 일부 + routers/plans + page.tsx + types.ts)
- **금지 (0줄)**: 2 (PlanCard.tsx, component_map.md)
- **예상 LOC**: ~+2500 신규 / ~+400 수정 (backend ~+1500 + frontend ~+600 + docs ~+400)

## 제외 (Out-of-Scope) → `non_goals.md` 참조

Brand Memory / RAG 본격화 / 결제 / 팀 / multi-provider / Phase 1 endpoint 제거 / PlanCard 4-layer / prompt_registry — Phase 7+ 이관.
