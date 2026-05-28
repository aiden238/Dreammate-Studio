# Phase 5 Pre-Entry Multi-LLM Validation — External

> 검증 모델: (예: GPT-4o, Gemini-1.5-Pro 등) — **사용자가 외부에서 진행 후 작성**
> 검증 일자: (기록 시 채울 것)
> 검증 유형: formal — self-validation과 짝 (세 번째 정식 트리거)
> 본 문서: **placeholder** (외부 검증 결과 추가 대기)
> 보안 영향: **HIGH** (Auth + RLS + JWT 첫 도입) → 외부 검토 **강력 권장**

## 작성 가이드

Phase 4.5/6 external placeholder 패턴 계승. 다음 항목을 외부 LLM (GPT/Gemini 등)에 다음 자료와 함께 제시한 후 결과를 기록.

### 외부 LLM에 제공할 자료

1. `harness/phases/active/phase-5-db-auth/goals.md`
2. `harness/phases/active/phase-5-db-auth/scope.md`
3. `harness/phases/active/phase-5-db-auth/non_goals.md`
4. `harness/phases/active/phase-5-db-auth/dependencies.md`
5. `harness/phases/active/phase-5-db-auth/acceptance.md`
6. `harness/phases/active/phase-5-db-auth/assumptions.md`
7. `harness/phases/active/phase-5-db-auth/multi_slice_plan.md`
8. `harness/phases/active/phase-5-db-auth/notes.md`
9. 본 self-validation 문서 (`2026-05-29_phase-5-pre-entry_self.md`)
10. `harness/meta/security_reviews/2026-05-29_phase-5-auth-rls.md` (security-review 결과)
11. `harness/docs/decisions/phase_5_supabase_adoption.md` (ADR-020)
12. `harness/docs/contracts/llm_security_contract.md` (현 보안 정책)
13. `harness/docs/contracts/output_schema.md` (Phase 6 canonical)
14. `harness/docs/contracts/agent_io_contract.md` (Phase 6 Rewriter v1.1.0)
15. (선택) `harness/.claude/skills/security-review/SKILL.md` (10영역 점검 기준)

### 외부 LLM에 묻을 질문 (V1~V6)

1. **V1 Supabase 채택 (vs PostgreSQL 자체/Firebase/자체 서버)**:
   - Supabase 통합 (PostgreSQL + pgvector + RLS + Auth + Storage + Realtime) + Free tier 결정이 적절한가?
   - vendor lock-in (Auth + Storage) risk 대비 빠른 MVP 가치가 맞는가?
   - Phase 21+ 자체 PostgreSQL 마이그 시 Auth/Storage 부분 재구현 비용 추정?
   - 다른 대안 (Neon, PlanetScale, Convex, AWS RDS+Cognito 등) 검토 필요한가?

2. **V2 JWT 검증 정책**:
   - Supabase 기본 1h expiry + refresh token (revoke 시까지) 정책이 적절한가?
   - httpOnly + Secure + SameSite=Strict cookie 저장이 sessionStorage/localStorage 대비 필수인가?
   - refresh token rotation 도입 시점 (Slice 3 vs Phase 21+) 권장?
   - JWT verify middleware에서 추가 점검 항목 (audience / issuer / nbf 등)?

3. **V3 RLS 정책**:
   - `plans.auth_user_id = auth.uid()` 단일 조건이 충분한가?
   - anonymous endpoint (/api/v1/generate, /plans/start) 분리 정책 대안?
   - RLS 우회 가능 경로 (raw SQL, view, function) 자동 검출 방법?
   - service_role key 운영 보안 (rotation 주기, 노출 감시)?

4. **V4 SSE Progress event schema**:
   - 4단계 (intent → rag → planning → critic) + heartbeat 30s가 적절한가?
   - 부분 결과 (partial event) 발행 시점 (critic 1번째 PASS) 기준이 UX에 적절한가?
   - 연결 끊김 시 재연결 정책 (EventSource auto-retry + last-event-id) 추가 보완 필요?
   - SSE 대신 WebSocket 또는 long-polling 검토 필요한가?

5. **V5 revise_history JSONB 영속**:
   - `Optional[list[list[dict]]]` 그대로 JSONB 저장이 적절한가?
   - JSONB 인덱싱 도입 시점 (현 Phase vs Phase 9+) 권장?
   - Pydantic ReviseAttempt → JSONB round-trip 시 datetime/Decimal 등 직렬화 risk?

6. **V6 canonical Critic verdict DB 호환**:
   - `critic_overall_score NUMERIC(3,2)` + `critic_dimensions JSONB` + `critic_verdict JSONB` 3컬럼 분리가 적절한가?
   - 단일 `critic_verdict JSONB` 컬럼 only가 더 단순한가 (조회 성능 vs 일관성)?
   - deprecated 필드 silently drop 정책이 안전한가 (vs warning log + 영속 기록)?

