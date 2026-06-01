# ADR-039: Phase 11 LLM Gateway A안 (alias→provider + Gemini 교차검증, gated)

> 상태: Accepted
> 결정일: 2026-06-01
> Phase: 11 (LLM Gateway A안) — 제품 phase (런타임 有, behavior-preserving)
> 관련: 제안서 `meta/proposals/2026-05-31_llm-gateway-design.md`(§3~§7 + §18.A) / ADR-018·029(Critic canonical) / ADR-027(MOA orchestrator) / CC-010(cost_control)
> ★ behavior-preserving (기존 0 수정) + gated default-off + flagship 기본 호출 0 + 키 commit 0

---

## Context

agents(intent/planning/critic/rewriter/memory)가 **concrete 모델명(config Field)에 직접 의존**하고 OpenAI SDK 호출이 agent 마다 산재 → provider 추가 시 N개 agent 동시 수정 필요. 모델 선택은 static config + 하드코딩, provider 추상화 없음(repo grep 0건). 단일 모델 self-bias 를 줄일 교차검증 seam 도 부재(제안서 §1~§2). 

사용자 결정(제안서 §18): **A안 먼저 구현**(OpenAI 보존 + Critic 교차검증만 추가, 최소 비용) → **B안은 후속 phase 지침**(3-provider 다양성). 빌드는 키 준비 후. ★ 가속 빌드 — 코드 S1·S2·S3 선완료(pytest 435), 본 ADR 은 retroactive 정식화.

## Decision

**LLM Gateway**(registry / alias / adapter)를 신규 레이어로 도입한다. agent 는 "무엇을(**alias** = 논리명)"만 알고, "어떤 모델/provider 로(**registry**)"는 gateway 가 결정한다. 그 위에 다른 family(Gemini) **1회 교차검증**(Critic 의 추가 pass)을 **gated default-off** 로 붙인다.

### 핵심 결정 (제안서 §3~§7)
1. **registry** (`llm/registry.py`) — concrete 모델 카탈로그: gpt-4o-mini / gpt-4o / gemini-cross(model_id=`settings.cross_validation_model`). provider/json_mode/max_tokens/cost/tier_allowed.
2. **alias** (`llm/aliases.py`) — 논리명 → registry key (tier×mode 입력). planning/intent/rewriter/memory→gpt-4o-mini, **critic={standard:gpt-4o, cost_saving:gpt-4o-mini}**(현 cost_saving 폴백 선언적 정식화), cross_validation→gemini-cross(gated).
3. **gateway** (`llm/gateway.py`) — `complete(alias, messages, *, tier, mode, ...)` 단일 진입 + `resolve_model(alias, tier, mode)`. adapter 선택(openai/google) + graceful 키 부재(LLMError).
4. **adapter** (`llm/providers/`) — ProviderAdapter Protocol + OpenAIAdapter + GeminiAdapter. ★ provider 추가 = adapter 1개 + registry 항목, **agent 코드 0 변경**.
5. **cross_validation** (`llm/cross_validation.py`) — Gemini 독립 8차원 평가(Critic canonical 동형) + `compare`(consensus / divergence / human_review_needed). ★ 순수 함수(자동 연결 0) + graceful(키없음/503/빈출력/파싱실패 → CrossCheck available=False).
6. **gated orchestrator hook** (`moa_orchestrator §5.5`) — critic 후 recommended plan 1회 교차검증. ★ `cross_validation_enabled` default **False** → 미발화. True 시 **로깅만**(Envelope/output_schema 0 변경) + 모든 예외 graceful.

### behavior-preserving 보장 (제안서 §4.1 Stage A)
- ★ A안은 **gateway 골격까지** — agents 미연결(Stage A 전환은 후속). 기존 agents 는 여전히 `client or OpenAI(...)` 직접 호출 → 기존 동작 100% 보존.
- `resolve_model("planning")==gpt-4o-mini`(= 현 settings.openai_model_default), `("critic","-","standard")==gpt-4o`(= 현 settings.openai_model_critic) — 단위 test 로 byte-identical 강제.
- cross_validation 은 gated default-off + 로깅만 → /generate Envelope = Phase 10 byte-identical.

### Gemini 튜닝 (제안서 §18.A)
- 기본값 `cross_validation_model=gemini-3.5-flash`(회복됨, 사용자 확정). thinking_budget=0(빈출력 회피) + **503 시 graceful + 재시도** + text fallback. 503 transient 시 fallback `gemini-3-flash-preview` / `gemini-2.5-flash`(`.env` 1줄).

## Result

- **LLM Gateway 골격** — registry/alias/gateway + openai/gemini adapter. agent=alias / gateway=provider 결정. pytest 381 → **435**(+54: gateway 31 + cross-val 19 + wiring 4). 기존 381 green(수정 0).
- **cross_validation** — Gemini 독립 8차원 + compare. ★ 라이브 consensus 입증(gemini-2.5-flash overall 0.7375 vs OpenAI Critic 0.72 → score_delta 0.0175 ≤ 0.2 → consensus).
- **gated default-off** — cross_validation_enabled=False → orchestrator hook 미발화 → 기존 흐름 100% 동일. 발화 시 로깅만(Envelope 불변).
- ★ behavior-preserving(기존 0 수정) + flagship 기본 호출 0(premium_review gated/A안 미구현) + 키 commit 0(registry env 참조만) + agent 6 유지(cross_validation = Critic 추가 pass).

## Consequences

### 긍정
- **provider 추상화 토대** — agent 가 concrete 모델명 의존 제거 → 후속 provider 추가 = adapter + registry, agent 코드 0 변경. 모델 교체 = `.env` 1줄.
- **self-bias 완화** — 생성=mini / 검증=gpt-4o / 교차검증=Gemini(다른 family). multi-llm-validation 정신을 런타임에 반영. consensus/divergence 관측.
- **정책 단일화** — cost_saving 의 "Critic gpt-4o→mini 폴백" 분산을 alias 표로 선언적 정식화(제안서 §6).
- **안전한 도입** — gated default-off + 로깅만 → 기존 사용자 흐름 불변. 활성/노출은 후속 + output_schema CC.

### 제약 / 한계
- **agents 미연결(Stage A 후속)** — gateway 가 만들어졌으나 agents 는 아직 직접 OpenAI SDK. Stage A 전환(2줄 교체)은 후속 phase.
- **cross_validation 로깅만** — 결과 응답 노출 0(output_schema contract-change 대상, 후속).
- **Gemini 503 transient** — gemini-3.5-flash 수요 급증 시 503. graceful 처리되나 라이브 시 fallback model 필요.
- **라이브 full /generate 데모 미실행** — wizard 전체 흐름(start→quick.initial→clarify→direction→generate) + flag ON 데모는 후속(test_integration_mvp 가 mock 으로 전체 커버).

## Non-Goals (재확인)
- provider 자동 활성(키없음 graceful skip) / Opus·flagship 기본 호출(premium_review gated, A안 미구현) / output_schema·Envelope 변경 / MOA agent 수 증가(cross_validation = Critic pass) / B안 3-provider(후속) / agents Stage A·B 전환(후속) / 실 키 평문 commit.

## 다음
- agents Stage A 전환(gateway 경유 OpenAI, 제안서 T-2) → B안(3-provider + Anthropic adapter + cost 재조정, §18.B) → cross_validation 응답 노출(output_schema CC) + full 라이브 /generate 데모.
