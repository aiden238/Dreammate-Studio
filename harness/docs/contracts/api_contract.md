# api_contract.md — 영상기획 AI 에이전트 REST API Contract

> 위치: `docs/contracts/api_contract.md`
> 상태: Phase 0–1 진입용 핵심 contract 초안
> 참조: `docs/contracts/output_schema.md` (envelope + body 스키마)
> 참조: `docs/contracts/agent_io_contract.md` (LLM 호출 비용/timeout)
> 참조: `docs/contracts/error_response_contract.md` (에러 응답)
> 참조: `docs/contracts/db_schema.md` (4계층 데이터 모델)
> 참조: `docs/contracts/rate_limit_policy.md` (S3-3에서 완성)
> 참조: `docs/contracts/llm_security_contract.md` (S3-3에서 완성)

---

## 0. 이 문서의 위치

이 문서는 영상기획 AI 에이전트 플랫폼이 클라이언트(Next.js PWA)와 외부 시스템에 노출하는 **RESTful HTTP API**의 endpoint 명세를 고정한다.

이 문서가 정의하는 대상:

1. MVP 9개 핵심 endpoint + 보조 endpoint
2. 인증 / 권한 / 세션 관리
3. 요청/응답 envelope 형식 (성공 시 ok=true, 실패 시 error_response_contract)
4. HTTP status ↔ error.code 매핑
5. 페이지네이션 / 정렬 / 필터 표준
6. WebSocket / SSE 채널 (progress stepper용)
7. 4계층 데이터 모델 검증 순서
8. API 버전 관리 / CORS
9. 응답 latency 목표 + progress stepper 강제 구간

이 문서가 정의하지 않는 대상 (별도 contract):

- LLM 내부 IO → `agent_io_contract.md`
- LLM 출력 본문 구조 → `output_schema.md`
- DB 스키마 → `db_schema.md`
- 에러 코드 사전 → `error_response_contract.md`
- rate limit 임계치 → `rate_limit_policy.md` (S3-3)

---

## 1. 설계 원칙

```
1. 모든 endpoint는 RESTful + JSON. multipart는 Phase 2+에서.
2. 모든 응답은 envelope: ok=true이면 data 객체, ok=false이면 error 객체 (+ 옵셔널 partial_result).
3. 모든 요청에 Authorization: Bearer <jwt> 필수 (Login/Refresh 제외).
4. 모든 요청에 X-Request-ID (uuid v4) 필수. 없으면 server가 생성 + 응답 헤더로 echo back.
5. 4계층 참조 무결성: Brand 없이 Domain 생성 금지, Domain 없이 Series 생성 금지 (server 검증).
6. 30s 이상 소요 endpoint는 SSE 또는 polling 권장. blocking call 금지.
7. POST는 idempotency-key 헤더 지원 (옵셔널, 중복 클릭 방어).
8. 모든 path는 /api/v1/ prefix. major bump 시 /api/v2/ 신규 생성 (deprecation 6개월).
9. CORS: 명시된 origin allowlist만 (production: dreammate.app, *.dreammate.app).
10. 응답 시간 목표: p95 < 500ms (조회), p95 < 60s (생성 endpoint는 진행률 노출 필수).
```

---

## 2. 공통 응답 envelope

### 2.1 성공 envelope

```json
{
  "ok": true,
  "data": { /* endpoint별 본문 */ },
  "meta": {
    "request_id": "uuid",
    "responded_at": "ISO8601",
    "schema_version": "1.0.0"
  }
}
```

### 2.2 실패 envelope

`error_response_contract.md` §3.1 그대로 사용.

```json
{
  "ok": false,
  "error": {
    "code": "E-INV-001",
    "category": "input_validation",
    "message": "missing required field: brand_name",
    "user_message": "필수 정보가 빠졌어요. 다시 확인해주세요.",
    "user_action": "reframe_input",
    "retryable": false,
    "request_id": "uuid",
    "trace_id": "string",
    "occurred_at": "ISO8601",
    "context": { "field": "brand_name" }
  },
  "partial_result": null
}
```

### 2.3 페이지네이션 envelope (목록 endpoint 공통)

```json
{
  "ok": true,
  "data": {
    "items": [],
    "pagination": {
      "cursor_next": "string | null",
      "cursor_prev": "string | null",
      "has_more": true,
      "page_size": 20
    }
  },
  "meta": { "...": "..." }
}
```

커서는 server-generated opaque token (uuid + timestamp 조합 base64). 클라이언트가 해석 금지.

---

## 3. 공통 헤더

### 3.1 요청 헤더 표준

| 헤더 | 필수 | 설명 |
|---|---|---|
| `Authorization` | yes (auth 제외) | `Bearer <supabase_jwt>` |
| `X-Request-ID` | yes | uuid v4. 클라이언트 생성. 없으면 server가 생성. |
| `X-Client-Version` | yes | `web@0.1.0`, `expo@0.1.0` 등. SemVer 형식. |
| `X-Idempotency-Key` | no | POST 중복 방어. uuid v4. 5분 유지. |
| `Content-Type` | yes | `application/json; charset=utf-8` |
| `Accept-Language` | no | `ko-KR` 기본. Phase 2+에서 다국어 분기. |

### 3.2 응답 헤더 표준

| 헤더 | 설명 |
|---|---|
| `X-Request-ID` | 요청의 uuid echo back. 디버깅 추적용. |
| `X-Trace-ID` | server↔LLM↔DB chain trace. 운영자 검색 키. |
| `X-RateLimit-Limit` | 현재 quota window 상한. |
| `X-RateLimit-Remaining` | 남은 호출 수. |
| `X-RateLimit-Reset` | quota 리셋 시각 (unix sec). |
| `Cache-Control` | 조회 endpoint는 `private, max-age=30`. 생성/변경은 `no-store`. |

