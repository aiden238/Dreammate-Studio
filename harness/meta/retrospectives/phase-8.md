# Phase 8 회고 — MOA Lite 본격 (orchestrator 추출 + SSE worker + prompt_registry 정식화)

> 종료일: 2026-05-29
> 유형: large phase (12~16h, 5 Slice)
> 총 시간: ~12~14h (실측)
> 결과: ✅ A1~A10 10/10 + M1~M5 5/5 PASS
> 작성자: Claude (Opus 4.8, 1M context)
> 트리거: phase-complete v1.2.0 §1.6 자동 게이트 여섯 번째 + §7 회고 자동 호출

---

## 사실 요약

Phase 8 (MOA Lite 본격 — orchestrator 추출 + SSE worker 통합 + prompt_registry 정식화, large phase)을 **2026-05-29 단일 일자**에 entry부터 archive까지 완수.

진입: ADR-024 (Phase 5.5) §확대 지점 + Phase 7 회고 §개선 제안 (NG8 prompt_registry P-007/P-008 정식화 누적 3회 defer 해소) + 사용자 결정 3건 (Scope 3개 모두 / Critic conservative adapter / SSE progress_store 브릿지). entry commit `8fbb645`.

5 Slices를 5 Waves로 분해 (모두 sequential + 모두 sub-agent dispatch):
- Wave 1 (Slice 1, `8fbb645`) — Pre-Entry: ai-architecture-review Skill ★ 첫 정식 + prompt-version-review Skill ★ 첫 정식(분석) + ADR-027/028/029 + multi-llm-validation formal 다섯 번째 V1~V7
- Wave 2 (Slice 2, `c25367a`) — MOA Orchestrator 추출 (behavior-preserving) + ProgressSink: `orchestration/{__init__, responses, progress_sink, moa_orchestrator}.py` 신규 + plans.py thin adapter화 (god-function 분해) + test_moa_orchestrator.py
- Wave 3 (Slice 3, `f5c534a`) — SSE Progress worker 통합: `orchestration/progress_store.py` 신규 + StoreProgressSink 완성 + plans.py sink 주입 + sse.py 실 stage read (graceful fallback) + test_sse_integration.py
- Wave 4 (Slice 4, `c7c7376`) — prompt_registry 정식화: contract-change (prompt_registry.md P-001~P-008 + AUX semver + agent_io_contract.md §5 Critic v1.1.0 adapter) + critic.py v1.0.0→v1.1.0 + normalize_to_canonical helper + test_prompt_registry_consistency.py (CC-003)
- Wave 5 (Slice 5, final) — Close + 회귀 검증 + smoke 14/14 + scenario_sim v4 20/20 + retrospective + archive + state docs

총 5 sub-agent dispatch (100% sub-agent 패턴, Phase 4.5/6/5/5.5/7 정신 계승). 충돌 0건. **§SELF-VERIFICATION 5/5 PASS**.

핵심 회귀 baseline 보존:
- **PlanCard.tsx 0줄 변경 5연속 (Phase 8 Slice 1~5)** → 누적 **24연속** (Phase 4 4 + Phase 4.5 5 + Phase 6 3 + Phase 5 5 + Phase 5.5 1 + Phase 7 1 + Phase 8 5) ★
- **component_map.md 0줄 변경 5연속 (Phase 8 Slice 1~5)** → 누적 **34연속** (Phase 2 6 + Phase 3 5 + Phase 4 4 + Phase 4.5 4 + Phase 6 3 + Phase 5 5 + Phase 5.5 1 + Phase 7 1 + Phase 8 5) ★
- pytest 223/223 baseline (Phase 7) → **249/249** (+26 신규: test_moa_orchestrator + test_sse_integration + test_prompt_registry_consistency, 기존 223 중 의도된 2 version assertion 외 수정 0)
- smoke_test_phase_8 **14/14** (13 PASS + 1 WARN intended, Phase 7 13 baseline + MOA orchestrator/SSE integration/prompt_registry consistency 1 통합 step 추가)
- scenario_simulation v4 **20/20 PASS** (P-X2 여섯 번째 자동 게이트, S16~S20 신규 MOA 5 추가)
- schema_stress_test **5/5 PASS** (Phase 6 baseline 유지)
- audit_naming **0 drift**
- audit_page_component **2 intended drift WARN** (Phase 5 baseline 계승 — AuthGuard + /login route)
- Phase 1~7 baseline 100% 보호 (behavior-preserving — Envelope byte-identical)

