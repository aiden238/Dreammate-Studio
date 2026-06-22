# 03. 아키텍처 + ADR (Architecture Decision Records)

> 채점 키워드: **아키텍처 · ADR · 디렉토리 구조 · 레이어 · 데이터 모델 · 다이어그램 · AI 파이프라인**

본 문서는 Dreammate Studio의 **레이어 아키텍처**, **디렉토리 구조**, **데이터 모델**, **AI 파이프라인**과 **ADR 인덱스(39개)** + 핵심 ADR 5개 요약을 담는다.
근거: `harness/docs/decisions/`, `harness/ai_system/`, `harness/CLAUDE.md`, `harness/AGENTS.md`.

---

## 1. 레이어 아키텍처 (Layered Architecture)

```text
┌─────────────────────────────────────────────────────────────┐
│  사용자 (모바일/웹 — PWA)                                      │
└───────────────────────────┬─────────────────────────────────┘
                            │ HTTPS (same-origin proxy: next rewrites /api/*)
┌───────────────────────────▼─────────────────────────────────┐
│  Frontend / BFF  — Next.js 14 (App Router, TypeScript)        │
│  · 11 routes (+/login) · Tailwind + shadcn/ui · PWA(next-pwa) │
│  · 카드 단위 결과 · 한 줄 방향 승인 · SSE progress 표시       │
└───────────────────────────┬─────────────────────────────────┘
                            │ JSON / SSE (JWT httpOnly cookie)
┌───────────────────────────▼─────────────────────────────────┐
│  Backend  — FastAPI (Python 3.11, Pydantic v2, SQLAlchemy 2) │
│  · 17 endpoints (/plans /auth /sse /me/* ...)                 │
│  · routers = thin HTTP adapter                                │
└───────────────────────────┬─────────────────────────────────┘
                            │ orchestration (service layer 중개)
┌───────────────────────────▼─────────────────────────────────┐
│  AI Engine  — MOA Lite Orchestrator                          │
│  Intent Router → RAG Lite → Plan Generator(3안) →            │
│  Critic(canonical 0~1, revise≤2) → Rewriter →               │
│  cross-provider judge → Brand Memory / PKM                    │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│  Data  — Supabase (PostgreSQL 15 + pgvector) + RLS + Auth     │
│  · 4계층 모델 · candidate/approved_knowledge · pkm_entries    │
│  · Cache: Redis (Upstash)                                     │
└─────────────────────────────────────────────────────────────┘
```

**레이어 책임 분리**
- **Frontend(BFF)**: 화면 + same-origin API 프록시. 영상 제작 UI 없음(기획 전용).
- **Backend(router)**: HTTP 경계만 담당하는 **thin adapter**. orchestration을 직접 인라인하지 않는다.
- **AI Engine(orchestrator)**: `moa_policy §2` — agent 간 직접 호출 금지, service layer가 항상 중개 (ADR-027로 god-function 분해).
- **Data**: 표준 PostgreSQL 호환 유지 → self-host 마이그 가능 (ADR-020).

---

## 2. 디렉토리 구조 (Directory Tree)

```text
Dreammate_Studio/
├── README.md                  ← 제품 소개 + 현재 상태 (루트)
├── docs/grading/              ← ★ 채점용 문서 패키지 (본 폴더)
└── harness/                   ← 운영 하네스
    ├── 00_START_HERE.md       ← 첫 진입
    ├── CLAUDE.md              ← 기획/설계 모델 라우터
    ├── AGENTS.md              ← 구현/QA 모델 라우터
    ├── PROJECT_STATE.md       ← 현재 상태 (권위 소스)
    ├── PHASE_REGISTRY.md      ← Phase 목록
    ├── .claude/skills/        ← Skill 19개 (단일 폴더, applies_to 태그)
    ├── ai_system/             ← MOA Lite + RAG Lite
    │   ├── architecture.md
    │   ├── orchestration/     ← flow.md, moa_policy.md
    │   └── prompts/           ← prompt_registry.md (P-XXX semver)
    ├── apps/web/              ← Next.js PWA 설계 (design.md, page_map, component_map)
    ├── backend/fastapi/       ← FastAPI (routers, orchestration, agents, schemas, rag, llm)
    ├── docs/
    │   ├── contracts/         ← 모든 결정의 단일 진실 소스 (api/db_schema/output_schema/agent_io …)
    │   ├── decisions/         ← ★ ADR 39개
    │   └── deploy_test_gates.md
    ├── eval/                  ← golden_set + 회귀 + human_review
    ├── knowledge/             ← llm_wiki + rag (promotion/quality_filter/retrieval)
    ├── meta/                  ← 회고 + 가드레일 + 패턴 + validations + handoffs
    ├── phases/active|archive/ ← Phase 문서
    └── product/               ← vision · scope · scenarios
```

---

## 3. 데이터 모델 — 4계층 + 개인 PKM