---

## 4. 인증 (Auth)

### 4.1 POST /api/v1/auth/login

Supabase Auth 위임 처리. 이 endpoint는 Supabase JS SDK 직접 호출이 권장이지만, 서버 라우팅이 필요한 경우 proxy.

**요청 헤더:**
```
Content-Type: application/json
X-Request-ID: <uuid>
X-Client-Version: web@0.1.0
```

**요청 바디:**
```json
{
  "method": "email_password | oauth_google | oauth_github",
  "email": "string | null",
  "password": "string | null",
  "oauth_redirect_url": "string | null"
}
```

**응답 바디 (성공):**
```json
{
  "ok": true,
  "data": {
    "user": {
      "user_id": "uuid",
      "email": "string",
      "display_name": "string",
      "onboarding_state": "pending | brand_created | first_plan_done"
    },
    "session": {
      "access_token": "string (JWT)",
      "refresh_token": "string",
      "expires_at": "ISO8601"
    }
  },
  "meta": { "...": "..." }
}
```

**Status ↔ error.code 매핑:**

| HTTP | error.code | 의미 |
|---|---|---|
| 200 | — | 성공 |
| 400 | E-INV-001 ~ E-INV-008 | 필드 검증 실패 |
| 401 | E-INV-007 | 비밀번호/토큰 불일치 |
| 429 | E-RL-004 | IP rate limit |
| 500 | E-UNK-001 | server error |
| 503 | E-DB-001 | Supabase 장애 |

**Rate limit:** IP당 분당 10회 (rate_limit_policy.md §3 IP 기준 — S3-3에서 완성).

---

### 4.2 POST /api/v1/auth/logout

**요청 헤더:** `Authorization: Bearer <jwt>` 필수.
**요청 바디:** `{}`
**응답:** `{ "ok": true, "data": { "logged_out_at": "ISO8601" } }`

서버 측 세션 무효화 + 클라이언트에서 토큰 폐기.

---

### 4.3 POST /api/v1/auth/refresh

리프레시 토큰으로 새 access_token 발급.

**요청 바디:**
```json
{ "refresh_token": "string" }
```

**응답 바디:**
```json
{
  "ok": true,
  "data": {
    "access_token": "string",
    "expires_at": "ISO8601"
  }
}
```

**Status:** 200, 401 (E-INV-007 토큰 만료/위조), 429.

---

## 5. Brand CRUD

### 5.1 GET /api/v1/brands

현재 사용자의 Brand 목록.

**Query parameters:**
- `cursor` (string, opaque, 옵셔널)
- `page_size` (int, 1–50, default 20)
- `include_deleted` (bool, default false)

**응답 바디:**
```json
{
  "ok": true,
  "data": {
    "items": [
      {
        "brand_id": "uuid",
        "name": "string",
        "short_idea": "string",
        "direction_label": "string | null",
        "tone": {},
        "target_summary": "string | null",
        "is_test_brand": false,
        "created_at": "ISO8601",
        "updated_at": "ISO8601",
        "domain_count": 3,
        "video_count": 12
      }
    ],
    "pagination": { "...": "..." }
  }
}
```

**Status:** 200, 401, 429, 503.

`Cache-Control: private, max-age=30`

---

### 5.2 POST /api/v1/brands

**요청 바디:**
```json
{
  "name": "string (1–40자, 사용자 안에서 unique)",
  "short_idea": "string (≤200자) | null",
  "direction_label": "string | null",
  "tone": { "primary": "string", "avoid": ["string"] }
}
```

**응답 바디 (201):**
```json
{
  "ok": true,
  "data": {
    "brand_id": "uuid",
    "name": "string",
    "short_idea": "string | null",
    "direction_label": "string | null",
    "tone": {},
    "is_test_brand": false,
    "created_at": "ISO8601",
    "updated_at": "ISO8601"
  }
}
```

**Status ↔ error.code:**

| HTTP | error.code |
|---|---|
| 201 | — |
| 400 | E-INV-001 ~ E-INV-004 |
| 401 | E-INV-007 |
| 409 | E-INV-005 (동일 이름) / E-DB-002 |
| 429 | E-RL-002 |
| 500/503 | E-UNK-001 / E-DB-001 |

---

### 5.3 GET /api/v1/brands/{brand_id}

단일 Brand 상세 + brand_memory_entries 요약.

**응답 바디:**
```json
{
  "ok": true,
  "data": {
    "brand_id": "uuid",
    "name": "string",
    "short_idea": "string | null",
    "direction_label": "string | null",
    "tone": {},
    "target_summary": "string | null",
    "brand_memory_summary": {
      "preferred_phrases_count": 5,
      "avoid_phrases_count": 3,
      "preferred_tone": "현실적·솔직형",
      "success_patterns_count": 2,
      "rejection_patterns_count": 1
    },
    "created_at": "ISO8601",
    "updated_at": "ISO8601"
  }
}
```

**Status:** 200, 401, 403 (E-INV-007 RLS), 404, 500, 503.

---

### 5.4 PATCH /api/v1/brands/{brand_id}

Brand 정보 수정. 부분 업데이트.

**요청 바디 (모든 필드 옵셔널):**
```json
{
  "name": "string",
  "direction_label": "string",
  "tone": {},
  "target_summary": "string"
}
```

