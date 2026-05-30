# Phase M0 — Multi-Slice Plan

> 3 Slice 모두 sub-agent dispatch, sequential. 총 4~7h. 런타임 변경 0 (A9).

---

## Wave 구조
```
Wave 1: Slice 1 [Pre-Entry + 핵심 contract 문서]
  ↓
Wave 2: Slice 2 [Workflow + Blueprint + templates]
  ↓
Wave 3: Slice 3 [harness-factory Skill + INDEX + Close]
```

---

## Slice 1 — Pre-Entry + 핵심 contract (1.5~2.5h)
1. `meta/validations/2026-05-31_phase-M0-pre-entry_self.md` V1~V6 (L3 도입 타당성 / 런타임 0 / proposal-first / meta-phase 격리 / Skill 키워드 scoping / blueprint 실측) + external placeholder
2. `docs/decisions/phase_M0_meta_factory.md` (ADR-035 — L3 Meta-Factory 도입, L1/L2/L3 모델, proposal-first, payoff deferred 명시)
3. `meta_factory/README.md` — L1/L2/L3 모델 (사용자 §5.1) + proposal-first 명시
4. `meta_factory/factory_contract.md` — 8 절대 규칙 (사용자 §5.2)
5. `meta_factory/domain_brief_schema.md` (사용자 §5.3) + `harness_blueprint_schema.md` (사용자 §5.4)
6. `meta_factory/architecture_patterns.md` — 6 패턴 (Pipeline/Fan-out·in/Expert Pool/Producer-Reviewer/Supervisor/Hierarchical Delegation) + Dreammate 매핑 (사용자 §5.5)
7. skill_usage_log + PROJECT_STATE (meta-phase 등록) + entry commit
- editable: meta/validations, docs/decisions/phase_M0_meta_factory, meta_factory/{README, factory_contract, domain_brief_schema, harness_blueprint_schema, architecture_patterns}, skill_usage_log, PROJECT_STATE, phases/active/phase-M0-*/notes
- ★ forbidden: backend/apps/migrations(A9 0줄), 기존 contracts, AGENTS/CLAUDE, 기존 Skill, eval, 이전 ADR, baseline test

## Slice 2 — Workflow + Blueprint + templates (1.5~2.5h)
1. `meta_factory/generation_workflow.md` — 11단계 (사용자 §5.6) + proposal-first 명시
2. `meta_factory/validation_workflow.md` — 6 검증 (trigger validation / skill conflict / contract consistency / with-without comparison / eval-run 연동 / generated harness acceptance) (사용자 §5.7) + ★ eval-run Skill 연동
3. `meta_factory/templates/{agent,skill,contract,eval,phase,project_state}_template.md` — 6 scaffold
4. `meta_factory/blueprints/dreammate_current_harness_blueprint.md` — 현재 하네스 **실측** 역정리 (10 섹션 + L3 부족점 5). ★ 실측: golden_set 11 케이스, .claude/agents 부재, ADR-001~034, CC-005, P-X1 47, 20 Skill, MOA orchestrator Supervisor 등
5. `meta_factory/outputs/generated_harnesses/.gitkeep` + `outputs/improvement_reports/.gitkeep`
6. commit
- editable: meta_factory/{generation_workflow, validation_workflow}, meta_factory/templates/*, meta_factory/blueprints/*, meta_factory/outputs/*
- ★ forbidden: Slice 1 문서 코어(소폭만), backend/apps/migrations, 기존 contracts/Skill/eval, 이전 ADR
- 참조 읽기: PROJECT_STATE/AGENTS/CLAUDE/INDEX/eval-run SKILL/contracts (blueprint 역정리)

## Slice 3 — harness-factory Skill + INDEX + Close (1~2h)
1. **contract-change Skill** — `.claude/skills/harness-factory/SKILL.md` 신규 (proposal-only, 키워드 scoped: "harness blueprint, meta_factory, harness scaffold, 도메인 하네스 생성, agent/skill scaffold 설계". 금지: "하네스 개선"/"메타 개선"/bare "하네스 감사". 허용/금지 §명시 + 사용하지 않는 경우 → harness-audit/meta-retrospective 라우팅)
2. `.claude/skills/INDEX.md` 수정 — #21 harness-factory 등록 (검토/감사 또는 신규 Meta-Factory 섹션) + 우선순위 표 (`harness-audit > harness-factory`, `contract-change > harness-factory`, `eval-run > harness-factory validation`) + Skill 수 20→21
3. `meta/proposals/2026-05-31_phase-M0-harness-factory-skill.md` (Skill 등록 proposal) + `docs/contract_changes/2026-05-31_phase-M0-skill-index.md` (CC-006)
4. **harness-audit Skill** — harness-factory 키워드 충돌 검토 (harness-audit/meta-retrospective/phase-start와 0 충돌 확인, 기록)
5. `scripts/smoke_test_phase_M0.ps1` (경량: ★ A9 런타임 변경 0 + meta_factory 구조 존재 + audit_naming + pytest 339 유지) + `scenario_simulation.ps1` v7 (SM1 meta_factory 구조 / SM2 harness-factory Skill / SM3 blueprint)
6. audit×2 + scenario_sim v7 실행
7. `meta/retrospectives/phase-M0.md` + patterns(P-X1 50 + P-META-FACTORY-001 신규) + skill_usage_log(harness-factory 등록, 트리거 0 — proposal-only)
8. phase-complete v1.2.0 (P-X2 아홉 번째)
9. archive 이동 + closing_notes (다음: harness-factory dry-run / trigger validation 샘플 / with-without 비교 샘플 / Phase 10 연결)
10. PROJECT_STATE / PHASE_REGISTRY / 00_START_HERE / README (meta-phase 등록)
11. final commit
- editable: .claude/skills/harness-factory(신규), INDEX.md(등록), proposals, contract_changes(CC-006), scripts/{smoke_test_phase_M0, scenario_simulation v7}, meta/{retrospectives/phase-M0, patterns, skill_usage_log}, phases/archive/phase-M0-*, closing_notes, state docs
- ★ forbidden: backend/apps/migrations(A9 0줄), 기존 contracts, AGENTS/CLAUDE, 기존 Skill(harness-factory 외), eval, 이전 ADR, baseline test

---

## 충돌 매트릭스
| Slice | meta_factory root | templates/blueprint | Skill+INDEX | docs/decisions | meta/proposals+CC | scripts | meta(retro/patterns) | state |
|---|---|---|---|---|---|---|---|---|
| 1 | ✅ 5 문서 | ❌ | ❌ | ✅ ADR-035 | ❌ | ❌ | ✅ valid+skill_usage | ✅ entry |
| 2 | ✅ 2 workflow | ✅ templates+blueprint+outputs | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| 3 | ❌ | ❌ | ✅ harness-factory+INDEX | ❌ | ✅ proposal+CC-006 | ✅ smoke+scenario v7 | ✅ retro+patterns | ✅ all |

Sequential 충돌 0.

---

## 누적 P-X1 streak
| Phase | streak |
|---|---|
| Phase 9.5 | 47 |
| Phase M0 | **3 (목표)** |
| **누적** | **50** |

## 시간 추정
| Slice | 시간 | 누적 |
|---|---|---|
| 1 | 1.5~2.5h | 1.5~2.5h |
| 2 | 1.5~2.5h | 3~5h |
| 3 | 1~2h | **4~7h** |
