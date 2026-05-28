# Phase 6 — Acceptance (A1~A10 + M1~M3)

## A1~A10

| ID | 항목 | 검증 |
|---|---|---|
| **A1** | Critic verdict canonical 표준 결정 (overall_score + dimensions) | `docs/contracts/output_schema.md` §CriticEvaluation canonical 명시 + ADR-018 |
| **A2** | select_best_plan_index fallback 축소 + deprecation note | `agents/critic.py` fallback chain 축소 + DeprecationWarning issued in tests |
| **A3** | Rewriter input/output contract 정식 등록 (P-008) | `docs/contracts/agent_io_contract.md` §P-008 + ADR-019 |
| **A4** | revise_history + recommended_plan_index contract 명시 | `docs/contracts/output_schema.md` Optional 필드 정식 |
| **A5** | Rewriter Pydantic 모델 도입 (RewriterInput / RewriterOutput) | `agents/rewriter.py` Pydantic 모델 + pytest |
| **A6** | Frontend types.ts ↔ backend schema 1:1 매핑 정합 | `lib/types.ts` CriticVerdict mirror + tsc 0 errors |
| **A7** | schema_stress_test 5~7 케이스 PASS | `tests/test_schema_stress.py` + `scripts/schema_stress_test.ps1` |
| **A8** | **PlanCard.tsx 0줄 (10연속) + component_map.md 0줄 (20연속)** | git diff HEAD~N HEAD --stat = 0 |
| **A9** | audit_naming + audit_page_component 0 drift | scripts (Slice 1 + 4) |
| **A10** | smoke_test_phase_6 10/10 PASS | `scripts/smoke_test_phase_6.ps1` 신규 |

## M1~M3 (메타)

| ID | 항목 | 검증 |
|---|---|---|
| **M1** | multi-llm-validation formal self V1~V5 PASS | `meta/validations/2026-05-29_phase-6-pre-entry_self.md` |
| **M2** | external validation placeholder 분리 (Phase 5 진입 전 채울 수 있도록) | `meta/validations/2026-05-29_phase-6-pre-entry_external.md` |
| **M3** | P-X1 §SELF-VERIFICATION **17연속 PASS** (Phase 6 Slice 1~4 모두) | sub-agent별 git diff --stat |

## 회귀 baseline (Phase 4.5 → Phase 6)

| 지표 | Phase 4.5 baseline | Phase 6 목표 |
|---|---|---|
| pytest | 109/109 | 115~117/115~117 (+5~7 schema stress) |
| smoke | 9/9 | **10/10** (smoke_test_phase_6) |
| scenario_simulation | 5/5 | 5/5 유지 |
| audit×2 | 0 drift | 0 drift |
| component_map.md 0줄 streak | 19 | **20** |
| PlanCard.tsx 0줄 streak | 9 | **10** |
| P-X1 streak | 13 | **17** |

## qa-check 카테고리 (v1.2.0, 11 카테고리)

Phase 6 final 활성 예상 (PASS / skip 분류):
- 1. 제품 / 범위 — PASS
- 2. AI 구조 (agent_io, output_schema) — **PASS** (핵심)
- 3. RAG — skip (NG9 정신)
- 4. 프론트 / UX — PASS (types.ts 정합)
- 5. 평가 — skip (NG9, Phase 9+)
- 6. 메타 개선 — PASS
- 7. 컨텍스트 — 필요 시
- 8. 큰 결정 / 교차검증 — **PASS** (M1 multi-llm-validation + contract-change)
- 9. Phase 운영 — PASS
- 10. 보안 / 인프라 — skip (NG1, Phase 5)
- 11. 비용 / 관측성 — skip (Phase 9+)

**예상**: 7 PASS / 4 skip.
