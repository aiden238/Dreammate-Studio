-- Phase 9 Slice 2 — 결과 저장 + 피드백 + Brand Memory 준비 (ADR-030 / ADR-031)
--
-- ★ 실 plans 테이블 정합 (Phase 5 0001_init.sql):
--     plans.id (PK) + plan_candidates (JSONB 3-plan 배열) + auth_user_id (nullable, anon 호환).
--     selected_option_index 0–2 = plan_candidates JSONB 배열 인덱스.
--   db_schema.md §4.2 idealized plan_options(option_id PK) + §4.3 idealized selected_plans
--   (selected_option_id → plan_options.option_id) 는 Phase 11+ 4계층 full linkage (NG2) — 본 migration 미반영.
--
-- additive only: 신규 테이블 3종. 기존 plans / plan_candidates / migrations 0001~0004 0 변경 → Phase 8 baseline 회귀 0.
-- idempotent: CREATE IF NOT EXISTS + DROP POLICY IF EXISTS (재실행 안전, Phase 5 0003_rls_policy.sql 패턴).
--
-- 적용 방법:
--   1. Supabase Dashboard → SQL Editor 에서 본 파일 실행.
--   2. 또는 Supabase CLI: `supabase db push`.
--
-- 참조:
--   - docs/contracts/db_schema.md §4.3 selected_plans (Phase 9 실 구현 추가) + §5.2 feedback_events + §6 brand_memory_entries
--   - docs/decisions/phase_9_feedback_selection.md (ADR-030 — 실 plans 정합 + graceful PlansRepo 패턴)
--   - docs/decisions/phase_9_brand_memory_prep.md (ADR-031 — Brand Memory 준비만, agent 미구현 Phase 10+)
--   - meta/security_reviews/2026-05-29_phase-9-feedback-pii.md (T1 reason PII 저장 전 마스킹 / T3 RLS user 격리)
--   - 0001_init.sql (plans.id / brands.id / brands.auth_user_id PK 정의) + 0003_rls_policy.sql (RLS 패턴)


-- ─── 1. selected_plans (plan 선택 — 실 plans 정합) ─────────────────────
-- ADR-030 §1: plan_id (→ plans.id) + selected_option_index (0–2, plan_candidates JSONB 배열 인덱스).
-- 선택 plan 내용은 plans.plan_candidates[selected_option_index] 로 조회 (4계층 미연결 무관).
CREATE TABLE IF NOT EXISTS selected_plans (
    id                    uuid primary key default gen_random_uuid(),
    plan_id               uuid not null references plans(id) on delete cascade,
    auth_user_id          uuid,                          -- nullable (anon 호환, Phase 5 패턴)
    selected_option_index smallint not null,             -- 0~2 (plan_candidates 배열 index)
    selection_reason      text,                          -- 사용자 선택 사유 (PII 저장 전 마스킹 — T1)
    created_at            timestamptz not null default now(),
    check (selected_option_index between 0 and 2)
);
create index if not exists idx_selected_plans_plan on selected_plans(plan_id);
create index if not exists idx_selected_plans_user on selected_plans(auth_user_id);


-- ─── 2. feedback_events (like/dislike/reject/regenerate — 실 plans 정합) ──
-- ADR-030 §2: plan_id (→ plans.id) + event_type enum + option_index (특정 candidate 대상, null=plan 전체).
-- target_kind/target_id (db_schema §5.2 idealized 4계층) 는 plan_id 정합으로 단순화 (Phase 9 범위).
CREATE TABLE IF NOT EXISTS feedback_events (
    id            uuid primary key default gen_random_uuid(),
    plan_id       uuid not null references plans(id) on delete cascade,
    auth_user_id  uuid,                                  -- nullable (anon 호환, Phase 5 패턴)
    option_index  smallint,                              -- 0~2 (특정 candidate 대상, null=plan 전체)
    event_type    text not null,                         -- 'like'|'dislike'|'reject'|'regenerate'
    reason        text,                                  -- 자유 입력 (PII 저장 전 마스킹 — security-review T1/T2)
    created_at    timestamptz not null default now(),
    check (event_type in ('like','dislike','reject','regenerate')),
    check (option_index is null or option_index between 0 and 2)
);
create index if not exists idx_feedback_plan on feedback_events(plan_id);
create index if not exists idx_feedback_user on feedback_events(auth_user_id);