---

### 5.5 DELETE /api/v1/brands/{brand_id}

Soft delete (deleted_at 채움).

**응답:** 204 No Content.

---

## 6. Domain CRUD

### 6.1 GET /api/v1/domains

**Query parameters:**
- `brand_id` (uuid, **필수** — 4계층 검증)
- `cursor`, `page_size`

`brand_id` 누락 시 400 E-INV-001.

**응답 바디:**
```json
{
  "ok": true,
  "data": {
    "items": [
      {
        "domain_id": "uuid",
        "brand_id": "uuid",
        "name": "string",
        "description": "string | null",
        "created_at": "ISO8601",
        "series_count": 4
      }
    ],
    "pagination": { "...": "..." }
  }
}
```

---

### 6.2 POST /api/v1/domains

**요청 바디:**
```json
{
  "brand_id": "uuid",
  "name": "string (1–40자, brand 안에서 unique)",
  "description": "string | null"
}
```

**4계층 검증:**
- `brand_id` 존재 + 현재 user 소유 → 아니면 E-INV-006 또는 E-INV-007
- 동일 brand_id 안에 동일 name 존재 시 E-INV-005

**Status:** 201, 400, 401, 403, 404 (brand 없음), 409, 429.

---

### 6.3 GET /api/v1/domains/{domain_id}

### 6.4 PATCH /api/v1/domains/{domain_id}

### 6.5 DELETE /api/v1/domains/{domain_id}

(Brand와 동일 패턴)

---

## 7. Series CRUD

### 7.1 GET /api/v1/series

**Query parameters:** `domain_id` (uuid, **필수**).

**응답 바디:**
```json
{
  "ok": true,
  "data": {
    "items": [
      {
        "series_id": "uuid",
        "domain_id": "uuid",
        "name": "string",
        "structure_type": "growth_record | experiment | community | review | informational | narrative | event_based | other",
        "description": "string | null",
        "cadence_hint": "string | null",
        "created_at": "ISO8601",
        "video_count": 7
      }
    ],
    "pagination": { "...": "..." }
  }
}
```

`structure_type` enum → `output_schema.md` §18.

---

### 7.2 POST /api/v1/series

**요청 바디:**
```json
{
  "domain_id": "uuid",
  "name": "string (1–60자)",
  "structure_type": "growth_record | ...",
  "description": "string | null",
  "cadence_hint": "string | null"
}
```

**4계층 검증:**
- `domain_id` → 그 domain의 `brand_id` → 현재 user 소유 여부 (2단계 join 검증)
- 동일 domain 안에 동일 name 존재 시 E-INV-005

---

### 7.3–7.5 GET/PATCH/DELETE /api/v1/series/{series_id}

---

## 8. Plan 생성 흐름 (핵심 9 endpoint 중 5개)

영상기획 세션 1개 = `video_project` 1개. 아래 endpoint들은 모두 같은 `plan_id` (= `video_id`)를 공유한다.

### 8.1 POST /api/v1/plans/start

새 영상기획 세션 시작. Discovery/Quick 자동 분기.

**요청 헤더:** `X-Idempotency-Key` 권장 (중복 클릭 방어).

**요청 바디:**
```json
{
  "series_id": "uuid | null",
  "short_idea": "string (≤200자)",
  "title": "string (1–60자) | null",
  "mode_hint": "auto | discovery | quick"
}
```

**Mode 분기 로직 (server-side):**
- `series_id` 제공 → Quick Mode 진입 (Brand+Domain+Series 컨텍스트 상속)
- `series_id` null + user에게 Brand 없음 → Discovery (Brand 단계부터)
- `series_id` null + Brand 있고 Domain 없음 → Discovery (Domain 단계부터)
- 자세한 분기 규칙 → `design.md` §5 mode trigger rules

**응답 바디 (201):**
```json
{
  "ok": true,
  "data": {
    "plan_id": "uuid",
    "video_id": "uuid (== plan_id, alias)",
    "mode": "discovery | quick",
    "current_step": "intent_filter | brand_card | domain_card | series_card | target_tone_card | direction_summary | quick_prompt",
    "inherited_context": {
      "brand_id": "uuid | null",
      "domain_id": "uuid | null",
      "series_id": "uuid | null"
    },
    "next_endpoint": "POST /api/v1/plans/{plan_id}/step",
    "status": "draft"
  }
}
```

**Status:** 201, 400 (E-INV-001/002), 401, 403, 404 (series_id가 user의 것이 아님), 429.

---

### 8.2 POST /api/v1/plans/{plan_id}/step

Discovery 5단계 진행. 각 호출이 1단계 카드 생성.

**요청 바디:**
```json
{
  "current_step": "intent_filter | brand_card | domain_card | series_card | target_tone_card | direction_summary",
  "user_input": "string | null",
  "previous_selection": {
    "step_name": "string",
    "selected_card": { "card_id": "uuid", "name": "string", "...": "..." },
    "direct_input": "string | null",
    "rejection_reasons": { "0": "이유1", "1": "이유2" }
  }
}
```

`previous_selection`은 첫 단계가 아닌 경우 필수. 사용자가 이전 단계에서 선택한 카드(또는 direct_input)를 누적해서 보낸다. server는 이를 `discovery_choices`에 INSERT.

**응답 바디:**

`output_schema.md`의 envelope를 그대로 따른다. step에 따라 body가 달라진다:

