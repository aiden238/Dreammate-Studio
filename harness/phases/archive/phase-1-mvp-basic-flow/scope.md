# Phase 1 — Scope

> Phase 1의 **작업 범위**를 명시한다. scope 밖 요청은 non_goals.md 확인 후 거절 또는 후속 Phase로 이관.

---

## In Scope

### Frontend (Next.js 14 PWA)

| 항목 | 설명 | 파일 위치 |
|---|---|---|
| 입력 페이지 (`/`) | 텍스트 입력 + 제출 버튼 | `apps/web/app/page.tsx` |
| 결과 페이지 (`/plan`) | 기획안 카드 1개 표시 | `apps/web/app/plan/page.tsx` |
| 진행 표시 | 4단계 progress stepper | `apps/web/components/ProgressStepper.tsx` |
| 오류 표시 | INV/LLM/RAG 오류 메시지 | `apps/web/components/ErrorCard.tsx` |
| PWA 기본 설정 | `manifest.json`, `next.config.js` | — |

UI 완성도 낮아도 됨. 흐름 증명 우선.

### Backend (FastAPI)

| 항목 | 설명 | 파일 위치 |
|---|---|---|
| `POST /api/v1/generate` | 핵심 endpoint | `backend/fastapi/routers/generate.py` |
| Intent Agent 호출 | P-001 프롬프트, 영상기획 외 차단 | `backend/fastapi/agents/intent.py` |
| Direction 생성 | P-002 프롬프트, 한 줄 방향 | `backend/fastapi/agents/direction.py` |
| RAG Lite 검색 | pgvector 검색 + fallback | `backend/fastapi/rag/retriever.py` |
| Planning Agent 호출 | P-003~P-006, 기획안 1개 | `backend/fastapi/agents/planning.py` |
| Critic Agent 호출 | P-007 프롬프트, 1회 평가 | `backend/fastapi/agents/critic.py` |
| output_schema 직렬화 | v1.0 준수 | `backend/fastapi/schemas/output.py` |
| `.env` 로드 | OPENAI_API_KEY, SUPABASE_URL 등 | `backend/fastapi/.env.example` |

### DB (Supabase / PostgreSQL)

| 항목 | 설명 |
|---|---|
| `video_projects` 테이블 생성 | db_schema.md §video_projects 기준 |
| `plan_candidates` 테이블 생성 | 기획안 1개 저장 |
| 익명 저장 (auth 없이) | Phase 5에서 Auth 추가 |

### 환경 구성

- `apps/web/.env.local.example`
- `backend/fastapi/.env.example`
- Docker Compose (선택, 로컬 실행 편의)

---

## 범위 경계 (Boundary)

```
Phase 1 포함                           Phase 1 미포함
─────────────────────────────────      ─────────────────────────────────
POST /api/v1/generate (단일 EP)        Discovery Wizard UI (Phase 3)
Quick Mode 입력 흐름 (텍스트 1개)      Quick Mode 카드 UI (Phase 3)
기획안 1개 생성                        기획안 3개 비교 (Phase 4+)
Critic 평가 1회                        Critic revise 2회 (Phase 4+)
익명 저장                              로그인 / 회원가입 (Phase 5)
pgvector fallback RAG               Brand Memory 추출 (Phase 4+)
```

---

## 예상 파일 변경 목록

```
apps/web/
  app/page.tsx              (신규)
  app/plan/page.tsx         (신규)
  app/layout.tsx            (신규)
  components/ProgressStepper.tsx  (신규)
  components/ErrorCard.tsx        (신규)
  public/manifest.json      (신규)
  next.config.js            (신규)
  package.json              (신규)

backend/fastapi/
  main.py                   (신규)
  routers/generate.py       (신규)
  agents/intent.py          (신규)
  agents/direction.py       (신규)
  agents/planning.py        (신규)
  agents/critic.py          (신규)
  rag/retriever.py          (신규)
  schemas/output.py         (신규)
  .env.example              (신규)
  requirements.txt          (신규)
```

---

## 완료 기준 요약

전체 완료 기준은 `acceptance.md` 참조.  
핵심: **텍스트 입력 → 기획안 1개 + Critic 평가 JSON 반환** end-to-end 동작.
