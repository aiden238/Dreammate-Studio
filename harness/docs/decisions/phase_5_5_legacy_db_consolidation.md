# ADR-023 — Phase 5.5 Legacy DB Consolidation

> Date: 2026-05-29
> Status: Accepted
> Phase: 5.5
> Related: ADR-020 (Phase 5 Supabase 채택), Phase 1 Slice 5 (legacy DB 인프라), Phase 5 Slice 2 (신규 DB layer)
> Validation: `meta/retrospectives/phase-5.md` §개선 제안 §1
> Sub-agent: Phase 5.5 Slice 2 dispatch

---

## Context

Phase 5 Slice 2 종료 시점, **legacy DB 인프라**와 **Phase 5 신규 인프라**가 공존하는 상태가 발견되었다:

| Layer | 위치 | 도입 시점 | 인터페이스 |
|---|---|---|---|
| **Legacy** | `db/supabase_client.py` (factory) | Phase 1 Slice 5 (2026-05-26) | `get_supabase_client() -> Any \| None` |
| **Legacy** | `db/__init__.py::save_video_planning(...)` (orchestrator) | Phase 1 Slice 5 (2026-05-26) | 단일 함수 (Intent/RAG/Planning/Critic) |
| **Legacy** | `db/repositories/video_project.py + plan_candidate.py` | Phase 1 Slice 5 (2026-05-26) | per-table insert 함수 |
| **Legacy** | `db/migrations/001_init.sql` | Phase 1 Slice 5 (2026-05-26) | video_projects + plan_candidates |
| **Phase 5** | `db/client.py` (Protocol + factory + graceful) | Phase 5 Slice 2 (2026-05-29) | `get_supabase() -> SupabaseClientLike \| None` |
| **Phase 5** | `db/repositories/plans_repo.py` (CRUD class) | Phase 5 Slice 2 (2026-05-29) | `PlansRepo.create/get/update/delete` (async) |
| **Phase 5** | `db/migrations/0001_init.sql + 0002 + 0003` | Phase 5 Slice 2/4 (2026-05-29) | plans + RLS policies |

두 layer 모두 **동작 + 모든 기존 테스트 PASS** 상태 (pytest 170/170 baseline). 그러나:

1. 미래 Phase (7 RAG, 8 MOA, 9 Feedback)에서 두 layer 중 어느 것을 사용할지 불명확.
2. legacy `save_video_planning`은 plans_repo와 인터페이스가 다름 (단일 함수 vs CRUD class, sync vs async).
3. 신규 코드가 legacy import 시 어느 path 가 canonical 인지 혼란 가능.
4. Phase 5/6 baseline 보호 의무 ★ (PlanCard 18연속 + component_map 28연속 + canonical critic/rewriter) 때문에 즉시 제거는 회귀 risk.

---

## Decision

**옵션 A 채택**: 공존 유지 + deprecated note + Phase 7+ 실 통합 검토.

### 구체적 조치

1. **`db/supabase_client.py`** — module docstring 최상단에 "DEPRECATED (Phase 5.5)" 명시 + module import 시 `DeprecationWarning` 1회 발행. 기존 함수/클래스 시그니처 변경 X (backward-compat 100%).
2. **`db/__init__.py::save_video_planning(...)`** — docstring 에 "DEPRECATED (Phase 5.5)" 명시 + 함수 호출 시 `DeprecationWarning` 발행. 기존 graceful 정책 (`skipped_no_db` / `failed_db_error` / `saved`) 모두 보존.
3. **`db/__init__.py`** module docstring — Phase 5 canonical (`get_supabase`, `PlansRepo`) 우선 export 명시, legacy backward-compat 분리 명시. `__all__` 에 canonical 4 + legacy 4 모두 노출 (호환 유지).
4. **회귀 0 보장** — pytest 170/170 → 172/172 (legacy deprecation 신규 검증 +2). 모든 Phase 1/4/4.5/5/6 baseline 테스트 PASS 유지.
5. **실 통합 시점** — Phase 7+ RAG 도입 직후 검토 (별도 ADR — ADR-024 RAG scope evolution 참조 예정).

### 대안 비교

| 옵션 | 장점 | 단점 | 채택? |
|---|---|---|---|
| **A. 공존 + deprecated note + 지연 통합** | 회귀 0 보장, Phase 5/6/7 baseline 보호, MVP 속도 유지 | legacy 코드 잔존 (mental overhead) | ✅ **채택** |
| B. 즉시 통합 (legacy → Phase 5 wrap) | 코드베이스 단일화, mental overhead 0 | 회귀 risk (Phase 1 8 케이스 깨질 가능), Phase 7 진입 지연 2~3h, plans table 과 video_projects/plan_candidates 의 schema 차이 mapping 부담 | ❌ |
| C. legacy 완전 제거 | 가장 깨끗 | 테스트 깨질 risk ▲▲, Phase 1 baseline 손상, Phase 5 baseline 무효화 위험 | ❌ |

