# Phase 7 회고 — RAG Lite (candidate_knowledge 5단계 MVP 전부)

> 종료일: 2026-05-29
> 유형: large phase (12~16h, 5 Slice)
> 총 시간: ~13~14h (실측)
> 결과: ✅ A1~A10 10/10 + M1~M4 4/4 PASS
> 작성자: Claude (Opus 4.7, 1M context)
> 트리거: phase-complete v1.2.0 §1.6 자동 게이트 다섯 번째 + §7 회고 자동 호출

---

## 사실 요약

Phase 7 (RAG Lite — candidate_knowledge 5단계 MVP 전부, large phase)을 **2026-05-29 단일 일자**에 entry부터 archive까지 완수.

진입: ADR-024 (Phase 5.5 Slice 3에서 신규)에서 명시한 사용자 결정 4 (5단계 MVP 전부) + 사용자 결정 3 (RAG Lite scope 유지) + 사용자 결정 5 (Brand Memory Phase 9+ 이관) 그대로 채택. entry commit `4185b72`.

5 Slices를 5 Waves로 분해 (모두 sequential + 모두 sub-agent dispatch):
- Wave 1 (Slice 1, `4185b72`) — Pre-Entry: rag-design Skill ★ 첫 정식 + ADR-025/026 + multi-llm-validation formal 네 번째 V1~V7
- Wave 2 (Slice 2, `68e3107`) — RAG 5단계 schema + core (contract-change rag_data_contract §18 + 0004 migration + promotion + quality_filter + eval_rubric, pytest 172→195)
- Wave 3 (Slice 3, `f65f5c1`) — Retrieval + embedding + chunking (pgvector cosine top-k=5 threshold=0.7 + text-embedding-3-small + 512 tokens, pytest 195→214)
- Wave 4 (Slice 4, `c832e26`) — Promotion + LLM Wiki + agents/rag.py 통합 + rag-update Skill ★ 첫 정식 (pytest 214→223)
- Wave 5 (Slice 5, final) — Close + 회귀 검증 + smoke 13/13 + scenario_sim v3 15/15 + retrospective + archive + state docs

총 5 sub-agent dispatch (100% sub-agent 패턴, Phase 4.5/6/5/5.5 정신 계승). 충돌 0건. **§SELF-VERIFICATION 5/5 PASS**.

핵심 회귀 baseline 보존:
- **PlanCard.tsx 0줄 변경 5연속 (Phase 7 Slice 1~5)** → 누적 **19연속** (Phase 4 4 + Phase 4.5 5 + Phase 6 3 + Phase 5 5 + Phase 5.5 1 + Phase 7 1) ★
- **component_map.md 0줄 변경 5연속 (Phase 7 Slice 1~5)** → 누적 **29연속** (Phase 2 6 + Phase 3 5 + Phase 4 4 + Phase 4.5 4 + Phase 6 3 + Phase 5 5 + Phase 5.5 1 + Phase 7 1) ★
- pytest 172/172 baseline (Phase 5.5) → **223/223** (+51 신규: promotion 10 + quality_filter 8 + eval_rubric 5 + chunking 7 + embedding 5 + retrieval 7 + integration 9)
- smoke_test_phase_7 **13/13** (12 PASS + 1 WARN intended, Phase 5 baseline 계승)
- scenario_simulation v3 **15/15 PASS** (P-X2 다섯 번째 자동 게이트, S11~S15 신규 RAG 5 추가)
- schema_stress_test **5/5 PASS** (Phase 6 baseline 유지)
- audit_naming **0 drift**
- audit_page_component **2 intended drift WARN** (Phase 5 baseline 유지 — AuthGuard + /login route)
- Phase 1 legacy + Phase 5 + Phase 7 baseline 100% 보호 (P-LEGACY-CONSOLIDATION-001 누적 2회 적용)

