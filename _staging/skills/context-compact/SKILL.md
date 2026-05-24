---
name: context-compact
description: |
  긴 세션에서 컨텍스트 윈도우가 차고 있을 때, 또는 다른 세션/모델로 작업을
  넘길 때, 무엇을 보존하고 무엇을 버릴지 절차로 압축한다. 풀스케일 하네스
  + 장기 Phase 운용 시 필수. 모든 Skill 위에서 최우선 트리거.
  키워드: "컨텍스트 압축", "context compaction", "session 길어짐", "요약하고 새 세션",
  "이어서 작업", "handoff", "대화 압축", "context full".
applies_to: [claude]
phase: [all]
related_state:
  - PROJECT_STATE.md
  - phases/active/
  - meta/handoffs/
version: v1.0.0
---

# context-compact

긴 세션은 컨텍스트 윈도우만 차지하는 게 아니라 모델 attention 품질도 떨어뜨린다. 적절한 시점에 압축하고 다음 세션으로 이어가는 게 신호 손실을 최소화한다.

## 트리거 조건

- 한 세션이 60K 토큰 이상으로 커진 경우
- 한 세션이 4시간 이상 지속된 경우
- 다른 모델/사용자에게 작업을 넘겨야 할 때
- 사용자가 "정리하고 새 세션에서 이어가자"
- Phase가 길어 한 세션에 끝나지 않을 때
- 명백한 attention drift 신호 (모델이 앞의 결정 잊거나, 같은 작업 반복)

## 우선순위

context-compact는 **다른 모든 Skill 위에 우선 트리거**된다. 컨텍스트가 부족하면 다른 Skill 실행 품질도 다 떨어지기 때문.

## 압축 절차

### 1. 현재 상태 스냅샷

세션을 끝내기 전 다음 정보를 정리:

```
## Session Snapshot

### 작업 중 Phase
- Phase: {phase-name}
- 시작 시점:
- 현재 진행률: 약 N% (acceptance.md 기준)

### 결정 누적 (이 세션에서 결정한 것)
- {결정 1}
- {결정 2}
- ...

### 미해결 질문
- {다음 세션에 결정해야 할 것 1}
- {결정해야 할 것 2}

### 작성된 / 변경된 파일
- {파일 경로 + 한 줄 요약}

### 미작성 (해야 하는데 못 한 것)
- {작업 단위}

### 발견된 이슈
- {나중에 처리할 이슈}

### 컨텍스트 핵심 (다음 세션이 알아야 할 것)
- {프로젝트 한 줄 요약}
- {지금 작업의 한 줄 목표}
- {핵심 제약 3–5개}
- {지금 막힌 지점 또는 다음 첫 작업}
```

### 2. 보존 vs 버림 분류

이 세션의 대화 내용을 다음 세 묶음으로 분류:

```
A. 영구 보존 (PROJECT_STATE / 결정 / 산출물)
   - 결정 내용
   - 만들어진 파일
   - 합의된 contract 변경
   - 검증 결과
   → 해당 파일/contract에 반영

B. 다음 세션 컨텍스트 (handoff package)
   - 현재 작업 상태
   - 미해결 질문
   - 다음 첫 작업
   - 핵심 컨텍스트 5–10줄
   → handoff 문서로 정리

C. 버릴 것 (탐색/시행착오/대화 잡담)
   - 시도했다 폐기한 방향
   - 의견 교환만 한 대화
   - 같은 정보 반복
   → 폐기, 단 회고에 패턴은 추출
```

### 3. PROJECT_STATE / 관련 문서 갱신

영구 보존 항목을 실제 파일에 반영:

```
PROJECT_STATE.md
  current_phase
  current_progress (요약)
  open_issues
  next_actions

phases/active/{phase}/notes.md
  이 세션의 진행 메모 누적

phases/active/{phase}/decisions.md
  이 세션에서 결정한 것 누적

docs/decisions/  
  ADR로 격상할 큰 결정은 별도 파일

meta/handoffs/{YYYY-MM-DD}.md  
  다음 세션용 핸드오프 패키지
```

contracts 변경이 필요한 결정은 contract-change Skill을 통한다.

### 4. 핸드오프 패키지 작성

`meta/handoffs/{YYYY-MM-DD-HHMM}.md`:

