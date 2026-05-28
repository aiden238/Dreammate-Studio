# Phase 6 — Assumptions (phase-start v1.3.0 §6 4점검 결과)

> 작성: 2026-05-29 (Phase 6 entry)
> 결과: ✅ **4-check 통과** — 진입 허용

---

## §6.1 Assumptions

### 1.1 확정 가정 (C1~C9)

| ID | 항목 | 근거 |
|---|---|---|
| C1 | **audit_naming PASS 0 drift (2026-05-29 entry)** | `scripts/audit_naming.ps1` 실행 결과 |
| C2 | Phase 4.5 baseline 유지 가능 | pytest 109/109 + smoke 9/9 + audit×2 0 drift + P-X1 13연속 |
| C3 | OpenAI API 환경 변화 없음 | Phase 4.5와 동일 |
| C4 | in-memory `_plan_store` 유지 가능 | NG5 (DB는 Phase 5) |
| C5 | PlanCard.tsx + component_map.md 0줄 보존 | NG6/NG7 (사용자 결정 6-a 정신 계승) |
| C6 | **contract 직접 수정 필요** — Phase 6 본질은 contract 안정화이므로 contract-change Skill 의무 호출 | Slice 2 |
| C7 | multi-llm-validation **formal self V1~V5** 가능 (지침 참조) | Phase 4.5 패턴 계승 |
| C8 | Critic fallback 4가지 deprecation note만 추가 (실제 제거는 Phase 9+ eval 후) | NG12 |
| C9 | prompt_registry 본문 정식화 X (semver/io/rollback 골격만) | NG8 |

### 1.2 불확실 항목 (U1~U4)

| ID | 항목 | 검증 시점 |
|---|---|---|
| U1 | Critic canonical `overall_score + dimensions` 결정이 추후 8-dim 가중치 도입과 호환되는가 | Phase 9+ eval-run 정식화 시 |
| U2 | Rewriter Pydantic 모델 도입 시 회귀 0 유지 가능한가 (현 dict 반환 → Pydantic 모델 변환) | Slice 3 stress test |
| U3 | frontend types.ts CriticVerdict 추가가 page.tsx 회귀 없는지 | Slice 3 tsc + build |
| U4 | schema_stress_test.ps1 자동화가 manual walkthrough 대비 충분한 표현력 | Slice 4 회고 시 재평가 |

### 1.3 Contract cross-reference (v1.2.0)

- `audit_naming.ps1` entry: **PASS 0 drift**
- 신규 명명 점검:
  - `CriticVerdict` (camelCase Pydantic model — Python 관례 OK)
  - `CriticDimensions` (camelCase)
  - `ReviseAttempt` (camelCase)
  - `RewriterInput` / `RewriterOutput` (camelCase)
  - `select_best_plan_index` (snake_case 함수, 기존 유지)
  - `schema_stress_test.ps1` (snake_case 파일명)
  - 모두 NAMING_POLICY 정합

---

## §6.2 Simplest Slice (3회 압축)

**1차**: "Critic canonical 결정 + Rewriter contract + revise_history schema + select_best_plan_index 축소 + types.ts + stress test"

**2차**: "Critic canonical Pydantic 모델 1개 + output_schema.md §CriticEvaluation 1줄 갱신"

**3차**: 
```python
# backend/fastapi/schemas/output.py (수정)
class CriticEvaluation(BaseModel):
    overall_score: float = Field(..., ge=0.0, le=1.0)
    dimensions: dict[str, float] = Field(default_factory=dict)
    # ...
```

→ Slice 2 첫 1시간 산출물. 그 후 fallback 축소 + Rewriter contract + types.ts + stress test 확장.

---

## §6.3 Surgical Scope

### Editable
```
docs/contracts/output_schema.md
docs/contracts/agent_io_contract.md
docs/contracts/api_contract.md (Optional)
backend/fastapi/agents/critic.py
backend/fastapi/agents/rewriter.py
backend/fastapi/schemas/output.py
backend/fastapi/tests/test_critic.py
backend/fastapi/tests/test_rewriter.py
backend/fastapi/tests/test_schema_stress.py (신규)
apps/web/lib/types.ts
docs/decisions/phase_6_critic_canonical.md (ADR-018)
docs/decisions/phase_6_rewriter_contract.md (ADR-019)
meta/validations/2026-05-29_phase-6-pre-entry_self.md (신규)
meta/validations/2026-05-29_phase-6-pre-entry_external.md (신규)
scripts/schema_stress_test.ps1 (신규)
scripts/smoke_test_phase_6.ps1 (신규)
meta/retrospectives/phase-6.md (신규)
meta/patterns.md
meta/skill_usage_log.md
PROJECT_STATE / PHASE_REGISTRY / 00_START_HERE / README × 2
phases/active/phase-6-*/* (entry files)
```

### Read-Only
```
docs/contracts/mvp_non_goals.md
docs/contracts/llm_security_contract.md
ai_system/*, knowledge/*, eval/*
backend/fastapi/agents/intent.py, planning.py, rag.py
backend/fastapi/routers/* (Slice 2/3에서 미수정 — schema 변경만 호환 보장)
```

### Forbidden (절대 수정 금지)
```
apps/web/components/PlanCard.tsx           ★ 10연속 0줄 baseline
apps/web/component_map.md                  ★ 20연속 0줄
apps/web/app/plan/[plan_id]/page.tsx       (회귀 검증만 — Slice 3 tsc/build로만)
apps/web/lib/api.ts                        (Phase 4.5 baseline)
backend/fastapi/routers/plans.py           (schema 변경 호환성으로 충분)
phases/archive/*, scripts/audit_*.ps1
.claude/skills/*  (phase-complete v1.2.0은 Phase 4.5에서 완료)
```

### Sub-agent SELF-VERIFICATION (P-X1) 의무 — 모든 Slice

```
1. git status
2. git diff --stat HEAD
3. editable / forbidden 대조
4. forbidden 변경 시:
   - PlanCard.tsx, component_map.md, routers/plans.py 변경 → 즉시 revert
   - RETURN 보고에 deviation 명시
5. 판정: forbidden 0건 → PASS
```

**Main session 사후**: `git diff HEAD~1 HEAD --stat | grep -E "PlanCard|component_map|routers/plans|page.tsx"` = 0 lines

---

## §6.4 Verification

| Acceptance | 검증 방법 | 자동 |
|---|---|---|
| A1 Critic canonical | output_schema.md 명시 + ADR-018 | 반자동 (string match) |
| A2 fallback 축소 + deprecation | pytest + DeprecationWarning capture | 자동 |
| A3 Rewriter contract | agent_io_contract.md §P-008 + ADR-019 | 반자동 |
| A4 revise_history + recommended_plan_index | output_schema.md 명시 | 반자동 |
| A5 Pydantic 모델 | pytest test_rewriter | 자동 |
| A6 types.ts 정합 | tsc 0 + next build 11 routes | 자동 |
| A7 schema stress | pytest test_schema_stress + schema_stress_test.ps1 | 자동 |
| A8 0줄 baseline | git diff --stat | 자동 |
| A9 audit 0 drift | scripts | 자동 |
| A10 smoke 10/10 | smoke_test_phase_6.ps1 | 자동 |

**자동화 비율**: 7/10 자동 + 3 반자동 (string match).

---

## §6 결과: ✅ 4-check 통과

**다음 단계**: Slice 1 sub-agent dispatch — Pre-Entry (validations self V1~V5 + external placeholder + contract gap analysis).
