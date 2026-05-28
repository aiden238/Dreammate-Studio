# Contract Change Proposal: Phase 5 Slice 2 — db_schema.md 갱신 + migration baseline

- 제안일: 2026-05-29
- 제안자: Claude Code (Phase 5 Slice 2 sub-agent)
- 대상 contract: `docs/contracts/db_schema.md`
- 변경 종류: 수정 (Phase 5 Slice 2 본문 갱신 + Phase 4.5/6 정합)
- 긴급도: 보통 (Phase 5 entry 의무)

## 변경 사유

Phase 5 Slice 2 작업 단위 (multi_slice_plan.md §Slice 2):
1. Supabase DB 영속화 baseline 구축 (in-memory `_plan_store` → PostgreSQL).
2. 4계층 데이터 모델 (User → Brand → Domain → Series → Video Project) 정식 시작.
3. Phase 4.5 (revise_history) + Phase 6 (canonical Critic) 컬럼 영속화.
4. ADR-020 (Supabase 채택) 정합 — db_schema.md §11 마이그레이션 노트 갱신.

기존 db_schema.md (v1 초안 — Phase 0~1 진입용) 는 풍부한 4계층 + Brand Memory + RAG 정의가 이미 존재. Phase 5 Slice 2 는 실제 migration SQL 과 plans 테이블 정식화를 추가하는 갱신.

## 변경 내용 (before/after)

### Before

```
db_schema.md §11. 마이그레이션 노트
  ### Phase 1 (MVP)
    위 모든 테이블 생성.
  ### Phase 11+ (확장)
    ...
```

Phase 1 baseline (`backend/fastapi/db/migrations/001_init.sql`) 에는 video_projects + plan_candidates 익명 저장 minimal 만 존재. 4계층 / plans 테이블 미정의.

### After

```
db_schema.md §11. 마이그레이션 노트
  ### Phase 1 (MVP) [legacy]
    001_init.sql: video_projects + plan_candidates 익명 minimal.
  ### Phase 5 Slice 2 (현)
    0001_init.sql: brands / domains / series / video_projects / plans 4계층 baseline.
    0002_phase_4_5_revise_history.sql: ALTER IF NOT EXISTS revise_history + recommended_plan_index + critic_evaluation (idempotent).
  ### Phase 5 Slice 4 (예정)
    0003_rls_policy.sql: RLS 정책 (ADR-021).
```

§9 RLS 절도 Phase 5 Slice 4 예고 추가.
§3.x 핵심 테이블에 Phase 5 신규 `plans` 테이블 정식 등록 (§3.6 신규).

## 영향 받는 영역

- [ ] API 응답 형식
- [x] DB 스키마 (baseline 등록)
- [ ] Agent IO
- [ ] Output Schema (Phase 6 canonical 호환만 — schema 변경 X)
- [ ] 프론트 컴포넌트
- [ ] Prompt
- [ ] RAG 파이프라인 (Phase 7+ pgvector baseline 보존)
- [ ] 평가 / golden_set
- [x] 보안 / 권한 (RLS 예고 — ADR-021 Slice 4)

## 영향 받는 파일 목록

```
docs/contracts/db_schema.md                                 (수정)
backend/fastapi/db/migrations/0001_init.sql                 (신규)
backend/fastapi/db/migrations/0002_phase_4_5_revise_history.sql (신규)
backend/fastapi/db/client.py                                (신규)
backend/fastapi/db/repositories/plans_repo.py               (신규)
backend/fastapi/db/__init__.py                              (수정 — export 추가)
backend/fastapi/db/repositories/__init__.py                 (수정 — export 추가)
backend/fastapi/config.py                                   (수정 — supabase_service_key 추가)
backend/fastapi/routers/plans.py                            (수정 — PlansRepo 인터페이스 도입, graceful 호환)
backend/fastapi/tests/test_db.py                            (수정 — Phase 5 Slice 2 6+ 케이스 추가)
```

## Rollback 방안

- migration 0001 + 0002 는 idempotent (IF NOT EXISTS) → revert 시 `DROP TABLE IF EXISTS plans / series / domains / brands / video_projects` 별도 manual SQL.
- PlansRepo 도입은 graceful (Supabase 없으면 in-memory) → 기존 `_plan_store: dict` 호환 보존.
- db_schema.md 갱신은 markdown text → 이전 commit 으로 git revert.
- 회귀 검증: pytest 144/144 → 150+/150+ (test_db.py +6 케이스).

## 마이그레이션 필요 여부

- [x] DB 마이그레이션 (0001 + 0002 신규)
- [ ] 기존 데이터 변환 (Phase 1 plan_candidates 데이터는 legacy 001_init 별도 운영, 본 Slice 영향 X)
- [ ] 사용자 통지 (내부 변경)
- [ ] 외부 API 클라이언트 통지 (API contract 무변경)

## 승인 기준

- 자기 단독 결정: 절차상 NO — 의미 변경 (4계층 baseline + plans 테이블 등록).
- 사용자 승인 필요: NO — Phase 5 multi_slice_plan.md §Slice 2 사전 승인 (사용자가 phase entry 시점에 multi_slice_plan 확정).
- 추가 검토 필요: NO — 보안 영향은 ADR-020 + security_reviews/2026-05-29_phase-5-auth-rls.md 에서 사전 점검 완료 (Slice 1).

→ **Phase 5 multi_slice_plan.md §Slice 2 사전 승인 효력으로 self-approved.**

## 결정

- [x] 승인 (Phase 5 multi_slice_plan.md sub-agent dispatch 효력)
- 결정자: Phase 5 multi_slice_plan.md §Slice 2 (사용자 phase entry 승인)
- 결정일: 2026-05-29
- 메모: contract-change Skill 절차 본격 두 번째 트리거 (Phase 6 Slice 1 §output_schema canonical 첫째 + Phase 5 Slice 2 db_schema 둘째).
