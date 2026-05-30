# harness_blueprint — podcast_episode_planning_harness (WITH 출력)

> 위치: `harness/meta_factory/outputs/TEST/podcast/harness_blueprint.md`
> 상태: Phase M1 Slice S1 — generation dry-run **출력 청사진**
> 형식: `meta_factory/harness_blueprint_schema.md`
> 입력: `domain_brief.md` (podcast_episode_planning_ai)
> 절차: `generation_workflow.md` 11단계 적용
> ★ proposal — validation 3필드 = pending. 6검증(S2) 통과 + 사용자 승인 전 active 아님 (factory_contract 규칙 7).

---

## 0. generation_workflow 11단계 실행 로그

| 단계 | 내용 | 본 dry-run 상태 |
|---|---|---|
| 1 | domain_brief 수집 | ✅ `domain_brief.md` (11 필드, forbidden_scope 6) |
| 2 | architecture pattern 선택 | ✅ §1 — supervisor 주 + 보조 4 (expert_pool 후보 포함) |
| 3 | agent 후보 생성 | ✅ §2 — 7 agent |
| 4 | skill 후보 생성 | ✅ §3 — 대부분 기존 재사용 + 1 신규 후보 |
| 5 | contract 후보 생성 | ✅ §4 — 4 contract |
| 6 | eval 후보 생성 | ✅ §5 — 4 eval |
| 7 | phase 구조 생성 | ✅ §6 — 5 phase (non_goals ← forbidden_scope 매핑) |
| 8 | routing 문서 생성 | ✅ §7 — AGENTS / CLAUDE 대응 |
| 9 | validation_workflow 실행 (6검증) | ⏸ **S2 가 수행** (validation 3필드 = pending) |
| 10 | outputs 격리 저장 | ✅ outputs/TEST/podcast/ (proposal-first, dry-run 격리) |
| 11 | 사용자 승인 후 적용 | ⏸ 미수행 (dry-run — active 전환 없음) |

---

## 1. 메타 + architecture_pattern (단계 2)

```yaml
harness_name: podcast_episode_planning_harness
purpose: "팟캐스트 에피소드 기획 AI — 오디오 대화 흐름 + 오프닝 후킹 + 게스트 브리프 + 쇼노트, 3-plan + Critic revise"

architecture_pattern:
  primary: supervisor              # orchestrator 가 전 단계 중개 — agent 간 직접 호출 0
  secondary:
    - fan_out_fan_in               # 기획안 3개 parallel 생성 (asyncio.gather) + 비용 3배·부분실패 graceful
    - producer_reviewer            # Planner → Critic → Rewriter revise loop (max 2 — 무한 루프 차단)
    - pipeline                     # Intent → RAG → Planning → Guest/Question → Shownotes → Critic → Save
  considered_not_adopted:
    - expert_pool                  # ★ GAP 관찰 — §8 참조 (채택/미채택 양면)
    - hierarchical_delegation      # 미채택 — 재귀 분해 작업 없음 (Dreammate 와 동일)
```

### 1.1 패턴 선택 근거 (architecture_patterns.md 6 패턴 기준)

| 패턴 | 채택 | 근거 |
|---|---|---|
| Supervisor (주) | ✅ | 7 agent 다단계 + 격리/추적/정책 일관 필요. Dreammate moa_orchestrator 동형. agents[].forbidden_actions 에 "직접 호출 금지" 필수 (규칙 2 of architecture_patterns §4). |
| Fan-out/Fan-in | ✅ | 기획안 3개 독립 병렬 생성 → 다양성(3후보 1선택). 비용 3배 + 부분 실패 graceful 명시 필요. |
| Producer-Reviewer | ✅ | 후킹·대화흐름 품질 중요 + 자동 평가 기준(podcast_planning_eval) 정의 가능. revise max 2 상한. |
| Pipeline | ✅ | 흐름이 명확한 선형(의도→기획→게스트→쇼노트→검증→저장) + graceful skip. |
| Expert Pool | ⚠ 후보 | 포맷(인터뷰/솔로/패널)별 특화 생성이 효과적일 수 있음. **단** 단일 planning agent 가 포맷을 입력 파라미터로 처리하면 불필요 → §8 GAP. dry-run 결론: **미채택**(Dreammate 균질 파이프라인 정신 유지, expert_pool 은 비용/유지보수 증가). |
| Hierarchical Delegation | ❌ | 재귀 분해 작업 없음. |

