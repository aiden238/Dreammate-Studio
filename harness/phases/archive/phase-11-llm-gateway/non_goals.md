# Phase 11 — Non-Goals

| ID | 항목 | 사유 |
|---|---|---|
| **NG1** | provider **자동 활성** (키 없으면 자동 사용) | ★ 키 없으면 graceful skip — gateway 가 `LLMError("missing key")` graceful, cross_validate 는 `CrossCheck(available=False)` 흡수. provider 활성 = 키 user-provided + 명시적 flag |
| **NG2** | Opus / GPT flagship **기본 호출** | ★ 스펙 금지 준수 — premium_review gated/off (A안 미구현, 제안서 §7). cross_validation 은 Gemini flash 1회만(저가). flagship 기본 경로 0 |
| **NG3** | **output_schema / Envelope 변경** | gateway 는 agent **아래 레이어** — Envelope 조립(orchestrator) 무관. cross_validation 결과는 **로깅만**, 응답 노출은 후속 + output_schema contract-change |
| **NG4** | **MOA agent 수 4 증가** | cross_validation = Critic 의 **추가 pass**(제안서 §7, moa_policy "4 agent 고정"). 새 agent 아님 |
| **NG5** | **B안 (3-provider 다양성)** | 후속 phase 지침(제안서 §18.B) — GPT/Claude/Gemini 3-plan + critic=Sonnet. cost_control 전면 재조정 + multi-llm-validation + eval-run 필요 |
| **NG6** | **Stage B (canonical `gw.complete()` 전환)** | agents 가 OpenAI SDK shape 제거하고 gateway.complete 호출로 전환 = 테스트 mock 갱신 수반 → provider 추가 phase 와 묶음(제안서 §4.1) |
| **NG7** | **agents Stage A 전환** (planning/critic 등 2줄 교체) | ★ A안 실구현은 gateway 골격 + cross_validation 까지. agents 의 `client or OpenAI(...)` → `gateway.openai_client()` 교체는 본 phase 범위 밖(제안서 T-2는 별도). agents 는 여전히 직접 OpenAI SDK 사용 — 기존 동작 100% 보존 |
| **NG8** | cross_validation **default 활성** | ★ `cross_validation_enabled` default False. CI/기존 사용자 흐름 미발화. 활성 = 명시적 flag(+GOOGLE 키) opt-in |
| **NG9** | cross_validation 결과의 **자동 채택/차단** | 로깅만 — verdict 비교(consensus/human_review_needed)는 관측 신호. revise 한도/Envelope/응답에 영향 0 |
| **NG10** | 영상 제작/편집 · TTS · BGM | ★ MVP **영구** non-goal (product_boundary) |
| **NG11** | 실 키 평문 (코드/commit/채팅) | ★ registry 는 env 참조만. .env user-provided + .gitignore. 키 commit 0 |

## ★ 핵심 원칙

1. **behavior-preserving**: 기존 endpoint/agent/test 0 수정 — 신규/additive + gated default-off (G6). pytest 381 green.
2. **gated default-off**: cross_validation_enabled=False → orchestrator hook 미발화 → 기존 흐름 100% 동일 (NG8).
3. **로깅만 (관측성)**: cross_validation 은 Envelope/output_schema/응답 0 변경 (NG3·NG9). 노출은 후속 contract-change.
4. **flagship 기본 호출 0**: premium_review gated/A안 미구현 (NG2). cross_validation = Gemini flash 저가 1회.
5. **A안 = Stage A 골격까지**: agents 전환(Stage A 2줄) / canonical(Stage B) / B안 / provider 추가는 후속 (NG5·NG6·NG7).
6. **키 0**: 실 키 평문 절대 금지 (NG11). graceful provider 비활성(NG1).

## 회피 패턴
- ❌ "gateway 만들었으니 agents 도 전환하자" → NG7 (Stage A 별도)
- ❌ "cross_validation 결과를 응답에 노출하자" → NG3·NG9 (로깅만, 후속 output_schema CC)
- ❌ "default 로 켜서 항상 교차검증하자" → NG8 (gated, opt-in)
- ❌ "Gemini 3-plan 도 추가하자" → NG5 (B안 후속, cost 재조정)
- ❌ "flagship 으로 premium 검증 붙이자" → NG2 (gated/A안 미구현)
- ❌ 실 키를 registry/config default 에 → NG11 (env 참조만)
