# Retrospective: Phase 5 — DB / Auth / RLS / SSE

> 작성일: 2026-05-29
> 종류: large phase (15~20h, 5 Slice — MVP 본격 영속화)
> 범위: Phase 5 전체 (Slice 1 entry → Slice 2~4 구현 → Slice 5 close)
> 작성자: Claude (Opus 4.7)
> 트리거: phase-complete v1.2.0 §1.6 자동 게이트 세 번째 + §7 회고 자동 호출

---

## 사실 요약

Phase 5 (DB / Auth / RLS / SSE — MVP 본격 영속화)를 **2026-05-29 단일 일자**에 entry부터 archive까지 완수.

진입: phase-start v1.3.0 4점검 PASS + 사용자 결정 "Phase 6 → Phase 5 순차" 계승. entry commit `badb2c0`.

5 Slices를 5 Waves로 분해 (모두 sequential + 모두 sub-agent dispatch):
- Wave 1 (Slice 1, `badb2c0`) — Pre-Entry + Security: validations self V1~V6 + external placeholder + **security-review Skill ★ 첫 정식 트리거** (T1~T6 위협 모델) + ADR-020 Supabase 채택 + scenario_simulation v2 (5→10 시나리오)
- Wave 2 (Slice 2, `d668c9d`) — Supabase + Schema migration + plans_repo: `db/client.py` + `db/migrations/0001_init.sql` + `0002_phase_4_5_revise_history.sql` + `db/repositories/plans_repo.py` (graceful fallback) + **contract-change Skill 두 번째 본격** (`db_schema.md` 신규) + test_db.py 9 cases
- Wave 3 (Slice 3, `3ba43b9`) — Auth + JWT + Frontend Login: `routers/auth.py` + `middleware/auth_middleware.py` + httpOnly cookie + Supabase Auth + `app/login/page.tsx` + `components/AuthGuard.tsx` + `lib/auth.ts` + test_auth.py 9 cases (PlanCard 무수정 wrapper 패턴)
- Wave 4 (Slice 4, `06890c9`) — RLS + SSE Progress D7: `db/migrations/0003_rls_policy.sql` (4 정책 + 2-hop subquery) + `routers/sse.py` (4단계 progress + Origin 검증) + `lib/sse.ts` (EventSource wrapper) + test_rls.py 4 + test_sse.py 4 + ADR-021 (RLS) + ADR-022 (SSE)
- Wave 5 (Slice 5, final) — Close + 회귀 검증: smoke_test_phase_5 12/12 + scenario_simulation v2 10/10 (P-X2 세 번째 자동 게이트) + **security-review Skill 두 번째 트리거** (final verification) + agent-io-check 회귀 + design-review impl §B + retrospective + patterns + archive + state docs

총 5 sub-agent dispatch (100% sub-agent 패턴, Phase 4.5/6 정신 계승). 충돌 0건. **§SELF-VERIFICATION 5/5 PASS**.

핵심 회귀 baseline 보존:
- **PlanCard.tsx 0줄 변경 5연속 (Phase 5 Slice 1~5)** → 누적 **17연속** (Phase 4 4 + Phase 4.5 5 + Phase 6 3 + Phase 5 5) ★
- **component_map.md 0줄 변경 5연속 (Phase 5 Slice 1~5)** → 누적 **27연속** (Phase 2 6 + Phase 3 5 + Phase 4 4 + Phase 4.5 4 + Phase 6 3 + Phase 5 5) ★
- pytest 144/144 baseline → **170/170** (+26 신규: test_db 9 + test_auth 9 + test_rls 4 + test_sse 4)
- smoke_test_phase_5 **12/12** (11 PASS + 1 WARN intended, AuthGuard + /login 신규 drift는 phase-complete v1.2.0 허용)
- scenario_simulation v2 **10/10 PASS** (P-X2 세 번째 자동 게이트, S6~S10 신규 5 시나리오)
- schema_stress_test **5/5 PASS** (Phase 6 baseline 유지)
- audit_naming **0 drift** (Slice 1 + Slice 5)
- audit_page_component **2 intended drift** (Slice 3 AuthGuard + /login route, Phase 5 의도된 신규 — phase-complete v1.2.0 허용)
- next build 12 routes (Phase 4 11 → +1 /login)
- tsc 0 / lint clean (Phase 6 baseline 유지)

