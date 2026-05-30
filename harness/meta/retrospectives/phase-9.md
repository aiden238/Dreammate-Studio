# Phase 9 회고 — 결과 저장 + 피드백 (selected_plans + feedback_events 영속화 + normalize wiring + Brand Memory 준비 + 피드백 UI)

> 종료일: 2026-05-31
> 유형: large phase (10~14h, 6 Slice)
> 총 시간: ~10~13h (실측)
> 결과: ✅ A1~A10 10/10 + M1~M4 4/4 PASS
> 작성자: Claude (Opus 4.8, 1M context)
> 트리거: phase-complete v1.2.0 §1.6 자동 게이트 일곱 번째 + §7 회고 자동 호출

---

## 사실 요약

Phase 9 (결과 저장 + 피드백 — selected_plans / feedback_events 영속화 + normalize_to_canonical wiring + Brand Memory 준비 + 피드백 UI wrapper, large phase)을 **2026-05-29 entry ~ 2026-05-31 close** 구간에 entry부터 archive까지 완수.

진입: Phase 8 회고 §개선 제안 §1 (normalize_to_canonical wiring — Phase 9+ 결과 저장 시점) + §5 (Brand Memory 자동 추출 ADR 신규, 누적 3회 confirm) + Phase 5 §개선 제안 §5 (per-user 누적 인프라) + 사용자 결정 3건 (Brand Memory 준비만 / 피드백 UI 포함 wrapper / normalize wiring Phase 9 연결). entry commit `de92e37`.

6 Slices를 6 Waves로 분해 (모두 sequential + 모두 sub-agent dispatch):
- Wave 1 (Slice 1, `de92e37`) — Pre-Entry: multi-llm-validation formal **여섯 번째** V1~V7 + security-review Skill **두 번째 정식** (피드백 reason PII T1~T6) + ADR-030 (feedback/selection persistence) + ADR-031 (Brand Memory prep — P-AUX-2 설계) + ADR-032 (normalize_to_canonical wiring)
- Wave 2 (Slice 2, `56cd3f0`) — Schema 0005 + Repo graceful: `0005_feedback_selection.sql` (selected_plans + feedback_events + brand_memory_entries + RLS) + selection_repo / feedback_repo / brand_memory_repo (PlansRepo graceful 패턴) + PII 마스킹 + contract-change (db_schema.md, CC-004) + test_selection_feedback.py
- Wave 3 (Slice 3, `d6e3fa0`) — API + normalize wiring: schemas/plans.py (Select/Feedback) + routers/plans.py (POST /select + POST /feedback + GET /feedback) + moa_orchestrator.py critic step `normalize_to_canonical` wiring + test_plans_feedback_api.py + test_critic_canonical_wiring.py. pytest 261→284
- Wave 4 (Slice 4, `bc94e1b`) — Brand Memory 준비: rag/feedback_to_candidate.py (feedback→candidate_knowledge status='pending' 적재 경로) + routers/plans.py candidate enqueue (graceful) + ADR-031 finalize + test_brand_memory_prep.py. pytest 284→293
- Wave 5 (Slice 5, `4d38062`) — Frontend 피드백 UI: apps/web/lib/{types,api}.ts (selectPlan / sendFeedback) + app/plan/[plan_id]/page.tsx inline 선택/반려 UI (PlanCard·component_map 0줄). tsc 0 + build 11 routes
- Wave 6 (Slice 6, final) — Close + 회귀 검증 + smoke 15/15 + scenario_sim v5 25/25 + retrospective + archive + state docs

총 6 sub-agent dispatch (100% sub-agent 패턴, Phase 4.5/6/5/5.5/7/8 정신 계승). 충돌 0건. **§SELF-VERIFICATION 6/6 PASS**.

핵심 회귀 baseline 보존:
- **PlanCard.tsx 0줄 변경 6연속 (Phase 9 Slice 1~6)** → 누적 **30연속** (Phase 4 4 + Phase 4.5 5 + Phase 6 3 + Phase 5 5 + Phase 5.5 1 + Phase 7 1 + Phase 8 5 + Phase 9 6) ★ — frontend slice 있어도 wrapper 패턴으로 0줄
- **component_map.md 0줄 변경 6연속 (Phase 9 Slice 1~6)** → 누적 **40연속** (Phase 2 6 + Phase 3 5 + Phase 4 4 + Phase 4.5 4 + Phase 6 3 + Phase 5 5 + Phase 5.5 1 + Phase 7 1 + Phase 8 5 + Phase 9 6) ★ — page.tsx inline (신규 component 등록 X)
- pytest 249/249 baseline (Phase 8) → **293/293** (+44 신규: test_selection_feedback + test_plans_feedback_api + test_critic_canonical_wiring + test_brand_memory_prep, 기존 249 수정 0 — normalize wiring은 additive Optional)
- smoke_test_phase_9 **15/15** (14 PASS + 1 WARN intended audit_page_component, Phase 8 14 baseline + feedback/selection 1 통합 step 추가)
- scenario_simulation v5 **25/25 PASS** (P-X2 일곱 번째 자동 게이트, S21~S25 신규 feedback/selection 5 추가)
- schema_stress_test **5/5 PASS** (Phase 6 baseline 유지)
- audit_naming **0 drift**
- audit_page_component **2 intended drift WARN** (Phase 5 baseline 계승 — AuthGuard + /login route, 피드백 UI page.tsx inline은 신규 route/component 미생성 → drift 추가 0)
- Phase 1~8 baseline 100% 보호 (normalize wiring additive Optional — critic_evaluation deprecated 0–5 병행 유지 회귀 0)

