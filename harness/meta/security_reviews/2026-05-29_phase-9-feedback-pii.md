# Phase 9 Security Review — 피드백 reason PII + reject 사유 + RLS user 격리 + GET 권한 (★ 두 번째 정식 트리거)

> Date: 2026-05-29
> Reviewer: Claude Code (self, security-review Skill 절차 따름)
> Trigger: Phase 9 entry — 피드백/선택 영속화 도입 (자유 입력 reason text → PII 신규 저장 surface)
> Skill: `.claude/skills/security-review/SKILL.md` v1.0.0 (트리거 조건 §1 "새 사용자 입력 경로 추가" + §5 "사용자 권한 정책 변경" — Phase 9 entry 로 차용)
> 트리거 순번: **두 번째 정식** (Phase 5 Slice 1 첫 정식 + Slice 5 final 에 이은 — P-SECURITY-REVIEW-001 2-trigger 패턴 강화)
> External review: 사용자 외부 진행 권장 (placeholder — `meta/validations/2026-05-29_phase-9-pre-entry_external.md` §Security-focused 추가 질문 S1~S5)
> Related contract: `docs/contracts/llm_security_contract.md` (§3.2 PII 검출+마스킹 + §4.4 잔존 + §8 E-SEC-006) + `docs/contracts/db_schema.md` (§5.2 feedback_events + §4.3 selected_plans + §9 RLS)

---

## §1. Scope 정의

### 검토 대상

1. **피드백 reason text 영속화** (Slice 2~3) — feedback_events.reason 자유 입력(like/dislike/reject/regenerate + reason) → PII 신규 저장 surface
2. **reject 사유 저장** (Slice 2~3) — 반려 이유 자유 입력 → 민감 정보(불만/감정/타인 식별자) 저장
3. **RLS user 격리** (Slice 2) — feedback_events.user_id / selected_plans 의 auth.uid() 격리 (다른 user 피드백 접근 차단)
4. **GET /plans/{id}/feedback 권한** (Slice 3) — 본인 plan 의 피드백만 조회 (Phase 5 plans RLS 정합)
5. **feedback → candidate_knowledge 적재 PII** (Slice 4) — RAG 승격 전 quality_filter PII 차단 (pending 단계)
6. **SQL injection baseline** (Supabase ORM) — selection/feedback endpoint 신규 입력 경로

### 미검토 (Phase 외)

- **NG1** P-AUX-2 brand_memory_extractor agent 실 구현 (Phase 10+) — 본 review 는 적재 경로(pending)까지만
- **NG12** RAG candidate 자동 promotion (Phase 11+) — 승격 보안은 rag-update Skill 두 번째 시점
- **Phase 11+** privacy_contract / user_consent_contract / data_retention_policy 본체 (placeholder — 본 review 는 baseline + 저장 전 마스킹 도입까지)
- **Phase 21+** MFA / refresh token rotation (Phase 5 T3 이관 유지)

### 본 review 가 다루지 않는 일반 보안 (외부 도구로 위임)

- 인프라 보안 (Supabase 측 — SOC 2 등)
- DDoS / WAF (Cloudflare, Phase 11+)
- 정기 dependency vulnerability scan (별도 운영 절차)

---

## §2. 위협 모델 (Threat Model)

llm_security_contract.md §0 의 위협 모델(PII 유출 + RAG 오염)에 Phase 9 피드백 도입 위협 6가지를 매핑:

| ID | 위협 | 영향 | 가능성 | 우선순위 | llm_security 매핑 |
|---|---|---|---|---|---|
| **T1** | 피드백 reason text PII (자유 입력 이메일/전화/주민/카드 등) → DB raw 저장 | 개인정보 노출 + retention 의무 증가 (raw PII 잔존) | 중 | **HIGH** | §3.2 PII 마스킹 + §4.4 잔존 + §8 E-SEC-006 |
| **T2** | reject 사유 저장 — 민감 정보 (불만/감정/타인 식별자/맥락) raw 저장 | 민감 정보 누적 + 노출 시 신뢰 손상 | 중 | MEDIUM | §3.2 + retention(Phase 11+) |
| **T3** | RLS user 격리 우회 (feedback_events.user_id ≠ auth.uid() 정책 bug / anon 접근) | 다른 user 피드백/선택 노출 | 중 | **HIGH** | §5 권한 / db_schema §9 RLS / Phase 5 T2 계승 |
| **T4** | GET /plans/{id}/feedback 권한 (본인 아닌 plan 의 피드백 조회) | 다른 user 피드백 history 노출 | 중 | **HIGH** | §5 권한 / Phase 5 plans RLS 정합 |
| **T5** | feedback → candidate_knowledge 적재 시 PII 누출 (RAG 승격 전 quality_filter 미통과 raw 진입) | PII 가 RAG 에 진입 → 다른 user 검색 결과 노출 | 낮 | MEDIUM | §RAG layer 5 + §3.2 + 영역 2 |
| **T6** | SQL injection (selection/feedback endpoint 신규 입력 — Supabase ORM 우회 / raw SQL 실수) | DB 손상 + 데이터 유출 | 매우낮 | LOW | §3.4 입력 검증 (Phase 5 T5 계승) |