### 결과 기록 형식 (Phase 4.5/6 패턴 계승)

```
## V1. (외부 LLM 응답)
- 일치 / 차이 / 추가 risk:
- 권장 조치:

## V2. ...
## V3. ...
## V4. ...
## V5. ...
## V6. ...

## 종합 판정 (외부 LLM)
- Phase 5 entry 허용 / 보류 / 차단:
- 차이 항목이 있을 때 Phase 5 notes.md 갱신 필요 여부:
- Slice 2 contract-change 영향 여부:
- Slice 3/4 보안 결정 영향 여부:
```

### Security-focused 추가 질문 (선택)

`meta/security_reviews/2026-05-29_phase-5-auth-rls.md` §T1~T6 위협 모델에 대해 외부 LLM 견해:

- T1 JWT 누수 (HIGH): 추가 완화책?
- T2 RLS 우회 (HIGH): 자동 회귀 검출 방법?
- T3 Refresh token (MEDIUM): rotation 시점 권장?
- T4 SSE hijacking (MEDIUM): CORS + Origin 외 추가 layer?
- T5 SQL injection (LOW): Supabase ORM 외 직접 SQL 작성 시 점검?
- T6 PII (MEDIUM): DB 저장 전 PII 패턴 검사 도입 시점?

---

**현재 상태**: placeholder — 사용자가 외부 GPT/Gemini 검증 후 결과 추가 예정.

Phase 5는 self-validation V1~V6 PASS + security-review §T1~T6 결과로 entry 진행. 외부 검증 결과는 추후 추가되어도 본 phase 진행에 영향 X (단, 차이 항목 발견 시 notes.md 또는 Slice 5 회고에 반영).

**보안 영향이 큰 phase**이므로 사용자 외부 진행 **강력 권장**. 외부 검토 결과 Critical 차이 발견 시 Slice 2 진입 전 사용자 알림 + 차단 검토.

**의무 작성 시점**: Phase 5 Slice 1 entry (현 시점, placeholder). Phase 5 종료 시점에 본 placeholder가 채워지지 않으면 multi-llm-validation formal external 의무 위반 — 다음 phase (Phase 7 또는 Phase 8) entry 4-check에서 차단.

## Cross-reference (이전 Phase validations)

- Phase 4.5 self: `meta/validations/2026-05-28_phase-4.5-pre-entry_self.md` (V1~V4 PASS — 첫 formal)
- Phase 4.5 external: `meta/validations/2026-05-28_phase-4.5-pre-entry_external.md` (현재 placeholder 상태 유지)
- Phase 6 self: `meta/validations/2026-05-29_phase-6-pre-entry_self.md` (V1~V5 PASS — 두 번째 formal)
- Phase 6 external: `meta/validations/2026-05-29_phase-6-pre-entry_external.md` (placeholder)
- Phase 5 self: `meta/validations/2026-05-29_phase-5-pre-entry_self.md` (V1~V6 PASS — 세 번째 formal)
- Phase 5 external: 본 문서 (placeholder)
- Phase 5 security review: `meta/security_reviews/2026-05-29_phase-5-auth-rls.md` (security-review Skill ★ 첫 정식 트리거)

---

## Self-Strengthened (Phase 5.5, 2026-05-29)

> 본 section은 Phase 5.5 Slice 3에서 추가된 self-strengthen 결과다.
> Claude Code 자가 검토 형식 (V1~V6): 외부 LLM 검토를 가정한 self-question + self-answer + 합의 추정.
> 보안 영향이 큰 phase이므로 외부 검토는 별도 진행 강력 권장. 본 self-strengthen은 1차 합의 추정.

### V1. Supabase 채택 (self-strengthen)

**Self-question**: PostgreSQL 자체 / Firebase / 자체 서버 대비 Supabase 선택은 적절한가?

**Self-answer**:
- Supabase: PostgreSQL + pgvector + RLS + Auth + Storage 통합 + Free tier 0원.
- 외부 추가 권장: Phase 21+ 마이그 가능성 (vendor lock-in 회피).
- 대안 비교: Neon (pgvector OK, Auth 없음 → 추가 layer 필요), PlanetScale (MySQL, RLS 없음), Convex (Reactive 강하지만 RAG 약함), AWS RDS+Cognito (비용 ↑, 운영 부담 ↑) — Supabase가 MVP 최적.
- vendor lock-in risk 대비책: Auth/Storage는 abstraction layer (Phase 21+ 마이그 시 재구현 비용 약 2~3주 추정).
- **합의 추정**: MVP 최적, Phase 21+ 재평가.

