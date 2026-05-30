# Phase 9.5 — Closing Notes (eval-run 정식화 + Critic deprecated 0–5 Full 제거)

> 종료일: 2026-05-31
> 결과: ✅ A1~A10 10/10 + M1~M4 4/4 PASS
> 트리거: phase-complete v1.2.0 §1.6 여덟 번째 자동 게이트 + §7 회고 자동 호출

---

## 산출물

### eval module (backend/fastapi/eval/) — 5 파일 신규
- `__init__.py` — eval module export
- `golden_set_loader.py` — `eval/golden_set.md` GS-001~GS-011 (11 케이스, 단일 출처) → [id, input, expected_properties] 구조화 파싱
- `runner.py` — mock-deterministic 회귀 (각 케이스 → mock pipeline → schema 준수 100% + structural 채점 + 비교 모드 + 실 LLM mode flag) + revise effect 통합
- `revise_effect.py` — revise loop 전/후 품질 delta (attempt별 canonical overall_score 0–1 변화 — Phase 4.5 D6 해소)
- `report.py` — regression_results §5 형식 출력

### 스크립트 + 테스트
- `scripts/eval_run.ps1` — runner 래퍼 → `eval/regression_results/phase-9.5_*.md` (gate=pass → exit 0)
- `scripts/smoke_test_phase_9_5.ps1` — 16 체크 (Phase 9 15 baseline + eval-run 1)
- `scripts/scenario_simulation.ps1` v6 — S26~S30 추가 (30/30, P-X2 여덟 번째)
- `backend/fastapi/tests/test_eval_runner.py` — loader + mock 회귀 + 임계값 게이트 §6
- `backend/fastapi/tests/test_revise_effect.py` — revise effect metric
- `eval/regression_results/phase-9.5_{baseline,pre-removal,post-removal}.md` — 회귀 결과 누적

### Critic deprecated 0–5 Full 제거
- `backend/fastapi/agents/critic.py` — select_best_plan_index deprecated fallback(overall_score_avg/scores/eight_dim_scores + DeprecationWarning) 제거 → canonical(overall_score → dimensions) 2 경로만. **run_critic 0–5 출력 + normalize_to_canonical(0–5→0–1) 불변** (P-007 NG3)
- `backend/fastapi/schemas/output.py` — CriticEvaluation Optional deprecated 0–5 필드(scores/overall_score_avg) 제거 (Pydantic extra='ignore'로 verdict 0–5 키 무시 → 회귀 0)
- `backend/fastapi/routers/generate.py` — Phase 1 endpoint canonical wiring 보강 (★ deviation — 아래)
- `apps/web/lib/types.ts` — CriticEvaluation canonical 전환 (deprecated 0–5 제거, page.tsx canonical 렌더 — PlanCard·component_map 0줄)
- `backend/fastapi/tests/test_critic.py` — 의도 delta (deprecated-fallback pytest.warns 케이스 갱신/제거, canonical 케이스 + run_critic 0–5 케이스 보존)

### contract + ADR
- ADR-033 (`docs/decisions/phase_9_5_eval_run_harness.md`) — eval-run harness mock-deterministic primary + 실 LLM mode flag + regression_results + 임계값 + §eval-design
- ADR-034 (`docs/decisions/phase_9_5_critic_deprecated_removal.md`) — Critic deprecated 0–5 Full 제거
- CC-005 — output_schema §9 (canonical-only) + agent_io_contract §5 (Critic canonical-only, run_critic 0–5 불변) + db_schema critic_evaluation deprecated 제거 정합

### meta
- `meta/validations/2026-05-31_phase-9.5-pre-entry_self.md` (V1~V7 PASS — formal 일곱 번째) + external placeholder
- `meta/retrospectives/phase-9.5.md` (회고)
- `meta/patterns.md` (P-X1-EFFECT-001 47연속 + P-EVAL-HARNESS-001 신규 + P-DEPRECATED-REMOVAL-001 신규 + P-VALIDATION-FORMAL-001 일곱 번째)
- `meta/skill_usage_log.md` (eval-design + eval-run 첫 정식 + contract-change CC-005)

---

## 최종 baseline 표

