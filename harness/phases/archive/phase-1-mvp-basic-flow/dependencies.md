# Phase 1 — Dependencies

---

## 이전 Phase 의존성

| Phase | 이름 | 상태 | 필요 이유 |
|---|---|---|---|
| **Phase 0** | 하네스 초기화 (Migration) | ✅ done (2026-05-26) | contracts, Skill, ai_system 구조 확립 |

Phase 0 완료 확인 방법:
- `phases/archive/phase-0-migration/acceptance.md` → 11/11 항목 `[x]`
- `PROJECT_STATE.md` → `phase_0_status: completed`

---

## 외부 서비스 의존성

| 서비스 | 용도 | 준비 필요 여부 |
|---|---|---|
| OpenAI API | gpt-4o-mini (Planning, Critic) + gpt-4o (Critic 일부) | ✅ API Key 필요 |
| Supabase | PostgreSQL + pgvector 호스팅 | ✅ Project 생성 필요 |

### Supabase 셋업 체크리스트

- [ ] Supabase 프로젝트 생성 (free tier 가능)
- [ ] `video_projects` 테이블 생성 (db_schema.md §video_projects)
- [ ] `plan_candidates` 테이블 생성 (db_schema.md §plan_candidates)
- [ ] pgvector extension 활성화 (`CREATE EXTENSION vector;`)
- [ ] `knowledge_chunks` 테이블 생성 (RAG Lite용)
- [ ] `SUPABASE_URL`, `SUPABASE_ANON_KEY` 확인

### OpenAI 셋업 체크리스트

- [ ] API Key 발급
- [ ] 사용 모델: `gpt-4o-mini` (기본), `gpt-4o` (Critic)
- [ ] 예상 비용: Phase 1 개발 중 $1–5 (작은 트래픽)

---

## 코드 의존성 (npm / pip)

Phase 1 시작 시 설치 필요:

### Frontend (Next.js)
```
next@14, react@18, react-dom@18
typescript, tailwindcss
@supabase/supabase-js
```

### Backend (FastAPI)
```
fastapi, uvicorn, pydantic
openai>=1.0
supabase-py
python-dotenv
pgvector (선택, ORM 사용 시)
```

---

## 관련 Contracts (읽어야 할 문서)

Phase 1 작업 시 필수 참조:

| 문서 | 이유 |
|---|---|
| `docs/contracts/api_contract.md` | POST /api/v1/generate 스펙 |
| `docs/contracts/agent_io_contract.md` | 4 Agent 입출력 형식 |
| `docs/contracts/output_schema.md` | 응답 JSON 구조 |
| `docs/contracts/db_schema.md` | 테이블 DDL |
| `ai_system/orchestration/flow.md` | Agent 실행 순서 |
| `ai_system/prompts/prompt_registry.md` | P-001~P-007 프롬프트 |
| `docs/contracts/error_response_contract.md` | 오류 코드 및 형식 |
| `docs/contracts/llm_security_contract.md` | PII 마스킹 (1단계) |

---

## 주의사항

- Phase 1에서는 Supabase Auth **미사용** (Phase 5에서 추가)
- OpenAI 비용이 우려되면 개발 중 `gpt-4o-mini`만 사용해도 됨
- pgvector 연결 실패 시 **fallback 필수** — 오류 반환 금지
