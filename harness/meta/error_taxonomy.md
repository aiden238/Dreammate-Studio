# error_taxonomy.md — 에러 분류 (메타 관점)

> 위치: `meta/error_taxonomy.md`
> 상태: Phase 0 Sprint S5 deep 작성 (placeholder 해소)
> 참조: `docs/contracts/error_response_contract.md` §4 (7 카테고리 사전)
> 참조: `eval/failure_taxonomy.md` (실패 분류는 eval), `meta/patterns.md`

---

## 0. 에러 분류 vs 실패 분류

본 문서와 `eval/failure_taxonomy.md`는 분리된 영역.

```
meta/error_taxonomy.md (이 문서):
- 시스템 에러의 카테고리 / 빈도 / 회복 가능성
- 패턴 추출 (시간 누적)
- 메타 개선 (개선 제안의 시드)

eval/failure_taxonomy.md:
- AI 출력 실패 (회귀 평가 관점)
- 영상기획안 품질 실패 분류
- 평가 자동화 시드
```

---

## 1. 7 카테고리 (error_response_contract §2 정합)

```
INV   input_validation    사용자/클라이언트 입력 검증 실패
LLM   llm_failure         LLM API 호출 실패 (timeout, parse, validation)
RAG   rag_failure         RAG 검색 실패 (pgvector, 인덱스, 임베딩)
DB    db_failure          Supabase/PostgreSQL 호출 실패
RL    rate_limit          속도/비용 제한 도달
SEC   security_block      prompt injection, 부적절 입력, 정책 위반
UNK   unknown             분류 안 된 5xx 에러
```

각 카테고리별 상세는 `docs/contracts/error_response_contract.md` §4.

---

## 2. 카테고리별 메타 분석

### 2.1 INV (input_validation)

```
주요 코드: E-INV-001 (필수 필드 누락), E-INV-006 (4계층 참조 무결성)

빈도 (예상):
- Phase 1~3 (UI 안정화 중): 높음 (사용자 학습 중)
- Phase 5+ (안정화 후): 낮음 (5% 이하)

심각도: 낮음 (사용자 입력 단의 즉시 안내 가능)

회복 가능성: 높음 (사용자가 다시 입력)

패턴 추출 시그널:
- 같은 코드가 동일 사용자에게 30% 이상 = UI 가이드 부족
- 같은 코드가 다수 사용자에게 = 폼 validation 강화 필요
```

### 2.2 LLM (llm_failure)

```
주요 코드: E-LLM-002 (JSON parse 실패), E-LLM-003 (schema validation),
          E-LLM-010 (revise 무한 루프), E-LLM-006 (광고 표현)

빈도 (예상):
- E-LLM-002: 1% 이내 (gpt-4o-mini 기준)
- E-LLM-003: 1~3% (output_schema 엄격성 따라)
- E-LLM-010: revise 도달 빈도의 5% (대부분 1회 안에 만족)

심각도: 중간 (사용자 체감 큼, 결과 못 받음)

회복 가능성: 중간 (재시도 가능, 단 prompt 수정 필요한 경우 forward fix)

패턴 추출 시그널:
- 특정 prompt에서 5% 이상 발생 = prompt 변경 후보
- E-LLM-006이 늘면 LLM 모델 변경 / 광고 사전 강화
- E-LLM-010이 늘면 Critic prompt 또는 revise_round 임계 재검토
```

### 2.3 RAG (rag_failure)

```
주요 코드: E-RAG-001 (pgvector 검색), E-RAG-003 (0건 반환)

빈도 (예상):
- E-RAG-001: 0.5% 이내 (인프라 안정성)
- E-RAG-003 (warning): 10~20% (콜드스타트 사용자에서 자주)

심각도: 낮음~중간 (rag_context=[] fallback 가능)

회복 가능성: 높음 (fallback)

패턴 추출 시그널:
- E-RAG-003이 30% 이상 = RAG 시드 데이터 부족
- E-RAG-001이 1% 이상 = pgvector 인프라 검토
```

### 2.4 DB (db_failure)

```
주요 코드: E-DB-001 (연결 실패), E-DB-002 (제약 위반), E-DB-005 (RLS 거부)

빈도 (예상):
- E-DB-001: 0.1% 이내 (Supabase managed 인프라)
- E-DB-002: 1~3% (사용자가 같은 이름 시도)
- E-DB-005: 0% (정상 동작 시) — 0이 아니면 보안 사고 의심

심각도: 중간~높음 (데이터 저장 못함)

회복 가능성: 자동 재시도 1회 + 사용자 안내

패턴 추출 시그널:
- E-DB-001이 0.5% 이상 = Supabase 또는 connection pool 검토
- E-DB-005가 발생 = 즉시 보안 인시던트
```

