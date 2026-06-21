---
name: bug-triage
description: |
  버그 또는 예상치 못한 동작 발견 시 사용한다. 원인 영역 분류, 재현 절차 정리,
  영향 범위 파악, 임시 우회 방법 확인, 수정 phase 생성 여부 결정까지 한 번에 처리한다.
  키워드: "버그", "bug", "오류", "에러 발생", "재현", "exception", "안 됨",
  "예상과 다름", "fix phase", "긴급 수정", "버그 수정", "fix", "hotfix".
applies_to: [agents]
phase: [all]
gate: mandatory  # 버그 수정 진입 전 강제 통과 게이트 (2026-06-21, HIP-C)
related_contracts:
  - docs/contracts/event_log_contract.md
related_state:
  - PHASE_REGISTRY.md
  - phases/active/
version: v1.1.0
---

# bug-triage

버그 발견 시 즉시 코드 수정에 들어가지 말고 분류부터 한다. 잘못된 영역을 고치는 시간이 분류에 쓰는 시간보다 훨씬 비싸다.

> ## ★ 강제 게이트 (v1.1.0, HIP-C — 2026-06-21)
>
> **버그 수정은 이 Skill을 우회할 수 없다.** "버그/오류/안 됨/에러/fix" 신호가 있으면 코드 한 줄
> 고치기 전에 **반드시** §1~§7 분류를 먼저 수행하고 분류 결과(`docs/bug_reports/{date}-{slug}.md`)를
> 남긴다. 우선순위 표(`instruction_index/priority_rules.md`)에서도 `bug-triage`는 정상 흐름을
> 일시 정지시키는 인터럽트 게이트다.
>
> **게이트 면제(예외)** — 아래만 triage 기록 없이 즉시 수정 가능:
> - 1줄 오타/타입/import 등 **자명한 기계적 수정**(원인 영역이 100% 명확).
> - 이미 동일 버그의 triage 기록이 존재하는 **연속 수정**.
> - **green 회복용 테스트/빌드 즉시 수정**(단, 사후 1줄 기록 권장).
>
> 그 외 모든 "왜 이런지 모르겠는" 동작·다영역 의심·재현 불명은 **분류 의무**. 분류 없이 수정 시작 =
> 절차 위반(가장 흔한 회귀 원인, §자주 발생하는 실수 1).

## 트리거 조건

- 사용자가 "안 돼", "이상한 결과 나옴", "에러 나" 같은 보고
- 테스트 실패
- agent_io_logs에서 error 비율 임계값 초과
- eval 회귀 실패
- 모니터링 알람

## 절차

### 1. 즉각적 수정 차단

버그 보고가 들어와도 **즉시 코드 수정에 들어가지 않는다**. 분류가 먼저.

### 2. 영역 분류

다음 9개 카테고리 중 어디에 해당하는지 판정:

```
1. Frontend UI      - 렌더링, 스타일, 인터랙션 오류
2. Frontend Logic   - 상태 관리, 라우팅, 폼 검증
3. API              - HTTP status, 응답 형식, 인증
4. DB               - 쿼리, 마이그레이션, 인덱스
5. RAG              - 검색 결과 부정확, 임베딩 오류
6. LLM Response     - schema 미준수, 비논리적 출력
7. JSON Parsing     - 응답 파싱 실패
8. Cost / Rate Limit - 한도 초과, 비용 폭주
9. Auth / Permission - 권한, RLS, 세션
```

판정 근거를 명시. 헷갈리면 복수 선택 가능 (예: "LLM Response + JSON Parsing").

### 3. 재현 절차 작성

다음 형식으로 정리:

```
## 재현 절차
환경: {prod / staging / local}
사용자: {user_id 또는 익명}
입력: {버그 발생까지의 입력 시퀀스}
기대: {기대했던 동작}
실제: {실제 동작}
빈도: {1회 / 간헐적 / 매번}

## 로그 단서
agent_io_logs:
  {관련 log_id 목록}
event_logs:
  {timestamp + event}
스택 트레이스:
  {있다면}
```

재현 안 되면 → **재현 가능할 때까지 코드 수정 금지**. "Heisenbug"는 별도 처리 절차.

### 4. 영향 범위 파악