회고 핵심 발견:
- ★ **P-X1 §SELF-VERIFICATION 22연속 PASS**: Phase 3:5 + Phase 4:4 + Phase 4.5:4 + Phase 6:4 + Phase 5:5 = 22 Slice 누적. P-AGENT-SCOPE-001 mitigation **22연속 입증**. large phase에서도 0건 재발.
- ★ **security-review Skill 첫 정식 + 두 번째 final**: Phase 5 Slice 1 entry 첫 정식 트리거 (T1~T6 위협 모델 + §4 영역 1~10) → Slice 5 두 번째 (Slice 2~4 실 구현 verify). 보안 결정 명시화 baseline 확립. **P-SECURITY-REVIEW-001 신규 후보**.
- ★ **contract-change Skill 두 번째 본격 트리거**: Phase 6 첫 (output_schema + agent_io_contract + api_contract 3 contract 동시 변경) → Phase 5 두 번째 (`db_schema.md` 신규 — DB schema 첫 정식 contract 등록). 회귀 0건 유지.
- ★ **multi-llm-validation formal 세 번째 트리거**: Phase 4.5 V1~V4 → Phase 6 V1~V5 → Phase 5 V1~V6 (Supabase 채택 / JWT / RLS / SSE / revise_history JSONB / canonical DB 영속). **P-VALIDATION-FORMAL-001 정식 패턴 확정 (3회 누적)**.
- ★ **P-X2 자동 게이트 세 번째 트리거**: Phase 4.5 첫 (5/5) → Phase 6 두 번째 (5/5) → Phase 5 세 번째 (10/10, scenario v2). 자동 게이트 표현력 ↑ (5 → 10 scenarios).
- ★ **graceful fallback 정신 일관 적용**: Supabase 미설정 시 in-memory dict (`_plan_store`) 그대로 → Phase 1~6 baseline 회귀 0건. **P-GRACEFUL-001 패턴 5번째 적용 입증**.
- ★ **4 ADR 신규** (Phase 5 자체): ADR-020 Supabase 채택 / ADR-021 RLS Policy / ADR-022 SSE Progress. Phase 6 ADR-018/019 (Critic canonical + Rewriter v1.1.0)와 함께 누적.
- ★ **PlanCard wrapper 패턴 17연속 입증**: Slice 3 AuthGuard wrapping + Slice 4 SSE Progress UI 모두 `app/plan/[plan_id]/page.tsx` wrapper로 PlanCard 무수정. wrapper 패턴 (Phase 4.5 첫) → Phase 5 5연속 입증.

---

## 데이터

