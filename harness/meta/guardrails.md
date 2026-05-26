# guardrails.md — 시스템 가드레일

> 위치: `meta/guardrails.md`
> 상태: Phase 0 Sprint S5 deep 작성 (placeholder 해소)
> 참조: `docs/contracts/llm_security_contract.md`, `docs/contracts/rate_limit_policy.md`
> 참조: `docs/contracts/error_response_contract.md`, `meta/error_taxonomy.md`

---

## 0. 가드레일 정의

> **가드레일은 시스템이 잘못된 방향으로 가는 것을 자동 차단하는 안전장치다.**

사용자 입력 / 처리 흐름 / 출력 모두에 적용된다. 위반 시 block / warn / sanitize 중 하나로 처리.

---

## 1. 가드레일 분류 (3 layer)

```
┌─────────────────────────────────────────────────────┐
│ INPUT     사용자/외부에서 들어오는 데이터          │
│ PROCESS   파이프라인 내부 실행                      │
│ OUTPUT    사용자/외부로 나가는 응답                 │
└─────────────────────────────────────────────────────┘
```

각 layer는 독립적으로 가드레일을 가지며, 위반 시 처리 방식이 다르다.

---

## 2. INPUT 가드레일

### 2.1 Intent Filter (영상기획 외 입력 차단)

```
대상:    모든 사용자 자유 텍스트 입력
규칙:    영상기획 도메인 외 입력 (예: "유튜브 자동 편집해줘") 차단
판정:    intent classifier (P-001 prompt) + keyword 사전
처리:    block + reframe_suggestion 제공 (E-SEC-002)
예외:    명시적 영상기획 키워드 포함 시 통과
```

→ `docs/contracts/llm_security_contract.md`, `ai_system/agents/intent_agent.md`

### 2.2 PII 차단

```
대상:    모든 사용자 입력 (자유 텍스트, 폼 필드)
규칙:    전화번호 / 이메일 / 주민번호 / 카드번호 패턴 감지
패턴:    error_response_contract §9.2 정의
처리:
- 사용자 입력에 PII 감지 시: 자동 마스킹 + E-SEC-006 ("개인정보 제외하고 다시")
- 로그에 PII 감지 시: 자동 마스킹 (절대 raw 저장 금지)
- LLM 호출 직전 마스킹 (LLM이 PII 학습 못하게)
```

### 2.3 Prompt Injection 방어

```
대상:    모든 사용자 텍스트 → LLM 호출 직전
규칙:    다음 패턴 차단:
- "ignore previous instructions"
- "system prompt is" / "your instructions are"
- 다양한 jailbreak 패턴 (정기 갱신)
판정:    keyword 사전 + LLM 1차 분류 (gpt-4o-mini, P-AUX-1)
처리:    block + E-SEC-001 (어떤 패턴이 차단됐는지 사용자에게 노출 금지)
누적:    같은 user_id가 1분 안에 5회 → 자동 1시간 차단
```

→ `docs/contracts/llm_security_contract.md` §4

### 2.4 광고 표현 사전 차단 (사용자 입력 단)

```
대상:    사용자 자유 텍스트 입력
규칙:    "최고의", "혁신적인", "획기적인", "유일한", "압도적인", "완벽한" 등
처리:    warn (block 아님) + "다른 표현으로 다시 입력해주세요" 안내
이유:    사용자가 광고 표현을 input으로 넣으면 LLM이 그대로 반영할 가능성 높음
```

### 2.5 입력 크기 제한

```
- 자유 텍스트: 최대 2000자 (UI 1000자, 서버 2000자 safety)
- 파일 업로드: 최대 5MB (Phase 2+)
- 한 세션당 영상기획 시도: rate_limit_policy 따름
- 한 영상기획 요청당 입력 필드 수: 최대 20개
```

---

## 3. PROCESS 가드레일

### 3.1 revise_round 무한 루프 차단

```
규칙:    Critic agent revise 최대 2회 (max_revise_round=2)
판정:    agent_io_envelope.revise_round 카운트
처리:    revise_round=2 도달 시 즉시 종료 → E-LLM-010 ("AI 개선이 한계에 도달")
이유:    무한 루프 방지 + 비용 통제
```

→ `ai_system/orchestration/moa_policy.md`, `docs/contracts/agent_io_contract.md`

### 3.2 cost 한도 (호출 단위 + 사용자 단위)

