# harness_blueprint — personal_finance_planning_harness (WITH 출력)

> 위치: `harness/meta_factory/outputs/TEST/finance/harness_blueprint.md`
> 상태: Phase M3 Slice S1 — generation dry-run **출력 청사진**
> 형식: `meta_factory/harness_blueprint_schema.md` **개선본** (validation pending-by-design enum G8 포함)
> 입력: `domain_brief.md` (personal_finance_planning_ai, 이질 도메인)
> 절차: `generation_workflow.md` 11단계 + architecture_patterns G1 결정기준 + generation_workflow G2 §4.1 결정트리 적용
> ★ proposal — validation 3필드 = pending / pending-by-design. 6검증(S2) 통과 + 사용자 승인 전 active 아님 (factory_contract 규칙 7).

---

## 0. generation_workflow 11단계 실행 로그

| 단계 | 내용 | 본 dry-run 상태 |
|---|---|---|
| 1 | domain_brief 수집 | ✅ `domain_brief.md` (11 필드 + data_model, forbidden_scope 7, risk high) |
| 2 | architecture pattern 선택 | ✅ §1 — supervisor 주 + 보조 3. ★ expert_pool 은 §1.2 G1 결정기준으로 **미채택** 판정 |
| 3 | agent 후보 생성 | ✅ §2 — 6 agent (2 조건부) |
| 4 | skill 후보 생성 | ✅ §3 — ★ G2 §4.1 결정트리로 신규 0 / 재사용 강제 (security-review 포함) |
| 5 | contract 후보 생성 | ✅ §4 — 4 contract (조건부 산출 cross-ref 포함) |
| 6 | eval 후보 생성 | ✅ §5 — 5 eval (★ high → security 강제, 조건부 차원 applies_when) |
| 7 | phase 구조 생성 | ✅ §6 — 5 phase (non_goals ← forbidden_scope 매핑) |
| 8 | routing 문서 생성 | ✅ §7 — AGENTS / CLAUDE 대응 |
| 9 | validation_workflow 실행 (6검증) | ⏸ **S2 가 수행** — 본 S1 은 validation 3필드 = pending / pending-by-design (§9) |
| 10 | outputs 격리 저장 | ✅ outputs/TEST/finance/ (proposal-first, dry-run 격리) |
| 11 | 사용자 승인 후 적용 | ⏸ 미수행 (dry-run — active 전환 없음) |

---

## 1. 메타 + architecture_pattern (단계 2)

```yaml
harness_name: personal_finance_planning_harness
purpose: "개인 재무 플래닝 AI — 목표→예산·저축·투자배분 플랜 3안 + 리스크/적합성 검토 (정보·기획 도구, 자문 아님), 3-plan + Critic revise"

architecture_pattern:
  primary: supervisor              # orchestrator 가 전 단계 중개 — agent 간 직접 호출 0 + 자문 발화 정책 일관 적용
  secondary:
    - fan_out_fan_in               # 플랜 3안(보수/중립/공격) parallel 생성 (asyncio.gather) + 비용 3배·부분실패 graceful
    - producer_reviewer            # Planner → Critic(적합성/리스크) → Rewriter revise loop (max 2 — 무한 루프 차단)
    - pipeline                     # Intent → RAG → Planning → [Debt] → [Insurance] → Critic → Save
  considered_not_adopted:
    - expert_pool                  # ★ G1 결정기준으로 미채택 (§1.2) — 목표유형(저축/투자/은퇴/부채)별 전문가 풀 vs 단일 planning 파라미터화 → 단일 채택
    - hierarchical_delegation      # 미채택 — 재귀 분해 작업 없음 (Dreammate 와 동일)
```

### 1.1 패턴 선택 근거 (architecture_patterns.md 6 패턴 기준)

