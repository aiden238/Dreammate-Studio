# backend_boundary.md

> ⚠️ **PLACEHOLDER** — 본 contract는 향후 Phase에서 채워질 예정.
> 현재는 스코프와 트리거만 명시. 정상 contract로 사용 금지.

## Status

```yaml
status: placeholder
fill_in_phase: 1+
priority: medium
estimated_final_lines: 200
last_updated: 2026-05-26
```

## Why Placeholder?

Phase 0은 contract / 골격 정의 단계. Phase 1+ 첫 backend endpoint 구현 시작 시점에 책임 경계를 정량 정의한다. 그 전까지는 `tech_stack_contract.md` §2.2, §3 (Supabase + PostgreSQL 병행)의 원칙이 가이드.

## Scope (TBD)

본 contract가 다룰 범위:

- FastAPI 백엔드 책임:
    - 비즈니스 로직 (4계층 검증, plan 생성 흐름)
    - LLM 호출 (모든 prompt 호출은 backend 경유)
    - RAG 검색 (pgvector 직접 접근)
    - agent_io_logs / intent_filter_logs 기록
    - 백그라운드 작업 (P-AUX-2 memory extractor)
    - 비용 quota 추적 + rate limit 적용
    - PII 마스킹 + prompt injection 검사 hook
- Supabase 책임 (직접 client SDK 또는 백엔드 경유):
    - Auth (email/password, OAuth)
    - RLS 정책 적용 (user-facing 경로)
    - Realtime (Phase 5+)
    - Storage (Phase 5+)
- Frontend 책임 (백엔드가 다루지 않는 것):
    - UI 상태 관리
    - 클라이언트 입력 검증 (1차)
    - SWR / React Query 캐싱
    - Supabase Auth 직접 호출 (또는 backend proxy)
- 책임 분리 원칙:
    - 보안 검사는 backend가 단일 책임 (frontend 검증은 UX 보조)
    - 비용 추적은 backend 단일 (frontend 표시는 응답 헤더 echo)
    - RLS는 user-facing 경로만, backend는 service role key로 우회 가능
- Phase 11+ 분리 검토:
    - Spring Boot Core (인증, 사용자 관리) + FastAPI AI Service (LLM, RAG)
    - 분리 트리거: 트래픽 규모 또는 팀 구성 변화
    - 분리 절차: API gateway 도입 → 단계적 마이그레이션
- 두 layer 간 데이터 일관성:
    - Supabase client SDK가 직접 write 가능한 테이블 목록
    - backend가 단일 write 경로인 테이블 (agent_io_logs, rag_*, brand_memory_entries 자동 INSERT 등)
- 백엔드 모듈 구조 (Phase 1+ 결정):
    - api/, services/, models/, agents/, rag/, security/, observability/

## Known Dependencies (when filled in)

외부 표준:
- 12-factor app §1 (Codebase), §2 (Dependencies), §6 (Processes)

내부 의존 contract:
- `docs/contracts/tech_stack_contract.md` §2.2, §3 (병행 사용 정책)
- `docs/contracts/api_contract.md` (endpoint 정의)
- `docs/contracts/agent_io_contract.md` (LLM 호출 위치)
- `docs/contracts/db_schema.md` (write 경로별 테이블)
- `docs/contracts/llm_security_contract.md` (보안 hook 위치)
- `docs/contracts/rate_limit_policy.md` (rate limit 위치)
- `docs/contracts/frontend_boundary.md` (placeholder, frontend 책임)
- `docs/contracts/env_contract.md` (placeholder, env 관리)

## Fill-In Trigger

다음 조건 충족 시 본 contract 작성 착수:
- Phase 1+ 진입 (첫 backend endpoint 구현 시작 시점)
- 또는 backend 모듈 구조 결정 시점
- 또는 Supabase ↔ FastAPI 권한 충돌 첫 발생 시
- 또는 Spring Boot 분리 검토 시점 (Phase 11+)

## Related Skill / Phase

- Skill: `ai-architecture-review`
- Phase: 1+
- 책임자: AI(초안) + 사용자(검토)
