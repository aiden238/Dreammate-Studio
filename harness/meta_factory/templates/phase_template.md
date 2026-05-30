# phase_template.md — phase scaffold 템플릿

> 위치: `harness/meta_factory/templates/phase_template.md`
> 상태: Phase M0 Slice 2 — 생성 하네스의 phase 정의 scaffold
> 결정: ADR-035
> 정합: 기존 `phases/active/{phase}/` 8 entry files 형식, harness_blueprint_schema.md §3.1 Phase
> ★ phase 구조는 entry 8 files (goals/scope/non_goals/dependencies/acceptance/assumptions/multi_slice_plan/notes).

---

## 사용법

generation_workflow 단계 7(phase 구조 생성)에서 blueprint.phases[] 의 각 항목을 이 형식으로 작성한다. phase entry 8 files 형식을 따르고, domain_brief.forbidden_scope → non_goals 로 매핑한다.

---

## Template (placeholder — 8 entry files)

### goals.md
```markdown
# {{phase}} — Goals
- {{핵심 목표 1}}
- {{핵심 목표 2}}
```

### scope.md
```markdown
# {{phase}} — Scope
## 포함 (In-Scope)
| 파일/영역 | 작업 |
|---|---|
| {{...}} | 신규/수정 |
## ★ 절대 수정 금지 (forbidden)
- {{forbidden 영역}}
```

### non_goals.md          # ★ 필수 — scope creep 차단
```markdown
# {{phase}} — Non-Goals
| ID | 항목 | 사유 |
|---|---|---|
| NG1 | {{...}} | {{...}} |   # domain_brief.forbidden_scope 매핑
```

### dependencies.md
```markdown
# {{phase}} — Dependencies
- 선행 phase: {{...}}
- 외부 의존: {{...}}
```

### acceptance.md         # ★ 필수 — 수락 기준
```markdown
# {{phase}} — Acceptance
| ID | 기준 | 검증 방법 |
|---|---|---|
| A1 | {{...}} | {{test / eval / audit}} |
```

### assumptions.md
```markdown
# {{phase}} — Assumptions
- {{가정 1 + 4-check 통과 여부}}
```

### multi_slice_plan.md
```markdown
# {{phase}} — Multi-Slice Plan
## Wave 구조
- Slice 1 [...] → Slice 2 [...] → ...
## 충돌 매트릭스
| Slice | 영역 A | 영역 B |
|---|---|---|
```

### notes.md
```markdown
# {{phase}} — Notes
## Entry ({{date}})
- {{진입 점검 결과}}
## Slice 1~N (작업 시 갱신)
```

---

## 작성 가이드

1. **non_goals.md 필수** (harness_blueprint_schema §3.3) — domain_brief.forbidden_scope 를 NG 항목으로 매핑. scope creep 차단의 핵심.
2. **acceptance.md 필수** — phase 종료 게이트. eval-run 임계값(validation_workflow 검증 5)을 acceptance 기준에 연결.
3. **scope.md 의 forbidden 영역** — sub-agent 작업 시 침범 금지 영역 명시 (P-AGENT-SCOPE-001 mitigation, P-X1 §SELF-VERIFICATION 정신).
4. **multi_slice_plan 충돌 매트릭스** — sub-agent 병렬/순차 시 폴더/파일 충돌 0 보장 (P-FOLDER-PARALLEL-001 정신).
5. **assumptions 4-check** — 진입 시 가정 점검 (phase-start 정신).
6. **rollback·retrospective 경로** (validation_workflow 검증 6) — 실패 시 되돌림 + 종료 후 회고 경로를 notes/acceptance 에 명시.
7. ★ 생성된 phase 구조는 outputs/ 에 먼저. active phase 등록은 사용자 승인 후 (proposal-first).

---

## Dreammate 예시 (참조)

```
phase entry 8 files: goals / scope / non_goals / dependencies / acceptance / assumptions / multi_slice_plan / notes
P-X1 §SELF-VERIFICATION: 모든 sub-agent commit 전 forbidden 영역 0줄 자기 검증 (47연속 PASS)
P-X2 자동 게이트: phase 종료 시 scenario_simulation 자동 실행 (변경성 검증)
```
