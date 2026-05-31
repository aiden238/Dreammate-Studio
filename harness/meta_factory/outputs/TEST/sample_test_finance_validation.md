# sample_test_finance_validation.md — Phase M3 Slice S2 검증 리포트

> 위치: `harness/meta_factory/outputs/TEST/sample_test_finance_validation.md`
> 상태: Phase M3 (Meta-Factory 이질 도메인 dry-run) Slice S2 — validation (S1 산출 finance blueprint 평가 + M2 개선 8요소 이질 도메인 유효성 + 범용성 판정 + 분기 권고)
> 입력(읽기 전용): `outputs/TEST/finance/{harness_blueprint, domain_brief, _without_baseline}.md` + `scaffolds/*`
> machinery(읽기만): `meta_factory/validation_workflow.md`(6검증) + `factory_contract.md` + `harness_blueprint_schema.md`(G8) + `domain_brief_schema.md`(G5·G6) + `architecture_patterns.md`(G1) + `generation_workflow.md`(G2 §4.1) + `templates/{agent,contract,eval,project_state}_template.md`(G3·G4·G7)
> Skill cross-ref: `.claude/skills/eval-run/SKILL.md`(검증5) + `.claude/skills/INDEX.md`(검증2)
> baseline 비교(읽기만): `outputs/TEST/sample_test_podcast_validation.md`(M1, 인접 도메인) + `sample_test_podcast_revalidation.md`(M2) + `podcast_eval_run_sample.md`(M2 eval 표본)
> ★ 목적: "성공" 이 아니라 **machinery 가 이질 도메인을 검증·표현할 수 있는가 + M2 개선의 범용 실효성 + 새 GAP + 분기 권고**. fail/pending/expressible 은 정상 결과.
> ★ 런타임 0 (A9) — 실 LLM 호출 / 실측 점수 없음. machinery 0줄 변경. 본 리포트는 blueprint 문서를 평가할 뿐.

---

## 0. 요약 (TL;DR)

| 항목 | 결과 |
|---|---|
| 6검증 분포 | **PASS 4 (검증1·2·3·6) / PENDING-BY-DESIGN 2 (검증4 품질·일관성 차원 / 검증5)** — 검증4 누락률 차원은 PASS |
| ★ M2 G1~G8 유효성 | **유효 7 (G1·G2·G4·G5·G6·G7·G8) / 부분 1 (G3 — enum 전제 대비 불리언 데이터조건 표현은 작동하나 schema 주석은 enum 예시만 = 표현은 유효·문서화는 부분)** / 부적합 0 |
| ★ 범용성 판정 | **범용 강함** — 미디어 hook/3-variant 창의다양성/썸네일 류 강요 0. blueprint 가 재무 고유(리스크/적합성/규제 forbidden/수치 합=100%)로 재정의됨 |
| ★ 새 GAP | **NEW-G9 유효 (minor)** / **NEW-G10 유효하나 부분중복 (nice-to-have)** / **NEW-G11 신규 발견 (nice-to-have)** — blocking 0 |
| with/without 누락률 | WITH 우세 (누락 0/6, forbidden 1/0, gate 1/0) — §E |
| blueprint validation 3필드 최종값 | trigger_validation=**pass** / contract_consistency=**pass** / with_without_skill_eval=**pass (누락률) / pending-by-design (품질·일관성)** |
| ★★ 분기 권고 | **Phase 10 직행 가능** — 범용 강함 + 새 GAP 전부 minor/nice-to-have (백로그로 충분, Phase 10 막지 않음) |
| 금지 위반 | **0** — machinery 0줄 변경 / 변경 전부 outputs/TEST/finance/ + 본 리포트 / `사진/` 무시 |

> ★ blueprint 가 6검증을 통과(또는 pending-by-design)해도 **사용자 승인 전 active 아님** (factory_contract 규칙 7, generation_workflow 단계 11). S2 는 검증만 수행하며 active 전환을 하지 않는다.

---

## A. 6 검증 실행 (validation_workflow.md 그대로)

### 검증 1 — trigger validation → **PASS** (G2 결정트리 강화 + supervisor 정합)

> 질문: 필요한 Skill/agent 가 의도 상황에 켜지고, 무관 상황에 안 켜지는가.

**(a) 켜져야 할 Skill 이 켜지는가 (description 키워드 매칭 dry-run)**

| 의도 작업 상황 | 켜져야 할 Skill | 트리거 키워드 매칭 (INDEX) | 결과 |
|---|---|---|---|
| 재무 플랜 회귀/품질 평가 | eval-run | "eval 실행"/"golden_set"/"regression"/"품질 평가" (blueprint §3) | ✅ 켜짐 |
| ★ 제3자 PII + 자문 발화 위협 검토 | security-review | "보안 검토"/"prompt injection"/"privacy" (risk high → 재사용 강제 §3.1) | ✅ 켜짐 |
| 6 agent IO drift 검사 | agent-io-check | "agent IO 점검"/"agent_io_contract"/"I/O 검증" | ✅ 켜짐 |
| contract/스키마 변경 | contract-change | "contract 변경"/"schema 변경" | ✅ 켜짐 |
| 3-plan parallel 비용 점검 | cost-review | "비용 검토"/"LLM cost"/"token usage" | ✅ 켜짐 |
| phase 진입/종료, 회고 | phase-start / phase-complete / meta-retrospective | (재사용, §7 라우터 안내) | ✅ 켜짐 |

**(b) 켜지면 안 되는 Skill (false trigger 0)**

- blueprint 는 **신규 Skill 0** (§3). 신규 키워드로 인한 false trigger 경로 자체가 없음 → false trigger **0**.
- 범위 밖 요청(실제 거래/이체/계좌 연동 자동화, 종목·펀드·보험상품 지정 추천, 세무·법률 자문)은 forbidden_scope 영역으로 어떤 Skill description 키워드와도 매칭되지 않음 → false trigger 0. (★ intent agent 가 "자문 요청은 정보 안내로 전환 또는 거절" — forbidden_actions, blueprint §2 — 으로 흡수하므로 Skill 트리거가 아니라 agent 게이트로 처리됨.)