| 항목 | 값 |
|---|---|
| 기간 | 2026-05-29 단일일 (다중 세션, sub-agent 5 dispatch) |
| Total commits (Phase 5) | 5 (Slice 1 badb2c0 + Slice 2 d668c9d + Slice 3 3ba43b9 + Slice 4 06890c9 + Slice 5 final) |
| 신규 파일 | ~30 (smoke_test_phase_5 + retrospective + closing_notes + db/__init__/client + 3 migrations + plans_repo + repositories/__init__ + routers/auth + middleware/auth_middleware + routers/sse + 4 tests + apps/web/app/login/page + components/AuthGuard + lib/auth + lib/sse + ADR-020/021/022 + 2 validations + 2 security_reviews + skill_usage_log 등) |
| 수정 파일 | ~10 (config.py + routers/plans.py 호환만 + lib/types.ts + app/plan/[plan_id]/page.tsx wrapper + meta/skill_usage_log.md + PROJECT_STATE.md + PHASE_REGISTRY.md + 00_START_HERE.md + README × 2) |
| 줄 수 변화 | +~2100 (backend +~1500 / frontend +~600 / scripts +~200 / contracts +~200 / docs/decisions +~150 / meta +~400) |
| 신규 ADR | 3 (ADR-020 Supabase + ADR-021 RLS + ADR-022 SSE) |
| 변경된 contract | 1 (db_schema.md 신규 — contract-change Skill 두 번째 본격) |
| backend db 신규 layer | db/ 폴더 신규 (client + repositories + migrations × 3) |
| backend agents 변경 | 0 (Phase 6 baseline 유지) |
| Frontend routes 변화 | 11 → 12 (+/login) |
| Frontend types 신규 interface | AuthSession |
| pytest 결과 | **170/170 PASS** (Phase 6 144 baseline + Phase 5 신규 26) |
| pytest 신규 케이스 | 26 (test_db 9 + test_auth 9 + test_rls 4 + test_sse 4) |
| audit_naming | 0 drift (Slice 1 + Slice 5) |
| audit_page_component | 2 intended drift (Slice 3 AuthGuard + /login route, phase-complete v1.2.0 허용 WARN) |
| smoke_test_phase_5 | **12/12** (11 PASS + 1 WARN, exit 0 PASS) |
| scenario_simulation v2 | **10/10 PASS** (P-X2 세 번째 자동 게이트) |
| schema_stress_test | 5/5 PASS (Phase 6 v2 유지) |
| next build | 12 routes (Phase 4 11 + Phase 5 Slice 3 /login) |
| tsc / lint | 0 errors / clean |
| Sub-agent dispatch | 5 (Slice 1~5 모두) |
| **P-X1 §SELF-VERIFICATION** | **5/5 PASS (Phase 5)** ★ |
| **P-X1 누적 streak** | **22연속 (Phase 3 5 + Phase 4 4 + Phase 4.5 4 + Phase 6 4 + Phase 5 5)** ★ |
| **PlanCard.tsx deviation** | **0건 (Phase 5 전체, 누적 17연속 — Phase 4 4 + Phase 4.5 5 + Phase 6 3 + Phase 5 5)** ★ |
| **component_map.md deviation** | **0건 (Phase 5 전체, 누적 27연속 — Phase 2 6 + Phase 3 5 + Phase 4 4 + Phase 4.5 4 + Phase 6 3 + Phase 5 5)** ★ |
| multi-llm-validation 트리거 | 1 formal self V1~V6 (세 번째) + 1 external placeholder |
| security-review 트리거 | 2 (Slice 1 entry 첫 정식 + Slice 5 final 두 번째) ★ |
| 식별된 P-pattern (Phase 5 신규) | 2 (P-RLS-001 + P-SSE-001) + 1 신규 후보 (P-SECURITY-REVIEW-001) + 2 update (P-X1-EFFECT-001 22연속 + P-VALIDATION-FORMAL-001 세 번째) |
| Phase 5 deferred → Phase 6+/7+/9+ 이관 | Legacy DB 통합 (Phase 1 db/supabase_client.py + Phase 5 db/client.py) / RAG sources (Phase 7+) / per-user rate-limit (Phase 9+) / audit-log (Phase 9+) / pgtap (Phase 9+) / Refresh token rotation (Phase 21+ MFA) |
| 시간 추정 vs 실측 | 15~20h (multi_slice_plan) → 실측 ~14-16h (1 day 다중 세션) |

---

## 분석

### 잘된 것

1. **★ P-X1 22연속 PASS — 5 Slice 모두 sub-agent + 충돌 0건**: Phase 5는 large phase (DB + Auth + RLS + SSE — 보안 영향) 임에도 5 Slice 모두 sub-agent dispatch. 각 sub-agent §SELF-VERIFICATION 수행하여 forbidden 영역 1줄도 침범 안 함. P-AGENT-SCOPE-001 mitigation **22연속 누적 입증**. large + 보안 phase에서도 효과 유지.

2. **★ security-review Skill 첫 정식 + 두 번째 final**: Slice 1 entry 첫 정식 트리거 (T1~T6 위협 모델 + §4 영역 1~10) → Slice 5 두 번째 final verification (Slice 2~4 실 구현 verify). 보안 결정 명시화 baseline 확립. T1 (JWT 누수) → httpOnly cookie, T2 (RLS 우회) → auth.uid() + 4 정책, T4 (SSE hijacking) → Origin 검증, T5 (SQL injection) → ORM, T6 (PII) → baseline 유지. **P-SECURITY-REVIEW-001 신규 후보 (보안 Skill 효과)**.

3. **★ contract-change Skill 두 번째 본격 트리거**: Phase 6 첫 본격 (3 contract 동시) → Phase 5 두 번째 본격 (`db_schema.md` 신규 — DB schema 첫 정식 contract). 4계층 데이터 모델 + plans + users + JSONB 컬럼 (revise_history + recommended_plan_index) 모두 contract 명시. 회귀 0건 유지.

