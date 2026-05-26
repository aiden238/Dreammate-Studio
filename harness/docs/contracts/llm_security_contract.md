# llm_security_contract.md — LLM 보안 표준 (요청·응답 2단계 검사)

> 위치: `docs/contracts/llm_security_contract.md`
> 상태: Phase 0–1 진입용 핵심 contract 초안
> 참조: `docs/contracts/api_contract.md` §20 (요청/응답 검사 hook 순서)
> 참조: `docs/contracts/agent_io_contract.md` §15 (agent 격리)
> 참조: `docs/contracts/error_response_contract.md` §4.6 (E-SEC-*), §13 (보안 응답 정책)
> 참조: `docs/contracts/output_schema.md` §14 (광고 단어 차단)
> 참조: `docs/contracts/rate_limit_policy.md` (반복 위반 차단 연계)
> 참조: `docs/contracts/privacy_contract.md` (Phase 7+ fill-in, PII 정책 본체)
> 참조: `meta/security_metrics.md` (정량 지표 누적)

---

## 0. 이 문서의 위치

영상기획 AI 에이전트에서 LLM과 직접 상호작용하는 모든 경로(사용자 입력 → LLM, LLM → 사용자 노출, LLM → DB)에서 **사용자 자신과 서비스를 보호하는 정책**을 고정한다. 본 contract는 5가지 위협 모델에 대응한다:

1. **Prompt Injection** — 사용자 입력이 시스템 지시를 덮어쓰려는 시도
2. **System Prompt Leakage** — 내부 prompt가 사용자에게 노출되는 사고
3. **RAG Data Poisoning** — 오염된 후보 지식이 promoted까지 도달하는 경로
4. **PII 유출** — 개인정보가 LLM 호출 / 로그 / 외부 응답에 그대로 흐르는 사고
5. **비용 폭주 / 남용** — 무한 루프 / 자동화된 요청 폭주로 인한 비용 사고

이 contract가 정의하지 않는 대상 (별도 contract로 분리):

- 토큰/요청 횟수 임계치 → `rate_limit_policy.md`
- PII 분류·동의·삭제 절차 본체 → `privacy_contract.md` (Phase 7+ placeholder)
- 데이터 보존 기간 → `data_retention_policy.md` (Phase 7+ placeholder)
- 사용자 동의 UI → `user_consent_contract.md` (Phase 7+ placeholder)
- RAG 승격 흐름의 품질 필터 → `rag_data_contract.md` §6

---

## 1. 설계 원칙

```
1. "Trust no input" — 사용자 입력은 항상 untrusted. 시스템 prompt와 결합하지 않고
   user role 메시지로만 LLM에 전달한다.
2. 2단계 검사가 필수: 요청 검사(LLM 호출 전) + 응답 검사(LLM 호출 후).
3. 차단(block)은 자동 + 즉시. 경고(warn)는 통과 + 로깅 + 누적 임계 알림.
4. 모든 검사 결과는 meta/security_metrics.md 또는 동등한 메트릭 스토어에 기록.
5. 차단 사유는 사용자에게 구체적으로 노출하지 않는다 (회피 학습 방지).
6. 시스템 prompt는 server-side 환경변수/파일에서만 로드. 클라이언트 또는 LLM
   응답을 통해 외부로 노출되는 경로를 절대 만들지 않는다.
7. 보안 사고는 silent fail 금지. 항상 audit_log에 기록 + 운영자 알림.
8. fail-safe 기본값: 모호한 경우 차단보다 통과를 우선 (사용자 경험 보호) —
   단 prompt injection / PII / 광고 1차 차단 단어는 fail-closed.
9. 보안 패치는 contract-change Skill 절차 + security-review Skill 검증을 반드시 통과.
10. 영상기획 외 입력(intent_filter)은 보안 차단이 아니라 reframe 제안 (UX 친화).
```

---

## 2. 2단계 자동 검사 흐름 (개요)