회고 핵심 발견:
- ★ **P-X1 §SELF-VERIFICATION 42연속 PASS**: Phase 3:5 + Phase 4:4 + Phase 4.5:4 + Phase 6:4 + Phase 5:5 + Phase 5.5:4 + Phase 7:5 + Phase 8:5 + Phase 9:6 = 42 Slice 누적. P-AGENT-SCOPE-001 mitigation **42연속 입증**. Phase 9는 db migration + repo + router + orchestrator + frontend 전 영역을 건드리는 large phase 임에도 0건 재발 — Slice별 폴더/파일 격리 + forbidden 명시로 baseline 침범 0. **frontend slice(Slice 5)에서도 PlanCard·component_map 0줄 유지** (wrapper 패턴).
- ★ **결과 저장 + 피드백 영속화 graceful (ADR-030)**: `selected_plans` (plan_id + selected_option_index 0–2 + selection_reason) + `feedback_events` (event_type like/dislike/reject/regenerate + reason) 를 SelectionRepo / FeedbackRepo로 영속화. **PlansRepo graceful 패턴 (Supabase 실패/미설정 시 in-memory dict)** 계승 — 회귀 0 + testability ↑ (P-GRACEFUL-001 6번째 입증). 피드백 reason 자유 입력은 **저장 전 PII 마스킹** (security-review T1).
- ★ **normalize_to_canonical wiring (ADR-032)**: Phase 8 Slice 4에서 추가된 `normalize_to_canonical` helper(additive, 미연결)를 Phase 9 Slice 3에서 `moa_orchestrator.py` critic step에 실 wiring — `verdict = normalize_to_canonical(run_critic(...))`. **critic_evaluation canonical(overall_score 0–1 + dimensions) live 활성** + deprecated 0–5(scores / overall_score_avg) 병행 유지 (NG3). helper는 **비파괴 사본** 반환 → 기존 pytest 249 수정 0 (회귀 0). deprecated warnings 67→16 감소 (canonical 우선 경로 정착).
- ★ **Brand Memory 준비 (ADR-031)**: 사용자 결정 5 (Phase 5.5+7+8 누적 confirm) — **schema(brand_memory_entries) + BrandMemoryRepo + feedback→candidate_knowledge(source_kind='user_feedback'/'user_choice', status='pending') 적재 경로 + P-AUX-2 brand_memory_extractor 설계 명세**만 선 구축. **agent 실 구현은 Phase 10+ 이관** (NG1). 적재는 pending 상태로만 (자동 승격 X — Phase 7 5단계 정합, NG12).
- ★ **피드백 UI inline wrapper (Slice 5)**: 선택 버튼 + 반려 이유 textarea를 `page.tsx` inline으로 추가 — **PlanCard.tsx 0줄 + component_map.md 0줄** (신규 component 미생성). selectPlan / sendFeedback (credentials include) lib/api.ts wrapper. design.md 정합 (모바일 우선 + 카드 단위 + 한 줄 방향 + wrapper 패턴).
- ★ **security-review Skill 세 번째 사용 (Phase 9 두 번째 정식)**: Phase 5 (entry 첫 정식 + final) 에 이은 — 피드백 reason PII (T1 저장 전 마스킹) + reject 사유(T2) + feedback_events/selected_plans RLS user 격리(T3) + GET /plans/{id}/feedback 권한(T4) + feedback→candidate PII(T5) + SQL injection(T6). **P-SECURITY-REVIEW-001 강화** (보안 영향 phase entry 정식 트리거 패턴, 누적 2 phase).

---

## 데이터