4. **★ multi-llm-validation formal 세 번째 트리거 (V1~V6)**: Phase 4.5 V1~V4 → Phase 6 V1~V5 → Phase 5 V1~V6 (Supabase 채택 / JWT / RLS / SSE / revise_history JSONB / canonical DB 영속). **P-VALIDATION-FORMAL-001 정식 패턴 확정 (3회 누적)**. self.md + external.md placeholder 분리 패턴 안정화.

5. **★ P-X2 자동 게이트 세 번째 트리거 + scenario_simulation v2 (10/10)**: phase-complete v1.2.0 §1.6에서 자동 호출. Phase 4.5 첫 (5/5) → Phase 6 두 번째 (5/5) → Phase 5 세 번째 (**10/10**, v2 — DB/Auth 5 시나리오 추가). 표현력 ↑ + 도입 비용 ↓.

6. **★ graceful fallback 정신 일관 적용**: Supabase 미설정 시 in-memory `_plan_store` dict 그대로 (Phase 1~4.5 baseline 유지). `db/client.py::get_supabase()` Protocol-based + `plans_repo.py` fallback 분기 → Phase 1~4.5 회귀 0건. **P-GRACEFUL-001 다섯 번째 적용 입증** (Phase 1 origin + Phase 4 multi-model + Phase 4.5 revise loop + Phase 6 Rewriter + Phase 5 DB).

7. **★ 4 ADR 신규 (Phase 5 자체)**: ADR-020 Supabase 채택 (대안 비교: PostgreSQL 자체 / Firebase / 자체 서버) + ADR-021 RLS Policy (auth.uid() + 4 정책 + anonymous 호환 NULLABLE) + ADR-022 SSE Progress (4단계 + Origin 검증 + cookie auth). 결정 근거 영구 기록.

8. **★ PlanCard wrapper 패턴 17연속 입증**: Slice 3 AuthGuard wrapping + Slice 4 SSE Progress UI 통합 모두 `app/plan/[plan_id]/page.tsx` wrapper. PlanCard 무수정 유지 → wrapper 패턴 (Phase 4.5 첫) → Phase 5 5연속 입증. **PlanCard.tsx 17연속 0줄 누적 streak 확립**.

9. **★ pytest 144 → 170 (+26) 회귀 0**: test_db 9 (Supabase mock + plans_repo CRUD) + test_auth 9 (JWT mock + login + me + logout) + test_rls 4 (다른 user 차단 + 본인 통과) + test_sse 4 (event stream + 4 steps + schema + Origin 403). 모두 PASS. conftest.py mock fixture 재사용 + cookie 기반 TestClient.

10. **★ Large phase (15~20h) + 보안 phase 안전 완수**: Phase 5 large phase + 첫 보안 phase (Auth + RLS + JWT + SSE)임에도 회귀 0 + deviation 0 + P-X1 5/5. mini-phase (Phase 4.5 + Phase 6) 정신을 large phase에 확장 성공.

### 안 된 것

1. **multi-llm-validation external placeholder만**: Phase 4.5/6과 같은 패턴 — external.md는 placeholder 작성, 실 외부 GPT/Gemini 검토는 사용자가 외부에서 진행 시 채움. 큰 보안 phase였음에도 사용자 결정 정합으로 placeholder 분리. **수용 가능 — 사용자 결정 정합**.

2. **legacy DB 인프라 잔존**: Phase 1 Slice 5에서 이미 일부 DB 인프라 작성됨 (`db/supabase_client.py` legacy + `db/save_video_planning`) → Slice 2가 공존 layer로 작성 (zero-padding 다른 0001 + Protocol-based get_supabase). 향후 Phase 6+에서 통합 권장. **개선 제안 §1 (Legacy DB 통합)**.

3. **Refresh token rotation 미구현**: Slice 1 권장 조치에서 NG로 결정 (Phase 21+ MFA 시점 도입). 현 7일 만료 후 재로그인.

4. **per-user rate-limit + audit-log 미도입**: security-review §4 권장 (Phase 9+ 이관). Phase 5 scope 제외.

5. **TestClient cookies= deprecation warning**: starlette 최신 API로 `client.cookies.set()` 사용 권장 (현 `cookies={...}` deprecated). 개선 제안 §3.

### 배운 것