```
[사용자 입력]
   │
   ▼
┌──────────────────────────────────────────────┐
│ Step 1: 요청 검사 (LLM 호출 전)               │
│  1.1 P-AUX-1 intent_filter (영상기획 외 차단)│
│  1.2 PII 패턴 검출 + 마스킹                  │
│  1.3 Prompt injection 패턴 차단              │
│  1.4 XSS / HTML / JS injection sanitize      │
│  1.5 입력 길이 / charset / unicode 검증      │
└──────────────────────────────────────────────┘
   │ (통과 시)
   ▼
[LLM 호출]
   │
   ▼
┌──────────────────────────────────────────────┐
│ Step 2: 응답 검사 (LLM 호출 후)               │
│  2.1 JSON parse + output_schema validation   │
│  2.2 광고적 표현 1차 차단 (재생성 1회)        │
│  2.3 광고적 표현 2차 경고 (통과 + warning)    │
│  2.4 PII 잔존 패턴 마스킹                    │
│  2.5 응답 sanitize (HTML/JS 제거)            │
│  2.6 system prompt leakage 검사               │
└──────────────────────────────────────────────┘
   │ (통과 시)
   ▼
[사용자에게 응답]
```

각 단계는 §3, §4에서 상세 정의.

---

## 3. Step 1 — 요청 검사 (LLM 호출 전)

`api_contract.md` §20.1의 hook 순서 중 6번(`user_input 텍스트 검사`)에 해당한다. 본 contract는 그 6번 안의 세부 흐름을 정의한다.

### 3.1 intent_filter (P-AUX-1)

| 항목 | 내용 |
|---|---|
| 검사 대상 | `user_input` 텍스트 |
| 통과 조건 | `decision == "allow"` 또는 `decision == "reframe_offer"` 후 사용자 수락 |
| 실패 시 | `decision == "block"` → reframe_suggestion=null → 사용자에게 안내 메시지 |
| 에러 코드 | `E-SEC-002` (intent block) |
| 로깅 | `intent_filter_logs` 테이블 (`db_schema.md` §5.3) |
| 메트릭 | `meta/security_metrics.md` — block 카운트 일/주/월 |

→ 자세한 P-AUX-1 본문 구조는 `output_schema.md` §11.

### 3.2 PII 검출 + 마스킹

검사 패턴 (정규식, NFC 정규화 후 적용):

```
직접 식별자 (자동 마스킹 또는 차단):
  전화번호      \d{2,3}-\d{3,4}-\d{4}                  → 010-****-1234 (뒤 4자리만 노출)
  휴대폰(붙임)   01[016789]\d{7,8}                      → 010****1234
  이메일        [A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}
                                                       → u***@***.com (앞 1자 + 도메인 첫 글자)
  주민번호      \d{6}-[1-4]\d{6}                        → ******-*******
  카드번호      \d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4} → ****-****-****-****
  계좌번호      \d{3}-\d{2,6}-\d{2,8}(-\d+)?            → ***-***-****
  IP주소        IPv4/IPv6 패턴                           → 마지막 옥텟 마스킹

간접 식별자 (마스킹 안 함, 단 명시 동의 확보 시에만 보존):
  이름          (한글 2~4자) 또는 (영문 First Last)     — 사용자 자기 입력은 허용
  주소          시/구/동/번지 패턴                       — 영상기획 입력에서 보통 불필요
  회사명        고유명사                                  — 사용자가 명시한 경우만 보존
```

처리 정책:

```
1. 직접 식별자가 user_input에서 발견되면:
   case A: 사용자 자기 정보로 추정 (예: "제 전화번호 010-... 화면에 띄워주세요")
     → 차단 (E-SEC-006). user_message: "개인정보가 포함된 것 같아요. 입력에서
                                       제외하고 다시 시도해주세요."
   case B: 영상기획과 무관 (예: "타겟이 010-... 사람")
     → 차단 (E-SEC-006)
   case C: 영상 콘텐츠 본문 자체에 등장 (드물지만 가능)
     → 마스킹 후 LLM 전달 + validation.warnings에 "pii_masked" 기록

2. 간접 식별자는 LLM 호출 직전 마스킹하지 않음 (영상기획 컨텍스트 자체).
   단 agent_io_logs 저장 시 raw_payload는 그대로, 90일 후 비식별화
   (→ data_retention_policy.md placeholder).

3. PII 마스킹 hook은 모든 prompt 호출 전 공통으로 실행되며,
   intent_filter (P-AUX-1) 호출에도 적용 (사용자 첫 입력 시점부터).
```

