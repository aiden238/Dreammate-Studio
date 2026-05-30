# Phase 8 — Multi-Slice Plan

> 5 Slice 모두 sub-agent dispatch, sequential
> 총 12~16h

---

## Wave 구조

```
Wave 1: Slice 1 [Pre-Entry — validations + ai-architecture-review + prompt-version-review(분석) + ADR-027/028/029]
  ↓
Wave 2: Slice 2 [MOA Orchestrator 추출 (behavior-preserving) + ProgressSink]
  ↓
Wave 3: Slice 3 [SSE Progress worker 통합 — progress_store 브릿지]
  ↓
Wave 4: Slice 4 [prompt_registry 정식화 — contract-change + prompt-version-review 적용]
  ↓
Wave 5: Slice 5 [Close]
```

---

## Slice 1 — Pre-Entry (1.5~2.5h)

### 작업 단위
1. `meta/validations/2026-05-29_phase-8-pre-entry_self.md` — V1~V7:
   - V1 orchestrator 추출 behavior-preserving 원칙
   - V2 ProgressSink 인터페이스 설계 (Null default 회귀 0)
   - V3 SSE progress_store 브릿지 (graceful, background task 미도입)
   - V4 Critic conservative adapter (Phase 6 canonical 불변, 사용자 결정)
   - V5 prompt_registry semver 정식화 범위
   - V6 prompt_id/version 단일 출처 정합 정책
   - V7 SSE 실시간 concurrency best-effort (single process)
2. `meta/validations/2026-05-29_phase-8-pre-entry_external.md` (placeholder)
3. **ai-architecture-review Skill ★ 첫 정식 트리거** — MOA orchestration 설계 검토 (4 agent 분리 + orchestrator 중개 + cost/fallback policy 정합). 결과 ADR-027 통합.
4. **prompt-version-review Skill ★ 첫 정식 트리거 (분석 단계)** — P-007 Critic 0–5↔0–1 drift 분석 + semver 계획 (Slice 4 적용). 결과 ADR-029 통합.
5. `docs/decisions/phase_8_moa_orchestrator.md` (ADR-027):
   - Context: plans_generate() god-function (400줄)
   - Decision: orchestration/moa_orchestrator.py 추출 (behavior-preserving) + ProgressSink Protocol
   - Constraints: Envelope byte-identical + pytest 223 수정 0
6. `docs/decisions/phase_8_sse_progress_integration.md` (ADR-028):
   - Context: sse.py mock 4단계 decoupled
   - Decision: in-memory progress_store 브릿지 + orchestrator emit + sse read + graceful fallback
   - Constraints: background task 미도입 (moa_policy §4), single-process best-effort, full async Phase 11+
7. `docs/decisions/phase_8_prompt_registry_semver.md` (ADR-029):
   - Context: prompt_registry P-007(0–5) ↔ Phase 6 canonical(0–1) drift
   - Decision: conservative adapter — P-007 prompt 0–5 유지 + 코드 0–1 정규화 + P-007 v1.0.0→v1.1.0 + Phase 6 canonical 불변
   - semver 정식화: P-001~P-008 + AUX + prompt_id/version 단일 출처
8. `meta/skill_usage_log.md` (phase-start 10 + multi-llm-validation 6 + ai-architecture-review 1 + prompt-version-review 1)
9. `PROJECT_STATE.md` (phase_8_*)
10. **entry commit**