| 패턴 | 채택 | 근거 |
|---|---|---|
| Supervisor (주) | ✅ | 6 agent 다단계 + 격리/추적 필요. ★ **자문 금지·원금보장 금지 정책을 orchestrator 가 모든 단계에 일관 적용**(forbidden_scope 도메인 금지) — 격리가 규제 리스크 차단의 핵심. agents[].forbidden_actions 에 "직접 호출 금지" 필수. |
| Fan-out/Fan-in | ✅ | 플랜 3안(보수/중립/공격 리스크 톤) 독립 병렬 생성 → 다양성(3후보 1선택). 비용 3배 + 부분 실패 graceful 명시. |
| Producer-Reviewer | ✅ | 적합성·리스크 검토 품질 중요 + 자동 평가 기준(finance_planning_eval) 정의 가능. revise max 2 상한. |
| Pipeline | ✅ | 흐름이 명확한 선형(의도→기획→부채→보험→검토→저장) + graceful skip. |
| Expert Pool | ❌ 미채택 | ★ §1.2 G1 결정기준 적용 결과. |
| Hierarchical Delegation | ❌ | 재귀 분해 작업 없음. |

### 1.2 ★ G1 적용 — expert_pool vs 단일 planning agent 파라미터화 결정 (architecture_patterns §2.1)

> 재무 도메인의 핵심 설계 질문: **목표유형(저축/부채상환/투자배분/은퇴/비상금)별로 전문가 agent 를 나눌(expert_pool)것인가, 단일 planning agent 가 목표유형을 파라미터로 받아 분기할 것인가?** architecture_patterns §2.1 의 4축 결정기준을 그대로 적용한다.

| 축 (§2.1) | 재무 도메인 판정 | 결론 신호 |
|---|---|---|
| 유형별 특화도 | **中** — 목표유형마다 강조 비율(저축률/투자배분/상환순서)은 다르나, **핵심 로직(소득-지출-목표 정합, 배분 합=100%, 리스크 성향 반영)은 공통**. 포맷 차이가 "입력 변수 + 산출 강조점" 수준. | 단일 쪽 |
| 포맷/유형 수 | 5종(저축/부채/투자/은퇴/비상금)이나, 실제 한 사용자의 종합 플랜은 **여러 목표를 동시에 한 배분 안에 담음**(전문가 1명에게 1유형만 라우팅하는 구조가 부자연) → 라우팅 분리가 오히려 통합 배분을 깨뜨림. | 단일 쪽 |
| 독립 진화 필요성 | 목표유형별 로직이 따로 진화하기보다 **하나의 배분 엔진이 함께 진화**(저축률 조정이 투자배분에 영향). 공통 로직 우세. | 단일 쪽 |
| 유지보수 우선순위 | ★ **단순성 우선** — expert N개 = 프롬프트 N벌 + 평가 N벌 + 라우팅 1벌 ≈ 관리 비용 N배(§2.1 임계 1줄). 재무 플랜의 특화 효용이 이 N배 비용을 넘지 못함. | 단일 쪽 |

- **결정**: ★ **단일 planning agent + 파라미터화 채택** (expert_pool 미채택). planning agent 가 `goal_types[]` + `risk_appetite` 를 입력 파라미터로 받아 한 번에 통합 배분 3안을 생성한다. 목표유형별 강조는 프롬프트 파라미터·산출 가중치로 처리.
- **단, 조건부 분리 agent 는 별도** — 목표유형 라우팅(expert_pool)과 **조건부 실행(conditional_execution)은 다른 축**이다. 부채 상환 우선순위(`debt_priority`)와 보험/비상금 검토(`insurance_review`)는 목표유형 전문가가 아니라 **"부채 있을 때만 / 부양가족 있을 때만" 실행되는 조건부 단계**다 → expert_pool 이 아니라 G3 conditional_execution 으로 표현(§2 agents).
- **미디어 편향 점검**: 팟캐스트(M1)도 포맷(솔로/인터뷰/패널)을 expert_pool 후보로 봤다가 단일 파라미터화로 결론냈다. 재무도 동일 결론이지만 **근거는 도메인 고유**(통합 배분이 유형 분리를 깨뜨림) — 미디어 결론을 복붙한 것이 아니라 §2.1 4축을 재무 데이터로 재평가했다.

---

## 2. agents[] (단계 3 — agent_template.md 개선본 기반, ★ G3 conditional_execution)

