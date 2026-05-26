# tech_stack_decision.md — 기술 스택 결정 기록 (ADR)

> 위치: `docs/decisions/tech_stack_decision.md`
> 상태: Phase 0 Sprint S5 deep 작성 (placeholder 해소)
> 참조: `docs/contracts/tech_stack_contract.md` (결정의 결과물)
> 참조: `meta/lessons_learned.md`, `meta/harness_improvement_proposals.md`

---

## 0. 본 문서의 위치

본 문서는 **ADR (Architecture Decision Record)** 형식의 의사결정 기록이다.
`docs/contracts/tech_stack_contract.md`는 **결정의 결과**를 담고,
본 문서는 **결정의 배경 + 대안 비교 + 트레이드오프**를 담는다.

---

## 1. 결정 요약

```
Frontend:    Next.js 14 (App Router) + TypeScript + Tailwind + shadcn/ui
Backend:     FastAPI (Python 3.11) + Pydantic v2 + SQLAlchemy 2.x
DB:          Supabase (PostgreSQL 15 + pgvector) + service role direct access
LLM:         OpenAI (gpt-4o-mini + gpt-4o)
Cache:       Redis (Upstash 또는 Render Redis)
Deploy:      Vercel (FE) + Render (BE) + Supabase (DB)
Embedding:   text-embedding-3-small (1536)
```

---

## 2. 대안 비교

### 2.1 Frontend: Next.js vs Remix vs SvelteKit

| 기준 | Next.js 14 | Remix | SvelteKit |
|---|---|---|---|
| 성숙도 | 높음 (대형 커뮤니티) | 중간 | 중간 |
| App Router (RSC) | ✓ | 부분 | △ |
| 호스팅 친화 | Vercel 공식 | Cloudflare 친화 | Vercel/Cloudflare |
| 한국 인력 | 가장 많음 | 적음 | 매우 적음 |
| PWA 지원 | next-pwa | 수동 | 수동 |
| 학습 곡선 | 중간 | 중간 | 낮음 |

**선택: Next.js 14**

### 2.2 Backend: FastAPI vs Express vs NestJS

| 기준 | FastAPI | Express | NestJS |
|---|---|---|---|
| 언어 | Python | Node.js | Node.js (TS) |
| AI / ML 친화 | 매우 높음 | 중간 | 중간 |
| 타입 안전성 | Pydantic v2 | (TS 추가) | 기본 TS |
| 성능 | 매우 좋음 | 좋음 | 좋음 |
| OpenAI SDK 친화 | 공식 Python SDK | 비공식 또는 fetch | 비공식 |
| 학습 곡선 | 낮음 | 낮음 | 중간 (DI 패턴) |

**선택: FastAPI**

### 2.3 DB: Supabase vs raw PostgreSQL vs Firebase

| 기준 | Supabase | raw PostgreSQL | Firebase |
|---|---|---|---|
| Auth | 내장 (OAuth) | 외부 (Auth0 등) | 내장 |
| RLS | 내장 | 수동 정책 | NoSQL (다른 모델) |
| pgvector | ✓ | ✓ | ✗ |
| 실시간 | postgres_changes | 추가 인프라 | 내장 |
| Managed | ✓ (자동 백업) | 자체 운영 | ✓ |
| 비용 | 무료 시작 | 인스턴스 비용 | 무료 시작 |
| vendor lock-in | 중간 (PostgreSQL 호환) | 없음 | 매우 높음 (NoSQL) |

**선택: Supabase**

---

## 3. 선택 이유 (요약)

```
Next.js 14:
- App Router로 RSC 활용 가능 (SEO + 성능)
- Vercel 공식 호스팅으로 배포 단순
- next-pwa 표준 (모바일 PWA 우선)
- 한국 개발자 인력 풀 가장 큼

FastAPI:
- Python 생태계 → OpenAI / LangChain 등 LLM 친화
- Pydantic v2로 타입 안전성 + 자동 schema validation
- async 지원으로 LLM 호출 처리 적합

Supabase:
- Auth + RLS + Realtime + Storage 통합
- pgvector 내장 (Phase 7 RAG에 즉시 사용)
- managed (백업 / 모니터링 자동)
- PostgreSQL 호환 → Phase 21+ self-host 전환 가능

OpenAI (gpt-4o-mini + gpt-4o):
- 한국어 품질 좋음 (Claude / Gemini 대비 약간 우위, 2026-05 시점)
- 비용 적정 (gpt-4o-mini $0.15/1M)
- Python SDK 안정

Redis:
- rate_limit 표준 (ZADD / Lua script)
- Upstash serverless로 비용 낮음
- idempotency key 표준 패턴
```

---

## 4. 트레이드오프

```
Next.js 14 vs Remix:
- 선택: Next.js
- 잃는 것: Remix의 더 단순한 데이터 로딩 패턴
- 얻는 것: 더 큰 커뮤니티 + Vercel 통합

FastAPI vs NestJS:
- 선택: FastAPI
- 잃는 것: Node 단일 언어 (FE + BE 동일)
- 얻는 것: Python LLM 생태계 + Pydantic v2 우수성

Supabase vs raw PostgreSQL:
- 선택: Supabase
- 잃는 것: 완전한 통제 + vendor lock-in 회피
- 얻는 것: Auth/RLS/Realtime 즉시 사용 + managed

OpenAI 단일 vs 멀티 provider:
- 선택: 단일 (Phase 1~5)
- 잃는 것: vendor lock-in 위험 + 비용 비교 불가
- 얻는 것: 통합 단순성 + 빠른 개발
- 완화: Phase 5+에서 Anthropic 병행 검토 (multi-llm-validation)
```

---

## 5. 재검토 트리거

다음 시점에 본 결정 재검토.

```
사용자 10만 명 도달:
  - PostgreSQL read replica 검토
  - Render → Fly.io 또는 AWS 마이그레이션 검토

p95 응답 시간 1초 초과 (정상 응답 기준):
  - Redis 캐시 강화
  - DB index 검토
  - Vercel Edge 활용

LLM 비용 매출의 30% 초과:
  - 자체 모델 fine-tuning 검토 (Phase 26+)
  - 모델 변경 (gpt-4o-mini → 더 저렴한 대안)

OpenAI API 안정성 저하 (Phase 5+):
  - Anthropic 또는 Gemini 병행
  - multi-llm-validation 도입

Supabase 한계 도달:
  - pgvector 1억+ chunk: Pinecone / Weaviate 검토
  - 사용자 10만+: self-host 검토

Phase 21+ 진입:
  - 본 contract 전체 재검토
```

---

## 6. 결정 과정 (Phase 0)

```
2026-05 (Phase 0 시작):
- 사용자 (1인 운영) 가정 하 빠른 검증 우선
- multi-llm-validation으로 Next.js / FastAPI / Supabase 합의
- 단일 LLM provider (OpenAI)로 시작 결정

다음 검토:
- Phase 5+ 진입 시 (사용자 데이터 누적 후)
- Phase 21+ 진입 시 (전체 재검토)
```

→ 자세한 contract는 `docs/contracts/tech_stack_contract.md`

---

## 7. 변경 이력

```
v1.0.0 (2026-05-26): Phase 0 Sprint S5-1. placeholder 해소 + deep 작성.
                      3 핵심 영역 대안 비교, 선택 이유, 트레이드오프, 재검토 트리거.
```
