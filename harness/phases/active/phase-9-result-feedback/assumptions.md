# Phase 9 — Assumptions (phase-start v1.3.0 §6 4점검)

> 작성: 2026-05-29
> 결과: ✅ **4-check 통과**

---

## §6.1 Assumptions

### 1.1 확정 가정 (C1~C11)

| ID | 항목 | 근거 |
|---|---|---|
| C1 | audit_naming PASS 0 drift (entry) | scripts/audit_naming.ps1 |
| C2 | Phase 8 baseline 유지 (pytest 249 + smoke 14 + scenario_sim v4 20 + P-X1 36) | Phase 8 Slice 5 |
| C3 | **결과저장/피드백은 실 `plans` 테이블 정합** (plan_candidates JSONB + option_index 0–2). db_schema.md idealized plan_options는 Phase 11+ (NG2) | gap 분석 |
| C4 | **Brand Memory 준비만** (사용자 결정 5) — schema + ADR + 적재 경로. P-AUX-2 agent 미구현 (NG1) | 사용자 결정 |
| C5 | **피드백 UI는 page.tsx inline wrapper** (PlanCard·component_map 무수정) — 사용자 결정 (wrapper) | 사용자 결정 |
| C6 | **normalize_to_canonical wiring** (사용자 결정) — critic step canonical 추가, deprecated 0–5 병행 (회귀 0) | 사용자 결정 + Phase 8 개선 §1 |
| C7 | repo graceful (Supabase 실패 시 in-memory) — Phase 5 PlansRepo 패턴 | Phase 5 baseline |
| C8 | security-review 두 번째 정식 (피드백 reason PII) | M2 |
| C9 | normalize wiring은 schemas/output.py CriticEvaluation 불변 (이미 Optional canonical 보유) | Phase 6 ADR-018 |
| C10 | mock 환경 unit test (실 Supabase/OpenAI 호출 X) | Phase 4~8 pattern |
| C11 | 피드백 reason text는 llm_security PII 마스킹 baseline 적용 (Phase 1 + security-review) | llm_security_contract |

### 1.2 불확실 항목 (U1~U6)

| ID | 항목 | 검증 시점 |
|---|---|---|
| U1 | normalize wiring이 critic_evaluation 구조를 바꿔 깨는 baseline test 수 (의도된 delta 경계) | Slice 3 pytest (Phase 8 Slice 4 패턴 — 최소 assertion만) |
| U2 | selected_plans가 실 plans 테이블 + option_index로 충분한가 (4계층 미연결 NG2 영향) | Slice 2 + Phase 11+ |
| U3 | feedback reason text 저장 시 PII 마스킹 적용 시점 (저장 전 vs 조회 시) | Slice 1 security-review |
| U4 | feedback → candidate_knowledge 적재가 Phase 7 5단계 pending과 정합한가 | Slice 4 |
| U5 | 피드백 UI inline이 component_map 0줄 유지 가능한가 (신규 component 안 만들고) | Slice 5 |
| U6 | normalize wiring 후 best-plan(recommended_plan_index) 정확도 변화 | Slice 3 + Phase 9.5 eval |

### 1.3 Contract cross-reference
- audit_naming entry: PASS 0 drift
- 신규 명명: `selection_repo`/`feedback_repo`/`brand_memory_repo` (snake_case) · `SelectionRepo`/`FeedbackRepo`/`BrandMemoryRepo` (PascalCase) · `selected_plans`/`feedback_events` (snake_case 테이블) · `0005_feedback_selection` (migration) — 모두 NAMING_POLICY 정합

---

## §6.2 Simplest Slice (3회 압축)

**1차**: "결과저장 + 피드백 + Brand Memory 준비 + normalize wiring + 피드백 UI"
**2차**: "selected_plans 저장 + SelectionRepo graceful + POST /select"
**3차**:
```python
# backend/fastapi/db/repositories/selection_repo.py
class SelectionRepo:
    async def select(self, plan_id: str, option_index: int, reason: str | None = None) -> dict:
        # graceful: Supabase or in-memory (PlansRepo 패턴)
```
→ **Slice 2 첫 1시간 산출물**.

---

## §6.3 Surgical Scope

