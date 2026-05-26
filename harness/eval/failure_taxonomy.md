# failure_taxonomy.md — 실패 분류 체계

> 위치: `eval/failure_taxonomy.md`
> 상태: Phase 0–1 진입용 베이스라인
> 참조: `docs/contracts/error_response_contract.md` §2 7 카테고리, §4 코드 사전
> 참조: `meta/patterns.md` (패턴 추출 누적)
> 참조: `eval/regression_eval.md` (회귀 실패 분류)

---

## 1. 목적

영상기획 AI 에이전트에서 발생하는 모든 실패를 일관된 분류로 묶어, 빈도 / 심각도 / 회복 가능성을 정량 측정한다. 실패 패턴은 `meta/patterns.md`에 누적되어 회고와 prompt 개선의 입력이 된다. error_response_contract의 7 카테고리를 1차 분류, 본 문서가 2차 세부 분류 + 분석 차원을 정의한다.

---

## 2. 평가 차원 (5 개)

### 2.1 category_distribution — 카테고리별 분포

```
정의: error_response_contract §2의 7 카테고리(INV/LLM/RAG/DB/RL/SEC/UNK) 발생 비율.
측정: 일/주/월 누적 카운트 + 비율.
임계 (정상 운영 baseline):
  - INV (input_validation): 5~15%
  - LLM (llm_failure): 1~3%
  - RAG (rag_failure): 0~1%
  - DB (db_failure): 0~0.1%
  - RL (rate_limit): 0~2% (정상 동작)
  - SEC (security_block): 0.1~1%
  - UNK (unknown): 0% 지향 (1건이라도 운영자 알림)
임계 초과 시 운영자 알림 (error_response_contract §10).
```

### 2.2 severity_distribution — 심각도별 분포

```
정의: 사용자 영향 / 데이터 손실 / 보안 사고 기준 심각도.
측정:
  S1 (critical) — 데이터 손실 / 보안 사고 / 다수 사용자 차단
  S2 (high)     — 한 사용자 세션 차단 + 부분 결과도 못 줌
  S3 (medium)   — 부분 결과는 노출, 일부 단계 실패
  S4 (low)      — warning만, 정상 동작
임계:
  - S1 = 0건 / 월 지향
  - S2 ≤ 5건 / 월
  - S3 ≤ 50건 / 월
  - S4 unlimited
```

### 2.3 recoverability — 회복 가능성

```
정의: 실패에서 회복 가능한 비율.
측정 (error_response_contract §8):
  - auto_retry_success: 자동 재시도 1~2회 성공
  - fallback_success: mini 모델 폴백 또는 partial_result 노출 성공
  - user_action_success: 사용자가 재시도 또는 reframe 후 성공
  - terminal: 회복 불가, 사용자 이탈
임계:
  - auto_retry_success + fallback_success ≥ 70%
  - terminal ≤ 5%
```

### 2.4 pattern_extraction — 패턴 추출도

```
정의: 누적 실패에서 추출된 공통 패턴 수.
측정: meta/patterns.md에 등록된 패턴 / 누적 실패 카운트.
임계: 월 ≥ 3개 패턴 추출
0점: 누적 100건 이상에서 패턴 0
5점: 매월 ≥ 5개 패턴 + 운영자 액션 반영
```

### 2.5 false_positive_rate — false positive 비율

```
정의: "실패"로 분류됐으나 실제로는 정상 케이스 비율.
측정:
  - 사용자 신고 ("정상 입력이 차단됐다")
  - 운영자 사후 검토에서 false positive 판정
임계 (카테고리별):
  - SEC: ≤ 2% (보안은 보수적, 약간의 false positive 허용)
  - INV: ≤ 1%
  - 기타: ≤ 0.5%
```

---

## 3. 실패 분류 표 (2차 세부)

### 3.1 INV — input_validation

```
INV-A 필수 필드 누락 (E-INV-001)
INV-B 필드 검증 (E-INV-002 ~ 004)
INV-C 권한 / 무결성 (E-INV-005 ~ 007)
INV-D JSON parse (E-INV-008)
INV-E 파일 업로드 (E-INV-009, Phase 2+)
```

### 3.2 LLM — llm_failure

```
LLM-A timeout (E-LLM-001)
LLM-B JSON parse / output_schema (E-LLM-002, 003, 007, 008)
LLM-C API 5xx / 4xx (E-LLM-004, 005)
LLM-D 광고 단어 / 검증 실패 (E-LLM-006)
LLM-E 비용 한도 (E-LLM-009)
LLM-F revise 무한 루프 (E-LLM-010)
```

### 3.3 RAG — rag_failure

```
RAG-A pgvector 검색 (E-RAG-001)
RAG-B 임베딩 API (E-RAG-002)
RAG-C 결과 0건 (E-RAG-003, warning이지 에러 아님)
RAG-D DB 연결 (E-RAG-004)
RAG-E 승격 흐름 (E-RAG-005)
```

### 3.4 DB — db_failure

```
DB-A 연결 (E-DB-001)
DB-B 제약 위반 (E-DB-002)
DB-C 동시성 / 트랜잭션 (E-DB-003)
DB-D 스토리지 (E-DB-004)
DB-E RLS / 권한 (E-DB-005)
DB-F query timeout (E-DB-006)
```

