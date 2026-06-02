# Phase 13 — Scope (출력 확장 — 제품 phase, gated 단계 롤아웃 + additive 스키마)

> ★ Phase 13 = **출력 확장(compact→rich)** 제품 phase. 이 프로젝트 **첫 의도적 출력 변경** — gated(flag OFF default) + additive(전부 Optional)로 안전하게. flag OFF 시 compact byte-identical(behavior-preserving).

## 포함 (In-Scope) — Entry + S1~S6

### Entry (본 문서 — phase-start 진입)
| 항목 | 작업 |
|---|---|
| `phases/active/phase-13-output-enrichment/` 8 entry | **신규** (goals/scope/non_goals/dependencies/acceptance/assumptions/multi_slice_plan/notes) |
| `meta/validations/2026-06-02_phase-13-pre-entry_self.md` (12th) | **신규** (multi-llm-validation self-form V1~V6) — ★ S1 직전 또는 entry 와 함께 |
| `PHASE_REGISTRY.md` / `PROJECT_STATE.md` | **수정** (Phase 13 active + Active 블록 갱신, Phase 12 done) |
- ★ 본 entry(문서)는 운영 코드 0 수정 — 실제 스키마/프롬프트 변경은 S1+ 에서.

### S1 — 스키마 확장 (output_schema contract-change + agent-io-check)
| 항목 | 작업 |
|---|---|
| `backend/fastapi/schemas/output.py` `Plan` | **수정 (additive)** — 결핍 feature 슬롯 추가: hook_variants[], beat(PlanFlowBeat)에 visual/dialogue/caption, shots[], thumbnail, title_candidates[], cta, references[], length_variants, target_audience, tone. ★ **전부 Optional default None/[]** → 기존 7필드(name/concept/hook/flow/pros/risks/approach_label)·기존 소비자 회귀 0 |
| `docs/contracts/output_schema.md` §8.1 | **수정 (contract-change, ★ additive)** — Plan rich 슬롯 정식 등록. agent-io-check 회귀 |
| `docs/contract_changes/2026-06-0X_phase-13-output-schema-rich.md` | **신규** — CC 로그 (output_schema rich 슬롯 additive) |
| tests | **신규/수정** — rich 슬롯 Optional default 검증 + 기존 Plan 직렬화 회귀 0 |
- ★ contract-change 경유 — output_schema 는 이 Slice 에서만. additive(Optional) → 기존 소비자(프론트 PlanCard·orchestrator·Critic) 무영향.

### S2 — 프롬프트 확장 (prompt-version-review → P-006 bump)
| 항목 | 작업 |
|---|---|
| `backend/fastapi/agents/planning.py` rich SYSTEM_PROMPT | **수정/신규** — planning rich 프롬프트(+ 3-plan hint)가 S1 rich 슬롯을 채우도록. ★ **gated** — rich 프롬프트는 flag ON 경로 전용, 기존 compact `SYSTEM_PROMPT` 보존(미삭제) |
| `ai_system/prompts/prompt_registry.md` P-006 | **수정 (prompt-version-review, semver bump)** — P-006 v1.0.0 → **v1.1.0**(rich 변형) + golden_set 회귀 + 단계적 활성(gated) + 이전 버전 deactivation 일정 |
| `docs/contract_changes/2026-06-0X_phase-13-prompt-p006.md` | **신규** — CC 로그 (prompt_registry P-006 bump) |
| tests | **신규/수정** — rich 프롬프트 상수/version 정합 |
- ★ prompt-version-review 경유 — P-006 semver bump + golden_set 회귀 + gated 활성. 기존 compact 프롬프트는 flag OFF 경로로 보존.

### S3 — gated wiring (config flag + 경로 분기)
| 항목 | 작업 |
|---|---|
| `backend/fastapi/config.py` `rich_output_enabled` | **수정 (additive)** — flag default **False** (기존 `multi_provider_plans_enabled`·`cross_validation_enabled` gated 패턴 동형) |
| `backend/fastapi/routers/generate.py` + `orchestration/moa_orchestrator.py` | **수정 (gated 분기)** — ON → rich prompt/schema 채움 / OFF → 기존 compact 100% 동일(Envelope byte-identical). behavior-preserving when OFF |
| tests | **신규** — flag ON/OFF 경로 분기 + OFF byte-identical 회귀 |
- ★ behavior-preserving — OFF 가 default → 기존 compact 흐름 byte-identical. ON 은 opt-in(검증 경로).

### S4 — Critic depth 반영 (prompt-version-review)
| 항목 | 작업 |
|---|---|
| `backend/fastapi/agents/critic.py` + prompt | **수정 (additive)** — Critic 평가에 depth_actionability 차원 추가(기존 8차원 점수 체계 additive — 얕으면 감점, 88점 함정 해소). ★ canonical 0–1 체계 정합(ADR-018) |
| `ai_system/prompts/prompt_registry.md` P-007 | **수정 (prompt-version-review, semver bump)** — Critic prompt depth 차원 bump + golden_set 회귀 |
| tests | **신규/수정** — depth 차원 점수 + gated 정합(compact 얕음 감점 / rich 충족) |
- ★ prompt-version-review 경유 + gated 정합(rich 출력 평가 시 depth 차원 활성). 기존 점수 체계 additive — 회귀 0.