---

## 2. agents[] (단계 3 — agent_template.md 기반)

> Dreammate 4 agent(intent/planning/critic/rewriter) → 팟캐스트 7 agent. guest_brief / question / shownotes 신규.
> ★ supervisor 패턴 → 모든 agent 의 forbidden_actions 에 "다른 agent 직접 호출 금지 (orchestrator 경유)" 포함.

```yaml
agents:
  - name: intent
    responsibility: "의도 분석 (시리즈 신규 / 단발 자동 분기 + Intent Filter)"
    inputs: [user_message, locale, show_context]
    outputs: [intent_ok, mode(series|single), reason, missing_fields]
    forbidden_actions:
      - 다른 agent 직접 호출 (orchestrator 경유)
      - plan/shownotes 생성
      - RAG 직접 의존

  - name: planning
    responsibility: "에피소드 기획안 3개 생성 (parallel) — angle + segment_flow[] + opening_hook"
    inputs: [user_message, mode, rag_context, show_context]
    outputs: [episode_plan_candidates x3]   # 각: angle, segment_flow[], opening_hook
    forbidden_actions:
      - Critic 직접 호출 (orchestrator 경유)
      - 게스트 인물정보 생성(추측) — guest_brief agent 담당
      - 오디오 파일/TTS 산출 (forbidden_scope)

  - name: guest_brief
    responsibility: "[게스트 모드] 게스트 소개·섭외 각도·사전 질문 브리프 생성"
    inputs: [episode_plan(selected), guest_seed(사용자 제공 인물정보)]
    outputs: [guest_brief]
    forbidden_actions:
      - 게스트 실제 섭외/연락 (이메일·DM 발송 — forbidden_scope)
      - 미제공 인물정보 날조 (PII 추측 금지 — llm_security)
      - 다른 agent 직접 호출

  - name: question
    responsibility: "인터뷰/토픽 질문 리스트 생성 (진부도 회피)"
    inputs: [episode_plan, guest_brief?, mode]
    outputs: [question_list]   # 각 질문 + cliche_flag
    forbidden_actions:
      - 쇼노트 생성 (shownotes agent 담당)
      - 다른 agent 직접 호출

  - name: shownotes
    responsibility: "쇼노트 + 에피소드 제목 후보 생성"
    inputs: [episode_plan, question_list?]
    outputs: [shownotes, title_candidates]
    forbidden_actions:
      - RSS/플랫폼 자동 업로드 (forbidden_scope)
      - 다른 agent 직접 호출

  - name: critic
    responsibility: "기획안 평가 (canonical overall_score + dimensions: 후킹/대화흐름/질문품질 등)"
    inputs: [episode_plan_dict, question_list?, shownotes?]
    outputs: [overall_verdict, overall_score, dimensions]
    forbidden_actions:
      - plan 직접 수정 (rewriter 담당)
      - 다른 agent 직접 호출

  - name: rewriter
    responsibility: "Critic verdict=revise 시 기획안/멘트 개선 (max 2)"
    inputs: [episode_plan_dict, verdict, critic_dimensions]
    outputs: [revised_episode_plan]
    forbidden_actions:
      - 무한 revise (critic_max_revise=2 상한)
      - 다른 agent 직접 호출
```

### 2.1 execution_policy 공통 (agent_template §execution_policy)
- timeout_ms: placeholder(예: 30000), max_retries: 2, graceful_on_failure: true (P-GRACEFUL-001 정신 — 외부 의존 실패 시 차단 0 + validation.warnings).

