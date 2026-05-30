# ADR-030 — Phase 9 Feedback / Selection Persistence (실 plans 테이블 정합)

> Date: 2026-05-29
> Status: Accepted
> Phase: 9 (결과 저장 + 피드백)
> Slice: 2~3 (구현) / Slice 1 (본 ADR 결정)
> Related: ADR-020 (phase_5_supabase_adoption — PlansRepo graceful), ADR-021 (phase_5_rls_policy — RLS user 격리 패턴),
>          ADR-031 (phase_9_brand_memory_prep — feedback→candidate 적재 cross-ref), ADR-032 (phase_9_critic_canonical_wiring)
> Skill: contract-change (Slice 2 — db_schema.md feedback/selection) + security-review (Slice 1 — 피드백 PII T1~T6)

## Context

db_schema.md 는 결과 저장 / 피드백 테이블을 **정의만** 보유하고 미구현(0001~0004 migration 만 반영):

- §4.3 `selected_plans` — `video_id`(PK) + `selected_option_id`(→ plan_options.option_id) + `selection_reason` — **4계층 idealized 정의**
- §4.2 `plan_options` — `option_id`(PK) + `video_id`(FK) + `option_index`(0–2) — 4계층 idealized, migration 미반영
- §5.2 `feedback_events` — `user_id` + `target_kind` + `target_id` + `event_type`(like/dislike/reject/regenerate) + `reason` — 정의만

**Gap (entry 시점)**:

- ★ 실 영속화는 **§3.6 `plans` 테이블**(Phase 5 Slice 2) — `id`(PK) + `plan_candidates`(JSONB 3-plan) + `recommended_plan_index`(0~2) + `critic_evaluation`(JSONB) + `auth_user_id`. plan_options 테이블은 **미생성**.
- db_schema §4.3 `selected_plans`(selected_option_id → plan_options.option_id)는 **4계층 full linkage** 전제 → plan_options 미존재 시 구현 불가.
- 즉 Phase 9 결과 저장 / 피드백은 **실 `plans` 테이블 정합**(plan_id + plan_candidates JSONB 배열 인덱스)으로 구현해야 하며, idealized plan_options 4계층은 Phase 11+ (NG2).
- 피드백 reason 은 자유 입력 text → PII 신규 저장 surface (security-review T1).

## Decision

### 1. selected_plans — 실 plans 테이블 정합

`0005_feedback_selection.sql`(Slice 2 신규)에 **실 plans 정합** selected_plans 신규:

| 컬럼 | 타입 | 정합 |
|---|---|---|
| `selection_id` | uuid PK | gen_random_uuid() |
| `plan_id` | uuid (→ plans.id) | 실 plans 테이블 참조 (NOT video_id) |
| `selected_option_index` | smallint, check between 0 and 2 | plan_candidates JSONB 배열 인덱스 (3-plan 중 선택) |
| `selection_reason` | text | 사용자 선택 사유 (PII 저장 전 마스킹 — T1) |
| `auth_user_id` | uuid | RLS 정합 (Phase 5 패턴) |
| `selected_at` | timestamptz | now() |

- 선택 plan 내용은 `plan_candidates[selected_option_index]` 로 조회 (4계층 미연결 무관).
- db_schema §4.3 idealized `selected_plans`(selected_option_id → plan_options)는 **Phase 11+ 4계층 full linkage** 로 명시 분리 (NG2). plan_options 테이블 신규 생성 X.

### 2. feedback_events — 실 plans 정합 + reason

`0005` 에 feedback_events 신규 (db_schema §5.2 정합 + 실 plans 연결):

| 컬럼 | 타입 | 정합 |
|---|---|---|
| `feedback_id` | uuid PK | gen_random_uuid() |
| `user_id` / `auth_user_id` | uuid | RLS 정합 (authenticated) |
| `plan_id` | uuid (→ plans.id) | 실 plans 테이블 참조 |
| `event_type` | text, enum | like / dislike / reject / regenerate |
| `reason` | text | 자유 입력 (PII 저장 전 마스킹 — T1, reject 사유 T2) |
| `created_at` | timestamptz | now() |

- target_kind/target_id(db_schema §5.2 idealized 4계층)는 plan_id 정합으로 단순화 (Phase 9 범위 — plan 단위 피드백).

### 3. SelectionRepo / FeedbackRepo — graceful (PlansRepo 패턴)

`db/repositories/selection_repo.py` + `feedback_repo.py`(Slice 2 신규) — PlansRepo graceful 패턴 계승:

```python
class SelectionRepo:
    def __init__(self, supabase_client=None, in_memory_store=None): ...
    async def select(self, plan_id, option_index, reason=None) -> dict: ...  # graceful Supabase or in-memory
    async def get(self, plan_id) -> dict | None: ...

class FeedbackRepo:
    async def record(self, plan_id, event_type, reason=None) -> dict: ...
    async def list(self, plan_id) -> list[dict]: ...
```

- Supabase 실패(URL/Key 미설정, 패키지 미설치, 연결 에러) 시 in-memory dict fallback — raise 금지 (P-GRACEFUL-001).
- `db/__init__.py` 에 SelectionRepo / FeedbackRepo export (additive).

### 4. API endpoints — thin adapter (Slice 3)