에러 코드 매핑: `E-SEC-006` (PII 노출 시도).
메트릭: PII 매칭률 (false positive / false negative 추정), 마스킹 적용 건수 일/주/월.

### 3.3 Prompt Injection 방어

**원칙: 시스템 prompt 격리.**

```
- 시스템 prompt는 LLM 호출 시 system role 메시지로만 전송.
- 사용자 입력은 항상 user role 메시지로만 전송 (system role에 절대 concat 금지).
- system role 메시지의 끝에 명시적 구분자 (예: "###USER_INPUT_BELOW###")를
  두지 않는다 — delimiter 우회의 입구가 된다.
- prompt template의 변수 치환은 server-side에서만 수행. 사용자 입력이
  template literal로 들어가는 경로 금지.
```

**메타 명령어 차단 패턴 (정규식, 대소문자 무시, 한·영 둘 다):**

```
1. "이전 지시(를)?\s*무시" / "이전 instructions?\s*ignore"
2. "system\s*prompt(을|를)?\s*(출력|보여|공개|드러내)" / "show\s+(the\s+)?system\s+prompt"
3. "너의?\s*(원래|진짜)\s*역할" / "what.*are.*you.*really"
4. "(앞으로|이제부터).*역할(을|는)?\s*[가-힣A-Za-z]+(으로|로)?\s*(바꿔|변경)"
   / "act\s+as\s+(a\s+)?[A-Za-z]+" (단 영상기획 컨텍스트는 예외)
5. "(`{3}|---|###).*(?:system|assistant|user)\s*[:：]" — role 위조 시도
6. "(jailbreak|DAN|do\s+anything\s+now)"
7. "<\|.*?\|>" — 모델 special token 위조 (예: <|im_start|>)
8. "```\s*system" / "```\s*assistant" — code fence를 통한 role 위조
```

처리 정책:

```
- 1~8번 중 어느 하나라도 매칭되면 즉시 E-SEC-001 차단.
- 차단 사유는 사용자에게 노출하지 않음: "사용할 수 없는 표현이 있어요. 다시 입력해주세요."
- 같은 user_id가 1분 안에 5회 반복 시도하면 자동 1시간 차단 (rate_limit_policy 연계).
- 차단된 raw_input은 intent_filter_logs에 그대로 저장 (분석용,
  90일 후 비식별화).
- 메트릭: 일/주/월 차단 횟수, 패턴별 적중 분포.
```

**출력 검증 (Step 2와 연계):**

LLM이 system prompt를 echo back하거나 메타 명령어를 그대로 출력하는 경우를 응답 검사에서 한 번 더 확인 (§4.6).

### 3.4 XSS / HTML / JS injection sanitize

```
- 사용자 입력에서 다음을 제거:
    <script>...</script>
    on{event}="..." (onclick, onerror, onload 등 모든 inline event handler)
    javascript: URI scheme
    data:text/html, vbscript:, mailto:javascript: 등 위험 scheme
- HTML 태그는 화이트리스트 방식: <b>, <i>, <em>, <strong>, <br>, <p> 만 허용
  (영상기획 입력에서 사실상 불필요하지만 사용자가 무심코 붙여넣은 경우 대비)
- sanitize 결과가 원본과 다르면 validation.warnings에 "xss_sanitized" 기록
- 단순 sanitize로 충분치 않은 명백한 공격 (예: <img src=x onerror=...) 발견 시
  E-SEC-005 차단
```

라이브러리 권장: DOMPurify (frontend), bleach (Python backend) — 단 직접 fallback regex도 유지.

에러 코드: `E-SEC-005`.

### 3.5 입력 길이 / charset / unicode 검증

```
- 길이 상한:
    user_input (intent_filter): 500자
    user_input (card 단계): 500자
    short_idea: 200자
    selection_reason / feedback.reason: 300자