---

## 3. skills[] (단계 4 — skill_template.md 기반, ★ 키워드 충돌 검토 대상)

> ★ 핵심 관찰: 팟캐스트 도메인의 절차 Skill 대부분은 **기존 21 Skill 재사용 가능**(contract-change / eval-run / phase-start·complete·review / harness-audit / qa-check / bug-triage / cost-review / rag-design·update / agent-io-check / ai-architecture-review / design-review / meta-retrospective / multi-llm-validation / prompt-version-review / eval-design / context-compact / harness-factory). 도메인 특화 신규 Skill 은 최소화.

```yaml
skills:
  # --- 재사용 (신규 0 — 키워드 충돌 0) ---
  - name: contract-change
    trigger_keywords: [contract 변경, schema 변경, breaking change]
    applies_to: [agents, claude]
    related_contracts: [전체]
    reuse: true

  - name: eval-run
    trigger_keywords: [eval 실행, golden_set, regression]
    applies_to: [agents]
    related_contracts: [output_schema]
    reuse: true                    # podcast_planning_eval 실행도 eval-run 절차 재사용 (별도 Skill 불필요)

  - name: agent-io-check
    trigger_keywords: [agent IO 점검, agent_io_contract, I/O 검증]
    applies_to: [agents]
    related_contracts: [agent_io_contract, output_schema]
    reuse: true                    # 7 agent IO drift 검사

  # --- 신규 후보 (★ 채택 보류 — S2 with-without 검토) ---
  - name: (없음 — 신규 Skill 후보 없음)
    note: >
      도메인 특화 Skill 신규 추가 후보를 검토했으나, 모든 절차(평가/검토/감사/회고/contract변경)가
      기존 Skill 로 커버됨. "podcast-eval-run" 같은 신규 Skill 은 eval-run 과 키워드 충돌(eval 실행/golden_set)
      → factory_contract 규칙 4 위반 위험. ★ 따라서 신규 Skill 0 권장 (GAP §8 참조: 도메인 데이터는
      golden_set/eval 채점차원으로 표현하고 Skill 절차는 재사용).
```

### 3.1 키워드 충돌 검토 (factory_contract 규칙 4 — 예비)
- 신규 Skill 0 → INDEX 기존 키워드와 충돌 0 (예비 판정). **실 검증은 S2 trigger_validation / skill conflict check.**

---

## 4. contracts[] (단계 5 — contract_template.md 기반, cross-ref 필수)

```yaml
contracts:
  - path: docs/contracts/agent_io_contract.md
    purpose: "7 agent (intent/planning/guest_brief/question/shownotes/critic/rewriter) 입출력·실행 정책"
  - path: docs/contracts/output_schema.md
    purpose: "Envelope / EpisodePlan(angle+segment_flow[]+opening_hook) / GuestBrief / QuestionList / Shownotes / Critic 본문"
  - path: docs/contracts/db_schema.md
    purpose: "데이터 계층 (User→Brand→Show→Season→Episode + guests + episode_plans + feedback) + JSONB"
  - path: docs/contracts/llm_security.md
    purpose: "게스트 인물정보 PII 마스킹 + prompt injection 차단 + PII 추측 금지"
```

### 4.1 cross-reference 축 (contract_template §작성가이드 1)
```
agent_io_contract  ↔  output_schema     (7 agent 출력 ↔ 본문 스키마)
output_schema      ↔  db_schema         (EpisodePlan/Shownotes JSONB ↔ episodes 테이블 컬럼)
api_contract*      ↔  apps/web types     (* 후속 — API 계약은 phase 진행 시)
db_schema          ↔  db/migrations      (테이블 ↔ migration — 런타임 미생성, 설계만)
```
- ★ 실 정합 검증은 S2 contract_consistency.

---

## 5. evals[] (단계 6 — eval_template.md 기반)