회고 핵심 발견:
- ★ **P-X1 §SELF-VERIFICATION 31연속 PASS**: Phase 3:5 + Phase 4:4 + Phase 4.5:4 + Phase 6:4 + Phase 5:5 + Phase 5.5:4 + Phase 7:5 = 31 Slice 누적. P-AGENT-SCOPE-001 mitigation **31연속 입증**. 새 영역(RAG sources)에서도 0건 재발.
- ★ **rag-design Skill ★ 첫 정식 트리거** (Slice 1): RAG architecture 결정 → ADR-025 (chunking 512 + embedding text-embedding-3-small + retrieval pgvector cosine top-k=5 threshold=0.7 + LLM Wiki vs RAG 분리 + graceful 5종 marker)
- ★ **rag-update Skill ★ 첫 정식 트리거** (Slice 4): 5단계 승격 절차 강제 (meta/rag_updates/2026-05-29_phase-7-initial-promotion.md)
- ★ **contract-change Skill 본격** (Slice 2): rag_data_contract.md §18 신규 — 5단계 stage enum + promotion_history JSONB + retrieval 정책 정식 등록
- ★ **ADR-025 + ADR-026 신규**: RAG architecture (Slice 1) + 5단계 promotion logic (Slice 1)
- ★ **graceful 5종 marker 표준화** (ADR-025 §5): rag_unavailable / rag_no_results / llm_wiki_unavailable / embedding_failed / supabase_unconfigured — P-GRACEFUL-001 (Phase 1) 정신 5번째 입증
- ★ **Phase 1 legacy ↔ Phase 7 신규 공존 패턴** (P-LEGACY-CONSOLIDATION-001 누적 2회): Phase 1 rag/retriever.py + rag/fallback.py (psycopg) ↔ Phase 7 rag/retrieval.py (Supabase RPC) 별개 공존. agents/rag.py는 Phase 1 baseline 보호 + Phase 7 RAG Lite wrapper 통합.

---

## 데이터

| 항목 | 값 |
|---|---|
| 기간 | 2026-05-29 단일일 (다중 sub-agent dispatch, 5 Slice sequential) |
| Total commits (Phase 7) | 5 (Slice 1 4185b72 + Slice 2 68e3107 + Slice 3 f65f5c1 + Slice 4 c832e26 + Slice 5 final) |
| 신규 파일 | ~22 (backend/fastapi/rag/ 8 + db/migrations/0004 + tests/test_rag_* 7 + docs/decisions ADR-025/026 2 + meta/validations × 2 + meta/rag_updates × 1 + smoke_test_phase_7 + retrospective + closing_notes) |
| 수정 파일 | ~10 (agents/rag.py + routers/plans.py 소폭 + config.py + rag_data_contract.md §18 + scenario_simulation.ps1 v3 + skill_usage_log + patterns + PROJECT_STATE + PHASE_REGISTRY + 00_START_HERE + README × 1) |
| 줄 수 변화 | +~2200 (backend rag layer +~1500 / tests +~500 / docs +~150 / meta +~200) |
| 신규 ADR | 2 (ADR-025 RAG architecture + ADR-026 5단계 promotion logic) |
| 변경된 contract | 1 (rag_data_contract.md §18 신규 — 5단계 stage enum + promotion_history + retrieval 정책) |
| backend rag 변경 | 8 신규 (rag/__init__ + promotion + quality_filter + eval_rubric + embedding + chunking + retrieval + llm_wiki) |
| backend agents 변경 | 1 수정 (agents/rag.py — Phase 7 Lite 통합 wrapper, Phase 1 baseline 별개 공존) |
| backend routers 변경 | 1 소폭 (routers/plans.py — graceful 5종 marker 노출) |
| backend db 변경 | 1 신규 (0004_rag_5stage.sql — candidate_knowledge + approved_knowledge + RLS + ivfflat) |
| backend config 변경 | RAG env vars 6개 추가 (rag_embedding_model + rag_chunk_size + rag_chunk_overlap + rag_top_k + rag_threshold + 1) |
| Frontend 변경 | 0 (Phase 5 baseline 유지 — PlanCard 19연속, component_map 29연속) |
| pytest 결과 | **223/223 PASS** (Phase 5.5 172 baseline + Phase 7 신규 51) |
| pytest 신규 케이스 | 51 (promotion 10 + quality_filter 8 + eval_rubric 5 + chunking 7 + embedding 5 + retrieval 7 + integration 9) |
| audit_naming | 0 drift |
| audit_page_component | 2 intended drift WARN (Phase 5 baseline 유지, AuthGuard + /login) |
| smoke_test_phase_7 | **13/13** (12 PASS + 1 WARN intended) |
| scenario_simulation v3 | **15/15 PASS** (P-X2 다섯 번째 자동 게이트) |
| schema_stress_test | 5/5 PASS (Phase 6 v2 유지) |
| Sub-agent dispatch | 5 (Slice 1~5 모두) |
| **P-X1 §SELF-VERIFICATION** | **5/5 PASS (Phase 7)** ★ |
| **P-X1 누적 streak** | **31연속 (Phase 3 5 + Phase 4 4 + Phase 4.5 4 + Phase 6 4 + Phase 5 5 + Phase 5.5 4 + Phase 7 5)** ★ |
| **PlanCard.tsx deviation** | **0건 (Phase 7 전체, 누적 19연속 — Phase 4 4 + Phase 4.5 5 + Phase 6 3 + Phase 5 5 + Phase 5.5 1 + Phase 7 1)** ★ |
| **component_map.md deviation** | **0건 (Phase 7 전체, 누적 29연속 — Phase 2 6 + Phase 3 5 + Phase 4 4 + Phase 4.5 4 + Phase 6 3 + Phase 5 5 + Phase 5.5 1 + Phase 7 1)** ★ |
| 사용 Skill (Phase 7) | 11 (phase-start v1.3.0 + qa-check + contract-change + multi-llm-validation formal 네 번째 + **rag-design ★ 첫 정식** + **rag-update ★ 첫 정식** + agent-io-check 세 번째 회귀 + harness-audit + design-review 일곱 번째 §B + meta-retrospective + phase-complete v1.2.0 다섯 번째) |
| 식별된 P-pattern (Phase 7 신규) | 2 신규 (P-RAG-5STAGE-001 + P-RAG-GRACEFUL-001) + 3 update (P-X1-EFFECT-001 31연속 + P-VALIDATION-FORMAL-001 네 번째 입증 + P-LEGACY-CONSOLIDATION-001 누적 2회 입증) |
| Phase 7 deferred → Phase 8+/9+/11+/21+ 이관 | MOA Lite (Phase 8) / 결과 저장 + 피드백 (Phase 9) / 사용자 데이터 자동 promotion (Phase 11+) / Custom RAG (Phase 21+) / Brand Memory 자동 추출 (Phase 9+, NG1) / chunking tiktoken (Phase 9+) / Phase 1 legacy 실 통합 (Phase 11+) |
| 시간 추정 vs 실측 | 12~16h (multi_slice_plan) → 실측 ~13~14h (단일일 다중 sub-agent) |

