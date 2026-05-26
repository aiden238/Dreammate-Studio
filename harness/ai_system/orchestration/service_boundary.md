# service_boundary.md — 서비스 경계 정책

> 위치: `ai_system/orchestration/service_boundary.md`
> 상태: S4-3 deep
> 참조: `docs/contracts/tech_stack_contract.md`, `docs/contracts/backend_boundary.md` (placeholder), `docs/contracts/frontend_boundary.md` (placeholder)
> 참조: `docs/contracts/llm_security_contract.md`, `docs/contracts/api_contract.md`

---

## 1. 책임 분리 원칙

영상기획 AI는 다음 3 layer로 분리한다:

1. **Frontend (Next.js)** — UI/UX, 로컬 1차 검증, 응답 표시.
2. **Backend (FastAPI + Supabase)** — API/오케스트레이션/persistence/LLM 호출.
3. **External (OpenAI / pgvector)** — LLM 추론, 벡터 검색.

각 layer는 자신의 책임 외 작업을 수행하지 않는다.

---

## 2. Frontend 책임

```
- UI/UX 렌더링 (Discovery 5단계 카드, Quick 입력, plan 결과 표시)
- SSE 이벤트 수신 + Stepper 업데이트
- 사용자 입력 1차 검증 (필수 필드, 길이 제한)
- localStorage 백업 (저장 실패 대비)
- Supabase Auth 직접 호출 (또는 backend proxy)
- SWR / React Query 캐싱
- 디자인 시스템 준수 (apps/web/design.md)
```

**금지:**
- LLM API 직접 호출 (보안 위반)
- DB 직접 write (Supabase RLS user-facing 경로만 허용)
- 비용/quota 추적 (응답 헤더 echo만 표시)
- prompt_registry / agent_io_contract 우회

---

## 3. Backend 책임

```
- API endpoint 제공 (api_contract §전체)
- 4 agent 오케스트레이션 (flow.md)
- LLM 호출 단일 책임 (모든 prompt 호출 backend 경유)
- RAG 검색 (pgvector 직접 접근)
- agent_io_logs / intent_filter_logs / cost_snapshots 기록
- 백그라운드 작업 (P-AUX-2 Memory Extractor)
- 비용 quota 추적 + rate limit 적용
- PII 마스킹 + prompt injection 검사 (llm_security_contract)
- 4계층 컨텍스트 검증 (brand → domain → series → video)
- revise_round 카운터 관리 (client 우회 불가)
```

**단일 진입점:** 모든 LLM 호출은 backend의 `agents/` 모듈을 통과한다. 우회 경로 없음.

---

## 4. LLM 호출 책임 분담

| 호출 주체 | 허용 | 이유 |
|---|---|---|
| Frontend | ✗ | API key 노출 위험 + prompt injection 차단 우회 위험 |
| Backend | ✓ | API key를 환경변수로 보관, 보안 hook 강제 |
| External (사용자가 만든 plugin 등) | ✗ MVP | Phase 21+ MCP 통합 검토 |

API key 관리:
- 환경변수: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY` (env_contract placeholder)
- Vault / Secrets Manager (Phase 11+)
- 절대 git 저장소에 commit 금지 (.gitignore + git pre-commit hook)

---

## 5. Supabase Auth 책임 분담

```
Frontend:
  - Supabase Client SDK로 직접 signIn/signUp/signOut
  - JWT를 backend API 호출 시 Authorization 헤더로 전송

Backend:
  - JWT 검증 (Supabase JWKS endpoint)
  - 검증 후 user_id 추출 → 모든 DB write에 첨부
  - RLS 우회가 필요한 경우 service role key 사용 (agent_io_logs INSERT 등)
```

---

## 6. 외부 Dependency

```
OpenAI (필수, Phase 0~10):
  - gpt-4o-mini: Intent / Planning / Rewriter / Memory Extractor / Knowledge Evaluator
  - gpt-4o: Critic (cost_saving 시 mini 폴백)
  - text-embedding-3-small: RAG embedding

Supabase (필수):
  - Auth (email/password, OAuth)
  - PostgreSQL (RLS 적용)
  - pgvector extension (RAG)
  - Realtime (Phase 5+ 검토)
  - Storage (Phase 11+ Package Agent 활성화 시)

Anthropic Claude (선택, Phase 11+ A/B):
  - claude-3-5-sonnet (Critic 대안)
  - claude-3-5-haiku (mini 대안)

Gemini (선택, Phase 11+ A/B):
  - gemini-2.0-flash
```

---

## 7. Backend 모듈 구조 (Phase 1+ 결정 예고)

`docs/contracts/backend_boundary.md` placeholder가 Phase 1+에서 다음을 정의:

```
backend/
├── api/          # FastAPI endpoint
├── services/     # 비즈니스 로직 (오케스트레이션)
├── agents/       # 4 agent + Memory Extractor 호출 모듈
├── rag/          # pgvector 검색 + chunking
├── security/     # PII 마스킹, prompt injection, JWT
├── observability/ # 로깅, metrics, tracing
└── models/       # SQLAlchemy / Pydantic 모델
```

→ backend_boundary placeholder가 Phase 1+에서 채워질 때 본 절을 확장.

---

## 8. Phase 11+ 분리 검토 (Spring Boot Core + FastAPI AI)

```
Spring Boot Core (Phase 11+):
  - 회원 / 권한 / 결제 / 팀 / 프로젝트 메타
  - 인증 / 세션 관리

FastAPI AI Service (현재 + 유지):
  - LLM / RAG / MOA / 검증 / 임베딩
  - agent_io_logs / cost_snapshots

분리 트리거:
  - 트래픽 규모 증가 (월 활성 사용자 1만+)
  - 팀 구성 변화 (백엔드 분업)
  - 결제/구독 기능 도입
```

---

## 9. 데이터 일관성 (write 경로)

| 테이블 | Supabase 직접 write | Backend write |
|---|---|---|
| users | ✓ (Auth trigger) | (관리자만) |
| brands, domains, series, video_projects | ✗ | ✓ (RLS user_id 검증 후) |
| plan_options | ✗ | ✓ |
| agent_io_logs, intent_filter_logs | ✗ | ✓ (service role key) |
| brand_memory_entries | ✗ | ✓ (P-AUX-2 자동 또는 사용자 명시 승인) |
| candidate_knowledge, approved_knowledge | ✗ | ✓ (rag-update Skill 경유) |

---

## 10. 의존성

- `docs/contracts/tech_stack_contract.md` (FastAPI + Supabase + Next.js)
- `docs/contracts/backend_boundary.md` (placeholder, Phase 1+)
- `docs/contracts/frontend_boundary.md` (placeholder, Phase 1+)
- `docs/contracts/api_contract.md` (endpoint 정의)
- `docs/contracts/llm_security_contract.md` (보안 hook)
- `docs/contracts/env_contract.md` (placeholder, env 관리)

---

## 11. Open Questions

1. Frontend LLM 호출 우회 시도 차단 — backend로만 호출 강제 정책(현재 적용).
2. Supabase Realtime 도입 시점(현재 미사용, Phase 5+ 검토).
3. Spring Boot Core 분리 트리거 임계(현재 월 1만 MAU).
4. MCP(Model Context Protocol) 통합 시 외부 plugin이 backend 우회 허용 여부(현재 금지).
5. Vault / Secrets Manager 도입 시점(현재 환경변수 직접 사용).