### 2.5 RL (rate_limit)

```
주요 코드: E-RL-001 (일일 비용), E-RL-002 (분당 요청), E-RL-005 (영상 수)

빈도 (예상):
- E-RL-005: 무료 사용자의 5~10% (정상)
- E-RL-002: 0.5% 이내 (자동화 도구 의심)

심각도: 낮음 (정상 동작)

회복 가능성: 시간 경과 시 자동 회복

패턴 추출 시그널:
- 정상 동작이라 패턴 추출 우선순위 낮음
- 단 E-RL-002 + E-RL-004가 동시 = DDoS / 자동화 공격 의심
```

### 2.6 SEC (security_block)

```
주요 코드: E-SEC-001 (injection), E-SEC-002 (intent 외), E-SEC-006 (PII)

빈도 (예상):
- E-SEC-002: 5~10% (영상기획 외 입력 자연 발생)
- E-SEC-001: 0.5% 이내 (드물지만 발생)
- E-SEC-006: 1~3% (PII 자동 마스킹 후 통과)

심각도: 높음 (보안 영향)

회복 가능성: 사용자 행동 변경 필요

패턴 추출 시그널:
- E-SEC-001 누적 5회 / 1분 / 1 user = 자동 1시간 차단
- E-SEC-004 (부적절 콘텐츠) 발생 = 즉시 운영자 알림
- 모든 SEC 패턴은 회피 학습 방지 위해 사용자에게 상세 노출 금지
```

### 2.7 UNK (unknown)

```
주요 코드: E-UNK-001 (분류 안 된 5xx), E-UNK-999 (catch-all)

빈도 (예상):
- 0.1% 이내 (정상 동작 시)
- 0.5% 이상이면 분류 강화 필요

심각도: 높음 (예측 불가)

회복 가능성: 낮음 (분류 안 됨)

패턴 추출 시그널:
- UNK 발생 시 즉시 운영자 알림
- 누적 5건 시 새 카테고리 추가 검토 (contract-change Skill)
- 동일 stack trace 패턴 = 코드 버그 후보
```

---

## 3. 카테고리별 우선순위 (메타 관점)

```
우선순위 1 (즉시 대응):
- SEC: 보안 사고
- UNK: 예측 불가
- DB (E-DB-005): RLS 우회

우선순위 2 (24시간 대응):
- LLM (5% 이상): 품질 영향
- DB (E-DB-001 0.5% 이상): 인프라
- RAG (E-RAG-001 1% 이상): RAG 인프라

우선순위 3 (주간 모니터링):
- INV: 사용자 가이드
- RL: 정상 동작 (단 패턴 변화 모니터링)
- LLM (E-LLM-010): revise 한계 도달 빈도

우선순위 4 (장기 분석):
- 카테고리 간 상관관계
- 사용자 세그먼트별 분포
```

---

## 4. 패턴 추출 (meta/patterns.md 연동)

본 분류에서 추출되는 패턴은 `meta/patterns.md`에 누적된다.

```
패턴 추출 기준:
1. 같은 코드가 30일 내 100건 이상 = 패턴 등록
2. 같은 코드가 단일 user_id에서 5회 이상 = 사용자 가이드 검토
3. 같은 카테고리 누적 빈도가 평소 3배 = 인프라 / prompt 검토
4. 새 코드 (UNK) 5건 이상 = 새 카테고리 추가 검토

추출 절차:
1. 매주 agent_io_logs / errors.log 통계 (자동)
2. 임계 도달 시 meta/patterns.md 신규 항목
3. meta-retrospective Skill 호출 (제안 생성)
4. harness_improvement_proposals.md 신규 항목
```

→ `meta/self_improvement_loop.md` 5단계 루프와 정합

---

## 5. failure_taxonomy.md와의 관계

```
실패 분류 (eval/failure_taxonomy.md):
- AI 출력의 품질 실패 (회귀 평가 관점)
- 예: "영상기획안이 너무 일반적", "Brand 톤 불일치", "hook 약함"
- 평가 자동화의 시드

에러 분류 (meta/error_taxonomy.md):
- 시스템 에러 (운영 관점)
- 예: "LLM API timeout", "DB 연결 실패", "PII 감지"
- 운영 / 인프라 / 보안 시그널
```

