# Phase 8 — Assumptions (phase-start v1.3.0 §6 4점검)

> 작성: 2026-05-29
> 결과: ✅ **4-check 통과**

---

## §6.1 Assumptions

### 1.1 확정 가정 (C1~C11)

| ID | 항목 | 근거 |
|---|---|---|
| C1 | audit_naming PASS 0 drift (entry) | scripts/audit_naming.ps1 |
| C2 | Phase 7 baseline 완전 유지 (pytest 223 + smoke 13 + scenario_sim v3 15 + P-X1 31) | Phase 7 Slice 5 |
| C3 | **god-function 추출은 behavior-preserving refactor** — 기존 pytest 223 수정 0이 동작 불변 증거 | non_goals 핵심 제약 |
| C4 | **Critic conservative adapter** (사용자 결정) — Phase 6 canonical(0–1) 불변, P-007 prompt(0–5) + 정규화 adapter 문서화 | 사용자 결정 |
| C5 | SSE 통합 = in-memory progress store 브릿지 (graceful) — background task 미도입 (moa_policy §4 sync, async Phase 11+) | 사용자 기본값 채택 |
| C6 | ProgressSink NullSink default → orchestrator 추출 시 회귀 0 (emit no-op) | 설계 원칙 |
| C7 | prompt_id/version은 각 agent 파일 상수 + registry 단일 출처 정합 (drift 검증 test) | gap 분석 |
| C8 | PlanCard.tsx + component_map.md 0줄 보존 (backend-only phase) | 자동 보장 |
| C9 | ai-architecture-review + prompt-version-review Skill 첫 정식 트리거 가능 | meta/skill_usage_log 활성 예상 |
| C10 | mock 환경 unit test 가능 (실 LLM/Supabase 호출 X) | Phase 4~7 pattern |
| C11 | SSE 실시간 concurrency는 단일 프로세스 best-effort (POST in-flight 중 GET read) — full async streaming은 Phase 11+ | ADR-028 명시 |

### 1.2 불확실 항목 (U1~U6)

| ID | 항목 | 검증 시점 |
|---|---|---|
| U1 | god-function 추출 시 graceful 처리 / 에러 코드 / validation.checks 순서 100% 보존 가능한가 | Slice 2 pytest (기존 test_plans / test_e2e PASS) |
| U2 | progress_store가 동기 blocking generate 중 SSE에서 실시간 read 가능한가 (single process) | Slice 3 + ADR-028 (best-effort 명시) |
| U3 | Critic 0–5↔0–1 adapter가 기존 run_critic 동작과 정합한가 (run_critic 이미 canonical 산출) | Slice 4 agent-io-check |
| U4 | prompt_registry 11개 prompt 상수 정합이 모든 agent 파일에 일관한가 | Slice 4 test_prompt_registry_consistency |
| U5 | orchestrator 추출 후 plans.py LOC가 충분히 감소하는가 (god-function 분해 실효) | Slice 2 |
| U6 | SSE progress_store TTL / cleanup 정책 (메모리 누수 방지) | Slice 3 (graceful + clear on complete) |

### 1.3 Contract cross-reference

- audit_naming entry: PASS 0 drift
- 신규 명명 점검:
  - `moa_orchestrator` / `generate_plan` (snake_case)
  - `ProgressSink` / `NullProgressSink` / `StoreProgressSink` (PascalCase class)
  - `progress_store` / `record` / `read` / `clear` (snake_case)
  - 모두 NAMING_POLICY 정합

---

## §6.2 Simplest Slice (3회 압축)

**1차**: "orchestrator 추출 + SSE 통합 + prompt_registry 정식화 + ProgressSink"

**2차**: "plans_generate() 로직을 generate_plan()으로 그대로 이동 + router는 호출만"

**3차**:
```python
# backend/fastapi/orchestration/moa_orchestrator.py
async def generate_plan(plan_id, plan_entry, req, *, progress: ProgressSink = NullProgressSink()) -> Envelope | ErrorEnvelope:
    # plans_generate() body 그대로 이관 (behavior-preserving)
    ...
```
router: `return await generate_plan(plan_id, plan_entry, req)`

→ **Slice 2 첫 1~2시간 산출물** (behavior-preserving 핵심). pytest 223 그대로 PASS가 증거.

---

## §6.3 Surgical Scope