**채택 근거**: Phase 5/6 baseline 무손상 + MVP 속도 우선. 옵션 B/C 의 잠재 이득은 Phase 7+ RAG 진입 후 누적된 통합 요구사항 (RAG metadata, candidate_knowledge 5단계 등)과 함께 한 번에 처리하는 편이 효율적이다 (ADR-024).

---

## Constraints

- **Phase 7+ RAG 통합 후** legacy 실 제거 결정 (별도 ADR — 예정 ADR-025 또는 통합 ADR).
- **DeprecationWarning capture**: pytest `filterwarnings` 기본 정책 (warning 표시, fail 처리 X) 사용. 명시적 검증 케이스는 `pytest.warns(DeprecationWarning)` 사용 (test_db.py 2 케이스 신규).
- **legacy 사용 코드는 신규 작성 금지** (코드 리뷰 시 차단). 신규 코드는 반드시 `from backend.fastapi.db import get_supabase` / `PlansRepo` 사용.
- **`__all__` 호환 유지** — legacy 4 export (`get_supabase_client`, `save_video_planning`, `PersistenceResult`, `SaveStatus`) 모두 노출 유지 (routers/generate.py 등 기존 사용처 무손상).

---

## Trade-offs

- **즉시 통합 회피** → Phase 5/6 baseline 보호 우선. 옵션 B/C 의 단기 이득 < 회귀 risk.
- **지연 통합 risk** — legacy 코드 잔존 → Phase 7+ 에서 한 번에 정리 필요. 통합 ADR (ADR-025+) 에서 plans ↔ video_projects/plan_candidates 의 schema 호환 mapping 명시 예정.
- **DeprecationWarning 발행** → pytest warning count 증가 (Phase 5 baseline 42 → Phase 5.5 51, neta +9 모두 의도된 deprecation). 사용자 응답 차단 0건 유지.
- **Mental overhead** — 신규 contributor 가 두 layer 차이를 학습해야 함. 본 ADR + `db/__init__.py` module docstring 으로 mitigation.

---

## Verification

### 자동 검증
- ✅ `pytest backend/fastapi/tests/` — 170/170 → 172/172 (회귀 0 + legacy deprecation 신규 검증 +2).
- ✅ `pytest backend/fastapi/tests/test_db.py` — 18/18 → 20/20.
- ✅ legacy import / 호출 시 DeprecationWarning 발행 (test_phase_5_5_legacy_supabase_client_emits_deprecation_warning, test_phase_5_5_legacy_save_video_planning_emits_deprecation_warning).
- ✅ Phase 1 e2e (router 200 + db_persistence warn) — `test_router_returns_200_even_when_db_fails` PASS 유지 (backward-compat 100%).

### 코드 리뷰 가드
- 신규 코드 PR 에서 `from backend.fastapi.db.supabase_client import` 또는 `from backend.fastapi.db import save_video_planning` 발견 시 reviewer 차단 + 본 ADR link.

### Phase 7+ 통합 시점 (별도 ADR 예정)
- candidate_knowledge 5단계 도입 시 plans ↔ video_projects/plan_candidates schema 통합 검토.
- legacy `save_video_planning` → `PlansRepo.create()` wrap or 폐기 결정.

---

## References

- `meta/retrospectives/phase-5.md` §개선 제안 §1 (legacy DB 통합 미결)
- `phases/archive/phase-5-db-auth/closing_notes.md` Phase 6+ 옵션 B (참조 — 본 Phase 5.5 에서 옵션 A 채택)
- ADR-020 (`docs/decisions/phase_5_supabase_adoption.md`) — Supabase 채택 baseline
- ADR-024 (예정, Phase 5.5 Slice 3 산출) — Phase 7 RAG scope evolution + legacy DB 실 통합 시점 cross-reference

---

## Status timeline

- 2026-05-29 — Phase 5.5 Slice 2 dispatch 에서 옵션 A 채택 + 본 ADR 작성 + 코드 반영 (`supabase_client.py` + `__init__.py` deprecated note + `test_db.py` 검증 +2).
- (예정) Phase 7+ RAG 통합 직후 — legacy 실 제거 결정 별도 ADR.
