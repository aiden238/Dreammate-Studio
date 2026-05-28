# Phase 4 — Closing Notes

> 작성: 2026-05-28 (phase-complete v1.1.0 절차 1단계)
> 결정: **정상 종료 (acceptance A1~A10 10/10 PASS · backend+frontend phase · P-X1 9연속 PASS · component_map 15연속 0줄 · PlanCard 4연속 0줄)**

---

## 1. Acceptance 확인 결과

| ID | 항목 | 상태 | 근거 |
|---|---|---|---|
| A1 | Contract Endpoints 4개 동작 | PASS | Slice 1+2 — POST /plans/start + wizard/{step} + /generate + GET /plans/{id} 모두 200 + Pydantic 응답 / test_plans.py 15 + test_3_plan.py 16 = 31 신규 테스트 PASS |
| A2 | 3-plan Generation (multi-model 가능 구조) | PASS | Slice 2 — body.plan_candidates length=3 + approach_label unique + config.py openai_models_for_3plan list (default 3) + ADR-015 multi-model 명시 |
| A3 | Critic verdict 노출 | PASS | Slice 2 — critic_evaluation 8 scores 정상 + overall_verdict 노출 + revise_round = 0 (D6 Phase 4.5+ 이관) |
| A4 | Phase 1 endpoint 회귀 0 | PASS | Slice 1 — POST /api/v1/generate 200 + 1 plan + X-API-Deprecation: Phase 4 header / test_e2e_slice1 19개 회귀 0 |
| A5 | Phase 3 frontend 회귀 0 | PASS | next build 11 routes / `/new` Mode Branching + Discovery 7-step + Quick 4-step 모두 OK |
| A6 | Frontend Phase 4 페이지 | PASS | Slice 3 — `/plan/[plan_id]` 라우팅 + PlanCard × 3 세로 스택 + 1 선택 highlight + **PlanCard.tsx 무변경 (조정 6-a)** ★ |
| A7 | pytest + build 회귀 0 | PASS | pytest 93/93 (62 baseline + 31 신규) / next build 11 routes / tsc 0 / lint clean |
| A8 | audit 자동 도구 0 drift | PASS | audit_naming 0 + audit_page_component 0 (Slice 4 D-1 해소) + smoke_test_phase_4 8/8 PASS |
| A9 | 변경성 시뮬레이션 5/5 회귀 + component_map.md 0줄 | PASS | 4 PASS + 1 WARN (Phase 3 결과 유지, Phase 4 +0 영향) + component_map.md **15연속 0줄** + §SELF-VERIFICATION **4/4 PASS** |
| A10 | retrospective + 다음 phase 결정 | PASS | retrospectives/phase-4.md 작성 + P-X1 9연속 측정 + **다음 phase A/B/C 옵션 명시 (사용자 결정 3-c)** + D6/D7/D8/D3/D4/D2/Phase 1 endpoint 제거 모두 deferred 명시 |

**A1~A10 10/10 PASS · 정상 종료.**

---

## 2. 강제 종료 / 이월 결정

```
결정: 정상 종료 (acceptance 10/10 PASS, audit_naming + audit_page_component 0 drift,
       변경성 4/5+1 WARN, P-X1 9/9 PASS, component_map 15연속 0줄, PlanCard 4연속 0줄,
       smoke 8/8 PASS, GPT 검토 채택 효과 6→4 Slices + ▼66% 시간)
이월 항목: D6 / D7 / D8 / D3 / D4 / D2 / Phase 1 endpoint 제거 (Phase 4.5+/5+/8+/9+ 인수)
완료 항목: D-1 (audit_page_component.ps1 Phase 4 정규화 — Slice 4 완료)
```

### 이월 항목 (다음 phase 인수)

