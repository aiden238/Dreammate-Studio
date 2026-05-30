# skill_template.md — Skill scaffold 템플릿

> 위치: `harness/meta_factory/templates/skill_template.md`
> 상태: Phase M0 Slice 2 — 생성 하네스의 Skill 정의 scaffold
> 결정: ADR-035
> 정합: `.claude/skills/INDEX.md` (Skill 충돌 규칙 + frontmatter + applies_to), harness_blueprint_schema.md §3.1 Skill, factory_contract 규칙 4/5
> ★ Skill 추가/변경은 contract-change Skill 절차를 따른다 (Skill 도 contract 처럼 취급).

---

## 사용법

generation_workflow 단계 4(skill 후보 생성)에서 blueprint.skills[] 의 각 항목을 이 형식으로 작성한다. frontmatter(name/description/applies_to/phase/version) + 본문(절차 + 사용하지 않는 경우)을 채운다. INDEX 형식과 정합해야 한다.

---

## Template (placeholder)

```markdown
---
name: {{skill-name}}                 # kebab-case 식별자
description: |
  {{이 Skill 을 언제 쓰는가 — 트리거 상황 설명}}.
  키워드: "{{키워드1}}", "{{키워드2}}", "{{키워드3}}".   # ★ 충돌 검토 대상 (scoped)
applies_to: [{{agents | claude | agents, claude}}]   # 라우터 분리 태그
phase: [{{phase-X | ongoing | all}}]
related_contracts:
  - {{docs/contracts/xxx.md}}
related_state:
  - {{meta/... 또는 eval/...}}
version: v1.0.0                       # semver — 변경 시 bump
---

# {{skill-name}}

{{한 줄 정의 — 이 Skill 이 강제하는 절차의 본질}}.

## 트리거 조건

- {{언제 자동 트리거되는가}}

## 절차

### 1. {{단계 1}}
{{...}}

### 2. {{단계 2}}
{{...}}

## 사용하지 않는 경우          # ★ 필수 — 다른 Skill 로 라우팅

- {{상황 A}} → `{{other-skill}}` Skill
- {{상황 B}} → `{{other-skill-2}}` Skill

## 다른 Skill 과의 관계

{{우선순위 / 호출 관계}}

## 종료 조건

- {{정상 종료 기준}}
```

---

## 작성 가이드

1. **description 키워드는 scoped** (factory_contract 규칙 4 + INDEX §사용 원칙 5) — 같은 키워드가 둘 이상 Skill 에 있으면 충돌. 기존/형제 Skill 의 소유 키워드를 침범하지 않게 좁게 정의.
2. **`사용하지 않는 경우` 섹션 필수** (INDEX §applies_to 의미) — 동일 본문에 두 역할이 공존할 수 있으므로 다른 Skill 로 라우팅하는 경로를 항상 둔다.
3. **Skill 본문은 절차만** (INDEX §사용 원칙 3) — 데이터/명세는 docs/contracts/, eval/, knowledge/ 에 둔다.
4. **applies_to 태그** — agents(구현/QA) / claude(기획/설계) / both. 라우터가 자기 역할 태그 Skill 만 인지.
5. **우선순위 표 편입** — 다른 Skill 과 동시 매칭 가능하면 INDEX 우선순위 표에 관계 추가 (validation_workflow 검증 2).
6. **version semver** — 변경 시 bump + contract-change Skill 절차(제안 → 검토 → 승인 → 반영) 경유 (factory_contract 규칙 5).
7. ★ 생성된 Skill 은 outputs/ 에 먼저 두고, active 반영은 사용자 승인 + contract-change 절차 후 (proposal-first).

---

## Dreammate 예시 (참조 — scoped 키워드)

```markdown
---
name: contract-change
description: |
  docs/contracts/ 안의 어떤 파일이라도 수정해야 할 때 사용한다.
  contracts 는 직접 편집하지 않고 항상 제안 → 검토 → 승인 → 반영 절차를 거친다.
  키워드: "contract 변경", "schema 변경", "breaking change".
applies_to: [agents, claude]
phase: [all]
version: v1.0.0
---
```
