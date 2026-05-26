# Phase 1 — Multi-Slice Execution Plan (Slices 2~7)

> 작성: 2026-05-26 (Slice 1 완료 직후)
> 방식: sub-agent 분산 실행 (context 관리 + 병렬 가능 시 병렬)
> 원칙: phase-start v1.1.0 §6.3 Surgical Scope + qa-check v1.1.0 §10 Simplicity

---

## 1. 의존성 그래프

```
Slice 1 ✅ DONE (FastAPI skeleton)
  │
  ├─ Slice 2 (Intent + Planning 분리) ──┐
  │    │                                │
  │    ├─ Slice 3 (Critic) ─────────────┤
  │    │                                ├─ Slice 5 (Supabase 저장)
  │    └─ Slice 4 (RAG Lite + fallback)─┘
  │
  └─ Slice 6 (Next.js 진입 UI) ────────────── Slice 7 (Stepper + ErrorCard)
```

---

## 2. Wave 분할 (병렬화 전략)

### Wave 1 — 병렬 (2 sub-agents)
- **A: Slice 2** — `backend/fastapi/` (Intent + Planning + ErrorEnvelope)
- **B: Slice 6** — `apps/web/` (Next.js entry pages)

폴더 분리로 충돌 0. 동시 진행 가능.

### Wave 2 — 순차 (1 sub-agent)
- **C: Slice 3** — Critic Agent (`agents/critic.py` + router.py 수정)

Slice 4와 router.py 동시 수정 위험 → 순차.

### Wave 3 — 순차 (1 sub-agent)
- **E: Slice 4** — RAG Lite + fallback (`rag/` 신규 + router.py + planning.py 수정)

### Wave 4 — 병렬 (2 sub-agents)
- **F: Slice 5** — Supabase 저장 (`db/` 신규 + router.py 수정)
- **G: Slice 7** — Frontend polish (`apps/web/components/`)

다시 폴더 분리로 충돌 0.

---

## 3. Sub-Agent 공통 절차

각 sub-agent는 Slice 1과 동일한 4-Phase 절차 수행:

```
Phase A. 컨텍스트 로딩 (필요한 contract만 — Surgical Scope)
Phase B. 파일 생성 (의존성 순서)
Phase C. 정적 검증 (py_compile / pytest / npm build)
Phase D. 하네스 기록 + commit + push
  - eval/qa_reports/phase-1-slice-{N}_{date}.md 작성
  - git commit "phase-1(slice-{N}): ..."
  - git push origin main
```

---

## 4. Slice별 상세 (각 sub-agent 프롬프트에 포함될 핵심)

### Slice 2 — Intent + Planning 분리

```yaml
editable:
  - backend/fastapi/agents/intent.py (신규, P-001 기반)
  - backend/fastapi/agents/planning.py (신규, P-006 기반)
  - backend/fastapi/agents/__init__.py (export 갱신)
  - backend/fastapi/schemas/output.py (ErrorEnvelope 활성화)
  - backend/fastapi/routers/generate.py (intent_planning → intent + planning)
  - backend/fastapi/tests/test_intent.py (신규)
  - backend/fastapi/tests/test_planning.py (신규)
  - backend/fastapi/tests/test_e2e_slice1.py (Slice 2 호환 갱신)
  - backend/fastapi/tests/conftest.py (mock 갱신)

forbidden:
  - backend/fastapi/agents/intent_planning.py (Slice 2에서 제거하거나 deprecated)
  - apps/web/, frontend 전체
  - docs/contracts/* (참조만)
  - PROJECT_STATE.md, PHASE_REGISTRY.md (main session이 갱신)

acceptance:
  - golden_set GS-001~003 (Intent 차단) 통과
  - golden_set GS-004~010 (정상 처리) 통과 또는 적절히 mock
  - 정상 입력 → HTTP 200 + envelope
  - 비관련 입력 → HTTP 422 + ErrorEnvelope (ok:false, error.code:"INV-001")
  - pytest 전체 통과 (기존 10 + 신규)
```

### Slice 6 — Next.js 진입 UI

