# Phase 9 — Multi-Slice Plan

> 6 Slice 모두 sub-agent dispatch, sequential
> 총 10~14h

---

## Wave 구조
```
Wave 1: Slice 1 [Pre-Entry — validations + security-review(두 번째) + ADR-030/031/032]
  ↓
Wave 2: Slice 2 [Schema 0005 + Repo (selection/feedback/brand_memory) graceful + contract-change]
  ↓
Wave 3: Slice 3 [API endpoints (select/feedback) + orchestrator + normalize_to_canonical wiring]
  ↓
Wave 4: Slice 4 [Brand Memory 준비 — feedback→candidate 적재 경로 + ADR-031 finalize]
  ↓
Wave 5: Slice 5 [Frontend 피드백 UI (page.tsx inline wrapper) — PlanCard·component_map 무수정]
  ↓
Wave 6: Slice 6 [Close]
```

---

## Slice 1 — Pre-Entry (1.5~2.5h)
1. `meta/validations/2026-05-29_phase-9-pre-entry_self.md` V1~V7 (selection/feedback 영속 / normalize wiring 회귀 / Brand Memory 준비 경계 / 피드백 PII / repo graceful / 실 plans 정합 / 피드백 UI wrapper)
2. external placeholder
3. **security-review Skill 두 번째 정식** → `meta/security_reviews/2026-05-29_phase-9-feedback-pii.md` (피드백 reason text PII + reject 사유 + RLS user 격리 + GET 피드백 권한)
4. ADR-030 (feedback/selection persistence — 실 plans 테이블 정합, graceful) + ADR-031 (Brand Memory prep — P-AUX-2 설계, agent 미구현 Phase 10+) + ADR-032 (normalize_to_canonical wiring — critic step canonical, deprecated 병행)
5. skill_usage_log + PROJECT_STATE + entry commit
- editable: meta/validations, meta/security_reviews, docs/decisions/phase_9_*, skill_usage_log, PROJECT_STATE, phases/active/phase-9-*/notes
- forbidden: backend/*, apps/web/*, contracts, scripts, skills, 이전 ADR, archive

## Slice 2 — Schema + Repo (2.5~3.5h)
1. **contract-change** — `docs/contracts/db_schema.md`: §4.3 selected_plans (실 plans 정합: plan_id + selected_option_index 0–2 + selection_reason) + §5.2 feedback_events 보강 + brand_memory prep cross-ref
2. `0005_feedback_selection.sql` 신규: selected_plans + feedback_events + discovery_choices(선택) + brand_memory_entries + RLS (Phase 5 패턴) — 실 plans/auth_user_id 정합
3. `selection_repo.py` + `feedback_repo.py` + `brand_memory_repo.py` (graceful, PlansRepo 패턴)
4. `db/__init__.py` export
5. `tests/test_selection_feedback.py` + `test_brand_memory_prep.py`(일부) — graceful CRUD
- editable: db/migrations/0005, db/repositories/{selection,feedback,brand_memory}_repo, db/__init__, db_schema.md, tests/test_selection_feedback
- forbidden: ★ db/{client,plans_repo,migrations 0001~0004}, schemas/output, agents, routers, orchestration(Slice 3), apps/web, PlanCard, component_map, 이전 ADR

## Slice 3 — API + orchestrator + normalize wiring (2.5~3.5h)
1. `schemas/plans.py`: SelectRequest/FeedbackRequest/SelectionResponse/FeedbackResponse
2. `routers/plans.py`: POST /plans/{id}/select + POST /plans/{id}/feedback + GET /plans/{id}/feedback (repo 호출 thin)
3. `orchestration/moa_orchestrator.py`: critic step에 `normalize_to_canonical` wiring (verdict = normalize_to_canonical(run_critic(...))) → critic_evaluation canonical 0–1 + deprecated 0–5 병행
4. `tests/test_plans_feedback_api.py` + `test_critic_canonical_wiring.py`
5. **★ normalize wiring 의도된 delta**: critic_evaluation canonical 추가로 깨지는 baseline test가 있으면 최소 assertion만 갱신 (Phase 8 Slice 4 패턴). schemas/output.py 불변.
6. agent-io-check (critic 정합)
- editable: schemas/plans, routers/plans, orchestration/moa_orchestrator, tests/{test_plans_feedback_api,test_critic_canonical_wiring}, (의도 delta) 해당 baseline assertion 최소
- forbidden: ★ schemas/output(불변), agents/*(critic 호출만), db/*(Slice 2), apps/web, PlanCard, component_map, 이전 ADR
- ★ 의도 delta 외 baseline test 수정 금지

## Slice 4 — Brand Memory 준비 (1.5~2h)
1. `rag/feedback_to_candidate.py`: feedback/selection → candidate_knowledge(source_kind='user_feedback'/'user_choice', status='pending') 적재 경로 (Phase 7 5단계 pending 정합, 자동 승격 X)
2. `routers/plans.py` (소폭): feedback 저장 시 candidate 적재 경로 연결 (graceful, 선택)
3. ADR-031 finalize (P-AUX-2 brand_memory_extractor 설계 명세 — input/output/활성화 조건 Phase 10+)
4. `tests/test_brand_memory_prep.py` 완성 (feedback→candidate 적재 + brand_memory_repo)
- editable: rag/feedback_to_candidate, routers/plans(소폭), docs/decisions/phase_9_brand_memory_prep(ADR-031), tests/test_brand_memory_prep
- forbidden: ★ rag/{promotion,retrieval,...}(Phase 7 baseline — 적재 경로만 신규), agents, schemas/output, orchestration(Slice 3), apps/web, PlanCard, component_map

## Slice 5 — Frontend 피드백 UI (wrapper) (1.5~2.5h)
1. `apps/web/lib/types.ts`: SelectRequest/Response + FeedbackRequest/Response
2. `apps/web/lib/api.ts`: selectPlan / sendFeedback (credentials include)
3. `apps/web/app/plan/[plan_id]/page.tsx`: 선택 버튼 + 반려 이유 입력 UI **inline** (PlanCard 외부 wrapper, 신규 component 안 만듦)
4. next build 11 routes + tsc 0 + lint clean
- editable: apps/web/{lib/types,lib/api,app/plan/[plan_id]/page.tsx}
- forbidden: ★ PlanCard.tsx(0줄), component_map.md(0줄 — 신규 component 등록 X), lib/auth(Phase 5), backend/*
- ★ PlanCard·component_map 0줄 사후 검증

## Slice 6 — Close (1~1.5h)
1. `scripts/smoke_test_phase_9.ps1` (15 체크: Phase 8 14 + feedback/selection 1)
2. `scripts/scenario_simulation.ps1` v5 (S21~S25: selected_plans / feedback_events / normalize wiring / brand_memory prep / 피드백 UI)
3. audit×2 + agent-io-check + design-review(피드백 UI) + ai-architecture-review(선택)
4. `meta/retrospectives/phase-9.md`
5. `meta/patterns.md` (P-X1 42연속 + P-FEEDBACK-LOOP-001 신규 후보 + P-CANONICAL-WIRING-001 신규 후보)
6. `meta/skill_usage_log.md` (security-review 두 번째 + contract-change)
7. phase-complete v1.2.0 (P-X2 일곱 번째 자동 게이트)
8. archive 이동 + closing_notes (Phase 9.5 eval-run / Phase 10 통합 권장)
9. state docs 갱신
- editable: scripts, meta/{retrospectives,patterns,skill_usage_log}, phases/archive/phase-9-*, closing_notes, state docs
- forbidden: backend/*, apps/web/*, contracts, 이전 ADR(030/031/032 보존), scripts/audit_*+schema_stress+smoke_4_5~8, skills, baseline test

---

## 충돌 매트릭스
| Slice | db/migr+repo | routers/plans | orchestrator | schemas/plans | rag | frontend | tests | contracts/ADR | meta/scripts | state |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ ADR-030/031/032 | ✅ valid+sec | ✅ entry |
| 2 | ✅ 0005+3 repo | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ selection_feedback | ✅ db_schema | ❌ | ❌ |
| 3 | ❌ | ✅ select/feedback API | ✅ normalize wiring | ✅ Select/Feedback | ❌ | ❌ | ✅ api+canonical | ❌ | ❌ | ❌ |
| 4 | ❌ | ✅ candidate 적재(소폭) | ❌ | ❌ | ✅ feedback_to_candidate | ❌ | ✅ brand_memory_prep | ✅ ADR-031 finalize | ❌ | ❌ |
| 5 | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ page+api+types | ❌ | ❌ | ❌ | ❌ |
| 6 | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ retrospective+patterns+scripts | ✅ all |

Sequential 충돌 0. (plans.py Slice 3 API + Slice 4 candidate 적재 소폭 — 순차 보장)

---

## 누적 P-X1 streak
| Phase | streak |
|---|---|
| Phase 8 | 36 |
| Phase 9 | **6 (목표)** |
| **누적** | **42** |

## 시간 추정
| Slice | 시간 | 누적 |
|---|---|---|
| 1 | 1.5~2.5h | 1.5~2.5h |
| 2 | 2.5~3.5h | 4~6h |
| 3 | 2.5~3.5h | 6.5~9.5h |
| 4 | 1.5~2h | 8~11.5h |
| 5 | 1.5~2.5h | 9.5~14h |
| 6 | 1~1.5h | **10.5~15.5h** |
