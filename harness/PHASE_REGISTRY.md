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
| **next** | **🟡 pending_user_decision (옵션 A/B/C, 사용자 결정 3-c)** | **next** | 옵션 A: Phase 4.5 mini-phase (Critic revise + Rewriter, 8~12h) / 옵션 B: Phase 5 DB/Auth (Supabase + RLS + SSE, 15~20h) / 옵션 C: Phase 6 / 9 / 11+ |
| 5 | DB / Auth 기본 구조 구현 | planned (option B 후보) | Supabase / PostgreSQL 연결 + RLS + SSE Progress (D7) |
| 6 | Output Schema + Agent IO 구현 | planned | AI 입출력 안정화 |
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
다음 Phase : **🟡 pending_user_decision (옵션 A/B/C, 사용자 결정 3-c)**
```

## 🟡 Next phase pending_user_decision (2026-05-28)

```
사용자가 셋 중 선택 후 다음 phase 진입 (phase-start v1.3.0 호출):

옵션 A: Phase 4.5 mini-phase (Critic revise loop + Rewriter)
  - D6 본격 구현 (P-008 Rewriter + Critic revise 최대 2회)
  - 추정 시간: 8~12h
  - 다음 → Phase 5
  - 권장 시점: 영상기획 품질 안정화 우선시

옵션 B: Phase 5 DB/Auth (Critic revise는 Phase 6+)
  - Supabase Auth + RLS + plan_store DB migration + SSE Progress (D7)
  - 추정 시간: 15~20h
  - 다음 → Phase 6 (Critic revise loop 통합)
  - 권장 시점: 다중 사용자 데이터 누적 + 보안 우선시

옵션 C: 다른 우선순위 (Phase 6 / 9 / 11+ 등)
  - 사용자 시점에서 우선순위 재평가
  - 권장 시점: 본 Phase 4 산출물 실 사용 + 데이터 누적 후

진입 전 권장 검토:
  - meta/retrospectives/phase-4.md
  - meta/proposals/2026-05-28_phase-4-retrospective-proposals.md (Z-X1~Z-X3 + P-X2)
  - phases/archive/phase-4-fastapi-extension/closing_notes.md
  - multi-llm-validation Skill **formal 호출** (옵션 B 또는 큰 phase 시 의무)
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
