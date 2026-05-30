# generation_workflow.md — 하네스 생성 11단계 절차

> 위치: `harness/meta_factory/generation_workflow.md`
> 상태: Phase M0 (Meta-Factory Prep, ★ meta-phase) Slice 2 — 새 하네스 생성 절차
> 결정: ADR-035
> 참조: domain_brief_schema.md (입력), harness_blueprint_schema.md (출력), architecture_patterns.md (6 패턴), factory_contract.md (8 규칙), validation_workflow.md (6 검증)
> ★ 런타임 변경 0 (A9) — 본 절차는 outputs/ 에 blueprint 를 설계할 뿐 L1/L2 를 직접 수정하지 않는다.

---

## 0. 이 문서의 위치

`generation_workflow.md` 는 `domain_brief`(입력 명세)를 받아 `harness_blueprint`(출력 청사진)를 설계하는 **11단계 절차**를 정의한다. 각 단계는 무엇을 입력받아 무엇을 산출하는지, 어떤 schema/패턴을 따르는지, 어떤 제약을 받는지 명시한다.

★ 핵심 — **proposal-first**: 본 절차의 산출물(blueprint / scaffold)은 **기존 프로젝트에 직접 적용하지 않는다**. `meta_factory/outputs/generated_harnesses/` 에 **먼저** 초안으로 저장하고, `validation_workflow.md` 6 검증 통과 + 사용자 승인 후에만 active 로 전환한다 (factory_contract 규칙 3/7).

---

## 1. 11단계 개요

```
1.  domain_brief 수집          (사람 작성 입력)
2.  architecture pattern 선택   (6 패턴 중)
3.  agent 후보 생성            (templates/agent_template.md)
4.  skill 후보 생성            (templates/skill_template.md)
5.  contract 후보 생성         (templates/contract_template.md)
6.  eval 후보 생성             (templates/eval_template.md)
7.  phase 구조 생성            (templates/phase_template.md)
8.  routing 문서 생성          (AGENTS/CLAUDE 형식)
9.  validation_workflow 실행    (6 검증 — validation_workflow.md)
10. outputs/generated_harnesses/ 에 초안 저장   (★ proposal-first — active 아님)
11. 사용자 승인 후 적용         (승인 전 active 전환 금지)
```

> 단계 1~8 = blueprint 설계. 단계 9 = 검증. 단계 10 = 격리 저장. 단계 11 = 사람 승인 게이트. **자동 적용 단계는 존재하지 않는다.**

---

## 2. 단계 상세

### 단계 1 — domain_brief 수집

- **입력**: (없음 — 사람이 의도를 정의)
- **산출**: `domain_brief_schema.md` 형식 YAML (domain_name / domain_summary / target_users / primary_tasks / output_artifacts / runtime_type / risk_level / required_contracts / required_evals / forbidden_scope / preferred_architecture_patterns).
- **규칙**: domain_brief 는 **사람이 작성**한다 (meta_factory 가 자동 생성하지 않음 — proposal-first 정신, domain_brief_schema §3.5). `forbidden_scope` 필수 (scope creep 차단).
- **게이트**: 필수 11 필드 누락 시 다음 단계 진행 금지.

### 단계 2 — architecture pattern 선택

- **입력**: domain_brief.preferred_architecture_patterns + primary_tasks.
- **산출**: blueprint.architecture_pattern (주 패턴 1 + 보조 list).
- **규칙**: `architecture_patterns.md` 의 6 패턴(pipeline / fan_out_fan_in / expert_pool / producer_reviewer / supervisor / hierarchical_delegation) **에서만 선택**. 임의 패턴 금지. 여러 패턴 조합 가능.
- **게이트**: supervisor 선택 시 단계 3 의 agents[].forbidden_actions 에 "직접 호출 금지" 명시 예정 표시.

### 단계 3 — agent 후보 생성

- **입력**: architecture_pattern + primary_tasks + output_artifacts.
- **산출**: blueprint.agents (각 agent: name / responsibility / inputs / outputs / forbidden_actions) — `templates/agent_template.md` scaffold 기반.
- **규칙**: 각 agent 의 `forbidden_actions` 필수 (격리 — harness_blueprint_schema §3.1). producer_reviewer 조합 시 reviewer→producer revise 횟수 상한 명시.
- **게이트**: agent IO 가 단계 5 의 agent_io contract 와 정합 가능한지 예비 점검.

### 단계 4 — skill 후보 생성

