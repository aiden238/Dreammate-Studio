# ADR-018 — Phase 6 Critic Verdict Canonical Standardization

> Date: 2026-05-29
> Status: Accepted
> Phase: 6 (Output Schema + Agent IO Stabilization)
> Slice: 2
> Related: ADR-016 (phase_4_5_critic_revise), ADR-017 (phase_4_5_best_plan_selection),
>          P-CRITIC-CANONICAL-001 (proposed, meta/patterns.md), Z-X3 (meta/proposals)

## Context

Phase 4.5 에서 `agents/critic.py::select_best_plan_index` 가 4가지 fallback (`overall_score_avg` → `overall_score` → `scores` → `dimensions`/`eight_dim_scores`) 을 사용했다. Critic 응답 구조가 미확정이어서 방어적 코딩 패턴이 누적되어 있었다.

Phase 5 DB 도입 전 canonical 결정이 필수다 (DB 컬럼 / API 응답 / frontend type 모두 영향).

`docs/contracts/output_schema.md` §9.1 은 Phase 4.5 시점까지 `overall_score_avg: float` + `scores: dict[str, int]` (0~5 정수) 만 명시하고 있었다. `select_best_plan_index` 의 fallback chain 자체는 contract 에 노출되지 않았다.

사전 검증 `meta/validations/2026-05-29_phase-6-pre-entry_self.md` §V1 에서 canonical 안 (`overall_score: float [0~1]` + `dimensions: dict[str, float]`) 채택 결정.

## Decision

### 1. CriticEvaluation canonical 필드 (Phase 6)

| 필드 | 타입 | 역할 |
|---|---|---|
| `overall_score` | float [0.0~1.0] | Critic 종합 점수 (정규화). canonical |
| `dimensions` | dict[str, float] | 8-dim 점수 dict (정규화 0~1). canonical |
| `overall_verdict` | Literal["approve", "revise", "reject"] | 의사결정 카테고리 (변경 없음) |
| `blocking_issues` | list[str] | 최대 3개 (변경 없음) |

### 2. Deprecated 필드 (Phase 9+ eval 후 제거 예정)

| 필드 | 사유 | 대체 |
|---|---|---|
| `overall_score_avg` | 0~5 float (비정규화) | `overall_score` (0~1) |
| `scores` | 0~5 정수 dict | `dimensions` (0~1 float) |
| `eight_dim_scores` | 별칭 | `dimensions` |
| `target_plan_id` | echo back 만 | (제거 예정) |
| `reasons`, `suggestions`, `revise_round` | 호환 유지 (Phase 9+ 별도 결정) | — |

Deprecated 필드 접근 시 `agents/critic.py::select_best_plan_index` 가 `warnings.warn(DeprecationWarning, ...)` 발행. `pytest.warns(DeprecationWarning)` 로 capture 의무화.

### 3. `select_best_plan_index` 우선순위

```
1. overall_score (canonical)
2. dimensions 평균 (canonical fallback)
3. overall_score_avg (deprecated + DeprecationWarning)
4. scores 평균 (deprecated + DeprecationWarning)
5. eight_dim_scores 평균 (deprecated + DeprecationWarning)
```

Tie-breaking: 동점 시 plan_index 가 더 작은 쪽 (deterministic — 동일 입력 동일 출력).

### 4. ReviseAttempt Pydantic 모델 (typing 강화)

Phase 4.5 Slice 2 에서 `Body.revise_history: Optional[list[list[dict[str, Any]]]]` 로 도입. Phase 6 에서 `ReviseAttempt` Pydantic 모델로 강화 (`backend/fastapi/schemas/output.py`).

```python
class ReviseAttempt(BaseModel):
    attempt: int = Field(..., ge=0)
    action: Literal["approve", "revise", "reject", "unknown"]
    revised: bool
    max_reached: bool | None = None
    critic_warning: str | None = None
    rewriter_warning: str | None = None
    model_config = {"extra": "allow"}  # 미래 확장 메타 허용
```

`Body.revise_history: Optional[list[list[ReviseAttempt]]]` 로 typing 강화. Pydantic v2 가 dict → ReviseAttempt 자동 변환하므로 `routers/plans.py` 변경 없음 (회귀 0).

`action="unknown"` 은 Critic 이 미정의 verdict 반환 시 폴백.

### 5. `Body.recommended_plan_index` 정식 등록 (Phase 4.5 ADR-017)

