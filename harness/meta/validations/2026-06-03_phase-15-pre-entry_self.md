# Phase 15 Pre-Entry — multi-llm-validation (self-form, 14th)

> 2026-06-03 | Phase 15(director 모드) 진입 타당성 self 교차검증. 기반 = project-1 PARKED 제안서(commercial-viral-mode-design.md). 결정: 로드맵 ① director → ② 검증 보강 → ③ PKM/RAG.

| # | 검증 질문 | 판정 | 근거 |
|---|---|---|---|
| **V1** | director 를 지금 빌드하는 게 타당한가(제안서는 PARKED인데)? | ✅ PASS | 제안서 §7.1/§7.2: director 는 **데이터레이어 비의존**(연출/리텐션) → "먼저 검증 가능"으로 명시. 선행조건 (b)위저드=Phase14 ✅. director 는 gated OFF+additive(운영 무영향) → (a)(c) 완전충족 전에도 안전. commercial_viral 만 데이터레이어+게이트 필요. |
| **V2** | director 슬롯 경계(open issue #1)가 타당한가? | ✅ PASS | hook_system/retention_architecture/scene_breakdown(director-subset) = 연출·리텐션(데이터 비의존). market/audience/brand/conversion/platform/measurement + scene 상업필드 = commercial_viral(NG1, 데이터레이어 종속). 제안서 §2.1 "중간 깊이" 정의와 정합. |
| **V3** | output_mode enum 일반화(flag→enum, #2)가 회귀 안전한가? | ✅ PASS | additive — `output_mode` default compact + `rich_output_enabled=True→rich` 매핑(backward-compat). Phase 13/14 OFF/rich 동작 보존. model_dump 모드별 제외로 compact/rich byte-identical. pytest 508 회귀 게이트. |
| **V4** | gated/additive 패턴이 Phase 13 와 동형인가? | ✅ PASS | DIRECTOR_FIELDS(PLAN_RICH_FIELDS 동형) + model_dump_for_mode + P-006/P-007 gated 공존 + config gate — P-GATED-OUTPUT-CHANGE-001 계승. 신규 endpoint/agent 0(기존 Planner/Critic mode 확장). |
| **V5** | 제품 경계/보장 위험은? | ✅ PASS | scene_breakdown=기획 의도/감정/리텐션 근거(촬영지시·완성대본 아님, 보정2/product_boundary). director 프롬프트 보장 표현 금지(보정1 계승). commercial 전환/측정 슬롯 제외(NG1). |
| **V6** | 비용/범위 폭증 위험은? | ✅ PASS | director = rich↔commercial_viral 중간(상업 10슬롯 미포함) → 토큰 증가 제한적. cost_control director additive(S6). default OFF → 운영 비용 무영향. 키 0. |

## 불확실(U) — assumptions §1.2
- U-1 director depth mock 채점 한계(실 LLM/human=로드맵 ②). U-2 scene N씬 상한. U-3 output_mode↔rich_output_enabled 공존 매핑 전 경로 회귀.

## 종합
- **진입 타당 (V1~V6 PASS)**. director = 데이터 비의존 중간 tier, gated/additive/OFF byte-identical. 제안서 §7.1 단계화(director 먼저) + 사용자 로드맵 정합. commercial_viral/PKM-RAG 는 NG(후속).
- P-VALIDATION-FORMAL-001 update (14th).