**(c) agent 트리거 ↔ architecture_pattern 정합 (supervisor)**

- 6 agent **전부** forbidden_actions 에 "다른 agent 직접 호출 (orchestrator 경유)" 명시 (blueprint §2, agent_draft). → supervisor 패턴 "agent 직접 호출 트리거 부재"(검증1 절차 3) **충족**.
- 조건부 agent(debt_priority/insurance_review)의 분기는 `has_debt`/`has_dependents` 데이터 트리거인데, 이 분기는 **orchestrator 가 소유**(agent 자율 트리거 0 — agent_draft §3, execution_policy 2.1) → supervisor 정합.

**판정 근거**: 켜져야 할 것 100% 트리거 (재사용 Skill 매칭 정상) AND 켜지면 안 될 것 0 false trigger (신규 0 + forbidden_scope agent 게이트) AND agent 트리거 supervisor 정합 → **PASS**.
> ⚠ 단서: dry-run 정적 검사(키워드 문자열 대조)로 판정. 실 Claude Code 자동 트리거 행위는 실행 미수행 → "정적 정합 PASS, 런타임 트리거 실측 미수행". (M1·M2 와 동일 단서.)

---

### 검증 2 — skill conflict check → **PASS** (G2 §4.1 결정트리로 4 후보 사전 차단)

> 질문: blueprint 제안 Skill 키워드가 기존 21 Skill description 키워드와 충돌하는가 (INDEX 규칙).

**(a) 채택 Skill 의 충돌 (실제 blueprint)**

- blueprint 가 **채택**한 Skill 은 전부 기존 21 Skill 재사용 (eval-run / security-review / agent-io-check / contract-change / cost-review + 라우터 안내). 신규 키워드 도입 0 → INDEX §사용원칙 5("같은 description 키워드 둘 이상 = 충돌") 위반 **0**.

**(b) S1 이 G2 §4.1 결정트리로 사전 거부한 4 후보 (skill_draft §1 — 채택 안 함)**