- charset: UTF-8 강제. NFC 정규화 후 검사 (NFKC는 글자 형태 변형 가능성).
- 차단할 unicode 카테고리:
    - 제로폭 문자 (U+200B ~ U+200F, U+FEFF) — prompt injection 회피 시도
    - 양방향 격리 문자 (U+202A ~ U+202E) — 보안 도구 회피
    - private use area (U+E000 ~ U+F8FF)
- 이모지는 허용 (UI 표현용)
```

위반 시: E-INV-003 (길이) 또는 sanitize + warning (특수 unicode).

---

## 4. Step 2 — 응답 검사 (LLM 호출 후)

`api_contract.md` §20.2의 응답 검사 hook에 해당.

### 4.1 JSON parse + output_schema validation

```
- LLM 응답을 JSON.parse → 실패 시 2회 재시도 (prompt에 "JSON으로만 응답" 강조)
- output_schema.md §3~§12의 해당 prompt body 검증 (필드/길이/enum)
- envelope.validation.passed=false면 §15(output_schema)의 case A/B/C 흐름 진입
- 에러 코드: E-LLM-002 (parse), E-LLM-003 (validation), E-LLM-007 (빈 응답)
```

본 contract는 위 흐름의 호출만 보장한다 (상세는 output_schema).

### 4.2 광고적 표현 1차 차단

→ `output_schema.md` §14.1의 1차 차단 단어 사전 적용.

```
사전: 최고의 / 혁신적 / 획기적 / 완벽한 / 1위 / 넘버원 / 압도적 / 역대급
검사: 정규식 또는 단어 경계 매칭 (Aho-Corasick 권장)
처리:
  1차 발견 → 자동 재생성 1회 (system prompt에 "광고적 과장 금지" 강조 추가)
  재시도 후에도 위반 → validation.passed=false + E-LLM-006
  사용자 메시지: "AI가 표현을 다듬는 데 문제가 생겼어요. 다시 시도해주세요."
예외:
  - direct_input 사용자 텍스트는 검사 대상 아님 (자기 표현 존중)
  - 단 direct_input이 LLM 응답에 재인용되어 들어오면 검사 대상
```

에러 코드: `E-LLM-006`.
메트릭: 일/주 단위 차단 횟수, prompt_id별 위반 비율.

### 4.3 광고적 표현 2차 경고

→ `output_schema.md` §14.1의 2차 경고 단어 사전 적용.

```
사전: 특별한 / 특별 / 놀라운 / 엄청난
처리: 통과 + validation.warnings에 "ad_warning: <word>" 기록
누적 임계: 동일 prompt_id에서 일 5건 초과 시 운영자 Slack #ops-alert 알림
조정: 누적 통계 기반으로 1차 차단 사전으로 승격하거나 사전 제거 (운영자 검토)
```

### 4.4 PII 잔존 패턴 마스킹

```
- LLM 응답에 사용자 입력 PII가 echo 또는 fabricate 형태로 등장할 수 있다.
- §3.2의 직접 식별자 패턴을 응답에도 동일하게 적용해서 발견 시 마스킹.
- 마스킹 적용 시 validation.warnings에 "pii_in_response_masked" 기록.
- 운영자 메트릭: false positive (마스킹된 게 PII가 아닌 경우) 분기 분석.
```

### 4.5 응답 sanitize (HTML/JS injection 제거)

```
- LLM 응답 중 사용자에게 직접 노출되는 텍스트 필드 (description, hook,
  one_line, beat, concept, reasons 등)에서:
    - <script> 태그 제거
    - onclick="..." 등 inline event 제거
    - javascript: URI scheme 제거
    - 마크다운 링크 URL은 https/http 외 차단
- sanitize 결과가 원본과 다르면 validation.warnings에 "response_sanitized" 기록.
```

### 4.6 system prompt leakage 검사

```
검사 패턴 (응답 본문 어디라도 매칭되면 차단):
- 시스템 prompt에 포함된 고정 marker 문자열 (운영자가 prompt 변경 시 marker 갱신)
- "You are a video planning AI" 등 영문 system 어구 echo (한국어 응답이라야 함)
- "DO NOT", "MUST", "NEVER" 등 명령어가 한국어 응답에 그대로 등장
- prompt template 변수의 placeholder (`{{brand_name}}`, `{user_input}` 등)
  가 마스킹되지 않은 채 등장