### 신규 위협 (Phase 9 도입 결과)

- **T1 핵심 신규 surface**: Phase 1~8 PII 마스킹 baseline 은 LLM 호출 직전(§3.2)/응답(§4.4) 대상. 피드백 reason 은 **LLM 호출 없이 직접 DB 저장**되는 자유 입력 경로 → 기존 hook 미적용 신규 surface. Phase 5 T6("DB 저장 전 재검사 도입 시점 = Phase 9+") 의 실현 지점.
- **T1+T5 chain**: 마스킹 안 된 reason 이 candidate_knowledge 로 적재(T5) → RAG 승격 시 다른 user 노출 → 저장 전 마스킹(T1) + quality_filter(T5) 이중 방어 필수.

---

## §3. 권장 조치

### T1: 피드백 reason PII — HIGH

**현 상태**: feedback_events.reason 미구현 (Slice 2 0005 migration 신규). 피드백 reason 은 자유 입력 text.

**권장**:
- **저장 전 마스킹 (시점 결정)**: feedback_repo INSERT **직전** llm_security §3.2 직접 식별자 패턴(전화 `\d{2,3}-\d{3,4}-\d{4}` / 이메일 / 주민 / 카드 / IP) 재검사 + 마스킹 (case B — 마스킹 후 저장). 조회 시 마스킹은 raw PII 가 DB 에 잔존하여 retention 의무 증가 → **저장 전 우선**.
- **warnings 기록**: 마스킹 적용 시 응답 validation.warnings 또는 로그에 "pii_masked" 기록 (§3.2 case B 정합).
- **E-SEC-006 매핑**: 사용자 자기 정보 추정(case A — "제 전화번호 화면에...")은 차단 옵션 / 일반 reason 의 PII 는 마스킹 후 저장.
- **Phase 9 범위**: 저장 전 마스킹 baseline 적용. 정교한 한국어 PII 라이브러리 / 명시 동의 절차는 Phase 11+ (privacy_contract).

**Acceptance 매핑**: A3 feedback 영속 + (선택) feedback reason 마스킹 test

### T2: reject 사유 저장 — MEDIUM

**현 상태**: event_type='reject' + reason 미구현 (Slice 2 신규).

**권장**:
- **민감 정보 인지**: reject 사유는 불만/감정/타인 식별자/맥락 포함 가능 → T1 저장 전 마스킹 동일 적용.
- **retention 정책 baseline**: db_schema §10 "feedback_events → 2년 보관 후 익명화" 정합. 본격 retention 자동화는 Phase 11+ (data_retention_policy placeholder).
- **노출 최소화**: reject 사유는 GET 조회 시 본인만(T4) + RLS(T3) — 운영 dashboard 노출 시 마스킹(영역 3).

**Acceptance 매핑**: A3 feedback 영속 (reject event_type 포함)

### T3: RLS user 격리 — HIGH

**현 상태**: feedback_events / selected_plans RLS 미작성 (Slice 2 0005 migration 신규 — Phase 5 RLS 패턴 계승).

**권장**:
- **RLS 정책 SQL** (Slice 2 0005 migration — Phase 5 0003_rls_policy.sql 패턴):
  ```sql
  alter table feedback_events enable row level security;
  create policy feedback_user_isolation on feedback_events
    for all
    using (user_id = auth.uid())
    with check (user_id = auth.uid());

  alter table selected_plans enable row level security;
  -- selected_plans 는 plan_id → plans 정합 → plans RLS(auth_user_id) 2-hop subquery
  create policy selected_plans_user_isolation on selected_plans
    for all
    using (plan_id in (select id from plans where auth_user_id = auth.uid() or auth_user_id is null))
    with check (plan_id in (select id from plans where auth_user_id = auth.uid()));
  ```
