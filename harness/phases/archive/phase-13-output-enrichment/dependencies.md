# Phase 13 — Dependencies

## 선행 phase (Phase 1~12 누적)

| 의존 | Phase 13 에서 |
|---|---|
| **Phase 12 깊이 격차 리포트** (`eval/regression_results/2026-06-02_phase-12-s2-s3-depth-gap.md`) | ★ **핵심 근거** — compact 0.231 vs rich 1.000(4.3x) + 결핍 10/13 feature 목록 = S1 스키마 슬롯·S2 프롬프트 확장의 직접 입력 |
| **Phase 12 S5 종합** (`phases/archive/phase-12-validation/s5_synthesis_and_phase13_proposal.md`) | Phase 13 우선순위·범위(어떤 feature 까지)·제품 경계 제안의 출처 |
| **depth_actionability rubric (CC-011)** (`eval/video_planning_eval.md` §2.A.1) | ★ S6 depth 재측정의 채점 차원(0.231→≥0.8 게이트) — Phase 13 은 rubric 변경 없이 그대로 재측정 |
| **golden_set 25** (`eval/golden_set.md`, Phase 12 S1) | S2 프롬프트 회귀(prompt-version-review) + S6 depth 재측정의 표본 |
| **output_schema / agent_io_contract** (`docs/contracts/output_schema.md` §8.1 `Plan` + agent_io) | ★ S1 rich 슬롯 additive 의 대상 contract — additive(Optional) + agent-io-check 회귀 |
| **prompt_registry P-006/P-007** (`ai_system/prompts/prompt_registry.md`) | ★ S2 P-006 bump(rich planning) + S4 P-007 bump(Critic depth) — prompt-version-review semver |
| **frontend PlanCard / design.md** (`apps/web/components/PlanCard.tsx` + `apps/web/design.md`) | ★ S5 conditional rich 렌더의 대상 — design-review 7원칙 정합 |
| **gated flag 패턴** (`config.py` `multi_provider_plans_enabled`·`cross_validation_enabled` default False) | ★ S3 `rich_output_enabled` default False 의 동형 패턴(Phase 11 계승) |
| **run_planning / moa_orchestrator** (`backend/fastapi/agents/planning.py` + `orchestration/moa_orchestrator.py`) | ★ S2 rich 프롬프트 + S3 gated 분기의 wiring 지점(behavior-preserving when OFF) |
| **cost_control_policy** (`ai_system/orchestration/cost_control_policy.md`) | ★ S6 rich 토큰 ↑ × 3안 재조정의 대상 |

## ★ B안(Phase 11) 비차단 잔여 — Phase 12 에서 승계 (추적·통합)

> Phase 11 B안(3-provider)의 정식화 일부가 비차단 잔여로 남아 Phase 12 에서 추적됨. Phase 13 이 **cost 재조정(S6)에서 B-RES-1 을 통합** 처리.

| ID | 잔여 항목 | Phase 13 처리 |
|---|---|---|
| **B-RES-1** | `cost_control_policy` 다중-provider cost 재조정 (§18.D) | ★ **S6 에 흡수** — rich 토큰 ↑ 재조정과 함께 cost_control_policy 갱신(contract-change). rich 비용 배수(× 3안) + 다중-provider 를 한 번에 |
| **B-RES-2** | B안 ADR (3-provider 결정 기록) | Phase 13 직후 또는 S6 ADR 에 묶음(선택) |
| **B-RES-3** | agent_io / registry contract-change (B안 3-provider 반영) | Phase 13 직후(비차단) — depth 슬롯 contract-change(S1)와 별개 |

→ ★ B-RES-1 = Phase 13 S6 통합(blocking 아님이나 cost 정책 정합상 함께). B-RES-2/3 = 추적(비차단).

## 측정 / 검증 의존 (S6)
- `backend/fastapi/eval/` (runner / golden_set_loader / mode / report — Phase 9.5/10) — depth 재측정 실행. 실 LLM eval mode(Phase 10 capability, default mock)를 측정용으로 1회 ON(실비용, 키 user-provided).
- mock-deterministic eval = CI 회귀 게이트 **유지** — depth 재측정은 측정 전용(Phase 12 NG9 계승).
- 키(OPENAI/ANTHROPIC/GOOGLE) = .env user-provided + .gitignore. flag ON 라이브 데모 = 승인 비용, 키 평문 0.

## Skill 의존
- `contract-change`(S1 output_schema rich 슬롯 / S6 cost_control 재조정, additive) / `agent-io-check`(S1 Plan ↔ agent_io 정합) / `prompt-version-review`(S2 P-006 bump / S4 P-007 depth bump, semver + golden_set 회귀) / `design-review`(S5 PlanCard rich UX 7원칙) / `eval-run`(S6 depth 재측정) / `cost-review`(S6 rich 토큰 + B-RES-1) / `multi-llm-validation`(entry self 12th) / `meta-retrospective`(S6 종합) / `phase-start`·`phase-complete`(진입·종료) / (참조) `ai-architecture-review`(rich 출력 orchestration 영향).

## 비의존 / 경계
- 모델 tier 상향(2차 레버, NG2) / 완성 대본·영상 제작(영구 non-goal, NG1) / staging 배포(Phase 14+, NG4) / golden_set·rubric 변경(Phase 12 산출 그대로 재측정, NG8) / B안 UX 노출(Phase 14+, NG9).
- ★ behavior-preserving when OFF: 기존 endpoint/agent/schema 에 **의존하되 flag OFF 경로는 byte-identical** — rich 는 flag ON opt-in. compact 프롬프트·기존 필드 보존.
