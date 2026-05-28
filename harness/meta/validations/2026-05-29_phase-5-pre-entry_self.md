# Phase 5 Pre-Entry Multi-LLM Validation — Self (Claude Code)

> 검증 모델: Claude Code (자가, 지침 참조)
> 검증 일자: 2026-05-29
> 검증 유형: formal (세 번째 정식 트리거 — Phase 4.5 첫 + Phase 6 둘째 + Phase 5 셋째)
> 외부 검증: `2026-05-29_phase-5-pre-entry_external.md` (별도 placeholder)
> Skill 의무 트리거: security-review (별도 문서 — `meta/security_reviews/2026-05-29_phase-5-auth-rls.md`)

## 검증 대상

1. Supabase 채택 결정 (vs PostgreSQL 자체 / Firebase / 자체 서버)
2. JWT 검증 정책 (expiry / refresh / revocation)
3. RLS 정책 (anonymous endpoint 호환 / user_id 검증)
4. SSE Progress event schema (4단계 + 부분 결과)
5. revise_history JSONB 영속 (Phase 4.5 dict round-trip)
6. canonical Critic verdict (Phase 6 ADR-018) DB schema 호환

## 참조한 지침

- `harness/CLAUDE.md` § AI 구조, 큰 결정, 보안
- `harness/AGENTS.md` (구현/QA 모델 라우터)
- `harness/docs/contracts/llm_security_contract.md` (Step 1+2 자동 검사 + §5 시스템 prompt 격리 + §6 RAG poisoning + §7 비용 보호)
- `harness/docs/contracts/output_schema.md` (Phase 6 §9 canonical — overall_score + dimensions)
- `harness/docs/contracts/agent_io_contract.md` (Phase 6 §6 Rewriter v1.1.0)
- `harness/meta/patterns.md` (P-CRITIC-CANONICAL-001, P-CONTRACT-FIRST-001, P-VALIDATION-FORMAL-001, P-X1-EFFECT-001, P-X2-EFFECT-001)
- Phase 6 closing_notes.md (Phase 5 진입 체크리스트)
- Phase 6 entry files (goals/scope/non_goals/dependencies/acceptance/assumptions/multi_slice_plan/notes)
- Phase 5 entry files (goals/scope/non_goals/dependencies/acceptance/assumptions/multi_slice_plan/notes)
- `.claude/skills/security-review/SKILL.md` (트리거 조건 + 10영역 점검)
- `.claude/skills/multi-llm-validation/SKILL.md` (formal 절차)

## 검증 결과 (V1~V6)

### V1. Supabase 채택 — PASS

- **대안 비교**:
  - **A. Supabase** (채택): PostgreSQL + pgvector + RLS + Auth + Storage + Realtime 통합 + Free tier (500MB DB, 50K MAU, 2GB Storage)
  - B. PostgreSQL 자체: Auth/Storage 별도 구현 필요 → 운영 부담 ↑
  - C. Firebase: 표준 NoSQL → pgvector 미지원 (Phase 7 RAG 비호환)
  - D. 자체 서버: 인프라 비용 + 보안 부담 + MVP 속도 ↓
- **채택 사유**:
  1. PostgreSQL + pgvector + RLS + Auth + Storage 통합 → 빠른 MVP baseline (Phase 5 15~20h 추정 가능)
  2. Free tier (500MB DB + 50K MAU) → 초기 비용 0
  3. 표준 PostgreSQL → Phase 21+ 자체 PostgreSQL 마이그 가능 (vendor lock-in risk ↓)
  4. confirmed_decision [18] RAG 5단계 승격 파이프라인 + pgvector 호환
  5. Phase 7+ RAG 진입 시 vector store 별도 도입 불요
- **잠재 risk**:
  - vendor lock-in (Auth + Storage 인터페이스) → Phase 21+ 마이그 시점 비용
  - Free tier 초과 시 비용 (50K MAU 초과 = $25/mo + storage 비례 가산)
  - Auth provider 단일 의존 (Supabase outage 시 영향 100%)
- **권장**:
  - ADR-020에 trade-off 명시 (vendor lock-in + Free tier 한도)
  - Phase 11+ cost-review Skill로 quota 추적 시작 (현 Phase 외)
  - Auth 추상화 계층 (`lib/auth.ts`)로 provider 교체 가능성 일부 확보

