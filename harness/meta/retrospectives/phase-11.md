# Phase 11 회고 — LLM Gateway A안 (cross-validation, 제품 phase)

> 종료일: 2026-06-01
> 유형: 제품 phase (런타임 有, behavior-preserving + gated default-off) — ★ 가속 빌드(코드 S1·S2·S3 선완료, entry 는 retroactive 정식화)
> 결과: ✅ LLM Gateway(alias→provider) + Gemini 교차검증(gated default-off) / pytest 381→435 / behavior-preserving / 라이브 consensus 입증 / 키 commit 0
> 트리거: phase-complete v1.2.0 §7 (retroactive)

---

## 1. 무엇을 했나 (3 Slice + 문서 정식화)
- **S1 (`e1422a6`)**: LLM Gateway 골격 — `llm/` 패키지(types/errors/registry/aliases/gateway + providers/base·openai_adapter·gemini_adapter) + config additive(google_api_key/cross_validation_model) + test_llm_gateway(31). agents 미연결(behavior-preserving). pytest 381→412.
- **S2 (`f382b6e`)**: cross_validation 모듈(cross_validate + compare, 순수 함수) + Gemini adapter 튜닝(thinking_budget=0 + 503 재시도 + text fallback) + config additive(cross_validation_enabled default False / gemini_thinking_budget) + test_llm_cross_validation(19). pytest 412→431.
- **S3 (`1ee1c08`)**: moa_orchestrator §5.5 gated hook(critic 후 1회 교차검증, default OFF, 로깅만, Envelope 불변, graceful) + per_plan_verdicts additive + test_cross_validation_wiring(4). pytest 431→435.
- **문서 정식화 (retroactive)**: entry 8 + closing_notes + ADR-039 + cost_control CC-010(additive) + 본 회고. ★ 코드 0 변경.

## 2. 핵심 결과
- **LLM Gateway 골격** — agent=alias / gateway=provider 결정. registry(gpt-4o-mini/gpt-4o/gemini-cross) + alias(critic={standard:gpt-4o, cost_saving:gpt-4o-mini}) + openai/gemini adapter. provider 추가 = adapter + registry, agent 코드 0 변경 토대.
- **pytest 381 → 435** (+54: gateway 31 + cross-val 19 + wiring 4). 기존 381 green(수정 0).
- **cross_validation** — Gemini 독립 8차원(Critic canonical 동형) + compare(consensus/divergence/human_review_needed). ★ gated default-off + 로깅만.
- **라이브 consensus 입증** — gateway 경유 OpenAI 실 생성 + Gemini cross_validate(gemini-2.5-flash overall 0.7375 vs OpenAI Critic 0.72 → score_delta 0.0175 ≤ 0.2 → consensus).
- **cost_control CC-010** — tier×mode→alias 표 + cross_validation 비용(Gemini 1회, gated) additive. 기존 §1~§10 보존.

## 3. 잘된 것
1. **behavior-preserving 4-Slice 가속** — 가속 빌드(코드 선완료)임에도 4 단계(S1·S2·S3 + 문서) 모두 기존 endpoint/agent/test 0 수정. gateway 신규 레이어(agents 미연결) + cross_validation gated default-off + 로깅만. P-BEHAVIOR-PRESERVING-001 정신을 LLM 추상화 phase 로 확장. 기존 381 green.
2. **라이브 교차검증 입증** — mock 만이 아니라 실제 gateway 경유 OpenAI 생성 + Gemini 독립평가 + compare consensus 까지 라이브 확인. single-model self-bias 완화 capability 실증.
3. **gateway 추상화** — agent 가 concrete 모델명 의존 제거(alias). provider 추가 = adapter 1개 + registry 항목, agent 코드 0. ADR-039 의 "agent=무엇(alias), gateway=어떻게(provider)" 분리 실현.
4. **모델 교체 = env 1줄** — Gemini model_id = `settings.cross_validation_model`. gemini-3.5-flash 503 transient 시 `.env` 에 `CROSS_VALIDATION_MODEL=gemini-3-flash-preview` 1줄로 fallback. 코드 0 변경.
5. **gated default-off 화해** — "교차검증 추가"(A안) ↔ "기존 동작 불변"(behavior-preserving) 표면 모순을 capability(구축) vs 발화(gated, opt-in) 로 분리. Phase 10 P-CAPABILITY-DEFAULT-OFF-001 계승. 비용 증가 0(default).

