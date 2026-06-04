-- Phase 26 S2 — 개인 PKM 출처(provenance) — pkm_entries.source_plan_id 추가
--
-- 무엇을: 개인 PKM(pkm_entries)에 brand_memory_entries(0005 §3) 와 동일한 source_plan_id 를 얹는다.
--   추출 hook(feedback → pkm_entries)이 어떤 plan 의 피드백에서 나온 entry 인지 기록하고,
--   /me/pkm-graph 가 그 출처를 source 노드 + sourced_from 엣지로 펼친다 (브랜드 PKM provenance 대칭).
--
-- ★ 설계 출처: 브랜드 PKM provenance(Phase 21 /me/pkm-graph source 노드)의 **개인 scope 대칭**.
--   brand_memory_entries.source_plan_id (0005 §3 line 66) 를 그대로 미러 — `references plans(id)
--   on delete set null` (plan 삭제 시 출처만 끊고 entry 는 보존).
--
-- additive only: 신규 컬럼 1종 + 인덱스 1종. 기존 pkm_entries(0006) RLS/CHECK/컬럼은 0 변경 →
--   source_plan_id 없는 기존 entry 는 NULL → 그래프 byte-identical (출처 노드/엣지 0).
-- idempotent: ADD COLUMN IF NOT EXISTS + CREATE INDEX IF NOT EXISTS (재실행 안전, 0006 패턴 계승).
--
-- 적용 방법 (★ operator 가 수동 적용 — NG11):
--   1. Supabase Dashboard → SQL Editor 에서 본 파일 실행.
--   2. 또는 Supabase CLI: `supabase db push`.
--
-- 참조:
--   - db/migrations/0005_feedback_selection.sql §3 (brand_memory_entries.source_plan_id — 미러 모델)
--   - db/migrations/0006_pkm_entries.sql (pkm_entries 본체 + RLS)
--   - backend/fastapi/db/repositories/pkm_repo.py (add_entry source_plan_id 배선)
--   - backend/fastapi/routers/me.py (_aggregate_pkm_graph — 개인 PKM source 엣지)


-- ─── 1. pkm_entries.source_plan_id (출처 plan — brand_memory_entries 미러) ──
-- source_plan_id → plans.id. plan 삭제 시 set null (출처만 끊고 entry 보존, 0005 §3 동일).
ALTER TABLE pkm_entries ADD COLUMN IF NOT EXISTS source_plan_id uuid REFERENCES plans(id) ON DELETE SET NULL;
CREATE INDEX IF NOT EXISTS idx_pkm_entries_source ON pkm_entries(source_plan_id);
