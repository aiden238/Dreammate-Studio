# Phase 6 — Multi-Slice Plan

> Slice 4개 모두 sub-agent dispatch (Phase 4.5 정신 계승)
> 모두 sequential

---

## Wave 구조

```
Wave 1: Slice 1 [Pre-Entry — validations + gap analysis]
  ↓
Wave 2: Slice 2 [Critic canonical + Rewriter contract — contract-change 호출]
  ↓
Wave 3: Slice 3 [Schema Stress + Frontend types.ts 정합]
  ↓
Wave 4: Slice 4 [Close + Phase 5 prep]
```

---

## Slice 1 — Pre-Entry (1.5~2h)

### 작업 단위
1. `meta/validations/2026-05-29_phase-6-pre-entry_self.md` 신규 — Claude Code 자가 검증 V1~V5:
   - **V1**: Critic verdict canonical 결정 (overall_score + dimensions vs 4가지 fallback)
   - **V2**: Rewriter input/output contract 정식 등록 시점 (Phase 6 vs Phase 7+)
   - **V3**: revise_history typing 강화 (List[dict] → List[ReviseAttempt])
   - **V4**: fallback 축소 + deprecation note 정책 (즉시 제거 X)
   - **V5**: frontend types.ts ↔ backend 1:1 매핑 도입 시점
2. `meta/validations/2026-05-29_phase-6-pre-entry_external.md` 신규 (placeholder, Phase 4.5 패턴)
3. Contract gap analysis 메모 (notes.md 또는 self-validation 본문):
   - 현 output_schema.md vs 실 backend schemas/output.py 차이 항목
   - 현 agent_io_contract.md vs 실 agents/rewriter.py 차이 항목
4. `meta/skill_usage_log.md` 갱신 (multi-llm-validation formal 2 + Phase 6 entry)
5. `PROJECT_STATE.md` active phase 갱신 (phase_6_*)
6. **entry commit**: "feat(phase-6): Slice 1 entry — validations + contract gap analysis"

### 영향 파일
- 신규: 2 validations + entry directory 8 files (이미 main에서 작성됨)
- 수정: skill_usage_log + PROJECT_STATE

