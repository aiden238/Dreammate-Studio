# db_schema.md — 영상기획 AI 에이전트 DB 스키마

> 위치: `docs/contracts/db_schema.md`
> 상태: Phase 5 Slice 2 갱신 (v1 → v1.1.0 — plans 테이블 + 4계층 migration baseline 등록)
> DB: PostgreSQL 15+ on Supabase, with pgvector extension
> 계층: User → Brand → Domain → Series → Video Project (4-layer)
> Related: ADR-020 (Supabase 채택), upcoming ADR-021 (RLS, Slice 4)
> Migration files: `backend/fastapi/db/migrations/0001_init.sql` (Phase 5 baseline), `0002_phase_4_5_revise_history.sql` (Phase 4.5/6 정합), `0003_rls_policy.sql` (Slice 4 예정)

---

## 1. 설계 원칙

```
1. 4계층(Brand/Domain/Series/Video)을 별도 테이블로 명시한다. (단일 projects 테이블 금지)
2. 모든 테이블에 created_at, updated_at, soft delete용 deleted_at을 둔다.
3. 사용자 선택 데이터(클릭, 거절 이유)는 별도 로그 테이블로 분리한다.
4. AI 호출 결과는 원본 JSON을 그대로 보관한다 (재현성).
5. 후보 지식(candidate_knowledge)은 RAG와 분리되어 있다가 승격 시 이동한다.
6. pgvector 임베딩 컬럼은 768 또는 1536차원 중 모델에 맞춰 단일 선택.
7. cascade 삭제는 금지. soft delete + 참조 무결성 유지.
8. 모든 ID는 uuid v4. (Supabase 기본)
```

---

## 2. ER 다이어그램 (텍스트)

```
auth.users (Supabase 관리)
    │
    └─ user_profiles (1:1)
            │
            └─ brands (1:N)
                    │
                    └─ brand_memory_entries (1:N)
                    │
                    └─ domains (1:N)
                            │
                            └─ series (1:N)
                                    │
                                    └─ video_projects (1:N)
                                            │
                                            ├─ video_briefs (1:1)
                                            ├─ plan_options (1:N, 보통 3)
                                            ├─ selected_plans (1:1)
                                            ├─ scripts (1:N, version)
                                            ├─ storyboards (1:N, version)
                                            ├─ quality_scores (1:N)
                                            ├─ revision_requests (1:N)
                                            └─ final_outputs (1:1)

부속 테이블:
    discovery_choices (사용자가 어떤 카드 클릭했는지)
    intent_filter_logs (영상기획 외 입력 차단 기록)
    agent_io_logs (모든 LLM 호출 IO)
    candidate_knowledge (RAG 승격 후보)
    rag_documents / rag_chunks (RAG 본체)
    feedback_events (likedislike, 거절 이유 등)
```

---

## 3. 핵심 테이블 정의

### 3.1 user_profiles

```sql
create table user_profiles (
    user_id           uuid primary key references auth.users(id) on delete cascade,
    display_name      text not null,
    email             text not null,
    avatar_url        text,
    onboarding_state  text not null default 'pending',   -- pending | brand_created | first_plan_done
    locale            text not null default 'ko-KR',
    created_at        timestamptz not null default now(),
    updated_at        timestamptz not null default now()
);
```

### 3.2 brands

```sql
create table brands (
    brand_id         uuid primary key default gen_random_uuid(),
    user_id          uuid not null references user_profiles(user_id),
    name             text not null,
    short_idea       text,                       -- 사용자가 처음 입력한 짧은 아이디어
    direction_label  text,                       -- "성장 기록형" 같은 선택된 방향
    tone             jsonb default '{}'::jsonb,  -- {primary, avoid, examples}
    target_summary   text,                       -- 카드 선택으로 도출된 타겟 요약
    is_test_brand    boolean default false,      -- 드림메이트 같은 테스트 브랜드 표시
    created_at       timestamptz not null default now(),
    updated_at       timestamptz not null default now(),
    deleted_at       timestamptz,
    unique (user_id, name)
);

create index idx_brands_user on brands(user_id) where deleted_at is null;
```

### 3.3 domains