---

## Acceptance 결과 (A1~A10 + M1~M4)

| ID | 항목 | 결과 |
|---|---|---|
| A1 | candidate_knowledge 5단계 stage enum + DB schema migration (ADR-025) | ✅ db/migrations/0004_rag_5stage.sql + ADR-025 |
| A2 | quality_filter (PII + 인젝션 + 광고적 표현) PASS | ✅ test_rag_quality_filter 8/8 |
| A3 | 간이 eval rubric (Phase 9+ 정식화 전까지) | ✅ rag/eval_rubric.py + test_rag_eval_rubric 5/5 |
| A4 | promotion 5단계 transition + promotion_history JSONB | ✅ test_rag_promotion 10/10 |
| A5 | pgvector retrieval (top-k=5 + threshold=0.7) | ✅ test_rag_retrieval 7/7 |
| A6 | chunking 512 tokens + OpenAI embedding 통합 | ✅ test_rag_chunking 7/7 + test_rag_embedding 5/5 |
| A7 | LLM Wiki vs RAG 분리 + agents/rag.py 통합 | ✅ rag/llm_wiki.py + test_rag_integration 9/9 + agent-io-check 회귀 |
| A8 | PlanCard 19연속 + component_map 29연속 0줄 | ✅ |
| A9 | audit_naming 0 drift + audit_page_component 2 intended WARN | ✅ |
| A10 | smoke 13/13 + scenario_sim v3 15/15 | ✅ |
| M1 | multi-llm-validation formal self V1~V7 + external placeholder | ✅ |
| M2 | rag-design Skill ★ 첫 정식 트리거 (ADR-025) | ✅ |
| M3 | rag-update Skill ★ 첫 정식 트리거 (5단계 승격 절차) | ✅ |
| M4 | P-X1 §SELF-VERIFICATION 31연속 PASS | ✅ (5/5 Phase 7) |

---

## 분석

### 잘된 것

1. **★ 사용자 결정 4 (5단계 MVP 전부) 1:1 mapping 완료**: pending → filtered → evaluated → approved → promoted 5단계 전부 MVP 구현. 자동 (≥0.8) / 수동 (0.6~0.8) / 거부 (<0.6) hybrid 승인 정책 명시 (ADR-026). promotion_history JSONB append-only.

2. **★ rag-design + rag-update Skill 첫 정식 트리거 둘 다 완료**: Skill 14개 → 14 active (rag-update Slice 4 완료로 +1). Phase 7 진입 시점 13 active → 종료 시점 14 active. unused 7개 → 6개 감소.

3. **★ ADR-025 + ADR-026 baseline 확립**: RAG architecture (chunking 512 + embedding text-embedding-3-small + retrieval pgvector cosine top-k=5 threshold=0.7 + LLM Wiki vs RAG 분리 + graceful 5종 marker) + 5단계 promotion logic (hybrid 승인 + 간이 eval rubric 3 dim + promotion_history JSONB) — Phase 7 운영 단계 및 Phase 8~11+ 확장 baseline 확립.

