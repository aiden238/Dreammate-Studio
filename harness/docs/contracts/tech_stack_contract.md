# tech_stack_contract.md — 기술 스택 고정 + Phase별 확장 정책

> 위치: `docs/contracts/tech_stack_contract.md`
> 상태: Phase 0–1 진입용 핵심 contract 초안
> 참조: `docs/contracts/api_contract.md` §0 (헤더 fix), §14 (CORS allowlist)
> 참조: `docs/contracts/db_schema.md` §1 (PostgreSQL + pgvector 전제)
> 참조: `docs/contracts/frontend_design_contract.md` §6.2 (PWA)
> 참조: `docs/contracts/env_contract.md` (placeholder, 환경변수 관리)
> 참조: `docs/contracts/backend_boundary.md` (placeholder, 백엔드 책임 경계)
> 참조: `docs/contracts/frontend_boundary.md` (placeholder, 프론트엔드 책임 경계)
> 참조: `product/mvp_scope.md`

---

## 0. 이 문서의 위치

영상기획 AI 에이전트 플랫폼의 **기술 선택을 고정**한다. 각 contract는 자기 책임 범위 안에서 본 contract의 선택을 전제로 작성된다. 본 contract 변경은 항상 contract-change Skill 절차 + multi-llm-validation 검증을 거친다.

이 contract가 정의하는 대상:

1. MVP 스택 (Phase 1~10)
2. Supabase + PostgreSQL 병행 사용 정책
3. Phase 21+ 확장 후보 (장기 비전)
4. MVP 후 조정 가능성 (provider 변경, 모바일 진입 등)
5. 버전 잠금 / 보안 패치 정책
6. 일관성 유지 원칙 (변경 시 절차)

---

## 1. 설계 원칙

```
1. MVP는 "검증된 + 운영 부담 작은 + 빠른 반복" 우선. 신기술 도입 보류.
2. Frontend / Backend / DB / LLM / Cache의 5개 layer를 명시. 책임 분리.
3. Supabase는 Auth/RLS/Realtime/Storage를 빠르게 활용. PostgreSQL은 같은 DB를
   백엔드(FastAPI)에서 ORM + pgvector로 직접 접근. 두 layer는 동일 DB를 향함.
4. 모든 의존성은 lockfile(package-lock.json / poetry.lock 또는 requirements.txt)로
   고정. 자동 minor 업그레이드 금지.
5. provider 변경은 multi-llm-validation Skill로 양쪽 비교 후 결정.
6. 본 contract의 변경은 dependency_map.yaml의 영향 파일 모두 검토 후 적용.
7. Phase 진입 시점에 본 contract의 "MVP 후 조정 가능성" 섹션을 검토.
```

---

## 2. MVP 스택 (Phase 1–10)

### 2.1 Frontend

```
- 프레임워크: Next.js 14 (App Router)
- 언어: TypeScript 5.x (strict mode)
- 스타일: Tailwind CSS 3.x
- UI 컴포넌트: shadcn/ui (Radix UI 기반)
- PWA: next-pwa + workbox (오프라인 미지원, "설치 가능"만)
- 상태 관리:
    - 서버 상태: SWR 또는 TanStack Query (Phase 1 시점 선택)
    - 클라이언트 로컬 상태: React useState + Context
    - 전역 상태: 도입 보류 (Phase 5+ Zustand 또는 Jotai 검토)
- 폼: React Hook Form + zod (스키마 검증)
- 분석: Vercel Analytics (Phase 1), Sentry (Phase 2+ 에러 추적)
```

### 2.2 Backend

```
- 프레임워크: FastAPI (Python 3.11+)
- 검증: Pydantic v2
- ORM: SQLAlchemy 2.x (async)
- 마이그레이션: Alembic
- 비동기 작업: 동기 처리 + SSE (Phase 1). Celery/Arq는 Phase 11+ 검토.
- 테스트: pytest + pytest-asyncio
- 린트: ruff + mypy (strict)
```

### 2.3 Database

**Supabase + PostgreSQL 병행 사용.** 동일 DB를 두 layer가 향함:

```
공통:
- PostgreSQL 15+ on Supabase 인프라
- pgvector extension (1536 차원, ivfflat 인덱스)

Supabase layer 책임 (직접 client SDK 사용):
- Auth: Supabase Auth (email/password + OAuth Google/GitHub)
- RLS: 사용자 데이터 접근 제어 (db_schema.md §4 정책)
- Realtime: postgres_changes 채널 (Phase 5+ 사용 검토, MVP에서는 미사용)
- Storage: 사용자 업로드 파일 (Phase 5+, MVP는 미사용)

PostgreSQL direct layer 책임 (FastAPI에서 직접 접근):
- 비즈니스 로직 / 트랜잭션 (SQLAlchemy)
- pgvector 검색 (rag_chunks)
- agent_io_logs / intent_filter_logs 등 운영 테이블 (service role key 사용)
- 백그라운드 작업 (memory extractor 등)

데이터 일관성:
- 동일 DB이므로 데이터는 자동 일관
- RLS는 user-facing 경로 (Supabase JS SDK)에만 적용
- 백엔드는 service role key로 RLS 우회 가능 (보안: server-side에서만)
```

### 2.4 LLM / Embedding

```
provider: OpenAI (Phase 1)
models:
- gpt-4o-mini: 기본 prompt 모두 (P-001 ~ P-006, P-008, P-AUX-1, P-AUX-2)
- gpt-4o: Critic (P-007) 표준 모드만. cost_saving 시 gpt-4o-mini 폴백.
- text-embedding-3-small: RAG embedding (1536 차원)

비용 단가 (2026-05 시점):
- gpt-4o-mini:        $0.15 / 1M input, $0.60 / 1M output
- gpt-4o:             $2.50 / 1M input, $10.00 / 1M output
- embedding-3-small:  $0.02 / 1M tokens

호출 라이브러리: openai (Python SDK 공식)
fallback provider: Anthropic Claude 3.5 Haiku (Phase 5+ 도입 검토, 본 contract v1에서는 OpenAI 단일)
```

### 2.5 Cache / Queue

```
Cache: Redis (Upstash 또는 Render Redis)
- rate limit counters (rate_limit_policy.md §4)
- session cache
- idempotency key (api_contract.md §17)
- 비용 누적 cache (5분 sync)

Queue: 없음 (Phase 1)
- 비동기 작업은 FastAPI BackgroundTasks (in-process) 또는 SSE
- Phase 11+ Celery 또는 Arq 도입 시점은 P-AUX-2 백그라운드 큐가 일정 수준 부하 도달 시
```

### 2.6 Deploy

```
Phase 1:
- Frontend: Vercel (Next.js 공식 호스팅)
- Backend: Render (Python web service) 또는 Railway
- DB: Supabase (managed PostgreSQL)
- Cache: Upstash Redis (serverless) 또는 Render Redis

Phase 5+:
- CDN: Vercel Edge Network (자동) + Cloudflare 옵션
- Backend autoscaling: Render의 autoscaling 또는 Fly.io 검토

Phase 21+:
- AWS ECS / EKS 검토 (비용 + 통제 +/- 트레이드오프 측정 후)
- 자체 Kubernetes는 비추천 (운영 부담)
```

### 2.7 CI / Observability

```
CI: GitHub Actions
- PR 시: lint + typecheck + unit test
- main merge 시: build + deploy preview
- nightly: eval/regression_results/ 회귀 자동 실행 (Phase 7+)

Observability:
- Sentry (Phase 2+): errors + performance
- OpenTelemetry (Phase 7+): 분산 추적 (FastAPI ↔ LLM ↔ DB)
- Vercel Analytics (Phase 1): 페이지 뷰
- 운영자 콘솔 (Phase 11+): 사용자별 비용 / 에러율
```

---

## 3. 병행 사용 (Supabase + PostgreSQL) 이유