> Dreammate 4 agent(intent/planning/critic/rewriter) → 재무 6 agent. debt_priority / insurance_review 신규 + **조건부 실행**.
> ★ supervisor 패턴 → 모든 agent 의 forbidden_actions 에 "다른 agent 직접 호출 금지 (orchestrator 경유)" + **자문/보장/상품추천 발화 금지** 포함.

```yaml
agents:
  - name: intent
    responsibility: "의도 분석 (단일 목표 / 종합 가구 자동 분기 + Intent Filter + 자문 요청 거절 필터)"
    inputs: [user_message, locale, household_context]
    outputs: [intent_ok, mode(single|household), reason, missing_fields, has_debt, has_dependents]
    forbidden_actions:
      - 다른 agent 직접 호출 (orchestrator 경유)
      - plan 생성
      - RAG 직접 의존
      - 투자 자문/상품 추천 발화 (forbidden_scope — 자문 요청은 정보 안내로 전환 또는 거절)

  - name: planning
    responsibility: "재무 플랜 3안 생성 (parallel, 보수/중립/공격) — budget_allocation + savings_target + investment_mix[]. ★ 목표유형은 파라미터(goal_types[])로 통합 처리 (§1.2 단일 agent 결정)"
    inputs: [user_message, mode, goal_types, risk_appetite, rag_context, household_context]
    outputs: [plan_candidates x3]   # 각: budget_allocation, savings_target, investment_mix[] (합=100% 검증)
    forbidden_actions:
      - Critic 직접 호출 (orchestrator 경유)
      - 특정 금융상품/종목 지정 (forbidden_scope — 자산군 카테고리 비율만, 상품명 금지)
      - 원금 보장/수익률 약속 발화 (forbidden_scope)
      - 제3자(부양가족/수익자) 미제공 정보 날조 (llm_security)

  - name: debt_priority
    responsibility: "[부채 있을 때만] 부채 상환 우선순위 정보 플랜 생성 (avalanche/snowball 등 일반 정보 제시)"
    inputs: [debts(사용자 제공 잔액·금리), plan(selected), savings_target]
    outputs: [debt_repayment_plan]   # 우선순위 + 사유(고금리/소액) — 정보 제시
    forbidden_actions:
      - 다른 agent 직접 호출 (orchestrator 경유)
      - 특정 대출 상품/대환 상품 추천 (forbidden_scope)
      - 법률/세무 자문 (forbidden_scope)
    conditional_execution:                 # ★ G3 — agent_template conditional_execution 슬롯 행사
      condition: has_debt == true          # 부채가 있을 때만 실행. 무부채 사용자는 이 agent 스킵 (분기 소유 = orchestrator)

  - name: insurance_review
    responsibility: "[부양가족 있을 때만] 보험/비상금 필요보장 검토 (필요보장 정보 — 상품 추천 아님)"
    inputs: [household_context, dependents(제3자 PII — 마스킹), plan(selected), savings_target]
    outputs: [insurance_review]   # 필요보장 갭 정보 + 비상금 권장 개월수(일반 정보)
    forbidden_actions:
      - 다른 agent 직접 호출 (orchestrator 경유)
      - 특정 보험상품/보험사 추천 (forbidden_scope)
      - 수익자(beneficiary) 미제공 정보 날조 (llm_security — 제3자 PII 추측 금지)
      - 원금/보장 약속 발화 (forbidden_scope)
    conditional_execution:                 # ★ G3 — agent_template conditional_execution 슬롯 행사
      condition: has_dependents == true    # 부양가족이 있을 때만 실행. 1인 가구는 이 agent 스킵

  - name: critic
    responsibility: "플랜 적합성/리스크 평가 (canonical overall_score + dimensions: 목표정합/저축현실성/리스크적합성 등)"
    inputs: [plan_dict, debt_repayment_plan?, insurance_review?, risk_appetite]
    outputs: [overall_verdict, overall_score, dimensions]
    forbidden_actions:
      - plan 직접 수정 (rewriter 담당)
      - 다른 agent 직접 호출 (orchestrator 경유)
      - 적합성을 자문/권유로 전환 (forbidden_scope — 검토는 정합성 점검이지 권유 아님)

  - name: rewriter
    responsibility: "Critic verdict=revise 시 플랜 배분/저축률 개선 (max 2)"
    inputs: [plan_dict, verdict, critic_dimensions]
    outputs: [revised_plan]
    forbidden_actions:
      - 무한 revise (critic_max_revise=2 상한)
      - 다른 agent 직접 호출 (orchestrator 경유)
      - 원금 보장/상품 추천 발화 (forbidden_scope)
```

