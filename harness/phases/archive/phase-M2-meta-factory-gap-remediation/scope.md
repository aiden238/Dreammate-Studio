# Phase M2 — Scope

> ★ 변경 영역 = `meta_factory/` machinery docs (G1~G8) + 재검증 산출물(`outputs/TEST/`) + meta/state + CC-007. 런타임 0 (A9).

## 포함 (In-Scope)

### S1 — 생성 입력/절차 cluster (G1/G2/G5/G6)

| 파일 | 작업 | GAP |
|---|---|---|
| `meta_factory/generation_workflow.md` | **수정** — 단계4 에 "신규 Skill vs 기존 재사용 결정트리" 추가 (키워드 충돌 검사 → 충돌 시 재사용 강제, INDEX 규칙 정합) | G2 ★ |
| `meta_factory/architecture_patterns.md` | **수정** — "expert_pool vs 단일 agent 파라미터화 결정 기준" 추가 (특화도/비용/유지보수 임계) | G1 |
| `meta_factory/domain_brief_schema.md` | **수정** — risk_level 판정에 "제3자(비사용자) PII → risk 상향 트리거" 축 (G5) + `data_model` 선택 필드 (계층/엔티티/PII 표시, G6) | G5 ★, G6 |

### S2 — scaffold/schema cluster (G3/G4/G7/G8)

| 파일 | 작업 | GAP |
|---|---|---|
| `meta_factory/templates/agent_template.md` | **수정** — `conditional_execution` 슬롯 (예: `condition: mode==guest`) | G3 ★ |
| `meta_factory/templates/contract_template.md` | **수정** — cross-ref 표에 "조건부 산출(conditional output)" 행 | G3 ★ |
| `meta_factory/templates/eval_template.md` | **수정** — 채점 차원에 `applies_when` (조건부 차원, 미해당 시 평균 제외) | G4 |
| `meta_factory/templates/project_state_template.md` | **수정** — `harness_status` enum (active / dry-run-blueprint / proposal) | G7 |
| `meta_factory/harness_blueprint_schema.md` | **수정** — validation enum 에 `pending-by-design`(실측 미수행 정상) 또는 차원별 sub-status | G8 |

### S3 — 재검증 (re-validate against M1 TEST, → `outputs/TEST/`)

| 파일 | 작업 |
|---|---|
| `outputs/TEST/sample_test_podcast_revalidation.md` | **신규** — 8 GAP before/after + 개선 machinery 로 6검증 재실행 (이전 GAP-flag PASS → 해소 확인) |
| `outputs/TEST/podcast/*` (해당분만) | **수정(소폭)** — 개선 슬롯 적용 시연 (예: guest_brief agent conditional_execution, domain_brief data_model, blueprint validation pending-by-design) — before/after 입증용 |

### doc-sync (main 세션, 별도 commit)

| 파일 | 작업 |
|---|---|
| `docs/contract_changes/2026-05-31_phase-M2-machinery-gap.md` | **신규** — CC-007 (8 machinery 변경 + cross-ref 정합 + proposal 추적) |
| `docs/decisions/phase_M2_meta_factory_gap_remediation.md` | **신규** — ADR-037 |
| `meta/retrospectives/phase-M2.md` / `meta/patterns.md` / `meta/skill_usage_log.md` | **신규/수정** |
| `meta/validations/2026-05-31_phase-M2-pre-entry_self.md` + external | **신규** (entry, 아홉 번째 formal) |
| `meta/proposals/2026-05-31_phase-M2-gap-remediation.md` | **신규** (entry — M1 §D proposal 추적 + 8 승인 변경) |
| `PROJECT_STATE / PHASE_REGISTRY` | **수정** (M2 등록 + done) |

## ★ 변경 허용 / 금지

```
변경 허용 (editable):
  meta_factory/{generation_workflow, architecture_patterns, domain_brief_schema, harness_blueprint_schema}.md  (S1·S2)
  meta_factory/templates/{agent, contract, eval, project_state}_template.md                                    (S2)
  meta_factory/outputs/TEST/**                                                                                  (S3 재검증)
  docs/contract_changes/ (CC-007) / docs/decisions/ (ADR-037) / meta/** / PROJECT_STATE / PHASE_REGISTRY        (entry + doc-sync)
  phases/active|archive/phase-M2-*/                                                                             (entry + close)

변경 금지 (forbidden) — A9 핵심:
  backend/fastapi/**  (런타임 0)
  apps/web/**         (런타임 0, PlanCard·component_map 포함)
  backend/fastapi/db/migrations/**  (런타임 0)
  docs/contracts/**   (기존 product contract — api/output_schema/agent_io/db_schema/rag/llm_security 변경 X)
  AGENTS.md / CLAUDE.md  (라우터)
  .claude/skills/**   (Skill 본문 — harness-factory 포함, machinery 문서만 변경)
  meta_factory/{README, factory_contract, validation_workflow}.md  (본 phase 미대상 — G1~G8 가 가리키는 파일만)
  meta_factory/blueprints/**  (M0 실측 — 변경 X)
  meta_factory/outputs/{generated_harnesses, improvement_reports}/**  (실 산출 영역 — TEST 와 분리)
  eval/** (golden_set 등 — 참조만)
  이전 ADR (001~036)
```

## 예상 파일 변경 수
- **machinery 수정**: 8 (generation_workflow + architecture_patterns + domain_brief_schema + harness_blueprint_schema + templates 4)
- **재검증 신규/수정**: ~3 (revalidation 리포트 1 + podcast 산출물 소폭 2)
- **doc-sync**: ~8 (CC-007 + ADR-037 + retrospective + patterns + skill_usage_log + validation 2 + proposal + state docs 2)
- **런타임 변경**: **0** (A9)
