# ADR-017 — Phase 4.5 Best-Plan Selection (Z-X3)

> Date: 2026-05-28
> Status: Accepted
> Phase: 4.5 (mini-phase, post Phase 4)
> Slice: 3
> Related: ADR-014 (phase_4_endpoint_migration), ADR-015 (phase_4_3plan_multi_model), ADR-016 (phase_4_5_critic_revise)

## Context

Phase 4 종료 시점 응답은 plan 3개를 동등 우선순위로 노출한다. 사용자가 3개 중 어느
plan 이 가장 좋은지 직접 판단해야 하는 부담이 있었다. Phase 4 retrospective(`meta/retrospectives/phase-4.md`)
및 사전 검증(`meta/validations/2026-05-28_phase-4.5-pre-entry_self.md` §V3) 에서
Z-X3 (Critic best-plan selection) 채택이 결정되었다.

Slice 2 에서 도입된 Critic revise loop 결과 plan 별 final verdict 가 누적되므로,
이를 활용해 8-dim 기준 best plan idx 를 응답에 포함시키면 frontend wrapper 에서
1개를 강조 표시할 수 있다. PlanCard.tsx 무수정 정책(사용자 결정 6-a) 은 그대로 유지.

## Decision

Phase 4.5 Slice 3 에서 다음을 도입한다:

1. **`select_best_plan_index(verdicts: list[dict]) -> int | None`** — `backend/fastapi/agents/critic.py` 추가.
   - 우선순위: `overall_score_avg` (Critic primary, 0~5 float) → `overall_score` → `scores` dict 8-dim 평균.
   - Tie-breaking: plan_index 가 더 작은 쪽 (deterministic — 동일 입력 동일 출력).
   - 모든 verdict invalid / 빈 list 시 `None` 반환 (frontend 에서 highlight 생략).
2. **`Body.recommended_plan_index: Optional[int]`** — `backend/fastapi/schemas/output.py` 신규 필드.
   - `plan_candidates` 순서 0~2 (max_length=3 enforce 그대로 유지).
   - critic skip / 모든 verdict invalid 시 `None`.
3. **Frontend wrapper highlight** — `apps/web/app/plan/[plan_id]/page.tsx`.
   - `recommended_plan_index === i` 일 때 wrapper `<div>` 에 `ring-2 ring-emerald-500 ring-offset-2` 적용.
   - 좌상단 "AI 추천" badge (wrapper `relative` 컨테이너에 absolute 배치).
   - `data-recommended="true"` data attribute (eval/observability 용).
   - selected ring (primary-500) 우선순위 > recommended ring (emerald-500) — 사용자 선택 시 badge 숨김.
4. **PlanCard.tsx 무수정 유지** — 사용자 결정 6-a 정신.
   - 8연속 0줄 baseline (Phase 1 Slice 7 이후 git diff 0).
   - D3/D4 4계층 정합은 Phase 5+ 이관.

## Rationale

- 3개 plan 중 1개 추천 → 사용자 결정 부담 ↓ (단, 사용자가 reject 가능 — 자동 선택 X).
- Critic verdict 효과 측정 가능 → `recommended_plan_index == user_selected_plan_index` 일치율 metric (Phase 9+ eval-run).
- wrapper UI 방식 → PlanCard 4계층 정합 미루기 (D3/D4 Phase 5+).
- Optional 필드 추가 패턴 → output_schema.md 회귀 0 (contract-change Skill 절차 불필요).

## Constraints

- 8-dim 가중치 동일 가정 — 실제 사용자 선호와 다를 수 있음. Phase 9+ eval-run 에서 학습 가능한 weighting 도입 검토 (NG8 범위 외).
- `recommended_plan_index` 가 `None` 일 수 있음 (모든 verdict invalid / critic skip) — frontend 에서 highlight 생략으로 처리 (방어).
- 선택과 추천이 충돌할 때 selected ring 우선 — UX 일관성 (사용자 의지 우선).
- PlanCard.tsx **0줄 변경 ★** — 1줄이라도 변경되면 사용자 결정 6-a 위반.

## Trade-offs

| 선택 | 채택 사유 | 미채택 후보 |
|---|---|---|
| `overall_score_avg` 우선 | Critic primary 출력 키, 0~5 정수 평균 (`_derive_verdict` 내부 산출) | 8-dim weighted sum (Phase 9+ 이관) |
| Tie-break = lower idx | deterministic, 테스트 안정성 | 무작위 선택 (eval 재현 불가) |
| wrapper highlight | PlanCard 무수정 정책 (6-a) | PlanCard 에 `recommended?: boolean` prop 추가 (D3/D4 이관 위반) |
| Optional 필드 | 회귀 0, 호환 변경 | breaking change (Phase 1 endpoint 영향) |

## Verification

- `pytest backend/fastapi/tests/test_critic.py::test_select_best_plan_index_*` (6 케이스):
  - returns_highest_score / tie_breaking / empty / all_invalid / scores_dimension_fallback / skips_invalid_uses_remaining
- `pytest backend/fastapi/tests/` 전체 회귀 0 (Slice 2 103 → 108~109).
- `next build` 11 routes 유지 + tsc 0 + lint clean.
- **`git diff HEAD~N HEAD -- apps/web/components/PlanCard.tsx --stat` = 0 lines** ★ (8연속 baseline).

## References

- `meta/proposals/2026-05-28_phase-4-retrospective-proposals.md` §Z-X3
- `meta/validations/2026-05-28_phase-4.5-pre-entry_self.md` §V3
- `phases/active/phase-4.5-critic-revise-loop/non_goals.md` (NG5 PlanCard 무수정)
- `phases/active/phase-4.5-critic-revise-loop/multi_slice_plan.md` Slice 3
- `docs/decisions/phase_4_5_critic_revise.md` (ADR-016 — 입력 verdict 출처)
- `docs/contracts/output_schema.md` §9 (Critic evaluation, recommended_plan_index 추후 반영)