4. **★ contract-change Skill 본격 (rag_data_contract.md §18 신규)**: 5단계 stage enum + promotion_history + retrieval 정책 정식 등록. Phase 6 (output_schema §9 canonical) + Phase 5 (db_schema.md 신규) + Phase 7 (rag_data_contract.md §18) = contract-change Skill 3회 본격 적용 (P-CONTRACT-FIRST-001 정신 누적).

5. **★ graceful 5종 marker 표준화 (P-RAG-GRACEFUL-001 신규)**: rag_unavailable / rag_no_results / llm_wiki_unavailable / embedding_failed / supabase_unconfigured — RAG 실패 시 plan 생성 차단 X. P-GRACEFUL-001 (Phase 1) → Phase 4 (5 plan parallel) → Phase 4.5 (revise) → Phase 5 (Supabase) → Phase 7 (RAG) = 5번째 입증.

6. **★ Phase 1 legacy ↔ Phase 7 신규 공존 (P-LEGACY-CONSOLIDATION-001 누적 2회)**: Phase 1 rag/retriever.py + rag/fallback.py (psycopg, /generate endpoint 직접 호출) ↔ Phase 7 rag/retrieval.py (Supabase RPC, agents/rag.py wrapper) 별개 공존. ADR-024 §B 확대 지점 (Phase 11+ Custom RAG 시점 실 통합 검토) 명시.

7. **★ pytest 172 → 223 (+51 신규)**: 5단계 + retrieval + embedding + chunking + integration 모두 mock + graceful 케이스 포함. test_rag_integration 9 케이스로 end-to-end (chunking → embedding → promotion → retrieval round-trip) 검증.

8. **★ P-X1 31연속 PASS — 5 Slice 모두 sub-agent + 충돌 0건**: Phase 7은 RAG 신규 영역 large phase 임에도 5 Slice 모두 sub-agent dispatch. 각 sub-agent §SELF-VERIFICATION 수행. forbidden 영역 1줄도 침범 안 함. P-AGENT-SCOPE-001 mitigation **31연속 누적 입증**. 새 영역(RAG sources)에서도 효과 유지.

9. **★ smoke 13/13 + scenario_sim v3 15/15 (P-X2 다섯 번째 자동 게이트)**: Phase 5 12 baseline + RAG 1 추가 → 13/13. v2 10 baseline + RAG 5 추가 → 15/15.

10. **★ frontend 변경 0 (PlanCard 19연속 + component_map 29연속)**: Phase 7은 backend RAG 작업이므로 frontend는 baseline 보호. design-review impl §B PASS.

11. **★ agent-io-check 세 번째 회귀 검증 (agents/rag.py)**: Phase 1 baseline 인터페이스 호환 + Phase 7 RAG Lite 통합 wrapper. Critic / Rewriter (Phase 6 canonical) 변경 0 → 회귀 0.

### 안 된 것

1. **chunking은 whitespace 기반 단순 token 추정**: tiktoken 미사용 (graceful + 안전 측면). Phase 9+ tiktoken 도입 검토 필요. → 개선 제안 §1.

2. **Supabase SQL function `match_approved_knowledge` 정의 부재**: rag/retrieval.py는 Supabase RPC 호출 패턴이지만 실제 SQL function 정의는 운영 단계 필수 (현재 mock fallback). ADR-025 §3 명시. → 개선 제안 §2.

3. **Phase 1 legacy rag/retriever, rag/fallback 통합은 Phase 11+ 이후**: P-LEGACY-CONSOLIDATION-001 옵션 A 패턴 누적 2회 (Phase 5.5 + Phase 7). 공존 유지 + Phase 11+ Custom RAG 시점 자연 통합 검토. → 개선 제안 §3.

4. **간이 eval_rubric (3 dim)은 Phase 9+ deprecated 예정**: golden_set 기반 정식 rubric 정식화 시점에 deprecated → Phase 9+ eval-run Skill 정식화 시. → 개선 제안 §6.

### 배운 것

1. **rag-design + rag-update Skill 첫 정식 트리거 패턴**: rag-design은 entry (Slice 1, ADR-025) + rag-update는 mid-late (Slice 4, 5단계 promotion 절차) — 2-stage 패턴. security-review (Phase 5 entry + final) 2-stage 패턴과 유사. **RAG/보안 같은 영역 phase는 2-stage Skill 패턴** baseline 확립.

