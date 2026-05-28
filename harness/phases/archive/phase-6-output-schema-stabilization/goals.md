# Phase 6 — Goals

> Phase: phase-6-output-schema-stabilization
> 유형: stabilization phase (Phase 5 DB/Auth 진입 전 contract 안정화)
> 진입일: 2026-05-29
> 예상 시간: 8~10h

## 한 줄 정의

Phase 4.5에서 추가된 Rewriter / revise_history / recommended_plan_index / Critic verdict 4가지 fallback 구조를 **contract + canonical schema로 안정화**하여, Phase 5 DB/Auth 진입 시 schema drift 위험을 0에 가깝게 만든다.

## 핵심 목표 (G1~G6)

| ID | 목표 | 검증 매핑 |
|---|---|---|
| **G1** | Critic verdict **단일 canonical 표준 결정** — `overall_score` + `dimensions` 정식화, 나머지 fallback은 deprecation note 추가 후 임시 유지 | A1, A2 |
| **G2** | Rewriter input/output contract 명시 — `agent_io_contract.md`에 P-008 schema 정식 등록 (prompt body는 인라인 유지, semver만 등록) | A3 |
| **G3** | revise_history + recommended_plan_index **contract 명시** — `output_schema.md`에 Optional 필드 정식 등록 + ADR-018/019 | A4 |
| **G4** | select_best_plan_index fallback 축소 + deprecation note (Phase 9+ eval 안정화 후 제거) | A5 |
| **G5** | Frontend types.ts ↔ backend schema 1:1 매핑 정합 검증 + schema_stress_test.ps1 신규 | A6, A7 |
| **G6** | 회귀 0 — Phase 4.5 baseline 유지 (pytest 109/109 → 115+/115+, smoke 9/9 → 10/10, audit 0 drift) | A8, A9, A10 |

## 메타 목표 (M1~M3)

| ID | 목표 | 결과물 |
|---|---|---|
| **M1** | multi-llm-validation **formal self** 두 번째 트리거 (V1 verdict canonical / V2 rewriter contract / V3 revise_history / V4 fallback reduction / V5 frontend type sync) | `meta/validations/2026-05-29_phase-6-pre-entry_self.md` |
| **M2** | external validation placeholder 분리 작성 (Phase 5 진입 전 사용자가 외부 GPT/Gemini 검토 채울 수 있도록) | `meta/validations/2026-05-29_phase-6-pre-entry_external.md` |
| **M3** | P-X1 §SELF-VERIFICATION **17연속 PASS** (Phase 3:5 + Phase 4:4 + Phase 4.5:4 + Phase 6:4) | sub-agent commit별 git diff --stat |

## 사용자 가치 (Why)

- **DB 진입 안전성 ↑**: Phase 5 DB schema에 박히기 전 canonical 결정 → migration 회귀 위험 ↓
- **Critic 발전 가능성 ↑**: 4 fallback 혼재 시 verdict 평가 일관성 ↓ → 단일 표준 = 추후 eval/A-B 비교 baseline
- **사용자 정신 계승**: Phase 4.5에서 검증된 multi-llm-validation formal + P-X1 + 0줄 baseline 패턴 유지

## 비목표 (별도 문서: non_goals.md)

Supabase / DB migration / Auth / RLS / SSE / PlanCard 수정 / prompt body 본문 작성 / revise effect eval — 모두 Phase 5+ / Phase 7+ / Phase 9+ 이관.
