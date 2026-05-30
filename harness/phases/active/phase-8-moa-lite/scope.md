# Phase 8 — Scope

## 포함 (In-Scope)

### Backend — Orchestration (신규 패키지)

| 파일 | 작업 |
|---|---|
| `backend/fastapi/orchestration/__init__.py` | **신규** — orchestration layer export |
| `backend/fastapi/orchestration/moa_orchestrator.py` | **신규** — `generate_plan()` (Intent→RAG→3-plan→Critic+revise→save→Envelope 이관) |
| `backend/fastapi/orchestration/progress_sink.py` | **신규** — ProgressSink Protocol + NullProgressSink + StoreProgressSink |
| `backend/fastapi/orchestration/progress_store.py` | **신규** — in-memory progress store (graceful, keyed by plan_id) |

### Backend — Router / SSE (수정, thin adapter화)

| 파일 | 작업 |
|---|---|
| `backend/fastapi/routers/plans.py` | **수정** — `plans_generate()` god-function → orchestrator 호출 thin adapter (behavior-preserving) |
| `backend/fastapi/routers/sse.py` | **수정** — mock 4단계 → progress_store read (실 stage 반영, graceful fallback 유지) |

### Backend — Agents (prompt_id/version 상수 정합만, 로직 불변)

| 파일 | 작업 |
|---|---|
| `backend/fastapi/agents/critic.py` | **수정 (소폭)** — PROMPT_VERSION v1.0.0→v1.1.0 (Critic adapter 명시) + 0–5↔0–1 정규화 주석/문서화 (로직 불변) |
| `backend/fastapi/agents/{intent,planning,rewriter}.py` | **참조 + 상수 검증** — registry 정합 확인 (변경 최소) |

### Contracts (contract-change Skill)

| 파일 | 작업 |
|---|---|
| `docs/contracts/agent_io_contract.md` | **수정** — orchestrator 중개 명시 + ProgressSink + Critic v1.1.0 adapter |
| `ai_system/prompts/prompt_registry.md` | **수정** — P-001~P-008 + AUX semver 정식화 + P-007 v1.1.0 + 0–5↔0–1 adapter §추가 |
| `ai_system/orchestration/moa_policy.md` | **수정 (선택)** — orchestrator 실 구현 cross-reference |
| `docs/contracts/api_contract.md` | **참조만** (SSE endpoint 기존 유지) |
| `docs/contracts/output_schema.md` | **참조만** (Phase 6 canonical 불변) |

### Tests

| 파일 | 작업 |
|---|---|
| `tests/test_moa_orchestrator.py` | **신규** — generate_plan + ProgressSink emit 검증 |
| `tests/test_sse_integration.py` | **신규** — progress_store ↔ sse read |
| `tests/test_prompt_registry_consistency.py` | **신규** — prompt_id/version 상수 ↔ registry 정합 |
| 모든 baseline tests | **수정 X** (Phase 7 223/223 보존 — behavior-preserving 핵심) |

### Frontend

| 파일 | 작업 |
|---|---|
| 모두 | **수정 X** (Phase 8 backend-only) |
| `apps/web/components/PlanCard.tsx` | **수정 절대 금지** ★ |
| `apps/web/component_map.md` | **수정 절대 금지** ★ |

### Meta / Scripts / Docs

| 파일 | 작업 |
|---|---|
| `meta/validations/2026-05-29_phase-8-pre-entry_self.md` | **신규** (M1) |
| `meta/validations/2026-05-29_phase-8-pre-entry_external.md` | **신규** (M1, placeholder) |
| `docs/decisions/phase_8_moa_orchestrator.md` | **신규** — ADR-027 |
| `docs/decisions/phase_8_sse_progress_integration.md` | **신규** — ADR-028 |
| `docs/decisions/phase_8_prompt_registry_semver.md` | **신규** — ADR-029 |
| `scripts/smoke_test_phase_8.ps1` | **신규** — 14 체크 |
| `scripts/scenario_simulation.ps1` | **수정** — v4 (S16~S20 MOA 시나리오 5 추가, 기존 v3 보존) |
| `meta/retrospectives/phase-8.md` | **신규** |
| `meta/patterns.md` | **수정** — P-MOA-ORCHESTRATOR-001 + P-BEHAVIOR-PRESERVING-001 신규 + P-X1 36 |
| `meta/skill_usage_log.md` | **수정** — ai-architecture-review + prompt-version-review 첫 정식 |
| `PROJECT_STATE.md` / `PHASE_REGISTRY.md` / `00_START_HERE.md` / `README.md` | **수정** |

## 예상 파일 변경 수

- **신규**: ~16 (orchestration 4 + tests 3 + ADR 3 + validations 2 + retrospective + smoke + closing_notes)
- **수정**: ~12 (plans.py + sse.py + critic.py + contracts 2~3 + scenario_sim + patterns + skill_usage + state docs)
- **금지 (0줄)**: 2 (PlanCard.tsx, component_map.md)
- **예상 LOC**: ~+1800 신규 / ~−250 (god-function 분해로 plans.py 축소) / ~+300 수정

## 제외 (Out-of-Scope) → `non_goals.md`
