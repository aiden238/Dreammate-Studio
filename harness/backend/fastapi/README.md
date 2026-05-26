# backend/fastapi

> ⚠️ **PLACEHOLDER** — 본 파일은 향후 Phase에서 채워질 예정.
> 현재는 스코프와 트리거만 명시. 정상 사용 금지.

## Status

```yaml
status: placeholder
fill_in_phase: 1+
priority: high
estimated_final_lines: 180
last_updated: 2026-05-26
```

## Why Placeholder?

FastAPI 백엔드 코드가 존재하지 않는 Phase 0 단계에서는 폴더 구조, 라우터
설계, 테스트 셋업을 확정할 수 없다. Phase 1 첫 endpoint 구현 시작 시 작성한다.

## Scope (TBD)

본 파일이 다룰 범위:
- FastAPI 백엔드 전체 폴더 구조 (라우터 / 서비스 / 리포지토리 계층)
- Pydantic v2 모델 정의 방식 (`output_schema.md` 기반)
- OpenAPI 자동 생성 설정 (`/docs`, `/openapi.json` 경로)
- SQLAlchemy (또는 대체) ORM 설정 및 마이그레이션
- LLM 호출 계층 (Anthropic SDK + prompt_registry 연계)
- RAG 검색 계층 (Claude SDK RAG Lite → pgvector 연계)
- MOA Lite 오케스트레이션 (Intent → Planning → Critic → Rewriter)
- 테스트 셋업 (pytest-asyncio, httpx TestClient)

## Known Dependencies (when filled in)

- `docs/contracts/tech_stack_contract.md` — Python 버전, 프레임워크 버전
- `docs/contracts/api_contract.md` — 엔드포인트 스펙 원천
- `docs/contracts/output_schema.md` — Pydantic 모델 기준
- `ai_system/architecture.md` — MOA Lite 오케스트레이션 구조
- `knowledge/rag/retrieval_policy.md` — RAG 검색 정책
- `docs/decisions/backend_strategy.md` — 아키텍처 결정 기록

## Fill-In Trigger

다음 조건 충족 시 본 파일 작성 착수:
- Phase 1 진입 및 `backend/fastapi/` 폴더 첫 코드 파일 생성
- `pyproject.toml` 의존성 확정 및 FastAPI 앱 초기화 완료

## 예시 폴더 구조 (fill-in 시 참고)

```
backend/fastapi/
├── app/
│   ├── main.py              # FastAPI 앱 진입점
│   ├── routers/             # API 라우터 (plans, feedback, search)
│   ├── services/            # 비즈니스 로직 (moa_service, rag_service)
│   ├── repositories/        # DB 접근 계층
│   ├── models/              # Pydantic 모델 (output_schema 기반)
│   └── core/                # 설정, 의존성 주입, 미들웨어
├── tests/                   # pytest 테스트
└── pyproject.toml           # 의존성 관리
```

## Related Skill / Phase

- Skill: agent-io-check, qa-check
- Phase: 1+
- 책임자: AI / 운영자