### Sub-agent prompt 핵심
- editable: phases/active/phase-6-*/* (entry는 main 작성 완료), meta/validations/*, skill_usage_log.md, PROJECT_STATE.md
- forbidden: backend/* (Slice 2), apps/web/* (Slice 3), docs/contracts/* (Slice 2 contract-change), scripts/*, archive/*, PlanCard, component_map
- P-X1 의무

---

## Slice 2 — Critic Canonical + Rewriter Contract (3~4h)

### 작업 단위
1. **contract-change Skill 호출** (인지된 변경 + 절차 따름):
   - `docs/contracts/output_schema.md` 갱신 — §CriticEvaluation canonical (overall_score + dimensions) + Optional revise_history + recommended_plan_index 정식 등록
   - `docs/contracts/agent_io_contract.md` 갱신 — §P-008 Rewriter (input: plan + critic_verdict / output: revised plan + meta), semver=1.0.0
   - `docs/contracts/api_contract.md` 갱신 (Optional) — /plans/{plan_id}/generate 응답 구조 명시
2. `backend/fastapi/schemas/output.py` 갱신:
   - `CriticEvaluation` canonical 필드 명시 (overall_score: float, dimensions: dict[str, float])
   - `ReviseAttempt` Pydantic 모델 신규
   - `Body.revise_history: Optional[list[list[ReviseAttempt]]]` typing 강화
3. `backend/fastapi/agents/critic.py` 갱신:
   - `CriticVerdict` 결과 구조 canonical fields 우선
   - `select_best_plan_index` fallback chain 축소 + `DeprecationWarning` 발행
4. `backend/fastapi/agents/rewriter.py` 갱신:
   - `RewriterInput`, `RewriterOutput` Pydantic 모델 도입
   - 기존 dict 반환은 Pydantic 모델 .model_dump()로 변환 (회귀 0)
5. `backend/fastapi/tests/test_critic.py` + `test_rewriter.py` 갱신 (canonical + deprecation 케이스 추가)
6. `docs/decisions/phase_6_critic_canonical.md` 신규 (ADR-018)
7. `docs/decisions/phase_6_rewriter_contract.md` 신규 (ADR-019)
8. **commit**: "feat(phase-6): Slice 2 — Critic canonical + Rewriter contract + ADR-018/019"

### 영향 파일 (3 contract + 4 backend + 2 test + 2 ADR = ~11)

### Sub-agent prompt 핵심
- editable: docs/contracts/{output_schema, agent_io_contract, api_contract}.md / backend/fastapi/{schemas/output.py, agents/critic.py, agents/rewriter.py, tests/test_critic.py, tests/test_rewriter.py} / docs/decisions/*.md
- forbidden: PlanCard, component_map, page.tsx, routers/plans.py (회귀 보장만), apps/web/* (Slice 3), scripts/*, archive/*
- P-X1 의무
- **contract-change Skill 절차 따름** — change 사유 명시 + 회귀 0 검증

---

## Slice 3 — Schema Stress + Frontend Type 정합 (2~3h)

### 작업 단위
1. `apps/web/lib/types.ts` 갱신:
   - `CriticVerdict` interface (overall_score + dimensions)
   - `ReviseAttempt` interface
   - `Body.revise_history: ReviseAttempt[][]`
   - 기존 type 호환 (Optional 유지)
2. `backend/fastapi/tests/test_schema_stress.py` 신규 (5~7 케이스):
   - best-plan tie + canonical
   - rewriter failure graceful
   - revise max 2 차단
   - critic dimensions 부재 시 fallback
   - frontend type ↔ backend dict round-trip
   - recommended_plan_index null 케이스
3. `scripts/schema_stress_test.ps1` 신규:
   - pytest test_schema_stress (자동)
   - tsc --noEmit (자동)
   - next build sanity (자동)
   - import sanity (Pydantic 모델 load)
4. tsc + next build 회귀 검증 (page.tsx 무수정으로 자동 호환 보장)
5. **commit**: "feat(phase-6): Slice 3 — schema stress + frontend types 정합"

### 영향 파일 (1 frontend + 1 test 신규 + 1 script 신규 = 3)

### Sub-agent prompt 핵심
- editable: apps/web/lib/types.ts / backend/fastapi/tests/test_schema_stress.py / scripts/schema_stress_test.ps1
- forbidden: PlanCard ★, component_map ★, page.tsx, agents/*, routers/*, schemas/* (Slice 2 영역), docs/contracts/* (Slice 2 영역)
- P-X1 의무
- PlanCard.tsx 0줄 검증 (`git diff --cached --stat | grep PlanCard` = empty)

---

## Slice 4 — Close + Phase 5 Prep (1~1.5h)

### 작업 단위
1. `scripts/smoke_test_phase_6.ps1` 신규 (10/10: Phase 4.5 9 + schema_stress 1)
2. `audit_naming` + `audit_page_component` final
3. `scenario_simulation.ps1` final (P-X2 두 번째 자동 게이트, 5/5 PASS 유지)
4. `agent-io-check` Skill **첫 정식 트리거** (Slice 2 contract 변경 후)
5. `design-review` impl §B
6. `meta-retrospective` → `meta/retrospectives/phase-6.md`
7. `meta/patterns.md`:
   - P-X1-EFFECT-001 update (**17연속**)
   - **P-CRITIC-CANONICAL-001 신규** (4 fallback → 1 canonical + deprecation 패턴)
   - **P-CONTRACT-FIRST-001 신규 후보** (DB 진입 전 contract 안정화 효과 입증)
8. `phase-complete` v1.2.0 (P-X2 두 번째 자동 게이트)
9. archive 이동: `phases/active/phase-6-*` → `phases/archive/phase-6-output-schema-stabilization/`
10. `closing_notes.md` 신규 (Phase 5 진입 조건 정리: external validation 채움 + security-review Skill 호출 권장)
11. PROJECT_STATE / PHASE_REGISTRY / 00_START_HERE / README × 2 갱신
12. **final commit**: "feat(phase-6): Slice 4 — close + Phase 5 prep + P-CRITIC-CANONICAL-001 신규"

### 영향 파일 (~10 신규/수정 + archive 이동)

### Sub-agent prompt 핵심
- editable: scripts/smoke_test_phase_6.ps1 / meta/retrospectives/phase-6.md / meta/patterns.md / archive 이동 / state docs / closing_notes.md
- forbidden: backend/* (Slice 2/3 완료), apps/web/* (Slice 3 완료), PlanCard ★, component_map ★, docs/contracts/* (Slice 2 완료), docs/decisions/* (Slice 2 ADR-018/019 완료), scripts/audit_*.ps1, .claude/skills/* (수정 X)
- P-X1 의무

---

## 충돌 매트릭스

| Slice | contracts | backend/agents | backend/schemas | backend/tests | frontend/types | scripts | meta | docs/decisions | state docs |
|---|---|---|---|---|---|---|---|---|---|
| 1 | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ validations + skill_usage | ❌ | ✅ PROJECT_STATE entry |
| 2 | ✅ output_schema + agent_io | ✅ critic + rewriter | ✅ canonical | ✅ critic + rewriter | ❌ | ❌ | ❌ | ✅ ADR-018/019 | ❌ |
| 3 | ❌ | ❌ | ❌ | ✅ test_schema_stress 신규 | ✅ CriticVerdict + ReviseAttempt | ✅ schema_stress_test | ❌ | ❌ | ❌ |
| 4 | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ smoke_test_phase_6 | ✅ retrospective + patterns | ❌ | ✅ all |

Sequential 진행 시 충돌 0.

---

## 누적 P-X1 streak 목표

| Phase | streak |
|---|---|
| Phase 3 | 5 |
| Phase 4 | 4 |
| Phase 4.5 | 4 |
| Phase 6 | **4 (목표)** |
| **누적** | **17** |

---

## 시간 추정

| Slice | 시간 | 누적 |
|---|---|---|
| 1 | 1.5~2h | 1.5~2h |
| 2 | 3~4h | 4.5~6h |
| 3 | 2~3h | 6.5~9h |
| 4 | 1~1.5h | **7.5~10.5h** |

GPT 검토안 8~12h 추정 → 4 Slice 압축으로 ▼20% 시간 목표.