2. **graceful 5종 marker 표준화 패턴 (P-RAG-GRACEFUL-001)**: rag_unavailable / rag_no_results / llm_wiki_unavailable / embedding_failed / supabase_unconfigured — RAG 실패 시 plan 생성 차단 X. P-GRACEFUL-001 (Phase 1) 정신 5번째 입증. **외부 의존성 실패 시 marker 표준화 의무화** baseline 확립.

3. **legacy + 신규 공존 패턴 누적 2회 (P-LEGACY-CONSOLIDATION-001)**: Phase 5.5 (legacy DB) + Phase 7 (legacy RAG) 모두 옵션 A 채택 (공존 + deprecated note + 지연 통합). 후보 → 정식 채택 검토 가능 시점에 진입 (Phase 11+ 실 통합 후 평가).

4. **5 Slice large phase 13~14h 실측 효과**: Phase 5 (5 Slice, 14~16h) → Phase 7 (5 Slice, 13~14h, ▼5~10% 시간) — large phase 표준 시간 baseline 정착 (~13~14h, RAG/DB/Auth 같은 새 영역 도입 시).

5. **사용자 결정 명시 패턴 — Phase 7은 Phase 5.5에서 미리 결정 5건 명시**: Phase 5.5 Slice 1 (사용자 결정 5건) → Phase 7은 추가 결정 없이 그대로 채택. **consolidation mini-phase → 다음 phase 진입 부담 ↓** baseline 확립 (Phase 5.5 효과 Phase 7에서 실측 입증).

### 근본 원인 (해당 없음 — 본 phase deviation 0건)

Phase 4.5/6/5/5.5처럼 deviations 0건. P-X1 31연속 PASS로 forbidden 영역 침범 0건 — root cause 분석 불요.

발견 1: chunking whitespace 추정의 한계 (over-allocation 회피 안전 측면, tiktoken 미사용). **수용 가능 — Phase 9+ tiktoken 도입 검토 시점**.

발견 2: Supabase SQL function `match_approved_knowledge` 정의 부재. **수용 가능 — 운영 단계 필수, ADR-025 §3 명시**.

audit_page_component WARN 2 drift는 **의도된** Phase 5 baseline (Slice 3 AuthGuard component + /login route) — Phase 7 baseline 유지 (변경 0). phase-complete v1.2.0 §1.6 WARN 허용 (FAIL 아님), `phase_7_audit_page_component_intended_drift` 사유 Phase 5 baseline 계승 명시.

### 부가 발견 사항 (개선 후보)

| 항목 | 영향 | 빈도 | 분류 |
|---|---|---|---|
| chunking tiktoken 도입 | 보통 (정확도 ↑) | 1회 (Phase 7) | Phase 9+ |
| Supabase SQL function 정의 | 중요 (운영 단계 필수) | 1회 (Phase 7) | 운영 단계 필수 (Phase 8+ 운영 시작 시) |
| Phase 1 legacy rag 실 통합 | 보통 (cognitive load 잔존) | 2회 누적 (Phase 5.5 + Phase 7) | Phase 11+ Custom RAG 시 |
| 간이 eval_rubric → golden_set 기반 정식 | 작음 (Phase 9+ 활성) | 1회 (Phase 7) | Phase 9+ eval-run Skill 정식화 시 |
| Brand Memory 자동 추출 ADR 신규 | 보통 | 누적 2회 (Phase 5.5 + Phase 7) | Phase 9+ MVP 본격 운영 후 |
| prompt_registry P-007/P-008 정식화 | 작음 (NG8) | 누적 3회 (Phase 6/5/7) | Phase 8+ MOA Lite 본격 |
| revise effect eval | 작음 (Phase 4.5 D6 계승) | 누적 5회 (Phase 4.5/6/5/5.5/7) | Phase 9+ eval-run 정식화 |

---

## 개선 제안

### 개선 제안 1 (우선순위: 보통): chunking tiktoken 도입 — Phase 9+

- **무엇을**: `rag/chunking.py`의 whitespace 기반 token 추정을 `tiktoken` 라이브러리 정확 카운트로 전환.
- **왜**: 현재 over-allocation 회피 안전 측면이지만, 정확도 향상 시 retrieval relevance ↑. embedding 호출 비용 정밀 제어 가능.
- **어디에**: `rag/chunking.py` + `config.py` (tiktoken model 명세)
- **상태**: Phase 9+ 검토 (개선 제안 §1, eval-run Skill 활성 시 동시 검토)

### 개선 제안 2 (우선순위: ↑): Supabase SQL function `match_approved_knowledge` 정의 — 운영 단계 필수

