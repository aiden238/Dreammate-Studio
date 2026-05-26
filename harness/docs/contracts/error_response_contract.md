# error_response_contract.md — 영상기획 AI 에이전트 에러 응답 표준

> 위치: `docs/contracts/error_response_contract.md`
> 상태: Phase 0–1 진입용 핵심 contract 초안
> 참조: `docs/contracts/api_contract.md` (HTTP 응답 envelope)
> 참조: `docs/contracts/output_schema.md` §15 (검증 실패 처리)
> 참조: `docs/contracts/agent_io_contract.md` §10 (재시도/폴백)
> 참조: `apps/web/design.md` §20 (Error UX 원칙), §22 (4단계 progress stepper)

---

## 0. 이 문서의 위치

플랫폼 전체에서 발생할 수 있는 에러를 **분류 / 코드화 / 사용자 노출 규칙 / 로깅 정책**으로 표준화한다. 프론트엔드는 이 문서의 응답 형식만 가정하고 처리할 수 있다.

이 문서가 정의하는 대상:

1. 에러 카테고리 7종 + 코드 체계
2. 에러 응답 표준 envelope
3. 사용자 메시지 (한국어, friendly tone)
4. 회복 정책 (재시도/폴백/사용자 액션)
5. 로깅 + PII 마스킹 정책
6. 4단계 progress stepper 중 에러 발생 시 부분 결과 노출
7. 운영자 알림 임계

---

## 1. 설계 원칙

```
1. 모든 API 응답은 ok=true/false 이분법. ok=false면 반드시 error 객체 존재.
2. 에러 메시지는 기술 메시지(log용)와 사용자 메시지(UX용)를 분리한다.
3. 사용자 메시지는 항상 한국어 친근체. 광고적 표현 / 영어 기술 용어 금지.
4. 모든 에러는 카테고리 + 코드를 가진다. 코드 체계는 E-{CATEGORY}-{NNN} 형식.
5. 부분 결과(partial_result)가 있으면 절대 버리지 않고 응답에 포함.
6. retryable=true면 retry_after(초) 명시. false면 사용자 액션 안내 필수.
7. request_id를 모든 에러에 부착. 사용자가 문의 시 즉시 추적 가능.
8. PII는 server-side 로그에서도 마스킹 (전화번호, 이메일, 주민번호 패턴).
9. 운영자 알림은 카테고리별 임계 도달 시 자동 (예: llm_failure 5%/15min).
```

---

## 2. 에러 카테고리

7개 카테고리로 모든 에러를 분류. 새 카테고리 추가는 contract-change Skill 절차.

```
input_validation   사용자/클라이언트 입력 검증 실패
llm_failure        LLM API 호출 실패 (timeout, parse, validation)
rag_failure        RAG 검색 실패 (pgvector, 인덱스, 임베딩)
db_failure         Supabase/PostgreSQL 호출 실패
rate_limit         속도/비용 제한 도달
security_block     prompt injection, 부적절 입력, 정책 위반
unknown            분류 안 된 5xx 에러
```

각 카테고리의 코드 prefix:

```
INV   input_validation
LLM   llm_failure
RAG   rag_failure
DB    db_failure
RL    rate_limit
SEC   security_block
UNK   unknown
```

---

## 3. 표준 응답 형식

### 3.1 Envelope

```json
{
  "ok": false,
  "error": {
    "code": "E-LLM-002",
    "category": "llm_failure",
    "message": "LLM JSON parse failed after 2 retries",
    "user_message": "AI 응답을 다듬는 중 문제가 생겼어요. 잠시 후 다시 시도해주세요.",
    "user_action": "retry | reframe_input | wait | contact_support | go_back",
    "retryable": true,
    "retry_after": 5,
    "request_id": "8a3b...",
    "trace_id": "abc-123",
    "occurred_at": "2026-05-26T08:30:15Z",
    "context": {
      "agent": "planner",
      "prompt_id": "P-006",
      "prompt_version": "v1.0.0"
    }
  },
  "partial_result": {
    "stage": "planner",
    "completed_steps": ["intent", "rag"],
    "data": {}
  }
}
```

