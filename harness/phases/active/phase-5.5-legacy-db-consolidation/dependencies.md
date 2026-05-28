# Phase 5.5 — Dependencies

## 이전 Phase 의존성

| Phase | 상태 | 의존 항목 |
|---|---|---|
| Phase 1 | ✅ done | `db/supabase_client.py`, `db/save_video_planning.py`, `tests/test_db.py` (legacy 8 케이스) |
| Phase 4 | ✅ done | /plans/{plan_id}/generate baseline |
| Phase 4.5 | ✅ done | external validation placeholder (강화 대상) |
| Phase 5 | ✅ done | **`db/client.py`, `plans_repo.py`, `db/migrations/0001/0002/0003`, `tests/test_db.py` (Phase 5 18 케이스), `routers/auth.py`, `routers/sse.py`, `middleware/auth_middleware.py`** + external placeholder |
| Phase 6 | ✅ done | canonical schema baseline + external placeholder |

**모두 done** — 강제 진행 사유 없음.

## Contract 참조 (수정 없음 — 본 phase는 ADR만 신규)

| Contract | 사용 |
|---|---|
| `docs/contracts/db_schema.md` | **참조만** (Phase 5 Slice 2 갱신 결과 그대로) |
| `docs/contracts/output_schema.md` | **참조만** |
| `docs/contracts/agent_io_contract.md` | **참조만** |
| `docs/contracts/api_contract.md` | **참조만** |
| `docs/contracts/llm_security_contract.md` | **참조만** |
| `docs/contracts/mvp_non_goals.md` | 참조 |

→ 본 phase는 contract-change Skill 호출 없음 (ADR 신규는 docs/decisions/이며 contract 변경 아님).

## Skill 의존성

| Skill | 호출 시점 | 필수 |
|---|---|---|
| `phase-start` v1.3.0 | entry | 필수 |
| `qa-check` v1.2.0 | Slice 1 + 4 final | 필수 |
| `harness-audit` | Slice 1 + 4 | 필수 |
| `meta-retrospective` | Slice 4 | 필수 |
| `phase-complete` v1.2.0 | Slice 4 final (P-X2 네 번째 자동 게이트) | 필수 |
| `multi-llm-validation` | (미호출) | Phase 5에서 형식 정착, Phase 5.5는 validation 강화 작업이므로 형식 재사용 |
| `contract-change` | (미호출) | ADR만 신규, contract 직접 변경 없음 |
| `security-review` | (미호출) | Phase 5에서 완료, 본 phase는 보안 변경 없음 |
| `agent-io-check` | (미호출) | 본 phase는 agents/* 변경 없음 |
| `design-review` | (미호출) | 본 phase는 frontend 변경 없음 |

## 환경 / 외부

- 변경 없음 (Phase 5 baseline 유지)
- pytest 170/170 → 170+/170+ (legacy 통합으로 +0~3, 회귀 0)
- next build 12 routes 유지
- audit×2 0 drift + 1 intended WARN (Phase 5 Slice 3 AuthGuard) 유지
