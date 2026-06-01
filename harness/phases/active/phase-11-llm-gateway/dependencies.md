# Phase 11 — Dependencies

## 선행 phase (Phase 1~10 누적)
| 의존 | Phase 11 에서 |
|---|---|
| Phase 1 `/api/v1/generate` + 3안 + Critic | gateway 가 감싸는 LLM 호출 패턴(agents 직접 OpenAI SDK + DI hook) |
| Phase 4 3-plan (`run_planning_parallel_3`) | registry/alias 가 모델 선택 추상화하는 대상 (A안은 동일 모델 유지) |
| Phase 4.5/6 Critic canonical (`normalize_to_canonical`, 0–5→0–1, ADR-018) | cross_validation 의 `compare` 가 같은 축(overall_score/dimensions 0–1)으로 비교 |
| Phase 8 MOA orchestrator (`moa_orchestrator.generate_plan`) | ★ cross-validation gated hook 삽입 지점(critic 단계 후). call-time namespace 해석(monkeypatch 보존) 계승 |
| Phase 9 selected_plans/feedback + per-plan canonical | recommended plan 의 critic canonical(per_plan_verdicts) 추출 — cross_validation 비교 입력 |
| Phase 10 behavior-preserving 통합 (pytest 381, test_integration_mvp) | ★ baseline — gated OFF 시 Envelope byte-identical 가드 |

## 설계 근거 (★ 메인)
- `meta/proposals/2026-05-31_llm-gateway-design.md` — 전체 설계(§1~§18). 특히:
  - §3 디렉터리 구조 / §4 Stage A behavior-preserving / §5 registry·alias / §6 cost_control 확장안 / §7 cross_validation gated / §11 migration M0~M5 / §18.A A안 + §18.0 모델 + §18.C 키 + §18.D cost 재조정.
- `meta/handoffs/2026-06-01_llm-gateway-handoff.md` — 세션 상태 + S1~S3 요약 + 키/모델 상태(gemini-3.5-flash 503 transient, fallback gemini-3-flash-preview).

## 구현 의존 (S1·S2·S3 — 선완료)
- `backend/fastapi/config.py` Phase 11 Field: `google_api_key` / `cross_validation_model`(default gemini-3.5-flash) / `cross_validation_enabled`(default False) / `gemini_thinking_budget`.
- `backend/fastapi/agents/critic.py` DIMENSIONS(8차원) — cross_validation CROSS_DIMENSIONS 동형.
- google-genai SDK (requirements.txt additive) — gemini_adapter.
- ★ DI 패턴(client/adapter 주입) — 테스트 mock → 실 API 0.

## contract 의존 (CC-010)
- `docs/contracts/cost_control_policy.md` — 확장 대상(현: user tier 무료/유료 + 호출당/세션당/일일 상한 + cost_saving Critic 폴백). ★ additive 확장 (tier×mode→alias 표 + cross_validation 비용).
- `docs/contracts/agent_io_contract.md` §9 (호출당 상한) — cost_control 의 단일 출처 참조(본 phase 미수정).

## Skill 의존
- `contract-change`(CC-010 cost_control) / `ai-architecture-review`(gateway 도입 — 큰 결정, ADR-039) / `multi-llm-validation`(생성≠검증≠교차검증 정신) / `phase-start`/`phase-complete`/`meta-retrospective` / (후속) `cost-review`(cross_validation 활성 시 비용 점검).

## 비의존 / 경계
- apps/web/** (frontend — provider 직접 호출 절대 없음, frontend→backend API만) / 영상 제작(영구 non-goal) / B안 provider(Anthropic/Grok adapter — 후속) / agents Stage A·B 전환(후속).
- ★ behavior-preserving: 기존 endpoint/agent/test 에 의존하되 **변경하지 않음** (gateway 는 신규 레이어, cross_validation 은 gated additive).
