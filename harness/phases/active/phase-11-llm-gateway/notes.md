# Phase 11 — Notes

## 진입 맥락
- Phase 10(MVP 통합) + 배포 Gate A 통과 후, 제안서(`meta/proposals/2026-05-31_llm-gateway-design.md`) 검토 → 사용자 결정: **A안 먼저 구현, B안은 후속 phase 지침**.
- ★ **가속 빌드**: 코드 S1·S2·S3 가 entry 문서 작성보다 먼저 완료·commit·push(pytest 435). 본 entry 는 **retroactive 정식화** — 코드 0 변경, 문서만.

## ★ A안 = "OpenAI 보존 + Gemini 교차검증만" (핵심)
```
A안 (Phase 11)  : 기존 OpenAI 동작 보존 + gateway(alias→provider) + Critic 교차검증(Gemini, gated). 최소 비용.
B안 (후속)       : GPT/Claude/Gemini 3-plan 다양성 + critic=Sonnet. cost_control 전면 재조정 (제안서 §18.B).
구현 단계        : Stage A(gateway 골격)까지 — agents Stage A 전환(2줄 교체)/Stage B(canonical)는 후속.
```

## ★ behavior-preserving + gated 화해 (표면 모순 해소)
```
"교차검증 추가"(A안) ↔ "기존 동작 불변"(behavior-preserving) — 모순 아님:
  gateway       = agents 아래 신규 레이어 (agents 미연결 — Stage A 후속). 기존 OpenAI 직접 호출 불변.
  cross_validation = 순수 함수 + orchestrator gated hook(default OFF) + 로깅만. Envelope/output_schema 0 변경.
→ "추가"(capability 구축) vs "발화"(gated, opt-in). Phase 10 P-CAPABILITY-DEFAULT-OFF-001 정신 계승.
```

## 6 핵심 항목 → Slice
| 항목 | Slice |
|---|---|
| LLM Gateway 골격(registry/alias/gateway + adapter) | S1 |
| alias→model byte-identical(현 default 보존) | S1 |
| cross_validation 모듈(cross_validate + compare) | S2 |
| Gemini adapter 튜닝(thinking_budget=0 + 503 재시도 + text fallback) | S2 |
| orchestrator gated hook(critic 후, 로깅만) | S3 |
| cost_control 확장(tier×mode→alias + cross_validation 비용, CC-010) | entry/close 문서 |

## ★ 안전 게이트
```
behavior-preserving : 기존 endpoint/agent/test 0 수정 (신규/additive만, pytest 381→435)
gated default-off    : cross_validation_enabled=False → hook 미발화 (기존 흐름 100% 동일)
로깅만              : cross_validation = Envelope/output_schema/응답 0 변경 (노출은 후속 CC)
flagship 기본 호출 0 : premium_review gated/A안 미구현. cross_validation = Gemini flash 저가 1회
키 0                : registry env 참조만 + .env user-provided + commit/채팅 평문 금지
P-X1                 : sub-agent forbidden 검사 연속 (60→63)
```

## 모델/키 메모 (★ 보안 — handoff §3)
- 키(OPENAI/ANTHROPIC/GOOGLE) = .env user-provided + .gitignore. **파일/commit/채팅 평문 절대 금지**. registry env 참조만.
- ★ 3개 키는 이전 노출 후 사용자 재발급 — 추가 노출 금지. Anthropic 오타(`ssk-ant`→`sk-ant`) 수정 완료.
- Gemini: 기본값 `cross_validation_model=gemini-3.5-flash`(사용자 확정). ⚠️ 2026-06-01 현재 503 transient(Google 수요 급증) — graceful. 라이브 시 `.env` 에 `CROSS_VALIDATION_MODEL=gemini-3-flash-preview`(임시 fallback), 회복 시 제거.

## 결정 대기 / 옵션
- cross_validation 결과 **응답 노출** — 현재 로깅만. 노출은 후속 + output_schema contract-change(NG3).
- agents Stage A 전환(2줄 교체, 제안서 T-2) — gateway 경유 OpenAI 호출. 본 phase 범위 밖(NG7).
- cross_validation 활성 시 cost_control 상한 반영 — CC-010 권고(additive Gemini 1회분).

## 다음 (Phase 11 이후)
- **agents Stage A 전환** — `client or OpenAI(...)` → `gateway.openai_client()` + `resolve_model(alias,...)` 2줄(제안서 §4.1, behavior-preserving).
- **B안 (Phase 12+)** — 3-provider 다양성(GPT/Claude/Gemini 3-plan) + Anthropic adapter + cost_control 전면 재조정(신모델 5~7배) + multi-llm-validation + eval-run(제안서 §18.B).
- **full 라이브 /generate 데모** — wizard 단계(start→quick.initial→clarify→direction→generate) + flag ON 으로 cross_validation 로그 라이브 확인.
- **cross_validation 응답 노출** — output_schema contract-change + consensus/divergence UX.
