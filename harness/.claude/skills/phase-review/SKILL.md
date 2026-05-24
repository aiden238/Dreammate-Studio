---
name: phase-review
description: |
  Phase 진행 중간 시점의 health check. phase-start(진입)와 phase-complete(종료)
  사이에서, acceptance 50% 도달 시점, scope creep 의심, 시간 초과 50%+ 등의
  상황에 트리거한다. "어디까지 왔지?" 류 질문에 응답하는 표준 절차.
  키워드: "phase 검토", "phase 점검", "scope creep 확인",
  "phase health check", "phase 중간 점검", "어디까지 왔지".
applies_to: [claude]
phase: [all]
related_contracts:
  - docs/contracts/mvp_non_goals.md
related_state:
  - PHASE_REGISTRY.md
  - PROJECT_STATE.md
  - phases/active/
version: v1.0.0
---

# phase-review

진행 중인 Phase의 건강도(진행률·scope 일치·blocker)를 한 번에 점검하는 절차.

## 트리거 조건

- Phase 중반(acceptance 약 50% 도달 시점)
- scope creep 의심: "이것도 같이" 요청이 누적되거나 commit이 scope.md에서 벗어남
- 예상 시간 50%+ 초과
- 사용자가 "어디까지 왔지?" / "phase 점검" / "scope 괜찮나" 요청
- 다른 Skill 진행 중 blocker가 잡혀 phase 자체를 재평가해야 할 때

## 사용하지 않는 경우

```
- Phase 진입 절차 → phase-start
- Phase 종료 절차 → phase-complete
- 회고/메타 개선 → meta-retrospective
- 하네스 전체 감사 → harness-audit
```

## 절차

### 1. 현재 Phase 로드

```
1. PROJECT_STATE.md → current_phase
2. PHASE_REGISTRY.md → 해당 Phase 상태
3. phases/active/{current-phase}/
   - goals.md
   - scope.md
   - non_goals.md
   - dependencies.md
   - acceptance.md
   - notes.md
```

`notes.md`가 없으면 본 Skill 종료 시 생성 제안.

### 2. commit 매핑

Phase 시작 시점 commit부터 현재까지 git log를 acceptance.md 항목과 매핑:

```
acceptance 항목 1: ✅ commit abc123 (예: design.md 작성)
acceptance 항목 2: ⏳ in-progress
acceptance 항목 3: ⬜ 미착수
```

매핑 안 되는 commit이 있다면 §3 scope creep 검사 대상.

### 3. scope creep 검사

다음 두 단계:

```
A. commit 목록 vs scope.md
   - scope.md에 없는 작업이 commit에 있는가?
B. commit 목록 vs non_goals.md
   - non_goals 항목을 건드린 commit이 있는가?
```

A는 의심, B는 위반. B 발견 시 즉시 사용자 알림 + 작업 중단 권장.

### 4. blocker 식별

다음을 한 줄씩 확인:

- 외부 의존 (다른 Phase 미완, 외부 API 미준비)
- 결정 보류 (사용자 답변 대기)
- 도구 / 환경 문제
- 정보 부족 (contract stub, golden_set 없음)

각 blocker에 후속 Skill 매핑:
- contract stub → `contract-change`
- 평가 자산 부족 → `eval-design`
- 큰 결정 → `multi-llm-validation`

### 5. 추정 시간 갱신

남은 acceptance × 평균 소요 시간으로 잔여 추정. 50%+ 초과 시:

- scope 축소 후보 식별 (필수 vs nice-to-have)
- non_goals.md로 옮길 항목 제안
- Phase 분할 가능성 검토

### 6. dependencies.md 갱신 제안

진행 중 새로 발견된 의존성을 `dependencies.md`에 추가 제안. 직접 수정은 하지 않음 — 사용자 확인 후.

### 7. notes.md 갱신

`phases/active/{current-phase}/notes.md`에 본 점검 결과 append (없으면 생성):

```
## YYYY-MM-DD phase-review
진행률: X/Y acceptance
blocker: ...
액션:    ...
```

## 출력 형식

```
[phase-review 결과] phase-04-mvp-frontend-discovery 2026-05-24
진행률      : 3/7 acceptance (43%)
commit 매핑 : scope 6, scope 외 1 (의심), non-goals 위반 0
scope creep : 의심 1건 — choice_logs UI 개선 commit이 scope.md에 없음
blocker     : output_schema.md §2 미정 → contract-change 트리거 필요
시간        : 추정 60% 사용, 잔여 acceptance 4개
액션        :
  - "choice_logs UI 개선" 작업이 본 Phase 범위인지 사용자 확인
  - contract-change 트리거 (output_schema §2)
  - dependencies.md 에 P-006 prompt 의존 추가 제안
```

## 금지 사항

- scope.md / non_goals.md 직접 수정 (사용자 결정 필요)
- Phase 상태(active/done)를 본 Skill에서 변경 (phase-complete 전담)
- 의심 작업을 임의로 OK 처리 (반드시 사용자 확인)
- non_goals 위반 commit을 발견하고 진행 계속 권장

## 자주 발생하는 실수

1. **commit 매핑 누락**: acceptance 항목과 무관한 commit을 그냥 "관련 작업"으로 분류. 반드시 매핑되지 않는 commit은 §3 검사 대상.
2. **시간 추정 임의값**: 근거 없는 60% 추정. 평균 소요 시간을 commit 수로 나눈 베이스라인 필요.
3. **blocker를 단일 메시지로**: 각 blocker가 어느 후속 Skill로 가는지 명시 안 함. 항상 매핑.
4. **notes.md 안 남김**: 다음 phase-review 때 직전 결과를 못 찾음. 반드시 append.

## 종료 조건

- §1~§7 수행 완료
- notes.md에 결과 append (또는 생성)
- 모든 blocker에 후속 Skill 매핑됨
- non_goals 위반 발견 시 사용자 결정 대기 상태
