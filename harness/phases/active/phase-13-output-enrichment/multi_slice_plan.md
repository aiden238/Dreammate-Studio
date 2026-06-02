# Phase 13 — Multi-Slice Plan

> Entry + 6 Slice (sub-agent) — 출력 확장 제품 phase. ★ 첫 의도적 출력 변경 — gated(flag OFF default) + additive(Optional)로 flag OFF byte-identical(behavior-preserving). 각 Slice P-X1 §SELF-VERIFICATION.

## Wave 구조 (계획)
```
Entry [8 entry + validation self 12th + PHASE_REGISTRY/PROJECT_STATE active]   (본 문서)
  ↓
S1 [스키마 확장 — Plan rich 슬롯 additive (output_schema contract-change + agent-io-check)]
  ↓
S2 [프롬프트 확장 — planning rich SYSTEM_PROMPT (prompt-version-review P-006 bump)]  ─┐ (S1 슬롯 의존)
  ↓                                                                                   │
S3 [gated wiring — rich_output_enabled default False + generate/orchestrator 분기]    ─┘
  ↓
S4 [Critic depth — depth_actionability 차원 additive (prompt-version-review P-007 bump)]  (S1·S3 의존)
  ↓
S5 [frontend — PlanCard rich conditional 렌더 (design-review)]   (S1 의존, 병행 가능)
  ↓
S6 [cost 재조정 + depth 재측정(≥0.8) + flag ON 라이브 데모 + phase-complete]   (전체 의존)
```