### 2.1 execution_policy 공통 (agent_template §execution_policy)
- timeout_ms: placeholder(예: 30000), max_retries: 2, graceful_on_failure: true (P-GRACEFUL-001 정신 — 외부 의존 실패 시 차단 0 + validation.warnings).
- ★ 조건부 agent(debt_priority/insurance_review): 조건 미충족 시 orchestrator 가 **스킵**(graceful — 산출물에 "해당 없음" 명시, 차단 0). 분기 소유 = orchestrator(supervisor 패턴) — agent 가 스스로 분기 트리거 금지.

---

## 3. skills[] (단계 4 — ★ G2 §4.1 신규 vs 재사용 결정트리 적용)

> ★ generation_workflow §4.1 결정트리를 **명시적으로 통과**. 기본값 = 재사용. 신규 생성은 무충돌 + 고유 가치 입증 시에만.

### 3.1 G2 §4.1 결정트리 통과 로그

```
검토 대상: 재무 도메인 절차 Skill 후보
1. 의도 작업 키워드 추출:
   - 재무 플랜 평가/회귀 → "eval 실행", "golden_set", "품질 평가"
   - 제3자 PII + 자문 발화 위협 검토 → "보안 검토", "security review", "PII"
   - agent IO drift → "agent IO 점검", "agent_io_contract"
   - 비용 점검 → "비용 검토", "LLM cost"
2. 기존 21 Skill description 키워드와 충돌 검사 (INDEX §사용원칙 5):
   - "eval 실행/golden_set/품질 평가" → 기존 eval-run 과 충돌 (4중첩)
   - "보안 검토/security review/PII" → 기존 security-review 와 충돌
   - "agent IO 점검/agent_io_contract" → 기존 agent-io-check 와 충돌
   - "비용 검토/LLM cost" → 기존 cost-review 와 충돌
3. 분기:
   - 모든 후보 = 충돌 발견 → ★ 기존 Skill 재사용 강제 (신규 생성 금지)
   - 신규 고유 가치 입증된 후보: 없음
   - → 신규 Skill 0 (YAGNI 차단: "재무 전용 finance-eval-run" 은 미래 수요만으로 정당화 불가 + eval-run 키워드 충돌)
```

- ★ **결론: 신규 Skill 0, 재사용 강제** (factory_contract 규칙 4 위반 0). 단계 8 라우터가 기존 Skill 로 안내.
- ★ **risk high 특수 효과**: `security-review` Skill 이 **재사용 강제 + 필수 경로**로 격상 (medium 이면 선택, high 는 강제 — domain_brief required_evals + 규칙 8).

```yaml
skills:
  # --- 재사용 (신규 0 — 키워드 충돌 0, G2 결정트리 "재사용 강제" 분기) ---
  - name: eval-run
    trigger_keywords: [eval 실행, golden_set, regression]
    applies_to: [agents]
    related_contracts: [output_schema]
    reuse: true                    # finance_planning_eval 실행도 eval-run 절차 재사용 (별도 Skill 불필요)

  - name: security-review
    trigger_keywords: [보안 검토, security review, PII 위협]
    applies_to: [agents, claude]
    related_contracts: [llm_security]
    reuse: true                    # ★ risk high → 제3자 PII + 자문 발화 위협 모델 검토에 필수 재사용 (규칙 8)

  - name: agent-io-check
    trigger_keywords: [agent IO 점검, agent_io_contract, I/O 검증]
    applies_to: [agents]
    related_contracts: [agent_io_contract, output_schema]
    reuse: true                    # 6 agent (2 조건부 포함) IO drift 검사

  - name: contract-change
    trigger_keywords: [contract 변경, schema 변경, breaking change]
    applies_to: [agents, claude]
    related_contracts: [전체]
    reuse: true

  - name: cost-review
    trigger_keywords: [비용 검토, LLM cost, token usage]
    applies_to: [agents, claude]
    related_contracts: [—]
    reuse: true                    # 3-plan parallel 비용 3배 점검

  # --- 신규 후보 (★ 채택 0 — G2 결정트리 충돌로 거부) ---
  - name: (없음 — 신규 Skill 후보 없음)
    note: >
      "finance-eval-run" / "finance-security-check" 등 도메인 특화 Skill 후보를 G2 §4.1 결정트리로 검토한 결과,
      전부 기존 eval-run / security-review 와 키워드 충돌(음의 효용) → 재사용 강제. 신규 0 권장.
      (도메인 데이터는 golden_set/finance_planning_eval 채점차원으로 표현하고, 절차 Skill 은 재사용.)
```

