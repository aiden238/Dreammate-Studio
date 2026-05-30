# Phase 9.5 — Scope

## 포함 (In-Scope)

### Backend — eval module (신규)

| 파일 | 작업 |
|---|---|
| `backend/fastapi/eval/__init__.py` | **신규** — eval module export |
| `backend/fastapi/eval/golden_set_loader.py` | **신규** — eval/golden_set.md 파싱 → 47 GS 케이스 구조화 (input/expected) |
| `backend/fastapi/eval/runner.py` | **신규** — golden_set 회귀 runner (mock-deterministic + 실 LLM mode flag) + schema/structural 채점 + 임계값 게이트 |
| `backend/fastapi/eval/revise_effect.py` | **신규** — revise loop 개선 효과 metric (mock-based) |
| `backend/fastapi/eval/report.py` | **신규** — regression_results 출력 (eval-run §5 형식) |

### Backend — Critic deprecated 제거 (Slice 4)

| 파일 | 작업 |
|---|---|
| `backend/fastapi/agents/critic.py` | **수정** — select_best_plan_index deprecated fallback(overall_score_avg/scores/eight_dim_scores branch + DeprecationWarning) 제거, canonical-only. normalize_to_canonical 정리 (run_critic 0–5 출력 불변 — P-007 contract). |
| `backend/fastapi/schemas/output.py` | **수정** — CriticEvaluation Optional deprecated 필드(overall_score_avg/scores/eight_dim_scores) 제거 (canonical overall_score + dimensions만) |

### Tests

| 파일 | 작업 |
|---|---|
| `tests/test_eval_runner.py` | **신규** — golden_set 로더 + mock 회귀 + 임계값 게이트 |
| `tests/test_revise_effect.py` | **신규** — revise effect metric |
| `tests/test_critic.py` | **수정 (의도된 delta)** — Phase 6 Slice 2 추가 deprecated-fallback `pytest.warns(DeprecationWarning)` 케이스 제거/canonical로 갱신 |
| `tests/test_prompt_registry_consistency.py` | **수정 (의도된 delta, 필요 시)** — normalize_to_canonical deprecated 관련 케이스 정합 |
| 그 외 baseline tests | **수정 X** (run_critic 0–5 출력 불변 → test_critic의 run_critic 케이스 보존) |

### Contracts / Skills

| 파일 | 작업 |
|---|---|
| `docs/contracts/output_schema.md` | **수정** (contract-change) — §9 CriticEvaluation deprecated 필드 제거 |
| `docs/contracts/agent_io_contract.md` | **수정** (contract-change) — §5 Critic deprecated 제거 + canonical-only |
| `docs/contracts/db_schema.md` | **수정** — critic_evaluation JSONB deprecated 필드 제거 note |
| `eval/golden_set.md` | **참조 + 선택 수정** — executable 케이스 format 정합 (contract-change 시) |
| `.claude/skills/eval-run/SKILL.md` + `eval-design/SKILL.md` | **참조** (첫 정식 트리거 — 절차 따름, Skill 파일 수정은 최소) |

### Frontend

| 파일 | 작업 |
|---|---|
| 모두 | **수정 X** (eval은 backend) |
| `apps/web/lib/types.ts` | **확인** — CriticEvaluation frontend mirror에 deprecated 필드 있으면 정합 (Phase 6 Slice 3에서 deprecated non-optional 유지했음 — page.tsx 회귀 주의) |
| `PlanCard.tsx` / `component_map.md` | **수정 절대 금지** ★ |

### Meta / Scripts / Docs

| 파일 | 작업 |
|---|---|
| `meta/validations/2026-05-31_phase-9.5-pre-entry_self.md` + external | **신규** |
| `docs/decisions/phase_9_5_eval_run_harness.md` | **신규** — ADR-033 |
| `docs/decisions/phase_9_5_critic_deprecated_removal.md` | **신규** — ADR-034 |
| `eval/regression_results/phase-9.5_{date}.md` | **신규** — 첫 eval-run 결과 |
| `scripts/eval_run.ps1` | **신규** — eval runner 래퍼 |
| `scripts/smoke_test_phase_9_5.ps1` | **신규** — 16 체크 |
| `scripts/scenario_simulation.ps1` | **수정** — v6 (S26~S30) |
| `meta/retrospectives/phase-9.5.md` / `patterns.md` / `skill_usage_log.md` | **수정/신규** |
| `PROJECT_STATE / PHASE_REGISTRY / 00_START_HERE / README` | **수정** |

## 예상 파일 변경 수
- **신규**: ~16 (eval module 5 + tests 2 + ADR 2 + validations 2 + regression_result + eval_run.ps1 + smoke + retrospective)
- **수정**: ~12 (critic.py + schemas/output + contracts 3 + test_critic delta + types 확인 + scenario_sim + patterns + skill_usage + state docs)
- **금지 (0줄)**: 2 (PlanCard.tsx, component_map.md)

## 제외 → `non_goals.md`