```sql
create table domains (
    domain_id     uuid primary key default gen_random_uuid(),
    brand_id      uuid not null references brands(brand_id),
    name          text not null,
    description   text,
    created_at    timestamptz not null default now(),
    updated_at    timestamptz not null default now(),
    deleted_at    timestamptz,
    unique (brand_id, name)
);

create index idx_domains_brand on domains(brand_id) where deleted_at is null;
```

### 3.4 series

```sql
create table series (
    series_id        uuid primary key default gen_random_uuid(),
    domain_id        uuid not null references domains(domain_id),
    name             text not null,             -- "대학생이 창업을 하며 겪은 이야기"
    structure_type   text,                      -- "growth_record" | "experiment" | "community" | ...
    description      text,
    cadence_hint     text,                      -- "주 1회" 등 운영 힌트
    created_at       timestamptz not null default now(),
    updated_at       timestamptz not null default now(),
    deleted_at       timestamptz,
    unique (domain_id, name)
);

create index idx_series_domain on series(domain_id) where deleted_at is null;
```

### 3.5 video_projects

```sql
create table video_projects (
    video_id           uuid primary key default gen_random_uuid(),
    series_id          uuid not null references series(series_id),
    title              text not null,
    short_idea         text,                    -- 영상별 짧은 아이디어
    mode               text not null,           -- 'discovery' | 'quick'
    one_line_direction text,                    -- 승인된 한 줄 방향
    status             text not null default 'draft',
                                                 -- draft | generating | plans_ready
                                                 -- | plan_selected | final | archived
    created_at         timestamptz not null default now(),
    updated_at         timestamptz not null default now(),
    deleted_at         timestamptz
);

create index idx_video_series on video_projects(series_id) where deleted_at is null;
create index idx_video_status on video_projects(status);
```

### 3.6 plans (Phase 5 Slice 2 신규 — _plan_store 영속화)

Phase 4 router 의 in-memory `_plan_store: dict` 를 PostgreSQL 영속화하는 테이블.
Phase 4.5 (revise loop) + Phase 6 (canonical Critic) 의 모든 산출물 컬럼 포함.

```sql
create table plans (
    id                      uuid primary key default gen_random_uuid(),
    auth_user_id            uuid,                          -- nullable: Phase 1 anonymous endpoint 호환 (Slice 4 ADR-021)
    video_project_id        uuid references video_projects(video_id) on delete set null,
    mode                    text not null,                 -- 'discovery' | 'quick'
    status                  text not null default 'draft', -- draft | generated | finalized
    wizard_state            jsonb default '{}'::jsonb,     -- Discovery 7-step / Quick 4-step 진행 상태
    plan_candidates         jsonb default '[]'::jsonb,     -- Phase 4 3-plan 결과
    critic_evaluation       jsonb,                         -- Phase 6 canonical (overall_score + dimensions)
    revise_history          jsonb,                         -- Phase 4.5 ADR-016 + Phase 6 ReviseAttempt
    recommended_plan_index  integer,                       -- Phase 4.5 ADR-017 best-plan (0~2)
    created_at              timestamptz not null default now(),
    updated_at              timestamptz not null default now()
);

create index idx_plans_auth_user_id     on plans(auth_user_id);
create index idx_plans_video_project_id on plans(video_project_id);
```

**JSONB schemas**:

- `critic_evaluation` (Phase 6 ADR-018 canonical):
  - `overall_score`: float [0.0~1.0]
  - `dimensions`: dict[str, float] (8-dim or subset)
  - `overall_verdict`: "approve" | "revise" | "reject"
  - (deprecated 필드 `overall_score_avg`, `scores`, `eight_dim_scores` 는 DB 미저장 — Phase 9+ 제거)
- `revise_history` (Phase 4.5 ADR-016 + Phase 6 ReviseAttempt typing):
  - `list[list[dict]]` — plan별 attempt list of dicts (`attempt`, `action`, `revised`, `max_reached?`, `critic_warning?`, `rewriter_warning?`)
- `wizard_state`:
  - Discovery 7-step (`step1`~`step7`) 또는 Quick 4-step (`quick.initial`/`quick.clarify`/`quick.direction`/`quick.generate`) 진행 상태
- `plan_candidates`:
  - 3-plan Plan model 배열 (output_schema.md §4 Plan)

**graceful fallback** (PlansRepo, Phase 5 Slice 2):
- Supabase 실패 시 (URL/Key 미설정, 패키지 미설치, 연결 에러) `_plan_store: dict` 로 in-memory fallback.
- `routers/plans.py` 는 PlansRepo 인터페이스 통해 호출 → Supabase or in-memory 자동 선택.