### 3.2 필드 정의

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `ok` | boolean | yes | 항상 false (에러 응답). |
| `error.code` | string | yes | `E-LLM-002` 같은 식별자. §4에서 정의. |
| `error.category` | string | yes | §2의 7개 카테고리 중 하나. |
| `error.message` | string | yes | 영어 기술 메시지. 로그/디버깅용. |
| `error.user_message` | string | yes | 한국어 친근체. UI 노출용. |
| `error.user_action` | string | yes | UI 단에서 표시할 액션 키. §6 참조. |
| `error.retryable` | boolean | yes | 자동/수동 재시도 가능 여부. |
| `error.retry_after` | int (sec) | no | retryable=true일 때만. 0=즉시. |
| `error.request_id` | uuid | yes | 추적 키. agent_io_logs와 매핑. |
| `error.trace_id` | string | no | 분산 추적 (server↔LLM 호출 chain). |
| `error.occurred_at` | ISO8601 | yes | 발생 시각 (UTC). |
| `error.context` | object | no | agent/prompt/db 등 추가 정보. |
| `partial_result` | object | no | 진행 중이던 부분 결과. §7 참조. |

---

## 4. 에러 코드 사전

### 4.1 input_validation (E-INV-*)

```
E-INV-001  필수 필드 누락 (request body 검증)
E-INV-002  필드 타입 불일치
E-INV-003  필드 길이 초과/부족
E-INV-004  enum 외 값
E-INV-005  중복 키 (예: 동일 brand_name)
E-INV-006  4계층 참조 무결성 위반 (예: 존재하지 않는 brand_id)
E-INV-007  user_id 권한 없음 (RLS 우회 시도)
E-INV-008  JSON 파싱 실패 (client → server)
E-INV-009  파일 업로드 형식/크기 위반 (Phase 2+)
```

### 4.2 llm_failure (E-LLM-*)

```
E-LLM-001  LLM API timeout
E-LLM-002  LLM 응답 JSON parse 실패 (2회 재시도 후)
E-LLM-003  LLM 응답이 output_schema validation 실패 (2회 재시도 후)
E-LLM-004  LLM API 5xx 에러
E-LLM-005  LLM API 4xx 에러 (요청 형식 문제)
E-LLM-006  LLM 응답에 광고적 표현 사전 위반 (재시도 후에도)
E-LLM-007  LLM 응답이 비어있음
E-LLM-008  LLM API 응답 너무 김 (max_tokens 초과)
E-LLM-009  LLM 비용 한도 초과 (호출 단위)
E-LLM-010  Critic revise 무한 루프 (revise_round=2 초과)
```

### 4.3 rag_failure (E-RAG-*)

```
E-RAG-001  pgvector 검색 실패 (인덱스 오류)
E-RAG-002  임베딩 생성 실패 (OpenAI embedding API 등)
E-RAG-003  rag_chunks 0건 (검색 결과 없음) — 사실 retryable이 아니라 warning
E-RAG-004  RAG DB 연결 timeout
E-RAG-005  candidate_knowledge 승격 흐름 실패
```

### 4.4 db_failure (E-DB-*)

```
E-DB-001  Supabase 연결 실패
E-DB-002  SQL 제약 위반 (unique, fk)
E-DB-003  트랜잭션 충돌 (concurrent update)
E-DB-004  스토리지 한도 초과
E-DB-005  RLS policy 거부
E-DB-006  query timeout (10s 이상)
```

### 4.5 rate_limit (E-RL-*)

```
E-RL-001  사용자 일일 비용 한도 초과
E-RL-002  사용자 분당 요청 수 한도 초과
E-RL-003  세션당 LLM 호출 횟수 초과
E-RL-004  IP 기준 분당 요청 수 초과 (DDoS 방어)
E-RL-005  무료 사용자 일일 영상 생성 횟수 초과
```

### 4.6 security_block (E-SEC-*)

