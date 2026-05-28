# Phase 5 — Assumptions (phase-start v1.3.0 §6 4점검)

> 작성: 2026-05-29
> 결과: ✅ **4-check 통과** — 진입 허용 (단 ★ external validation + security-review는 Slice 1에서 의무 수행)

---

## §6.1 Assumptions

### 1.1 확정 가정 (C1~C11)

| ID | 항목 | 근거 |
|---|---|---|
| C1 | **audit_naming PASS 0 drift (2026-05-29 entry)** | scripts/audit_naming.ps1 실행 |
| C2 | Phase 6 baseline 유지 가능 | pytest 144/144 + smoke 10/10 + schema_stress 5/5 + P-X1 17연속 |
| C3 | **Phase 6 canonical schema 안정** — Critic canonical + Rewriter v1.1.0 + revise_history + recommended_plan_index 모두 DB 영속 가능 (ADR-018/019) | Phase 6 종료 baseline |
| C4 | Supabase 사용 가능 — 사용자가 외부에서 프로젝트 생성 + URL/Anon Key 제공 | 환경 의존 (인적) |
| C5 | PostgreSQL + pgvector extension 자동 제공 (Supabase 기본) | Supabase 문서 |
| C6 | FastAPI StreamingResponse + frontend EventSource로 SSE 구현 가능 | 표준 패턴 |
| C7 | mock 기반 unit test 가능 — 실 DB 호출 없이 plans_repo / auth 검증 | pytest pattern |
| C8 | PlanCard.tsx + component_map.md 0줄 보존 가능 — AuthGuard + SSE Progress UI는 wrapper / 별도 컴포넌트 | NG8/NG9 + Phase 4.5 wrapper UI 패턴 계승 |
| C9 | revise_history JSONB 컬럼 round-trip 가능 — PostgreSQL JSONB 표준 + Pydantic dict 직렬화 | C3 + PostgreSQL 표준 |
| C10 | security-review Skill 첫 정식 트리거 가능 — 절차 따름 (위험 평가 + 권장 사항 명시) | meta/skill_usage_log Phase 5 활성 예상 |
| C11 | multi-llm-validation formal self V1~V6 + external 작성 가능 | Phase 4.5 + Phase 6 패턴 계승 |

### 1.2 불확실 항목 (U1~U6)

| ID | 항목 | 검증 시점 |
|---|---|---|
| U1 | Supabase Auth 토큰 expiry 정책 (1h vs 24h vs custom) | Slice 3 결정 |
| U2 | RLS 정책 SQL이 모든 endpoint에서 일관 작동 (특히 anonymous /generate 호환) | Slice 4 pytest |
| U3 | SSE keep-alive / heartbeat 정책 (30s? 60s?) | Slice 4 결정 |
| U4 | SSE 연결 끊김 시 클라이언트 재연결 정책 | Slice 4 결정 |
| U5 | _plan_store → DB migration 시 graceful fallback이 실 user 데이터 유실 위험 | Slice 2 mock test |
| U6 | revise effect eval (NG15) 미적용 상태에서 revise_history JSONB 저장 시 무용 데이터 누적 위험 | Phase 9+ eval 도입 시 재평가 |

### 1.3 Contract cross-reference

- `audit_naming.ps1` entry: PASS 0 drift
- 신규 명명 점검:
  - `plans` / `users` / `brands` / `domains` / `series` / `video_projects` (snake_case 테이블명)
  - `revise_history` (JSONB 컬럼)
  - `recommended_plan_index` (INTEGER 컬럼)
  - `auth_user_id` (UUID, Supabase auth.users.id FK)
  - `SUPABASE_URL`, `SUPABASE_ANON_KEY` (env var SCREAMING_SNAKE_CASE)
  - 모두 NAMING_POLICY 정합

---

## §6.2 Simplest Slice (3회 압축)

**1차**: "Supabase 연결 + Auth + RLS + SSE 통합"

**2차**: "_plan_store dict 1개를 Supabase 1 테이블로 영속화 + JWT 검증 미들웨어 1개"

**3차**: 
```python
# backend/fastapi/db/client.py
from supabase import create_client, Client
def get_supabase() -> Client:
    return create_client(settings.supabase_url, settings.supabase_anon_key)

# tests/test_db.py
def test_supabase_client_creation():
    client = get_supabase()
    assert client is not None
```

→ **Slice 2 첫 30분 산출물**. 이후 plans_repo + Auth + RLS + SSE 확장.

---

## §6.3 Surgical Scope

