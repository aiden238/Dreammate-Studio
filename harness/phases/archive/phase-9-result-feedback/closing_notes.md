# Phase 9 — Closing Notes

> 종료일: 2026-05-31
> 결과: A1~A10 10/10 + M1~M4 4/4 PASS
> 다음 phase: **🟡 pending_user_decision** (A Phase 9.5 eval-run / B Phase 10 통합 / C Phase 11+)

---

## 최종 산출물

### Backend DB layer (~+600 LOC, 4 신규)
- `backend/fastapi/db/migrations/0005_feedback_selection.sql` (selected_plans + feedback_events + brand_memory_entries + RLS — 실 plans/auth_user_id 정합, brand_id → brands(id) PK, source_plan_id → plans.id)
- `backend/fastapi/db/repositories/selection_repo.py` (`SelectionRepo` — select/get graceful, Supabase 실패/미설정 시 in-memory fallback, PlansRepo 패턴)
- `backend/fastapi/db/repositories/feedback_repo.py` (`FeedbackRepo` — record/list_for_plan graceful + reason 저장 전 PII 마스킹, security-review T1)
- `backend/fastapi/db/repositories/brand_memory_repo.py` (`BrandMemoryRepo` — Brand Memory 준비, graceful)

### Backend rag / orchestration / routers (수정 3 + 신규 1)
- `backend/fastapi/rag/feedback_to_candidate.py` (신규 — feedback/selection → candidate_knowledge(source_kind='user_feedback'/'user_choice', status='pending') 적재 경로, 자동 승격 X — Phase 7 5단계 정합)
- `backend/fastapi/orchestration/moa_orchestrator.py` (수정 — critic step `verdict = normalize_to_canonical(run_critic(...))` wiring, canonical 0–1 live + deprecated 0–5 병행, additive 비파괴 사본 → 회귀 0)
- `backend/fastapi/routers/plans.py` (수정 — POST /plans/{id}/select + POST /plans/{id}/feedback + GET /plans/{id}/feedback API + feedback→candidate enqueue graceful)
- `backend/fastapi/schemas/plans.py` (수정 — SelectPlanRequest/Response + FeedbackRequest/Response + FeedbackListResponse)
- `backend/fastapi/db/repositories/__init__.py` + `rag/__init__.py` (export)

### Frontend 피드백 UI (~+200 LOC, wrapper — PlanCard·component_map 0줄)
- `apps/web/lib/types.ts` (SelectRequest/Response + FeedbackRequest/Response)
- `apps/web/lib/api.ts` (selectPlan / sendFeedback — credentials include)
- `apps/web/app/plan/[plan_id]/page.tsx` (선택 버튼 + 반려 이유 textarea **inline** — PlanCard 외부 wrapper, 신규 component 미생성)

### Tests (+44 신규, 기존 249 수정 0)
- `test_selection_feedback.py` — SelectionRepo/FeedbackRepo graceful CRUD + in-memory fallback + reason PII 마스킹
- `test_plans_feedback_api.py` — POST /select + POST /feedback + GET /feedback endpoint + RLS user 격리
- `test_critic_canonical_wiring.py` — normalize_to_canonical wiring 후 critic_evaluation canonical(0–1) + deprecated 0–5 병행 (회귀 0)
- `test_brand_memory_prep.py` — feedback→candidate(pending) 적재 + brand_memory_repo

### Contracts / ADRs
- `docs/decisions/phase_9_feedback_selection.md` (ADR-030, Slice 1 — feedback/selection persistence 실 plans 정합 + graceful PlansRepo 패턴)
- `docs/decisions/phase_9_brand_memory_prep.md` (ADR-031, Slice 1 + Slice 4 finalize — Brand Memory 준비 P-AUX-2 설계, agent 미구현 Phase 10+)
- `docs/decisions/phase_9_critic_canonical_wiring.md` (ADR-032, Slice 1 — normalize_to_canonical wiring, deprecated 0–5 병행)
- `docs/contracts/db_schema.md` (§4.3 selected_plans + §5.2 feedback_events + brand_memory prep cross-ref, Slice 2 — CC-004)