```markdown
# Session Handoff

- 종료 일시: {YYYY-MM-DD HH:MM}
- 다음 세션 예정: {언제, 같은 사람 / 다른 사람 / 다른 모델}
- Phase: {phase-name}

## 30초 요약 (다음 세션 시작 시 가장 먼저 읽기)
{3–5문장으로 지금 어디 있고 다음에 뭘 할지}

## 핵심 컨텍스트
{프로젝트, Phase, 제약 5–10줄}

## 진행 상태
- 완료: {목록}
- 진행 중: {지금 막힌 지점}
- 미시작: {예정 작업}

## 미해결 질문
- {질문 1} — 결정 책임자: {user / claude / 추가 자료 필요}
- {질문 2}

## 다음 첫 작업
{한 시간 안에 끝낼 수 있는 작업 단위}
- 입력: {필요한 컨텍스트}
- 산출물: {기대 결과}
- 사용할 Skill: {Skill 이름}

## 참조 파일 (다음 세션이 우선 열어볼 것)
1. PROJECT_STATE.md
2. phases/active/{phase}/{file}
3. {기타}

## 함정 / 주의
- {이전 세션에서 발견한 함정}
- {반복 실수 패턴}
```

### 5. 새 세션 시작 절차

다음 세션이 시작될 때 (같은 모델이든 다른 모델이든):

```
1. PROJECT_STATE.md 읽기
2. 최신 meta/handoffs/{...}.md 읽기 (30초 요약 + 핵심 컨텍스트)
3. phase-start Skill 트리거 (현재 phase 컨텍스트 재구성)
4. 다음 첫 작업으로 진입
```

새 세션이 위 절차를 무시하고 곧장 작업하려 하면 context-compact가 즉시 막아야 함.

## 토큰 임계값 가이드

```
< 20K   : 정상, 압축 불필요
20–40K  : 모니터링, 슬슬 정리 준비
40–60K  : 압축 권장, 큰 결정 마무리하고 휴식
60–80K  : 압축 필수, 새 세션 시작
> 80K   : 위험, 즉시 압축
```

이 임계값은 모델별로 다름. Claude는 200K context지만 attention 품질은 60K부터 떨어지기 시작.

## 압축 종류

### A. 부분 압축 (in-session)

세션 도중 일부 정보 정리:

```
- 결정된 사항을 PROJECT_STATE에 즉시 반영
- 시행착오 폴더(작성한 코드 중 폐기한 것) 삭제
- 같은 정보 반복 출력 방지
- 결정 요약 카드 작성 후 본문 압축
```

비용 적고 자주 가능.

### B. 전체 압축 (session end)

세션 끝낼 때 full handoff package 작성.

위 1–4단계 모두 수행.

### C. 긴급 압축 (context near full)

토큰 한계 임박:

```
1. 즉시 30초 요약만 작성
2. 미저장 결정사항만 PROJECT_STATE에 반영
3. 최소 핸드오프 패키지 (다음 첫 작업만)
4. 세션 종료
```

후속: 다음 세션에서 정식 압축 보완.

## 다른 모델로 핸드오프 시 추가 작업

multi-LLM 워크플로 일부:

```
1. 받는 모델이 모르는 우리만의 용어 풀이
   ("Discovery Mode", "4계층" 등 → 1줄 정의)

2. 받는 모델이 우리 contracts를 읽을 수 있는지 확인
   (Claude Code는 가능, ChatGPT는 수동 첨부)

3. 받는 모델의 강점에 맞춘 작업 분배
   (코드 구현은 Codex, 검토는 Claude 같은)

4. 받은 결과를 다시 우리 컨텍스트로 통합
   (별도 통합 단계로 분리)
```

multi-llm-validation Skill과 조합.

## 자주 발생하는 실수

1. **세션 끝낼 때 압축 안 하고 종료**: 다음 세션이 처음부터 헤맴.
2. **핸드오프에 30초 요약 누락**: 정보는 다 있는데 어디서 시작할지 모름.
3. **버려야 할 대화를 보존**: 컨텍스트 비용만 늘어남.
4. **PROJECT_STATE 갱신 누락**: handoff 문서와 PROJECT_STATE 불일치.
5. **긴급 압축인데 정식 압축처럼 시간 씀**: 토큰 한계 도달 직전엔 최소만.
6. **새 세션이 PROJECT_STATE 안 읽고 시작**: phase-start Skill 우선 트리거 필요.

## 다른 Skill과의 관계

```
모든 Skill   : 컨텍스트 부족 신호 시 context-compact가 우선 트리거됨
phase-start  : 새 세션 시작 시 항상 phase-start 호출
phase-complete : phase 종료와 context 압축이 겹치면 phase-complete + 핸드오프
multi-llm-validation : 다른 모델로 넘길 때 핸드오프 패키지 그대로 사용
contract-change : 압축 중 발견된 contract 변경 필요는 별도 처리
```

## 종료 조건

- 핸드오프 패키지 완성 + PROJECT_STATE 갱신 → 정상 종료, 새 세션 진입 권한
- 긴급 압축 → 최소 정보 보존 후 종료, 다음 세션에서 보완
- 사용자가 압축 거부 (계속 같은 세션) → 부분 압축만 수행 후 작업 계속