```yaml
editable:
  - apps/web/package.json
  - apps/web/tsconfig.json
  - apps/web/next.config.js
  - apps/web/tailwind.config.ts
  - apps/web/postcss.config.js
  - apps/web/.env.local.example
  - apps/web/.gitignore
  - apps/web/app/layout.tsx
  - apps/web/app/page.tsx
  - apps/web/app/plan/page.tsx
  - apps/web/app/globals.css
  - apps/web/components/PlanCard.tsx
  - apps/web/lib/api.ts
  - apps/web/public/manifest.json
  - apps/web/README.md

forbidden:
  - apps/web/design.md, page_map.md, component_map.md (read-only)
  - backend/, docs/, eval/, phases/
  - PROJECT_STATE.md

acceptance:
  - npm install 성공 (또는 의존성 명세만, install은 사용자 환경)
  - npm run build (또는 next build) 성공
  - / 페이지: 텍스트 입력 + 제출 버튼
  - /plan 페이지: 결과 카드 1개 표시 (fetch API 호출 → Slice 1 endpoint)
  - 360px viewport 가로 스크롤 없음 (CSS responsive)
```

### Slice 3 — Critic Agent

```yaml
editable:
  - backend/fastapi/agents/critic.py (신규, P-007 기반)
  - backend/fastapi/agents/__init__.py (export 갱신)
  - backend/fastapi/schemas/output.py (CriticEvaluation 추가, Body에 포함)
  - backend/fastapi/routers/generate.py (Critic 호출 추가)
  - backend/fastapi/tests/test_critic.py (신규)
  - backend/fastapi/tests/conftest.py (mock 갱신)

acceptance:
  - body.critic_evaluation 5필드 이상 채움 (scores)
  - failure_cases FC-001~005 케이스 mock 입력 → Critic이 flag (낮은 점수)
  - revise 호출 없음 (Phase 1은 평가만)
```

### Slice 4 — RAG Lite + fallback

```yaml
editable:
  - backend/fastapi/rag/__init__.py (신규)
  - backend/fastapi/rag/retriever.py (신규)
  - backend/fastapi/rag/fallback.py (신규)
  - backend/fastapi/agents/planning.py (RAG context 주입)
  - backend/fastapi/routers/generate.py (RAG 호출 추가)
  - backend/fastapi/schemas/output.py (rag_references 활성화)
  - backend/fastapi/tests/test_rag_fallback.py (신규)

acceptance:
  - pgvector 끊긴 상태에서도 정상 응답 (fallback)
  - body.rag_references 배열 (빈 배열 허용)
  - validation.warnings에서 phase_1_no_rag 제거
```

### Slice 5 — Supabase 저장

```yaml
editable:
  - backend/fastapi/db/__init__.py (신규)
  - backend/fastapi/db/supabase_client.py (신규)
  - backend/fastapi/db/repositories/video_project.py (신규)
  - backend/fastapi/db/repositories/plan_candidate.py (신규)
  - backend/fastapi/db/migrations/001_init.sql (신규)
  - backend/fastapi/routers/generate.py (저장 호출)
  - backend/fastapi/schemas/output.py (meta.project_id 추가)
  - backend/fastapi/tests/test_db.py (신규)

acceptance:
  - DB 연결 가능 시 video_projects + plan_candidates row 생성
  - DB 연결 실패 시 응답 정상 (저장 오류로 사용자 차단 금지)
  - mock Supabase로 pytest 통과
```

### Slice 7 — Frontend stepper + ErrorCard

```yaml
editable:
  - apps/web/components/ProgressStepper.tsx (신규)
  - apps/web/components/ErrorCard.tsx (신규)
  - apps/web/app/page.tsx (stepper 통합)
  - apps/web/app/plan/page.tsx (ErrorCard 통합)
  - apps/web/public/manifest.json (PWA 기본)
  - apps/web/public/icon-192.png (placeholder)

acceptance:
  - INV-001 응답 → ErrorCard 노출
  - 4단계 stepper 표시 (Intent → Direction → RAG → Plan)
  - manifest.json Chrome DevTools 검증 통과
  - Phase 1 smoke test 8단계 완주
```

