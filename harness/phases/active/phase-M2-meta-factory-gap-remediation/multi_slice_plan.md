# Phase M2 — Multi-Slice Plan

> 3 Slice (sub-agent, sequential) + entry(main) + doc-sync(main). 총 3~5h. ★ 런타임 0 (A9) + additive-only (A5).

---

## Wave 구조
```
entry (main)  : 8 phase 파일 + validation self(9th) + proposal(M1 §D 추적)
  ↓
Wave 1: S1 [생성 입력/절차 cluster — G1/G2/G5/G6]   (sub-agent, machinery edit)
  ↓
Wave 2: S2 [scaffold/schema cluster — G3/G4/G7/G8]   (sub-agent, machinery edit)
  ↓
Wave 3: S3 [재검증 — M1 TEST 재적용 before/after]    (sub-agent, outputs/TEST/ + machinery 읽기)
  ↓
doc-sync (main): CC-007 + ADR-037 + retrospective + patterns + skill_usage_log + state + archive
```

---

## entry (main 세션)
- 8 phase 파일 (본 폴더) + `meta/validations/2026-05-31_phase-M2-pre-entry_self.md` (V1~V5: 8 GAP 반영 타당성 / additive backward-compat / A9 런타임0 / CC-007 scope / 재검증 계획) + external placeholder + `meta/proposals/2026-05-31_phase-M2-gap-remediation.md` (M1 §D proposal 추적 + 8 승인 변경 표)
- entry commit

## Slice S1 — 생성 입력/절차 cluster (~1h, sub-agent)
1. `generation_workflow.md` 단계4 — **G2** 신규 Skill vs 기존 재사용 결정트리 (① 의도 작업 키워드 추출 → ② 기존 21 Skill 키워드 충돌 검사(INDEX 규칙) → ③ 충돌 시 재사용 강제 / 무충돌 + 신규 가치 입증 시에만 신규. YAGNI 차단)
2. `architecture_patterns.md` — **G1** expert_pool vs 단일 agent 파라미터화 결정 기준 (특화도 高 + 포맷 수 多 + 독립 진화 → expert_pool / 그 외 단일 agent 파라미터화. 비용·유지보수 임계 명시)
3. `domain_brief_schema.md` — **G5** risk_level 판정에 "제3자(비사용자) PII 처리 → risk 등급 상향 트리거" 축 + **G6** `data_model` 선택 필드 (계층 구조 + 엔티티 + PII 표시)
4. self-verification (P-X1) + commit (`feat(meta-m2): S1 generation/input cluster — G1/G2/G5/G6 machinery`)
- **editable**: `meta_factory/{generation_workflow, architecture_patterns, domain_brief_schema}.md` (오직)
- ★ **forbidden**: backend/apps/migrations(A9), docs/contracts, AGENTS/CLAUDE, .claude/skills, meta_factory/{README,factory_contract,validation_workflow,harness_blueprint_schema}.md + templates + blueprints + outputs(S3 전), eval, 이전 ADR, phases
- ★ **additive-only**: 기존 절차/필드 삭제·재명명 금지 — 추가만

## Slice S2 — scaffold/schema cluster (~1~1.5h, sub-agent)
1. `templates/agent_template.md` — **G3** `conditional_execution` 슬롯 (예: `condition: mode==guest` — 조건부 실행 agent 표현)
2. `templates/contract_template.md` — **G3** cross-ref 표에 "조건부 산출(conditional output)" 행 (X 조건일 때만 산출)
3. `templates/eval_template.md` — **G4** 채점 차원에 `applies_when` (조건부 차원 + 미해당 시 평균에서 제외 규칙)
4. `templates/project_state_template.md` — **G7** `harness_status` enum (active / dry-run-blueprint / proposal)
5. `harness_blueprint_schema.md` — **G8** validation 3필드 enum 에 `pending-by-design`(실측 미수행 정상) + 차원별 sub-status 가이드
6. self-verification (P-X1) + commit (`feat(meta-m2): S2 scaffold/schema cluster — G3/G4/G7/G8 machinery`)
- **editable**: `meta_factory/templates/{agent, contract, eval, project_state}_template.md` + `meta_factory/harness_blueprint_schema.md` (오직)
- ★ **forbidden**: S1 과 동일 (단 S1 대상 3파일도 이 Slice 에선 비변경)
- ★ **additive-only**

