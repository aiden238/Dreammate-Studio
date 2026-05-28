# Phase 5 Security Review — Final Verification (★ 두 번째 트리거)

> Date: 2026-05-29
> Reviewer: Claude Code (self, security-review Skill 절차 따름)
> Trigger: Phase 5 Slice 5 종료 직전 — Slice 1 entry security review 결과를 Slice 2~4 실 구현 후 verify
> Skill: `.claude/skills/security-review/SKILL.md` v1.0.0 (트리거 조건 §1 "Phase 종료 직전 — 보안 영향 있는 Phase")
> 관련 review: `2026-05-29_phase-5-auth-rls.md` (Slice 1 entry, 첫 정식 트리거)

---

## §1. Scope (Slice 1 entry와 동일)

1. **Supabase Auth + JWT** (Slice 3 — 실 구현 완료)
2. **RLS 정책** (Slice 4 — 0003_rls_policy.sql 적용)
3. **SSE 연결 보안** (Slice 4 — Origin 검증 + cookie auth)
4. **PII 마스킹 + 프롬프트 인젝션 차단 baseline** (Phase 1 유지)

---

## §2. Slice 1~4 결과 verify (T1~T6)

### T1: JWT 누수 — HIGH → ✅ PASS (Slice 3 구현)

**Slice 1 권장 조치**:
- httpOnly cookie 저장 (XSS 방지)
- SameSite=Lax (CSRF 1차 방어)
- 7일 만료 (refresh 24시간 sliding window — Phase 21+ rotation)

**Slice 3 구현 결과**:
- ✅ `routers/auth.py::login()` — httpOnly + SameSite=Lax cookie 설정 (`response.set_cookie(..., httponly=True, samesite="lax")`)
- ✅ JWT secret env var (`config.py::jwt_secret_key`) — production 검증 필요 (Phase 11+)
- ✅ logout endpoint — cookie 만료 + 클라이언트 storage 제거
- ✅ middleware/auth_middleware.py — `request.state.user` 주입, missing/invalid → 401
- ✅ test_auth.py 9 cases — mock JWT round-trip + invalid token rejection + logout cookie 만료

**잔존 risk** (Phase 21+ 이관):
- Refresh token rotation 미구현 (현 7일 만료 후 재로그인) — Phase 21+ MFA/WebAuthn 시점 도입

### T2: RLS 우회 — HIGH → ✅ PASS (Slice 4 구현)

**Slice 1 권장 조치**:
- `auth.uid()` 강제 정책 (plans + video_projects + series + domains via brands)
- anonymous endpoint (`/api/v1/generate` Phase 1) 호환을 위한 NULLABLE auth_user_id
- service_role 사용 백엔드만 (API 응답에 노출 X)

**Slice 4 구현 결과**:
- ✅ `db/migrations/0003_rls_policy.sql` — ENABLE ROW LEVEL SECURITY + 4 정책 (SELECT/INSERT/UPDATE/DELETE)
- ✅ `auth.uid() = auth_user_id` 직접 매칭 (plans, video_projects)
- ✅ series → video_projects via brand_id (2-hop subquery 정책 — ADR-021)
- ✅ domains → brands.auth_user_id (1-hop)
- ✅ anonymous endpoint 호환: auth_user_id NULLABLE (Phase 1 /generate 유지)
- ✅ test_rls.py 4 cases — 다른 user plan 차단 + 본인 plan 통과 + anonymous 호환 + service_role bypass 검증

**잔존 risk** (Phase 6+ 이관):
- service_role 사용 boundary 명시 부족 — Phase 6+ DB layer 통합 시 명시 (개선 제안 §1)
- RLS 정책 SQL bug 자동 감지 부재 — Phase 9+ eval-run pgtap 도입 검토

### T3: Refresh token 무한 사용 — MEDIUM → 🟡 PARTIAL (Phase 21+ 이관)

**현 상태**: 7일 만료 후 재로그인 (rotation 미구현, NG로 Slice 1에서 결정)
**잔존**: Phase 21+ MFA/WebAuthn 도입 시 rotation 필요

### T4: SSE hijacking — MEDIUM → ✅ PASS (Slice 4 구현)

**Slice 1 권장 조치**:
- CORS Origin 검증 (whitelist만 허용)
- cookie 기반 인증 (Authorization header 노출 회피)
- heartbeat 30s + auto-reconnect

**Slice 4 구현 결과**:
- ✅ `routers/sse.py::progress()` — `request.headers.get("origin")` 검증, whitelist 미일치 → 403
- ✅ cookie 기반 auth (EventSource `withCredentials=true`) — `apps/web/lib/sse.ts`
- ✅ `X-Accel-Buffering: no` header (nginx 호환)
- ✅ asyncio.sleep heartbeat 30s
- ✅ test_sse.py 4 cases — event_stream content type + 4 progress steps + event schema 정합 + invalid origin 403