---

## 5. 병렬 실행 시 안전 장치

### 5.1 Wave 내 sub-agent들이 동일 파일 수정 방지

```
Wave 1: Slice 2 = backend/ / Slice 6 = apps/web/  → 충돌 0
Wave 4: Slice 5 = backend/ / Slice 7 = apps/web/  → 충돌 0
```

### 5.2 PROJECT_STATE.md / PHASE_REGISTRY.md 충돌 회피

- 모든 sub-agent에 PROJECT_STATE/PHASE_REGISTRY 수정 금지 명시
- main session이 wave 완료 시점에 일괄 갱신

### 5.3 git push 경쟁

- 각 sub-agent가 자체 commit + push 수행
- 병렬 push 시 한쪽 실패하면 → 해당 sub-agent가 git pull --rebase 후 재push
- 또는 main session이 wave 종료 후 push 정리

---

## 6. 진행 트래킹 (실행 완료)

```yaml
phase_1_multi_slice_progress:
  wave_1:
    status: completed
    sub_agents: [A_slice_2, B_slice_6]
    completed_at: 2026-05-26
    commits: [0baff33, d1cafca]
    pytest: 23/23
    frontend_build: pass
  wave_2:
    status: completed
    sub_agents: [C_slice_3]
    completed_at: 2026-05-26
    commits: [7ebe422]
    pytest: 39/39
  wave_3:
    status: completed
    sub_agents: [E_slice_4]
    completed_at: 2026-05-26
    commits: [a55729c]
    pytest: 49/49
  wave_4:
    status: completed
    sub_agents: [F_slice_5, G_slice_7]
    completed_at: 2026-05-26
    commits: [17a0283, 720059b]
    pytest: 62/62
    frontend_build: pass
```

## 7. 최종 결과

```
총 sub-agent dispatch: 6 (Wave 1 병렬 2 + Wave 2 1 + Wave 3 1 + Wave 4 병렬 2)
총 commit: 7 Slice commits + 1 plan commit
파일 통계:
  backend/fastapi/: 28 파일 (agents 6, db 7, rag 5, routers 2, schemas 3, tests 7, config/main/init 4)
  apps/web/: 30 파일 (app 4, components 4, lib 4, public 5, configs 13)
  eval/qa_reports/: 9 reports (entry + slice-1~7 + smoke_test_instructions)
검증:
  pytest: 62/62 PASS
  frontend tsc: 0 errors
  frontend lint: clean
  frontend build: 5 pages compiled
```

## 8. 식별된 후속 항목

- `plan_options` (api_contract §4.2) vs `plan_candidates` (db_schema, Slice 5) — contract-change 필요
- `meta.prompt_id` = Planning(P-006), Intent는 validation.checks (convention 결정)
- ErrorEnvelope 4-필드 minimal (contract §3.2 추가 필드는 Slice 5+ 또는 Phase 2)
- `HTTP_422_UNPROCESSABLE_ENTITY` DeprecationWarning (Starlette upstream, 우리 코드 무영향)
- ProgressStepper 실 SSE 미연결 (Phase 4 SSE migration 시 연결)
- PNG icon → SVG 사용 (Phase 2+ 디자인 작업 시 PNG 보강)
- `/health` slice="3"에서 멈춤 (Slice 4/5/7 미동기화) — Phase 1 종료 시 정리

위 항목은 `eval/qa_reports/phase-1-final_2026-05-26.md`에서 종합 정리.

---

## 7. 종료 조건 (Phase 1 완료)

- Slice 1~7 모두 commit + push
- pytest 전체 통과
- npm run build 성공
- eval/qa_reports/phase-1-final_2026-05-26.md 작성
- smoke test 8단계 완주 (assumptions.md §4.4)
- meta-retrospective Skill로 회고 작성

---

## 8. 변경 이력

- 2026-05-26: 최초 작성 (Slice 1 완료 후, Wave 1~4 분할)
