# backend_strategy.md — 백엔드 전략 결정 (ADR)

> 위치: `docs/decisions/backend_strategy.md`
> 상태: Phase 0 Sprint S5 deep 작성 (placeholder 해소)
> 참조: `docs/contracts/tech_stack_contract.md` §2.2, `docs/contracts/api_contract.md`
> 참조: `docs/contracts/db_schema.md`, `ai_system/orchestration/flow.md`

---

## 0. 결정 요약

```
MVP (Phase 1~10):
- FastAPI (Python 3.11+)
- Pydantic v2 (검증)
- SQLAlchemy 2.x (ORM, async)
- Alembic (migration)
- 동기 처리 + SSE (비동기는 Phase 11+)

Phase 11+:
- Celery 또는 Arq (비동기 큐) 도입 검토

Phase 21+:
- Spring Boot (Java/Kotlin) 또는 NestJS 마이그레이션 검토
```

---

## 1. FastAPI 선택 이유

```
1. Python LLM 생태계 친화
   - OpenAI 공식 Python SDK 사용
   - LangChain / LlamaIndex 등 LLM 라이브러리 풍부
   - LLM ↔ 영상기획 도메인 데이터 처리에 Python이 자연

2. Pydantic v2의 강력함
   - 자동 schema validation (output_schema 의무)
   - JSON Schema 자동 생성 (api_contract.md 자동 doc)
   - 타입 안전성 (mypy strict)

3. 빠른 개발
   - 데코레이터 기반 routing (Flask / Express 친화)
   - 의존성 주입 내장
   - 자동 OpenAPI docs

4. 성능
   - Starlette + uvicorn (async 우수)
   - LLM 호출 (I/O bound) 처리에 적합
   - Node.js Express 대비 동등 또는 더 빠름

5. 학습 곡선
   - 기본 Python 익숙하면 즉시 시작 가능
   - 한국 백엔드 개발자 친화 (Django / Flask 출신 많음)
```

→ `docs/decisions/tech_stack_decision.md` §2.2 정합

---

## 2. ORM 선택: SQLAlchemy 2.x vs Tortoise vs raw SQL

| 기준 | SQLAlchemy 2.x | Tortoise ORM | raw SQL |
|---|---|---|---|
| 성숙도 | 매우 높음 | 중간 | (N/A) |
| async 지원 | ✓ (2.x) | ✓ | (수동) |
| 타입 힌트 | 우수 (Mapped[]) | 좋음 | 없음 |
| migration | Alembic (강력) | aerich | (수동) |
| 복잡한 query | 강함 (Core + ORM) | 중간 | 가장 강함 |
| pgvector 지원 | sqlalchemy-pgvector | 제한적 | 자유 |
| 학습 곡선 | 중간 (2.x 새 API) | 낮음 | 낮음 (SQL만 알면) |

**선택: SQLAlchemy 2.x**

```
이유:
- 성숙도가 압도적으로 높음 (Django ORM 다음 표준).
- async + 타입 힌트 (Mapped[]) 2.x에서 우수.
- Alembic은 가장 강력한 Python migration 도구.
- pgvector 검색은 raw SQL과 ORM 혼합 사용 (rag_chunks 등).
```

---

## 3. 비동기 처리 정책

### 3.1 현재 (Phase 1~10): 동기 + SSE

```
영상기획 1건 (대기 60초+):
1. 클라이언트가 POST /api/plan 요청
2. FastAPI가 SSE 스트림 시작
3. 4단계 (Intent → RAG → Plan → Critic) 진행
4. 각 단계 완료 시 SSE event 발송 (4단계 progress stepper UX)
5. 완료 시 결과 응답 + 스트림 종료

장점: 단순 + 추가 인프라 없음.
단점: FastAPI worker 1개가 60초 동안 점유 (concurrency 제약).
```

### 3.2 Phase 11+: Celery / Arq 도입 검토

```
트리거 조건:
- 동시 사용자 100명 이상
- worker pool 부족 발생
- P-AUX-2 백그라운드 큐 (memory extractor 등) 부하 증가

도입 후 흐름:
1. POST /api/plan → task_id 즉시 반환
2. 클라이언트 polling 또는 webhook
3. Celery worker가 4단계 비동기 진행
4. 완료 시 결과 저장 + 알림

Celery vs Arq:
- Celery: 표준 + 풍부한 기능 + Redis 의존
- Arq: 가벼움 + asyncio 친화 + 학습 곡선 낮음
- 결정: Phase 11+ 진입 시 multi-llm-validation으로 재검토
```

---

## 4. 인증 / 인가

