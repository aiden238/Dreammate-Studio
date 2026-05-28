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
| **next** | **🟡 Phase 7 (RAG Lite) — pending planning** (사용자 명시: Phase 5.5 진행 후 기획 시작) | **next** | RAG Lite + candidate_knowledge 5단계 MVP (ADR-024, 12~16h, 4~5 Slice) + rag-design ★ 첫 정식 |
| 7 | RAG Lite 구현 | planned | 초기 지식 검색 + candidate_knowledge 5단계 |
| 8 | MOA Lite 구현 | planned | Intent / Planner / Critic / Rewriter |
| 9 | 결과 저장 + 피드백 저장 | planned | 사용자 선택 / 수정 / 반려 저장 |
| 10 | MVP 통합 테스트 | planned | MVP 전체 검증 |
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

## 🟡 Next phase: Phase 7 (RAG Lite) — pending planning (2026-05-29)

```
Phase 5.5 종료. Phase 7 (RAG Lite) 기획 시작 대기 (사용자 명시: "Phase 5.5 진행 후 페이즈 7 기획 시작").

Phase 7 — RAG Lite (candidate_knowledge 5단계 MVP, 12~16h)
  - candidate_knowledge 5단계 승격 전부 (pending → filtered → evaluated → approved → promoted)
    - 사용자 결정 4 (Phase 5.5 명시) — ADR-024 §5단계 MVP
  - pgvector 활용 (Supabase 기본 제공, Phase 5 ADR-020 baseline)
  - **rag-design Skill ★ 첫 정식 트리거** (RAG architecture 결정)
  - rag-update Skill 진행 중 (5단계 승격 절차 강제)
  - contract-change Skill (rag_data_contract.md 갱신 또는 신규)
  - prompt-version-review P-007/P-008 정식화 (NG8 해소)
  - 4~5 Slice 분할 예상 (sequential, 모두 sub-agent dispatch)

Phase 7 진입 전 권장:
  - [ ] phase-start v1.3.0 4점검 (9번째 trigger)
  - [ ] multi-llm-validation formal self (네 번째 트리거, V형식 + external placeholder)
  - [ ] ADR-024 (Phase 7 RAG scope evolution) 재확인
  - [ ] candidate_knowledge 5단계 MVP scope 재확인 (사용자 결정 4)
  - [ ] (옵션) External validation × 3 진짜 외부 검토 (사용자 외부 GPT/Gemini, Phase 5.5 §개선 제안 §2)

확대 지점 (ADR-024 §확대 지점, 다른 phase 확장 경로):
  → Phase 11+ 사용자 데이터 자동 promotion
  → Phase 21+ Custom RAG / Graph RAG
  → Phase 7+ Hybrid retrieval (BM25 + vector)
  → Phase 8+ Multi-modal RAG (제한)
  → Phase 9+ Re-ranking model

진입 전 권장 검토:
  - meta/retrospectives/phase-5.5.md (P-LEGACY-CONSOLIDATION-001 신규 후보 + 개선 제안 §1~3)
  - meta/patterns.md (P-X1-EFFECT-001 26연속, P-VALIDATION-FORMAL-001 정식 확정 + self-strengthen V-form)
  - phases/archive/phase-5.5-legacy-db-consolidation/closing_notes.md (Phase 7 진입 baseline + 권장 Skill)
  - docs/decisions/phase_7_rag_scope_evolution.md (ADR-024)
  - docs/decisions/phase_5_5_legacy_db_consolidation.md (ADR-023, Phase 7+ 실 통합 시점 명시)
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