### V2. JWT 검증 정책 — PASS

- **현 상태**: llm_security_contract.md §5.2 환경변수 격리만 명시 (Supabase service role key 등). JWT expiry / refresh / revocation 정책 명시 X.
- **Phase 5 결정 안**:
  - **expiry**: Supabase 기본 1h (custom 가능, 보안 vs UX trade-off — 1h 채택)
  - **refresh token**: Supabase 기본 expiry 없음 (revoke 시까지) → **Slice 3에서 rotation 검토 결정**
  - **revocation**: Supabase Auth /admin/users/{id}/revoke API (Phase 21+ 본격 운영)
  - **저장**: httpOnly + Secure + SameSite=Strict cookie (sessionStorage / localStorage 미사용)
- **llm_security_contract §8 E-SEC 코드 연계**:
  - E-SEC-007 (계정 도용 의심) — JWT가 다른 IP에서 동시 사용 시 flag
- **잠재 risk**:
  - refresh token 누수 시 무한 접근 (rotation 없음 → 단일 유출 = 영구 접근)
  - JWT가 localStorage에 저장될 경우 XSS 한 번으로 토큰 유출 → httpOnly cookie 의무
  - Supabase Auth /admin API는 service_role key 필요 → backend-only
- **권장**:
  - Slice 3 lib/auth.ts에서 httpOnly cookie 강제, sessionStorage 미사용 명시
  - Slice 3 결정 후 ADR-021 또는 별도 ADR에 정책 명시
  - security_metrics.md (Phase 7+) JWT abnormal use 추적 항목 추가

### V3. RLS 정책 — PASS

- **현 상태**: llm_security_contract.md §1.10 "기본값 fail-safe 통과" + security-review SKILL §5 "auth.uid()로 본인 데이터만 접근" 점검 항목 존재. 실제 정책 SQL 미작성.
- **Phase 5 결정 안**:
  - **plans 테이블**: `plans.auth_user_id = auth.uid()` 일치 시만 SELECT/UPDATE/DELETE 허용
  - **video_projects 테이블**: 동일 (`auth_user_id = auth.uid()`)
  - **anonymous endpoint 호환**:
    - `/api/v1/generate` (Phase 1 endpoint, NG7 → Phase 8+ 제거) → RLS 미적용 (별도 anon role)
    - `/plans/start` (entry, Phase 5에서 결정) → 익명 가능, plans 생성 시 `auth_user_id = NULL` 허용 또는 임시 게스트 ID
  - **service_role**: backend-only (api 응답에 service_role key 노출 절대 금지 — llm_security_contract §5.2 정합)
- **잠재 risk**:
  - anonymous endpoint에서 다른 user plan 읽기 가능 → endpoint 분리 필수
  - RLS 정책 SQL bug → bypass risk (security-review §5 핵심 점검)
  - service_role key 클라이언트 노출 시 모든 RLS 우회 가능
- **권장**:
  - Slice 4 ADR-021에 anon/auth endpoint 분리 정책 명시
  - test_rls.py에 다른 user plan 접근 → 403/404 차단 케이스 3+ 추가 (acceptance A6)
  - service_role key는 .env (server-side only) + NEXT_PUBLIC_* prefix 금지 (llm_security §5.2)

### V4. SSE Progress event schema — PASS

- **현 상태**: confirmed_decision [10] "30~60초 대기 시 4단계 progress + 부분 결과 노출" 결정 있음. 실제 event schema 미작성.
- **Phase 5 결정 안**:
  - **4단계**: intent → rag → planning → critic (Phase 4 retrospective 기준 + Phase 4.5 revise 통합)
  - **event schema**:
    ```typescript
    interface SSEProgressEvent {
      type: "progress" | "partial" | "complete" | "error";
      step: number; // 0~4
      step_name: "intent" | "rag" | "planning" | "critic" | "done";
      message: string; // 사용자 노출 메시지
      payload?: any; // partial 시 부분 결과 (예: critic verdict 미완성)
      timestamp: string; // ISO8601
    }
    ```
  - **heartbeat**: 30s (연결 유지, EventSource 표준)
  - **부분 결과**: critic step에서 1번째 plan PASS 시점에 partial event 발행 (사용자 즉시 노출)
