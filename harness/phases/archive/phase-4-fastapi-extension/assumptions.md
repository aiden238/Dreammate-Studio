# Phase 4 — Assumptions (phase-start v1.3.0 §6 4점검)

> 작성: 2026-05-28
> GPT 검토 채택 후 재조율판 (4 Slices)

---

## 1. Assumptions

### 1.1 확정 가정

| # | 가정 | 근거 |
|---|---|---|
| A1 | Phase 0/1/2/3 baseline 가용 (pytest 62 + next build OK + audit 0 drift) | 4 archive |
| A2 | Phase 1 endpoint `/api/v1/generate` 무수정 보존 (header만 추가) | 사용자 결정 5-a |
| A3 | PlanCard 무수정 (D3는 Phase 5+) | 사용자 결정 6-a |
| A4 | component_map.md read-only 절대 (조정 4번 11+ 연속 0줄 목표) | Phase 3 패턴 |
| A5 | 3-plan = 3 parallel call (asyncio.gather) + multi-model 인터페이스 | 사용자 결정 4-b |
| A6 | Critic revise loop / Rewriter / SSE / PlanComparisonCard 본격 = Phase 4.5 또는 Phase 5+ 이관 | GPT 검토 채택 |
| A7 | 다음 phase 선택은 Slice 4 retrospective에서 (옵션 A/B/C) | 사용자 결정 3-c |
| A8 | P-X1 §SELF-VERIFICATION 4연속 PASS 목표 (Phase 3 5 + Phase 4 4 = 9 streak) | phase-start v1.3.0 |
| A9 | **Contract cross-reference 점검** (v1.3.0 §6.1): audit_naming 0 drift (2026-05-28) | 진입 시 실행 확인 |

### 1.2 불확실 항목 (W4-X)

| ID | 항목 | 검증 시점 |
|---|---|---|
| W4-1 | 3-plan LLM cost (3 parallel, gpt-4o-mini × 3 ≈ $0.001~0.003/호출) | Slice 2 실측 |
| W4-2 | 3개 approach_label unique 강제 시 retry 1회로 충분한지 | Slice 2 검증 |
| W4-3 | PlanCard × 3 360px 가독성 (세로 스택 + scroll snap) | Slice 3 manual |
| W4-4 | Phase 1 / Phase 4 endpoint 동시 운영 시 frontend 어댑터 비용 | Slice 1 진입 시 |
| W4-5 | multi-model 인터페이스 default 값 (모두 mini vs 1개 4o) | Slice 2 dispatch 전 결정 |

(SSE / revise / 4-layer 관련 W4-X는 다음 phase로 이관)

### 1.3 Contract cross-reference 점검 (v1.3.0 §6.1)

```
[2026-05-28] scripts/audit_naming.ps1 실행
결과:
  plan_candidates   PASS   0 drift
  video_projects    PASS   0 drift
  critic_evaluation PASS   0 drift
  rag_references    PASS   0 drift

→ Phase 4 진입 baseline OK.
```

---

## 2. Simplest Slice (3회 압축)

```
1차 답: 4 endpoints + 3-plan + Critic revise + SSE + Frontend 4-layer + Final (6 Slices)
2차 답: 4 endpoints + 3-plan + Frontend 최소 + Final (GPT 검토 채택 — 4 Slices)
3차 답: POST /plans/{id}/generate 1개만 + plans length 3 응답 (sync, frontend 추후)
```

**최종 Slice 2 baseline**:
- `POST /api/v1/plans/{plan_id}/generate` sync 호출
- `asyncio.gather` 3 parallel
- plans length 3 + approach_label unique
- Critic 1회 평가 (revise 없음)
- Phase 3 P-THIN-VERTICAL-001 패턴 재사용

→ Slice 1 (endpoints baseline)이 정립되면 Slice 2가 패턴 복제.

---

## 3. Surgical Scope

### 3.1 editable

```
backend/fastapi/
  routers/plans.py             (NEW)
  schemas/plans.py             (NEW)
  agents/planning.py           (UPDATE — 3 parallel + multi-model)
  schemas/output.py            (UPDATE — plans length 3)
  routers/generate.py          (UPDATE — X-API-Deprecation header만)
  config.py                    (UPDATE — openai_models_for_3plan list)
  tests/test_plans.py          (NEW)
  tests/test_3_plan.py         (NEW)

apps/web/
  app/plan/[plan_id]/page.tsx  (NEW)
  app/plan/page.tsx            (UPDATE 최소 — Phase 4 redirect 선택)
  lib/api.ts                   (UPDATE — Phase 4 endpoints)
  lib/types.ts                 (UPDATE — Phase 4 타입)

scripts/smoke_test_phase_4.ps1 (NEW)
docs/decisions/phase_4_endpoint_migration.md (ADR-014)
docs/decisions/phase_4_3plan_multi_model.md (ADR-015)
phases/active/phase-4-fastapi-extension/ (9 entry files, 작성 중)
eval/qa_reports/phase-4-*.md
meta/handoffs/2026-05-28_phase-4-entry.md
meta/retrospectives/phase-4.md
```

