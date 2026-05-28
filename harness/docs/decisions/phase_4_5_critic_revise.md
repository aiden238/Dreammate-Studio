# ADR-016 — Phase 4.5 Critic Revise Loop + Rewriter Agent

> Date: 2026-05-28
> Status: Accepted
> Phase: 4.5 (mini-phase, post Phase 4)
> Slice: 2
> Related: ADR-014 (phase_4_endpoint_migration), ADR-015 (phase_4_3plan_multi_model)

## Context

Phase 4 종료 시점 Critic verdict는 단일 호출 결과만 노출 (overall_verdict / scores / blocking_issues).
verdict가 `revise`일 때 plan을 자동 개선하는 절차가 없어 사용자가 직접 수정해야 하는 부담이 있었다.
Phase 4 회고(`meta/retrospectives/phase-4.md`)와 사전 검증(`meta/validations/2026-05-28_phase-4.5-pre-entry_self.md` §V1)에서
revise loop 도입이 Phase 5 진입 전 우선순위로 결정되었다.

## Decision

Phase 4.5 Slice 2에서 다음을 도입한다:

1. **Rewriter Agent (P-008)** — `backend/fastapi/agents/rewriter.py` 신규.
   - `async def run_rewriter(plan, critic_verdict, *, model, client) -> dict`
   - 인라인 시스템 프롬프트 (Phase 6+ prompt_registry 정식화 전까지 — NG7).
   - graceful: LLM 실패 / non-dict 응답 / JSON parse 실패 시 원본 plan 반환 + `_rewriter_warning` 마커.
2. **Critic Revise Loop** — `/api/v1/plans/{plan_id}/generate` endpoint에서 plan별 최대 2회 revise.
   - plan 별로 asyncio.gather 병렬 처리 (Planning parallel 패턴 재사용).
   - run_critic은 sync 함수이므로 `loop.run_in_executor` 로 thread pool 위임.
3. **revise_history 응답 노출** — `Body.revise_history: list[list[dict]] | None`.
   - 외부 list = plan index (plan_candidates 와 동일 순서).
   - 내부 list = attempt 0, 1, 2, ... 순차 dict (attempt / action / revised / max_reached?).
4. **`critic_max_revise` 설정** — `config.Settings.critic_max_revise: int = 2`.
   - 환경변수 `CRITIC_MAX_REVISE` 로 override 가능.
   - 0 = loop 비활성. 1~2 권장. 5 상한.

## Constraints

- Rewriter 실패 시 원본 plan 유지 + `_rewriter_warning` 마커 (graceful, 사용자 차단 금지).
- 인라인 prompt 사용 (NG7: Phase 6+ prompt_registry 정식화 전까지).
- revise 효과 eval은 Phase 9+ (NG8: eval-run Skill 정식화 이후).
- Optional 필드 추가 패턴 → output_schema.md 회귀 0 (contract-change Skill 절차 불필요, ADR 만 누적).
- PlanCard.tsx 무수정 (사용자 결정 6-a 계승) — best-plan UI 는 Slice 3 wrapper 에서 처리.

## Rationale

- Critic verdict가 만들어내는 가치 활성화 (Phase 4 까지는 진단만, 개선 미실행).
- 최대 2회 차단으로 무한 루프 위험 0 (확정 결정 [5]).
- Optional 필드 추가 패턴 → output_schema 회귀 0 (호환성 유지).
- asyncio.gather 패턴 재사용으로 3 plan × revise 1~2회의 latency 폭증 방지 (parallel).
- 인라인 prompt → 본 Phase scope 압축. prompt_registry 정식화는 prompt 수가 충분히 누적된 Phase 6+에서 단일 phase 로 분리.

## Trade-offs

- **LLM 호출 횟수 ↑**: plan당 최대 4회 (critic 1회 + revise×2의 각 round critic+rewriter 2회 × 2 = 6회 worst case).
  - 완화: critic_max_revise=2 상한 + plan별 parallel.
  - Phase 9+ cost-review Skill 로 실제 비용 추적 예정.
- **prompt_registry 미사용**: Phase 6+ 정식 등록 시 prompt drift risk.
  - 완화: Phase 4.5 는 단일 함수 단일 prompt 이므로 risk 낮음. ADR-016 본문에 prompt 전문 기록.
- **revise 효과 unmeasured**: NG8 — Phase 9+ eval-run 정식화까지 정량 측정 불가.
  - 완화: U1 (assumptions §1.2) 로 Phase 4.5 회고 시점 재평가 예약.

## Verification

- `pytest backend/fastapi/tests/test_rewriter.py` (6 케이스: 메타 / 기본 / custom model / failure / non-dict / invalid-json / empty-dict).
- `pytest backend/fastapi/tests/test_plans.py::test_revise_history_present_in_response`
- `pytest backend/fastapi/tests/test_plans.py::test_revise_loop_max_2_blocks_third_revise`
- `pytest backend/fastapi/tests/test_plans.py::test_critic_approve_no_revise`
- Phase 4 baseline (pytest 93/93 + smoke 8/8) 회귀 0 유지.
- smoke_test_phase_4_5.ps1 revise 케이스 추가는 Slice 4 에서 진행.

## References

- `phases/active/phase-4.5-critic-revise-loop/goals.md` (G1, G2)
- `phases/active/phase-4.5-critic-revise-loop/scope.md` (in-scope §1.1)
- `phases/active/phase-4.5-critic-revise-loop/non_goals.md` (NG7, NG8)
- `phases/active/phase-4.5-critic-revise-loop/assumptions.md` (§6.2 Simplest Slice = `run_rewriter()`)
- `phases/active/phase-4.5-critic-revise-loop/multi_slice_plan.md` (Slice 2 작업 단위)
- `meta/validations/2026-05-28_phase-4.5-pre-entry_self.md` (§V1 revise loop 필요성)
- `meta/proposals/2026-05-28_phase-4-retrospective-proposals.md` (Z-X3 best-plan, Phase 4.5 mini-phase 권장)
- `ai_system/prompts/prompt_registry.md` (P-008 자리 — Phase 6+ 정식 등록 예정)
