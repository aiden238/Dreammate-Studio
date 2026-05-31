# Phase M3 — Scope

> ★ dry-run (M1 동형) — 산출물 전부 `meta_factory/outputs/TEST/` 격리. machinery 개선본은 **읽기만**. 런타임 0.

## 포함 (In-Scope) — 전부 outputs/TEST/

### S1 — generation (개선 machinery 적용, → `outputs/TEST/finance/`)
| 파일 | 작업 |
|---|---|
| `_without_baseline.md` | 신규 — machinery 미참조 naive 재무 하네스 (오염 최소화, 먼저 작성) |
| `domain_brief.md` | 신규 — domain_brief_schema **개선본**(data_model G6 + 제3자 PII risk G5) 형식 |
| `harness_blueprint.md` | 신규 — harness_blueprint_schema **개선본**(validation pending-by-design G8) 형식 |
| `scaffolds/{agent,skill,contract,eval,phase,project_state}_draft.md` | 신규 — templates **개선본**(conditional_execution G3 / applies_when G4 / harness_status G7) 기반 |

### S2 — validation + M2 개선 점검 (→ `outputs/TEST/`)
| 파일 | 작업 |
|---|---|
| `sample_test_finance_validation.md` | 신규 — 6검증(4상태) + ★ M2 G1~G8 실사용 점검표 + 범용성 판정(미디어 편향 유무) + 새 GAP + 종합(분기 권고) |

### doc-sync (main 세션, 별도 commit)
- `meta/retrospectives/phase-M3.md` + `docs/decisions/phase_M3_*.md`(ADR-038, 선택) + patterns(P-X1 57 + P-META-FACTORY-002 범용성 2차) + skill_usage_log(harness-factory 세 번째 실 트리거) + PROJECT_STATE / PHASE_REGISTRY + closing_notes + archive.

## ★ 변경 허용 / 금지
```
변경 허용 (editable) — dry-run sub-agent:
  harness/meta_factory/outputs/TEST/**          (★ S1·S2 산출 — finance/ + validation 리포트)

변경 금지 (forbidden) — dry-run sub-agent:
  harness/backend/fastapi/** , apps/web/** , db/migrations/**   (A9 — 0줄)
  harness/AGENTS.md / CLAUDE.md / PROJECT_STATE.md / PHASE_REGISTRY.md
  harness/docs/contracts/**
  harness/.claude/skills/**
  harness/meta_factory/*.md (machinery 개선본 — 읽기만, 변경 X)
  harness/meta_factory/templates/** , blueprints/**            (읽기만)
  harness/meta_factory/outputs/{generated_harnesses,improvement_reports}/**  (실 산출 — TEST 분리)
  harness/meta_factory/outputs/TEST/podcast/** , TEST/sample_test_podcast_*  (M1·M2 산출 — 보존, 변경 X)
  harness/eval/** , phases/** , 이전 ADR
```

## ★ doc-sync 분리 (GPT 보완 ③ 계승)
phase 등록·회고·archive 는 dry-run 종료 후 main 세션 별도 commit (sub-agent outputs/TEST/ 게이트 무오염).

## 예상 파일 변경 수
- dry-run 신규(TEST/finance + validation): ~9 (without 1 + brief 1 + blueprint 1 + scaffold 6) + validation 1 = ~10, 전부 `meta_factory/outputs/TEST/**`
- dry-run 런타임 변경 0 (A9) / outputs/TEST/ 외 0 (MG1) / machinery 변경 0 (개선본 읽기만)
- doc-sync: ~6 (retro + patterns + skill_usage_log + state 2 + closing). 분기 시 Phase 10 entry 별도.
