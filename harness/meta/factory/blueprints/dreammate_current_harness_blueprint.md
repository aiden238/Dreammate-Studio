# dreammate_current_harness_blueprint.md — 현재 하네스 실측 역정리

> 위치: `harness/meta/factory/blueprints/dreammate_current_harness_blueprint.md`
> 상태: Phase M0 (Meta-Factory Prep, ★ meta-phase) Slice 2 — 현재 Dreammate 하네스를 harness_blueprint 형식으로 **실측 역정리**
> 결정: ADR-035
> 참조: harness_blueprint_schema.md (출력 schema), architecture_patterns.md (6 패턴 + Dreammate 매핑), validation_workflow.md (6 검증)
> ★ 실측 (추측 금지) — 본 문서의 수치/구조는 저장소를 직접 읽어 확인한 값이다 (작성 시점 기준).
> ★ 런타임 변경 0 (A9) — 본 문서는 현재 하네스를 **읽어서 정리**할 뿐 L1/L2 를 수정하지 않는다.

---

## 0. 이 문서의 위치

본 blueprint 는 현재 Dreammate 구현 하네스(L2)와 그 위 product runtime(L1)을 `harness_blueprint_schema.md` 형식으로 역정리한 **실측 청사진**이다. 신규 도메인 하네스 생성 시 참조 baseline 이자, L3 Meta-Factory 가 정확히 무엇을 확장해야 하는지(§10 부족점)를 도출하는 근거 문서다.

★ blueprint 는 proposal 이지만, 본 문서는 **현재 active 하네스의 사후 정리**이므로 validation 필드는 "현재 운영 중(live)" 로 표기한다 (신규 생성 blueprint 의 pending 과 구분).

> ★ **LIVING blueprint 전환 (2026-06-05, HIP-010 S2)** — 본 청사진은 Phase M0(작성 시점) 스냅샷에서 **정기 갱신되는 self-map** 으로 전환된다. 갱신 주체 = 009-S1 cadence(harness-audit 정기 트리거) + 009-S2 meta/factory `validation_workflow` reflexive 실행. 본문 §2~§11 은 작성 시점(Phase 0~9.5) 스냅샷이며, 최신 델타는 아래 §0.1.

## 0.1 LIVING UPDATE (2026-06-05)

> 본문 세부(특히 §4 agent 목록)의 전수 재실측은 009-S2 reflexive 실행에서 수행. 아래는 headline 델타.

| 항목 | M0 스냅샷(§본문) | 현재 (2026-06-05) |
|---|---|---|
| phases | 0~9.5 done + M0 active | **0~26 + M0~M3 전부 done/archive**, next=pending_user_decision |
| pytest | 339 | **789** (Phase 26 baseline 779 + HIP-006 텔레메트리/cost 10) |
| Skill 수 | 20→21 | **21** (harness-factory 포함) |
| contract changes | CC-001~005 | **CC-001~034** / ADR 035+ |
| meta 레이어 | `meta/` + `meta_factory/` (2폴더) | **`meta/` 단일** (meta_factory → `meta/factory/` 병합, 2026-06-05) |
| agents | 5 (intent/planning/critic/rewriter/rag) | + brand_injection/brand_memory_extractor/topic_discovery/pkm 등 (PKM·브랜딩·commercial 확장) — §4 전수 재실측 = 009-S2 |
| output_mode | compact (rich gated) | **4-tier** compact/rich/director/commercial_viral (전부 gated) |
| 관측성 | 없음 | **agent_io 텔레메트리 발신기(HIP-006) + cost-review aggregator** (`backend/fastapi/observability/`) |
| 자기개선 | self_improvement_loop(루프) | + **harness-audit 최초 완주**(`meta/audits/`) + HIP-006~010 로드맵(`meta/improvement_roadmap_hip006-010.md`) |

★ §10 "부족점 5"(생성 자동화/.claude agents/trigger dry-run/with-without/acceptance)는 여전히 유효 — L3 reflexive 적용(HIP-009)으로 **우리 하네스 자기유지**에 재겨냥됨.

