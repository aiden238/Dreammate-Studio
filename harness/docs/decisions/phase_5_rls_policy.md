# ADR-021 — Phase 5 RLS Policy

> Date: 2026-05-29
> Status: Accepted
> Phase: 5 Slice 4
> Related: ADR-020 (Supabase 채택), security-review §T2 (RLS 우회 HIGH), V3 (RLS 정책)

---

## Context

Phase 5 가 다중 사용자 영속 데이터를 처음 도입한다 (Slice 2 — Supabase + 4계층 + plans).
다중 사용자 시스템은 본인 row 외의 데이터에 접근하지 못해야 한다. 동시에 Phase 1 의
`/api/v1/generate` (NG7 → Phase 8+ 제거 예정) 와 Phase 5 의 `/plans/start` 는
인증 없이 (anon role) 호출되며, 이들은 본 RLS 정책에 의해 차단되어서는 안 된다.

security-review §T2 (RLS 우회) 는 HIGH 우선순위로 다음을 권장한다:

- plans.auth_user_id = auth.uid() 직접 검증.
- anonymous endpoint 와 authenticated endpoint 의 명확한 분리.
- service_role key 운영 정책 (backend .env only).

## Decision

### 1. RLS 활성화 대상 (5 테이블)

- `brands`           — auth_user_id 직접
- `domains`          — brand 통한 인증 (auth_user_id 없음)
- `series`           — domain → brand 통한 인증 (2-hop JOIN)
- `video_projects`   — auth_user_id 직접
- `plans`            — auth_user_id 직접 (★ 핵심)

### 2. 정책 구조

- **brands / video_projects / plans**: `auth_user_id = auth.uid()` 직접 검증.
- **domains / series**: 상위 테이블의 `auth_user_id` 를 `EXISTS (SELECT 1 ... JOIN ...)` 로 검증.
- **plans 추가 보호**: `auth_user_id IS NOT NULL AND auth_user_id = auth.uid()` —
  authenticated 사용자가 anonymous row (auth_user_id NULL) 를 본인 row 로 오인 못함.

### 3. anonymous endpoint 분리

- `/api/v1/generate` (Phase 1 endpoint, NG7) → **anon role** (RLS 적용 안 됨).
- `/api/v1/plans/start` (Phase 5 진입 endpoint) → **anon role** 가능.
- `/api/v1/plans/{plan_id}/generate`, `/api/v1/plans/{plan_id}` → **authenticated role** (RLS 강제).
- `/api/v1/plans/{plan_id}/progress` (Slice 4 SSE) → user 옵션 (auth 있으면 검증, 없으면 anonymous progress).

Supabase 의 anon role 호출은 정책 비교 대상이 되지 않으므로 (authenticated 와 anon
는 별도 역할), Phase 1 호환은 자동 유지된다.

### 4. service_role key 운영

- backend `.env` only (`SUPABASE_SERVICE_KEY` — `NEXT_PUBLIC_*` prefix 절대 금지).
- RLS 우회는 Supabase 표준 동작 (정책상 의도된 admin path).
- rotation 주기 90일 — Phase 11+ 자동화.

### 5. Migration 파일

- `backend/fastapi/db/migrations/0003_rls_policy.sql` 신규.
- idempotent (`DROP POLICY IF EXISTS` 선행 후 `CREATE POLICY`).
- 0001/0002 이전 migration 무변경.

## Implementation impact

- 본 Slice 4 에서는 SQL 파일만 추가 (Supabase Dashboard 또는 CLI 적용은 운영자 작업).
- Slice 4 `test_rls.py` 4 케이스로 정책 ↔ PlansRepo 호환 검증.
- db_schema.md §9 에 anonymous endpoint 분리 명시 (Slice 2 baseline 유지 + Slice 4 확정).

## Trade-offs

- **Anonymous + Authenticated endpoint 분리** → routing 복잡도 ↑. 단, Phase 8+ 에서
  /generate 제거 시 자연 단순화.
- **계층 정책 (domains via brands, series via 2-hop)** → 매 row 마다 EXISTS subquery →
  성능 영향. 완화: 0001_init.sql 의 기존 인덱스 + 본 SQL §6 의 partial index 보강.
- **service_role key 사용 시 RLS 전체 우회** → Supabase 표준이지만, key 노출 시
  치명적. backend .env 강제 + frontend `NEXT_PUBLIC_*` prefix 금지로 차단.
- **plans.auth_user_id NULL 명시 차단** → anonymous row 를 인증 사용자가 못 봄.
  단, 운영자(service_role) 는 여전히 모든 row 접근 가능 (의도된 admin path).

## Alternatives considered

- **a) 단일 plans 테이블 + 정책 없이 application layer 에서 user_id 필터**
  → 권한 검사 누락 risk + audit 어려움 → 거절.
- **b) 모든 테이블에 auth_user_id 컬럼 + 직접 정책 (JOIN 없음)**
  → schema 단순화되지만 4계층 의미 손실 + domains 가 brand 와 분리될 수 있음 → 거절.
- **c) RLS 미활성화 + backend 가 service_role key 로 모든 요청 처리**
  → backend 가 항상 RLS 우회 → DB 자체 방어선 0 → 거절.

선택: 본 ADR 의 계층 정책 + plans 직접 검증 + anon/auth 분리.

## References

- `meta/security_reviews/2026-05-29_phase-5-auth-rls.md` §3 T2, §4 권한/RLS (영역 5)
- `meta/validations/2026-05-29_phase-5-pre-entry_self.md` §V3
- `docs/contracts/db_schema.md` §9 RLS, §2 ER 다이어그램
- `docs/contracts/llm_security_contract.md` §5.2 (service_role key)
- `backend/fastapi/db/migrations/0001_init.sql` (테이블 정의)
- `backend/fastapi/db/migrations/0003_rls_policy.sql` (본 ADR 의 정책 SQL)
