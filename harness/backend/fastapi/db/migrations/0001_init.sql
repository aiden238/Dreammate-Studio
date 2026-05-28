-- Phase 5 Slice 2 — initial schema (4계층 + plans + users)
--
-- 본 파일은 Phase 5 신규 baseline 이다. Phase 1 Slice 5 의 `001_init.sql`
-- (video_projects + plan_candidates 익명 저장 minimal) 과 별도 운영된다.
--
-- Naming convention: 0001~0099 = Phase 5+ 4-digit zero-padded.
--                    001~099   = Phase 1~4 3-digit (legacy, 보존).
--
-- 적용 방법:
--   1. Supabase Dashboard → SQL Editor 에서 본 파일 실행.
--   2. 또는 Supabase CLI: `supabase db push`.
--
-- 4계층 데이터 모델 (User → Brand → Domain → Series → Video Project)
-- 확정 결정 [6] 정합. Brand Memory placeholder (tone JSONB) 는 Phase 6+ 활용.
--
-- 참조:
--   - docs/contracts/db_schema.md §2~7 (Phase 5 갱신 본문)
--   - docs/decisions/phase_5_supabase_adoption.md (ADR-020)
--   - meta/validations/2026-05-29_phase-5-pre-entry_self.md §V5, §V6
--   - meta/security_reviews/2026-05-29_phase-5-auth-rls.md §3 T2 (RLS 예고)

-- ─── 1. brands ──────────────────────────────────────────────────────
-- 확정 결정 [6] 4계층 최상위. Brand Memory tone (Phase 6+) placeholder 포함.
CREATE TABLE IF NOT EXISTS brands (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    auth_user_id    UUID NOT NULL,                       -- Supabase auth.users.id (Slice 3 FK)
    name            TEXT NOT NULL,
    description     TEXT,
    tone            JSONB DEFAULT '{}'::jsonb,           -- Brand Memory placeholder (Phase 6+)
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ─── 2. domains ─────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS domains (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    brand_id        UUID NOT NULL REFERENCES brands(id) ON DELETE CASCADE,
    name            TEXT NOT NULL,
    description     TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ─── 3. series ──────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS series (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    domain_id       UUID NOT NULL REFERENCES domains(id) ON DELETE CASCADE,
    name            TEXT NOT NULL,
    description     TEXT,
    target          JSONB DEFAULT '{}'::jsonb,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ─── 4. video_projects ──────────────────────────────────────────────
-- Phase 5 신규 — Phase 1 Slice 5 `video_projects` (legacy 001_init.sql) 와는 별도 운영.
-- Slice 3 (Auth) 도입 시 auth_user_id NOT NULL REFERENCES auth.users(id) 확정.
CREATE TABLE IF NOT EXISTS video_projects (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    series_id       UUID REFERENCES series(id) ON DELETE SET NULL,
    auth_user_id    UUID NOT NULL,                       -- Slice 3 FK
    title           TEXT NOT NULL,
    status          TEXT NOT NULL DEFAULT 'draft',       -- draft | published
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ─── 5. plans (Phase 5 핵심 — _plan_store dict 의 영속화) ─────────────
-- Phase 4 Slice 1 router 의 _plan_store: dict 를 PostgreSQL 영속화.
-- Phase 4.5 (revise loop) + Phase 6 (canonical Critic) 컬럼 모두 포함.
-- Slice 4 RLS 정책 (ADR-021): auth_user_id = auth.uid() (NULL 은 anonymous endpoint 별도 처리).
CREATE TABLE IF NOT EXISTS plans (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    auth_user_id            UUID,                        -- nullable: Phase 1 /api/v1/generate anonymous 호환 (Slice 4 ADR-021)
    video_project_id        UUID REFERENCES video_projects(id) ON DELETE SET NULL,
    mode                    TEXT NOT NULL,               -- 'discovery' | 'quick'
    status                  TEXT NOT NULL DEFAULT 'draft', -- draft | generated | finalized
    wizard_state            JSONB DEFAULT '{}'::jsonb,
    plan_candidates         JSONB DEFAULT '[]'::jsonb,   -- Phase 4 3-plan 결과
    critic_evaluation       JSONB,                       -- Phase 6 canonical (overall_score + dimensions)
    revise_history          JSONB,                       -- Phase 4.5 ADR-016 + Phase 6 ReviseAttempt
    recommended_plan_index  INTEGER,                     -- Phase 4.5 ADR-017 best-plan
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ─── indexes ────────────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_plans_auth_user_id       ON plans(auth_user_id);
CREATE INDEX IF NOT EXISTS idx_plans_video_project_id   ON plans(video_project_id);
CREATE INDEX IF NOT EXISTS idx_brands_auth_user_id      ON brands(auth_user_id);
CREATE INDEX IF NOT EXISTS idx_video_projects_auth_user ON video_projects(auth_user_id);
CREATE INDEX IF NOT EXISTS idx_domains_brand_id         ON domains(brand_id);
CREATE INDEX IF NOT EXISTS idx_series_domain_id         ON series(domain_id);

-- ─── 비고 ───────────────────────────────────────────────────────────
-- Slice 3 (Auth + JWT, multi_slice_plan.md):
--   - auth_user_id NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE 도입.
-- Slice 4 (RLS, ADR-021 예정):
--   - 0003_rls_policy.sql 에서 plans / video_projects RLS 활성화.
--   - anonymous endpoint (/api/v1/generate, /plans/start) 는 anon role 분리.