---

## 1. 현재 하네스 목적 (영상기획 AI 에이전트)

```yaml
harness_name: dreammate_video_planning_harness
purpose: "영상 제작이 아니라 영상기획을 돕는 AI 에이전트 (Discovery + Quick 하이브리드 UX)"
```

- **핵심 정의**: 영상 **제작** AI 가 아니라 영상 **기획** AI 에이전트 (CLAUDE.md §프로젝트 정의).
- **UX**: Hybrid — Discovery Wizard(7단계) + Quick Mode(짧은 프롬프트 → 부족 정보 질문 → 한 줄 방향 승인).
- **데이터 모델**: 4계층 (User → Brand → Domain → Series → Video).
- **핵심 흐름**: 입력 → 의도 분석(Discovery/Quick 분기) → 부족 정보 질문 → 한 줄 방향 승인 → LLM Wiki/RAG 검색 → 영상기획안 3개 생성 → Critic 검증(revise 최대 2회) → 개선안 반영 → 저장 → 피드백(Brand Memory 준비).

---

## 2. 현재 product runtime (L1 — 실측)

```yaml
runtime_type: product_saas
```

| 레이어 | 실측 구성 |
|---|---|
| **Backend** | FastAPI (`backend/fastapi/`) — 17 endpoints 누적 (Phase 1~9: /generate, /plans/{id}/generate, /auth/*, /sse/*, /plans/{id}/select, /plans/{id}/feedback 등) |
| **Frontend** | Next.js 14 PWA (`apps/web/`) — 11 routes (+/login) |
| **DB** | Supabase (PostgreSQL + pgvector) — 4계층 schema + plans + selected_plans + feedback_events + candidate_knowledge + JSONB |
| **RAG** | RAG Lite — pgvector retrieval (cosine + top-k=5 + threshold=0.7) + OpenAI text-embedding-3-small + chunking 512 tokens/overlap 50 + LLM Wiki 보조 (RAG > LLM Wiki 우선) |
| **진행 표시** | SSE Progress 4단계 (실 stage 연동, progress_store 브릿지, ADR-022/028) |
| **오케스트레이션** | MOA Lite — `orchestration/moa_orchestrator.py::generate_plan` (Supervisor) + 3-plan parallel + Critic revise loop |
| **인증/보안** | JWT httpOnly cookie + RLS 정책 (auth.uid() + 4 정책 + 2-hop subquery) + PII 마스킹 |

★ 실측: `backend/fastapi/orchestration/` = `moa_orchestrator.py` + `progress_sink.py` + `progress_store.py` + `responses.py` + `__init__.py`. `backend/fastapi/agents/` = `intent.py` + `planning.py` + `critic.py` + `rewriter.py` + `rag.py`.

---

## 3. 현재 implementation harness (L2 — 실측)

| 구성 | 실측 |
|---|---|
| **라우터** | `AGENTS.md` (구현/QA 모델) + `CLAUDE.md` (기획/설계 모델) |
| **상태** | `PROJECT_STATE.md` + `PHASE_REGISTRY.md` (Phase 0~9.5 done + M0 active) |
| **계약** | `docs/contracts/` — **21 파일** (api / output_schema / agent_io v1.3.0 / db_schema / llm_security / rate_limit / error_response / rag_data / frontend_design / tech_stack / data_retention / privacy / user_consent / accessibility / event_log / backend_boundary / frontend_boundary / product_boundary / mvp_non_goals / data / env) |
| **결정** | `docs/decisions/` — ADR-001~035 (phase_M0_meta_factory = ADR-035) |
| **계약 변경** | `docs/contract_changes/` — CC-001 ~ CC-005 (+ px1-self-verification 기록) |
| **운영** | `phases/` (active/archive) + `eval/` + `.claude/skills/` |
| **Skill** | **20 Skill** (작성 시점, INDEX.md 기준) → harness-factory 추가로 **21** (Slice 3 예정) |
| **메타** | `meta/self_improvement_loop.md` (5단계 루프) + `meta/retrospectives` + `meta/validations` + `meta/patterns.md` |
| **테스트** | pytest **339** (Phase 9.5 baseline) |

★ 실측: `docs/contracts/` 21 파일, `docs/decisions/` ADR 최신 = ADR-035, `docs/contract_changes/` CC 최신 = CC-005. Skill 20개(harness-factory 미도입, Slice 3).

---

## 4. 현재 agent 구조 (실측 — moa_orchestrator Supervisor)

```yaml
architecture_pattern:
  primary: supervisor              # moa_orchestrator.py::generate_plan 중개
  secondary: [fan_out_fan_in, producer_reviewer, pipeline]
```

| Agent | responsibility | forbidden_actions (실측 정신) |
|---|---|---|
| **intent** (`agents/intent.py`) | 의도 분석 (Discovery/Quick 분기 + Intent Filter) | RAG 직접 의존, plan 생성 (agent_io §1.6) |
| **planning** (`agents/planning.py`) | 영상기획안 3개 생성 (parallel, multi-model) | Critic 직접 호출 (orchestrator 경유) |
| **critic** (`agents/critic.py`) | plan 평가 (canonical overall_score + dimensions) | plan 직접 수정 (Rewriter 담당) |
| **rewriter** (`agents/rewriter.py`) | Critic verdict=revise 시 plan 개선 (max 2) | 무한 revise (critic_max_revise 상한) |
| **rag** (`agents/rag.py`) | RAG Lite 검색 + graceful marker (Planning 에만 주입) | Intent/Critic/Rewriter 직접 의존 |

**Supervisor (실측 — `moa_orchestrator.py`)**:
- `generate_plan` 이 Intent → RAG → 3-plan parallel → Critic+revise → DB save → Envelope 조립을 **중개**. agent 간 직접 호출 0 (moa_policy §2 정합).
- Fan-out/Fan-in: `run_planning_parallel_3` + plan별 Critic `asyncio.gather` (병렬).
- Producer-Reviewer: Planner → Critic(canonical normalize) → verdict=revise 시 Rewriter → 재평가, `critic_max_revise`(기본 2) 차단.
- Pipeline + graceful: 단방향 step + RAG/Critic/Rewriter/DB 실패 흡수 (graceful skip).

**ProgressSink (실측 — `progress_sink.py`)**: `NullProgressSink` default(no-op, 회귀 0) + `StoreProgressSink`(SSE 브릿지 `progress_store.py`).

★ 실측: 현재 agent 5개 — orchestrator 가 Supervisor 로 중개. `architecture_patterns.md §3` 의 Dreammate 매핑(supervisor 주 + fan_out_fan_in/producer_reviewer/pipeline 보조)과 정합.

---

## 5. 현재 skill 구조 (실측 — 20 Skill → 21)

```yaml
skills_count: 20                   # 작성 시점 (INDEX.md) → harness-factory 추가로 21 (Slice 3)
```

- **절차 핵심 14**: phase-start / phase-complete / contract-change / bug-triage / rag-update / eval-run / qa-check / cost-review / meta-retrospective / design-review / security-review / prompt-version-review / multi-llm-validation / context-compact.
- **검토/감사 6**: agent-io-check / ai-architecture-review / eval-design / harness-audit / phase-review / rag-design.
- **(Slice 3 예정) Meta-Factory 1**: harness-factory (proposal-only, 키워드 scoped — 본 Phase M0 Slice 3 에서 #21 등록).

**Skill 규율 (실측 — INDEX.md)**:
- 모든 Skill 은 description 키워드 매칭 자동 트리거 (수동 호출 금지).
- 같은 description 키워드 둘 이상 = 충돌 (즉시 수정).
- Skill 추가/변경은 contract-change Skill 절차 (Skill 도 contract 취급).
- 우선순위 충돌 해결 표 (context-compact > 전체 / contract-change > 절차 / harness-audit > meta-retrospective 등).
- applies_to 태그(agents / claude / both)로 라우터 분리.

★ 실측: `.claude/skills/` 디렉토리 = 20 Skill 폴더 + INDEX.md (harness-factory 부재 — Slice 3). INDEX.md 헤더 "총 20개 (절차 14 + 검토/감사 6)".

---

## 6. 현재 contracts (실측 — 21 파일 + ADR-001~035 + CC-005)

**contracts (21, 실측)**: api / output_schema / agent_io(v1.3.0 정신) / db_schema / llm_security / rate_limit / error_response / rag_data / frontend_design / tech_stack / data_retention / privacy / user_consent / accessibility / event_log / backend_boundary / frontend_boundary / product_boundary / mvp_non_goals / data / env.

**ADR (실측 — ADR-001~035)**: 최신 = ADR-035 (phase_M0_meta_factory.md, L3 Meta-Factory 도입). 직전 = ADR-033/034 (Phase 9.5 eval-run / Critic deprecated 제거). ADR-027~032 (Phase 8~9 MOA/SSE/prompt_registry/feedback/Brand Memory prep/normalize wiring).

**CC (실측 — CC-001~CC-005)**:
- CC-001: plan_options vs plan_candidates (Phase 1)
- CC-003: prompt_registry semver (Phase 8)
- CC-004: db_schema feedback/selection (Phase 9)
- CC-005: critic deprecated 제거 (Phase 9.5)
- (+ px1-sub-agent-self-verification 기록)
- CC-006 = INDEX Skill 등록 (Phase M0 Slice 3 예정).

**Cross-reference 정합 축 (실측)**:
- prompt_registry ↔ output_schema (prompt 출력 ↔ Envelope/Plan/Critic 본문)
- api_contract ↔ apps/web/lib/types (API 응답 ↔ 프론트 타입)
- db_schema ↔ db/migrations/000N (테이블/JSONB ↔ migration)
- agent_io ↔ agents[] IO (4 agent + orchestrator)

★ 실측: `docs/contracts/` 21 파일 / `docs/decisions/` ADR-035 최신 / `docs/contract_changes/` CC-005 최신 (CC-006 미도입).

---

## 7. 현재 eval 구조 (실측 — golden_set 11 케이스)

```yaml
evals:
  - path: eval/golden_set.md
    purpose: "회귀 단일 출처 — 11 케이스 (GS-001~GS-011)"
  - path: eval/video_planning_eval.md
    purpose: "8차원 critic 채점"
  - path: eval/regression_eval.md
    purpose: "회귀 실행/리포트 기준"
  - path: eval/human_review_rubric.md
    purpose: "사람 검토 5점 척도"
```

- **golden_set: 11 케이스** (GS-001~GS-011, 실측 — golden_set.md §2). P0 7(GS-001~006,010) / P1 3(GS-007~009) / P2 1(GS-011).
- **eval-run runner**: mock-deterministic primary + 실 LLM mode flag (Phase 9.5 ADR-033, 첫 정식). golden_set markdown → 구조화 파싱.
- **revise effect eval**: attempt별 canonical 0–1 delta (Phase 9.5 — Phase 4.5 D6 해소, mean_delta 0.092).
- **video_planning_eval 8차원**: intent_fit / target_clarity / hook_strength / message_clarity / structure / feasibility / brand_consistency / differentiation.
- **임계값 (eval-run §6)**: schema 준수율 100% / 평균 점수 ±0.3 / 비용 +30% / latency +20% / 차단 단어 0%.
- **이원 트랙** (eval/INDEX.md): 구현 검증(pytest/jsonschema) + 플랫폼 품질(golden_set/rubric/LLM-as-judge).

★ 실측: golden_set.md = 11 케이스 (GS-001~GS-011), v1.0.0. (entry plan 일부 "47" 기재는 Phase 9.5 에서 정정됨 — 실측 11.)

---

## 8. 현재 phase 구조 (실측 — Phase 0~9.5 done + M0 meta-phase)

```yaml
phases_done: [0, 1, 2, 3, 4, 4.5, 6, 5, 5.5, 7, 8, 9, 9.5]
phase_active: M0                   # ★ meta-phase (제품 phase 아님)
phase_next: pending_user_decision  # A Phase 10 통합 / B Phase 11+
```

- **Phase 0~9.5 done** (PHASE_REGISTRY 실측): 0 migration / 1 MVP / 2 PWA 설계 / 3 PWA 구현 / 4 FastAPI / 4.5 Critic revise / 6 Output Schema / 5 DB·Auth / 5.5 Legacy 통합 / 7 RAG Lite / 8 MOA Lite / 9 결과·피드백 / 9.5 eval-run + Critic deprecated 제거.
- **Phase M0 active** = ★ meta-phase (L3 Meta-Factory skeleton + contract + validation, 3 Slice, 런타임 0). PHASE_REGISTRY 제품 phase(10/11)와 번호 분리.
- **P-X1 47연속** (Phase 9.5 종료 baseline). Phase M0 진행 중 (Slice별 §SELF-VERIFICATION, 목표 누적 50).
- **P-X2 자동 게이트**: phase 종료 시 scenario_simulation 자동 실행 (Phase 9.5 = v6 30/30, 여덟 번째).
- **phase entry 8 files**: goals / scope / non_goals / dependencies / acceptance / assumptions / multi_slice_plan / notes.

★ 실측: PHASE_REGISTRY Phase 0~9.5 done + M0 active. P-X1 47 (Phase 9.5 종료, M0 진행 중). pytest 339 baseline.

---

## 9. 현재 강점 (실측)

1. **P-X1 §SELF-VERIFICATION 47연속 PASS** (Phase 3~9.5 누적, 0 deviation) — 모든 sub-agent 가 commit 전 forbidden 영역 0줄 자기 검증. PlanCard 35연속 / component_map 45연속 0줄.
2. **behavior-preserving 리팩토링** (Phase 8 — plans.py 659→243 god-function 분해, Envelope byte-identical, 기존 test 수정 0 = 동작 불변 증거).
3. **graceful 일관 적용** (P-GRACEFUL-001 — RAG/Critic/Rewriter/DB 실패 시 사용자 차단 0 + validation.warnings 자기설명 + 5종 marker 표준화).
4. **proposal-first 규율** — contracts 직접 편집 금지 + contract-change 절차 + meta/proposals + outputs 격리. self_improvement_loop "자동 수정 아님" 정신.
5. **contract-change / eval-run 정식화** — CC-001~005 누적 + eval-run mock-deterministic 회귀 게이트(Phase 9.5 ADR-033) + 임계값 자동 차단.
6. **multi-llm-validation formal 7회** (P-VALIDATION-FORMAL-001 — self + external 분리, 큰 phase 의무 baseline).
7. **P-X2 자동 게이트** — phase 종료 시 변경성 시뮬 자동 실행 (▼99% 시간).
8. **3계층 모델 명문화** (Phase M0 — L1 runtime / L2 harness / L3 meta_factory + factory_contract 8 규칙).

★ 실측: patterns.md P-X1-EFFECT-001 (47연속) + P-BEHAVIOR-PRESERVING-001 + P-GRACEFUL-001 + P-VALIDATION-FORMAL-001 (7회) + P-X2-EFFECT-001.

---

## 10. L3 Meta-Factory 확장 시 부족한 점 (실측 근거)

> 본 절은 L3 Meta-Factory 가 **무엇을 채워야 하는가**를 현재 하네스 실측으로 도출한다. Phase M0 는 skeleton·contract·validation 까지만 (payoff deferred) — 아래 5 부족점의 실 구현은 사용자 승인 후 다음 phase.

### 부족점 1 — 하네스 생성 자동화 없음

- **실측**: 현재 하네스는 Phase 0 migration 으로 사람이 수작업 조립. 새 도메인 하네스를 domain_brief → blueprint → validation 으로 만드는 **재현 가능한 절차/도구가 없다**.
- **L3 대응 (Phase M0)**: `generation_workflow.md` 11단계 + `domain_brief_schema` + `harness_blueprint_schema` 로 절차를 정의 (skeleton·contract 까지 — 실 도구는 NG11, 다음 phase).

### 부족점 2 — `.claude/agents` 자동 생성 없음

- **실측**: `.claude/agents/` 디렉토리 **부재** (확인됨). agent 정의는 `backend/fastapi/agents/*.py` (런타임 코드)에만 존재하고, agent scaffold 를 선언적으로 생성하는 경로가 없다.
- **L3 대응 (Phase M0)**: `templates/agent_template.md` 로 agent scaffold 형식(name/responsibility/inputs/outputs/forbidden_actions)을 정의. `.claude/agents` 자동 생성은 NG12 (다음 phase).

### 부족점 3 — trigger dry-run 테스트 부족

- **실측**: Skill 은 description 키워드 자동 트리거지만, "필요 Skill 이 켜지는가 / 켜지면 안 되는 Skill 이 안 켜지는가"를 **사전 dry-run 검증하는 절차가 부족**하다 (현재는 INDEX 충돌 규칙 + harness-audit 사후 점검에 의존).
- **L3 대응 (Phase M0)**: `validation_workflow.md` 검증 1(trigger validation) + 검증 2(skill conflict check)로 dry-run 기준을 정의. 실 dry-run 테스트 샘플은 다음 phase.

### 부족점 4 — with-skill / without-skill 비교 부족

- **실측**: Skill 추가의 효용(누락률/품질/일관성 개선)을 적용 전/후로 **정량 비교하는 절차가 부족**하다 (Skill 도입이 YAGNI 인지 검증하는 baseline 미비).
- **L3 대응 (Phase M0)**: `validation_workflow.md` 검증 4(with-without comparison) + eval-run 연동(검증 5)로 비교 기준을 정의. 실 비교 샘플은 다음 phase.

### 부족점 5 — generated_harness acceptance 기준 부족

- **실측**: 생성된(또는 새) 하네스가 "최소한 갖춰야 할 것"(최소 파일 구조 / 금지 범위 / phase 구조 / eval gate / rollback·retrospective 경로)을 **명문화한 수락 기준이 없다**.
- **L3 대응 (Phase M0)**: `validation_workflow.md` 검증 6(generated harness acceptance) + `factory_contract.md` 8 규칙으로 수락 기준을 정의.

---

## 11. validation (현재 하네스 — live)

```yaml
validation:
  trigger_validation: live          # Skill 자동 트리거 운영 중 (INDEX 충돌 0)
  contract_consistency: live        # CC-001~005 + agent-io-check 6회 회귀 PASS
  with_without_skill_eval: live      # eval-run mock-deterministic 회귀 게이트 (Phase 9.5)
```

> 신규 생성 blueprint 의 validation 3 필드는 pending 으로 시작(harness_blueprint_schema §3.4)하지만, 본 문서는 현재 active 하네스 사후 정리이므로 live 로 표기. L3 Meta-Factory 가 채울 부족점(§10)은 이 live 운영에서 관찰된 gap 이다.

---

## 12. 다음 단계

- 본 blueprint 는 신규 도메인 하네스 생성 시 참조 baseline + L3 부족점 도출 근거.
- §10 부족점 5 의 실 구현(생성 도구 / .claude/agents / trigger dry-run / with-without 비교 / acceptance 자동 점검)은 Phase M0 범위 밖 (skeleton·contract·validation 까지만, payoff deferred).
- harness-factory Skill(proposal-only) + INDEX #21 등록 = Phase M0 Slice 3.
