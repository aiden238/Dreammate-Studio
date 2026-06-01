# Phase 12 — Multi-Slice Plan

> Entry + 5 Slice (sub-agent) — 검증/계획 phase. ★ 운영 코드 0 수정 + behavior-preserving(pytest 471). 각 Slice P-X1 §SELF-VERIFICATION.

## Wave 구조 (계획)
```
Entry [8 entry + validation self 11th + PHASE_REGISTRY/PROJECT_STATE active]   (본 문서)
  ↓
S1 [golden_set 15→~25 + depth/actionability 차원 (contract-change additive)]
  ↓
S2 [실 LLM eval 1회 실행 → 차원별 점수 리포트]  ─┐ (S1 확장본·차원 의존)
  ↓                                              │
S3 [깊이 격차 정량 (compact vs rich)]            ─┘
  ↓
S4 [human review kit (표본 + 시트 + 대조 설계)]   (S2 점수 대조, 병행 가능)
  ↓
S5 [검증 종합 + Phase 13 우선순위 (meta-retrospective) + close]
```

## Entry (본 문서 — phase-start)
1. 8 entry(goals/scope/non_goals/dependencies/acceptance/assumptions/multi_slice_plan/notes).
2. `meta/validations/2026-06-02_phase-12-pre-entry_self.md` (multi-llm-validation self 11th, V1~V6).
3. `PHASE_REGISTRY.md` Phase 12 `next`→`active` + `PROJECT_STATE.md` Active 갱신.
- sub-agent: **main** (entry).  P-X1: 운영 .py 0 + pytest 471.
- editable: phases/active/phase-12-validation/**, validation self, PHASE_REGISTRY, PROJECT_STATE.
- forbidden: ★ backend/fastapi/**, apps/web/**, eval/golden_set·rubric(S1), 운영 contracts.
- ★ 산출물: entry 8 + validation + registry/state active.

## Slice 1 — golden_set 확장 + depth/actionability 차원 (eval-design + contract-change)
1. `eval/golden_set.md` 15→~25 (신규 ~10, ★ additive 회귀 보존).
2. eval rubric 에 **depth(깊이)·actionability(실행가능성)** 평가 차원 추가(★ additive, 기존 차원 보존).
3. `docs/contract_changes/2026-06-02_phase-12-eval-depth.md` (CC 로그).
- sub-agent: 1 dispatch.  P-X1: 운영 .py 0 + 기존 15 케이스 회귀(mock 게이트).
- editable: eval/golden_set.md, eval rubric(depth/actionability), CC 로그.
- forbidden: 운영 코드, 기존 케이스 의미 변경, output_schema/prompt_registry.
- ★ 산출물: golden_set ~25 + depth/actionability rubric + CC 로그.

## Slice 2 — 실 LLM eval 실행 (eval-run, ★ 실비용)
1. 실 LLM eval mode ON(Phase 10 capability) → golden_set ~25, **현 compact 운영 프롬프트 기준선** 1회 실행.
2. 차원별 실 품질 점수 + 임계값 판정 → `eval/regression_results/phase-12-*` 저장.
- sub-agent: 1 dispatch.  P-X1: 운영 .py 0 + 키 0(.env user-provided).
- editable: eval/regression_results/phase-12-* (eval 데이터 신규).
- forbidden: 운영 코드, CI 게이트 실 LLM 전환(mock 유지), 키 평문.
- ★ 산출물: 차원별 점수 리포트(baseline 수치).

## Slice 3 — 깊이 격차 정량 분석 (compact vs rich)
1. 같은 모델(gpt-4o-mini) · compact(현 운영) vs rich(확장 측정-프롬프트) 비교 측정.
2. metric: 필드수 / beat 깊이 / 대사·자막·샷·썸네일 유무 / 토큰 / 실행가능성 → "현재 깊이 X / 잠재 Y / gap Z".
- sub-agent: 1 dispatch.  P-X1: 운영 .py 0 + rich = 측정 전용(운영 미반영).
- editable: eval/regression_results/phase-12-depth-gap-* (분석 리포트 신규).
- forbidden: ★ 운영 prompt_registry/output_schema(Phase 13), 완성 대본(product_boundary), 키 평문.
- ★ 산출물: 깊이 격차 수치(구체 metric).

## Slice 4 — human review 표본 kit 준비
1. 사용자 직접 채점 표본 셋 + `eval/human_review_rubric.md` 기반 채점 시트.
2. LLM eval 점수(S2) ↔ human 점수 대조 설계.
- sub-agent: 1 dispatch.  P-X1: 운영 .py 0.
- editable: eval/ human review kit(표본 + 시트 + 대조 설계 문서, 신규).
- forbidden: 운영 코드, 사용자 실 채점 강행(kit 까지 — 실 채점 deferred).
- ★ 산출물: human review kit + 대조 설계.

## Slice 5 — 검증 종합 + Phase 13 우선순위 (meta-retrospective + close)
1. MO1~MO3 종합 + 깊이 격차 결론 + 확장 ROI/우선순위 → `meta/retrospectives/phase-12.md`.
2. `phases/active/phase-12-validation/closing_notes.md` (+ 선택 ADR: 검증 baseline + 깊이 격차 결정).
3. PROJECT_STATE/PHASE_REGISTRY done 갱신 + archive 이동.
- sub-agent: **main** (close).  P-X1: 운영 .py 0 + pytest 471.
- editable: meta/retrospectives/phase-12.md, closing_notes, state docs, (선택 ADR).
- forbidden: 운영 코드, Phase 13 구현 선반영.
- ★ 산출물: 종합 리포트 + Phase 13~20 우선순위 근거.

## 충돌 매트릭스 (Slice)
| Slice | golden_set/rubric | eval 데이터 | 분석 리포트 | human kit | 회고/close |
|---|---|---|---|---|---|
| S1 | ✅ | ❌ | ❌ | ❌ | ❌ |
| S2 | ❌ | ✅ | ❌ | ❌ | ❌ |
| S3 | ❌ | ❌ | ✅ | ❌ | ❌ |
| S4 | ❌ | ❌ | ❌ | ✅ | ❌ |
| S5 | ❌ | ❌ | ❌ | ❌ | ✅ |
Sequential(S2·S3 는 S1 의존) 충돌 0.

## P-X1 streak
| Phase | streak |
|---|---|
| Phase 11 | (누적) |
| Phase 12 | +Entry·S1~S5 (운영 코드 0, behavior-preserving) |

## 시간 추정
Entry ~1.5h + S1 ~1.5h + S2(실 LLM 1회) ~1h + S3(깊이 격차) ~2h + S4(human kit) ~1.5h + S5(종합) ~2h.
