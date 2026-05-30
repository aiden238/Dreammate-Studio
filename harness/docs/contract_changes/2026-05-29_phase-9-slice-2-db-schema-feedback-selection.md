# Contract Change Log — Phase 9 Slice 2 db_schema.md feedback/selection 실 plans 정합 + brand_memory prep

> ID: CC-004
> Status: **decided + applied** (2026-05-29, Phase 9 Slice 2)
> Date: 2026-05-29
> Decision: Idealized 정의 보존 + Phase 9 실 구현 블록 additive (ADR-030/031 선행 승인 + security-review 선행 기반)
> Author: Claude (Phase 9 Slice 2 sub-agent)
> Related contracts: `docs/contracts/db_schema.md` (§4.3 / §5.2 / §6)
> Related ADR: ADR-030 (`docs/decisions/phase_9_feedback_selection.md`) + ADR-031 (`docs/decisions/phase_9_brand_memory_prep.md`)
> Proposal: `meta/proposals/2026-05-29_phase-9-slice-2-db-schema-feedback-selection.md`
> Security: `meta/security_reviews/2026-05-29_phase-9-feedback-pii.md` (T1 reason PII 마스킹 / T3 RLS user 격리)
> Skill: contract-change (절차) + security-review (선행, Slice 1)

---

## 1. 변경 요약

| 대상 | 변경 |
|---|---|
| `db_schema.md §4.3 selected_plans` | Idealized(plan_options.option_id → Phase 11+ 4계층 NG2) 라벨 + **Phase 9 실 구현** 블록 추가 (plan_id → plans(id) + selected_option_index 0–2 + auth_user_id + RLS T3). |
| `db_schema.md §5.2 feedback_events` | Idealized(target_kind+target_id → Phase 11+) 라벨 + **Phase 9 실 구현** 블록 (plan_id → plans(id) + option_index null=plan 전체 + event_type enum + reason PII 마스킹 T1 + RLS T3). |
| `db_schema.md §6 brand_memory_entries` | Idealized 정의 보존 + **Phase 9 준비** 블록 (brands(id) + source_plan_id, BrandMemoryRepo 수동/준비용, 자동 추출 agent P-AUX-2 미구현 Phase 10+ NG1 / 적재 pending NG12). |

## 2. 코드 영향 (additive only)

```
backend/fastapi/db/migrations/0005_feedback_selection.sql            — 신규 (실 구현 SoT: selected_plans + feedback_events + brand_memory_entries + RLS, idempotent)
backend/fastapi/db/repositories/selection_repo.py                    — 신규 SelectionRepo (graceful, PlansRepo 패턴)
backend/fastapi/db/repositories/feedback_repo.py                     — 신규 FeedbackRepo (graceful) + mask_pii (reason 저장 전 마스킹 T1)
backend/fastapi/db/repositories/brand_memory_repo.py                 — 신규 BrandMemoryRepo (graceful, 준비용)
backend/fastapi/db/{__init__,repositories/__init__}.py               — export (additive)
backend/fastapi/tests/test_selection_feedback.py                     — 신규 (12 케이스: graceful CRUD + PII 마스킹 + option_index)
```

## 3. 회귀 안전 근거

- **idealized 정의 불변**: §4.3 / §5.2 / §6 의 기존 idealized SQL 블록은 0 변경 — Phase 9 실 구현 블록만 additive 추가.
- **실 plans 테이블 불변**: 0005 는 신규 테이블 3종 CREATE IF NOT EXISTS 만 — plans / plan_candidates 컬럼 + PlansRepo + db/client + migrations 0001~0004 0 변경.
- **plan_options 테이블 미생성** (NG2): idealized §4.2 참조 보존만 — Phase 11+ 4계층 full linkage.
- **자동 추출 0** (NG1): P-AUX-2 agent 파일 미생성 + orchestration 미연결.
- **graceful**: Supabase 실패 시 in-memory fallback (raise 0, 사용자 차단 0건 — PlansRepo 패턴).

## 4. 검증 결과

```
pytest backend/fastapi/tests/: 249 → 261 PASS (test_selection_feedback +12).
기존 249 baseline assertion 수정 0 (additive only).
db/{client,plans_repo}.py / migrations 0001~0004: 0줄.
schemas/output.py / agents/* / routers/* / orchestration/*: 0줄.
PlanCard.tsx / component_map.md: 0줄.
reason PII 마스킹(T1): test_feedback_reason_pii_masked_on_record + test_mask_pii_patterns PASS (이메일/전화/주민/카드 → [masked]).
```

## 5. Rollback

- db_schema.md 변경은 git revert (Phase 9 실 구현 블록만 제거 — idealized 원복).
- 0005 + repo 3종 + export 는 additive — 제거 시 기존 plans + PlansRepo 불변 (회귀 0).

## 6. 변경 이력

- 2026-05-29: 제안서 작성(meta/proposals CC-004) + db_schema.md §4.3/§5.2/§6 반영 + 0005 migration + repo 3종 + 검증 261 PASS (Phase 9 Slice 2).