| 지표 | Phase 9 | Phase 9.5 final |
|---|---|---|
| pytest | 293/293 | **339/339** (+46 신규) |
| smoke | 15/15 | **16/16** (15 PASS + 1 WARN intended) |
| scenario_simulation | v5 25/25 | **v6 30/30** (P-X2 여덟 번째) |
| eval gate (eval_run.ps1) | — | **PASS** (schema 1.0 / pass 1.0 / revise mean_delta 0.092 / improved 0.6 / regressed 0.2) |
| schema_stress_test | 5/5 | 5/5 (CriticEvaluation deprecated 제거 정합) |
| audit_naming | 0 drift | **0 drift** |
| audit_page_component | 2 intended WARN | **2 intended WARN** (Phase 5 baseline 계승) |
| Critic deprecated warnings | 16 | **0** |
| PlanCard.tsx 0줄 | 30연속 | **35연속** |
| component_map.md 0줄 | 40연속 | **45연속** |
| P-X1 streak | 42 | **47** (Phase 9.5 Slice 1~5: 5) |
| Total commits (Phase 9.5) | — | 5 (190822e + bfac0c4 + 8a18276 + 864e83e + final) |

---

## ★ generate.py canonical wiring deviation (실측 발견)

Slice 4 deprecated 제거 작업 중 **Phase 1 legacy `/api/v1/generate` endpoint가 critic verdict를 normalize_to_canonical 경유 없이 직접 노출**하던 누락 발견 → `routers/generate.py` canonical wiring 보강 (Phase 9 moa_orchestrator wiring 패턴 정합). deprecated 제거 후 Phase 1 endpoint에서도 canonical 일관 노출 + 회귀 방지.

- **근본 원인**: Phase 9 normalize wiring은 moa_orchestrator critic step에만 추가 — Phase 1 legacy /generate는 별도 경로라 미커버. 점진 wiring(helper → 단일 지점)은 다른 consumer를 자동 커버하지 않음.
- **수용**: deprecated 제거 정합 보강, 회귀 방지. eval 제거 전/후 동일 입증.
- **★ 향후 필수**: **신규 critic consumer는 normalize_to_canonical 경유 필수** (canonical 단일 표준 보장). P-CANONICAL-WIRING-001 + P-DEPRECATED-REMOVAL-001 §6 기록.

---

## 다음 phase 옵션 (사용자 결정 대기)

### A. Phase 10 — MVP 통합 테스트 (6~8h)
- MVP 전체 end-to-end 검증 (Discovery + Quick → 3-plan → Critic revise (canonical-only) → save → select → feedback → SSE progress)
- Phase 1~9.5 누적 baseline 통합 회귀 + eval-run golden_set 회귀 baseline 활용
- P-AUX-2 brand_memory_extractor agent 실 구현 (Phase 9 개선 제안 §1 — 데이터 누적 후)
- 배포 테스트 게이트 A~G 준비

### B. 다른 우선순위 (Phase 11+)
- 4계층 full linkage (plan_options/video_projects, Phase 9 개선 제안 §3, 누적 2회)
- 사용자 데이터 자동 promotion (rag-update Skill 두 번째, Phase 9 개선 제안 §5)
- SSE full async worker / prompt A/B 실행 인프라 / Supabase SQL function 정의 / cost-review Skill 정식화

---

## 운영 권장 (Phase 9.5 deferred)

1. **실 LLM eval mode 운영 활성** (Phase 10+): mock-deterministic primary로 구축 — 실 LLM 8차원 eval은 mode flag + 문서만. 비용/예산 확보 후 운영 (cost-review 연계).
2. **RAG eval_rubric → golden_set 정식화** (Phase 10+, NG1): Phase 7 간이 eval_rubric(relevance/clarity/safety 3 dim) → golden_set 기반 정식 rubric. Phase 9.5 eval harness 흡수.
3. **golden_set 11 → 확대** (Phase 10+, NG10): GS-001~GS-011 (11 케이스) → 도메인/엣지 케이스 확대 (47+). eval-design Skill 두 번째 트리거 baseline.
4. **신규 critic consumer normalize_to_canonical 경유 필수** (Phase 10+ 정합): generate.py 보강으로 현 consumer는 모두 canonical — 향후 신규 consumer는 normalize 경유 강제.
