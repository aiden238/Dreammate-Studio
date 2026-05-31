# Phase 10 — Scope (제품 phase — 런타임 변경 有)

## 포함 (In-Scope)

### S1 — MVP end-to-end 통합 + 누적 회귀
| 항목 | 작업 |
|---|---|
| `backend/fastapi/tests/test_integration_mvp.py` | **신규** — 전체 흐름 통합 테스트 (Discovery+Quick 분기 → 3안 생성 → Critic revise canonical → save(selected_plans) → select → feedback(PII 마스킹) → SSE progress). mock-deterministic (실 LLM 0) |
| `scripts/smoke_test_phase_10.ps1` | **신규** — 통합 smoke (Phase 1~9.5 누적 체크 통합 + 신규 통합 흐름) |
| `scripts/scenario_simulation.ps1` | **수정** — v8 (S31~ MVP 통합 시나리오) |

### S2 — P-AUX-2 brand_memory_extractor agent
| 항목 | 작업 |
|---|---|
| `backend/fastapi/agents/brand_memory_extractor.py` | **신규** — feedback_events/selected_plans → brand memory 추출 agent (Phase 9 brand_memory_repo 활성, ADR-031 설계 기반). graceful + PII 마스킹 계승 |
| `backend/fastapi/tests/test_brand_memory_extractor.py` | **신규** — 추출 로직 + graceful + PII 테스트 |
| `docs/contracts/agent_io_contract.md` | **수정 (contract-change CC-008)** — P-AUX-2 brand_memory_extractor IO 정식 등록 |
| `ai_system/prompts/prompt_registry.md` | **수정 (가능 시)** — P-AUX-2 prompt 등록 (prompt-version-review) |

### S3 — eval 정식화 (실행 default mock)
| 항목 | 작업 |
|---|---|
| `backend/fastapi/eval/runner.py` (또는 모드 모듈) | **수정** — 실 LLM eval mode **경로 정식화** (mode flag wire). ★ default mock-deterministic, 실 LLM 은 opt-in (키 제공 시) |
| `eval/golden_set.md` | **수정 (contract-change)** — 11 → 확대 (대표 케이스 추가) |
| `eval/rag_eval_rubric.md` (또는 rag eval 정식) | **신규 (contract-change)** — RAG eval_rubric golden_set 정식화 (Phase 9.5 NG1) |
| `eval/regression_results/phase-10_*.md` | **신규** — Phase 10 eval-run 결과 (mock) |

### S4 — 배포 게이트 + Close
| 항목 | 작업 |
|---|---|
| `docs/deploy_test_gates.md` (또는 deploy/) | **신규** — Deploy Test A~G 체크리스트/준비 문서 |
| 회고/patterns/skill_usage_log/state/archive | **doc-sync** |

## contract-change 대상 (MG2)
- agent_io_contract.md (P-AUX-2 IO) — CC-008
- golden_set.md (확대) + rag_eval_rubric (신규) — CC-009 (eval contracts)
- (가능 시) prompt_registry.md (P-AUX-2 prompt) — prompt-version-review

## ★ 변경 허용 / 금지
```
변경 허용 (editable):
  backend/fastapi/{agents/brand_memory_extractor, eval/*, tests/*}  (S1·S2·S3)
  scripts/{smoke_test_phase_10, scenario_simulation v8}
  eval/{golden_set, rag_eval_rubric, regression_results}            (contract-change)
  docs/contracts/agent_io_contract.md / prompt_registry.md          (contract-change)
  docs/deploy_test_gates.md / docs/decisions(ADR) / meta/** / state / phases/phase-10

변경 금지 (forbidden):
  ★ 영상 제작/편집·TTS·BGM 관련 (MVP 영구 non-goal)
  ★ 실 LLM eval default 활성 (capability 만 — default mock 유지)
  apps/web/components/PlanCard.tsx (35연속 0줄 — 통합 테스트는 wrapper/page 레벨)
  apps/web/component_map.md (45연속 0줄 — 신규 컴포넌트 없으면 무수정)
  meta_factory/** (Meta-Factory detour 종료 — 본 phase 무관)
  기존 endpoint 의 응답 schema 파괴적 변경 (behavior-preserving — 신규 추가만)
  4계층 full linkage / SSE async worker / prompt A/B (Phase 11+)
```

## 예상 변경 수
- 신규: ~10 (integration test + smoke + brand_memory_extractor + tests + eval rubric + deploy gates + ADR + regression_results)
- 수정: ~8 (scenario_sim v8 + eval/runner mode + golden_set + agent_io_contract + prompt_registry + state docs)
- pytest: 339 → 확대 (+신규, 기존 수정 0)
