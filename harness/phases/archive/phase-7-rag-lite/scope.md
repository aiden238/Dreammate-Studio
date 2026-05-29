# Phase 7 — Scope

## 포함 (In-Scope)

### Contracts (contract-change Skill)

| 파일 | 작업 |
|---|---|
| `docs/contracts/rag_data_contract.md` | **수정** — 5단계 stage enum + promotion_history JSONB + retrieval 정책 정식 등록 |
| `docs/contracts/api_contract.md` | **수정** (선택) — RAG search/promote endpoint 추가 시 |
| `docs/contracts/output_schema.md` | **참조만** (Phase 6 canonical 그대로) |

### Backend (backend/fastapi/)

| 파일 | 작업 |
|---|---|
| `rag/__init__.py` | **신규** — RAG layer export |
| `rag/promotion.py` | **신규** — 5단계 transition logic + promotion_history |
| `rag/quality_filter.py` | **신규** — PII + 인젝션 + 광고적 표현 필터 |
| `rag/eval_rubric.py` | **신규** — 간이 eval rubric (Phase 9+ 정식화 전) |
| `rag/embedding.py` | **신규** — OpenAI embedding wrapper (graceful) |
| `rag/retrieval.py` | **신규** — pgvector cosine + top-k=5 + threshold=0.7 |
| `rag/chunking.py` | **신규** — 512 tokens 표준 chunker |
| `rag/llm_wiki.py` | **신규** — 정적 지식 wrapper (LLM Wiki vs RAG 분리) |
| `db/migrations/0004_rag_5stage.sql` | **신규** — candidate_knowledge + approved_knowledge 테이블 + pgvector extension |
| `agents/rag.py` | **수정** — Phase 1 baseline → RAG Lite 통합 (graceful) |
| `routers/plans.py` | **수정** (소폭) — RAG 호출 통합 (graceful fallback 유지) |
| `routers/rag.py` | **신규** (선택) — RAG search/promote 관리 endpoint |
| `config.py` | **수정** — RAG 관련 환경변수 (embedding model, top-k, threshold) |
| `tests/test_rag_promotion.py` | **신규** — 5단계 전환 케이스 |
| `tests/test_rag_retrieval.py` | **신규** — pgvector mock + top-k + threshold |
| `tests/test_rag_quality_filter.py` | **신규** — PII + 인젝션 + 광고 |
| `tests/test_rag_chunking.py` | **신규** — 512 tokens 표준 |
| `tests/test_rag_integration.py` | **신규** — end-to-end RAG flow |
| 모든 baseline tests | **수정 X** (Phase 5.5 172/172 보존) |

### Knowledge (참조 + 갱신)

| 파일 | 작업 |
|---|---|
| `knowledge/rag/promotion_rule.md` | **수정** (선택) — 5단계 명세 강화 |
| `knowledge/rag/retrieval_policy.md` | **수정** (선택) — top-k + threshold 명시 |
| `knowledge/rag/quality_filter.md` | **참조만** |
| `knowledge/rag/metadata_schema.md` | **참조만** |
| `knowledge/llm_wiki/index.md` | **참조만** (LLM Wiki vs RAG 분리 baseline) |

### Frontend (apps/web/)

| 파일 | 작업 |
|---|---|
| 모두 | **수정 X** (RAG는 backend 작업 중심, frontend는 영향 0) |
| `components/PlanCard.tsx` | **수정 절대 금지** ★ — 19연속 |
| `component_map.md` | **수정 절대 금지** ★ — 29연속 |

### Meta / Scripts / Docs

| 파일 | 작업 |
|---|---|
| `meta/validations/2026-05-29_phase-7-pre-entry_self.md` | **신규** (M1) |
| `meta/validations/2026-05-29_phase-7-pre-entry_external.md` | **신규** (M1) |
| `docs/decisions/phase_7_rag_architecture.md` | **신규** — ADR-025 |
| `docs/decisions/phase_7_promotion_logic.md` | **신규** — ADR-026 |
| `docs/decisions/phase_7_quality_filter.md` | **신규** (선택) — ADR-027 |
| `scripts/smoke_test_phase_7.ps1` | **신규** — 13 체크 |
| `scripts/scenario_simulation.ps1` | **수정** — v3 (RAG 5단계 시나리오 5 추가) |
| `meta/retrospectives/phase-7.md` | **신규** |
| `meta/patterns.md` | **수정** — P-RAG-5STAGE-001 신규 + P-X1-EFFECT-001 update (31) |
| `meta/skill_usage_log.md` | **수정** — rag-design + rag-update 1 (첫 정식) |
| `PROJECT_STATE.md` / `PHASE_REGISTRY.md` / `00_START_HERE.md` / `README.md` × 2 | **수정** |

## 예상 파일 변경 수

- **신규**: ~25 (RAG layer 7 + tests 5 + ADR 2~3 + validations 2 + retrospective + scripts 1 + 1 migration)
- **수정**: ~10 (contracts 1~2 + agents/rag + routers/plans + config + scenario_sim + patterns + skill_usage + state docs × 5)
- **금지 (0줄)**: 2 (PlanCard.tsx, component_map.md)
- **예상 LOC**: ~+2500 신규 / ~+400 수정

## 제외 (Out-of-Scope) → `non_goals.md` 참조