### 3.2 키워드 충돌 검토 (factory_contract 규칙 4 — 예비)
- 신규 Skill 0 → INDEX 기존 키워드와 충돌 0 (예비 판정). **실 검증은 S2 trigger_validation / skill conflict check.**

---

## 4. contracts[] (단계 5 — contract_template.md 개선본 기반, ★ 조건부 산출 cross-ref)

```yaml
contracts:
  - path: docs/contracts/agent_io_contract.md
    purpose: "6 agent (intent/planning/debt_priority/insurance_review/critic/rewriter) 입출력·실행 정책 + 조건부 실행"
  - path: docs/contracts/output_schema.md
    purpose: "Envelope / FinancialPlan(budget_allocation+savings_target+investment_mix[]) / DebtPlan / InsuranceReview / Critic 본문 + 비자문 디스클레이머 필드"
  - path: docs/contracts/db_schema.md
    purpose: "데이터 계층 (User→Household→FinancialGoal→Plan→Allocation + dependents + beneficiary + debts + feedback) + JSONB"
  - path: docs/contracts/llm_security.md
    purpose: "금융 PII(소득·자산·부채) + 제3자 PII(부양가족·수익자) 마스킹/날조 금지 + prompt injection 차단 + ★ 자문/원금보장/상품추천 발화 차단"
```

### 4.1 cross-reference 축 + ★ 조건부 산출 (contract_template §3 개선본)
```
agent_io_contract  ↔  output_schema     (6 agent 출력 ↔ 본문 스키마)
output_schema      ↔  db_schema         (FinancialPlan/Allocation JSONB ↔ plans/allocations 테이블 컬럼)
api_contract*      ↔  apps/web types     (* 후속 — API 계약은 phase 진행 시)
db_schema          ↔  db/migrations      (테이블 ↔ migration — 런타임 미생성, 설계만)

조건부 산출(conditional output) — contract_template §3 열:
  debt_repayment_plan   → 조건부 산출: has_debt == true 일 때만 (debt_priority agent conditional_execution 정합)
  insurance_review      → 조건부 산출: has_dependents == true 일 때만 (insurance_review agent conditional_execution 정합)
  plan_candidates       → 항상 산출 (—)
```
- ★ 실 정합 검증은 S2 contract_consistency. 조건부 산출 축은 G3 conditional_execution 과 1:1 정합.

---

## 5. evals[] (단계 6 — eval_template.md 개선본 기반, ★ G4 applies_when 조건부 차원)

```yaml
evals:
  - path: eval/golden_set.md
    purpose: "회귀 케이스 (FP-001~ : 단일목표/종합가구/부채有/부양가족有/은퇴/비상금/세금모드). case_id 고정, priority P0/P1/P2"
  - path: eval/regression_eval.md
    purpose: "mock-deterministic CI 회귀 (비용 0)"
  - path: eval/finance_planning_eval.md
    purpose: "도메인 채점 차원 (아래 §5.1)"
  - path: eval/human_review_rubric.md
    purpose: "★ risk high 강제 — 사람 검토 (리스크 적합성/자문경계 정성 판단)"
  - path: eval/security_review.md
    purpose: "★ risk high 강제 — 제3자 PII 마스킹/날조 + 자문/보장/상품추천 발화 차단 위협 모델 (규칙 8)"
```

