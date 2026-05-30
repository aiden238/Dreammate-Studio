# harness_blueprint_schema.md — 하네스 청사진 출력 schema

> 위치: `harness/meta_factory/harness_blueprint_schema.md`
> 상태: Phase M0 Slice 1 — L3 Meta-Factory 의 **생성 출력** 구조
> 결정: ADR-035
> 참조: domain_brief_schema.md (생성 입력), architecture_patterns.md (6 패턴), factory_contract.md (8 규칙), validation_workflow.md (6 검증, Slice 2)

---

## 0. 이 문서의 위치

harness_blueprint 는 domain_brief(입력)를 받아 generation_workflow(Slice 2)가 설계하는 **출력 청사진**이다. "이 하네스가 어떤 agent / skill / contract / eval / phase / routing 으로 구성되는가" 를 구조화한다. 현재 하네스를 역정리할 때도 동일 schema 를 쓴다 (`blueprints/dreammate_current_harness_blueprint.md`, Slice 2).

★ blueprint 는 **proposal** 이다 — validation_workflow 6 검증 통과 전 active 아님 (factory_contract 규칙 7). 생성 blueprint 는 outputs/generated_harnesses/ 에 둔다.

---

## 1. Schema 필드

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `harness_name` | string | ✅ | 하네스 식별자 (snake_case) |
| `purpose` | string | ✅ | 한 줄 목적 (domain_brief.domain_summary 계승) |
| `architecture_pattern` | enum \| list | ✅ | architecture_patterns.md 6 패턴 (주 패턴 + 보조) |
| `agents` | list[Agent] | ✅ | agent 정의 (아래 Agent 구조) |
| `skills` | list[Skill] | ✅ | Skill 정의 (아래 Skill 구조) |
| `contracts` | list[Contract] | ✅ | contract 정의 (path + purpose) |
| `evals` | list[Eval] | ✅ | eval 정의 (path + purpose) |
| `phases` | list[Phase] | ✅ | phase 정의 (아래 Phase 구조) |
| `routing_docs` | list[string] | ✅ | 라우터 문서 (예: AGENTS.md / CLAUDE.md) |
| `validation` | Validation | ✅ | 검증 결과 (아래 Validation 구조) |

### 1.1 하위 구조

```
Agent:
  name: string                # agent 식별자
  responsibility: string      # 한 줄 책임
  inputs: list[string]        # 입력 (envelope 필드 / 이전 agent 출력)
  outputs: list[string]       # 출력 (schema 필드)
  forbidden_actions: list[string]   # 이 agent 가 하지 않는 것

Skill:
  name: string                # Skill 식별자 (kebab-case)
  trigger_keywords: list[string]    # 트리거 키워드 (충돌 검토 대상)
  applies_to: list[enum]      # agents | claude | both
  related_contracts: list[string]   # 연관 contract

Contract:
  path: string                # docs/contracts/*.md
  purpose: string             # 무엇을 정의하는가

Eval:
  path: string                # eval/*.md
  purpose: string             # 무엇을 측정하는가

Phase:
  phase_name: string          # phase 식별자
  goals: list[string]         # 핵심 목표
  non_goals: list[string]     # 절대 금지
  acceptance: list[string]    # 수락 기준

Validation:
  trigger_validation: pass | fail | pending | pending-by-design      # Skill/agent 트리거 정합
  contract_consistency: pass | fail | pending | pending-by-design    # contract ↔ 구현 정합
  with_without_skill_eval: pass | fail | pending | pending-by-design # Skill 효용 비교
  # pending-by-design : "실측 미수행이 정상인 경우" — 예: 검증5 eval-run 이 dry-run(실 LLM 미호출)이라
  #                     절차/임계값/케이스 매핑은 적용 가능하나 실 점수만 미측정. 단순 pending(미완)과 구별.
  # 차원별 sub-status (선택) : 한 필드가 혼합 상태일 때 차원별로 분해 표기 가능
  #   예: with_without_skill_eval: pass (누락률) / pending-by-design (품질·일관성, 소표본·실측 미수행)
```

---

## 2. YAML 예시 (Dreammate 역작성 발췌 — 참조용)

> 아래는 현재 Dreammate 하네스를 blueprint 형식으로 역작성한 **발췌 예시**다 (실측 전체 역정리는 `blueprints/dreammate_current_harness_blueprint.md`, Slice 2).

