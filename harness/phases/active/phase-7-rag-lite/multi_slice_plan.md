# Phase 7 — Multi-Slice Plan

> 5 Slice 모두 sub-agent dispatch, sequential
> 총 12~16h

---

## Wave 구조

```
Wave 1: Slice 1 [Pre-Entry — validations + rag-design Skill 첫 정식 + ADR-025/026]
  ↓
Wave 2: Slice 2 [RAG 5단계 Schema + Core — contract-change + migrations + promotion + quality_filter + eval_rubric]
  ↓
Wave 3: Slice 3 [Retrieval + Embedding — pgvector + chunking + embedding]
  ↓
Wave 4: Slice 4 [Promotion + LLM Wiki + 통합 — rag-update Skill 첫 정식 + agents/rag + routers/plans 통합]
  ↓
Wave 5: Slice 5 [Close — smoke + scenario_sim v3 + 회고 + archive]
```

---

## Slice 1 — Pre-Entry (1.5~2h)

### 작업 단위
1. `meta/validations/2026-05-29_phase-7-pre-entry_self.md` 신규 — Claude Code 자가 검증 V1~V7:
   - V1 ADR-024 5단계 채택 정합 (Phase 5.5 결정 확인)
   - V2 chunk size 512 tokens 적절성
   - V3 top-k=5 + threshold=0.7 정합
   - V4 OpenAI embedding model (`text-embedding-3-small`) 채택
   - V5 graceful fallback 정신 (RAG 실패 시 plan 차단 X)
   - V6 LLM Wiki vs RAG 분리 명확
   - V7 5단계 자동/수동 승인 정책 (간이 eval rubric)
2. `meta/validations/2026-05-29_phase-7-pre-entry_external.md` 신규 (placeholder, Phase 4.5/6/5/5.5 패턴 계승)
3. **rag-design Skill ★ 첫 정식 트리거** — RAG architecture 결정 문서화
4. `docs/decisions/phase_7_rag_architecture.md` 신규 (ADR-025):
   - Context: Phase 7 RAG Lite scope (ADR-024 기반)
   - Decision: chunking 512 + embedding `text-embedding-3-small` + retrieval cosine + top-k=5 + threshold=0.7 + LLM Wiki vs RAG 분리
   - Constraints: graceful fallback, pgvector extension 활용
   - Alternatives: chunk size 256/1024 비교, embedding model 비교
5. `docs/decisions/phase_7_promotion_logic.md` 신규 (ADR-026):
   - 5단계 transition 규칙
   - 간이 eval rubric (3~5 dim — relevance / clarity / safety)
   - 사용자 승인 정책 (자동 transition vs 수동 승인 기준)
   - promotion_history JSONB schema
6. `meta/skill_usage_log.md` 갱신:
   - phase-start +1 (10)
   - multi-llm-validation +1 (5, formal 네 번째)
   - **rag-design 0 → 1 (첫 정식 트리거)**
7. `PROJECT_STATE.md` 갱신 (phase_7_* 필드 + active phase)
8. **entry commit**: "feat(phase-7): Slice 1 entry — rag-design Skill 첫 정식 + ADR-025/026 + validations V1~V7"

### 영향 파일 (~5 신규 + 2 수정)

