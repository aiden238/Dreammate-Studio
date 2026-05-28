# Phase 5.5 — Acceptance (A1~A8 + M1~M2)

## A1~A8

| ID | 항목 | 검증 |
|---|---|---|
| **A1** | Legacy DB 통합 결정 명시 (ADR-023) — 두 layer 공존 / 통합 / 단계적 deprecation 중 명확한 선택 | `docs/decisions/phase_5_5_legacy_db_consolidation.md` |
| **A2** | Phase 1 legacy `tests/test_db.py` + Phase 5 `tests/test_db.py` 모두 PASS (회귀 0) | pytest 170+/170+ |
| **A3** | external validation 3개 self-strengthen 완료 (Phase 4.5 V1~V4 + Phase 6 V1~V5 + Phase 5 V1~V6) | `meta/validations/*_external.md` 3개 |
| **A4** | `docs/decisions/phase_7_rag_scope_evolution.md` 신규 (ADR-024) — RAG Lite + 5단계 + 확대 지침 + 다른 phase 확장 경로 | 파일 존재 + 핵심 키 명시 |
| **A5** | Brand Memory **Phase 9+** confirmation 명시 (Phase 5.5 non_goals NG2 + 회고) | non_goals.md NG2 + retrospective 본문 |
| **A6** | **PlanCard.tsx 18연속 0줄** + **component_map.md 28연속 0줄** | git diff badb2c0..HEAD --stat |
| **A7** | audit_naming + audit_page_component (Phase 5 intended WARN 외 0 drift) | scripts |
| **A8** | smoke_test_phase_5 12/12 PASS 유지 (재실행) + scenario_simulation v2 10/10 PASS 유지 | scripts |

## M1~M2 (메타)

| ID | 항목 |
|---|---|
| **M1** | P-X1 §SELF-VERIFICATION **26연속 PASS** (Slice 1~4 모두) |
| **M2** | Phase 7 RAG 진입 baseline 확립 (사용자 결정 4: candidate_knowledge 5단계 MVP 전부, ADR-024 명시) |

## 회귀 baseline (Phase 5 → Phase 5.5)

| 지표 | Phase 5 | Phase 5.5 목표 |
|---|---|---|
| pytest | 170/170 | 170+/170+ (회귀 0) |
| smoke_test_phase_5 | 12/12 | 12/12 유지 |
| scenario_simulation v2 | 10/10 | 10/10 유지 |
| schema_stress_test | 5/5 | 5/5 유지 |
| audit_naming | 0 drift | 0 drift |
| audit_page_component | 2 intended WARN | 2 intended WARN |
| component_map.md 0줄 streak | 27 | **28** |
| PlanCard.tsx 0줄 streak | 17 | **18** |
| P-X1 streak | 22 | **26** |

## qa-check 카테고리

Phase 5.5 final 예상: 5 PASS / 6 skip (mini-phase, 코드 변경 최소 — 메타 작업 중심)