```
- 영향 받는 사용자: {1명 / 일부 / 전체}
- 영향 받는 기능: {화면, API, AI agent}
- 데이터 손상 가능성: {없음 / 있음}
- 보안 영향: {없음 / 있음}
- 비용 영향: {없음 / 있음}
```

데이터 손상 또는 보안 영향이 있으면:
- 즉시 영향 차단 (해당 기능 일시 비활성)
- 보안 영역이면 security-review Skill 추가 트리거

### 5. 임시 우회 방법 검토

수정 전에 사용자가 작업을 이어갈 수 있는 우회 방법 있는지:

```
- 다른 경로로 같은 작업 가능?
- 일부 기능 비활성으로 나머지 사용 가능?
- 수동 처리 가능?
```

있으면 사용자에게 즉시 안내.

### 6. 수정 Phase 생성 여부 결정

| 긴급도 | 처리 방식 |
|---|---|
| **Critical** (데이터 손상 / 보안 / 매출 영향) | 현재 작업 중단, hotfix phase 즉시 생성 |
| **High** (핵심 기능 불가, 다수 사용자 영향) | 현재 phase 끝나는 대로 fix phase |
| **Medium** (일부 기능, 우회 가능) | 다음 정규 phase에 포함 |
| **Low** (사소, 1명 영향) | 백로그 추가, 우선순위 낮음 |

Critical / High는 phase-start Skill로 새 phase 진입.

### 7. 분류 결과 기록

`docs/bug_reports/{YYYY-MM-DD}-{slug}.md`에 다음 형식으로 저장:

```markdown
# Bug Report: {짧은 제목}

- 발견일: {YYYY-MM-DD}
- 보고자: {user_id 또는 시스템}
- 분류: {9개 카테고리 중 선택}
- 긴급도: {Critical / High / Medium / Low}
- 상태: triaged → fixing → fixed → verified → closed

## 재현 절차
{2단계 내용}

## 영향 범위
{3단계 내용}

## 임시 우회
{4단계 내용}

## 수정 계획
- Phase: {hotfix-001 or 기존 phase}
- 예상 작업: {파일 또는 영역}
- 예상 소요: {시간}

## 후속
- 회귀 테스트 추가 필요: 예/아니오
- golden_set에 케이스 추가 필요: 예/아니오
- contract 변경 필요: 예/아니오 (있으면 contract-change Skill)
```

## 분류 가이드

### Frontend UI vs Frontend Logic

```
UI:    화면이 깨짐, 색이 잘못, 버튼이 안 보임 → CSS / 컴포넌트 트리
Logic: 클릭은 되는데 결과가 잘못, 상태가 안 바뀜 → 상태/이벤트
```

### LLM Response vs JSON Parsing

```
LLM:    응답은 JSON인데 내용이 비논리 → prompt 문제 (prompt-version-review 후속)
Parser: 응답이 JSON 아니거나 schema 어김 → output_schema 또는 prompt
```

### RAG vs LLM Response

```
RAG:  관련 없는 chunk가 반환됨 → 임베딩 / 인덱스 / 쿼리
LLM:  RAG는 잘 가져왔는데 답변이 이상 → prompt 또는 모델
```

## 다른 Skill과의 관계

```
contract-change       : 수정이 contract에 영향 시
prompt-version-review : LLM Response 또는 JSON Parsing 카테고리일 때
security-review       : 보안 영향 카테고리일 때
cost-review           : Cost / Rate Limit 카테고리일 때
rag-update            : RAG 카테고리일 때
phase-start           : Critical/High일 때 hotfix phase 진입
```

## 자주 발생하는 실수

1. **분류 없이 코드부터 수정**: 다른 영역 고침.
2. **재현 안 되는데 수정 시도**: 같은 버그 재발.
3. **영향 범위 파악 없이 fix**: 다른 곳 회귀 발생.
4. **임시 우회 안 알려줌**: 사용자가 멈춰있음.
5. **bug report 작성 안 함**: 같은 분류의 버그가 반복돼도 패턴 인식 안 됨.
6. **golden_set에 케이스 추가 안 함**: 동일 버그 회귀.

## 종료 조건

- 분류 완료 + 수정 계획 결정 → 정상 종료 (수정 작업은 별도 Skill/Phase로 위임)
- 재현 불가 → "Heisenbug" 태그로 분류만 기록, 모니터링 강화 후 종료
- Critical → hotfix phase 진입 후 종료