```text
User (인증 주체, JWT)
 └── Brand (브랜드: 톤·메시지·아이덴티티)
      └── Domain (분야/카테고리)
           └── Series (반복 콘텐츠 시리즈)
                └── Video (개별 영상기획 프로젝트)

[횡단] 개인 PKM "2nd brain"
 · pkm_entries (개인 지식, source_plan_id로 출처 추적)
 · brand_memory_entries (브랜드 기억, 피드백 자동 추출)
 · candidate_knowledge → approved_knowledge (RAG 5단계 승격)
```

- **소유 검증**: `/me/videos`는 User→Brand→Domain→Series→Video **4-hop 소유 검증** (미소유 404).
- **격리**: RLS + retrieval 단계 `brand_id` 강제 (ADR-025 §3).
- **출처 추적**: 생성된 plan_id를 PKM/지식 추출 시 기록(`_append_source_provenance` 공유 헬퍼).

---

## 4. AI 파이프라인 (MOA Lite + RAG Lite)

```text
[입력] user_input
   │
   ▼  ① Intent Router (run_intent)  ── 영상기획 외 차단(Intent Filter, INV-001)
   │
   ▼  ② RAG Lite ─ pgvector cosine top_k=5, threshold=0.7, brand_id 격리
   │      └ candidate_knowledge → (filter→evaluate→approve→promote) → approved_knowledge
   │      └ 0 results 시 LLM Wiki fallback (RAG > LLM Wiki 우선)
   │
   ▼  ③ Plan Generator ─ 3안 병렬 (asyncio.gather)
   │      slot0 OpenAI / slot1 Claude(haiku) / slot2 Gemini(flash) — 다양성
   │
   ▼  ④ Critic Agent ─ canonical overall_score(0~1) + dimensions(8차원)
   │      └ verdict=revise → ⑤ Rewriter (max 2회) → 재평가
   │      └ recommended_plan_index 산출
   │
   ▼  ⑤ cross-provider judge (Claude) ─ 사람정렬 계측기 (gated)
   │      └ false-approve 10/10 → 0/10 (88점 함정 해소)
   │
   ▼  ⑥ Envelope 조립 (Meta + Body + Validation 7 checks)
   │      └ SSE 4단계 progress emit (intent/rag/planning/critic + complete)
   │
   ▼  ⑦ 저장 + 피드백 → Brand Memory / PKM 자동 추출
[출력] 영상기획안 3개 + 추천안 + 검증 결과
```

**핵심 정책**
- **revise 최대 2회** — 무한 루프 차단 (`for attempt in range(max_revise+1)` + break).
- **graceful** — 단일 agent 실패 시 부분 결과 노출 (Critic 실패→skip, Rewriter 실패→원본 유지).
- **Envelope byte-identical** — orchestrator 추출 시 동작 보존(behavior-preserving) 게이트.

---

## 5. ADR 인덱스 (`harness/docs/decisions/` — 39개 파일)

> ADR = Architecture Decision Record. **결정의 배경 + 대안 비교 + 트레이드오프**를 기록. contract는 결정의 *결과*, ADR은 결정의 *근거*.

| 영역 | ADR 파일 |
|---|---|
| **전략** | tech_stack_decision · backend_strategy · frontend_design_strategy · mobile_strategy · observability_strategy · orchestration_strategy · rag_strategy · eval_dual_track |
| **Phase 1~4** | phase_1_simplest_slice · phase_2_design_layered_minimal · phase_2_variants_3_components · phase_3_tailwind_tokens_mapping · phase_3_mode_branching_middleware · phase_4_endpoint_migration · phase_4_3plan_multi_model |
| **Critic/Rewriter** | phase_4_5_critic_revise · phase_4_5_best_plan_selection · phase_6_critic_canonical · phase_6_rewriter_contract |
| **DB/Auth/SSE** | phase_5_supabase_adoption · phase_5_rls_policy · phase_5_sse_progress · phase_5_5_legacy_db_consolidation |
| **RAG** | phase_7_rag_scope_evolution · phase_7_rag_architecture · phase_7_promotion_logic |
| **MOA** | phase_8_moa_orchestrator · phase_8_sse_progress_integration · phase_8_prompt_registry_semver |
| **피드백/eval** | phase_9_feedback_selection · phase_9_critic_canonical_wiring · phase_9_brand_memory_prep · phase_9_5_eval_run_harness · phase_9_5_critic_deprecated_removal |
| **메타/통합/게이트웨이** | phase_M0_meta_factory · phase_M1_meta_factory_sample_test · phase_M2_meta_factory_gap_remediation · phase_10_mvp_integration · phase_11_llm_gateway |

(총 39개. cross-provider judge 등 일부 후속 결정은 PROJECT_STATE / 회고에 기록.)

---

## 6. 핵심 ADR 5개 요약

