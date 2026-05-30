# ADR-032 — Phase 9 normalize_to_canonical Wiring (critic step canonical, deprecated 0–5 병행)

> Date: 2026-05-29
> Status: Accepted
> Phase: 9 (결과 저장 + 피드백)
> Slice: 3 (구현 — orchestrator critic step wiring) / Slice 1 (본 ADR 결정)
> Related: ADR-018 (phase_6_critic_canonical — CriticEvaluation canonical, 불변 대상), ADR-029 (phase_8_prompt_registry_semver — normalize_to_canonical helper 도입),
>          ADR-027 (phase_8_moa_orchestrator — orchestrator critic step)
> Skill: (없음 — 코드 wiring, schemas/output.py 불변 — contract-change 미발동)

## Context

Phase 8 Slice 4 (ADR-029)에서 `backend/fastapi/agents/critic.py` 에 `normalize_to_canonical(verdict)` helper 를 도입했으나 **pipeline 미연결** 상태:

- `normalize_to_canonical` 는 **비파괴 사본** 반환 — `out = dict(verdict)` 후 `scores`(0–5)가 있으면 `dimensions[k] = scores[k]/5.0` + `overall_score = overall_score_avg/5.0` 를 `setdefault`/조건부 추가. **기존 0–5 필드(scores/overall_score_avg)는 보존**.
- helper docstring 명시: "additive 코드 유틸이며 run_critic 반환에 강제 주입하지 않는다."
- 즉 현재 `run_critic` 은 0–5 deprecated 형식을 산출하고, canonical 우선순위는 `select_best_plan_index` 에서만 작동. live pipeline(orchestrator critic step)은 canonical 0–1 을 critic_evaluation 에 저장하지 않음.

**Gap (Phase 8 개선 §1 — "normalize_to_canonical wiring, Phase 9+ 결과 저장 시점")**:

- orchestrator critic step 이 `run_critic(...)` 결과를 critic_evaluation(DB plans.critic_evaluation JSONB)에 저장할 때 0–5 만 저장 → canonical(0–1 + dimensions)이 live 미활용.
- Phase 6 ADR-018 CriticEvaluation 은 canonical(overall_score 0–1 + dimensions)을 **선언**했으나 run_critic 산출이 0–5 → schema 와 실 산출 간 표현 gap.

## Decision

### 1. critic step wiring

orchestrator critic step (`orchestration/moa_orchestrator.py` 또는 critic helper)에서 run_critic 결과를 `normalize_to_canonical` 로 감싼다:

```python
verdict = normalize_to_canonical(run_critic(plan, ...))
# verdict = { scores: {...0-5...}, overall_score_avg: 0-5,   # deprecated 병행 유지
#             dimensions: {...0-1...}, overall_score: 0-1,    # canonical 추가
#             overall_verdict, blocking_issues, ... }
```

- critic_evaluation 에 canonical(overall_score 0–1 + dimensions) **추가** 저장.
- deprecated 0–5(scores / overall_score_avg) **병행 유지** (helper 비파괴 — 보존).
- best-plan 선택(`select_best_plan_index`)은 canonical(overall_score → dimensions) 우선 → wiring 후 canonical 채워지면 deprecated fallback DeprecationWarning 경로 미진입 (동작 결과 동일, 경고만 감소).

### 2. schemas/output.py CriticEvaluation 불변

- `CriticEvaluation`(schemas/output.py)은 Phase 6 ADR-018 에서 canonical(overall_score 0–1 + dimensions) + deprecated(scores/overall_score_avg) **모두 Optional** → canonical 추가도 deprecated 유지도 schema 변경 0.
- **schemas/output.py 수정 0** (이미 Optional canonical 필드 보유 — Phase 6).
- output_schema.md(contract) 불변 → contract-change 미발동.

### 3. 의도된 critic_evaluation delta (Phase 8 Slice 4 패턴)

- wiring 으로 critic_evaluation dict 에 canonical 키(dimensions / overall_score)가 추가됨.
- critic_evaluation **구조를 직접 assert** 하는 baseline test 가 있으면 = **의도된 delta** (Phase 8 Slice 4 version-bump 선례) → 해당 assertion **만 최소 갱신**.
- 그 외 baseline test 수정 0. "wiring 김에 0–5 제거"는 NG3 위반 (Phase 9.5 eval-run 시점).

