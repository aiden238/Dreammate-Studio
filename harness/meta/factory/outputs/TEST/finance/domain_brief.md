# domain_brief — personal_finance_planning_ai (WITH 입력)

> 위치: `harness/meta_factory/outputs/TEST/finance/domain_brief.md`
> 상태: Phase M3 (Meta-Factory 이질 도메인 dry-run) Slice S1 — generation dry-run **입력 명세**
> 형식: `meta_factory/domain_brief_schema.md` **개선본** (11 필드 + G6 data_model 선택 필드)
> 입력 도메인: 개인 재무 플래닝 AI (★ 이질 도메인 — planning-shaped, 미디어/콘텐츠 무관)
> ★ dry-run 테스트 자료 — active 하네스 아님 (outputs/TEST/finance/ 격리, factory_contract 규칙 3/7)
> ★ 자격증명/API 키/실 금융 알고리즘 없음 — 하네스 설계 placeholder 만.

---

## 0. 이 문서의 위치

`domain_brief_schema.md` **개선본** 형식을 그대로 따라 작성한 **개인 재무 플래닝 AI** 도메인 입력 명세.
generation_workflow 단계 1(domain_brief 수집)의 산출. 단계 2~11 이 이 brief 를 입력으로 harness_blueprint 를 설계한다.

이 도메인은 M1(팟캐스트, 미디어 인접)·M2(영상기획 baseline)와 **이질**이다 — 미디어/콘텐츠 생성이 아니라 **개인 재무 목표 → 예산·저축·투자배분 플랜 생성 + 리스크/적합성 검토**의 planning-shaped 도메인. 범용성 2차 검증이 목적: machinery 가 미디어 편향 없이 이질 도메인을 표현할 수 있는가.

- 공통(planning-shaped 골격): 입력 의도 분석 → 부족 정보 질문 → 후보 N개 생성 → 검토(Critic) → revise → 저장.
- 차이: 콘텐츠 후킹/대화흐름 → 예산 적정성/저축률/리스크 적합성; 게스트(제3자 PII) → **부양가족/수익자(제3자 PII)**; 영상 segment → 예산/저축/투자배분 Allocation.

---

## 1. domain_brief (schema 11 필드 — YAML)