### Meta / security
- `meta/validations/2026-05-29_phase-9-pre-entry_self.md` (V1~V7 PASS — formal 여섯 번째)
- `meta/validations/2026-05-29_phase-9-pre-entry_external.md` (placeholder)
- `meta/security_reviews/2026-05-29_phase-9-feedback-pii.md` (security-review 두 번째 정식 — 피드백 reason PII T1~T6)
- `meta/retrospectives/phase-9.md` (본 phase 회고)
- `meta/patterns.md` (P-FEEDBACK-LOOP-001 신규 + P-CANONICAL-WIRING-001 신규 + P-X1-EFFECT-001 update 42연속 + P-VALIDATION-FORMAL-001 update 여섯 번째)
- `meta/skill_usage_log.md` (Phase 9 사용 요약 11 Skill — security-review 두 번째 정식 + contract-change CC-004)

### Scripts
- `scripts/smoke_test_phase_9.ps1` 신규 (15 체크 — 14 PASS + 1 WARN intended)
- `scripts/scenario_simulation.ps1 v5` (25 시나리오, S21~S25 feedback/selection 추가, P-X2 일곱 번째)

---

## Phase 9 핵심 baseline

| 지표 | Phase 9 종료 |
|---|---|
| pytest | **293/293** (Phase 8 249 baseline + 44 신규, 기존 수정 0) |
| smoke_test_phase_9 | **15/15** (14 PASS + 1 WARN intended — Phase 5 baseline AuthGuard + /login) |
| scenario_simulation v5 | **25/25** (P-X2 일곱 번째 자동 게이트, S21~S25 feedback/selection 추가) |
| schema_stress_test | 5/5 (Phase 6 v2 유지) |
| audit_naming | 0 drift |
| audit_page_component | 2 intended WARN (Phase 5 baseline 계승 — 피드백 UI page.tsx inline은 신규 route/component 미생성 → +0) |
| deprecated critic warnings | 67 → 16 (normalize wiring canonical 우선 경로 정착) |
| component_map.md 0줄 | **40연속** (Phase 2 6 + Phase 3 5 + Phase 4 4 + Phase 4.5 4 + Phase 6 3 + Phase 5 5 + Phase 5.5 1 + Phase 7 1 + Phase 8 5 + Phase 9 6) |
| PlanCard.tsx 0줄 | **30연속** (Phase 4 4 + Phase 4.5 5 + Phase 6 3 + Phase 5 5 + Phase 5.5 1 + Phase 7 1 + Phase 8 5 + Phase 9 6 — frontend slice 있어도 wrapper) |
| P-X1 streak | **42연속** (Phase 3 5 + Phase 4 4 + Phase 4.5 4 + Phase 6 4 + Phase 5 5 + Phase 5.5 4 + Phase 7 5 + Phase 8 5 + Phase 9 6) |

---

## 다음 Phase 옵션 (사용자 결정 대기)

### A. Phase 9.5 — eval-run Skill 정식화 (4~6h)
- golden_set 회귀 + revise effect eval (Phase 4.5 D6 누적 7회 deferred 해소)
- **Critic deprecated 0–5 fallback 완전 제거** (Phase 9 canonical live 활성 → 다음 단계, Phase 6 ADR-018 + Phase 8 + Phase 9 누적 3회)
- 간이 RAG eval_rubric → golden_set 기반 정식 (Phase 7 개선 제안 §6 흡수)
- **eval-design + eval-run Skill 첫 정식 트리거 baseline** (Phase 9 canonical live 활성으로 eval baseline 준비 완료)

### B. Phase 10 — MVP 통합 테스트 (6~8h)
- MVP 전체 end-to-end 검증 (Discovery + Quick → 3-plan → Critic revise (canonical) → save → select → feedback → SSE progress)
- Phase 1~9 누적 baseline 통합 회귀
- **P-AUX-2 brand_memory_extractor agent 실 구현** (Phase 9 schema + 적재 경로 준비 완료 → 데이터 누적 후 활성)
- 배포 테스트 게이트 A~G 준비

### C. 다른 우선순위 (Phase 11+)
- **4계층 full linkage** (plan_options/video_projects — selected_plans 실 plans 정합 → idealized schema 연결, 누적 2회 Phase 5 + Phase 9)
- 사용자 데이터 자동 promotion (rag-update Skill 두 번째 — feedback→candidate pending 적재 완료)
- SSE full async worker (누적 2회 Phase 5 + Phase 8) / prompt A/B 실행 인프라 (multi-provider 대비)
- Supabase SQL function `match_approved_knowledge` 정의 (운영 단계 필수) / cost-review Skill 정식화

