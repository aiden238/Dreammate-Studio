# Phase 4.5 — Goals

> Phase: phase-4.5-critic-revise-loop
> 유형: mini-phase (Phase 4 후속, Phase 5 진입 전 안정화)
> 진입일: 2026-05-28
> 예상 시간: 12~16h

## 한 줄 정의

Phase 4 baseline(3-plan + multi-model + Critic verdict) 위에 **Rewriter Agent (P-008) + Critic Revise Loop + Best-Plan Selection (Z-X3) + P-X2 자동 게이트**를 얹어, 영상기획 품질을 한 단계 끌어올린다.

## 핵심 목표 (G1~G6)

| ID | 목표 | 검증 매핑 |
|---|---|---|
| **G1** | Rewriter Agent (P-008) 구현 — Critic verdict가 `revise`일 때 plan 개선 | A1 |
| **G2** | Critic Revise Loop — 최대 2회 (무한 루프 차단) + revise_history 노출 | A2, A3 |
| **G3** | Best-Plan Selection (Z-X3) — Critic 8-dim 종합으로 `recommended_plan_index` 노출 | A4 |
| **G4** | Frontend wrapper highlight — PlanCard.tsx **무수정** 유지 (5연속 0줄) | A5, A6 |
| **G5** | P-X2 채택 — `phase-complete` Skill v1.2.0 변경성 시뮬 자동 게이트 + `scenario_simulation.ps1` 신규 | A9 |
| **G6** | 회귀 0 — Phase 4 baseline 유지 (pytest 93/93 → 100+/100+ + smoke 8/8 → 9/9 + audit 0 drift + component_map 0줄 16연속) | A7, A8, A10 |

## 메타 목표 (M1~M3)

| ID | 목표 | 결과물 |
|---|---|---|
| **M1** | multi-llm-validation **formal** 첫 트리거 — Claude Code 자가 검증 (지침 참조) | `meta/validations/2026-05-28_phase-4.5-pre-entry_self.md` |
| **M2** | 외부 검증 placeholder 분리 (사용자가 외부 GPT/Gemini 진행 시 별도 누적) | `meta/validations/2026-05-28_phase-4.5-pre-entry_external.md` (placeholder) |
| **M3** | P-X1 §SELF-VERIFICATION **13연속 PASS** 목표 (Phase 3 5 + Phase 4 4 + Phase 4.5 4) | sub-agent commit별 git diff --stat 검증 |

## 사용자 가치 (Why)

- **품질 ↑**: revise loop로 첫 plan의 약점(weakness)이 자동 보완 → Critic verdict approve 비율 ↑
- **결정 부담 ↓**: 3 plan 중 추천 1개 highlight → 사용자가 reject 가능하되 default 결정 부담 ↓
- **회귀 안전망 ↑**: P-X2 자동 게이트로 Phase 5(DB/Auth) 진입 전 변경성 시뮬 자동화 → 이후 phase 안정성 확보
- **장기 운영 ↑**: multi-llm-validation formal 첫 트리거로 `meta/validations/` 누적 시작 → 큰 phase 진입 시 단일 모델 편향 회피 baseline

## 비목표 (별도 문서: non_goals.md)

DB 영속화 / Supabase / Auth / SSE / PlanCard 수정 / prompt_registry 정식화 / revise 효과 eval — 모두 Phase 5+ 이관.
