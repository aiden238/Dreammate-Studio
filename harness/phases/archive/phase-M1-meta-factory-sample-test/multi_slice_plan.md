# Phase M1 — Multi-Slice Plan

> 2 Slice (dry-run, sub-agent dispatch, sequential) + 별도 doc-sync 1단계 (main 세션).
> 총 2.5~4h. ★ dry-run 은 `meta_factory/outputs/**` 외부 0줄 (MG1) + 런타임 0 (A9).

---

## Wave 구조
```
Wave 1: Slice S1 [generation — without baseline + with blueprint + 6 scaffold]   (sub-agent, outputs only)
  ↓
Wave 2: Slice S2 [validation — 6검증 + with/without 6지표 + GAP 리포트]          (sub-agent, outputs only)
  ↓
Wave 3: doc-sync  [phase 등록/회고/archive]                                       (★ main 세션, 별도 commit — GPT 보완 ③)
```

---

## Slice S1 — Generation (1.5~2.5h, sub-agent)

`harness-factory` Skill 진입 → generation_workflow 11단계 dry-run.

1. **without baseline 먼저** (오염 최소화) — meta_factory/AGENTS/CLAUDE **미참조**, 일반 프롬프트("팟캐스트 에피소드 기획 AI 하네스 구조를 설계하라")만으로 naive 구조 작성 → `outputs/TEST/podcast/_without_baseline.md`
2. **with — domain_brief 작성**: `domain_brief_schema.md` 형식으로 팟캐스트 brief (도메인 정의/계층/forbidden_scope/필요 agent·skill·contract·eval 후보) → `.../podcast/domain_brief.md`
3. **with — generation_workflow 11단계 실행**: architecture_patterns 6 중 선택 → agent/skill/contract/eval/phase 후보 생성 → `harness_blueprint.md` (`harness_blueprint_schema` 형식, validation 3필드 슬롯 비워둠) → `.../podcast/harness_blueprint.md`
4. **6 scaffold draft**: `templates/{agent,skill,contract,eval,phase,project_state}_template.md` 기반 → `.../podcast/scaffolds/*_draft.md`
5. self-verification (P-X1) + commit (`feat(meta-m1): S1 podcast harness generation dry-run`)

- **editable**: `meta_factory/outputs/TEST/podcast/**` (오직)
- ★ **forbidden**: 그 외 전부 — backend/apps/migrations(A9), AGENTS/CLAUDE/PROJECT_STATE/PHASE_REGISTRY, docs/contracts, .claude/skills(harness-factory 포함 — 읽기만), meta_factory root·templates·blueprints(읽기만), `outputs/{generated_harnesses,improvement_reports}/`(실 산출 영역 — TEST 와 분리), eval, phases(M1 entry 포함), 이전 ADR
- **참조 읽기**: meta_factory 전체(machinery) + architecture_patterns + templates + (도메인 상식)

## Slice S2 — Validation + with/without + GAP (1~1.5h, sub-agent)

`harness-factory` → validation_workflow 6검증 + `eval-run` cross-ref(검증 5).

1. **6 검증 실행** (각 PASS/FAIL/PENDING/GAP):
   - 1 trigger validation / 2 skill conflict(INDEX 규칙) / 3 contract consistency(prompt↔output, api↔front, db↔migration, agent_io) / 4 with-without comparison / 5 eval-run 연동(절차 적용 가능성 — PENDING 예상) / 6 generated harness acceptance(최소 구조/forbidden 매핑/phase 8파일/eval gate/rollback·retro 경로)
2. **with/without 6 지표 수치표** (GPT 보완 ① — 주관 서술 금지):
   누락 필수파일 수 / forbidden_scope 반영(0·1) / Skill trigger 충돌 수 / contract cross-ref 누락 수 / eval gate 존재(0·1) / proposal-first 위반(0·1) — with 열 vs without 열
3. **5 gaps 재현 표** (A6) — M0 blueprint 의 현재 하네스 5 부족점이 팟캐스트에서 재현되는지
4. **GAP 목록 + 보완 제안** → `outputs/TEST/sample_test_podcast_validation.md`
5. blueprint.validation 3필드(trigger_validation/contract_consistency/with_without_skill_eval) 결과 기입 (harness_blueprint.md 소폭 수정)
6. **판정 종합** (A7) — 4상태 요약 + 다음 개선 입력
7. self-verification (P-X1) + commit (`feat(meta-m1): S2 podcast validation + with/without + GAP`)

- **editable**: `meta_factory/outputs/TEST/**` (improvement 리포트 + blueprint validation 필드만)
- ★ **forbidden**: S1 과 동일 (outputs 외 전부)
- **참조 읽기**: validation_workflow + eval-run SKILL §3~§6 + INDEX(충돌/우선순위) + M0 blueprint(5 gaps) + S1 산출물

## Wave 3 — doc-sync (★ main 세션, 별도 commit — dry-run 과 분리)

> GPT 보완 ③: "테스트 결과를 phase notes/retrospective 에 기록하려면 별도 doc-sync 로 분리." → sub-agent dry-run 의 outputs 게이트(MG1)를 깨지 않기 위해, 아래는 main 세션이 수행.

1. `meta/retrospectives/phase-M1.md` — 6검증 결과 + with/without 수치 + GAP 요약 + 다음 개선
2. `meta/patterns.md`(P-X1 52, P-META-FACTORY-002 첫 dry-run) + `skill_usage_log.md`(harness-factory 첫 실트리거)
3. (선택) `docs/decisions/phase_M1_meta_factory_sample_test.md` (ADR-036 — 첫 dry-run 방법·결과)
4. `PROJECT_STATE.md` / `PHASE_REGISTRY.md` — M1 등록 + 완료
5. phase-complete v1.2.0 (P-X2 열 번째) — archive 이동(git mv)
6. `00_START_HERE.md` / `README` 등록 (필요 시)
7. doc-sync commit (`docs(meta-m1): phase-M1 close — retrospective + GAP 등록`)

---

## 충돌 매트릭스
| Slice | outputs/TEST/podcast | outputs/TEST (report) | meta(retro/patterns) | state/registry | 비고 |
|---|---|---|---|---|---|
| S1 | ✅ (without+brief+blueprint+scaffold) | ❌ | ❌ | ❌ | sub-agent, outputs only |
| S2 | ✅ (blueprint validation 필드만) | ✅ (validation 리포트) | ❌ | ❌ | sub-agent, outputs only |
| doc-sync | ❌ | ❌ | ✅ | ✅ | ★ main 세션, 별도 commit |

Sequential 충돌 0. dry-run(S1·S2) ↔ doc-sync 권한 분리.

## 누적 P-X1 streak
| Phase | streak |
|---|---|
| Phase M0 | 50 (누적) |
| Phase M1 | **+2 (S1·S2 목표)** |
| **누적** | **52** |

## 시간 추정
| 단계 | 시간 | 누적 |
|---|---|---|
| S1 | 1.5~2.5h | 1.5~2.5h |
| S2 | 1~1.5h | 2.5~4h |
| doc-sync | 0.3~0.5h | ~3~4.5h |
