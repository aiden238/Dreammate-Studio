# Phase 5 — Acceptance (A1~A10 + M1~M4)

## A1~A10

| ID | 항목 | 검증 | Slice |
|---|---|---|---|
| **A1** | Supabase client 연결 (mock 환경) | `pytest tests/test_db.py::test_supabase_client_connect_mock` | Slice 2 |
| **A2** | 4계층 + plans + users schema migration | `db/migrations/0001_init.sql` + 0002 적용 가능 + ADR-020 | Slice 2 |
| **A3** | _plan_store → plans_repo CRUD 영속화 (graceful 유지) | `pytest tests/test_db.py::test_plans_repo_*` (5+ 케이스) | Slice 2 |
| **A4** | Supabase Auth + JWT 검증 | `pytest tests/test_auth.py` (3+ 케이스) | Slice 3 |
| **A5** | Frontend /login + AuthGuard 동작 | `next build` + tsc 0 + lint clean + login page render | Slice 3 |
| **A6** | RLS 정책 — 다른 user plan 접근 차단 | `pytest tests/test_rls.py::test_other_user_plan_forbidden` | Slice 4 |
| **A7** | SSE Progress 4단계 + 부분 결과 | `pytest tests/test_sse.py` (3+ 케이스, event schema 검증) + ADR-022 | Slice 4 |
| **A8** | Phase 6 canonical schema DB 호환 | revise_history + recommended_plan_index JSONB 컬럼 round-trip | Slice 2 |
| **A9** | **PlanCard.tsx 0줄 (13연속) + component_map.md 0줄 (23연속)** | git diff --stat | Slice 3 + 5 |
| **A10** | smoke_test_phase_5 12/12 PASS | `scripts/smoke_test_phase_5.ps1` | Slice 5 |

## M1~M4 (메타)

| ID | 항목 | 검증 |
|---|---|---|
| **M1** | multi-llm-validation formal self **V1~V6** + external 실제 작성 (또는 placeholder 분리) | `meta/validations/2026-05-29_phase-5-pre-entry_self.md` + external |
| **M2** | **security-review Skill 첫 정식 트리거** (Auth + RLS 도입 위험 평가) | `meta/security_reviews/2026-05-29_phase-5-auth-rls.md` |
| **M3** | scenario_simulation.ps1 **v2** (DB/Auth 시나리오 5 추가) | `scripts/scenario_simulation.ps1` v2 — 10 시나리오 PASS |
| **M4** | P-X1 §SELF-VERIFICATION **22연속 PASS** (Phase 5 Slice 1~5 모두) | sub-agent 5 dispatch |

## 회귀 baseline (Phase 6 → Phase 5)

| 지표 | Phase 6 | Phase 5 목표 |
|---|---|---|
| pytest | 144/144 | 165~175/165~175 (+21+ 신규: DB 5 + Auth 3 + RLS 3 + SSE 3 + 통합) |
| smoke | 10/10 | **12/12** (smoke_test_phase_5: Phase 6 10 + DB connect + RLS test) |
| scenario_simulation | 5/5 | **10/10** (v2 — DB/Auth 5 추가) |
| schema_stress_test | 5/5 | 5/5 유지 |
| audit×2 | 0 drift | 0 drift |
| component_map.md 0줄 streak | 22 | **23** |
| PlanCard.tsx 0줄 streak | 12 | **13** |
| P-X1 streak | 17 | **22** |

## qa-check 카테고리 (v1.2.0)

Phase 5 final 예상:
- 1. 제품/범위 — PASS
- 2. AI 구조 — PASS (회귀 0)
- 3. RAG — skip (Phase 7)
- 4. 프론트/UX — PASS (AuthGuard + SSE)
- 5. 평가 — skip (Phase 9+)
- 6. 메타 — PASS
- 7. 컨텍스트 — 필요 시
- 8. 큰 결정 — **PASS** (security-review + multi-llm-validation + contract-change)
- 9. Phase 운영 — PASS
- **10. 보안/인프라 — PASS** (★ 첫 정식 활성화 — Auth + RLS + JWT)
- 11. 비용/관측성 — skip (Phase 9+)

**예상**: 8 PASS / 3 skip.