### Editable
```
backend/fastapi/orchestration/* (신규 4)
backend/fastapi/routers/plans.py (thin adapter화)
backend/fastapi/routers/sse.py (progress_store read)
backend/fastapi/agents/critic.py (PROMPT_VERSION v1.1.0 + adapter 주석, 로직 불변)
backend/fastapi/agents/{intent,planning,rewriter}.py (상수 검증, 변경 최소)
backend/fastapi/tests/test_moa_orchestrator.py (신규)
backend/fastapi/tests/test_sse_integration.py (신규)
backend/fastapi/tests/test_prompt_registry_consistency.py (신규)
docs/contracts/agent_io_contract.md (Slice 4 contract-change)
ai_system/prompts/prompt_registry.md (Slice 4 contract-change)
ai_system/orchestration/moa_policy.md (선택, cross-ref)
docs/decisions/phase_8_{moa_orchestrator,sse_progress_integration,prompt_registry_semver}.md (ADR-027/028/029)
meta/validations/2026-05-29_phase-8-pre-entry_{self,external}.md
meta/retrospectives/phase-8.md
meta/patterns.md / meta/skill_usage_log.md
scripts/smoke_test_phase_8.ps1 (신규) / scripts/scenario_simulation.ps1 (v4)
phases/active/phase-8-*/* (entry)
PROJECT_STATE / PHASE_REGISTRY / 00_START_HERE / README
```

### Read-Only
```
docs/contracts/output_schema.md (Phase 6 canonical 불변 — NG5)
docs/contracts/api_contract.md
backend/fastapi/schemas/output.py (Phase 6 canonical)
backend/fastapi/rag/* (Phase 7 baseline)
backend/fastapi/db/* (Phase 5 baseline)
backend/fastapi/middleware/* (Phase 5)
모든 이전 ADR (ADR-014~026)
```

### Forbidden (절대 금지)
```
apps/web/components/PlanCard.tsx ★ (0줄)
apps/web/component_map.md ★ (0줄)
apps/web/* (전체 — backend-only phase)
backend/fastapi/schemas/output.py (Phase 6 canonical — NG5)
backend/fastapi/agents/rag.py (Phase 7 baseline — orchestrator가 호출만)
backend/fastapi/db/* (Phase 5 baseline)
backend/fastapi/middleware/* (Phase 5)
backend/fastapi/routers/{auth}.py (Phase 5 baseline — sse.py만 수정)
모든 baseline tests (test_critic, test_rewriter, test_schema_stress, test_plans, test_3_plan, test_auth, test_rls, test_sse, test_db, test_intent, test_rag_*, ...) — Phase 8 신규 test만 가능 ★ behavior-preserving 핵심
docs/contracts/{output_schema, db_schema, frontend_design_contract}.md
이전 ADR (ADR-014~026)
scripts/audit_*.ps1, schema_stress_test.ps1, smoke_test_phase_4_5/5/6/7.ps1
.claude/skills/*
phases/archive/*
knowledge/*
```

**★ Behavior-preserving 게이트**: 기존 baseline test (특히 test_plans, test_e2e_slice1, test_sse, test_3_plan) 를 **수정하지 않고** PASS시키는 것이 orchestrator 추출의 정당성 증거. 테스트 수정이 필요하면 추출이 동작을 바꾼 것 → 재작업.

### Sub-agent SELF-VERIFICATION (P-X1) — 모든 Slice 의무

Main session 사후 검증:
```bash
git diff HEAD~1 HEAD --stat | grep -E "PlanCard|component_map|apps/web/|schemas/output|agents/rag|db/|middleware/|routers/auth|test_(critic|rewriter|schema_stress|plans|3_plan|auth|rls|sse|db|intent|rag)|contracts/(output_schema|db_schema|frontend)|decisions/(phase_4|phase_5|phase_6|phase_7)|audit_|schema_stress_test|smoke_test_phase_(4_5|5|6|7)|skills/|archive/" = 0 lines
```

---

## §6.4 Verification

| Acceptance | 검증 | 자동 |
|---|---|---|
| A1 orchestrator | pytest test_moa_orchestrator | 자동 |
| A2 thin adapter | LOC 감소 + 위임 | 반자동 |
| A3 behavior-preserving | 기존 pytest 223 PASS (수정 0) | 자동 ★ |
| A4 ProgressSink | pytest emit | 자동 |
| A5 progress_store | pytest test_sse_integration | 자동 |
| A6 SSE read | pytest + 기존 test_sse | 자동 |
| A7 prompt semver | pytest test_prompt_registry_consistency + agent-io-check | 자동 |
| A8 0줄 | git diff | 자동 |
| A9 audit | scripts | 자동 |
| A10 smoke 14 + scenario v4 20 | scripts | 자동 |

자동 9 + 반자동 1 = 10/10.

---

## §6 결과: ✅ 4-check 통과

**다음 단계**: Slice 1 sub-agent dispatch — validations + ai-architecture-review + prompt-version-review (분석) + ADR-027/028/029.
