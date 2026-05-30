# Phase M0 — Assumptions (phase-start v1.3.0 §6 4점검)

> 작성: 2026-05-31
> 결과: ✅ **4-check 통과**

---

## §6.1 Assumptions

### 1.1 확정 가정 (C1~C9)

| ID | 항목 | 근거 |
|---|---|---|
| C1 | audit_naming PASS 0 drift (entry) | scripts/audit_naming.ps1 |
| C2 | Phase 9.5 baseline 유지 (pytest 339 + P-X1 47 + PlanCard 35 + component_map 45) | Phase 9.5 |
| C3 | **런타임 변경 0** (사용자 §2 금지) — 문서/skeleton/Skill만. A9 핵심 게이트 | 사용자 지침 |
| C4 | **proposal-first** — 생성물은 meta_factory/outputs/ 또는 meta/proposals/에 먼저 (자동 반영 X) | 사용자 §0/§2 |
| C5 | **meta-phase** (사용자 결정) — PHASE_REGISTRY 제품 phase와 분리, phase-M0-* | 사용자 결정 |
| C6 | **harness-factory Skill 추가** (proposal-only, 키워드 scoped) — INDEX #21 | 사용자 결정 |
| C7 | `.claude/agents/` 부재 확인 → blueprint 부족점 "agent 자동 생성 없음" 실측 근거 | entry 확인 |
| C8 | golden_set 11 케이스 (47 아님) — blueprint §7 실측 | Phase 9.5 발견 |
| C9 | blueprint는 실측 (ADR-001~034, CC-005, P-X1 47, 20 Skill→21) — 추측 금지 | R2 |

### 1.2 불확실 항목 (U1~U4)

| ID | 항목 | 검증 시점 |
|---|---|---|
| U1 | harness-factory 키워드가 harness-audit/meta-retrospective와 실제 충돌 없는가 | Slice 3 harness-audit 충돌 검토 |
| U2 | meta_factory 명명(snake_case 파일 + meta_factory 폴더)이 audit_naming 정합한가 | Slice 1~3 audit |
| U3 | meta-phase가 PHASE_REGISTRY/PROJECT_STATE 제품 phase 흐름 오염 없이 등록되는가 | Slice 3 state docs |
| U4 | blueprint 역정리가 현재 하네스를 정확히 반영하는가 (실측 vs 문서 drift) | Slice 2 blueprint |

### 1.3 Contract cross-reference
- audit_naming entry: PASS 0 drift
- 신규 명명: `meta_factory` (폴더), `factory_contract`/`domain_brief_schema`/`harness_blueprint_schema`/`architecture_patterns`/`generation_workflow`/`validation_workflow` (snake_case md), `harness-factory` (Skill, kebab — 기존 Skill 명명 정합), `phase-M0-meta-factory` (phase dir) — NAMING_POLICY 점검 (M0 대문자 허용 여부 audit 확인, 안 되면 phase-m0 소문자)

---

## §6.2 Simplest Slice (3회 압축)
**1차**: "meta_factory 전체 + Skill + blueprint"
**2차**: "factory_contract + README (L1/L2/L3) 먼저"
**3차**:
```markdown
# meta_factory/factory_contract.md
1. product runtime 직접 수정 금지
2. 기존 harness 직접 변경 금지
... (8 규칙)
```
→ **Slice 1 첫 산출물** (contract 먼저 = 이후 모든 문서의 제약 정의).

---

## §6.3 Surgical Scope

### Editable
```
harness/meta_factory/** (신규 전부)
.claude/skills/harness-factory/SKILL.md (신규)
.claude/skills/INDEX.md (수정 — #21 등록만)
docs/decisions/phase_M0_meta_factory.md (ADR-035)
meta/validations/2026-05-31_phase-M0-pre-entry_{self,external}.md
meta/proposals/2026-05-31_phase-M0-harness-factory-skill.md
docs/contract_changes/2026-05-31_phase-M0-skill-index.md (CC-006)
meta/retrospectives/phase-M0.md / meta/patterns.md / meta/skill_usage_log.md
scripts/{smoke_test_phase_M0.ps1, scenario_simulation.ps1 v7}
PROJECT_STATE / PHASE_REGISTRY / 00_START_HERE / README (meta-phase 등록 최소)
phases/active/phase-M0-*/* (entry)
```

### Read-Only (blueprint 역정리 + 참조)
```
PROJECT_STATE / AGENTS / CLAUDE / PHASE_REGISTRY / INDEX (현재 구조)
docs/contracts/** (구조 참조 — 변경 X)
eval/** (golden_set 등 — 참조 X)
backend/fastapi/** (Supervisor 패턴 매핑 — 읽기만)
meta/self_improvement_loop.md
```

### Forbidden (절대 금지 — A9 핵심)
```
backend/fastapi/** (FastAPI runtime — 0줄 ★)
apps/web/** (Next.js — 0줄 ★, PlanCard·component_map 포함)
backend/fastapi/db/migrations/** (Supabase — 0줄 ★)
docs/contracts/*.md (기존 contract 직접 변경 X — INDEX는 contract-change 경유)
AGENTS.md / CLAUDE.md (라우터 직접 변경 X)
기존 .claude/skills/*/SKILL.md (harness-factory 신규 외)
eval/** (변경 X)
이전 ADR (014~034) / phases/archive/** (참조만)
모든 baseline test (변경 0 — 런타임 무관)
```

### Sub-agent SELF-VERIFICATION (P-X1) — 모든 Slice 의무
Main 사후 (★ A9): `git diff HEAD~1 HEAD --stat | grep -E "backend/fastapi|apps/web|db/migrations|docs/contracts/[a-z]|^AGENTS|^CLAUDE|PlanCard|component_map|tests/test_"` = 0 lines (런타임/기존 contract/test 0 — INDEX.md만 예외)

---

## §6.4 Verification
| Acceptance | 검증 | 자동 |
|---|---|---|
| A1~A8 | 파일 존재 + string match | 반자동 |
| A9 런타임 0 | git diff backend/apps/migrations | 자동 ★ |
| A10 요약 | closing_notes + 보고 | 수동 |
자동/반자동 중심 (문서 phase).

---

## §6 결과: ✅ 4-check 통과
**다음**: Slice 1 sub-agent — validations + meta_factory 핵심 contract 문서 (README/factory_contract/schemas/architecture_patterns) + ADR-035.
