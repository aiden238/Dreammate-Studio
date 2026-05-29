-- Phase 7 Slice 2 — RAG 5단계 schema
--
-- ADR-024 (Phase 5.5 RAG scope evolution) + ADR-025 (Phase 7 RAG architecture)
-- + ADR-026 (Phase 7 promotion logic) 정합.
--
-- 적용 방법:
--   1. Supabase Dashboard → SQL Editor 에서 본 파일 실행.
--   2. 또는 Supabase CLI: `supabase db push`.
--
-- 핵심 원칙:
--   1. 5단계 enum (pending → filtered → evaluated → approved → promoted)
--   2. candidate_knowledge: 5단계 추적 + promotion_history append-only
--   3. approved_knowledge: 5단계 종료 — retrieval 활성 대상
--   4. pgvector extension + ivfflat index (1536 dim — text-embedding-3-small)
--   5. RLS: Phase 5 0003_rls_policy.sql 패턴 계승 (auth_user_id + brand 격리)
--
-- 참조:
--   - docs/contracts/rag_data_contract.md §18 (Phase 7 정식 등록)
--   - docs/decisions/phase_7_rag_architecture.md (ADR-025)
--   - docs/decisions/phase_7_promotion_logic.md (ADR-026)
--   - 0001_init.sql (brands FK), 0003_rls_policy.sql (RLS 패턴)


-- ─── 0. pgvector extension ─────────────────────────────────────────────
CREATE EXTENSION IF NOT EXISTS vector;


-- ─── 1. knowledge_stage enum ───────────────────────────────────────────
DO $$ BEGIN
    CREATE TYPE knowledge_stage AS ENUM (
        'pending',      -- 1단계: 진입
        'filtered',     -- 2단계: quality_filter 통과
        'evaluated',    -- 3단계: eval_rubric ≥ 0.6
        'approved',     -- 4단계: hybrid (자동 ≥ 0.8 / 수동 0.6~0.8)
        'promoted'      -- 5단계: approved_knowledge 이동
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;


-- ─── 2. candidate_knowledge ────────────────────────────────────────────
-- Phase 7 RAG Lite 정식 등록 (ADR-024/025/026).
-- §18.2 contract 정합.
CREATE TABLE IF NOT EXISTS candidate_knowledge (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content             TEXT NOT NULL,
    stage               knowledge_stage DEFAULT 'pending',
    metadata            JSONB DEFAULT '{}'::jsonb,
    embedding           vector(1536),                          -- text-embedding-3-small
    auth_user_id        UUID NULL,                              -- Phase 1 anonymous 호환 (ADR-021 패턴)
    brand_id            UUID REFERENCES brands(id) ON DELETE SET NULL,  -- retrieval 격리 (ADR-025 §3)
    promotion_history   JSONB DEFAULT '[]'::jsonb,             -- append-only (ADR-026 §2)
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);


-- ─── 3. approved_knowledge ─────────────────────────────────────────────
-- promoted 단계 진입 시 이동 — retrieval 활성 대상.
CREATE TABLE IF NOT EXISTS approved_knowledge (
    id                     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_candidate_id    UUID REFERENCES candidate_knowledge(id) ON DELETE SET NULL,
    content                TEXT NOT NULL,
    metadata               JSONB DEFAULT '{}'::jsonb,
    embedding              vector(1536),
    auth_user_id           UUID NULL,
    brand_id               UUID REFERENCES brands(id) ON DELETE SET NULL,
    promoted_at            TIMESTAMPTZ DEFAULT NOW()
);


-- ─── 4. b-tree indexes (Phase 5 패턴 계승) ──────────────────────────────
CREATE INDEX IF NOT EXISTS idx_candidate_stage      ON candidate_knowledge(stage);
CREATE INDEX IF NOT EXISTS idx_candidate_brand      ON candidate_knowledge(brand_id);
CREATE INDEX IF NOT EXISTS idx_candidate_auth_user  ON candidate_knowledge(auth_user_id);
CREATE INDEX IF NOT EXISTS idx_approved_brand       ON approved_knowledge(brand_id);
CREATE INDEX IF NOT EXISTS idx_approved_auth_user   ON approved_knowledge(auth_user_id);


-- ─── 5. ivfflat embedding index (pgvector cosine) ──────────────────────
-- ADR-025 §7.2 — lists=100 적정 범위 (10K~100K chunks)
CREATE INDEX IF NOT EXISTS idx_candidate_embedding ON candidate_knowledge
    USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

CREATE INDEX IF NOT EXISTS idx_approved_embedding ON approved_knowledge
    USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);


-- ─── 6. RLS (Phase 5 0003_rls_policy.sql 패턴 계승) ────────────────────
-- 인증 endpoint: auth_user_id = auth.uid()
-- anonymous endpoint: auth_user_id IS NULL 허용 (Phase 1 호환, ADR-021 패턴)
ALTER TABLE candidate_knowledge ENABLE ROW LEVEL SECURITY;
ALTER TABLE approved_knowledge  ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "candidate_owner"        ON candidate_knowledge;
DROP POLICY IF EXISTS "approved_owner_read"    ON approved_knowledge;
DROP POLICY IF EXISTS "approved_owner_write"   ON approved_knowledge;

CREATE POLICY "candidate_owner" ON candidate_knowledge
    FOR ALL
    USING (auth_user_id = auth.uid() OR auth_user_id IS NULL)
    WITH CHECK (auth_user_id = auth.uid() OR auth_user_id IS NULL);

CREATE POLICY "approved_owner_read" ON approved_knowledge
    FOR SELECT
    USING (auth_user_id = auth.uid() OR auth_user_id IS NULL);

CREATE POLICY "approved_owner_write" ON approved_knowledge
    FOR INSERT
    WITH CHECK (auth_user_id = auth.uid() OR auth_user_id IS NULL);


-- ─── 7. comments (ADR cross-reference) ─────────────────────────────────
COMMENT ON TABLE candidate_knowledge IS
    'Phase 7 RAG candidate_knowledge 5단계 (ADR-024/025/026). promotion_history append-only.';
COMMENT ON TABLE approved_knowledge IS
    'Phase 7 RAG approved_knowledge — promoted 단계 (ADR-026). retrieval 활성 대상.';
COMMENT ON COLUMN candidate_knowledge.stage IS
    '5단계 enum (pending → filtered → evaluated → approved → promoted). knowledge_stage type.';
COMMENT ON COLUMN candidate_knowledge.promotion_history IS
    'Append-only transition log (ADR-026 §2). 삭제/수정 금지 — 이력 보존.';
COMMENT ON COLUMN candidate_knowledge.embedding IS
    'pgvector 1536 dim (text-embedding-3-small, ADR-025 §2).';


-- ─── 8. verification ──────────────────────────────────────────────────
-- 본 migration 적용 후 다음 쿼리로 검증 가능:
--
--   SELECT typname FROM pg_type WHERE typname = 'knowledge_stage';
--   SELECT tablename FROM pg_tables WHERE tablename IN ('candidate_knowledge', 'approved_knowledge');
--   SELECT indexname FROM pg_indexes WHERE tablename IN ('candidate_knowledge', 'approved_knowledge');
--   SELECT tablename, policyname FROM pg_policies
--     WHERE tablename IN ('candidate_knowledge', 'approved_knowledge');
--
-- 자동 검증: backend/fastapi/tests/test_rag_promotion.py + test_rag_quality_filter.py + test_rag_eval_rubric.py
