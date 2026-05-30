---
name: harness-factory
description: |
  하네스 blueprint / meta_factory / harness scaffold / 도메인 하네스 생성 /
  agent·skill scaffold 설계가 필요할 때 사용한다 (L3 Meta-Harness Factory 진입점).
  domain_brief 기반 harness 초안 생성 + 기존 하네스 충돌 분석을 담당한다.
  ★ proposal-only — 생성물은 outputs/ 또는 meta/proposals/ 에 먼저 두고 자동 적용하지 않는다.
  키워드: "하네스 blueprint", "meta_factory", "harness scaffold", "도메인 하네스 생성",
  "agent/skill scaffold 설계", "harness-factory".
applies_to: [claude]
phase: [phase-10, ongoing]
related_contracts:
  - meta_factory/factory_contract.md
related_state:
  - meta_factory/README.md
  - meta_factory/generation_workflow.md
  - meta_factory/validation_workflow.md
  - meta_factory/domain_brief_schema.md
  - meta_factory/harness_blueprint_schema.md
  - meta_factory/architecture_patterns.md
  - meta_factory/blueprints/dreammate_current_harness_blueprint.md
  - meta_factory/outputs/
version: v1.0.0
---

# harness-factory

L3 Meta-Harness Factory(`harness/meta_factory/`)의 진입점. `domain_brief` 입력을 받아 `harness_blueprint` 초안을 설계·역정리·검증하고, 기존 하네스 충돌을 분석하여 개선을 제안한다. ★ **자동 적용 도구가 아니라 proposal-only 도구** — 생성물은 `meta_factory/outputs/` 또는 `meta/proposals/` 에 **먼저** 두고, `validation_workflow.md` 6 검증 + 사용자 승인 전까지 active 로 간주하지 않는다 (factory_contract 규칙 3/7).

## 트리거 조건

- 새 도메인 하네스 생성 요청 (`도메인 하네스 생성` / `harness scaffold`)
- 하네스 blueprint 작성/역정리 요청 (`하네스 blueprint` — 현재 하네스 청사진 정리 또는 신규 설계)
- `meta_factory` scaffold 설계 (agent·skill·contract·eval·phase 템플릿 기반 초안)
- 기존 하네스의 구조 충돌 분석 (Skill 키워드 충돌 / trigger 정합 / with-without 비교) — generation/validation 절차 영역

## 절차

### 1. domain_brief 수집

- 사람이 `domain_brief_schema.md` 형식(11 필드: domain_name / domain_summary / target_users / primary_tasks / output_artifacts / runtime_type / risk_level / required_contracts / required_evals / forbidden_scope / preferred_architecture_patterns)으로 입력을 작성한다.
- meta_factory 가 domain_brief 를 자동 생성하지 않는다 (proposal-first). `forbidden_scope` 필수.

### 2. generation_workflow 11단계 실행

- `generation_workflow.md` 의 11단계(domain_brief 수집 → architecture pattern 선택 → agent/skill/contract/eval/phase 후보 생성 → routing 문서 → validation 실행 → outputs 격리 → 사용자 승인)를 따른다.
- agent·skill·contract·eval·phase scaffold 는 `templates/{agent,skill,contract,eval,phase,project_state}_template.md` 6 scaffold 기반 (자동 편집 아님 — 템플릿 채움).
- architecture pattern 은 `architecture_patterns.md` 6 패턴(pipeline / fan_out_fan_in / expert_pool / producer_reviewer / supervisor / hierarchical_delegation)에서만 선택.

### 3. validation_workflow 6 검증

- `validation_workflow.md` 의 6 검증(trigger validation / skill conflict check / contract consistency / with-without skill comparison / ★ eval-run 연동 / generated harness acceptance)으로 blueprint 를 평가한다.
- 검증 5(eval-run 연동)는 `eval-run` Skill §3~§6 을 cross-ref (별도 평가 체계를 새로 만들지 않음). 검증 2(skill conflict)는 `INDEX.md` 의 키워드 충돌 규칙 + 우선순위 표를 따른다.
- 하나라도 fail → blueprint 는 active 로 진행 불가, outputs/ 에 머무르며 보완.

### 4. outputs/generated_harnesses/ 초안 저장 (★ proposal-first)

- 검증 결과가 담긴 blueprint 를 `meta_factory/outputs/generated_harnesses/` 에 초안으로 저장 (active 아님).
- 개선 제안은 `meta_factory/outputs/improvement_reports/` 또는 `meta/proposals/` 에 제출.
- active 경로(AGENTS/CLAUDE/contracts/phases/기존 skills 운영 위치)에 쓰기 발생 시 즉시 revert (규칙 위반).

### 5. 사용자 승인 게이트

