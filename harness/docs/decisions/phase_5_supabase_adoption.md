# ADR-020 — Phase 5 Supabase Adoption

> Date: 2026-05-29
> Status: Accepted
> Phase: 5 (DB / Auth / RLS / SSE)
> Related: ADR-018 (Critic canonical), ADR-019 (Rewriter v1.1.0), upcoming ADR-021 (RLS policy), ADR-022 (SSE Progress)
> Validation: `meta/validations/2026-05-29_phase-5-pre-entry_self.md` §V1
> Security review: `meta/security_reviews/2026-05-29_phase-5-auth-rls.md` §3 T1~T2, §10 (5)(8)

---

## Context

Phase 5는 in-memory `_plan_store` (Phase 1~6 baseline)를 영속화하고 다중 사용자 안전 운영 baseline을 확립하는 phase다. confirmed_decisions [6] 4계층 데이터 모델(User → Brand → Domain → Series → Video Project), [18] RAG candidate_knowledge 5단계 승격 (pgvector 의존), [19] PII 마스킹 + 프롬프트 인젝션 차단을 모두 영속 layer에 도입한다.

선택지는 4가지였다:

| 후보 | 강점 | 약점 |
|---|---|---|
| **A. Supabase** (PostgreSQL + pgvector + Auth + Storage + Realtime 통합) | Free tier 0원 시작 / 통합 SDK / RLS 내장 / pgvector 기본 / Auth UI 제공 | vendor lock-in (Auth + Storage 인터페이스), Free tier 한도 (500MB DB / 50K MAU) |
| B. PostgreSQL 자체 (Neon, RDS 등) | 표준 PostgreSQL, vendor lock-in 최소 | Auth/Storage 별도 구현 (예: NextAuth + S3) → 운영 부담 ↑, MVP 속도 ↓ |
| C. Firebase | 빠른 시작, 모바일 우호 | 표준 NoSQL → pgvector 미지원 (Phase 7 RAG 비호환), 4계층 관계형 모델 부적합 |
| D. 자체 서버 | 완전 제어 | 인프라 비용 + 보안 부담 + DevOps 인력 + MVP 속도 ▼▼ |

Phase 5는 **15~20h 5 Slice** 예상이며, 솔로/소규모 팀 운영을 전제로 한다. MVP 단계에서 운영 부담 최소화가 핵심 제약이다.

---

## Decision

**Supabase를 채택한다.**

채택 사유:

1. **통합 인프라**: PostgreSQL + pgvector + RLS + Auth + Storage + Realtime을 단일 SDK로 제공 → Phase 5 (Auth + DB + RLS + SSE) 작업이 한 platform 위에서 일관됨. Phase 7 RAG 진입 시 pgvector를 별도 도입할 필요 없음 (confirmed_decision [18] 정합).

2. **Free tier 0원 시작**: 500MB DB + 50K MAU + 2GB Storage + 1GB egress / month. MVP 운영 단계에서 비용 0으로 시작 가능 (cost-review Phase 9+ 시점에 quota 추적 시작).

3. **표준 PostgreSQL**: Supabase는 PostgreSQL 위에 얇은 layer (PostgREST + GoTrue + Realtime). DB 자체는 vanilla PostgreSQL → Phase 21+ 자체 PostgreSQL (Neon, RDS, 자체 서버) 마이그가 가능. Auth/Storage 부분만 재구현 비용 (lib/auth.ts 추상화로 일부 흡수).

4. **RLS 내장**: Row Level Security는 PostgreSQL 표준 기능이지만, Supabase는 `auth.uid()` 함수와 Auth + JWT 통합 자동 (별도 구현 불필요). Phase 5 confirmed_decision [6] 다중 사용자 보안 baseline의 핵심.

5. **Auth 보안 baseline**: GoTrue (Supabase Auth)는 OAuth2 / OTP / Magic Link / Email+Password 모두 지원. JWT verify + refresh token rotation (Slice 3 옵션 활성화 가능) baseline 제공 → 자체 구현 시 보안 risk ↓.

