# Phase 5 — Multi-Slice Plan

> Slice 5개 모두 sub-agent dispatch
> 모두 sequential (DB → Auth → RLS+SSE → Close 의존 chain)
> 총 15~20h

---

## Wave 구조

```
Wave 1: Slice 1 [Pre-Entry — security-review + ADR-020 + scenario_sim v2 + validations]
  ↓
Wave 2: Slice 2 [Supabase 연결 + Schema migration + plans_repo]
  ↓
Wave 3: Slice 3 [Auth + JWT + Frontend Login + AuthGuard]
  ↓
Wave 4: Slice 4 [RLS 정책 + SSE Progress D7 + ADR-021/022]
  ↓
Wave 5: Slice 5 [Close + 회귀 검증 + 회고]
```

---

## Slice 1 — Pre-Entry + Security (2~3h)

### 작업 단위
1. `meta/validations/2026-05-29_phase-5-pre-entry_self.md` 신규 (V1~V6 — Supabase 채택 / Auth 정책 / RLS 정책 / SSE 정책 / revise_history JSONB / canonical DB 영속)
2. `meta/validations/2026-05-29_phase-5-pre-entry_external.md` 신규 (placeholder + Phase 6 외부 검증 결과 흡수 또는 Phase 5 자체)
3. **security-review Skill 첫 정식 트리거** → `meta/security_reviews/2026-05-29_phase-5-auth-rls.md` 작성:
   - JWT 검증 정책 (만료 / refresh / revocation)
   - RLS 정책 (anonymous endpoint 호환 / user_id 검증 / 우회 risk)
   - SSE 연결 보안 (CORS / origin 검증 / 토큰 유효성)
   - PII 마스킹 + 프롬프트 인젝션 차단 (Phase 1 baseline 유지)