- **자동 검증** (Slice 2 test_selection_feedback.py — mock 환경에서는 graceful in-memory, 실 Supabase RLS 는 운영 검증): user_a 가 user_b feedback 조회 → 차단.
- **graceful 정합**: in-memory fallback(mock) 시 RLS 미적용 → 실 Supabase 에서만 RLS 강제 (V5 risk 명시).

**Acceptance 매핑**: A1~A3 (selection/feedback RLS 정합)

### T4: GET /plans/{id}/feedback 권한 — HIGH

**현 상태**: GET endpoint 미구현 (Slice 3 routers/plans.py 신규).

**권장**:
- **본인 plan 검증**: GET /plans/{id}/feedback 은 plan_id → plans.auth_user_id = auth.uid() 검증 후 해당 plan 의 feedback 만 반환 (Phase 5 plans RLS 정합).
- **404 vs 403**: 다른 user plan_id 조회 → 404(존재 노출 회피) 또는 403 — Phase 5 패턴(404 권장).
- **anonymous 처리**: auth_user_id IS NULL(게스트 plan, Phase 5 anon endpoint)은 RLS `or auth_user_id is null` 정합 — 단 feedback_events.user_id 는 NOT NULL(user_profiles 참조) → 게스트 피드백은 Phase 9 범위 외(authenticated only).

**Acceptance 매핑**: A5 API endpoints (GET feedback 권한)

### T5: feedback → candidate_knowledge 적재 PII — MEDIUM

**현 상태**: rag/feedback_to_candidate.py 미구현 (Slice 4 신규 — source_kind='user_feedback'/'user_choice', status='pending').

**권장**:
- **이중 방어**: ① feedback reason 저장 전 마스킹(T1) 적용 후 candidate content 진입 + ② Phase 7 5단계 quality_filter(layer 5 promoted INSERT 직전 PII 잔존 검사 — llm_security §RAG) — pending 단계는 RAG 노출 전이므로 다른 user 영향 0.
- **pending 고정**: 적재는 status='pending' 까지만 — 자동 승격 X (NG12). 승격은 rag-update Skill(Phase 11+).
- **source_id 추적**: candidate.source_id 로 feedback/selection 원본 추적 (PII 삭제 요청 시 역추적 — 영역 9).

**Acceptance 매핑**: A7 Brand Memory 준비 (feedback→candidate 적재 pending)

### T6: SQL injection — LOW

**현 상태**: Supabase ORM (PostgREST) 기본 사용 → parameterized query 자동 (Phase 5 T5 계승).

**권장**:
- **ORM 강제**: selection/feedback repo 는 Supabase python client(.table().insert/select) 사용 — 직접 SQL 작성 0.
- **migration 정적**: 0005_feedback_selection.sql 은 idempotent + 입력 변수 없음 (정적 schema 정의).
- **input validation**: SelectRequest/FeedbackRequest Pydantic schema validation (event_type enum like/dislike/reject/regenerate + option_index 0–2 범위 + reason 길이 제한).

**Acceptance 매핑**: 별도 acceptance X (baseline 유지)

---

## §4. 영역별 점검 결과 (security-review SKILL §점검 영역 1~10)

| 영역 | 점검 항목 (요약) | 결과 | 비고 |
|---|---|---|---|
| 1. 프롬프트 인젝션 | llm_security §3.3 baseline (피드백 reason 은 LLM 호출 없음 — 직접 DB) | **PASS** (baseline 유지) | 피드백 reason 은 LLM-facing 아님 → 인젝션 surface 아님 |
| 2. RAG 오염 | feedback → candidate 적재 (pending + quality_filter, 자동 승격 X) | **PARTIAL** → Slice 4 적재 경로 + quality_filter 후 PASS | T5 — pending 단계, 승격은 NG12 |
| 3. PII 노출 | 피드백 reason / reject 사유 저장 전 마스킹 (T1+T2) | **PARTIAL** → Slice 2~3 저장 전 마스킹 후 PASS | T1 신규 surface (Phase 5 T6 실현) |
| 4. 외부 도구 호출 | LLM tool use 없음 (피드백은 repo CRUD) | **N/A** | 변경 0 |
| 5. 권한 / RLS | feedback_events / selected_plans RLS (T3) + GET 권한 (T4) | **PARTIAL** → Slice 2 RLS + Slice 3 GET 권한 후 PASS | 본 Slice 1 시점 미구현 |
| 6. 입력 검증 | SelectRequest/FeedbackRequest Pydantic (event_type enum + option_index 0–2 + reason 길이) | **PARTIAL** → Slice 3 schema 후 PASS | T6 baseline |
| 7. 비용 폭탄 | 피드백은 LLM 호출 없음 (repo CRUD) — rate_limit baseline | **PASS** (baseline 유지) | 피드백 자체 비용 0 (적재 quality_filter 만 P-EVAL-1) |
| 8. 인증 / 세션 | Phase 5 JWT + httpOnly cookie baseline (feedback endpoint authenticated) | **PASS** (baseline 유지) | feedback/select 는 authenticated role |
| 9. 데이터 보존 / 삭제 | db_schema §10 feedback_events 2년 후 익명화 (retention placeholder) | **N/A** (Phase 11+) | retention 자동화 placeholder |
| 10. 로그 / 감사 추적 | agent_io_logs + errors.log baseline + pii_masked warnings (T1) | **PASS** (baseline 유지) | 마스킹 적용 warnings 기록 |