### T5: SQL injection — LOW → ✅ PASS (baseline 유지)

- ✅ Supabase ORM 사용 (raw SQL 없음, `plans_repo.py` 전체 parameterized)
- ✅ migrations만 SQL — read-only schema 정의

### T6: PII 마스킹 우회 — MEDIUM → ✅ PASS (baseline 유지)

- ✅ Phase 1 `llm_security_contract.md §3.2` 마스킹 baseline 유지
- ✅ DB column 정책: plans.body JSONB (raw input 저장 시 90일 retention 의무 Phase 7+)
- ✅ agent_io_logs 미도입 (Phase 9+) — DB raw PII 누적 risk 0

**잔존 risk** (Phase 9+ 이관):
- DB column-level PII detection 자동화 부재 — Phase 9+ eval-run + audit-log 활성화 시 도입

---

## §3. 영역 1~10 점검 결과 (Slice 5 final)

| 영역 | 상태 | 근거 |
|---|---|---|
| 1. 프롬프트 인젝션 | ✅ PASS | Phase 1 baseline 유지, intent_filter 1차 방어 |
| 2. RAG 오염 | N/A | Phase 7+ |
| 3. PII | ✅ PASS | baseline 유지, Phase 9+ DB column scanning 추가 권장 |
| 4. 외부 도구 호출 | N/A | MVP 없음 |
| 5. 권한/RLS | ✅ PASS | Slice 4 0003_rls_policy.sql + auth.uid() + 4 정책 |
| 6. 입력 검증 | ✅ PASS | Pydantic schema validation + length limit (Phase 1 baseline) |
| 7. 비용 폭탄 | ✅ PASS | Critic revise max 2 + Phase 4.5 baseline + Phase 9+ per-user rate limit |
| 8. 인증/세션 | ✅ PASS | Slice 3 JWT 7일 + httpOnly cookie + logout cookie 만료 |
| 9. retention/삭제 | 🟡 PARTIAL | Phase 7+ retention 정책 도입 (DB column-level) |
| 10. 로그/감사 | 🟡 PARTIAL | Phase 9+ audit-log 활성화 |

**합계**: PASS 6 / PARTIAL 2 / N/A 2

---

## §4. Phase 6+ 권장 후속 (개선 제안)

| 항목 | 권장 phase | 우선순위 |
|---|---|---|
| Per-user rate limit (LLM quota) | Phase 9+ | ↑ |
| Audit-log (사용자 접근 + 권한 변경) | Phase 9+ | ↑ |
| Encryption at rest | Supabase 기본 제공 (별도 작업 없음) | — |
| PII column-level detection | Phase 9+ | 보통 |
| Refresh token rotation | Phase 21+ MFA 시점 | 보통 |
| pgtap (RLS 정책 SQL 자동 검증) | Phase 9+ | 보통 |
| Legacy DB 통합 (Phase 1 db/supabase_client.py + Phase 5 db/client.py) | Phase 6+ | ↑ |

---

## §5. 종합 판정

✅ **Phase 5 보안 baseline 달성 — PASS**

- T1~T6 위협 모델: 5 PASS + 1 PARTIAL (T3 refresh rotation, Phase 21+ 이관)
- 영역 1~10: 6 PASS + 2 PARTIAL (retention/audit-log, Phase 9+ 이관) + 2 N/A (RAG/외부 도구)
- Slice 3/4 실 구현이 Slice 1 권장 조치를 모두 반영
- test_auth (9) + test_rls (4) + test_sse (4) = 17 cases 모두 PASS

**Phase 6+ 진입 차단 risk 없음**. Phase 5 다음 phase (옵션 A/B/C/D 모두) 진입 가능.

---

## §6. security_metrics 갱신

`meta/security_metrics.md` (placeholder, Phase 9+ 정식 활성화):

| 영역 | 마지막 점검 | 결과 | 다음 점검 |
|---|---|---|---|
| 프롬프트 인젝션 | 2026-05-29 (Phase 5 final) | PASS | Phase 7+ RAG 본격화 시 |
| PII | 2026-05-29 (Phase 5 final) | PASS | Phase 9+ DB column scan 도입 시 |
| 권한/RLS | 2026-05-29 (Phase 5 final) | PASS (★ 첫 정식 baseline) | Phase 9+ pgtap 도입 시 |
| 인증/세션 | 2026-05-29 (Phase 5 final) | PASS (★ 첫 정식 baseline) | Phase 21+ MFA 도입 시 |
| 비용 폭탄 | 2026-05-29 (Phase 5 final) | PASS | Phase 9+ per-user rate limit 도입 시 |

---

## §7. 변경 이력

- 2026-05-29 (Phase 5 Slice 5 close): 두 번째 security-review 트리거 — Slice 1 entry 권장 조치 ↔ Slice 2~4 실 구현 verify PASS. Phase 5 보안 baseline 달성 확인.