### ADR — 기술 스택 결정 (`tech_stack_decision.md`)
- **결정**: Next.js 14 + TypeScript / FastAPI(Python 3.11) + Pydantic v2 / Supabase(PostgreSQL 15 + pgvector) / OpenAI(gpt-4o-mini+gpt-4o) / Redis(Upstash) / Vercel·Render·Supabase 배포.
- **배경**: 솔로 운영 가정, 빠른 검증 우선. multi-llm-validation으로 합의.
- **대안**: Frontend(Remix/SvelteKit), Backend(Express/NestJS), DB(raw PostgreSQL/Firebase).
- **트레이드오프**: 단일 LLM provider로 시작(통합 단순성↑, lock-in 위험↑) → Phase 5+ Anthropic 병행 완화. *(이후 임베딩=Gemini 한국어 우위 채택으로 진화.)*

### ADR-020 — Supabase 채택 (`phase_5_supabase_adoption.md`)
- **결정**: DB/Auth/RLS/SSE를 Supabase(PostgreSQL+pgvector+GoTrue) 단일 플랫폼으로.
- **배경**: 통합 인프라 + Free tier 0원 + RLS/pgvector 내장 → Phase 7 RAG 즉시 호환.
- **대안**: raw PostgreSQL(Neon/RDS, Auth 직접), Firebase(NoSQL → pgvector 미지원), 자체 서버.
- **트레이드오프**: Auth/Storage vendor lock-in ↔ MVP 속도. DB는 표준 PostgreSQL 유지 → self-host 마이그 가능. JWT httpOnly cookie + RLS로 사용자 격리.

### ADR-025 — RAG Architecture (`phase_7_rag_architecture.md`)
- **결정**: chunk 512 tokens(overlap 50) / 임베딩 1536dim / pgvector cosine top_k=5 threshold=0.7 / **brand_id 격리 강제** / **RAG > LLM Wiki 우선**(0 results 시 fallback).
- **배경**: candidate_knowledge 5단계 승격(후보→필터→평가→승인→승격) MVP.
- **대안**: chunk 256/1024, threshold 0.65/0.75, BM25 hybrid·cross-encoder re-rank(→Phase 9+로 이관).
- **트레이드오프**: Lite scope 우선. *진화*: text-embedding-3-small 한국어 약함(0.7 미달) → **Gemini embedding 채택**(0.7 통과 3/3, 임베딩=Gemini/생성=GPT 분리).

### ADR-027 — MOA Orchestrator 추출 (`phase_8_moa_orchestrator.md`)
- **결정**: router에 인라인된 ~400줄 god-function(`plans_generate`)을 `orchestration/moa_orchestrator.py` service layer로 추출. router는 thin adapter.
- **배경**: `moa_policy §2` 위반(orchestration이 HTTP 경계에 결합) + 단일 책임 위반.
- **대안**: "추출 김에 로직 개선"(scope creep + 회귀 위험) → 거부.
- **트레이드오프**: **behavior-preserving** — Envelope byte-identical, 기존 pytest 223 수정 0(동작이 바뀌면 추출이 틀린 것). ProgressSink Protocol로 SSE 결합도↓.

### ADR-016 / ADR-018 — Critic Revise + Canonical (`phase_4_5_critic_revise.md`, `phase_6_critic_canonical.md`)
- **결정**: Critic verdict가 `revise`면 Rewriter로 **최대 2회** 자동 개선(`critic_max_revise=2`). 점수는 **canonical overall_score(0~1) + dimensions(0~1)** 단일 표준.
- **배경**: Phase 4까지 Critic은 진단만, 개선 미실행. 0~5/0~1 혼재 + fallback chain 누적.
- **대안**: 무한 revise(차단), 0~5 유지(deprecated).
- **트레이드오프**: LLM 호출↑(완화: 2회 상한 + plan별 parallel). *진화*: 0~5 deprecated 제거(Phase 9.5) → canonical 0~1 단일화. Critic 낙관 편향("88점 함정")은 **cross-provider Claude judge**로 보강(false-approve 10→0).

---

## 7. 주요 시행착오 (설계 진화)

| # | 문제 | 해결 |
|---|---|---|
| ① | **Critic "88점 함정"** — critic 89점 vs 사람 44점, calibration 단독으론 verdict 0건 못 뒤집음 | cross-provider Claude judge(사람정렬, 괴리 0.53) → false-approve 10/10 → 0/10 |
| ② | **RAG 한국어 임베딩 약함** — text-embedding-3-small 0.7 미달 | Gemini embedding 채택(0.7 통과 3/3), 임베딩=Gemini/생성=GPT 분리 |
| ③ | **MOA god-function** — plans.py ~659줄 | orchestrator 추출(behavior-preserving, Envelope byte-identical) |
| ④ | **Critic 점수 표준 혼재** — 0~5 deprecated | canonical 0~1 단일 표준으로 제거(warnings 67→0) |
</content>