| ID | 항목 | 권장 처리 시점 |
|---|---|---|
| **D6** | Critic revise loop + Rewriter (P-008) | Phase 4.5 mini-phase 또는 Phase 6 |
| **D7** | SSE Progress streaming | Phase 5 (Auth/RLS와 함께) |
| **D8** | PlanComparisonCard 본격 4-layer | Phase 5+ |
| **D3** (Phase 3 인수) | PlanCard 4-layer 재정의 | Phase 5+ (D4와 함께, 조정 3번 정합) |
| **D4** (Phase 3 인수) | PlanComparisonCard 상세 spec | Phase 5+ |
| **D2** (Phase 3 인수) | QuickInputCard alt variants | Phase 9 (사용자 데이터 누적 후) |
| **Phase 1 endpoint 제거** | 사용자 결정 5-a | Phase 8+ (마이그 완료 후) |
| **D-1** | `/plan/[plan_id]` audit 정규화 | **✅ Slice 4 완료 (audit_page_component.ps1 Phase 4 정규화 case 추가)** |

### D1 (Step 2~7 wireframe) — Phase 11+ 처리 권장 (Phase 3 인수 유지)

Phase 11+ design review 시점에 보강 권장.

---

## 3. 다음 Phase 옵션 (사용자 결정 3-c) ★

retrospectives/phase-4.md §다음 phase 진입 권장 사항 + 본 §3에서 동일 명시. 사용자가 셋 중 선택.

### 옵션 A: Phase 4.5 mini-phase (Critic revise loop + Rewriter)

```
산출물:
  - D6 본격 구현 (P-008 Rewriter)
  - Critic revise 최대 2회 (overall_verdict='revise'시 P-008 호출)
  - revise_round 0/1/2 노출
  - 최종 응답 verdict approve|reject 강제
추정 시간: 8~12h
Acceptance:
  - Critic verdict 'revise'시 P-008 호출 → 갱신된 plan_candidates
  - revise_round 최대 2 (무한 루프 차단, 사용자 결정 5 정합)
  - 최종 응답 verdict 항상 approve|reject (revise 없음)
의존성: Phase 4 4 endpoints + P-007 Critic + P-008 placeholder
다음 → Phase 5 (DB/Auth + SSE)
권장 시점: 사용자가 영상기획 품질 안정화를 우선시할 때
```

### 옵션 B: Phase 5 DB/Auth (Critic revise는 Phase 6+)

```
산출물:
  - Supabase Auth + RLS
  - plan_store DB migration (in-memory → Supabase row)
  - SSE Progress streaming (D7)
  - 사용자 세션 인증 + plan_id 권한 검증
추정 시간: 15~20h
Acceptance:
  - 다중 사용자 + plan_id 권한 분리
  - SSE Progress 30~60초 대기 UX 활성화
  - Critic revise는 Phase 6+ 통합
의존성: Phase 4 contract endpoints (DB 이관) + Supabase 프로비저닝
다음 → Phase 6 (Output Schema + Agent IO 안정화 + Critic revise loop 통합)
권장 시점: 사용자가 다중 사용자 데이터 누적 + 보안 우선시할 때
```

### 옵션 C: 다른 우선순위 (사용자 시점 재평가)

```
가능 후보:
  - Phase 6 Output Schema (P-006/P-007/P-008 안정화 + agent_io 통합)
  - Phase 9 결과 저장 + Brand Memory 자동 추출 (UX 데이터 베이스)
  - Phase 11+ 안정화 (eval / cost / UX 검증)
추정 시간: 시점에 따라
권장 시점: 사용자가 본 Phase 4 산출물 실 사용 + 데이터 누적 후 우선순위 재평가
```

---

## 4. 다음 Phase로 가져갈 학습 / 컨텍스트

`meta/retrospectives/phase-4.md`에 통합 작성됨. 핵심:

- ★ **P-X1-EFFECT-001 (update 9연속)**: P-X1 §SELF-VERIFICATION 9연속 PASS (Phase 3 5 + Phase 4 4). P-AGENT-SCOPE-001 mitigation 누적 입증. Phase 5+ 모든 sub-agent에 의무 유지.
- ★ **P-GPT-REVIEW-001 (신규)**: 외부 LLM 검토 (GPT) 채택 효과 — Phase 4 6→4 Slices (▼33%), 18~26h → 6~8h (▼66%). 후속 큰 phase 진입 전 multi-llm-validation Skill 정식 호출 권장.
- ★ **multi-model 인터페이스 baseline 확립**: config.py openai_models_for_3plan list로 Phase 21+ Anthropic / Custom 추가 시 ≤ 3 파일 영향.
- ★ **deviations.md 첫 활용 사이클 완성**: D-1 Slice 3 발견 → Slice 4 audit script 보강으로 해소 → contract-change 우회 + 후속 phase 이관 가이드 baseline.
- **P-AGENT-SCOPE-001** → Mitigated (9연속 입증 누적, 0건 재발)
- **P-THIN-VERTICAL-001** → backend phase 입증 (Phase 4 Slice 2 3-plan + multi-model end-to-end)
- **P-GRACEFUL-001** → multi-call 환경 자연 확장 (3 parallel retry/fallback)

