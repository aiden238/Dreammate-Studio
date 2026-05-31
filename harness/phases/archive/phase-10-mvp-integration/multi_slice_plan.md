# Phase 10 — Multi-Slice Plan

> 4 Slice (sub-agent, sequential) + entry(main, multi-llm 10th) + close. 제품 phase — 런타임 변경 有, behavior-preserving.

## Wave 구조
```
entry (main) : 8 phase 파일 + multi-llm-validation formal 10th + external
  ↓
S1 [MVP end-to-end 통합 + 누적 baseline 회귀]        (sub-agent, tests + scripts)
  ↓
S2 [P-AUX-2 brand_memory_extractor agent 실구현]      (sub-agent, agents + contract-change CC-008 + tests)
  ↓
S3 [eval 정식화 — 실 LLM mode capability + RAG rubric + golden_set 확대]  (sub-agent, eval + CC-009 + eval-run 회귀)
  ↓
S4 [배포 게이트 A~G 준비 + Close]                     (sub-agent/main, docs + 회고 + archive)
```

## entry (main)
- 8 phase 파일 + `meta/validations/2026-05-31_phase-10-pre-entry_self.md` (V1~V?: 통합 범위 / P-AUX-2 additive 회귀 0 / eval mode 경계 default mock / behavior-preserving / golden_set 확대 / 배포 게이트) + external placeholder + entry commit.

## Slice 1 — MVP end-to-end 통합 + 누적 회귀 (sub-agent)
1. `tests/test_integration_mvp.py` — 전체 흐름 통합 (Discovery+Quick 분기 → 3안 → Critic revise canonical → save selected_plans → select → feedback PII → SSE progress). mock-deterministic.
2. `scripts/smoke_test_phase_10.ps1` — 통합 smoke (Phase 1~9.5 누적 + 신규 통합 흐름).
3. `scripts/scenario_simulation.ps1` v8 — S31~ MVP 통합 시나리오.
4. pytest 게이트 (339 + 신규, 기존 수정 0) + P-X1 + commit.
- editable: `backend/fastapi/tests/test_integration_mvp.py`, `scripts/{smoke_test_phase_10, scenario_simulation}`
- forbidden: 기존 endpoint/test 수정(behavior-preserving), apps/web/{PlanCard, component_map}, meta_factory, 영상 제작, eval contracts(S3), agents(S2)

## Slice 2 — P-AUX-2 brand_memory_extractor agent (sub-agent)
1. `agents/brand_memory_extractor.py` — feedback_events/selected_plans → brand memory 추출 (brand_memory_repo 적재). graceful + PII 마스킹. orchestrator 경유 additive (기존 흐름 불변).
2. `tests/test_brand_memory_extractor.py` — 추출 + graceful + PII.
3. **contract-change CC-008** — `agent_io_contract.md` P-AUX-2 IO 등록 + (가능 시) `prompt_registry.md` P-AUX-2 prompt (prompt-version-review).
4. agent-io-check 정합 + pytest 게이트 + P-X1 + commit.
- editable: `backend/fastapi/agents/brand_memory_extractor.py`, `tests/test_brand_memory_extractor.py`, `docs/contracts/agent_io_contract.md`, `ai_system/prompts/prompt_registry.md`, (필요 시 orchestrator additive hook)
- forbidden: 기존 agent 응답 변경(behavior-preserving), eval(S3), 통합 test(S1), 영상 제작

## Slice 3 — eval 정식화 (sub-agent)
1. `eval/runner.py`(또는 모드 모듈) — 실 LLM eval mode **경로 정식화** (mode flag wire). ★ default mock-deterministic, 실 LLM opt-in.
2. **contract-change CC-009** — `eval/golden_set.md` 11→확대 + `eval/rag_eval_rubric.md` 신규 (RAG eval_rubric 정식, Phase 9.5 NG1).
3. eval-run 회귀 (mock) → `eval/regression_results/phase-10_*.md` (임계값 게이트).
4. eval-design/eval-run + P-X1 + commit.
- editable: `backend/fastapi/eval/*`, `eval/{golden_set, rag_eval_rubric, regression_results}`
- forbidden: 실 LLM default 활성(NG2 — capability 만), 키 커밋, agents(S2), 통합 test(S1)

## Slice 4 — 배포 게이트 + Close
1. `docs/deploy_test_gates.md` — Deploy Test A~G 체크리스트/준비.
2. audit×2 + scenario_sim v8 + smoke_test_phase_10 + eval-run 실행 + qa-check(release gate) + agent-io-check + design-review(page 레벨, PlanCard 무수정 확인).
3. ADR(들) + 회고 + patterns + skill_usage_log + closing_notes.
4. phase-complete v1.2.0 (P-X2) + archive + state docs + final commit.

## 충돌 매트릭스
| Slice | tests/integration+scripts | agents/extractor+agent_io | eval/* | docs/deploy+meta+state |
|---|---|---|---|---|
| S1 | ✅ | ❌ | ❌ | ❌ |
| S2 | ❌ | ✅ | ❌ | ❌ |
| S3 | ❌ | ❌ | ✅ | ❌ |
| S4 | ❌ | ❌ | (회귀 실행) | ✅ |
Sequential 충돌 0.

## P-X1 streak
| Phase | streak |
|---|---|
| M3 | 57 |
| Phase 10 | +4 (S1·S2·S3·S4 목표) |
| 누적 | **61** |

## 시간 추정
entry 0.5h + S1 ~3h + S2 ~3h + S3 ~3h + S4 ~2h = **~11.5~15h** (large 제품 phase).