## Entry (본 문서 — phase-start)
1. 8 entry(goals/scope/non_goals/dependencies/acceptance/assumptions/multi_slice_plan/notes).
2. `meta/validations/2026-06-02_phase-13-pre-entry_self.md` (multi-llm-validation self 12th, V1~V6 — gated 롤아웃 / additive 스키마 / 첫 출력 변경 안전성).
3. `PHASE_REGISTRY.md` Phase 13 active + `PROJECT_STATE.md` Active 갱신 (Phase 12 done).
- sub-agent: **main** (entry).  P-X1: 운영 .py 0 + pytest 471.
- editable: phases/active/phase-13-output-enrichment/**, validation self, PHASE_REGISTRY, PROJECT_STATE.
- forbidden: ★ 운영 .py/contract 사전 변경(S1+ 에서만).
- ★ 산출물: entry 8 + validation + registry/state active.

## Slice 1 — 스키마 확장 (contract-change + agent-io-check)
1. `backend/fastapi/schemas/output.py` `Plan` + `PlanFlowBeat` 에 결핍 feature 슬롯 추가 — ★ 전부 Optional default None/[] (hook_variants[]/beat visual·dialogue·caption/shots[]/thumbnail/title_candidates[]/cta/references[]/length_variants/target_audience/tone).
2. `docs/contracts/output_schema.md` §8.1 Plan rich 슬롯 정식 등록 (contract-change, additive) + agent_io_contract 정합.
3. `docs/contract_changes/2026-06-0X_phase-13-output-schema-rich.md` (CC 로그) + tests(Optional default + 기존 직렬화 회귀 0).
- sub-agent: 1 dispatch.  P-X1: 기존 7필드·소비자 회귀 0 + agent-io-check PASS.
- editable: output.py, output_schema.md, agent_io_contract(정합), CC 로그, tests.
- forbidden: 기존 필드 삭제·재명명(NG5), breaking change, gated 분기(S3), 프롬프트(S2).
- ★ 산출물: Plan rich 슬롯(additive) + output_schema CC + agent-io-check.

## Slice 2 — 프롬프트 확장 (prompt-version-review → P-006 bump)
1. `backend/fastapi/agents/planning.py` rich SYSTEM_PROMPT(+ 3-plan hint) — S1 rich 슬롯 채움. ★ 기존 compact 프롬프트 보존(flag OFF 경로).
2. `ai_system/prompts/prompt_registry.md` P-006 v1.0.0 → v1.1.0 (prompt-version-review: semver + golden_set 회귀 + gated 단계 활성 + 이전 버전 deactivation 일정).
3. `docs/contract_changes/2026-06-0X_phase-13-prompt-p006.md` (CC 로그) + tests(rich prompt 상수/version 정합).
- sub-agent: 1 dispatch.  P-X1: 기존 compact 프롬프트 보존 + golden_set 회귀 + 운영 .py minimal.
- editable: planning.py(rich, compact 보존), prompt_registry.md P-006, CC 로그, tests.
- forbidden: compact 프롬프트 삭제, gated 분기(S3), output_schema(S1).
- ★ 산출물: rich planning 프롬프트 + P-006 v1.1.0.

## Slice 3 — gated wiring (config flag + 경로 분기)
1. `backend/fastapi/config.py` `rich_output_enabled` default **False** (Phase 11 gated 패턴 동형).
2. `backend/fastapi/routers/generate.py` + `orchestration/moa_orchestrator.py` gated 분기 — ON → rich prompt/schema 채움 / OFF → 기존 compact byte-identical(Envelope 불변).
3. tests — flag ON/OFF 분기 + OFF byte-identical 회귀.
- sub-agent: 1 dispatch.  P-X1: ★ flag OFF byte-identical(behavior-preserving) + pytest green.
- editable: config.py, generate.py, moa_orchestrator.py, tests.
- forbidden: flag default ON(NG3), OFF 경로 동작 변경(NG6), output_schema(S1)/프롬프트(S2) 재변경.
- ★ 산출물: rich_output_enabled gated wiring (OFF byte-identical).

## Slice 4 — Critic depth 반영 (prompt-version-review → P-007 bump)
1. `backend/fastapi/agents/critic.py` + prompt — depth_actionability 차원 additive(기존 8차원 canonical 0–1 보존 + 얕으면 감점, 88점 함정 해소).
2. `ai_system/prompts/prompt_registry.md` P-007 bump (prompt-version-review + golden_set 회귀).
3. tests — depth 차원 점수 + gated 정합(compact 얕음 감점 / rich 충족).
- sub-agent: 1 dispatch.  P-X1: 기존 점수 체계 회귀 0(additive) + prompt-version-review.
- editable: critic.py, prompt_registry.md P-007, tests.
- forbidden: canonical 0–1 체계 변경(ADR-018 보존), output_schema(S1).
- ★ 산출물: Critic depth_actionability 차원 + P-007 bump.

## Slice 5 — frontend 렌더링 (design-review, conditional)
1. `apps/web/components/PlanCard.tsx` + `apps/web/lib/types.ts` + `apps/web/lib/api.ts` — rich 필드 conditional 렌더(후크 변형/타임코드·화면·대사·자막/샷/썸네일/제목/길이변형).
2. design-review 7원칙(모바일 우선, 카드 단위, 영상 제작 UI 미포함) + component_map(필요 시).
- sub-agent: 1 dispatch.  P-X1: ★ rich 있을 때만 렌더(conditional) + 기존 compact 렌더 회귀 0 + tsc/build.
- editable: PlanCard.tsx, lib/types.ts, lib/api.ts, component_map(필요 시).
- forbidden: 기존 compact 렌더 회귀(NG7), 영상 제작 UI(product_boundary), backend(S1~S4).
- ★ 산출물: PlanCard rich conditional 렌더 (/generate 화면).

## Slice 6 — cost 재조정 + 검증 + 종료 (cost-review + eval-run + phase-complete)
1. `ai_system/orchestration/cost_control_policy.md` rich 토큰 ↑ × 3안 재조정 + B-RES-1(다중-provider §18.D) 통합 (contract-change).
2. golden_set depth_actionability(CC-011) rich 경로 재측정 → 목표 **0.231 → ≥0.8** (`eval/regression_results/phase-13-*`) + flag ON 라이브 데모(실 LLM, 키 user-provided).
3. `meta/retrospectives/phase-13.md` + closing_notes + (선택 ADR) + PROJECT_STATE/PHASE_REGISTRY done + archive 이동.
- sub-agent: **main** (close) 또는 1 dispatch.  P-X1: 키 0 + flag OFF byte-identical 최종 회귀 + pytest green.
- editable: cost_control_policy.md, eval/regression_results/phase-13-*, retrospective, closing, state docs, (선택 ADR).
- forbidden: flag default ON(NG3), 키 평문(NG10), staging 배포(NG4).
- ★ 산출물: cost 재조정 + depth 재측정(≥0.8) + 라이브 데모 + close.

## 충돌 매트릭스 (Slice)
| Slice | output.py/schema | planning prompt | config/wiring | critic | frontend | cost/eval/close |
|---|---|---|---|---|---|---|
| S1 | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| S2 | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ |
| S3 | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ |
| S4 | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ |
| S5 | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ |
| S6 | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
Sequential(S2·S3 는 S1 의존 / S4 는 S1·S3 / S5 는 S1 / S6 는 전체) 충돌 0.

## Skill 트리거 (Slice별)
| Slice | Skill |
|---|---|
| Entry | multi-llm-validation(self 12th) + phase-start |
| S1 | contract-change(output_schema additive) + agent-io-check |
| S2 | prompt-version-review(P-006 bump) + contract-change(CC 로그) |
| S3 | (behavior-preserving 게이트 — gated 분기, OFF byte-identical) |
| S4 | prompt-version-review(P-007 depth bump) |
| S5 | design-review(PlanCard rich 7원칙) |
| S6 | cost-review(rich 토큰 + B-RES-1) + eval-run(depth 재측정) + contract-change(cost_control) + meta-retrospective + phase-complete |

## P-X1 streak
| Phase | streak |
|---|---|
| Phase 12 | (누적 — 운영 코드 0, behavior-preserving) |
| Phase 13 | +Entry·S1~S6 (★ flag OFF byte-identical + additive — 첫 출력 변경에도 기존 회귀 0) |

## 시간 추정
Entry ~1.5h + S1(스키마) ~1.5h + S2(프롬프트 P-006) ~2h + S3(gated wiring) ~1.5h + S4(Critic depth) ~1.5h + S5(frontend) ~2h + S6(cost+재측정+close, 실 LLM 1회) ~2.5h.
