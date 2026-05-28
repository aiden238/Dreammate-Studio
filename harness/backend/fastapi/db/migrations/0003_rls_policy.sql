-- Phase 5 Slice 4 — RLS (Row Level Security) 정책
--
-- security-review §T2 (RLS 우회 HIGH) 권장 적용.
-- ADR-021 (docs/decisions/phase_5_rls_policy.md) 정합.
--
-- 적용 방법:
--   1. Supabase Dashboard → SQL Editor 에서 본 파일 실행.
--   2. 또는 Supabase CLI: `supabase db push`.
--
-- 핵심 원칙:
--   1. 인증 사용자(authenticated role)는 본인 row 만 read/write.
--   2. anonymous role 은 RLS 와 별도 정책으로 처리 — Phase 1 endpoint
--      (`/api/v1/generate`) 와 `/plans/start` 는 anon role 로 호출되며
--      본 정책이 차단하지 않는다 (auth.uid() IS NULL 시 정책 미적용).
--   3. service_role key 는 RLS 우회 (Supabase 표준, backend .env only).
--
-- 참조:
--   - meta/security_reviews/2026-05-29_phase-5-auth-rls.md §3 T2
--   - docs/contracts/db_schema.md §9 RLS
--   - 0001_init.sql (테이블 정의), 0002_phase_4_5_revise_history.sql (revise_history)


-- ─── 0. RLS 활성화 ─────────────────────────────────────────────────────
-- 모든 사용자 소유 테이블에 RLS 활성화.
ALTER TABLE brands           ENABLE ROW LEVEL SECURITY;
ALTER TABLE domains          ENABLE ROW LEVEL SECURITY;
ALTER TABLE series           ENABLE ROW LEVEL SECURITY;
ALTER TABLE video_projects   ENABLE ROW LEVEL SECURITY;
ALTER TABLE plans            ENABLE ROW LEVEL SECURITY;


-- ─── 1. brands ─────────────────────────────────────────────────────────
-- 본인 row 만 read/write. auth.uid() 는 Supabase JWT 의 user_id 를 반환.
DROP POLICY IF EXISTS "brands_owner_read"   ON brands;
DROP POLICY IF EXISTS "brands_owner_insert" ON brands;
DROP POLICY IF EXISTS "brands_owner_update" ON brands;
DROP POLICY IF EXISTS "brands_owner_delete" ON brands;

CREATE POLICY "brands_owner_read" ON brands
    FOR SELECT
    USING (auth_user_id = auth.uid());

CREATE POLICY "brands_owner_insert" ON brands
    FOR INSERT
    WITH CHECK (auth_user_id = auth.uid());

CREATE POLICY "brands_owner_update" ON brands
    FOR UPDATE
    USING (auth_user_id = auth.uid())
    WITH CHECK (auth_user_id = auth.uid());

CREATE POLICY "brands_owner_delete" ON brands
    FOR DELETE
    USING (auth_user_id = auth.uid());


-- ─── 2. domains ────────────────────────────────────────────────────────
-- domains 는 auth_user_id 컬럼이 없음 → 상위 brands 통해 인증.
DROP POLICY IF EXISTS "domains_via_brand_read"   ON domains;
DROP POLICY IF EXISTS "domains_via_brand_insert" ON domains;
DROP POLICY IF EXISTS "domains_via_brand_update" ON domains;
DROP POLICY IF EXISTS "domains_via_brand_delete" ON domains;

CREATE POLICY "domains_via_brand_read" ON domains
    FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM brands
            WHERE brands.id = domains.brand_id
              AND brands.auth_user_id = auth.uid()
        )
    );

CREATE POLICY "domains_via_brand_insert" ON domains
    FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM brands
            WHERE brands.id = domains.brand_id
              AND brands.auth_user_id = auth.uid()
        )
    );

CREATE POLICY "domains_via_brand_update" ON domains
    FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 FROM brands
            WHERE brands.id = domains.brand_id
              AND brands.auth_user_id = auth.uid()
        )
    );

CREATE POLICY "domains_via_brand_delete" ON domains
    FOR DELETE
    USING (
        EXISTS (
            SELECT 1 FROM brands
            WHERE brands.id = domains.brand_id
              AND brands.auth_user_id = auth.uid()
        )
    );


-- ─── 3. series ─────────────────────────────────────────────────────────
-- series 는 domain_id → brand_id → auth_user_id 두 단계 JOIN 으로 인증.
-- 성능: idx_series_domain_id + idx_domains_brand_id + idx_brands_auth_user_id
-- (0001_init.sql 기존 인덱스) 로 완화.
DROP POLICY IF EXISTS "series_via_domain_read"   ON series;
DROP POLICY IF EXISTS "series_via_domain_insert" ON series;
DROP POLICY IF EXISTS "series_via_domain_update" ON series;
DROP POLICY IF EXISTS "series_via_domain_delete" ON series;