### Editable
```
backend/fastapi/db/migrations/0005_feedback_selection.sql (신규)
backend/fastapi/db/repositories/{selection_repo,feedback_repo,brand_memory_repo}.py (신규)
backend/fastapi/db/__init__.py (export)
backend/fastapi/rag/feedback_to_candidate.py (신규, 선택)
backend/fastapi/routers/plans.py (select/feedback endpoint)
backend/fastapi/orchestration/moa_orchestrator.py (normalize wiring — critic step)
backend/fastapi/schemas/plans.py (Select/Feedback Pydantic)
backend/fastapi/tests/test_{selection_feedback,plans_feedback_api,critic_canonical_wiring,brand_memory_prep}.py (신규)
apps/web/app/plan/[plan_id]/page.tsx (피드백 UI inline wrapper)
apps/web/lib/{api.ts, types.ts} (select/feedback)
docs/contracts/db_schema.md (contract-change)
docs/decisions/phase_9_{feedback_selection,brand_memory_prep,critic_canonical_wiring}.md (ADR-030/031/032)
meta/validations/2026-05-29_phase-9-pre-entry_{self,external}.md
meta/security_reviews/2026-05-29_phase-9-feedback-pii.md
scripts/{smoke_test_phase_9.ps1, scenario_simulation.ps1 v5}
meta/{retrospectives/phase-9.md, patterns.md, skill_usage_log.md}
PROJECT_STATE / PHASE_REGISTRY / 00_START_HERE / README
phases/active/phase-9-*/* (entry)
```

### Read-Only
```
docs/contracts/output_schema.md (CriticEvaluation canonical 불변 NG3)
backend/fastapi/schemas/output.py (Phase 6 canonical — 불변)
backend/fastapi/agents/critic.py (normalize_to_canonical helper 호출만, 변경 X)
backend/fastapi/db/{client,repositories/plans_repo,migrations/0001~0004}.* (Phase 5/7 baseline)
ai_system/prompts/prompt_registry.md (P-AUX-2 참조)
```

### Forbidden (절대 금지)
```
apps/web/components/plan/PlanCard.tsx ★ (0줄)
apps/web/component_map.md ★ (0줄 — 신규 component 등록 X)
backend/fastapi/schemas/output.py (Phase 6 canonical 불변 — NG3)
backend/fastapi/agents/{intent,planning,critic,rewriter,rag}.py (critic.py는 normalize_to_canonical 호출만, 로직 변경 X)
backend/fastapi/db/{client.py, repositories/plans_repo.py, migrations/0001~0004} (Phase 5/7 baseline)
backend/fastapi/routers/{auth,sse,generate}.py (Phase 5/8 baseline)
backend/fastapi/middleware/* (Phase 5)
모든 baseline test (normalize wiring 의도된 critic_evaluation delta만 — Phase 8 Slice 4 패턴, 최소 assertion)
docs/contracts/{output_schema,agent_io_contract,api_contract}.md (참조만 — db_schema만 contract-change)
이전 ADR (ADR-014~029)
scripts/audit_*.ps1, schema_stress_test.ps1, smoke_test_phase_4_5/5/6/7/8.ps1
.claude/skills/*, phases/archive/*, knowledge/*
```

### Sub-agent SELF-VERIFICATION (P-X1) — 모든 Slice 의무
Main 사후:
```bash
git diff HEAD~1 HEAD --stat | grep -E "PlanCard|component_map|schemas/output|agents/(intent|planning|critic|rewriter|rag)|db/(client|repositories/plans_repo|migrations/000[1-4])|routers/(auth|sse|generate)|middleware|output_schema|agent_io_contract|api_contract|decisions/(phase_4|phase_5|phase_6|phase_7|phase_8)|audit_|schema_stress|smoke_test_phase_(4_5|5|6|7|8)|skills/|archive/" = 0 lines (normalize wiring 의도 baseline delta 예외)
```

---

## §6.4 Verification
| Acceptance | 검증 | 자동 |
|---|---|---|
| A1~A7 | pytest (selection/feedback/canonical/brand_memory) | 자동 |
| A8 피드백 UI + 0줄 | next build + tsc + lint + git diff | 자동 |
| A9 audit | scripts | 자동 |
| A10 smoke 15 + scenario v5 25 | scripts | 자동 |
자동 10/10.

---

## §6 결과: ✅ 4-check 통과
**다음**: Slice 1 sub-agent — validations + security-review + ADR-030/031/032.