### 5.1 채점 차원 (eval_template §B 개선본 — 도메인별 정의 + ★ G4 applies_when 조건부 차원)
> Dreammate 8차원을 재무로 변환 + 조건부 차원:

| Dreammate | 재무 대응 | applies_when (G4) |
|---|---|---|
| intent_fit | goal_fit (목표-플랜 정합) | — (무조건) |
| target_clarity | profile_clarity (재무 프로필 반영) | — (무조건) |
| hook_strength | actionability (실행 가능성/구체성) | — (무조건) |
| message_clarity | clarity (설명 명료성) | — (무조건) |
| structure | allocation_coherence (배분 합=100%·내부 정합) | — (무조건) |
| feasibility | savings_realism (저축률 현실성 vs 소득-지출) | — (무조건) |
| brand_consistency | risk_appetite_fit (리스크 성향 적합성) | — (무조건) |
| differentiation | plan_differentiation (3안 보수/중립/공격 차별성) | — (무조건) |
| (신규) | advisory_boundary_compliance (자문/보장/상품추천 발화 0) | — (무조건, ★ 도메인 금지 게이트) |
| (신규) | debt_priority_soundness (부채 우선순위 합리성) | **applies_when: has_debt == true** |
| (신규) | insurance_adequacy (필요보장 검토 적정성) | **applies_when: has_dependents == true** |
| (신규) | tax_efficiency (세금 최적화 고려) | **applies_when: mode includes tax_optimization** |

→ 무조건 9차원 + 조건부 3차원(applies_when). ★ **G4 핵심**: 조건부 차원은 미해당 케이스에서 **평균 계산에서 제외**(차원 수를 적용 차원만으로 셈) — 무부채 사용자의 plan 을 debt_priority_soundness 0점으로 끌어내리지 않음. 세금최적화 모드 아닐 때 tax_efficiency 제외.

### 5.2 임계값 (eval_template §C / eval-run §6 정합)
- schema 준수율 < 100% → 즉시 fail; 평균 점수 하락 > 0.3 → fail+사람검토; 비용 증가 > 30% → cost-review; latency > 20% → 경고; ★ **advisory_boundary 차단 단어(자문/보장/상품추천) 검출 > 0% → 즉시 fail** (도메인 금지 게이트 — 차단 단어 규칙을 재무 자문 발화로 확장).

---

## 6. phases[] (단계 7 — phase_template.md 기반, ★ non_goals ← forbidden_scope 매핑)

```yaml
phases:
  - phase_name: phase-F0-foundation
    goals: [데이터 계층 설계(User→Household→FinancialGoal→Plan→Allocation), output_schema/db_schema 초안, 비자문 디스클레이머 필드]
    non_goals: [투자 자문/상품 추천, 실제 거래/계좌 연동]      # ← forbidden_scope
    acceptance: [4 contract 초안 존재, db_schema ↔ output_schema cross-ref 0 drift, 제3자 PII 엔티티(dependents/beneficiary) 마스킹 설계]

  - phase_name: phase-F1-mvp-planning
    goals: [intent + planning(3-plan 보수/중립/공격) + critic + rewriter MVP, golden_set FP-001~ 정의]
    non_goals: [부채/보험 (F2), 자동 promotion, 세무·법률 자문]   # ← forbidden_scope
    acceptance: [golden_set 회귀 PASS, schema 준수 100%, revise max 2 차단, ★ advisory_boundary 차단 단어 0% 게이트]

  - phase_name: phase-F2-conditional-modules
    goals: [debt_priority + insurance_review 조건부 agent, debt_priority_soundness/insurance_adequacy 차원 추가]
    non_goals: [특정 대출·보험 상품 추천, 수익자 정보 외부 발송]   # ← forbidden_scope
    acceptance: [조건부 e2e(has_debt/has_dependents 분기), ★ 제3자 PII 마스킹(llm_security) 검증, security-review 통과]

  - phase_name: phase-F3-eval-hardening
    goals: [finance_planning_eval 9+3차원 정식화, human_review_rubric, regression CI 게이트, ★ security_review eval]
    non_goals: [Plan Memory 자동 추출]   # ← forbidden_scope (후속)
    acceptance: [eval-run 임계값 게이트 통과, ★ human_review + security_review 강제 통과(risk high), applies_when 조건부 차원 평균 제외 동작]

  - phase_name: phase-F4-plan-memory (후속)
    goals: [Plan Memory 추출(피드백→candidate, rag-update 5단계 경유)]
    non_goals: [사람 검토 없는 자동 승격, 제3자 PII 의 Memory 무단 보존]   # ← forbidden_scope (규칙 8)
    acceptance: [candidate→approved 승격 사람 검토 게이트, security-review 통과(제3자 PII)]
```

