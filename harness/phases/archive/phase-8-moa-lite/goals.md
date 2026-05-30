# Phase 8 — Goals

> Phase: phase-8-moa-lite
> 유형: large phase (MOA Lite 본격 — orchestration 분리 + SSE worker + prompt_registry 정식화)
> 진입일: 2026-05-29
> 예상 시간: 12~16h (5 Slice 모두 sub-agent dispatch)

## 한 줄 정의

`plans_generate()` 400줄 god-function에 인라인된 MOA orchestration(Intent→RAG→3-plan→Critic+revise→save→Envelope)을 **서비스 레이어 orchestrator로 추출**(behavior-preserving)하고, **SSE Progress를 실 orchestration stage와 연동**하며, **prompt_registry P-001~P-008 + AUX를 semver로 정식화**하여 MOA Lite를 본격 운영 구조로 완성한다.

## 핵심 목표 (G1~G8)

| ID | 목표 | 검증 |
|---|---|---|
| **G1** | MOA Orchestrator 추출 — `orchestration/moa_orchestrator.py` 신규, `plans_generate()` 로직 이관, router는 thin adapter | A1, A2 |
| **G2** | **Behavior-preserving** — Envelope byte-identical + pytest 223 그대로 PASS (회귀 0) | A3 |
| **G3** | ProgressSink 인터페이스 — orchestrator가 stage별 emit (NullProgressSink default = 회귀 0) | A4 |
| **G4** | SSE Progress 실 worker 통합 — progress store 브릿지 + sse.py가 실 stage read (graceful fallback) | A5, A6 |
| **G5** | prompt_registry 정식화 — P-001~P-008 + AUX semver + prompt_id/version 단일 출처 정합 | A7 |
| **G6** | Critic 0–5↔0–1 conservative adapter — P-007 v1.0.0→v1.1.0, Phase 6 canonical 불변 (사용자 결정) | A7 |
| **G7** | **PlanCard.tsx + component_map.md 0줄 유지** (Phase 8 backend-only) | A8 |
| **G8** | 회귀 0 — Phase 7 baseline (pytest 223 + smoke 13 + scenario_sim v3 15) 유지/확장 | A9, A10 |

## 메타 목표 (M1~M5)

| ID | 목표 |
|---|---|
| **M1** | multi-llm-validation **formal self** 다섯 번째 트리거 + external placeholder |
| **M2** | **ai-architecture-review Skill ★ 첫 정식 트리거** (MOA orchestration 설계) |
| **M3** | **prompt-version-review Skill ★ 첫 정식 트리거** (P-007 Critic semver + drift 해소) |
| **M4** | P-X1 §SELF-VERIFICATION **36연속 PASS** (Phase 7:31 + Phase 8:5) |
| **M5** | contract-change Skill (agent_io_contract + prompt_registry) — Phase 8 Slice 4 |

## 사용자 가치 (Why)

- **유지보수성 ↑**: 400줄 god-function 분해 → orchestration 로직 단일 책임 + 테스트 격리
- **UX ↑**: SSE Progress가 실 stage 반영 → 30~60초 대기 중 정확한 진행 표시 (확정 결정 [10] 실 구현)
- **prompt 운영 baseline**: semver + 단일 출처 정합 → 추후 A/B + 모델 교체 안전 (Phase 21+ multi-provider 대비)
- **MOA Lite 본격 완성**: moa_policy.md §2 "오케스트레이터가 항상 중개" 정합 (현재 router 인라인 위반 해소)

## 비목표 (별도 문서: non_goals.md)

비동기 큐 / background task / Brand Memory extractor / prompt A/B 실행 / 새 agent 추가 / PlanCard 수정 / Critic canonical 재정의 — 모두 Phase 9+/11+ 이관.