- **입력**: primary_tasks + 운영 절차(생성/검토/감사/평가).
- **산출**: blueprint.skills (각 Skill: name / trigger_keywords / applies_to / related_contracts) — `templates/skill_template.md` scaffold 기반.
- **규칙**: `trigger_keywords` 는 **충돌 검토 대상** (factory_contract 규칙 4) — 기존/형제 Skill 키워드와 비중첩. `applies_to` 태그(agents / claude / both)로 라우터 분리. Skill 본문은 절차만 (데이터는 contract/eval/knowledge).
- **게이트**: 단계 9 trigger validation + skill conflict check 로 키워드 충돌 확인 예정.

#### 단계 4.1 — 신규 Skill vs 기존 재사용 결정트리 (★ G2, M1 검증4 근거)

> 신규 Skill 후보를 제안하기 **전에** 아래 트리를 통과한다. 기본값은 **재사용** — 신규 생성은 무충돌 + 고유 가치 입증 시에만.

```
1. 의도 작업의 키워드 추출 (이 Skill 이 어떤 표현으로 트리거되어야 하는가)
2. 기존 21 Skill 의 description 키워드와 충돌 검사 (INDEX §사용원칙 5 — "같은 description 키워드가 둘 이상 = 충돌")
3. 분기:
   - 충돌 발견 시  → 기존 Skill 재사용 강제 (신규 생성 금지). 라우터에서 기존 Skill 로 안내.
   - 무충돌 AND 신규 고유 가치 입증 시  → 신규 Skill 제안 (단계 4 scaffold 진행).
   - 무충돌 BUT 고유 가치 미입증 시  → 신규 생성 보류 (YAGNI 차단 — 미래 수요만으로 Skill 을 만들지 않는다).
```

- **YAGNI 차단 1줄**: "지금 필요 없는데 나중에 쓸지도 모른다"는 신규 Skill 생성 사유가 되지 못한다 — 충돌 위험만 늘리고 효용은 deferred.
- **근거 (M1 검증4)**: M1 dry-run 의 `podcast-eval-run` 신규 Skill 은 기존 `eval-run` 과 키워드 4중첩("eval 실행"/"golden_set"/"regression"/"품질 평가") → 충돌 = **음의 효용**으로 입증되어 채택 거부됨. 즉 "재사용이 옳다"가 절차로 명문화된다 (충돌 검사 → 충돌 시 재사용 강제).
- **게이트**: 본 결정트리에서 "재사용 강제" 로 분기된 Skill 은 단계 4 의 신규 scaffold 대상에서 제외하고, 단계 8 라우터가 기존 Skill 로 안내하도록 표시.

### 단계 5 — contract 후보 생성

- **입력**: domain_brief.required_contracts + agents IO.
- **산출**: blueprint.contracts (각 contract: path / purpose) — `templates/contract_template.md` scaffold 기반.
- **규칙**: cross-reference 정합 필수 (예: prompt_registry ↔ output_schema ↔ agent_io ↔ db_schema). 기존 하네스의 contract 형식(목적/필드/JSONB schema/cross-ref)을 따른다.
- **게이트**: 단계 9 contract consistency 검증 예정.

### 단계 6 — eval 후보 생성

- **입력**: domain_brief.required_evals + output_artifacts.
- **산출**: blueprint.evals (각 eval: path / purpose) — `templates/eval_template.md` scaffold 기반.
- **규칙**: golden_set 케이스 형식 + 채점 차원 + 임계값을 `eval-run` Skill 형식에 정합. `risk_level: high` → human_review + security 평가 강제 (factory_contract 규칙 8).
- **게이트**: 단계 9 eval-run 연동 검증 예정.

### 단계 7 — phase 구조 생성

- **입력**: primary_tasks + output_artifacts + forbidden_scope.
- **산출**: blueprint.phases (각 phase: goals / non_goals / acceptance + entry files 8종) — `templates/phase_template.md` scaffold 기반.
- **규칙**: phase entry 8 files(goals / scope / non_goals / dependencies / acceptance / assumptions / multi_slice_plan / notes) 형식. domain_brief.forbidden_scope → phases[].non_goals 매핑 필수 (scope creep 차단).
- **게이트**: acceptance / non_goals / rollback·retrospective 경로 존재 확인 (단계 9 acceptance 검증).

### 단계 8 — routing 문서 생성

- **입력**: agents + skills + contracts + evals + phases.
- **산출**: blueprint.routing_docs (구현/QA 모델 라우터 + 기획/설계 모델 라우터 — AGENTS.md / CLAUDE.md 형식).
- **규칙**: 라우터는 본문 지침을 담지 않고 작업 유형별 참조 문서 + Skill 을 안내한다. `applies_to` 태그로 역할별 Skill 인지 분리.
- **게이트**: 모든 agent/skill/contract/eval/phase 가 라우팅 경로에 연결되는지 점검.

