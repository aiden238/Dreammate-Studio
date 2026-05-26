-- Phase 1 Slice 5 — 익명 저장용 최소 스키마
--
-- Phase 1 deviation from db_schema.md §3.5 / §4.2 (intentional):
--   - 익명 저장 — user_id NULL allow. Phase 5에서 NOT NULL + auth.users FK + RLS 추가.
--   - brand/domain/series 4계층 미도입 — series_id 외래키 제외.
--   - plan_options 대신 plan_candidates 명칭 (work_plan.md Slice 5 정합).
--
-- 적용 방법:
--   1. Supabase Dashboard → SQL Editor 에서 본 파일 실행.
--   2. 또는 Supabase CLI: `supabase db push` (migration 설정 후).
--
-- Phase 1 Slice 5 acceptance:
--   - video_projects row 생성 확인
--   - plan_candidates row 생성 확인
--   - DB 미연결 상태에서도 응답 200 (meta.project_id=null)

-- ─── video_projects ─────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS video_projects (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NULL,                            -- Phase 5: NOT NULL + REFERENCES auth.users
    request_id  UUID NOT NULL,                        -- envelope.meta.request_id
    input_text  TEXT NOT NULL,
    locale      VARCHAR(10) NOT NULL DEFAULT 'ko-KR',
    phase       INTEGER NOT NULL DEFAULT 1,
    slice       INTEGER NOT NULL DEFAULT 5,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_video_projects_user_id    ON video_projects (user_id);
CREATE INDEX IF NOT EXISTS idx_video_projects_request_id ON video_projects (request_id);
CREATE INDEX IF NOT EXISTS idx_video_projects_created_at ON video_projects (created_at DESC);

-- ─── plan_candidates ────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS plan_candidates (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id      UUID NOT NULL REFERENCES video_projects(id) ON DELETE CASCADE,
    option_index    SMALLINT NOT NULL DEFAULT 0 CHECK (option_index BETWEEN 0 AND 2),
    name            VARCHAR(50) NOT NULL,
    concept         TEXT,
    hook            TEXT,
    approach_label  VARCHAR(20) DEFAULT 'informational',
    -- Slice 4 RAG references + Slice 3 Critic 평가를 통합 저장 (Slice 4 QA §5.3(a))
    -- 구조: { "plan": {...}, "critic_evaluation": {...}, "rag_references": [...] }
    raw_llm_json    JSONB,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_plan_candidates_project_id    ON plan_candidates (project_id);
CREATE INDEX IF NOT EXISTS idx_plan_candidates_raw_llm_json  ON plan_candidates USING GIN (raw_llm_json);

-- ─── 비고 ───────────────────────────────────────────────────────────
-- Phase 5 진입 시 다음 migration (002_*.sql) 으로 추가 예정:
--   - ALTER TABLE video_projects ALTER COLUMN user_id SET NOT NULL;
--   - ALTER TABLE video_projects ADD CONSTRAINT video_projects_user_fk
--       FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE;
--   - RLS policy: row 단위 user_id = auth.uid() 강제
--   - Phase 2+: series_id / domain_id / brand_id 추가 + 4계층 정합.