- **llm_security_contract §7 비용 보호 정합**: 단일 세션당 SSE 최대 5분 timeout (cost spike 방어)
- **잠재 risk**:
  - 연결 끊김 시 재연결 정책 부재 → 사용자 진행 상태 손실
  - SSE event에 PII 포함 가능성 (예: partial 결과의 user_input echo) → PII 마스킹 필수
  - CORS 미설정 시 다른 origin에서 SSE 청취 가능 → Origin 검증 필수
- **권장**:
  - Slice 4 ADR-022 — EventSource retry 자동 + 클라이언트 last-event-id 활용
  - test_sse.py에 4단계 + partial + heartbeat + reconnect 케이스
  - llm_security_contract §3.4 XSS sanitize를 SSE message에도 적용

### V5. revise_history JSONB 영속 — PASS

- **현 상태**: Phase 4.5 ADR-016 + Phase 6 V3 강화 (ReviseAttempt Pydantic 모델). Phase 6 schemas/output.py에서 `revise_history: Optional[list[list[dict]]]`.
- **Phase 5 결정 안**:
  - **컬럼**: `plans.revise_history JSONB` (PostgreSQL JSONB 표준)
  - **Phase 4.5 dict 구조** (`list[list[dict]]`) 그대로 JSONB 저장 가능 (Pydantic dict 직렬화 → JSONB native 변환)
  - **round-trip**: Pydantic Body.model_validate() ↔ JSONB ↔ Pydantic 직렬화 round-trip 검증 (test_db.py acceptance A8)
- **잠재 risk**:
  - JSONB 인덱싱 미사용 시 검색 성능 ↓ (현 단계 read-only, Phase 9+ 결정)
  - revise effect eval (NG15) 미적용 상태에서 누적 시 무용 데이터 (Phase 9+ eval-run 정식화 후 재평가)
  - PostgreSQL JSONB 크기 제한 1GB (실용 한도 ~1MB) → revise_history 정상 범위 < 10KB 충분
- **권장**:
  - Slice 2 migration 0002에 `revise_history JSONB NULL DEFAULT NULL` 명시
  - test_db.py에 revise_history round-trip 케이스 (Phase 4.5 dict 구조 보존 검증)
  - 인덱싱은 Phase 9+ eval 운영 시작 후 결정

### V6. Phase 6 canonical Critic verdict DB 호환 — PASS

- **현 상태**: Phase 6 ADR-018 canonical (overall_score: float [0.0~1.0] + dimensions: dict[str, float]) + fallback 4 임시 호환 + DeprecationWarning.
- **Phase 5 결정 안**:
  - **plans 테이블 컬럼**:
    - `critic_overall_score NUMERIC(3,2)` (0.00~1.00, NULL 허용 — critic 실패 시)
    - `critic_dimensions JSONB` (8-dim dict, NULL 허용)
    - `critic_verdict JSONB` (전체 verdict 객체, audit용 — overall_verdict + blocking_issues + recommended_changes 포함)
  - **deprecated 필드** (overall_score_avg, scores, eight_dim_scores):
    - 별도 컬럼 X (응답 호환만 유지, Phase 9+ 완전 제거)
    - DB에는 canonical만 저장
  - **recommended_plan_index**: `plans.recommended_plan_index INTEGER NULL` 컬럼
- **Phase 6 baseline 정합**:
  - Pydantic CriticEvaluation → JSONB round-trip 호환 (Phase 6 schemas/output.py 검증 완료)
  - revise_history와 함께 plans 단일 row에 저장
- **잠재 risk**:
  - deprecated 필드를 클라이언트가 보내올 때 무시 정책 (silently drop vs warning)
  - canonical 0~1 정규화 vs DB NUMERIC(3,2) 정밀도 (소수점 둘째 자리까지 충분)
- **권장**:
  - Slice 2 db_schema.md에 컬럼 정의 명시 (canonical만, deprecated X)
  - Slice 2 plans_repo.py에서 deprecated 필드 silently drop + log.warn 발행
  - test_db.py에 canonical round-trip 케이스

## 종합 판정

**Phase 5 entry 허용 — 6/6 PASS (V1~V6)**

