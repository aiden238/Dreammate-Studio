# Contract Change Proposal: Phase 9 Slice 2 — db_schema.md feedback/selection 실 plans 정합 + brand_memory prep

- 제안일: 2026-05-29
- 제안자: Claude Code (Phase 9 Slice 2 sub-agent)
- 대상 contract: `docs/contracts/db_schema.md`
- 변경 종류: 수정 (Phase 9 실 구현 명시 추가 — idealized 정의 보존)
- 긴급도: 보통 (Phase 9 Slice 2 결과 저장 + 피드백 의무)
- ID: CC-004 (Phase 8 CC-003 패턴 계승)

## 변경 사유

Phase 9 Slice 2 (multi_slice_plan.md §Slice 2 + ADR-030/031):

1. 결과 저장 / 피드백을 **실 `plans` 테이블 정합**으로 0005 migration 에 신규 (selected_plans + feedback_events + brand_memory_entries).
2. db_schema.md §4.3 `selected_plans` + §5.2 `feedback_events` 는 idealized 4계층 (plan_options.option_id / target_kind+target_id) 정의만 보유 → Phase 9 실 구현(plan_id + selected_option_index 0–2)과 **분리 명시** 필요.
3. §6 `brand_memory_entries` 는 Phase 9 준비(BrandMemoryRepo 수동/준비용) 명시 + 자동 추출 agent (P-AUX-2) Phase 10+ cross-ref (ADR-031 / NG1).

idealized plan_options(§4.2) 4계층 full linkage 는 Phase 11+ (NG2) — 본 변경은 **참조 보존**만 (신규 plan_options 테이블 생성 X).

## 변경 내용 (before/after)

### Before (§4.3 selected_plans)
```sql
create table selected_plans (
    video_id          uuid primary key references video_projects(video_id),
    selected_option_id uuid not null references plan_options(option_id),
    selection_reason   text,
    selected_at        timestamptz not null default now()
);
```

### After (§4.3)
- 기존 idealized 정의에 **"Phase 11+ 4계층 full linkage (NG2)"** 라벨 추가.
- **Phase 9 실 구현 (0005_feedback_selection.sql)** 블록 추가: `plan_id references plans(id)` + `selected_option_index smallint check 0–2` (plan_candidates JSONB 배열 인덱스) + `selection_reason` + `auth_user_id`.

### Before (§5.2 feedback_events)
```sql
create table feedback_events (
    feedback_id  uuid primary key default gen_random_uuid(),
    user_id      uuid not null references user_profiles(user_id),
    target_kind  text not null,                -- 'plan_option' | ...
    target_id    uuid not null,
    event_type   text not null,
    reason       text,
    created_at   timestamptz not null default now()
);
```

### After (§5.2)
- 기존 idealized 정의에 **"Phase 11+ idealized 4계층 (target_kind+target_id)"** 라벨.
- **Phase 9 실 구현** 블록: `plan_id references plans(id)` + `option_index`(null=plan 전체) + `event_type` enum + `reason`(PII 저장 전 마스킹 — T1) + `auth_user_id`.

### Before / After (§6 brand_memory_entries)
- 기존 정의 보존 + **Phase 9 준비** 주석: BrandMemoryRepo(수동/준비용 CRUD) 0005 등록, 자동 추출 agent(P-AUX-2 brand_memory_extractor) **미구현 Phase 10+** (ADR-031 / NG1). source_video_id 는 실 구현에서 source_plan_id(→ plans.id) 로 정합.

## 영향 받는 영역

- [ ] API 응답 형식 (Slice 3)
- [x] DB 스키마 (신규 테이블 3종 — 실 plans 정합 명시)
- [ ] Agent IO
- [ ] Output Schema (불변)
- [ ] 프론트 컴포넌트
- [ ] Prompt (P-AUX-2 참조만 — registry 가 SoT)
- [ ] RAG 파이프라인 (feedback→candidate 적재는 Slice 4)
- [ ] 평가 / golden_set
- [x] 보안 / 권한 (RLS user 격리 — security-review T3 / T1 reason PII 마스킹)

## 영향 받는 파일 목록

```
docs/contracts/db_schema.md (§4.3 / §5.2 / §6 — Phase 9 실 구현 추가)
backend/fastapi/db/migrations/0005_feedback_selection.sql (신규 — 실 구현 SoT)
backend/fastapi/db/repositories/{selection,feedback,brand_memory}_repo.py (신규)
backend/fastapi/db/{__init__,repositories/__init__}.py (export)
backend/fastapi/tests/test_selection_feedback.py (신규)
```

## Rollback 방안

- db_schema.md 변경은 git revert (idealized 정의 원복 — Phase 9 실 구현 블록만 제거).
- 신규 테이블/repo 는 additive — 0005 미적용 시 기존 plans + PlansRepo 불변 (회귀 0).

## 마이그레이션 필요 여부
- [x] DB 마이그레이션 (0005 신규 — idempotent CREATE IF NOT EXISTS, 기존 데이터 변환 0)
- [ ] 기존 데이터 변환
- [ ] 사용자 통지
- [ ] 외부 API 클라이언트 통지

## 승인 기준
- 영향 받는 파일 3개 이상 + 새 테이블 추가 → **사용자 승인 필요 (4-2)**.
- 보안 영향(RLS + reason PII) → security-review Skill 선행 완료 (Slice 1 `2026-05-29_phase-9-feedback-pii.md`) → 추가 검토(4-3) 충족.
- 단, idealized 정의는 **불변** (실 구현 블록 additive 명시만) → 의미 변경 최소 + ADR-030/031 선행 승인 기반.

## 결정
- [x] 승인 (ADR-030/031 선행 승인 + security-review 선행 + Phase 9 entry 사용자 결정 기반 — Slice 2 자기 반영)
- 결정자: 사용자 결정 (Phase 9 entry) + ADR-030/031 (Slice 1 Accepted)
- 결정일: 2026-05-29
- 메모: idealized plan_options 4계층(§4.2)은 Phase 11+ (NG2) 참조 보존. 실 구현 SoT = 0005_feedback_selection.sql.
