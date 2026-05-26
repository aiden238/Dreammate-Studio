# rate_limit_policy.md — 요청 빈도·비용 제한 정책

> 위치: `docs/contracts/rate_limit_policy.md`
> 상태: Phase 0–1 진입용 핵심 contract 초안
> 참조: `docs/contracts/api_contract.md` §3.2 (응답 헤더), §16 (rate limit envelope)
> 참조: `docs/contracts/error_response_contract.md` §4.5 (E-RL-*), §5.2
> 참조: `docs/contracts/agent_io_contract.md` §9 (비용 통제, 세션/일일 상한)
> 참조: `docs/contracts/llm_security_contract.md` §7 (cost 보호 협력)
> 참조: `ai_system/orchestration/cost_control_policy.md` (모델 폴백 트리거)

---

## 0. 이 문서의 위치

`api_contract.md`가 응답 헤더 형식과 endpoint별 정책의 자리만 잡았다면, 본 contract는 **구체적 임계치 + window 정책 + tier별 분기**를 고정한다.

이 contract가 정의하는 대상:

1. 4개 tier (anonymous / free / paid / internal)
2. tier × endpoint × window 매트릭스
3. quota window 종류 (sliding / fixed / token bucket)
4. 응답 헤더 표준 (`X-RateLimit-*`, `Retry-After`)
5. 초과 시 응답 envelope + partial_result
6. 비용 quota (LLM 호출 일일 상한)
7. 부정 사용 감지 + 자동 차단 절차
8. 정책 변경 시 사전 공지 절차

이 contract가 정의하지 않는 대상:

- LLM 호출당/세션당 비용 상한 본체 → `agent_io_contract.md` §9
- 모델 폴백 (gpt-4o ↔ mini) → `ai_system/orchestration/cost_control_policy.md`
- 보안 차단 (반복 prompt injection 등) → `llm_security_contract.md` §7
- 결제 / 유료 tier 정의 → Phase 11+ (별도 contract)

---

## 1. 설계 원칙

```
1. 모든 endpoint에 rate limit이 적용된다. 무한 호출 가능 endpoint 금지.
2. tier별 차등. anonymous < free < paid < internal.
3. quota window는 sliding(기본). 정확한 추적이 필요한 곳에만 사용.
   단순 burst 방어는 fixed window + token bucket으로 충분.
4. 초과 시 HTTP 429 + E-RL-* 코드 + Retry-After 헤더. partial_result는 보존.
5. 응답 헤더는 모든 응답(성공/실패 무관)에 부착. 클라이언트가 사전에
   임계 근접을 알 수 있어야 함.
6. 비용 quota는 호출 횟수와 별도. 토큰 사용량 × 모델 단가 = 비용.
7. 정책 변경(임계치 인상/인하 포함)은 24시간 사전 공지 후 적용.
8. 부정 사용 감지는 silent fail 금지. 차단 시 사용자에게 안내 + 운영자 알림.
9. 무료 사용자는 영상기획 흐름을 끝까지 경험할 수 있는 최소 한도 보장.
10. 사용자 1인이 IP 다수에서 호출(또는 IP 1개 user 다수)하는 경우는 보안 신호로
   취급. rate limit이 아니라 E-SEC-007 (계정 도용 의심) 큐로 분기.
```

---

## 2. Tier 정의

### 2.1 anonymous

```
대상: 로그인 안 한 사용자 (IP 기준 식별)
특징: 매우 제한적. intent_filter / 카드 미리보기 같은 read-only 또는
       경량 endpoint만 노출.
적용 endpoint: POST /api/v1/intent/check, POST /api/v1/auth/login (재시도 방어)
              (그 외 endpoint는 401 응답)
quota: §3 표 참조
```

### 2.2 free

```
대상: 로그인 한 일반 사용자 (Supabase Auth 활성 세션)
특징: MVP 핵심 사용자층. Discovery 5단계 + 생성 흐름을 끝까지 경험 가능.
quota: §3 표 참조. 일일 영상 생성 ~5건, 일일 LLM 비용 ~$0.10.
```

### 2.3 paid (Phase 11+ 진입)

```
대상: 결제 완료 사용자 (subscription 또는 credit)
특징: free의 5~10배 한도. cost_saving 강제 폴백 없음.
quota: Phase 11+에서 본 contract 갱신 시 확정. 본 v1.0에서는 placeholder.
```

### 2.4 internal

