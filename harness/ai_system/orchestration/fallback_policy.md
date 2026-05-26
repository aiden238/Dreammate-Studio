# fallback_policy.md — 폴백 정책

> 위치: `ai_system/orchestration/fallback_policy.md`
> 상태: S4-3 deep
> 참조: `docs/contracts/error_response_contract.md`, `docs/contracts/agent_io_contract.md` §10
> 참조: `ai_system/orchestration/flow.md`, `cost_control_policy.md`

---

## 1. 원칙

- **사용자 데이터 보존**: 어떤 실패에서도 사용자 입력은 잃지 않는다.
- **부분 성공 노출**: 일부라도 성공한 결과는 노출하고 경고 표시.
- **silent fail 금지**: timeout/실패는 항상 명시적 에러 응답.
- **재시도 보수적**: cost가 큰 호출은 재시도 횟수 제한.
- **사용자 안내 친근**: 기술적 에러 코드 노출 금지, 자연어 안내.

---

## 2. Agent별 폴백

### 2.1 Intent Agent

```
P-AUX-1 실패:
  1차: 1회 재시도 (지수 백오프 1s)
  2차: ambiguous로 가정 + 사용자에게 "다시 입력해주세요" 안내
        + 사용자 입력은 화면에 보존

카드 생성 (P-001~P-004) 실패:
  1차: 2회 재시도
  2차: 부분 결과 노출 (4장 중 N장 성공 → user_input_slot 1장 + 성공 N장)
        + warning: "후보 일부만 생성되었어요"

P-005 / P-005q 실패:
  1차: 2회 재시도
  2차: 사용자에게 에러 + "재시도" 버튼 + 누적 selections 보존

prompt injection 감지:
  즉시 block + intent_filter_logs(reason='prompt_injection') 기록
  사용자에게: "입력을 다시 확인해주세요"
  관리자 알림 (security_metrics)
```

기본 가정: Intent가 실패하면 다음 단계로 진행하지 않는다 (planning_request로 임의 분류 금지).

---

### 2.2 Planning Agent

```
P-006 실패:
  1차: 1회 재시도 (지수 백오프 2s) — cost 큰 호출이라 재시도 보수적
  2차: 캐시된 generic 템플릿 plan 1개 노출 (선택 컨텍스트 기반)
        + warning: "AI가 일시적으로 응답하지 못해 기본 템플릿을 제공해요"
  3차: 사용자에게 에러 노출 + "재시도" 버튼

부분 성공 (3 plan 중 N개):
  성공한 N개 노출 + "추가로 생성하기" 버튼

JSON 파싱 실패:
  schema repair 1회 → 실패 시 전체 재시도 1회 → 실패 시 generic 템플릿

RAG 검색 실패:
  rag_context = [] + warning("no_rag_reference") → Planning 진행
  사용자에게 명시 안내 없음 (품질 약간 저하 가능)
```

---

### 2.3 Critic Agent

```
P-007 1개 실패 (3 plan 중):
  1차: 1회 재시도
  2차: 해당 plan에 verdict 없이 노출 + "검토 불가" warning
        나머지 2 plan은 정상 표시

P-007 전체 실패:
  자동 approve 가정 (revise_round 무관)
  + 사용자에게: "AI 검토 실패. 직접 선택해주세요" 안내
  + plan 본문은 정상 노출

revise_round = 2 도달 + 여전히 revise:
  강제 approve (agent_io §5.8)
  validation.warnings = "forced_approve_after_max_revise"
  사용자 안내: "AI 개선이 한계에 도달했어요. 직접 다듬어보시겠어요?"

cost_saving 모드:
  gpt-4o → gpt-4o-mini 자동 폴백 (호출 전)
```

---

### 2.4 Rewriter Agent

```
P-008 실패:
  1차: 1회 재시도
  2차: 원본 plan 유지 + 사용자 안내: "개선 실패. 직접 수정해보세요"

addressed_blocking_issues = []:
  warning: "개선이 미흡합니다" + 사용자 선택 (원본 vs 개선안)

JSON 파싱 실패:
  schema repair 1회 → 실패 시 원본 plan 유지
```

---

### 2.5 Memory Extractor (P-AUX-2)

```
실패:
  사용자에게 노출 안 함 (백그라운드 작업)
  24h 후 재시도 큐에 등록
  3회 누적 실패 시 관리자 알림 (security_metrics)

conflicts_with_existing=true:
  자동 INSERT 안 함, pending queue → 다음 세션 시작 시 사용자 승인 노출
```

---

## 3. 인프라/외부 의존 실패

### 3.1 RAG (pgvector) 실패

```
검색 실패 (DB error):
  Planning은 rag_context=[]로 진행 + warning
  사용자 무관 (품질 약간 저하)
  RAG 가용성 모니터링 (security_metrics)
```

### 3.2 DB 저장 실패

```
plan_options INSERT 실패:
  사용자 입력 + plan 결과는 frontend localStorage 백업
  사용자에게: "저장 중 오류. 다시 시도해주세요"
  재시도 버튼 (idempotent)

agent_io_logs INSERT 실패:
  로그 실패는 사용자 응답에 영향 주지 않음
  외부 fallback (CloudWatch 등) 큐에 적재
```

### 3.3 LLM API 외부 장애

```
OpenAI 5xx:
  최대 2회 재시도 (지수 백오프 1s → 2s → 4s)
  실패 시 사용자에게 에러 + "잠시 후 재시도" 안내

OpenAI rate limit 429:
  exponential backoff 3회 → 실패 시 cost_saving 모드 자동 전환
```

---

## 4. 사용자 메시지 톤

기본 톤: **친근체 + 기술 용어 회피**.

| 상황 | 사용자 메시지 예시 |
|---|---|
| Intent 실패 | "이해하지 못했어요. 다시 한 번 말씀해 주실래요?" |
| Planning 실패 | "기획안 만들기에 잠시 어려움이 있었어요. 다시 시도해주세요." |
| Critic 실패 | "AI 검토를 마치지 못했어요. 직접 선택해보세요." |
| revise 한계 | "AI 개선이 한계에 도달했어요. 직접 다듬어보시겠어요?" |
| 비용 한도 | "오늘 사용량 한도에 도달했어요. 내일 다시 만나요." |
| RAG 0건 | (사용자 무관, warning만 내부 기록) |

---

## 5. 의존성

- `docs/contracts/error_response_contract.md` (에러 코드 매핑)
- `docs/contracts/agent_io_contract.md` §10 (재시도/폴백)
- `ai_system/orchestration/flow.md` (단계별 위치)
- `ai_system/orchestration/cost_control_policy.md` (cost 한도 시 처리)
- `meta/security_metrics.md` (모니터링)

---

## 6. Open Questions

1. Planning generic 템플릿 제공의 품질 임계(현재 미정) — 너무 단순하면 오히려 사용자 실망 우려.
2. Critic 전체 실패 시 자동 approve가 적절한지(현재 적용) — UX 검증 필요.
3. revise_round 한계 도달 시 plan 폐기 vs 강제 approve 후 사용자 선택(현재 후자).
4. Memory Extractor 3회 누적 실패 알림 채널(현재 미정).
5. OpenAI rate limit 429 발생 시 cost_saving 자동 전환의 사용자 안내 여부(현재 무음).
