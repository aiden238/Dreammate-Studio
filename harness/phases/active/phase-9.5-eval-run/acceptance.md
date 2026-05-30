# Phase 9.5 — Acceptance (A1~A10 + M1~M4)

## A1~A10

| ID | 항목 | 검증 | Slice |
|---|---|---|---|
| **A1** | golden_set 로더 — eval/golden_set.md → 47 GS 케이스 구조화 | pytest `test_eval_runner.py::test_loader` | 2 |
| **A2** | eval-run runner — mock-deterministic 회귀 + schema/structural 채점 + regression_results 출력 | pytest `test_eval_runner.py` + `eval/regression_results/phase-9.5_*.md` | 2 |
| **A3** | 임계값 게이트 — schema 준수 100% / 점수 변화 ±0.3 / 광고·차단 단어 (eval-run §6) | pytest `test_eval_runner.py::test_threshold_gate` | 2 |
| **A4** | revise effect eval — revise loop 개선 효과 metric | pytest `test_revise_effect.py` | 3 |
| **A5** | eval-design + eval-run Skill 첫 정식 + 실 LLM mode 문서 | ADR-033 + `scripts/eval_run.ps1` + regression_results | 1~3 |
| **A6** | **Critic deprecated 0–5 Full 제거** — select_best_plan_index fallback + CriticEvaluation Optional deprecated 필드 | critic.py + schemas/output.py + agent-io-check | 4 |
| **A7** | contract-change — output_schema + agent_io_contract + db_schema deprecated 제거 정합 | contract-change CC-005 | 4 |
| **A8** | **PlanCard.tsx 0줄 + component_map.md 0줄** | git diff | 5 |
| **A9** | audit_naming 0 drift + audit_page_component 2 intended WARN | scripts | 5 |
| **A10** | smoke_test_phase_9_5 16/16 + scenario_sim v6 30/30 | scripts | 5 |

## M1~M4 (메타)

| ID | 항목 |
|---|---|
| **M1** | multi-llm-validation formal self 일곱 번째 + external placeholder |
| **M2** | **eval-design + eval-run Skill ★ 둘 다 첫 정식 트리거** |
| **M3** | contract-change Skill (deprecated 0–5 제거 — CC-005) |
| **M4** | P-X1 §SELF-VERIFICATION **47연속 PASS** (Slice 1~5) |

## 회귀 baseline (Phase 9 → Phase 9.5)

| 지표 | Phase 9 | Phase 9.5 목표 |
|---|---|---|
| pytest | 293/293 | 305~315 (+12~22 eval, test_critic 의도 delta) |
| smoke | 15/15 | **16/16** (eval-run 1 추가) |
| scenario_simulation | v5 25/25 | **v6 30/30** (+5 eval/deprecated) |
| schema_stress_test | 5/5 | 5/5 유지 (CriticEvaluation deprecated 제거 정합) |
| audit_naming | 0 drift | 0 drift |
| audit_page_component | 2 intended WARN | 2 intended WARN |
| component_map.md 0줄 | 40 | **유지** (+5 → 45) |
| PlanCard.tsx 0줄 | 30 | **유지** (+5 → 35) |
| P-X1 streak | 42 | **47** |
| Critic deprecated warnings | 16 | **0** (deprecated 제거) |

## qa-check 카테고리 (Phase 9.5 final 예상)
- 1 제품/범위 PASS / 2 AI 구조 **PASS** (Critic canonical 단일화) / 3 RAG skip (eval_rubric Phase 10+) / 4 프론트 PASS (변경 0) / **5 평가/품질 PASS** (★ 첫 본격 — golden_set runner) / 6 메타 PASS / 7 컨텍스트 / 8 큰 결정 **PASS** (eval-design + contract-change + multi-llm) / 9 Phase 운영 PASS / 10 보안 skip / 11 비용 skip
- **예상**: 8 PASS / 3 skip.