---

## 4. Video Project 산출물 테이블

### 4.1 video_briefs

```sql
create table video_briefs (
    video_id        uuid primary key references video_projects(video_id),
    purpose         text,
    target          text,
    tone            text,
    format          text,                       -- "shorts_30s" | "reels_60s" | ...
    inherited_from  jsonb,                      -- {brand_id, domain_id, series_id} (메모리 상속 출처)
    created_at      timestamptz not null default now(),
    updated_at      timestamptz not null default now()
);
```

### 4.2 plan_options

3개 기획안 카드. 항상 3개를 생성하는 게 원칙.

```sql
create table plan_options (
    option_id     uuid primary key default gen_random_uuid(),
    video_id      uuid not null references video_projects(video_id),
    option_index  smallint not null,            -- 0, 1, 2
    name          text not null,
    concept       text,
    hook          text,
    flow          jsonb,                        -- [{beat: "...", duration: 3}, ...]
    pros          text,
    risks         text,
    raw_llm_json  jsonb,                        -- 원본 LLM 응답 보관
    created_at    timestamptz not null default now(),
    unique (video_id, option_index),
    check (option_index between 0 and 2)
);

create index idx_plan_options_video on plan_options(video_id);
```

### 4.3 selected_plans

#### Idealized (Phase 11+ — 4계층 full linkage, NG2)

`plan_options.option_id` 참조 전제. plan_options 테이블(§4.2)이 존재하는 4계층 full linkage 에서만 적용 — Phase 11+.

```sql
create table selected_plans (
    video_id          uuid primary key references video_projects(video_id),
    selected_option_id uuid not null references plan_options(option_id),
    selection_reason   text,                    -- 사용자가 입력한 선택 이유
    selected_at        timestamptz not null default now()
);
```

#### Phase 9 실 구현 (`0005_feedback_selection.sql` — 실 plans 정합, ADR-030)

실 영속화는 `plans` 테이블(§3.6, plan_candidates JSONB 3-plan 배열) 정합. plan_options 미생성이므로 `selected_option_index`(0–2, plan_candidates 배열 인덱스)로 선택 식별. 선택 plan 내용은 `plans.plan_candidates[selected_option_index]` 로 조회.

```sql
create table selected_plans (
    id                    uuid primary key default gen_random_uuid(),
    plan_id               uuid not null references plans(id) on delete cascade,
    auth_user_id          uuid,                          -- nullable (anon 호환, Phase 5 패턴)
    selected_option_index smallint not null,             -- 0~2 (plan_candidates 배열 index)
    selection_reason      text,                          -- 사용자 선택 사유 (PII 저장 전 마스킹 — security-review T1)
    created_at            timestamptz not null default now(),
    check (selected_option_index between 0 and 2)
);
-- RLS: auth_user_id = auth.uid() (anon nullable 허용) — 0005, Phase 5 0003_rls_policy.sql 패턴 (T3).
```

### 4.4 scripts / storyboards

```sql
create table scripts (
    script_id   uuid primary key default gen_random_uuid(),
    video_id    uuid not null references video_projects(video_id),
    version     int not null,
    content     text not null,
    raw_llm_json jsonb,
    created_at  timestamptz not null default now(),
    unique (video_id, version)
);

create table storyboards (
    storyboard_id uuid primary key default gen_random_uuid(),
    video_id      uuid not null references video_projects(video_id),
    version       int not null,
    shots         jsonb not null,              -- [{shot_no, description, duration, camera}, ...]
    raw_llm_json  jsonb,
    created_at    timestamptz not null default now(),
    unique (video_id, version)
);
```

### 4.5 quality_scores (Critic Agent 결과)