6. **Phase 진입 속도**: Phase 5 acceptance 10개 중 7개가 Supabase 통합 기능 위에서 직접 검증 가능 (A1 Supabase mock / A2 schema / A3 plans_repo / A4 Auth JWT / A5 frontend login / A6 RLS / A7 SSE). 자체 구현 시 추가 ~10h.

---

## Constraints

### Vendor lock-in

- **Auth + Storage 인터페이스**는 Supabase 전용 → Phase 21+ 마이그 시점 재구현 비용 발생
- **완화 방법**:
  - `lib/auth.ts` 추상화 계층 도입 (Slice 3) — provider 교체 가능성 일부 확보
  - 직접 SQL은 표준 PostgreSQL 문법 강제 → DB layer는 마이그 비용 최소
  - service_role key + RLS 정책 SQL은 표준 PostgreSQL 호환

### Free tier 한도

- **DB**: 500MB → MVP 단계 충분, 초과 시 $25/mo Pro
- **MAU**: 50K → MVP 단계 충분
- **Storage**: 2GB → 영상 자동 편집 NG14 정합 (영상 파일 저장 X) → 충분
- **Egress**: 1GB/month → SSE + API 응답 + 페이지 로드 합산 시 초과 가능 (Phase 11+ 모니터링 시작)
- **추적**: Phase 11+ cost-review Skill로 quota 추적 시작 (현 Phase 외)

### Provider 단일 의존

- Supabase outage 시 영향 100%
- **완화**: graceful fallback 유지 (Slice 2 plans_repo.py에서 Supabase 실패 시 _plan_store dict 임시 유지)
- 완전 차단 발생 시 hotfix phase 진입 (security-review Skill §4 절차)

---

## Trade-offs

| 영역 | 채택안 (Supabase) | 대안 (자체 PostgreSQL) | 선택 사유 |
|---|---|---|---|
| MVP 속도 | ▲▲▲ | ▼ | MVP 우선 |
| Vendor lock-in | ▼ (중간) | ▲▲ | 빠른 MVP 가치가 vendor risk 상회 |
| 운영 부담 | ▼ (낮음) | ▲▲ (인프라 + Auth + Storage 직접) | 솔로 운영 |
| 비용 (초기) | $0 (Free tier) | $20+/mo (Neon Pro 등) + 직접 인프라 | Free tier 활용 |
| 비용 (장기) | $25/mo + 초과 가산 | 직접 인프라 비용 (대규모 시 ▼) | Phase 21+ 재평가 |
| Auth 보안 | GoTrue baseline 제공 | 자체 구현 (보안 risk ↑) | Supabase 보안 baseline 의존 |
| RLS 도입 | 자동 (auth.uid() 통합) | 자체 구현 (JWT verify + 정책 SQL) | 빠른 구현 |
| pgvector | 기본 제공 | 별도 도입 필요 | Phase 7 RAG 호환 |
| 마이그 가능성 | DB layer 가능, Auth/Storage 재구현 | 완전 자유 | DB 단계 표준 PostgreSQL 유지 |

---

## Implementation impact

### Phase 5 (현)

- **Slice 2**: Supabase python client 도입 (`supabase` package) + `db/client.py` + 환경변수 (`SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_KEY`)
- **Slice 2**: db_schema.md 신규 + 0001_init.sql (4계층 + plans + users) + 0002_phase_4_5_revise_history.sql
- **Slice 2**: plans_repo.py 신규 — graceful fallback (Supabase 실패 시 _plan_store dict)
- **Slice 3**: Supabase Auth (signInWithPassword) + lib/auth.ts (JS client + httpOnly cookie)
- **Slice 4**: 0003_rls_policy.sql + auth.uid() 강제 (ADR-021)
- **Slice 4**: SSE — Supabase Realtime은 미사용 (FastAPI StreamingResponse 직접, ADR-022)

### Phase 7+ (RAG)