1. **graceful fallback + Protocol-based DI 패턴 안정성 입증**: Supabase 미설정 / 실패 시 in-memory dict 그대로 → Phase 1~6 baseline 회귀 0건. DB layer 추가 시 동일 패턴 권장 — Phase 7+ RAG / Phase 9+ eval-run 등.

2. **wrapper 패턴 large phase 확장 효과**: Phase 4.5 첫 (Plan card 무수정 + page wrapper) → Phase 6 baseline 유지 → Phase 5 5연속 (AuthGuard wrapping + SSE Progress UI). PlanCard 17연속 0줄. **wrapper 패턴은 large + 보안 phase에서도 유효** (PlanCard는 visual + 비즈니스 로직만, auth/state는 wrapper에서 흡수).

3. **security-review Skill 첫 트리거 → final verification 두 번째 트리거 패턴**: Slice 1 entry → 위협 모델 T1~T6 + 권장 조치 → Slice 2~4 실 구현 → Slice 5 final verify (T1~T6 ↔ 실 구현 ↔ 잔존 risk). **2-trigger 패턴은 보안 phase 표준화 가능**. Phase 7+ RAG security, Phase 9+ retention 도입 시 동일 패턴 재사용.

4. **scenario_simulation v2 (5 → 10) — P-X2 evolution 패턴**: Phase 4.5 첫 (5 scenarios) → Phase 6 두 번째 (5 유지) → Phase 5 세 번째 (10 — DB/Auth 5 추가). file count 휴리스틱 표현력 ↑ + 도입 비용 ↓. **P-X2-EFFECT-001 evolution 패턴 (v1 file count → v1.5 file count 확장 → v2 schema_stress matrix → v3 stub patch + rollback 시뮬레이션 후보)**.

5. **contract-change Skill (db_schema.md 신규) — schema-first DB 도입 패턴**: 4계층 데이터 모델 + plans + users + JSONB 컬럼 → DB migration 작성 전 contract 명시. Phase 5 Slice 2 schema drift 위험 0. **schema-first 패턴 Phase 7+ RAG schema, Phase 9+ eval schema 도입 시 재사용**.

6. **legacy + new layer 공존 패턴 (zero-padding 다른 0001 migrations)**: Phase 1 Slice 5 db/supabase_client.py legacy + Phase 5 Slice 2 db/client.py 공존 → Protocol-based get_supabase로 분리. **즉시 통합 vs 공존 후 통합 결정**: Phase 6+ 통합 mini-phase 권장 (개선 제안 §1). 즉시 통합은 회귀 위험 ↑, 공존은 cognitive load ↑.

### 근본 원인 (해당 없음 — 본 phase deviation 0건)

Phase 4.5/6처럼 deviations 0건. closing_notes.md deviations 섹션 비어있음. P-X1 22연속 PASS로 forbidden 영역 침범 0건 — root cause 분석 불요.

audit_page_component WARN 2 drift는 **의도된** 신규 (Slice 3 AuthGuard component + /login route) — phase-complete v1.2.0 §1.6 WARN 허용 (FAIL 아님), `phase_5_audit_page_component_intended_drift` 사유 명시.

### 부가 발견 사항 (개선 후보)

| 항목 | 영향 | 빈도 | 분류 |
|---|---|---|---|
| Phase 1 db/supabase_client.py legacy 잔존 | 보통 (cognitive load) | 1회 (Phase 5 Slice 2 발견) | Phase 6+ 통합 mini-phase |
| TestClient cookies= deprecation | 작음 (starlette 최신 API) | 다수 (test_auth.py) | Phase 6+ 마이그 |
| EmailStr 의존성 | 작음 (자체 정규식 사용) | 1회 (Slice 3) | Phase 6+ pydantic[email] 추가 검토 |
| SSE worker mock 4단계 | 보통 (실 plan 생성 worker 연동 부재) | 1회 (Slice 4) | Phase 8+ MOA Lite 통합 |
| per-user rate-limit 미도입 | 보통 (비용 폭탄 risk) | 1회 (security-review §4) | Phase 9+ |
| audit-log 미도입 | 보통 (운영 가시성) | 1회 (security-review §4) | Phase 9+ |
| pgtap RLS 자동 검증 | 작음 (수동 test_rls만) | 1회 (security-review §4) | Phase 9+ |

---

