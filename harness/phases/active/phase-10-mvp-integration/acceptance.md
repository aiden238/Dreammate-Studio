# Phase 10 — Acceptance (A1~A10 + MG1~MG4)

| ID | 항목 | 검증 | Slice |
|---|---|---|---|
| **A1** | MVP end-to-end 통합 테스트 — 전체 흐름(Discovery+Quick→3안→Critic revise canonical→save→select→feedback→SSE) 자동 PASS | test_integration_mvp.py green | S1 |
| **A2** | Phase 1~9.5 누적 baseline 통합 회귀 — pytest 339 유지(기존 수정 0) + smoke + scenario_sim v8 | pytest + smoke_test_phase_10 + scenario_sim | S1 |
| **A3** | P-AUX-2 brand_memory_extractor agent 실 구현 — feedback → brand memory 추출 + graceful + PII 마스킹 | test_brand_memory_extractor green | S2 |
| **A4** | P-AUX-2 agent_io_contract 정식 등록 (CC-008) + agent-io-check 정합 | contract + agent-io-check | S2 |
| **A5** | 실 LLM eval mode 정식화 (capability) — mode flag 실 경로 wire + 문서. ★ default mock | eval mode flag + 문서 + default mock 확인 | S3 |
| **A6** | RAG eval_rubric golden_set 정식화 + golden_set 11→확대 (CC-009) | eval contracts + golden_set N>11 | S3 |
| **A7** | eval-run 회귀 (mock) PASS — 임계값 게이트 통과 | regression_results/phase-10 | S3 |
| **A8** | 배포 테스트 게이트 A~G 준비 문서 | deploy_test_gates.md A~G | S4 |
| **A9-PP** | behavior-preserving — 기존 endpoint/test 동작 불변 (신규 추가만) | pytest 기존 339 수정 0 + Envelope 불변 | 전 Slice |
| **A10** | 결과 요약 — 변경 파일 + 통합 결과 + 배포 준비 상태 + 다음 phase | closing_notes + 보고 | S4 |

## MG1~MG4 (메타)
| ID | 항목 | 검증 |
|---|---|---|
| **MG1** | multi-llm-validation formal 열 번째 (통합 + P-AUX-2 IO + eval mode 경계) + external | meta/validations V1~V? |
| **MG2** | contract-change CC-008(agent_io P-AUX-2) + CC-009(eval golden_set/RAG rubric) | docs/contract_changes |
| **MG3** | P-X1 §SELF-VERIFICATION 연속 유지 (57 + Slice 수) | sub-agent 검사 |
| **MG4** | pytest 339 → 확대 (+신규, 기존 수정 0) + eval gate PASS | pytest + eval |

## ★ behavior-preserving 게이트 (A9-PP — 제품 phase 핵심)
```
신규만 추가 — 기존 endpoint 응답 schema / 기존 test 수정 0
검증: pytest 기존 339 전부 green (신규 추가분만 증가) + 통합 테스트가 기존 흐름을 깨지 않음
P-AUX-2 agent: 기존 MOA 흐름에 additive (orchestrator 경유, 기존 응답 불변 — Phase 9 적재 경로 활성화일 뿐)
```

## ★ eval mode 경계 (A5 — 사용자 결정)
```
실 LLM eval mode = capability 정식화 (mode flag 실 경로 + 문서) — default OFF
CI/게이트 실행 = mock-deterministic (비용 0)
실 LLM run = opt-in (OPENAI/ANTHROPIC 키 사용자 제공 시) — Phase 10 CI 미실행
★ 실제 키/자격증명 파일 커밋 금지 (.env user-provided)
```

## 회귀 baseline (Phase 9.5/M-detour → Phase 10)
| 지표 | 직전 | Phase 10 목표 |
|---|---|---|
| pytest | 339 | **339 + 신규** (기존 수정 0) |
| smoke | 16 (9.5) | smoke_test_phase_10 (통합) |
| scenario_sim | v7 33 (M0) | **v8 +통합 시나리오** |
| eval gate | 9.5 baseline | phase-10 mock 회귀 PASS |
| P-X1 streak | 57 (M3) | **57 + Slice 수** |
| PlanCard / component_map 0줄 | 35 / 45 | **유지** (page 레벨 통합, 신규 컴포넌트 0) |
| Skill 수 | 21 | 21 유지 |
| agent 수 | (Intent/Planning/Critic/Rewriter + RAG) | **+P-AUX-2 brand_memory_extractor** |

## qa-check (Phase 10 — release gate 본격)
- 1 제품/범위 / 2 AI 구조(P-AUX-2) / 3 RAG(rubric) / 4 프론트(page 통합) / 5 평가(eval mode + golden_set) / 6 메타 / 7 컨텍스트 / 8 큰 결정(multi-llm) / 9 Phase 운영 / 10 보안(brand memory PII) / 11 비용(mock — 0) — **다수 PASS 예상 (통합 release gate)**.