```
E-SEC-001  prompt injection 시도 감지
E-SEC-002  영상기획 외 입력 (intent_filter block)
E-SEC-003  광고적 과장 표현 사전 위반 (사용자 입력 단)
E-SEC-004  부적절 콘텐츠 (욕설/혐오/성/폭력 카테고리)
E-SEC-005  XSS 시도 (HTML/JS 인젝션)
E-SEC-006  PII 노출 시도 (전화번호/주민번호 등을 LLM에 보내려 함)
E-SEC-007  계정 도용 의심 (비정상 사용 패턴)
```

### 4.7 unknown (E-UNK-*)

```
E-UNK-001  분류되지 않은 server error
E-UNK-002  외부 서비스 (이메일, 알림 등) 실패
E-UNK-999  fallback 에러 (catch-all)
```

---

## 5. 사용자 메시지 (한국어, friendly tone)

### 5.1 작성 원칙

```
1. "오류가 발생했습니다" 같은 메시지 금지. 항상 무엇을/왜/어떻게의 흐름.
2. 한국어 친근체 (~예요, ~해주세요). 존댓말 유지.
3. 광고적 과장 표현 금지 ("최고의 솔루션", "혁신적인 시스템" 등 일체 금지).
4. 영어 기술 용어 금지 (timeout → "응답이 늦어졌어요", parse → "정리하는 중").
5. 다음 행동을 항상 제시. 사용자가 멍하니 화면을 보게 두지 않는다.
6. 50자 이내. 모바일 1줄 표시 우선.
7. 부분 결과가 있으면 메시지에 명시 ("일부 결과는 확인하실 수 있어요").
```

### 5.2 카테고리별 표준 user_message

```
E-INV-001  "필수 정보가 빠졌어요. 다시 확인해주세요."
E-INV-006  "이전에 만든 데이터를 못 찾았어요. 페이지를 새로고침해주세요."
E-INV-007  "권한이 없는 항목이에요. 로그인 상태를 확인해주세요."

E-LLM-001  "AI 응답이 늦어져서 멈췄어요. 다시 시도해주세요."
E-LLM-002  "AI 응답을 정리하는 중 문제가 생겼어요. 다시 시도해주세요."
E-LLM-003  "AI가 형식에 맞지 않게 답했어요. 다시 시도해주세요."
E-LLM-004  "AI 서버가 잠시 불안정해요. 1분 후 다시 시도해주세요."
E-LLM-006  "AI가 표현을 다듬는 데 문제가 생겼어요. 다시 시도해주세요."
E-LLM-009  "오늘 AI 사용량 한도에 도달했어요. 내일 다시 만나요."
E-LLM-010  "AI 개선이 한계에 도달했어요. 직접 다듬어보시겠어요?"

E-RAG-001  "참고 자료를 못 가져왔어요. 자료 없이 진행할까요?"
E-RAG-003  (warning 처리, 에러 아님) → "참고 자료 없이 만든 결과예요."

E-DB-001   "데이터를 저장하는 중 문제가 생겼어요. 잠시 후 다시 시도해주세요."
E-DB-002   "이미 같은 이름이 있어요. 다른 이름으로 만들어주세요."

E-RL-001   "오늘 사용량 한도에 도달했어요. 내일 다시 만나요."
E-RL-002   "너무 빠르게 요청하셨어요. 잠시 기다려주세요."
E-RL-005   "오늘 만들 수 있는 영상 수에 도달했어요."

E-SEC-001  "입력에 사용할 수 없는 표현이 있어요. 다시 입력해주세요."
E-SEC-002  "영상기획과 거리가 있는 내용 같아요. 다른 방식으로 도와드릴까요?"
E-SEC-004  "이 내용은 도와드리기 어려워요. 다른 주제로 시도해주세요."
E-SEC-006  "개인정보가 포함된 것 같아요. 입력에서 제외하고 다시 시도해주세요."

E-UNK-001  "잠시 문제가 생겼어요. 다시 시도하거나 처음으로 돌아가주세요."
E-UNK-999  "예상치 못한 문제가 생겼어요. 새로고침해주세요."
```

---

## 6. user_action 키 사전

UI 단에서 액션 버튼 라벨/동작에 매핑.