```sql
create table quality_scores (
    score_id        uuid primary key default gen_random_uuid(),
    video_id        uuid not null references video_projects(video_id),
    target_kind     text not null,             -- 'plan_option' | 'script' | 'final'
    target_id       uuid not null,             -- option_id / script_id / final_id
    intent_fit      smallint check (intent_fit between 0 and 5),
    target_clarity  smallint check (target_clarity between 0 and 5),
    hook_strength   smallint check (hook_strength between 0 and 5),
    message_clarity smallint check (message_clarity between 0 and 5),
    structure       smallint check (structure between 0 and 5),
    feasibility     smallint check (feasibility between 0 and 5),
    brand_consistency smallint check (brand_consistency between 0 and 5),
    differentiation smallint check (differentiation between 0 and 5),
    reasons         jsonb not null,            -- {intent_fit: "이유...", ...}
    suggestions     jsonb not null,            -- {intent_fit: "개선안...", ...}
    raw_llm_json    jsonb,
    created_at      timestamptz not null default now()
);

create index idx_quality_target on quality_scores(target_kind, target_id);
```

### 4.6 revision_requests

```sql
create table revision_requests (
    revision_id  uuid primary key default gen_random_uuid(),
    video_id     uuid not null references video_projects(video_id),
    target_kind  text not null,                -- 'plan_option' | 'script' | 'storyboard'
    target_id    uuid not null,
    reason       text not null,
    requested_changes text,
    rewriter_result   jsonb,                   -- Rewriter Agent 결과
    created_at   timestamptz not null default now()
);
```

### 4.7 final_outputs

```sql
create table final_outputs (
    video_id        uuid primary key references video_projects(video_id),
    plan            text not null,             -- 최종 영상기획서 (markdown)
    hook            text,
    script          text,
    structure       jsonb,
    shooting_notes  text,
    upload_caption  text,
    hashtags        text[],
    community_hooks text,                      -- 커뮤니티 유입 문구
    raw_payload     jsonb,                     -- 패키지 원본
    created_at      timestamptz not null default now(),
    updated_at      timestamptz not null default now()
);
```

---

## 5. 학습 신호 테이블

### 5.1 discovery_choices (Discovery 카드 클릭 데이터)

```sql
create table discovery_choices (
    choice_id      uuid primary key default gen_random_uuid(),
    user_id        uuid not null references user_profiles(user_id),
    brand_id       uuid references brands(brand_id),
    domain_id      uuid references domains(domain_id),
    series_id      uuid references series(series_id),
    video_id       uuid references video_projects(video_id),
    step_name      text not null,              -- 'brand' | 'domain' | 'series' | 'target' | 'tone'
    presented_options jsonb not null,          -- AI가 제시한 5장 카드 전체
    selected_option   jsonb,                   -- 선택된 1장 (또는 null = 직접 입력)
    rejected_options  jsonb,                   -- 선택 안 된 4장
    direct_input      text,                    -- 직접 입력했을 때
    rejection_reasons jsonb,                   -- {option_index: "이유"}
    created_at        timestamptz not null default now()
);

create index idx_discovery_user on discovery_choices(user_id);
create index idx_discovery_step on discovery_choices(step_name);
```

### 5.2 feedback_events

#### Idealized (Phase 11+ — 4계층 target_kind+target_id, NG2)

```sql
create table feedback_events (
    feedback_id  uuid primary key default gen_random_uuid(),
    user_id      uuid not null references user_profiles(user_id),
    target_kind  text not null,                -- 'plan_option' | 'script' | 'storyboard' | 'final'
    target_id    uuid not null,
    event_type   text not null,                -- 'like' | 'dislike' | 'reject' | 'regenerate'
    reason       text,
    created_at   timestamptz not null default now()
);

create index idx_feedback_target on feedback_events(target_kind, target_id);
create index idx_feedback_user on feedback_events(user_id);
```

#### Phase 9 실 구현 (`0005_feedback_selection.sql` — 실 plans 정합, ADR-030)

target_kind/target_id 는 plan_id 정합으로 단순화 (Phase 9 = plan 단위 피드백). target_kind = `'plan_candidate'` (plan_id + option_index) 로 표현 — `option_index`(0–2)는 특정 candidate 대상, null = plan 전체. `reason` 은 자유 입력 → **저장 전 PII 마스킹**(이메일/전화/주민/카드 → `[masked]`, FeedbackRepo INSERT 직전 — security-review T1/T2).

