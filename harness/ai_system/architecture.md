# architecture.md — 영상기획 AI 시스템 아키텍처

> 위치: `ai_system/architecture.md`
> 상태: S4-3 deep
> 참조: `ai_system/orchestration/flow.md`, `moa_policy.md`, `cost_control_policy.md`, `fallback_policy.md`, `service_boundary.md`
> 참조: `docs/contracts/agent_io_contract.md`, `tech_stack_contract.md`, `api_contract.md`
> Skill: `ai-architecture-review`

---

## 1. 아키텍처 원칙

```
1. 단순성 (Simplicity First):
   - MOA Lite 4 agent 고정. Full MOA, recursive MOA, LangGraph 등 외부 그래프 프레임워크 사용 안 함.
   - RAG Lite 5단계 파이프라인. Custom RAG는 Phase 21+ 분리.
   - 동기 처리 기본. 비동기는 백그라운드 작업(P-AUX-2)만.

2. 비용 통제 (Cost Control by Design):
   - 모델 선택 기본 gpt-4o-mini. Critic만 gpt-4o.
   - 호출당 / 세션당 / 일일 사용자당 상한 강제.
   - cost_saving 모드 자동 강등.

3. 분리 (Separation):
   - Frontend / Backend / External 3-layer 책임 분리.
   - LLM 호출은 backend 단일 책임.
   - LLM Wiki(코드 동봉) vs RAG(DB) vs Brand Memory(사용자 단위) 분리.

4. 확장 가능성 (Phased Evolution):
   - MVP는 Phase 0~10 범위.
   - Phase 11~20: 비동기, package_agent, MCP 통합.
   - Phase 21~30: Custom RAG, research_agent, 자체 모델.
   - 각 Phase의 진입 trigger를 contract로 명시.

5. 사용자 중심 (User-First):
   - Hybrid UX: Discovery 5단계 + Quick 1단계 자동 분기.
   - 4계층 데이터 모델 (User → Brand → Domain → Series → Video).
   - 30~60초 안에 결과 도착 보장.
   - 사용자 명시 승인 없이 자동 진행 금지.
```

---

## 2. 시스템 다이어그램

```
                    ┌─────────────────────────────────┐
                    │       Frontend (Next.js)        │
                    │  - Discovery 5단계 + Quick UI   │
                    │  - SSE 수신 + 4단계 Stepper     │
                    │  - Supabase Auth 직접 호출      │
                    └────────────┬────────────────────┘
                                 │ HTTPS + JWT
                                 ▼
                    ┌─────────────────────────────────┐
                    │     Backend (FastAPI)           │
                    │                                 │
                    │  ┌─────────────────────────┐   │
                    │  │   Orchestration Layer   │   │
                    │  │   (services/flow.py)    │   │
                    │  └────┬──────┬──────┬──────┘   │
                    │       │      │      │          │
                    │       ▼      ▼      ▼          │
                    │  ┌─────┐ ┌─────┐ ┌──────┐     │
                    │  │Intent│ │Plan-│ │Critic│     │
                    │  │      │ │ning │ │      │     │
                    │  └──┬──┘ └──┬──┘ └──┬──┘     │
                    │     │       │        │         │
                    │     │       ▼        │         │
                    │     │    ┌─────┐    │         │
                    │     │    │ RAG │    │         │
                    │     │    │Lite │    │         │
                    │     │    └─────┘    │         │
                    │     │               │         │
                    │     ▼               ▼         │
                    │  ┌────────────────────┐      │
                    │  │ Security / Cost /  │      │
                    │  │ Observability      │      │
                    │  └─────────┬──────────┘      │
                    └────────────┼────────────────┘
                                 │
                  ┌──────────────┼──────────────┐
                  ▼              ▼              ▼
            ┌──────────┐  ┌──────────┐  ┌────────────┐
            │ OpenAI   │  │Supabase  │  │ pgvector   │
            │ (LLM)    │  │ (Auth/DB)│  │ (RAG)      │
            └──────────┘  └──────────┘  └────────────┘
```

---

## 3. 4 Agent 역할 매트릭스

| Agent | 책임 | 모델 | RAG | Brand Memory | 병렬 | 위치 |
|---|---|---|---|---|---|---|
| Intent | 분류 + 카드 생성 + 한 줄 방향 | gpt-4o-mini | no | partial(P-002+) | no | agents/intent_agent.md |
| Planning | 3 plan 생성 | gpt-4o-mini | yes (top_k=5, sim≥0.7, 최대 3) | full | no | agents/planning_agent.md |
| Critic | 8 차원 채점 + verdict | gpt-4o (cost_saving=mini) | no | partial (avoid, tone) | yes (×3) | agents/critic_agent.md |
| Rewriter | revise 적용 | gpt-4o-mini | no | full | no | agents/rewrite_agent.md |
| Memory Extractor (P-AUX-2) | Brand Memory 추출 | gpt-4o-mini | no | full(현재 상태) | no (백그라운드) | (prompt only) |

