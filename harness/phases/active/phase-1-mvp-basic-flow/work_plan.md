# Phase 1 — Work Plan (Slice 분해)

> phase-start v1.1.0 §6.2 Simplest Slice 기반 작업 단위 분해
> 작성일: 2026-05-26
> 적용 원칙: 각 Slice는 독립 commit + 자동 테스트 통과 후 다음 Slice 진입

---

## Slice 개요

```
Slice 1 → Slice 2 → Slice 3 → Slice 4 → Slice 5 → Slice 6 → Slice 7
  ↓        ↓        ↓        ↓        ↓        ↓        ↓
 API     Agent    Critic   RAG      DB       UI      Polish
 부트    분리     평가     fallback 저장     진입     완성
```

각 Slice 완료 = 1개 commit + smoke test 통과 + assumptions.md notes 갱신.

---

## Slice 1 — FastAPI 단일 endpoint + JSON 반환

**목표**: `curl POST /api/v1/generate` 로 schema-valid JSON 1개 반환

### 산출물 (5 파일)
- `backend/fastapi/main.py` (FastAPI app)
- `backend/fastapi/routers/generate.py` (POST endpoint)
- `backend/fastapi/schemas/output.py` (Pydantic envelope/body/validation)
- `backend/fastapi/schemas/input.py` (request body)
- `backend/fastapi/.env.example`
- `backend/fastapi/requirements.txt`

### 구현 핵심
- gpt-4o-mini 1회 호출 (Intent + Planning 통합 단일 프롬프트)
- prompt_registry P-001 + P-006 결합 임시 프롬프트 사용 (Slice 2에서 분리)
- 더미 RAG (빈 배열), 더미 Critic (null) 채워서 schema 준수

### Acceptance
- [ ] `uvicorn main:app` 기동
- [ ] curl 호출 시 HTTP 200 + output_schema v1.0 구조 준수
- [ ] `pytest backend/tests/e2e_slice1.py` 통과

### 추정 시간
2~3시간

### Commit message
```
phase-1(slice-1): FastAPI POST /api/v1/generate skeleton + schema-valid JSON
```

---

## Slice 2 — Intent / Planning Agent 분리

**목표**: 단일 호출 → 2개 Agent 직렬 호출 (Intent → Planning)

### 산출물
- `backend/fastapi/agents/intent.py` (P-001 Intent Agent)
- `backend/fastapi/agents/planning.py` (P-006 Planning Agent)
- `backend/fastapi/agents/__init__.py`

### 구현 핵심
- Intent Agent: 영상기획 외 입력 → `INV-001` 반환
- Planning Agent: Intent 통과 시 plan_candidate 1개 생성
- Agent 간 IO는 `docs/contracts/agent_io_contract.md` 준수

### Acceptance
- [ ] golden_set GS-001, GS-002, GS-003 케이스 통과
- [ ] 비관련 입력 → `error.code == "INV-001"`
- [ ] `pytest backend/tests/intent.py` 통과
- [ ] `pytest backend/tests/planning.py` 통과

### 추정 시간
3~4시간

### Commit message
```
phase-1(slice-2): split into Intent + Planning agents with INV-001 filter
```

---

## Slice 3 — Critic Agent 추가

**목표**: Planning 결과를 Critic이 평가 (revise 없이 1회)

### 산출물
- `backend/fastapi/agents/critic.py` (P-007 Critic Agent, 평가만)
- `backend/fastapi/tests/critic.py`

### 구현 핵심
- gpt-4o (Critic은 더 강한 모델, agent_io_contract §critic)
- 평가 5차원 점수: hook / target_fit / brand / execution / overall
- revise 호출 없음 (Phase 4+ 에서 추가)

### Acceptance
- [ ] `body.critic_evaluation.scores` 5필드 모두 채움
- [ ] `body.critic_evaluation.suggestions` 배열 (revise 없이 제안만)
- [ ] `pytest backend/tests/critic.py` 통과

### 추정 시간
2~3시간

### Commit message
```
phase-1(slice-3): add Critic agent with 5-dimension scoring (no revise)
```

---

## Slice 4 — RAG Lite + fallback

**목표**: pgvector 검색 → 결과 또는 fallback (빈 배열) 반환

### 산출물
- `backend/fastapi/rag/retriever.py` (pgvector 검색)
- `backend/fastapi/rag/fallback.py` (실패 시 빈 배열)
- `backend/fastapi/rag/__init__.py`

### 구현 핵심
- pgvector 연결 실패 → 오류 반환 금지, fallback 호출
- top_k=3 검색, similarity threshold 0.7
- 결과를 Planning Agent에 context 주입

### Acceptance
- [ ] pgvector 미연결 상태에서도 정상 응답
- [ ] `body.rag_references` 배열 채움 (빈 배열 허용)
- [ ] `pytest backend/tests/rag_fallback.py` 통과

### 추정 시간
3~4시간

### Commit message
```
phase-1(slice-4): RAG Lite retriever with pgvector + graceful fallback
```

