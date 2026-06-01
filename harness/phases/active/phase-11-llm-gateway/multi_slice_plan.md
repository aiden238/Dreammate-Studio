# Phase 11 — Multi-Slice Plan

> 3 Slice (sub-agent, sequential) — 코드 선완료(commit·push) + entry/close(retroactive 문서). 제품 phase — 런타임 有, behavior-preserving + gated default-off.

## Wave 구조 (실제 진행)
```
S1 [LLM Gateway 골격]                  (commit e1422a6)
  ↓
S2 [cross_validation 모듈 + Gemini 튜닝] (commit f382b6e)
  ↓
S3 [orchestrator gated hook]            (commit 1ee1c08)
  ↓
entry/close (본 문서, retroactive)       — 8 entry + closing_notes + ADR-039 + CC-010 + retrospective (★ 코드 0 변경)
```

## Slice 1 — LLM Gateway 골격 (commit `e1422a6`)
1. `llm/types.py` — canonical LLMMessage/LLMRequest/LLMResponse/Usage.
2. `llm/errors.py` — LLMError(provider 에러 래핑).
3. `llm/registry.py` — gpt-4o-mini / gpt-4o / gemini-cross(model_id=settings.cross_validation_model).
4. `llm/aliases.py` — planning/intent/rewriter/memory→gpt-4o-mini, critic={standard:gpt-4o, cost_saving:gpt-4o-mini}, cross_validation→gemini-cross.
5. `llm/gateway.py` — LLMGateway.complete(alias,...) + resolve_model + graceful 키 부재 + adapter 선택(openai/google).
6. `llm/providers/{base,openai_adapter,gemini_adapter}.py` — ProviderAdapter Protocol + OpenAI/Gemini.
7. `config.py` additive(google_api_key / cross_validation_model) + requirements.txt + test_llm_gateway(31).
- editable: `backend/fastapi/llm/**`, `config.py`(additive), `requirements.txt`, `tests/test_llm_gateway.py`
- forbidden: agents/routers/orchestration/eval/contracts/frontend 수정. 기존 Field 삭제/rename.
- acceptance: resolve_model byte-identical(A2) + 31 test green + 기존 381 무영향.

## Slice 2 — cross_validation 모듈 + Gemini 튜닝 (commit `f382b6e`)
1. `llm/cross_validation.py` — cross_validate(Gemini 8차원, graceful) + compare(consensus/divergence/recommendation). ★ 순수 함수(자동 연결 0).
2. `llm/providers/gemini_adapter.py` 수정 — thinking_budget=0 + 503 재시도 + text fallback.
3. `config.py` additive — cross_validation_enabled(default False) + gemini_thinking_budget.
4. test_llm_cross_validation(19) — graceful + compare(consensus/divergence/unavailable), mock DI(실 API 0).
- editable: `backend/fastapi/llm/cross_validation.py`, `llm/providers/gemini_adapter.py`, `config.py`(additive), `tests/test_llm_cross_validation.py`
- forbidden: orchestrator/agents/routers 자동 연결(S3에서 gated), 기존 test 수정, 키 commit.
- acceptance: cross_validate graceful + compare 정확 + 19 test green + 기존 무영향.

## Slice 3 — orchestrator gated hook (commit `1ee1c08`)
1. `orchestration/moa_orchestrator.py` 수정(additive, gated) — §5.5 cross-validation hook: critic 후 recommended plan 1회 교차검증. ★ cross_validation_enabled default OFF → 미발화. True 시 cross_validate + compare + **로깅만**. per_plan_verdicts 누적(additive). 모든 예외 graceful.
2. test_cross_validation_wiring(4) — OFF 미발화(기존 흐름 동일) + ON 발화 + graceful, mock DI.
- editable: `backend/fastapi/orchestration/moa_orchestrator.py`(additive gated), `tests/test_cross_validation_wiring.py`
- forbidden: Envelope/output_schema 변경, 기존 critic/Rewriter 흐름 변경, default-on, 키 commit.
- acceptance: OFF 시 Envelope byte-identical(A6) + ON 시 hook 발화 + 4 test green + 기존 381 green.

## entry/close (본 retroactive 문서 — ★ 코드 0 변경)
1. 8 entry(goals/scope/non_goals/dependencies/acceptance/assumptions/multi_slice_plan/notes) + closing_notes.
2. ADR-039(`docs/decisions/phase_11_llm_gateway.md`).
3. contract-change CC-010 — `cost_control_policy.md` additive 확장 + `docs/contract_changes/2026-06-01_phase-11-cost-control.md`.
4. `meta/retrospectives/phase-11.md`.
- editable: 위 문서들만. forbidden: ★ backend/fastapi/** , apps/web/** , tests , 기존 다른 contracts (코드 0 변경).

## 충돌 매트릭스 (코드 Slice)
| Slice | llm/(gateway) | llm/cross_validation+gemini | orchestration+wiring test |
|---|---|---|---|
| S1 | ✅ | ❌ | ❌ |
| S2 | ❌ | ✅ | ❌ |
| S3 | ❌ | ❌ | ✅ |
Sequential 충돌 0.

## P-X1 streak
| Phase | streak |
|---|---|
| Phase 10 | 60 |
| Phase 11 | +3 (S1·S2·S3) |
| 누적 | **63** |

## 시간 추정 (실측 — 가속 빌드)
S1 + S2 + S3 코드 ~수h(가속) + entry/close(retroactive 문서) ~1.5h.
