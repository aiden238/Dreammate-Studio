---
name: cost-review
description: |
  LLM API 비용과 인프라 비용을 점검할 때 사용한다. 요청당 LLM 호출 수,
  토큰 사용량, 모델별 비용 분포, 실패 요청 비용, 사용자별 사용량 상한
  위반 여부를 분석하고, 최적화 제안 또는 저비용 모드 도입을 권장한다.
  키워드: "비용 검토", "cost review", "LLM cost", "token usage", "비용 폭탄",
  "예산 초과", "비용 분석", "agent_io_logs 분석".
applies_to: [agents, claude]
phase: [phase-9, phase-10, ongoing]
related_contracts:
  - docs/contracts/rate_limit_policy.md
  - docs/contracts/db_schema.md (agent_io_logs)
related_state:
  - agent_io_logs (DB 테이블)
  - eval/cost_snapshots/
version: v1.0.0
---

# cost-review

LLM 비용은 작은 누수가 쌓여 한 달 운영비를 위협할 수 있다. 정기 점검과 임계값 기반 알람을 강제한다.

## 트리거 조건

- 정기 (주 1회)
- prompt-version-review 5단계 활성화 +14일 자동
- 사용자 또는 운영자 비용 알람
- qa-check의 카테고리 7 fail
- 새 모델 도입 후

## 점검 단위

### 1. 세션당 비용

`agent_io_logs`에서 `request_id` 기준 그룹화:

```sql
select
  request_id,
  count(*)         as llm_calls,
  sum(input_tokens) + sum(output_tokens) as total_tokens,
  sum(cost_usd)    as session_cost
from agent_io_logs
where created_at > now() - interval '7 days'
group by request_id;
```

#### 기준값 (Discovery 1세션)

```
LLM 호출 수    : 11–14회 정상, 20회 초과는 이상
총 토큰        : 15K 정상, 30K 초과는 이상
세션 비용      : $0.008–0.012 정상, $0.05 초과는 이상
latency 총합   : 30–60s 정상, 120s 초과는 이상
```

#### 기준값 (Quick 1세션)

```
LLM 호출 수    : 7–10회 정상, 15회 초과는 이상
총 토큰        : 10K 정상
세션 비용      : $0.005–0.008 정상
```

### 2. 사용자별 일일 비용

```sql
select user_id, date_trunc('day', created_at) as day,
       sum(cost_usd) as daily_cost,
       count(distinct request_id) as sessions
from agent_io_logs
where created_at > now() - interval '30 days'
group by user_id, day;
```

#### 기준값 (무료 티어 기준)

```
일일 비용        : $0.10 미만 정상
일일 세션 수     : 5세션 미만 정상
주간 비용        : $0.50 미만 정상
```

티어별 상한 변경은 `rate_limit_policy.md` 변경 → contract-change.

### 3. Prompt별 비용

```sql
select prompt_id, prompt_version, model,
       avg(input_tokens + output_tokens) as avg_tokens,
       avg(cost_usd)                     as avg_cost,
       count(*)                          as calls,
       sum(cost_usd)                     as total
from agent_io_logs
where created_at > now() - interval '7 days'
group by prompt_id, prompt_version, model;
```

비용 큰 prompt 식별. 보통 `P-006`(plan_candidates)이 가장 큼.

### 4. 실패 비용

실패한 호출도 토큰을 쓰면 비용 발생.

```sql
select prompt_id, count(*) as failures,
       sum(input_tokens + output_tokens) as wasted_tokens,
       sum(cost_usd) as wasted_cost
from agent_io_logs
where error is not null
  and created_at > now() - interval '7 days'
group by prompt_id;
```

실패율이 5% 초과 → bug-triage Skill (JSON Parsing 카테고리).

### 5. 모델별 분포

```
gpt-4o-mini       : 80% 이상이 정상
gpt-4o            : 5–10% (high-quality 평가용)
Claude Haiku      : 0–10% (보조)
local embedding   : 별도 카운트
```

비싼 모델 비중이 갑자기 늘면 누군가 모델 다운그레이드 안 한 코드 경로 있음.

## 절차

### 1. 위 5개 단위 모두 쿼리 실행

기간: 지난 7일 (정기) 또는 마지막 변경 시점 이후 (이벤트성).

### 2. 임계값 비교

```
| 지표 | 임계값 | 위반 시 |
|------|--------|---------|
| 세션당 비용 (P95) | $0.05 | 즉시 분석 |
| 세션당 호출 수 (P95) | 20 | 파이프라인 점검 |
| 사용자 일일 비용 | $0.10 | rate limit 차단 |
| 실패율 | 5% | bug-triage |
| 비싼 모델 비중 | 20% | 코드 경로 분석 |
| 주간 총 비용 증가 | +30% w/w | 즉시 alert |
```