| 신규 Skill 후보 | 추출 키워드 | 기존 충돌 (INDEX) | 분기 |
|---|---|---|---|
| finance-eval-run | "eval 실행"/"golden_set"/"품질평가" | eval-run (#6) 4중첩 | ❌ 충돌 → 재사용 강제 |
| finance-security-check | "보안 검토"/"PII"/"security review" | security-review (#11) | ❌ 충돌 → 재사용 강제 |
| finance-cost-check | "비용 검토"/"LLM cost" | cost-review (#8) | ❌ 충돌 → 재사용 강제 |
| finance-io-check | "agent IO 점검"/"agent_io" | agent-io-check (#15) | ❌ 충돌 → 재사용 강제 |

→ machinery(generation_workflow §4.1 + INDEX 충돌 규칙 + factory_contract 규칙 4)가 4 후보 전부를 **진입 시점 사전 차단**. ★ **M1 대비 진화 확인**: M1 은 podcast-eval-run 1개를 검증4 에서 **사후** "음의 효용"으로 거부했으나, M3 재무는 G2 결정트리가 4개 후보를 단계4 진입 전 **사전 분기**. M2 G2 개선(generation_workflow §4.1)이 이질 도메인에서 "사후 발견 → 사전 차단"을 실제로 수행함 = machinery 작동 지점.

**(c) 우선순위 표 편입**

- 채택 Skill 0 신규 → INDEX 우선순위 표 변경 불필요. 동시 매칭 가능한 관계(eval-run > harness-factory / contract-change > harness-factory)는 이미 INDEX §우선순위 충돌 해결에 존재 → 추가 편입 불요.

**판정 근거**: 채택 Skill 키워드 충돌 **0** AND machinery 가 4 후보를 결정트리로 사전 차단 → **PASS** (신규 Skill 0 권장이 절차로 검증을 통과).

---

### 검증 3 — contract consistency → **PASS** (cross-ref drift 0, ★ G3 조건부 산출 축 작동 — M1 GAP 해소 상태로 시작)

> 질문: prompt↔output / api↔front / db↔migration / agent_io↔agents[] cross-ref 가 정합하는가 + 조건부 산출 축 정합.

**4 정합 축 + 조건부 산출 축 점검** (blueprint §4.1 + contract_draft §3):

| # | 정합 축 | blueprint 상 정의 | 누락 |
|---|---|---|---|
| 1 | agent_io ↔ output_schema | 6 agent 출력(plan_candidates/debt_repayment_plan/insurance_review/critic 등) ↔ output_schema 본문 5종(contract_draft §1) | **0** |
| 2 | output_schema ↔ db_schema | FinancialPlan/Allocation JSONB ↔ plans/allocations 테이블 (contract_draft §3, blueprint §4.1) | **0 (설계 정합)** |
| 3 | api_contract ↔ frontend | blueprint §4.1 "* 후속 — API 계약은 phase 진행 시" **명시적 deferral** | **0 (현 단계 비대상)** |
| 4 | db_schema ↔ migration | "런타임 미생성, 설계만"(blueprint §4.1) — A9 정합 | **0 (dry-run 정상)** |
| ★ 5 | **조건부 산출(conditional output)** | debt_repayment_plan(has_debt) / insurance_review(has_dependents) → contract_draft §3 cross-ref 열에 1급 표현, agent conditional_execution.condition 과 동일 조건식 1:1 정합 | **0 (양면 정합)** |

**누락 항목 합계: 0.**

**★ 관찰 (M1 대비 핵심 변화 — GAP 해소 상태로 시작)**: M1 검증3 은 drift 0 이었으나 "조건부 산출 축 부재 = 표현력 GAP(G3)" 를 별도 flag 했다. M3 재무는 **G3 가 이미 contract_template §3 에 반영된 machinery** 로 시작하므로, contract_draft §3 가 debt/insurance 의 조건부 산출을 cross-ref 열로 **1급 표현** + agent_draft conditional_execution 과 양면 정합 → **검증3 의 GAP-flag 가 발생하지 않음**(M2 S3 가 M1 에 additive 로 해소한 것이, M3 에서는 생성 시점부터 적용됨). 이질 도메인에서 2개 조건부 산출 + 서로 다른 불리언 데이터 트리거(has_debt vs has_dependents)를 표현 → G3 표현력 범용 재확인.

**판정 근거**: 4 축 + 조건부 산출 축 cross-ref 누락 **0**, GAP-flag 없음 → **PASS**.

---

### 검증 4 — with-skill / without-skill comparison → **PASS (누락률) / PENDING-BY-DESIGN (품질·일관성)**

> 질문: machinery 적용 전(WITHOUT)/후(WITH) 결과가 어떻게 달라지는가 (누락률 / 품질 / 일관성). 상세 수치는 §E.

**3 지표 (validation_workflow 검증4 절차)**:

1. **누락률 (machinery 강제 절차 단계의 누락)** — WITH < WITHOUT **입증** (§E 6지표 정량):
   - WITHOUT(`_without_baseline.md`)은 forbidden_scope→non_goals 매핑(0), eval gate(0), contract cross-ref(4축+조건부 누락), 충돌 검토 절차(미수행), 제3자 PII risk 판정(감으로 "민감정보로 묶음" §5), 조건부 실행("if 문으로 처리" §5)을 **전부 누락 또는 감으로 처리**.
   - WITH 은 이 전부를 machinery 슬롯으로 **강제 표현**. → 누락률 WITH ≪ WITHOUT.
2. **품질 (산출물 품질 점수)** — **PENDING-BY-DESIGN**: 실 LLM 산출물 점수는 검증5 가 pending-by-design(실측 미수행)이므로 의미 품질 점수 비교 불가. dry-run 범위상 정상. (★ M1 은 단순 PENDING 이었으나 M3 는 G8 enum 으로 pending-by-design 명시.)
3. **일관성 (반복 실행 편차)** — **PENDING-BY-DESIGN**: 반복 실행 실측 없음 (dry-run 정상).

**YAGNI 차단 점검 (절차 3)**: 신규 Skill 0 권장이 정당한가? — WITH(재사용)이 WITHOUT(절차 부재) 대비 누락률을 명확히 낮추면서, 신규 Skill 추가 없이 달성. 신규 Skill 강행 시 검증2 충돌(4 후보 전부) = 음의 효용. → **신규 Skill 0 이 옳다**를 검증4 가 지지.

**판정 근거**: 누락률 지표 WITH ≪ WITHOUT 정량 입증(§E) → **PASS (누락률)**. 품질·일관성 2지표는 실 산출물 부재로 **PENDING-BY-DESIGN(정상 미측정)**. ★ 정량 우열 단정 금지 — 누락률·구조 차원만 결정적, 의미 품질은 미측정.

---

### 검증 5 — eval-run 연동 (★) → **PENDING-BY-DESIGN (절차 적용 가능 / 실측 미수행)** [정상, G8 enum]

> 질문: eval-run §3~§6 절차가 재무 harness 에 **적용 가능한가**. ★ 실 LLM 호출/실측 점수 미수행 → pending-by-design 이 정상.

#### eval-run §3~§6 적용 가능성 (절차 cross-ref)

| eval-run 단계 | 재무 harness 적용 가능성 | 매핑 근거 |
|---|---|---|
| §3 실행 (golden_set 케이스 → 출력) | ✅ **적용 가능** | golden_set FP-001~ 정의됨(eval_draft FP-001 단일목표/무부채·1인 + FP-004 부채+부양가족 동시 케이스 완비: input/has_debt/has_dependents/expected_path/passing_criteria). 비교 모드 사용 가능. |
| §4 채점 (schema 준수율 + 품질 차원 + 다양성) | ✅ **적용 가능** | schema 준수율 1차 게이트 + finance_planning_eval 무조건 9 + 조건부 3(applies_when) 자동 채점 + plan_differentiation(3안 cosine 다양성). |
| §5 결과 저장 (regression_results/{trigger}_{날짜}.md) | ✅ **적용 가능** | 동일 리포트 형식 차용 가능 (M2 podcast_eval_run_sample.md 가 mock-deterministic 으로 시연한 패턴 동형). |
| §6 임계값 판정 | ✅ **적용 가능** | blueprint §5.2 + eval_draft §C 가 eval-run §6 임계값과 동일 + ★ **advisory_boundary 차단 단어(자문/원금보장/상품추천) >0% → 즉시 fail** 게이트가 도메인 금지를 eval 차단으로 연결. |

#### golden_set 케이스 매핑 가능성 → ✅ 가능

- FP-001(무부채·1인 → 조건부 차원 평균 제외) / FP-004(부채+부양가족 동시 → 조건부 2차원 평균 포함) 케이스 구조가 eval-run §3 입력 형식과 정합. **G4 applies_when 의 양면(제외/포함)을 golden_set 케이스가 직접 시연** — has_debt/has_dependents 불리언 데이터 조건이 케이스 input 에 1급으로 들어감.

#### 임계값 게이트 → phase 종료 차단 연결 가능성 → ✅ 가능

- blueprint §6 phase-F1.acceptance "★ advisory_boundary 차단 단어 0% 게이트" + phase-F3.acceptance "eval-run 임계값 게이트 통과 / human_review + security_review 강제 통과(risk high) / applies_when 조건부 차원 평균 제외 동작" → 임계값 위반이 phase 종료(acceptance 미충족)를 **차단**하는 경로 존재.

#### eval-run §5 형식 리포트 (요약 점수표 — ★ 값은 [미측정] placeholder)

```markdown
# Eval Run: finance-harness-S2-validation (★ 절차 적용성 점검 — 실측 미수행)
- 트리거: harness-factory validation (검증5)
- 케이스 수: FP-001~ (정의됨 / 실행 안 함)
- 비교 대상: WITH blueprint (WITHOUT 은 eval 형식 부재 → 비교 불가)

## 요약 점수
| 지표 | WITH(설계 가능) | 실측 |
|---|---|---|
| schema 준수율 | 100% 게이트 정의됨 | [미측정 — 실 LLM 미호출] |
| finance_planning 평균(무조건 9 + 조건부 applies_when) | 채점 차원 정의됨 | [미측정] |
| advisory_boundary_compliance (차단 단어 0%) | 하드 게이트 정의됨 | [미측정] |
| 다양성 (plan_differentiation, cos sim) | 3안 다양성 측정 가능 | [미측정] |
| 평균 latency / 비용 | placeholder timeout 30000ms, 3-plan 비용 3배 | [미측정] |

## 임계값 점검 (적용 가능 여부)
- schema 준수율 < 100% → fail : ✅ 게이트 정의됨 (미실행)
- 평균 점수 하락 > 0.3 → fail : ✅ 게이트 정의됨 (미실행)
- 비용 증가 > 30% → cost-review : ✅ 게이트 정의됨 (미실행)
- latency 증가 > 20% → 경고 : ✅ 게이트 정의됨 (미실행)
- ★ 자문/원금보장/상품추천 차단 단어 > 0% → fail : ✅ 게이트 정의됨 (미실행)

## 결정
PENDING-BY-DESIGN — 절차/임계값/케이스 매핑 **전부 적용 가능**. 실 점수는 LLM 호출 없는 dry-run 이므로 미측정(정상).
human_review_needed: 해당 없음 (실행 자체 미수행).
```

> ★ M2 podcast 는 mock-deterministic 표본 1회를 별도 실행(`podcast_eval_run_sample.md`)해 pending-by-design 의 mock 차원을 measured 로 전환했다. 재무는 **본 S2 범위에서 표본 실행을 하지 않음**(task 가 "검증5 = PENDING-BY-DESIGN, G8" 으로 명시) → pending-by-design 유지가 정상. 실 mock 표본은 후속(eval-run 위임) 가능하나 분기 판정에는 불필요.

**우선순위 정합**: `eval-run > harness-factory validation` (INDEX) — 실 평가는 eval-run 절차 소유. 본 검증은 "적용 가능성"만 확인하고 실 평가를 eval-run 에 위임.

**판정 근거**: eval-run §3~§6 절차 + 임계값 게이트 + golden_set 케이스 매핑 **전부 적용 가능**하나, 실 LLM 호출/실측 점수는 dry-run 범위 밖 → **PENDING-BY-DESIGN (절차 적용 가능 / 실측 미수행)** = 정상 (G8 enum).

---

### 검증 6 — generated harness acceptance → **PASS** (5 체크리스트 전부 충족, ★ forbidden_scope→non_goals 매핑 + risk high 경로 강화)

> 질문: 생성 harness 가 최소 수락 기준 5개를 만족하는가.

| # | 수락 체크 | 충족 | 근거 |
|---|---|---|---|
| 1 | 최소 파일 구조 (라우터+상태+contracts+phases+eval+skills) | ✅ | 라우터 AGENTS/CLAUDE(§7) + 상태 project_state_draft + contracts 4(§4) + phases 5(§6) + eval 5(§5) + skills(재사용, §3). 6/6 디렉토리 대응. |
| 2 | forbidden_scope → non_goals + 라우터 금지 매핑 | ✅ | domain_brief.forbidden_scope 7 → phases[].non_goals(§6 각 phase) + phase_draft NG1~NG6. ★ 라우터(CLAUDE/AGENTS)에서 security-review 가 risk high 로 강조됨. scope creep + **규제 금지** 차단 경로 존재. |
| 3 | phase 8 files 형식 + acceptance 존재 | ✅ | phase_draft 가 8 files(goals/scope/non_goals/dependencies/acceptance/assumptions/multi_slice_plan/notes) **전부** 채움. acceptance A1~A4(A3 security-review risk high 강제, A4 advisory_boundary 게이트) 존재. blueprint §6 은 goals/non_goals/acceptance 만(proposal 단계). |
| 4 | eval gate → 종료/배포 차단 연결 | ✅ | 검증5 임계값 게이트 + ★ advisory_boundary 차단 단어 0% → phase-F1/F3 acceptance 차단 연결(§6). schema<100% / 점수↓>0.3 / 차단단어>0% → fail = 종료 차단. |
| 5 | rollback·retrospective 경로 존재 | ✅ | phase_draft notes.md: rollback=contract 초안 git revert(런타임 0 변경 → 안전) + retrospective=meta-retrospective(제3자 PII·자문 경계 설계 회고). blueprint §6 phase-F2/F4 security-review 게이트. |

**판정 근거**: 5 체크리스트 **전부 충족** → **PASS**. (blueprint §6 이 proposal 단계라 phase entry 를 goals/non_goals/acceptance 3개로 축약했으나, phase_draft 가 8 files 완본 예시 제공 — 형식 충족 입증. M1 과 동일 구조.)

---

## B. ★ M2 G1~G8 실사용 유효성 점검표 (핵심 — A3)

> S1 이 "사용했다"고 보고한 각 개선요소를 **검증 관점에서 재평가**: 유효(이질 도메인에서 실제로 의도대로 작동) / 부분(작동하나 한계·문서화 미흡) / 부적합(이질 도메인에 안 맞거나 오작동).

| G | S1 사용 | S2 유효성 판정 | 이질 도메인 적합 근거 |
|---|---|---|---|
| **G1** (expert vs 단일 결정기준, architecture_patterns §2.1) | expert_pool(목표유형별) 미채택 → 단일 planning + `goal_types[]` 파라미터화. §2.1 4축으로 사전 판정 | **유효** | 4축 판정이 재무에 **타당**. 핵심: §2.1 "포맷/유형 수" 축에서 "한 사용자의 종합 플랜은 여러 목표를 **한 배분 안에** 담음 → 전문가 1명에게 1유형 라우팅이 통합 배분을 깨뜨림"은 재무 고유 근거(미디어 복붙 아님). expert N개 = 관리비용 N배 임계도 정상 적용. ★ S1 이 "목표유형 라우팅(expert_pool)과 조건부 실행(conditional_execution)은 다른 축"이라고 명시 분리(blueprint §1.2)한 것은 G1 의 정밀 적용 — 검증 관점에서 옳음. |
| **G2** (skill 신규 vs 재사용 결정트리, generation_workflow §4.1) | 4 후보(finance-eval-run 등) 사전 거부 → 신규 0 / 재사용 강제 | **유효** | 검증2 가 직접 입증(§A). M1 의 1개 사후 거부 → M3 의 4개 사전 차단으로 표현력·적용범위 확대. risk high 가 security-review 를 "재사용 강제 + 필수"로 격상하는 상호작용도 결정트리와 정합 — 도메인 무관 절차 Skill 재사용 = 범용 신호. |
| **G3** (conditional_execution + 조건부 산출, agent_template/contract_template §3) | debt_priority(has_debt) / insurance_review(has_dependents) 조건부 + contract 조건부 산출 열 | **부분** | ★ **task 가 집중 지목한 항목**. 표현 자체는 **유효** — agent conditional_execution.condition 에 `has_debt == true` 같은 **불리언 데이터 조건**을 넣고 contract 조건부 산출 열과 1:1 정합(검증3 양면 drift 0). 그러나 **template 문서화가 enum mode 전제에 치우침**: agent_template 슬롯 주석·예시(`condition: mode == guest`)와 작성가이드 6("모드/게스트 등")이 전부 **enum mode 예시만** 제시. 불리언 데이터조건(`has_debt`)은 슬롯이 자유표현식(`{{condition_expr}}`)이라 **표현은 수용**되나, template 이 "enum mode 외 불리언 데이터 트리거도 1급"임을 명문화하지 않아 작성자가 mode 로 우회 모델링할 위험. → **표현은 유효 / 문서화는 부분** (NEW-G11 로 기록, nice-to-have). |
| **G4** (eval applies_when 조건부 차원, eval_template §B) | 조건부 차원 3(debt/insurance/tax) applies_when + 미해당 평균 제외 | **유효** | M1(+2) 대비 +3 + **has_debt 같은 불리언 데이터 조건도 applies_when 으로 표현**(eval_draft §B). FP-001(무부채·1인=무조건 9차원) vs FP-004(부채+부양가족=11차원, tax 제외) 케이스가 제외/포함 양면을 golden_set 에 1급 시연 → applies_when 범용 작동. (G3 와 달리 eval_template 작성가이드 4 가 "모드/포맷 의존" 표현이나 eval_draft 가 데이터조건으로 자연 확장 — 검증5 적용가능성에서 정합 확인.) |
| **G5** (제3자 PII risk 상향 트리거, domain_brief_schema §1.1) | medium→high **실제 상향** + required_evals 에 human_review+security_review 강제 | **유효** | ★ **task 집중 지목**. M1 팟캐스트는 제3자 PII 1종(Guest)으로 "medium 유지 + 상향 후보 명시"(M2 판정=expressible)에 그쳤다. 재무는 **제3자 PII 2종(Dependent+Beneficiary) + 금융 민감정보(소득·자산·부채) 결합** → 트리거가 **실제 등급 상향(medium→high)으로 귀결**(domain_brief §G5). 상향 효과(human_review_rubric + security_review 강제 = factory_contract 규칙 8)가 required_evals·skill_draft·phase acceptance(A3)에 일관 전파됨 → **M1 의 expressible 을 M3 가 addressed(실 상향 귀결)로 시연**. G5 가 미디어 외 규제 도메인에서 정상·강하게 작동. ⚠ 단, dry-run 이므로 실 등급 확정(security-review 강제 발동)은 여전히 사용자 승인 사항(M2 판정 정신 유지) — 판정 축은 유효, 등급 확정 게이트는 승인. |
| **G6** (data_model 1급 필드, domain_brief_schema §1.2) | User→Household→FinancialGoal→Plan→Allocation 5계층 + 9 엔티티 + PII 표시 | **유효** | ★ **task 집중 지목**. 미디어 계층(Brand/Show/Episode)을 **재무 계층으로 완전 치환** + Dependent/Beneficiary 제3자 PII 신규 엔티티를 pii 필드에 1급 표시(G5 트리거와 직결). 계층 구조가 도메인 무관하게 schema 안에서 표현됨 → G6 범용. (M1 은 4계층, M3 은 5계층 + 조건부 입력 Debt 엔티티 — 계층 깊이·엔티티 수 확장도 schema 가 수용.) |
| **G7** (harness_status enum, project_state_template) | `harness_status: dry-run-blueprint` + `phase_F0_status: planned` | **유효** | dry-run blueprint ↔ 실 phase 분리를 1급 표현(project_state_draft §G7). M1 의 "(제안)" 수동 표기·custom 키 우회를 표준 enum 이 대체. 규제 도메인(risk high)에서 outputs/ 격리 의도를 구조적으로 보존 → G7 범용. |
| **G8** (validation pending-by-design enum, harness_blueprint_schema §3.1) | 검증5 = pending-by-design / 검증4 품질·일관성 = pending-by-design sub-status | **유효** | blueprint §9 가 단순 pending(미완) 과 "dry-run 범위상 정상 미측정"을 구별 표현. 검증4·5 의 정상 미측정을 enum 으로 1급 표기 → G8 범용 (도메인 무관). |

**유효성 분포: 유효 7 (G1·G2·G4·G5·G6·G7·G8) / 부분 1 (G3 — 표현 유효·문서화 부분) / 부적합 0.**

> ★ 핵심 해석: M2 의 8 개선요소가 **이질(규제) 도메인에서 전부 실효** (부적합 0). 특히 G5 가 M1(expressible)을 넘어 **실 등급 상향으로 귀결**, G3·G4 가 enum mode 를 넘어 **불리언 데이터 트리거(has_debt/has_dependents)** 까지 표현. G3 만 "표현은 작동하나 template 문서가 enum 예시에 치우침"으로 부분 — 이는 machinery 결함이 아니라 **문서화 GAP**(NEW-G11, nice-to-have)이며 표현력 자체는 정상.

---

## C. 범용성 판정 (A5) — **범용 강함**

> 질문: machinery 가 미디어 편향(창의 hook / 3-variant 창의다양성 / 썸네일 류)을 재무에 강요했는가? blueprint 가 재무 고유로 재정의됐는가?

### 미디어 편향 신호 점검

| 미디어 편향 후보 | 재무 blueprint 에서 강요됐나 | 판정 |
|---|---|---|
| 창의 hook / opening_hook | ❌ 강요 0 — 재무 blueprint 에 hook 차원 없음. eval 채점차원이 **actionability(실행가능성)** 로 재정의(hook_strength → actionability, blueprint §5.1). | 편향 없음 |
| 3-variant **창의 다양성** | △ 형태는 계승(3안)되나 **의미가 재정의됨** — "창의적 다양성"이 아니라 **보수/중립/공격 리스크 톤** 3안(blueprint §1.1 fan_out_fan_in). plan_differentiation 차원도 "리스크 톤 차별성"으로 재정의. fan_out_fan_in 패턴 자체는 도메인 무관 카탈로그(architecture_patterns)이므로 편향 아님. | 편향 없음 (패턴 재사용 ≠ 미디어 종속) |
| 썸네일 / SEO 제목 류 | ❌ 강요 0 — 재무 산출물에 썸네일·SEO 개념 없음. | 편향 없음 |
| brand_consistency | ❌ → **risk_appetite_fit(리스크 성향 적합성)** 으로 재정의(§5.1). | 편향 없음 (재정의됨) |

### 재무 고유로 재정의됐는가 (positive 신호)

- **리스크/적합성**: Critic 차원이 goal_fit/savings_realism/**risk_appetite_fit** 으로 재정의. producer_reviewer 패턴이 "리스크/적합성 검토"로 재무화.
- **규제 forbidden**: forbidden_scope 7항 중 4항이 **도메인 자체 규제 금지**(투자자문/원금보장/상품추천/세무·법률자문) — 미디어엔 없던 영구·법적 금지. advisory_boundary_compliance 하드 게이트(차단 단어 >0% → fail)로 eval 차단까지 연결.
- **수치 정합**: budget_allocation/investment_mix **합=100% 검증**, savings_target 율 — 미디어엔 없던 수치 제약을 output_schema·eval(allocation_coherence)·validation 규칙으로 표현.
- **제3자 PII 2종**: Dependent+Beneficiary(부양가족/수익자) — 미디어 Guest 1종보다 짙은 가구 부양 맥락.

**판정: 범용 강함.** 근거 — (1) 미디어 편향 신호(hook/썸네일/창의다양성/brand) 강요 **0**, (2) 계승된 형태(3안/supervisor/producer_reviewer/pipeline)는 **architecture_patterns 6패턴 카탈로그**의 도메인 무관 재사용이지 미디어 종속이 아님(S1 이 §1.2 에서 "미디어 결론 복붙이 아니라 §2.1 4축을 재무 데이터로 재평가"라고 명시), (3) blueprint 가 리스크/적합성/규제 forbidden/수치 합=100% 라는 **재무 고유 축으로 적극 재정의**됨. machinery 가 미디어 편향 없이 이질 도메인을 표현 → **범용성 2차 검증 PASS (강함)**.

> ⚠ 정직성 단서: "범용 강함"은 **표현·설계 차원**의 판정이다. 실 LLM 산출물이 재무 도메인에서 의미 품질을 내는지는 검증5 pending-by-design 으로 미측정. "machinery 가 이질 도메인을 편향 없이 표현할 수 있다"가 결론이지 "실 품질 우월"이 아니다.

---

## D. 새 GAP 검출 (A6) — ★ 보수적·정직하게

### S1 제기 GAP 재평가 (검증 관점)

| GAP | S1 관찰 | S2 재평가 (유효/중복) | 심각도 | 보완 방향 (★ 기록만 — 반영 X) |
|---|---|---|---|---|
| **NEW-G9** forbidden_scope 의 "규제 금지" vs "scope creep(MVP 제외)" 미구분 | regulatory_forbidden(투자자문/원금보장 = 영구·법적) 과 deferred_scope(Plan Memory = 후속 phase)가 한 필드에 혼재 | **유효** — 검증 관점에서 재확인. domain_brief.forbidden_scope 7항이 **이질 종류**(4항 규제 금지 + 3항 후속/외부액션)인데 schema 가 단일 list. phase_draft non_goals(NG1~NG4 규제 / NG6 후속)에서도 같은 표에 혼재(phase_draft §메모가 직접 지적). eval advisory_boundary 하드 게이트로 규제 금지를 강등 표현했으나 domain_brief 단계엔 구분 필드 없음. **중복 아님** (G5 는 risk 축, G9 는 forbidden_scope 축 — 별개). | **minor** | domain_brief_schema.forbidden_scope 를 `regulatory_forbidden`(영구·법적, 하드 게이트 필수) / `deferred_scope`(후속 phase) 2 하위 구분 (선택 필드, backward-compat). |
| **NEW-G10** risk_level 단일 enum (data_risk vs regulatory_risk 미분해) | "PII 위험(high)"과 "규제·자문 위험"이 다른 종류인데 한 등급에 압축 | **유효하나 부분 중복** — 검증 관점: risk_level high 가 **data_risk(제3자 PII) 기준으로 도출**됐고(domain_brief §G5), 규제 위험은 이미 **forbidden_scope + advisory_boundary 하드 게이트**라는 **별도 더 강한 장치**로 표현됨. 즉 "규제 위험을 risk_level 에 못 담는다"는 관찰은 맞으나, 규제 위험이 **누락된 게 아니라 다른 축(forbidden_scope/G9)으로 이미 표현**됨 → G10 의 실익은 "risk 분해로 G5 트리거와 G9 를 정밀 연결"하는 **표현 정밀도 개선**에 한정. NEW-G9 와 부분 중복(둘 다 "규제 vs 데이터 종류 구분"이라는 같은 뿌리). | **nice-to-have** | risk_level 을 `data_risk` / `regulatory_risk` 축 분해 (선택). 단 G9(forbidden_scope 구분)와 함께 설계해야 중복 회피 — 단독 가치 낮음. |

### S2 신규 발견 GAP

| GAP | S2 발견 | 심각도 | 보완 방향 (★ 기록만) |
|---|---|---|---|
| **NEW-G11** conditional_execution / applies_when 의 **불리언 데이터 트리거** template 문서화 부재 | G3 유효성 점검(§B)에서 발견. agent_template conditional_execution 슬롯과 작성가이드 6, eval_template applies_when 작성가이드 4 가 전부 **enum mode 예시(`mode == guest`)만** 제시. 재무는 `has_debt`/`has_dependents` 같은 **불리언 데이터 존재 조건**으로 분기하는데, 슬롯이 자유표현식이라 **표현은 수용**되나 template 이 "enum mode 외 데이터 트리거도 1급"임을 명문화 안 함 → 작성자가 인공 enum mode 로 우회 모델링할 위험. (재무는 S1 이 올바로 불리언으로 표현했으나, machinery 문서가 그 사용을 명시 안내하지 않음.) | **nice-to-have** | agent_template 작성가이드 6 / eval_template 작성가이드 4 에 "조건은 enum mode 뿐 아니라 **불리언 데이터 존재 조건**(예: `has_debt == true`)도 표현 가능 — 분기 트리거는 mode/데이터 무관 orchestrator 소유" 1줄 추가 (machinery 변경 아님, 문서 명료화). |

### GAP 심각도 종합 (분기 판정 입력)

```
NEW-G9   regulatory vs deferred forbidden 구분 부재   → minor       (백로그 — Phase 10 안 막음)
NEW-G10  risk_level data vs regulatory 분해           → nice-to-have (G9 와 함께, 부분 중복)
NEW-G11  conditional 불리언 데이터조건 문서화 부재    → nice-to-have (표현은 작동, 문서만)
─────────────────────────────────────────────────────────────────
blocking : 0
minor    : 1 (G9)
nice-to-have : 2 (G10, G11)
```

> ★ 보수적·정직: **blocking GAP 0**. NEW-G9 는 유효한 minor(규제 도메인에서 의미 있으나 advisory_boundary 하드 게이트로 이미 실질 차단됨 — 표현 정밀도 개선이지 안전 누락 아님). NEW-G10 은 G9 와 부분 중복 + 규제 위험이 이미 다른 축으로 표현됨 → nice-to-have. NEW-G11 은 표현이 이미 작동하고 문서 명료화만 필요 → nice-to-have. 어느 것도 Phase 10 을 막는 안전·정합 결함이 아님.

---

## E. with/without 보조 (누락률 차원) — 간단히

> WITH = `harness_blueprint.md`, WITHOUT = `_without_baseline.md`. 측정 = 문서 정적 대조.

| # | 지표 | WITH | WITHOUT | 근거 (1줄) |
|---|---|---|---|---|
| 1 | 누락된 필수 구조 수 (6: 라우터/상태/contracts/phases/eval/skills) | **0** | **6** | WITHOUT(naive §2~§3) = 라우터·상태·contract디렉토리·phase·eval-gate·skills 구조 부재 (agent 4종 + prose 데이터모델만). |
| 2 | forbidden_scope → non_goals/라우터 금지 매핑 (0/1) | **1** | **0** | WITHOUT §4 "디스클레이머 붙인다" 상식 수준, non_goals 개념 0 / WITH = 7항→NG1~6 매핑. |
| 3 | Skill trigger 충돌 수 | **0** | **0** | WITH = 신규 0(채택, 4 후보 사전 거부) → 충돌 0 / WITHOUT = trigger_keywords 미정의(기능 나열만) = 충돌 측정 불가 0. (★ 의미 차: WITH 은 검토 후 0, WITHOUT 은 절차 부재로 0.) |
| 4 | contract cross-ref + 조건부 산출 누락 수 | **0** | **5** | WITHOUT §2.4 "프롬프트 하나"·§6 "if 문으로 처리" = 4 cross-ref + 조건부 산출 축 전부 미정의 / WITH = 검증3 누락 0. |
| 5 | eval gate (advisory_boundary 포함) 존재 (0/1) | **1** | **0** | WITHOUT §2.4 "산수 체크/너무 위험 안 함" 감 수준, 임계값·차단 게이트 0 / WITH = 임계값+advisory_boundary 0% 하드 게이트→phase acceptance 차단. |
| 6 | 제3자 PII risk 판정 (0=감/1=구조적 트리거) | **1** | **0** | WITHOUT §5 "그냥 민감정보로 묶어서 처리하면 되지 않을까" 감 / WITH = G5 트리거로 medium→high 구조적 도출 + human_review+security 강제. |

> 누락률 WITH ≪ WITHOUT 정량 입증. 품질·일관성은 검증5 pending-by-design 으로 미측정(§A 검증4). ★ M1 대비 추가: 지표6(제3자 PII risk 구조적 판정)에서 WITHOUT 이 "감으로 묶음"을 명시 노출 → G5 의 가치가 이질 도메인에서 더 선명.

---

## F. ★ 종합 분기 권고 (A7 — 사용자 지침)

### 입력 종합

```
범용성 판정          : 범용 강함 (미디어 편향 강요 0 + 재무 고유 재정의)
M2 G1~G8 유효성      : 유효 7 / 부분 1(G3 문서화) / 부적합 0
새 GAP 심각도        : blocking 0 / minor 1(NEW-G9) / nice-to-have 2(NEW-G10, NEW-G11)
6검증                : PASS 4 / PENDING-BY-DESIGN 2 (정상 미측정)
금지 위반            : 0
```

### 판정 기준 대조 (task F 규칙)

- **"추가 검증/반영/수정 필요"** 조건: blocking GAP 있음 **or** 미디어 편향 약함(미디어 종속) → **둘 다 해당 없음** (blocking 0, 범용 강함).
- **"없음 → Phase 10 직행"** 조건: 범용 강함 **AND** 새 GAP 이 minor/nice-to-have 뿐(백로그로 충분) → **충족**.

### ★★ 분기 권고: **Phase 10 직행 가능**

**이유**:
1. **범용 강함** — machinery 가 이질(규제) 도메인을 미디어 편향 없이 표현. M2 8 개선요소 전부 실효(부적합 0), 특히 G5 가 M1 의 expressible 을 넘어 **실 등급 상향으로 귀결**, G3·G4 가 불리언 데이터 트리거까지 표현. 범용성 2차 검증 통과.
2. **blocking GAP 0** — 새 GAP 3개(G9 minor / G10·G11 nice-to-have)는 전부 **표현 정밀도·문서 명료화** 차원이며 안전·정합 결함이 아님. NEW-G9(규제 금지 구분)조차 advisory_boundary 하드 게이트로 이미 실질 차단됨 → 백로그로 충분.
3. **6검증 정상** — fail 0. PENDING-BY-DESIGN 2 는 dry-run 범위상 정상(G8 enum 으로 명시). active 전환 아님은 규칙 7 로 보존.

**단서 (정직성 — Phase 10 직행이 "완벽"이 아니라 "막을 이유 없음"임을 명확히)**:
- 실 LLM 의미 품질은 검증5 pending-by-design 으로 **여전히 미측정** — "범용 강함"은 표현·설계 차원 판정이지 실측 우월이 아니다.
- 새 GAP 3개는 **Phase 10 진입을 막지 않으나 백로그로 보존** 권장 (NEW-G9 를 먼저, G10/G11 은 G9 와 함께 또는 후순위). M2 식 반영(proposal → contract-change → 승인)은 Phase 10 이후 여유 시점에 선택적.
- G5 실 등급 확정(security-review 강제 발동)은 재무 하네스 **실 진입 시 사용자 승인 사항** — dry-run 에서 표현·도출까지만.

> 결론: **Phase 10 직행 가능**. 추가 검증/반영/수정은 **불필요**(백로그 보존으로 충분). 본 dry-run 의 핵심 산출물은 "범용성 2차 검증 PASS(강함) + 새 GAP 3개(전부 minor/nice-to-have) + M2 개선 실효 입증"이다.

---

## G. 다음 단계 / 위임

- 본 리포트는 검증만 수행 — blueprint 는 6검증(PASS 4 / PENDING-BY-DESIGN 2)에도 **사용자 승인 전 active 아님** (factory_contract 규칙 7).
- 새 GAP 3개(NEW-G9/G10/G11)의 실 machinery 보완은 **proposal-only** (D 섹션 보완 방향 — 실 변경은 contract-change Skill 경유 + 사용자 승인). ★ S2 는 기록만, machinery 0줄 변경.
- 실 eval-run 표본(검증5 pending-by-design 의 mock 차원 측정)은 필요 시 eval-run §3~§6 절차로 별도 위임 (`eval-run > harness-factory validation`) — 분기 판정에는 불필요.

---

## H. 금지 / 격리 확인

- machinery 문서(validation_workflow / factory_contract / generation_workflow / architecture_patterns / domain_brief_schema / harness_blueprint_schema / templates/*) — **읽기만, 0줄 변경**.
- 변경 파일: 본 리포트 1 (신규) + `outputs/TEST/finance/harness_blueprint.md` validation 3필드 결과 기입(additive). 전부 `meta_factory/outputs/TEST/finance/` + `outputs/TEST/` 하위.
- backend/fastapi / apps/web / db/migrations / docs/contracts / AGENTS/CLAUDE/PROJECT_STATE/PHASE_REGISTRY / .claude/skills / meta_factory root machinery·templates·blueprints / TEST/podcast·sample_test_podcast_* (M1·M2 보존) / outputs/{generated_harnesses,improvement_reports} / eval / phases / 이전 ADR — **변경 0**.
- 자격증명/키 — 0 (placeholder 만). `사진/`(untracked) 무시.

---

이 검증 리포트는 meta_factory machinery(validation_workflow 6검증 + factory_contract 8규칙 + M2 개선 G1~G8 + eval-run §3~§6 cross-ref + INDEX 충돌 규칙)를 이질 도메인(개인 재무 플래닝) blueprint 에 적용하여 작성됨. 산출물은 문서(.md)만, machinery/런타임/기존 하네스 0줄 변경 (A9).