---

## 운영 단계 권장

- **P-AUX-2 brand_memory_extractor agent 실 구현** — Phase 10+ (현재 schema + 적재 경로 + 설계 명세만 선 구축, agent 미구현 — 데이터 누적 후 자동 추출 활성, ADR-031)
- **Critic deprecated 0–5 fallback 완전 제거** — Phase 9.5 eval-run 정식화 후 (현재 normalize wiring으로 canonical 0–1 live 활성 + deprecated 0–5 병행 회귀 0 우선, warnings 67→16, NG3)
- **4계층 full linkage** — Phase 11+ (현재 selected_plans 실 plans 정합 plan_id + selected_option_index, idealized plan_options(option_id FK) 연결은 4계층 데이터 모델 본격 활성 시점, NG2)
- **사용자 데이터 자동 promotion** — Phase 10+/11+ (현재 feedback→candidate pending 적재 완료, 자동 승격은 데이터 누적 후 rag-update Skill 두 번째)
- **per-user rate-limit + audit-log** — 운영 단계 (Phase 5 §개선 제안 §5 누적, 피드백 spam 방지)

---

## Phase 9 사용자 결정 1:1 mapping (3건, 2026-05-29 entry 시 명시)

| 결정 ID | 결정 내용 | Phase 9 mapping |
|---|---|---|
| Brand Memory | 준비만 (ADR + schema + 피드백 적재) — P-AUX-2 agent 미구현, 자동 추출 Phase 10+ | ✅ ADR-031 + brand_memory_entries schema + BrandMemoryRepo + feedback→candidate(pending) 적재 경로 + P-AUX-2 설계 명세 (agent 미구현 NG1, 적재 pending NG12) |
| Frontend | 피드백 UI 포함 (wrapper) — 선택/반려 page.tsx inline, PlanCard·component_map 무수정 | ✅ page.tsx inline 선택 버튼 + 반려 이유 textarea + lib/api selectPlan/sendFeedback — PlanCard 0줄 + component_map 0줄 (wrapper, 신규 component 미생성) |
| normalize_to_canonical | Phase 9 연결 — critic step canonical 0–1 live, deprecated 0–5 병행 회귀 0 | ✅ moa_orchestrator critic step wiring (ADR-032) — canonical 0–1 live + deprecated 0–5 병행, additive 비파괴 사본 → 기존 pytest 249 수정 0 (회귀 0), warnings 67→16 |

추가 결정 0건 (entry 시점 3건 명시 → Slice 진행 중 추가 결정 없이 그대로 채택). 실측 발견 1건 (FK 정합 교정: brand_id → brands(id) PK + source_plan_id → plans.id, db_schema idealized plan_options 대신 실 plans 정합 — NG2 정합).

---

## 변경 이력

- 2026-05-31: Phase 9 closing notes 최초 작성 (Slice 6 final). A1~A10 10/10 + M1~M4 4/4 PASS. **결과저장(selected_plans) + 피드백(feedback_events) 영속화 graceful + PII 마스킹 (ADR-030) + normalize_to_canonical wiring (critic_evaluation canonical 0–1 live, deprecated 0–5 병행 회귀 0, ADR-032) + Brand Memory 준비 (feedback→candidate pending 적재, P-AUX-2 agent 미구현 Phase 10+, ADR-031) + 피드백 UI inline (PlanCard·component_map 0줄) + security-review 두 번째 정식 (피드백 PII) + contract-change CC-004 (db_schema.md 실 plans 정합) + P-FEEDBACK-LOOP-001/P-CANONICAL-WIRING-001 신규 후보 + P-X1 42연속 + PlanCard 30연속 + component_map 40연속 + pytest 293/293 + smoke 15/15 + scenario_sim v5 25/25 + P-X2 일곱 번째 자동 게이트**. 다음 phase = 🟡 pending_user_decision (옵션 A Phase 9.5 eval-run / B Phase 10 통합 / C Phase 11+).
