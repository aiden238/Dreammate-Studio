-- Phase 5 Slice 2 — Phase 4.5 + Phase 6 산출물 컬럼 정합 (idempotent ALTER)
--
-- 본 파일은 idempotent (ALTER ... IF NOT EXISTS) 다.
-- 0001_init.sql 의 plans 테이블에 이미 revise_history + recommended_plan_index +
-- critic_evaluation 컬럼이 포함되어 있지만, Phase 4.5/6 호환을 명시적으로 표현하기 위해
-- 별도 migration 으로 분리 보관한다.
--
-- 시나리오:
--   A. 0001 부터 fresh deploy → 본 0002 는 no-op (모든 컬럼 이미 존재).
--   B. Phase 5 이전 schema 가 이미 있는 환경 → 본 0002 가 누락 컬럼 추가.
--
-- 참조:
--   - meta/validations/2026-05-29_phase-5-pre-entry_self.md §V5 (revise_history JSONB)
--   - meta/validations/2026-05-29_phase-5-pre-entry_self.md §V6 (canonical Critic DB 호환)
--   - docs/decisions/phase_4_5_critic_revise_loop.md (Phase 4.5 ADR-016)
--   - docs/decisions/phase_4_5_recommended_plan.md (Phase 4.5 ADR-017)
--   - docs/decisions/phase_6_*.md (Phase 6 ADR-018 canonical)

ALTER TABLE plans
    ADD COLUMN IF NOT EXISTS revise_history          JSONB,
    ADD COLUMN IF NOT EXISTS recommended_plan_index  INTEGER,
    ADD COLUMN IF NOT EXISTS critic_evaluation       JSONB;

-- ─── comments ────────────────────────────────────────────────────────
COMMENT ON COLUMN plans.revise_history IS
    'Phase 4.5 ADR-016 + Phase 6 ReviseAttempt typing (list[list[dict]])';

COMMENT ON COLUMN plans.recommended_plan_index IS
    'Phase 4.5 ADR-017 + Phase 6 Critic best-plan index (0~2)';

COMMENT ON COLUMN plans.critic_evaluation IS
    'Phase 6 ADR-018 canonical: overall_score (0~1) + dimensions (dict[str, float]) + overall_verdict';