```
대상: 운영자 / 자동 테스트 / eval 회귀 / 본 하네스의 sanity script
특징: rate limit 면제 (또는 매우 높은 상한). 단 비용은 추적.
식별: service role JWT 또는 X-Internal-Bot 헤더 + IP allowlist
주의: 외부 노출 금지. CI/CD pipeline과 운영자 콘솔만 사용.
```

---

## 3. Tier × endpoint × window 매트릭스

### 3.1 anonymous

| Endpoint | per-minute | per-hour | per-day | 비고 |
|---|---|---|---|---|
| `POST /api/v1/auth/login` | 10 / IP | 60 / IP | 200 / IP | brute force 방어 |
| `POST /api/v1/intent/check` | 5 / IP | 30 / IP | 100 / IP | LLM 호출 포함 |
| 그 외 | 0 (401) | — | — | 인증 필요 |

burst: token bucket capacity = 분당 limit × 1.5 (예: login 15 burst).

### 3.2 free

**조회 endpoint (LLM 호출 없음):**

| Endpoint | per-minute | per-hour | per-day |
|---|---|---|---|
| `GET /api/v1/brands` | 60 / user | 600 / user | 5000 / user |
| `GET /api/v1/domains` | 60 / user | 600 / user | 5000 / user |
| `GET /api/v1/series` | 60 / user | 600 / user | 5000 / user |
| `GET /api/v1/plans/{id}` | 60 / user | 600 / user | 5000 / user |
| `GET /api/v1/plans/{id}/status` | 120 / user | — | — | polling 허용 |

**생성·변경 endpoint (CRUD, LLM 호출 없음):**

| Endpoint | per-minute | per-hour | per-day |
|---|---|---|---|
| `POST /api/v1/brands` | 5 / user | 30 / user | 100 / user |
| `POST /api/v1/domains` | 10 / user | 60 / user | 300 / user |
| `POST /api/v1/series` | 10 / user | 60 / user | 300 / user |
| `PATCH /*` | 30 / user | 300 / user | 1000 / user |
| `DELETE /*` | 10 / user | 60 / user | 200 / user |

**LLM 호출 endpoint (별도 엄격):**

| Endpoint | per-minute | per-hour | per-day | 비고 |
|---|---|---|---|---|
| `POST /api/v1/intent/check` | 20 / user | 200 / user | 500 / user | api_contract §10.1 정합 |
| `POST /api/v1/plans/start` | 3 / user | 20 / user | 50 / user | 신규 세션 |
| `POST /api/v1/plans/{id}/step` | 10 / user | 100 / user | 300 / user | Discovery 단계당 |
| `POST /api/v1/plans/{id}/generate` | 2 / user | 10 / user | **5 / user** | 핵심 비용 endpoint |
| `POST /api/v1/plans/{id}/select` | 10 / user | 60 / user | 100 / user | |
| `POST /api/v1/plans/{id}/feedback` | 20 / user | 200 / user | 500 / user | |

**IP 기준 추가 제한 (botnet 방어, free + anonymous 통합):**

| 대상 | per-minute | per-hour |
|---|---|---|
| 모든 endpoint 총합 | 100 / IP | 2000 / IP |
| LLM endpoint 총합 | 30 / IP | 500 / IP |

→ `api_contract.md` §4.1의 "IP당 분당 10회"는 anonymous 로그인 시도에 한정. 본 표가 그것을 포함하는 상위 매트릭스.

### 3.3 paid (Phase 11+)

```
free의 limit × 5 ~ × 10 권장 (Phase 11+에서 확정).
LLM 호출 일일 quota: 50건 / user / day (generate 기준).
비용 quota: $5.00 / user / day.
```

### 3.4 internal

```
모든 endpoint rate limit 면제. 단 다음 로깅 의무:
- service role JWT 사용 횟수 일/주/월 집계
- batch eval 호출은 별도 메트릭 (eval/regression_results/)
- 비용은 별도 internal_cost_log에 누적 (사용자 quota와 분리)
```

---

## 4. Quota window 정책

### 4.1 sliding window (기본)