| current_step | response.data | output_schema 참조 |
|---|---|---|
| intent_filter | P-AUX-1 body | §11 |
| brand_card | P-001 body (cards[] + user_input_slot) | §3 |
| domain_card | P-002 body | §4 |
| series_card | P-003 body | §5 |
| target_tone_card | P-004 body (target_cards + tone_cards) | §6 |
| direction_summary | P-005 body (one_line + components) | §7 |

응답에 추가되는 메타:

```json
{
  "ok": true,
  "data": {
    "envelope": { /* output_schema envelope 전체 */ },
    "step": {
      "completed": "domain_card",
      "next": "series_card | direction_summary | null",
      "progress": { "current": 3, "total": 6 }
    }
  }
}
```

**Status:** 200, 400, 401, 403, 404 (plan_id 없음 또는 권한 없음), 429, 502 (LLM 실패 → E-LLM-*), 500.

**Latency 목표:**
- intent_filter: p95 < 5s
- brand_card / domain_card / series_card / target_tone_card: p95 < 30s
- direction_summary: p95 < 20s

30s 초과 시 SSE 권장 (§13 참조).

---

### 8.3 POST /api/v1/plans/{plan_id}/generate

3개 기획안 생성 (P-006 Planner Agent).

**요청 바디:**
```json
{
  "approved_direction": "string (P-005 one_line, 사용자가 수정했을 수 있음)",
  "approved_components": {
    "target": "string",
    "message": "string",
    "format": "shorts_30s | ...",
    "length_sec": 30
  },
  "use_rag": true,
  "use_critic": true,
  "use_rewriter": false,
  "cost_mode": "standard | cost_saving"
}
```

**응답 바디:**

생성 시작 응답 (즉시 반환):

```json
{
  "ok": true,
  "data": {
    "plan_id": "uuid",
    "generation_id": "uuid (이 generate 호출의 trace)",
    "status": "generating",
    "estimated_duration_sec": 45,
    "progress_channel": {
      "type": "sse",
      "url": "/api/v1/plans/{plan_id}/progress?gen_id={generation_id}"
    }
  }
}
```

이후 progress는 SSE (§13)로 streaming. 최종 결과는 GET /api/v1/plans/{plan_id}로 조회.

또는 progress_channel이 polling인 경우:

```json
{
  "progress_channel": {
    "type": "polling",
    "url": "/api/v1/plans/{plan_id}/status",
    "interval_sec": 2
  }
}
```

**최종 결과 (GET /api/v1/plans/{plan_id}에서 조회 시):**
```json
{
  "ok": true,
  "data": {
    "plan_id": "uuid",
    "status": "plans_ready",
    "plan_candidates": [
      { /* P-006 plan 1개, output_schema §8 */ },
      { /* plan 2 */ },
      { /* plan 3 */ }
    ],
    "critic_evaluation": { /* output_schema §9 canonical (Phase 6 ADR-018: overall_score + dimensions) */ },
    "revise_history": [
      /* output_schema §9-A.1: plan_candidates 순서 외부 list, attempt 순차 내부 list */
      [ { "attempt": 0, "action": "revise", "revised": true }, { "attempt": 1, "action": "approve", "revised": false } ]
    ],
    "recommended_plan_index": 1, /* output_schema §9-A.2 (Phase 4.5 ADR-017): Critic best-plan idx or null */
    "rag_references": [ /* rag_used 통합 */ ]
  }
}
```

**Phase 4.5+6 응답 필드** (output_schema.md 정합):

| 필드 | 출처 | 비고 |
|---|---|---|
| `critic_evaluation` | output_schema §9 | Phase 6 canonical (overall_score + dimensions). deprecated 필드 (overall_score_avg / scores) Optional 호환 |
| `revise_history` | output_schema §9-A.1 (Phase 4.5 ADR-016) | plan별 revise loop attempt log (max 2회) |
| `recommended_plan_index` | output_schema §9-A.2 (Phase 4.5 ADR-017 Z-X3) | Critic best-plan idx (null = critic skip / all invalid) |

레거시 응답 (Phase 4.5 이전) 에서는 `quality_scores: [...]` 키를 사용했으나 Phase 6 부터는 `critic_evaluation` 단일 객체로 통합 (output_schema §9 정합).

**Status:** 200 (생성 시작 ack), 400, 401, 403, 404, 422 (E-INV-006 4계층 검증 실패), 429 (E-RL-001 비용 한도), 502 (E-LLM-*), 503.

**Latency:** generate 호출 자체는 p95 < 500ms (즉시 ack). 실제 생성은 30~60s (progress stepper 필수).

**비용 추적:** `agent_io_logs`에 누적. 세션당 상한 초과 시 E-RL-001 → `agent_io_contract.md` §9 참조.

---

### 8.4 POST /api/v1/plans/{plan_id}/select

3개 plan 중 1개 선택 + 선택 이유 저장.

**요청 바디:**
```json
{
  "selected_option_id": "uuid (plan_candidates.option_id)",
  "selection_reason": "string (≤200자) | null"
}
```

**응답 바디:**
```json
{
  "ok": true,
  "data": {
    "plan_id": "uuid",
    "selected_option_id": "uuid",
    "selected_at": "ISO8601",
    "status": "plan_selected",
    "next_endpoint": "POST /api/v1/plans/{plan_id}/feedback (옵셔널) | GET /api/v1/plans/{plan_id} (final 조회)"
  }
}
```

**DB 영향:**
- `selected_plans` INSERT
- `video_projects.status` = `plan_selected`
- `feedback_events` INSERT (event_type=`like`, target=선택된 option_id)
- 거절된 2개 option에 대해 `feedback_events` (event_type=`reject`) INSERT — `previous_selection.rejection_reasons` 활용

