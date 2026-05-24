---
name: meta-retrospective
description: |
  Phase 종료 후 또는 반복 실패 발견 시 회고를 작성하고 하네스/프로세스 개선안을
  제안한다. 자동 수정이 아니라 항상 제안 → 검토 → 승인 → 반영 구조. 메타 하네스
  (하네스 자체를 개선하는 작업)의 진입점.
  키워드: "회고", "retrospective", "메타 개선", "반복 실패", "하네스 개선",
  "meta proposal", "프로세스 개선", "post-mortem".
applies_to: [claude]
phase: [all]
related_state:
  - meta/retrospectives/
  - meta/proposals/
  - meta/skill_usage_log.md
version: v1.0.0
---

# meta-retrospective

좋은 회고는 사람을 비판하지 않고 시스템을 비판한다. 같은 실수가 반복되면 그건 사람 문제가 아니라 하네스 문제다.

## 트리거 조건

- phase-complete 7단계에서 자동 호출
- 같은 카테고리 bug-triage가 3회 이상 반복
- prompt-version-review에서 rollback 발생
- cost-review에서 알람 발생
- rag-update에서 회귀 평가 실패
- 사용자가 "회고하자", "이거 왜 자꾸 반복되지?"

## 회고 종류

### 1. Phase 회고

- 트리거: phase-complete 종료 시
- 범위: 한 Phase에서 일어난 일
- 결과물: `meta/retrospectives/{phase-name}.md`

### 2. 반복 실패 회고

- 트리거: 같은 패턴 실수가 2회 이상 발견
- 범위: 패턴 자체
- 결과물: `meta/retrospectives/pattern-{slug}.md`

### 3. Skill 사용 회고

- 트리거: 정기 (월 1회) 또는 Skill이 충돌/누락이 의심될 때
- 범위: Skill 시스템 전체
- 결과물: `meta/retrospectives/skills-{YYYY-MM}.md`

### 4. 하네스 전체 회고

- 트리거: 분기 1회 또는 큰 마일스톤
- 범위: 하네스 전체 구조
- 결과물: `meta/retrospectives/harness-{YYYY-Q}.md`

## 절차

### 1. 데이터 수집

회고 종류에 따라 다음 데이터 모음:

#### Phase 회고

```
- phases/active/{phase-name}/notes.md
- phases/active/{phase-name}/closing_notes.md (있다면)
- 해당 Phase 기간의 bug_reports
- 해당 Phase 기간의 agent_io_logs 통계
- 해당 Phase 기간의 eval 결과
- 해당 Phase 기간의 cost_snapshots
- 해당 Phase 기간의 contract-change 제안서
```

#### 반복 실패 회고

```
- 동일 카테고리 bug_reports 전체
- 발생 시점 / 빈도 / 영향
- 매 발생 시 대응 방식 비교
```

### 2. 분석 프레임

기본 4 질문:

```
1. 잘된 것: 의도대로 작동한 것, 효율적이었던 것
2. 안 된 것: 막힌 것, 실수, 회귀
3. 배운 것: 다음에 적용할 학습
4. 시스템 개선: 같은 실수 안 반복하려면 하네스를 어떻게 바꿀까
```

추가 프레임 (사용 선택):

#### 5 Whys

문제 1개 잡고 "왜?"를 5번 물어 근본 원인 도달.

```
문제: prompt 회귀 평가 통과했는데 운영에서 실패
왜 1: 사용자 입력이 golden_set 케이스보다 다양해서
왜 2: golden_set이 실제 사용자 분포를 반영 못 해서
왜 3: 실제 입력 샘플을 골든셋에 주기적으로 추가 안 해서
왜 4: golden_set 갱신 절차가 명시되지 않아서
왜 5: eval-run Skill에 golden_set 갱신 단계가 없어서
→ 개선안: eval-run에 7단계(golden_set 갱신) 추가
```

#### 영향-빈도 매트릭스

```
        | 영향 작음 | 영향 큼
빈도 낮 |  무시     | 매뉴얼 대응
빈도 높 |  자동화    | 즉시 개선
```

### 3. 회고 문서 작성

`meta/retrospectives/{trigger}-{YYYY-MM-DD}.md`:

