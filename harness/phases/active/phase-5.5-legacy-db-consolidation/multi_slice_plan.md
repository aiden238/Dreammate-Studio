# Phase 5.5 — Multi-Slice Plan

> 4 Slice 모두 sub-agent dispatch, sequential
> 총 4~6h

---

## Wave 구조

```
Wave 1: Slice 1 [Pre-Entry — entry commit + state docs]
  ↓
Wave 2: Slice 2 [Legacy DB 통합 + ADR-023]
  ↓
Wave 3: Slice 3 [Validation 강화 × 3 + ADR-024 RAG scope evolution + Brand Memory confirmation]
  ↓
Wave 4: Slice 4 [Close — 회고 + archive + state docs]
```

---

## Slice 1 — Pre-Entry (30~60min)

### 작업 단위
1. `meta/skill_usage_log.md` 갱신 (phase-start +1)
2. `PROJECT_STATE.md` 갱신 (phase_5_5_* 필드 + current_sprint phase-5.5-slice-1)
3. notes.md §Slice 1 진행 메모 추가
4. **entry commit**: "feat(phase-5.5): Slice 1 entry — consolidation mini-phase + legacy DB + validation 강화 + Phase 7 prep"

### 영향 파일 (~3 수정 + entry commit)

### Sub-agent prompt 핵심
- editable: meta/skill_usage_log.md / PROJECT_STATE.md / phases/active/phase-5.5-*/notes.md
- forbidden: 거의 모든 코드 + entry files 외 phases/active/phase-5.5-* + 이전 phase 모든 산출물
- P-X1 의무

---

## Slice 2 — Legacy DB 통합 + ADR-023 (2~3h)

### 작업 단위
1. Phase 1 legacy 파일 검토:
   - `backend/fastapi/db/supabase_client.py` (factory 패턴, Phase 1 Slice 5 작성)
   - `backend/fastapi/db/save_video_planning.py` (orchestrator)
   - 기존 tests/test_db.py (Phase 1 8 케이스 + Phase 5 9 케이스 + RLS 4 + SSE 4 = 25 total. 단, test_db.py만 18 케이스로 가정. 실제는 read 후 확인)
2. 통합 결정 (3가지 옵션 중 선택):
   - **옵션 A**: 공존 유지 + deprecated note (legacy는 그대로, deprecated 마커만, 실 통합은 Phase 7+)
   - **옵션 B**: 즉시 통합 (legacy `supabase_client` → Phase 5 `get_supabase()` wrap, save_video_planning → plans_repo)
   - **옵션 C**: legacy 완전 제거 (테스트 깨질 risk, 비권장)
3. **권장 옵션 A** (회귀 0 보장 + Phase 7 이후 자연 통합) → ADR-023에 명시
4. 실제 작업:
   - `backend/fastapi/db/supabase_client.py` 상단에 deprecated docstring 추가 + Phase 5 `get_supabase()` 호출로 위임 (옵션 A 패턴):
     ```python
     """DEPRECATED (Phase 5.5): use backend.fastapi.db.client.get_supabase() instead.
     Phase 1 legacy factory. Will be removed in Phase 7+ after RAG integration.
     """
     ```
   - `backend/fastapi/db/save_video_planning.py` 상단에 deprecated docstring 추가 + plans_repo 호환 패턴 명시
   - `backend/fastapi/db/__init__.py` export 정리 (legacy + new 명확 분리)
   - 회귀 검증: pytest 170/170 유지
5. `docs/decisions/phase_5_5_legacy_db_consolidation.md` 신규 (ADR-023):
   - Context: Phase 1 + Phase 5 두 DB layer 공존 발견
   - Decision: **옵션 A** (deprecated note + Phase 7+ 실 통합)
   - Constraints: 회귀 0 + plans_repo 인터페이스를 새 코드에서 사용
   - Trade-offs: 즉시 통합 risk vs 지연된 통합 risk → 지연 우선 (Phase 5/6 baseline 보호)
6. **commit**: "feat(phase-5.5): Slice 2 — Legacy DB consolidation (deprecated note + ADR-023)"

### 영향 파일 (~3 수정 + 1 신규)

