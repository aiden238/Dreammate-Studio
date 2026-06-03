# Phase 15 — Multi-Slice Plan

> Entry + 6 Slice (Phase 13 tier 구조 계승). director = output_mode 3rd tier. ★ compact/rich byte-identical(behavior-preserving) + additive/gated + 키 0 + pytest 508 회귀 게이트. 각 Slice sub-agent + P-X1 §SELF-VERIFICATION.

## Wave 구조
```
Entry [8 + validation self 14th + REGISTRY/STATE active]  (본 문서)
  ↓
S1 [output_mode enum + director 스키마 슬롯 additive + model_dump 모드별 제외 (compact/rich byte-identical) + output_schema CC + agent-io-check]
  ↓                                                  ┌ (S1 슬롯 의존)
S2 [P-006 director 프롬프트 (DIRECTOR_SYSTEM_PROMPT v1.2.0, gated) — prompt-version-review]  ─┤
  ↓                                                  │
S3 [gated wiring — output_mode 분기 (generate/orchestrator/plans), compact/rich byte-identical / director ON]  ─┘
  ↓
S4 [Critic director 차원 (retention_design, P-007 v1.3.0 gated)]  (S1·S3 의존)
  ↓
S5 [frontend PlanCard director 조건부 (design-review)]  (S1 의존, 병행 가능)
  ↓
S6 [cost director 재조정 + director depth 측정 + 라이브 데모 + phase-complete]  (전체 의존)
```

## Entry (본 문서 — phase-start)
- 8 entry + `meta/validations/2026-06-03_phase-15-pre-entry_self.md`(self 14th, V1~V6) + PHASE_REGISTRY(15 active) + PROJECT_STATE active.
- sub-agent: **main**. P-X1: 운영 .py 0(entry=계획).

## S1 — output_mode enum + director 스키마 (contract-change + agent-io-check)
1. `config.py`: `output_mode: Literal["compact","rich","director"]="compact"` + backward-compat 매핑(rich_output_enabled=True → "rich"). helper `effective_output_mode(settings)`.
2. `schemas/output.py`: `DirectorScene`(scene_intent/viewer_emotion/retention_device/why_this_works/fallback_scene?) + `Plan` director 슬롯(hook_system list[str] / retention_architecture str|None / scene_breakdown list[DirectorScene]) + `DIRECTOR_FIELDS` + `model_dump_for_mode(mode)`(compact: rich∪director 제외 / rich: director 제외 / director: 없음). 기존 model_dump_compact 보존(=compact).
3. `output_schema.md` §8.1 director 슬롯 + output_mode 노트 (contract-change CC) + agent-io-check.
4. tests: 모드별 직렬화(compact/rich byte-identical + director 포함) + Optional default + 매핑.
- sub-agent: 1. forbidden: 프롬프트(S2)/wiring(S3)/commercial 슬롯(NG1). ★ 산출: enum + director 슬롯 + byte-identical.

## S2 — P-006 director 프롬프트 (prompt-version-review)
1. `agents/planning.py`: `DIRECTOR_SYSTEM_PROMPT`(rich + hook_system/retention/scene 채움 + 브리프 경계 + 보장 표현 금지) + `DIRECTOR_PROMPT_VERSION="v1.2.0"` + `_build_director_system_prompt_with_hint`. ★ compact/rich 프롬프트 보존, 런타임 미연결(wiring=S3).
2. `prompt_registry.md` §7 P-006 v1.2.0(director, gated 공존) + CC.
3. tests(director 프롬프트 슬롯 지시 + compact/rich 보존 + 버전).
- sub-agent: 1. forbidden: wiring(S3)/스키마(S1). ★ 산출: director 프롬프트 + P-006 v1.2.0.

## S3 — gated wiring (output_mode 분기)
1. `generate.py`+`moa_orchestrator.py`+`routers/plans.py`: 현 rich_enabled boolean 분기 → `effective_output_mode` 분기. compact/rich byte-identical(기존) / director → director prompt+schema(model_dump_for_mode). planning 프롬프트 선택(compact/rich/director).
2. tests: 3-mode 분기 + compact/rich byte-identical 회귀.
- sub-agent: 1. P-X1: ★ compact/rich byte-identical. forbidden: 스키마(S1)/프롬프트(S2) 재변경. ★ 산출: output_mode gated wiring.

## S4 — Critic director 차원 (prompt-version-review)
1. `agents/critic.py`: `DIMENSIONS_DIRECTOR = DIMENSIONS_RICH + ["retention_design"]`(director gated) + run_critic output_mode 분기(8/9/10) + _derive_verdict dimensions 인자 재사용.
2. `prompt_registry.md` §7 P-007 v1.3.0(director 10차원, gated 공존 — v1.1.0 8 / v1.2.0 9 / v1.3.0 10) + CC.
3. tests: director 차원 + 얕은 director 감점 + compact/rich 회귀 0.
- sub-agent: 1. forbidden: canonical 0–1 체계(ADR-018)/commercial 차원(NG5). ★ 산출: retention_design + P-007 v1.3.0.

## S5 — frontend PlanCard director 조건부 (design-review)
1. `apps/web/components/PlanCard.tsx` + `lib/types.ts`: director 슬롯 조건부 섹션(hook_system / retention_architecture / scene_breakdown). rich 위 additive — 값 있을 때만(compact/rich 회귀 0).
2. design-review 7원칙(모바일/카드/제작UI 미포함).
- sub-agent: 1. P-X1: rich 렌더 회귀 0 + tsc/build. forbidden: backend(S1~S4). ★ 산출: PlanCard director 섹션.

## S6 — cost + 검증 + 종료
1. `cost_control_policy.md` director cost(rich↔commercial_viral 중간) additive(contract-change).
2. director depth 측정(`eval/regression_results/phase-15-*`) + flag director 라이브 데모(실 LLM, 키 user-provided).
3. retrospective + closing + REGISTRY/STATE done + archive.
- sub-agent: main 또는 1. forbidden: default ON(NG3)/키 평문. ★ 산출: cost + depth + 라이브 + close.

## 충돌 매트릭스
| Slice | config/schema | planning prompt | wiring | critic | frontend | cost/close |
|---|---|---|---|---|---|---|
| S1 | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| S2 | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ |
| S3 | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ |
| S4 | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ |
| S5 | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ |
| S6 | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
S2·S3 는 S1 의존 / S4 는 S1·S3 / S5 는 S1 / S6 는 전체. 충돌 0.

## Skill 트리거
| Slice | Skill |
|---|---|
| Entry | multi-llm-validation(self 14th) + phase-start |
| S1 | contract-change(output_schema director) + agent-io-check |
| S2 | prompt-version-review(P-006 v1.2.0) + contract-change |
| S3 | (behavior-preserving 게이트 — compact/rich byte-identical) |
| S4 | prompt-version-review(P-007 v1.3.0) |
| S5 | design-review |
| S6 | cost-review + eval-run(director depth) + contract-change(cost) + meta-retrospective + phase-complete |

## 시간 추정
Entry ~1h + S1 ~2h + S2 ~1.5h + S3 ~2h + S4 ~1.5h + S5 ~2h + S6 ~2h.
