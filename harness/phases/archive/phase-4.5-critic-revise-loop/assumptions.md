# Phase 4.5 — Assumptions (phase-start v1.3.0 §6 4점검 결과)

> 작성 시점: 2026-05-28 (Phase 4.5 entry)
> phase-start v1.3.0 §6 절차 결과
> 결과: ✅ **4-check 통과** — 진입 허용

---

## §6.1 Assumptions (가정)

### 1.1 확정 가정

| ID | 항목 | 근거 |
|---|---|---|
| C1 | **audit_naming 통과 (2026-05-28)** — 0 drift detected | `scripts/audit_naming.ps1` 본 entry 시점 실행 결과 (PASS) |
| C2 | Phase 4 baseline 유지 가능 (회귀 0) | Phase 4 종료 시 smoke 8/8 + audit 0 + pytest 93/93 + tsc 0 + lint clean — Phase 4.5는 *추가 필드*만 도입 |
| C3 | OpenAI API 가용성 (gpt-4o-mini, gpt-4o) | Phase 4와 동일 환경 |
| C4 | in-memory `_plan_store: dict` 유지 가능 | NG1 (DB는 Phase 5+) — 단일 프로세스 메모리로 revise loop 충분 |
| C5 | PlanCard.tsx + component_map.md 0줄 보존 가능 | 사용자 결정 6-a 정신 + Z-X3 wrapper UI 방식 (PlanCard prop 미추가) |
| C6 | output_schema.md 신규 필드 (revise_history, recommended_plan_index)는 **Optional 추가**이므로 contract-change 불필요 | output_schema의 Optional 필드 추가 패턴은 회귀 0 (호환성 유지) |
| C7 | multi-llm-validation **formal self** 가능 (Claude Code 자가 검증) | 사용자 결정 — Claude Code가 지침 참조하면서 self-validation, 외부 검증은 별도 파일 |
| C8 | P-X2 채택 시 Phase 4.5 본 scope에 +1~2h 추가 가능 (총 12~16h) | 사용자 결정 — Phase 4.5에서 채택 |
| C9 | Z-X3 포함 시 Phase 4.5 본 scope에 +2~3h 추가 가능 | 사용자 결정 — 포함 (8~12h → 10~15h → 12~16h 총합) |

### 1.2 불확실 항목 (U-X)

| ID | 항목 | 검증 시점 |
|---|---|---|
| U1 | Rewriter 인라인 prompt가 실 LLM 응답에서 verdict.weakness를 충분히 반영하는가 | Slice 2 pytest + manual walkthrough (golden_set FC-001~005 일부 케이스로 sanity check, NG8 정식 eval은 Phase 9+) |
| U2 | Critic 8-dim 평균 점수의 tie-breaking이 사용자 직관과 일치하는가 | Slice 3 pytest + 추후 사용자 데이터 누적 시 검증 (Phase 9+ eval) |
| U3 | revise loop 2회 횟수가 실제로 충분한지 (3회+ 필요한 케이스 빈도) | Slice 4 manual + Phase 4.5 종료 후 데이터 누적 |
| U4 | P-X2 자동 게이트의 scenario_simulation.ps1이 변경성 시뮬 5/5 PASS를 안정적으로 재현하는가 | Slice 4 final (첫 자동 게이트 트리거) |

→ U1~U4 모두 **Phase 4.5 회고 시점**에 재평가. eval 정식화는 Phase 9+.

### 1.3 Contract cross-reference 점검 (v1.2.0)

- `audit_naming.ps1` 실행 결과: **PASS 0 drift detected** (2026-05-28)
- Checked: plan_candidates / video_projects / critic_evaluation / rag_references — 모두 PASS
- 추가 명명 점검 (Phase 4.5 신규):
  - `revise_history` (snake_case, output_schema 일관)
  - `recommended_plan_index` (snake_case)
  - `select_best_plan_index` (snake_case 함수명)
  - `run_rewriter` (snake_case, run_planning과 일관)
  - 신규 명명은 audit_naming whitelist 추가 불필요 (deprecated 단어 미사용)

---

## §6.2 Simplest Slice (최소 작동 단위)

### 3회 압축 반복

**1차 답** ("이 Phase에서 작동 확인 가능한 가장 작은 단위?"):
> "Rewriter agent + Critic revise loop + Best-Plan + Frontend highlight 통합 동작"

**2차 압축** ("더 줄일 수 있는가?"):
> "Rewriter agent + Critic verdict가 revise일 때 1회 revise → schemas/output revise_history 노출 (best-plan / frontend X)"

**3차 압축** ("더 줄일 수 있는가?"):
> "`run_rewriter(plan, verdict) -> dict` 함수 1개 + pytest 1 케이스 (verdict.weakness 반영 후 plan 재생성, 1회만)"

### 최종 Simplest Slice

```python
# backend/fastapi/agents/rewriter.py (신규)
async def run_rewriter(
    plan: dict,
    critic_verdict: dict,
    *,
    model: str = "gpt-4o-mini",
    client: Any | None = None,
) -> dict:
    """Critic verdict의 weakness 항목을 반영하여 plan을 1회 개선."""
    # 인라인 prompt + OpenAI call + retry 0 (Phase 4.5 1차)
    ...
```

**검증**: `pytest tests/test_rewriter.py::test_basic_revise` 1 케이스 PASS.

이것이 **Slice 2의 첫 1시간 산출물**. 이후 Slice 2 후반에서 revise loop 통합 (routers/plans.py), Slice 3에서 best-plan + wrapper UI 확장.

