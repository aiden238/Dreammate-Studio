# Proposal: Phase M2 — Meta-Factory 8 GAP Remediation

> 날짜: 2026-05-31
> 유형: machinery 개선 proposal (contract-change CC-007 대상)
> 원천 proposal: `meta_factory/outputs/TEST/sample_test_podcast_validation.md §D` (M1 dry-run 발견)
> 절차: self_improvement_loop §0 — 제안(M1 §D) → 검토(본 문서) → 승인(사용자 "전체 8개") → 반영(M2 S1·S2) → 로그(CC-007)
> ★ 모든 변경 additive-only — 기존 machinery 필드·절차 삭제·재명명 0 (backward-compat)

---

## 배경

Phase M1 dry-run 이 meta_factory machinery(generation_workflow + validation_workflow + schema + templates)를 팟캐스트 도메인에 1회 적용하여 **8 GAP** 을 발견. 사용자 결정: **전체 8개 반영** + **M1 TEST 재적용 검증**. 본 proposal 은 8 GAP → machinery 변경을 추적한다.

## 승인된 8 변경 (M1 §D → M2 반영)

| GAP | M1 관찰 (§D) | M2 변경 (additive) | 파일 | Slice |
|---|---|---|---|---|
| **G1** | expert_pool vs 단일 agent 파라미터화 기준 약함 | "결정 기준" 섹션 추가 (특화도/포맷수/독립진화/비용·유지보수 임계) | architecture_patterns.md | S1 |
| **G2** ★ | skill 신규 vs 재사용 결정트리 부재 (검증4 입증) | 단계4 에 결정트리 추가 (키워드 충돌 검사 → 충돌 시 재사용 강제, YAGNI 차단) | generation_workflow.md | S1 |
| **G5** ★ | 제3자(게스트) PII risk 미반영 (medium 모호) | risk_level 판정에 "제3자 PII → 등급 상향 트리거" 축 추가 | domain_brief_schema.md | S1 |
| **G6** | data_model schema 밖 별도 섹션 우회 | `data_model` 선택 필드 추가 (계층/엔티티/PII 표시) | domain_brief_schema.md | S1 |
| **G3** ★ | conditional_execution / 조건부 산출 표현 부재 | agent_template `conditional_execution` 슬롯 + contract_template cross-ref "조건부 산출" 행 | agent_template.md + contract_template.md | S2 |
| **G4** | eval 조건부 차원 우회(notes) | 채점 차원에 `applies_when` (미해당 시 평균 제외) 추가 | eval_template.md | S2 |
| **G7** | dry-run 상태 표현 부재 ("(제안)" 수동) | `harness_status` enum 추가 (active/dry-run-blueprint/proposal) | project_state_template.md | S2 |
| **G8** | validation pending 단일값 (정상 pending 구분 불가) | validation enum 에 `pending-by-design` 추가 (+ 차원별 sub-status) | harness_blueprint_schema.md | S2 |

## 검토 (승인 근거)

- **타당성**: 8 GAP 전부 M1 6검증이 실제로 부딪힌 표현력/결정 기준 부재 (검증3 조건부축 / 검증4 with-without / 검증5 pending). 추측이 아닌 실측 근거.
- **additive-only**: 전부 추가형 → 기존 M1 blueprint backward-compat. 파괴적 변경 0.
- **우선순위**: 핵심 G2(skill 재사용 결정트리) / G3(conditional) / G5(제3자 PII) 가 생성 품질·안전 직결. G7/G8 은 meta-phase 표현력. G1/G4/G6 은 결정 기준·필드 보강.

## 검증 계획 (S3 재검증)
- M1 TEST 팟캐스트 산출물에 개선 슬롯 적용 → 8 GAP before/after + 6검증 재실행 → `outputs/TEST/sample_test_podcast_revalidation.md`.
- 기대: 검증3 조건부축 부재 → G3 슬롯으로 해소 / 검증5 pending → G8 pending-by-design 으로 표현 / 게스트 PII → G5 risk 격상으로 판정 가능.

## 반영 후 (CC-007)
- 8 machinery 변경 완료 → `docs/contract_changes/2026-05-31_phase-M2-machinery-gap.md` (CC-007) 로그.
- improvement backlog 8 → 0.