## Constraints

- **canonical 추가 + deprecated 0–5 병행 ★**: critic_evaluation 에 canonical(overall_score 0–1 + dimensions) 추가, deprecated(scores / overall_score_avg) 병행 유지. 0–5 제거는 **Phase 9.5 eval-run (NG3)** — "wiring 김에 0–5 제거" 금지.
- **schemas/output.py 불변 ★**: CriticEvaluation 모델 0 변경 (Phase 6 ADR-018 canonical — 이미 Optional canonical 보유). output_schema.md 불변 → contract-change 미발동.
- **의도된 delta 만 최소 baseline assertion 갱신**: critic_evaluation 구조 직접 assert 하는 baseline test 만 최소 갱신 (Phase 8 Slice 4 패턴). 그 외 baseline test 수정 0 → 회귀 0.
- **helper 비파괴 정합**: normalize_to_canonical 는 비파괴 사본(setdefault — 기존 canonical 보존) → wiring 시 dimensions/overall_score 충돌 없음. run_critic 로직 불변 (critic.py forbidden — helper 호출만).
- **best-plan 정확도 (U6)**: canonical overall_score(dimensions 평균/5.0) 기반 best-plan 변화는 Phase 9.5 eval 에서 측정 (Phase 9 는 wiring + 회귀 0 만).

## Trade-offs

| 선택 | 채택 사유 | 미채택 후보 |
|---|---|---|
| canonical 추가 + 0–5 병행 | 회귀 0 (Optional schema) + canonical live 활용 + 점진 마이그레이션 | 0–5 제거 즉시 — NG3 (eval-run 회귀 검증 전 위험) |
| schemas/output.py 불변 | Phase 6 canonical 보존 + contract 안정 | schema 변경 — Phase 6 ADR-018 재변경 (불필요) |
| 의도된 delta 최소 assertion | behavior-preserving (Phase 8 Slice 4 선례) + 회귀 추적 | 모든 test 갱신 — 동작 변경 위장 |
| wiring 시점 Phase 9 | Phase 8 개선 §1 + 결과 저장 시점 정합 | Phase 8 wiring — Phase 8 behavior-preserving 원칙 위반 |

## Verification

- `pytest backend/fastapi/tests/test_critic_canonical_wiring.py` (Slice 3 신규):
  - `test_wiring_adds_canonical` — critic step 후 critic_evaluation 에 overall_score 0–1 + dimensions 존재
  - `test_wiring_keeps_deprecated` — scores 0–5 + overall_score_avg 0–5 병행 유지 (회귀 0)
  - `test_canonical_in_range` — overall_score / dimensions 값 0.0~1.0 clamp
  - `test_best_plan_canonical_priority` — select_best_plan_index canonical 우선 (DeprecationWarning 미발생)
- **기존 baseline 회귀 0** (의도된 critic_evaluation delta — canonical 추가 assert 하는 test 만 최소 갱신, Phase 8 Slice 4 패턴).
- **schemas/output.py git diff = 0 lines** (CriticEvaluation 불변).

## References

- `backend/fastapi/agents/critic.py` (`normalize_to_canonical` — 비파괴 additive helper / `run_critic` 0–5 산출 / `select_best_plan_index` canonical 우선)
- `backend/fastapi/schemas/output.py` (CriticEvaluation canonical Optional — 불변)
- `docs/decisions/phase_6_critic_canonical.md` (ADR-018 — CriticEvaluation canonical, 정합 대상 불변)
- `docs/decisions/phase_8_prompt_registry_semver.md` (ADR-029 — normalize_to_canonical helper 도입, P-007 v1.1.0)
- `docs/decisions/phase_8_moa_orchestrator.md` (ADR-027 — orchestrator critic step)
- `meta/validations/2026-05-29_phase-9-pre-entry_self.md` §V2 (normalize wiring 회귀 0)
- `phases/active/phase-9-result-feedback/{goals,scope,non_goals,assumptions,multi_slice_plan}.md`
