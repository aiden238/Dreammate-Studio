# Phase 7 — Acceptance (A1~A10 + M1~M4)

## A1~A10

| ID | 항목 | 검증 |
|---|---|---|
| **A1** | candidate_knowledge 5단계 stage enum 정의 + DB schema migration (ADR-025) | `db/migrations/0004_rag_5stage.sql` + ADR-025 |
| **A2** | quality_filter (PII + 인젝션 + 광고적 표현 차단 단어) PASS | `pytest tests/test_rag_quality_filter.py` |
| **A3** | 간이 eval rubric (Phase 9+ 정식화 전까지) | `rag/eval_rubric.py` + tests |
| **A4** | promotion 5단계 transition logic + promotion_history JSONB | `pytest tests/test_rag_promotion.py` |
| **A5** | pgvector retrieval (top-k=5 + threshold=0.7) | `pytest tests/test_rag_retrieval.py` |
| **A6** | chunking 512 tokens 표준 + OpenAI embedding 통합 | `pytest tests/test_rag_chunking.py` |
| **A7** | LLM Wiki vs RAG 분리 명확 (static vs dynamic) + agents/rag.py 통합 | `rag/llm_wiki.py` + `pytest tests/test_rag_integration.py` + agent-io-check |
| **A8** | **PlanCard.tsx 19연속 0줄** + **component_map.md 29연속 0줄** | git diff badb2c0..HEAD --stat |
| **A9** | audit_naming + audit_page_component (0 drift + 2 intended WARN 유지) | scripts |
| **A10** | smoke_test_phase_7 13/13 PASS + scenario_simulation v3 15/15 PASS | scripts |

## M1~M4 (메타)

| ID | 항목 |
|---|---|
| **M1** | multi-llm-validation formal self V형식 + external placeholder |
| **M2** | **rag-design Skill ★ 첫 정식 트리거** (ADR-025) |
| **M3** | **rag-update Skill ★ 첫 정식 트리거** (5단계 승격 절차) |
| **M4** | P-X1 §SELF-VERIFICATION **31연속 PASS** (Phase 5.5:4 + Phase 7:5) |

## 회귀 baseline

| 지표 | Phase 5.5 | Phase 7 목표 |
|---|---|---|
| pytest | 172/172 | 195~210/195~210 (+25~40 신규) |
| smoke | 12/12 | **13/13** (RAG 1 추가) |
| scenario_simulation | v2 10/10 | **v3 15/15** (+5 RAG 시나리오) |
| schema_stress_test | 5/5 | 5/5 유지 |
| audit×2 | 0 drift + 2 intended WARN | 0 drift + 2 intended WARN |
| component_map.md 0줄 | 28 | **29연속** |
| PlanCard.tsx 0줄 | 18 | **19연속** |
| P-X1 streak | 26 | **31연속** |

## qa-check 카테고리

Phase 7 final 예상 활성:
- 1. 제품 / 범위 — PASS
- 2. AI 구조 (agent_io, output_schema) — PASS
- **3. RAG (정책 / 메타 / 품질)** — **PASS** (★ 첫 본격 활성화)
- 4. 프론트 / UX — PASS (회귀 0)
- 5. 평가 / 품질 — skip (eval-run Phase 9+)
- 6. 메타 개선 — PASS
- 7. 컨텍스트 — 필요 시
- 8. 큰 결정 / 교차검증 — PASS (multi-llm-validation + rag-design + contract-change)
- 9. Phase 운영 — PASS
- 10. 보안 / 인프라 — PASS (PII + 인젝션 + RLS Phase 5 baseline)
- 11. 비용 / 관측성 — skip (Phase 11+ cost-review)

**예상**: 9 PASS / 2 skip.