```
retry              "다시 시도" 버튼. retryable=true에서만.
reframe_input      "다시 입력하기" 버튼. 입력 폼으로 돌아감.
wait               버튼 없음. retry_after 카운트다운만 표시.
contact_support    "문의하기" 버튼. request_id 미리 채워서 폼 열기.
go_back            "처음으로" 버튼. 현재 진행 폐기.
continue_partial   "부분 결과로 진행" 버튼. partial_result 사용.
skip_rag           "참고 자료 없이 진행" 버튼. RAG 실패 시.
manual_edit        "직접 다듬기" 버튼. revise 한계 도달 시.
```

UI 단에서는 동시에 최대 2개 액션 노출. 우선순위:

```
1순위: retry (retryable=true이고 retry_after≤30s)
2순위: continue_partial (partial_result 있음)
3순위: reframe_input / manual_edit
4순위: go_back / contact_support
```

---

## 7. 4단계 progress stepper 중 에러 처리

`apps/web/design.md` §22 `GenerationProgressStepper`의 4단계:

```
[1] Intent  →  [2] RAG  →  [3] Plan  →  [4] Critic
```

각 단계에서 에러 발생 시 부분 결과 노출 정책.

### 7.1 [1] Intent 실패

```
partial_result.stage = "intent"
partial_result.completed_steps = []
partial_result.data = { /* 사용자가 직전에 선택한 카드들 */ }

UX:
- 입력 폼으로 돌아감 + 이전 선택은 그대로 유지.
- user_action: "reframe_input"
```

### 7.2 [2] RAG 실패

```
partial_result.stage = "rag"
partial_result.completed_steps = ["intent"]
partial_result.data = {
  "approved_direction": "...",
  "selected_context": { ... }
}

UX:
- "참고 자료를 못 가져왔어요. 자료 없이 진행할까요?" + "참고 자료 없이 진행" 버튼.
- user_action: "skip_rag" (자동으로 Planner를 rag_context=[]로 호출)
- 동시 user_action: "retry"
```

### 7.3 [3] Planner 실패

```
case A: 0개 plan 성공
  partial_result.stage = "planner"
  partial_result.completed_steps = ["intent", "rag"]
  partial_result.data = { plans: [] }
  user_action: "retry"

case B: 1~2개 plan 성공
  partial_result.stage = "planner_partial"
  partial_result.completed_steps = ["intent", "rag"]
  partial_result.data = { plans: [/* 성공한 plan만 */] }
  user_action: "continue_partial" (부분 결과 사용 + Critic은 성공한 plan에만 실행)
  동시 user_action: "retry" (3개 다시 생성)
```

### 7.4 [4] Critic 실패

```
case A: 3개 plan 모두 Critic 실패
  partial_result.stage = "critic"
  partial_result.completed_steps = ["intent", "rag", "planner"]
  partial_result.data = { plans: [...], scores: [] }
  UX: plan은 노출하되 점수 없이. "AI 검토가 실패해서 직접 골라주세요."
  user_action: "continue_partial"

case B: 일부만 실패
  partial_result.data = { plans: [...], scores: [/* 성공한 것만 */] }
  UX: 성공한 plan에는 점수 노출, 실패한 plan에는 "검토 불가" 배지.
  user_action: "continue_partial" + "retry"
```

### 7.5 stepper UX 표시

```
[1 Intent ✓]  [2 RAG ✗]  [3 Plan -]  [4 Critic -]
                ↑
                ⚠ 에러 + 사용자 액션 카드 노출
```

실패한 단계는 ✗ 표시, 진행되지 못한 단계는 회색 `-` 표시. 사용자가 retry/skip 후 stepper 갱신.

---

## 8. 회복 정책 (server-side)

### 8.1 자동 재시도

```
- 모든 LLM 호출: 지수 백오프 1s → 2s → 4s, 최대 2회 (→ agent_io_contract.md §10)
- DB 쓰기 충돌 (E-DB-003): 즉시 1회 재시도
- 임베딩 API timeout (E-RAG-002): 1회 재시도
```

### 8.2 폴백