```
인증 (Authentication):
- Supabase Auth (Email + Google + GitHub OAuth)
- JWT 발급 (Supabase가 자동)
- frontend에서 Supabase JS SDK 사용

인가 (Authorization):
- 사용자 데이터 (Brand / Series / Video Project): RLS (Row Level Security)
- 운영 테이블 (agent_io_logs 등): service role key (RLS 우회)
- service role key는 backend env에만 존재 (절대 client 노출 금지)

흐름:
1. 사용자 로그인 → Supabase Auth → JWT 발급
2. Frontend가 JWT를 Authorization header로 backend에 전송
3. Backend가 JWT 검증 → user_id 추출
4. SQLAlchemy session: user 컨텍스트 (사용자 데이터)
5. Service role: 운영 데이터 (RLS 우회)

위반 시: E-INV-007 ("권한이 없는 항목이에요")
```

→ `docs/contracts/api_contract.md` §0 (헤더), `docs/contracts/db_schema.md` §4 (RLS)

---

## 5. Phase 21+ Spring Boot 마이그레이션 후보

```
Spring Boot 후보 이유 (Phase 21+):
- 대규모 트래픽 처리 (Java JIT + Tomcat/Netty)
- multi-tenant 인프라 친화 (enterprise tier)
- 한국 기업 표준 (인력 풀, 협업 친화)
- gRPC / 메시지 큐 (Kafka) 통합 친화

마이그레이션 시나리오:
1. FastAPI ↔ Spring Boot 부하 테스트 (multi-llm-validation)
2. 결과 정합성 비교 (output_schema 동일성)
3. 점진 마이그레이션 (endpoint 단위 이전)
4. dual-write 기간 → cutover → FastAPI 폐기

지연 트리거:
- 동시 사용자 1000명 미만 → Spring 불필요
- 비용 효율성 충분 → FastAPI 유지
- 마이그레이션 비용 > 효익 → 보류

→ 자세한 검토는 Phase 22에서 (PHASE_REGISTRY.md)
```

---

## 6. 코드 구조 (제안, Phase 1+ 확정)

```
backend/fastapi/
├── app/
│   ├── api/                # endpoint 정의 (FastAPI router)
│   │   ├── v1/
│   │   │   ├── intent.py
│   │   │   ├── plan.py
│   │   │   ├── critic.py
│   │   │   └── ...
│   ├── core/               # 설정, 의존성 주입
│   ├── models/             # SQLAlchemy models
│   ├── schemas/            # Pydantic schemas (output_schema 준수)
│   ├── services/           # 비즈니스 로직
│   │   ├── agents/         # MOA Lite agents
│   │   └── rag/            # RAG 로직
│   ├── repositories/       # DB 접근
│   └── utils/              # 공통 유틸
├── alembic/                # migration
├── tests/
└── pyproject.toml
```

→ Phase 4 진입 시 정식 확정 (`backend/fastapi/README.md`)

---

## 7. 측정 / 모니터링

```
Sentry (Phase 2+):
- error 자동 수집
- performance tracing
- request_id / trace_id 자동 부착

OpenTelemetry (Phase 7+):
- FastAPI ↔ LLM ↔ DB ↔ Redis 분산 추적
- p50 / p95 / p99 응답 시간

agent_io_logs:
- 모든 LLM 호출 로그 (SDK 자동)
- 사용자 데이터 분석용

운영자 콘솔 (Phase 11+):
- 사용자별 비용 / 에러율
- 실시간 모니터링
```

→ `docs/decisions/observability_strategy.md`

---

## 8. 의존성 관리

```
- requirements.txt 또는 poetry.lock 강제
- 모든 dependency 정확한 버전 고정
- pip install --require-hashes 권장
- 자동 minor 업그레이드 금지

보안 패치:
- pip-audit 주간 실행
- Critical CVE: 24시간 내 patch
- High CVE: 7일 내 patch
```

→ `docs/contracts/tech_stack_contract.md` §7, §8

---

## 9. 재검토 트리거

```
1. 동시 사용자 100명 도달 → 비동기 처리 도입 (Celery/Arq)
2. FastAPI worker pool 부족 → 인프라 scale-up 또는 비동기
3. Sentry 에러율 1% 초과 → 코드 품질 review
4. p95 응답 시간 60초 초과 → DB index / 캐시 강화
5. Phase 21+ 진입 → Spring Boot 마이그레이션 검토
6. multi-tenant 요구 (enterprise tier) → 코드 구조 재설계
```

---

## 10. 변경 이력

```
v1.0.0 (2026-05-26): Phase 0 Sprint S5-1. placeholder 해소 + deep 작성.
                      FastAPI 선택 이유, ORM 비교, 비동기 정책, 인증/인가,
                      Spring Boot 후보, 코드 구조 제안, 재검토 트리거.
```