```
Supabase 사용 이유:
- Auth 빠르게 구축 (이메일 인증, OAuth 즉시 사용)
- RLS로 user 데이터 자동 격리 (RLS 정책만 작성)
- Realtime / Storage 추후 필요 시 즉시 사용
- managed PostgreSQL (백업, 모니터링 자동)

PostgreSQL direct 사용 이유:
- FastAPI에서 ORM(SQLAlchemy) 사용 — 비즈니스 로직 표현력
- pgvector 검색은 ORM보다 raw SQL이 자연스러움
- service role key로 RLS 우회가 필요한 운영 테이블 (agent_io_logs 등)
- 트랜잭션 / 복잡한 join은 backend에서 처리

함정 (주의):
- Supabase client SDK가 RLS 적용된 row를 직접 INSERT/UPDATE 시,
  backend의 ORM session과 캐시 정합성에 주의 (특히 brand_memory_entries).
- service role key는 절대 client에 노출 금지. backend env에서만 사용.
- 두 layer가 같은 table을 동시 write하는 경로는 최소화. 가능하면 backend가
  단일 write 경로 (Supabase는 read + auth만, MVP 후반에서).
```

→ `backend_boundary.md` placeholder에서 책임 경계 상세 정의 (Phase 1 진입 시).

---

## 4. Phase 21+ 확장 (장기 비전)

본 항목은 현재 결정 사항이 아니며, Phase 21+ 진입 시점에 본 contract가 갱신될 후보다.

```
Frontend:
- Expo React Native: 모바일 네이티브 앱 (PWA → Native 전환 시점)
- Tauri 또는 Electron: 데스크탑 앱 (요구 발생 시)

Backend:
- Spring Boot (Java/Kotlin) 또는 NestJS: 대규모 트래픽 또는 multi-tenant 시
- gRPC: 내부 마이크로서비스 통신
- Apache Kafka: 이벤트 기반 아키텍처 (Phase 21+ 분석 pipeline)

Vector / RAG:
- Pinecone / Weaviate / Qdrant: pgvector가 한계 도달 시 (대략 1억+ chunk)
- 자체 RAG 인프라 구축: Phase 21+ 검토 (비용 vs 통제)

LLM:
- Fine-tuned 자체 모델 (영상기획 특화)
- 멀티 provider routing (OpenAI / Anthropic / Gemini 자동 선택)
- self-hosted open-source (Llama, Mistral) 검토

Deploy:
- AWS ECS / EKS (자체 Kubernetes는 보류)
- multi-region active-active (사용자 100만 도달 시점)

Observability:
- Datadog 또는 Honeycomb (OpenTelemetry 이상의 깊은 분석)
- ML 기반 비정상 탐지
```

---

## 5. MVP 후 조정 가능성 (명시)

```
LLM provider:
- OpenAI 단일 → Anthropic Claude / Google Gemini 병행 검토
- 시점: Phase 5+ (eval 누적 데이터 기반 비교 후)
- 절차: multi-llm-validation Skill로 양쪽 비교 → 회귀 평가 → 본 contract 갱신

Cache:
- Redis → Memcached: 단순 캐시면 충분한 경우. 단 rate limit ZADD는 Redis 필요.
- Cloudflare KV / Workers KV: edge 캐시 검토 (Phase 11+)

Queue:
- 없음 → Celery (Python) 또는 Arq (asyncio 친화)
- 시점: P-AUX-2 백그라운드 큐 부하 일정 수준 도달 시 (Phase 11+)

모바일:
- PWA → Expo React Native
- 시점: Phase 21+ 또는 사용자 UX 요구에 따라 앞당김 가능
- 전환 절차: backend API는 그대로, frontend 코드 분리

DB 확장:
- read replica: 사용자 10만 도달 시점 검토
- sharding: Supabase 단일 region 한계 도달 시 (multi-region)
- 보조 OLAP: 분석용 ClickHouse / BigQuery (Phase 21+, eval 데이터 분석)

배포:
- Render → Fly.io (지역 분산이 필요한 시점)
- Vercel → AWS Amplify (cost 또는 vendor lock-in 회피 검토)
```

---

## 6. 일관성 유지 원칙

