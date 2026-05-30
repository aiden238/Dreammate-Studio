# PHASE_REGISTRY

## 운영 원칙

- 전체 Phase는 큰 지도 역할을 한다.
- 현재 active Phase만 상세히 작성한다.
- planned는 다음 2~3개만 중간 상세화한다.
- archive는 기본 참조하지 않는다.
- **active Phase는 항상 1개만.**

## Phase 목록

| Phase | 이름 | 상태 | 목적 |
|---|---|---|---|
| 0 | 하네스 초기화 (Migration) | **done** (2026-05-26) | GPT 골격 + 우리 콘텐츠 병합, Sprint S0~S5 완료 |
| 1 | MVP 기본 플로우 | **done** (2026-05-26) | 7 Slices + pytest 62/62 + automated smoke 5/5 + CC-001 + 회고 archive 완료 |
| 2 | design.md 기반 PWA 설계 (Discovery + Quick 분기) | **done** (2026-05-27) | 6 Slices + design_handoff 5/5 PASS + design-review 7원칙 + audit_naming 0 + P-AGENT-SCOPE-001 발견 |
| 3 | Next.js PWA 기본 UI 구현 (Discovery + Quick 분기) | **done** (2026-05-28) | 6 Slices + acceptance 10/10 + audit_naming + audit_page_component 0 drift + smoke 7/7 + 변경성 4/5+1 WARN + **P-X1 5/5 PASS + component_map 6연속 0줄** |
| 4 | FastAPI 기본 백엔드 구현 (확장) | **done** (2026-05-28) | 4 Slices (GPT 검토 6→4 채택) + acceptance 10/10 + audit_naming + audit_page_component 0 drift (D-1 해소) + smoke 8/8 + **P-X1 9연속 PASS + component_map 15연속 0줄 + PlanCard 4연속 0줄 + GPT 검토 ▼66% 시간** |
| 4.5 | Critic Revise Loop + Rewriter + Z-X3 + P-X2 | **done** (2026-05-28) | 4 Slices (모두 sub-agent) + A1~A10 + M1~M3 + P-X1 13연속 + PlanCard 9연속 + component_map 19연속 + P-X2 자동 게이트 첫 + multi-llm-validation formal 첫 + pytest 109/109 + smoke 9/9 |
| 6 | Output Schema + Agent IO Stabilization | **done** (2026-05-29) | 4 Slices (모두 sub-agent) + A1~A10 10/10 + M1~M3 + P-X1 17연속 + PlanCard 12연속 + component_map 22연속 + pytest 144/144 + smoke 10/10 + Critic canonical (ADR-018) + Rewriter v1.1.0 (ADR-019) + agent-io-check 첫 정식 + contract-change 본격 + P-CONTRACT-FIRST-001 신규 |
| 5 | DB / Auth / RLS / SSE | **done** (2026-05-29) | 5 Slices (모두 sub-agent) + A1~A10 10/10 + M1~M4 4/4 + **P-X1 22연속** + PlanCard 17연속 + component_map 27연속 + pytest 170/170 (+26) + smoke 12/12 + scenario_sim v2 10/10 (P-X2 세 번째) + Supabase + JWT httpOnly + RLS (ADR-021) + SSE 4단계 (ADR-022) + ADR-020 + security-review 첫+두 번째 + contract-change 두 번째 본격 (db_schema.md) + agent-io-check 두 번째 회귀 + P-RLS-001 + P-SSE-001 + P-SECURITY-REVIEW-001 신규 후보 + P-VALIDATION-FORMAL-001 정식 확정 |
| 5.5 | Legacy DB Consolidation + Validation 강화 + Phase 7 Prep | **done** (2026-05-29) | 4 Slices (모두 sub-agent) + A1~A8 + M1~M2 + **P-X1 26연속** + PlanCard 18연속 + component_map 28연속 + ADR-023 (Legacy DB 옵션 A) + ADR-024 (Phase 7 RAG scope evolution) + external × 3 self-strengthen V-form + Brand Memory Phase 9+ confirm + pytest 172/172 (+2 deprecation) + smoke 12/12 + scenario_sim v2 10/10 (P-X2 네 번째) + P-LEGACY-CONSOLIDATION-001 신규 후보 + legacy backward-compat 100% |
| 7 | RAG Lite (candidate_knowledge 5단계 MVP 전부) | **done** (2026-05-29) | 5 Slices (모두 sub-agent) + A1~A10 10/10 + M1~M4 4/4 + **P-X1 31연속** + PlanCard 19연속 + component_map 29연속 + ADR-025 (RAG architecture) + ADR-026 (5단계 promotion logic) + rag-design ★ 첫 정식 + rag-update ★ 첫 정식 + contract-change rag_data_contract §18 + pytest 223/223 (+51 신규) + smoke 13/13 + scenario_sim v3 15/15 (P-X2 다섯 번째) + P-RAG-5STAGE-001 신규 + P-RAG-GRACEFUL-001 신규 + P-LEGACY-CONSOLIDATION-001 누적 2회 (정식 채택 임박) + graceful 5종 marker |
| 8 | MOA Lite 본격 (orchestrator 추출 + SSE worker + prompt_registry 정식화) | **done** (2026-05-29) | 5 Slices (모두 sub-agent) + A1~A10 10/10 + M1~M5 5/5 + **P-X1 36연속** + PlanCard 24연속 + component_map 34연속 + ADR-027 (MOA orchestrator behavior-preserving) + ADR-028 (SSE progress integration) + ADR-029 (prompt_registry semver) + ai-architecture-review ★ 첫 정식 + prompt-version-review ★ 첫 정식 + contract-change CC-003 (prompt_registry + agent_io_contract v1.2.0) + pytest 249/249 (+26 신규) + smoke 14/14 + scenario_sim v4 20/20 (P-X2 여섯 번째) + P-MOA-ORCHESTRATOR-001 신규 + P-BEHAVIOR-PRESERVING-001 신규 + plans.py 659→243 god-function 분해 + Critic v1.1.0 conservative adapter |
| 9 | 결과 저장 + 피드백 (selected_plans + feedback_events 영속화 + normalize wiring + Brand Memory 준비 + 피드백 UI) | **done** (2026-05-31) | 6 Slices (모두 sub-agent) + A1~A10 10/10 + M1~M4 4/4 + **P-X1 42연속** + PlanCard 30연속 + component_map 40연속 + ADR-030 (feedback/selection persistence) + ADR-031 (Brand Memory prep — P-AUX-2 설계 agent 미구현 Phase 10+) + ADR-032 (normalize_to_canonical wiring) + security-review 두 번째 정식 (피드백 PII) + contract-change CC-004 (db_schema.md 실 plans 정합) + pytest 249→293/293 (+44 신규, 기존 수정 0) + smoke 15/15 + scenario_sim v5 25/25 (P-X2 일곱 번째) + P-FEEDBACK-LOOP-001 신규 + P-CANONICAL-WIRING-001 신규 + 피드백 UI inline (PlanCard·component_map 0줄) + deprecated warnings 67→16 |
| 9.5 | eval-run 정식화 + Critic deprecated 0–5 Full 제거 | **done** (2026-05-31) | 5 Slices (모두 sub-agent) + A1~A10 10/10 + M1~M4 4/4 + **P-X1 47연속** + PlanCard 35연속 + component_map 45연속 + ADR-033 (eval-run harness mock-deterministic) + ADR-034 (Critic deprecated 0–5 Full 제거) + eval-design ★ 첫 정식 + eval-run ★ 첫 정식 + contract-change CC-005 (output_schema §9 + agent_io_contract §5 canonical-only + db_schema) + pytest 293→339/339 (+46) + smoke 16/16 + scenario_sim v6 30/30 (P-X2 여덟 번째) + eval gate PASS (revise mean_delta 0.092) + Critic warnings 16→0 + P-EVAL-HARNESS-001 신규 + P-DEPRECATED-REMOVAL-001 신규 + revise effect eval (Phase 4.5 D6 해소) + generate.py canonical wiring 보강 |
| **M0** | **Meta-Factory Prep (★ meta-phase — L3 Meta-Harness Factory skeleton)** | **done** (2026-05-31) | 3 Slices (모두 sub-agent) + A1~A10 10/10 + M1~M3 3/3 + **★ 런타임 변경 0 (A9 — FastAPI/Next.js/Supabase 0줄)** + **P-X1 50연속** + PlanCard 35연속 + component_map 45연속 + ADR-035 (L3 Meta-Factory 도입) + CC-006 (INDEX harness-factory #21 Skill 등록) + harness-factory Skill ★ 신규 등록 (proposal-only, 키워드 scoped) + multi-llm-validation formal 여덟 번째 (★ 첫 meta-phase, V1~V6) + pytest 339 유지 + smoke_test_phase_M0 6/6 + scenario_sim v7 33/33 (P-X2 아홉 번째, SM1~SM3) + Skill 20→21 + P-META-FACTORY-001 신규 + meta_factory/ 7 루트 + templates 6 + blueprint 실측 + outputs (★ 제품 phase 번호 분리 detour) |
| **next** | **🟡 pending_user_decision** (A Phase 10 통합 / B Phase 11+) | **next** | Phase 9.5 + Phase M0(meta-phase) ✅ done — 다음 제품 phase 사용자 결정 대기 (meta-phase detour 종료) |
| 10 | MVP 통합 테스트 | planned | MVP 전체 end-to-end 검증 + Phase 1~9.5 누적 baseline 통합 회귀 + eval-run golden_set 회귀 baseline 활용 + P-AUX-2 brand_memory_extractor agent 실 구현 + 실 LLM eval mode + RAG eval_rubric golden_set 정식화 + 배포 테스트 게이트 준비 |
| 11~20 | 서비스 안정화 | future | UX, eval, cost, fallback, 피드백 |
| 21~30 | 확장 / 고도화 | future | Spring, Expo, Custom RAG, LangGraph |

## Phase 0 완료 (archive)

`phases/archive/phase-0-migration/`

```
Status     : ✅ DONE (2026-05-26)
Goal       : GPT 골격 + 우리 콘텐츠 병합하여 운영 가능한 하네스 완성
Result     : 11/11 acceptance 통과, 6 commit (S0~S5), ~50,000줄 하네스
Acceptance : 모두 충족 (acceptance.md 참조)
다음 Phase : 1. MVP 기본 플로우 (active, 진입 대기)
```

## Phase 1 done (archive)

`phases/archive/phase-1-mvp-basic-flow/`

```
Status     : ✅ DONE (2026-05-26)
Goal       : 영상기획 AI 에이전트의 핵심 흐름 구현 (입력 → 기획 → 검증 → 저장)
Result     : 7 Slices + pytest 62/62 + automated smoke 5/5 + CC-001 + retrospective
Acceptance : 8/8 implementation pass + Manual smoke (사용자 release 단계, Phase 외)
Sub-agent  : 6 dispatches (Wave 1×2 + Wave 2 + Wave 3 + Wave 4×2), 충돌 0
회고       : meta/retrospectives/phase-1.md
개선 제안  : meta/proposals/2026-05-26_phase-1-retrospective-proposals.md (P1~P4)
다음 Phase : 2. design.md 기반 PWA 설계 (active, 진입 대기)
```

## Phase 2 done (archive)

`phases/archive/phase-2-pwa-design/`

```
Status     : ✅ DONE (2026-05-27)
Goal       : design.md 기반 PWA 설계 (Discovery wizard + Quick Mode 분기, 4계층 데이터 모델 화면 매핑)
Result     : 6 Slices + 5 Waves + acceptance 10/10 PASS + audit_naming 0 drift (모든 Slice) + 변경성 시뮬레이션 5/5 PASS + design-review 7 원칙 정합 + qa-check v1.2.0 11 카테고리 (5 PASS / 6 skip - spec phase)
산출물     : 17 신규/수정 (design_system 4 + ADR 2 + flow specs 4 + wireframes 4 + design_handoff 1 + page_map 1 + component_map 1) — apps/web/* 약 3962 insertions / 0 코드
Sub-agent  : 6 dispatches (Wave 1 + Wave 2 + Wave 3×2 + Wave 4 + Wave 5), 충돌 0
회고       : meta/retrospectives/phase-2.md
신규 패턴  : P-AGENT-SCOPE-001 (sub-agent forbidden 침범, 무충돌) + P-DESIGN-LAYERED-001 (변경성 보장 효과)
개선 제안  : meta/proposals/2026-05-27_phase-2-retrospective-proposals.md (P-X1~P-X5, proposed 상태)
다음 Phase : 3. Next.js PWA 기본 UI 구현 (active, 진입 대기)
```

## Phase 3 done (archive)

`phases/archive/phase-3-pwa-impl/`

```
Status     : ✅ DONE (2026-05-28)
Goal       : Next.js PWA UI 실 구현 (Phase 2 spec 기반)
Result     : 6 Slices + 5 Waves + acceptance 10/10 PASS + audit_naming 0 drift + audit_page_component.ps1 (D5) 신규 0 drift + 변경성 4/5 PASS + 1 WARN + design-review 7 원칙 정합 (impl) + qa-check v1.2.0 11 카테고리 (8 PASS / 3 skip) + smoke 7/7 PASS
산출물     : ~20 신규 (apps/web/* 18 + scripts 2) — 약 +2905 코드 / +6550 전체
Sub-agent  : 5 dispatches (Wave 1 + Wave 2 + Wave 3×2 + Wave 4), 충돌 0
회고       : meta/retrospectives/phase-3.md
신규 패턴  : P-X1-EFFECT-001 (P-X1 §SELF-VERIFICATION 5/5 효과 입증) + P-THIN-VERTICAL-001 (Thin Vertical Slice 효과)
Mitigated  : P-AGENT-SCOPE-001 (Phase 2 발견 → Phase 3 P-X1 적용 후 0건 재발)
개선 제안  : meta/proposals/2026-05-28_phase-3-retrospective-proposals.md (Y-X1~Y-X3, proposed 상태) + Phase 2 P-X2 채택 권장
다음 Phase : 4. FastAPI 기본 백엔드 구현 (active, 진입 대기)
```

## Phase 4 done (archive)

`phases/archive/phase-4-fastapi-extension/`

```
Status     : ✅ DONE (2026-05-28)
Goal       : 기존 /generate 유지 + 새 /plans/{plan_id}/generate + 3-plan + Critic verdict + 회귀 0
Result     : 4 Slices + 4 Waves (sequential) + acceptance 10/10 PASS + audit_naming + audit_page_component 0 drift (Slice 4 D-1 해소) + 변경성 4/5 + 1 WARN (Phase 3 결과 유지, Phase 4 +0 영향) + 보조 시나리오 3/3 PASS + design-review 7원칙 정합 (impl) + qa-check v1.2.0 (9 PASS / 2 skip) + smoke 8/8 PASS
산출물     : ~15 신규 + 8 수정 + 9 archive 이동 (backend +1850 / frontend +280 / docs/decisions ADR-014+015 / scripts +170 / QA 5 reports / 회고 + closing_notes)
Sub-agent  : 3 dispatches (Slice 1~3 — Slice 4 본 회고는 main session), 충돌 0
회고       : meta/retrospectives/phase-4.md
신규 패턴  : P-GPT-REVIEW-001 (외부 LLM 검토 채택 효과 — 6→4 Slices, ▼66% 시간) + P-X1-EFFECT-001 update (9연속)
Mitigated  : P-AGENT-SCOPE-001 (9연속 누적 입증 — Phase 3 5 + Phase 4 4)
개선 제안  : meta/proposals/2026-05-28_phase-4-retrospective-proposals.md (Z-X1~Z-X3, proposed) + Phase 2 P-X2 채택 권장 (우선순위 ↑)
GPT 검토   : 채택 (6→4 Slices ▼33% / 18~26h → 6~8h ▼66%)
핵심 성과  : **P-X1 9연속 PASS + component_map.md 15연속 0줄 + PlanCard.tsx 4연속 0줄 + GPT 검토 채택 효과 실증**
다음 Phase : Phase 4.5 mini-phase (사용자 결정 옵션 A 채택)
```

## Phase 4.5 done (archive)

`phases/archive/phase-4.5-critic-revise-loop/`

```
Status     : ✅ DONE (2026-05-28)
유형       : mini-phase (Phase 4 후속 + Phase 5 진입 전 안정화)
Goal       : Critic revise loop + Rewriter + Z-X3 best-plan + P-X2 자동 게이트
Result     : 4 Slices (모두 sub-agent) + A1~A10 10/10 + M1~M3 3/3 + smoke 9/9 + scenario_simulation 5/5 (P-X2 첫) + pytest 109/109 (+16) + audit 0 drift × 2
산출물     : ~12 신규 + ~10 수정 (backend +450 / frontend +45 / scripts +200 / docs +300 / meta +200)
Sub-agent  : 4 dispatches (Slice 1~4 모두), 충돌 0 — P-X1 §SELF-VERIFICATION 4/4 PASS
회고       : meta/retrospectives/phase-4.5.md
신규 패턴  : P-X2-EFFECT-001 + P-VALIDATION-FORMAL-001 + P-X1-EFFECT-001 update (13연속)
Mitigated  : P-AGENT-SCOPE-001 (13연속 누적 입증 — Phase 3:5 + Phase 4:4 + Phase 4.5:4)
사용자 결정 : Z-X3 포함 + P-X2 채택 + multi-llm-validation formal (Claude Code 자가 검증, 외부 placeholder 분리) + 4 Slice 모두 sub-agent
핵심 성과  : **P-X1 13연속 PASS + PlanCard 9연속 + component_map 19연속 + multi-llm-validation formal 첫 + P-X2 자동 게이트 첫**
다음 Phase : Phase 6 (Output Schema + Agent IO Stabilization, 옵션 B 변형 채택)
```

## Phase 6 done (archive)

`phases/archive/phase-6-output-schema-stabilization/`

```
Status     : ✅ DONE (2026-05-29)
유형       : stabilization mini-phase (Phase 5 DB/Auth 진입 전 contract 안정화)
Goal       : Critic verdict canonical 결정 + Rewriter contract 강화 + revise_history/recommended_plan_index 정식 등록 + DB 진입 전 schema drift 위험 0
Result     : 4 Slices (모두 sub-agent) + A1~A10 10/10 + M1~M3 3/3 + smoke 10/10 + schema_stress_test 5/5 (P-X2 v2) + scenario_simulation 5/5 (P-X2 두 번째) + pytest 144/144 (+35) + audit×2 0 drift
산출물     : ~10 신규 + ~10 수정 + 3 contract 갱신 (output_schema + agent_io_contract + api_contract) + ADR-018/019
Sub-agent  : 4 dispatches (Slice 1~4 모두), 충돌 0 — P-X1 4/4 PASS
회고       : meta/retrospectives/phase-6.md
신규 패턴  : P-CRITIC-CANONICAL-001 + P-CONTRACT-FIRST-001 (신규 후보) + P-X1-EFFECT-001 update (17연속) + P-VALIDATION-FORMAL-001 update (두 번째 입증)
Mitigated  : P-AGENT-SCOPE-001 (17연속 누적 입증 — Phase 3:5 + Phase 4:4 + Phase 4.5:4 + Phase 6:4)
Skill 첫 정식: agent-io-check (첫 정식) + contract-change (본격 실 변경) + multi-llm-validation formal 두 번째 + phase-complete v1.2.0 두 번째 자동 게이트
GPT 검토안 정신: 6→4 Slice 압축 (▼33%) + 시간 8~12h → 실측 ~8h (▼20%, P-GPT-REVIEW-001 두 번째 적용)
핵심 성과  : **P-X1 17연속 PASS + PlanCard 12연속 + component_map 22연속 + Critic canonical 결정 + Rewriter v1.1.0 + agent-io-check 첫 정식 + contract-change 본격**
다음 Phase : **🟡 Phase 5 (DB/Auth) — pending entry** (사용자 결정 "Phase 6 → Phase 5 순차" 계승)
```

## Phase 5 done (archive)

`phases/archive/phase-5-db-auth/`

```
Status     : ✅ DONE (2026-05-29)
유형       : large phase (15~20h — MVP 본격 영속화)
Goal       : Supabase + PostgreSQL 영속화 + Supabase Auth + JWT + RLS + SSE Progress D7
Result     : 5 Slices (모두 sub-agent) + A1~A10 10/10 + M1~M4 4/4 + smoke 12/12 (11 PASS + 1 WARN intended) + scenario_simulation v2 10/10 (P-X2 세 번째) + schema_stress 5/5 (Phase 6 유지) + pytest 170/170 (+26) + audit_naming 0 drift × 2 + audit_page_component 2 intended drift WARN (Slice 3 AuthGuard + /login 신규)
산출물     : ~30 신규 + ~10 수정 (backend db/auth/sse +1500 / frontend AuthGuard + login + sse.ts +600 / tests +400 / docs/contracts/db_schema.md + ADR-020/021/022 / scripts/smoke_test_phase_5.ps1 / meta retrospectives/security_reviews/validations)
Sub-agent  : 5 dispatches (Slice 1~5 모두), 충돌 0 — P-X1 5/5 PASS
회고       : meta/retrospectives/phase-5.md
신규 패턴  : P-RLS-001 + P-SSE-001 + P-SECURITY-REVIEW-001 (신규 후보) + P-X1-EFFECT-001 update (22연속) + P-VALIDATION-FORMAL-001 update (세 번째 정식 확정)
Mitigated  : P-AGENT-SCOPE-001 (22연속 누적 입증 — Phase 3:5 + Phase 4:4 + Phase 4.5:4 + Phase 6:4 + Phase 5:5)
Skill 첫 정식: security-review (★ 첫 정식 Slice 1 + 두 번째 final Slice 5) + contract-change (두 번째 본격 — db_schema.md) + multi-llm-validation formal 세 번째 (V1~V6) + phase-complete v1.2.0 세 번째 자동 게이트 + agent-io-check 두 번째 회귀
4 ADR      : ADR-020 Supabase + ADR-021 RLS Policy + ADR-022 SSE Progress
핵심 성과  : **P-X1 22연속 PASS + PlanCard 17연속 + component_map 27연속 + Supabase 영속화 + JWT httpOnly cookie + RLS 정책 + SSE 4단계 + security-review 첫 정식 + 두 번째 final + contract-change 두 번째 본격**
다음 Phase : **🟡 pending_user_decision** (Phase 7 RAG / Phase 6+ legacy / Phase 8 MOA / Phase 9 저장-피드백)
```

## Phase 5.5 done (archive)

`phases/archive/phase-5.5-legacy-db-consolidation/`

```
Status     : ✅ DONE (2026-05-29)
유형       : consolidation mini-phase (Phase 5 후속 + Phase 7 진입 전 정리)
Goal       : Legacy DB 옵션 A 채택 (ADR-023) + external validation × 3 self-strengthen + ADR-024 Phase 7 RAG scope evolution + Brand Memory Phase 9+ confirm + Phase 7 진입 baseline 확립
Result     : 4 Slices (모두 sub-agent) + A1~A8 8/8 + M1~M2 2/2 + smoke 12/12 (재실행) + scenario_simulation v2 10/10 (P-X2 네 번째) + schema_stress 5/5 + pytest 172/172 (+2 legacy deprecation) + audit_naming 0 drift + audit_page_component 2 intended WARN (Phase 5 baseline 유지)
산출물     : ~6 신규 + ~10 수정 (backend db/* deprecated note +~100 / docs/decisions ADR-023+024 +~250 / meta validations × 3 강화 + retrospective + closing_notes / state docs × 5)
Sub-agent  : 4 dispatches (Slice 1~4 모두), 충돌 0 — P-X1 4/4 PASS
회고       : meta/retrospectives/phase-5.5.md
신규 패턴  : P-LEGACY-CONSOLIDATION-001 신규 후보 + P-X1-EFFECT-001 update (26연속) + P-VALIDATION-FORMAL-001 update (self-strengthen V-form sub-pattern)
Mitigated  : P-AGENT-SCOPE-001 (26연속 누적 입증 — Phase 3:5 + Phase 4:4 + Phase 4.5:4 + Phase 6:4 + Phase 5:5 + Phase 5.5:4)
사용자 결정 : 5건 1:1 mapping (legacy 옵션 A / external 강화 / Phase 7 Lite 유지 / 5단계 MVP 전부 / Brand Memory Phase 9+)
2 ADR      : ADR-023 Legacy DB 옵션 A + ADR-024 Phase 7 RAG scope evolution (5단계 MVP + 확대 지점 A~F)
핵심 성과  : **P-X1 26연속 PASS + PlanCard 18연속 + component_map 28연속 + legacy backward-compat 100% + Phase 7 진입 baseline 확립**
다음 Phase : **🟡 Phase 7 (RAG Lite — candidate_knowledge 5단계 MVP, 12~16h) — pending planning** (사용자 명시)
```

## Phase 7 done (archive)

`phases/archive/phase-7-rag-lite/`

```
Status     : ✅ DONE (2026-05-29)
유형       : large phase (12~16h — RAG Lite + candidate_knowledge 5단계 MVP 전부)
Goal       : candidate_knowledge 5단계 파이프라인 전부 (pending → filtered → evaluated → approved → promoted) + pgvector retrieval + LLM Wiki vs RAG 분리 + agents/rag.py 통합
Result     : 5 Slices (모두 sub-agent) + A1~A10 10/10 + M1~M4 4/4 + smoke 13/13 (12 PASS + 1 WARN intended) + scenario_simulation v3 15/15 (P-X2 다섯 번째) + schema_stress 5/5 (Phase 6 유지) + pytest 172 → 223/223 (+51 신규) + audit_naming 0 drift × 1 + audit_page_component 2 intended drift WARN (Phase 5 baseline 계승)
산출물     : ~22 신규 + ~10 수정 (backend rag layer +1500 / db/migrations/0004 / tests +500 / docs rag_data_contract §18 + ADR-025/026 / scripts smoke_test_phase_7 + scenario_simulation v3 / meta retrospectives + rag_updates + validations + patterns + skill_usage_log)
Sub-agent  : 5 dispatches (Slice 1~5 모두), 충돌 0 — P-X1 5/5 PASS
회고       : meta/retrospectives/phase-7.md
신규 패턴  : P-RAG-5STAGE-001 (신규 후보) + P-RAG-GRACEFUL-001 (신규 후보) + P-X1-EFFECT-001 update (31연속) + P-VALIDATION-FORMAL-001 update (네 번째 입증) + P-LEGACY-CONSOLIDATION-001 update (누적 2회 — 정식 채택 임박)
Mitigated  : P-AGENT-SCOPE-001 (31연속 누적 입증 — Phase 3:5 + Phase 4:4 + Phase 4.5:4 + Phase 6:4 + Phase 5:5 + Phase 5.5:4 + Phase 7:5)
Skill 첫 정식: rag-design (★ 첫 정식, Slice 1 → ADR-025) + rag-update (★ 첫 정식, Slice 4 → meta/rag_updates/2026-05-29_phase-7-initial-promotion.md) + contract-change 세 번째 본격 (Slice 2 rag_data_contract.md §18) + multi-llm-validation formal 네 번째 (V1~V7 PASS) + phase-complete v1.2.0 다섯 번째 자동 게이트 + agent-io-check 세 번째 회귀
2 ADR      : ADR-025 RAG architecture + ADR-026 5단계 promotion logic
사용자 결정 : 3건 mapping (Phase 5.5에서 이미 명시 — RAG Lite scope 유지 / 5단계 MVP 전부 / Brand Memory Phase 9+ 이관)
핵심 성과  : **P-X1 31연속 PASS + PlanCard 19연속 + component_map 29연속 + 5단계 파이프라인 전부 MVP + rag-design/rag-update 둘 다 첫 정식 + ADR-025/026 + graceful 5종 marker 표준화 + Phase 1 legacy ↔ Phase 7 신규 공존 누적 2회**
다음 Phase : **🟡 Phase 8 (MOA Lite 본격) — done**
```

## Phase 8 done (archive)

`phases/archive/phase-8-moa-lite/`

```
Status     : ✅ DONE (2026-05-29)
유형       : large phase (12~16h — MOA Lite 본격 orchestration 추출 + SSE worker + prompt_registry 정식화)
Goal       : plans_generate() god-function의 MOA orchestration을 service layer orchestrator로 추출 (behavior-preserving) + SSE Progress 실 stage 연동 + prompt_registry P-001~P-008 semver 정식화
Result     : 5 Slices (모두 sub-agent) + A1~A10 10/10 + M1~M5 5/5 + smoke 14/14 (13 PASS + 1 WARN intended) + scenario_simulation v4 20/20 (P-X2 여섯 번째) + schema_stress 5/5 (Phase 6 유지) + pytest 223 → 249/249 (+26 신규) + audit_naming 0 drift × 1 + audit_page_component 2 intended drift WARN (Phase 5 baseline 계승)
산출물     : ~13 신규 + ~10 수정 (backend orchestration layer +700 / tests +600 / docs ADR-027/028/029 + prompt_registry semver + agent_io_contract v1.2.0 + scripts smoke_test_phase_8 + scenario_simulation v4 + meta retrospectives + validations + patterns + skill_usage_log + closing_notes)
Sub-agent  : 5 dispatches (Slice 1~5 모두), 충돌 0 — P-X1 5/5 PASS
회고       : meta/retrospectives/phase-8.md
신규 패턴  : P-MOA-ORCHESTRATOR-001 (god-function → service layer 추출 behavior-preserving 신규 후보) + P-BEHAVIOR-PRESERVING-001 (기존 test 수정 0 = 동작 불변 증거 신규 후보) + P-X1-EFFECT-001 update (36연속) + P-VALIDATION-FORMAL-001 update (다섯 번째 입증)
Mitigated  : P-AGENT-SCOPE-001 (36연속 누적 입증 — Phase 3:5 + Phase 4:4 + Phase 4.5:4 + Phase 6:4 + Phase 5:5 + Phase 5.5:4 + Phase 7:5 + Phase 8:5)
Skill 첫 정식: ai-architecture-review (★ 첫 정식, Slice 1 → ADR-027 + Slice 5 회고) + prompt-version-review (★ 첫 정식, Slice 1 분석 + Slice 4 적용 → ADR-029) + contract-change 네 번째 본격 (Slice 4 CC-003 — prompt_registry + agent_io_contract v1.2.0) + multi-llm-validation formal 다섯 번째 (V1~V7 PASS) + phase-complete v1.2.0 여섯 번째 자동 게이트 + agent-io-check 네 번째 회귀
3 ADR      : ADR-027 MOA orchestrator behavior-preserving + ADR-028 SSE progress integration + ADR-029 prompt_registry semver
사용자 결정 : 3건 mapping (Scope 3개 모두 / Critic conservative adapter Phase 6 canonical 불변 / SSE progress_store 브릿지 background task 미도입)
핵심 성과  : **P-X1 36연속 PASS + PlanCard 24연속 + component_map 34연속 + MOA Orchestrator 추출 (plans.py 659→243 god-function 분해) + behavior-preserving (Envelope byte-identical, 기존 test 수정 0 의도된 2 version assertion 제외) + SSE 실 stage 통합 + prompt_registry semver 정식화 (NG8 누적 3회 해소) + Critic v1.1.0 conservative adapter + ai-architecture-review/prompt-version-review 둘 다 첫 정식**
다음 Phase : **🟡 pending_user_decision** (A Phase 9 저장-피드백 / B Phase 9.5+ eval-run / C Phase 10 통합 / D Phase 11+)
```

## Phase 9 done (archive)

`phases/archive/phase-9-result-feedback/`

```
Status     : ✅ DONE (2026-05-31)
유형       : large phase (10~14h — 결과 저장 + 피드백 + normalize wiring + Brand Memory 준비 + 피드백 UI)
Goal       : plan 선택/피드백 영속화(실 plans 정합) + normalize_to_canonical wiring(critic step canonical 0–1 live, deprecated 0–5 병행 회귀 0) + Brand Memory 준비(P-AUX-2 설계 agent 미구현 Phase 10+) + 피드백 UI wrapper(PlanCard·component_map 무수정)
Result     : 6 Slices (모두 sub-agent) + A1~A10 10/10 + M1~M4 4/4 + smoke 15/15 (14 PASS + 1 WARN intended) + scenario_simulation v5 25/25 (P-X2 일곱 번째) + schema_stress 5/5 (Phase 6 유지) + pytest 249 → 293/293 (+44 신규, 기존 수정 0) + audit_naming 0 drift × 1 + audit_page_component 2 intended drift WARN (Phase 5 baseline 계승)
산출물     : ~16 신규 + ~10 수정 (backend db/migrations/0005 + selection/feedback/brand_memory repo + rag/feedback_to_candidate + routers/plans select/feedback API + orchestration/moa_orchestrator normalize wiring + frontend lib/types+api+page.tsx inline 피드백 UI + tests +44 / docs db_schema.md + ADR-030/031/032 / scripts smoke_test_phase_9 + scenario_simulation v5 / meta retrospectives + security_reviews + validations + patterns + skill_usage_log + closing_notes)
Sub-agent  : 6 dispatches (Slice 1~6 모두), 충돌 0 — P-X1 6/6 PASS
회고       : meta/retrospectives/phase-9.md
신규 패턴  : P-FEEDBACK-LOOP-001 (피드백 영속 graceful + PII 마스킹 신규 후보) + P-CANONICAL-WIRING-001 (Phase N helper → live pipeline wiring additive 회귀 0 신규 후보) + P-X1-EFFECT-001 update (42연속) + P-VALIDATION-FORMAL-001 update (여섯 번째 입증)
Mitigated  : P-AGENT-SCOPE-001 (42연속 누적 입증 — Phase 3:5 + Phase 4:4 + Phase 4.5:4 + Phase 6:4 + Phase 5:5 + Phase 5.5:4 + Phase 7:5 + Phase 8:5 + Phase 9:6)
Skill 첫 정식: security-review (두 번째 정식, Slice 1 — 피드백 reason PII T1~T6, P-SECURITY-REVIEW-001 강화) + contract-change 다섯 번째 본격 (Slice 2 CC-004 — db_schema.md selected_plans/feedback_events 실 plans 정합) + multi-llm-validation formal 여섯 번째 (V1~V7 PASS) + phase-complete v1.2.0 일곱 번째 자동 게이트 + agent-io-check 다섯 번째 회귀
3 ADR      : ADR-030 feedback/selection persistence + ADR-031 Brand Memory prep (P-AUX-2 설계) + ADR-032 normalize_to_canonical wiring
사용자 결정 : 3건 mapping (Brand Memory 준비만 agent Phase 10+ / 피드백 UI wrapper PlanCard·component_map 무수정 / normalize wiring critic step canonical deprecated 병행)
핵심 성과  : **P-X1 42연속 PASS + PlanCard 30연속 + component_map 40연속 + 결과저장(selected_plans) + 피드백(feedback_events) 영속화 graceful + PII 마스킹 + normalize_to_canonical wiring (canonical 0–1 live, deprecated 0–5 병행 회귀 0, warnings 67→16) + Brand Memory 준비 (feedback→candidate pending 적재, agent Phase 10+) + 피드백 UI inline (PlanCard·component_map 0줄) + security-review 두 번째 정식 + contract-change CC-004**
다음 Phase : Phase 9.5 eval-run 정식화 (✅ done 2026-05-31)
```

## Phase 9.5 done (archive)

`phases/archive/phase-9.5-eval-run/`

```
Status     : ✅ DONE (2026-05-31)
유형       : eval mini-phase (6~10h — eval-run 정식화 + Critic deprecated 0–5 Full 제거)
Goal       : golden_set 회귀 runner(mock-deterministic, CI 가능) + revise effect eval(Phase 4.5 D6 해소) → eval-design/eval-run Skill 첫 정식 + eval로 canonical-only 품질 검증 후 Critic deprecated 0–5 Full 제거(canonical 단일 표준)
Result     : 5 Slices (모두 sub-agent) + A1~A10 10/10 + M1~M4 4/4 + smoke 16/16 (15 PASS + 1 WARN intended) + scenario_simulation v6 30/30 (P-X2 여덟 번째) + eval gate PASS (schema 1.0 / pass 1.0 / revise mean_delta 0.092 / improved 0.6 / regressed 0.2) + schema_stress 5/5 (Phase 6 유지) + pytest 293 → 339/339 (+46 신규) + audit_naming 0 drift × 1 + audit_page_component 2 intended drift WARN (Phase 5 baseline 계승) + Critic deprecated warnings 16→0
산출물     : ~12 신규 + ~8 수정 (backend/fastapi/eval module 5: __init__/golden_set_loader/runner/revise_effect/report + scripts/eval_run.ps1 + tests test_eval_runner+test_revise_effect / agents/critic.py deprecated 제거 + schemas/output.py CriticEvaluation 제거 + routers/generate.py canonical wiring + apps/web/lib/types.ts canonical 전환 + tests/test_critic 의도 delta + docs ADR-033/034 + output_schema/agent_io_contract/db_schema CC-005 + scripts smoke_test_phase_9_5 + scenario_simulation v6 / meta retrospectives + validations + patterns + skill_usage_log + closing_notes + eval/regression_results × 3)
Sub-agent  : 5 dispatches (Slice 1~5 모두), 충돌 0 — P-X1 5/5 PASS
회고       : meta/retrospectives/phase-9.5.md
신규 패턴  : P-EVAL-HARNESS-001 (golden_set mock-deterministic 회귀 + 임계값 게이트 신규 후보) + P-DEPRECATED-REMOVAL-001 (eval 안전망으로 deprecated 제거 신규 후보) + P-X1-EFFECT-001 update (47연속) + P-VALIDATION-FORMAL-001 update (일곱 번째 입증)
Mitigated  : P-AGENT-SCOPE-001 (47연속 누적 입증 — Phase 3:5 + Phase 4:4 + Phase 4.5:4 + Phase 6:4 + Phase 5:5 + Phase 5.5:4 + Phase 7:5 + Phase 8:5 + Phase 9:6 + Phase 9.5:5)
Skill 첫 정식: eval-design (★ 첫 정식, Slice 1 — golden_set executable format + 채점 차원 + 임계값 게이트) + eval-run (★ 첫 정식, Slice 2~3 — mock-deterministic 회귀 + revise effect) + contract-change 여섯 번째 본격 (Slice 4 CC-005 — output_schema §9 + agent_io_contract §5 canonical-only) + multi-llm-validation formal 일곱 번째 (V1~V7 PASS) + phase-complete v1.2.0 여덟 번째 자동 게이트 + agent-io-check 여섯 번째 회귀
2 ADR      : ADR-033 eval-run harness (mock-deterministic primary + 실 LLM mode flag + 임계값 + §eval-design) + ADR-034 Critic deprecated 0–5 Full 제거 (fallback + CriticEvaluation Optional, run_critic 0–5 불변 P-007 NG3)
사용자 결정 : 2건 mapping (Critic deprecated Full 제거 eval 검증 후 / eval mock-deterministic primary + RAG eval_rubric Phase 10+ 이관)
핵심 성과  : **P-X1 47연속 PASS + PlanCard 35연속 + component_map 45연속 + eval-design + eval-run Skill 첫 정식 (golden_set 11 케이스 mock-deterministic runner + 임계값, ADR-033) + revise effect eval (Phase 4.5 D6 해소 — mean_delta 0.092 / regressed 20%) + Critic deprecated 0–5 Full 제거 (ADR-034 + CC-005, eval 제거 전/후 동일 입증, warnings 16→0) + generate.py canonical wiring 보강 (Phase 1 endpoint normalize 누락 회귀 방지)**
★ deviation : generate.py canonical wiring 보강 (수용 — Phase 1 endpoint normalize 누락 발견·보강, 향후 신규 critic consumer normalize_to_canonical 경유 필수)
다음 Phase : **🟡 pending_user_decision** (A Phase 10 통합 / B Phase 11+)
```

## Phase M0 done (archive) — ★ meta-phase

`phases/archive/phase-M0-meta-factory/`

```
Status     : ✅ DONE (2026-05-31)
유형       : ★ meta-phase (제품 phase 아님 — L3 Meta-Harness Factory skeleton + contract + validation, 4~7h)
Goal       : 현재 구현 하네스(L2) 유지 + 상위에 harness/meta_factory/ (L3) skeleton + factory_contract(8 규칙 proposal-first) + domain_brief/harness_blueprint schema + architecture_patterns(6 + Dreammate 매핑) + workflow + templates 6 + 현재 하네스 blueprint 실측 + harness-factory Skill(proposal-only). ★ 자동 generator 아니라 skeleton·contract·validation 까지만 (payoff deferred).
Result     : 3 Slices (모두 sub-agent) + A1~A10 10/10 + M1~M3 3/3 + ★ 런타임 변경 0 (A9 — backend/fastapi 0 / apps/web 0 / db/migrations 0, git diff fff913e..HEAD 게이트) + smoke_test_phase_M0 6/6 + scenario_simulation v7 33/33 (P-X2 아홉 번째) + pytest 339 유지 + audit_naming 0 drift + audit_page_component 2 intended drift WARN (Phase 5 baseline 계승)
산출물     : ~24 신규 + ~6 수정 (meta_factory 7 루트 + templates 6 + blueprint + outputs 2 + ADR-035 + validations 2 + harness-factory/SKILL.md + proposal + CC-006 + smoke_test_phase_M0 + retrospective + closing_notes / INDEX.md #21 + scenario_simulation v7 + patterns + skill_usage_log + state docs 4)
Sub-agent  : 3 dispatches (Slice 1~3 모두), 충돌 0 — P-X1 3/3 PASS
회고       : meta/retrospectives/phase-M0.md
신규 패턴  : P-META-FACTORY-001 (L3 proposal-first 메타 레이어 신규 후보) + P-X1-EFFECT-001 update (50연속) + P-VALIDATION-FORMAL-001 update (여덟 번째 ★ 첫 meta-phase 입증)
Mitigated  : P-AGENT-SCOPE-001 (50연속 누적 입증 — Phase 3:5 + ... + Phase 9.5:5 + Phase M0:3)
Skill 첫 정식: harness-factory (★ 신규 등록 #21, proposal-only 키워드 scoped — 트리거 0 payoff deferred) + contract-change 일곱 번째 (CC-006 INDEX Skill 등록) + multi-llm-validation formal 여덟 번째 (V1~V6, ★ 첫 meta-phase) + harness-audit 키워드 충돌 검토 (충돌 0) + phase-complete v1.2.0 아홉 번째 자동 게이트
1 ADR      : ADR-035 L3 Meta-Factory 도입 (L1/L2/L3 + proposal-first + payoff deferred + skeleton-only)
1 CC       : CC-006 INDEX harness-factory #21 Skill 등록 (Skill 도 contract 처럼 취급)
사용자 결정 : 3건 mapping (meta-phase 격리 제품 phase 번호 분리 / harness-factory proposal-only 키워드 scoping / proposal-first 생성물 outputs/meta proposals 격리)
핵심 성과  : **P-X1 50연속 PASS + ★ FastAPI/Next.js/Supabase 런타임 변경 0줄 (A9) + L3 Meta-Harness Factory skeleton (meta_factory/ 7 루트 + templates 6 + blueprint 실측 + outputs) + factory_contract 8 규칙(proposal-first) + harness-factory Skill proposal-only (21번째, 키워드 scoped 충돌 0) + validation_workflow ↔ eval-run 연동 + ★ 첫 meta-phase 제품 흐름 무오염**
다음 단계  : harness-factory dry-run / trigger validation 샘플 / with-without 비교 샘플 (Phase M1+) / Phase 10 연결 (meta_factory blueprint = 온보딩·감사 baseline) — meta-phase detour 종료, next_phase_status pending_user_decision
```

## 🟡 Next phase: pending_user_decision (2026-05-31)

```
Phase 9.5 종료. 다음 phase는 사용자 결정 대기.

다음 phase 옵션:

A. Phase 10 — MVP 통합 테스트 (6~8h)
  - MVP 전체 end-to-end 검증 (Discovery + Quick → 3-plan → Critic revise (canonical-only) → save → select → feedback → SSE progress)
  - Phase 1~9.5 누적 baseline 통합 회귀 + eval-run golden_set 회귀 baseline 활용
  - P-AUX-2 brand_memory_extractor agent 실 구현 (Phase 9 schema + 적재 경로 준비 완료 → 데이터 누적 후 활성)
  - 실 LLM eval mode 운영 활성 (Phase 9.5 개선 제안 §1) + RAG eval_rubric golden_set 정식화 (개선 제안 §2) + golden_set 11 → 확대 (개선 제안 §3)
  - 배포 테스트 게이트 A~G 준비

B. 다른 우선순위 (Phase 11+)
  - 4계층 full linkage (plan_options/video_projects — selected_plans 실 plans 정합 → idealized schema 연결, 누적 2회 Phase 5 + Phase 9)
  - 사용자 데이터 자동 promotion (rag-update Skill 두 번째 — feedback→candidate pending 적재 완료)
  - SSE full async worker (누적 2회 Phase 5 + Phase 8) / prompt A/B 실행 인프라 (multi-provider 대비)
  - Supabase SQL function `match_approved_knowledge` 정의 (운영 단계 필수) / cost-review Skill 정식화

진입 전 권장 검토:
  - meta/retrospectives/phase-9.5.md (P-EVAL-HARNESS-001 + P-DEPRECATED-REMOVAL-001 신규 후보 + 개선 제안 §1~3)
  - meta/patterns.md (P-X1-EFFECT-001 47연속, P-VALIDATION-FORMAL-001 일곱 번째, P-EVAL-HARNESS-001 + P-DEPRECATED-REMOVAL-001 신규)
  - phases/archive/phase-9.5-eval-run/closing_notes.md (Phase 9.5 baseline + generate.py deviation + 다음 옵션 A/B + 운영 권장)
  - docs/decisions/phase_9_5_eval_run_harness.md (ADR-033)
  - docs/decisions/phase_9_5_critic_deprecated_removal.md (ADR-034)
  - docs/contracts/output_schema.md §9 + agent_io_contract.md §5 (Phase 9.5 Slice 4 — CC-005 canonical-only)
```

## Phase 2~3 Hybrid UX 분기 (planned, 중간 상세화)

```
Phase 2. design.md 기반 PWA 설계 (Discovery + Quick)
  - 4계층 데이터 모델 (User → Brand → Domain → Series → Video) 화면 매핑
  - Discovery wizard 7단계 (Brand → Domain → Series → Target → Tone → Direction Summary → Generate)
  - Quick mode 흐름 (짧은 프롬프트 → 1–2 부족 정보 질문 → 한 줄 방향 승인)
  - Mode 자동 분기 규칙 (Brand/Domain/Series 컨텍스트 유무로)
  - page_map.md, component_map.md 작성

Phase 3. Next.js PWA UI 구현
  - Discovery wizard 화면 구현 (단계당 5 카드)
  - Quick mode 화면 구현
  - Direction Approval 카드 (양 모드 공통)
  - Plan 후보 3개 비교 카드
  - 진행 stepper (4단계 + 부분 결과 노출)
```

## 배포 테스트 게이트

- Deploy Test A: Local Smoke Test
- Deploy Test B: Staging 배포
- Deploy Test C: 내부 알파 테스트
- Deploy Test D: Beta Staging
- Deploy Test E: 제한 사용자 테스트
- Deploy Test F: 비용 / 성능 테스트
- Deploy Test G: Production Readiness