```
정의: 현재 시각 기준으로 정확히 N초/분/시 전까지의 호출 수 카운트
구현: Redis ZADD + ZREMRANGEBYSCORE
   key = "rl:{tier}:{user_id_or_ip}:{endpoint_group}:{window}"
   ZADD key <timestamp> <request_id>
   ZREMRANGEBYSCORE key 0 (<now - window>)
   ZCARD key → 현재 카운트
장점: 정확함. burst 우회 어려움.
단점: Redis 부하. 모든 호출이 ZADD + ZREMRANGEBYSCORE 수행.
적용:
  - LLM endpoint per-day quota
  - 비용 quota (per-day, per-month)
  - 보안 임계 (1분 5회 prompt injection 등)
```

### 4.2 fixed window

```
정의: UTC 기준 정시(0초, 0분, 자정)부터 N초/분/시까지 카운트, 이후 리셋
구현: Redis INCR + EXPIRE
   key = "rl:fixed:{tier}:{user_id}:{endpoint}:{YYYYMMDDHHMM}"
   INCR key (TTL = window 길이)
장점: 빠름. Redis 한 번의 INCR.
단점: window 경계 직전·직후 burst 가능 (이론상 limit × 2)
적용:
  - 조회 endpoint (정확도 덜 중요)
  - 응답 헤더 X-RateLimit-* 표시용
```

### 4.3 token bucket (burst 허용)

```
정의: 일정 속도로 token 충전 + 호출 시 token 소비
구현: 사용자별 bucket {capacity, refill_rate, current, last_refill}
   호출 시: refill 계산 → token >= 1이면 소비 + 통과, 미만이면 거부
장점: 정상 사용자가 잠깐의 burst를 흡수할 수 있음
단점: Redis WATCH/MULTI 또는 Lua script로 atomic 보장 필요
적용:
  - login / auth (burst capacity = limit × 1.5)
  - LLM endpoint의 분 단위 (capacity = limit × 1.2)
```

### 4.4 선택 가이드

```
endpoint 종류                  기본 선택
--------------------------     ----------------------
read-heavy 조회                fixed window (1분)
경량 CRUD                       fixed window (1분) + sliding (1일)
LLM 호출                        token bucket (분) + sliding (일)
비용 quota                       sliding (일/월) — 정확성 필수
보안 차단 (반복 시도)             sliding (1분, 1시간) — 정확성 필수
```

---

## 5. 응답 헤더 표준

`api_contract.md` §3.2 정합. 본 contract가 헤더 사양을 확정.

| 헤더 | 형식 | 값 | 비고 |
|---|---|---|---|
| `X-RateLimit-Limit` | int | 현재 window의 limit | 가장 임박한 window 기준 |
| `X-RateLimit-Remaining` | int | 남은 호출 수 | 0이면 다음 요청 차단 |
| `X-RateLimit-Reset` | int (unix sec) | 리셋 시각 | sliding은 가장 오래된 호출 + window |
| `X-RateLimit-Window` | string | `1m` / `1h` / `1d` | 임박한 window 라벨 |
| `Retry-After` | int (sec) | 다음 시도까지 대기 초 | 429 응답 시 필수 |

복수 window가 동시 적용되는 경우 (분 + 시 + 일):
```
가장 임박한 window (Remaining이 가장 적은) 기준 1개만 헤더에 반영.
단 X-RateLimit-Policy 헤더 (선택)로 multi-window 정책 요약 노출 가능:
  X-RateLimit-Policy: "10;w=60, 100;w=3600, 500;w=86400"
  (IETF draft-polli-ratelimit-headers 형식 참고)
```

---

## 6. 초과 시 응답 envelope

`error_response_contract.md` §3 + §4.5 정합.

```json
{
  "ok": false,
  "error": {
    "code": "E-RL-002",
    "category": "rate_limit",
    "message": "rate limit exceeded for endpoint /api/v1/plans/start (per-minute)",
    "user_message": "너무 빠르게 요청하셨어요. 잠시 기다려주세요.",
    "user_action": "wait",
    "retryable": true,
    "retry_after": 30,
    "request_id": "...",
    "occurred_at": "2026-05-26T08:30:15Z",
    "context": {
      "endpoint": "/api/v1/plans/start",
      "window": "1m",
      "limit": 3,
      "reset_at": 1748246430,
      "tier": "free"
    }
  },
  "partial_result": null
}
```

HTTP status: `429 Too Many Requests`.

### 6.1 코드 매핑

