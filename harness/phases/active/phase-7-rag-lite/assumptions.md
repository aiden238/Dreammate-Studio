# Phase 7 — Assumptions (phase-start v1.3.0 §6 4점검)

> 작성: 2026-05-29
> 결과: ✅ **4-check 통과**

---

## §6.1 Assumptions

### 1.1 확정 가정 (C1~C11)

| ID | 항목 | 근거 |
|---|---|---|
| C1 | audit_naming PASS 0 drift (entry) | scripts/audit_naming.ps1 |
| C2 | Phase 5.5 baseline 완전 유지 (pytest 172/172 + smoke 12/12 + scenario_sim v2 10/10 + P-X1 26연속) | Phase 5.5 Slice 4 결과 |
| C3 | **ADR-024 채택 그대로 적용** (candidate_knowledge 5단계 전부 + 추정 12~16h) | 사용자 결정 4 |
| C4 | Brand Memory **Phase 9+** 이관 그대로 (NG1) | 사용자 결정 5 |
| C5 | Supabase pgvector extension 사용 가능 (Phase 5 baseline 활용) | ADR-020 |
| C6 | OpenAI embedding API (`text-embedding-3-small`) 사용 가능 | Phase 4/4.5 OpenAI baseline |
| C7 | mock 환경 unit test 가능 (실 Supabase / OpenAI 호출 없이) | pytest pattern |
| C8 | graceful fallback 정신 유지 — RAG 실패 시 plan 생성 차단 X (warning 추가) | P-GRACEFUL-001 |
| C9 | LLM Wiki vs RAG 분리 명확 (static vs dynamic) | knowledge/llm_wiki/ + knowledge/rag/ baseline |
| C10 | PlanCard.tsx + component_map.md 0줄 보존 가능 (RAG는 backend 작업 중심) | 자동 보장 |
| C11 | rag-design Skill 첫 정식 트리거 가능 (절차 따름) | meta/skill_usage_log Phase 7 활성 예상 |

### 1.2 불확실 항목 (U1~U6)

| ID | 항목 | 검증 시점 |
|---|---|---|
| U1 | chunk size 512 tokens가 영상기획 도메인에 적절한가 (256? 1024?) | Slice 3 ADR-025 결정 + Phase 9+ eval로 재평가 |
| U2 | top-k=5 + threshold=0.7이 정확도/recall trade-off에 적절한가 | Slice 3 ADR-025 + Phase 9+ eval |
| U3 | 간이 eval rubric (3~5 dim)이 Phase 9+ 정식 rubric으로 자연 진화 가능한가 | Phase 9+ 진입 시 |
| U4 | 5단계 자동 transition (사용자 승인 미적용) 비율이 적절한가 — 자동 비율 너무 높으면 quality ↓ | Slice 4 + Phase 11+ |
| U5 | promotion_history JSONB 누적이 추후 검색 / 분석에 충분한가 (GIN 인덱스 미적용) | Phase 9+ |
| U6 | agents/rag.py 통합 시 routers/plans.py 호환 (회귀 0) 가능한가 | Slice 4 graceful |

### 1.3 Contract cross-reference

- audit_naming entry: PASS 0 drift
- 신규 명명 점검:
  - `candidate_knowledge` / `approved_knowledge` (snake_case 테이블)
  - `promotion_history` (snake_case JSONB)
  - `stage` ENUM('pending', 'filtered', 'evaluated', 'approved', 'promoted') (snake_case enum)
  - `chunk_size`, `top_k`, `threshold` (snake_case config)
  - `embedding_model` (snake_case)
  - 모두 NAMING_POLICY 정합

---

## §6.2 Simplest Slice (3회 압축)

**1차**: "5단계 promotion + retrieval + chunking + embedding + LLM Wiki + agents/rag.py + 통합"

**2차**: "candidate_knowledge 1 row pending → filtered → evaluated → approved → promoted transition 함수 1개"

**3차**:
```python
# backend/fastapi/rag/promotion.py
def transition(item: dict, target_stage: Literal["filtered", "evaluated", "approved", "promoted"]) -> dict:
    """단일 transition (현 stage → target_stage)."""
    item["stage"] = target_stage
    item.setdefault("promotion_history", []).append({"to": target_stage, "at": now()})
    return item
```

→ **Slice 2 첫 1시간 산출물**.

---

## §6.3 Surgical Scope