- 6 검증 전부 pass + 사용자 승인 전까지 generated harness 는 active 로 간주하지 않는다.
- Skill/contract 의 실제 active 반영은 `contract-change` Skill 절차(제안 → 검토 → 승인 → 반영)를 경유. PROJECT_STATE 등 상태 문서 갱신은 사용자 승인 없이 금지.

## 허용 / 금지 (★ factory_contract 8 규칙 정합)

### 허용

- domain_brief 기반 harness blueprint **초안** 생성 (역정리 + 정방향 설계)
- agent·skill·contract·eval·phase **scaffold 제안** (6 템플릿 기반)
- 기존 하네스 충돌 분석 (Skill 키워드 충돌 / trigger 정합 / with-without 비교) — 분석·제안만
- 생성물을 `meta_factory/outputs/generated_harnesses/` 에 저장
- 기존 하네스 개선을 `meta_factory/outputs/improvement_reports/` 또는 `meta/proposals/` 에 제안

### 금지

- `AGENTS.md` / `CLAUDE.md` / `PROJECT_STATE.md` / `PHASE_REGISTRY.md` / `docs/contracts/**` **직접 수정** (proposal-first — factory_contract 규칙 2/5/6)
- product runtime 코드 수정 — FastAPI(`backend/fastapi/**`) / Next.js(`apps/web/**`) / Supabase(`db/migrations/**`) (factory_contract 규칙 1 — A9)
- 기존 `.claude/skills/*` **직접 추가·삭제·변경** (contract-change Skill 절차 경유 — 규칙 4/5)
- 사용자 승인 없이 generated harness 를 active 로 전환 (validation_workflow 통과 전 active 아님 — 규칙 7)
- domain_brief 자동 생성 / 자동 generator 코드 작성 (payoff deferred — skeleton·proposal 까지만)

## 사용하지 않는 경우

```
- 기존 하네스 정기 감사 (stub / 깨진 참조 / 미사용 Skill 점검) → harness-audit Skill
- 기존 하네스/프로세스 개선·회고 (반복 실패 / 메타 개선 / post-mortem) → meta-retrospective Skill
- docs/contracts/ 또는 기존 Skill 본문의 실 변경 → contract-change Skill
- 평가 실행 자체 (golden_set 회귀 / 품질 평가) → eval-run Skill
- 평가 체계 설계 (새 차원 / rubric / golden_set 확장) → eval-design Skill
- 새 product phase 진입/재개 → phase-start Skill
```

> ★ harness-factory 는 **생성·blueprint·scaffold 설계** 영역이다. **감사**(harness-audit) / **개선·회고**(meta-retrospective) / **contract 실 변경**(contract-change) / **평가 실행**(eval-run) 키워드는 침범하지 않는다 (키워드 scoped — INDEX 충돌 검토 0).

## 다른 Skill 과의 관계 (우선순위)

```
harness-audit         > harness-factory             # 기존 하네스 감사가 생성보다 상위
contract-change       > harness-factory             # contract/Skill 실 변경은 항상 절차 통과
eval-run              > harness-factory (validation) # 검증 5 의 실 평가는 eval-run 절차가 상위
meta-retrospective    ⊥ harness-factory             # 개선·회고(L2 in-place) ≠ 생성·blueprint(L3) — 키워드 분리
```

- harness-factory 의 validation_workflow 검증 5 는 `eval-run` Skill §3~§6 을 호출 (위임).
- 생성된 Skill/contract 의 active 반영은 `contract-change` Skill 절차로 위임.
- 기존 하네스 개선 제안은 self_improvement_loop + `meta-retrospective` 문화와 책임 분리 (L3 = 하네스 생성·blueprint / meta-retrospective = L2 in-place 개선).

## 종료 조건

- domain_brief → blueprint 초안이 `meta_factory/outputs/generated_harnesses/` 에 저장됨 (proposal-first)
- validation_workflow 6 검증 결과(pass/fail/pending)가 blueprint 와 함께 기록됨
- active 반영이 필요한 항목은 contract-change Skill 로 라우팅됨 (사용자 승인 게이트)
- ★ 어떤 경우에도 런타임(L1)/기존 하네스(L2) 자동 수정 0 (factory_contract 규칙 1/2)

## 변경 이력

- v1.0.0 (2026-05-31 Phase M0 Slice 3): harness-factory Skill 신규 등록 (proposal-only, 키워드 scoped). L3 Meta-Harness Factory(meta_factory/) 진입점 — domain_brief → blueprint 초안 + 충돌 분석 + 개선 제안. INDEX #21 + 우선순위(harness-audit > harness-factory, contract-change > harness-factory, eval-run > harness-factory validation) + 키워드 충돌 검토 0. ADR-035 + CC-006.
