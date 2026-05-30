# contract_template.md — contract scaffold 템플릿

> 위치: `harness/meta_factory/templates/contract_template.md`
> 상태: Phase M0 Slice 2 — 생성 하네스의 contract 정의 scaffold
> 결정: ADR-035
> 정합: 기존 `docs/contracts/*.md` 형식 (목적/필드/JSONB schema/cross-ref), harness_blueprint_schema.md §3.1 Contract, factory_contract 규칙 5
> ★ contract 변경은 contract-change Skill 절차를 따른다. meta_factory 가 contract 를 직접 편집하지 않는다.

---

## 사용법

generation_workflow 단계 5(contract 후보 생성)에서 blueprint.contracts[] 의 각 항목을 이 형식으로 작성한다. 기존 하네스 contract 형식(헤더 + 목적 + 필드 표 + JSONB schema + cross-reference)을 따른다.

---

## Template (placeholder)

```markdown
# {{contract_name}}.md — {{한 줄 제목}}

> 위치: `docs/contracts/{{contract_name}}.md`
> 상태: {{Phase X 진입용 / 안정}}
> 참조: {{형제 contract 1}}, {{형제 contract 2}}    # ★ cross-ref

---

## 0. 이 문서의 위치

{{이 contract 가 무엇을 정의하고, 무엇을 정의하지 않는가}}.

이 문서가 정의하는 대상:
- {{대상 1}}

이 문서가 정의하지 않는 대상:
- {{대상 X}} → `{{다른 contract}}`

---

## 1. 필드 정의

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| {{field_1}} | {{type}} | ✅ | {{...}} |
| {{field_2}} | {{type}} | — | {{...}} |

---

## 2. JSONB schema (해당 시)

\`\`\`json
{
  "{{key}}": "{{type — 예시}}"
}
\`\`\`

---

## 3. Cross-reference                # ★ 정합 축

| 이 contract 의 필드 | 정합 대상 | 정합 규칙 | 조건부 산출(conditional output) |
|---|---|---|---|
| {{field}} | {{output_schema §X / db_schema 테이블 / frontend type}} | 1:1 매핑 | {{— (항상 산출) / 예: mode == guest 일 때만 산출}} |

---

## 4. 변경 이력
- {{vX.Y.Z (YYYY-MM-DD)}}: {{변경 내용}}
```

---

## 작성 가이드

1. **cross-reference 필수** (validation_workflow 검증 3) — 3 정합 축을 명시:
   - prompt_registry ↔ output_schema (prompt 출력 ↔ 본문 스키마)
   - api_contract ↔ frontend·api client (API 응답 ↔ 프론트 타입)
   - db_schema ↔ migration (테이블/컬럼/JSONB ↔ migration)
   - **조건부 산출(conditional output) 열** — 이 출력이 특정 조건(예: `mode == guest`)일 때만 산출되는지 cross-ref 가 1급으로 표현한다. 조건 없으면 `—`(항상 산출). agent 측 `conditional_execution.condition`(agent_template) 과 정합 — 조건부 agent 의 출력은 contract 에서도 조건부 산출로 표기.
2. **"정의하지 않는 대상" 명시** — contract 경계를 분명히 해 중복/drift 방지 (P-DRIFT-001 정신).
3. **canonical + deprecated 명시** — 다중 fallback 누적 시 canonical 1 + 우선 fallback 1 + deprecated N + 제거 시점 (P-CRITIC-CANONICAL-001 정신).
4. **JSONB schema 는 키/타입/예시** — 자유 텍스트 필드는 검증 규칙(길이/enum)을 함께 명시.
5. **변경 이력 semver** — 변경 시 bump + contract-change Skill 절차 경유 (factory_contract 규칙 5).
6. ★ 생성된 contract 는 outputs/ 에 먼저 두고, active 반영은 사용자 승인 + contract-change 절차 후 (proposal-first, 규칙 3).

---

## Dreammate 예시 (참조 — cross-ref 축)

```
agent_io_contract.md  ↔  output_schema.md     (agent 출력 ↔ 본문 스키마)
api_contract.md       ↔  apps/web/lib/types   (API 응답 ↔ 프론트 타입)
db_schema.md          ↔  db/migrations/000N    (테이블 ↔ migration)
```