```
호출 단위:
- 단일 LLM 호출당 max_tokens 강제 (input 8K / output 4K)
- 호출당 비용 추정 > $0.10 시 자동 차단 (E-LLM-009)
- 비용 추정은 호출 전 input token count 기반

사용자 단위:
- anonymous: 일 $0.50 한도
- free: 월 $5.00 한도
- paid: 월 $30.00 한도 (Phase 12+)
- 한도 도달 시 E-RL-001
- Redis 비용 누적 cache (5분 sync)
```

→ `docs/contracts/rate_limit_policy.md`

### 3.3 timeout (LLM 호출당)

```
- LLM 호출 timeout: 30초 (E-LLM-001)
- RAG 검색 timeout: 5초 (E-RAG-004)
- DB query timeout: 10초 (E-DB-006)
- 전체 영상기획 요청 timeout: 90초 (4단계 합)
- timeout 도달 시 partial_result 반환 (error_response_contract §7)
```

### 3.4 RAG 검색 결과 0건 처리

```
규칙:    rag_chunks 0건 반환 시 warning (block 아님)
처리:    rag_context=[] 그대로 Planning agent 호출
사용자 노출: "참고 자료 없이 만든 결과예요" warning
이유:    RAG 부재 시에도 기본 LLM 지식으로 결과 생성 가능
```

### 3.5 agent_io_envelope 검증

```
규칙:    각 agent 호출 시 input/output envelope이 agent_io_contract 준수
판정:    Pydantic v2 validation
처리:    검증 실패 시 1회 자동 재시도 → 실패 시 E-LLM-003
```

### 3.6 RAG 데이터 격리 (사용자 / Brand 단위)

```
규칙:    한 사용자의 candidate_knowledge는 다른 사용자에게 노출 금지 (승격 전)
판정:    RAG 검색 시 user_id / brand_id 필터링
처리:    위반 시 block + 운영자 알림 (보안 사고)
```

→ `knowledge/rag/promotion_rule.md`, `docs/contracts/rag_data_contract.md`

---

## 4. OUTPUT 가드레일

### 4.1 광고 단어 차단 (LLM 응답)

```
대상:    모든 LLM 응답 (Planning 3 후보, Critic, Rewriter)
규칙:    광고 표현 사전 위반 시:
- 1회: 자동 재시도 (prompt에 광고 표현 금지 강조)
- 2회: 자동 sanitize (해당 단어 제거 또는 대체)
- 3회: E-LLM-006 ("AI가 표현을 다듬는 데 문제가 생겼어요")
사전: docs/contracts/output_schema.md §광고 표현 사전 (정기 갱신)
```

### 4.2 JSON schema 검증

```
대상:    모든 LLM 응답 (구조화 출력)
규칙:    output_schema.md의 schema에 통과해야 함
판정:    Pydantic v2 validation
처리:    1회 재시도 → 실패 시 E-LLM-003
```

→ `docs/contracts/output_schema.md`

### 4.3 응답 길이 제한

```
- 영상기획안 한 후보: 최대 2000자
- Critic 평가 코멘트: 최대 500자
- 사용자 메시지 (error.user_message): 최대 100자 (UI 1줄)
- 초과 시 자동 truncate + warning 로그
```

### 4.4 PII 출력 차단

```
대상:    LLM 응답 + API 응답
규칙:    응답에 PII 패턴 감지 시 자동 마스킹
이유:    LLM이 RAG 데이터의 PII를 실수로 노출 가능성 차단
```

### 4.5 stack trace / 내부 정보 차단

```
- error.user_message에 stack trace 노출 금지
- DB 컬럼명 / SQL 구문 / 내부 host:port 노출 금지
- 위반 시 자동 sanitize + 운영자 알림
```

→ `docs/contracts/error_response_contract.md` §9.4

### 4.6 응답 헤더 보안

```
- X-Content-Type-Options: nosniff
- X-Frame-Options: DENY
- Strict-Transport-Security: max-age=31536000
- Content-Security-Policy: default-src 'self'; ...
- 위반 응답은 게이트웨이에서 차단
```

→ `docs/contracts/api_contract.md` §0

---

## 5. 가드레일 위반 처리 매트릭스

