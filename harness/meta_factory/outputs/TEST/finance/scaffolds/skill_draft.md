# skill_draft — personal_finance_planning_harness (scaffold, ★ G2 신규 vs 재사용 결정)

> 위치: `harness/meta_factory/outputs/TEST/finance/scaffolds/skill_draft.md`
> 상태: Phase M3 Slice S1 — skill scaffold dry-run
> 형식: `meta_factory/templates/skill_template.md` + generation_workflow §4.1 결정트리(G2)
> ★ Skill 추가/변경은 contract-change Skill 절차 — 본 scaffold 는 설계 초안 (proposal-first, 규칙 4/5).

---

## 0. 사용 template + G2 결정

generation_workflow 단계 4 산출. ★ **핵심 결과: 신규 Skill 0** — G2 §4.1 결정트리가 모든 도메인 특화 Skill 후보를 "기존 재사용 강제" 로 분기시킴. 따라서 skill_template 의 신규 frontmatter 를 채우지 않고, **재사용 매핑 + 결정 로그**를 scaffold 로 남긴다.

---

## 1. ★ G2 §4.1 결정트리 통과 로그

```
검토 후보 → 판정:
┌─────────────────────────────┬──────────────────────────────┬─────────────┐
│ 신규 Skill 후보             │ 추출 키워드                  │ 기존 충돌    │
├─────────────────────────────┼──────────────────────────────┼─────────────┤
│ finance-eval-run            │ eval 실행/golden_set/품질평가 │ eval-run (4중첩) → 충돌 │
│ finance-security-check      │ 보안 검토/PII/security review │ security-review → 충돌  │
│ finance-cost-check          │ 비용 검토/LLM cost            │ cost-review → 충돌      │
│ finance-io-check            │ agent IO 점검/agent_io        │ agent-io-check → 충돌   │
└─────────────────────────────┴──────────────────────────────┴─────────────┘
분기: 전부 "충돌 발견" → 기존 Skill 재사용 강제 (신규 생성 금지). 고유 가치 입증 후보 없음.
→ ★ 신규 Skill 0. YAGNI 차단: "재무 전용이라 따로 있으면 편할 것" 은 신규 사유 불가 (충돌 위험만 증가).
```

---

## 2. 재사용 Skill 매핑 (신규 0 — 키워드 충돌 0)

| 의도 작업 | 재사용 Skill (기존 21 중) | applies_to | 비고 |
|---|---|---|---|
| 재무 플랜 회귀/품질 평가 | `eval-run` | agents | finance_planning_eval 실행도 eval-run 절차 |
| ★ 제3자 PII + 자문 발화 위협 검토 | `security-review` | agents, claude | ★ risk high → **재사용 강제 + 필수**(규칙 8) |
| 6 agent IO drift | `agent-io-check` | agents | 조건부 agent 2 포함 IO 정합 |
| contract/Skill 실 변경 | `contract-change` | agents, claude | output_schema/db_schema/llm_security 변경 |
| 3-plan parallel 비용 점검 | `cost-review` | agents, claude | 비용 3배 점검 |
| 새 평가 차원/golden_set 확장 | `eval-design` | claude | finance_planning_eval 차원 설계 |
| 하네스 생성/blueprint | `harness-factory` | claude | 본 dry-run 진입점 |

## 3. (참고) 만약 신규였다면 — skill_template frontmatter (★ 미채택 — 충돌로 작성 안 함)

```markdown
# (작성하지 않음 — G2 결정트리 "재사용 강제" 분기로 신규 Skill 0)
# 신규 Skill 을 만들었다면 description 키워드가 기존 eval-run/security-review 와 충돌하여
# factory_contract 규칙 4 위반 → 무효. 재사용이 옳다.
```

---

## ★ G2 적용 메모 (M2 결정트리 행사)

- **팟캐스트(M1) 대비**: M1 은 `podcast-eval-run` 신규 후보를 검증4 에서 사후 "음의 효용"으로 거부했다. 재무는 **사전 결정트리**로 4개 후보를 전부 진입 시점에 거부 → G2 가 "사후 발견"을 "사전 차단"으로 바꿈을 이질 도메인에서 확인.
- **risk high 특수 신호**: 재무는 security-review 가 단순 재사용이 아니라 **재사용 강제 + 필수 경로**(risk high → 규칙 8). G2 결정트리 + risk_level 의 상호작용이 새로 관찰됨 (S2 입력).
- 신규 Skill 0 = 도메인이 이질이어도 절차 Skill 은 도메인 무관 재사용 가능하다는 범용성 신호.

---

이 scaffold 는 skill_template + generation_workflow §4.1(G2)을 이질 도메인(재무)에 적용 (dry-run, 신규 Skill 0 — contract-change 미경유).