placeholder agents:
- package_agent.md — Phase 11+ (PDF/슬라이드 export)
- research_agent.md — Phase 21+ (외부 검색)

---

## 4. RAG Lite 5단계 통합

```
사용자 피드백 / llm_wiki / 외부 시드 / 내부 생성
                │
                ▼
        1. pending (candidate_knowledge)
                │ quality_filter.md 자동
                ▼
        2. filtered
                │ P-EVAL-1 자동 평가
                ▼
        3. evaluated
                │ 운영자 승인 (or 자동, Phase 11+)
                ▼
        4. approved
                │ approved_knowledge INSERT
                ▼
        5. promoted (RAG 검색 활성)
```

RAG 검색은 Planning Agent만 사용 (agent_io §12). 검색 정책:
- 쿼리: approved_direction + selected_series.name + selected_domain.name
- top_k = 5 → similarity ≥ 0.7 → 최대 3 chunk 채택
- 빈 결과 시: warning + Planning 진행

→ `knowledge/rag/retrieval_policy.md`, `chunking_policy.md` 참조.

---

## 5. 데이터 흐름

### 5.1 요청 흐름 (User → Result)

```
User Input
  → Intent (P-AUX-1)
  → [Discovery: P-001~P-005 카드 5장 / Quick: P-005q]
  → 사용자 한 줄 방향 승인
  → RAG retrieval (Planning 한정)
  → Planning (P-006, 3 plan)
  → Critic × 3 (P-007 병렬)
  → [선택: Rewriter P-008, revise_round 0→2]
  → 사용자 plan 선택 (/select)
  → video_projects + plan_options 저장
```

### 5.2 응답 흐름 (SSE 이벤트)

api_contract §13 정합. Frontend는 SSE로:
- `intent_started/completed`
- `cards_card_emitted` (4회)
- `direction_summary`
- `rag_retrieved`
- `planning_started/plan_emitted` (3회)
- `critic_started/result` (3회)
- `session_completed`
- `error` (단계별)

### 5.3 저장 흐름 (Persistence)

```
모든 agent 호출 → agent_io_logs INSERT (호출 직전) + UPDATE (완료/실패)
Intent 결과 → intent_filter_logs (P-AUX-1만), discovery_choices
RAG → 검색 로그(별도 테이블 또는 agent_io_logs.metadata)
Planning → plan_options (3 plan + RAG 인용)
Critic → quality_scores (8 차원 + verdict + revise_round)
Rewriter → revision_requests
사용자 선택 → choice_logs + video_projects.status='selected'
사용자 피드백 → feedback_events
```

### 5.4 학습 흐름 (Feedback Loop)

```
세션 종료 (status='final')
  → P-AUX-2 백그라운드 큐
  → brand_memory_entries 자동 INSERT (조건부, confidence≥0.9)
  → 우수 패턴 → candidate_knowledge (선택률≥0.5)
  → 5단계 승격 → approved_knowledge
  → 다음 사용자 RAG에 활용 (anonymized)
```

---

## 6. 외부 시스템

```
OpenAI (Phase 0~10 필수):
  - gpt-4o-mini: Intent, Planning, Rewriter, Memory Extractor, Knowledge Evaluator
  - gpt-4o: Critic (cost_saving = mini 폴백)
  - text-embedding-3-small: RAG embedding

Supabase:
  - Auth: email/password, OAuth
  - PostgreSQL: 모든 비즈니스 데이터
  - pgvector extension: RAG
  - Realtime: Phase 5+ 검토
  - Storage: Phase 11+ (Package Agent 활성화 시)

pgvector:
  - approved_knowledge embedding (1536 dim, text-embedding-3-small)
  - cosine similarity 검색
  - HNSW 인덱스 (Phase 1+ 첫 RAG 구현 시)

Anthropic / Gemini (Phase 11+ A/B 검토):
  - Claude 3.5 Sonnet/Haiku (Critic 대안)
  - Gemini 2.0 Flash
```

→ `docs/contracts/tech_stack_contract.md`, `service_boundary.md` 참조.

---

## 7. Phase별 진화

### 7.1 Phase 1-10: MVP (MOA Lite + RAG Lite + SDK)

```
- 4 agent 동기 처리
- RAG Lite 5단계
- Supabase + FastAPI + Next.js
- OpenAI gpt-4o-mini + gpt-4o
- 무료 사용자 일 $0.10 한도
- Hybrid UX (Discovery + Quick)
```

### 7.2 Phase 11-20: 안정화 + 확장