| 항목 | 값 |
|---|---|
| 기간 | 2026-05-29 entry ~ 2026-05-31 close (다중 sub-agent dispatch, 6 Slice sequential) |
| Total commits (Phase 9) | 6 (Slice 1 de92e37 + Slice 2 56cd3f0 + Slice 3 d6e3fa0 + Slice 4 bc94e1b + Slice 5 4d38062 + Slice 6 final) |
| 신규 파일 | ~16 (db/migrations/0005_feedback_selection.sql + db/repositories 3: selection_repo/feedback_repo/brand_memory_repo + schemas/plans.py 확장 + rag/feedback_to_candidate.py + tests 4: test_selection_feedback/test_plans_feedback_api/test_critic_canonical_wiring/test_brand_memory_prep + docs/decisions ADR-030/031/032 3 + meta/validations × 2 + meta/security_reviews 1 + smoke_test_phase_9 + retrospective + closing_notes) |
| 수정 파일 | ~7 (routers/plans.py select/feedback API + candidate enqueue + orchestration/moa_orchestrator.py normalize wiring + db/repositories/__init__ export + rag/__init__ export + apps/web/{lib/types,lib/api,app/plan/[plan_id]/page.tsx} + db_schema.md + scenario_simulation.ps1 v5 + state docs) |
| 줄 수 변화 | +~1700 (backend repo/migration +~600 / tests +~500 / frontend +~200 / docs ADR +~250 / contracts +~80 / meta +~200) |
| 신규 ADR | 3 (ADR-030 feedback/selection persistence + ADR-031 Brand Memory prep + ADR-032 normalize_to_canonical wiring) |
| 변경된 contract | 1 (db_schema.md §4.3 selected_plans + §5.2 feedback_events + brand_memory prep cross-ref) — CC-004 |
| backend db 변경 | 4 신규 (0005 migration + selection_repo + feedback_repo + brand_memory_repo) |
| backend routers 변경 | 1 수정 (plans.py — select/feedback/GET API + candidate enqueue graceful) |
| backend orchestration 변경 | 1 수정 (moa_orchestrator.py — critic step normalize_to_canonical wiring, additive) |
| backend rag 변경 | 1 신규 (feedback_to_candidate.py — feedback→candidate 적재 경로) |
| Frontend 변경 | 3 (lib/types.ts + lib/api.ts + app/plan/[plan_id]/page.tsx inline 피드백 UI — PlanCard 0줄 + component_map 0줄) |
| pytest 결과 | **293/293 PASS** (Phase 8 249 baseline + Phase 9 신규 44) |
| pytest 신규 케이스 | 44 (test_selection_feedback + test_plans_feedback_api + test_critic_canonical_wiring + test_brand_memory_prep 통합 44) |
| 기존 pytest 수정 | 0 (normalize wiring additive Optional — critic_evaluation canonical 추가는 기존 assertion 불침범) |
| audit_naming | 0 drift |
| audit_page_component | 2 intended drift WARN (Phase 5 baseline 계승, AuthGuard + /login — 피드백 UI page.tsx inline은 신규 route/component 미생성 → +0) |
| smoke_test_phase_9 | **15/15** (14 PASS + 1 WARN intended) |
| scenario_simulation v5 | **25/25 PASS** (P-X2 일곱 번째 자동 게이트, S21~S25 추가) |
| schema_stress_test | 5/5 PASS (Phase 6 v2 유지) |
| deprecated critic warnings | 67 → 16 (normalize wiring canonical 우선 경로 정착) |
| Sub-agent dispatch | 6 (Slice 1~6 모두) |
| **P-X1 §SELF-VERIFICATION** | **6/6 PASS (Phase 9)** ★ |
| **P-X1 누적 streak** | **42연속 (Phase 3 5 + Phase 4 4 + Phase 4.5 4 + Phase 6 4 + Phase 5 5 + Phase 5.5 4 + Phase 7 5 + Phase 8 5 + Phase 9 6)** ★ |
| **PlanCard.tsx deviation** | **0건 (Phase 9 전체, 누적 30연속 — frontend slice 있어도 wrapper)** ★ |
| **component_map.md deviation** | **0건 (Phase 9 전체, 누적 40연속 — page.tsx inline)** ★ |
| 사용 Skill (Phase 9) | 11 (phase-start v1.3.0 열한 번째 + qa-check + multi-llm-validation formal 여섯 번째 + **security-review 두 번째 정식 (Slice 1)** + contract-change CC-004 (Slice 2) + agent-io-check 다섯 번째 (Slice 3 + Slice 6) + harness-audit (Slice 6) + design-review 아홉 번째 §B (Slice 6) + meta-retrospective (Slice 6) + phase-complete v1.2.0 일곱 번째 (Slice 6)) |
| 식별된 P-pattern (Phase 9 신규) | 2 신규 (P-FEEDBACK-LOOP-001 + P-CANONICAL-WIRING-001) + 2 update (P-X1-EFFECT-001 42연속 + P-VALIDATION-FORMAL-001 여섯 번째 입증) |
| Phase 9 deferred → Phase 9.5+/10+/11+ 이관 | P-AUX-2 brand_memory_extractor agent 실 구현 (Phase 10+) / Critic deprecated 0–5 완전 제거 (Phase 9.5 eval-run) / 4계층 full linkage plan_options (Phase 11+) / eval-run 정식화 (Phase 9.5) |
| 시간 추정 vs 실측 | 10~14h (multi_slice_plan) → 실측 ~10~13h (다중 sub-agent) |

---

## Acceptance 결과 (A1~A10 + M1~M4)

| ID | 항목 | 결과 |
|---|---|---|
| A1 | `selected_plans` schema (0005 migration, 실 plans 정합 option_index 0–2) | ✅ 0005_feedback_selection.sql + ADR-030 |
| A2 | SelectionRepo graceful (select/get, in-memory fallback) | ✅ test_selection_feedback.py |
| A3 | `feedback_events` + FeedbackRepo (like/dislike/reject/regenerate + reason) | ✅ test_selection_feedback.py |
| A4 | API — POST /plans/{id}/select + /feedback + GET /plans/{id}/feedback | ✅ test_plans_feedback_api.py |
| A5 | orchestrator/plans 정합 (회귀 0) | ✅ 기존 pytest 249 수정 0 PASS |
| A6 | normalize_to_canonical wiring — critic_evaluation canonical(0–1) 저장 (deprecated 0–5 병행) | ✅ test_critic_canonical_wiring.py + agent-io-check drift 0 |
| A7 | Brand Memory 준비 — brand_memory_entries schema + BrandMemoryRepo + feedback→candidate 적재 + ADR-031 | ✅ test_brand_memory_prep.py + ADR-031 |
| A8 | 피드백 UI wrapper — 선택/반려 (page.tsx inline) + PlanCard·component_map 0줄 | ✅ next build 11 routes + tsc 0 + lint + git diff 0줄 |
| A9 | audit_naming 0 drift + audit_page_component 2 intended WARN | ✅ |
| A10 | smoke_test_phase_9 15/15 + scenario_sim v5 25/25 | ✅ (smoke 14 PASS + 1 WARN intended) |
| M1 | multi-llm-validation formal self V1~V7 + external placeholder (여섯 번째) | ✅ |
| M2 | security-review Skill 두 번째 정식 (피드백 reason PII + reject 사유) | ✅ |
| M3 | contract-change Skill (db_schema.md feedback/selection 정식 — 실 plans 정합) | ✅ CC-004 |
| M4 | P-X1 §SELF-VERIFICATION 42연속 PASS (Slice 1~6 모두) | ✅ (6/6 Phase 9) |

