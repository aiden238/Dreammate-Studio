# Phase M0 — Acceptance (A1~A10 + M1~M3)

> 사용자 지침 §8 A1~A10 채택 + 메타 목표

## A1~A10 (사용자 지침 §8)

| ID | 항목 | 검증 | Slice |
|---|---|---|---|
| **A1** | `harness/meta_factory/` 기본 구조 생성 | 디렉토리 + 파일 존재 | 1~2 |
| **A2** | README.md가 L1/L2/L3 구조 명확 설명 | string match (L1/L2/L3) | 1 |
| **A3** | factory_contract.md가 런타임 미변경 + proposal-first 명시 | string match (8 규칙) | 1 |
| **A4** | domain_brief_schema.md + harness_blueprint_schema.md 존재 | 파일 + schema 필드 | 1~2 |
| **A5** | architecture_patterns.md 6 패턴 + Dreammate 매핑 | 6 패턴 + Supervisor=orchestrator 등 | 1 |
| **A6** | validation_workflow.md — trigger validation + skill conflict + with/without + eval-run 연동 | 6 검증 섹션 | 2 |
| **A7** | dreammate_current_harness_blueprint.md 현재 하네스 역정리 + L3 부족점 | 10 섹션 + 부족점 5 (실측) | 2 |
| **A8** | harness-factory Skill INDEX 등록 + 키워드 충돌 검토 기록 | INDEX #21 + 우선순위 + proposal | 3 |
| **A9** | **FastAPI/Next.js/Supabase runtime 변경 0** | git diff backend/apps/migrations = 0 | 전 Slice |
| **A10** | 결과 요약 — 변경 파일 + 목적 + 다음 phase 제안 | closing_notes + 보고 | 3 |

## M1~M3 (메타)

| ID | 항목 |
|---|---|
| **M1** | multi-llm-validation formal self 여덟 번째 + external placeholder (L3 도입 타당성) |
| **M2** | contract-change Skill (INDEX Skill 등록 — CC-006) + harness-factory proposal-only 확인 |
| **M3** | P-X1 §SELF-VERIFICATION **50연속 PASS** (Slice 1~3) |

## 회귀 baseline (Phase 9.5 → M0)

| 지표 | Phase 9.5 | M0 목표 |
|---|---|---|
| pytest | 339/339 | **339 유지** (런타임 변경 0 → 회귀 0) |
| **FastAPI/Next/Supabase 변경** | — | **0줄 (A9 핵심)** |
| smoke | 16/16 | smoke_test_phase_M0 (경량: 런타임 회귀 0 + meta_factory 존재 + audit) |
| scenario_simulation | v6 30/30 | **v7 33/33** (+3 meta_factory 시나리오) |
| audit_naming | 0 drift | 0 drift (meta_factory 명명 정합) |
| component_map.md 0줄 | 45 | **유지** (frontend 변경 0) |
| PlanCard.tsx 0줄 | 35 | **유지** |
| P-X1 streak | 47 | **50** |
| Skill 수 | 20 | **21** (harness-factory) |

## qa-check 카테고리 (M0 final 예상)
- 1 제품/범위 PASS (런타임 변경 0 — 범위 정확) / 2 AI 구조 skip / 3 RAG skip / 4 프론트 skip (변경 0) / 5 평가 PASS (validation_workflow ↔ eval-run 연동) / 6 **메타 PASS** (★ 핵심 — Meta-Factory) / 7 컨텍스트 / 8 큰 결정 **PASS** (multi-llm + contract-change INDEX) / 9 Phase 운영 PASS / 10 보안 skip / 11 비용 skip
- **예상**: 5 PASS / 6 skip (meta-phase 특성).
