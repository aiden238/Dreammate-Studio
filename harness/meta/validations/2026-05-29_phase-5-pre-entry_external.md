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