---

## Slice 5 — Supabase 저장

**목표**: 기획안 생성 결과를 `video_projects` + `plan_candidates` 테이블에 저장

### 산출물
- `backend/fastapi/db/supabase_client.py`
- `backend/fastapi/db/repositories/video_project.py`
- `backend/fastapi/db/repositories/plan_candidate.py`
- Supabase migration: `video_projects`, `plan_candidates` 테이블 (db_schema.md 준수)

### 구현 핵심
- 인증 없이 익명 저장 (`user_id` NULL 허용)
- 저장 실패 시 응답은 정상 (저장 오류로 사용자 차단 금지)
- 저장 결과를 `meta.project_id`에 포함

### Acceptance
- [ ] `video_projects` row 생성 확인
- [ ] `plan_candidates` row 생성 확인
- [ ] DB 연결 실패 시도 응답 정상 (`meta.project_id == null`)
- [ ] `pytest backend/tests/db.py` 통과

### 추정 시간
3~4시간

### Commit message
```
phase-1(slice-5): Supabase persistence for video_projects + plan_candidates
```

---

## Slice 6 — Next.js 진입 UI

**목표**: `/` 입력 → `/plan` 결과 표시 (최소 UI)

### 산출물
- `apps/web/app/page.tsx` (입력)
- `apps/web/app/plan/page.tsx` (결과)
- `apps/web/app/layout.tsx`
- `apps/web/components/PlanCard.tsx`
- `apps/web/lib/api.ts` (fetch wrapper)
- `apps/web/package.json`, `tsconfig.json`, `next.config.js`, `tailwind.config.ts`

### 구현 핵심
- 텍스트 입력 + 제출 버튼만 (Wizard UI는 Phase 3)
- 제출 → backend 호출 → `/plan` 라우팅 + 결과 표시
- 스타일링 최소 (TailwindCSS 기본만)

### Acceptance
- [ ] `npm run dev` 후 http://localhost:3000 접근 가능
- [ ] 텍스트 입력 + 제출 동작
- [ ] `/plan` 페이지에서 카드 1개 표시
- [ ] 360px 모바일 뷰포트에서 가로 스크롤 없음

### 추정 시간
4~5시간

### Commit message
```
phase-1(slice-6): Next.js 14 PWA entry pages (input + plan)
```

---

## Slice 7 — 진행 stepper + 오류 카드

**목표**: 4단계 progress + INV/LLM/RAG 오류 표시

### 산출물
- `apps/web/components/ProgressStepper.tsx` (Intent → Direction → RAG → Plan)
- `apps/web/components/ErrorCard.tsx` (오류 코드별 메시지)
- `apps/web/public/manifest.json` (PWA 기본)

### 구현 핵심
- 진행 stepper는 폴링 또는 SSE 둘 중 단순한 쪽 (Phase 1은 폴링 권장)
- 오류 카드는 `error_response_contract.md` 형식 준수
- PWA manifest는 아이콘 1개 + 이름만 (배포는 Phase 10)

### Acceptance
- [ ] 4단계 stepper 표시
- [ ] INV-001 오류 시 ErrorCard 노출
- [ ] manifest.json 유효 (Chrome DevTools 검증)
- [ ] **Phase 1 전체 smoke test 8단계 통과** (assumptions.md §4.4)

### 추정 시간
3~4시간

### Commit message
```
phase-1(slice-7): progress stepper + error card + PWA manifest (Phase 1 complete)
```

---

## 전체 추정

| Slice | 추정 시간 | 누적 |
|---|---|---|
| 1 | 2~3h | 2~3h |
| 2 | 3~4h | 5~7h |
| 3 | 2~3h | 7~10h |
| 4 | 3~4h | 10~14h |
| 5 | 3~4h | 13~18h |
| 6 | 4~5h | 17~23h |
| 7 | 3~4h | 20~27h |

**Phase 1 총 예상**: 20~27시간 (1.5~2주 part-time 또는 4~5일 full-time)

---

## Slice 진입 규칙

```
1. 이전 Slice 모든 acceptance 통과 확인
2. assumptions.md §1.2 불확실 항목 중 해당하는 것 검증
3. 다음 Slice의 산출물 / acceptance 재확인
4. 작업 시작
5. 완료 시:
   - pytest 통과
   - git commit (Slice 단위 message)
   - meta/handoffs/ 누적 기록 (선택)
   - PROJECT_STATE.md migration_progress 갱신
```

---

## scope creep 경고

다음 발견 시 즉시 작업 중단:
- assumptions.md §3.2 read-only 파일 수정 필요성
- non_goals.md 항목 구현 유혹
- Slice 범위 초과 산출물 (예: Slice 1에서 UI도 같이)
- "조금만 더" 추가 기능

→ 사용자에게 알림 + 결정 요청.

---

## 변경 이력

- 2026-05-26: Slice 1~7 최초 작성 (Simplest Slice 도출 결과 반영)