```
Critic 실패 (E-LLM-001~005)
  → 자동 mini 모델 폴백 (cost_saving) → 그래도 실패면 사용자 노출.

RAG 실패 (E-RAG-001, E-RAG-004)
  → rag_context=[]로 Planner 계속 진행 + warning. 사용자에게 "자료 없이 진행했어요" 표시.

LLM 비용 한도 (E-LLM-009, E-RL-001)
  → 자동 폴백 없음. 사용자에게 즉시 안내.

DB 일시 장애 (E-DB-001)
  → 최대 30s 재시도 큐 → 회복 시 자동 INSERT. 사용자에겐 "저장 중" UI.
```

→ 자세한 폴백 절차는 `ai_system/orchestration/fallback_policy.md` 참조.

### 8.3 사용자 액션 필요

```
- 모든 input_validation 에러
- 모든 security_block 에러
- E-LLM-010 (revise 한계)
- 모든 rate_limit 에러
- E-RAG-003 (검색 결과 0) — warning이지만 사용자 선택지 제공
```

---

## 9. 로깅 정책

### 9.1 로깅 대상

```
모든 에러는 logs/api/errors.log 또는 동등한 구조화 로그에 기록.

기록 필드:
- timestamp (UTC)
- request_id, trace_id
- user_id (마스킹: 앞 4자만)
- error.code, category
- error.message (raw, 마스킹 후)
- stack trace (server 내부 에러만)
- agent / prompt_id / prompt_version (LLM 에러일 때)
- input_payload (마스킹 후)
```

### 9.2 PII 마스킹

```
다음 패턴은 모든 로그에서 자동 마스킹:
- 전화번호: \d{2,3}-\d{3,4}-\d{4} → 010-****-****
- 이메일: \S+@\S+\.\S+ → u***@***.com (앞 1자만 + 도메인 마스킹)
- 주민번호: \d{6}-\d{7} → ******-*******
- 카드번호: \d{4}-\d{4}-\d{4}-\d{4} → ****-****-****-****
- IP주소 (v4/v6): 마지막 옥텟 마스킹 (예: 192.168.1.* )

user_input 텍스트에 위 패턴이 발견되면 LLM 호출 직전에 마스킹 + E-SEC-006 발생.
```

### 9.3 보관 기간

```
errors.log:             1년 (raw text 90일 → 그 이후 통계만)
agent_io_logs:          1년 (raw_payload 90일 → 비식별화)
intent_filter_logs:     1년
audit_log (보안 관련):  3년
```

→ 자세한 보존 정책은 `docs/contracts/data_retention_policy.md` 참조.

### 9.4 외부 노출 금지

```
사용자에게 보내는 응답에는 stack trace, 내부 host/port, DB 컬럼명, SQL 구문 일체 금지.
이런 정보는 error.message에도 포함 금지 (로그에만).
```

---

## 10. 운영자 알림 임계

```
카테고리        임계                          알림 채널
llm_failure     5% / 15분                     Slack #ops-alert
db_failure      1건 / 즉시                    Slack #ops-alert + PagerDuty
rag_failure     10% / 15분                    Slack #ops-alert
security_block  10건 / 1분 (동일 user_id)     Slack #security
rate_limit      해당 없음 (정상 동작)         —
unknown         1건 / 즉시                    Slack #ops-alert
input_validation 30% / 15분 (이상 패턴)       Slack #ops-alert (낮은 우선순위)
```

알림 본문에 request_id를 포함해서 즉시 추적 가능하게.

---

## 11. 클라이언트 처리 규칙

### 11.1 응답 받기

```typescript
// 의사 코드
const res = await fetch('/api/...');
const json = await res.json();

if (!json.ok) {
  showError({
    title: getCategoryTitle(json.error.category),
    message: json.error.user_message,
    actions: getActions(json.error.user_action),
    retryAfter: json.error.retry_after,
    requestId: json.error.request_id
  });

  if (json.partial_result) {
    preservePartialResult(json.partial_result);
  }
  return;
}
```

### 11.2 절대 금지

```
- json.error.message (영어 기술 메시지)를 사용자에게 그대로 노출 금지.
- response.status (HTTP 코드)만으로 사용자 메시지 결정 금지. 항상 error.code 사용.
- partial_result를 무시하고 화면을 클리어 금지.
```