```yaml
domain_name: personal_finance_planning_ai
domain_summary: "개인 재무 목표(저축/부채상환/투자배분/은퇴/비상금)를 입력받아 예산·저축·투자배분 플랜 3안을 생성하고 리스크/적합성을 검토하는 정보·기획 도구 (투자 자문·상품 추천 아님)"

target_users:
  - 재무 목표를 정리하려는 개인 (월급 생활자/프리랜서)
  - 가구 단위 재무를 계획하는 가장 (부양가족 있는 가구)
  - 부채 상환 + 저축 병행 계획이 필요한 사용자

primary_tasks:
  - 의도 분석 (단일 목표 정리 / 종합 가구 재무 플랜 자동 분기 — Quick / Discovery 대응)
  - 부족 정보 질문 (소득·고정지출·부채 유무·부양가족 유무·목표 우선순위·리스크 성향)
  - 재무 플랜 3안 생성 (각: 예산 배분 + 저축 목표 + 투자배분 비율 — 보수/중립/공격 톤)
  - [부채 있을 때만] 부채 상환 우선순위 플랜 생성 (avalanche/snowball 등 정보 제시)
  - [부양가족 있을 때만] 보험/비상금 검토 (필요보장 정보 — 상품 추천 아님)
  - 리스크/적합성 검토 (Critic: 목표-플랜 정합성/저축률 현실성/리스크 성향 적합성)
  - 결과 저장 + 사용자 피드백 (Plan Memory 추출은 후속 phase)

output_artifacts:
  - 재무 플랜 후보 (plan_candidates 3안 — budget_allocation + savings_target + investment_mix[])
  - 부채 상환 우선순위 플랜 (debt_repayment_plan — 조건부: 부채 있을 때만)
  - 보험/비상금 검토 (insurance_review — 조건부: 부양가족 있을 때만)
  - 적합성/리스크 검토 (Critic canonical overall_score + dimensions)
  - 선택/피드백 기록
  - ★ 모든 산출물에 비자문 디스클레이머 (정보·기획용, 투자 자문/원금 보장 아님 — forbidden_scope 정합)

runtime_type: product_saas        # FastAPI/Next/DB 런타임을 갖는 제품 SaaS (Dreammate 와 동형 가정)

# ★ G5 적용 (domain_brief_schema §1.1 제3자 PII risk 상향 트리거):
risk_level: high                  # ★ medium → high 상향 (아래 §G5 판정). 제3자(부양가족/수익자) PII + 금융 민감정보(소득·자산·부채)
                                  #    → high 상향 시 required_evals 에 human_review + security-review 강제 (factory_contract 규칙 8)

required_contracts:
  - agent_io_contract             # MOA agent 입출력/실행 정책 (intent/planning/critic/rewriter + debt/insurance 조건부)
  - output_schema                 # Envelope / FinancialPlan(budget+savings+investment_mix) / DebtPlan / InsuranceReview / Critic 본문
  - db_schema                     # 데이터 계층 (User→Household→FinancialGoal→Plan→Allocation + dependents + beneficiary + feedback)
  - llm_security                  # 금융 PII 마스킹(소득·자산·부채 + 제3자 부양가족/수익자) + prompt injection 차단 + 자문 발화 차단

required_evals:
  - golden_set                    # 회귀 케이스 (FP-001~ : 단일목표/종합가구/부채有/부양가족有/은퇴/비상금)
  - regression_eval               # mock-deterministic CI 회귀 (비용 0)
  - finance_planning_eval         # 도메인 채점 차원 (목표정합/저축현실성/리스크적합성 등 — §G6 연결)
  - human_review_rubric           # ★ risk high → 사람 검토 강제 (적합성/리스크 정성 판단)
  - security_review               # ★ risk high → 제3자 PII + 자문 발화 위협 모델 검토 강제 (factory_contract 규칙 8)

forbidden_scope:                  # ★ 필수 — 이 하네스가 하지 않는 것 (scope creep + 규제 리스크 차단)
  - 투자 자문/투자 권유            # ★ 도메인 자체 금지 — 정보·기획 도구 한정 (자문업 아님)
  - 원금 보장/수익률 약속          # ★ 도메인 자체 금지 — 어떤 보장 발화도 금지
  - 특정 금융상품 추천 (종목/펀드/보험상품 지정)  # ★ 도메인 자체 금지 — 일반 정보·카테고리만
  - 세무/법률 자문                # ★ 도메인 자체 금지 — 전문 자격 영역 제외
  - 실제 거래/이체/계좌 연동 자동화  # 사람 행위·외부 액션 — AI 가 실행 금지
  - 자동 promotion (사람 검토 없이 RAG/Memory 승격)  # rag-update 5단계 경유 (factory_contract 규칙 8)
  - Plan Memory 자동 추출          # 후속 phase (Dreammate Brand Memory Phase 10+ 대응)

preferred_architecture_patterns:  # architecture_patterns.md 6 패턴에서만 선택
  - supervisor                    # orchestrator 중개 (agent 격리 + 자문 발화 정책 일관 적용)
  - fan_out_fan_in                # 플랜 3안 (보수/중립/공격) parallel 생성
  - producer_reviewer             # Planner → Critic(적합성/리스크) → Rewriter (revise max 2)
  - pipeline                      # Intent → (RAG) → Planning → [Debt] → [Insurance] → Critic → Save
  # expert_pool 은 §G1(blueprint) 에서 결정기준으로 채택/미채택 판단 — 여기선 후보로도 명시하지 않음(단일 파라미터화 가설)

# ★ G6 적용 (domain_brief_schema §1.2 data_model 선택 필드 — 계층/엔티티/PII 를 schema 안 1급 표현):
data_model:
  hierarchy: "User → Household → FinancialGoal → Plan → Allocation"
  entities: [User, Household, Dependent, Beneficiary, FinancialGoal, Debt, Plan, Allocation, Feedback]
  pii:                            # 각 엔티티 PII 표시 (★ 제3자 PII 명시 — §1.1 risk 상향 트리거와 연결)
    User: 사용자 PII (계정/소득/자산/부채 — 금융 민감정보)
    Household: 가구 구성 (가구원 수/형태)
    Dependent: ★ 제3자(비사용자) PII — 부양가족 이름·연령·관계·건강/소득 의존도 (동의·노출 책임 ↑, risk 상향 트리거)
    Beneficiary: ★ 제3자(비사용자) PII — 수익자 이름·관계·지정 비율 (보험/유산 맥락, 동의·노출 책임 ↑)
    FinancialGoal: 사용자 PII (목표 금액/시점)
    Debt: 사용자 PII (부채 잔액/금리 — 금융 민감정보)
    Feedback: 사용자 PII (선택/수정 요청)
```

---

## 2. 데이터 계층 (User → Household → FinancialGoal → Plan → Allocation)

```
User                  사용자 계정 (소득·자산·부채 — 금융 민감 PII)
 └─ Household          가구/부양가족 컨텍스트 (가구원·형태)
     ├─ Dependent      ★ 부양가족 (제3자 PII — 이름·연령·관계·의존도, 마스킹 대상)
     ├─ Beneficiary    ★ 수익자 (제3자 PII — 이름·관계·지정 비율, 마스킹 대상)
     └─ FinancialGoal  재무 목표 (저축/부채상환/투자배분/은퇴/비상금)
         ├─ Debt       부채 항목 (잔액·금리 — 조건부 상환 우선순위의 입력)
         └─ Plan       플랜 후보 (3안: 보수/중립/공격 → 1안 선택)
             └─ Allocation  배분 항목 (예산 카테고리/저축률/투자배분 비율)
         └─ Feedback   사용자 피드백 (선택/수정 요청)
```