4. `docs/decisions/phase_5_supabase_adoption.md` 신규 (ADR-020) — Supabase 채택 사유 + 대안 (PostgreSQL 자체 / Firebase / 자체 서버) + trade-off
5. `scripts/scenario_simulation.ps1` v2 — 5 시나리오 추가:
   - S6: Supabase 연결 (env var + client init)
   - S7: RLS 정책 변경 (db/migrations/*.sql)
   - S8: user 분리 (auth_user_id 컬럼)
   - S9: JWT 검증 (middleware)
   - S10: SSE event schema (routers/sse.py)
6. `meta/skill_usage_log.md` 갱신 (phase-start +1, multi-llm-validation +1 formal 세 번째, security-review 0→1 첫 정식, qa-check +1)
7. `PROJECT_STATE.md` active phase 갱신 (phase_5_*)
8. **entry commit**: "feat(phase-5): Slice 1 entry — security-review + ADR-020 + scenario_sim v2 + validations"

### 영향 파일 (~7 신규 + 3 수정)

### Sub-agent prompt 핵심
- editable: meta/validations/*, meta/security_reviews/* (신규 폴더), docs/decisions/ADR-020, scripts/scenario_simulation.ps1 (v2 — 단 기존 시나리오 5는 보존), meta/skill_usage_log.md, PROJECT_STATE.md, phases/active/phase-5-*/notes.md
- **forbidden**: backend/* (Slice 2/3 영역), apps/web/* (Slice 3 영역), docs/contracts/* (Slice 2), PlanCard ★, component_map ★, scripts/audit_*, schema_stress_test, smoke_test_phase_*, .claude/skills/*, archive/*, phases/active/phase-5-*/* (entry files 외)
- P-X1 의무

---

## Slice 2 — Supabase + Schema migration + plans_repo (4~5h)

### 작업 단위
1. `backend/fastapi/db/__init__.py` + `db/client.py` 신규 — Supabase client + 환경변수 + connection pool
2. `backend/fastapi/db/migrations/0001_init.sql` 신규 — 4계층 + plans + users
3. `backend/fastapi/db/migrations/0002_phase_4_5_revise_history.sql` 신규 — revise_history JSONB + recommended_plan_index INTEGER
4. **contract-change Skill 호출** — `docs/contracts/db_schema.md` 신규 (테이블 정의 + relations + JSONB schema + RLS 예고)
5. `backend/fastapi/db/repositories/plans_repo.py` 신규 — get / create / update / delete + graceful fallback (Supabase 실패 시 _plan_store dict 유지)
6. `backend/fastapi/config.py` 수정 — supabase_url / supabase_anon_key / supabase_service_key
7. `backend/fastapi/routers/plans.py` 수정 — _plan_store 직접 접근을 plans_repo 통해 (graceful fallback 유지)
8. `backend/fastapi/tests/test_db.py` 신규 — Supabase client mock + plans_repo CRUD 5+ 케이스
9. **commit**: "feat(phase-5): Slice 2 — Supabase 연결 + Schema migration + plans_repo"

### 영향 파일 (~8 신규 + 3 수정)

### Sub-agent prompt 핵심
- editable: backend/fastapi/db/*, config.py, routers/plans.py (호환만), tests/test_db.py, docs/contracts/db_schema.md
- **forbidden**: ★ PlanCard, component_map, backend/fastapi/agents/* (Phase 6 baseline), schemas/output.py (Phase 6 canonical), routers/auth.py + sse.py (Slice 3/4), tests/test_critic, test_rewriter, test_schema_stress, test_plans, test_3_plan (Phase 4.5/6 baseline), apps/web/* (Slice 3), docs/contracts/{output_schema, agent_io_contract}.md (Phase 6 baseline), docs/decisions/phase_4_5_*, phase_6_* (이전 ADR), scripts/* (Slice 1 + 5), .claude/skills/*, archive/*
- contract-change Skill 절차 (db_schema.md 신규 = 변경)
- P-X1 의무

---

## Slice 3 — Auth + JWT + Frontend Login (4~5h)

### 작업 단위
1. `backend/fastapi/routers/auth.py` 신규 — /auth/login (Supabase signInWithPassword) + /auth/me (current user) + /auth/logout
2. `backend/fastapi/middleware/auth_middleware.py` 신규 — JWT 검증 + request.state.user 주입
3. `backend/fastapi/config.py` 수정 (선택) — JWT settings
4. `backend/fastapi/tests/test_auth.py` 신규 — JWT mock 3+ 케이스
5. `apps/web/app/login/page.tsx` 신규 — Supabase Auth login form
6. `apps/web/components/AuthGuard.tsx` 신규 — wrapper, 미인증 → /login redirect
7. `apps/web/lib/auth.ts` 신규 — Supabase JS client + session 관리
8. `apps/web/lib/types.ts` 수정 — AuthSession + User types
9. `apps/web/app/plan/[plan_id]/page.tsx` 수정 — AuthGuard wrapping (PlanCard 무수정 유지, wrapper 정신 계승)
10. **commit**: "feat(phase-5): Slice 3 — Auth + JWT + Frontend Login + AuthGuard"

### 영향 파일 (~7 신규 + 3 수정)

### Sub-agent prompt 핵심
- editable: backend/fastapi/{routers/auth.py, middleware/, config.py (선택), tests/test_auth.py}, apps/web/{app/login/page.tsx, components/AuthGuard.tsx, lib/auth.ts, lib/types.ts, app/plan/[plan_id]/page.tsx (wrapper만)}
- **forbidden**: ★ PlanCard.tsx (절대 수정 X, AuthGuard는 wrapper)
- component_map.md, lib/api.ts, agents/*, schemas/*, routers/plans.py (Slice 2), routers/sse.py (Slice 4), db/* (Slice 2), tests/test_db (Slice 2), tests/test_critic / test_rewriter / test_schema_stress / test_plans / test_3_plan (baseline), docs/* (Slice 2/4 ADR), scripts/*, .claude/skills/*, archive/*
- P-X1 의무

---

## Slice 4 — RLS + SSE Progress D7 (3~4h)

### 작업 단위
1. `backend/fastapi/db/migrations/0003_rls_policy.sql` 신규 — RLS 정책 (plans + video_projects user_id = auth.uid())
2. `backend/fastapi/routers/sse.py` 신규 — /plans/{plan_id}/progress SSE endpoint (4단계 progress + 부분 결과)
3. `backend/fastapi/tests/test_rls.py` 신규 — 다른 user plan 접근 차단 3+ 케이스
4. `backend/fastapi/tests/test_sse.py` 신규 — SSE event schema + 4단계 3+ 케이스
5. `apps/web/lib/sse.ts` 신규 — EventSource wrapper
6. `apps/web/app/plan/[plan_id]/page.tsx` 수정 (소폭) — Progress UI 통합 (SSE listener, PlanCard 외부 wrapper)
7. `docs/decisions/phase_5_rls_policy.md` 신규 (ADR-021)
8. `docs/decisions/phase_5_sse_progress.md` 신규 (ADR-022)
9. **commit**: "feat(phase-5): Slice 4 — RLS 정책 + SSE Progress D7 + ADR-021/022"

### 영향 파일 (~7 신규 + 1 수정)

### Sub-agent prompt 핵심
- editable: backend/fastapi/{db/migrations/0003, routers/sse.py, tests/test_rls.py, tests/test_sse.py}, apps/web/{lib/sse.ts, app/plan/[plan_id]/page.tsx (Progress wrapper만)}, docs/decisions/ADR-021/022
- **forbidden**: ★ PlanCard, component_map, agents/*, schemas/*, routers/{plans.py, auth.py} (Slice 2/3), middleware (Slice 3), db/repositories (Slice 2), db/migrations/0001/0002 (Slice 2), config.py (Slice 2/3), lib/{auth.ts, types.ts, api.ts} (Slice 3), components/AuthGuard.tsx (Slice 3), app/login/page.tsx (Slice 3), tests/{test_critic, test_rewriter, test_schema_stress, test_plans, test_3_plan, test_db, test_auth} (baseline + Slice 2/3), docs/contracts/* (Slice 2), docs/decisions/{phase_4_5_*, phase_6_*, phase_5_supabase} (Slice 1/2 ADR), scripts/*, .claude/skills/*, archive/*
- P-X1 의무

---

## Slice 5 — Close + 회귀 검증 (2~3h)

### 작업 단위
1. `scripts/smoke_test_phase_5.ps1` 신규 (12 체크: Phase 6 10 + DB connect + RLS test)
2. `scripts/scenario_simulation.ps1` v2 final 실행 (10/10 PASS, P-X2 세 번째 자동 게이트)
3. audit_naming + audit_page_component final (0 drift)
4. **security-review Skill 두 번째 트리거** (final, 의도된 시행 + 결과 검증)
5. design-review impl §B (PASS 목표)
6. agent-io-check (회귀 검증)
7. `meta/retrospectives/phase-5.md` 신규 + patterns.md 갱신:
   - P-X1-EFFECT-001 update (22연속)
   - **P-RLS-001 신규** (RLS 정책 + auth.uid 패턴)
   - **P-SSE-001 신규** (SSE Progress + 4단계 + 부분 결과 패턴)
   - **P-SECURITY-REVIEW-001 신규 후보** (security-review Skill 첫 정식 효과)
8. phase-complete v1.2.0 (P-X2 자동 게이트 세 번째)
9. archive 이동
10. `closing_notes.md` 신규 (Phase 7 RAG 또는 Phase 8 MOA Lite 권장)
11. PROJECT_STATE / PHASE_REGISTRY / 00_START_HERE / README × 2 갱신
12. **final commit**: "feat(phase-5): Slice 5 — Phase 5 close + P-X1 22연속 + security-review 두 번째"

### 영향 파일 (~6 신규 + 6 수정 + archive)

### Sub-agent prompt 핵심
- editable: scripts/smoke_test_phase_5.ps1, meta/retrospectives/phase-5.md, meta/patterns.md, meta/skill_usage_log.md, phases/archive/phase-5-* (이동), closing_notes.md, PROJECT_STATE, PHASE_REGISTRY, 00_START_HERE, README × 2
- **forbidden**: 거의 모든 코드 (Slice 2/3/4 산출물 보존) + PlanCard ★ + component_map ★ + agents/* + schemas/* + 모든 tests + 모든 contracts + 모든 prior ADRs + scripts/audit_* + scenario_simulation (v2는 Slice 1 영역) + smoke_test_phase_4_5/6 + .claude/skills/*
- P-X1 의무

---

## 충돌 매트릭스 (Slice × 영향 영역)

| Slice | meta | db | routers | middleware | agents | schemas | tests | apps/web | contracts | decisions | scripts | state docs |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | ✅ V+SR+log+state | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ ADR-020 | ✅ scenario_sim v2 | ✅ entry |
| 2 | ❌ | ✅ client+migrations+repo | ✅ plans.py | ❌ | ❌ | ❌ | ✅ test_db | ❌ | ✅ db_schema 신규 | ❌ | ❌ | ❌ |
| 3 | ❌ | ❌ | ✅ auth.py | ✅ auth_middleware | ❌ | ❌ | ✅ test_auth | ✅ login + AuthGuard + auth.ts + types.ts + page.tsx wrapper | ❌ | ❌ | ❌ | ❌ |
| 4 | ❌ | ✅ migrations/0003 | ✅ sse.py | ❌ | ❌ | ❌ | ✅ test_rls + test_sse | ✅ sse.ts + page.tsx Progress | ❌ | ✅ ADR-021/022 | ❌ | ❌ |
| 5 | ✅ retrospective + patterns + log | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ smoke_test_phase_5 | ✅ all |

Sequential 진행 시 충돌 0. (각 Slice의 backend/apps/web 수정은 다른 Slice 영역과 겹치지 않음.)

---

## 누적 P-X1 streak 목표

| Phase | streak |
|---|---|
| Phase 3 | 5 |
| Phase 4 | 4 |
| Phase 4.5 | 4 |
| Phase 6 | 4 |
| Phase 5 | **5 (목표)** |
| **누적** | **22** |

---

## 시간 추정

| Slice | 시간 | 누적 |
|---|---|---|
| 1 | 2~3h | 2~3h |
| 2 | 4~5h | 6~8h |
| 3 | 4~5h | 10~13h |
| 4 | 3~4h | 13~17h |
| 5 | 2~3h | **15~20h** |
