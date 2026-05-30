# Phase 8 — Acceptance (A1~A10 + M1~M5)

## A1~A10

| ID | 항목 | 검증 | Slice |
|---|---|---|---|
| **A1** | MOA Orchestrator 추출 — `orchestration/moa_orchestrator.py::generate_plan()` 존재 | pytest `test_moa_orchestrator.py` | 2 |
| **A2** | router thin adapter화 — `plans_generate()` 가 orchestrator 호출 (god-function 분해) | plans.py LOC ▼ + orchestrator 위임 | 2 |
| **A3** | **Behavior-preserving** — 기존 pytest 223 수정 없이 PASS + Envelope byte-identical | `pytest backend/fastapi/tests/` 223 그대로 | 2 |
| **A4** | ProgressSink 인터페이스 — orchestrator stage별 emit (Null default 회귀 0) | pytest `test_moa_orchestrator.py::test_progress_sink_emits` | 2 |
| **A5** | progress_store 브릿지 — in-memory graceful store | pytest `test_sse_integration.py` | 3 |
| **A6** | SSE 실 stage read — sse.py가 progress_store 읽음 + graceful fallback | pytest `test_sse_integration.py` + 기존 test_sse 유지 | 3 |
| **A7** | prompt_registry semver 정식화 + Critic v1.1.0 adapter + 상수 정합 | pytest `test_prompt_registry_consistency.py` + agent-io-check | 4 |
| **A8** | **PlanCard.tsx 0줄 + component_map.md 0줄** (backend-only) | git diff entry..HEAD --stat | 5 |
| **A9** | audit_naming 0 drift + audit_page_component 2 intended WARN 유지 | scripts | 5 |
| **A10** | smoke_test_phase_8 14/14 PASS + scenario_sim v4 20/20 PASS | scripts | 5 |

## M1~M5 (메타)

| ID | 항목 |
|---|---|
| **M1** | multi-llm-validation formal self V형식 + external placeholder (다섯 번째 트리거) |
| **M2** | **ai-architecture-review Skill ★ 첫 정식 트리거** (MOA orchestration 설계, ADR-027) |
| **M3** | **prompt-version-review Skill ★ 첫 정식 트리거** (P-007 semver, ADR-029) |
| **M4** | P-X1 §SELF-VERIFICATION **36연속 PASS** (Slice 1~5 모두) |
| **M5** | contract-change Skill (agent_io_contract + prompt_registry) |

## 회귀 baseline (Phase 7 → Phase 8)

| 지표 | Phase 7 | Phase 8 목표 |
|---|---|---|
| pytest | 223/223 | 245~255 (+22~32 신규, 기존 223 수정 0) |
| smoke | 13/13 | **14/14** (smoke_test_phase_8: MOA 1 추가) |
| scenario_simulation | v3 15/15 | **v4 20/20** (+5 MOA 시나리오) |
| schema_stress_test | 5/5 | 5/5 유지 |
| audit_naming | 0 drift | 0 drift |
| audit_page_component | 2 intended WARN | 2 intended WARN |
| component_map.md 0줄 | 29 | **유지** (backend-only, +5 → 34) |
| PlanCard.tsx 0줄 | 19 | **유지** (backend-only, +5 → 24) |
| P-X1 streak | 31 | **36** |

## qa-check 카테고리 (Phase 8 final 예상)

- 1. 제품/범위 — PASS
- **2. AI 구조 (agent_io, output_schema, MOA orchestration)** — **PASS** (핵심)
- 3. RAG — PASS (회귀 0)
- 4. 프론트/UX — PASS (변경 0)
- 5. 평가 — skip (eval-run Phase 9+)
- 6. 메타 — PASS
- 7. 컨텍스트 — 필요 시
- 8. 큰 결정 — **PASS** (ai-architecture-review + prompt-version-review + multi-llm-validation + contract-change)
- 9. Phase 운영 — PASS
- 10. 보안/인프라 — PASS (회귀 0, SSE Origin 유지)
- 11. 비용/관측성 — skip (Phase 11+)

**예상**: 9 PASS / 2 skip.
