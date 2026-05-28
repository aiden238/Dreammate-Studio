# Phase 4 — Scope

> 작업 범위 (재조율판, GPT 검토 반영). Scope 밖은 Phase 4.5 / 5+로 이관.

---

## In Scope

### 1. Slice 1 — Foundation Contract Endpoints

| 산출물 | 위치 |
|---|---|
| 4 endpoints router | `backend/fastapi/routers/plans.py` |
| Phase 4 input schemas | `backend/fastapi/schemas/plans.py` |
| Phase 1 endpoint deprecated header | `backend/fastapi/routers/generate.py` (UPDATE: `X-API-Deprecation` header만) |
| 4 endpoints smoke tests | `backend/fastapi/tests/test_plans.py` |
| ADR-014 endpoint migration 정책 | `docs/decisions/phase_4_endpoint_migration.md` |

### 2. Slice 2 — Thin Vertical 3-plan (★ multi-model 가능 구조)

| 산출물 | 위치 |
|---|---|
| 3 parallel async call + multi-model 인터페이스 | `backend/fastapi/agents/planning.py` (UPDATE) |
| `Body.plan_candidates` length 3 활성 | `backend/fastapi/schemas/output.py` (UPDATE) |
| `POST /plans/{id}/generate` 본격 구현 | `backend/fastapi/routers/plans.py` (UPDATE) |
| 3-plan 검증 tests | `backend/fastapi/tests/test_3_plan.py` |
| Multi-model config (향후 확장) | `backend/fastapi/config.py` (UPDATE: `openai_models_for_3plan` list) |
| ADR-015 3-plan multi-model 구조 | `docs/decisions/phase_4_3plan_multi_model.md` |

### 3. Slice 3 — Frontend 3-plan minimal

| 산출물 | 위치 |
|---|---|
| Phase 4 결과 페이지 (3-plan list) | `apps/web/app/plan/[plan_id]/page.tsx` |
| Phase 1 페이지 보존 (Phase 4 query 시 redirect 선택) | `apps/web/app/plan/page.tsx` (UPDATE 최소) |
| Phase 4 endpoints fetch wrapper | `apps/web/lib/api.ts` (UPDATE) |
| Phase 4 응답 타입 | `apps/web/lib/types.ts` (UPDATE) |
| **PlanCard.tsx 무변경** ★ (조정 6-a) | — |

### 4. Slice 4 — Final + Archive

| 산출물 | 위치 |
|---|---|
| smoke test | `scripts/smoke_test_phase_4.ps1` |
| qa-check v1.2.0 final | `eval/qa_reports/phase-4-final_2026-05-28.md` |
| retrospective | `meta/retrospectives/phase-4.md` |
| 다음 phase 선택지 | retrospective + closing_notes에 명시 |
| closing_notes | `phases/active/phase-4-fastapi-extension/closing_notes.md` |
| archive 이동 | `phases/active → archive/phase-4-fastapi-extension/` |
| 상태 파일 갱신 | PROJECT_STATE / PHASE_REGISTRY / 00_START_HERE / README |

---

## 범위 경계

```
Phase 4 포함                                Phase 4 미포함
─────────────────────────────────           ─────────────────────────────────
4 contract endpoints (sync)                  SSE Progress streaming (Phase 5+)
3-plan generation (parallel)                 Critic revise loop + Rewriter (Phase 4.5+)
Multi-model 인터페이스 (구조만, default 단일 모델)  실제 multi-provider (Anthropic 등) (Phase 21+)
Critic 8-dim verdict 노출 (현재 구조 유지)    Critic verdict UI 본격 (Phase 5+)
Frontend 3-plan minimal (PlanCard × 3)       PlanComparisonCard 4-layer 본격 (Phase 5+)
Phase 1 endpoint 호환 유지                   Phase 1 endpoint 제거 (Phase 8+ 사용자 결정 5)
component_map.md read-only (조정 4번)         PlanCard 4-layer 재정의 (Phase 5+, D3)
```

---

## 예상 파일 변경 (15 신규 / 6 수정)

```
신규 (~15):
  backend/fastapi/
    routers/plans.py
    schemas/plans.py
    tests/test_plans.py
    tests/test_3_plan.py
  apps/web/
    app/plan/[plan_id]/page.tsx
  scripts/smoke_test_phase_4.ps1
  docs/decisions/phase_4_endpoint_migration.md (ADR-014)
  docs/decisions/phase_4_3plan_multi_model.md (ADR-015)
  phases/active/phase-4-fastapi-extension/ (9 entry files)
  eval/qa_reports/ (6 reports)
  meta/handoffs/2026-05-28_phase-4-entry.md
  meta/retrospectives/phase-4.md

수정:
  backend/fastapi/agents/planning.py (3-plan + multi-model)
  backend/fastapi/schemas/output.py (plans length 3)
  backend/fastapi/routers/generate.py (deprecated header)
  backend/fastapi/config.py (multi-model config)
  apps/web/lib/api.ts (Phase 4 endpoints)
  apps/web/lib/types.ts (Phase 4 타입)
  apps/web/app/plan/page.tsx (Phase 4 redirect, 선택)
  PROJECT_STATE / PHASE_REGISTRY / 00_START_HERE / README
```

---

## 완료 기준 요약

`acceptance.md` A1~A10 참조. 핵심:
- 4 endpoints 200 응답
- 3-plan length 3 + approach_label unique
- Phase 1 endpoint 회귀 0
- Phase 3 frontend 회귀 0
- audit_naming + audit_page_component 0 drift
- pytest 62 + 신규 ≥ 12 = 74+ PASS
- **§SELF-VERIFICATION (P-X1) 4연속 PASS** (Slice 1~4 모두)
- **component_map.md 11연속 0줄** (Phase 3 7 + Phase 4 4)
