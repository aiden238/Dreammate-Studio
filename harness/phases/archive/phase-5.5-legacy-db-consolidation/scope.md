# Phase 5.5 — Scope

## 포함 (In-Scope)

### Backend (소폭, legacy 통합)

| 파일 | 작업 |
|---|---|
| `backend/fastapi/db/supabase_client.py` (Phase 1 legacy) | **수정 또는 wrapper** — Phase 5 `db/client.py` 호환 또는 deprecated note 추가 |
| `backend/fastapi/db/save_video_planning.py` (Phase 1 legacy) | **수정 또는 wrapper** — `plans_repo` 인터페이스 호환 또는 deprecated note |
| `backend/fastapi/db/__init__.py` | **수정** — 통합 인터페이스 export (legacy + new 명확 분리 또는 single export) |
| `backend/fastapi/tests/test_db.py` | **수정** (필요 시) — legacy 통합 후 회귀 검증 |
| `backend/fastapi/db/client.py` (Phase 5) | **수정 X** (Phase 5 baseline 보존) |
| `backend/fastapi/db/repositories/plans_repo.py` (Phase 5) | **수정 X** |
| `backend/fastapi/db/migrations/*` | **수정 X** |
| `backend/fastapi/routers/*` | **수정 X** |
| `backend/fastapi/agents/*` | **수정 절대 금지** ★ (Phase 6 canonical baseline) |
| `backend/fastapi/schemas/output.py` | **수정 절대 금지** ★ |

### Frontend

| 파일 | 작업 |
|---|---|
| 모두 | **수정 X** (Phase 5 baseline 유지) |
| `apps/web/components/PlanCard.tsx` | **수정 절대 금지** ★ — 18연속 |
| `apps/web/component_map.md` | **수정 절대 금지** ★ — 28연속 |

### Meta / Docs (핵심 영역)

| 파일 | 작업 |
|---|---|
| `meta/validations/2026-05-28_phase-4.5-pre-entry_external.md` | **수정** — self-strengthen (Claude Code 자가 검증 V1~V4 형식으로 placeholder 채움) |
| `meta/validations/2026-05-29_phase-6-pre-entry_external.md` | **수정** — self-strengthen V1~V5 |
| `meta/validations/2026-05-29_phase-5-pre-entry_external.md` | **수정** — self-strengthen V1~V6 |
| `docs/decisions/phase_5_5_legacy_db_consolidation.md` | **신규** — ADR-023 |
| `docs/decisions/phase_7_rag_scope_evolution.md` | **신규** — ADR-024 |
| `meta/retrospectives/phase-5.5.md` | **신규** |
| `meta/patterns.md` | **수정** — P-X1-EFFECT-001 update (26연속) + P-LEGACY-CONSOLIDATION-001 신규 후보 |
| `meta/skill_usage_log.md` | **수정** — Phase 5.5 추가 |
| `PROJECT_STATE.md` / `PHASE_REGISTRY.md` / `00_START_HERE.md` / `README.md` × 2 | **수정** |
| `phases/active/phase-5.5-*/* (entry files)` | **main 작성 완료, 수정 X** |

### Scripts

| 파일 | 작업 |
|---|---|
| `scripts/smoke_test_phase_5.ps1` | **재실행** (final 검증, 12/12 유지) |
| `scripts/scenario_simulation.ps1` (v2) | **재실행** (10/10 유지) |
| `scripts/audit_naming.ps1` + `audit_page_component.ps1` | **재실행** (0 drift 유지) |
| `scripts/smoke_test_phase_5_5.ps1` | **신규 X** (Phase 5.5는 코드 변경 최소, 별도 smoke 불필요. smoke_test_phase_5 재사용) |

## 예상 파일 변경 수

- **신규**: ~5 (2 ADR + 회고 + closing_notes + entry directory 산출물)
- **수정**: ~8 (legacy DB 소폭 + 3 validations 강화 + state docs × 4 + patterns + skill_usage)
- **금지 (0줄)**: 2 (PlanCard.tsx, component_map.md)
- **예상 LOC**: ~+800 신규 / ~+300 수정 (도구 / 회고 중심, 코드 변경 최소)

## 제외 (Out-of-Scope) → `non_goals.md` 참조