---

## 분석

### 잘된 것

1. **★ 결과 저장 + 피드백 영속화 graceful (ADR-030) — PlansRepo 패턴 6번째 입증**: `selected_plans` + `feedback_events` 를 SelectionRepo / FeedbackRepo 로 영속화하되 **Supabase 실패/미설정 시 in-memory dict fallback** (Phase 5 PlansRepo 패턴 계승). 응답 200 + graceful → 개발 환경에서 Supabase 없이도 동작 + testability ↑ (pytest mock 자동화). P-GRACEFUL-001 (Phase 1) 정신 6번째 입증.

2. **★ normalize_to_canonical wiring (ADR-032) — Phase 8 helper → live pipeline 연결 (additive 회귀 0)**: Phase 8 §개선 제안 §1 (helper 미연결) 해소. `moa_orchestrator.py` critic step에서 `verdict = normalize_to_canonical(run_critic(...))` 로 wiring → critic_evaluation canonical(0–1) **live 활성**. 핵심: helper가 **비파괴 사본** 반환 → deprecated 0–5 병행 유지 + 기존 pytest 249 수정 0 (additive Optional). deprecated warnings 67→16 감소 (canonical 우선 경로 정착). P-BEHAVIOR-PRESERVING-001 (Phase 8) 정신 — additive helper 우선.

3. **★ Brand Memory 준비 경계 정확 준수 (ADR-031) — schema + 적재 경로만, agent 미구현**: 사용자 결정 5 (준비만) 정확 구현 — brand_memory_entries schema + BrandMemoryRepo + feedback→candidate(status='pending') 적재 경로 + P-AUX-2 설계 명세만 선 구축. **agent 실 구현은 Phase 10+ 이관** (NG1). 적재는 pending 상태로만 (자동 승격 X — Phase 7 5단계 정합 NG12). over-engineering 회피 + 인프라 선구축 동시 달성.

4. **★ 피드백 UI inline wrapper (Slice 5) — frontend slice에서도 PlanCard·component_map 0줄**: 선택 버튼 + 반려 이유 textarea를 page.tsx inline으로 추가하되 **PlanCard.tsx 0줄 + component_map.md 0줄** (신규 component 미생성). Phase 4~8은 backend-only라 frontend 0줄이 자연스러웠으나, **Phase 9는 실제 frontend 작업이 있는 slice에서도 wrapper 패턴으로 baseline 보호** — P-X1 + 사용자 결정 6-a 정신의 frontend 확장 입증.

5. **★ security-review Skill 세 번째 사용 (Phase 9 두 번째 정식) — P-SECURITY-REVIEW-001 강화**: Phase 5 (entry 첫 정식 + final) 에 이은 보안 영향 phase entry 정식 트리거. 피드백 reason PII (T1 저장 전 마스킹) + RLS user 격리(T3) + GET 권한(T4) + candidate PII(T5). 보안 영향 phase entry 패턴 누적 2 phase → 정식 채택 임박.

6. **★ pytest 249 → 293 (+44 신규) + 기존 수정 0**: test_selection_feedback (graceful CRUD + PII 마스킹 + in-memory fallback) + test_plans_feedback_api (select/feedback/GET endpoint + RLS) + test_critic_canonical_wiring (normalize wiring canonical 0–1 + deprecated 0–5 병행) + test_brand_memory_prep (feedback→candidate 적재 + brand_memory_repo). **normalize wiring은 additive Optional → 기존 249 수정 0** (회귀 0).

7. **★ P-X1 42연속 PASS — 6 Slice 모두 sub-agent + 충돌 0건**: Phase 9는 db migration + repo + router + orchestrator + frontend 전 영역을 건드리는 large phase 임에도 6 Slice 모두 sub-agent dispatch. Slice별 폴더/파일 격리 + forbidden 명시로 baseline 침범 0. P-AGENT-SCOPE-001 mitigation **42연속 누적 입증**.

8. **★ smoke 15/15 + scenario_sim v5 25/25 (P-X2 일곱 번째 자동 게이트)**: Phase 8 14 baseline + feedback/selection 통합 step → 15/15 (14 PASS + 1 WARN intended). v4 20 baseline + feedback/selection 5 (S21~S25) 추가 → 25/25.

9. **★ contract-change CC-004 — db_schema.md 실 plans 정합**: db_schema.md §4.3 selected_plans (plan_id + selected_option_index 0–2 + selection_reason — 실 plans 테이블 정합, idealized plan_options Phase 11+ NG2) + §5.2 feedback_events 보강 + brand_memory prep cross-ref. P-CONTRACT-FIRST-001 누적 5회.