---

## 5. Phase 2 → Phase 3 → Phase 4 패턴 흐름

```
Phase 2 회고 → P-X1 등록 (proposal)
        ↓
Phase 3 pre-entry → P-X1 채택 + 적용 (phase-start v1.2.0 → v1.3.0, commit 3d0b0fb)
        ↓
Phase 3 실행 → §SELF-VERIFICATION 5/5 PASS, component_map 6연속 0줄
        ↓
Phase 3 회고 → P-X1-EFFECT-001 등록 + Y-X1~Y-X3 proposals
        ↓
Phase 4 진입 (GPT 검토 채택) → 6→4 Slices, 사용자 결정 7개 반영
        ↓
Phase 4 실행 → §SELF-VERIFICATION 4/4 PASS, component_map 15연속 0줄, PlanCard 4연속 0줄
        ↓
Phase 4 회고 → P-X1-EFFECT-001 update (9연속) + P-GPT-REVIEW-001 신규 + Z-X1~Z-X3 proposals
        ↓
다음 phase (A/B/C, 사용자 결정 대기) → P-X1 유지 + P-X2 (변경성 시뮬 게이트) 채택 권장 + multi-llm-validation formal 권장
```

---

## 6. 미해결 항목 (다음 Phase에서 처리 권장)

| ID | 항목 | 권장 처리 Phase |
|---|---|---|
| D6 / D7 / D8 / D3 / D4 / D2 / Phase 1 endpoint 제거 | (위 §2 참조) | 위 표 참조 |
| D1 | Step 2~7 wireframe 상세 | Phase 11+ |
| **P-X2** (Phase 2) + **Y-X1** 통합 | 변경성 시뮬레이션 phase-complete 자동 게이트 + 매핑표 spec/code 칸 분리 | **다음 phase 진입 전 채택 권장 (우선순위 ↑)** |
| **Z-X1** (Phase 4 신규) | audit_page_component.ps1 dynamic route 정규화 표준화 (Y-X2 흡수) | Phase 5+ 진입 직전 |
| Z-X2 (Phase 4 신규) | multi-provider client factory baseline | Phase 21+ 진입 직전 (현 단계 over-engineering 우려) |
| Z-X3 (Phase 4 신규) | Critic best-plan 선택 로직 (recommended_plan_index) | Phase 4.5+ Critic revise 도입 시 |
| Y-X3 | Sub-path 분리 패턴 표준 등록 (P-FOLDER-PARALLEL-001 확장) | Phase 5+ Wave 3 재발 시 (조건부) |
| P-X3 (Phase 2) | design-review SKILL.md spec-only 분기 | Phase 11+ design phase 재진입 시 |
| P-X4 (Phase 2) | worktree isolation | deferred 유지 (P-X1 9/9 효과 충분) |
| P-X5 (Phase 2) | 매트릭스 표준 등록 | P-X2 통합 자연 흡수 (deferred) |
| **multi-llm-validation formal 첫 사용** | 다음 큰 phase 진입 전 정식 호출 | **Phase 5+ 진입 전 권장** |
| Phase 1 U1~U5 + Phase 2 U2-1~U2-8 | 사용자 .env / 실 운영 누적 후 | Phase 5+ 실 사용자 누적 시 |

---

## 7. Phase 4 → 다음 phase 핸드오프

본 closing_notes + 다음 산출물이 다음 phase 진입 baseline:

### Phase 4 핵심 산출물 (실 코드)