처리:
- 발견 시 즉시 자동 재생성 1회 (이때 prompt에 marker는 제외)
- 재시도 후에도 발견 시 → validation.passed=false + 운영자 즉시 알림
- 사용자에게는 "AI 응답을 정리하는 중 문제가 생겼어요" (E-LLM-002 호환)
- 누적 1건이라도 발생하면 audit_log에 critical 기록 + Slack #security 즉시 알림
```

---

## 5. 시스템 prompt 격리 정책

### 5.1 저장 위치

```
- 모든 prompt template: ai_system/prompts/templates/P-NNN/v{version}/system.md
- 변수 치환은 server-side render 단계에서 단방향 (사용자 입력은 template literal에
  들어가지 않고 별도 user role 메시지로만 전송)
- prompt template 파일에는 marker 행 1개 추가 (예: 첫 줄에 <PROMPT_MARKER:P-006-v1.0.0>)
  — §4.6 검사에서 응답 echo 차단용
```

### 5.2 환경변수 격리

```
- LLM API key, embedding API key, Supabase service role key는
  모두 server-side .env에서만 로드 (→ env_contract.md placeholder)
- client (Next.js)에는 절대 노출 금지. NEXT_PUBLIC_* prefix 사용 금지.
- env_contract에서 비밀 회전 정책 정의 (Phase 2+)
```

### 5.3 로깅 격리

```
- agent_io_logs.input_payload에는 user_input과 system prompt를 모두 저장하되,
  외부 노출 시점 (예: 사용자 문의 응답)에는 system 부분만 마스킹.
- errors.log 등 외부 도구(Sentry)에 전송되는 로그에는 system prompt 자체를
  포함시키지 않는다. 대신 prompt_id + prompt_version만 기록.
```

---

## 6. RAG Data Poisoning 방어

본 contract는 RAG 흐름의 보안 게이트만 정의한다. 상세 흐름은 `rag_data_contract.md` §5~§7.

```
방어 layer:
  layer 1 (수집): source_kind 명시 + 출처 검증. 익명 후보 금지.
  layer 2 (filtered): 자동 품질 필터. 광고 단어 위반은 즉시 rejected.
  layer 3 (evaluated): LLM 자동 평가 + 광고/부적절 콘텐츠 재검사.
  layer 4 (approved): 운영자 승인 필수 (자동 승격은 제한된 source_kind만).
  layer 5 (promoted): rag_chunks INSERT 직전 PII 잔존 검사 + 광고 단어 검사.

검색 단계 보안:
  - top_k=5 → similarity≥0.7 → 채택 최대 3개 (rag_data §6)
  - 검색 결과가 사용자에게 노출되는 시점에 한번 더 PII / 광고 검사
  - 사용자가 RAG 결과를 거절하거나 negative feedback 5건 누적 시
    해당 chunk를 quarantine 큐로 이동 (운영자 검토)
```

에러 코드: 검색 자체 실패는 `E-RAG-*`. 보안 차단은 `E-SEC-003` (광고 위반) 또는 `E-SEC-006` (PII).

---

## 7. 비용 보호 (cost-spike 차단)

`rate_limit_policy.md`와 본 contract가 함께 책임.

```
본 contract 책임:
- 단일 LLM 호출의 max_tokens / timeout이 agent_io_contract.md §3~§7 정의를
  초과하는 경우 즉시 abort (E-LLM-008 또는 E-LLM-001)
- Critic revise_round=2 도달 시 강제 approve (output_schema §9.3 / agent_io §5.8)
- 동일 user_id가 30초 안에 같은 endpoint 10회 호출 시 자동 1분 차단
  (botnet / 무한 루프 방어)

