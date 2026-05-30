# Phase 9 — Notes

## Entry (2026-05-29)

- phase-start v1.3.0 §6 4점검 PASS (C1~C11, U1~U6)
- audit_naming PASS 0 drift
- Phase 8 baseline 유지 (pytest 249 + smoke 14 + scenario_sim v4 20 + P-X1 36 + PlanCard 24 + component_map 34)
- 6 Slice 모두 sub-agent dispatch

### 사용자 결정 (2026-05-29) — 반드시 반영
- **Brand Memory: 준비만** (ADR + schema + 피드백 적재) — P-AUX-2 agent 미구현, 자동 추출 Phase 10+ (사용자 결정 5 누적 confirm)
- **Frontend: 피드백 UI 포함** (wrapper) — 선택/반려 page.tsx inline, PlanCard·component_map 무수정
- **normalize_to_canonical: Phase 9 연결** — critic step canonical 0–1 live, deprecated 0–5 병행 회귀 0 (Phase 8 개선 §1)

### Gap 분석 (entry 시점)
- db_schema.md는 feedback_events/selected_plans/discovery_choices/brand_memory_entries **정의만** (0001~0004만 migrated). 피드백 테이블 미구현.
- ★ 실 구현은 `plans` 테이블 + plan_candidates JSONB + option_index(0–2). db_schema idealized plan_options(selected_plans→plan_options.option_id)는 **Phase 11+ 4계층 full linkage (NG2)**. Phase 9 selection/feedback은 **실 plans 테이블 정합** (plan_id + selected_option_index).
- P-AUX-2 brand_memory_extractor prompt만 registry 존재, agent 미구현.
- normalize_to_canonical helper(Phase 8) 존재, pipeline 미연결.

### 핵심 제약
- normalize wiring은 critic_evaluation canonical 추가 (deprecated 0–5 병행) — schemas/output.py 불변, 의도된 baseline delta만 최소 갱신 (Phase 8 Slice 4 패턴)
- 피드백 UI는 page.tsx inline (신규 component 안 만듦 → component_map 0줄)

### Skill 정식 트리거
- security-review 두 번째 정식 (Slice 1 — 피드백 PII)

## Slice 1~6 (작업 시 갱신)

### Slice 1 — Pre-Entry ✅ (sub-agent, 2026-05-29)

- `meta/validations/2026-05-29_phase-9-pre-entry_self.md` — formal **여섯 번째** self V1~V7 PASS (selection/feedback 실 plans 정합 / normalize wiring 회귀 0 / Brand Memory 준비 경계 / 피드백 reason PII / repo graceful / 피드백 UI wrapper / feedback→candidate 적재)
- `meta/validations/2026-05-29_phase-9-pre-entry_external.md` — placeholder (사용자 외부 진행 권장)
- `meta/security_reviews/2026-05-29_phase-9-feedback-pii.md` — **security-review 두 번째 정식 트리거** (T1 피드백 reason PII 저장 전 마스킹 / T2 reject 사유 / T3 feedback_events·selected_plans RLS / T4 GET 권한 / T5 candidate 적재 PII / T6 SQL injection + 영역 1~10: 4 PARTIAL → Slice 2~4 후 PASS)
- ADR-030 (`phase_9_feedback_selection.md`) — 실 plans 테이블 정합 (plan_id + selected_option_index 0–2 + plan_candidates JSONB, idealized plan_options Phase 11+ NG2) + graceful PlansRepo 패턴
- ADR-031 (`phase_9_brand_memory_prep.md`) — Brand Memory 준비만 (schema + BrandMemoryRepo + feedback→candidate 적재 + P-AUX-2 설계 명세), agent 미구현 Phase 10+ (NG1), 적재 pending NG12
- ADR-032 (`phase_9_critic_canonical_wiring.md`) — normalize_to_canonical wiring (critic step canonical 0–1 + dimensions 추가, deprecated 0–5 병행, schemas/output.py 불변, 의도 delta 최소)
- `meta/skill_usage_log.md` — phase-start 11 / qa-check 36 / multi-llm-validation 7 (6 formal) / security-review 3 (Phase 5 2 + Phase 9 1) + Phase 9 entry 요약 row + footer
- `PROJECT_STATE.md` — Phase 9 active 전환 + migration_progress (current_sprint phase-9-slice-1 + phase_9_* 키 + total_commits 77)
- **코드 변경 0** (Slice 1 문서) — PlanCard·component_map 0줄 / forbidden 0

다음: Slice 2 sub-agent — Schema 0005 (selected_plans + feedback_events + brand_memory_entries + RLS) + Repo 3종 graceful + contract-change (db_schema.md).
