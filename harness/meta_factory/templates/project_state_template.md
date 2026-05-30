# project_state_template.md — PROJECT_STATE scaffold 템플릿

> 위치: `harness/meta_factory/templates/project_state_template.md`
> 상태: Phase M0 Slice 2 — 생성 하네스의 상태 문서 scaffold
> 결정: ADR-035
> 정합: 기존 `PROJECT_STATE.md` 형식 (migration_progress yaml + confirmed_decisions), factory_contract 규칙 6
> ★ PROJECT_STATE 는 사용자 승인 없이 갱신하지 않는다 (규칙 6).

---

## 사용법

generation_workflow 단계 8(routing 문서 생성)과 함께, 생성 하네스의 상태 문서를 이 형식으로 작성한다. migration_progress yaml + confirmed_decisions 형식을 따른다.

---

## Template (placeholder)

```markdown
# PROJECT_STATE

## 현재 상태
{{이 하네스가 지금 어디까지 와 있는가 — 1~2 문단}}.

## 현재 Active Phase
**🟢 {{Phase X}} active ({{date}})** — {{한 줄 정의}}.

## confirmed_decisions          # 사용자 확정 결정 누적
```
{{N}}. {{결정 항목}}: {{선택 + 사유}}   # 예: 1. runtime_type: product_saas
```

## migration_progress
\`\`\`yaml
current_sprint: "{{phase-X-slice-N}}"
current_sprint_step: {{step 식별자}}
total_steps_in_sprint: {{N}}
last_completed_action: "{{직전 완료 작업}}"
next_action: "{{다음 작업}}"
blocker: {{null | 차단 사유}}
{{phase_X_status}}: {{planned | active | completed}}
{{phase_X_completion_date}}: {{YYYY-MM-DD}}
{{phase_X_archive_location}}: {{phases/archive/...}}
\`\`\`

## baseline
- {{test N + 누적 지표 — 회귀 0 기준}}
```

---

## 작성 가이드

1. **migration_progress yaml 필수** — current_sprint / last_completed_action / next_action / blocker 를 항상 최신화 (라우터 진입 시 첫 참조 문서).
2. **confirmed_decisions 누적** — 사용자 확정 결정을 번호로 누적 보관. domain_brief 의 선택(runtime_type / risk_level / forbidden_scope)을 포함.
3. **active phase 1개 원칙** — PHASE_REGISTRY 와 정합. active phase 는 항상 1개만.
4. **baseline 명시** — test 수 + 누적 지표(회귀 0 기준). phase 종료 시 갱신.
5. ★ **사용자 승인 게이트** (factory_contract 규칙 6) — PROJECT_STATE 는 사용자 승인 없이 갱신하지 않는다. 생성 시에도 outputs/ 에 먼저 두고, active 반영은 승인 후 (proposal-first).
6. **archive 경로** — 종료 phase 는 archive 로 이동(git mv) + closing_notes 경로 기록.

---

## Dreammate 예시 (참조)

```yaml
current_sprint: "phase-M0-slice-2"
last_completed_action: "Slice 1 entry — meta_factory 핵심 5 문서 + ADR-035"
next_action: "Slice 2 — workflow + templates + blueprint"
blocker: null
phase_M0_status: active        # meta-phase
baseline: pytest 339 + P-X1 47 + Skill 20 (런타임 무관 불변)
```