### 3.5 RL — rate_limit

```
RL-A 사용자 일일 비용 (E-RL-001)
RL-B 사용자 분당 (E-RL-002)
RL-C 세션당 호출 (E-RL-003)
RL-D IP 차단 (E-RL-004)
RL-E 영상 생성 횟수 (E-RL-005)
```

### 3.6 SEC — security_block

```
SEC-A prompt injection (E-SEC-001)
SEC-B intent block (E-SEC-002)
SEC-C 광고 표현 (E-SEC-003)
SEC-D 부적절 콘텐츠 (E-SEC-004)
SEC-E XSS (E-SEC-005)
SEC-F PII 노출 (E-SEC-006)
SEC-G 계정 도용 (E-SEC-007)
```

### 3.7 UNK — unknown

```
UNK-A 분류되지 않은 server (E-UNK-001)
UNK-B 외부 서비스 (E-UNK-002)
UNK-C catch-all (E-UNK-999)
```

---

## 4. 입력 / 출력 형식

### 4.1 입력 (정기 분석)

```yaml
analysis_period: "2026-05-01 ~ 2026-05-31"   # 일/주/월
data_sources:
  - "errors.log"
  - "intent_filter_logs"
  - "agent_io_logs.error"
  - "audit_log"
filter:
  user_segment: null | "free" | "paid"
  phase: null | "phase-0"
```

### 4.2 출력

```yaml
period: "..."
total_failures: 1234
category_distribution:
  INV: 0.12
  LLM: 0.03
  RAG: 0.005
  DB: 0.001
  RL: 0.02
  SEC: 0.008
  UNK: 0.0001
severity_distribution:
  S1: 0
  S2: 3
  S3: 45
  S4: 1186
recoverability:
  auto_retry_success: 0.72
  fallback_success: 0.15
  user_action_success: 0.10
  terminal: 0.03
patterns_extracted: 4
false_positive_rate:
  SEC: 0.015
  INV: 0.005
scores:
  category_distribution: 0~5
  severity_distribution: 0~5
  recoverability: 0~5
  pattern_extraction: 0~5
  false_positive_rate: 0~5
taxonomy_health_avg: 0~5
```

---

## 5. 자동 평가 vs 수동 평가

| 차원 | 자동 | 수동 |
|---|---|---|
| category_distribution | 자동 (logs 집계) | 운영자 검토 |
| severity_distribution | 자동 (severity 룰 매핑) | 운영자 1차 (S1, S2 검증) |
| recoverability | 자동 (재시도 / 폴백 결과 추적) | 운영자 보조 |
| pattern_extraction | 자동 (clustering) + 운영자 | 운영자 주도 |
| false_positive_rate | 자동 (사용자 신고) + 운영자 | 운영자 주도 |

---

## 6. 임계값

```
모든 차원 ≥ 3: passing (운영 건전)
1 차원이라도 < 3: warning
1 차원이라도 < 2: failing (긴급 회고 트리거)

특수 게이트:
- S1 ≥ 1건: 즉시 운영자 알림 + 사후 audit
- UNK ≥ 1건: 즉시 분류 + 코드 추가
- terminal > 10%: 회복 정책 재검토 (revise / fallback 강화)
- SEC false_positive > 5%: 인젝션 패턴 재검토 (false positive 잡기)
```

---

## 7. meta/patterns.md 연동

`meta/patterns.md`에 다음 형식으로 패턴 누적:

```yaml
pattern_id: P-001
discovered_at: 2026-05-26
category: LLM-B
description: "JSON parse 실패가 P-006에서만 발생, 다른 prompt는 정상"
frequency: 23회 / 1주
root_cause: "P-006 prompt가 markdown 코드펜스를 자주 포함"
action: "P-006 system prompt에 'JSON만 응답' 강조 추가"
status: open | in_progress | resolved
```

운영자가 매월 meta-retrospective Skill에서 패턴 회고 + 액션 검토.

---

## 8. 관련 contract / Skill 연결

```
contract:
  - error_response_contract.md (전체)
  - llm_security_contract.md §3 (SEC-A ~ G)
  - rate_limit_policy.md (RL-A ~ E)

Skill:
  - meta-retrospective (월간 패턴 회고)
  - harness-audit (분류 체계 자체의 audit)
  - contract-change (새 카테고리 추가 시)

연관 평가:
  - regression_eval.md (회귀 실패도 본 분류 적용)
  - security_eval.md (SEC 차원 본체)
  - phase_eval.md (Phase 종료 시 누적 분포 확인)
```

---

## 9. Open Questions

1. UNK 카테고리의 zero 지향이 현실적인가 — 누적 1년 후 통계로 재평가.
2. severity 룰 매핑 자동화 — 룰 기반 vs LLM-as-judge.
3. 패턴 추출 클러스터링 알고리즘 — embedding 기반 vs 토큰 빈도.
4. false_positive_rate의 사용자 신고 채널 — 현재 없음, Phase 1에서 신고 버튼 도입 필요.
5. terminal 5% 이상 시 자동 액션 — 현재 운영자 알림만, 자동 회복 정책 강화 가능한가.
6. 다국어 시 카테고리 분포 차이 측정 — Phase 2+.
