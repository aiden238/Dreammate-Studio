# Phase 11 — Scope (제품 phase — 런타임 有, behavior-preserving)

> ★ 가속 빌드: 코드 S1·S2·S3 는 이미 완료·commit·push (pytest 435). 본 entry 는 retroactive 정식화.

## 포함 (In-Scope)

### S1 — LLM Gateway 골격 (commit `e1422a6`)
| 항목 | 작업 |
|---|---|
| `backend/fastapi/llm/types.py` | **신규** — canonical LLMMessage / LLMRequest / LLMResponse / Usage (provider-neutral) |
| `backend/fastapi/llm/errors.py` | **신규** — LLMError (provider 에러를 canonical 로 래핑) |
| `backend/fastapi/llm/registry.py` | **신규** — concrete 모델 카탈로그 (gpt-4o-mini / gpt-4o / gemini-cross). Gemini model_id = `settings.cross_validation_model` |
| `backend/fastapi/llm/aliases.py` | **신규** — 논리 alias → registry key (tier×mode 입력). critic={standard:gpt-4o, cost_saving:gpt-4o-mini} |
| `backend/fastapi/llm/gateway.py` | **신규** — LLMGateway.complete(alias,...) 단일 진입 + resolve_model + graceful 키 부재 |
| `backend/fastapi/llm/providers/{base,openai_adapter,gemini_adapter}.py` | **신규** — ProviderAdapter Protocol + OpenAI/Gemini 구현 |
| `backend/fastapi/config.py` | **수정 (additive)** — `google_api_key` / `cross_validation_model` Field (기존 Field 보존) |
| `backend/fastapi/tests/test_llm_gateway.py` | **신규** — alias→model 해석(현 default byte-identical) + registry + 에러 정규화 + DI mock |
| `backend/fastapi/requirements.txt` | **수정 (additive)** — google-genai 등 |

### S2 — cross_validation 모듈 + Gemini 튜닝 (commit `f382b6e`)
| 항목 | 작업 |
|---|---|
| `backend/fastapi/llm/cross_validation.py` | **신규** — cross_validate(Gemini 독립 8차원 평가, graceful) + compare(consensus/divergence/recommendation). 순수 함수(자동 연결 없음) |
| `backend/fastapi/llm/providers/gemini_adapter.py` | **수정** — thinking_budget=0(빈출력 회피) + 503 재시도 + text fallback |
| `backend/fastapi/config.py` | **수정 (additive)** — `cross_validation_enabled`(default False) / `gemini_thinking_budget` Field |
| `backend/fastapi/tests/test_llm_cross_validation.py` | **신규** — cross_validate graceful + compare(consensus/divergence/unavailable) 단위 (실 API 0, mock DI) |

### S3 — orchestrator gated hook (commit `1ee1c08`)
| 항목 | 작업 |
|---|---|
| `backend/fastapi/orchestration/moa_orchestrator.py` | **수정 (additive, gated)** — critic 단계 후 §5.5 cross-validation hook. ★ `cross_validation_enabled` default OFF → 미발화. True 시 recommended plan 1회 교차검증 + **로깅만**. per_plan_verdicts 누적(additive). 모든 예외 graceful |
| `backend/fastapi/tests/test_cross_validation_wiring.py` | **신규** — gated OFF 시 미발화(기존 흐름 동일) + ON 시 hook 발화 + graceful (mock DI) |

### 본 entry (문서 정식화 — ★ 코드 0 변경)
| 항목 | 작업 |
|---|---|
| `phases/active/phase-11-llm-gateway/` 8 entry + closing_notes | **신규** |
| `docs/decisions/phase_11_llm_gateway.md` (ADR-039) | **신규** |
| `docs/contracts/cost_control_policy.md` | **수정 (contract-change CC-010, ★ additive)** — tier×mode→alias 표 + cross_validation 비용 |
| `docs/contract_changes/2026-06-01_phase-11-cost-control.md` (CC-010) | **신규** |
| `meta/retrospectives/phase-11.md` | **신규** |

## contract-change 대상 (MG2)
- `cost_control_policy.md` (tier×mode→alias 표 + cross_validation 비용) — **CC-010** (★ additive, behavior-preserving)

> ★ A안 범위에서 다른 contract(tech_stack / agent_io / prompt_registry / moa_policy)는 **소폭 노트** 후보(제안서 §10)이나, agents 가 아직 gateway 미연결(Stage A 후속) → IO 스키마/prompt 본문 불변. 본 phase 는 cost_control 만 정식 확장.

## ★ 변경 허용 / 금지

```
변경 허용 (editable — 본 entry 문서 작업):
  phases/active/phase-11-llm-gateway/**
  docs/decisions/phase_11_llm_gateway.md (ADR-039)
  docs/contracts/cost_control_policy.md           (contract-change CC-010, ★ additive 확장)
  docs/contract_changes/2026-06-01_phase-11-cost-control.md (CC-010)
  meta/retrospectives/phase-11.md

변경 금지 (forbidden — 본 entry 작업):
  ★ 코드 0 변경 — backend/fastapi/** , apps/web/** (S1·S2·S3 선완료, pytest 435 무관)
  ★ Envelope / output_schema 변경
  ★ 기존 다른 contracts (tech_stack / agent_io / prompt_registry / moa_policy / db_schema)
  ★ tests 0 수정
  ★ 실 키 평문 (registry 는 env 참조만, .env user-provided)
  영상 제작/편집 (MVP 영구 non-goal)
```

## 변경 수 (코드 — 이미 완료)
- S1: 신규 11 + 수정 2 (config additive + requirements). +394 test.
- S2: 신규 1 + 수정 2 (gemini_adapter + config additive). +cross-val test.
- S3: 수정 1 (moa_orchestrator additive gated) + 신규 1 test.
- pytest: 381 → **435** (+54: gateway 31 + cross-val 19 + wiring 4). 기존 381 green, 기존 수정 0.

## 변경 수 (문서 — 본 entry)
- 신규: ~12 (entry 8 + closing_notes + ADR-039 + CC-010 로그 + retrospective). 수정: 1 (cost_control_policy additive).