**Status:** 200, 400, 401, 403, 404, 409 (이미 선택됨 — E-DB-003).

---

### 8.5 POST /api/v1/plans/{plan_id}/feedback

피드백 저장 + Brand Memory 추출 (P-AUX-2 백그라운드 트리거).

**요청 바디:**
```json
{
  "target_kind": "plan_option | final | revision",
  "target_id": "uuid",
  "event_type": "like | dislike | reject | regenerate",
  "reason": "string (≤300자) | null",
  "trigger_memory_extraction": true
}
```

**응답 바디:**
```json
{
  "ok": true,
  "data": {
    "feedback_id": "uuid",
    "memory_extraction_queued": true,
    "memory_extraction_job_id": "uuid | null"
  }
}
```

`trigger_memory_extraction=true`이면 P-AUX-2를 백그라운드 큐에 enqueue. 응답은 즉시 반환. 사용자는 이 작업의 결과를 다음 세션 진입 시 "이거 추가할까요?" UI로 확인 (`brand_memory_entries` pending queue).

**Status:** 201, 400, 401, 403, 404, 429.

---

### 8.6 브랜딩 세션 (Akinator 주제발굴) — Phase 18 (CC-023)

주제 미정 사용자를 **LLM 동적 스무고개**로 좁혀 후보 주제 3개 + 브랜딩 방향(톤/타깃/포맷)을 제안. `/plans/start` 로 plan_id 발급 후 진행. 상태는 `wizard_data.branding`(history+candidates+selected) 누적. auth-optional(Q&A); brand_memory 시드는 authed + gated(`branding_pkm_seed_enabled`).

- **POST /api/v1/plans/{plan_id}/branding/next** — body `{answer?, selected_option?}` → `{mode:"ask"|"done", question, options(2~4)|null, step, max_questions}`. 직전 답변 기록 + 다음 적응형 질문(또는 done, MAX_QUESTIONS=8 상한). agent **P-AUX-3** ask.
- **POST /api/v1/plans/{plan_id}/branding/finalize** — → `{candidates:[{topic,tone,target,format,why_fit} ×3]}`. agent **P-AUX-3** finalize.
- **POST /api/v1/plans/{plan_id}/branding/select** — body `{topic, tone?, target?, format?}` → `{ok, seeded}`. 택1 저장(`initial_input` 설정 → 후속 generate 연결) + (gated+authed) brand_memory 시드(tone→preferred_tone 등, conf 0.9, dedup, Phase 17 재사용).

**Status:** 200, 404(INV-006). graceful — agent/seed 실패 시 500 금지(ask→done / finalize→[] / select→seeded 0). flag OFF·익명 → 시드 0(byte-identical, selected/initial_input은 저장).

---

## 9. Plan 조회 endpoint

### 9.1 GET /api/v1/plans/{plan_id}

전체 상태 조회. 진행 중이든 완료든.

**Query parameters:**
- `include` (comma-separated): `plan_candidates,quality_scores,selected,final,feedback,memory_proposals`
  - 기본값: `plan_candidates,quality_scores,selected`
  - `all` 키워드도 허용 (모든 sub-resource 포함)

**응답 바디:**
```json
{
  "ok": true,
  "data": {
    "plan_id": "uuid",
    "video_id": "uuid",
    "mode": "discovery | quick",
    "status": "draft | generating | plans_ready | plan_selected | final | archived",
    "title": "string",
    "short_idea": "string",
    "one_line_direction": "string | null",
    "context": {
      "brand": { "brand_id": "uuid", "name": "string" },
      "domain": { "domain_id": "uuid", "name": "string" },
      "series": { "series_id": "uuid", "name": "string" }
    },
    "plan_candidates": [ /* P-006 plans, include=plan_candidates일 때 */ ],
    "quality_scores": [ /* P-007 results, include=quality_scores일 때 */ ],
    "selected_plan": { /* selected_plans row, include=selected일 때 */ },
    "final_output": { /* output_schema §17 통합 JSON, include=final일 때 */ },
    "feedback_events": [],
    "memory_proposals": [],
    "created_at": "ISO8601",
    "updated_at": "ISO8601"
  }
}
```

**Status:** 200, 401, 403, 404.

`Cache-Control: private, max-age=10` (생성 중인 plan은 자주 갱신 가능성).

---

### 9.2 GET /api/v1/plans/{plan_id}/status

진행 중 plan의 status만 가볍게 조회 (polling용).

**응답 바디:**
```json
{
  "ok": true,
  "data": {
    "plan_id": "uuid",
    "status": "generating | plans_ready | ...",
    "progress": {
      "stage": "intent | rag | planner | critic | done",
      "percent": 60,
      "current_agent": "critic",
      "completed_count": 2,
      "total_count": 3,
      "started_at": "ISO8601",
      "estimated_finish_at": "ISO8601"
    },
    "partial_result": null
  }
}
```

`partial_result` 구조는 `error_response_contract.md` §7 그대로.

**Latency:** p95 < 200ms. polling 주기 2s.

---

## 10. Intent Check 단독 호출

### 10.1 POST /api/v1/intent/check

P-AUX-1 단독 호출. 사용자가 입력 중 "이거 영상기획 맞아?" 자동 확인.

**요청 바디:**
```json
{
  "user_input": "string (1–500자)",
  "context": {
    "current_page": "string (예: /new/quick)",
    "brand_id": "uuid | null"
  }
}
```

**응답 바디:**

`output_schema.md` §11 P-AUX-1 envelope 그대로.