```
1. 본 contract 변경 시:
   - contract-change Skill 절차 통과 (PR + 회귀 평가 + 영향 분석)
   - dependency_map.yaml의 영향 파일 모두 검토
   - PROJECT_STATE.md의 "최근 변경" 섹션에 기록

2. 주요 dependency 추가 시 (예: 새 라이브러리, 새 API):
   - multi-llm-validation Skill 권장 (특히 frontend 프레임워크, ORM, LLM provider)
   - eval/multi_llm_results/에 비교 결과 누적

3. Phase 진입 시 본 contract 검토 항목:
   - "MVP 후 조정 가능성" 섹션에 해당 Phase 트리거가 있는지 확인
   - 있으면 본 contract 갱신 작업을 해당 Phase의 task로 추가
   - 없으면 변경 없이 통과

4. 보안 패치:
   - CVE 공지 받으면 7일 내 패치 (lockfile 갱신 + 회귀 테스트)
   - Critical CVE는 24시간 내 패치
   - 패치 절차: meta/security_metrics.md 또는 audit_log에 기록
```

---

## 7. 버전 잠금 정책

```
package.json (frontend):
- 모든 dependency를 정확한 버전(^ 또는 ~ 사용)으로 고정
- package-lock.json 커밋 의무
- npm ci로 install (npm install 금지 in CI)

requirements.txt 또는 poetry.lock (backend):
- 모든 dependency 정확한 버전 고정
- pip install -r requirements.txt --require-hashes 권장
- poetry 사용 시 poetry.lock 커밋 의무

PostgreSQL / Supabase:
- 주 버전 고정 (PostgreSQL 15.x)
- minor 업그레이드는 Supabase 공지 + 본 contract 검토 후

LLM 모델:
- prompt_registry.md에서 prompt_id별 model + version 고정
- 모델 변경은 multi-llm-validation Skill 절차 (agent_io_contract §16)

업그레이드 절차:
- minor: 분기별로 검토 + 회귀 통과 시 적용
- major: contract-change Skill + 1주일 staging 검증 + 회귀 통과 후 적용
```

---

## 8. 보안 업데이트 정책

```
- npm audit / pip-audit 주간 실행 (CI에 통합)
- Critical CVE (CVSS ≥ 9.0): 24시간 내 패치
- High CVE (CVSS 7.0~8.9): 7일 내 패치
- Medium CVE (CVSS 4.0~6.9): 30일 내 패치
- Low CVE: 분기별 검토

패치 후:
- 회귀 테스트 (eval/regression_results/) 통과 필수
- 패치 내역은 meta/security_metrics.md에 누적 (Phase 7+)
- 사용자 영향이 있는 패치는 PROJECT_STATE.md 공지
```

---

## 9. Cross-reference 빠른 표

| 영역 | 본 contract 위치 | 의존 contract / 파일 |
|---|---|---|
| Frontend 스택 | §2.1 | frontend_design_contract, frontend_boundary (placeholder) |
| Backend 스택 | §2.2 | api_contract, backend_boundary (placeholder) |
| DB 병행 | §2.3, §3 | db_schema.md, llm_security §5.2 |
| LLM | §2.4 | agent_io_contract §3~§7, prompt_registry |
| Cache/Queue | §2.5 | rate_limit_policy §4, api_contract §17 |
| Deploy | §2.6 | env_contract (placeholder) |
| CI | §2.7 | .github/workflows/ (Phase 2+) |
| 환경변수 | §2.6 + env | env_contract (placeholder) |

---

## 10. Open Questions

1. SWR vs TanStack Query 최종 선택 — Phase 1 진입 시 frontend-boundary에서 확정.
2. Render vs Railway vs Fly.io — 초기 트래픽 측정 후. 현재 Render 우선.
3. Anthropic Claude 도입 시점 — Phase 5+ A/B 결과에 따름.
4. Celery vs Arq vs FastAPI BackgroundTasks 한계 — P-AUX-2 부하 측정 후.
5. Supabase Realtime을 어디서 활용할지 — Phase 5+ 협업/알림 기능 도입 시점.
6. PostgreSQL 자체 운영(셀프 호스팅) vs Supabase managed 영구 유지 — Phase 21+ 결정.

---

## 11. 변경 이력

```
v1.0.0 (2026-05-26): Sprint S3-3 초안. MVP 스택 고정, Supabase + PostgreSQL 병행 정책,
                      Phase 21+ 확장 후보, MVP 후 조정 가능성, 버전 잠금, 보안 업데이트.
```
