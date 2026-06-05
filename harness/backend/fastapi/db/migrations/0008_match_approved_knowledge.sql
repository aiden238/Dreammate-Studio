-- Phase HIP-008 S2 (2026-06-05) — match_approved_knowledge RPC 함수 정의
--
-- 배경 (meta/audits/2026-06-05.md §B): RAG retrieval(rag/retrieval.py)이 Supabase RPC
--   `match_approved_knowledge` 를 호출하나 **함수가 정의된 적 없어** 운영에서 graceful-empty
--   (try/except → []), 즉 RAG 가 사실상 동작하지 않았다. 본 migration 이 그 함수를 정의해
--   retrieval 을 실제 동작시킨다 (ADR-025 §3 — 1 - (embedding <=> $1) AS similarity).
--
-- 적용 방법 (운영자 — NG11):
--   1. Supabase Dashboard → SQL Editor 에서 본 파일 실행 (0004 적용 후).
--   2. 또는 Supabase CLI: `supabase db push`.
--
-- RPC 계약 (rag/retrieval.py 호출 정합):
--   params: query_embedding(vector 1536) / match_threshold(float, 기본 0.7) /
--           match_count(int, 기본 5=top_k) / filter_brand_id(uuid, NULL=무필터) /
--           filter_auth_user_id(uuid, NULL=무필터)
--   returns: id / content / metadata / brand_id / auth_user_id / similarity
--   (retrieval.py 는 content 로 dedupe + top_k cap. similarity 는 정렬·관측용.)
--
-- 격리 (ADR-025 §3 + 0004 RLS 패턴 계승):
--   - filter_brand_id 제공 시 해당 brand 로 한정.
--   - filter_auth_user_id 제공 시 본인 소유 OR 전역(auth_user_id IS NULL) 만 — RLS
--     "auth_user_id = auth.uid() OR auth_user_id IS NULL" 정합 (익명·전역 지식 공유).
--   - SECURITY INVOKER(기본) — RLS 와 함께 동작. service-key 우회 경로(Phase 17)에서도
--     함수 내 filter 조건으로 격리 유지.
--
-- 참조: docs/contracts/rag_data_contract.md §18, docs/decisions/phase_7_rag_architecture.md (ADR-025),
--       0004_rag_5stage.sql (approved_knowledge 테이블 + ivfflat index).


CREATE OR REPLACE FUNCTION match_approved_knowledge(
    query_embedding     vector(1536),
    match_threshold     float DEFAULT 0.7,
    match_count         int   DEFAULT 5,
    filter_brand_id     uuid  DEFAULT NULL,
    filter_auth_user_id uuid  DEFAULT NULL
)
RETURNS TABLE (
    id            uuid,
    content       text,
    metadata      jsonb,
    brand_id      uuid,
    auth_user_id  uuid,
    similarity    float
)
LANGUAGE sql
STABLE
AS $$
    SELECT
        ak.id,
        ak.content,
        ak.metadata,
        ak.brand_id,
        ak.auth_user_id,
        1 - (ak.embedding <=> query_embedding) AS similarity
    FROM approved_knowledge ak
    WHERE ak.embedding IS NOT NULL
      AND (1 - (ak.embedding <=> query_embedding)) >= match_threshold
      AND (filter_brand_id IS NULL OR ak.brand_id = filter_brand_id)
      AND (
            filter_auth_user_id IS NULL
            OR ak.auth_user_id = filter_auth_user_id
            OR ak.auth_user_id IS NULL          -- 전역/익명 지식은 인증 사용자도 조회 (RLS 정합)
          )
    ORDER BY ak.embedding <=> query_embedding   -- 거리 오름차순 = similarity 내림차순
    LIMIT match_count;
$$;

COMMENT ON FUNCTION match_approved_knowledge IS
    'HIP-008 S2 — RAG retrieval RPC (approved_knowledge cosine top-k). rag/retrieval.py 계약 정합. ADR-025 §3.';


-- ─── verification (적용 후) ────────────────────────────────────────────
--   SELECT proname FROM pg_proc WHERE proname = 'match_approved_knowledge';
--   -- 스모크 (임베딩 1개 있을 때): 빈 결과라도 에러 없이 0행 반환되면 함수 정상.
--   SELECT * FROM match_approved_knowledge(
--     (SELECT embedding FROM approved_knowledge LIMIT 1), 0.0, 3, NULL, NULL);