```json
{
  "ok": true,
  "data": {
    "envelope": {
      "meta": { "...": "..." },
      "body": {
        "decision": "allow | block | reframe_offer",
        "reason": "string",
        "reframe_suggestion": "string | null",
        "matched_categories": ["string"],
        "confidence": 0.78
      },
      "validation": { "...": "..." }
    }
  }
}
```

**Status:** 200, 400, 401, 429.

**Latency:** p95 < 5s (P-AUX-1은 분류만, 빠름).

**Rate limit:** 사용자당 분당 20회 (자동 호출 가능성 고려).

---

## 11. HTTP Status Code ↔ error.code 매핑 표

`error_response_contract.md` §12와 정합.

| HTTP | 의미 | 주로 발생하는 error.code |
|---|---|---|
| 200 | OK | — |
| 201 | Created | — |
| 204 | No Content (DELETE) | — |
| 400 | Bad Request | E-INV-001, E-INV-002, E-INV-003, E-INV-004, E-INV-008 |
| 401 | Unauthorized | E-INV-007 (토큰 없음/만료) |
| 403 | Forbidden | E-INV-007 (RLS), E-SEC-001~007 |
| 404 | Not Found | E-INV-006 (4계층 참조 없음) |
| 409 | Conflict | E-INV-005 (unique 위반), E-DB-002, E-DB-003 |
| 422 | Unprocessable Entity | E-INV-006 (참조 무결성), E-SEC-002~006 |
| 429 | Too Many Requests | E-RL-001~005 |
| 500 | Internal Server Error | E-UNK-001, E-UNK-999 |
| 502 | Bad Gateway | E-LLM-001~010 (외부 LLM 의존) |
| 503 | Service Unavailable | E-DB-001, E-DB-004, E-RAG-001, E-RAG-004 |

**원칙:** 클라이언트는 HTTP status가 아니라 `error.code`로 분기. HTTP status는 게이트웨이/CDN이 변경할 수 있음.

---

## 12. 4계층 데이터 모델 검증

### 12.1 순차 필수 검증

```
Brand 생성     → user_id 인증만 필요
Domain 생성    → brand_id 존재 + user 소유 검증 필수
Series 생성    → domain_id 존재 + 그 domain의 brand_id가 user 소유 검증 필수
Video 생성     → series_id 존재 + 2단계 join 검증 (series → domain → brand → user)
```

server에서 매 endpoint마다 위 검증을 수행한다. 실패 시 E-INV-006 (404 또는 422).

### 12.2 RLS 우회 시도 처리

Supabase RLS는 user_id 기반 자동 필터. 만약 user A가 user B의 brand_id를 query에 넣으면:
- Supabase 쿼리 결과가 빈 행 → server는 404 E-INV-006 응답
- 명시적 user_id 비교가 fail이면 → 403 E-INV-007

### 12.3 4계층 cascade 정책

- `deleted_at` soft delete만 허용
- Brand soft delete → 하위 Domain/Series/Video는 자동 archived 상태로 전환 (deleted_at은 NOT 갱신, 단 status='archived')
- 하위에서 다시 active로 복원하려면 Brand 복원 필요

---

## 13. WebSocket / SSE 채널 (Progress Stepper)

30s 이상 소요 endpoint (`/plans/{plan_id}/generate`)는 SSE 권장.

### 13.1 SSE endpoint

`GET /api/v1/plans/{plan_id}/progress?gen_id={generation_id}`

**응답 헤더:**
```
Content-Type: text/event-stream
Cache-Control: no-store
Connection: keep-alive
```

**이벤트 형식:**

```
event: stage_started
data: {"stage": "rag", "started_at": "2026-05-26T08:30:15Z"}

event: stage_completed
data: {"stage": "rag", "completed_at": "...", "result_summary": {"rag_chunks_used": 3}}

event: partial_result
data: {"plan_index": 0, "plan": { /* P-006 plan 1개 */ }}

event: critic_result
data: {"plan_id": "uuid", "overall_verdict": "approve", "overall_score_avg": 4.1}

event: error
data: {"error": { /* error_response_contract.md envelope */ }, "partial_result": {...}}

event: done
data: {"status": "plans_ready", "final_url": "/api/v1/plans/{plan_id}"}
```

### 13.2 단계 정의 (4단계 stepper)

`error_response_contract.md` §7과 정합.

```
[1] intent   → [2] rag    → [3] planner   → [4] critic   → done
```

각 stage마다 `stage_started` + `stage_completed` 이벤트.

### 13.3 클라이언트 처리

- `partial_result` 이벤트가 도착하면 즉시 UI에 plan 1개 노출 (3개 다 기다리지 않음)
- `error` 이벤트가 도착해도 `partial_result.data`가 있으면 보존 (`continue_partial` 액션 활성화)
- `done` 이벤트 도착 시 GET /api/v1/plans/{plan_id}로 최종 상태 fetch

### 13.4 Fallback: long polling

SSE 미지원 환경(특정 모바일 브라우저, proxy)에서는:
- `GET /api/v1/plans/{plan_id}/status` 2s polling
- 동일 progress 정보 + partial_result 노출

### 13.5 취소

`DELETE /api/v1/plans/{plan_id}/progress?gen_id={generation_id}` — 생성 중인 작업 취소. 부분 결과는 저장됨 (status=`generating_cancelled`).

---

## 14. CORS 정책

### 14.1 Origin allowlist

```
production:
  https://dreammate.app
  https://*.dreammate.app (subdomain wildcards)

staging:
  https://staging.dreammate.app

development:
  http://localhost:3000
  http://localhost:3001
  http://127.0.0.1:3000
```