### Editable
```
backend/fastapi/rag/* (신규)
backend/fastapi/db/migrations/0004_rag_5stage.sql (신규)
backend/fastapi/agents/rag.py (수정)
backend/fastapi/routers/plans.py (소폭 수정)
backend/fastapi/routers/rag.py (선택 신규)
backend/fastapi/config.py (수정)
backend/fastapi/tests/test_rag_*.py (5 신규)
docs/contracts/rag_data_contract.md (수정 — contract-change)
docs/contracts/api_contract.md (선택 수정)
docs/decisions/phase_7_rag_architecture.md (ADR-025 신규)
docs/decisions/phase_7_promotion_logic.md (ADR-026 신규)
docs/decisions/phase_7_quality_filter.md (선택 ADR-027 신규)
knowledge/rag/promotion_rule.md (선택 수정 강화)
knowledge/rag/retrieval_policy.md (선택 수정)
meta/validations/2026-05-29_phase-7-pre-entry_self.md (신규)
meta/validations/2026-05-29_phase-7-pre-entry_external.md (신규)
meta/retrospectives/phase-7.md (신규)
meta/patterns.md
meta/skill_usage_log.md
scripts/smoke_test_phase_7.ps1 (신규)
scripts/scenario_simulation.ps1 (v3 수정 — 기존 v2 보존)
phases/active/phase-7-*/* (entry files)
PROJECT_STATE / PHASE_REGISTRY / 00_START_HERE / README × 2
```

### Read-Only
```
docs/contracts/output_schema.md (Phase 6 canonical)
docs/contracts/agent_io_contract.md (Phase 6 baseline, agents/rag.py 변경 시 v1.0.0 → v1.1.0 검토)
docs/contracts/llm_security_contract.md
backend/fastapi/agents/{intent, planning, critic, rewriter}.py (Phase 6 baseline)
backend/fastapi/schemas/output.py (Phase 6 canonical)
backend/fastapi/db/{client, repositories, migrations/0001/0002/0003}.* (Phase 5 baseline)
backend/fastapi/routers/{auth, sse}.py (Phase 5 baseline)
backend/fastapi/middleware/* (Phase 5 baseline)
backend/fastapi/db/{supabase_client, save_video_planning}.* (Phase 5.5 deprecated)
모든 baseline tests
모든 이전 ADR (ADR-014~024)
knowledge/llm_wiki/*, eval/*, ai_system/*
```

### Forbidden (절대 금지)
```
apps/web/components/PlanCard.tsx ★ (19연속 0줄)
apps/web/component_map.md ★ (29연속 0줄)
apps/web/* (모두, RAG는 backend 작업)
backend/fastapi/agents/{intent, planning, critic, rewriter}.py (Phase 6 baseline)
backend/fastapi/schemas/output.py (Phase 6 canonical)
backend/fastapi/db/{client, repositories/, migrations/0001/0002/0003}.* (Phase 5 baseline)
backend/fastapi/routers/{auth, sse}.py (Phase 5 baseline)
backend/fastapi/middleware/* (Phase 5)
모든 baseline tests (test_critic, test_rewriter, test_schema_stress, test_plans, test_3_plan, test_auth, test_rls, test_sse, test_db ...)
scripts/audit_*.ps1, scenario_simulation.ps1 (v2 기존 보존, v3 추가만), schema_stress_test.ps1, smoke_test_phase_4_5/5/6.ps1
.claude/skills/* (수정 금지)
phases/archive/*
이전 ADR (ADR-014~024) — ADR-025~027만 신규
docs/contracts/{output_schema, agent_io_contract, llm_security_contract, mvp_non_goals, db_schema, frontend_design_contract}.md (참조만)
```

### Sub-agent SELF-VERIFICATION (P-X1) 의무 — 모든 Slice

기존 패턴 유지. Main session 사후 검증:
```bash
git diff HEAD~1 HEAD --stat | grep -E "PlanCard|component_map|apps/web/|agents/(intent|planning|critic|rewriter)|schemas/output|db/(client|repositories|migrations/(0001|0002|0003))|routers/(auth|sse)|middleware|test_(critic|rewriter|schema_stress|plans|3_plan|auth|rls|sse|db)|contracts/(output_schema|agent_io|llm_security|mvp_non_goals|db_schema|frontend)|decisions/(phase_4_5|phase_6|phase_5_supabase|phase_5_rls|phase_5_sse|phase_5_5)|audit_|scenario_simulation\.ps1\$|schema_stress_test|smoke_test_phase_(4_5|5|6)\.ps1|skills/|archive/" = 0 lines
```

---

## §6.4 Verification

| Acceptance | 검증 | 자동 |
|---|---|---|
| A1 5단계 enum + migration | sql 파일 + ADR-025 | 반자동 |
| A2 quality_filter | pytest | 자동 |
| A3 eval rubric | pytest | 자동 |
| A4 promotion | pytest | 자동 |
| A5 retrieval | pytest | 자동 |
| A6 chunking + embedding | pytest | 자동 |
| A7 LLM Wiki vs RAG + agents/rag | agent-io-check + pytest | 자동 |
| A8 0줄 baseline | git diff | 자동 |
| A9 audit | scripts | 자동 |
| A10 smoke 13/13 + scenario_sim v3 15/15 | scripts | 자동 |

자동 8 + 반자동 2 = 10/10.

---

## §6 결과: ✅ 4-check 통과

**다음 단계**: Slice 1 sub-agent dispatch.