### 종합

- **PASS**: 5 영역 (1, 4·N/A, 7, 8, 10) + N/A 2 (4, 9)
- **PARTIAL → PASS 예정**: 4 영역 (2, 3, 5, 6) — Slice 2~4 구현 후 PASS 달성
- **N/A**: 2 영역 (4 외부 도구, 9 retention Phase 11+)

---

## §5. 보안 baseline

Phase 9 entry 시점 baseline (Slice 1):

- [x] llm_security_contract.md §3 Step 1 자동 검사 baseline 유지 (intent_filter + PII + injection + XSS + 길이)
- [x] llm_security_contract.md §4 Step 2 자동 검사 baseline 유지 (schema + 광고 + PII 잔존 + sanitize)
- [x] llm_security_contract.md §3.2 PII 직접 식별자 패턴 baseline (전화/이메일/주민/카드/IP)
- [x] Phase 5 Auth + JWT httpOnly cookie + RLS 정책 baseline 유지 (T3/T4 정합 기반)
- [x] Phase 7 5단계 quality_filter PII 차단 baseline 유지 (T5 정합 기반)

Phase 9 Slice 2~4 도입 (PARTIAL → PASS 예정):

- [ ] 피드백 reason / reject 사유 저장 전 §3.2 PII 마스킹 (T1+T2) — Slice 2~3
- [ ] feedback_events / selected_plans RLS 정책 (T3) — Slice 2 (0005 migration, Phase 5 패턴)
- [ ] GET /plans/{id}/feedback 본인 plan 권한 (T4) — Slice 3
- [ ] feedback → candidate 적재 quality_filter PII 차단 (T5) — Slice 4 (pending + 자동 승격 X NG12)
- [ ] SelectRequest/FeedbackRequest Pydantic 입력 검증 (T6) — Slice 3

Phase 11+ 강화 (장기):

- [ ] privacy_contract / user_consent_contract / data_retention_policy 본문 (placeholder → 본문)
- [ ] feedback_events 2년 후 익명화 자동화 (retention)
- [ ] 한국어 PII 라이브러리 (false negative 최소화)

---

## §6. 외부 검토 권장

본 self review 는 단일 모델 (Claude Code). **사용자가 외부 GPT/Gemini 로 검토 권장**:

### 외부 LLM 에 추가 질문 권장 항목

1. **피드백 reason PII 마스킹 시점** — 저장 전 vs 조회 시 best practice + retention 영향
2. **한국어/영어 혼용 PII detection** — false negative 최소화 라이브러리/패턴
3. **RLS 2-hop subquery (selected_plans → plans)** — 성능/우회 알려진 케이스
4. **GET feedback 권한 (404 vs 403)** — 존재 노출 회피 표준
5. **feedback → candidate PII 누출** — RAG 승격 전 quality_filter 가 충분한가, 추가 layer 권장?
6. **reject 사유 retention** — 민감 정보(불만/감정) 저장 기간 + 익명화 권장

### 외부 검토 결과 처리

- **PASS** 일치: notes.md 에 기록만, Phase 9 진행 계속
- **차이** 있음: Phase 9 notes.md §외부 검토 차이에 기록 + Slice 6 회고 §개선 제안 반영
- **Critical 차이**: Slice 2 진입 전 사용자 알림 + 차단 검토 (예: 저장 전 마스킹 대신 차단 권장 등)

---

## §7. 후속 조치 (Slice 매핑)

