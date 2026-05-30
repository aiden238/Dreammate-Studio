# ADR-034 — Phase 9.5 Critic deprecated 0–5 Full 제거 (fallback + CriticEvaluation Optional 필드)

> Date: 2026-05-31
> Status: Accepted
> Phase: 9.5 (eval-run 정식화 + Critic deprecated 0–5 Full 제거)
> Slice: 4 (구현 — critic.py + schemas/output.py + contract-change CC-005) / Slice 1 (본 ADR 결정)
> Related: ADR-018 (phase_6_critic_canonical — CriticEvaluation canonical 선언 + deprecated "Phase 9+ 제거" 명시), ADR-029 (phase_8_prompt_registry_semver — P-007 v1.1.0 + normalize helper), ADR-032 (phase_9_critic_canonical_wiring — canonical live wiring), ADR-033 (phase_9_5_eval_run_harness — 본 제거의 eval baseline)
> Skill: contract-change (CC-005 — output_schema + agent_io_contract + db_schema critic_evaluation deprecated 제거)

## Context

Critic 평가 체계는 Phase 6 (ADR-018)에서 **canonical(overall_score 0–1 + dimensions)** 로 통일됐으나, Phase 1~4.5 호환을 위해 deprecated 0–5 필드 + fallback 을 병행 유지해왔다. ADR-018 은 "Phase 9+ eval 후 제거" 를 명시했고, Phase 6/8/9 내내 누적 deferred (3회).

**현 상태 (critic.py + schemas/output.py 정독)**:

1. `run_critic` (critic.py:144~264) — LLM 에 0–5 8차원 산출 요청(SYSTEM_PROMPT) → `norm_scores`(0~5 clamp) + `overall_score_avg`(0–5 평균) + verdict 반환. **P-007 prompt contract (LLM-facing 0–5)**.
2. `normalize_to_canonical` (critic.py:280~318) — 비파괴 사본 + `dimensions[k] = scores[k]/5.0` + `overall_score = overall_score_avg/5.0` (0–5 읽어 0–1 생성).
3. `select_best_plan_index` (critic.py:324~414) — canonical(overall_score → dimensions) 우선 + **deprecated fallback**(overall_score_avg → scores/eight_dim_scores + `warnings.warn(DeprecationWarning)`, line 372~401). docstring(line 338): "Phase 9+ eval-run Skill 정식화 후 deprecated fallback 완전 제거 (별도 contract-change 절차)".
4. `CriticEvaluation` (schemas/output.py:154~212) — canonical(`overall_score` / `dimensions`) + **Optional deprecated 필드**(`scores: CriticScores | None` / `overall_score_avg: float | None` — line 193~209, "Phase 9+ eval 후 제거 예정 — DeprecationWarning 발행").

**Phase 9 wiring 으로 deprecated fallback = dead code (ADR-032)**:
- Phase 9 에서 `verdict = normalize_to_canonical(run_critic(...))` wiring → critic_evaluation 에 canonical(0–1 + dimensions) 항상 populated. → `select_best_plan_index` 의 deprecated fallback branch(overall_score_avg/scores/eight_dim_scores)는 canonical 우선 로직이 항상 먼저 매치 → **미진입 dead code**. Phase 9 deprecated warnings 67→16 (잔존 16 = 이 fallback + schema Optional).

## Decision

### 1. 제거 대상 (Full 제거)

#### 1.1 `select_best_plan_index` deprecated fallback (critic.py)

- **제거**: line 372~401 deprecated fallback branch 3개 — ⓐ `overall_score_avg`(0–5) + DeprecationWarning, ⓑ `scores`/`eight_dim_scores` dict 평균 + DeprecationWarning 2발행. + 상단 `import warnings` (다른 사용 없으면).
- **유지**: canonical 우선 로직 — `overall_score`(0–1) + `dimensions` dict 평균(0–1). → canonical-only `_score()`.
- docstring (line 331~338) canonical 우선순위 1~2 만 남기고 deprecated 3~4 + "Phase 9+ 제거 예정" 문구 제거.

#### 1.2 `CriticEvaluation` Optional deprecated 0–5 필드 (schemas/output.py)

- **제거**: `scores: CriticScores | None`(line 193~200) + `overall_score_avg: float | None`(line 203~209) — deprecated 0–5 필드.
- **유지**: canonical `overall_score: float | None`(0–1) + `dimensions: dict[str, float]`(0–1) + `overall_verdict` + `blocking_issues` + `revise_round` + `reasons` + `suggestions` + `target_plan_id`.
- `CriticScores` 모델(line 141~151) 은 run_critic 0–5 내부 산출 + (필요 시) verdict dict 타이핑용으로 유지 가능 — CriticEvaluation 에서만 deprecated 참조 제거. (Slice 4 에서 CriticScores 잔존 참조 확인 후 결정 — schema 외 사용 없으면 제거 후보).
- **Pydantic `extra='ignore'`**: CriticEvaluation 이 verdict dict(run_critic 산출 0–5 키 scores/overall_score_avg)를 받을 때 0–5 키를 **무시** (extra='ignore' — Pydantic v2 default 이나 명시) → verdict dict 그대로 넘겨도 canonical 만 추출 → 회귀 0.