-- ─── 3. brand_memory_entries (Phase 9 준비 — agent 미구현, ADR-031 / NG1) ──
-- db_schema §6 정의를 등록. BrandMemoryRepo 수동/준비용 entry CRUD 만 — 자동 추출 agent (P-AUX-2) Phase 10+.
-- brand_id → brands.id (실 0001_init.sql PK). source_plan_id → plans.id (실 plans 정합).
CREATE TABLE IF NOT EXISTS brand_memory_entries (
    entry_id        uuid primary key default gen_random_uuid(),
    brand_id        uuid references brands(id) on delete cascade,
    entry_type      text not null,                       -- preferred_tone|avoid_phrase|preferred_phrase|success_pattern|rejection_pattern
    content         text not null,
    source_plan_id  uuid references plans(id) on delete set null,
    confidence      real default 0.5,                    -- 0–1, 자동 추출 신뢰도 (Phase 10+)
    is_user_locked  boolean default false,               -- 사용자 잠금 항목은 자동 갱신 금지 (Phase 10+)
    created_at      timestamptz not null default now(),
    updated_at      timestamptz not null default now(),
    check (entry_type in ('preferred_tone','avoid_phrase','preferred_phrase','success_pattern','rejection_pattern'))
);
create index if not exists idx_brand_memory_brand on brand_memory_entries(brand_id);


-- ─── 4. RLS (Phase 5 0003_rls_policy.sql 패턴 — user 격리, security-review T3) ──
-- in-memory fallback(mock) 시 RLS 미적용 → 실 Supabase 에서만 강제 (ADR-030 §Constraints).
-- anon nullable 허용: auth_user_id IS NULL (게스트 plan, Phase 5 anon endpoint 정합).

ALTER TABLE selected_plans  ENABLE ROW LEVEL SECURITY;
ALTER TABLE feedback_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE brand_memory_entries ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "selected_plans_user_isolation"  ON selected_plans;
DROP POLICY IF EXISTS "feedback_events_user_isolation"  ON feedback_events;
DROP POLICY IF EXISTS "brand_memory_owner"              ON brand_memory_entries;

-- selected_plans: auth_user_id = auth.uid() (anon nullable 허용)
CREATE POLICY "selected_plans_user_isolation" ON selected_plans
    FOR ALL
    USING (auth_user_id = auth.uid() OR auth_user_id IS NULL)
    WITH CHECK (auth_user_id = auth.uid() OR auth_user_id IS NULL);

-- feedback_events: auth_user_id = auth.uid() (anon nullable 허용)
CREATE POLICY "feedback_events_user_isolation" ON feedback_events
    FOR ALL
    USING (auth_user_id = auth.uid() OR auth_user_id IS NULL)
    WITH CHECK (auth_user_id = auth.uid() OR auth_user_id IS NULL);

-- brand_memory_entries: brands 를 통한 user 격리 (Phase 5 domains_via_brand 패턴 — brands.id / brands.auth_user_id)
CREATE POLICY "brand_memory_owner" ON brand_memory_entries
    FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM brands
            WHERE brands.id = brand_memory_entries.brand_id
              AND brands.auth_user_id = auth.uid()
        )
    )
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM brands
            WHERE brands.id = brand_memory_entries.brand_id
              AND brands.auth_user_id = auth.uid()
        )
    );


-- ─── 5. comments ──────────────────────────────────────────────────────
COMMENT ON TABLE selected_plans       IS 'Phase 9 ADR-030 — plan 선택 (실 plans 정합, selected_option_index 0–2)';
COMMENT ON TABLE feedback_events       IS 'Phase 9 ADR-030 — 피드백 (like/dislike/reject/regenerate, reason PII 마스킹 T1)';
COMMENT ON TABLE brand_memory_entries IS 'Phase 9 ADR-031 준비 — BrandMemoryRepo 수동/준비용, 자동 추출 agent 미구현 Phase 10+ (NG1)';


-- ─── 6. 비고 (Phase 11+ 4계층 full linkage — NG2) ──────────────────────
-- db_schema.md §4.2 plan_options(option_id PK) + §4.3 idealized selected_plans(selected_option_id → plan_options)
-- 는 Phase 11+ 4계층 full linkage. 본 migration 은 실 plans + plan_candidates JSONB 배열 인덱스 정합만 반영.
-- 자동 추출 (P-AUX-2 brand_memory_extractor) + feedback → candidate_knowledge 자동 승격은 Phase 10+/11+ (NG1/NG12).
