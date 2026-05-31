# contract_draft — output_schema (scaffold, ★ G3 조건부 산출 열)

> 위치: `harness/meta_factory/outputs/TEST/finance/scaffolds/contract_draft.md`
> 상태: Phase M3 Slice S1 — contract scaffold dry-run
> 형식: `meta_factory/templates/contract_template.md` 개선본 (cross-ref 의 "조건부 산출" 열)
> ★ contract 변경은 contract-change Skill 절차 — meta_factory 직접 편집 0. 본 scaffold 는 설계 초안 (proposal-first, 규칙 5).

---

## 0. 사용 template

generation_workflow 단계 5 산출. contract_template.md 형식(헤더+목적+필드표+JSONB+cross-ref)으로 output_schema 초안 작성. ★ **G3 조건부 산출(conditional output) 열**을 cross-ref 에 행사.

---

## (초안) output_schema.md — 재무 플랜 출력 본문 스키마

```markdown
# output_schema.md — 재무 플랜 출력 본문 스키마

> 위치: `docs/contracts/output_schema.md`
> 상태: Phase F0 진입용 (설계 초안 — dry-run)
> 참조: agent_io_contract.md, db_schema.md, llm_security.md    # ★ cross-ref

## 0. 이 문서의 위치

6 agent(intent/planning/debt_priority/insurance_review/critic/rewriter)의 출력 본문 스키마를 정의한다.

이 문서가 정의하는 대상:
- FinancialPlan / DebtPlan / InsuranceReview / Critic 본문 + 비자문 디스클레이머 필드

이 문서가 정의하지 않는 대상:
- agent 실행 정책(timeout/retry/조건부 실행) → `agent_io_contract.md`
- 테이블/컬럼/JSONB 영속 → `db_schema.md`
- PII 마스킹·자문 발화 차단 규칙 → `llm_security.md`

## 1. 필드 정의

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| plan_candidates | FinancialPlan[3] | ✅ | 보수/중립/공격 3안 |
| FinancialPlan.budget_allocation | object | ✅ | 카테고리별 예산 비율 (합=100%) |
| FinancialPlan.savings_target | object | ✅ | 저축 목표 금액/율 |
| FinancialPlan.investment_mix | Allocation[] | ✅ | 자산군 카테고리 비율 (★ 상품명 금지 — 카테고리만, 합=100%) |
| debt_repayment_plan | DebtPlan | — | ★ 조건부 산출 (has_debt 일 때만) |
| insurance_review | InsuranceReview | — | ★ 조건부 산출 (has_dependents 일 때만) |
| disclaimer | string(enum) | ✅ | 비자문 디스클레이머 (정보·기획용, 자문/원금보장 아님) |
| critic | Critic | ✅ | overall_verdict / overall_score / dimensions |
```

## 2. JSONB schema (해당 시)

\`\`\`json
{
  "investment_mix": [{"asset_class": "string(카테고리 — 상품명 아님)", "ratio": "number(0~1)"}],
  "savings_target": {"monthly_amount": "number", "rate": "number(0~1)"}
}
\`\`\`

## 3. Cross-reference (★ 정합 축 + 조건부 산출 열 — G3)

| 이 contract 의 필드 | 정합 대상 | 정합 규칙 | 조건부 산출(conditional output) |
|---|---|---|---|
| plan_candidates | agent_io planning.outputs | 1:1 | — (항상 산출) |
| FinancialPlan.investment_mix | db_schema allocations 테이블 | 1:1 JSONB | — (항상 산출) |
| **debt_repayment_plan** | agent_io debt_priority.outputs | 1:1 | ★ **has_debt == true 일 때만 산출** (debt_priority conditional_execution 정합) |
| **insurance_review** | agent_io insurance_review.outputs | 1:1 | ★ **has_dependents == true 일 때만 산출** (insurance_review conditional_execution 정합) |
| disclaimer | llm_security 자문 발화 차단 | enum 고정 | — (항상 산출, ★ 도메인 금지 게이트) |

## 4. 변경 이력
- v0.1.0 (2026-05-31): F0 진입용 설계 초안 (dry-run — M3 S1).

---

## 작성가이드 점검 (contract_template §작성가이드)

1. ✅ cross-reference 필수 — 4 정합 축 + **조건부 산출 열**(debt/insurance) 명시.
2. ✅ "정의하지 않는 대상" 명시 — agent_io/db_schema/llm_security 로 경계 분리 (P-DRIFT-001 정신).
3. ✅ JSONB 키/타입/예시 — investment_mix 는 카테고리만(상품명 금지 검증 규칙).
4. ✅ 변경 이력 semver — 실 active 반영은 contract-change Skill 경유 (규칙 5).

## ★ G3 조건부 산출 적용 메모

- **팟캐스트(M1) 대비**: M1 은 조건부 산출이 guest_brief/question_list/shownotes (mode==guest 1축). 재무는 **2개 조건부 산출(debt/insurance) + 서로 다른 데이터 트리거(has_debt vs has_dependents)** → 조건부 산출 열이 다축 조건을 1급으로 표현함을 확인.
- **agent ↔ contract 양면 정합**: agent_draft 의 conditional_execution.condition 과 contract cross-ref 의 조건부 산출 열이 동일 조건식으로 1:1 정합 (G3 양면 = drift 0 설계).

---

이 scaffold 는 contract_template 개선본(G3 조건부 산출 열)을 이질 도메인(재무)에 적용 (dry-run, active 아님 — contract-change 미경유).
