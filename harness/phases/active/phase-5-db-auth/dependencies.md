# Phase 5 — Dependencies

## 이전 Phase 의존성

| Phase | 상태 | 의존 항목 |
|---|---|---|
| Phase 0~3 | ✅ done | 기본 (참조 제한) |
| Phase 4 | ✅ done | /plans/{plan_id}/generate + 3-plan + multi-model |
| Phase 4.5 | ✅ done | Rewriter + Critic revise loop + revise_history + recommended_plan_index |
| Phase 6 | ✅ done | **★ Critic canonical (overall_score + dimensions) + Rewriter v1.1.0 + canonical schema** (Phase 5 DB 영속화의 핵심 baseline) |

**모두 done** — 강제 진행 사유 없음.

## Contract 참조 + 수정

| Contract | 사용 |
|---|---|
| `docs/contracts/db_schema.md` | **신규 작성** (Slice 2) |
| `docs/contracts/api_contract.md` | **수정** (Auth + SSE endpoints) |
| `docs/contracts/llm_security_contract.md` | **참조 + 선택 수정** (JWT + RLS) |
| `docs/contracts/output_schema.md` | **참조만** — Phase 6 canonical 그대로 DB 영속화 |
| `docs/contracts/agent_io_contract.md` | **참조만** — Phase 6 Rewriter v1.1.0 유지 |
| `docs/contracts/mvp_non_goals.md` | 참조 |
| `docs/contracts/rate_limit_policy.md` | **수정** (선택, 사용자별 quota) |

## Skill 의존성

| Skill | 호출 시점 | 필수 |
|---|---|---|
| `phase-start` v1.3.0 | entry | 필수 |
| `multi-llm-validation` | **Slice 1** (formal self + external) | **필수** (Phase 6 baseline 계승) |
| **`security-review`** | **Slice 1 + Slice 4 final** (Auth/RLS 도입) | **★ 첫 정식 트리거 의무** |
| `contract-change` | Slice 2 (db_schema.md 신규 + api_contract 갱신) | 필수 |
| `qa-check` v1.2.0 | Slice 1~5 (entry + final) | 필수 |
| `harness-audit` | Slice 1 + Slice 5 final | 필수 |
| `design-review` | Slice 5 (impl §B + AuthGuard + SSE UI 정합) | 필수 |
| `agent-io-check` | Slice 5 (회귀 검증) | 필수 |
| `meta-retrospective` | Slice 5 | 필수 |
| `phase-complete` v1.2.0 | Slice 5 final (P-X2 세 번째 자동 게이트) | 필수 |
| `prompt-version-review` | 미호출 | Phase 7+ |

## 환경 / 외부 (★ 신규 도입)

- **Supabase 프로젝트** 신규 생성 필요 (사용자가 외부에서 생성 후 URL/Anon Key 제공)
- `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_KEY` 환경변수
- **PostgreSQL** + `pgvector` extension (Supabase 기본 제공)
- **JWT secret** (Supabase 자동 발급)
- **SSE**: FastAPI `StreamingResponse` + frontend EventSource API
- pytest mock: Supabase client mock (실 DB 호출 없이 unit test)
- next build / tsc 0 / lint clean 유지

## 진입 전 의무 (Phase 6 closing_notes 계승)

- [ ] external validation `2026-05-29_phase-5-pre-entry_external.md` 작성 (사용자 외부 검토 또는 Slice 1 placeholder)
- [ ] security-review Skill 절차 따름 (의무, 첫 정식 트리거)
- [ ] ADR-020 (Supabase 채택) 결정 사유 명시
- [ ] contract-change Skill (db_schema.md 신규)
- [ ] scenario_simulation v2 (DB/Auth 시나리오 5 추가)