---

## §6.3 Surgical Scope (수술적 범위)

### Editable (수정/신규 가능)

```
backend/fastapi/agents/rewriter.py          (신규)
backend/fastapi/agents/critic.py            (수정 — select_best_plan_index)
backend/fastapi/routers/plans.py            (수정 — revise loop + best-plan 통합)
backend/fastapi/schemas/output.py           (수정 — Optional 필드 추가)
backend/fastapi/config.py                   (선택 수정 — critic_max_revise)
backend/tests/test_rewriter.py              (신규)
backend/tests/test_plans.py                 (수정)
backend/tests/test_critic.py                (수정)
apps/web/app/plan/[plan_id]/page.tsx        (수정 — wrapper)
apps/web/lib/types.ts                       (수정 — Optional 필드)
docs/decisions/phase_4_5_critic_revise.md   (신규 — ADR-016)
docs/decisions/phase_4_5_best_plan_selection.md (신규 — ADR-017)
meta/validations/2026-05-28_phase-4.5-pre-entry_self.md (신규)
meta/validations/2026-05-28_phase-4.5-pre-entry_external.md (신규, placeholder)
.claude/skills/phase-complete/SKILL.md      (수정 — v1.2.0 §1.6)
scripts/scenario_simulation.ps1              (신규)
scripts/smoke_test_phase_4_5.ps1             (신규)
meta/retrospectives/phase-4.5.md             (신규)
meta/patterns.md                              (수정)
meta/skill_usage_log.md                       (수정)
PROJECT_STATE.md / PHASE_REGISTRY.md / 00_START_HERE.md / README.md / harness/README.md (수정)
phases/active/phase-4.5-critic-revise-loop/* (entry files)
```

### Read-Only (참조만)

```
docs/contracts/*  (모두)
ai_system/*  
knowledge/*
eval/*  (NG8 정신)
```

### Forbidden (절대 수정 금지)

```
apps/web/components/plan/PlanCard.tsx   ★ 5연속 0줄 유지
apps/web/component_map.md               ★ 16연속 0줄 유지
phases/archive/*                         (기본 참조 금지)
phases/active/phase-4.5-*/non_goals.md   (단어 수준 금지 목록 — non_goals 단어 본 phase 신규 파일에 등장 금지)
```

### Sub-agent SELF-VERIFICATION (P-X1) 의무 — v1.3.0

모든 Slice (1~4) sub-agent prompt에 다음 절차 포함 필수:

```
SELF-VERIFICATION (P-X1, 작업 완료 직전 필수):

1. git status (staged + unstaged 파일)
2. git diff --stat HEAD (수정 파일 목록 + LOC)
3. editable / forbidden 목록 대조
4. forbidden 영역 변경 발견 시:
   - PlanCard.tsx 또는 component_map.md 변경 → 즉시 git checkout HEAD -- {file} revert
   - 의도하지 않은 변경 → revert
   - RETURN A SUMMARY § "deviations / open issues"에 명시
5. 판정: forbidden 영역 0건 → PASS / 1건+ → FAIL (revert 재검증)
```

**Main session 사후 검증**: `git diff HEAD~1 HEAD --stat | grep -E "PlanCard|component_map"` = **0 lines** (Slice 1~4 모두).

---

## §6.4 Verification (검증)

각 acceptance에 검증 방법 1:1 매핑:

| Acceptance | 검증 방법 | 자동/수동 |
|---|---|---|
| A1 Rewriter 구현 | `pytest tests/test_rewriter.py` | 자동 |
| A2 Revise 최대 2회 | `pytest tests/test_plans.py::test_revise_loop_max_2` | 자동 |
| A3 revise_history 응답 | `pytest tests/test_plans.py::test_revise_history_structure` + schemas check | 자동 |
| A4 best-plan index | `pytest tests/test_critic.py::test_select_best_plan_index_*` | 자동 |
| A5 wrapper highlight | `next build` + tsc + lint + page.tsx wrapper class string match | 반자동 (string match) |
| A6 PlanCard 0줄 | `git diff HEAD~N HEAD -- ...PlanCard.tsx --stat` | 자동 |
| A7 component_map 0줄 | `git diff HEAD~N HEAD -- ...component_map.md --stat` | 자동 |
| A8 audit 0 drift | `scripts/audit_naming.ps1` + `scripts/audit_page_component.ps1` | 자동 |
| A9 P-X2 자동 게이트 | `phase-complete` Skill v1.2.0이 `scripts/scenario_simulation.ps1` 자동 호출 → 5/5 PASS | 자동 |
| A10 smoke 9/9 | `scripts/smoke_test_phase_4_5.ps1` | 자동 |

**자동화 비율**: 10/10 자동 (반자동 1 string match 포함). 수동 검증 0 — 회귀 위험 ↓.

---

## §6 결과: ✅ 4-check 통과, Phase 4.5 진입 허용

- **Assumptions**: 확정 9 + 불확실 4 (모두 회고 시점 재평가)
- **Simplest Slice**: `run_rewriter()` 함수 1개 + pytest 1 케이스
- **Surgical Scope**: editable 명시 + forbidden 2 (PlanCard / component_map) — P-X1 §SELF-VERIFICATION 13연속 목표
- **Verification**: 10/10 자동 (반자동 1)

**다음 단계**: Slice 1 sub-agent dispatch — Pre-Entry (validations + P-X2 + entry commit).