### 3.2 read-only (★ Phase 4 강조)

```
docs/contracts/                      ← 전체
ai_system/                            ← prompt_registry P-008 미도입
apps/web/component_map.md ★          ← 조정 4번 절대 (11+ 연속 0줄)
apps/web/components/PlanCard.tsx ★   ← 사용자 결정 6-a 무수정
apps/web/components/{ErrorCard, ProgressStepper, SubmitButton}.tsx ← Phase 1 유지
apps/web/components/discovery/*       ← Phase 2/3 유지
apps/web/components/common/*          ← Phase 3 유지
apps/web/components/quick/*           ← Phase 3 유지
apps/web/app/{page, plan/page}.tsx    ← Phase 1 보존 (plan/page.tsx는 최소 UPDATE 가능)
apps/web/app/new/*                    ← Phase 3 보존
apps/web/lib/{design_tokens, state/wizard, discovery_state, quick_state, mode_branching, errors}.ts
                                      ← Phase 3 baseline
apps/web/page_map.md, design_handoff.md, design_system/*, *flow.md, wireframes/* ← Phase 2
apps/web/design.md
backend/fastapi/agents/{intent, critic}.py  ← Phase 2/3 stable
backend/fastapi/rag/*, db/*           ← Phase 1 stable
backend/fastapi/{main, lifespan}.py    ← stable (config은 multi-model 추가만)
.claude/skills/
PROJECT_STATE / PHASE_REGISTRY        ← main session
```

### 3.3 forbidden

```
phases/archive/  ← Phase 0/1/2/3
phases/planned/phase_5~30
```

---

## 4. Verification

### 4.1 자동

| 검증 | 도구 | Slice |
|---|---|---|
| audit_naming 0 drift | scripts/audit_naming.ps1 | 매 |
| audit_page_component 0 drift | scripts/audit_page_component.ps1 | 매 (특히 Slice 3) |
| pytest 62 + 신규 ≥ 12 = 74+ | python -m pytest -q | 매 |
| next build / tsc / lint 0 | npm run build / npx tsc / npx next lint | Slice 3+ |
| Phase 1 endpoint 회귀 | curl POST /api/v1/generate | 매 |
| Phase 4 endpoints 동작 | curl 4개 | Slice 2+ |
| §SELF-VERIFICATION (P-X1) | git diff --stat | 매 Slice 의무 |

### 4.2 수동

| 검증 | 방법 | Slice |
|---|---|---|
| 3-plan unique approach_label | sub-agent 출력 검증 | Slice 2 |
| PlanCard × 3 360px UX | manual visual | Slice 3 |
| 변경성 시뮬 5/5 회귀 | walkthrough | Slice 4 |
| LLM cost 측정 | Slice 2 sub-agent 보고 | Slice 2 |

### 4.3 P-X1 §SELF-VERIFICATION (모든 sub-agent 의무)

```bash
git status
git diff --stat HEAD
```

검증 항목:
- editable 외 forbidden 0건
- **component_map.md 0줄 (Slice 1~4 모두)**
- **PlanCard.tsx 0줄 (Phase 4 전체)**
- Phase 1 endpoint 회귀 0
- Phase 3 baseline 0줄

---

## 5. 4점검 요약

| 점검 | 결과 |
|---|---|
| Assumptions | 확정 9개 + 불확실 5개 + audit_naming 0 drift |
| Simplest Slice | Slice 2 = 3 parallel call + plans length 3 (P-THIN-VERTICAL 재사용) |
| Surgical Scope | editable 15개 / read-only 광범위 (PlanCard 강조) / forbidden 명확 |
| Verification | 자동 7개 + 수동 4개 + P-X1 4 Slice 의무 |

---

## 6. 다음 단계

1. `work_plan.md` 작성 (Slice 1~4 detail)
2. `multi_slice_plan.md` 작성 (Wave 1~4 sequential)
3. `meta/handoffs/2026-05-28_phase-4-entry.md`
4. `eval/qa_reports/phase-4-entry-check_2026-05-28.md`
5. PROJECT_STATE / PHASE_REGISTRY 갱신
6. 진입 commit + push
7. **Wave 1 Slice 1 sub-agent dispatch**
8. Wave 2 (Slice 2) → Wave 3 (Slice 3) → Wave 4 (Slice 4)
9. **Slice 4 retrospective에서 다음 phase 결정** (사용자 결정 3-c)
