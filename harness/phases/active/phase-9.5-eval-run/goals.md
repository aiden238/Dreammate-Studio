# Phase 9.5 — Goals

> Phase: phase-9.5-eval-run
> 유형: eval mini-phase (eval-run 정식화 + Critic deprecated 0–5 Full 제거)
> 진입일: 2026-05-31
> 예상 시간: 6~10h (5 Slice 모두 sub-agent dispatch)

## 한 줄 정의

**golden_set 회귀 runner(mock-deterministic, CI 가능)**와 **revise effect eval**을 구현하여 eval-design/eval-run Skill을 첫 정식 트리거하고, eval로 canonical-only 품질을 검증한 뒤 **Critic deprecated 0–5 fallback + CriticEvaluation Optional deprecated 필드를 Full 제거**(contract-change)하여 Critic 평가 체계를 canonical(0–1) 단일 표준으로 정리한다.

## 핵심 목표 (G1~G7)

| ID | 목표 | 검증 |
|---|---|---|
| **G1** | eval-run golden_set 회귀 runner — `backend/fastapi/eval/` module (47 GS 케이스 로더 + mock-deterministic 회귀 + schema/structural 채점) + regression_results 출력 | A1, A2 |
| **G2** | 임계값 게이트 — eval-run Skill §6 (schema 준수 100% / 점수 변화 ±0.3 / 광고 표현 / 차단 단어) | A3 |
| **G3** | **revise effect eval** — revise loop 개선 효과 측정 (Phase 4.5 D6 해소, mock-based) | A4 |
| **G4** | eval-design + eval-run Skill **첫 정식 트리거** + 실 LLM mode 문서 (mock primary) | A5, M2 |
| **G5** | **Critic deprecated 0–5 Full 제거** — select_best_plan_index fallback + DeprecationWarning + CriticEvaluation Optional deprecated 필드 (eval 검증 후) | A6 |
| **G6** | contract-change (output_schema + agent_io_contract + db_schema critic_evaluation) — deprecated 필드 제거 정합 | A7, M3 |
| **G7** | 회귀 0 — Phase 9 baseline (pytest 293) 유지 + 의도된 test_critic deprecated-fallback delta만 | A8, A9, A10 |

## 메타 목표 (M1~M4)

| ID | 목표 |
|---|---|
| **M1** | multi-llm-validation formal self 일곱 번째 + external placeholder |
| **M2** | **eval-design + eval-run Skill ★ 둘 다 첫 정식 트리거** |
| **M3** | contract-change Skill (deprecated 0–5 제거 — output_schema + agent_io_contract + db_schema) |
| **M4** | P-X1 §SELF-VERIFICATION **47연속 PASS** (Phase 9:42 + Phase 9.5:5) |

## 사용자 가치 (Why)

- **품질 안전망**: golden_set 회귀 runner → prompt/RAG/모델 변경 시 자동 품질 검증 baseline (확정 결정 [20] semver 회귀)
- **Critic 단일 표준**: deprecated 0–5 제거 → critic_evaluation canonical(0–1) 단일화 → 유지보수 ↓ + eval 정합 + DB/frontend type 단순화
- **revise 효과 실증**: Phase 4.5부터 미측정이던 revise loop 개선 효과 첫 측정
- **누적 deferred 해소**: Critic deprecated 제거(Phase 6 ADR-018 다음 단계, 누적 다회) + revise eval(Phase 4.5 D6) 동시 해소

## 비목표 (별도 문서: non_goals.md)

RAG eval_rubric → golden_set 정식화(Phase 10+) / 실 LLM eval harness 우선(mock primary) / run_critic 0–5 출력 제거(P-007 prompt contract 불변) / P-AUX-2 agent / async / PlanCard·component_map 수정.