### Sub-agent prompt 핵심
- editable: meta/validations/*, docs/decisions/phase_7_rag_architecture.md, docs/decisions/phase_7_promotion_logic.md, meta/skill_usage_log.md, PROJECT_STATE.md, phases/active/phase-7-*/notes.md
- forbidden: backend/* (Slice 2~4 영역), apps/web/*, scripts/*, docs/contracts/* (Slice 2 contract-change), 이전 ADRs, .claude/skills/*, archive/*, entry files (notes 외)
- P-X1 의무

---

## Slice 2 — RAG 5단계 Schema + Core (3~4h)

### 작업 단위
1. **contract-change Skill 호출** — `docs/contracts/rag_data_contract.md` 갱신:
   - 5단계 stage enum 정식 등록
   - promotion_history JSONB schema
   - retrieval 정책 (top-k + threshold)
2. `backend/fastapi/db/migrations/0004_rag_5stage.sql` 신규:
   - CREATE EXTENSION IF NOT EXISTS vector
   - `candidate_knowledge` 테이블 (id, content, stage ENUM, metadata JSONB, embedding vector(1536), auth_user_id NULL, created_at, updated_at, promotion_history JSONB)
   - `approved_knowledge` 테이블 (id, content, source_candidate_id FK, metadata JSONB, embedding vector(1536), promoted_at)
   - RLS 정책 (auth_user_id 분리, anonymous 검색 가능)
   - GIN index on promotion_history (선택, Phase 9+ 도입 가능성 명시)
   - ivfflat index on embedding
3. `backend/fastapi/rag/__init__.py` 신규 — layer export
4. `backend/fastapi/rag/promotion.py` 신규 — 5단계 transition logic:
   - `transition(item, target_stage)` 함수
   - `pending → filtered`: quality_filter 통과 조건
   - `filtered → evaluated`: eval_rubric 통과 조건
   - `evaluated → approved`: 사용자 승인 또는 자동 임계
   - `approved → promoted`: approved_knowledge 테이블 이동
   - promotion_history 누적 + timestamp
5. `backend/fastapi/rag/quality_filter.py` 신규 — PII + 인젝션 + 광고적 표현:
   - PII pattern (이메일 / 전화번호 / 주민번호 등)
   - 인젝션 차단 (Phase 1 baseline 패턴)
   - 광고적 표현 차단 단어 list (확정 결정 [9])
6. `backend/fastapi/rag/eval_rubric.py` 신규 — 간이 rubric:
   - relevance / clarity / safety 3~5 dim
   - 각 0.0~1.0 점수
   - 종합 threshold 0.6 이상 PASS
7. `backend/fastapi/tests/test_rag_promotion.py` 신규 (5단계 transition 5+ 케이스)
8. `backend/fastapi/tests/test_rag_quality_filter.py` 신규 (PII + 인젝션 + 광고 3+ 케이스)
9. **commit**: "feat(phase-7): Slice 2 — RAG 5단계 schema + core (contract-change + migrations + promotion + quality_filter)"

### 영향 파일 (~7 신규 + 1 수정 contract)

### Sub-agent prompt 핵심
- editable: backend/fastapi/rag/{__init__, promotion, quality_filter, eval_rubric}.py, db/migrations/0004_rag_5stage.sql, tests/test_rag_{promotion, quality_filter}.py, docs/contracts/rag_data_contract.md
- forbidden: Slice 3/4 영역 (rag/{embedding, retrieval, chunking, llm_wiki}.py, agents/rag.py, routers/plans.py, config.py 추가 X — Slice 3에서), Phase 5/6 baseline, apps/web/*, PlanCard, component_map, 이전 ADRs, scripts, skills, archive
- contract-change Skill 절차 따름
- P-X1 의무

---

## Slice 3 — Retrieval + Embedding (3~4h)

### 작업 단위
1. `backend/fastapi/rag/embedding.py` 신규 — OpenAI embedding wrapper:
   - `embed(text: str, model: str = "text-embedding-3-small") -> list[float]` (1536 dim)
   - graceful: 실패 시 None + warning
2. `backend/fastapi/rag/chunking.py` 신규 — 512 tokens 표준:
   - `chunk(text: str, size: int = 512, overlap: int = 50) -> list[str]`
3. `backend/fastapi/rag/retrieval.py` 신규 — pgvector cosine:
   - `search(query: str, top_k: int = 5, threshold: float = 0.7) -> list[dict]`
   - pgvector cosine distance 활용 (`<=>` operator)
   - graceful fallback (Supabase 미설정 시 빈 list + warning)
4. `backend/fastapi/config.py` 수정 — RAG 환경변수:
   - `rag_embedding_model: str = "text-embedding-3-small"`
   - `rag_chunk_size: int = 512`
   - `rag_chunk_overlap: int = 50`
   - `rag_top_k: int = 5`
   - `rag_threshold: float = 0.7`
5. `backend/fastapi/tests/test_rag_chunking.py` 신규 (512 + overlap 3+ 케이스)
6. `backend/fastapi/tests/test_rag_retrieval.py` 신규 (pgvector mock + top-k + threshold 3+ 케이스)
7. `backend/fastapi/tests/test_rag_embedding.py` 신규 (OpenAI mock + graceful 2+ 케이스)
8. **commit**: "feat(phase-7): Slice 3 — retrieval + embedding + chunking (pgvector cosine + top-k=5 + 512 tokens)"

### 영향 파일 (~6 신규 + 1 수정 config)

### Sub-agent prompt 핵심
- editable: backend/fastapi/rag/{embedding, chunking, retrieval}.py, config.py, tests/test_rag_{chunking, retrieval, embedding}.py
- forbidden: Slice 2 영역 (rag/{promotion, quality_filter, eval_rubric}.py, db/migrations/0004, docs/contracts/rag_data_contract.md), Slice 4 영역 (rag/llm_wiki.py, agents/rag.py, routers/plans.py), Phase 5/6 baseline, apps/web/*, PlanCard, component_map, scripts, skills, archive
- P-X1 의무

---

## Slice 4 — Promotion + LLM Wiki + 통합 (2~3h)

### 작업 단위
1. `backend/fastapi/rag/llm_wiki.py` 신규 — 정적 지식 wrapper:
   - 정적 LLM Wiki 항목 in-memory cache
   - `lookup(topic: str) -> dict | None` — static lookup
   - LLM Wiki vs RAG 분리 (LLM Wiki = static / RAG = dynamic candidate_knowledge)
2. **rag-update Skill ★ 첫 정식 트리거** — 5단계 승격 절차 강제 적용 (Skill 절차 따름):
   - meta/rag_updates/2026-05-29_phase-7-initial-promotion.md 또는 회고 본문 §rag-update 결과 기록
3. `backend/fastapi/agents/rag.py` 수정 — Phase 1 baseline → RAG Lite 통합:
   - 기존 stub or simple wrapper를 retrieval.search() 호출로 변환
   - graceful: RAG 실패 시 plan 생성 차단 X (warning + 빈 results)
4. `backend/fastapi/routers/plans.py` 수정 (소폭) — RAG 호출 통합:
   - 기존 `run_rag` 호출 패턴이 있으면 그대로 활용 (변경 최소)
   - validation.warnings에 `rag_unavailable` 마커 추가 (graceful)
5. (선택) `backend/fastapi/routers/rag.py` 신규 — 관리 endpoint:
   - `POST /api/v1/rag/promote` (수동 승인)
   - `GET /api/v1/rag/candidates?stage=pending` (검토 list)
6. `backend/fastapi/tests/test_rag_integration.py` 신규 — end-to-end:
   - chunking → embedding → promotion 5단계 → retrieval round-trip 3+ 케이스
   - graceful failure 통합 케이스
7. **commit**: "feat(phase-7): Slice 4 — promotion + LLM Wiki + agents/rag 통합 (rag-update Skill 첫 정식)"

### 영향 파일 (~3~4 신규 + 2~3 수정)

### Sub-agent prompt 핵심
- editable: backend/fastapi/rag/llm_wiki.py, agents/rag.py, routers/plans.py (소폭 — graceful), routers/rag.py (선택), tests/test_rag_integration.py, meta/rag_updates/* (선택)
- forbidden: Slice 2/3 산출물 (rag/{promotion, quality_filter, eval_rubric, embedding, chunking, retrieval}.py, db/migrations/0004), config.py (Slice 3 영역), Phase 5/6 baseline 모든 곳, apps/web/*, PlanCard, component_map, scripts, skills, archive, 이전 ADRs
- rag-update Skill 절차 따름
- P-X1 의무

---

## Slice 5 — Close (1~2h)

### 작업 단위
1. `scripts/smoke_test_phase_7.ps1` 신규 (13 체크: Phase 5 12 + RAG 1 추가)
2. `scripts/scenario_simulation.ps1` v3 (5 시나리오 추가):
   - S11: RAG 5단계 schema (db/migrations/0004 + rag_data_contract)
   - S12: chunking 변경 (rag/chunking.py + config)
   - S13: retrieval threshold 변경 (rag/retrieval.py + config)
   - S14: quality_filter 변경 (rag/quality_filter.py)
   - S15: LLM Wiki entry 추가 (rag/llm_wiki.py)
3. audit×2 final (0 drift + 2 intended WARN 유지)
4. design-review impl §B (frontend 변경 0 회귀 검증)
5. agent-io-check (agents/rag.py 변경 검증)
6. `meta/retrospectives/phase-7.md` 신규
7. `meta/patterns.md`:
   - P-X1-EFFECT-001 update (**31연속**)
   - **P-RAG-5STAGE-001 신규** (5단계 transition + promotion_history 패턴)
   - **P-RAG-GRACEFUL-001 신규** (RAG 실패 시 plan 생성 차단 X 패턴)
8. `meta/skill_usage_log.md` 갱신 (rag-design 1 + rag-update 1 + agent-io-check +1 + contract-change +1 + 기타)
9. phase-complete v1.2.0 (P-X2 다섯 번째 자동 게이트)
10. archive 이동: `phases/active/phase-7-*` → `phases/archive/phase-7-rag-lite/`
11. `closing_notes.md` (Phase 8 MOA Lite 또는 Phase 9 저장/피드백 권장)
12. PROJECT_STATE / PHASE_REGISTRY / 00_START_HERE / README × 2 갱신
13. **final commit**: "feat(phase-7): Slice 5 — close (P-X1 31연속 + rag-design + rag-update 첫 정식 + P-RAG-5STAGE-001)"

### 영향 파일 (~6 신규 + 7 수정 + archive)

### Sub-agent prompt 핵심
- editable: scripts/smoke_test_phase_7.ps1, scripts/scenario_simulation.ps1 (v3 추가, 기존 v2 보존), meta/retrospectives/phase-7.md, meta/patterns.md, meta/skill_usage_log.md, phases/archive/phase-7-* (이동), closing_notes.md, state docs × 5
- forbidden: backend/* (Slice 2~4 산출물 보존 + Phase 5/6 baseline), apps/web/*, PlanCard, component_map, docs/* (Slice 1~2 산출물 보존 + 이전), 이전 ADRs (ADR-025/026 보존), scripts/audit_* + schema_stress_test + smoke_test_phase_4_5/5/6, .claude/skills/* (수정 X)
- P-X1 의무

---

## 충돌 매트릭스 (Slice × 영향 영역)

| Slice | rag/promotion | rag/embedding/retrieval/chunking | rag/llm_wiki | agents/rag.py | routers/plans.py | migrations/0004 | contracts/rag_data | config | tests | docs/decisions | meta | scripts | state docs |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ ADR-025/026 | ✅ validations + skill_usage | ❌ | ✅ entry |
| 2 | ✅ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | ❌ | ✅ promotion + quality_filter | ❌ | ❌ | ❌ | ❌ |
| 3 | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ chunking + retrieval + embedding | ❌ | ❌ | ❌ | ❌ |
| 4 | ❌ | ❌ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ integration | ❌ | ✅ rag_updates (선택) | ❌ | ❌ |
| 5 | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ retrospective + patterns + skill_usage | ✅ smoke_test_phase_7 + scenario_sim v3 | ✅ all |

Sequential 진행 시 충돌 0.

---

## 누적 P-X1 streak 목표

| Phase | streak |
|---|---|
| Phase 3 | 5 |
| Phase 4 | 4 |
| Phase 4.5 | 4 |
| Phase 6 | 4 |
| Phase 5 | 5 |
| Phase 5.5 | 4 |
| Phase 7 | **5 (목표)** |
| **누적** | **31** |

---

## 시간 추정

| Slice | 시간 | 누적 |
|---|---|---|
| 1 | 1.5~2h | 1.5~2h |
| 2 | 3~4h | 4.5~6h |
| 3 | 3~4h | 7.5~10h |
| 4 | 2~3h | 9.5~13h |
| 5 | 1~2h | **10.5~15h** (ADR-024 추정 12~16h 정합) |
