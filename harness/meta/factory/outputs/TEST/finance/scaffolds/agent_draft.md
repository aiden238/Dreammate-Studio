# agent_draft — personal_finance_planning_harness (scaffold, ★ G3 conditional_execution)

> 위치: `harness/meta_factory/outputs/TEST/finance/scaffolds/agent_draft.md`
> 상태: Phase M3 Slice S1 — agent scaffold dry-run
> 형식: `meta_factory/templates/agent_template.md` 개선본 (conditional_execution 슬롯)
> ★ 런타임 0 — agent 정의(설계)만. 실제 agent 코드 미생성 (factory_contract 규칙 1).

---

## 0. 사용 template

generation_workflow 단계 3 산출. agent_template.md placeholder 를 재무 6 agent 로 채움. ★ **G3 conditional_execution** 슬롯을 부채/부양가족 조건부 agent 에 행사.

---

## 1. 무조건 실행 agent (조건 슬롯 생략 = 항상 실행, backward-compat)

```yaml
# ── agent: planning ──────────────────────────────────────────
name: planning
responsibility: "재무 플랜 3안 생성 (parallel, 보수/중립/공격). 목표유형은 파라미터(goal_types[])로 통합 처리 (단일 agent 결정 — blueprint §1.2 G1)"
inputs: [user_message, mode, goal_types, risk_appetite, rag_context, household_context]
outputs: [plan_candidates]            # x3: budget_allocation + savings_target + investment_mix[] (합=100% 검증)
forbidden_actions:
  - 다른 agent 직접 호출 (orchestrator 경유 — supervisor 패턴)
  - 특정 금융상품/종목 지정 (forbidden_scope — 자산군 카테고리 비율만)
  - 원금 보장/수익률 약속 발화 (forbidden_scope)
# conditional_execution 슬롯 생략 → 항상 실행 (무조건 agent)
prompt_ids: [P-FIN-PLAN-001]          # placeholder (prompt_registry 미생성)
execution_policy:
  timeout_ms: 30000
  max_retries: 2
  graceful_on_failure: true           # LLM/RAG 실패 시 차단 0 + validation.warnings
```

---

## 2. ★ 조건부 실행 agent (G3 conditional_execution 행사)

> agent_template 작성가이드 6: 조건이 있으면 `conditional_execution.condition` 으로 1급 표현, 분기 소유 = orchestrator(supervisor). 조건 없으면 슬롯 생략(항상 실행).

```yaml
# ── agent: debt_priority ── (★ 부채 있을 때만) ───────────────
name: debt_priority
responsibility: "[부채 있을 때만] 부채 상환 우선순위 정보 플랜 (avalanche/snowball 일반 정보 제시)"
inputs: [debts, plan, savings_target]
outputs: [debt_repayment_plan]        # 우선순위 + 사유(고금리/소액) — 정보 제시
forbidden_actions:
  - 다른 agent 직접 호출 (orchestrator 경유)
  - 특정 대출/대환 상품 추천 (forbidden_scope)
  - 법률/세무 자문 (forbidden_scope)
conditional_execution:                # ★ G3
  condition: has_debt == true         # 부채 있을 때만 실행. 무부채 사용자 → orchestrator 가 이 agent 스킵
prompt_ids: [P-FIN-DEBT-001]
execution_policy:
  timeout_ms: 20000
  max_retries: 1
  graceful_on_failure: true           # 스킵 시 산출물에 "해당 없음(무부채)" 명시 — 차단 0

# ── agent: insurance_review ── (★ 부양가족 있을 때만) ────────
name: insurance_review
responsibility: "[부양가족 있을 때만] 보험/비상금 필요보장 검토 (필요보장 정보 — 상품 추천 아님)"
inputs: [household_context, dependents, plan, savings_target]   # dependents = 제3자 PII (마스킹)
outputs: [insurance_review]           # 필요보장 갭 정보 + 비상금 권장 개월수(일반 정보)
forbidden_actions:
  - 다른 agent 직접 호출 (orchestrator 경유)
  - 특정 보험상품/보험사 추천 (forbidden_scope)
  - 수익자(beneficiary)/부양가족 미제공 정보 날조 (llm_security — 제3자 PII 추측 금지)
  - 원금/보장 약속 발화 (forbidden_scope)
conditional_execution:                # ★ G3
  condition: has_dependents == true   # 부양가족 있을 때만 실행. 1인 가구 → orchestrator 가 이 agent 스킵
prompt_ids: [P-FIN-INS-001]
execution_policy:
  timeout_ms: 20000
  max_retries: 1
  graceful_on_failure: true           # 스킵 시 "해당 없음(부양가족 없음)" 명시 — 차단 0
```

---

## 3. ★ G3 적용 메모 (M2 conditional_execution 행사)

- **팟캐스트(M1) 대비**: M1 은 조건축이 `mode == guest` (모드 1축) 중심이었다. 재무는 **데이터 트리거 2축**(`has_debt` / `has_dependents`) — 모드가 아니라 가구/부채 데이터 존재 여부로 분기. → conditional_execution.condition 이 enum 모드뿐 아니라 **불리언 데이터 조건**도 표현함을 확인 (G3 표현력 범용).
- **분기 소유**: 두 조건부 agent 모두 분기를 스스로 트리거하지 않고 orchestrator(supervisor)가 has_debt/has_dependents 를 보고 스킵 결정. agent 격리 유지.
- **contract 정합**: 두 agent 의 출력(debt_repayment_plan / insurance_review)은 contract_draft §조건부 산출 cross-ref 에서 동일 조건으로 표기 (G3 양면 정합).
- **graceful 스킵**: 조건 미충족 시 산출물에 "해당 없음" 명시(차단 0) — P-GRACEFUL-001 정신 계승.

---

이 scaffold 는 agent_template 개선본(G3 conditional_execution)을 이질 도메인(재무)에 적용 (dry-run, active 아님).