## 개선 제안

### 개선 제안 1 (우선순위: ↑): Legacy DB 통합 mini-phase (Phase 6+)

- **무엇을**: Phase 1 Slice 5의 `db/supabase_client.py` legacy + Phase 5 Slice 2의 `db/client.py` 통합. zero-padding 다른 0001 migrations 통합. Protocol-based DI 일원화.
- **왜**: 공존 layer는 cognitive load ↑. 향후 RAG / agent_io_logs 도입 시 동일 패턴 누적되면 정리 비용 ↑↑. Phase 6+ mini-phase (4~6h)로 통합 권장.
- **어디에**: `backend/fastapi/db/*` 통합 + migrations 통합 zero-padding
- **상태**: Phase 6+ entry 시점 사용자 검토

### 개선 제안 2 (우선순위: 보통): TestClient cookies= 마이그

- **무엇을**: `test_auth.py`에서 `client.cookies.set(...)` 패턴으로 마이그 (현 `cookies={...}` deprecated).
- **왜**: starlette 최신 API 정합 + DeprecationWarning 발행 제거 → pytest warnings 청정 baseline 유지.
- **어디에**: `backend/fastapi/tests/test_auth.py`
- **상태**: Phase 6+ entry 시점

### 개선 제안 3 (우선순위: 보통): EmailStr 의존성 추가 검토

- **무엇을**: Slice 3 자체 정규식 (`re.match` email pattern) → `pydantic[email]` 추가 검토.
- **왜**: 정규식 한계 (RFC 5322 정합 부족). 사용자 데이터 보호 baseline 강화.
- **어디에**: `backend/fastapi/routers/auth.py` LoginRequest
- **상태**: Phase 6+ 사용자 데이터 본격화 시점

### 개선 제안 4 (우선순위: 보통): SSE worker 실 plan 생성 worker와 연동

- **무엇을**: 현 Slice 4 mock 4단계 → 실 plan 생성 worker (`routers/plans.py::generate_plans`) 와 연동. SSE event는 mock asyncio.sleep이 아니라 실 worker progress callback 수신.
- **왜**: Phase 8+ MOA Lite 본격화 시 worker 통합 필수. 현 SSE는 UX 시연용.
- **어디에**: `backend/fastapi/routers/sse.py` + `routers/plans.py` worker callback
- **상태**: Phase 8+ MOA Lite entry 시점

### 개선 제안 5 (우선순위: ↑): per-user rate-limit + audit-log 도입 (Phase 9+)

- **무엇을**: per-user LLM quota (분당/일별 호출 수 상한) + audit-log (사용자 접근 / 권한 변경 / 보안 이벤트). security-review §4 권장.
- **왜**: 비용 폭탄 방지 (T7 신규 위협) + 운영 가시성 baseline.
- **어디에**: `backend/fastapi/middleware/rate_limit_middleware.py` 신규 + `backend/fastapi/db/migrations/0004_audit_log.sql` 신규
- **상태**: Phase 9+ cost-review Skill 활성 시점

### 개선 제안 6 (우선순위: 낮음): pgtap RLS 자동 검증 (Phase 9+)

- **무엇을**: `db/migrations/0003_rls_policy.sql` 정책 → pgtap 자동 테스트 셋. 현 test_rls.py 4 cases는 mock 기반.
- **왜**: RLS 정책 SQL bug 자동 감지. Supabase 자체 pgtap 지원 확인.
- **어디에**: `backend/fastapi/db/tests/test_rls_pgtap.sql` 신규
- **상태**: Phase 9+ eval-run 정식화 시점

---

## 패턴 등록 (meta/patterns.md 갱신)