| ID | 항목 | 결과 | 후속 조치 |
|---|---|---|---|
| V1 | Supabase 채택 | PASS | ADR-020 명시 |
| V2 | JWT 정책 | PASS | Slice 3 httpOnly cookie 의무 |
| V3 | RLS 정책 | PASS | Slice 4 ADR-021 + anon/auth 분리 |
| V4 | SSE schema | PASS | Slice 4 ADR-022 + Origin 검증 |
| V5 | revise_history JSONB | PASS | Slice 2 migration 0002 |
| V6 | canonical DB 호환 | PASS | Slice 2 db_schema.md canonical만 |

다음: Slice 2 sub-agent dispatch — Supabase 연결 + Schema migration + plans_repo + contract-change (db_schema.md 신규).

## Contract gap analysis (현 상태 vs Phase 5 목표)

| 항목 | docs/contracts | 실 backend | 차이 | Slice 작업 |
|---|---|---|---|---|
| DB schema | `db_schema.md` 명시 X (참조만 — llm_security §3.1 intent_filter_logs 등) | _plan_store (in-memory dict) | DB 정식 등록 + 4계층 테이블 | Slice 2 db_schema.md 신규 + 0001/0002 migration |
| JWT 정책 | llm_security_contract.md §5.2 환경변수만 명시 | 미구현 | JWT verify middleware + expiry/refresh 정책 | Slice 3 auth_middleware.py + 정책 ADR |
| RLS 정책 | security-review SKILL §5 체크리스트만 명시 | 미구현 | 정책 SQL + auth.uid() 강제 | Slice 4 0003_rls_policy.sql + ADR-021 |
| SSE event schema | confirmed_decision [10] 결정만 명시 | 미구현 | event schema + 4단계 + heartbeat | Slice 4 routers/sse.py + ADR-022 |
| plans 테이블 | 미명시 | _plan_store dict | revise_history JSONB + recommended_plan_index + critic canonical | Slice 2 plans_repo.py + 0001/0002 |
| Auth endpoint | api_contract.md /auth/* 명시 X | 미구현 | /auth/login + /auth/me + /auth/logout | Slice 3 routers/auth.py + api_contract §8.* 갱신 |

## 외부 검증 연계

self-validation 단일 모델 (Claude Code) 결과. 외부 검증 결과 (GPT/Gemini)는 `2026-05-29_phase-5-pre-entry_external.md` placeholder에 사용자가 외부 진행 후 채울 수 있음.

Phase 5는 보안 영향 큰 phase (Auth + RLS) → 외부 검증 권장. 단 Phase 4.5/6 패턴 계승으로 external placeholder는 **사용자 외부 진행 권장** 형식 유지. self-validation V1~V6 PASS 결과로 Phase 5 entry 진행.

두 결과 차이 항목 발견 시:
- Phase 5 진행 중 `notes.md`에 기록
- Slice 5 회고 §개선 제안 반영
- Critical 차이 (Supabase 채택 자체 변경 등) 시 Slice 2 진입 전 사용자 알림

## Cross-reference (이전 Phase validations)

- Phase 4.5 self: `meta/validations/2026-05-28_phase-4.5-pre-entry_self.md` (V1~V4 PASS — 첫 formal)
- Phase 4.5 external: `meta/validations/2026-05-28_phase-4.5-pre-entry_external.md` (placeholder 유지)
- Phase 6 self: `meta/validations/2026-05-29_phase-6-pre-entry_self.md` (V1~V5 PASS — 두 번째 formal)
- Phase 6 external: `meta/validations/2026-05-29_phase-6-pre-entry_external.md` (placeholder 유지)
- Phase 5 self: 본 문서 (V1~V6 PASS — 세 번째 formal)
- Phase 5 external: `meta/validations/2026-05-29_phase-5-pre-entry_external.md` (placeholder)
- Phase 5 security review: `meta/security_reviews/2026-05-29_phase-5-auth-rls.md` (security-review Skill ★ 첫 정식)

## Skill 트리거 기록

- multi-llm-validation: **세 번째 formal 트리거** (Phase 4.5 첫 + Phase 6 둘째 + Phase 5 셋째) → P-VALIDATION-FORMAL-001 정식 패턴 입증 강화 (3회 누적)
- security-review: **★ 첫 정식 트리거** (별도 문서) → unused → active 전환
- phase-start: 7번째 트리거 (Phase 1+2+3+4+4.5+6+5)