### Sub-agent prompt 핵심
- editable: backend/fastapi/db/{supabase_client.py, save_video_planning.py, __init__.py}, backend/fastapi/tests/test_db.py (필요 시), docs/decisions/phase_5_5_legacy_db_consolidation.md
- forbidden: 그 외 모든 코드 (Phase 5 baseline 보존), apps/web/*, PlanCard, component_map, docs/contracts/*, 이전 ADRs, scripts, skills, archive, meta (Slice 3 영역)
- P-X1 의무

---

## Slice 3 — Validation 강화 + ADR-024 RAG scope evolution + Brand Memory (1~2h)

### 작업 단위
1. **External validation self-strengthen × 3**:
   - `meta/validations/2026-05-28_phase-4.5-pre-entry_external.md`: Claude Code 자가 검토 V1~V4 (Critic revise loop / Rewriter prompt / Z-X3 best-plan / P-X2 자동 게이트) — 각 항목별 self response 작성 (외부 검토 가정한 self-question + self-answer)
   - `meta/validations/2026-05-29_phase-6-pre-entry_external.md`: V1~V5 (Critic canonical / Rewriter contract / revise_history typing / fallback 축소 / frontend types 1:1)
   - `meta/validations/2026-05-29_phase-5-pre-entry_external.md`: V1~V6 (Supabase / JWT / RLS / SSE / revise_history JSONB / canonical DB)
   - 모두 "Self-strengthened (Phase 5.5)" 헤더 추가 + 차이/일치 메모 형식
2. **ADR-024 신규** `docs/decisions/phase_7_rag_scope_evolution.md`:
   - Context: Phase 7 RAG 진입 전 scope 결정 + 추후 확대 경로 명시 (사용자 결정 3+4)
   - Decision:
     - RAG **Lite scope MVP** = candidate_knowledge **5단계 전부 구현** (pending → filtered → evaluated → approved → promoted) (사용자 결정 4)
     - 추정 시간 12~16h (8~12h 원안에서 상향)
   - 확대 지점 (다른 phase로 확장 가능):
     - Phase 11+ 사용자 데이터 자동 promotion (실 사용자 피드백 누적 기반)
     - Phase 21+ Custom RAG (자체 embedding model + custom retrieval)
     - Phase 21+ Graph RAG (관계 graph 기반 retrieval)
     - 추가 layer: hybrid retrieval (BM25 + vector), re-ranking model, multi-modal RAG (이미지 + 영상)
   - 트리거 조건: 각 확대 지점별 활성화 조건 명시 (예: "사용자 1000+ 후 Phase 11 자동 promotion 검토")
3. **Brand Memory Phase 9+ confirmation** (사용자 결정 5):
   - 이미 `phases/active/phase-5.5-*/non_goals.md` §NG2 명시 완료
   - ADR-024 본문에 §"Brand Memory 자동 추출 별도 처리"로 cross-reference 명시 ("Phase 9+ 이관 — confirmed by user 2026-05-29")
4. **commit**: "feat(phase-5.5): Slice 3 — validation 강화 × 3 + ADR-024 RAG scope evolution + Brand Memory Phase 9+ confirm"

### 영향 파일 (~3 수정 + 1 신규)

### Sub-agent prompt 핵심
- editable: meta/validations/*_external.md × 3 (강화), docs/decisions/phase_7_rag_scope_evolution.md (신규)
- forbidden: backend/* 전체 (Slice 2 영역 + Phase 5 baseline), apps/web/*, docs/contracts/*, 이전 ADRs (ADR-023 보존), scripts, skills, archive, PROJECT_STATE/PHASE_REGISTRY (Slice 4 final)
- P-X1 의무

---

## Slice 4 — Close (30~60min)

### 작업 단위
1. `scripts/audit_naming.ps1` + `audit_page_component.ps1` 재실행 (0 drift + 1 intended WARN 유지)
2. `scripts/scenario_simulation.ps1` 재실행 (v2 10/10 유지) — P-X2 네 번째 자동 게이트
3. `scripts/smoke_test_phase_5.ps1` 재실행 (12/12 유지) — Phase 5.5는 별도 smoke 미작성, Phase 5 smoke 재사용
4. `meta/retrospectives/phase-5.5.md` 신규 (개선 제안 §1~3)
5. `meta/patterns.md` 갱신:
   - P-X1-EFFECT-001 update (22→26연속)
   - **P-LEGACY-CONSOLIDATION-001 신규 후보** (옵션 A 패턴 = 공존 + deprecated note + 지연 통합)
6. `meta/skill_usage_log.md` 갱신 (Phase 5.5 사용 요약 5 Skill: phase-start + qa-check + harness-audit + meta-retrospective + phase-complete)
7. archive 이동: `phases/active/phase-5.5-*` → `phases/archive/phase-5.5-legacy-db-consolidation/`
8. `closing_notes.md` 신규 (Phase 7 진입 prep — ADR-024 link, candidate_knowledge 5단계 명시)
9. PROJECT_STATE / PHASE_REGISTRY / 00_START_HERE / README × 2 갱신:
   - phase_5_5_status: completed
   - next_phase: phase-7-rag-lite (사용자 결정: "Phase 5.5 진행 후 페이즈 7 기획 시작" → Phase 7 진입 준비)
10. **final commit**: "feat(phase-5.5): Slice 4 — close (P-X1 26연속 + ADR-024 RAG scope) + Phase 7 prep"

### 영향 파일 (~6 수정 + 1 신규 + archive 이동)

### Sub-agent prompt 핵심
- editable: scripts (실행만), meta/retrospectives/phase-5.5.md, meta/patterns.md, meta/skill_usage_log.md, phases/archive/phase-5.5-* (이동), closing_notes.md (신규), state docs × 5
- forbidden: backend/*, apps/web/*, docs/*, 이전 ADRs, .claude/skills/*
- P-X1 의무

---

## 충돌 매트릭스

| Slice | backend/db | tests | meta | docs | scripts | state docs |
|---|---|---|---|---|---|---|
| 1 | ❌ | ❌ | ✅ skill_usage_log | ❌ | ❌ | ✅ entry |
| 2 | ✅ legacy (수정 소폭) | ✅ test_db (필요 시) | ❌ | ✅ ADR-023 | ❌ | ❌ |
| 3 | ❌ | ❌ | ✅ validations × 3 | ✅ ADR-024 | ❌ | ❌ |
| 4 | ❌ | ❌ | ✅ retrospective + patterns + skill_usage + closing_notes | ❌ | ✅ 실행만 | ✅ all |

Sequential 진행 시 충돌 0.

---

## 누적 P-X1 streak

| Phase | streak |
|---|---|
| Phase 3 | 5 |
| Phase 4 | 4 |
| Phase 4.5 | 4 |
| Phase 6 | 4 |
| Phase 5 | 5 |
| Phase 5.5 | **4 (목표)** |
| **누적** | **26** |

---

## 시간 추정

| Slice | 시간 |
|---|---|
| 1 | 30~60min |
| 2 | 2~3h |
| 3 | 1~2h |
| 4 | 30~60min |
| **합계** | **4~6h** |