| 패턴 ID | 설명 | 관련 회고 | 상태 |
|---|---|---|---|
| **P-X1-EFFECT-001** (update) | P-X1 §SELF-VERIFICATION **22연속 PASS** 효과 누적 측정 (Phase 3 5 + Phase 4 4 + Phase 4.5 4 + Phase 6 4 + Phase 5 5) | phase-3 + phase-4 + phase-4.5 + phase-6 + phase-5 | 갱신 (Phase 5) — large + 보안 phase에서도 효과 입증 + PlanCard 17연속 + component_map 27연속 |
| **P-RLS-001** (신규) | RLS 정책 + 인증/익명 endpoint 분리 패턴 (auth.uid() + 4 정책 + NULLABLE auth_user_id + 2-hop subquery via brands) | phase-5 | 신규 등록 (Phase 5) — Phase 7+ Custom RAG / Phase 9+ retention 도입 시 재사용 |
| **P-SSE-001** (신규) | SSE 4단계 progress + Origin 검증 + cookie-based auth (withCredentials=true) + heartbeat 30s + X-Accel-Buffering | phase-5 | 신규 등록 (Phase 5) — Phase 8+ MOA Lite worker 통합 시 evolution |
| **P-SECURITY-REVIEW-001** (신규 후보) | security-review Skill 2-trigger 패턴 (entry 위협 모델 + final verification) — 보안 phase 표준화 | phase-5 | 신규 등록 후보 (Phase 5 첫 정식 + 두 번째 final 입증, Phase 7+/9+ 보안 phase 재사용 후 정식 채택 검토) |
| **P-VALIDATION-FORMAL-001** (update) | multi-llm-validation formal self + 외부 분리 패턴 세 번째 입증 (Phase 4.5 V1~V4 → Phase 6 V1~V5 → Phase 5 V1~V6) | phase-4.5 + phase-6 + phase-5 | 정식 패턴 확정 (Phase 5 세 번째 트리거로 3회 누적) |

→ Phase 1~6 누적 패턴:
- P-DRIFT-001 (mitigated) / P-SLICE-001 / P-GRACEFUL-001 (Phase 5 다섯 번째 적용 입증) / P-FOLDER-PARALLEL-001 / P-AGENT-SCOPE-001 (mitigated by P-X1, **22연속 입증**) / P-DESIGN-LAYERED-001 / P-X1-EFFECT-001 (update **22연속**) / P-THIN-VERTICAL-001 / P-GPT-REVIEW-001 / P-X2-EFFECT-001 (Phase 5 세 번째 자동 게이트) / P-VALIDATION-FORMAL-001 (Phase 5 세 번째 입증 — 정식 확정) / P-CRITIC-CANONICAL-001 (Phase 6) / P-CONTRACT-FIRST-001 (Phase 6 후보 → Phase 5 db_schema.md 적용으로 효과 확장) — 모두 효과 유지

---

## Skill 사용 로그 (Phase 5 동안)

| Skill | Phase 5 사용 횟수 | 비고 |
|---|---|---|
| phase-start (v1.3.0) | 1 | Phase 5 entry, 4점검 PASS (Slice 1) |
| qa-check (v1.2.0) | 1 | Slice 1 entry (11 카테고리 정합) — Slice 5 final qa-check 흡수 |
| contract-change | **1 본격** ★ | Slice 2 `db_schema.md` 신규 — **두 번째 본격 실 변경 통과** (Phase 6 첫 본격 이후) + 회귀 0 |
| meta-retrospective | 1 (지금) | 본 문서 |
| phase-complete (v1.2.0) | 1 | Phase 5 종료 (v1.2.0 §1.6 **세 번째** 자동 게이트, scenario_simulation v2 10/10 PASS) |
| design-review | 1 | Slice 5 impl §B (여섯 번째 사용 — PlanCard 17연속 무수정 정합) |
| harness-audit | 1 | Slice 5 audit_naming + audit_page_component 자동 호출 (audit_naming 0 drift + audit_page_component 2 intended drift WARN) |
| multi-llm-validation | **1 formal self V1~V6** (세 번째) + **1 external placeholder** | **세 번째 formal 트리거** — P-VALIDATION-FORMAL-001 세 번째 입증 → 정식 패턴 확정 |
| **agent-io-check** | **1 회귀** | Slice 5 회귀 검증 — Rewriter v1.1.0 + Critic canonical (Phase 6 baseline) 정합 유지 PASS. Phase 5는 agents 변경 0이므로 회귀만 |
| **security-review** | **2 ★ 첫 정식 + 두 번째 final** | Slice 1 entry 첫 정식 (T1~T6 위협 모델 + §4 영역 1~10) + Slice 5 final verification (Slice 2~4 실 구현 verify). **P-SECURITY-REVIEW-001 신규 후보** |
| 기타 unused | — | eval-design / rag-design / prompt-version-review 등 (Phase 7/9+ 활성화 예상) |

