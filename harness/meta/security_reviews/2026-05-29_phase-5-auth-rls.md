# Phase 5 Security Review — Auth + RLS + JWT + SSE (★ 첫 정식 트리거)

> Date: 2026-05-29
> Reviewer: Claude Code (self, security-review Skill 절차 따름)
> Trigger: Phase 5 entry — Supabase Auth + RLS + JWT + SSE 첫 도입
> Skill: `.claude/skills/security-review/SKILL.md` v1.0.0 (트리거 조건 §1 "새 사용자 입력 경로" + §5 "사용자 권한 정책 변경" + Phase 종료 직전 → Phase 5 entry로 차용)
> External review: 사용자 외부 진행 권장 (placeholder — `meta/validations/2026-05-29_phase-5-pre-entry_external.md` §Security-focused 추가 질문)
> Related contract: `docs/contracts/llm_security_contract.md` v1.0.0 (Step 1+2 자동 검사 + §5 시스템 prompt 격리 + §6 RAG poisoning + §7 비용 보호 + §8 E-SEC 코드)

---

## §1. Scope 정의

### 검토 대상

1. **Supabase Auth + JWT 도입** (Slice 3) — /auth/login, /auth/me, /auth/logout, auth_middleware.py
2. **Row Level Security 정책** (Slice 4) — plans, video_projects 테이블 user 분리
3. **SSE 연결 보안** (Slice 4) — /plans/{plan_id}/progress event endpoint
4. **PII 마스킹 + 프롬프트 인젝션 차단 baseline 유지** (llm_security_contract.md §3 ↔ Phase 5 호환)

### 미검토 (Phase 외)

- **NG1** Brand Memory PII (Phase 6+) — DB column 정의 시 brand_memory 컬럼만 허용
- **NG5** 결제 / Team 보안 (Phase 21+)
- **NG13** Custom RAG security review (Phase 21+)
- **Phase 7+** placeholder 항목: privacy_contract, user_consent_contract, data_retention_policy (별도 phase 진입 시 본 review 재호출)

### 본 review가 다루지 않는 일반 보안 (외부 도구로 위임)

- 인프라 보안 (Supabase 측 — SOC 2, ISO 27001 등)
- DDoS / botnet 차단 (Cloudflare / WAF, Phase 11+)
- 정기 dependency vulnerability scan (별도 운영 절차)

---

## §2. 위협 모델 (Threat Model)

llm_security_contract.md §0의 5가지 위협 모델에 Auth/RLS 위협 6가지를 매핑:

| ID | 위협 | 영향 | 가능성 | 우선순위 | llm_security 매핑 |
|---|---|---|---|---|---|
| **T1** | JWT 토큰 누수 (XSS / 저장 위치 실수) | 사용자 데이터 노출 (다른 user 데이터 접근 가능) | 중 | **HIGH** | §5 격리 + §8 E-SEC-007 계정 도용 |
| **T2** | RLS 정책 우회 (anonymous endpoint에서 다른 user plan 읽기 / 정책 SQL bug) | 다른 user plan 전체 노출 | 중 | **HIGH** | §5 권한 / security-review SKILL §5 |
| **T3** | Refresh token 무한 사용 (revoke 불가 시 영구 접근) | 장기 데이터 노출 | 낮 | MEDIUM | §5 인증 / Phase 7+ MFA placeholder |
| **T4** | SSE 연결 hijacking (CORS 미설정 / Origin 우회) | 실시간 partial 결과 + PII 노출 | 낮 | MEDIUM | §3.4 XSS + §4.5 응답 sanitize |
| **T5** | SQL injection (Supabase ORM 우회 / raw SQL 실수) | DB 손상 + 데이터 유출 | 매우낮 | LOW | §3.4 입력 검증 |
| **T6** | PII 마스킹 우회 (DB 직접 저장 단계에서 raw PII 누적) | 개인정보 노출 (90일 후 비식별화 의무) | 낮 | MEDIUM | §3.2 PII 마스킹 + §4.4 잔존 |

### 신규 위협 (Phase 5 도입 결과)