```yaml
evals:
  - path: eval/golden_set.md
    purpose: "회귀 케이스 (PE-001~ : 솔로/인터뷰/패널/시리즈오프닝/단발). case_id 고정, priority P0/P1/P2"
  - path: eval/regression_eval.md
    purpose: "mock-deterministic CI 회귀 (비용 0)"
  - path: eval/podcast_planning_eval.md
    purpose: "도메인 채점 차원 (아래 §5.1)"
  - path: eval/human_review_rubric.md
    purpose: "사람 검토 (오프닝 후킹 임팩트 / 게스트 적절성 정성 판단)"
```

### 5.1 채점 차원 (eval_template §작성가이드 4 — 도메인별 정의)
> Dreammate 8차원을 팟캐스트로 변환:

| Dreammate | 팟캐스트 대응 | 비고 |
|---|---|---|
| intent_fit | intent_fit | 동일 |
| target_clarity | target_clarity | 동일 |
| hook_strength | opening_hook_strength | 썸네일→오프닝 멘트 후킹 |
| message_clarity | message_clarity | 동일 |
| structure | conversation_flow | 영상 flow→오디오 대화 흐름 자연스러움 |
| feasibility | recording_feasibility | 녹음 현실성(길이/포맷) |
| brand_consistency | brand_consistency | 동일 |
| differentiation | differentiation | 동일 |
| (신규) | question_quality | 게스트 모드 질문 진부도/깊이 (영상기획엔 없음) |
| (신규) | guest_fit | 게스트-주제 적합성 (게스트 모드) |

→ 8 + 2(question_quality / guest_fit) = **10 차원** (조건부: 게스트 모드일 때 +2).

### 5.2 임계값 (eval_template §C / eval-run §6 정합)
- schema 준수율 < 100% → 즉시 fail; 평균 점수 하락 > 0.3 → fail+사람검토; 비용 증가 > 30% → cost-review; latency > 20% → 경고; 차단 단어 > 0% → fail.

---

## 6. phases[] (단계 7 — phase_template.md 기반, ★ non_goals ← forbidden_scope 매핑)

```yaml
phases:
  - phase_name: phase-P0-foundation
    goals: [데이터 계층 설계(User→Brand→Show→Season→Episode), output_schema/db_schema 초안]
    non_goals: [오디오 녹음/편집, RSS 업로드]      # ← forbidden_scope
    acceptance: [4 contract 초안 존재, db_schema ↔ output_schema cross-ref 0 drift]

  - phase_name: phase-P1-mvp-planning
    goals: [intent + planning(3-plan) + critic + rewriter MVP, golden_set PE-001~ 정의]
    non_goals: [게스트/쇼노트 (P2), TTS 음성 생성, 자동 promotion]   # ← forbidden_scope
    acceptance: [golden_set 회귀 PASS, schema 준수 100%, revise max 2 차단 검증]

  - phase_name: phase-P2-guest-shownotes
    goals: [guest_brief + question + shownotes agent, question_quality/guest_fit 차원 추가]
    non_goals: [게스트 실제 섭외/연락 자동화, 음원 배포]   # ← forbidden_scope
    acceptance: [게스트 모드 e2e, PII 마스킹(llm_security) 검증, question cliche_flag 동작]

  - phase_name: phase-P3-eval-hardening
    goals: [podcast_planning_eval 10차원 정식화, human_review_rubric, regression CI 게이트]
    non_goals: [Show Memory 자동 추출]   # ← forbidden_scope (후속)
    acceptance: [eval-run 임계값 게이트 통과, human_review 샘플 검토 완료]

  - phase_name: phase-P4-show-memory (후속)
    goals: [Show Memory 추출(피드백→candidate, rag-update 5단계 경유)]
    non_goals: [사람 검토 없는 자동 승격]   # ← forbidden_scope (규칙 8)
    acceptance: [candidate→approved 승격 사람 검토 게이트, security-review 통과]
```