**Phase 5 사용 요약**: 11 Skill 활용 (phase-start v1.3.0 + qa-check + contract-change (db_schema.md) + multi-llm-validation formal 세 번째 + **security-review ★ 첫 정식 + 두 번째 final** + agent-io-check (회귀) + harness-audit + design-review + meta-retrospective + phase-complete v1.2.0 세 번째). Phase 1~5 누적 = **12 Skill 활성화**, 8 unused. **security-review + contract-change 본격 안정화**.

**Phase 6+ 진입 시 활성 예상 Skill**: phase-start v1.3.0 + qa-check + multi-llm-validation formal external 의무 (legacy DB 통합 결정 시) + harness-audit + 다음 phase별 (RAG: rag-design + rag-update / MOA: ai-architecture-review / 저장-피드백: eval-design).

---

## 다음 액션

```
- [x] 본 회고 문서 작성 완료
- [x] meta/patterns.md P-X1-EFFECT-001 update (22연속) + P-RLS-001 신규 + P-SSE-001 신규 + P-SECURITY-REVIEW-001 신규 후보 + P-VALIDATION-FORMAL-001 update (세 번째)
- [x] meta/skill_usage_log.md 갱신 (Phase 5 누적 + security-review 두 번째 + contract-change 두 번째 본격)
- [x] phases/active/phase-5-db-auth/closing_notes.md 작성 (다음 phase 옵션 A/B/C/D)
- [x] phases/active → phases/archive 이동 (git mv)
- [x] PROJECT_STATE / PHASE_REGISTRY / 00_START_HERE / README × 2 갱신
- [ ] 다음 Phase (A/B/C/D) 사용자 결정 대기
```

---

## 다음 phase 옵션 (사용자 결정 대기)

### 옵션 A: Phase 7 — RAG Lite 구현 (8~12h)

- candidate_knowledge 5단계 승격 (pending → filtered → evaluated → approved → promoted)
- pgvector 활용 (Supabase 기본 제공)
- rag-design + rag-update Skill 첫 정식 트리거 예상
- prompt-version-review P-007/P-008 정식화 (NG8 해소)

### 옵션 B: Phase 6+ legacy DB 통합 mini-phase (4~6h) + Phase 7

- Phase 5 개선 제안 §1 — Phase 1 db/supabase_client.py + Phase 5 db/client.py 통합
- migrations zero-padding 통합
- Protocol-based DI 일원화
- 이후 Phase 7 진입

### 옵션 C: Phase 9 — 결과 저장 + 피드백 (6~10h)

- 사용자 plan 선택 / 수정 / 반려 누적
- Phase 5 plans_repo + RLS 활용
- Brand Memory 자동 추출 (확정 결정 [8]) baseline 활성화
- audit-log + per-user rate-limit (security-review §4 권장) 부분 활성화

### 옵션 D: Phase 8 — MOA Lite 본격 (12~16h)

- Intent / Planner / Critic / Rewriter 완전 분리
- Phase 5 SSE Progress worker 통합 (Slice 4 mock → 실 worker)
- ai-architecture-review Skill 첫 정식 트리거 예상
- prompt-version-review P-007/P-008 정식화 (NG8 해소)

진입 전 권장 (체크리스트, 옵션 무관):
- [ ] Legacy DB 통합 결정 (Phase 5 발견 #1)
- [ ] Brand Memory 자동 추출 (확정 결정 [8]) Phase 7+ 활용 baseline 활성화
- [ ] external validation 사용자 채움 (Phase 5 placeholder)

---

## 변경 이력

- 2026-05-29: Phase 5 회고 최초 작성 (phase-complete v1.2.0 §1.6 세 번째 자동 게이트 + §7 회고 자동 호출). **P-X1-EFFECT-001 update (22연속) + P-RLS-001 신규 + P-SSE-001 신규 + P-SECURITY-REVIEW-001 신규 후보 + P-VALIDATION-FORMAL-001 update (세 번째 → 정식 확정) 패턴 등록**. P-AGENT-SCOPE-001 mitigation 22/22 입증. **security-review Skill 첫 정식 + 두 번째 final 트리거 PASS + contract-change Skill 두 번째 본격 실 변경 통과**. 다음 phase = 🟡 pending_user_decision (옵션 A Phase 7 / B Phase 6+legacy / C Phase 9 / D Phase 8).
