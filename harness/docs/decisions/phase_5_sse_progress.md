# ADR-022 — Phase 5 SSE Progress (D7)

> Date: 2026-05-29
> Status: Accepted
> Phase: 5 Slice 4
> Related: 확정 결정 [10] (30-60초 progress + 부분 결과), security-review §T4 (SSE hijacking MEDIUM), V4 (SSE 정책)

---

## Context

확정 결정 [10] (PROJECT_STATE) 는 30~60초 plan 생성 대기 동안 사용자 이탈을
방지하기 위해 부분 결과 / progress 노출을 의무화한다. design.md §22
(Generation Progress) 도 정합한다.

또한 security-review §T4 는 SSE 도입이 새로운 위협 surface 임을 지적한다:
- Origin 미검증 시 다른 도메인이 SSE 스트림 hijack.
- 토큰 전송 경로 — EventSource 는 표준 Authorization 헤더 X.
- partial event payload 의 PII / XSS sanitize.

## Decision

### 1. 전송 방식: SSE (Server-Sent Events) 채택

- vs WebSocket: SSE 가 충분 (단방향 server → client). WebSocket 의 양방향성은
  본 progress 시나리오에 불필요.
- 표준 `EventSource` API (브라우저 내장) + HTTP/1.1 keep-alive.
- 인프라 단순 (HTTP 응답으로 처리, WebSocket 별도 protocol 불요).

### 2. 4 단계 progress

- `intent`   (step 1) — duration_estimate_sec 5
- `rag`      (step 2) — duration_estimate_sec 10
- `planning` (step 3) — duration_estimate_sec 30 (3-plan parallel)
- `critic`   (step 4) — duration_estimate_sec 15 (revise 포함 가능)

종료: `complete` 이벤트 (step=4).

### 3. Event schema

```json
{
  "type": "progress" | "complete" | "error",
  "step": 1-4,
  "name": "intent" | "rag" | "planning" | "critic",  // progress 만
  "message": "string",
  "plan_id": "uuid",
  "duration_estimate_sec": 5-30,  // optional, progress 만
  "payload": {...}                // optional, 부분 결과 (Phase 6+ worker 연동)
}
```

SSE wire 포맷: `data: <json>\n\n`.

### 4. 보안 (security-review §T4 권장 적용)

- **Origin 화이트리스트**: `ALLOWED_ORIGINS` set (localhost:3000/3001 + production
  도메인). 외부 origin → 403 origin_not_allowed.
- **인증**: cookie 기반 (Slice 3 baseline). EventSource `withCredentials: true` →
  httpOnly `sb_access_token` 자동 동반.
- **Origin 없음 (curl / server-to-server)**: dev 편의 허용 (production 환경은
  reverse proxy 가 Origin 강제 가능).
- **heartbeat**: SSE 자체 keepalive + EventSource 자동 재연결 (브라우저 표준).
- **rate limit**: user 당 SSE 동시 연결 수 제한은 Phase 11+ 운영 정책.
- **payload sanitize**: 부분 결과는 Phase 6+ worker 와 연동 시 PII / XSS sanitize
  (llm_security_contract §3.4 + §4.5 정합) — baseline 유지.

### 5. Frontend wrapper

- `apps/web/lib/sse.ts` 신규: `subscribeToPlanProgress(planId, onEvent, onError)`.
- `complete` 수신 시 자동 close.
- onerror 시 caller 통지 + EventSource 자체 재연결.

### 6. UI 통합

- `apps/web/app/plan/[plan_id]/page.tsx` 에 Progress section 추가.
- **PlanCard.tsx 무수정** ★ — Progress UI 는 PlanCard 외부 wrapper (aria-live=polite).

## Implementation impact

- backend: `routers/sse.py` 신규 + `main.py` 1 줄 router 등록.
- frontend: `lib/sse.ts` 신규 + `app/plan/[plan_id]/page.tsx` 약 20 줄 (useEffect + UI section).
- tests: `tests/test_sse.py` 4 케이스 (content-type + 5 이벤트 + schema + Origin 차단).

## Trade-offs

- **SSE 는 단방향**: client → server 양방향 메시지 필요 시 WebSocket (Phase 21+).
- **HTTP/1.1 keep-alive 제한**: HTTP/2 멀티플렉싱 미지원 환경에서 연결 수 ↑.
- **프록시 / CDN buffering**: `X-Accel-Buffering: no` 헤더로 nginx 완화. Cloudflare
  등 CDN 도입 시 별도 검증 필요 (Phase 11+).
- **mock progress**: 본 Slice 4 baseline 은 4 단계를 즉시 emit 한다. 실 worker 와
  동기화는 Phase 6+ orchestration 도입 시 본격화.

## Alternatives considered

- **a) Long polling**: 구현 단순하지만 latency + 서버 부하 → 거절.
- **b) WebSocket**: 양방향 불필요 + 인프라 복잡 (별도 protocol) → 거절.
- **c) JS polling /api/v1/plans/{id}**: REST 호출 반복 → 부분 결과 표현 어려움 + 부하 → 거절.
- **d) Push 전용 메시지 큐 (Pusher 등)**: 외부 SaaS 의존 + 비용 → MVP 외 → 거절.

선택: SSE + EventSource 표준.

## References

- 확정 결정 [10] (PROJECT_STATE.md)
- `apps/web/design.md` §22 (Generation Progress)
- `meta/security_reviews/2026-05-29_phase-5-auth-rls.md` §3 T4
- `meta/validations/2026-05-29_phase-5-pre-entry_self.md` §V4
- `backend/fastapi/routers/sse.py` (본 ADR 의 구현)
- `apps/web/lib/sse.ts` (frontend wrapper)
- `apps/web/app/plan/[plan_id]/page.tsx` (UI 통합)
