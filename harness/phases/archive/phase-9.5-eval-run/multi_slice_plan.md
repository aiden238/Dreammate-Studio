# Phase 9.5 — Multi-Slice Plan

> 5 Slice 모두 sub-agent dispatch, sequential. 총 6~10h.
> ★ 순서 핵심: eval runner(2~3) → eval 검증 → deprecated 제거(4)

---

## Wave 구조
```
Wave 1: Slice 1 [Pre-Entry — validations + eval-design Skill 첫 정식 + ADR-033/034]
  ↓
Wave 2: Slice 2 [eval-run golden_set runner — loader + mock 회귀 + 채점 + 임계값 + report]
  ↓
Wave 3: Slice 3 [revise effect eval + eval-run Skill 실행 (canonical-only 품질 baseline)]
  ↓
Wave 4: Slice 4 [Critic deprecated 0–5 Full 제거 — eval 검증 후 + contract-change]
  ↓
Wave 5: Slice 5 [Close]
```

---

## Slice 1 — Pre-Entry (1~2h)
1. `meta/validations/2026-05-31_phase-9.5-pre-entry_self.md` V1~V7 (eval mock-deterministic / golden_set 파싱 / revise effect metric / deprecated 제거 경계(run_critic 불변) / 제거 순서(eval→제거) / 임계값 게이트 / frontend types 정합)
2. external placeholder
3. **eval-design Skill 첫 정식** — golden_set executable format 설계 (markdown 47 케이스 → 구조화) + revise effect metric 정의 + 채점 차원(schema 준수 + structural, 실 LLM 8차원은 mode). 결과 ADR-033 통합.
4. ADR-033 (eval-run harness — mock-deterministic + 실 LLM mode + 임계값 게이트 + regression_results) + ADR-034 (Critic deprecated 0–5 Full 제거 — fallback + schema, run_critic 불변, eval 검증 순서)
5. skill_usage_log + PROJECT_STATE + entry commit
- forbidden: backend/*, apps/web/*, contracts, scripts, skills, 이전 ADR, archive

## Slice 2 — eval-run golden_set runner (2~3h)
1. `eval/__init__.py` + `eval/golden_set_loader.py` (eval/golden_set.md → 47 GS 케이스 [id, input, expected_properties])
2. `eval/runner.py` (mock-deterministic 회귀: 각 케이스 → mock pipeline → schema 준수 + structural 채점 + 비교 모드 + 실 LLM mode flag)
3. `eval/report.py` (regression_results §5 형식 출력)
4. `scripts/eval_run.ps1` (runner 래퍼 → eval/regression_results/phase-9.5_{date}.md)
5. `tests/test_eval_runner.py` (loader + mock 회귀 + 임계값 게이트 §6)
6. eval-run Skill 첫 정식 (golden_set 회귀 실행 — mock)
- editable: eval/{__init__,golden_set_loader,runner,report}, scripts/eval_run.ps1, eval/regression_results/phase-9.5_*, tests/test_eval_runner
- forbidden: agents, schemas, orchestration, routers, db, apps/web, contracts(Slice 4), 이전 ADR, baseline test

## Slice 3 — revise effect eval (1.5~2h)
1. `eval/revise_effect.py` (revise loop 전/후 품질 delta metric — mock-based: revise attempt별 canonical score 변화)
2. `eval/runner.py` (소폭) — revise effect 통합
3. `tests/test_revise_effect.py`
4. eval-run으로 canonical-only 품질 baseline 기록 (Slice 4 제거 검증 기준)
- editable: eval/revise_effect, eval/runner(소폭), tests/test_revise_effect, eval/regression_results(갱신)
- forbidden: Slice 2 loader/report 코어(소폭만), agents/schemas/orchestration, apps/web, contracts

## Slice 4 — Critic deprecated 0–5 Full 제거 (1.5~2.5h) ★ delicate
1. **eval 검증** — Slice 2~3 runner로 canonical-only 품질 baseline 확인 (제거 전 회귀 기준)
2. `backend/fastapi/agents/critic.py`: select_best_plan_index deprecated fallback(overall_score_avg/scores/eight_dim_scores branch + DeprecationWarning) 제거 → canonical-only. **run_critic 0–5 출력 불변** (P-007 contract). normalize_to_canonical 유지 (0–5→0–1 변환).
3. `backend/fastapi/schemas/output.py`: CriticEvaluation Optional deprecated 필드(overall_score_avg/scores/eight_dim_scores) 제거 (canonical overall_score + dimensions만). Pydantic extra='ignore'로 verdict의 0–5 키 무시 (회귀 0).
4. `apps/web/lib/types.ts` (필요 시): CriticEvaluation frontend deprecated 정합 (page.tsx 회귀 0 — tsc/build 확인)
5. **contract-change** — output_schema §9 + agent_io_contract §5 + db_schema critic_evaluation deprecated 제거 (CC-005)
6. `tests/test_critic.py` (의도 delta) — select_best_plan_index deprecated-fallback `pytest.warns` 케이스 canonical로 갱신/제거. run_critic 0–5 케이스 보존.
7. `tests/test_prompt_registry_consistency.py` (의도 delta, 필요 시)
8. agent-io-check (canonical-only 정합) + eval-run 회귀 (제거 후 품질 동일 확인)
- editable: critic.py, schemas/output.py, apps/web/lib/types.ts(필요시), output_schema/agent_io_contract/db_schema, test_critic(의도 delta)/test_prompt_registry_consistency(의도 delta), tests
- forbidden: ★ run_critic 0–5 로직(NG3), orchestration/routers/db/middleware, agents(critic 외), 의도 delta 외 baseline test, PlanCard ★ component_map ★, 이전 ADR
- ★ eval 검증 후 제거 (순서) + 의도 delta 최소

## Slice 5 — Close (1~1.5h)
1. `scripts/smoke_test_phase_9_5.ps1` (16 체크: Phase 9 15 + eval-run 1)
2. `scripts/scenario_simulation.ps1` v6 (S26~S30: eval runner / revise effect / deprecated 제거 / canonical-only / regression_results)
3. audit×2 + agent-io-check + design-review(frontend 변경 0)
4. `meta/retrospectives/phase-9.5.md` + patterns(P-X1 47 + P-EVAL-HARNESS-001 신규 + P-DEPRECATED-REMOVAL-001 신규) + skill_usage_log(eval-design + eval-run 첫 정식)
5. phase-complete v1.2.0 (P-X2 여덟 번째)
6. archive 이동 + closing_notes (Phase 10 통합 / Phase 11+ 권장)
7. state docs
- forbidden: backend/*, apps/web/*, contracts, 이전 ADR(033/034 보존), scripts/audit_*+schema_stress+smoke_4_5~9, skills, baseline test

---

## 충돌 매트릭스
| Slice | eval module | critic.py | schemas | tests | contracts | apps/web | scripts | meta | state |
|---|---|---|---|---|---|---|---|---|---|
| 1 | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ valid+ADR | ✅ entry |
| 2 | ✅ loader+runner+report | ❌ | ❌ | ✅ test_eval_runner | ❌ | ❌ | ✅ eval_run.ps1 | ❌ | ❌ |
| 3 | ✅ revise_effect | ❌ | ❌ | ✅ test_revise_effect | ❌ | ❌ | ❌ | ❌ | ❌ |
| 4 | ❌ | ✅ deprecated 제거 | ✅ CriticEvaluation | ✅ 의도 delta | ✅ CC-005 | ✅ types(필요시) | ❌ | ❌ | ❌ |
| 5 | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ smoke+scenario v6 | ✅ retrospective+patterns | ✅ all |

Sequential 충돌 0.

---

## 누적 P-X1 streak
| Phase | streak |
|---|---|
| Phase 9 | 42 |
| Phase 9.5 | **5 (목표)** |
| **누적** | **47** |

## 시간 추정
| Slice | 시간 | 누적 |
|---|---|---|
| 1 | 1~2h | 1~2h |
| 2 | 2~3h | 3~5h |
| 3 | 1.5~2h | 4.5~7h |
| 4 | 1.5~2.5h | 6~9.5h |
| 5 | 1~1.5h | **7~11h** |