`routers/plans.py`(Slice 3 수정):
- POST /plans/{id}/select — repo.select 호출 (option_index 0–2 + reason 저장 전 PII 마스킹)
- POST /plans/{id}/feedback — repo.record 호출 (event_type enum + reason 마스킹)
- GET /plans/{id}/feedback — repo.list 호출 (본인 plan 권한 — T4)

`schemas/plans.py`(Slice 3): SelectRequest / FeedbackRequest / SelectionResponse / FeedbackResponse Pydantic (event_type enum + option_index 0–2 + reason 길이 제한 — T6).

## Constraints

- **실 plans 테이블 정합 ★**: selected_plans / feedback_events 는 `plan_id`(→ plans.id) + `selected_option_index`(0–2, plan_candidates JSONB 배열 인덱스) 정합. db_schema §4.3 idealized `selected_plans`(selected_option_id → plan_options.option_id) + §4.2 plan_options 테이블은 **Phase 11+ 4계층 full linkage (NG2)** — Phase 9 plan_options 테이블 신규 생성 X (참조만).
- **additive only**: 신규 테이블 3종(selected_plans/feedback_events + brand_memory_entries ADR-031) + repo 3종 — 기존 plans/plan_candidates 컬럼 + PlansRepo + db/client + migrations 0001~0004 **0 변경** → Phase 8 baseline(pytest 249) 회귀 0.
- **RLS user 격리 ★**: feedback_events.user_id = auth.uid() + selected_plans 는 plan_id → plans.auth_user_id 2-hop subquery (Phase 5 0003_rls_policy.sql 패턴 — security-review T3). in-memory fallback(mock) 시 RLS 미적용 → 실 Supabase 에서만 강제.
- **피드백 reason PII ★**: feedback reason / selection_reason / reject 사유는 llm_security §3.2 직접 식별자 패턴 **저장 전 마스킹**(feedback_repo INSERT 직전 — security-review T1+T2, E-SEC-006). Phase 5 T6("DB 저장 전 재검사 = Phase 9+")의 실현.
- **graceful (PlansRepo 패턴)**: Supabase 실패 시 in-memory fallback, raise 금지.
- **피드백 UI wrapper**: 선택 버튼 + 반려 이유 입력은 `apps/web/app/plan/[plan_id]/page.tsx` inline wrapper (PlanCard.tsx 0줄 + component_map.md 0줄 — Phase 4.5 recommended highlight / Phase 5 AuthGuard wrapper 계승, NG6/NG7).

## Trade-offs

| 선택 | 채택 사유 | 미채택 후보 |
|---|---|---|
| 실 plans 정합 (plan_id + option_index) | 실 영속화 테이블 그대로 활용 + 4계층 미연결 무관 + 회귀 0 | idealized plan_options 4계층 — plan_options 테이블 신규 필요 (NG2 scope creep) |
| selected_option_index 0–2 (plan_candidates 배열 인덱스) | 3-plan 중 선택 식별 충분 + JSONB 정합 | selected_option_id(plan_options FK) — 4계층 의존 |
| 저장 전 PII 마스킹 | raw PII DB 잔존 방지 + retention 의무 최소 | 조회 시 마스킹 — raw 잔존 |
| graceful (PlansRepo 패턴) | Phase 5 baseline 계승 + mock 환경 test | strict (Supabase 필수) — 테스트/dev 곤란 |
| 피드백 UI inline wrapper | PlanCard·component_map 0줄 유지 (wrapper 정신) | 신규 FeedbackCard component — component_map 등록 (NG7) |

## Verification

- `pytest backend/fastapi/tests/test_selection_feedback.py` (Slice 2 신규):
  - SelectionRepo graceful select/get (Supabase mock + in-memory fallback)
  - FeedbackRepo graceful record/list
  - option_index 0/1/2 + out-of-range 거부
- `pytest backend/fastapi/tests/test_plans_feedback_api.py` (Slice 3 신규):
  - POST /select + POST /feedback + GET feedback (본인 plan 권한 T4)
  - feedback reason 저장 전 PII 마스킹 (T1)
- **기존 baseline 249 회귀 0** (additive — plans/plan_candidates 불변).
- **`git diff --stat | grep -E "PlanCard|component_map"` = 0 lines** (Slice 5 — 피드백 UI wrapper).

## References

- `docs/contracts/db_schema.md` §3.6 plans (실 영속화 테이블) + §4.2 plan_options (idealized — Phase 11+) + §4.3 selected_plans (idealized) + §5.2 feedback_events + §9 RLS
- `docs/decisions/phase_5_supabase_adoption.md` (ADR-020 — PlansRepo graceful 패턴)
- `docs/decisions/phase_5_rls_policy.md` (ADR-021 — RLS user 격리 + 2-hop subquery)
- `backend/fastapi/db/repositories/plans_repo.py` (graceful Supabase or in-memory — selection/feedback repo 모델)
- `meta/security_reviews/2026-05-29_phase-9-feedback-pii.md` (T1 피드백 reason PII + T2 reject 사유 + T3 RLS + T4 GET 권한 + T6 SQL injection)
- `meta/validations/2026-05-29_phase-9-pre-entry_self.md` §V1 (실 plans 정합) + §V4 (피드백 PII) + §V5 (repo graceful) + §V6 (UI wrapper)
- `phases/active/phase-9-result-feedback/{goals,scope,non_goals,assumptions,multi_slice_plan}.md`