## 4. 아쉬운 것 / 한계
1. **gemini-3.5-flash 503 transient** — 2026-06-01 Google 수요 급증으로 기본 모델 503 지속(retryDelay 22s). graceful 처리되나 라이브 시 fallback model(gemini-3-flash-preview / gemini-2.5-flash) 필요. 회복 후 기본값 복귀.
2. **full /generate wizard 데모 미실행** — Quick 모드 라이브는 wizard 단계(start→quick.initial→clarify→direction→generate) 필요. 전체 흐름 + flag ON cross_validation 로그 라이브 데모는 후속(test_integration_mvp 가 mock 으로 전체 커버).
3. **agents Stage A 미전환** — gateway 가 만들어졌으나 agents 는 아직 직접 OpenAI SDK(`client or OpenAI(...)`). Stage A 전환(2줄 교체, 제안서 T-2)은 후속 phase. gateway 는 cross_validation 경로로만 라이브 사용 중.
4. **cross_validation 로깅만** — 결과 응답 노출 0(output_schema contract-change 대상, 후속). consensus/divergence UX 미구현.
5. **B안 미착수** — 3-provider 다양성(GPT/Claude/Gemini 3-plan) + cost 전면 재조정은 후속 phase 지침(제안서 §18.B). 키 3개 준비됨.

## 5. 패턴
- **P-X1-EFFECT-001 update (63연속)** — S1·S2·S3 sub-agent forbidden 검사 연속(Phase 10 60 → 63).
- **P-LLM-GATEWAY-001 (신규 후보)** — agent=alias / gateway=provider 결정 레이어 도입(registry/alias/adapter) + provider 추가 시 agent 0 변경 + 모델 교체 env 1줄. behavior-preserving(agents 미연결 Stage A 후속).
- **P-BEHAVIOR-PRESERVING-001 update** — LLM 추상화 phase 에서도 기존 0 수정 + 신규/additive(gateway 신규 레이어) + gated default-off(cross_validation hook). pytest 381→435 기존 green.
- **P-CAPABILITY-DEFAULT-OFF-001 update** — cross_validation = capability 구축(S1~S3) vs 발화(gated default-off). "추가" ↔ "불변" 모순 화해 재사용(Phase 10 eval mode 계승).
- **P-CONTRACT-FIRST-001 update** — CC-010(cost_control additive) 누적 11회.

## 6. 다음 단계
- **agents Stage A 전환** — `client or OpenAI(...)` → `gateway.openai_client()` + `resolve_model(alias,...)` 2줄(제안서 §4.1·T-2, behavior-preserving). gateway 경유 OpenAI 호출.
- **B안 (Phase 12+)** — 3-provider 다양성 + Anthropic adapter + **cost_control 전면 재조정**(신모델 5~7배, 제안서 §18.B·§18.D) + multi-llm-validation + eval-run(provider 간 품질·비용 비교).
- **orchestrator 라이브 데모** — full /generate wizard 전체 흐름 + flag ON cross_validation 로그 라이브 확인.
- **cross_validation 응답 노출** — output_schema contract-change + consensus/divergence UX.

## 7. 메타 정합
- LLM Gateway 추상화 토대 + 교차검증 capability(gated) — provider 다양성 확장 발판.
- behavior-preserving + gated default-off + 로깅만 + 키 0 — 제품 안정화 phase 규율 유지.
- ★ Phase 1~11 = MVP 통합(Phase 10) + LLM Gateway A안(Phase 11). 다음 = agents Stage A 전환 / B안 / 배포 Gate B~G.
