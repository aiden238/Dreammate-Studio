# Phase M2 — Goals (Meta-Factory GAP Remediation)

> Phase: phase-M2-meta-factory-gap-remediation
> 유형: **meta-phase** (제품 phase 아님 — L3 machinery 개선. ★ M1 과 달리 machinery 문서를 **실제로 변경**)
> 진입일: 2026-05-31
> 예상 시간: 3~5h (S1·S2·S3 sub-agent + doc-sync)
> ★ 런타임 변경 0 (FastAPI/Next.js/Supabase 0줄, A9) — 변경 영역은 `meta_factory/` machinery docs + meta + state
> ★ **contract-change (CC-007)** — machinery(L3 contract) 변경은 contract-change Skill 절차 경유. proposal-first (M1 improvement_report §D → 검토 → 승인 → 반영)

## 한 줄 정의

Phase M1 dry-run 이 발견한 **8 GAP**(G1~G8)을 `meta_factory/` machinery 문서에 반영하여 L3 Meta-Factory 의 표현력·결정 기준을 보강하고, 개선된 machinery 를 **M1 TEST 팟캐스트 산출물에 재적용(re-validate)** 하여 각 GAP 이 실제로 해소됨을 before/after 로 입증한다. 모든 변경은 contract-change(CC-007) + proposal-first.

## M1 → M2 흐름

```
M1 (dry-run)  : machinery 0 변경 — 8 GAP 발견 (outputs/TEST/sample_test_podcast_validation.md §D)
M2 (이번)      : machinery 실제 변경 (CC-007) — 8 GAP 반영 + M1 TEST 재적용으로 해소 입증
```

## 8 GAP → 파일 → Slice (전부 반영 — 사용자 결정 "전체 8개")

| GAP | 내용 | 대상 파일 | Slice |
|---|---|---|---|
| **G2** ★ | 신규 Skill vs 기존 재사용 **결정트리** (키워드 충돌 검사 → 충돌 시 재사용 강제) | `generation_workflow.md` 단계4 | S1 |
| **G1** | expert_pool vs 단일 agent **파라미터화 결정 기준** (특화도/비용/유지보수) | `architecture_patterns.md` | S1 |
| **G5** ★ | **제3자(비사용자) PII** 처리 시 risk 등급 상향 트리거 축 | `domain_brief_schema.md` risk_level | S1 |
| **G6** | `data_model` 선택 필드 (계층 구조 + 엔티티 + PII 표시) | `domain_brief_schema.md` | S1 |
| **G3** ★ | `conditional_execution` 슬롯 + cross-ref "조건부 산출" 행 | `agent_template.md` + `contract_template.md` | S2 |
| **G4** | 채점 차원 `applies_when` (조건부 차원, 미해당 시 평균 제외) | `eval_template.md` | S2 |
| **G7** | `harness_status` enum (active / dry-run-blueprint / proposal) | `project_state_template.md` | S2 |
| **G8** | validation enum `pending-by-design` (실측 미수행이 정상) | `harness_blueprint_schema.md` | S2 |

## 핵심 목표 (G-S1 ~ G-close)

| ID | 목표 | 검증 |
|---|---|---|
| **GA** | S1 cluster (G1/G2/G5/G6) machinery 반영 — 생성 입력/절차 보강 | A1 |
| **GB** | S2 cluster (G3/G4/G7/G8) machinery 반영 — scaffold/schema 표현력 보강 | A2 |
| **GC** | M1 TEST 팟캐스트 산출물에 개선 machinery **재적용** → GAP 해소 before/after | A3 (re-validate) |
| **GD** | **CC-007** contract-change 로그 (8 변경 + cross-ref 정합 + proposal 추적) | A4 |
| **GE** | machinery backward-compat — 기존 M1 blueprint 가 개선 machinery 하에서도 유효 (추가만, 파괴적 변경 0) | A5 |

## 메타 목표 (MG1~MG3)

| ID | 목표 |
|---|---|
| **MG1** | A9 — FastAPI/Next.js/Supabase **0줄** (machinery/meta/state 만 변경) |
| **MG2** | multi-llm-validation formal self **아홉 번째** (8 GAP 반영 타당성 + backward-compat) + external placeholder |
| **MG3** | P-X1 §SELF-VERIFICATION **55연속** (M1 52 + M2 S1·S2·S3 3) |

## 사용자 가치 (Why)

- **payoff 실현**: M1 이 "machinery 가 검증 가능하다"를 입증했고, M2 는 그 검증이 찾은 GAP 을 실제 개선으로 전환 — Meta-Factory self-improvement loop 의 첫 완주 (발견 → 반영 → 재검증).
- **다음 도메인 하네스 품질 ↑**: 개선된 machinery(결정트리/conditional/PII risk/data_model)는 차기 도메인(이질 도메인 dry-run / 2nd 하네스) 생성 품질을 직접 향상.
- **백로그 0**: 8 GAP 전부 반영 → improvement_reports 백로그 소거 (사용자 결정).

## ★ 절대 금지 (non_goals.md 상세)

런타임 코드(FastAPI/Next/Supabase) 변경 / 기존 product contracts(api/output_schema/agent_io/db_schema/rag/llm_security) 변경 / 기존 Skill 본문 변경(harness-factory 포함 — machinery 문서만) / AGENTS·CLAUDE 라우터 변경 / 자동 generator 코드 / 2nd 하네스 실 생성 / generated harness active 전환 — 모두 범위 밖.