### 3. 위반 분석

각 위반에 대해 원인 가설:

```
세션당 호출 수 ↑ : 같은 prompt 반복 호출 / 재시도 루프 / Critic 무한 revise
세션당 비용 ↑    : 큰 모델 사용 / RAG context 과대 주입 / max_tokens 큼
실패율 ↑         : prompt 변경 / 모델 변경 / 입력 형식 변화
일일 비용 ↑      : 한 사용자 abuse / API key 유출
```

### 4. 최적화 제안

```
A. 캐싱 강화
   - 같은 입력 해시 반복 시 캐시 hit 비율 확인
   - 24h TTL 적용 가능한 prompt 식별

B. 모델 다운그레이드
   - Critic Agent: gpt-4o-mini로 충분한지 평가
   - Hook 평가: 더 작은 모델 가능?

C. context 다이어트
   - RAG chunk 수 3 → 2로 줄이기
   - prompt에서 불필요한 예시 제거
   - Brand Memory 주입 시 가장 중요한 N개만

D. 실패 재시도 제한
   - JSON 파싱 실패 재시도 1회로 제한
   - exponential backoff 적용

E. 저비용 모드
   - 유료 티어 전 사용자에게 "빠른 모드" (Critic 생략) 제공
   - bulk 처리 시 batch API 활용
```

### 5. 결과 기록

`eval/cost_snapshots/{YYYY-MM-DD}.md`:

```markdown
# Cost Review {YYYY-MM-DD}

## 기간 요약
- 기간: {start} ~ {end}
- 총 비용: $X.XX
- 총 호출: N
- 평균 세션 비용: $X.XX
- w/w 변화: +X%

## 위반 항목
{있으면 나열}

## Prompt별 비용 분포
{표}

## 모델별 분포
{표}

## 권장 최적화
{우선순위 순 3–5개}

## 다음 점검
- 정기: {다음 주 같은 요일}
- 트리거 기반: {prompt-version-review 등으로 자동}
```

### 6. 위반 시 후속 작업

```
즉시 차단 필요    → rate limit 임시 강화 (API 단)
prompt 최적화 필요 → prompt-version-review Skill
파이프라인 수정    → 새 phase 진입 (phase-start)
긴급 alert         → 사용자/팀에게 알림 + 운영 모드 일시 변경
```

## 비용 폭탄 시나리오와 대응

### 시나리오 1: 한 사용자가 자동화 스크립트로 abuse

- 발견: 같은 user_id가 분당 10세션 이상
- 대응: rate_limit_policy의 분당 상한 적용 → API 단 차단
- 후속: 해당 user_id 검토, 영구 차단 여부 결정

### 시나리오 2: Critic 무한 revise 루프

- 발견: 같은 request_id에 Critic이 10회 이상 호출
- 대응: Critic revise 최대 횟수 강제 (보통 2회)
- 후속: prompt-version-review로 Critic prompt 점검

### 시나리오 3: RAG context 폭증

- 발견: input_tokens가 평소 2배 이상
- 대응: top_k 임시 축소 (5 → 3)
- 후속: rag-update로 RAG 인덱스 정리

### 시나리오 4: 모델 다운그레이드 누락

- 발견: 새 Phase 진입 후 gpt-4o 호출 비중 급증
- 대응: 환경 변수 / 코드 경로 점검
- 후속: bug-triage (코드 영역) + phase-complete docs-sync 강화

## 자주 발생하는 실수

1. **정기 점검 미실시**: 한 달 뒤에 큰 청구서로 발견.
2. **사용자별 분석 생략**: 일부 abuser가 비용 80% 소모.
3. **실패 비용 무시**: 실패해도 input tokens는 소모됨.
4. **prompt별 분리 없이 합계만**: 어디 prompt가 비싼지 모름.
5. **알람 임계값 너무 높음**: 폭증 후에 알람.
6. **w/w 변화율 안 봄**: 절대값만 보면 점진적 증가 못 잡음.

## 다른 Skill과의 관계

```
qa-check              : 카테고리 7 위반 시 cost-review 호출
prompt-version-review : 활성화 +14일 자동 호출
rag-update            : context 폭증 시
bug-triage            : 실패율 ↑ 또는 코드 경로 이슈 시
contract-change       : rate_limit_policy 또는 임계값 변경 시
```

## 종료 조건

- 위반 없음 → 정상 종료, 다음 정기 점검 일정 등록
- 위반 있음 + 후속 Skill 위임 → 위임 후 종료
- 긴급 차단 필요 → 즉시 rate limit 강화 + 사용자 알림 + meta-retrospective 트리거
