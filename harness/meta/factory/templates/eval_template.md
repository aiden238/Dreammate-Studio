# eval_template.md — eval scaffold 템플릿

> 위치: `harness/meta/factory/templates/eval_template.md`
> 상태: Phase M0 Slice 2 — 생성 하네스의 eval 정의 scaffold
> 결정: ADR-035
> 정합: `eval/golden_set.md` (케이스 형식 GS-XXX), `.claude/skills/eval-run/SKILL.md` (실행/채점/임계값), harness_blueprint_schema.md §3.1 Eval
> ★ eval 실행은 eval-run Skill 절차(§3~§6)를 따른다. golden_set 갱신은 contract-change Skill 경유.

---

## 사용법

generation_workflow 단계 6(eval 후보 생성)에서 blueprint.evals[] 의 각 항목을 이 형식으로 작성한다. golden_set 케이스 형식 + 채점 차원 + 임계값을 eval-run 형식에 정합한다.

---

## Template (placeholder)

### A. golden_set 케이스 형식

```yaml
case_id: {{XX-001}}                  # 고정 ID — 한 번 부여 후 변경 금지
name: "{{한 줄 설명}}"
priority: {{P0 | P1 | P2}}           # P0 필수 100% / P1 ≥90% / P2 ≥80%
input:
  {{input_field}}: "{{...}}"
expected_path:
  - {{단계별 기대 경로}}
expected_output:
  body_keys: [{{...}}]
  validation:
    - {{자동 검증 가능한 규칙}}
  passing_criteria:
    - {{케이스 단위 합/불 기준}}
notes:
  - {{설계 의도, 회귀 시 주의점}}
```

### B. 채점 차원

```
{{dimension_1}}   # 예: intent_fit                     (무조건 차원 — 항상 채점)
{{dimension_2}}   # 예: hook_strength                  (무조건 차원)
...               # 산출물 품질을 N 차원으로 자동/사람 채점

# 조건부 차원 (선택) — applies_when 속성으로 모드/포맷 의존 차원을 1급 표현:
{{conditional_dimension}}:
  applies_when: {{condition_expr}}   # 예: mode == guest — 게스트 모드일 때만 채점되는 차원
                                     #     (예: question_quality / guest_fit)
# ★ applies_when 미해당 시: 해당 차원을 그 케이스의 평균 점수 계산에서 **제외**한다
#   (N 고정이 아니라 적용 차원 수로 평균 — 미해당 차원을 0점/누락으로 끌어내리지 않음).
#   applies_when 없으면 = 무조건 차원(항상 평균에 포함, backward-compat 기본값).
```

### C. 임계값 (eval-run §6 정합)

```
| 지표 | 임계값 | 위반 시 |
|------|--------|---------|
| schema 준수율 | < 100% | 즉시 fail, rollback |
| 평균 점수 하락 | > {{0.3}} | fail, 사람 검토 |
| 비용 증가 | > {{30%}} | cost-review 트리거 |
| latency 증가 | > {{20%}} | 경고 |
| 차단 단어 검출 | > 0% | fail |
```
```

---

## 작성 가이드

1. **case_id 고정** (golden_set §6) — 한 번 부여 후 변경 금지. 추가 시 다음 번호 채번, 재사용 금지.
2. **priority 등급** — P0(필수 100%) / P1(≥90%) / P2(≥80%). CI 게이트 차단 정책 정합.
3. **schema 준수 100% 필수** (eval-run §4) — 자동 채점의 1차 게이트.
4. **채점 차원은 산출물 도메인별** — Dreammate 는 8차원(intent_fit/target_clarity/hook_strength/message_clarity/structure/feasibility/brand_consistency/differentiation). 도메인에 맞게 정의.
   - **조건부 차원은 `applies_when`** — 모드/포맷 의존 차원(예: 게스트 모드의 question_quality/guest_fit)은 `applies_when: 조건` 으로 표현한다. 조건 **미해당 시 그 차원을 평균 계산에서 제외**(차원 수를 적용 차원만으로 셈) — 미해당 차원을 notes 로 우회하지 않는다. `applies_when` 없으면 무조건 차원(항상 채점).
5. **임계값은 eval-run §6 정합** — schema 준수율 / 평균 점수 / 비용 / latency / 차단 단어. validation_workflow 검증 5 가 이 임계값을 사용.
6. **mock-deterministic primary** — CI 가능한 비용 0 회귀를 기본으로, 실 LLM mode 는 flag (eval-run 정신 계승).
7. **golden_set 갱신은 contract-change 경유** (golden_set §7) — golden_set 은 contract 로 취급.
8. ★ 생성된 eval 은 outputs/ 에 먼저. 실 평가 실행은 eval-run Skill 이 상위 절차 (`eval-run > harness-factory validation`).

---

## Dreammate 예시 (참조)

```
golden_set: 11 케이스 (GS-001~GS-011, P0 7 / P1 3 / P2 1)
채점 차원: 8 (video_planning_eval.md)
임계값: schema 100% / 평균 ±0.3 / 비용 +30% / latency +20% / 차단 단어 0%
runner: mock-deterministic primary + 실 LLM mode flag (eval-run 정식)
```
