# Phase 14 — Goals (위저드 ↔ 백엔드 실연결, Scope A 최소 배선)

## 한 줄 정의
mock 상태인 위저드(`/new/quick` 4단계 · `/new/discovery` 7단계)를 **실제 백엔드 생성 경로**(`/plans/start` → `/plans/{id}/wizard/{step}` → `/plans/{id}/generate` → `/plan/[plan_id]`)에 배선하여, 랜딩 `/` 외에 **위저드로도 실 기획안(rich gated)** 이 생성되게 한다. ★ 랜딩 `/` 경로는 무변경(behavior-preserving).

## 목표
1. **위저드 = 실 생성**: Quick/Discovery 위저드가 setTimeout/setInterval mock(`buildMockPlan`)을 버리고, 수집한 입력으로 실제 `/generate`(3-plan, Critic, RAG) 를 호출 → `/plan/[plan_id]` 에서 rich 카드로 표시.
2. **세 endpoint 정식 사용**: `startPlan`(plan_id 발급) → `wizardStep`(step 입력 백엔드 누적) → `generateMultiPlan`(3안 생성). 백엔드는 누적된 `wizard_data`를 생성 입력으로 **additive** 소비(랜딩 `initial_input` 경로 byte-identical).
3. **rich gated 자동 상속**: 위저드도 `/generate` 경로를 쓰므로 `rich_output_enabled`(default OFF) 분기를 자동 상속 — 별도 rich 배선 불필요.
4. **데이터 흐름 통일**: 위저드 결과를 `/plan/[plan_id]`(GET `/plans/{id}` 백엔드 read)로 라우팅 → 랜딩(`dreammate.slice6.plan` sessionStorage)과 분리돼 있던 위저드 키를 백엔드 단일 출처로 수렴.

## 성공 기준 (acceptance 요약)
- Quick 4단계 + Discovery 7단계 완주 → 실 `/generate` 호출 → `/plan/[plan_id]` 에서 실 3-plan 표시 (mock plan 제거).
- 랜딩 `/` 흐름 byte-identical (pytest 499 회귀 0) + 키 0.
- rich `rich_output_enabled=true` 시 위저드 결과도 rich (gated 상속 입증).

## 비목표 (요약 — 상세 non_goals.md)
- ❌ per-step **P-001~P-005 실 LLM 카드 생성**(brand/domain/series/target/tone/direction) — PARKED **PKM/RAG Orchestrator** 영역(provisional P16~17). 중간 step 카드는 현행 휴리스틱/mock UX 유지(입력 수집용).
- ❌ rich default OFF→ON 전환(Phase 14 후보 A — 별도 결정).
- ❌ 완성 대본/영상 제작 (product_boundary 영구).

## 근거
- project-1(메인 세션) 위저드 분석: 위저드 mock, 랜딩만 실동작, 실연결=한 페이즈 분량, per-step LLM=PKM/RAG(PARKED).
- `meta/handoffs/2026-06-03_checkpoint-phase13-done.md` §3 (Phase 14 우선순위 2 = 위저드 실연결, PARKED 선행조건).
