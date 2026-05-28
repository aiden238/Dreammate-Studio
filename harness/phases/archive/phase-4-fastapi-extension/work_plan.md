# Phase 4 — Work Plan (4 Slices, GPT 검토 채택)

> phase-start v1.3.0 §6.2 Simplest Slice + GPT 검토로 6→4 Slices 축소
> 작성: 2026-05-28

---

## Slice 개요

```
Slice 1 (Foundation) → Slice 2 (Thin Vertical 3-plan) → Slice 3 (Frontend minimal) → Slice 4 (Final)
모두 sequential (사용자 결정 2-a).
```

---

## Slice 1 — Foundation: Contract Endpoints

**목표**: Phase 4 새 endpoints 4개 baseline. Phase 1 endpoint 무수정 (header만).

### 산출물
- `backend/fastapi/routers/plans.py` (NEW)
  - `POST /api/v1/plans/start` → plan_id 발급
  - `POST /api/v1/plans/{plan_id}/wizard/{step}` → skeleton 200 (Phase 4는 mock 응답)
  - `POST /api/v1/plans/{plan_id}/generate` → skeleton (Slice 2 본격)
  - `GET /api/v1/plans/{plan_id}` → 임시 envelope (Slice 2 후 실제 저장된 결과)
- `backend/fastapi/schemas/plans.py` (NEW — input/output schemas)
- `backend/fastapi/routers/generate.py` UPDATE — `X-API-Deprecation: Phase 4` response header (실 동작 무변경)
- `backend/fastapi/main.py` UPDATE — `plans_router` include (minimal)
- `backend/fastapi/tests/test_plans.py` (NEW — 4 endpoints smoke ≥ 6 케이스)
- `docs/decisions/phase_4_endpoint_migration.md` (ADR-014)

### Acceptance
- 4 endpoints 200 응답
- Phase 1 endpoint 회귀 0 + X-API-Deprecation header 노출
- pytest 62 + 신규 ≥ 6 = **68+ PASS**
- audit_naming 0 drift
- **§SELF-VERIFICATION PASS** (component_map.md / PlanCard.tsx 0줄)

### 추정: 2~3h

### Commit
```
phase-4(slice-1): Foundation — 4 contract endpoints + Phase 1 deprecated header
```

---

## Slice 2 — Thin Vertical: 3-plan Generation ★ (multi-model 가능)

**목표**: `POST /plans/{id}/generate` 본격 구현 — 3 parallel async call + multi-model 인터페이스.

### 산출물
- `backend/fastapi/agents/planning.py` UPDATE:
  - `async def run_planning_parallel_3(user_input, *, models=None) -> list[dict]`
  - `asyncio.gather(run_planning(...), run_planning(...), run_planning(...))` (3 parallel)
  - `models` 파라미터 — list[str] of 3 (default: config.openai_models_for_3plan)
  - approach_label 분기 (각 호출마다 다른 hint: narrative / informational / experiment_or_other)
  - retry 1회 (3개 unique 강제, 중복 시 1개 재호출)
- `backend/fastapi/schemas/output.py` UPDATE:
  - `Body.plan_candidates` `max_length=3` 활성
  - validation.warnings 동적 — len(plans)==3 시 phase_1_single_plan 제거
- `backend/fastapi/config.py` UPDATE:
  - `openai_models_for_3plan: list[str] = ["gpt-4o-mini", "gpt-4o-mini", "gpt-4o-mini"]` (default — Slice 2 dispatch 전 사용자 결정 가능)
- `backend/fastapi/routers/plans.py` UPDATE: `POST /plans/{id}/generate` 본격 — Intent → RAG → 3-plan parallel → Critic 1회 평가 → DB 저장 → Envelope
- `backend/fastapi/tests/test_3_plan.py` (NEW — ≥ 6 케이스):
  - 3-plan length === 3
  - approach_label set === 3 (unique)
  - validation.warnings에서 `phase_1_single_plan` 제거
  - Phase 1 endpoint 1-plan 회귀
  - multi-model 인터페이스 (models 파라미터 변경 시 영향) 검증
  - parallel error 시 graceful (1개 실패해도 2개 + fallback 1개)
- `docs/decisions/phase_4_3plan_multi_model.md` (ADR-015 — multi-model 구조)

### Acceptance
- 3-plan length 3 + approach_label unique
- multi-model 인터페이스 검증 (models 파라미터 분기)
- Phase 1 endpoint 회귀 0
- pytest 회귀 0 (68 + 신규 ≥ 6 = 74+)
- **§SELF-VERIFICATION PASS**

### 추정: 2~3h

### Commit
```
phase-4(slice-2): Thin Vertical — 3-plan parallel generation + multi-model interface
```

---

## Slice 3 — Frontend 3-plan minimal

**목표**: `/plan/[plan_id]` 페이지 3-plan 표시 + 1 선택. **PlanCard 무변경**.

### 산출물
- `apps/web/app/plan/[plan_id]/page.tsx` (NEW)
  - useEffect로 `GET /api/v1/plans/{plan_id}` 호출
  - `body.plan_candidates` 3개 PlanCard 세로 스택 렌더
  - 카드 클릭 시 selected state (sessionStorage 저장 + visual highlight)
  - Loading / Error 상태 (Phase 1 ErrorCard 재사용)
