# Phase 12 — Scope (검증/계획 phase — 런타임 0, behavior-preserving)

> ★ Phase 12 = **측정·계획 phase**. 운영 코드(backend/fastapi/**, apps/web/**) 0 수정. 산출물 = eval 데이터 + 분석 리포트 + human review kit + 확장 우선순위 제안.

## 포함 (In-Scope) — Entry + S1~S5

### Entry (본 문서 — phase-start 진입)
| 항목 | 작업 |
|---|---|
| `phases/active/phase-12-validation/` 8 entry | **신규** (goals/scope/non_goals/dependencies/acceptance/assumptions/multi_slice_plan/notes) |
| `meta/validations/2026-06-02_phase-12-pre-entry_self.md` (11th) | **신규** (multi-llm-validation self-form V1~V6) |
| `PHASE_REGISTRY.md` / `PROJECT_STATE.md` | **수정** (Phase 12 `next`→`active` + Active 블록 갱신) |

### S1 — golden_set 확장 + depth/actionability 차원 추가 (eval-design)
| 항목 | 작업 |
|---|---|
| `eval/golden_set.md` | **수정 (contract-change, ★ additive)** — 15→~25 케이스 (신규 ~10, 기존 15 회귀 보존). 깊이·실행가능성 측정에 적합한 케이스 보강 |
| `eval/` rubric (depth/actionability 차원) | **수정/신규 (contract-change, ★ additive)** — eval rubric 에 **depth(깊이)·actionability(실행가능성)** 평가 차원 정식 등록. 기존 차원(hook 강도/구체성/도메인 적합성) 보존 |
| `docs/contract_changes/2026-06-02_phase-12-eval-depth.md` | **신규** — CC 로그 (golden_set 확장 + depth/actionability 차원) |
- ★ contract-change 경유 — golden_set·rubric 은 **이 Slice 에서만** 변경. 다른 Slice·entry 는 사전 변경 금지.

### S2 — 실 LLM eval 실행 (eval-run, ★ 실비용)
| 항목 | 작업 |
|---|---|
| 실 LLM eval 1회 실행 | golden_set ~25 + **현 compact 운영 프롬프트 기준선** → 차원별 실 품질 점수 + 임계값 판정. ★ 실 LLM 호출 = 실비용(사용자 승인됨) |
| `eval/regression_results/phase-12-*` | **신규** — 차원별 점수 리포트 (baseline 수치 저장, jsonl + 요약) |
- ★ eval 실행 = 측정 capability(Phase 10 구축, mode flag). 운영 endpoint 미경유 — eval runner 가 직접 호출. 운영 코드 0 수정.

### S3 — 깊이 격차 정량 분석 (compact vs rich)
| 항목 | 작업 |
|---|---|
| compact vs rich 비교 측정 | 같은 모델(gpt-4o-mini) · compact(현 운영) vs rich(확장 측정-프롬프트) — 필드수 / beat 깊이 / 대사·자막·샷·썸네일 유무 / 토큰 / 실행가능성 |
| `eval/regression_results/phase-12-depth-gap-*` (또는 분석 리포트) | **신규** — "현재 깊이 X / 잠재 Y / gap Z" 수치 도출 + 차원별 격차 |
- ★ rich 프롬프트는 **측정 전용** — 운영 prompt_registry / output_schema 0 수정 (확장은 Phase 13). product_boundary 유지: rich 도 "기획 브리프"여야 함(완성 대본/영상 미산출).

### S4 — human review 표본 kit 준비
| 항목 | 작업 |
|---|---|
| human review 표본 + rubric 시트 | 사용자가 직접 채점할 표본 셋 + `eval/human_review_rubric.md` 기반 채점 시트 + LLM 점수 대조 설계 |
| `eval/` human review kit (표본 + 시트 + 대조 설계 문서) | **신규** — 채점 kit 까지가 Phase 12 산출. ★ 사용자 실 채점 시간 소요분은 **deferred**(kit 준비 = acceptance) |
- LLM-as-judge(S2 점수) ↔ human 점수 대조 = MO3 신뢰도 확인 설계.

### S5 — 검증 종합 + Phase 13 확장 우선순위 제안 (meta-retrospective)
| 항목 | 작업 |
|---|---|
| `meta/retrospectives/phase-12.md` | **신규** — MO1~MO3 종합 + 깊이 격차 결론 + 확장 ROI/우선순위 (Phase 13~20 데이터 근거) |
| `phases/active/phase-12-validation/closing_notes.md` | **신규 (종료 시)** — Phase 12 총괄 |
| ADR (Phase 12 검증 방법·결론) | **신규 (선택, 종료 시)** — 검증 baseline + 깊이 격차 결정 기록 |

## contract-change 대상 (MG2)
- `eval/golden_set.md` (15→~25) + eval rubric depth/actionability 차원 — **S1 에서 contract-change 경유** (★ additive, behavior-preserving). 본 entry 는 **계획만** — 사전 변경 0.

## ★ 변경 허용 / 금지

```
변경 허용 (editable):
  Entry  : phases/active/phase-12-validation/**  +  meta/validations/2026-06-02_phase-12-pre-entry_self.md
           PHASE_REGISTRY.md (Phase 12 active) + PROJECT_STATE.md (Active 갱신)
  S1     : eval/golden_set.md (contract-change additive) + eval rubric depth/actionability (contract-change additive)
           docs/contract_changes/2026-06-02_phase-12-eval-depth.md
  S2~S3  : eval/regression_results/phase-12-* (eval 데이터·분석 리포트 신규)
  S4     : eval/ human review kit (표본 + 시트 + 대조 설계, 신규)
  S5     : meta/retrospectives/phase-12.md + closing_notes.md (+ 선택 ADR)

변경 금지 (forbidden):
  ★ 운영 코드 0 변경 — backend/fastapi/** , apps/web/**  (Phase 12 = 측정·문서만)
  ★ 운영 prompt_registry / output_schema / agent_io 등 contract (S1 의 eval rubric/golden_set 만 예외, contract-change 경유)
  ★ 본 entry 단계에서 golden_set/eval 사전 변경 (S1 에서만)
  ★ tests 0 수정 (pytest 471 유지)
  ★ 실 키 평문 (.env user-provided + .gitignore)
  운영 staging 배포 (Phase 13+) / 영상 제작·편집 (영구 non-goal)
```

## 변경 수 (entry — 본 문서)
- 신규: 8 entry + validation self(11th). 수정: PHASE_REGISTRY + PROJECT_STATE. ★ 운영 .py 0.

## 변경 수 (S1~S5 — 예정, 본 entry 범위 밖)
- S1: golden_set + rubric(additive) + CC 로그. S2: eval 데이터(신규). S3: 분석 리포트(신규). S4: human review kit(신규). S5: 회고 + close. ★ 전 Slice 운영 코드 0.
