# backend/fastapi — Dreammate Studio FastAPI Backend

> Status: **active** (Phase 1 Slice 1 진행 중)
> Phase: 1 / Slice 1
> Last updated: 2026-05-26

---

## 1. 현재 범위 (Phase 1 Slice 1)

```
POST /api/v1/generate (sync, 1 plan)
GET  /health
GET  /openapi.json
GET  /docs           (Swagger UI)
GET  /redoc
```

**Phase 1 deviation from api_contract.md §8.3** — 의도된 단순화:

| 항목 | Contract (Phase 4 목표) | Phase 1 Slice 1 |
|---|---|---|
| Endpoint | `POST /api/v1/plans/{plan_id}/generate` | `POST /api/v1/generate` |
| 응답 | async ack + SSE | sync |
| plan 수 | 3 | 1 |
| Critic | revise 최대 2회 | 미포함 (Slice 3 추가) |
| RAG | pgvector | fallback dummy (Slice 4) |
| DB 저장 | 필수 | 미포함 (Slice 5) |

Slice 1~7 점진 확장 → Phase 4에서 contract endpoint 정합.
상세: `phases/active/phase-1-mvp-basic-flow/work_plan.md`.

---

## 2. 폴더 구조

```
backend/fastapi/
├── main.py                       FastAPI app + lifespan + CORS
├── config.py                     pydantic-settings (env-based)
├── requirements.txt              의존성 (Slice별 점진 추가)
├── .env.example                  환경변수 템플릿
├── .gitignore                    Python
├── README.md                     이 파일
├── routers/
│   ├── __init__.py
│   └── generate.py               POST /api/v1/generate
├── schemas/
│   ├── __init__.py
│   ├── input.py                  GenerateRequest
│   └── output.py                 Envelope / Meta / Body / Plan / Validation
├── agents/
│   ├── __init__.py
│   └── intent_planning.py        Intent + Planning 통합 1회 호출 (임시)
└── tests/
    ├── __init__.py
    ├── conftest.py               OpenAI mock fixture
    └── test_e2e_slice1.py        Slice 1 acceptance
```

Slice별 추가 예정:
- Slice 2: `agents/intent.py`, `agents/planning.py`
- Slice 3: `agents/critic.py`
- Slice 4: `rag/retriever.py`, `rag/fallback.py`
- Slice 5: `db/supabase_client.py`, `db/repositories/`

---

## 3. 실행

### 3.1 의존성 설치

```bash
cd backend/fastapi
python -m venv .venv
source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3.2 환경변수 설정

```bash
cp .env.example .env
# .env 편집:
# OPENAI_API_KEY=sk-...
```

### 3.3 서버 기동

```bash
# 프로젝트 루트(harness/)에서:
uvicorn backend.fastapi.main:app --reload --port 8000

# 또는 backend/fastapi/에서:
uvicorn main:app --reload --port 8000
```

### 3.4 동작 검증 (curl)

```bash
curl -X POST http://localhost:8000/api/v1/generate \
  -H "Content-Type: application/json" \
  -d '{"input":"유튜브 채널 첫 영상 기획해줘"}'
```

기대 응답: `200 OK` + envelope JSON (meta / body / validation).

### 3.5 OpenAPI 문서

기동 후 브라우저에서 `http://localhost:8000/docs` 접속.

---

## 4. 테스트

```bash
# 프로젝트 루트(harness/)에서:
pytest backend/fastapi/tests/ -v

# 또는:
cd backend/fastapi
pytest tests/ -v
```

**테스트 특징:**
- OpenAI API 키 없이도 통과 (conftest.py에서 mock 주입)
- Slice 1 acceptance A1 + A6 자동 검증
- pytest 8.x + httpx TestClient

---

## 5. 관련 문서

### 5.1 Contracts (참조용, 수정 금지)

- `docs/contracts/api_contract.md` §8.3 (Phase 4 migration 목표)
- `docs/contracts/output_schema.md` (envelope 정의)
- `docs/contracts/agent_io_contract.md` (Agent IO)
- `docs/contracts/error_response_contract.md` (Slice 2부터 사용)
- `docs/contracts/llm_security_contract.md` (Slice 2+ PII 마스킹)

### 5.2 Phase 1 컨텍스트

- `phases/active/phase-1-mvp-basic-flow/goals.md`
- `phases/active/phase-1-mvp-basic-flow/scope.md`
- `phases/active/phase-1-mvp-basic-flow/assumptions.md` (4점검 결과)
- `phases/active/phase-1-mvp-basic-flow/work_plan.md` (Slice 1~7)
- `phases/active/phase-1-mvp-basic-flow/acceptance.md` (A1~A8)

### 5.3 결정 기록

- `docs/decisions/phase_1_simplest_slice.md` (ADR-008)
- `docs/decisions/eval_dual_track.md` (ADR-009)
- `docs/decisions/backend_strategy.md`

### 5.4 평가

- `eval/INDEX.md` (이원 트랙 색인)
- `eval/qa_reports/phase-1-entry-check_2026-05-26.md`
- `eval/golden_set.md` (Slice 2에서 사용)
- `eval/failure_cases.md` (Slice 3에서 사용)

---

## 6. 변경 이력

- 2026-05-26: Slice 1 진입 — placeholder → active 전환, 코어 7파일 신규 작성