```sql
create table feedback_events (
    id            uuid primary key default gen_random_uuid(),
    plan_id       uuid not null references plans(id) on delete cascade,
    auth_user_id  uuid,                                  -- nullable (anon 호환, Phase 5 패턴)
    option_index  smallint,                              -- 0~2 (특정 candidate 대상, null=plan 전체)
    event_type    text not null,                         -- 'like'|'dislike'|'reject'|'regenerate'
    reason        text,                                  -- PII 저장 전 마스킹 (security-review T1/T2)
    created_at    timestamptz not null default now(),
    check (event_type in ('like','dislike','reject','regenerate')),
    check (option_index is null or option_index between 0 and 2)
);
create index idx_feedback_plan on feedback_events(plan_id);
create index idx_feedback_user on feedback_events(auth_user_id);
-- RLS: auth_user_id = auth.uid() (anon nullable 허용) — 0005 (T3).
```

### 5.3 intent_filter_logs

```sql
create table intent_filter_logs (
    log_id      uuid primary key default gen_random_uuid(),
    user_id     uuid not null references user_profiles(user_id),
    video_id    uuid references video_projects(video_id),
    raw_input   text not null,
    decision    text not null,                 -- 'allow' | 'block' | 'allow_after_reframe'
    reason      text,                          -- AI 판단 이유
    created_at  timestamptz not null default now()
);

create index idx_intent_filter_user on intent_filter_logs(user_id);
```

---

## 6. Brand Memory

#### Idealized 정의 (4계층 — source_video_id)

```sql
create table brand_memory_entries (
    entry_id     uuid primary key default gen_random_uuid(),
    brand_id     uuid not null references brands(brand_id),
    entry_type   text not null,                -- 'preferred_tone' | 'avoid_phrase'
                                                -- | 'preferred_phrase' | 'success_pattern'
                                                -- | 'rejection_pattern'
    content      text not null,
    source_video_id uuid references video_projects(video_id),
    confidence   real default 0.5,             -- 0–1, 자동 추출일 때 신뢰도
    is_user_locked boolean default false,      -- 사용자가 직접 잠근 항목은 자동 갱신 금지
    created_at   timestamptz not null default now(),
    updated_at   timestamptz not null default now()
);

create index idx_brand_memory on brand_memory_entries(brand_id);
```

#### Phase 9 준비 (`0005_feedback_selection.sql` — 실 정합, ADR-031)

Phase 9 는 **준비만** (사용자 결정 5 / NG1): schema 등록 + `BrandMemoryRepo`(graceful, 수동/준비용 entry CRUD) 만. **자동 추출 agent(P-AUX-2 `brand_memory_extractor`)는 미구현 — Phase 10+** (MVP 운영 + 데이터 누적 후, ai_system/prompts/prompt_registry.md 가 명세 SoT). feedback/selection → candidate_knowledge 적재 경로(§7.2 source_kind)는 Phase 9 Slice 4 (pending 까지만 — 자동 승격 X, NG12).

실 구현은 `brands(id)` (0001_init.sql PK) + `source_plan_id`(→ plans.id) 정합 (idealized `source_video_id` 대신).

```sql
create table brand_memory_entries (
    entry_id        uuid primary key default gen_random_uuid(),
    brand_id        uuid references brands(id) on delete cascade,
    entry_type      text not null,             -- preferred_tone|avoid_phrase|preferred_phrase|success_pattern|rejection_pattern
    content         text not null,
    source_plan_id  uuid references plans(id) on delete set null,
    confidence      real default 0.5,          -- 0–1 (자동 추출 신뢰도 — Phase 10+)
    is_user_locked  boolean default false,
    created_at      timestamptz not null default now(),
    updated_at      timestamptz not null default now(),
    check (entry_type in ('preferred_tone','avoid_phrase','preferred_phrase','success_pattern','rejection_pattern'))
);
-- RLS: brands(id) 를 통한 user 격리 (Phase 5 domains_via_brand 패턴) — 0005.
```

---

## 7. AI 인프라 테이블

### 7.1 agent_io_logs (모든 LLM 호출 IO)

```sql
create table agent_io_logs (
    log_id         uuid primary key default gen_random_uuid(),
    user_id        uuid references user_profiles(user_id),
    video_id       uuid references video_projects(video_id),
    agent_name     text not null,              -- 'intent' | 'planner' | 'critic' | 'rewriter' | 'card_generator'
    prompt_id      text not null,              -- 'P-001' 등 prompt_registry 키
    prompt_version text not null,              -- 'v1.0.2'
    model          text not null,              -- 'gpt-4o-mini' 등
    input_payload  jsonb not null,
    output_payload jsonb,
    error          text,
    latency_ms     int,
    input_tokens   int,
    output_tokens  int,
    cost_usd       numeric(10, 6),
    created_at     timestamptz not null default now()
);

create index idx_agent_logs_video on agent_io_logs(video_id);
create index idx_agent_logs_agent on agent_io_logs(agent_name);
create index idx_agent_logs_prompt on agent_io_logs(prompt_id, prompt_version);
```

