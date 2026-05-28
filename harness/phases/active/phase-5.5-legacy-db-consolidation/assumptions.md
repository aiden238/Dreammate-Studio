# Phase 5.5 — Assumptions (phase-start v1.3.0 §6 4점검)

> 작성: 2026-05-29
> 결과: ✅ **4-check 통과**

---

## §6.1 Assumptions

### 1.1 확정 가정 (C1~C8)

| ID | 항목 | 근거 |
|---|---|---|
| C1 | **audit_naming PASS 0 drift (2026-05-29 entry)** | scripts/audit_naming.ps1 실행 |
| C2 | Phase 5 baseline 완전 유지 — pytest 170/170 + smoke 12/12 + scenario_sim v2 10/10 + P-X1 22연속 | Phase 5 Slice 5 결과 |
| C3 | Legacy DB 인프라 (Phase 1 `db/supabase_client.py` + `save_video_planning`)와 Phase 5 신규 (`db/client.py` + `plans_repo`) 두 layer **공존 유지** 결정 — 단순 통합보다 안전 (회귀 0 보장) | 사용자 결정 1 + ADR-023 |
| C4 | external validation 강화 = Claude Code self-strengthen (사용자가 외부 GPT/Gemini 진행 시 추가 가능 유지) | 사용자 결정 2 |
| C5 | Phase 7 RAG candidate_knowledge 5단계 MVP **전부 구현** 결정 (사용자 결정 4) — 추정 시간 12~16h, ADR-024에 명시 | 사용자 결정 4 |
| C6 | Brand Memory 자동 추출 **Phase 9+** 이관 confirmation | 사용자 결정 5 |
| C7 | PlanCard.tsx + component_map.md 0줄 보존 가능 — 본 phase는 코드 변경 최소 (legacy DB 통합 외) | 자동 보장 |
| C8 | contract-change / security-review / agent-io-check / design-review / multi-llm-validation Skill **미호출** — 본 phase는 ADR + 문서 작성 중심 | 위 |

### 1.2 불확실 항목 (U1~U4)

| ID | 항목 | 검증 시점 |
|---|---|---|
| U1 | Legacy `save_video_planning` orchestrator와 Phase 5 `plans_repo` 인터페이스가 future-compat한가 | Slice 2 pytest |
| U2 | external validation self-strengthen이 외부 검토 결과를 충분히 대체 가능한가 | Phase 7+ 진입 시 재평가 |
| U3 | Phase 7 RAG 5단계 MVP 추정 시간 (12~16h)이 정확한가 | Phase 7 진입 시 plan에서 재추정 |
| U4 | Brand Memory Phase 9+ 이관 시 4계층 schema에 미리 brand_memory 컬럼 placeholder 필요 여부 | Phase 9+ 진입 시 결정 |

### 1.3 Contract cross-reference

- audit_naming entry: PASS 0 drift
- 신규 명명 점검:
  - `phase_5_5_legacy_db_consolidation` (snake_case, ADR-023)
  - `phase_7_rag_scope_evolution` (snake_case, ADR-024)
  - `P-LEGACY-CONSOLIDATION-001` (패턴 명명 표준)
  - 모두 NAMING_POLICY 정합

---

## §6.2 Simplest Slice (3회 압축)

**1차**: "Legacy DB 통합 + 3 validation 강화 + Phase 7 진화 문서 + Brand Memory 이관 확인 + 회고"

**2차**: "ADR-023 + ADR-024 + 3 validation 강화 (각 V1~V형식)"

**3차**:
```markdown
# docs/decisions/phase_5_5_legacy_db_consolidation.md
Context: Phase 1 + Phase 5 두 DB layer 공존
Decision: 공존 유지 + deprecated note (Phase 7+ 실 통합 결정 미루기)
```

→ **Slice 2 첫 30분 산출물**. 이후 ADR-024 + validation 3개 강화 확장.

---

## §6.3 Surgical Scope