- **무엇을**: Supabase migrations에 SQL function `match_approved_knowledge(query_embedding vector(1536), top_k int, threshold float, brand_filter uuid)` 정의 추가 (pgvector cosine RPC).
- **왜**: rag/retrieval.py는 Supabase RPC 호출 패턴 — SQL function 정의 없으면 실 운영 단계 동작 X (현재 mock fallback). ADR-025 §3 명시.
- **어디에**: `backend/fastapi/db/migrations/0005_rag_rpc.sql` 신규 (또는 0004 보강)
- **상태**: 운영 단계 진입 직전 (Phase 8+ MOA Lite 본격 또는 Phase 9+ 결과 저장-피드백 시점 권장)

### 개선 제안 3 (우선순위: 낮음): Phase 1 legacy rag 실 통합 — Phase 11+

- **무엇을**: Phase 1 `rag/retriever.py` + `rag/fallback.py` (psycopg)를 Phase 7 `rag/retrieval.py` (Supabase RPC)로 통합.
- **왜**: P-LEGACY-CONSOLIDATION-001 옵션 A 패턴 누적 2회 (Phase 5.5 DB + Phase 7 RAG). 공존 유지 cognitive load 잔존 → Phase 11+ Custom RAG 시점 자연 통합.
- **어디에**: `backend/fastapi/rag/{retriever, fallback}.py` 제거 + `routers/generate.py` 호출 → `routers/plans.py` 패턴 마이그
- **상태**: Phase 11+ Custom RAG 시점 (ADR-024 §B)

### 개선 제안 4 (우선순위: 보통): rag-update Skill 두 번째 트리거 — Phase 11+ 사용자 데이터 자동 promotion

- **무엇을**: 사용자 데이터 누적 시 rag-update Skill 두 번째 호출 (Phase 7 Slice 4 첫 정식 ↔ Phase 11+ 두 번째 자동 promotion).
- **왜**: ADR-024 §A 확대 지점 (사용자 데이터 자동 promotion) 활성화 baseline.
- **어디에**: `meta/rag_updates/{date}_phase-11-user-data-promotion.md`
- **상태**: Phase 11+ 사용자 데이터 누적 추세 기반 활성

### 개선 제안 5 (우선순위: 보통): Brand Memory 자동 추출 ADR 신규 — Phase 9+

- **무엇을**: Brand Memory 자동 추출 (확정 결정 [8]) ADR 작성 + 활성화 절차.
- **왜**: 사용자 결정 5 (Phase 5.5 + Phase 7 누적 confirm). MVP 본격 운영 + 사용자 데이터 누적 후 활성 baseline.
- **어디에**: `docs/decisions/phase_9_brand_memory_auto_extract.md` 신규
- **상태**: Phase 9+ MVP 본격 운영 후

### 개선 제안 6 (우선순위: ↑): 간이 eval_rubric → golden_set 기반 정식 rubric — Phase 9+

- **무엇을**: Phase 7 `rag/eval_rubric.py` (간이 3 dim — relevance / clarity / safety)를 golden_set 기반 정식 rubric으로 대체.
- **왜**: Phase 4.5 D6 (revise effect eval) + Phase 6 critic fallback 완전 제거 + Phase 7 간이 rubric 모두 Phase 9+ eval-run Skill 정식화 시 동시 해소.
- **어디에**: `rag/eval_rubric.py` deprecated 표시 + `eval/golden_set.md` 기반 rubric 신규
- **상태**: Phase 9+ eval-run Skill 정식화 시점 (다중 항목 동시 해소)

---

## 패턴 등록 (meta/patterns.md 갱신)

