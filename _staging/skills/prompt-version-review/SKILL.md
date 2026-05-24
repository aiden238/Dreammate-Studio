---
name: prompt-version-review
description: |
  ai_system/prompts/prompt_registry.md의 어떤 프롬프트(P-001 등)라도 변경할 때 사용한다.
  semver 버전 부여, golden_set 회귀 평가, A/B 또는 단계적 활성화, 이전 버전
  deactivation 일정을 강제한다. 모델 변경 시에도 트리거.
  키워드: "prompt 변경", "P-XXX 수정", "prompt_registry 업데이트", "semver",
  "prompt rollback", "모델 변경", "prompt new version".
applies_to: [agents, claude]
phase: [phase-4, phase-5, phase-6, phase-9, ongoing]
related_contracts:
  - ai_system/prompts/prompt_registry.md
  - docs/contracts/agent_io_contract.md
  - docs/contracts/output_schema.md
related_state:
  - eval/golden_set.md
  - prompt_registry_log (DB 테이블)
  - agent_io_logs (DB 테이블)
version: v1.0.0
---

# prompt-version-review

프롬프트 변경은 LLM 출력 품질에 직접 영향을 주므로, 항상 버전 관리 + 회귀 평가를 거친다.

## 트리거 조건

- `ai_system/prompts/prompt_registry.md`의 P-XXX 텍스트 변경
- 새 prompt 추가
- prompt의 output schema 변경
- 사용 모델 변경 (gpt-4o-mini → gpt-4o, Claude로 교체 등)
- temperature, max_tokens 같은 호출 파라미터 변경
- 시스템 prompt 공통 규칙 변경

## 절차

### 1. contract-change 절차 우선 통과

prompt_registry.md는 contract이다. 먼저 contract-change Skill로 변경 제안서 작성.

```
대상 contract: ai_system/prompts/prompt_registry.md
영향 받는 영역: Prompt 체크
```

### 2. semver 부여

변경 종류에 따라 새 version을 정한다.

```
patch (v1.0.0 → v1.0.1)
  - 오탈자
  - 예시 추가
  - 설명 명확화
  - 출력 결과에 영향 없음

minor (v1.0.0 → v1.1.0)
  - 새 입력 변수 추가 (선택적)
  - 새 규칙 추가
  - 출력 구조 유지하면서 내부 표현 개선

major (v1.0.0 → v2.0.0)
  - output schema 변경
  - 호환성 깨지는 변경
  - 모델 교체
  - 시스템 prompt 공통 규칙 변경
```

`v0.x.y`는 실험 버전. 운영 진입 시 v1.0.0.

### 3. prompt_registry.md 갱신 (제안 상태)

기존 P-XXX 항목 위에 새 버전 블록 추가. 이전 버전은 일정 기간 함께 보존.

```markdown
## P-006 · plan_candidates

### v1.0.0 (active, deactivate_at: 2025-12-01)
...

### v1.1.0 (proposed → active 후보, 평가 대기)
...
```

### 4. golden_set 회귀 평가

`eval/golden_set.md`의 영향 받는 케이스로 신구 버전 동시 실행.

#### 평가 케이스 선택

```
P-001 ~ P-004 (카드 생성)    : 최소 5케이스 × 5장 카드
P-005 (한 줄 방향)          : 최소 5케이스
P-006 (plan_candidates)     : 최소 8케이스 × 3 plans
P-007 (Critic)              : 최소 10케이스 (기획안에 대한 평가)
P-008 (Rewriter)            : 최소 8케이스
P-AUX-* (보조)              : 최소 3케이스
```

각 케이스를 두 버전(v1.0.0, v1.1.0)에 동일 입력으로 호출하고 결과 비교.

#### 비교 지표

| 지표 | 산출 방법 | 기준 |
|---|---|---|
| schema 준수율 | JSON 파싱 성공 비율 | 100% 필수 |
| Critic 평균 점수 | 8차원 평균 | 신버전이 구버전 ±0.3 이내 |
| 다양성 | 후보 간 cosine similarity | 큰 차이 없어야 함 |
| 응답 시간 | 평균 latency | 신버전이 +20% 이내 |
| 토큰 사용량 | 평균 input+output | 신버전이 +30% 이내 |

#### 사람 검토 (major bump 시 필수)

