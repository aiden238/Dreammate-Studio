# Phase 4.5 — Acceptance Criteria (A1~A10)

> 완료 기준. Slice 4 final에서 10/10 PASS 필수.

## A1~A10

| ID | 항목 | 검증 방법 | Slice |
|---|---|---|---|
| **A1** | Rewriter Agent (P-008) 구현 + run_rewriter() 동작 | pytest `test_rewriter.py::test_basic_revise` + agents/rewriter.py 존재 | Slice 2 |
| **A2** | Critic Revise Loop 최대 2회 (3회 시 차단) | pytest `test_plans.py::test_revise_loop_max_2` | Slice 2 |
| **A3** | revise_history 응답 노출 (verdict + revised_at + revision_count) | pytest `test_plans.py::test_revise_history_structure` + schemas/output.py 통과 | Slice 2 |
| **A4** | Z-X3 recommended_plan_index (Critic 8-dim best-plan 선택) | pytest `test_critic.py::test_select_best_plan_index_*` (0/1/2 + tie) | Slice 3 |
| **A5** | Frontend wrapper highlight 동작 | next build 11 routes + tsc 0 + lint clean + page.tsx wrapper class 검증 | Slice 3 |
| **A6** | **PlanCard.tsx 0줄 변경 (5연속)** | `git diff HEAD~N HEAD -- apps/web/components/plan/PlanCard.tsx --stat` = 0 | Slice 3 + Slice 4 |
| **A7** | **component_map.md 0줄 변경 (16연속)** | `git diff HEAD~N HEAD -- apps/web/component_map.md --stat` = 0 | Slice 4 |
| **A8** | audit_naming + audit_page_component 0 drift | scripts (Slice 1 entry + Slice 4 final) | Slice 1 + 4 |
| **A9** | **P-X2 자동 게이트 첫 작동** — `scenario_simulation.ps1` 5/5 PASS via `phase-complete` v1.2.0 | phase-complete Skill 자동 호출 결과 | Slice 4 |
| **A10** | smoke_test_phase_4_5 9/9 PASS | `scripts/smoke_test_phase_4_5.ps1` 실행 결과 | Slice 4 |

## 추가 메타 검증 (M1~M3)

| ID | 항목 | 검증 |
|---|---|---|
| **M1** | multi-llm-validation **formal self** 첫 트리거 | `meta/validations/2026-05-28_phase-4.5-pre-entry_self.md` 존재 + skill_usage_log 반영 |
| **M2** | 외부 검증 placeholder 파일 분리 작성 | `meta/validations/2026-05-28_phase-4.5-pre-entry_external.md` 존재 (placeholder 형식 유효) |
| **M3** | P-X1 §SELF-VERIFICATION **13연속 PASS** | Slice 1~4 sub-agent commit별 git diff --stat 검증 |

## 회귀 baseline (Phase 4 → Phase 4.5 유지)

| 지표 | Phase 4 baseline | Phase 4.5 목표 |
|---|---|---|
| pytest | 93/93 | 100~103/100~103 (신규 7~10 추가) |
| next build | 11 routes | 11 routes (page.tsx 수정만, route 추가 0) |
| tsc | 0 errors | 0 errors |
| lint | clean | clean |
| audit_naming | 0 drift | 0 drift |
| audit_page_component | 0 drift | 0 drift |
| smoke_test | 8/8 PASS | 9/9 PASS (smoke_test_phase_4_5.ps1) |
| component_map.md 0줄 streak | 15 | **16** |
| PlanCard.tsx 0줄 streak | 4 | **5** |
| P-X1 §SELF-VERIFICATION streak | 9 | **13** |

## qa-check 카테고리 (v1.2.0, 11 카테고리)

| 카테고리 | Slice 4 final 활성 여부 |
|---|---|
| 1. 제품 / 범위 (scope creep) | PASS 목표 |
| 2. AI 구조 (agent_io, output_schema) | PASS 목표 (Rewriter agent_io 신규 정합) |
| 3. RAG (정책 / 메타 / 품질) | skip (NG7, 본 phase RAG 변경 0) |
| 4. 프론트 / UX | PASS 목표 (wrapper UI 검증) |
| 5. 평가 / 품질 (golden_set 회귀) | skip (NG8) |
| 6. 메타 개선 (patterns / retrospective) | PASS 목표 |
| 7. 컨텍스트 / 세션 | (필요 시) |
| 8. 큰 결정 / 교차검증 | PASS 목표 (M1 multi-llm-validation formal) |
| 9. Phase 운영 (state docs / registry) | PASS 목표 |
| 10. 보안 / 인프라 | skip (NG2/NG3) |
| 11. 비용 / 관측성 | skip (Phase 9+) |

**예상**: 7 PASS / 4 skip.
