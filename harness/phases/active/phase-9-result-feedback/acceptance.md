# Phase 9 — Acceptance (A1~A10 + M1~M4)

## A1~A10

| ID | 항목 | 검증 | Slice |
|---|---|---|---|
| **A1** | `selected_plans` schema (0005 migration, 실 plans 테이블 정합 option_index 0–2) | sql 파일 + ADR-030 | 2 |
| **A2** | SelectionRepo graceful (select/get, in-memory fallback) | pytest `test_selection_feedback.py` | 2 |
| **A3** | `feedback_events` + FeedbackRepo (like/dislike/reject/regenerate + reason) | pytest `test_selection_feedback.py` | 2 |
| **A4** | API — POST /plans/{id}/select + /feedback + GET /plans/{id}/feedback | pytest `test_plans_feedback_api.py` | 3 |
| **A5** | orchestrator/plans 정합 (회귀 0) | 기존 pytest 249 유지 | 3 |
| **A6** | **normalize_to_canonical wiring** — critic_evaluation canonical(0–1) 저장 (deprecated 0–5 병행) | pytest `test_critic_canonical_wiring.py` + agent-io-check | 3 |
| **A7** | Brand Memory 준비 — brand_memory_entries schema + BrandMemoryRepo + feedback→candidate 적재 경로 + **ADR-031 (P-AUX-2 설계, agent 미구현)** | pytest `test_brand_memory_prep.py` + ADR-031 | 4 |
| **A8** | **피드백 UI wrapper** — 선택/반려 (page.tsx inline) + **PlanCard·component_map 0줄** | next build 11 routes + tsc 0 + lint + git diff 0줄 | 5 |
| **A9** | audit_naming 0 drift + audit_page_component 2 intended WARN | scripts | 6 |
| **A10** | smoke_test_phase_9 15/15 + scenario_sim v5 25/25 | scripts | 6 |

## M1~M4 (메타)

| ID | 항목 |
|---|---|
| **M1** | multi-llm-validation formal self 여섯 번째 + external placeholder |
| **M2** | **security-review Skill 두 번째 정식** (피드백 reason PII + reject 사유 저장) |
| **M3** | contract-change Skill (db_schema.md feedback/selection 정식 — 실 plans 정합) |
| **M4** | P-X1 §SELF-VERIFICATION **42연속 PASS** (Slice 1~6) |

## 회귀 baseline (Phase 8 → Phase 9)

| 지표 | Phase 8 | Phase 9 목표 |
|---|---|---|
| pytest | 249/249 | 275~290 (+26~40, baseline 수정은 normalize wiring 의도된 delta만) |
| smoke | 14/14 | **15/15** (smoke_test_phase_9) |
| scenario_simulation | v4 20/20 | **v5 25/25** (+5 feedback/selection 시나리오) |
| schema_stress_test | 5/5 | 5/5 유지 |
| audit_naming | 0 drift | 0 drift |
| audit_page_component | 2 intended WARN | 2~3 intended WARN (피드백 UI page.tsx inline) |
| component_map.md 0줄 | 34 | **유지** (+6 → 40) |
| PlanCard.tsx 0줄 | 24 | **유지** (+6 → 30, frontend slice 있어도 wrapper) |
| P-X1 streak | 36 | **42** |

## qa-check 카테고리 (Phase 9 final 예상)
- 1 제품/범위 PASS / 2 AI 구조 PASS (normalize wiring) / 3 RAG PASS (candidate 적재 경로) / 4 프론트/UX **PASS** (피드백 UI) / 5 평가 skip (eval-run Phase 9.5) / 6 메타 PASS / 7 컨텍스트 필요시 / 8 큰 결정 **PASS** (security-review + contract-change + multi-llm) / 9 Phase 운영 PASS / **10 보안/인프라 PASS** (피드백 PII + RLS) / 11 비용 skip
- **예상**: 9 PASS / 2 skip.