10. **★ FK 정합 교정 (실측 발견)**: 0005 migration에서 brand_memory_entries.brand_id → **brands(id)** (실 0001_init.sql PK), source_plan_id → plans.id (실 plans 정합). db_schema idealized plan_options(selected_plans→plan_options.option_id) 대신 **실 plans 테이블 정합** (plan_id + selected_option_index). 4계층 full linkage는 Phase 11+ (NG2).

### 안 된 것

1. **P-AUX-2 brand_memory_extractor agent 미구현**: 사용자 결정 5 (준비만) — schema + 적재 경로 + 설계 명세만 선 구축, agent 실 구현은 Phase 10+. 적재는 pending 상태로만 (자동 승격 X). → 개선 제안 §1.

2. **Critic deprecated 0–5 fallback 잔존**: normalize wiring으로 canonical 0–1 live 활성했으나 deprecated 0–5(scores / overall_score_avg) 병행 유지 (NG3, 회귀 0 우선). 완전 제거는 Phase 9.5 eval-run 정식화 후 (Phase 6 ADR-018 + Phase 8 누적 3회). → 개선 제안 §2.

3. **4계층 full linkage 미연결**: selected_plans는 실 plans 테이블 정합 (plan_id + selected_option_index). db_schema idealized plan_options(option_id FK) 연결은 Phase 11+ 4계층 full linkage (NG2). 실 plans 정합으로 우선 동작 + idealized schema는 운영 단계 후 점진 연결. → 개선 제안 §3.

4. **eval-run 미실행**: Critic canonical live 활성으로 eval baseline은 준비됐으나 eval-run Skill 정식화는 Phase 9.5 (개선 제안 §2와 동시). → 개선 제안 §4.

### 배운 것

1. **피드백 영속 graceful + PII 마스킹 패턴 (P-FEEDBACK-LOOP-001)**: 사용자 선택/피드백을 영속화할 때 (1) PlansRepo graceful (Supabase 실패 시 in-memory) + (2) reason 자유 입력 저장 전 PII 마스킹 + (3) RLS user 격리 + (4) candidate 적재는 pending 상태로만 (자동 승격 X) 4종 조합. P-GRACEFUL-001 + P-RLS-001 + P-RAG-5STAGE-001(pending) 정신 통합.

2. **Phase N helper → live pipeline wiring 패턴 (P-CANONICAL-WIRING-001)**: 이전 phase에서 additive로 추가한 helper(미연결)를 후속 phase에서 live pipeline에 wiring할 때 — (1) helper는 비파괴 사본 반환 + (2) deprecated 병행 유지 + (3) additive Optional → 기존 test 수정 0 (회귀 0). Phase 8 normalize_to_canonical helper → Phase 9 orchestrator wiring 첫 적용.

3. **frontend slice에서도 wrapper로 baseline 0줄 보호**: backend-only가 아닌 실 frontend 작업 slice에서도 page.tsx inline + lib/api wrapper 패턴으로 PlanCard·component_map 0줄 유지 가능. 신규 component 미생성 = component_map drift +0 + audit_page_component WARN 추가 0. P-X1의 frontend 확장.

4. **실 schema 정합 vs idealized schema 분리**: db_schema.md는 idealized 4계층 (plan_options.option_id) 정의이나, 실 구현은 plans 테이블 + plan_candidates JSONB + option_index(0–2). Phase 9는 **실 plans 정합** 우선 (NG2) — idealized full linkage는 운영 단계 후 점진. 실측 발견 = FK 교정 (brands(id) PK + plans.id).

5. **large phase 10~13h 실측 효과 누적**: Phase 5 (~14~16h) → Phase 7 (~13~14h) → Phase 8 (~12~14h) → Phase 9 (~10~13h). feedback/selection 같은 CRUD-heavy + frontend wrapper phase도 표준 범위. Slice별 명확한 forbidden + graceful 패턴 재사용으로 시간 절감.

### 근본 원인 (해당 없음 — 본 phase deviation 0건)

Phase 4.5/6/5/5.5/7/8처럼 deviations 0건. P-X1 42연속 PASS로 forbidden 영역 침범 0건 — root cause 분석 불요.

발견 1 (FK 정합 교정): 0005 migration 작성 시 brand_memory_entries.brand_id → brands(id) (실 0001_init.sql PK 정합) + source_plan_id → plans.id. db_schema idealized plan_options(option_id) 대신 실 plans 테이블 정합 (plan_id + selected_option_index). **수용 가능 — NG2 (4계층 full linkage Phase 11+) 정합.**

발견 2 (의도 없는 baseline delta 0건): normalize wiring은 additive Optional (helper 비파괴 사본) → 기존 pytest 249 수정 0. Phase 8 (의도된 2 version assertion 갱신) 과 달리 **Phase 9는 baseline test delta 0건** — wiring이 출력 의미를 바꾸지 않음(canonical 추가, deprecated 병행).

audit_page_component WARN 2 drift는 **의도된** Phase 5 baseline (AuthGuard component + /login route) — Phase 9 피드백 UI는 page.tsx inline (신규 route/component 미생성) → drift 추가 0. phase-complete v1.2.0 §1.6 WARN 허용 (FAIL 아님), `phase_9_audit_page_component_intended_drift` 사유 Phase 5 baseline 계승 명시.