### Editable
```
docs/contracts/{db_schema.md (신규), api_contract.md, llm_security_contract.md, rate_limit_policy.md}
backend/fastapi/{db/*, routers/auth.py (신규), routers/sse.py (신규), routers/plans.py (수정 호환), middleware/auth_middleware.py (신규), config.py, tests/test_db.py, tests/test_auth.py, tests/test_rls.py, tests/test_sse.py}
apps/web/{app/login/page.tsx (신규), components/AuthGuard.tsx (신규), lib/auth.ts (신규), lib/sse.ts (신규), app/plan/[plan_id]/page.tsx (수정), lib/types.ts (수정)}
docs/decisions/phase_5_*.md (ADR-020~022)
meta/{validations/*, security_reviews/* (신규 폴더), retrospectives/phase-5.md, patterns.md, skill_usage_log.md}
scripts/{scenario_simulation.ps1 (v2), smoke_test_phase_5.ps1 (신규)}
phases/active/phase-5-*/*
PROJECT_STATE / PHASE_REGISTRY / 00_START_HERE / README × 2
```

### Read-Only (참조만)
```
docs/contracts/output_schema.md (Phase 6 canonical 그대로)
docs/contracts/agent_io_contract.md (Phase 6 Rewriter v1.1.0 그대로)
backend/fastapi/agents/* (Phase 6 baseline 보존)
backend/fastapi/schemas/output.py (Phase 6 canonical)
```

### Forbidden (절대 수정 금지)
```
apps/web/components/PlanCard.tsx           ★ 13연속 0줄 목표
apps/web/component_map.md                  ★ 23연속 0줄
backend/fastapi/agents/critic.py, rewriter.py, planning.py, intent.py, rag.py (Phase 6 baseline)
backend/fastapi/schemas/output.py (Phase 6 canonical)
backend/fastapi/tests/test_critic.py, test_rewriter.py, test_schema_stress.py, test_plans.py, test_3_plan.py, test_rewriter.py (Phase 4.5/6 baseline)
docs/contracts/output_schema.md, agent_io_contract.md (Phase 6 baseline)
docs/decisions/phase_4_5_*.md, phase_6_*.md (이전 ADR)
scripts/audit_*.ps1, schema_stress_test.ps1, smoke_test_phase_4_5.ps1, smoke_test_phase_6.ps1
.claude/skills/* (수정 금지 — phase-complete v1.2.0은 Phase 4.5에서 완료)
phases/archive/*
```

### Sub-agent SELF-VERIFICATION (P-X1) — 모든 Slice 의무

기존 패턴 유지 — git status + git diff --stat + editable/forbidden 대조 + forbidden 1줄 변경 시 즉시 revert.

**Main session 사후**: 
```bash
git diff HEAD~1 HEAD --stat | grep -E "PlanCard|component_map|critic\.py|rewriter\.py|planning\.py|intent\.py|output\.py|test_critic|test_rewriter|test_schema_stress|test_plans|audit_|schema_stress_test|smoke_test_phase_(4_5|6)" = 0 lines
```

---

## §6.4 Verification

각 acceptance에 검증 방법:

| Acceptance | 검증 | 자동 |
|---|---|---|
| A1 Supabase mock | pytest test_db.py::test_supabase_client_connect_mock | 자동 |
| A2 schema migration | sql 파일 존재 + ADR-020 + pytest dry-run | 반자동 |
| A3 plans_repo CRUD | pytest test_db.py | 자동 |
| A4 Auth JWT | pytest test_auth.py | 자동 |
| A5 frontend login | next build + tsc + lint + page.tsx string match | 반자동 |
| A6 RLS | pytest test_rls.py | 자동 |
| A7 SSE | pytest test_sse.py + ADR-022 | 자동 |
| A8 canonical DB | revise_history JSONB round-trip pytest | 자동 |
| A9 0줄 baseline | git diff --stat | 자동 |
| A10 smoke 12/12 | smoke_test_phase_5.ps1 | 자동 |

자동 8 + 반자동 2 = 10/10 자동화 (수동 0).

---

## §6 결과: ✅ 4-check 통과 + ★ 진입 직전 의무

**의무 (Slice 1에서)**:
1. external validation 작성 (사용자 외부 또는 self 강화)
2. security-review Skill 첫 정식 트리거
3. ADR-020 Supabase 채택 결정
4. scenario_simulation v2 (DB/Auth 시나리오 5 추가)

**다음 단계**: Slice 1 sub-agent dispatch.