| Slice | 조치 항목 | 검증 |
|---|---|---|
| **Slice 1** (현) | 본 security-review 작성 + ADR-030/031/032 + external placeholder | meta/security_reviews/2026-05-29_phase-9-feedback-pii.md 존재 |
| **Slice 2** | 0005 migration (feedback_events/selected_plans/brand_memory_entries + RLS T3) + repo graceful | RLS 정책 SQL (Phase 5 패턴) + db_schema contract-change |
| **Slice 3** | select/feedback endpoint + 저장 전 PII 마스킹(T1) + GET 권한(T4) + Pydantic(T6) | endpoint test + 본인 plan 권한 |
| **Slice 4** | feedback → candidate 적재(T5) — pending + quality_filter + 자동 승격 X (NG12) | test_brand_memory_prep (pending 적재) |
| **Slice 6** | (선택) security 후속 검증 + retrospective §보안 반영 | security_metrics row 갱신 권장 |

---

## §8. Acceptance

Phase 9 종료 시점 (Slice 6):

- [ ] 피드백 reason / reject 사유 저장 전 PII 마스킹 baseline 적용 (T1+T2)
- [ ] feedback_events / selected_plans RLS 정책 (T3) — 0005 migration
- [ ] GET /plans/{id}/feedback 본인 plan 권한 (T4)
- [ ] feedback → candidate 적재 pending + quality_filter PII 차단 (T5, 자동 승격 X)
- [ ] SelectRequest/FeedbackRequest Pydantic 입력 검증 (T6)
- [ ] llm_security_contract.md baseline 유지 (Phase 1~8 회귀 0)

---

## §9. Critical 발견 처리 (security-review SKILL §4)

본 review 에서 Critical 발견 X (PARTIAL 4건은 의도된 Slice 2~4 구현 대기).

**만약 Slice 2~4 진행 중 Critical 발견 시**:
1. 영향 영역 즉시 비활성화 (feature flag)
2. hotfix phase 진입 (별도 phase 또는 Slice 추가)
3. meta-retrospective 즉시 트리거
4. contract-change Skill 로 llm_security_contract.md 또는 privacy_contract.md 강화 검토
5. 사용자에게 영향 통지 (해당 시)

---

## §10. security_metrics 등록 (security-review SKILL §5)

`meta/security_metrics.md` 에 Phase 9 row 추가 (Slice 6 에서 갱신):

```
| 영역 | 마지막 점검 | 결과 | 다음 점검 |
|------|------------|------|-----------|
| 프롬프트 인젝션 (1) | 2026-05-29 | PASS (baseline) | 정기 (월 1회) |
| RAG 오염 (2) | 2026-05-29 | PARTIAL → Slice 4 후 PASS | RAG 변경 시 / Phase 11+ 자동 promotion |
| PII (3) | 2026-05-29 | **PARTIAL → Slice 2~3 저장 전 마스킹 후 PASS** | Phase 11+ privacy_contract 본문 |
| 외부 도구 (4) | N/A | N/A | Phase 11+ |
| 권한 / RLS (5) | 2026-05-29 | **PARTIAL → Slice 2~3 후 PASS** | Phase 9 Slice 6 |
| 입력 검증 (6) | 2026-05-29 | PARTIAL → Slice 3 후 PASS | 정기 (월 1회) |
| 비용 폭탄 (7) | 2026-05-29 | PASS (baseline) | Phase 11+ cost-review |
| 인증 / 세션 (8) | 2026-05-29 | PASS (Phase 5 baseline) | Phase 21+ MFA |
| 데이터 보존 (9) | N/A | N/A | Phase 11+ retention_policy |
| 로그 / 감사 (10) | 2026-05-29 | PASS (baseline + pii_masked warnings) | 정기 (월 1회) |
```

본 row 는 Slice 6 close 직후 `meta/security_metrics.md` 에 반영 권장 (Phase 9 closing notes).

---

## §11. 변경 이력

```
v1.0.0 (2026-05-29): Phase 9 entry — security-review Skill ★ 두 번째 정식 트리거 (Phase 5 첫 정식 + final 에 이은).
                      §1 Scope (피드백 reason PII + reject + RLS + GET 권한 + candidate 적재) +
                      §2 Threat Model T1~T6 + §3 권장 조치 + §4 영역 1~10 점검 (5 PASS/N-A + 4 PARTIAL) +
                      §5 baseline + §6 외부 검토 권장 + §7 Slice 매핑 + §8 Acceptance +
                      §9 Critical 처리 + §10 security_metrics 등록. P-SECURITY-REVIEW-001 2-trigger 패턴 강화 (Phase 5 + Phase 9).
```

---

**End of Phase 9 Security Review v1.0.0 — security-review Skill ★ second formal trigger (피드백 PII).**