회고 핵심 발견:
- ★ **P-X1 §SELF-VERIFICATION 36연속 PASS**: Phase 3:5 + Phase 4:4 + Phase 4.5:4 + Phase 6:4 + Phase 5:5 + Phase 5.5:4 + Phase 7:5 + Phase 8:5 = 36 Slice 누적. P-AGENT-SCOPE-001 mitigation **36연속 입증**. agents/* 전면 재구조화 위험 영역(Phase 8 진입 시 재발 위험 ↑로 표기) 임에도 0건 재발 — orchestration/ 신규 폴더로 격리하여 baseline test 수정 0 (의도된 2 version assertion 제외).
- ★ **MOA Orchestrator 추출 (ADR-027)**: `plans_generate()` god-function의 MOA orchestration(Intent→RAG→3-plan→Critic+revise→save→Envelope)을 `orchestration/moa_orchestrator.py::generate_plan()`로 추출. plans.py LOC ▼ (659줄 인라인 → 243줄 thin adapter — god-function 분해). late-import monkeypatch honor 패턴으로 기존 test mock 호환 유지.
- ★ **behavior-preserving (P-BEHAVIOR-PRESERVING-001 신규)**: orchestrator 추출 = Envelope byte-identical + 기존 pytest 223 수정 0 (의도된 contract 변경 = Slice 4 Critic v1.1.0 version assertion 정확히 2건 격리 제외). **기존 test 수정 0 = 동작 불변 증거** — refactor 정당성 입증.
- ★ **ProgressSink + progress_store 브릿지 (ADR-028)**: `ProgressSink` Protocol + `NullProgressSink`(no-op default 회귀 0) + `StoreProgressSink`(in-memory progress_store record). orchestrator가 stage별 emit, sse.py가 progress_store read (graceful fallback → store 비면 기존 mock 4단계). background task 미도입 (moa_policy §4 sync, full async Phase 11+).
- ★ **prompt_registry semver 정식화 (ADR-029, CC-003)**: P-001~P-008 + P-AUX-1/2 + P-EVAL-1 각 semver/활성 정책 명시 + prompt_id/version 단일 출처 정합. **Critic v1.1.0 conservative adapter** — P-007 prompt(0–5) 유지 + 코드-side `normalize_to_canonical` helper(0–5→0–1) 추가 + Phase 6 canonical(0–1, ADR-018) 불변 + deprecated 병행. helper는 additive (run_critic 미강제 → 회귀 0).
- ★ **ai-architecture-review + prompt-version-review Skill 둘 다 ★ 첫 정식 트리거**: Skill 14 active → **16 active** (Phase 8 종료). ai-architecture-review = MOA orchestration 설계 검토 (Slice 1 ADR-027 + Slice 5 회고 두 번째). prompt-version-review = P-007 semver 분석(Slice 1) + 적용(Slice 4).

---

## 데이터

| 항목 | 값 |
|---|---|
| 기간 | 2026-05-29 단일일 (다중 sub-agent dispatch, 5 Slice sequential) |
| Total commits (Phase 8) | 5 (Slice 1 8fbb645 + Slice 2 c25367a + Slice 3 f5c534a + Slice 4 c7c7376 + Slice 5 final) |
| 신규 파일 | ~13 (backend/fastapi/orchestration/ 5: __init__/responses/progress_sink/moa_orchestrator/progress_store + tests 3: test_moa_orchestrator/test_sse_integration/test_prompt_registry_consistency + docs/decisions ADR-027/028/029 3 + meta/validations × 2 + smoke_test_phase_8 + retrospective + closing_notes) |
| 수정 파일 | ~10 (routers/plans.py thin adapter + routers/sse.py 실 stage read + agents/critic.py v1.1.0 + prompt_registry.md + agent_io_contract.md + moa_policy.md + scenario_simulation.ps1 v4 + test_critic.py(version assert) + test_e2e_slice1.py(version assert) + state docs) |
| 줄 수 변화 | +~1900 (backend orchestration +~700 / tests +~600 / docs ADR +~250 / contracts +~150 / meta +~200) |
| 신규 ADR | 3 (ADR-027 MOA orchestrator behavior-preserving + ADR-028 SSE progress integration + ADR-029 prompt_registry semver) |
| 변경된 contract | 2 (prompt_registry.md semver 정식화 + agent_io_contract.md v1.2.0 §5 Critic v1.1.0 adapter + §8 orchestrator 중개) — CC-003 |
| backend orchestration 변경 | 5 신규 (__init__ + responses + progress_sink + moa_orchestrator + progress_store) |
| backend routers 변경 | 2 수정 (plans.py thin adapter + StoreProgressSink 주입 / sse.py 실 stage read + graceful fallback) |
| backend agents 변경 | 1 수정 (agents/critic.py — PROMPT_VERSION v1.1.0 + normalize_to_canonical helper, run_critic 미강제 → 회귀 0) |
| Frontend 변경 | 0 (Phase 5 baseline 유지 — PlanCard 24연속, component_map 34연속) |
| pytest 결과 | **249/249 PASS** (Phase 7 223 baseline + Phase 8 신규 26) |
| pytest 신규 케이스 | 26 (test_moa_orchestrator + test_sse_integration + test_prompt_registry_consistency 통합 26) |
| 기존 pytest 수정 | 2 (test_critic.py:93 + test_e2e_slice1.py:172 — Critic v1.1.0 version-string assertion, Phase 6 Rewriter 선례 — 의도된 contract delta) |
| plans.py LOC | 659 (god-function 인라인) → **243** (thin adapter, god-function 분해) |
| audit_naming | 0 drift |
| audit_page_component | 2 intended drift WARN (Phase 5 baseline 계승, AuthGuard + /login) |
| smoke_test_phase_8 | **14/14** (13 PASS + 1 WARN intended) |
| scenario_simulation v4 | **20/20 PASS** (P-X2 여섯 번째 자동 게이트) |
| schema_stress_test | 5/5 PASS (Phase 6 v2 유지) |
| Sub-agent dispatch | 5 (Slice 1~5 모두) |
| **P-X1 §SELF-VERIFICATION** | **5/5 PASS (Phase 8)** ★ |
| **P-X1 누적 streak** | **36연속 (Phase 3 5 + Phase 4 4 + Phase 4.5 4 + Phase 6 4 + Phase 5 5 + Phase 5.5 4 + Phase 7 5 + Phase 8 5)** ★ |
| **PlanCard.tsx deviation** | **0건 (Phase 8 전체, 누적 24연속 — Phase 4 4 + Phase 4.5 5 + Phase 6 3 + Phase 5 5 + Phase 5.5 1 + Phase 7 1 + Phase 8 5)** ★ |
| **component_map.md deviation** | **0건 (Phase 8 전체, 누적 34연속 — Phase 2 6 + Phase 3 5 + Phase 4 4 + Phase 4.5 4 + Phase 6 3 + Phase 5 5 + Phase 5.5 1 + Phase 7 1 + Phase 8 5)** ★ |
| 사용 Skill (Phase 8) | 10 (phase-start v1.3.0 열 번째 + qa-check + multi-llm-validation formal 다섯 번째 + **ai-architecture-review ★ 첫 정식** + **prompt-version-review ★ 첫 정식** + contract-change CC-003 + agent-io-check 네 번째 + harness-audit + design-review 여덟 번째 §B + meta-retrospective + phase-complete v1.2.0 여섯 번째) |
| 식별된 P-pattern (Phase 8 신규) | 2 신규 (P-MOA-ORCHESTRATOR-001 + P-BEHAVIOR-PRESERVING-001) + 2 update (P-X1-EFFECT-001 36연속 + P-VALIDATION-FORMAL-001 다섯 번째 입증) |
| Phase 8 deferred → Phase 9+/11+ 이관 | normalize_to_canonical wiring (Phase 9+) / SSE full async worker (Phase 11+) / prompt A/B 실행 (Phase 11+) / Critic deprecated fallback 완전 제거 (Phase 9+ eval-run) / 결과 저장 + 피드백 (Phase 9) / multi-provider prompt (Phase 21+) |
| 시간 추정 vs 실측 | 12~16h (multi_slice_plan) → 실측 ~12~14h (단일일 다중 sub-agent) |

---

## Acceptance 결과 (A1~A10 + M1~M5)

| ID | 항목 | 결과 |
|---|---|---|
| A1 | MOA Orchestrator 추출 — `orchestration/moa_orchestrator.py::generate_plan()` 존재 | ✅ test_moa_orchestrator.py |
| A2 | router thin adapter화 — plans_generate() orchestrator 호출 (god-function 분해) | ✅ plans.py 659→243 LOC + orchestrator 위임 |
| A3 | Behavior-preserving — 기존 pytest 223 수정 없이 PASS + Envelope byte-identical | ✅ (의도된 2 version assertion 격리 제외, 회귀 0) |
| A4 | ProgressSink 인터페이스 — orchestrator stage별 emit (Null default 회귀 0) | ✅ test_moa_orchestrator.py::progress_sink |
| A5 | progress_store 브릿지 — in-memory graceful store | ✅ test_sse_integration.py |
| A6 | SSE 실 stage read — sse.py가 progress_store 읽음 + graceful fallback | ✅ test_sse_integration.py + 기존 test_sse 유지 |
| A7 | prompt_registry semver 정식화 + Critic v1.1.0 adapter + 상수 정합 | ✅ test_prompt_registry_consistency.py + agent-io-check drift 0 |
| A8 | PlanCard.tsx 0줄 + component_map.md 0줄 (backend-only) | ✅ (PlanCard 24연속 + component_map 34연속) |
| A9 | audit_naming 0 drift + audit_page_component 2 intended WARN 유지 | ✅ |
| A10 | smoke_test_phase_8 14/14 PASS + scenario_sim v4 20/20 PASS | ✅ (smoke 13 PASS + 1 WARN intended) |
| M1 | multi-llm-validation formal self V1~V7 + external placeholder (다섯 번째) | ✅ |
| M2 | ai-architecture-review Skill ★ 첫 정식 트리거 (MOA orchestration, ADR-027) | ✅ |
| M3 | prompt-version-review Skill ★ 첫 정식 트리거 (P-007 semver, ADR-029) | ✅ |
| M4 | P-X1 §SELF-VERIFICATION 36연속 PASS (Slice 1~5 모두) | ✅ (5/5 Phase 8) |
| M5 | contract-change Skill (agent_io_contract + prompt_registry) — Slice 4 | ✅ CC-003 |

---

## 분석

### 잘된 것

1. **★ MOA Orchestrator 추출 (ADR-027) — god-function 분해 완료**: `plans_generate()` 659줄 인라인 god-function의 MOA orchestration(Intent→RAG→3-plan→Critic+revise→save→Envelope)을 `orchestration/moa_orchestrator.py::generate_plan()`로 서비스 레이어 추출. plans.py는 243줄 thin adapter (`return await generate_plan(...)`). moa_policy §2 "오케스트레이터가 항상 중개" 정합 회복 (router 인라인 위반 해소).

2. **★ behavior-preserving (P-BEHAVIOR-PRESERVING-001 신규) — 기존 test 수정 0 = 동작 불변 증거**: orchestrator 추출은 동작 보존 리팩터 — Envelope byte-identical. 기존 pytest 223 중 의도된 contract 변경(Slice 4 Critic v1.1.0 version assertion 정확히 2건)만 격리하고 나머지 전부 수정 0 PASS. test 수정 필요 = 재작업 신호인데 발생 0건. **refactor 정당성을 test diff 0으로 입증.**

3. **★ ProgressSink + progress_store 브릿지 (ADR-028)**: `ProgressSink` Protocol + `NullProgressSink`(no-op default → 회귀 0) + `StoreProgressSink`(progress_store record). orchestrator stage별 emit + sse.py가 progress_store read + graceful fallback(store 비면 기존 mock 4단계 → 기존 test_sse 보존). background task 미도입 (moa_policy §4 sync, full async Phase 11+). Phase 5 SSE mock asyncio.sleep → 실 stage 반영 (확정 결정 [10] 실 구현).

4. **★ prompt_registry semver 정식화 (ADR-029, CC-003) — NG8 누적 3회 defer 해소**: P-001~P-008 + P-AUX-1/2 + P-EVAL-1 각 semver/활성 정책 명시 + prompt_id/version 단일 출처 정합. Phase 6/5/7 누적 3회 deferred 되던 prompt_registry P-007/P-008 정식화를 Phase 8에서 해소. contract-change Skill 본격 네 번째 (CC-003).

5. **★ Critic v1.1.0 conservative adapter — Phase 6 canonical(ADR-018) 불변**: 사용자 결정 (conservative adapter) 정확 구현 — P-007 prompt(0–5) 유지 + 코드-side `normalize_to_canonical` helper(dimensions=scores/5.0, overall_score=avg/5.0) 추가 + Phase 6 canonical(0–1) 불변 + deprecated 0–5 병행. helper는 additive (run_critic 반환에 강제 주입 X → 출력 의미 불변, 회귀 0). PROMPT_VERSION v1.0.0→v1.1.0 minor (output schema 불변, 내부 표현 개선).

6. **★ ai-architecture-review + prompt-version-review Skill 둘 다 ★ 첫 정식 트리거**: Skill 14 active → 16 active (Phase 8 종료). ai-architecture-review = MOA orchestration 설계 검토 (Slice 1 — 4 agent 분리 + orchestrator 중개 + cost/fallback policy 정합 → ADR-027 + Slice 5 회고 두 번째). prompt-version-review = P-007 Critic 0–5↔0–1 drift 분석 + semver 계획 (Slice 1) → 적용 (Slice 4). Phase 7 (rag-design + rag-update) 정신 계승 — 영역별 Skill 첫 정식 baseline 확립.

7. **★ pytest 223 → 249 (+26 신규)**: test_moa_orchestrator (generate_plan 기본 + ProgressSink emit + NullProgressSink 회귀 0 + 에러 경로 보존) + test_sse_integration (progress_store record→sse read round-trip + graceful fallback + clear on complete) + test_prompt_registry_consistency (상수↔registry 매핑 정합 + normalize_to_canonical 0–5→0–1 + registry 문서화 검증) 모두 mock + graceful 케이스 포함.

8. **★ P-X1 36연속 PASS — 5 Slice 모두 sub-agent + 충돌 0건**: Phase 8은 agents/* 재구조화 위험 영역 large phase 임에도 5 Slice 모두 sub-agent dispatch. orchestration/ 신규 폴더로 격리하여 baseline 침범 0. P-AGENT-SCOPE-001 mitigation **36연속 누적 입증**. Phase 7 회고가 "Phase 8 재발 위험 ↑"로 표기한 영역에서도 효과 유지.

9. **★ smoke 14/14 + scenario_sim v4 20/20 (P-X2 여섯 번째 자동 게이트)**: Phase 7 13 baseline + MOA orchestrator/SSE integration/prompt_registry consistency 통합 step → 14/14 (13 PASS + 1 WARN intended). v3 15 baseline + MOA 5 (S16~S20) 추가 → 20/20.

10. **★ frontend 변경 0 (PlanCard 24연속 + component_map 34연속)**: Phase 8은 backend-only orchestration 작업이므로 frontend는 baseline 보호. design-review impl §B PASS.

### 안 된 것

1. **normalize_to_canonical helper는 wiring 미연결**: `run_critic` 반환에 강제 주입 X (additive, 회귀 0 우선). 실 canonical 우선순위 wiring은 Phase 9+ (결과 저장 시점 select_best_plan_index 통합 검토). → 개선 제안 §1.

2. **SSE progress_store는 single-process in-memory**: graceful best-effort. background task 미도입 (moa_policy §4 sync). multi-worker / multi-client broadcast는 Phase 11+ full async worker 시점. → 개선 제안 §2.

3. **prompt A/B 실행 인프라 미구현**: prompt_registry semver는 정식화했으나 A/B 단계적 활성화(10%→50%→100%) 실행은 Phase 11+ multi-provider 대비 시점. → 개선 제안 §3.

4. **Critic deprecated 0–5 fallback 잔존**: conservative adapter로 0–5 병행 유지 (회귀 0 우선). 완전 제거는 Phase 9+ eval-run 정식화 후 (Phase 6 ADR-018 다음 단계 누적). → 개선 제안 §4.

### 배운 것

1. **god-function → service layer 추출 패턴 (P-MOA-ORCHESTRATOR-001)**: 신규 폴더(orchestration/)로 격리 + late-import monkeypatch honor(기존 test mock 호환) + ProgressSink Null default(회귀 0) 3종 조합으로 behavior-preserving 추출 baseline 확립. agents/* 재구조화 위험 영역도 baseline 침범 0.

2. **behavior-preserving refactor의 test diff 0 증거 (P-BEHAVIOR-PRESERVING-001)**: 동작 보존 리팩터의 정당성은 "기존 test 수정 0"으로 입증된다. 의도된 contract 변경(version assertion)만 최소 assertion으로 격리하고 나머지 전부 보존 — Phase 6 Rewriter v1.1.0 선례(정확히 2 baseline assertion delta)와 동일 패턴.

3. **conservative adapter 패턴 (additive helper)**: 기존 canonical 불변 + LLM-facing prompt 불변 + 코드-side 정규화 helper additive(강제 주입 X) → 회귀 0 + 의미 불변 동시 달성. P-CRITIC-CANONICAL-001 (Phase 6) 정신 계승 — 즉시 제거 risk 회피.

4. **영역별 Skill 첫 정식 트리거 패턴 누적**: Phase 5 security-review (2-trigger entry+final) + Phase 7 rag-design/rag-update (entry+mid) + Phase 8 ai-architecture-review/prompt-version-review (entry 분석 + Slice 4/5 적용). 큰 phase는 영역 특화 Skill 첫 정식 + ADR 통합 패턴 정착.

5. **large phase 12~14h 실측 효과 누적**: Phase 5 (~14~16h) → Phase 7 (~13~14h) → Phase 8 (~12~14h). large phase 표준 시간 baseline 정착 (~12~14h). orchestration 추출 같은 refactor-heavy phase도 동일 범위.

### 근본 원인 (해당 없음 — 본 phase deviation 0건)

Phase 4.5/6/5/5.5/7처럼 deviations 0건. P-X1 36연속 PASS로 forbidden 영역 침범 0건 — root cause 분석 불요.

발견 1 (Slice 1 Gap 정정): entry 가정 "run_critic 이미 canonical 산출" → 실측: `run_critic`은 0–5 deprecated 형식만 산출, canonical은 `CriticEvaluation` Optional 수용 + `select_best_plan_index`에서만 canonical 우선. **conservative adapter 필요성 정당화 강화** — Slice 4에서 `normalize_to_canonical` helper 추가 (additive, run_critic 미강제 → 회귀 0). ADR-029 §Amendment 반영. **수용 가능 — 의도된 delta.**

발견 2 (의도 delta): baseline 2 version pin (test_critic:93 + test_e2e_slice1:172) — Critic v1.1.0 version-string assertion 갱신. Phase 6 Rewriter v1.1.0 선례와 동일 (정확히 2 baseline assertion delta). **behavior-preserving 예외 = 의도된 contract 변경만 최소 assertion 격리.**

audit_page_component WARN 2 drift는 **의도된** Phase 5 baseline (Slice 3 AuthGuard component + /login route) — Phase 8 baseline 계승 (변경 0). phase-complete v1.2.0 §1.6 WARN 허용 (FAIL 아님), `phase_8_audit_page_component_intended_drift` 사유 Phase 5 baseline 계승 명시.

### 부가 발견 사항 (개선 후보)

| 항목 | 영향 | 빈도 | 분류 |
|---|---|---|---|
| normalize_to_canonical wiring 연결 | 보통 (canonical 우선순위 실 활성) | 1회 (Phase 8) | Phase 9+ (결과 저장 시점) |
| SSE full async worker | 보통 (multi-worker/broadcast) | 누적 2회 (Phase 5 + Phase 8) | Phase 11+ |
| prompt A/B 실행 인프라 | 작음 (semver 정식화 완료) | 1회 (Phase 8) | Phase 11+ multi-provider |
| Critic deprecated 0–5 fallback 완전 제거 | 작음 (회귀 0 우선) | 누적 2회 (Phase 6 + Phase 8) | Phase 9+ eval-run |
| revise effect eval | 작음 (Phase 4.5 D6 계승) | 누적 6회 (Phase 4.5/6/5/5.5/7/8) | Phase 9+ eval-run |
| Brand Memory 자동 추출 ADR 신규 | 보통 | 누적 3회 (Phase 5.5 + Phase 7 + Phase 8) | Phase 9+ MVP 본격 운영 후 |

---

## 개선 제안

### 개선 제안 1 (우선순위: 보통): normalize_to_canonical wiring 연결 — Phase 9+

- **무엇을**: `agents/critic.py::normalize_to_canonical` helper를 `run_critic` 반환 또는 `select_best_plan_index` canonical 우선순위에 실 wiring.
- **왜**: 현재 additive helper로 회귀 0 우선 (강제 주입 X). 결과 저장 시점에 canonical 0–1 우선순위 실 활성 필요.
- **어디에**: `backend/fastapi/agents/critic.py` + `orchestration/moa_orchestrator.py` (Critic 호출 지점)
- **상태**: Phase 9+ 결과 저장 + 피드백 시점 (Critic deprecated 제거와 동시 검토)

### 개선 제안 2 (우선순위: 보통): SSE full async worker — Phase 11+

- **무엇을**: in-memory single-process progress_store → background task / 외부 store (Redis 등) + multi-worker / multi-client broadcast.
- **왜**: 현재 graceful best-effort (moa_policy §4 sync). 운영 단계 multi-worker 환경 / 한 plan 여러 device 동시 표시 시 필수.
- **어디에**: `backend/fastapi/orchestration/progress_store.py` + `routers/sse.py` (ADR-028 §full async Phase 11+)
- **상태**: Phase 11+ (Phase 5 SSE 개선 제안 §4 누적 2회 — full async 시점)

### 개선 제안 3 (우선순위: 낮음): prompt A/B 실행 인프라 — Phase 11+

- **무엇을**: prompt_registry semver 기반 A/B 단계적 활성화(major 시 10%→50%→100%) 실행 인프라.
- **왜**: Phase 8에서 semver 정식화 완료 (baseline). A/B 실행은 multi-provider 대비 시점 (확정 결정 [20]).
- **어디에**: `ai_system/prompts/prompt_registry.md` §활성 정책 + 실행 layer 신규
- **상태**: Phase 11+ multi-provider 대비 (prompt-version-review Skill 두 번째 트리거)

### 개선 제안 4 (우선순위: ↑): Critic deprecated 0–5 fallback 완전 제거 — Phase 9+

- **무엇을**: Critic conservative adapter의 deprecated 0–5 병행 fallback 완전 제거 + normalize_to_canonical canonical 단일화.
- **왜**: Phase 6 ADR-018 (canonical + deprecated 단계적 축소) 다음 단계 누적 2회 (Phase 6 + Phase 8). eval-run 정식화 후 deprecated 3 + 0–5 모두 제거.
- **어디에**: `backend/fastapi/agents/critic.py` + `output_schema.md §9` + 별도 contract-change 절차
- **상태**: Phase 9+ eval-run Skill 정식화 시점 (Phase 4.5 D6 revise effect eval + 간이 RAG eval_rubric 정식화와 동시 해소)

### 개선 제안 5 (우선순위: 보통): Brand Memory 자동 추출 ADR 신규 — Phase 9+

- **무엇을**: Brand Memory 자동 추출 (확정 결정 [8]) ADR 작성 + 활성화 절차.
- **왜**: 사용자 결정 5 (Phase 5.5 + Phase 7 + Phase 8 누적 3회 confirm). MVP 본격 운영 + 사용자 데이터 누적 후 활성.
- **어디에**: `docs/decisions/phase_9_brand_memory_auto_extract.md` 신규
- **상태**: Phase 9+ MVP 본격 운영 후 (결과 저장 + 피드백 phase)

### 개선 제안 6 (우선순위: 보통): revise effect eval 정식화 — Phase 9+

- **무엇을**: Critic revise loop의 effect (revise 전후 품질 개선폭) 정식 eval.
- **왜**: Phase 4.5 D6 deferred 누적 6회 (Phase 4.5/6/5/5.5/7/8). eval-run Skill 정식화 시점 동시 해소.
- **어디에**: `eval/golden_set.md` 기반 revise effect rubric + eval-run Skill
- **상태**: Phase 9+ eval-run Skill 정식화 시점 (다중 항목 동시 해소)

---

## 패턴 등록 (meta/patterns.md 갱신)

| 패턴 ID | 설명 | 관련 회고 | 상태 |
|---|---|---|---|
| **P-X1-EFFECT-001** (update) | P-X1 §SELF-VERIFICATION **36연속 PASS** 효과 누적 측정 (Phase 3 5 + Phase 4 4 + Phase 4.5 4 + Phase 6 4 + Phase 5 5 + Phase 5.5 4 + Phase 7 5 + Phase 8 5) | phase-3 + ... + phase-8 | 갱신 (Phase 8) — agents/* 재구조화 위험 영역에서도 효과 입증 + PlanCard 24연속 + component_map 34연속 |
| **P-MOA-ORCHESTRATOR-001** (신규) | god-function → service layer 추출 (신규 폴더 격리 + late-import monkeypatch honor + ProgressSink Null default) — plans.py 659→243 god-function 분해 (Envelope byte-identical) | phase-8 | 신규 등록 후보 (Phase 8 첫 적용, Phase 9+ orchestration 확장 시점 효과 재측정 후 정식 채택 검토) |
| **P-BEHAVIOR-PRESERVING-001** (신규) | behavior-preserving refactor 정당성 = 기존 test 수정 0 (동작 불변 증거) + 의도된 contract 변경만 최소 assertion 격리 (Phase 6 Rewriter / Phase 8 Critic version pin 정확히 2건) | phase-8 | 신규 등록 후보 |
| **P-VALIDATION-FORMAL-001** (update) | multi-llm-validation formal self + 외부 분리 패턴 — Phase 4.5/6/5/7/8 = 다섯 번째 입증 (Phase 5.5 self-strengthen V-form sub-pattern 보존) | phase-4.5 + ... + phase-8 | 갱신 (Phase 8 다섯 번째 입증 — V7 MOA orchestration) |

→ Phase 1~8 누적 패턴:
- P-DRIFT-001 (mitigated) / P-SLICE-001 / P-GRACEFUL-001 / P-FOLDER-PARALLEL-001 / P-AGENT-SCOPE-001 (mitigated by P-X1, **36연속 입증**) / P-DESIGN-LAYERED-001 / P-X1-EFFECT-001 (update **36연속**) / P-THIN-VERTICAL-001 / P-GPT-REVIEW-001 / P-X2-EFFECT-001 (Phase 8 여섯 번째 자동 게이트) / P-VALIDATION-FORMAL-001 (Phase 8 다섯 번째 입증) / P-CRITIC-CANONICAL-001 (Phase 6 → Phase 8 conservative adapter 계승) / P-CONTRACT-FIRST-001 (Phase 8 CC-003 누적 4회) / P-RLS-001 / P-SSE-001 (Phase 8 progress_store 실 stage 통합) / P-SECURITY-REVIEW-001 / P-LEGACY-CONSOLIDATION-001 / P-RAG-5STAGE-001 / P-RAG-GRACEFUL-001 / **P-MOA-ORCHESTRATOR-001 (Phase 8 신규 후보)** / **P-BEHAVIOR-PRESERVING-001 (Phase 8 신규 후보)** — 모두 효과 유지

---

## Skill 사용 로그 (Phase 8 동안)

| Skill | Phase 8 사용 횟수 | 비고 |
|---|---|---|
| phase-start (v1.3.0) | 1 | Phase 8 entry, 4점검 PASS (Slice 1) — 누적 10번째 |
| qa-check (v1.2.0) | 1 | Slice 1 entry 시 호출 |
| multi-llm-validation | 1 (formal 다섯 번째) | Slice 1 V1~V7 PASS (orchestrator 추출 behavior-preserving / ProgressSink Null default / SSE progress_store 브릿지 / Critic conservative adapter / prompt semver / 단일 출처 정합 / SSE best-effort) |
| **ai-architecture-review** | **1 ★ 첫 정식** | Slice 1 — MOA orchestration 설계 검토 (4 agent 분리 + orchestrator 중개 moa_policy §2 정합 + cost/fallback policy 보존) → ADR-027. Slice 5 회고 검토 (두 번째 사용, 구조 PASS) |
| **prompt-version-review** | **1 ★ 첫 정식** | Slice 1 분석 (P-007 0–5↔0–1 drift + semver 계획) + Slice 4 적용 (P-007 v1.0.0→v1.1.0 minor) → ADR-029. NG8 누적 3회 defer 해소 |
| contract-change | 1 (CC-003) | Slice 4 — prompt_registry.md semver 정식화 + agent_io_contract.md v1.2.0 §5 Critic v1.1.0 adapter + §8 orchestrator 중개. 회귀 0 유지 |
| agent-io-check | 1 (네 번째 회귀) | Slice 5 — agent_io_contract §5 (v1.1.0 + adapter) ↔ critic.py drift 0 + orchestrator 중개 검증 |
| harness-audit | 1 | Slice 5 audit_naming + audit_page_component 자동 호출 (0 drift + 2 intended WARN 유지) |
| design-review | 1 (impl §B 여덟 번째) | Slice 5 — frontend 변경 0 검증 (PlanCard 24연속 + component_map 34연속) |
| meta-retrospective | 1 (지금) | 본 문서 |
| phase-complete (v1.2.0) | 1 | Phase 8 종료 (v1.2.0 §1.6 **여섯 번째** 자동 게이트, scenario_simulation v4 20/20 PASS) |
| 기타 unused (의도된) | — | security-review (Phase 5 완료, Phase 8 보안 변경 0 — SSE Origin 유지) / eval-run / eval-design (Phase 9+) / rag-design / rag-update (Phase 7 완료) / context-compact (불요) / phase-review (불요) / bug-triage (불요) / cost-review (Phase 9+) |

**Phase 8 사용 요약**: 10 Skill 활용 (phase-start v1.3.0 + qa-check + multi-llm-validation formal 다섯 번째 + **ai-architecture-review ★ 첫 정식** (Slice 1) + **prompt-version-review ★ 첫 정식** (Slice 1 분석 + Slice 4 적용) + contract-change CC-003 (Slice 4) + agent-io-check 네 번째 회귀 (Slice 5) + harness-audit (Slice 5) + design-review 여덟 번째 §B (Slice 5) + meta-retrospective (Slice 5) + phase-complete v1.2.0 여섯 번째 자동 게이트 (Slice 5)). Phase 1~8 누적 = **16 Skill 활성화**, 4 unused. **ai-architecture-review + prompt-version-review 둘 다 첫 정식 트리거** (Phase 8 MOA Lite 본격 baseline 확립).

---

## 다음 액션

```
- [x] 본 회고 문서 작성 완료
- [x] meta/patterns.md update (P-X1-EFFECT-001 36연속 + P-MOA-ORCHESTRATOR-001 신규 + P-BEHAVIOR-PRESERVING-001 신규 + P-VALIDATION-FORMAL-001 다섯 번째)
- [x] meta/skill_usage_log.md 갱신 (Phase 8 사용 요약 10 Skill — ai-architecture-review + prompt-version-review 첫 정식)
- [x] phases/active/phase-8-* → phases/archive 이동
- [x] closing_notes.md 작성 (Phase 8 baseline + 다음 옵션 A/B/C/D + 운영 권장)
- [x] PROJECT_STATE / PHASE_REGISTRY / 00_START_HERE / README 갱신
- [ ] 다음 phase 사용자 결정 대기 (A Phase 9 저장/피드백 / B Phase 9.5 eval-run / C Phase 10 통합 / D Phase 11+)
```

---

## 다음 phase 옵션 (사용자 결정 대기)

### A. Phase 9 — 결과 저장 + 피드백 (6~10h)
- 사용자 plan 선택 / 수정 / 반려 누적
- Phase 5 plans_repo + RLS + Phase 7 RAG + Phase 8 orchestrator 활용
- Brand Memory 자동 추출 ADR 신규 (개선 제안 §5, 누적 3회 confirm)
- normalize_to_canonical wiring 연결 (개선 제안 §1) + per-user rate-limit + audit-log

### B. Phase 9.5+ — eval-run Skill 정식화 (4~6h)
- golden_set 회귀 + revise effect eval (Phase 4.5 D6 누적 6회 deferred 해소)
- Critic deprecated 0–5 fallback 완전 제거 (개선 제안 §4, Phase 6 ADR-018 다음 단계)
- 간이 RAG eval_rubric → golden_set 기반 정식 (Phase 7 개선 제안 §6 흡수)
- eval-design + eval-run Skill 첫 정식 트리거 baseline

### C. Phase 10 — MVP 통합 테스트 (6~8h)
- MVP 전체 end-to-end 검증 (Discovery + Quick → 3-plan → Critic revise → save → SSE progress)
- Phase 1~8 누적 baseline 통합 회귀
- 배포 테스트 게이트 A~G 준비

### D. 다른 우선순위 (Phase 11+)
- SSE full async worker (개선 제안 §2, 누적 2회)
- prompt A/B 실행 인프라 (개선 제안 §3 — multi-provider 대비)
- 사용자 데이터 자동 promotion (rag-update Skill 두 번째)
- Supabase SQL function 정의 (운영 단계 필수) / cost-review Skill 정식화

---

## 변경 이력

- 2026-05-29: Phase 8 회고 최초 작성 (phase-complete v1.2.0 §1.6 여섯 번째 자동 게이트 + §7 회고 자동 호출). **P-X1-EFFECT-001 update (36연속) + P-MOA-ORCHESTRATOR-001 신규 + P-BEHAVIOR-PRESERVING-001 신규 + P-VALIDATION-FORMAL-001 update (다섯 번째) 패턴 등록**. P-AGENT-SCOPE-001 mitigation 36/36 입증. **ai-architecture-review + prompt-version-review Skill 둘 다 ★ 첫 정식 트리거 완료 + ADR-027/028/029 + contract-change CC-003 (prompt_registry semver + agent_io_contract v1.2.0) + MOA orchestrator 추출 (plans.py 659→243 god-function 분해) + behavior-preserving (Envelope byte-identical, 기존 test 수정 0 의도된 2 version assertion 제외) + SSE 실 stage 통합 + Critic v1.1.0 conservative adapter (Phase 6 canonical 불변)**. 다음 phase = 🟡 pending_user_decision (옵션 A Phase 9 저장-피드백 / B Phase 9.5 eval-run / C Phase 10 통합 / D Phase 11+).