| 위반 종류 | 처리 | 사용자 노출 | 로그 / 알림 |
|---|---|---|---|
| Intent 외 입력 | block | E-SEC-002 + reframe | intent_filter_logs |
| PII 입력 감지 | sanitize + block | E-SEC-006 안내 | 마스킹 후 로그 |
| Prompt injection | block | E-SEC-001 (일반 안내) | 운영자 알림 (#security) |
| 광고 표현 (input) | warn | "다른 표현 추천" | warning 로그 |
| 입력 크기 초과 | block | E-INV-003 | 일반 로그 |
| revise_round 초과 | block | E-LLM-010 + manual_edit | warning 로그 |
| 비용 한도 초과 | block | E-LLM-009 또는 E-RL-001 | cost_snapshots/ |
| LLM timeout | block + partial | E-LLM-001 + retry | warning 로그 |
| 광고 표현 (output) | sanitize → block | E-LLM-006 (3회 후) | warning 로그 |
| Schema 검증 실패 | retry → block | E-LLM-003 | error 로그 |
| 응답 길이 초과 | truncate + warn | (사용자 모름) | warning 로그 |
| 내부 정보 노출 | sanitize | (자동 제거) | 운영자 알림 |

---

## 6. 가드레일 임계 자동 조정 (Phase 11+ 검토)

```
다음 가드레일은 학습 기반 동적 조정 후보:

- Intent Filter 정확도 임계 (현재 keyword + LLM)
- 비용 한도 (사용자별 사용 패턴 기반)
- PII 패턴 (새 패턴 자동 발견)
- 광고 표현 사전 (영상기획 도메인 특화 갱신)

조정 절차:
1. eval/regression_results/ 누적 데이터 분석
2. 임계 조정 제안 → harness_improvement_proposals.md
3. contract-change Skill 통과
4. A/B 테스트 (10% → 50% → 100%)
```

---

## 7. 가드레일 변경 절차

```
1. 신규 가드레일 추가:
   - contract-change Skill 절차
   - 영향 분석 (false positive 가능성)
   - eval/regression 100건 이상 통과 후 적용

2. 임계 조정:
   - 정량 근거 (현재 false positive율 / false negative율)
   - 14일 staging 검증
   - A/B 테스트 (큰 조정만)

3. 가드레일 제거:
   - 매우 신중하게 (보안 영향)
   - multi-llm-validation Skill 필수
   - 사용자 승인 명시
```

---

## 8. 가드레일 위반 누적 추적

```
같은 user_id의 반복 위반 패턴:

5회 / 1분 (보안):
  - Intent 위반, prompt injection
  - → 자동 1시간 차단 + 운영자 알림

10회 / 1일 (광고):
  - 광고 표현 사용자 입력
  - → 경고 메시지 + 가이드 노출

3회 / 1일 (부적절):
  - 부적절 콘텐츠 (E-SEC-004)
  - → 운영자 즉시 알림 + 계정 정지 검토

기록 위치: meta/security_metrics.md (Phase 7+ 누적)
```

→ `docs/contracts/error_response_contract.md` §13, `meta/security_metrics.md`

---

## 9. 가드레일 측정 지표

```
1. false positive율 (정상 입력 차단)
   - 목표: 3% 이하

2. false negative율 (잘못된 입력 통과)
   - 목표: 5% 이하

3. 위반 누적 빈도
   - 사용자당 일평균 위반 횟수
   - 0.5회 이상이면 가이드 강화 필요

4. 가드레일 처리 시간
   - 호출당 추가 latency
   - 목표: 100ms 이하 (INPUT) + 200ms 이하 (OUTPUT)
```

---

## 10. 확장 가능성 (Phase X+ 보강 예정)

```
Phase 5+:  광고 표현 사전 영상기획 도메인 특화 갱신.
Phase 7+:  RAG 데이터 격리 정밀화 (Brand 단위 → Series 단위).
Phase 11+: 가드레일 임계 자동 조정 (학습 기반).
Phase 21+: ML 기반 비정상 입력 감지 (E-SEC-007 보강).
```

---

## 11. Open Questions

1. Intent Filter false positive 3% 임계가 적절한지 — 실 사용자 데이터로 조정.
2. revise_round=2가 너무 짧은지 — paid tier에서 4로 늘릴지 검토.
3. 비용 한도 도달 시 사용자 안내가 paid 추천으로 자연스러운지 — UX 검증.
4. PII 마스킹 후 LLM 호출 시 결과 품질 영향 — 학습 효과 측정.
5. 광고 표현 사전이 너무 엄격해서 사용자가 답답해 하는 사례 — sensitivity 조정.

---

## 12. 변경 이력

```
v1.0.0 (2026-05-26): Phase 0 Sprint S5-1. placeholder 해소 + deep 작성.
                      3 layer (INPUT/PROCESS/OUTPUT) 가드레일, 위반 처리 매트릭스,
                      누적 추적, 측정 지표.
```