rate_limit_policy 책임:
- per-user / per-IP / per-org 임계치 + 응답 헤더
- 비용 quota window
- 일/월 비용 상한
```

메트릭: cost spike 1.5x 평균 초과 incidents, 자동 abort 횟수.

---

## 8. 에러 코드 매핑 (E-SEC-*)

`error_response_contract.md` §4.6 정합.

| 코드 | 의미 | 검사 단계 | 처리 |
|---|---|---|---|
| E-SEC-001 | prompt injection 시도 감지 | Step 1 §3.3 | block, 1분 5회 시 1h 자동 차단 |
| E-SEC-002 | 영상기획 외 입력 (intent block) | Step 1 §3.1 | block, reframe 안내 |
| E-SEC-003 | 광고적 과장 표현 (사용자 입력 단) | Step 1 §3.2 보조 | warn 또는 block |
| E-SEC-004 | 부적절 콘텐츠 (욕설/혐오/성/폭력) | Step 1 + 운영자 | block, 누적 3회 시 계정 정지 큐 |
| E-SEC-005 | XSS 시도 (HTML/JS 인젝션) | Step 1 §3.4 | sanitize 또는 block |
| E-SEC-006 | PII 노출 시도 | Step 1 §3.2 + Step 2 §4.4 | mask 또는 block |
| E-SEC-007 | 계정 도용 의심 (비정상 사용 패턴) | rate_limit + 본 contract | flag, 운영자 검토 큐 |

사용자에게 노출되는 메시지는 `error_response_contract.md` §5.2 그대로.

---

## 9. security_metrics 기록 정책

`meta/security_metrics.md`가 누적할 정량 지표 (placeholder이지만 Phase 7+ 본격 운영).

```
일/주/월 집계 항목:
- Prompt injection 차단 횟수 (패턴별)
- PII 마스킹 적용 건수 + false positive 추정
- 광고 1차 차단 횟수 (prompt_id별)
- 광고 2차 경고 누적
- XSS sanitize 적용 건수
- intent_filter block 횟수
- Critic revise_round=2 강제 approve 횟수
- system prompt leakage 의심 사례 (응답 검사 4.6)
- cost spike incidents (1.5x 평균 이상)
- rate limit 위반 user_id / IP

저장 위치:
- Phase 0~6: eval/security_reviews/ 에 마크다운으로 누적 (수동 또는 주간 자동)
- Phase 7+: meta/security_metrics.md 본문에 정량 표 + 시계열 갱신
```

→ `meta/security_metrics.md`에 이미 작성 트리거 stub 있음. Phase 7 진입 시 본 contract가 출처가 된다.

---

## 10. security-review Skill 연동

```
- security-review Skill (.claude/skills/security-review/SKILL.md)은 본 contract를
  체크리스트로 사용한다.
- 매 Phase 종료 시 또는 contract-change Skill 절차 안에서 호출.
- 결과는 eval/security_reviews/{YYYY-MM-DD}_review.md로 누적.
- Skill의 10영역 점검 항목은 본 contract §2~§7의 흐름과 1:1로 매핑되어야 함.
```

→ `.claude/skills/security-review/SKILL.md`가 본 contract와 정합해야 한다 (Phase 진입 시점에 dependency_map.yaml로 명시).

---

## 11. 보안 사고 대응 절차

```
1. 격리 (Containment)
   - 사고 감지 즉시 영향 범위 확인 (user_id, IP, endpoint, prompt_id)
   - 필요 시 해당 endpoint 임시 비활성화 (feature flag) 또는 1시간 차단
   - prompt injection 성공 의심 시 해당 prompt_version 즉시 freeze

2. 분석 (Analysis)
   - agent_io_logs + intent_filter_logs + errors.log 에서 동일 trace_id 추적
   - PII 유출 의심 시 누구의 어떤 정보가 어디까지 흘렀는지 정확히 파악
   - 같은 패턴의 과거 사례를 audit_log에서 검색

3. 패치 (Mitigation)
   - 패턴 추가 시 본 contract §3~§4의 정규식/사전 갱신 (contract-change Skill)
   - prompt template 수정 시 prompt-version-review Skill로 회귀 평가
   - 새 marker 추가 시 모든 의존 prompt에 적용