### S5 — frontend 렌더링 (design-review, conditional)
| 항목 | 작업 |
|---|---|
| `apps/web/components/PlanCard.tsx` + `apps/web/lib/types.ts` + `apps/web/lib/api.ts` | **수정 (conditional 렌더)** — rich 필드 표시(후크 변형/타임코드·화면·대사·자막/샷/썸네일/제목/길이변형). ★ rich 데이터 있을 때만(conditional) — 기존 compact 렌더 회귀 0 |
| design-review | rich 카드 UX (모바일 우선, 카드 단위, 영상 제작 UI 미포함) 7원칙 정합 |
| `apps/web/component_map.md` (필요 시) | **수정 (필요 시)** — PlanCard rich 섹션 반영 |
- ★ conditional/gated — rich 데이터(flag ON 경로) 있을 때만 렌더, 기존 compact 렌더 byte-identical.

### S6 — cost 재조정 + 검증 + 종료 (cost-review + eval-run + phase-complete)
| 항목 | 작업 |
|---|---|
| `ai_system/orchestration/cost_control_policy.md` | **수정 (contract-change)** — rich 토큰 ↑ × 3안 재조정 + B안 잔여 **B-RES-1** 통합(다중-provider cost 재조정 §18.D) |
| golden_set depth 재측정 | **신규 리포트** — rich 경로 depth_actionability(CC-011) 재측정 → 목표 **0.231 → ≥0.8** 확인 (`eval/regression_results/phase-13-*`) |
| flag ON 라이브 데모 | rich 출력 실 생성 + /generate 화면 rich 렌더 라이브 확인 (실 LLM, 키 user-provided) |
| `meta/retrospectives/phase-13.md` + closing_notes + (선택 ADR) | **신규 (종료 시)** — Phase 13 총괄 + 회고 + archive 이동 |

## contract-change 대상 (MG2)
- `docs/contracts/output_schema.md` (Plan rich 슬롯 additive — S1) + `ai_system/prompts/prompt_registry.md` (P-006 bump — S2 / P-007 depth — S4, prompt-version-review) + `ai_system/orchestration/cost_control_policy.md` (rich cost 재조정 — S6). ★ 전부 additive/behavior-preserving. 본 entry 는 **계획만** — 사전 변경 0.

## ★ 변경 허용 / 금지

```
변경 허용 (editable):
  Entry  : phases/active/phase-13-output-enrichment/**  +  meta/validations/2026-06-02_phase-13-pre-entry_self.md
           PHASE_REGISTRY.md (Phase 13 active) + PROJECT_STATE.md (Active 갱신)
  S1     : backend/fastapi/schemas/output.py (Plan additive) + docs/contracts/output_schema.md (contract-change) + CC 로그 + tests
  S2     : backend/fastapi/agents/planning.py (rich prompt, compact 보존) + prompt_registry.md P-006 bump (prompt-version-review) + CC 로그 + tests
  S3     : backend/fastapi/config.py (rich_output_enabled default False) + routers/generate.py + orchestration/moa_orchestrator.py (gated 분기) + tests
  S4     : backend/fastapi/agents/critic.py (depth 차원 additive) + prompt_registry.md P-007 bump + tests
  S5     : apps/web/components/PlanCard.tsx + lib/types.ts + lib/api.ts (conditional rich 렌더) + component_map (필요 시)
  S6     : cost_control_policy.md (rich cost 재조정 + B-RES-1) + eval/regression_results/phase-13-* (depth 재측정) + retrospective + closing + (선택 ADR)

변경 금지 (forbidden):
  ★ 기존 compact 프롬프트/스키마 삭제·breaking change (전부 additive Optional / compact 프롬프트 보존)
  ★ flag default ON (rich_output_enabled default False 유지 — 검증 후 별도 결정)
  ★ 완성 대본/영상 제작·편집·TTS·BGM (product_boundary 영구 non-goal — 확장본도 "기획 브리프")
  ★ 모델 tier 상향 (2차 레버, prompt/schema 후 재측정 뒤)
  ★ staging 배포 (Phase 14+)
  ★ 실 키 평문 (.env user-provided + .gitignore)
  ★ 본 entry 단계에서 운영 .py/contract 사전 변경 (S1+ 에서만)
```

## 변경 수 (entry — 본 문서)
- 신규: 8 entry + validation self(12th). 수정: PHASE_REGISTRY + PROJECT_STATE. ★ 운영 .py 0 (본 작업 = 종료+entry, 문서/계획만).

## 변경 수 (S1~S6 — 예정, 본 entry 범위 밖)
- S1: output.py Plan additive + output_schema CC + tests. S2: planning rich prompt + P-006 bump + tests. S3: config flag + generate/orchestrator gated + tests. S4: critic depth + P-007 bump + tests. S5: PlanCard/types/api conditional. S6: cost 재조정 + depth 재측정 + close. ★ S1~S4·S6 = backend / S5 = frontend / 전 Slice flag OFF byte-identical 게이트.