### Sub-agent 핵심
- editable: meta/validations/*, docs/decisions/phase_8_*.md, meta/skill_usage_log.md, PROJECT_STATE.md, phases/active/phase-8-*/notes.md
- forbidden: backend/* (Slice 2~4), apps/web/*, contracts (Slice 4), scripts, skills, archive, 이전 ADRs, entry files(notes 외)
- P-X1 의무

---

## Slice 2 — MOA Orchestrator 추출 (behavior-preserving) (4~5h) ★ 핵심

### 작업 단위
1. `backend/fastapi/orchestration/__init__.py` 신규 — export
2. `backend/fastapi/orchestration/progress_sink.py` 신규:
   - `ProgressSink` Protocol (`emit(stage: str, **meta) -> None`)
   - `NullProgressSink` (no-op default — 회귀 0)
   - `StoreProgressSink` (progress_store에 record — Slice 3에서 활용, Slice 2는 stub 가능)
3. `backend/fastapi/orchestration/moa_orchestrator.py` 신규:
   - `async def generate_plan(plan_id, plan_entry, req, *, progress=NullProgressSink()) -> Envelope | JSONResponse`
   - `plans_generate()` body **그대로 이관** (Intent→RAG→3-plan→Critic+revise→save→Envelope)
   - 각 stage 경계에서 `progress.emit("intent"/"rag"/"planning"/"critic"/"complete")` 삽입 (emit은 Null이면 no-op)
   - graceful 처리 / 에러 코드(E-LLM-*, INV-*) / validation.checks 순서 **100% 보존**
4. `backend/fastapi/routers/plans.py` 수정:
   - `plans_generate()` → orchestrator 호출 thin adapter (`return await generate_plan(...)`)
   - `_plan_store` / `_plans_repo` 는 그대로 (또는 orchestrator로 이동 + 호환 유지)
   - `_not_found_response` / `_error_envelope_response` helper는 orchestrator와 공유 (orchestration/ 또는 router 유지)
5. `backend/fastapi/tests/test_moa_orchestrator.py` 신규:
   - generate_plan 기본 동작 (mock agents)
   - ProgressSink emit 호출 검증 (stage별)
   - NullProgressSink 회귀 0
   - 에러 경로 (Intent 차단 / Planning 실패) 보존
6. **★ behavior-preserving 검증**: `pytest backend/fastapi/tests/` 기존 223 **수정 0** PASS (특히 test_plans / test_e2e_slice1 / test_3_plan)
7. **commit**

### 영향 파일 (4 신규 + 1~2 수정 + 1 test 신규)

### Sub-agent 핵심
- editable: backend/fastapi/orchestration/*, routers/plans.py, tests/test_moa_orchestrator.py
- forbidden: ★ 모든 baseline tests (수정 0 = behavior-preserving 증거), schemas/output.py, agents/* (rag 포함), sse.py (Slice 3), db/*, middleware/*, contracts, apps/web/*, PlanCard, component_map, scripts, skills, archive
- P-X1 의무 + **기존 test 수정 0 사후 검증**

---

## Slice 3 — SSE Progress worker 통합 (2~3h)

### 작업 단위
1. `backend/fastapi/orchestration/progress_store.py` 신규:
   - `_store: dict[str, list[dict]]` (plan_id → events, in-memory graceful)
   - `record(plan_id, event)` / `read(plan_id) -> list[dict]` / `clear(plan_id)`
   - TTL/cleanup: complete 시 또는 maxlen 제한 (메모리 누수 방지, U6)
2. `orchestration/progress_sink.py` `StoreProgressSink` 완성 — emit → progress_store.record
3. `backend/fastapi/routers/plans.py` 수정 (소폭) — generate 시 StoreProgressSink 주입 (plan_id keyed)
4. `backend/fastapi/routers/sse.py` 수정:
   - mock `_progress_generator` → progress_store read 우선
   - graceful fallback: store 비어있으면 기존 mock 4단계 (기존 test_sse 보존)
   - 실 stage 반영 (intent → rag → planning → critic → complete)
5. `backend/fastapi/tests/test_sse_integration.py` 신규:
   - progress_store record → sse read round-trip
   - graceful fallback (store empty → mock)
   - clear on complete
6. **기존 test_sse 4 케이스 수정 0 PASS** (graceful fallback 보장)
7. **commit**

### 영향 파일 (1 신규 + 3 수정 + 1 test 신규)

### Sub-agent 핵심
- editable: backend/fastapi/orchestration/{progress_store.py, progress_sink.py}, routers/{plans.py, sse.py}, tests/test_sse_integration.py
- forbidden: Slice 2 moa_orchestrator 코어 로직 (progress emit 지점은 Slice 2 완료), schemas, agents, db, middleware, 모든 baseline tests(test_sse 포함 — graceful로 보존), contracts, apps/web/*, PlanCard, component_map, scripts, skills, archive
- P-X1 의무

---

## Slice 4 — prompt_registry 정식화 (2~3h)

### 작업 단위
1. **prompt-version-review Skill 적용** (Slice 1 분석 → Slice 4 실 적용)
2. **contract-change Skill 호출**:
   - `ai_system/prompts/prompt_registry.md` — P-001~P-008 + AUX semver 정식화 + P-007 v1.0.0→v1.1.0 + §0–5↔0–1 adapter 추가
   - `docs/contracts/agent_io_contract.md` — orchestrator 중개 + Critic v1.1.0 adapter 명시
3. `backend/fastapi/agents/critic.py` 수정 (소폭):
   - `PROMPT_VERSION = "v1.1.0"` (0–5↔0–1 adapter 명시, 정규화 로직 불변 — 이미 canonical 산출)
   - adapter 주석 + 0–5 LLM 출력 → 0–1 dimensions 정규화 docstring
4. `backend/fastapi/agents/{intent,planning,rewriter}.py` — PROMPT_ID/VERSION 상수 registry 정합 검증 (변경 최소)
5. `backend/fastapi/tests/test_prompt_registry_consistency.py` 신규:
   - 각 agent 파일 PROMPT_ID/VERSION 상수 ↔ registry 정합
   - P-007 v1.1.0 adapter 검증 (0–5 입력 → 0–1 dimensions)
6. **agent-io-check Skill** — agent_io_contract ↔ 구현 drift 0
7. **회귀 0**: 기존 test_critic 등 수정 0 PASS
8. **commit**

### 영향 파일 (1 신규 test + 2 contract + 1~4 agent 소폭)

### Sub-agent 핵심
- editable: ai_system/prompts/prompt_registry.md, docs/contracts/agent_io_contract.md, ai_system/orchestration/moa_policy.md(선택), backend/fastapi/agents/critic.py(소폭) + {intent,planning,rewriter}.py(상수 검증), tests/test_prompt_registry_consistency.py
- forbidden: schemas/output.py(Phase 6 canonical — NG5), orchestration/* (Slice 2/3), routers/* (Slice 2/3), db, middleware, rag, 모든 baseline tests(test_critic 포함 — 회귀 0), output_schema.md, 이전 ADRs, apps/web/*, PlanCard, component_map, scripts, skills, archive
- contract-change Skill 절차
- P-X1 의무

---

## Slice 5 — Close (1~2h)

### 작업 단위
1. `scripts/smoke_test_phase_8.ps1` 신규 (14 체크: Phase 7 13 + MOA orchestrator 1)
2. `scripts/scenario_simulation.ps1` v4 (S16~S20 MOA 시나리오 5 추가, 기존 v3 보존):
   - S16 orchestrator 추출 (moa_orchestrator.py)
   - S17 ProgressSink 인터페이스 (progress_sink.py)
   - S18 progress_store 브릿지 (progress_store.py)
   - S19 SSE 실 stage (sse.py + progress_store)
   - S20 prompt_registry semver (prompt_registry.md + critic.py v1.1.0)
3. audit×2 + agent-io-check + ai-architecture-review(회고) + design-review(frontend 변경 0)
4. `meta/retrospectives/phase-8.md` 신규
5. `meta/patterns.md`:
   - P-X1-EFFECT-001 update (**36연속**)
   - **P-MOA-ORCHESTRATOR-001 신규** (god-function → service layer 추출)
   - **P-BEHAVIOR-PRESERVING-001 신규** (기존 test 수정 0 = refactor 정당성 증거)
6. `meta/skill_usage_log.md` (ai-architecture-review 1 + prompt-version-review 1 첫 정식 + 기타)
7. phase-complete v1.2.0 (P-X2 여섯 번째 자동 게이트)
8. archive 이동
9. `closing_notes.md` (Phase 9 결과저장/피드백 권장)
10. PROJECT_STATE / PHASE_REGISTRY / 00_START_HERE / README 갱신
11. **final commit**

### Sub-agent 핵심
- editable: scripts/smoke_test_phase_8.ps1, scenario_simulation.ps1(v4), meta/retrospectives/phase-8.md, patterns.md, skill_usage_log.md, phases/archive/phase-8-*(이동), closing_notes.md, state docs
- forbidden: backend/*, apps/web/*, PlanCard, component_map, contracts, 이전 ADRs(ADR-027/028/029 보존), scripts/audit_*+schema_stress+smoke_4_5/5/6/7, skills
- P-X1 의무

---

## 충돌 매트릭스

| Slice | orchestration | plans.py | sse.py | critic.py | tests | contracts/registry | meta/docs | scripts | state |
|---|---|---|---|---|---|---|---|---|---|
| 1 | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ validations+ADR | ❌ | ✅ entry |
| 2 | ✅ orchestrator+sink | ✅ thin adapter | ❌ | ❌ | ✅ test_moa | ❌ | ❌ | ❌ | ❌ |
| 3 | ✅ store+sink完成 | ✅ sink 주입 | ✅ read | ❌ | ✅ test_sse_integ | ❌ | ❌ | ❌ | ❌ |
| 4 | ❌ | ❌ | ❌ | ✅ v1.1.0 | ✅ test_prompt | ✅ registry+agent_io | ❌ | ❌ | ❌ |
| 5 | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ retrospective+patterns | ✅ smoke+scenario | ✅ all |

Sequential 시 충돌 0. (plans.py는 Slice 2 thin adapter화 → Slice 3 sink 주입 소폭 — 순차 보장)

---

## 누적 P-X1 streak

| Phase | streak |
|---|---|
| Phase 7 | 31 |
| Phase 8 | **5 (목표)** |
| **누적** | **36** |

---

## 시간 추정

| Slice | 시간 | 누적 |
|---|---|---|
| 1 | 1.5~2.5h | 1.5~2.5h |
| 2 | 4~5h | 5.5~7.5h |
| 3 | 2~3h | 7.5~10.5h |
| 4 | 2~3h | 9.5~13.5h |
| 5 | 1~2h | **10.5~15.5h** (추정 12~16h 정합) |