### 7.2 candidate_knowledge (RAG 승격 후보)

```sql
create table candidate_knowledge (
    candidate_id  uuid primary key default gen_random_uuid(),
    source_kind   text not null,              -- 'user_choice' | 'user_feedback' | 'final_output' | 'manual'
    source_id     uuid,                       -- 출처 레코드 ID
    content       text not null,
    metadata      jsonb default '{}'::jsonb,
    quality_score real,                       -- 품질 필터 점수
    status        text not null default 'pending',
                                              -- pending | filtered | evaluated | approved
                                              -- | promoted | rejected
    reviewer      text,                       -- 'auto' | user_id | 'human_reviewer'
    review_notes  text,
    created_at    timestamptz not null default now(),
    updated_at    timestamptz not null default now()
);

create index idx_candidate_status on candidate_knowledge(status);
```

**승격 흐름** (`status` 전이):

```
pending → filtered → evaluated → approved → promoted
                                       ↘ rejected
```

`promoted` 상태가 되면 별도 ETL이 `rag_documents` + `rag_chunks`에 데이터 복제.

### 7.3 rag_documents / rag_chunks

```sql
create extension if not exists vector;

create table rag_documents (
    document_id   uuid primary key default gen_random_uuid(),
    source_type   text not null,              -- 'llm_wiki' | 'external_seed'
                                              -- | 'user_promoted' | 'curated'
    source_path   text,                       -- LLM Wiki 파일 경로 등
    title         text,
    metadata      jsonb default '{}'::jsonb,
    is_active     boolean default true,
    created_at    timestamptz not null default now(),
    updated_at    timestamptz not null default now()
);

create table rag_chunks (
    chunk_id     uuid primary key default gen_random_uuid(),
    document_id  uuid not null references rag_documents(document_id) on delete cascade,
    chunk_index  int not null,
    content      text not null,
    embedding    vector(1536),                -- 모델에 맞춰 차원 변경 가능
    metadata     jsonb default '{}'::jsonb,
    created_at   timestamptz not null default now(),
    unique (document_id, chunk_index)
);

create index idx_rag_embedding on rag_chunks
    using ivfflat (embedding vector_cosine_ops)
    with (lists = 100);

create index idx_rag_doc on rag_chunks(document_id);
```

### 7.4 prompt_registry_log

```sql
create table prompt_registry_log (
    log_id        uuid primary key default gen_random_uuid(),
    prompt_id     text not null,
    version       text not null,
    template      text not null,
    activated_at  timestamptz not null default now(),
    deactivated_at timestamptz,
    notes         text,
    unique (prompt_id, version)
);
```

---

## 8. 인덱스 / 성능

```sql
-- 4계층 조회 가속
create index idx_brand_user_active on brands(user_id) where deleted_at is null;
create index idx_domain_active     on domains(brand_id) where deleted_at is null;
create index idx_series_active     on series(domain_id) where deleted_at is null;
create index idx_video_active      on video_projects(series_id) where deleted_at is null;

-- 학습 신호 분석
create index idx_choices_created on discovery_choices(created_at desc);
create index idx_feedback_created on feedback_events(created_at desc);

-- 비용 모니터링
create index idx_logs_user_created on agent_io_logs(user_id, created_at desc);
create index idx_logs_cost on agent_io_logs(created_at) where cost_usd > 0;
```

---

## 9. RLS (Row Level Security)

Supabase 기준. **Phase 5 Slice 4 (ADR-021) 에서 본격 활성화 예정** — 본 Slice 2 는 컬럼 baseline 만 등록.

```sql
alter table brands enable row level security;
create policy brands_owner on brands
    for all using (user_id = auth.uid());

alter table domains enable row level security;
create policy domains_owner on domains
    for all using (
        brand_id in (select brand_id from brands where user_id = auth.uid())
    );

-- series, video_projects, video_briefs, plan_options, ... 동일 패턴

-- Phase 5 Slice 4 plans RLS (ADR-021 예정):
alter table plans enable row level security;
create policy plans_user_isolation on plans
    for all
    using (auth_user_id = auth.uid() or auth_user_id is null)
    with check (auth_user_id = auth.uid());
```