연동 케이스:

```
- LLM 응답이 schema 검증 통과했지만 품질이 낮음 = failure_taxonomy 영역
- LLM 응답이 schema 검증 실패 (E-LLM-003) = error_taxonomy 영역
- 두 분류는 동시에 발생 가능 (예: schema 통과 + 품질 낮음 + revise 한계)
```

---

## 6. 카테고리 추가 / 제거 절차

```
새 카테고리 추가:
1. contract-change Skill (error_response_contract §2 갱신)
2. 영향 분석 (api_contract 응답 형식, frontend 처리 로직)
3. 신규 에러 코드 사전 정의
4. UX 단의 user_message + user_action 정의
5. multi-llm-validation 권장

카테고리 제거:
- 거의 발생하지 않음 (한 번 정의된 카테고리는 영구 유지)
- 단 7 카테고리는 향후 8 / 9로 확장 가능
- 제거 절차: 매우 신중 (back-compat 영향)
```

---

## 7. 메트릭 / 알림

```
실시간 모니터링 (Sentry + 자체 dashboard):
- 카테고리별 5분 평균 빈도
- 평소 3배 도달 시 자동 알림 (Slack)

일일 통계:
- 카테고리별 발생 횟수 + 비율
- 새 코드 (UNK) 발생 여부
- 누적 패턴 (meta/patterns.md 자동 갱신)

주간 보고:
- 카테고리별 추세 (4주 비교)
- 사용자 세그먼트별 분포
- 인프라 / prompt 영향 분석
```

→ `docs/contracts/error_response_contract.md` §10 운영자 알림 임계 정합

---

## 8. 카테고리 → Skill 매핑

```
INV 패턴 발견 → design-review Skill (UI 가이드 강화)
LLM 패턴 발견 → prompt-version-review Skill (prompt 변경 검토)
RAG 패턴 발견 → rag-design Skill (RAG 구조 검토) 또는 rag-update Skill (시드 추가)
DB 패턴 발견 → bug-triage Skill (인프라 조사)
RL 패턴 발견 → cost-review Skill (비용 분석)
SEC 패턴 발견 → security-review Skill (보안 강화)
UNK 패턴 발견 → harness-audit Skill (구조 점검)
```

---

## 9. 카테고리별 측정 지표

```
1. 카테고리별 발생 빈도 (월간)
   - 목표: 정상 운영 시 모든 카테고리 합계 < 5% (요청 수 대비)

2. 회복 시간 (카테고리별 평균)
   - INV / RL: 즉시 (사용자 액션)
   - LLM / RAG / DB: < 60초 (자동 재시도)
   - SEC: 즉시 (block 자체가 처리)
   - UNK: < 24시간 (운영자 분석)

3. UNK → 분류된 카테고리 변환률
   - 새 UNK 발생 시 30일 내 80% 이상 분류

4. 사용자 영향
   - 카테고리별 영향 사용자 수 / 전체 사용자
   - 광고 표현 / PII 사고: 0이 목표
```

---

## 10. 확장 가능성 (Phase X+ 보강 예정)

```
Phase 5+:  카테고리별 실 데이터 갱신 (현재는 추정).
Phase 7+:  새 카테고리 검토 (예: COLLABORATION 협업 에러).
Phase 11+: ML 기반 카테고리 자동 분류 (UNK → 분류).
Phase 21+: 다국어 시 카테고리 자체는 유지, user_message만 변경.
```

---

## 11. Open Questions

1. 7 카테고리가 충분한지 / 8~10으로 확장 필요한지 — 실 데이터로 결정.
2. UNK 카테고리의 자동 분류 도입 시점 (Phase 11+ vs 더 일찍).
3. SEC 카테고리 안의 sub-classification (injection / intent / PII / 부적절) 분리 필요성.
4. failure_taxonomy와의 통합 가능성 — 현재 분리가 옳은지.
5. 카테고리별 우선순위가 정적인지 / 시기별 동적 조정 필요한지.

---

## 12. 변경 이력

```
v1.0.0 (2026-05-26): Phase 0 Sprint S5-1. placeholder 해소 + deep 작성.
                      7 카테고리 깊이 확장 + 빈도 / 심각도 / 회복 가능성,
                      패턴 추출 시그널, failure_taxonomy 관계, Skill 매핑.
```