### 14.2 Allowed headers

```
Authorization, Content-Type, X-Request-ID, X-Client-Version, X-Idempotency-Key, Accept-Language
```

### 14.3 Exposed headers

```
X-Request-ID, X-Trace-ID, X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset
```

### 14.4 Credentials

`Access-Control-Allow-Credentials: true` (refresh token cookie 사용 시).

### 14.5 Preflight cache

`Access-Control-Max-Age: 86400` (24h).

---

## 15. API 버전 관리

### 15.1 path prefix

모든 endpoint는 `/api/v1/` prefix. major bump 시 `/api/v2/` 신규 path 생성.

### 15.2 Deprecation 정책

- v1 deprecation 공지: response 헤더 `Deprecation: true, Sunset: <RFC1123 date>`
- v2 출시 후 v1은 최소 6개월 유지
- 마지막 30일은 응답 헤더에 `Sunset-Warning: <epochsec>` 추가
- API 변경 RFC는 `meta/api_change_proposals/` 폴더 (Phase 11+)

### 15.3 Minor / patch

- minor: 새 endpoint 추가, 새 옵셔널 필드 추가 → 같은 /api/v1/
- patch: 문서/메시지 수정 → 같은 /api/v1/

→ `output_schema.md` §19 semver 규칙과 정합.

---

## 16. Rate Limit

자세한 임계치는 `rate_limit_policy.md` (S3-3에서 완성). 본 contract에서는 형식만 고정.

### 16.1 응답 헤더

모든 응답에 다음 헤더 포함:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 87
X-RateLimit-Reset: 1748246400  (unix sec)
```

### 16.2 초과 시 응답

```json
{
  "ok": false,
  "error": {
    "code": "E-RL-002",
    "category": "rate_limit",
    "user_message": "너무 빠르게 요청하셨어요. 잠시 기다려주세요.",
    "user_action": "wait",
    "retryable": true,
    "retry_after": 30
  }
}
```

HTTP status: 429.

### 16.3 quota window

- IP 기반: 분 단위 sliding window
- User 기반: 시간 단위 + 일 단위 (비용 quota는 일 단위)

→ S3-3 `rate_limit_policy.md`에서 endpoint별 임계치 확정.

---

## 17. Idempotency

POST endpoint 중 다음은 `X-Idempotency-Key` 헤더 지원:

- POST /api/v1/brands
- POST /api/v1/domains
- POST /api/v1/series
- POST /api/v1/plans/start
- POST /api/v1/plans/{plan_id}/select
- POST /api/v1/plans/{plan_id}/feedback

### 17.1 동작

- 같은 idempotency-key로 5분 이내 재호출 시 → 첫 응답 그대로 반환 (재실행 안 함)
- 5분 후 새 키로 인식
- 키 형식: uuid v4 권장 (client 생성)

### 17.2 캐싱

서버는 idempotency cache를 Redis 등에 저장. key = `idem:{user_id}:{key}`, value = 응답 envelope, TTL 5분.

---

## 18. Latency 목표

| Endpoint | p50 | p95 | 진행률 노출 |
|---|---|---|---|
| POST /api/v1/auth/* | 200ms | 800ms | no |
| GET /api/v1/brands | 100ms | 500ms | no |
| POST /api/v1/brands | 200ms | 1s | no |
| GET /api/v1/domains | 100ms | 500ms | no |
| POST /api/v1/domains | 200ms | 1s | no |
| GET/POST /api/v1/series | (Brand 동일) | | |
| POST /api/v1/plans/start | 300ms | 1s | no |
| POST /api/v1/plans/{plan_id}/step | 8s | 30s | **yes (5s+)** |
| POST /api/v1/plans/{plan_id}/generate (ack) | 300ms | 800ms | — |
| POST /api/v1/plans/{plan_id}/generate (실생성, SSE) | 35s | 60s | **yes** |
| GET /api/v1/plans/{plan_id} | 200ms | 600ms | no |
| GET /api/v1/plans/{plan_id}/status | 100ms | 200ms | no |
| POST /api/v1/plans/{plan_id}/select | 300ms | 1s | no |
| POST /api/v1/plans/{plan_id}/feedback | 200ms | 800ms | no |
| POST /api/v1/intent/check | 1s | 5s | no |

### 18.1 진행률 노출 강제 조건

`p95 ≥ 30s`인 endpoint는 다음 중 하나 필수:
- SSE progress channel (권장)
- Polling status endpoint
- 부분 결과 streaming

빈 로딩 스피너 + 30s 대기는 금지 (`design.md` §22).

---

## 19. 예시: 전체 흐름 (Discovery → Final)

### 19.1 시나리오: 신규 사용자가 첫 영상기획 만들기

```
1. POST /api/v1/auth/login                  → 200 + access_token
2. POST /api/v1/plans/start                 → 201 {plan_id, mode: "discovery", current_step: "brand_card"}
3. POST /api/v1/plans/{plan_id}/step
   { current_step: "brand_card", user_input: "창업동아리 활동을 영상으로" }
                                              → 200 + cards[4] (P-001)
4. POST /api/v1/plans/{plan_id}/step
   { current_step: "domain_card",
     previous_selection: { step_name: "brand_card", selected_card: {...} } }
                                              → 200 + cards[4] (P-002)
5. ... (series → target_tone → direction_summary 반복) ...
6. POST /api/v1/plans/{plan_id}/generate
   { approved_direction: "...", approved_components: {...}, use_rag: true, use_critic: true }
                                              → 200 ack + SSE url