### Editable
```
backend/fastapi/db/{supabase_client.py, save_video_planning.py, __init__.py}  (legacy 소폭 — wrapper 또는 deprecated note)
backend/fastapi/tests/test_db.py  (필요 시 회귀 보강)
docs/decisions/phase_5_5_legacy_db_consolidation.md  (ADR-023 신규)
docs/decisions/phase_7_rag_scope_evolution.md  (ADR-024 신규)
meta/validations/2026-05-28_phase-4.5-pre-entry_external.md  (self-strengthen)
meta/validations/2026-05-29_phase-6-pre-entry_external.md  (self-strengthen)
meta/validations/2026-05-29_phase-5-pre-entry_external.md  (self-strengthen)
meta/retrospectives/phase-5.5.md  (신규)
meta/patterns.md
meta/skill_usage_log.md
phases/active/phase-5.5-*/* (entry는 main 작성, 수정 X — notes.md만 갱신)
PROJECT_STATE / PHASE_REGISTRY / 00_START_HERE / README × 2
```

### Read-Only
```
docs/contracts/*  (수정 없음)
backend/fastapi/db/client.py (Phase 5 baseline)
backend/fastapi/db/repositories/plans_repo.py (Phase 5 baseline)
backend/fastapi/db/migrations/*  (Phase 5 baseline)
backend/fastapi/agents/*, schemas/*, routers/*, middleware/*  (모든 baseline 보존)
apps/web/*  (Phase 5 baseline)
모든 기존 ADR (ADR-014~022)
```

### Forbidden (절대 금지)
```
apps/web/components/PlanCard.tsx ★ (18연속 0줄)
apps/web/component_map.md ★ (28연속 0줄)
backend/fastapi/agents/* (Phase 6 canonical baseline)
backend/fastapi/schemas/output.py (Phase 6 canonical)
backend/fastapi/routers/* (Phase 5 baseline)
backend/fastapi/middleware/* (Phase 5)
backend/fastapi/db/client.py + repositories/plans_repo.py + migrations/* (Phase 5 보존)
backend/fastapi/tests/{test_critic, test_rewriter, test_schema_stress, test_plans, test_3_plan, test_auth, test_rls, test_sse, test_intent, test_rag, ...}.py (baseline)
docs/contracts/* (수정 금지 — ADR만 신규)
docs/decisions/{phase_4_5_*, phase_6_*, phase_5_*}.md (이전 ADR 보존)
scripts/audit_*.ps1, scenario_simulation.ps1, schema_stress_test.ps1, smoke_test_phase_4_5/6/5.ps1
.claude/skills/* (수정 금지)
phases/archive/*
meta/security_reviews/* (Phase 5 산출물 보존)
```

### Sub-agent SELF-VERIFICATION (P-X1) 의무

기존 패턴 유지.

**Main session 사후 검증**: 
```bash
git diff HEAD~1 HEAD --stat | grep -E "PlanCard|component_map|agents/|schemas/|routers/|middleware/|db/(client|repositories|migrations)|test_(critic|rewriter|schema_stress|plans|3_plan|auth|rls|sse)|contracts/|decisions/(phase_4_5|phase_6|phase_5_supabase|phase_5_rls|phase_5_sse)|audit_|scenario_simulation|schema_stress_test|smoke_test_phase_(4_5|6|5)|skills/|archive/" = 0 lines
```

---

## §6.4 Verification

| Acceptance | 검증 | 자동 |
|---|---|---|
| A1 ADR-023 | string match | 반자동 |
| A2 pytest 회귀 0 | pytest | 자동 |
| A3 3 validation 강화 | string match (V1~V6 항목 존재) | 자동 |
| A4 ADR-024 | string match | 반자동 |
| A5 Brand Memory NG2 | non_goals.md grep | 자동 |
| A6 0줄 baseline | git diff --stat | 자동 |
| A7 audit | scripts | 자동 |
| A8 smoke + scenario_sim 유지 | scripts | 자동 |

자동 6 + 반자동 2 = 8/8 자동화.

---

## §6 결과: ✅ 4-check 통과

**다음 단계**: Slice 1 sub-agent dispatch.