CREATE POLICY "series_via_domain_read" ON series
    FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM domains
            JOIN brands ON brands.id = domains.brand_id
            WHERE domains.id = series.domain_id
              AND brands.auth_user_id = auth.uid()
        )
    );

CREATE POLICY "series_via_domain_insert" ON series
    FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM domains
            JOIN brands ON brands.id = domains.brand_id
            WHERE domains.id = series.domain_id
              AND brands.auth_user_id = auth.uid()
        )
    );

CREATE POLICY "series_via_domain_update" ON series
    FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 FROM domains
            JOIN brands ON brands.id = domains.brand_id
            WHERE domains.id = series.domain_id
              AND brands.auth_user_id = auth.uid()
        )
    );

CREATE POLICY "series_via_domain_delete" ON series
    FOR DELETE
    USING (
        EXISTS (
            SELECT 1 FROM domains
            JOIN brands ON brands.id = domains.brand_id
            WHERE domains.id = series.domain_id
              AND brands.auth_user_id = auth.uid()
        )
    );


-- ─── 4. video_projects ─────────────────────────────────────────────────
-- video_projects 는 auth_user_id 직접 컬럼 (0001_init.sql §4).
DROP POLICY IF EXISTS "video_projects_owner" ON video_projects;

CREATE POLICY "video_projects_owner" ON video_projects
    FOR ALL
    USING (auth_user_id = auth.uid())
    WITH CHECK (auth_user_id = auth.uid());


-- ─── 5. plans ──────────────────────────────────────────────────────────
-- security-review §T2 핵심: plans.auth_user_id = auth.uid() 직접 검증.
-- anonymous endpoint (/api/v1/generate, /plans/start) 는 auth.uid() = NULL 이며
-- 본 정책의 비교(NULL = NULL → NULL, falsey)로 차단되지만, anon role 호출 시
-- Supabase 는 RLS 정책 자체를 적용하지 않으므로(authenticated 와 anon 역할 분리)
-- Phase 1 호환은 유지된다.
--
-- 추가 보호: auth_user_id IS NULL 인 row 는 인증 사용자가 본인 row 로
-- 오인하지 못하도록 명시적 차단 (USING 절에서 NOT NULL 강제).
DROP POLICY IF EXISTS "plans_authenticated_read"   ON plans;
DROP POLICY IF EXISTS "plans_authenticated_insert" ON plans;
DROP POLICY IF EXISTS "plans_authenticated_update" ON plans;
DROP POLICY IF EXISTS "plans_authenticated_delete" ON plans;

CREATE POLICY "plans_authenticated_read" ON plans
    FOR SELECT
    USING (
        auth_user_id IS NOT NULL
        AND auth_user_id = auth.uid()
    );

CREATE POLICY "plans_authenticated_insert" ON plans
    FOR INSERT
    WITH CHECK (
        auth_user_id IS NOT NULL
        AND auth_user_id = auth.uid()
    );

CREATE POLICY "plans_authenticated_update" ON plans
    FOR UPDATE
    USING (
        auth_user_id IS NOT NULL
        AND auth_user_id = auth.uid()
    )
    WITH CHECK (
        auth_user_id IS NOT NULL
        AND auth_user_id = auth.uid()
    );

CREATE POLICY "plans_authenticated_delete" ON plans
    FOR DELETE
    USING (
        auth_user_id IS NOT NULL
        AND auth_user_id = auth.uid()
    );


-- ─── 6. RLS performance indexes (보강) ─────────────────────────────────
-- 0001_init.sql 에 이미 idx_plans_auth_user_id, idx_brands_auth_user_id,
-- idx_video_projects_auth_user, idx_domains_brand_id, idx_series_domain_id
-- 가 존재. RLS 조회 hot path 보강용 partial index.
CREATE INDEX IF NOT EXISTS idx_plans_rls_lookup
    ON plans(auth_user_id)
    WHERE auth_user_id IS NOT NULL;


-- ─── 7. anonymous endpoint 분리 노트 ───────────────────────────────────
--
-- Supabase 의 anon role 호출은 본 RLS 정책의 비교 대상이 되지 않는다:
--   - /api/v1/generate (Phase 1 endpoint, NG7 → Phase 8+ 제거 예정) → anon role
--   - /api/v1/plans/start (Phase 5 진입 endpoint, auth 무관) → anon role
--   - /api/v1/plans/{plan_id}/generate, /api/v1/plans/{plan_id} → authenticated role
--
-- backend 가 service_role key 로 호출하는 경우 RLS 전체 우회 (Supabase 표준 동작).
-- 따라서 service_role key 는 절대 frontend 노출 금지 (llm_security_contract §5.2).


-- ─── 8. verification ──────────────────────────────────────────────────
-- 본 migration 적용 후 다음 쿼리로 정책 활성 여부 확인 가능:
--
--   SELECT tablename, policyname, permissive, roles, cmd
--   FROM   pg_policies
--   WHERE  schemaname = 'public'
--   ORDER  BY tablename, policyname;
--
-- 자동 검증: backend/fastapi/tests/test_rls.py (Slice 4).