### 단계 9 — validation_workflow 실행 (★ 6 검증)

- **입력**: 단계 1~8 의 blueprint (validation 3 필드 = pending).
- **산출**: `validation_workflow.md` 6 검증 결과 (trigger validation / skill conflict check / contract consistency / with-without skill comparison / ★ eval-run 연동 / generated harness acceptance).
- **규칙**: blueprint.validation 의 trigger_validation / contract_consistency / with_without_skill_eval 를 pending → pass/fail 로 갱신. eval-run 연동은 `eval-run` Skill §3~§6 절차를 cross-ref.
- **게이트**: 6 검증 중 하나라도 fail → blueprint 는 active 로 진행 불가 (factory_contract 규칙 7). outputs/ 에 머무르며 보완.

### 단계 10 — outputs/generated_harnesses/ 에 초안 저장 (★ proposal-first)

- **입력**: 검증 결과가 담긴 blueprint.
- **산출**: `meta_factory/outputs/generated_harnesses/{harness_name}_blueprint.md` (또는 폴더) — **active 아님**.
- **규칙 (★ 핵심)**: 생성 결과는 **기존 프로젝트(L2 운영 경로)에 직접 적용하지 않는다**. 반드시 `generated_harnesses/` 에 **먼저** 둔다. 개선 제안은 `outputs/improvement_reports/` 또는 `meta/proposals/` 에 둔다 (factory_contract 규칙 3).
- **게이트**: active 경로(AGENTS/CLAUDE/contracts/phases/skills 운영 위치)에 쓰기 발생 시 즉시 revert (규칙 위반).

### 단계 11 — 사용자 승인 후 적용

- **입력**: 6 검증 전부 pass + generated_harnesses 초안.
- **산출**: 사용자 승인 기록 → (승인 시) active 전환 절차로 인계.
- **규칙**: 생성된 harness 는 6 검증 통과 + **사용자 승인** 전까지 active 로 간주하지 않는다 (factory_contract 규칙 7). PROJECT_STATE 등 상태 문서 갱신은 사용자 승인 없이 금지 (규칙 6). Skill/contract 의 실제 active 반영은 `contract-change` Skill 절차를 경유 (규칙 5).
- **게이트**: 사용자 승인 없이 단계 11 을 자동 수행하지 않는다 — 본 절차의 종착점은 사람의 판단이다.

---

## 3. 단계 ↔ template / schema 매핑

| 단계 | 입력 schema | 산출 | template | 검증 |
|---|---|---|---|---|
| 1 | — | domain_brief | (사람 작성) | 11 필드 |
| 2 | domain_brief | architecture_pattern | architecture_patterns.md | 6 패턴 한정 |
| 3 | pattern | agents[] | agent_template.md | forbidden_actions |
| 4 | tasks | skills[] | skill_template.md | 키워드 충돌 |
| 5 | required_contracts | contracts[] | contract_template.md | cross-ref |
| 6 | required_evals | evals[] | eval_template.md | eval-run 정합 |
| 7 | forbidden_scope | phases[] | phase_template.md | non_goals 매핑 |
| 8 | 전체 | routing_docs[] | (AGENTS/CLAUDE 형식) | 라우팅 연결 |
| 9 | blueprint | validation 결과 | validation_workflow.md | 6 검증 |
| 10 | 검증 blueprint | generated_harnesses/ | — | proposal-first |
| 11 | pass + 초안 | 승인 기록 | — | 사용자 승인 |

---

## 4. 작성 규칙 (요약)

1. **proposal-first 절대** — 단계 10/11 전 active 적용 금지 (factory_contract 규칙 3/7).
2. **6 패턴 한정** — 단계 2 임의 패턴 금지 (architecture_patterns.md).
3. **forbidden 우선** — domain_brief.forbidden_scope → phases[].non_goals (단계 7) 필수 매핑.
4. **키워드 충돌 0** — 단계 4 Skill trigger_keywords 비중첩 (단계 9 검증).
5. **contract 변경은 contract-change 경유** — 단계 11 실 반영 시 (규칙 5).
6. **사용자 승인 게이트** — 단계 11 은 자동화하지 않는다 (payoff deferred, skeleton-only).

---

## 5. 다음 단계

생성된 blueprint → `validation_workflow.md` 6 검증 (단계 9) → outputs/generated_harnesses/ (단계 10) → 사용자 승인 (단계 11) → (승인 시) active 전환. 현재 하네스를 동일 절차로 역정리한 실측 결과는 `blueprints/dreammate_current_harness_blueprint.md`.