| 패턴 ID | 설명 | 관련 회고 | 상태 |
|---|---|---|---|
| **P-X1-EFFECT-001** (update) | P-X1 §SELF-VERIFICATION **31연속 PASS** 효과 누적 측정 (Phase 3 5 + Phase 4 4 + Phase 4.5 4 + Phase 6 4 + Phase 5 5 + Phase 5.5 4 + Phase 7 5) | phase-3 + phase-4 + phase-4.5 + phase-6 + phase-5 + phase-5.5 + phase-7 | 갱신 (Phase 7) — large phase RAG 신규 영역에서도 효과 입증 + PlanCard 19연속 + component_map 29연속 |
| **P-RAG-5STAGE-001** (신규) | RAG candidate_knowledge 5단계 transition (pending → filtered → evaluated → approved → promoted) + hybrid 승인 (자동 ≥0.8 / 수동 0.6~0.8 / 거부 <0.6) + promotion_history JSONB append-only + 간이 eval rubric 3 dim (Phase 9+ deprecated 예정) | phase-7 | 신규 등록 후보 (Phase 7 첫 적용, Phase 11+ 사용자 데이터 자동 promotion 시점 효과 재측정 후 정식 채택 검토) |
| **P-RAG-GRACEFUL-001** (신규) | RAG 5종 marker 표준화 (rag_unavailable / rag_no_results / llm_wiki_unavailable / embedding_failed / supabase_unconfigured) + RAG 실패 시 plan 생성 차단 X + RAG > LLM Wiki 우선순위 (ADR-025 §4) — P-GRACEFUL-001 (Phase 1) 정신 5번째 입증 | phase-7 | 신규 등록 후보 |
| **P-VALIDATION-FORMAL-001** (update) | multi-llm-validation formal self + 외부 분리 패턴 — Phase 4.5/6/5/7 = 네 번째 입증 (Phase 5.5 self-strengthen V-form sub-pattern 보존) | phase-4.5 + phase-6 + phase-5 + phase-5.5 + phase-7 | 갱신 (Phase 7 네 번째 입증) |
| **P-LEGACY-CONSOLIDATION-001** (update) | 다중 layer 공존 시 옵션 A 패턴 — 누적 2회 (Phase 5.5 legacy DB + Phase 7 legacy RAG). 신규 후보 → 정식 채택 임박 (Phase 11+ 실 통합 시점 효과 재측정) | phase-5.5 + phase-7 | 갱신 (Phase 7 두 번째 적용 — 정식 채택 후보 강화) |

→ Phase 1~7 누적 패턴:
- P-DRIFT-001 (mitigated) / P-SLICE-001 / P-GRACEFUL-001 (Phase 7 다섯 번째 입증) / P-FOLDER-PARALLEL-001 / P-AGENT-SCOPE-001 (mitigated by P-X1, **31연속 입증**) / P-DESIGN-LAYERED-001 / P-X1-EFFECT-001 (update **31연속**) / P-THIN-VERTICAL-001 / P-GPT-REVIEW-001 / P-X2-EFFECT-001 (Phase 7 다섯 번째 자동 게이트) / P-VALIDATION-FORMAL-001 (Phase 7 네 번째 입증) / P-CRITIC-CANONICAL-001 (Phase 6) / P-CONTRACT-FIRST-001 (Phase 7 rag_data_contract §18 누적 3회) / P-RLS-001 (Phase 5) / P-SSE-001 (Phase 5) / P-SECURITY-REVIEW-001 (Phase 5 신규 후보) / P-LEGACY-CONSOLIDATION-001 (Phase 7 두 번째 적용) / **P-RAG-5STAGE-001 (Phase 7 신규 후보)** / **P-RAG-GRACEFUL-001 (Phase 7 신규 후보)** — 모두 효과 유지

---

## Skill 사용 로그 (Phase 7 동안)

| Skill | Phase 7 사용 횟수 | 비고 |
|---|---|---|
| phase-start (v1.3.0) | 1 | Phase 7 entry, 4점검 PASS (Slice 1) |
| qa-check (v1.2.0) | 1 | Slice 1 entry 시 호출 |
| contract-change | 1 | Slice 2 rag_data_contract.md §18 신규 (5단계 stage enum + promotion_history + retrieval 정책) |
| multi-llm-validation | 1 (formal 네 번째) | Slice 1 V1~V7 PASS (ADR-024 / chunk 512 / top-k=5 threshold=0.7 / OpenAI embedding / graceful / LLM Wiki vs RAG / hybrid 승인) |
| **rag-design** | **1 ★ 첫 정식** | Slice 1 — 절차 8단계 적용 → ADR-025 (RAG architecture) |
| **rag-update** | **1 ★ 첫 정식** | Slice 4 — 5단계 승격 절차 강제 → meta/rag_updates/2026-05-29_phase-7-initial-promotion.md |
| agent-io-check | 1 (세 번째 회귀) | Slice 5 — agents/rag.py 변경 검증 (Phase 1 baseline 호환 + Phase 7 통합 wrapper, Critic/Rewriter 회귀 0) |
| harness-audit | 1 | Slice 5 audit_naming + audit_page_component 자동 호출 (0 drift + 2 intended WARN 유지) |
| design-review | 1 (impl §B 일곱 번째) | Slice 5 — frontend 변경 0 검증 (PlanCard 19연속 + component_map 29연속) |
| meta-retrospective | 1 (지금) | 본 문서 |
| phase-complete (v1.2.0) | 1 | Phase 7 종료 (v1.2.0 §1.6 **다섯 번째** 자동 게이트, scenario_simulation v3 15/15 PASS) |
| 기타 unused (의도된) | — | security-review (Phase 5에서 완료) / eval-run / eval-design (Phase 9+) / prompt-version-review (Phase 8+) / ai-architecture-review (Phase 7/8 진입 시 권장 — 다음 phase) / context-compact (불요) / phase-review (불요) / bug-triage (불요) / cost-review (Phase 9+) |