```markdown
# Retrospective: {제목}

- 작성일: {YYYY-MM-DD}
- 종류: {phase / pattern / skill / harness}
- 범위: {Phase 식별자 또는 패턴 식별자}
- 작성자: {user 또는 claude}

## 사실 요약
{무슨 일이 있었는지 5–10줄}

## 데이터
- 기간:
- 영향 받은 작업:
- 비용/시간 영향:
- 사용자 영향:

## 분석
### 잘된 것
- 

### 안 된 것
- 

### 배운 것
- 

### 근본 원인 (5 Whys 또는 영향-빈도)
- 

## 개선 제안
{여러 개 가능, 각각 명확하게}

### 제안 1: {이름}
- 무엇을: {바꿀 것}
- 왜: {기대 효과}
- 어디에: {파일 / 프로세스 / Skill}
- 영향: {영향 받는 영역}
- 위험: {부작용 가능성}
- 우선순위: {높음/보통/낮음}

### 제안 2: ...

## 다음 액션
- [ ] 제안 1을 meta/proposals/에 등록
- [ ] 제안 2를 백로그에 추가
- [ ] 관련 Skill 트리거 (contract-change, prompt-version-review 등)
```

### 4. 제안서로 변환

회고에서 나온 개선 제안 중 채택할 것을 `meta/proposals/`로 옮긴다.

이때 contract-change Skill의 제안서 템플릿 사용. 메타 하네스 변경도 contract 변경과 동일한 절차를 따름.

### 5. 자동 수정 금지

```
❌ 절대 금지:
- 회고에서 "이러면 좋겠다"를 바로 코드/문서에 반영
- Skill 자동 갱신
- Contract 자동 갱신
- 사용자 승인 없이 프로세스 변경

✅ 항상:
- meta/proposals/에 제안서 등록
- 사용자에게 검토 요청
- 승인 후 contract-change Skill로 반영
```

### 6. 패턴 인식

여러 회고를 가로질러 보이는 패턴 추출.

`meta/patterns.md`에 누적:

```
- 패턴: "prompt 변경 후 운영 회귀가 골든셋으로 안 잡힘"
  관련 회고: retro-A, retro-B, retro-D
  현재 상태: 개선 진행 중 (proposals/2025-XX-fix-golden-set.md)
  
- 패턴: "Phase 종료 시 docs-sync 빠뜨려 다음 phase 시작 시 갈등"
  관련 회고: retro-C, retro-E
  현재 상태: phase-complete v1.0.0에 docs-sync 단계로 반영됨
```

### 7. Skill 사용 로그 갱신

`meta/skill_usage_log.md`:

```
| Skill | 트리거 횟수 (월) | 마지막 트리거 | 비고 |
|-------|------------------|----------------|------|
| phase-start | 8 | 2026-01-05 | 정상 |
| contract-change | 15 | 2026-01-12 | 정상 |
| rag-update | 0 | - | Phase 8 진입 후 활성화 예정 |
| migration-readiness | 0 | - | Phase 21+ |
```

6개월 0회 트리거된 Skill은 폐기 후보로 표시.

## 자주 발생하는 실수

1. **사람 비판 회고**: "X가 실수했음" → "X가 실수하기 쉬운 시스템이었음"으로 재구성.
2. **개선 제안 없이 분석만**: 회고는 액션이 나와야 함.
3. **회고 후 자동 반영**: 항상 제안서 → 승인 → 반영.
4. **너무 많은 제안**: 5개 이상 제안은 우선순위 안 매김 시 다 흐지부지.
5. **패턴 인식 누락**: 같은 회고가 반복되는데 별개 사건으로 처리.
6. **사실 요약 생략하고 분석부터**: 무슨 일이 있었는지 6개월 뒤에 못 알아봄.

## 다른 Skill과의 관계

```
phase-complete    : 종료 시 자동 호출
bug-triage        : 반복 발견 시 호출
prompt-version-review : rollback 시 호출
cost-review       : 알람 시 호출
contract-change   : 개선 제안 반영 시 거치는 절차
```

## 종료 조건

- 회고 문서 작성 + 채택된 제안의 meta/proposals/ 등록 → 정상 종료
- 사용자가 회고 자체를 보류 → 데이터만 보관 후 종료
- 긴급 패턴 발견 (security/cost) → 즉시 contract-change 트리거 후 종료