### 11.3 retry_after 처리

```
retryable=true AND retry_after > 0:
  → 버튼에 카운트다운 ("5초 후 다시 시도")
  → 카운트 끝나면 자동 재시도 (사용자가 다른 액션 안 했을 때만)
retryable=false:
  → retry 버튼 비활성. wait/manual/reframe 액션만 표시.
```

---

## 12. HTTP status 매핑 (참고)

API contract 측 가이드. 자세한 매핑은 `docs/contracts/api_contract.md`에서 확정.

```
input_validation  → 400
security_block    → 403 (또는 422)
rate_limit        → 429
db_failure        → 503
rag_failure       → 503
llm_failure       → 502 (외부 의존)
unknown           → 500
```

단 HTTP status에 의존하지 말고 `error.code`로만 분기. 게이트웨이가 HTTP 코드를 바꿔도 코드는 유지.

---

## 13. 보안 응답 정책

```
E-SEC-001 (prompt injection):
  - intent_filter_logs에 raw_input 그대로 기록 (분석용)
  - 사용자에게는 "사용할 수 없는 표현이 있어요"만 노출
  - 어떤 패턴이 차단됐는지 사용자에게 노출 금지 (회피 학습 방지)
  - 같은 user_id가 1분 안에 5회 시도하면 자동 1시간 차단

E-SEC-002 (intent block):
  - reframe_offer 제공 가능하면 함께 노출 (재구성 안내)
  - 단순 block은 reframe_suggestion=null로 응답

E-SEC-004 (부적절 콘텐츠):
  - 운영자 즉시 알림
  - 누적 3회 시 계정 정지 검토 큐
```

---

## 14. 확장 가능성 (Phase 2+)

```
- WebSocket / SSE 에러 envelope (스트리밍 응답 중 일부 chunk 실패)
- offline 큐 (네트워크 실패 시 client 단 보관 → 재연결 시 자동 sync)
- 다국어 user_message (locale=en-US, ja-JP)
- 운영자 대시보드 (실시간 에러율, request_id 검색)
- ML 기반 비정상 입력 감지 (E-SEC-007 보강)
- 에러별 사용자 학습 시그널 (어떤 에러를 자주 보는 사용자는 도움말 노출 강화)
```

---

## 15. Cross-reference 빠른 표

| 에러 발생 위치 | 주 카테고리 | 의존 contract |
|---|---|---|
| API 입력 검증 | input_validation | api_contract.md |
| LLM agent 호출 | llm_failure | agent_io_contract.md §10 |
| Output validation | llm_failure | output_schema.md §15 |
| RAG 검색 | rag_failure | rag_data_contract.md |
| Supabase 호출 | db_failure | db_schema.md, api_contract.md |
| 사용량 한도 | rate_limit | rate_limit_contract.md, cost_control_policy.md |
| 보안 검사 | security_block | llm_security_contract.md |
| 4단계 stepper | (다양) | apps/web/design.md §22 |

---

## 16. Open Questions

1. partial_result 보관 기간 — 클라이언트 측 (sessionStorage) vs 서버 측 (Redis 임시).
2. retry_after의 정확도 — fixed (5s) vs 동적 (모델 큐 길이 기반).
3. E-SEC-001의 1시간 차단 vs 영구 차단 vs 운영자 수동 검토 트리거.
4. 다국어 지원 시 user_message 키-값 사전 분리 시점 (현재 인라인).
5. partial_result의 schema 검증 — 부분 결과도 output_schema validation 통과해야 하는지.
6. 운영자 알림 임계 자동 조정 (학습 기반) vs fixed.
7. E-LLM-010 (revise 한계) 후 사용자가 manual_edit 선택 시 UI 흐름 — 별도 페이지 vs 모달.

---

## 17. 변경 이력

```
v1.0.0 (2026-05-26): Sprint S3-1 초안. 7 카테고리 + 코드 사전, envelope, user_message 표준,
                      4단계 stepper 에러 처리, 로깅/PII 마스킹, 운영자 알림 임계.
```