> ★ phase entry 8 files 는 실 phase 진입 시 생성 — 본 blueprint 는 goals/non_goals/acceptance 만 (proposal 단계).

---

## 7. routing_docs[] (단계 8)

```yaml
routing_docs:
  - AGENTS.md       # 구현/QA 모델 라우터 (agent-io-check / eval-run / qa-check / bug-triage / cost-review 등)
  - CLAUDE.md       # 기획/설계 모델 라우터 (ai-architecture-review / contract-change / security-review / harness-factory 등)
```
- 라우터는 본문 지침이 아니라 작업 유형별 참조 문서 + Skill 안내. applies_to 태그로 역할 분리 (Dreammate 정신 계승). ★ risk high → security-review 가 양 라우터에서 강조됨.

---

## 8. ★ 관찰 / 범용성 신호 / 새 GAP 후보 (dry-run 목적 = 범용성 2차 검증)

> M1 6 GAP(G1~G6) + M2 추가(G7/G8)가 **이질 도메인에서 정상 작동하는지** 확인 + 새 GAP 후보 발굴.

| # | 관찰 | 판정 |
|---|---|---|
| ✅ G1 (expert/단일) | 목표유형별 expert_pool vs 단일 파라미터화 판단을 §2.1 4축으로 **사전 결정**. 미디어(포맷) 결론을 재무(목표유형)에 복붙하지 않고 도메인 고유 근거("통합 배분이 유형 분리를 깨뜨림")로 단일 채택 → **G1 범용 작동**. | machinery 정상 |
| ✅ G2 (skill 재사용) | §3.1 결정트리로 신규 0 / 재사용 강제 명시 통과. risk high 가 security-review 를 "재사용 강제 필수"로 격상하는 케이스 추가 발견 → **G2 범용 + high 특수경로 확인**. | machinery 정상 |
| ✅ G3 (conditional) | debt_priority(has_debt) / insurance_review(has_dependents) 2 조건부 agent 를 conditional_execution 으로 표현. 팟캐스트(mode==guest 1축)보다 **조건축 2개 + 데이터 트리거(has_debt/has_dependents)** 로 더 풍부 → **G3 범용 + 표현력 충분**. | machinery 정상 |
| ✅ G4 (applies_when) | 조건부 차원 3개(debt/insurance/tax) applies_when 표현 + 평균 제외. 팟캐스트(+2)보다 많고 **mode 외 데이터 조건(has_debt)도 applies_when 으로 표현 가능** 확인 → **G4 범용**. | machinery 정상 |
| ✅ G5 (제3자 PII) | 부양가족 + 수익자 = 제3자 PII 2종 → 트리거가 **실제 medium→high 상향**으로 귀결(팟캐스트는 상향 후보에 그침). 금융 민감정보 결합으로 high 강제 경로(human_review+security_review) 작동 → **G5 범용 + 상향 실귀결 시연**. | machinery 정상 |
| ✅ G6 (data_model) | User→Household→FinancialGoal→Plan→Allocation 5계층 + 9 엔티티 + PII 표시를 data_model 1급 필드로 표현. 미디어 계층 완전 치환 성공 → **G6 범용 (계층 구조가 도메인 무관하게 표현됨)**. | machinery 정상 |
| ✅ G7 (harness_status) | project_state_draft 에 harness_status: dry-run-blueprint 적용 (§scaffold). | machinery 정상 |
| ✅ G8 (pending-by-design) | §9 validation 에 pending-by-design + sub-status 적용. | machinery 정상 |
| ⚠ NEW-G9 후보 | **forbidden_scope = "도메인 자체 금지(규제)"** 와 **forbidden_scope = "scope creep(MVP 제외)"** 가 한 필드에 혼재. 재무는 투자자문/원금보장/상품추천/세무자문이 **법적·규제 금지**(MVP 후순위가 아니라 영구·법적 금지)인데, schema 는 둘을 구분하지 않음. eval 의 advisory_boundary_compliance 같은 **하드 게이트 차원**으로 강등 표현했으나, domain_brief 단계에서 "regulatory_forbidden vs deferred_scope" 구분 필드가 있으면 더 안전. | domain_brief_schema 후보 GAP (S2 입력) |
| ⚠ NEW-G10 후보 | risk_level 이 **단일 enum(low/medium/high)**. 재무는 "PII 위험(high)"과 "규제·자문 위험(별도 축)"이 다른 종류인데 한 등급에 압축됨. risk 를 **축 분해(data_risk / regulatory_risk)** 하면 G5 트리거와 NEW-G9 를 더 정밀히 연결 가능. | domain_brief_schema 후보 GAP (S2 입력) |