Phase 4.5 에서 도입된 `recommended_plan_index: Optional[int]` 를 `output_schema.md` §9-A.2 에 정식 등록.

## Constraints

- **DeprecationWarning 발행 의무**: deprecated key 접근 시 `warnings.warn` 호출. `pytest.warns(DeprecationWarning)` capture 의무 (회귀 검출 늦음 위험 완화).
- **Phase 9+ eval-run Skill 정식화 후 deprecated fallback 완전 제거** (별도 contract-change 절차). Phase 6 에서는 deprecation note 만, 실 제거 X (NG12).
- **frontend types.ts 에 canonical field 만 정식 export** (deprecated 는 미노출) — Slice 3 영역.
- **routers/plans.py 회귀 0**: `CriticEvaluation(**first_verdict)` 호출 패턴 호환 유지 (모든 deprecated 필드 Optional 강등 + Pydantic v2 dict 변환).
- **PlanCard.tsx 0줄 / component_map.md 0줄 ★** (사용자 결정 6-a / NG6 / NG7).

## Trade-offs

| 선택 | 채택 사유 | 미채택 후보 |
|---|---|---|
| 정규화 0~1 (canonical) | 다중 차원 가중치 도입 용이 + JSON object 직렬화 호환 | 0~5 정수 유지 (Phase 1 호환 — 별도 컨버터 필요) |
| dimensions: dict[str, float] | 8-dim 키 확장 유연성 + frontend Record<string, number> 매핑 | 고정 필드 (8개 Pydantic BaseModel) — 키 확장 시 breaking change |
| Optional 호환 + deprecated 표시 | 회귀 0 (Phase 1~4.5 호환 유지) + Phase 9+ eval 안정화 후 완전 제거 | 즉시 제거 — 회귀 위험 ↑, golden_set 미통과 위험 |
| ReviseAttempt extra="allow" | 미래 확장 메타 (예: cost / latency) 허용 → typing drift 방지 | strict schema — 변경 시마다 contract bump 필요 |
| DeprecationWarning + pytest.warns | 회귀 검출 자동화 (warning silent 방지) | log only — 누락 위험 |

## Verification

- `pytest backend/fastapi/tests/test_critic.py` (이전 14 케이스 + 신규 6~7 케이스):
  - `test_select_best_plan_index_canonical_overall_score_preferred`
  - `test_select_best_plan_index_canonical_dimensions_fallback`
  - `test_select_best_plan_index_canonical_overrides_deprecated`
  - `test_select_best_plan_index_eight_dim_scores_deprecated_warns`
  - `test_critic_evaluation_canonical_fields_optional`
  - `test_critic_evaluation_backward_compat_phase_1_45`
  - 기존 6 케이스 (`select_best_plan_index_*`) 에 `pytest.warns(DeprecationWarning)` 추가
- `pytest backend/fastapi/tests/` 전체 회귀: Phase 4.5 baseline 109/109 → Phase 6 113~115/113~115
- **`git diff --cached --stat | grep -E "PlanCard|component_map|routers/plans"` = 0 lines** ★ (PlanCard 10연속 / component_map 20연속 / routers/plans.py 회귀 0)

## Migration

Phase 9+ eval-run Skill 정식화 후 deprecated 완전 제거 (별도 contract-change 절차):

1. golden_set 회귀 평가 통과 (`overall_score` 만 사용한 cost / latency / 정확도 baseline)
2. `output_schema.md` v2.0.0 major bump (breaking change)
3. `agents/critic.py` deprecated fallback 5단계 → 2단계 (canonical only)
4. `Body.critic_evaluation` Optional 필드 (target_plan_id / scores / overall_score_avg) 제거
5. PROJECT_STATE.md migration 완료 명시

## References

- `meta/validations/2026-05-29_phase-6-pre-entry_self.md` §V1, §V3
- `meta/proposals/2026-05-28_phase-4-retrospective-proposals.md` §Z-X3
- `phases/active/phase-6-output-schema-stabilization/non_goals.md` NG12 (fallback 완전 제거 Phase 9+ 이관)
- `phases/active/phase-6-output-schema-stabilization/scope.md` Slice 2
- `docs/contracts/output_schema.md` §9 / §9-A (Phase 6 갱신)
- `docs/decisions/phase_4_5_critic_revise.md` (ADR-016 — revise loop)
- `docs/decisions/phase_4_5_best_plan_selection.md` (ADR-017 — Z-X3)
- `docs/decisions/phase_6_rewriter_contract.md` (ADR-019 — Rewriter v1.1.0)