### Phase 5 anonymous endpoint 분리 (Slice 4 ADR-021)

- `/api/v1/generate` (Phase 1 endpoint, NG7 → Phase 8+ 제거) → anon role (RLS 미적용)
- `/plans/start` (Phase 5) → anon role 가능, auth_user_id NULL 허용 (임시 게스트 ID)
- `/plans/{plan_id}/generate`, `/plans/{plan_id}` (GET/UPDATE/DELETE) → authenticated role (RLS 강제)

서비스 롤(`service_role`)은 RLS 우회 가능하지만, 일반 API는 항상 사용자 토큰으로 작동. service_role key 는 backend .env only (NEXT_PUBLIC_* prefix 절대 금지 — llm_security_contract.md §5.2).

---

## 10. 데이터 보존 / 삭제

```
soft delete (deleted_at) → 30일 → hard delete
discovery_choices, feedback_events → 2년 보관 후 익명화
agent_io_logs → 1년 (raw payload는 90일 후 비식별화)
candidate_knowledge (status=rejected) → 90일 후 hard delete
candidate_knowledge (status=promoted) → 영구 (단, 출처 user_id는 익명화)
intent_filter_logs → 1년
```

사용자 계정 삭제 시:

```
brands ~ video_projects: soft delete 후 30일
agent_io_logs: 즉시 user_id null 처리 (raw_payload는 유지)
candidate_knowledge: 이미 promoted된 항목은 익명화 후 보존
```

---

## 11. 마이그레이션 노트

### Phase 1 (MVP, legacy)

- `backend/fastapi/db/migrations/001_init.sql` — video_projects + plan_candidates 익명 저장 minimal.
- 3-digit zero-padded naming (legacy 보존).
- 익명 저장 (user_id NULL allow), 4계층 미도입.

### Phase 5 Slice 2 (현)

- `backend/fastapi/db/migrations/0001_init.sql` — brands / domains / series / video_projects / plans 4계층 baseline (Phase 5 신규).
- `backend/fastapi/db/migrations/0002_phase_4_5_revise_history.sql` — ALTER IF NOT EXISTS revise_history + recommended_plan_index + critic_evaluation (idempotent).
- 4-digit zero-padded naming (Phase 5+).
- Phase 4.5 (revise loop) + Phase 6 (canonical Critic) 산출물 컬럼 정합.
- ADR-020 (Supabase 채택) 정합 — graceful fallback (Supabase 실패 시 in-memory dict).

### Phase 5 Slice 3 (Auth, 예정)

- ALTER TABLE plans / video_projects / brands ALTER COLUMN auth_user_id SET NOT NULL + REFERENCES auth.users(id) ON DELETE CASCADE (Supabase Auth 도입 후).

### Phase 5 Slice 4 (RLS, 예정 ADR-021)

- `backend/fastapi/db/migrations/0003_rls_policy.sql` — plans / video_projects / brands / domains / series RLS 활성화.
- anonymous endpoint (/api/v1/generate, /plans/start) 별도 anon role 분리.

### Phase 11+ (확장)

- `team_workspaces` + `team_members` 추가
- `subscriptions` + `credits_balance` 추가
- `prompt_versions` 별도 테이블화

### Phase 21+ (Spring Boot 분리)

- 회원/결제/팀 관련 테이블은 Spring Boot 측 DB로 분리 후 user_id만 외래 참조.
- AI/RAG/Eval 관련 테이블은 FastAPI 측 DB 유지.
- 분리 시 user_id 외래 키 제약은 application-level로 전환.

---

## 12. Open Questions

1. pgvector 차원 (1536 vs 768) — 사용할 임베딩 모델 확정 후 결정.
2. `agent_io_logs.raw_payload` 90일 후 비식별화 방식 — 마스킹 vs 삭제.
3. Series 단위 메모리(brand_memory와 별개)를 둘지.
4. `plan_options.flow` JSON 스키마 — `output_schema.md`에서 별도 정의 필요.
5. RLS 정책의 admin 우회 — 운영자 대시보드 도입 시점에 결정.
6. Multi-brand 사용자가 최대 몇 개까지 브랜드를 만들 수 있는지 (무료/유료 차등).
