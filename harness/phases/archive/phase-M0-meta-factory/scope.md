# Phase M0 — Scope

## 포함 (In-Scope) — 모두 신규 문서/skeleton

### meta_factory/ 루트 (신규)

| 파일 | 작업 |
|---|---|
| `harness/meta_factory/README.md` | **신규** — L1/L2/L3 모델 + proposal-first 명시 |
| `harness/meta_factory/factory_contract.md` | **신규** — 8 절대 규칙 (런타임 미변경 + proposal-first) |
| `harness/meta_factory/domain_brief_schema.md` | **신규** — 도메인 입력 schema |
| `harness/meta_factory/harness_blueprint_schema.md` | **신규** — blueprint 출력 schema |
| `harness/meta_factory/architecture_patterns.md` | **신규** — 6 패턴 + Dreammate 매핑 |
| `harness/meta_factory/generation_workflow.md` | **신규** — 11단계 생성 절차 |
| `harness/meta_factory/validation_workflow.md` | **신규** — 6 검증 (trigger/conflict/contract/with-without/eval-run/acceptance) |

### meta_factory/ 하위 (신규)

| 경로 | 작업 |
|---|---|
| `meta_factory/templates/{agent,skill,contract,eval,phase,project_state}_template.md` | **신규** — 6 scaffold 템플릿 |
| `meta_factory/blueprints/dreammate_current_harness_blueprint.md` | **신규** — 현재 하네스 실측 역정리 |
| `meta_factory/outputs/generated_harnesses/.gitkeep` | **신규** |
| `meta_factory/outputs/improvement_reports/.gitkeep` | **신규** |

### Skill (proposal-only, 1개)

| 파일 | 작업 |
|---|---|
| `.claude/skills/harness-factory/SKILL.md` | **신규** — proposal-only (키워드 scoping) |
| `.claude/skills/INDEX.md` | **수정** — #21 harness-factory 등록 + 우선순위 표 + 충돌 검토 |

### Docs / Meta (신규)

| 파일 | 작업 |
|---|---|
| `docs/decisions/phase_M0_meta_factory.md` | **신규** — ADR-035 (L3 Meta-Factory 도입) |
| `meta/validations/2026-05-31_phase-M0-pre-entry_self.md` + external | **신규** |
| `meta/proposals/2026-05-31_phase-M0-harness-factory-skill.md` | **신규** — Skill 등록 contract-change proposal |
| `docs/contract_changes/2026-05-31_phase-M0-skill-index.md` | **신규** — CC-006 (INDEX Skill 등록) |
| `meta/retrospectives/phase-M0.md` | **신규** |
| `meta/patterns.md` / `meta/skill_usage_log.md` | **수정** |
| `PROJECT_STATE / PHASE_REGISTRY / 00_START_HERE / README` | **수정** (meta-phase 등록) |

### Scripts

| 파일 | 작업 |
|---|---|
| `scripts/smoke_test_phase_M0.ps1` | **신규** — meta-phase 경량 체크 (런타임 회귀 0 + meta_factory 구조 존재 + audit) |
| `scripts/scenario_simulation.ps1` | **수정** — v7 (SM1~SM3 meta_factory 시나리오) |

## ★ 절대 수정 금지 (forbidden — non_goals)

```
backend/fastapi/** (FastAPI runtime — 0줄)
apps/web/** (Next.js — 0줄, PlanCard·component_map 포함)
backend/fastapi/db/migrations/** (Supabase migration — 0줄)
docs/contracts/{api,output_schema,agent_io,db_schema,llm_security,...}.md (기존 contract 직접 변경 X)
AGENTS.md / CLAUDE.md (라우터 직접 변경 X)
기존 .claude/skills/*/SKILL.md (harness-factory 신규 외 변경 X)
eval/** (golden_set 등 — 참조만, 변경 X)
phases/archive/** (참조만)
이전 ADR (014~034)
```

## 예상 파일 변경 수
- **신규**: ~22 (meta_factory 7 루트 + templates 6 + blueprint 1 + .gitkeep 2 + Skill 1 + ADR-035 + validations 2 + proposal + CC-006 + retrospective + smoke)
- **수정**: ~6 (INDEX.md + scenario_sim + patterns + skill_usage + state docs)
- **런타임 변경**: **0** (A9)