- Dreammate 4계층(User→Brand→Domain→Series→Video) 대비: 미디어 계층(Brand/Show/Episode)이 **재무 계층(Household/FinancialGoal/Plan/Allocation)**으로 완전히 치환됨. `Dependent`/`Beneficiary` 가 **제3자 PII 신규 엔티티** (영상기획·팟캐스트엔 없던 가구 부양 맥락).
- ★ 팟캐스트는 제3자 PII 가 `Guest` 1종이었으나, 재무는 `Dependent` + `Beneficiary` **2종 + 의료/금전 의존 맥락** → 제3자 PII 위험이 한 단계 더 짙음.

---

## 3. 핵심 흐름

```
사용자 입력 (재무 목표 or 가구 종합 재무 상황)
  → 의도 분석 (단일 목표 / 종합 가구 자동 분기 + Intent Filter + 자문 요청 거절 필터)
  → 부족 정보 질문 (소득·고정지출·부채 유무·부양가족 유무·리스크 성향)
  → 한 줄 기획 방향 승인
  → (RAG: 일반 재무 정보/가이드 참고 — graceful skip, 상품·종목 데이터 아님)
  → 재무 플랜 3안 생성 (parallel — 보수/중립/공격)
  → [부채 있을 때만] 부채 상환 우선순위 플랜
  → [부양가족 있을 때만] 보험/비상금 필요보장 검토
  → Critic 검토 (목표정합/저축현실성/리스크적합성) → revise 최대 2회
  → 결과 저장 (+ 비자문 디스클레이머) → 사용자 피드백 저장
```

---

## 4. 필요한 agent / skill / contract / eval 후보

| 종류 | 후보 | 비고 |
|---|---|---|
| agent | intent, planning, debt_priority, insurance_review, critic, rewriter | Dreammate 4 → 6 (debt_priority/insurance_review 조건부 신규) |
| skill | 기존 21 Skill 재사용 (eval-run / contract-change / agent-io-check / security-review / cost-review 등) | ★ 신규 Skill 0 가설 — S2 with-without 검토. ★ risk high → security-review 재사용 강제 |
| contract | agent_io_contract, output_schema, db_schema, llm_security | §1 required_contracts |
| eval | golden_set, regression_eval, finance_planning_eval, human_review_rubric, security_review | §1 required_evals (★ high → security 강제) |

> ★ 후보는 단계 2~7 에서 harness_blueprint 로 구조화된다 (다음 파일).

---

## 5. 작성 규칙 점검 (domain_brief_schema §3)

1. ✅ forbidden_scope 필수 — 7 항목 명시 (★ 4 항목이 **도메인 자체 금지**: 투자자문/원금보장/상품추천/세무·법률자문).
2. ✅ **risk_level: high → required_evals 에 human_review + security_review 강제** (규칙 8 정합) — 충족 (§G5 트리거로 도출).
3. runtime_type: product_saas → 런타임 contract 필요 — 충족.
4. ✅ preferred_architecture_patterns 는 6 패턴에서만 선택 (supervisor/fan_out_fan_in/producer_reviewer/pipeline; expert_pool 은 blueprint §G1 결정기준에 위임).
5. ✅ 사람이 작성 (meta_factory 자동 생성 아님 — proposal-first).

---

## §G5. 제3자 PII risk 상향 트리거 적용 (domain_brief_schema §1.1)

> ★ G5 개선 슬롯을 **이질 도메인에서 적극 행사**. 팟캐스트(M1)는 트리거를 "medium 유지 + 상향 후보 명시" 로 보수 적용했으나, 재무는 트리거를 **실제 등급 상향(medium → high)**으로 행사한다.

- **트리거 발동 조건**: `data_model.pii.Dependent` 와 `data_model.pii.Beneficiary` 가 **제3자(비사용자) PII** 로 표시됨 → §1.1 제3자 PII 상향 트리거 충족.
- **재판정 근거**:
  - 사용자 PII 만 가정하면 medium (소득·자산은 사용자 본인 정보).
  - 그러나 (a) **부양가족·수익자 = 제3자 PII** (동의·노출 책임이 사용자 PII 보다 큼) + (b) 부양가족은 **연령·건강/소득 의존도** 등 민감 카테고리 인접 + (c) **금융 민감정보(소득·자산·부채)** 자체가 노출 시 피해 큼 → 두 축이 겹쳐 **`medium → high` 상향**.
- **상향 효과** (factory_contract 규칙 8 정합):
  - required_evals 에 `human_review_rubric` + `security_review` **강제 포함** (medium 이면 권장이었으나 high 는 강제).
  - llm_security contract 가 제3자 PII 마스킹/날조 금지 + 자문 발화 차단을 1급으로 다룸.
- ★ 팟캐스트 대비 차이: M1 은 제3자 PII 1종(Guest)으로 "상향 후보"에 그쳤으나, 재무는 제3자 PII 2종 + 금융 민감정보 결합 → **트리거가 실제 등급 상향으로 귀결**되는 케이스를 시연. G5 가 미디어 외 도메인에서도 정상 작동함을 검증.

---

이 domain_brief 는 meta_factory machinery(domain_brief_schema **개선본** — G5 제3자 PII 트리거 + G6 data_model 필드)를 참조하여 작성됨 (WITH arm, 이질 도메인).
