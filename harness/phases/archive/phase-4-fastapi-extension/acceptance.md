# Phase 4 — Acceptance Criteria

> A1~A10 모두 통과해야 phase-complete 진입 가능.

---

## A1. Contract Endpoints 4개 동작

```
체크: POST /plans/start + POST /plans/{id}/wizard/{step} + POST /plans/{id}/generate + GET /plans/{id}
기준: 모두 HTTP 200 + Pydantic 응답
```

- [ ] `POST /api/v1/plans/start` 200 + plan_id 발급
- [ ] `POST /api/v1/plans/{plan_id}/wizard/{step}` 200 (Phase 4는 skeleton)
- [ ] `POST /api/v1/plans/{plan_id}/generate` 200 + 3-plan
- [ ] `GET /api/v1/plans/{plan_id}` 200 + Envelope

---

## A2. 3-plan Generation (★ multi-model 가능 구조)

```
체크: body.plan_candidates length=3 + approach_label 3개 unique + multi-model 인터페이스
기준:
  - plans length === 3
  - 3개 approach_label set 크기 === 3 (모두 다름)
  - planning.py가 model 파라미터 분기 가능 (default 단일, 향후 multi)
```

- [ ] plans length 3
- [ ] approach_label unique
- [ ] `validation.warnings`에서 `phase_1_single_plan` 제거
- [ ] config.py에 `openai_models_for_3plan` list (default 단일 모델, 길이 3)
- [ ] ADR-015에 multi-model 구조 명시

---

## A3. Critic verdict 노출

```
체크: body.critic_evaluation 8-dim verdict 구조 노출 (revise loop 없음)
기준: overall_verdict ∈ ["approve", "revise", "reject"]
```

- [ ] critic_evaluation 8 scores 정상 채움
- [ ] overall_verdict 노출 (revise 시도 Rewriter 호출 X — Phase 4.5+ deferred)
- [ ] revise_round = 0 (Phase 4 = revise 없음)

---

## A4. Phase 1 endpoint 회귀 0

```
체크: 기존 POST /api/v1/generate 동작 + Phase 1 frontend / + /plan 정상
기준:
  - curl POST /api/v1/generate → 200 + plans length 1 (Phase 1 호환)
  - X-API-Deprecation: Phase 4 header 노출
  - 응답 body 형식 Phase 1 그대로
```

- [ ] Phase 1 endpoint 200 + 1 plan
- [ ] X-API-Deprecation header 노출
- [ ] Phase 1 frontend `/` 및 `/plan` 정상 라우팅

---

## A5. Phase 3 frontend 회귀 0

```
체크: Phase 3 모든 routes 정상
기준:
  - /new (Mode Branching) → redirect 동작
  - /new/discovery/step/1~7 모두 정상
  - /new/quick + /quick/clarify + /quick/direction + /quick/generate 모두 정상
```

- [ ] `/new` Mode Branching 동작
- [ ] Discovery 7-step 모두 200
- [ ] Quick 4-step 모두 200

---

## A6. Frontend Phase 4 페이지

```
체크: /plan/[plan_id]/page.tsx 3-plan 표시 + 선택 동작
기준:
  - PlanCard × 3 (세로 스택)
  - 카드 1개 선택 시 highlight + sessionStorage 저장
  - 360px viewport 적합
```

- [ ] /plan/[plan_id] 라우팅 동작
- [ ] PlanCard × 3 렌더링
- [ ] 1개 선택 highlight
- [ ] **PlanCard.tsx 무변경 확인** (조정 6-a, D3 Phase 5+)

---

## A7. pytest + build 회귀 0

```
체크: 모든 자동 검증 PASS
```

- [ ] pytest 62 + 신규 ≥ 12 = **74+ PASS** (회귀 0)
- [ ] next build 0 errors
- [ ] tsc --noEmit 0 errors
- [ ] next lint clean

---

## A8. audit 도구 0 drift

```
체크: 모든 자동 audit 통과
```

- [ ] audit_naming 0 drift
- [ ] audit_page_component 0 drift (PlanCard 무변경, /plan/[plan_id] 신규는 page_map 갱신 필요 시 contract-change)
- [ ] smoke_test_phase_4 통과

---

## A9. 변경성 시뮬레이션 5/5 회귀 + component_map.md 0줄

```
체크: design_handoff.md §6.1 5 시나리오 회귀 walkthrough
```

- [ ] 5 시나리오 4~5 PASS (시나리오 5 Quick mode 폐기는 Phase 3 결과 유지)
- [ ] **`component_map.md` 0줄 수정 (4 Slices 모두)** ★ 11+ 연속 보존
- [ ] **§SELF-VERIFICATION (P-X1) 4/4 PASS**

---

## A10. retrospective + 다음 phase 결정

```
체크: Slice 4에서
```

- [ ] `meta/retrospectives/phase-4.md` 작성
- [ ] P-X1 효과 6연속 측정 (Phase 3 5 + Phase 4 4 = 9 PASS streak)
- [ ] **사용자 결정 3-c 반영**: 다음 phase 선택지를 retrospective + closing_notes에 제시
  - 옵션 A: Phase 4.5 mini-phase (Critic revise + Rewriter)
  - 옵션 B: Phase 5 DB/Auth (Critic revise는 Phase 6+)
  - 옵션 C: 다른 우선순위
- [ ] **D6 / D7 / D8 / D3 / D4 / D2 모두 deferred 명시** (closing_notes)

---

## Done Definition

A1~A10 모두 통과 + 4 commits push + archive 이동.

## 이후 Phase

Slice 4 retrospective에서 사용자가 다음 phase 선택 (사용자 결정 3-c).