### 2. 불변 (제거 X — NG3, P-007 prompt contract)

- **`run_critic` 0–5 출력 (critic.py:144~264) — 불변 ★**: SYSTEM_PROMPT 0–5 8차원 정의 + `norm_scores`(0~5) + `overall_score_avg`(0–5) + `_derive_verdict` (0–5 기준 verdict). LLM 이 0–5 산출 → normalize_to_canonical 이 0–1 변환. **P-007 prompt contract (LLM-facing 0–5)**. critic.py 의 run_critic 로직 forbidden (fallback branch 만 제거).
- **`normalize_to_canonical` 0–5→0–1 변환 (critic.py:280~318) — 불변**: scores(0–5) 읽어 dimensions(0–1) + overall_score(0–1) 생성 — canonical 생성의 단일 경로. 유지.
- **★ 모순 없음**: run_critic 0–5 산출 + normalize 입력으로만 0–5 존재. 외부 schema(CriticEvaluation) + best-plan 선택은 canonical(0–1)만 소비. CriticEvaluation 0–5 필드 제거 + extra='ignore' → verdict 0–5 키 무시 → 회귀 0.

### 3. 순서 (eval 검증 후 제거 ★)

```
Slice 2~3: eval runner 구축 (ADR-033) → canonical-only 품질 baseline 기록
           (eval/regression_results/phase-9.5_{date}.md)
   ↓
Slice 4:   canonical-only baseline 확인 (제거 전 회귀 기준)
           → deprecated fallback + schema 0–5 제거
           → 동일 eval 재실행 → 품질 동일 (회귀 0) 확인
```

- eval 없이 제거 금지 (안전망 우선). canonical(0–1)만으로 best-plan 선택 + 회귀 품질이 deprecated 0–5 시절과 동일함을 eval 로 먼저/나중 검증.

### 4. 의도된 baseline delta (Phase 8 Slice 4 패턴)

- **test_critic.py** select_best_plan_index deprecated-fallback `pytest.warns(DeprecationWarning)` 케이스 (6개) — canonical 로 갱신/제거:
  - `test_select_best_plan_index_returns_highest_score` (overall_score_avg)
  - `test_select_best_plan_index_tie_breaking_prefers_lower_index` (overall_score_avg)
  - `test_select_best_plan_index_all_invalid_returns_none` (overall_score_avg)
  - `test_select_best_plan_index_uses_scores_dimension_fallback` (scores)
  - `test_select_best_plan_index_skips_invalid_uses_remaining` (overall_score_avg)
  - `test_select_best_plan_index_eight_dim_scores_deprecated_warns` (eight_dim_scores)
  - → deprecated 입력은 canonical 없음 → None 반환 또는 canonical 입력으로 갱신. canonical 케이스(`_canonical_overall_score_preferred` / `_canonical_dimensions_fallback` / `_canonical_overrides_deprecated`)는 **보존** (canonical 경로 불변).
- **test_critic.py** CriticEvaluation 0–5 compat 케이스 (line 475~490 `scores` + `overall_score_avg` 생성) — schema 변경 반영 갱신.
- **run_critic 0–5 케이스 보존** (line 110/133 overall_score_avg == 4.0 등) — run_critic 불변 (NG3).
- **test_prompt_registry_consistency / test_schema_stress / test_moa_orchestrator / test_plans** (U4) — deprecated 입력(overall_score_avg/scores) 케이스만 의도 delta, canonical 입력 케이스 불변. Slice 4 pytest 에서 의도 delta 수 확정.
- 그 외 baseline test 수정 0 → behavior-preserving (Phase 8 P-BEHAVIOR-PRESERVING-001).

### 5. frontend types 정합 (V7 — 필요 시)

- `apps/web/lib/types.ts` `CriticEvaluation` — `scores`/`overall_score_avg` **non-optional**(line 135~147, "page.tsx 가 직접 호출 .toFixed/.map" + "Phase 9+ deprecated 제거 시 page.tsx 와 함께 동시 마이그레이션").
- Slice 4 에서 **page.tsx 가 critic_evaluation 0–5(scores/overall_score_avg)를 렌더하는지 확인** → 렌더 시 canonical(overall_score 0–1 / dimensions) 전환 (page.tsx inline wrapper — **PlanCard·component_map 0줄 ★**) + types non-optional 제거. tsc(0 error) + next build(11 routes) 회귀 0 (U3).

## Constraints