> ★ phase entry 8 files(goals/scope/non_goals/dependencies/acceptance/assumptions/multi_slice_plan/notes)는 실 phase 진입 시 생성 — 본 blueprint 는 goals/non_goals/acceptance 만 (proposal 단계).

---

## 7. routing_docs[] (단계 8)

```yaml
routing_docs:
  - AGENTS.md       # 구현/QA 모델 라우터 (agent-io-check / eval-run / qa-check / bug-triage 등)
  - CLAUDE.md       # 기획/설계 모델 라우터 (ai-architecture-review / design-review / contract-change / harness-factory 등)
```
- 라우터는 본문 지침이 아니라 작업 유형별 참조 문서 + Skill 안내. applies_to 태그로 역할 분리 (Dreammate 정신 계승).

---

## 8. ★ GAP / 관찰 메모 (dry-run 목적 = GAP 발견)

| # | GAP / 관찰 | machinery 측면 |
|---|---|---|
| G1 | **expert_pool 패턴 적용 모호** — 포맷(인터뷰/솔로/패널)별 특화 생성이 expert_pool 후보지만, planning agent 가 포맷을 파라미터로 받으면 불필요. architecture_patterns.md 는 "언제 expert_pool vs 단일 agent 파라미터화" 판단 기준이 약함. | architecture_patterns 선택 기준 보강 필요 |
| G2 | **신규 Skill 0 이 정상인가?** — 도메인 특화 절차 Skill 이 전부 기존 재사용으로 커버됨. generation_workflow 단계 4 는 "skill 후보 생성"을 전제하나, 재사용이 우월할 때의 가이드(신규 vs 재사용 결정 트리)가 없음. | generation_workflow 단계 4 보강 |
| G3 | **agents 7개 — agent_io_contract 형식이 4 agent(MOA) 전제** — guest_brief/question/shownotes 처럼 조건부(게스트 모드일 때만 실행) agent 의 execution_policy(조건부 실행/skip) 표현이 template 에 없음. | agent_template 에 conditional_execution 슬롯 부재 |
| G4 | **채점 차원이 조건부(게스트 모드 +2)** — eval_template 의 채점 차원은 고정 N 전제. 조건부 차원(모드 의존) 표현 부재. | eval_template 조건부 차원 미지원 |
| G5 | **PII = 게스트 인물정보** — llm_security 가 사용자 입력 PII 중심. 제3자(게스트) 인물정보 마스킹/날조 금지는 Dreammate 에 없던 risk. risk_level medium 으로 충분한지 모호(제3자 PII → high 검토 여지). | domain_brief risk_level 판정 기준에 "제3자 PII" 축 부재 |
| G6 | **data layer 5계층 + Guest** — domain_brief_schema 에 데이터 계층을 구조화하는 전용 필드 없음(primary_tasks/output_artifacts 로 우회 서술). 본 dry-run 은 §2 별도 섹션으로 보강. | domain_brief_schema 에 data_model 필드 부재 |

> 이 6 GAP 은 S2 validation 6검증 + 6지표 비교의 입력. dry-run 의 핵심 산출물.

---

## 9. validation (★ 3 필드 = pending — S2 가 수행)

```yaml
validation:
  trigger_validation: pending        # Skill/agent 트리거 정합 — S2 validation_workflow 검증 1
  contract_consistency: pending      # contract ↔ 설계 정합 (cross-ref 축) — S2 검증 3
  with_without_skill_eval: pending   # Skill 효용 비교 (신규 0 권장의 검증) — S2 검증 4
```

> factory_contract 규칙 7: validation 3필드가 pending 인 본 blueprint 는 **active 아님**. outputs/TEST/ 에 격리. 6검증 통과 + 사용자 승인 전 적용 금지.

---

이 blueprint 는 meta_factory machinery(generation_workflow 11단계 + harness_blueprint_schema + architecture_patterns + 6 templates)를 적용하여 작성됨 (WITH arm).