4. 회고 (Postmortem)
   - meta/retrospectives/{YYYY-MM-DD}_security_incident.md 작성
   - 재발 방지책을 meta/patterns.md에 누적
   - 사고가 사용자에게 영향을 미친 경우 privacy_contract의 통지 절차
     (Phase 7+ fill-in) 발동
```

---

## 12. Phase 7+ 강화 항목 (현재는 placeholder)

```
- rate limit per-organization (현재 per-user, per-IP만)
- MFA / WebAuthn / passkey 지원 (Supabase Auth 확장)
- API key rotation 자동화 (현재 수동)
- 비밀 회전 정책 (env_contract placeholder에서 정의)
- 감사 로그 (audit_log) 본격 운영 — 현재는 errors.log 흡수
- ML 기반 비정상 입력 감지 (E-SEC-007 보강)
- DDoS / botnet 차단 (Cloudflare 또는 WAF 연계)
- DLP (Data Loss Prevention) 통합 — Phase 11+
- SOC 2 / ISO 27001 준수 대비 — Phase 21+
```

→ `phases/upcoming/`에 각 Phase 진입 시 본 항목을 풀어내는 task 생성.

---

## 13. Cross-reference 빠른 표

| 검사 단계 | 입력 소스 | 출력 | 의존 contract |
|---|---|---|---|
| Step 1.1 intent_filter | user_input | allow/block/reframe | output_schema §11, error_response §4.6 |
| Step 1.2 PII 마스킹 | user_input | masked text + warnings | privacy_contract (Phase 7+) |
| Step 1.3 injection 차단 | user_input | block 또는 통과 | rate_limit (반복 차단), error_response §13 |
| Step 1.4 XSS sanitize | user_input | sanitized text | frontend_design §6 (서버 sanitize 보조) |
| Step 2.1 schema validation | LLM 응답 | passed=true/false | output_schema §15 |
| Step 2.2 광고 1차 차단 | LLM 응답 | regenerate 또는 통과 | output_schema §14 |
| Step 2.4 PII 잔존 | LLM 응답 | masked or block | privacy_contract |
| Step 2.6 system leak | LLM 응답 | regenerate + alert | audit_log (Phase 7+) |

---

## 14. Open Questions

1. prompt injection 메타 명령어 사전(§3.3)을 정규식 리스트로 둘지, ML 분류기로
   진화시킬지 — Phase 7+ 누적 데이터로 결정.
2. PII 마스킹 false positive vs false negative 균형 — 사용자 자기 입력 보호와
   영상 콘텐츠 본문 보존 사이의 트레이드오프.
3. system prompt marker(§5.1)를 prompt 안에 두는 방식이 LLM 응답 품질에
   영향을 주는지 — A/B 측정 필요.
4. RAG poisoning 탐지의 자동 quarantine 임계치 (현재 negative feedback 5건) —
   누적 데이터로 조정.
5. 보안 사고 회고를 retrospectives와 통합 폴더로 둘지 별도로 둘지.
6. cost spike 자동 abort 임계치 (1.5x 평균) — 정상 트래픽 변동 폭과의 균형.

---

## 15. 확장 가능성 (MVP 후 조정)

```
- LLM provider 다중화 시 (Anthropic, Gemini): system prompt 격리 정책이
  provider별 API 차이를 흡수해야 함 (예: Anthropic은 system 파라미터 별도).
- function calling / tool use 도입 시: tool 호출 인자에 대한 별도 sanitize 필요.
- voice input 시 (Phase 11+): 음성 → 텍스트 변환 직후 PII 마스킹 시점이 추가됨.
- 다국어 (en-US, ja-JP) 시: 메타 명령어 사전을 locale별 분기.
- 자체 모델 fine-tune 시 (Phase 21+): system prompt 형식 자체가 달라질 수 있음 —
  본 contract의 격리 정책은 그대로 유지되어야 함.
```

---

## 16. 변경 이력

```
v1.0.0 (2026-05-26): Sprint S3-3 초안. 2단계 자동 검사 흐름 (요청·응답),
                      PII 사전, prompt injection 패턴, system leak 검사,
                      RAG poisoning 게이트, 비용 보호, E-SEC-* 코드 매핑,
                      security_metrics 연동, 사고 대응 절차.
```