7. SSE: stage_started / partial_result / done 이벤트 수신
8. GET /api/v1/plans/{plan_id}?include=plan_candidates,quality_scores
                                              → 200 + plans[3] + scores[3]
9. POST /api/v1/plans/{plan_id}/select
   { selected_option_id: "...", selection_reason: "..." }
                                              → 200
10. POST /api/v1/plans/{plan_id}/feedback
    { target_kind: "plan_option", target_id: "...", event_type: "like",
      trigger_memory_extraction: true }
                                              → 201 + memory_extraction_job_id
11. GET /api/v1/plans/{plan_id}?include=final  → 200 + final_output
```

### 19.2 시나리오: Quick Mode (같은 Series에 새 영상 추가)

```
1. POST /api/v1/plans/start
   { series_id: "<existing>", short_idea: "OT 준비 과정", mode_hint: "quick" }
                                              → 201 {plan_id, mode: "quick"}
2. POST /api/v1/plans/{plan_id}/step
   { current_step: "quick_prompt", user_input: "OT 준비 과정 영상" }
                                              → 200 + P-005q (one_line + missing_info[2])
3. POST /api/v1/plans/{plan_id}/step
   { current_step: "direction_summary", user_input: "<answers>" }
                                              → 200 + P-005 final
4. POST /api/v1/plans/{plan_id}/generate     → SSE
5. (Discovery와 동일)
```

---

## 20. 보안 / 검사 hook (요약)

자세한 정책은 `llm_security_contract.md` (S3-3) 참조.

### 20.1 요청 검사 hook 순서

```
1. JWT 검증 (Supabase)         → 실패 401
2. Rate limit 검사             → 초과 429
3. Body schema 검증            → 실패 400
4. 4계층 무결성 검사            → 실패 422 (E-INV-006)
5. RLS 검증 (Supabase)          → 실패 403
6. user_input 텍스트 검사:
   - PII 패턴 (전화/주민/카드)  → 마스킹 또는 E-SEC-006
   - prompt injection 패턴      → E-SEC-001 (1분 5회 자동 차단)
   - XSS 패턴                   → sanitize 또는 E-SEC-005
7. Idempotency key 검사         → 캐시 hit이면 즉시 응답
8. (정상 처리)
```

### 20.2 응답 검사 hook

```
1. LLM 응답 envelope validation (output_schema §15)
2. 광고 단어 검사 (output_schema §14)
3. PII 마스킹 (응답에 사용자 입력 echo 시)
4. response sanitize (HTML/JS injection 제거)
```

---

## 21. 확장 가능성 (Phase 2+)

```
- WebSocket 양방향 (현재는 SSE 단방향)
- GraphQL endpoint 추가 (현재는 REST 단일)
- multipart upload (이미지 reference, 영상 미리보기) — Phase 5+
- Webhook (third-party 알림, 영상 업로드 연동) — Phase 11+
- Public API (third-party developer access, OAuth scope) — Phase 21+
- Batch endpoint (BFS로 5개 brand 한번에 조회) — 성능 최적화 시점
- LLM streaming token (현재는 chunk 단위) — UX 개선
- multi-locale path (`/api/v1/ko/`, `/api/v1/en/`)
```

---

## 22. Cross-reference 빠른 표

| Endpoint | 본문 스키마 | 에러 코드 | DB 영향 |
|---|---|---|---|
| POST /auth/login | (auth own) | E-INV-007, E-RL-004 | session 발급 |
| GET /brands | brands list | — | brands SELECT |
| POST /brands | brands one | E-INV-005, E-DB-002 | brands INSERT |
| POST /plans/start | mode 분기 + plan_id | E-INV-006 | video_projects INSERT |
| POST /plans/{plan_id}/step | output_schema §3~§7,§11 | E-LLM-* | discovery_choices, agent_io_logs |
| POST /plans/{plan_id}/generate | ack + SSE | E-LLM-*, E-RAG-*, E-RL-001 | plan_candidates ×3, quality_scores |
| POST /plans/{plan_id}/select | selection ack | E-DB-003 | selected_plans, feedback_events |
| POST /plans/{plan_id}/feedback | feedback ack + memory job | — | feedback_events, P-AUX-2 queue |
| POST /intent/check | output_schema §11 | E-LLM-*, E-RL-002 | intent_filter_logs |

---

## 23. Open Questions

1. SSE vs WebSocket 최종 선택 — 모바일 PWA 호환성 검증 후. 현재 SSE 우선.
2. Idempotency-key TTL (현재 5분) — 사용자가 새로고침 → 동일 액션 재시도 패턴 측정 후 조정.
3. polling 주기 (현재 2s) — 비용 vs UX 트레이드오프, partial_result 도착 빈도에 맞춰 조정.
4. GET /api/v1/plans/{plan_id}의 `include=all` 응답 크기 — Phase 2+에서 GraphQL 검토.
5. `previous_selection.rejection_reasons` 강제 여부 — 사용자가 거절만 하고 이유 안 쓰면 학습 데이터 손실.
6. Mode 자동 분기 vs 사용자가 매번 명시 선택 — onboarding A/B 검토.
7. SSE 연결 끊김 후 재연결 정책 (현재 클라이언트 책임) — server-side replay queue 필요 여부.

---

## 24. 변경 이력

```
v1.0.0 (2026-05-26): Sprint S3-2 초안. 9 MVP endpoint 명세, SSE progress channel,
                      4계층 검증, HTTP status 매핑, CORS, idempotency, latency 목표.
```