> 이 관찰은 S2 validation 6검증 + with/without 비교의 입력. ★ G1~G8 전부 이질 도메인에서 정상 작동 확인 = **범용성 2차 검증 PASS 신호**. NEW-G9/G10 은 재무(규제 도메인) 고유로 발굴된 신규 GAP 후보.

---

## 9. validation (★ 3 필드 = pending / pending-by-design — S2 가 수행, G8 enum 행사)

```yaml
validation:
  trigger_validation: pass               # ★ S2 검증 1 PASS — 재사용 5 Skill 트리거 정합 + 신규 0 → false trigger 0 + 6 agent supervisor 정합(직접 호출 금지). (정적 정합 PASS, 런타임 트리거 실측 미수행 — sample_test_finance_validation.md §A1)
  contract_consistency: pass             # ★ S2 검증 3 PASS — 4 cross-ref 축 + 조건부 산출 축(debt has_debt / insurance has_dependents) drift 0, G3 양면 정합. GAP-flag 없음. (§A3)
  with_without_skill_eval: pass / pending-by-design  # ★ S2 검증 4 — 누락률 PASS(WITH 누락0 ≪ WITHOUT 누락6, §E) / 품질·일관성 = pending-by-design(실 LLM 미호출 dry-run 정상, G8). (§A4)

# ★ G8 enum 행사 (harness_blueprint_schema §3.1 Validation — pending vs pending-by-design 구별):
#   eval_run_integration: pending-by-design   # 검증5 — 절차/임계값/케이스 매핑 전부 적용 가능 / 실 LLM 호출 실측만 미수행 = dry-run 정상
#                                             #   (단순 pending(미완)이 아니라 "dry-run 범위상 정상 미측정")
#   with_without_skill_eval 도 S2 에서 차원별 sub-status 예상: 누락률=pass(정량) / 품질·일관성=pending-by-design(소표본·실측 미수행)
```

> factory_contract 규칙 7: validation 필드가 어떤 상태든 본 blueprint 는 **사용자 승인 전 active 아님**. outputs/TEST/finance/ 에 격리. S1(generation)은 validation 을 pending/pending-by-design 슬롯으로만 두고, 실 6검증은 S2(validation)가 수행한다.
> ★ G8 적용 의미: 검증 5(eval-run 연동)는 실 LLM 미호출이 **정상**인 dry-run → `pending`(미완)이 아니라 `pending-by-design`(정상 미측정)으로 사전 표기. M1 이 단순 PENDING 으로만 기록하던 것을 enum 확장으로 명시.

---

이 blueprint 는 meta_factory machinery 개선본(generation_workflow 11단계 + G1 expert/단일 결정기준 + G2 skill 재사용 결정트리 + harness_blueprint_schema G8 + 6 templates G3/G4/G7)을 이질 도메인(개인 재무 플래닝)에 적용하여 작성됨 (WITH arm, 범용성 2차 검증).
