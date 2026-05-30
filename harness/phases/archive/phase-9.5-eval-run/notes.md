# Phase 9.5 — Notes

## Entry (2026-05-31)

- phase-start v1.3.0 §6 4점검 PASS (C1~C10, U1~U5)
- audit_naming PASS 0 drift
- Phase 9 baseline 유지 (pytest 293 + smoke 15 + scenario_sim v5 25 + P-X1 42 + PlanCard 30 + component_map 40)
- 5 Slice 모두 sub-agent dispatch

### 사용자 결정 (2026-05-31) — 반드시 반영
- **Critic deprecated 0–5: Full 제거** (select_best_plan_index fallback + DeprecationWarning + CriticEvaluation Optional deprecated 필드). run_critic 0–5 출력 불변 (P-007 prompt contract, NG3). eval 검증 후 제거 (순서).
- **eval-run: Mock-deterministic primary** + 실 LLM mode 문서. **RAG eval_rubric Phase 10+ 이관** (NG1).

### Gap 분석 (entry 시점)
- golden_set.md 47 GS 케이스 spec만 (runner 없음). eval-run/eval-design Skill 미사용.
- ★ run_critic = LLM-facing 0–5 (P-007 prompt, 제거 대상 아님). normalize_to_canonical = 0–5→0–1. select_best_plan_index = deprecated fallback(overall_score_avg/scores/eight_dim_scores + DeprecationWarning, Phase 6 Slice 2 추가) → Phase 9 wiring으로 canonical 항상 존재 → dead code → 제거 대상.
- CriticEvaluation Optional deprecated 필드 → schema 제거 대상.
- revise effect Phase 4.5부터 미측정 (D6).
- backend/fastapi/eval/ module 없음 (신규).

### 핵심 제약 (★)
- 제거 순서: Slice 2~3 eval runner 구축 → eval로 canonical-only 품질 검증 → Slice 4 제거 (회귀 통과 후)
- 의도된 baseline delta: test_critic의 select_best_plan_index deprecated-fallback pytest.warns 케이스만 (Phase 8 Slice 4 패턴). run_critic 0–5 케이스 보존.
- mock-deterministic eval (CI 가능, 비용 0). 실 LLM은 mode flag + 문서.

### Skill 첫 정식 트리거
- eval-design (Slice 1) + eval-run (Slice 2~3)

## Slice 1~5 (작업 시 갱신)

### Slice 1 — Pre-Entry ✅ (2026-05-31, sub-agent)

- **validations**: `meta/validations/2026-05-31_phase-9.5-pre-entry_self.md` (V1~V7 PASS — formal 일곱 번째) + external placeholder.
  - V1 eval mock-deterministic / V2 golden_set markdown→구조화 파싱 / V3 revise effect metric(mock) / V4 deprecated 제거 경계(run_critic 0–5 불변 P-007) / V5 제거 순서(eval→검증→제거) / V6 임계값 게이트 / V7 frontend types CriticEvaluation 정합.
- **eval-design Skill ★ 첫 정식 트리거** — golden_set executable format(loader GS- prefix 필터, 단일 출처) + 채점 차원(schema 준수 100% + structural, 실 LLM 8차원은 mode flag) + revise effect metric(attempt별 canonical overall_score 0–1 delta) + 임계값 게이트(schema 100% / 점수 ±0.3 / 광고 >5% fail / 차단 단어 >0% fail) → ADR-033 §eval-design 통합.
- **ADR-033** (`docs/decisions/phase_9_5_eval_run_harness.md`) — eval-run harness mock-deterministic primary + 실 LLM mode flag + regression_results + 임계값 + §eval-design.
- **ADR-034** (`docs/decisions/phase_9_5_critic_deprecated_removal.md`) — Critic deprecated 0–5 Full 제거 (select_best_plan_index fallback + CriticEvaluation Optional 0–5 필드, run_critic 0–5 불변 NG3, normalize_to_canonical 유지, eval 검증 순서, 의도 delta = test_critic deprecated-fallback 6 케이스, frontend types V7).
- **skill_usage_log** — eval-design 0→1 (★ 첫 정식) + multi-llm-validation 7(formal 일곱째) + phase-start 12 + qa-check 37 + Phase 9.5 요약.
- **PROJECT_STATE** — active 전환 + phase_9_5_* 키 + total_commits 83→84.

#### Slice 1 발견 (★ 후속 Slice 주의)
- **golden_set 케이스 수 정정**: entry plan 일부 문서가 "47 케이스" 로 기재되어 있으나 현 `eval/golden_set.md` v1.0.0 §2 는 **GS-001~GS-011 (11 케이스)** 만 정의 (§0/§3 명시). Slice 2 loader 는 실제 11 케이스를 단일 출처로 파싱. 케이스 확대(11 → 47+)는 NG10 (Phase 10+).
- **frontend CriticEvaluation non-optional (V7 — Slice 4 주의)**: `apps/web/lib/types.ts` line 135~147 — `scores`/`overall_score_avg` 가 **non-optional** (Phase 6 Slice 3, "page.tsx 가 .toFixed/.map 직접 호출" + "Phase 9+ deprecated 제거 시 page.tsx 와 함께 동시 마이그레이션"). Slice 4 에서 page.tsx 가 critic 0–5 를 렌더하는지 확인 → 렌더 시 canonical(0–1) 전환 (page.tsx inline wrapper — PlanCard·component_map 0줄) + types non-optional 제거 + tsc/build 회귀 0.
- **select_best_plan_index 참조 (Slice 4)**: deprecated fallback(critic.py:372~401) 제거 대상 + canonical 우선 유지. 참조 파일 5종 (routers/plans.py / orchestration/moa_orchestrator.py / tests/test_critic.py / agents/critic.py / tests/test_schema_stress.py) — canonical 입력은 불변, deprecated 입력 케이스만 의도 delta.
- **test_critic deprecated-fallback pytest.warns 케이스 6개 (의도 delta)**: `_returns_highest_score` / `_tie_breaking_prefers_lower_index` / `_all_invalid_returns_none` / `_uses_scores_dimension_fallback` / `_skips_invalid_uses_remaining` / `_eight_dim_scores_deprecated_warns`. canonical 케이스 3 + run_critic 케이스 보존.