## Slice S3 — 재검증 (re-validate against M1 TEST, ~1h, sub-agent)
1. M1 산출물(`outputs/TEST/podcast/*`) + 개선 machinery(S1·S2) 읽기
2. 개선 슬롯 **적용 시연** (소폭): guest_brief/question/shownotes agent 에 conditional_execution / domain_brief 에 data_model + 게스트 PII risk 격상 / blueprint validation 에 pending-by-design / project_state 에 harness_status=dry-run-blueprint
3. **8 GAP before/after 표** + 개선 machinery 로 **6검증 재실행** (M1 에서 GAP-flag 였던 검증3 조건부축 / 검증4 표현 / 검증5 pending 표현이 이제 해소/표현 가능한지)
4. → `outputs/TEST/sample_test_podcast_revalidation.md` (8 GAP 해소 판정 + 6검증 재판정 + backward-compat 확인)
5. self-verification (P-X1) + commit (`feat(meta-m2): S3 re-validate M1 TEST — 8 GAP before/after`)
- **editable**: `meta_factory/outputs/TEST/**` (오직 — revalidation 리포트 + podcast 소폭 적용)
- ★ **forbidden**: machinery 문서(S1·S2 산출 — 읽기만, 재변경 X) + backend/apps/migrations + docs/contracts + Skill + 이전 ADR + phases

## doc-sync (main 세션, 별도 commit)
1. `docs/contract_changes/2026-05-31_phase-M2-machinery-gap.md` — **CC-007** (8 machinery 변경 + cross-ref 정합 + M1 §D proposal 추적 + backward-compat 확인)
2. `docs/decisions/phase_M2_meta_factory_gap_remediation.md` — **ADR-037**
3. `meta/retrospectives/phase-M2.md` + `meta/patterns.md` (P-X1 55 + P-META-FACTORY-002 update self-improvement loop 완주 + P-CONTRACT-FIRST-001 누적 7회) + `meta/skill_usage_log.md` (contract-change CC-007 + harness-factory 두 번째 실 트리거)
4. `PROJECT_STATE.md` / `PHASE_REGISTRY.md` (M2 등록 + done)
5. closing_notes + archive 이동 (git mv)
6. doc-sync commit (`docs(meta-m2): phase-M2 close — CC-007 + 재검증 + GAP 백로그 0`)

---

## 충돌 매트릭스
| Slice | gen/arch/brief | templates+blueprint_schema | outputs/TEST | CC/ADR/meta | state |
|---|---|---|---|---|---|
| entry | ❌ | ❌ | ❌ | ✅ valid+proposal | ✅ entry |
| S1 | ✅ 3 파일 | ❌ | ❌ | ❌ | ❌ |
| S2 | ❌ | ✅ 5 파일 | ❌ | ❌ | ❌ |
| S3 | ❌ (읽기만) | ❌ (읽기만) | ✅ revalidation | ❌ | ❌ |
| doc-sync | ❌ | ❌ | ❌ | ✅ CC-007+ADR+retro | ✅ all |

Sequential 충돌 0 (S1·S2 파일 비중첩이나 git index race 회피 위해 순차).

## 누적 P-X1 streak
| Phase | streak |
|---|---|
| Phase M1 | 52 (누적) |
| Phase M2 | **+3 (S1·S2·S3 목표)** |
| **누적** | **55** |

## 시간 추정
| 단계 | 시간 | 누적 |
|---|---|---|
| entry | 0.3h | 0.3h |
| S1 | ~1h | ~1.3h |
| S2 | ~1~1.5h | ~2.3~2.8h |
| S3 | ~1h | ~3.3~3.8h |
| doc-sync | ~0.5h | **~3.8~4.3h** |