| 코드 | 의미 | tier | 안내 |
|---|---|---|---|
| E-RL-001 | 일일 비용 한도 초과 | free / paid | "오늘 사용량 한도에 도달했어요. 내일 다시 만나요." |
| E-RL-002 | 분당 요청 수 초과 | 전체 | "너무 빠르게 요청하셨어요. 잠시 기다려주세요." |
| E-RL-003 | 세션당 LLM 호출 횟수 초과 | 전체 | "이 세션의 사용량이 임계에 도달했어요. 새 세션을 시작해주세요." |
| E-RL-004 | IP 분당 요청 수 초과 | anonymous | "잠시 후 다시 시도해주세요." |
| E-RL-005 | 일일 영상 생성 횟수 초과 | free | "오늘 만들 수 있는 영상 수에 도달했어요." |

### 6.2 partial_result 보존

```
generate 진행 중 quota 초과 (드물지만 일일 비용 한도 도달):
- 이미 완료된 stage의 결과는 partial_result로 보존
- user_action: "continue_partial" + "wait"
- 다음 day reset 후 같은 plan_id로 재진행 가능
```

### 6.3 user_action 안내

```
wait: 카운트다운 표시, retry_after 끝나면 자동 재시도
contact_support: 24h 이상 차단 시 (E-SEC-007 의심 시 등)
upgrade (Phase 11+): paid tier 안내 (free quota 도달 시)
```

---

## 7. 비용 quota (LLM 호출 일일/월 상한)

`agent_io_contract.md` §9와 협력. 본 contract가 user-level 노출 정책 담당.

```
free tier:
  per-user per-day:  $0.10  (대략 generate 3~5회)
  per-user per-month: $2.00 (안전망. 일일 누적 ≠ 월 단순합)

paid tier (Phase 11+):
  per-user per-day:  $1.00
  per-user per-month: $20.00

전체 시스템 안전망 (운영자 비상):
  daily_total_budget:  $100 (모든 user 합산)
  monthly_total_budget: $2000

브랜드(brand_id) 단위 (Phase 11+ 협업 기능 대비):
  per-brand per-day:  $0.50 (free), $5.00 (paid)
```

### 7.1 cost_saving 모드 강등

`ai_system/orchestration/cost_control_policy.md` 참조. 본 contract는 트리거 조건만 정의.

```
user 일일 비용 사용량이:
  ≥ 50% → 정상 (alerting 없음)
  ≥ 75% → 사용자에게 "사용량이 75%에 도달했어요. 곧 절약 모드로 전환돼요." 안내
  ≥ 90% → 자동 cost_saving 모드 (Critic gpt-4o → gpt-4o-mini)
  ≥ 100% → 신규 LLM endpoint 호출 차단 (E-RL-001). 조회는 가능.
```

월 비용은 도달 시 즉시 차단 (cost_saving fallback 없음 — 운영 보호).

### 7.2 누적 계산 방식

```
- LLM 호출마다 agent_io_logs.cost_usd 기록
- 일일 누적: WHERE user_id = ? AND created_at >= today_utc_start
- 월 누적: WHERE user_id = ? AND created_at >= month_start_utc
- Redis cache: rl:cost:{user_id}:{YYYYMMDD} = 누적 cost (TTL 25h)
- 5분마다 DB와 sync (cache miss 시 DB SUM 후 cache write)
```

---

## 8. 부정 사용 감지

본 contract는 패턴만 정의. 실제 자동 차단은 `llm_security_contract.md` §7과 협력.

### 8.1 패턴

```
1. 동일 user_id + 동일 endpoint + 동일 body hash 1분 내 10회 → 자동 1분 차단
   (무한 루프 / 자동화 의심)
2. 동일 IP에서 5분 내 신규 user_id 가입 3회 이상 → IP 1시간 차단
3. 동일 user_id가 동시에 5개 이상 IP에서 호출 → E-SEC-007 큐 (계정 도용 의심)
4. anonymous에서 login 실패 30회 / 1시간 → IP 24시간 차단 + 운영자 알림
5. generate 호출 후 동일 plan_id에 대해 cancel/restart 10회 / 1시간 → 1시간 차단
```

### 8.2 차단 정책

```
- 1분 차단: 자동 해제. 사용자에게 wait 안내.
- 1시간 차단: 자동 해제. user_message에 "잠시 후 다시 시도해주세요" + Slack #ops-alert.
- 24시간 차단: 자동 해제. user_action: contact_support 안내.
- E-SEC-007 큐: 운영자 검토 후 수동 해제. 계정 동결 가능.
```

### 8.3 메트릭