1. `backend/fastapi/routers/plans.py` (4 endpoints — POST /plans/start + wizard/{step} + /generate + GET /plans/{id})
2. `backend/fastapi/schemas/plans.py` (Pydantic request / response)
3. `backend/fastapi/agents/planning.py` (run_planning_parallel_3 + approach_hints + retry + fallback)
4. `backend/fastapi/schemas/output.py` (Body Phase 4 + compute_validation_warnings_phase4)
5. `backend/fastapi/config.py` (openai_models_for_3plan list)
6. `backend/fastapi/main.py` (version + description)
7. `backend/fastapi/routers/generate.py` (X-API-Deprecation header, 본문 무변경)
8. `backend/fastapi/tests/test_plans.py` (15 신규 테스트)
9. `backend/fastapi/tests/test_3_plan.py` (16 신규 테스트)
10. `backend/fastapi/tests/conftest.py` (mock_planning_parallel_3_ok fixture)
11. `apps/web/app/plan/[plan_id]/page.tsx` (Phase 4 결과 페이지)
12. `apps/web/app/plan/page.tsx` (Phase 1 동작 + Phase 4 query redirect)
13. `apps/web/lib/api.ts` (Phase 4 fetch wrappers)
14. `apps/web/lib/types.ts` (Phase 4 타입)
15. `docs/decisions/phase_4_endpoint_migration.md` (ADR-014)
16. `docs/decisions/phase_4_3plan_multi_model.md` (ADR-015)

### Phase 4 audit / smoke 도구

17. `scripts/smoke_test_phase_4.ps1` (신규, 8 steps)
18. `scripts/audit_page_component.ps1` (Phase 4 dynamic /plan/[plan_id] 정규화 보강 — D-1 해소)

### Phase 4 QA + 회고 산출물

19. `eval/qa_reports/phase-4-entry-check_2026-05-28.md` + `phase-4-slice-1~3_2026-05-28.md` + `phase-4-final_2026-05-28.md` (5 reports)
20. `meta/retrospectives/phase-4.md`
21. `meta/proposals/2026-05-28_phase-4-retrospective-proposals.md` (Z-X1~Z-X3)
22. `meta/patterns.md` (P-X1-EFFECT-001 update 9연속 + P-GPT-REVIEW-001 신규)
23. `meta/skill_usage_log.md` (Phase 4 누적)
24. 본 closing_notes

### Phase 1+2+3 archive 참조 (필요 시)

- `phases/archive/phase-1-mvp-basic-flow/closing_notes.md`
- `phases/archive/phase-2-pwa-design/closing_notes.md`
- `phases/archive/phase-3-pwa-impl/closing_notes.md`
- `meta/retrospectives/phase-1.md` + `phase-2.md` + `phase-3.md`

---

## 8. 다음 phase 첫 작업 후보 (사용자 결정에 따라)

### 옵션 A 채택 시 (Phase 4.5)

1. P-008 Rewriter 본격 구현 (agents/rewriter.py)
2. agents/critic.py에 revise 트리거 분기
3. POST /plans/{id}/generate에서 revise_round 0/1/2 loop
4. tests/test_revise_loop.py 신규

### 옵션 B 채택 시 (Phase 5)

1. Supabase 프로비저닝 (.env.example + supabase/migrations/)
2. plan_store → Supabase plans 테이블 migration
3. Auth + RLS (Row-Level Security) baseline
4. SSE Progress (D7) /plans/{id}/generate/stream endpoint
5. multi-llm-validation Skill **formal 호출** (DB/Auth 설계 검증)

### 옵션 C 채택 시 (사용자 시점 재평가)

- Phase 6 / 9 / 11+ 중 사용자 선택

**다음 phase 진입 전 검토 권장**:
- `meta/proposals/2026-05-28_phase-4-retrospective-proposals.md` (Z-X1~Z-X3 + Phase 2 P-X2 채택)
- `meta/retrospectives/phase-4.md`
- 본 closing_notes

---

## 9. 변경 이력

- 2026-05-28: 정상 종료 결정 + closing_notes 작성 (phase-complete v1.1.0 §1). **A1~A10 10/10 PASS + P-X1 9/9 효과 입증 + component_map 15연속 0줄 + PlanCard 4연속 0줄 + GPT 검토 채택 효과 ▼66% 시간**. **다음 phase 옵션 A/B/C 명시 (사용자 결정 3-c)**.