### 부가 발견 사항 (개선 후보)

| 항목 | 영향 | 빈도 | 분류 |
|---|---|---|---|
| P-AUX-2 brand_memory_extractor agent 실 구현 | 보통 (Brand Memory 자동 추출 활성) | 1회 (Phase 9 준비 완료) | Phase 10+ |
| Critic deprecated 0–5 fallback 완전 제거 | 작음 (canonical live 활성) | 누적 3회 (Phase 6 + Phase 8 + Phase 9) | Phase 9.5 eval-run |
| 4계층 full linkage (plan_options/video_projects) | 보통 (idealized schema 연결) | 누적 2회 (Phase 5 + Phase 9) | Phase 11+ |
| eval-run 정식화 | 보통 (canonical baseline 준비됨) | 누적 7회 (Phase 4.5~9) | Phase 9.5 |
| SSE full async worker | 작음 | 누적 2회 (Phase 5 + Phase 8) | Phase 11+ |
| 사용자 데이터 자동 promotion (rag-update 두 번째) | 작음 (feedback→candidate pending 적재 완료) | 1회 (Phase 9) | Phase 10+/11+ |

---

## 개선 제안

### 개선 제안 1 (우선순위: ↑): P-AUX-2 brand_memory_extractor agent 실 구현 — Phase 10+

- **무엇을**: feedback_events / selected_plans 누적 데이터 → brand_memory_entries 자동 추출하는 P-AUX-2 brand_memory_extractor agent 실 구현.
- **왜**: Phase 9에서 schema + 적재 경로 + 설계 명세만 선 구축 (ADR-031). 사용자 결정 5 (준비만, agent Phase 10+). MVP 통합 + 데이터 누적 후 활성.
- **어디에**: `backend/fastapi/agents/brand_memory_extractor.py` 신규 + ADR-031 §활성화 조건
- **상태**: Phase 10+ MVP 통합 테스트 후 (데이터 누적 시점)

### 개선 제안 2 (우선순위: ↑): Critic deprecated 0–5 fallback 완전 제거 — Phase 9.5

- **무엇을**: normalize wiring으로 canonical 0–1 live 활성 완료 → deprecated 0–5(scores / overall_score_avg) fallback 완전 제거 + canonical 단일화.
- **왜**: Phase 6 ADR-018 (canonical + deprecated 단계적 축소) 다음 단계 누적 3회 (Phase 6 + Phase 8 + Phase 9). Phase 9에서 canonical live 활성 + warnings 67→16 → eval-run 정식화 후 완전 제거 조건 충족.
- **어디에**: `backend/fastapi/agents/critic.py` + `output_schema.md §9` + 별도 contract-change 절차
- **상태**: Phase 9.5 eval-run Skill 정식화 시점 (revise effect eval + 간이 RAG eval_rubric 정식화와 동시)

### 개선 제안 3 (우선순위: 보통): 4계층 full linkage (plan_options/video_projects) — Phase 11+

- **무엇을**: selected_plans 실 plans 정합(plan_id + selected_option_index) → db_schema idealized plan_options(option_id FK) + video_projects 4계층 full linkage.
- **왜**: Phase 9는 실 plans 테이블 정합 우선 (NG2). idealized 4계층 schema 연결은 운영 단계 + 4계층 데이터 모델 본격 활성 시점.
- **어디에**: `db/migrations/` 신규 (plan_options 테이블 + FK) + `db_schema.md §4` linkage 정식
- **상태**: Phase 11+ 4계층 데이터 모델 본격 활성 (누적 2회 Phase 5 + Phase 9)

### 개선 제안 4 (우선순위: ↑): eval-run Skill 정식화 — Phase 9.5

- **무엇을**: golden_set 회귀 + revise effect eval + Critic canonical 기반 정식 eval + 간이 RAG eval_rubric → golden_set 기반 정식.
- **왜**: Phase 9 normalize wiring으로 critic canonical 0–1 live 활성 → eval baseline 준비 완료. Phase 4.5 D6 revise effect eval deferred 누적 7회 (Phase 4.5~9). eval-design + eval-run Skill 첫 정식 트리거 baseline.
- **어디에**: `eval/golden_set.md` + `eval/video_planning_eval.md` + eval-run Skill
- **상태**: Phase 9.5 (개선 제안 §2와 동시 — Critic deprecated 완전 제거)

### 개선 제안 5 (우선순위: 보통): 사용자 데이터 자동 promotion (rag-update 두 번째) — Phase 10+/11+

- **무엇을**: feedback→candidate_knowledge(pending) 적재 데이터 → 5단계 파이프라인 자동 promotion (rag-update Skill 두 번째 트리거).
- **왜**: Phase 9에서 feedback→candidate pending 적재 경로 완료 (ADR-031). 데이터 누적 후 자동 승격 활성 (Phase 7 5단계 정합).
- **어디에**: `backend/fastapi/rag/promotion.py` + rag-update Skill (ADR-024 §A 확대 지점)
- **상태**: Phase 10+/11+ 데이터 누적 시점 (rag-update Skill 두 번째 정식)

---

## 패턴 등록 (meta/patterns.md 갱신)