- T1+T2 = "토큰 + RLS bypass" 조합 시 사용자 1명이 전체 DB 노출 가능 → critical chain (별도 점검)
- T6 신규 surface: DB 영속화 도입 → PII가 in-memory에서 DB로 흐름 → retention 정책 의무 시작점 (Phase 7+)

---

## §3. 권장 조치

### T1: JWT 누수 — HIGH

**현 상태**: Supabase Auth 도입 직전 (Slice 3에서 결정).

**권장**:
- **저장 위치**: httpOnly + Secure + SameSite=Strict cookie (sessionStorage / localStorage 미사용)
  - XSS 한 번으로 토큰 유출 차단
  - frontend lib/auth.ts에서 cookie 직접 set/get 불가 (서버에서만)
- **TTL**: Supabase 기본 1h access token (custom 가능, 1h 채택)
- **refresh token**: 별도 httpOnly cookie, expiry 30일 (Slice 3 결정)
- **CORS**: 명시적 origin 허용 (development: http://localhost:3000, production: 별도 도메인)
- **logout**: Supabase Auth signOut() + 서버측 refresh token revoke

**llm_security_contract §5.2 정합**:
- Supabase service_role key는 server-side .env (NEXT_PUBLIC_* prefix 금지)
- anon key는 frontend OK (이 자체는 RLS 정책으로 보호)

**Acceptance 매핑**: A4 Auth JWT (test_auth.py)

### T2: RLS 우회 — HIGH

**현 상태**: RLS 정책 SQL 미작성 (Slice 4에서 0003_rls_policy.sql 신규).

**권장**:
- **anonymous endpoint 분리**:
  - `/api/v1/generate` (Phase 1 endpoint, NG7 → Phase 8+ 제거) → anon role (RLS 미적용)
  - `/plans/start` (Phase 5에서 결정) → anon role 가능, auth_user_id NULL 허용 또는 임시 게스트 ID
  - `/plans/{plan_id}/generate`, `/plans/{plan_id}` (GET/UPDATE/DELETE) → authenticated role (RLS 강제)
- **RLS 정책 SQL** (Slice 4 0003_rls_policy.sql):
  ```sql
  ALTER TABLE plans ENABLE ROW LEVEL SECURITY;
  CREATE POLICY plans_user_isolation ON plans
    FOR ALL
    USING (auth_user_id = auth.uid() OR auth_user_id IS NULL)
    WITH CHECK (auth_user_id = auth.uid());
  ```
- **자동 검증** (Slice 4 test_rls.py):
  - user_a JWT로 user_b plan_id 조회 → 403 또는 404
  - anon role로 다른 user plan_id 조회 → 403 또는 404
  - service_role key 응답 노출 안 되는지 검사
- **service_role 운영**: backend .env only, rotation 주기 90일 (Phase 11+)

**Acceptance 매핑**: A6 RLS (test_rls.py)

### T3: Refresh token — MEDIUM

**현 상태**: Supabase 기본 refresh token expiry 없음 (revoke 시까지).

**권장**:
- **rotation**: Slice 3에서 검토 (refresh 시마다 새 token 발행 + 이전 token 무효화)
  - Slice 3 도입 권장: 단일 토큰 유출 시 무한 접근 위험 차단
  - 구현 비용: Supabase Auth flowType: 'pkce' + rotation 옵션 (간단)
- **revoke API**: Supabase Auth /admin/users/{id}/revoke (Phase 21+ admin UI 도입 시 활성)
- **expiry 강제**: refresh token 자체 expiry 30일 (configurable)

**Phase 21+ 이관**:
- MFA / WebAuthn / passkey (llm_security §12 정합)
- 비정상 사용 패턴 자동 감지 (E-SEC-007 ML 보강)

**Acceptance 매핑**: A4 부분 (rotation 도입 시 추가 테스트)

### T4: SSE hijacking — MEDIUM

**현 상태**: SSE endpoint 미구현 (Slice 4 routers/sse.py 신규).

**권장**:
- **Origin 검증**: SSE endpoint middleware에서 Origin 헤더 화이트리스트 검사
- **JWT 검증**: SSE 연결 시작 시 Authorization 헤더 또는 query token verify
  - EventSource는 기본 Authorization 헤더 X → query parameter token 또는 cookie 의존
  - cookie 의존 권장 (T1 정합 — httpOnly cookie 자동 전송)
- **CORS**: 명시적 origin (Allow-Credentials: true 필수 — cookie 동반)
- **CSRF**: SameSite=Strict cookie로 자동 방어 (T1 정합)
- **heartbeat**: 30s ping → 5분 이상 inactive 연결 자동 close (cost spike 방어 §7)
- **rate limit**: user당 SSE 동시 연결 수 1 (다중 연결 시 이전 close)

**llm_security §3.4 + §4.5 정합**:
- SSE message 본문에 XSS sanitize 적용
- partial event payload에 PII 마스킹 (§3.2 + §4.4)

**Acceptance 매핑**: A7 SSE (test_sse.py)

### T5: SQL injection — LOW

**현 상태**: Supabase ORM (PostgREST) 기본 사용 → parameterized query 자동.

**권장**:
- **ORM 강제**: 직접 SQL 작성 최소화 (Supabase python client 사용)
- **prepared statement**: 직접 SQL 작성 필요 시 (예: migration script) prepared statement 의무
- **migration 보안**: Slice 2 db/migrations/*.sql 파일은 idempotent + 입력 변수 없음 (정적 schema 정의)
- **input validation**: 모든 API endpoint에 Pydantic schema validation (Phase 1 baseline 유지)

**llm_security §3.4 정합**:
- XSS / HTML / JS injection sanitize는 SQL injection과 별개로 유지

**Acceptance 매핑**: 별도 acceptance X (baseline 유지)

### T6: PII — MEDIUM

**현 상태**: Phase 1 intent.py PII 마스킹 baseline 존재 (llm_security §3.2). DB 영속화 도입 시 잔존 위험.

**권장**:
- **baseline 유지**: Phase 1 intent.py PII 마스킹 + llm_security §3.2 패턴 그대로 적용
- **DB 저장 전 검사**: plans_repo.py에서 INSERT 직전 PII 패턴 재검사
  - 현 Phase 외 (Phase 9+ retention 정책 본격화 시) 도입 권장
  - 본 Slice 2에서는 baseline 의존 (intent.py 마스킹 통과 데이터만 plans_repo에 도달)
- **agent_io_logs**: raw_payload는 그대로 저장 (llm_security §3.2 case C) + 90일 후 비식별화 (Phase 9+ data_retention_policy)
- **응답 잔존**: §4.4 정합 (LLM 응답에 PII echo 시 마스킹) baseline 유지

**Phase 7+ 강화**:
- privacy_contract.md (placeholder → 본문 작성)
- user_consent_contract.md (placeholder → 본문 작성)
- data_retention_policy.md (placeholder → 본문 작성)

**Acceptance 매핑**: baseline 유지 (별도 acceptance X)

---

## §4. 영역별 점검 결과 (security-review SKILL §점검 영역 1~10)

| 영역 | 점검 항목 (요약) | 결과 | 비고 |
|---|---|---|---|
| 1. 프롬프트 인젝션 | llm_security §3.3 8 패턴 baseline | **PASS** (baseline 유지) | Phase 1 intent.py + Step 1 hook 그대로 |
| 2. RAG 오염 | candidate → promoted 5단계 (NG2 → Phase 7) | **N/A** (Phase 7+) | rag-update Skill 절차 보존 |
| 3. PII 노출 | llm_security §3.2 + §4.4 baseline | **PASS** (baseline 유지) | DB 저장 단계 신규 surface → T6 권장 |
| 4. 외부 도구 호출 | LLM tool use 없음 | **N/A** | Phase 8+ MOA 본격 시 재평가 |
| 5. 권한 / RLS | Supabase RLS 정책 (T2 핵심) | **PARTIAL** → Slice 4 0003_rls + ADR-021 후 PASS | 본 Slice 1 시점 미구현 |
| 6. 입력 검증 | Pydantic schema + length / charset / unicode | **PASS** (baseline 유지) | llm_security §3.5 |
| 7. 비용 폭탄 | Critic max 2 + SSE 5분 timeout + rate_limit_policy | **PASS** | llm_security §7 + cost-review (Phase 9+) |
| 8. 인증 / 세션 | JWT + Supabase Auth (T1+T3) | **PARTIAL** → Slice 3 lib/auth.ts + httpOnly cookie 후 PASS | 본 Slice 1 시점 미구현 |
| 9. 데이터 보존 / 삭제 | retention_policy placeholder (Phase 7+) | **N/A** (Phase 7+) | DB 도입 = retention 의무 시작점 |
| 10. 로그 / 감사 추적 | agent_io_logs + intent_filter_logs + errors.log baseline | **PASS** (baseline 유지) | llm_security §9 security_metrics |

### 종합

- **PASS**: 5 영역 (1, 3, 6, 7, 10) — baseline 유지
- **PARTIAL → PASS 예정**: 2 영역 (5, 8) — Slice 3/4에서 구현 후 PASS 달성
- **N/A**: 3 영역 (2, 4, 9) — Phase 7+ 이관

---

## §5. 보안 baseline

Phase 5 entry 시점 baseline (Slice 1):

- [x] llm_security_contract.md §3 Step 1 자동 검사 baseline 유지 (intent_filter + PII + injection + XSS + 길이)
- [x] llm_security_contract.md §4 Step 2 자동 검사 baseline 유지 (schema + 광고 + PII 잔존 + sanitize + leakage)
- [x] llm_security_contract.md §5 시스템 prompt 격리 + 환경변수 격리 baseline
- [x] llm_security_contract.md §7 비용 보호 baseline (Critic max 2 + cost-review Phase 9+)
- [x] llm_security_contract.md §8 E-SEC-* 코드 매핑 baseline

Phase 5 Slice 3/4 도입 (PARTIAL → PASS 예정):

- [ ] Supabase Auth 도입 + httpOnly cookie 저장 (T1) — Slice 3
- [ ] RLS 정책 SQL + anonymous/authenticated endpoint 분리 (T2) — Slice 4 (ADR-021)
- [ ] SSE Origin 검증 + cookie 의존 + heartbeat (T4) — Slice 4 (ADR-022)
- [ ] PII 마스킹 baseline 유지 + DB 저장 전 재검사 도입 시점 결정 (T6) — Phase 9+ 이관

Phase 21+ 강화 (장기):

- [ ] Refresh token rotation (T3) — Phase 21+
- [ ] SQL injection 자동 검사 (T5) — Supabase ORM baseline + 정기 dependency scan
- [ ] MFA / WebAuthn / passkey (T1 보강) — Phase 21+
- [ ] ML 기반 비정상 패턴 감지 (E-SEC-007) — Phase 11+

---

## §6. 외부 검토 권장

본 self review는 단일 모델 (Claude Code). **사용자가 외부 GPT/Gemini로 검토 권장**:

### 외부 LLM에 추가 질문 권장 항목

1. **Supabase RLS 정책 우회 vulnerability 알려진 케이스** — view, function, raw SQL을 통한 우회 사례
2. **JWT 토큰 저장 best practice** — httpOnly cookie vs OAuth2 PKCE vs Web Crypto API + IndexedDB
3. **SSE keep-alive / heartbeat 표준** — 30s ping이 industry standard인지 확인 + 더 안전한 대안
4. **Refresh token rotation 도입 시점** — Phase 5 Slice 3 즉시 vs Phase 21+ 지연 권장
5. **PII detection library 추천** — 한국어 + 영어 혼용 환경에서 false positive 최소화
6. **service_role key 운영** — rotation 자동화 도구 + 노출 감시 방법

### 외부 검토 결과 처리

- **PASS** 일치: notes.md에 기록만, Phase 5 진행 계속
- **차이** 있음: Phase 5 notes.md §외부 검토 차이에 기록 + Slice 5 회고 §개선 제안 반영
- **Critical 차이**: Slice 2 진입 전 사용자 알림 + 차단 검토 (예: Supabase 대신 다른 provider 권장 등)

---

## §7. 후속 조치 (Slice 매핑)

| Slice | 조치 항목 | 검증 |
|---|---|---|
| **Slice 1** (현) | 본 security-review 작성 + ADR-020 + external placeholder | meta/security_reviews/2026-05-29_phase-5-auth-rls.md 존재 |
| **Slice 2** | db_schema.md 신규 + 0001/0002 migration (RLS 예고) | T6 baseline 유지 (PII 마스킹 통과 데이터만 plans_repo) |
| **Slice 3** | auth_middleware.py + lib/auth.ts (httpOnly cookie) + /auth/* endpoints | T1+T3 권장 적용 + test_auth.py JWT 검증 3+ 케이스 |
| **Slice 4** | 0003_rls_policy.sql + sse.py + Origin 검증 + ADR-021/022 | T2+T4 권장 적용 + test_rls.py 다른 user 403/404 + test_sse.py Origin 거부 |
| **Slice 5** | **security-review Skill 두 번째 트리거** (final, 의도된 시행 + 결과 검증) | 본 review 후속 검증 + retrospective §개선 제안 |

---

## §8. Acceptance

Phase 5 종료 시점 (Slice 5 final security-review 재트리거):

- [ ] Slice 4 RLS pytest: 다른 user plan 접근 → 403/404 차단 (test_rls.py)
- [ ] Slice 4 SSE pytest: anonymous origin → 거부 (test_sse.py)
- [ ] Slice 3 Auth pytest: JWT 만료 / 위조 / refresh / logout 정상 (test_auth.py)
- [ ] llm_security_contract.md baseline 유지 (Phase 1 testing 회귀 0)
- [ ] **security-review Skill 두 번째 트리거** (의도된 시행, Slice 5)
- [ ] PII 마스킹 baseline 유지 (Phase 1 회귀 0)

---

## §9. Critical 발견 처리 (security-review SKILL §4)

본 review에서 Critical 발견 X (PARTIAL 2건은 의도된 Slice 3/4 구현 대기).

**만약 Slice 2~4 진행 중 Critical 발견 시**:
1. 영향 영역 즉시 비활성화 (feature flag)
2. hotfix phase 진입 (별도 phase 또는 Slice 추가)
3. meta-retrospective 즉시 트리거
4. contract-change Skill로 llm_security_contract.md 강화 검토
5. 사용자에게 영향 통지 (해당 시)

---

## §10. security_metrics 등록 (security-review SKILL §5)

`meta/security_metrics.md`에 Phase 5 baseline row 추가 (Slice 5에서 갱신):

```
| 영역 | 마지막 점검 | 결과 | 다음 점검 |
|------|------------|------|-----------|
| 프롬프트 인젝션 (1) | 2026-05-29 | PASS (baseline) | Phase 7+ RAG 진입 시 |
| RAG 오염 (2) | N/A | N/A | Phase 7 |
| PII (3) | 2026-05-29 | PASS (baseline) | Phase 9+ (DB 저장 전 재검사 도입 시) |
| 외부 도구 (4) | N/A | N/A | Phase 8+ MOA |
| 권한 / RLS (5) | 2026-05-29 | **PARTIAL → Slice 4 후 PASS** | Phase 5 Slice 5 final |
| 입력 검증 (6) | 2026-05-29 | PASS (baseline) | 정기 (월 1회) |
| 비용 폭탄 (7) | 2026-05-29 | PASS (baseline) | Phase 9+ cost-review |
| 인증 / 세션 (8) | 2026-05-29 | **PARTIAL → Slice 3 후 PASS** | Phase 5 Slice 5 final |
| 데이터 보존 (9) | N/A | N/A | Phase 7+ retention_policy |
| 로그 / 감사 (10) | 2026-05-29 | PASS (baseline) | 정기 (월 1회) |
```

본 row는 Slice 5 final review 직후 `meta/security_metrics.md`에 반영 권장 (Phase 5 closing notes).

---

## §11. 변경 이력

```
v1.0.0 (2026-05-29): Phase 5 entry — security-review Skill ★ 첫 정식 트리거.
                      §1 Scope + §2 Threat Model T1~T6 + §3 권장 조치 +
                      §4 영역 1~10 점검 + §5 baseline + §6 외부 검토 권장 +
                      §7 Slice 매핑 + §8 Acceptance + §9 Critical 처리 +
                      §10 security_metrics 등록.
```

---

**End of Phase 5 Security Review v1.0.0 — security-review Skill ★ first formal trigger.**
