# Phase 9.5 — Dependencies

## 이전 Phase 의존성

| Phase | 상태 | 의존 항목 |
|---|---|---|
| Phase 4.5 | ✅ done | revise loop (revise effect eval 대상, D6) |
| Phase 6 | ✅ done | Critic canonical (ADR-018) + select_best_plan_index deprecated fallback (Phase 6 Slice 2 — 제거 대상) + test_critic DeprecationWarning 케이스 |
| Phase 7 | ✅ done | RAG eval_rubric 간이 (NG1 — Phase 10+ 이관) |
| Phase 8 | ✅ done | normalize_to_canonical helper + orchestrator critic step |
| Phase 9 | ✅ done | **normalize wiring (canonical 항상 populated → deprecated fallback dead)** + critic_evaluation canonical 0–1 live |

**모두 done** — Phase 9 wiring이 deprecated 제거의 전제 (canonical-only 가능).

## Contract 참조 + 수정

| Contract | 사용 |
|---|---|
| `eval/golden_set.md` | **참조** (47 GS 케이스 — runner 입력) + 선택 수정 (executable format) |
| `eval/video_planning_eval.md` | **참조** (8차원 채점) |
| `eval/regression_eval.md` + `eval/regression_results/` | **참조 + 출력** |
| `docs/contracts/output_schema.md` | **수정 대상** (Slice 4 — CriticEvaluation deprecated 제거) |
| `docs/contracts/agent_io_contract.md` | **수정 대상** (Slice 4 — Critic canonical-only) |
| `docs/contracts/db_schema.md` | **수정** (critic_evaluation JSONB deprecated note) |

## Skill 의존성

| Skill | 호출 시점 | 필수 |
|---|---|---|
| `phase-start` v1.3.0 | entry | 필수 |
| `multi-llm-validation` | Slice 1 | 필수 |
| **`eval-design`** | **Slice 1 ★ 첫 정식** (golden_set executable format + revise effect metric 설계) | **필수** |
| **`eval-run`** | **Slice 2~3 ★ 첫 정식** (golden_set 회귀 + revise effect 실행) | **필수** |
| `contract-change` | Slice 4 (output_schema + agent_io_contract — deprecated 제거) | 필수 |
| `agent-io-check` | Slice 4 (canonical-only 정합) + Slice 5 | 필수 |
| `qa-check` v1.2.0 | Slice 1 + 5 | 필수 |
| `harness-audit` | Slice 1 + 5 | 필수 |
| `design-review` | Slice 5 (frontend 변경 0 회귀) | 필수 |
| `meta-retrospective` | Slice 5 | 필수 |
| `phase-complete` v1.2.0 | Slice 5 (P-X2 여덟 번째) | 필수 |

## 환경 / 외부
- mock-deterministic eval (실 LLM 호출 X — CI 가능). 실 LLM mode는 flag + 문서 (NG2)
- pytest: 293 → 305~315 (+12~22: eval_runner + revise_effect) + test_critic 의도 delta
- next build / tsc / lint: 회귀 0 (frontend 변경 0, types.ts deprecated 정합 주의)
- **eval 검증 → deprecated 제거 순서**: Slice 2~3 eval runner로 canonical-only 품질 baseline 확보 → Slice 4 제거 (eval 회귀 통과 확인)