| 패턴 ID | 설명 | 관련 회고 | 상태 |
|---|---|---|---|
| **P-X1-EFFECT-001** (update) | P-X1 §SELF-VERIFICATION **42연속 PASS** 효과 누적 측정 (Phase 3 5 + Phase 4 4 + Phase 4.5 4 + Phase 6 4 + Phase 5 5 + Phase 5.5 4 + Phase 7 5 + Phase 8 5 + Phase 9 6) | phase-3 + ... + phase-9 | 갱신 (Phase 9) — frontend slice 있어도 wrapper로 PlanCard 30연속 + component_map 40연속 |
| **P-FEEDBACK-LOOP-001** (신규) | 피드백 영속 graceful + PII 마스킹 (PlansRepo graceful + reason 저장 전 PII 마스킹 + RLS user 격리 + candidate 적재 pending 상태) | phase-9 | 신규 등록 후보 (Phase 9 첫 적용, Phase 10+ Brand Memory agent 활성 시점 효과 재측정) |
| **P-CANONICAL-WIRING-001** (신규) | Phase N helper → live pipeline wiring (helper 비파괴 사본 + deprecated 병행 + additive Optional → 기존 test 수정 0 회귀 0) — Phase 8 normalize_to_canonical helper → Phase 9 orchestrator wiring | phase-9 | 신규 등록 후보 (Phase 9 첫 적용, Phase 9.5 deprecated 완전 제거 시점 효과 재측정) |
| **P-VALIDATION-FORMAL-001** (update) | multi-llm-validation formal self + 외부 분리 패턴 — Phase 4.5/6/5/7/8/9 = 여섯 번째 입증 | phase-4.5 + ... + phase-9 | 갱신 (Phase 9 여섯 번째 입증 — V7 selection/feedback + normalize wiring + Brand Memory 준비) |

→ Phase 1~9 누적 패턴:
- P-DRIFT-001 (mitigated) / P-SLICE-001 / P-GRACEFUL-001 (Phase 9 6번째 입증 — feedback graceful) / P-FOLDER-PARALLEL-001 / P-AGENT-SCOPE-001 (mitigated by P-X1, **42연속 입증**) / P-DESIGN-LAYERED-001 / P-X1-EFFECT-001 (update **42연속**) / P-THIN-VERTICAL-001 / P-GPT-REVIEW-001 / P-X2-EFFECT-001 (Phase 9 일곱 번째 자동 게이트) / P-VALIDATION-FORMAL-001 (Phase 9 여섯 번째 입증) / P-CRITIC-CANONICAL-001 (Phase 9 normalize wiring으로 canonical live 활성) / P-CONTRACT-FIRST-001 (Phase 9 CC-004 누적 5회) / P-RLS-001 (Phase 9 feedback/selection RLS) / P-SSE-001 / P-SECURITY-REVIEW-001 (Phase 9 두 번째 정식 — 강화) / P-LEGACY-CONSOLIDATION-001 / P-RAG-5STAGE-001 (Phase 9 candidate pending 적재 정합) / P-RAG-GRACEFUL-001 / P-MOA-ORCHESTRATOR-001 (Phase 9 orchestrator 확장 — normalize wiring) / P-BEHAVIOR-PRESERVING-001 (Phase 9 additive wiring 회귀 0) / **P-FEEDBACK-LOOP-001 (Phase 9 신규 후보)** / **P-CANONICAL-WIRING-001 (Phase 9 신규 후보)** — 모두 효과 유지

---

## Skill 사용 로그 (Phase 9 동안)

| Skill | Phase 9 사용 횟수 | 비고 |
|---|---|---|
| phase-start (v1.3.0) | 1 | Phase 9 entry, 4점검 PASS (Slice 1) — 누적 11번째 |
| qa-check (v1.2.0) | 1 | Slice 1 entry 시 호출 |
| multi-llm-validation | 1 (formal 여섯 번째) | Slice 1 V1~V7 PASS (selection/feedback 실 plans 정합 / normalize wiring 회귀 0 / Brand Memory 준비 경계 / 피드백 reason PII / repo graceful / 피드백 UI wrapper / feedback→candidate 적재) |
| **security-review** | **1 (Phase 9 두 번째 정식)** | Slice 1 — 피드백 reason PII (T1 저장 전 마스킹) + reject 사유(T2) + feedback_events/selected_plans RLS(T3) + GET 권한(T4) + candidate PII(T5) + SQL injection(T6). P-SECURITY-REVIEW-001 강화 (보안 영향 phase entry 패턴 누적 2 phase) |
| contract-change | 1 (CC-004) | Slice 2 — db_schema.md §4.3 selected_plans + §5.2 feedback_events + brand_memory prep cross-ref (실 plans 정합). 회귀 0. P-CONTRACT-FIRST-001 누적 5회 |
| agent-io-check | 1 (다섯 번째) | Slice 3 normalize wiring 정합 + Slice 6 회귀 — agent_io_contract §5 Critic v1.1.0 adapter ↔ critic.py + orchestrator wiring drift 0 |
| harness-audit | 1 | Slice 6 audit_naming + audit_page_component 자동 호출 (0 drift + 2 intended WARN 유지) |
| design-review | 1 (impl §B 아홉 번째) | Slice 6 — 피드백 UI page.tsx inline 검증 (PlanCard 30연속 + component_map 40연속 무수정 + design.md 정합) |
| meta-retrospective | 1 (지금) | 본 문서 |
| phase-complete (v1.2.0) | 1 | Phase 9 종료 (v1.2.0 §1.6 **일곱 번째** 자동 게이트, scenario_simulation v5 25/25 PASS) |
| 기타 unused (의도된) | — | rag-design / rag-update (Phase 7 완료, 적재 경로만 신규 — Skill 절차 비호출) / eval-run / eval-design (Phase 9.5+) / ai-architecture-review / prompt-version-review (Phase 8 완료, Phase 9 변경 0) / context-compact / phase-review / bug-triage / cost-review (불요) |