```
- 비동기 처리 도입 (큐 기반 백그라운드)
- package_agent 활성화 (PDF/슬라이드 export)
- MCP (Model Context Protocol) 통합 검토
- Anthropic / Gemini A/B 운영
- Spring Boot Core 분리 검토 (트래픽 임계 시)
- 자동 승격(promotion) 임계 활성화
- 협업 (team workspace) 도입
- 유료 tier 가격 책정
```

### 7.3 Phase 21-30: 자체 인프라

```
- Custom RAG (자체 코퍼스, 자체 임베딩 모델 검토)
- research_agent (외부 검색, 실시간 트렌드)
- Multi-agent voting (Critic 3 모델 평균)
- 자체 모델 fine-tuning 검토 (cost ROI 분석 후)
- 다국어 영상기획
- 자동 재평가 (모델 업데이트 시 approved_knowledge 일괄 재평가)
```

---

## 8. 비기능 요구사항 (NFR)

```
Latency:
  - Discovery 카드 1장: ≤ 30초
  - Plan 3개 + Critic 완료: ≤ 60초
  - Quick 한 줄 방향: ≤ 5초
  - SSE heartbeat: 5초 주기

가용성:
  - 99.0% (Phase 0~10)
  - 99.5% (Phase 11+)
  - OpenAI/Supabase 외부 의존성은 별도 SLO

비용:
  - 무료 사용자 월 $5 이하 (대략 50세션)
  - 유료 사용자: Phase 11+에서 가격 책정

품질:
  - golden_set 회귀 통과율 ≥ 90% (eval/golden_set.md 11 케이스)
  - revise_round 평균 ≤ 1.5
  - 사용자 만족도 ≥ 4.0 / 5 (Phase 5+ 측정)

보안:
  - prompt injection 차단율 ≥ 95% (llm_security_contract)
  - PII 마스킹 누락 0% (privacy_contract placeholder)
```

---

## 9. 모니터링 / 관측가능성

```
agent_io_logs:
  - 모든 LLM 호출 (cost, latency, tokens, model, prompt_version)
  - prompt_id별 평균 latency / 실패율
  - prompt_version 분기 분석 (A/B)

intent_filter_logs:
  - P-AUX-1 차단/허용 분포
  - prompt injection 시도 감지

security_metrics:
  - 차단 시도 추이
  - PII 검출 빈도
  - rate limit 위반

cost_snapshots:
  - 일/주/월 누적 cost
  - 사용자별 상한 위반 사례
  - cost-review Skill 정기 실행 결과

quality_snapshots (Phase 7+):
  - golden_set 회귀 결과
  - 사용자 만족도 분포
  - revise_round 평균
```

→ `meta/security_metrics.md`, `eval/cost_snapshots/`, `eval/quality_snapshots/`(Phase 7+) 참조.

---

## 10. ai-architecture-review Skill 연동

본 아키텍처는 다음 시점에 `ai-architecture-review` Skill로 정기 검토한다:

```
- Phase 7+ 진입 시 (MVP 안정화 점검)
- Phase 11+ 진입 시 (비동기 전환 검토)
- 신규 agent 추가 제안 시
- orchestration policy 변경 제안 시
- 분기별 정기 검토 (Phase 11+)
```

큰 결정(예: agent 추가, RAG 구조 변경)은 `multi-llm-validation` Skill로 교차 검증 보강.

---

## 11. Cross-reference 빠른 표

| 영역 | 주 contract | 보조 contract |
|---|---|---|
| Agent IO | agent_io_contract.md | output_schema.md, prompt_registry.md |
| 흐름 | orchestration/flow.md | orchestration/moa_policy.md |
| 비용 | orchestration/cost_control_policy.md | rate_limit_policy.md |
| 폴백 | orchestration/fallback_policy.md | error_response_contract.md |
| 보안 | llm_security_contract.md | privacy_contract.md (placeholder) |
| RAG | rag_data_contract.md | knowledge/rag/*.md |
| 메모리 | ai_system/memory/user_memory_policy.md | candidate_knowledge_policy.md |
| 서비스 경계 | orchestration/service_boundary.md | tech_stack_contract.md, backend_boundary.md (placeholder) |
| 평가 | eval/video_planning_eval.md | golden_set.md, regression_eval.md |

---

## 12. Open Questions

1. Phase 11+ 비동기 전환 트래픽 임계(현재 미정) — 동기 처리 한계점 측정 필요.
2. Critic gpt-4o 고정 정책의 cost ROI — cost_saving mode 사용 비율 누적 후 재평가.
3. Custom RAG 도입 시점(Phase 21+) — 사용자 코퍼스 규모 임계 결정 필요.
4. MCP 통합 시 backend 우회 허용 여부(현재 금지).
5. 자체 모델 fine-tuning ROI — Phase 21+ cost 분석 + 품질 vs 비용.
6. 다국어 영상기획 진입 시 4계층 데이터 모델 영향(Brand language 필드 추가 필요).