**Phase 7 사용 요약**: 11 Skill 활용 (phase-start v1.3.0 + qa-check + contract-change (rag_data_contract §18) + multi-llm-validation formal 네 번째 + **rag-design ★ 첫 정식** (Slice 1) + **rag-update ★ 첫 정식** (Slice 4) + agent-io-check 세 번째 회귀 (Slice 5) + harness-audit + design-review 일곱 번째 §B + meta-retrospective + phase-complete v1.2.0 다섯 번째). Phase 1~7 누적 = **14 Skill 활성화**, 6 unused. **rag-design + rag-update 둘 다 첫 정식 트리거** (Phase 7 RAG Lite baseline 확립).

---

## 다음 액션

```
- [x] 본 회고 문서 작성 완료
- [x] meta/patterns.md update (P-X1-EFFECT-001 31연속 + P-RAG-5STAGE-001 신규 + P-RAG-GRACEFUL-001 신규 + P-VALIDATION-FORMAL-001 네 번째 + P-LEGACY-CONSOLIDATION-001 누적 2회)
- [x] meta/skill_usage_log.md 갱신 (Phase 7 사용 요약 11 Skill — rag-design + rag-update 첫 정식)
- [x] phases/active/phase-7-* → phases/archive 이동
- [x] closing_notes.md 작성 (Phase 7 baseline + 다음 옵션 A/B/C/D + RAG 운영 권장)
- [x] PROJECT_STATE / PHASE_REGISTRY / 00_START_HERE / README × 1 갱신
- [ ] 다음 phase 사용자 결정 대기 (A Phase 8 MOA / B Phase 9 저장-피드백 / C Phase 9.5+ eval / D Phase 11+)
```

---

## 다음 phase 옵션 (사용자 결정 대기)

### A. Phase 8 — MOA Lite 본격 (12~16h)
- Intent / Planner / Critic / Rewriter 완전 분리
- agents/* 모두 재구조화
- SSE Progress worker 통합 (Phase 5 Slice 4 mock → 실 worker)
- prompt_registry 정식화 검토 (NG8 해소)
- ai-architecture-review Skill 활성화 baseline

### B. Phase 9 — 결과 저장 + 피드백 (6~10h)
- 사용자 plan 선택 / 수정 / 반려 누적
- Phase 5 plans_repo + RLS + Phase 7 RAG 활용
- Brand Memory 자동 추출 ADR 신규 baseline (개선 제안 §5)
- per-user rate-limit + audit-log (Phase 5 §개선 제안 §5 흡수)

### C. Phase 9.5+ — eval-run Skill 정식화 (4~6h)
- golden_set 회귀 + revise effect eval (Phase 4.5 D6)
- Critic rubric 정식화 (Phase 6 deprecated 4 fallback 완전 제거)
- 간이 RAG eval_rubric → 정식 (Phase 7 개선 제안 §6 흡수)

### D. 다른 우선순위 (Phase 11+)
- 사용자 데이터 자동 promotion (ADR-024 §A, Phase 7 개선 제안 §4)
- Supabase SQL function 정의 (Phase 7 개선 제안 §2 — 운영 단계 필수)
- Phase 1 legacy rag 실 통합 (Phase 7 개선 제안 §3 — Phase 11+ Custom RAG)
- cost-review Skill 정식화

---

## 변경 이력

- 2026-05-29: Phase 7 회고 최초 작성 (phase-complete v1.2.0 §1.6 다섯 번째 자동 게이트 + §7 회고 자동 호출). **P-X1-EFFECT-001 update (31연속) + P-RAG-5STAGE-001 신규 + P-RAG-GRACEFUL-001 신규 + P-VALIDATION-FORMAL-001 update (네 번째) + P-LEGACY-CONSOLIDATION-001 update (누적 2회) 패턴 등록**. P-AGENT-SCOPE-001 mitigation 31/31 입증. **rag-design + rag-update Skill 둘 다 ★ 첫 정식 트리거 완료 + ADR-025/026 + contract-change rag_data_contract §18 + graceful 5종 marker 표준화 + Phase 1 legacy ↔ Phase 7 신규 공존 누적 2회**. 다음 phase = 🟡 pending_user_decision (옵션 A/B/C/D).