**Phase 9 사용 요약**: 11 Skill 활용 (phase-start v1.3.0 + qa-check + multi-llm-validation formal 여섯 번째 + **security-review 두 번째 정식** (Slice 1) + contract-change CC-004 (Slice 2) + agent-io-check 다섯 번째 (Slice 3 + Slice 6) + harness-audit (Slice 6) + design-review 아홉 번째 §B (Slice 6) + meta-retrospective (Slice 6) + phase-complete v1.2.0 일곱 번째 자동 게이트 (Slice 6)). Phase 1~9 누적 = **16 Skill 활성화**, 4 unused. **security-review 두 번째 정식 트리거** (P-SECURITY-REVIEW-001 강화 — 보안 영향 phase entry 패턴 누적 2 phase).

---

## 다음 액션

```
- [x] 본 회고 문서 작성 완료
- [x] meta/patterns.md update (P-X1-EFFECT-001 42연속 + P-FEEDBACK-LOOP-001 신규 + P-CANONICAL-WIRING-001 신규 + P-VALIDATION-FORMAL-001 여섯 번째)
- [x] meta/skill_usage_log.md 갱신 (Phase 9 사용 요약 11 Skill — security-review 두 번째 정식 + contract-change CC-004)
- [x] phases/active/phase-9-* → phases/archive 이동
- [x] closing_notes.md 작성 (Phase 9 baseline + 다음 옵션 A/B/C + 운영 권장)
- [x] PROJECT_STATE / PHASE_REGISTRY / 00_START_HERE / README 갱신
- [ ] 다음 phase 사용자 결정 대기 (A Phase 9.5 eval-run / B Phase 10 통합 / C Phase 11+)
```

---

## 다음 phase 옵션 (사용자 결정 대기)

### A. Phase 9.5 — eval-run Skill 정식화 (4~6h)
- golden_set 회귀 + revise effect eval (Phase 4.5 D6 누적 7회 deferred 해소)
- Critic deprecated 0–5 fallback 완전 제거 (개선 제안 §2, Phase 6 ADR-018 + Phase 8 + Phase 9 누적 3회)
- 간이 RAG eval_rubric → golden_set 기반 정식 (Phase 7 개선 제안 §6 흡수)
- eval-design + eval-run Skill 첫 정식 트리거 baseline (Phase 9 canonical live 활성으로 eval baseline 준비 완료)

### B. Phase 10 — MVP 통합 테스트 (6~8h)
- MVP 전체 end-to-end 검증 (Discovery + Quick → 3-plan → Critic revise (canonical) → save → select → feedback → SSE progress)
- Phase 1~9 누적 baseline 통합 회귀
- P-AUX-2 brand_memory_extractor agent 실 구현 (개선 제안 §1 — 데이터 누적 후)
- 배포 테스트 게이트 A~G 준비

### C. 다른 우선순위 (Phase 11+)
- 4계층 full linkage (plan_options/video_projects, 개선 제안 §3, 누적 2회)
- 사용자 데이터 자동 promotion (rag-update Skill 두 번째, 개선 제안 §5)
- SSE full async worker (누적 2회 Phase 5 + Phase 8) / prompt A/B 실행 인프라 (multi-provider 대비)
- Supabase SQL function 정의 (운영 단계 필수) / cost-review Skill 정식화

---

## 변경 이력

- 2026-05-31: Phase 9 회고 최초 작성 (phase-complete v1.2.0 §1.6 일곱 번째 자동 게이트 + §7 회고 자동 호출). **P-X1-EFFECT-001 update (42연속) + P-FEEDBACK-LOOP-001 신규 + P-CANONICAL-WIRING-001 신규 + P-VALIDATION-FORMAL-001 update (여섯 번째) 패턴 등록**. P-AGENT-SCOPE-001 mitigation 42/42 입증. **security-review Skill 두 번째 정식 트리거 (피드백 PII) + contract-change CC-004 (db_schema.md feedback/selection 실 plans 정합) + 결과저장(selected_plans) + 피드백(feedback_events) 영속화 graceful + PII 마스킹 (ADR-030) + normalize_to_canonical wiring (critic_evaluation canonical 0–1 live, deprecated 0–5 병행 회귀 0, ADR-032) + Brand Memory 준비 (feedback→candidate pending 적재, P-AUX-2 agent 미구현 Phase 10+, ADR-031) + 피드백 UI inline (PlanCard·component_map 0줄)**. pytest 249→293 (+44, 기존 수정 0) / smoke 14→15 / scenario_sim v4 20→v5 25. 다음 phase = 🟡 pending_user_decision (옵션 A Phase 9.5 eval-run / B Phase 10 통합 / C Phase 11+).