minor/patch: 자동 지표만 통과하면 OK.
major: 자동 지표 + 사람 검토자가 결과 10개 정성 평가.

### 5. 활성화

회귀 평가 통과 시:

#### patch / minor

```
1. prompt_registry.md에 새 버전 'active' 표시
2. 이전 버전은 'deprecated' 표시 + deactivate_at 날짜 설정 (보통 +14일)
3. prompt_registry_log 테이블에 INSERT
4. 운영 환경의 PROMPT_ACTIVE_VERSION 환경 변수 갱신
5. agent_io_logs는 새 prompt_version으로 분기됨
```

#### major

A/B 단계적 활성화 권장.

```
Phase A (7일): 신버전 10% 트래픽
Phase B (7일): 50% 트래픽
Phase C: 100% 전환, 구버전 deprecated
Phase D (+14일): 구버전 deactivated (호출 차단)
```

A/B 라우팅은 `agent_io_logs.prompt_version` 기준 사후 분석 가능해야 함.

### 6. 모니터링 기간

활성화 후 다음을 모니터링:

```
+24h  : schema 파싱 실패율 (>0.1%이면 즉시 rollback)
+72h  : Critic 평균 점수 추이
+7d   : 사용자 feedback_events (like/dislike/reject 비율)
+14d  : 비용 변화 (cost-review Skill 트리거)
```

기준 초과 시 즉시 rollback (이전 버전 재활성화).

### 7. Rollback

신버전 문제 발견 시:

```
1. PROMPT_ACTIVE_VERSION 즉시 이전 버전으로
2. prompt_registry.md에서 신버전 'rolled_back' 표시
3. agent_io_logs에 rollback 이벤트 기록
4. meta/retrospective/에 사례 기록 (meta-retrospective Skill로 위임)
5. 신버전은 폐기가 아니라 v1.1.1로 수정 후 재평가
```

## 다른 Skill과의 관계

```
contract-change   → 항상 선행 (prompt_registry.md는 contract)
eval-run          → 4단계에서 호출
multi-llm-validation → major bump 시 다른 모델로 교차 검증
cost-review       → 5단계 활성화 후 +14d 자동 트리거
rag-update        → RAG 참고 자료가 prompt에 주입되는 경우 영향 확인
security-review   → 시스템 prompt 공통 규칙 변경 시 필수
```

## 모델 교체 특별 절차

같은 prompt 텍스트라도 모델이 바뀌면 별도 version 부여.

```
P-006 v1.0.0 (gpt-4o-mini) → P-006 v2.0.0 (gpt-4o)
```

이유: 같은 prompt도 모델별로 출력 분포가 다르며 schema 준수율, 비용, latency가 모두 달라진다.

#### 추가 점검

- 토큰화 차이로 인한 max_tokens 재설정
- temperature 등 호환 파라미터 재검증
- output schema 강제 방식 (function calling vs structured output) 호환성

## 자주 발생하는 실수

1. **회귀 평가 생략**: "이 정도 수정은 괜찮겠지" → 항상 통과.
2. **patch와 minor 혼동**: 출력에 영향 있으면 무조건 minor 이상.
3. **이전 버전 즉시 삭제**: deactivate_at까지 함께 운영해야 rollback 가능.
4. **prompt_registry_log 갱신 누락**: agent_io_logs와 join 안 됨 → 추적 불가.
5. **A/B 라우팅 없이 major bump 즉시 100%**: 문제 발견이 늦어짐.
6. **모델 교체를 patch로 처리**: 동일 prompt 다른 모델은 항상 major.

## 산출물

prompt-version-review 1회 실행의 산출물:

```
meta/proposals/ : 변경 제안서 (contract-change 산출물)
ai_system/prompts/prompt_registry.md : 신버전 추가
eval/regression_results/{prompt_id}_{version}.md : 회귀 평가 결과
prompt_registry_log : DB INSERT
PROMPT_ACTIVE_VERSION env 갱신 기록
모니터링 일정 등록 (alert 또는 cron)
```

## 종료 조건

- 신버전 활성화 + 모니터링 등록 완료 → 정상 종료
- 회귀 평가 실패 → 제안서에 사유 기록, prompt 수정 후 재시작
- Rollback → meta-retrospective Skill로 위임 후 종료
