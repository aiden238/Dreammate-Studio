# Phase 11 — Acceptance (A1~A8 + MG1~MG3)

| ID | 항목 | 검증 | Slice |
|---|---|---|---|
| **A1** | LLM Gateway 골격 — `llm/` 패키지(types/errors/registry/aliases/gateway + providers). agent=alias / gateway=provider 결정 | test_llm_gateway green (31) | S1 |
| **A2** | alias→model = 현 default **byte-identical** — `resolve_model("planning")==gpt-4o-mini` / `("critic","-","standard")==gpt-4o` / `("critic","-","cost_saving")==gpt-4o-mini` | gateway 단위 test 강제 | S1 |
| **A3** | cross_validation 모듈 — cross_validate(Gemini 8차원, graceful) + compare(consensus/divergence/human_review_needed). 순수 함수 | test_llm_cross_validation green (19) | S2 |
| **A4** | Gemini adapter 튜닝 — thinking_budget=0 + 503 재시도 + text fallback. config Field additive(graceful 키 부재) | gemini_adapter + config | S2 |
| **A5** | orchestrator gated hook — critic 후 1회 교차검증. ★ default OFF → 미발화 + ON 시 발화 + 로깅만 + graceful | test_cross_validation_wiring green (4) | S3 |
| **A6** | **gated default-off** — `cross_validation_enabled=False` → hook 미발화 → 기존 흐름 100% 동일(Envelope byte-identical) | wiring test OFF 경로 + test_integration_mvp | S3 |
| **A7-PP** | **behavior-preserving** — 기존 endpoint/agent/test 0 수정. pytest 381 → 435(신규/additive만) | pytest 기존 381 green + Envelope 불변 | 전 Slice |
| **A8** | **라이브 입증** — gateway 경유 OpenAI 실 생성 + Gemini cross_validate 독립평가 + compare consensus | 수동 라이브(키 user-provided, CI 미실행) | S2/S3 |

## MG1~MG3 (메타)
| ID | 항목 | 검증 |
|---|---|---|
| **MG1** | ADR-039 (LLM Gateway + cross_validation, gated default-off) | docs/decisions/phase_11_llm_gateway.md |
| **MG2** | contract-change CC-010 — cost_control_policy 확장(tier×mode→alias + cross_validation 비용, ★ additive) | docs/contract_changes/2026-06-01_phase-11-cost-control.md |
| **MG3** | P-X1 §SELF-VERIFICATION 연속 유지 (60 → 63, S1·S2·S3) | sub-agent/commit 검사 |

## ★ behavior-preserving 게이트 (A7-PP — 제품 phase 핵심)
```
신규/additive만 — 기존 endpoint 응답 schema / 기존 agent / 기존 test 수정 0
gateway: 신규 llm/ 레이어 (agents 미연결 — Stage A 후속). 기존 OpenAI 직접 호출 경로 불변
cross_validation: 순수 함수 + orchestrator gated hook(default OFF). 발화 시에도 로깅만 — Envelope 0 변경
검증: pytest 기존 381 전부 green (신규 +54: gateway 31 + cross-val 19 + wiring 4)
```

## ★ gated default-off 게이트 (A6 — 안전 핵심)
```
cross_validation_enabled default False → moa_orchestrator §5.5 hook 미발화
→ /generate Envelope = Phase 10 와 byte-identical (test_integration_mvp 가드)
True 시: critic 후 Gemini 1회 교차검증 + 로깅(model/gemini_score/openai_score/agreement/recommendation)
         — 모든 예외 graceful 흡수(logger.exception), 응답 무영향
활성 = 명시적 flag(CROSS_VALIDATION_ENABLED) + GOOGLE 키 opt-in (CI 미실행, 키 commit 0)
```

## ★ 라이브 입증 (A8 — handoff §2 기록)
```
gateway 경유 OpenAI 실 생성 ✅ (alias "planning"→gpt-4o-mini = 현 default byte-identical)
cross_validate Gemini 독립 8차원 평가 + compare(consensus/divergence) ✅
  예: gemini-2.5-flash overall 0.7375 vs OpenAI Critic 0.72 → score_delta 0.0175 ≤ 0.2 → consensus 입증
⚠️ gemini-3.5-flash 503 transient(Google 수요 급증) — graceful 처리. fallback: gemini-3-flash-preview / gemini-2.5-flash
키 commit 0 (.env user-provided)
```

## 회귀 baseline (Phase 10 → Phase 11)
| 지표 | Phase 10 final | Phase 11 |
|---|---|---|
| pytest | 381 | **435** (+54: gateway 31 + cross-val 19 + wiring 4. 기존 381 green, 수정 0) |
| gated default-off | — | **cross_validation_enabled=False** (Envelope 불변) |
| 라이브 교차검증 | — | **consensus 입증** (Gemini vs OpenAI, 수동) |
| agent 수 | 6 | **6 유지** (cross_validation = Critic 추가 pass, 새 agent 0) |
| P-X1 streak | 60 | **63** (S1·S2·S3) |
| contract-change | CC-009 | **CC-010** (cost_control additive, 누적 11회) |
| PlanCard / component_map 0줄 | 35 / 45 | **유지** (frontend 0 변경) |
| 키 commit | 0 | **0 유지** (.env user-provided, registry env 참조만) |

## qa-check (Phase 11 — release gate)
- 2 AI 구조(gateway/alias/cross_validation) / 8 큰 결정(ADR-039 + ai-architecture-review) / 11 비용(cost_control CC-010 additive) 중심 — behavior-preserving + gated default-off 게이트 PASS 예상.