- `apps/web/app/plan/page.tsx` UPDATE 최소:
  - Phase 1 endpoint 응답 형식 그대로 유지
  - Phase 4 query `?plan_id=xxx` 감지 시 `/plan/[plan_id]` redirect (선택)
- `apps/web/lib/api.ts` UPDATE:
  - `generateMultiPlan(planId): Promise<MultiPlanEnvelope>` 신규
  - 기존 `generate(input)` 그대로
  - 4 Phase 4 endpoints fetch wrapper 추가
- `apps/web/lib/types.ts` UPDATE:
  - `MultiPlanEnvelope` (plans length 3 활성)
  - 기존 `Envelope` (Phase 1 호환) 유지

### Acceptance
- `/plan/[plan_id]` 렌더링 + 3 PlanCard + 1 선택
- Phase 1 `/plan` 회귀 0
- Phase 3 `/new/*` 회귀 0
- **PlanCard.tsx 0줄 수정 확인** ★ (사용자 결정 6-a)
- next build / tsc / lint 0 errors
- audit_page_component 0 drift (PlanCard 변경 X)
- **§SELF-VERIFICATION PASS**

### 추정: 2~3h

### Commit
```
phase-4(slice-3): Frontend 3-plan minimal — /plan/[plan_id] PlanCard×3 stack
```

---

## Slice 4 — Final + Archive + 다음 phase 결정 ★

**목표**: 검증 + retrospective + archive + **다음 phase 선택지 명시** (사용자 결정 3-c).

### 산출물
- `scripts/smoke_test_phase_4.ps1` (NEW):
  - Phase 3 baseline (audit_naming + audit_page_component + next build + pytest 62)
  - Phase 4 신규 (4 endpoints + 3-plan + Phase 1 호환)
  - 11~14 routes prerender 검증
- `eval/qa_reports/phase-4-final_2026-05-28.md` (qa-check v1.2.0 11 카테고리)
- `meta/retrospectives/phase-4.md`:
  - P-X1 효과 9연속 측정 (Phase 3 5 + Phase 4 4)
  - GPT 검토 채택 회고 (6→4 Slices 축소 효과)
  - **다음 phase 3 옵션 제시** (A: Phase 4.5 / B: Phase 5 / C: 다른 우선순위)
- `meta/proposals/2026-05-28_phase-4-retrospective-proposals.md` (있다면)
- `phases/active/phase-4-fastapi-extension/closing_notes.md`:
  - A1~A10 결과
  - deferred 명세 (D6 / D7 / D8 / D3 / D4 / D2 / Phase 1 endpoint 제거)
  - **다음 phase 옵션 A/B/C 사용자 결정 대기 표기**
- 변경성 시뮬 5/5 회귀 walkthrough
- meta/patterns.md 갱신 (있다면)
- meta/skill_usage_log.md 누적
- archive 이동 (git mv)
- PROJECT_STATE / PHASE_REGISTRY / 00_START_HERE / README

### Acceptance
- A1~A10 모두 PASS
- 변경성 시뮬 5/5 회귀 (Phase 3 결과 유지)
- P-X1 9연속 streak 달성
- **component_map.md 11+ 연속 0줄 (Phase 3 7 + Phase 4 4 = 11) 보존 확인**
- archive 이동 완료
- 다음 phase 옵션 명시 (A/B/C)

### 추정: 1~2h

### Commit
```
phase-4(slice-4): Final QA + smoke + retrospective + archive + next phase 옵션 명시
```

---

## 전체 추정

| Slice | 시간 | 누적 |
|---|---|---|
| 1 (Foundation) | 2~3h | 2~3h |
| 2 (Thin Vertical) | 2~3h | 4~6h |
| 3 (Frontend) | 2~3h | 6~9h |
| 4 (Final) | 1~2h | **7~11h** |

**Phase 4 총**: 7~11h (Phase 3의 약 50%, GPT 검토 채택 효과).

---

## Slice 진입 규칙 (P-X1 의무)

```
1. 이전 Slice acceptance 통과 확인
2. audit_naming 0 drift 확인
3. sub-agent prompt에 §SELF-VERIFICATION 의무 명시
4. Sub-agent dispatch
5. 완료 시:
   - sub-agent의 §SELF-VERIFICATION 결과 확인 (git status + diff --stat)
   - main session §SELF-VERIFICATION (git log -1 --stat + forbidden grep)
   - audit_naming + audit_page_component + pytest + build 검증
   - git commit message에 §SELF-VERIFICATION PASS 명시
```

---

## scope creep 경고 (GPT 검토 강조)

다음 발견 시 즉시 중단:
- non_goals 항목 추가 시도 (SSE / revise loop / 4-layer 재정의)
- component_map.md 변경 충동
- PlanCard.tsx 변경 충동
- multi-llm-validation 없이 사용자 결정 5-a (Phase 1 endpoint 제거) 시도

→ 즉시 retrospective 또는 deviations.md 기록.

---

## 변경 이력

- 2026-05-28: Slice 1~4 최초 작성 (GPT 검토 채택 후 6→4 Slices)
