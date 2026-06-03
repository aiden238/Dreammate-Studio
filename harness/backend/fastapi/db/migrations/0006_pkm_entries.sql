-- Phase 17 다-S3 — 개인 PKM (personal PKM) — pkm_entries 테이블
--
-- ★ 설계 출처: meta/proposals/2026-06-03_pkm-rag-orchestrator-design.md §8.2 (pkm_entries) +
--     §2/§6.2 (우선순위: user_locked / personal > brand). 본 slice 는 scope='personal' 만 구현
--     (series 는 후속 — CHECK 에는 허용하되 코드 경로는 personal 한정).
--
-- 무엇을: 사용자 개인(계정) 단위 메모리 — auth_user_id 로 격리되는 brand-독립(User 계층) PKM.
--   기존 brand_memory_entries(brand_id keyed, 0005)는 그대로 유지하고, 그 "위에" personal scope 를
--   additive 로 얹는다. 주입 시 personal > brand 우선(설계 §6.2 user_locked/personal 최우선).
--
-- additive only: 신규 테이블 1종. 기존 plans / brands / brand_memory_entries / migrations
--   0001~0005 는 0 변경 → Phase 16 baseline 회귀 0.
-- idempotent: CREATE IF NOT EXISTS + DROP POLICY IF EXISTS (재실행 안전, 0005 패턴 계승).
--
-- 적용 방법:
--   1. Supabase Dashboard → SQL Editor 에서 본 파일 실행.
--   2. 또는 Supabase CLI: `supabase db push`.
--
-- 참조:
--   - meta/proposals/2026-06-03_pkm-rag-orchestrator-design.md §8.2 / §2 / §6.2
--   - docs/contracts/db_schema.md §pkm_entries (메인 세션이 contract-change 로 반영 — 본 migration 과 정합)
--   - db/migrations/0005_feedback_selection.sql (selected_plans user-isolation RLS 패턴 복제 모델)
--   - backend/fastapi/db/repositories/pkm_repo.py (graceful PkmRepo)


-- ─── 1. pkm_entries (개인 PKM — User 계층, brand-독립) ───────────────────
-- §8.2: personal/series scope. 본 slice 는 personal 만 사용(series 는 CHECK 허용·후속 구현).
-- auth_user_id 로 격리(RLS) — brand_id 없이 계정 단위 메모리. entry_type 은 brand_memory_entries
--   enum 5종과 정합(주입 시 build_brand_constraint_preamble 재사용 가능).
CREATE TABLE IF NOT EXISTS pkm_entries (
    id              uuid primary key default gen_random_uuid(),
    scope           text not null,                       -- 'personal' (this slice) | 'series' (후속)
    auth_user_id    uuid,                                -- personal 격리 (RLS, anon nullable 허용)
    content         text not null,
    entry_type      text,                                -- preferred_tone|avoid_phrase|preferred_phrase|success_pattern|rejection_pattern (brand_memory_entries enum 정합)
    is_user_locked  boolean default false,               -- ★ user_locked 최우선 (설계 §6.2) — 자동 갱신/덮어쓰기 금지
    confidence      real default 0.5,                    -- 0–1, 자동 추출 신뢰도 (후속)
    created_at      timestamptz not null default now(),
    updated_at      timestamptz not null default now(),
    check (scope in ('personal','series'))
);
create index if not exists idx_pkm_entries_user on pkm_entries(auth_user_id);


-- ─── 2. RLS (0005 selected_plans user-isolation 패턴 — 계정 격리) ────────
-- in-memory fallback(mock) 시 RLS 미적용 → 실 Supabase 에서만 강제 (0005 §Constraints).
-- anon nullable 허용: auth_user_id IS NULL (게스트, Phase 5 anon endpoint 정합).
-- ★ PII/격리: personal entry 는 요청 auth_user_id(= auth.uid()) 본인만 접근.

ALTER TABLE pkm_entries ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "pkm_entries_user_isolation" ON pkm_entries;

-- pkm_entries: auth_user_id = auth.uid() (anon nullable 허용 — 0005 selected_plans 패턴)
CREATE POLICY "pkm_entries_user_isolation" ON pkm_entries
    FOR ALL
    USING (auth_user_id = auth.uid() OR auth_user_id IS NULL)
    WITH CHECK (auth_user_id = auth.uid() OR auth_user_id IS NULL);


-- ─── 3. comments ──────────────────────────────────────────────────────
COMMENT ON TABLE pkm_entries IS 'Phase 17 다-S3 — 개인 PKM (personal scope, auth_user_id 격리, User 계층 brand-독립). 설계 proposal §8.2. series scope 는 후속.';
COMMENT ON COLUMN pkm_entries.is_user_locked IS '★ user_locked 최우선 (설계 §6.2) — 자동 갱신/덮어쓰기 금지.';


-- ─── 4. 비고 (후속 slice — series scope / embedding / source_candidate_id) ──
-- 설계 §8.2 full 스키마(brand_id / series_id / embedding vector(1536) / source_candidate_id)는
-- series PKM + orchestrator vector 단계 도입 시 additive 로 확장(별도 migration). 본 slice 는
-- personal scope 최소 컬럼만 — 주입(읽기) 경로만 배선(쓰기 자동화 X, NG12 계승).
