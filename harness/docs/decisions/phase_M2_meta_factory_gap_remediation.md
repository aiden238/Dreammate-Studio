# ADR-037: Meta-Factory GAP Remediation (M1 발견 8 GAP machinery 반영)

> 상태: Accepted
> 결정일: 2026-05-31
> Phase: M2 (Meta-Factory GAP Remediation, ★ meta-phase)
> 관련: ADR-035 (L3 도입) / ADR-036 (M1 dry-run) / CC-007 (machinery 변경 로그)
> ★ 런타임 0 (A9) + additive-only (backward-compat)

---

## Context

Phase M1 dry-run 이 meta_factory machinery 의 **8 GAP**(G1~G8)을 발견(ADR-036). machinery 가 "검증 가능하다"는 것은 입증됐으나, 검증이 찾은 GAP(조건부 표현력 / 결정 기준 부재 / 제3자 PII / dry-run 상태 표현 등)이 미해소 상태로 남음. self-improvement loop(M0 도입 → M1 검증 → ?) 를 완주하려면 발견된 GAP 을 실제 개선으로 전환해야 함.

사용자 결정: **전체 8개(G1~G8) 반영** + **M1 TEST 재적용(re-validate) 검증**.

## Decision

**Phase M2 (meta-phase)** 로 8 GAP 을 meta_factory machinery 에 **additive-only** 로 반영하고(contract-change CC-007), 개선된 machinery 를 M1 TEST 팟캐스트 산출물에 **재적용하여 before/after 로 해소를 입증**한다.

1. **additive-only**: 8 변경 전부 추가형(새 결정트리/필드/슬롯/enum 값/표 열). 기존 필드·절차 삭제·재명명 0 → M1 blueprint backward-compat.
2. **contract-change (CC-007)**: machinery = L3 contract. proposal(M1 §D) → 검토 → 승인 → 반영 → 로그.
3. **2 cluster + 재검증**: S1 생성-입력/절차(G1/G2/G5/G6) + S2 scaffold/schema(G3/G4/G7/G8) + S3 재검증.
4. **런타임 0 (A9)**: machinery/meta/state/outputs/TEST 만 변경.

## 8 GAP → 변경

| GAP | 변경 (additive) | 파일 |
|---|---|---|
| G1 | expert_pool vs 단일 agent 결정 기준 (4축 + 비용 임계) | architecture_patterns.md §2.1 |
| G2 ★ | 신규 Skill vs 재사용 결정트리 (키워드 충돌 → 재사용 강제) | generation_workflow.md §4.1 |
| G3 ★ | conditional_execution 슬롯 + 조건부 산출 cross-ref 열 | agent_template + contract_template |
| G4 | 채점 차원 applies_when (미해당 시 평균 제외) | eval_template.md §B |
| G5 ★ | 제3자 PII risk 상향 트리거 | domain_brief_schema.md §1.1 |
| G6 | data_model 선택 필드 | domain_brief_schema.md §1.2 |
| G7 | harness_status enum (active/dry-run-blueprint/proposal) | project_state_template.md |
| G8 | validation pending-by-design enum | harness_blueprint_schema.md §1.1 |

## Result (S3 재검증)

- **백로그 8 → 0**: addressed 7 + expressible 1 (G5 — 안전 판정 축은 해소, 실 등급 변경은 사용자 승인 게이트라 dry-run 에선 표현까지) + open 0.
- **6검증 재판정 PASS 5 / PENDING-BY-DESIGN 1**:
  - 검증3(contract): M1 "조건부 산출 축 부재 GAP" → G3 로 **해소** (drift 0 유지).
  - 검증5(eval-run): M1 단순 PENDING → G8 **pending-by-design** 으로 "절차 적용 가능/실측 미수행 = 정상" 명시 구별.
- **backward-compat ✅**: M1 blueprint 가 개선 machinery 하에서도 valid (additive + 기본값).

## Consequences

### 긍정
- **self-improvement loop 완주**: M0(도입) → M1(검증·GAP 발견) → M2(반영·재검증). Meta-Factory 가 스스로를 개선하는 첫 사이클 완료.
- **차기 도메인 품질 ↑**: 결정트리/conditional/PII risk/data_model 가 차기 dry-run·2nd 하네스 생성 품질을 직접 향상.
- **백로그 0**: improvement_reports GAP 소거.
- additive-only 로 회귀 위험 0 (A5 게이트 + S3 입증).

### 제약 / 한계
- **G5 expressible(완전 addressed 아님)**: 제3자 PII risk **판정 축**은 추가됐으나 실 등급 변경은 사용자 승인 게이트 (dry-run 표현까지).
- **검증5 실측 여전히 미해소**: pending-by-design 으로 **표현**은 개선됐으나 실 eval-run 점수는 별도 (eval-run §3~§6 mock-deterministic 표본 — 다음 단계).
- machinery 개선 효과의 정량 입증은 소표본(M1 팟캐스트 1 도메인) — 차기 도메인 dry-run 시 재측정.

## Non-Goals (재확인)
- product contract / Skill 본문 / 라우터 / runtime 변경 (NG1~NG4).
- machinery 파괴적 변경 (NG9 — additive-only).
- 새 GAP 발굴 / 2nd 하네스 실 생성 (NG7/NG8).

## 다음 ADR 후보
- 검증5 실 eval-run 표본 결과 (eval-run §3~§6).
- (선택) 이질 도메인 dry-run 으로 개선 machinery 범용성 2차 검증.