```
일/주 단위 집계 (meta/security_metrics.md 연동):
- 자동 차단 발생 건수 (패턴별)
- 평균 차단 지속 시간
- 차단 해제 후 같은 user의 재발 빈도
- false positive 추정 (사용자 문의 통계)
```

---

## 9. 정책 변경 / 갱신 절차

```
1. 임계치 인상/인하 또는 새 endpoint 추가 시:
   a. 본 contract PR 작성 → contract-change Skill 절차 통과
   b. 변경 사항을 PROJECT_STATE.md의 "최근 변경" 섹션에 기록
   c. 사용자에게 24시간 사전 공지:
      - 인앱 배너 (변경일 48시간 전부터)
      - 이메일 (인상은 7일 전, 인하는 24시간 전)
   d. 변경 적용 후 1주일은 staging 환경에서 추적 (운영자 콘솔)

2. 긴급 인하 (보안 사고로 인한 quota 강제 인하):
   - 사전 공지 면제. 적용 후 24시간 내 사용자에게 사후 공지.
   - meta/retrospectives/{YYYY-MM-DD}_quota_emergency.md 작성

3. 자동 조정 (학습 기반, Phase 11+):
   - 사용자 패턴 변화에 따라 임계치 자동 ±10% 조정 검토
   - 단 자동 조정 결과는 항상 contract-change 절차로 승격되어야 함
```

---

## 10. tier 분류 hook

```
요청 진입 시 server-side가 다음 순서로 tier 결정:

1. X-Internal-Bot 헤더 + IP allowlist 매칭 → internal
2. JWT 검증 성공 + user_profiles.subscription_tier == 'paid' → paid (Phase 11+)
3. JWT 검증 성공 + 그 외 → free
4. JWT 없거나 검증 실패 → anonymous

결정된 tier는 X-Tier 응답 헤더로 echo (내부 디버깅용. production은 비공개 옵션).
```

---

## 11. Cross-reference 빠른 표

| 정책 | 정의 위치 | 참조처 |
|---|---|---|
| 응답 헤더 형식 | 본 contract §5 | api_contract §3.2 |
| HTTP 429 envelope | error_response §3 | 본 contract §6 |
| E-RL-* 코드 | error_response §4.5 | 본 contract §6.1 |
| 호출당 비용 상한 | agent_io §9.1 | 본 contract §7 |
| 세션당 비용 상한 | agent_io §9.2 | 본 contract §7 |
| 일일 비용 상한 | agent_io §9.3 | 본 contract §7 |
| 보안 반복 차단 | llm_security §7 | 본 contract §8 |
| 모델 폴백 트리거 | cost_control_policy.md | 본 contract §7.1 |

---

## 12. 확장 가능성 (Phase 7+ / Phase 11+)

```
Phase 7+:
- per-organization quota (현재 per-user)
- region별 분기 (KR/JP/US) — 다국가 진입 시
- WAF / Cloudflare Rate Limiting 통합 (DDoS 방어)

Phase 11+ (paid tier 진입):
- credit-based quota (호출 횟수 외에 credit 소비)
- custom tier (enterprise client별 협상)
- spike absorption (정상 사용자 burst 흡수 buffer 5분)

Phase 21+:
- 멀티 region active-active (Redis cluster sharding)
- GraphQL endpoint별 cost 계산 (Phase 21+ GraphQL 도입 시)
```

---

## 13. Open Questions

1. sliding vs fixed window의 endpoint별 분배 — 현재는 가이드만, Phase 1 endpoint
   구현 시점에 endpoint마다 확정 필요.
2. Redis 단일 인스턴스 vs sharding — 초기 사용자 1만 이하면 단일로 충분.
3. 일일 비용 quota 도달 시 cost_saving 자동 전환 vs 명시적 사용자 안내 — UX 측정.
4. anonymous tier가 intent/check를 호출할 수 있게 한 것이 보안 위험인지 — 추후 측정.
5. paid tier의 정확한 한도 (Phase 11+) — 비용 분석 후 확정.
6. 부정 사용 패턴(§8)의 임계치 — false positive 측정 후 조정.
7. internal tier의 IP allowlist 관리 (환경변수 vs 별도 admin UI).

---

## 14. 변경 이력

```
v1.0.0 (2026-05-26): Sprint S3-3 초안. 4 tier × endpoint × window 매트릭스,
                      sliding/fixed/token bucket 정책, 응답 헤더 표준,
                      비용 quota (일/월), 부정 사용 감지 패턴, 정책 변경 절차.
```