- pgvector extension 활성화 (Supabase 기본 제공) + `rag_chunks` 테이블 + embedding 컬럼
- candidate_knowledge 5단계 승격 pipeline (confirmed_decision [18]) DB 영속

### Phase 11+ (cost-review)

- Supabase quota 추적 (DB / MAU / Storage / Egress)
- cost-review Skill 활성 (현재 unused)

### Phase 21+ (확장)

- Supabase → 자체 PostgreSQL 마이그 검토 시점 (50K MAU 초과 + Pro tier 비용 vs 자체 인프라)
- Auth/Storage 재구현 (또는 외부 IDP — Auth0, Cognito 등)

---

## Security implications

(상세는 `meta/security_reviews/2026-05-29_phase-5-auth-rls.md` 참조)

- **T1 JWT 누수**: Supabase Auth + httpOnly cookie (Slice 3 의무) → mitigated
- **T2 RLS 우회**: anonymous/authenticated endpoint 분리 + RLS 정책 SQL (Slice 4 ADR-021) → mitigated
- **T3 Refresh token**: Supabase 기본 + rotation (Slice 3 옵션) → MEDIUM 잔존
- **T4 SSE hijacking**: Origin 검증 + cookie 의존 (Slice 4 ADR-022) → mitigated
- **T5 SQL injection**: Supabase ORM (PostgREST) parameterized → mitigated
- **T6 PII**: llm_security_contract baseline 유지 → Phase 9+ 강화

---

## Rollback policy

본 ADR 채택을 철회해야 하는 시나리오:

1. Supabase Free tier 한도 초과 + Pro tier 비용이 자체 인프라 대비 명백히 비효율
2. Supabase 측 보안 인시던트 / 신뢰 손상
3. Phase 21+ 자체 PostgreSQL + 외부 IDP 도입 결정 시 (정상 evolution)

**철회 시 절차**:
1. 새 ADR (ADR-NNN) 작성 — 철회 사유 + 후속 provider 결정
2. contract-change Skill로 `docs/contracts/db_schema.md` + `docs/contracts/llm_security_contract.md` §5 갱신
3. lib/auth.ts 추상화 계층 활용 → Auth provider 교체 (frontend 영향 최소화)
4. DB layer는 표준 PostgreSQL 호환 → 데이터 export/import만 (Supabase pg_dump 표준 호환)

**예상 마이그 비용** (Phase 21+ 시점, 참고):
- DB layer: ~4~8h (pg_dump + 자체 PostgreSQL import + 환경변수 변경)
- Auth layer: ~16~24h (Auth provider 교체 + lib/auth.ts 재작성 + 사용자 재인증 통보)
- Storage layer: ~4~8h (현재 미사용, Phase 21+ 도입 시 평가)

---

## References

- Validation: `meta/validations/2026-05-29_phase-5-pre-entry_self.md` §V1 Supabase 채택 PASS
- Security: `meta/security_reviews/2026-05-29_phase-5-auth-rls.md` §3 T1~T6 권장 조치
- Contract baseline: `docs/contracts/llm_security_contract.md` §5 시스템 prompt 격리, §6 RAG poisoning, §7 비용 보호
- Phase 6 closing: `phases/archive/phase-6-output-schema-stabilization/closing_notes.md` (Phase 5 진입 체크리스트)
- confirmed_decisions: [6] 4계층 모델, [18] RAG 5단계 승격, [19] PII + 인젝션 차단
- Phase 5 entry: `phases/active/phase-5-db-auth/goals.md` G1~G7, `acceptance.md` A1~A10
- Upcoming ADRs: ADR-021 (RLS policy, Slice 4), ADR-022 (SSE Progress, Slice 4)

---

## 변경 이력

```
v1.0.0 (2026-05-29): Phase 5 Slice 1 entry. Supabase 채택 결정 — 대안 비교 +
                      Free tier 활용 + RLS 내장 + pgvector 호환 + vendor
                      lock-in trade-off 명시. Slice 2~4 구현 가이드 + Phase 7+
                      RAG / Phase 11+ cost-review / Phase 21+ 마이그 계획 포함.
```