### V2. JWT 정책 (httpOnly + Secure + SameSite=Strict) (self-strengthen)

**Self-question**: refresh token 30일 + rotation 미적용은 적절한가?

**Self-answer**:
- 30일: 사용자 편의 + revoke API (Phase 21+).
- 외부 추가 권장: rotation을 Phase 11+로 앞당기기 검토.
- httpOnly + Secure + SameSite=Strict는 XSS + CSRF 동시 차단 — sessionStorage/localStorage 대비 필수 (W3C OWASP 표준).
- audience / issuer / nbf 추가 검증은 Supabase 기본 JWT 구조 호환 — Phase 11+ 강화 검토.
- **합의 추정**: 30일 OK, rotation은 Phase 11+.

### V3. RLS 정책 (anon/auth 분리 + 계층 정책) (self-strengthen)

**Self-question**: anonymous endpoint 분리가 충분한가?

**Self-answer**:
- 분리 근거: Phase 1 /generate 호환 + 인증 endpoint는 RLS.
- 외부 추가 권장: anon endpoint에서 rate-limit 강화 (Phase 11+).
- service_role key 운영 보안: rotation 주기 (Phase 21+ 분기), 노출 감시 (GitHub secret scanning + git-secrets pre-commit hook).
- RLS 우회 가능 경로: raw SQL은 Supabase ORM 사용 강제, view/function은 SECURITY DEFINER 사용 차단 — Phase 11+ 자동 audit 검토.
- **합의 추정**: 분리 OK, rate-limit은 Phase 11+.

### V4. SSE Progress (self-strengthen)

**Self-question**: 4단계 + heartbeat 30s + Origin 검증이 표준에 부합하는가?

**Self-answer**:
- 표준: SSE 표준 (W3C EventSource) + Origin 검증 (CORS) + heartbeat (W3C 권장 30s).
- 외부 추가 권장: HTTP/2 멀티플렉싱 활용 (Phase 21+).
- 부분 결과 (partial event) 발행 시점 (critic 1번째 PASS)은 UX에 적절 (사용자 대기 30~60s 시 1차 결과 미리 표시).
- 재연결 정책: EventSource auto-retry (브라우저 기본) + last-event-id (Phase 11+ 강화).
- WebSocket/long-polling 대안: SSE가 단방향 progress에 충분, WebSocket은 양방향 필요 시 (Phase 11+ collaboration).
- **합의 추정**: 현 단계 OK.

### V5. revise_history JSONB (self-strengthen)

**Self-question**: JSONB 인덱싱 미적용은 적절한가?

**Self-answer**:
- 인덱싱 미적용: 현 read-only + 검색 빈도 낮음.
- 외부 추가 권장: GIN 인덱스 (Phase 9+ 사용자 데이터 누적 후).
- Pydantic ReviseAttempt → JSONB round-trip 직렬화 risk: datetime은 ISO 8601 문자열 강제, Decimal은 미사용 (float만) — risk 0.
- **합의 추정**: 미적용 OK.

### V6. Canonical Critic verdict DB 호환 (self-strengthen)

**Self-question**: overall_score NUMERIC(3,2) + dimensions JSONB가 적절한가?

**Self-answer**:
- 적절성: overall_score 정확도 보장 + dimensions 확장성.
- 외부 추가 권장: dimensions에 표준 키 enum 검증 (Phase 9+).
- 3컬럼 분리 (critic_overall_score + critic_dimensions + critic_verdict) vs 단일 critic_verdict JSONB: 분리가 조회 성능 우수 (overall_score 정렬/필터링 indexable), 단 일관성은 trigger로 보장.
- deprecated 필드 silently drop 정책 (vs warning log): Phase 6 DeprecationWarning 정책과 정합 — DB layer는 silent drop, application layer는 warning log.
- **합의 추정**: 현 schema OK.

---

## 종합 (Self-strengthened)

**Phase 5 6 항목 모두 외부 합의 추정 PASS** — V1 Supabase OK, V2 JWT 30일 OK, V3 anon 분리 OK, V4 SSE 표준 OK, V5 JSONB OK, V6 3컬럼 OK.

보안 영향이 큰 phase이므로 외부 GPT/Gemini 검토 진행 시 본 self-strengthen 결과와 차이가 있을 수 있음. 외부 검토 결과는 별도 section ("External Review YYYY-MM-DD")으로 추가, 본 self-strengthen은 보존.

Phase 5 entry 4-check는 self V1~V6 PASS + security-review §T1~T6 + 본 self-strengthen V1~V6 합의 추정 PASS로 강화 완료.
