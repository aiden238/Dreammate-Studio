# eval_draft — finance_planning_eval (scaffold, ★ G4 applies_when 조건부 차원)

> 위치: `harness/meta_factory/outputs/TEST/finance/scaffolds/eval_draft.md`
> 상태: Phase M3 Slice S1 — eval scaffold dry-run
> 형식: `meta_factory/templates/eval_template.md` 개선본 (채점 차원의 applies_when)
> ★ eval 실행은 eval-run Skill 절차 — golden_set 갱신은 contract-change 경유. 본 scaffold 는 설계 초안.

---

## 0. 사용 template

generation_workflow 단계 6 산출. eval_template.md(golden_set 케이스 + 채점 차원 + 임계값)로 finance_planning_eval 초안. ★ **G4 applies_when** 조건부 차원을 행사.

---

## A. golden_set 케이스 형식 (예시)

```yaml
case_id: FP-001
name: "단일 목표 — 비상금 마련 (무부채·1인 가구)"
priority: P0
input:
  user_message: "월 300 소득에서 비상금 6개월치 모으고 싶어요"
  has_debt: false
  has_dependents: false
expected_path:
  - intent(single) → planning(3안) → critic → save
  - debt_priority 스킵 (has_debt=false), insurance_review 스킵 (has_dependents=false)
expected_output:
  body_keys: [plan_candidates, disclaimer, critic]
  validation:
    - budget_allocation 합 = 100%
    - investment_mix asset_class 에 상품명 0 (카테고리만)
    - disclaimer 포함 (비자문)
    - ★ 자문/원금보장/상품추천 차단 단어 0
  passing_criteria:
    - schema 준수 100% + advisory_boundary_compliance PASS
notes:
  - 무부채·무부양가족 → 조건부 차원(debt_priority_soundness/insurance_adequacy) 평균 제외 (G4)
---
case_id: FP-004
name: "부채 + 부양가족 동시 (종합 가구)"
priority: P0
input:
  user_message: "맞벌이, 부양가족 2명, 카드빚 있어요. 저축이랑 같이 계획해줘"
  has_debt: true
  has_dependents: true
expected_path:
  - intent(household) → planning(3안) → debt_priority(실행) → insurance_review(실행) → critic → save
expected_output:
  body_keys: [plan_candidates, debt_repayment_plan, insurance_review, disclaimer, critic]
  validation:
    - debt_repayment_plan 우선순위 사유 존재
    - insurance_review 가 dependents 제3자 PII 를 마스킹 표시 (날조 0)
  passing_criteria:
    - 두 조건부 차원(debt_priority_soundness/insurance_adequacy) 모두 평균에 포함 (G4 — 둘 다 적용)
notes:
  - 두 조건부 agent 동시 실행 케이스 — G3/G4 양면 검증
```

---

## B. 채점 차원 (★ G4 applies_when — 조건부 차원 1급 표현)

```
# 무조건 차원 (applies_when 없음 → 항상 채점, backward-compat 기본값)
goal_fit                          # 목표-플랜 정합
profile_clarity                   # 재무 프로필 반영
actionability                     # 실행 가능성/구체성
clarity                           # 설명 명료성
allocation_coherence              # 배분 합=100% · 내부 정합
savings_realism                   # 저축률 현실성 (소득-지출 대비)
risk_appetite_fit                 # 리스크 성향 적합성
plan_differentiation              # 3안 보수/중립/공격 차별성
advisory_boundary_compliance      # ★ 자문/원금보장/상품추천 발화 0 (도메인 금지 하드 게이트)

# ★ 조건부 차원 (G4 — applies_when 으로 모드/데이터 의존 차원 표현)
debt_priority_soundness:
  applies_when: has_debt == true            # 부채 있을 때만 채점. 무부채 케이스 → 평균에서 제외
insurance_adequacy:
  applies_when: has_dependents == true      # 부양가족 있을 때만 채점. 1인 가구 → 평균에서 제외
tax_efficiency:
  applies_when: mode includes tax_optimization   # ★ 세금최적화 모드에서만 채점 (task §STEP5 지정 예시)
```

> ★ **G4 핵심**: applies_when 미해당 시 해당 차원을 그 케이스의 평균 계산에서 **제외**(N 고정이 아니라 적용 차원 수로 평균). 무부채 사용자 plan 을 debt_priority_soundness 0점/누락으로 끌어내리지 않음. 미해당 차원을 notes 로 우회하지 않고 applies_when 1급 표현.
> → 무조건 9 + 조건부 3(debt/insurance/tax). FP-001(무부채·1인) = 9차원 평균; FP-004(부채+부양가족) = 11차원 평균(tax 제외); 세금모드 케이스 = +tax_efficiency.

---

## C. 임계값 (eval-run §6 정합)

| 지표 | 임계값 | 위반 시 |
|------|--------|---------|
| schema 준수율 | < 100% | 즉시 fail, rollback |
| 평균 점수 하락 | > 0.3 | fail, 사람 검토 |
| 비용 증가 | > 30% | cost-review 트리거 (3-plan parallel) |
| latency 증가 | > 20% | 경고 |
| ★ 자문/원금보장/상품추천 차단 단어 검출 | > 0% | **즉시 fail** (도메인 금지 게이트 — advisory_boundary) |

---

## ★ G4 적용 메모 (M2 applies_when 행사)

- **팟캐스트(M1) 대비**: M1 조건부 차원 +2(question_quality/guest_fit, mode==guest 1축). 재무는 +3(debt/insurance/tax) + **데이터 조건(has_debt)도 applies_when 으로 표현** → applies_when 이 enum 모드뿐 아니라 불리언 데이터 조건도 표현함을 확인 (G4 표현력 범용).
- **risk high 연결**: advisory_boundary_compliance 는 무조건 차원이면서 **차단 단어 임계값(>0% → fail)**으로 hard gate — risk high 도메인의 규제 위반(자문 발화)을 eval 게이트로 차단.

---

이 scaffold 는 eval_template 개선본(G4 applies_when 조건부 차원)을 이질 도메인(재무)에 적용 (dry-run, active 아님).