```yaml
harness_name: dreammate_video_planning_harness
purpose: "영상기획 AI 에이전트 — Discovery + Quick UX, 3-plan + Critic revise"
architecture_pattern:
  primary: supervisor          # orchestrator 중개 (moa_orchestrator)
  secondary: [fan_out_fan_in, producer_reviewer, pipeline]

agents:
  - name: intent
    responsibility: "의도 분석 (Discovery/Quick 분기 + Intent Filter)"
    inputs: [user_message, locale]
    outputs: [intent_ok, reason]
    forbidden_actions: [RAG 직접 의존, plan 생성]
  - name: planning
    responsibility: "영상기획안 3개 생성 (parallel, multi-model)"
    inputs: [user_message, rag_context]
    outputs: [plan_candidates x3]
    forbidden_actions: [Critic 직접 호출]
  - name: critic
    responsibility: "plan 평가 (canonical overall_score + dimensions)"
    inputs: [plan_dict]
    outputs: [overall_verdict, overall_score, dimensions]
    forbidden_actions: [plan 직접 수정]
  - name: rewriter
    responsibility: "Critic verdict=revise 시 plan 개선 (max 2)"
    inputs: [plan_dict, verdict]
    outputs: [revised_plan]
    forbidden_actions: [무한 revise]

skills:
  - name: contract-change
    trigger_keywords: [contract 변경, schema 변경, breaking change]
    applies_to: [agents, claude]
    related_contracts: [전체]
  - name: eval-run
    trigger_keywords: [eval 실행, golden_set, regression]
    applies_to: [agents]
    related_contracts: [output_schema]

contracts:
  - path: docs/contracts/agent_io_contract.md
    purpose: "MOA 4 agent 입출력/실행 정책"
  - path: docs/contracts/output_schema.md
    purpose: "Envelope/Plan/Critic 출력 본문"

evals:
  - path: eval/golden_set.md
    purpose: "회귀 케이스 11개 (GS-001~GS-011) 단일 출처"
  - path: eval/video_planning_eval.md
    purpose: "8차원 critic 채점"

phases:
  - phase_name: phase-9.5-eval-run
    goals: [eval-run 정식화, Critic deprecated 0–5 제거]
    non_goals: [run_critic 0–5 변경, RAG eval_rubric]
    acceptance: [golden_set 회귀 PASS, canonical-only 품질 동일]

routing_docs:
  - AGENTS.md       # 구현/QA 모델 라우터
  - CLAUDE.md       # 기획/설계 모델 라우터

validation:
  trigger_validation: pending       # Slice 2 validation_workflow
  contract_consistency: pending
  with_without_skill_eval: pending
```

---

## 3. 작성 규칙

1. **agents[].forbidden_actions 필수** — agent 격리(직접 호출 금지) 가 architecture_pattern(특히 supervisor)의 핵심.
2. **skills[].trigger_keywords 는 충돌 검토 대상** — INDEX 의 기존 Skill 키워드와 비중첩 (factory_contract 규칙 4).
3. **phases[].non_goals 필수** — scope creep 차단.
4. **validation 3 필드는 생성 직후 pending** — validation_workflow(Slice 2) 통과 후 pass. pending blueprint 는 active 아님 (factory_contract 규칙 7).
   - **pending-by-design 구별** — 실측이 dry-run 이라 미수행이 **정상**인 경우(예: 검증5 eval-run 이 실 LLM 미호출)는 단순 `pending`(미완) 과 구별해 `pending-by-design` 으로 기록한다. validation_workflow §4 판정 종합과 정합: `pending-by-design` 은 "미완 보완 대상"이 아니라 "dry-run 범위상 정상" 이며, 여전히 active 아님(규칙 7) 은 유지된다 — 기존 pass/fail/pending 판정 의미는 보존하고 정상 미측정만 추가 구별. 한 필드가 차원별로 혼합(누락률=pass / 품질=pending-by-design)이면 sub-status 로 분해 표기.
5. blueprint 는 domain_brief 의 required_contracts / required_evals / forbidden_scope 를 contracts / evals / phases[].non_goals 로 매핑해야 한다.

---

## 4. 다음 단계

blueprint 출력 → `validation_workflow.md` 6 검증 (Slice 2 — trigger / conflict / contract / with-without / eval-run / acceptance) → 전부 pass 시 사용자 승인 → (승인 시) active 전환. 실측 역정리 blueprint 는 `blueprints/dreammate_current_harness_blueprint.md` (Slice 2).
