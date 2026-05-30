# Phase 9.5 — Assumptions (phase-start v1.3.0 §6 4점검)

> 작성: 2026-05-31
> 결과: ✅ **4-check 통과**

---

## §6.1 Assumptions

### 1.1 확정 가정 (C1~C10)

| ID | 항목 | 근거 |
|---|---|---|
| C1 | audit_naming PASS 0 drift (entry) | scripts/audit_naming.ps1 |
| C2 | Phase 9 baseline 유지 (pytest 293 + smoke 15 + scenario_sim v5 25 + P-X1 42) | Phase 9 Slice 6 |
| C3 | **eval-run mock-deterministic primary** (사용자 결정) — 실 LLM mode는 flag + 문서 (CI 가능, 비용 0) | 사용자 결정 |
| C4 | **Critic deprecated Full 제거** (사용자 결정) — fallback + CriticEvaluation Optional 필드. run_critic 0–5 출력 불변 (P-007 contract, NG3) | 사용자 결정 |
| C5 | **순서**: Slice 2~3 eval runner → eval로 canonical-only 검증 → Slice 4 제거 (회귀 통과 후) | gap 분석 |
| C6 | Phase 9 wiring으로 canonical 항상 populated → select_best_plan_index deprecated fallback dead → 제거 안전 | Phase 9 ADR-032 |
| C7 | test_critic의 run_critic 0–5 케이스 보존 (run_critic 불변), select_best_plan_index deprecated-fallback 케이스만 의도 delta | NG3 |
| C8 | RAG eval_rubric 정식화 Phase 10+ (NG1) | 사용자 결정 |
| C9 | frontend types.ts CriticEvaluation deprecated 필드 정합 (Phase 6 Slice 3에서 non-optional 유지 → page.tsx 회귀 주의) | U3 |
| C10 | mock golden_set 채점 — schema 준수 + structural (실 LLM 8차원 채점은 mode flag) | C3 |

### 1.2 불확실 항목 (U1~U5)

| ID | 항목 | 검증 시점 |
|---|---|---|
| U1 | golden_set.md 47 케이스가 executable 구조로 파싱 가능한가 (markdown → 구조화) | Slice 2 loader |
| U2 | mock-deterministic 채점이 실 LLM 품질 신호를 충분히 대리하는가 (schema/structural 한계) | Slice 2 + 실 LLM mode |
| U3 | CriticEvaluation deprecated 제거가 frontend types.ts/page.tsx 회귀 유발하는가 (Phase 6 Slice 3 non-optional) | Slice 4 tsc/build |
| U4 | select_best_plan_index deprecated 제거로 깨지는 test_critic 케이스 수 (의도 delta 경계) | Slice 4 pytest |
| U5 | revise effect mock metric이 실제 개선을 대리하는가 | Slice 3 + 실 LLM |

### 1.3 Contract cross-reference
- audit_naming entry: PASS 0 drift
- 신규 명명: `eval/golden_set_loader` / `eval/runner` / `eval/revise_effect` / `eval/report` (snake_case) · `eval_run.ps1` · `smoke_test_phase_9_5.ps1` — NAMING_POLICY 정합

---

## §6.2 Simplest Slice (3회 압축)
**1차**: "eval runner + revise effect + deprecated 제거"
**2차**: "golden_set 47 케이스 로드 → mock 회귀 → schema 준수율 리포트"
**3차**:
```python
# backend/fastapi/eval/golden_set_loader.py
def load_golden_set() -> list[dict]:
    """eval/golden_set.md → [{id, input, expected_properties}, ...]"""
```
→ **Slice 2 첫 1시간 산출물** (loader). 이후 runner + 채점 + report 확장.

---

## §6.3 Surgical Scope

### Editable
```
backend/fastapi/eval/{__init__,golden_set_loader,runner,revise_effect,report}.py (신규)
backend/fastapi/agents/critic.py (Slice 4 — deprecated fallback 제거, run_critic 0–5 불변)
backend/fastapi/schemas/output.py (Slice 4 — CriticEvaluation deprecated Optional 필드 제거)
backend/fastapi/tests/{test_eval_runner,test_revise_effect}.py (신규)
backend/fastapi/tests/test_critic.py (의도 delta — deprecated-fallback 케이스)
backend/fastapi/tests/test_prompt_registry_consistency.py (의도 delta, 필요 시)
apps/web/lib/types.ts (Slice 4 — CriticEvaluation deprecated 정합, 필요 시)
docs/contracts/{output_schema,agent_io_contract,db_schema}.md (contract-change)
eval/golden_set.md (선택 — executable format)
docs/decisions/phase_9_5_{eval_run_harness,critic_deprecated_removal}.md (ADR-033/034)
meta/validations/2026-05-31_phase-9.5-pre-entry_{self,external}.md
eval/regression_results/phase-9.5_*.md
scripts/{eval_run.ps1, smoke_test_phase_9_5.ps1, scenario_simulation.ps1 v6}
meta/{retrospectives/phase-9.5.md, patterns.md, skill_usage_log.md}
PROJECT_STATE / PHASE_REGISTRY / 00_START_HERE / README
phases/active/phase-9.5-*/* (entry)
```

### Read-Only
```
eval/golden_set.md (참조 우선), eval/video_planning_eval.md, eval/regression_eval.md
backend/fastapi/agents/{intent,planning,rewriter,rag}.py
backend/fastapi/orchestration/* (Phase 8 — normalize wiring 호출만)
backend/fastapi/db/* (Phase 5/9)
```

### Forbidden (절대 금지)
```
apps/web/components/plan/PlanCard.tsx ★ (0줄)
apps/web/component_map.md ★ (0줄)
backend/fastapi/agents/critic.py의 run_critic 0–5 출력 로직 (P-007 contract 불변 — NG3, fallback/schema만 제거)
backend/fastapi/orchestration/*, routers/*, db/*, middleware/* (Phase 5~9 baseline)
backend/fastapi/agents/{intent,planning,rewriter,rag}.py
의도 delta(test_critic deprecated-fallback) 외 모든 baseline test
이전 ADR (014~032), scripts/audit_*+schema_stress+smoke_4_5~9, skills, archive
```

### Sub-agent SELF-VERIFICATION (P-X1) — 모든 Slice
Main 사후: `git diff HEAD~1 HEAD --stat | grep -E "PlanCard|component_map|orchestration|routers|db/|middleware|agents/(intent|planning|rewriter|rag)|audit_|schema_stress|smoke_test_phase_(4_5|5|6|7|8|9)\b|skills/|archive/|decisions/(phase_4|phase_5|phase_6|phase_7|phase_8|phase_9_feedback|phase_9_brand|phase_9_critic)"` = 0 (run_critic 0–5 불변 + 의도 delta 예외)

---

## §6.4 Verification
| Acceptance | 검증 | 자동 |
|---|---|---|
| A1~A4 | pytest (eval_runner + revise_effect) | 자동 |
| A5 eval Skill | ADR-033 + eval_run.ps1 + regression_results | 반자동 |
| A6 deprecated 제거 | critic.py + schemas + agent-io-check | 자동 |
| A7 contract-change | CC-005 | 반자동 |
| A8 0줄 | git diff | 자동 |
| A9 audit | scripts | 자동 |
| A10 smoke 16 + scenario v6 30 | scripts | 자동 |
자동 8 + 반자동 2.

---

## §6 결과: ✅ 4-check 통과
**다음**: Slice 1 sub-agent — validations + eval-design Skill 첫 정식 + ADR-033/034.