- **run_critic 0–5 불변 ★ (NG3)**: SYSTEM_PROMPT 0–5 + norm_scores + overall_score_avg + _derive_verdict 산출 불변 (P-007 prompt contract). critic.py forbidden — select_best_plan_index fallback branch + import warnings 만 제거.
- **normalize_to_canonical 불변**: 0–5→0–1 변환 로직 유지 (canonical 생성 단일 경로).
- **eval 검증 후 제거 ★**: Slice 2~3 eval runner → canonical-only baseline → Slice 4 제거 → 동일 eval 재실행 회귀 0 (ADR-033 안전망). eval 없이 제거 금지.
- **의도 delta 최소**: test_critic deprecated-fallback 케이스(6) + CriticEvaluation 0–5 compat + (필요 시) test_prompt_registry_consistency/test_schema_stress 의 deprecated 입력 케이스만 갱신 (Phase 8 Slice 4 패턴). canonical 케이스 + run_critic 케이스 + 그 외 baseline 보존.
- **contract-change CC-005 ★**: output_schema §9 CriticEvaluation deprecated 필드 제거 + agent_io_contract §5 Critic canonical-only + db_schema critic_evaluation JSONB deprecated 필드 제거 note (Slice 4). eval 회귀 통과 후 contract 반영.
- **frontend PlanCard·component_map 0줄 ★**: types.ts + page.tsx(필요 시 canonical 전환)는 component 아님 (PlanCard·component_map 무수정 — NG8/NG9).
- **Pydantic extra='ignore'**: CriticEvaluation 이 verdict dict 0–5 키(scores/overall_score_avg) 받을 때 무시 → 회귀 0.

## Trade-offs

| 선택 | 채택 사유 | 미채택 후보 |
|---|---|---|
| deprecated fallback + schema Full 제거 | Phase 9 wiring 으로 dead code + canonical 단일 표준 + 유지보수↓ + warnings 16→0 | 추가 deferral — ADR-018 "Phase 9+ 제거" 4회 누적 위반 |
| run_critic 0–5 불변 | P-007 prompt contract (LLM-facing 0–5) + LLM 출력 contract 안정 | run_critic 0–5 제거 — NG3 (prompt contract 파괴) |
| eval 검증 후 제거 | canonical-only 안전망 + 회귀 추적 | eval 없이 제거 — 정확도 회귀 미검증 |
| 의도 delta 최소 | behavior-preserving (Phase 8 선례) + 회귀 추적 | 모든 test 갱신 — 동작 변경 위장 |
| frontend canonical 전환 (필요 시) | backend 0–5 미노출 정합 + types 일관 | frontend 0–5 non-optional 유지 — 런타임 undefined 회귀 |

## Verification

- `pytest backend/fastapi/tests/` (Slice 4 — 의도 delta 만 갱신, 그 외 0):
  - select_best_plan_index canonical-only (deprecated 입력 → None 또는 canonical 갱신, DeprecationWarning 미발생)
  - CriticEvaluation canonical-only (scores/overall_score_avg 제거 후 verdict dict extra='ignore')
  - run_critic 0–5 케이스 보존 (NG3 — overall_score_avg == 4.0 등 불변)
- `eval/regression_results/phase-9.5_{date}.md` 재실행 — 제거 후 canonical-only 품질 동일 (회귀 0).
- agent-io-check — agent_io_contract §5 Critic canonical-only ↔ critic.py drift 0.
- frontend (필요 시): tsc 0 error + next build 11 routes (page.tsx canonical 전환 + PlanCard·component_map 0줄).
- `git diff` — critic.py run_critic 로직 0 변경 (fallback branch + import warnings 만) + schemas/output.py CriticEvaluation deprecated 필드만 제거.

## References

- `docs/decisions/phase_6_critic_canonical.md` (ADR-018 — CriticEvaluation canonical 선언 + deprecated "Phase 9+ 제거" 명시)
- `docs/decisions/phase_8_prompt_registry_semver.md` (ADR-029 — P-007 v1.1.0 + normalize_to_canonical helper)
- `docs/decisions/phase_9_critic_canonical_wiring.md` (ADR-032 — canonical live wiring → deprecated fallback dead code)
- `docs/decisions/phase_9_5_eval_run_harness.md` (ADR-033 — 본 제거의 canonical-only eval baseline 안전망)
- `backend/fastapi/agents/critic.py` (run_critic 0–5 불변 NG3 / normalize_to_canonical 불변 / select_best_plan_index:338 deprecated fallback 제거 대상)
- `backend/fastapi/schemas/output.py` (CriticEvaluation:193~209 Optional deprecated 0–5 필드 제거 대상)
- `apps/web/lib/types.ts` (CriticEvaluation:135~147 frontend non-optional — page.tsx 동시 마이그레이션)
- `backend/fastapi/tests/test_critic.py` (select_best_plan_index deprecated-fallback pytest.warns 케이스 6 — 의도 delta)
- `meta/validations/2026-05-31_phase-9.5-pre-entry_self.md` §V4/V5/V7 (제거 경계 / 순서 / frontend 정합)
- `phases/active/phase-9.5-eval-run/{goals,scope,non_goals,assumptions,multi_slice_plan}.md`
