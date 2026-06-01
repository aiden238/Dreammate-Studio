# Phase 11 — Goals (LLM Gateway A안 — cross-validation)

> Phase: phase-11-llm-gateway
> 유형: **제품 phase (런타임 有)** — ★ behavior-preserving (기존 0 수정, additive + gated default-off)
> 진입일: 2026-06-01 (★ 가속 빌드 — 코드 S1·S2·S3 선완료, 본 entry 는 retroactive 정식화)
> 결정 근거: 사용자 — **A안 먼저 구현, B안은 후속 phase 지침** (제안서 §18.A / §18.B)
> 근거 문서: `meta/proposals/2026-05-31_llm-gateway-design.md` (§1~§18, ★ 메인 설계 근거)

## 한 줄 정의

기존 **OpenAI 동작을 100% 보존**한 채, agent 가 concrete 모델명이 아닌 **alias(논리명)**만 참조하고 **LLM Gateway** 가 alias→provider/model 을 결정하는 단일 seam 을 도입하고, 그 위에 **다른 family(Gemini) 1회 교차검증**(Critic 의 추가 pass, ★ gated default-off, 로깅만)을 additive 하게 붙인다. → provider 추가 시 agent 코드 0 변경 + single-model self-bias 완화.

## ★ A안 결정 + behavior-preserving 화해

```
A안 (Phase 11 구현 범위)  : OpenAI 보존 + Critic 교차검증(Gemini)만 추가. 최소 비용 증가.
B안 (후속 phase 지침)      : 3-provider 다양성(GPT/Claude/Gemini 3-plan). cost_control 전면 재조정 (제안서 §18.B).
구현 단계                  : Stage A(OpenAI-only wrapping)까지 — Stage B(canonical complete 전환)는 provider 추가 phase.
게이트                     : cross_validation_enabled default False → orchestrator hook 미발화 (기존 흐름 100% 동일).
```

→ "교차검증 추가"(A안) 이면서 "기존 동작 불변"(behavior-preserving)은 모순이 아니다: gateway 는 agent **아래 레이어**(Envelope 무관), cross_validation 은 **gated default-off + 로깅만**(Envelope/output_schema 0 변경). 제안서 §4.1 Stage A + §7 gated 정합.

## 핵심 목표 (G1~G6)

| ID | 목표 | Slice |
|---|---|---|
| **G1** | **LLM Gateway 골격** — `llm/` 패키지(types/errors/registry/aliases/gateway + providers/base·openai_adapter·gemini_adapter). agent 는 alias 만, gateway 가 provider 결정 | S1 |
| **G2** | **alias→model 해석 = 현 default byte-identical** — `resolve_model("planning")==gpt-4o-mini`, `resolve_model("critic","-","standard")==gpt-4o`, `("critic","-","cost_saving")==gpt-4o-mini` (현 cost_saving 폴백 정식화) | S1 |
| **G3** | **cross_validation 모듈** — `cross_validate`(Gemini 독립 8차원 평가, Critic canonical 동형) + `compare`(consensus / divergence / human_review_needed). graceful(키없음/503/빈출력/파싱실패 흡수) | S2 |
| **G4** | **Gemini adapter 튜닝** — thinking_budget=0(빈출력 회피) + 503 재시도 + text fallback. config Field(`google_api_key` / `cross_validation_model` / `gemini_thinking_budget`) additive | S2 |
| **G5** | **orchestrator gated hook** — moa_orchestrator critic 단계 후, recommended plan 1회 교차검증. ★ `cross_validation_enabled` default OFF + **로깅만** + 모든 예외 graceful + Envelope 불변 | S3 |
| **G6** | **behavior-preserving 회귀 0** — 기존 endpoint/agent/test 0 수정. pytest 381 → 435 (신규/additive만) | 전 Slice |

## 메타 목표 (MG1~MG3)

| ID | 목표 |
|---|---|
| **MG1** | ADR-039 (LLM Gateway + cross_validation) — agent=alias / gateway=provider 결정, gated default-off |
| **MG2** | contract-change — `cost_control_policy.md` 확장 (tier×mode→alias 표 + cross_validation 비용, ★ additive) CC-010 |
| **MG3** | P-X1 §SELF-VERIFICATION 연속 유지 (Phase 10 60 → Phase 11 **63**, S1·S2·S3) |

## 사용자 가치 (Why)

- **provider 추상화**: agent 가 concrete 모델명 의존 제거 → 후속 provider 추가 = adapter 1개 + registry 항목, **agent 코드 0 변경**. 모델 교체 = `.env` 1줄(`CROSS_VALIDATION_MODEL=`).
- **self-bias 완화**: 생성=gpt-4o-mini / 검증=gpt-4o / 교차검증=Gemini(다른 family) — multi-llm-validation 정신을 런타임에 반영. consensus / divergence 관측.
- **정책 단일화**: 현 cost_saving 의 "Critic gpt-4o→mini 폴백" 로직 분산을 **alias 표로 선언적 정식화**(제안서 §6).
- **안전한 도입**: gated default-off + 로깅만 → 기존 사용자 흐름 100% 불변. 활성/노출은 후속 + output_schema contract-change.

## ★ 절대 금지 (non_goals.md 상세)

provider 자동 활성(키없음 graceful skip) / Opus·flagship **기본 호출**(premium_review gated, A안 미구현) / output_schema·Envelope 변경 / MOA agent 수 4 증가(cross_validation = Critic 추가 pass) / B안(3-provider 다양성, 후속) / Stage B canonical 전환(provider 추가 phase) / 영상 제작(영구 non-goal) / 실 키 평문 커밋.
