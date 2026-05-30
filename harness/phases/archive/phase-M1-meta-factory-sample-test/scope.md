# Phase M1 — Scope

> ★ 범위는 **`meta_factory/outputs/` 내부 dry-run 만**으로 제한 (GPT 최종 판단). 그 외 전부 forbidden.

## 포함 (In-Scope) — 전부 `meta_factory/outputs/` 내부, proposal-first

### S1 산출물 — `outputs/TEST/podcast/` (신규 — ★ TEST 폴더)

| 파일 | 작업 | 비고 |
|---|---|---|
| `_without_baseline.md` | **신규** | without 팔 — meta_factory 미참조 일반 프롬프트 결과 (★ machinery 읽기 전 먼저 작성, 오염 최소화) |
| `domain_brief.md` | **신규** | with 팔 입력 — `domain_brief_schema.md` 형식 (forbidden_scope 포함) |
| `harness_blueprint.md` | **신규** | with 팔 출력 — `harness_blueprint_schema.md` 형식 (validation 3필드 포함) |
| `scaffolds/{agent,skill,contract,eval,phase,project_state}_draft.md` | **신규** | 6 scaffold draft (`templates/` 기반) |

### S2 산출물 — `outputs/TEST/` (신규 — ★ TEST 폴더)

| 파일 | 작업 | 비고 |
|---|---|---|
| `sample_test_podcast_validation.md` | **신규** | 6 검증 결과 (PASS/FAIL/PENDING/GAP) + with/without 6지표 수치표 + GAP 목록 + 보완 제안 |
| `outputs/TEST/podcast/harness_blueprint.md` | **수정(소폭)** | validation 3필드(trigger_validation/contract_consistency/with_without_skill_eval) 결과 기입만 |

## ★★ 변경 허용 / 금지 (GPT 보완 ③ — 강제 게이트)

```
변경 허용 (editable) — dry-run sub-agent:
  harness/meta_factory/outputs/TEST/**          (★ TEST 폴더 — 본 phase 의 모든 dry-run 산출물 여기에만)

변경 금지 (forbidden) — dry-run sub-agent:
  harness/meta_factory/outputs/{generated_harnesses,improvement_reports}/**  (★ 실 산출 영역 — TEST 와 분리, 변경 X)
  harness/backend/fastapi/**          (A9 — 0줄)
  harness/apps/web/**                 (A9 — 0줄, PlanCard·component_map 포함)
  harness/backend/fastapi/db/migrations/**   (A9 — 0줄)
  harness/AGENTS.md / harness/CLAUDE.md      (라우터)
  harness/PROJECT_STATE.md / harness/PHASE_REGISTRY.md
  harness/docs/contracts/**           (기존 contract)
  harness/.claude/skills/**           (harness-factory 포함 — 읽기만)
  harness/meta_factory/*.md (root)    (machinery 문서 — 읽기만, 변경 X)
  harness/meta_factory/{templates,blueprints}/**  (읽기만)
  harness/eval/**                     (golden_set 등 — 읽기만)
  harness/phases/**                   (M1 entry/notes 포함 — dry-run 중 변경 X)
  이전 ADR (001~035)
```

> ★ dry-run sub-agent 는 **machinery 와 기존 하네스를 읽기만** 하고, 출력은 **오직 `outputs/`** 에만 쓴다.

## ★ 별도 doc-sync 로 분리 (GPT 보완 ③ — dry-run 에 포함 X)

다음 phase 운영 작업은 dry-run 종료 **후**, main 세션이 **별도 commit** 으로 수행 (sub-agent dry-run 과 분리):

```
PROJECT_STATE.md / PHASE_REGISTRY.md   — M1 meta-phase 등록 + 완료 기록
meta/retrospectives/phase-M1.md        — dry-run 결과 + GAP 요약 + 다음 개선
meta/patterns.md / skill_usage_log.md  — P-X1 52 + harness-factory 첫 트리거 기록
phases/active → archive (git mv)        — phase-complete
00_START_HERE.md / README              — 등록 (필요 시)
(선택) docs/decisions ADR-036          — 첫 dry-run 방법·결과 요약
```

## 예상 파일 변경 수
- **dry-run 신규** (TEST/): ~9 (without 1 + brief 1 + blueprint 1 + scaffold 6) + validation 리포트 1 = ~11, 전부 `meta_factory/outputs/TEST/**`
- **dry-run runtime 변경**: **0** (A9) / **dry-run `outputs/TEST/` 외 변경**: **0** (MG1)
- **별도 doc-sync**: ~6 (state/registry/retro/patterns/usage/archive) — main 세션 별도 commit
