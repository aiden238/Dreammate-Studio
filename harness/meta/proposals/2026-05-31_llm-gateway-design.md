# Proposal: LLM Gateway / Model Registry / Alias / Tier 도입 설계

> 날짜: 2026-05-31
> 유형: **설계 제안 (proposal-only)** — ★ 코드/contract/endpoint/schema **0 변경**. 본 문서는 제안서일 뿐.
> 작성 근거: GPT 기획안 + Claude 구조 검토(13개 지정 문서 실측)
> 대상 phase: **Phase 11 후보** (제품 안정화/확장 — 현재는 설계만)
> 절차: contract-change/ai-architecture-review/multi-llm-validation 경유 (실 구현 시)
> 상태: **Draft 제안** (검토 → 승인 → 별도 phase 구현)

---

## 0. 판정 요약 (Claude 검토 결론)

GPT 기획안은 **타당하며 프로젝트와 정합**한다(tech_stack_contract "OpenAI 단일 + Anthropic Phase 5+ 검토" / config "multi-provider Phase 21+" / behavior-preserving 문화). 단 4가지를 **기존 자산 위에 매핑**하여 drift 를 막는다:

| GPT 원안 | Claude 보완 |
|---|---|
| 새 "plan tier" 개념 | 기존 `cost_control_policy` 의 **user tier(무료/유료) × cost mode(standard/cost_saving)** 위에 매핑 (새 축 추가 X) |
| premium_review 교차검증 | **Critic agent 가 대안 모델로 추가 pass** — 새 agent 아님(MOA 4 agent 불변, moa_policy 정합). gated/default-off |
| gateway 도입 | **DI(`client`)/monkeypatch 보존** + agents 가 **alias** 참조 → 339 test green(behavior-preserving) |
| model registry/alias | agents 가 concrete 모델명 의존 제거 → provider 추가 시 **agent 코드 0 변경** |

---

## 1. 현재 LLM 호출 구조 요약 (실측)

### 1.1 호출 패턴 (agents 직접 OpenAI SDK)
```python
# planning.py(127), critic.py(173), intent.py(82), rewriter.py 동일
_client = client or OpenAI(api_key=settings.openai_api_key)   # ① 직접 생성 (DI override 가능)
_model  = model or settings.openai_model_default               # ② static config 모델명
_client.chat.completions.create(model=_model, messages=[...], response_format={"type":"json_object"}, ...)
except OpenAIError: logger.exception(...); raise               # ③ 에러 전파 (planning 만 _fallback_plan_dict)
```
- **DI hook 존재**: 모든 agent 가 `client: OpenAI | None = None`, `model: str | None = None` 수용 (테스트 mock 주입용).
- **3-plan**: `run_planning_parallel_3()` 가 `settings.openai_models_for_3plan_list`(3개 슬롯) 기반 병렬 — 슬롯별 모델 다르게 가능, default 동일 모델×3.
- **orchestrator**: `moa_orchestrator.generate_plan()` 이 `plans_router.run_intent/run_planning_parallel_3/run_critic/run_rewriter` 를 **call-time namespace 해석**으로 호출 (monkeypatch 보존 목적).

### 1.2 모델 정책 (config.py — static)
| alias 역할 | 현재 config Field | 값 |
|---|---|---|
| 기본(Intent/Planning/Rewriter/Memory) | `openai_model_default` | gpt-4o-mini |
| Critic | `openai_model_critic` | gpt-4o |
| 3-plan 슬롯 | `openai_models_for_3plan_list` | [gpt-4o-mini]×3 |

### 1.3 비용 정책 (cost_control_policy.md)
- **user tier**: 무료/유료(Phase 11+). **cost mode**: standard / cost_saving / blocked.
- 호출당/세션당/일일 상한. cost_saving = **Critic 만 gpt-4o→gpt-4o-mini 폴백**.
- ★ "plan tier" / "model tier" / "premium" / registry / alias 개념 **없음**.

### 1.4 부재 (gap)
- gateway/registry/alias/router 레이어 **없음**(repo grep 0건).
- 모델 선택 = static config + 하드코딩. provider 추상화 없음.
- 교차검증(다른 모델로 재검) 없음.

---

## 2. 왜 LLM Gateway 가 필요한가

1. **호출 산재**: OpenAI 생성·모델선택·에러처리가 agent 마다 중복 → provider 추가 시 N개 agent 동시 수정 필요.
2. **모델 하드 결합**: agent 가 concrete 모델명(config Field)에 직접 의존 → 모델/provider 교체가 agent 코드 변경.
3. **정책 분산**: cost mode 기반 모델 폴백(Critic)이 cost_control_policy ↔ critic.py 양쪽에 흩어짐.
4. **교차검증 부재**: 단일 모델 self-bias. 고급 모델 1회 교차검증(premium_review)을 붙일 seam 없음.
5. **관측성**: 모델별 호출/비용/지연 로깅이 분산.

→ **Gateway = 단일 seam**. agent 는 "무엇을(alias)"만 알고, "어떤 모델/provider 로(registry)"는 gateway 가 결정. provider 추가 = adapter 1개 + registry 항목, agent 0 변경.

---

## 3. 제안 디렉터리 구조 — `harness/backend/fastapi/llm/`

```
backend/fastapi/llm/
├── __init__.py                 # 공개 API (get_gateway, LLMGateway, resolve_alias)
├── types.py                    # canonical LLMRequest / LLMResponse / Usage (provider-neutral)
├── registry.py                 # model_registry — concrete 모델 카탈로그 (provider/model_id/cost/limits/capabilities)
├── aliases.py                  # model_alias — 논리명("planning"/"critic"/"premium_review") → registry 해석 (tier×mode 입력)
├── gateway.py                  # LLMGateway — complete(alias, messages, ...) 단일 진입. 에러 정규화 + 로깅 + 비용 추정
├── errors.py                   # LLMError (OpenAIError 등 provider 에러를 canonical 로 래핑)
└── providers/
    ├── __init__.py
    ├── base.py                 # ProviderAdapter Protocol (.complete(model_id, messages, ...) -> LLMResponse)
    └── openai_adapter.py       # ★ 유일 구현 (OpenAI SDK 래핑). Anthropic/Gemini adapter 는 후속 phase
```

> ★ provider 추상화 **인터페이스만** 준비(`providers/base.py`). 실제 구현은 `openai_adapter.py` 하나. Anthropic/Gemini 는 §8(후속).

### 핵심 객체
- **model_registry**: `{ "gpt-4o-mini": {provider:"openai", model_id:"gpt-4o-mini", input_cost, output_cost, max_tokens, json_mode:true}, "gpt-4o": {...} }`. 현재는 OpenAI 2개.
- **model_alias**: 논리명 → registry 키. `{ "planning":"gpt-4o-mini", "critic":"gpt-4o", "rewriter":"gpt-4o-mini", "memory":"gpt-4o-mini", "premium_review": <gated> }`. tier×mode 가 입력(§6).
- **LLMGateway.complete(alias, messages, *, tier, mode, response_format, temperature, max_tokens, client=None) -> LLMResponse**.

---

## 4. OpenAI-only Gateway wrapping 방식 (★ behavior-preserving)

### 4.1 2단계 migration (스펙 "먼저 OpenAI-only wrapping" 준수)

**Stage A — OpenAI-only, 최소 침습 (behavior-preserving)**
- agents 의 두 줄만 교체:
  ```python
  # before
  _client = client or OpenAI(api_key=settings.openai_api_key)
  _model  = model or settings.openai_model_default
  # after (Stage A)
  gw = get_gateway()
  _client = client or gw.openai_client()                 # DI override 그대로 (테스트 mock 주입 보존)
  _model  = model or gw.resolve_model("planning", tier=..., mode=...)   # alias 해석
  _client.chat.completions.create(model=_model, ...)     # 호출부 동일 (OpenAI SDK shape 유지)
  ```
- ★ **테스트 무영향**: 기존 fixture 는 `client=mock` 주입 + `run_*` monkeypatch → `client or ...` 의 `client` 분기 그대로 → 339 test green. model 해석만 gateway 로 이동(내부값 동일).
- ★ **결과 동일**: alias "planning"→gpt-4o-mini, "critic"→gpt-4o = 현재 default 와 byte-identical.

**Stage B — provider-neutral (후속, provider 추가 시)**
- agents 가 `gw.complete(alias, messages, ...) -> LLMResponse(canonical)` 호출로 전환. OpenAI SDK shape 가 agent 에서 사라짐.
- 이 단계에서 테스트 mock 이 `client` → `gateway` 로 이동(테스트 갱신 수반) → **별도 phase**(provider 추가와 묶음).

> Phase 11(본 제안 실구현)은 **Stage A 까지만**. Stage B 는 provider 추가 phase 와 묶어 별도.

### 4.2 canonical 응답 (types.py)
```
LLMResponse: { text: str, model_id: str, alias: str, usage: {prompt_tokens, completion_tokens}, raw: Any(optional) }
```
- Critic 의 `normalize_to_canonical`(0–5→0–1) 정신과 동형 — provider 응답 차이를 흡수할 토대.

---

## 5. model_registry / model_alias 구조

### 5.1 registry (concrete 모델 카탈로그)
```yaml
gpt-4o-mini: { provider: openai, model_id: gpt-4o-mini, json_mode: true, max_tokens: 1500,
               cost: { input: 0.00015, output: 0.0006 }, tier_allowed: [free, paid] }
gpt-4o:      { provider: openai, model_id: gpt-4o,      json_mode: true, max_tokens: 1500,
               cost: { input: 0.0025,  output: 0.01 },   tier_allowed: [free, paid] }
# (후속) claude-3-5-sonnet / gemini-2.0-flash → §8
```

### 5.2 alias (논리명 → registry, tier×mode 입력)
```yaml
planning:       { default: gpt-4o-mini }
critic:         { standard: gpt-4o, cost_saving: gpt-4o-mini }   # ← 현 cost_saving 폴백을 alias 로 정식화
rewriter:       { default: gpt-4o-mini }
memory:         { default: gpt-4o-mini }
intent:         { default: gpt-4o-mini }
premium_review: { enabled: false }                               # ← §7, gated/default-off
```
- agents 는 **alias 만** 참조. registry/alias 는 config 또는 llm/aliases.py 에 선언적 정의.
- ★ 이게 핵심 decoupling: provider 추가 = registry 항목 + alias 값 변경, **agent 코드 0**.

---

## 6. plan tier 별 모델 정책 — cost_control_policy 확장안 (contract-change)

> ★ GPT "plan tier" 를 **기존 user tier × cost mode** 위에 매핑 (새 축 추가 X).

| tier × mode | planning | critic | rewriter | premium_review |
|---|---|---|---|---|
| free × standard | gpt-4o-mini | gpt-4o | gpt-4o-mini | ❌ off |
| free × cost_saving | gpt-4o-mini | **gpt-4o-mini** | gpt-4o-mini | ❌ off |
| paid × standard | gpt-4o-mini | gpt-4o | gpt-4o-mini | ⚪ opt-in(§7) |
| paid × premium(신규, 후속) | gpt-4o-mini | gpt-4o | gpt-4o-mini | ✅ 1회 교차검증 |

- gateway 가 `resolve_model(alias, tier, mode)` 로 위 표를 적용. 현 cost_saving 의 "Critic 폴백"을 alias 표로 **선언적 정식화**(로직 분산 해소).
- **현 동작 보존**: free×standard = 현재 default. cost_saving = 현재 Critic 폴백과 동일.
- "premium" mode 와 premium_review 활성은 **후속**(유료 정책 Phase 11+ 정의와 동기).

---

## 7. premium_review 교차검증 정책 (gated, 후속 — ★ 새 agent 아님)

> moa_policy "4 agent 고정" 준수 — premium_review 는 **Critic agent 의 추가 pass**(agent 수 불변).

- **정의**: 표준 Critic(gpt-4o) 평가 후, **선택적으로** 고급/대안 모델(Sonnet 또는 GPT 상급)로 **1회 교차검증 pass** → 두 평가 비교(불일치 시 human_review_needed 또는 보수적 채택).
- **게이트(필수)**:
  - `default OFF` (alias `premium_review.enabled=false`). ★ Opus/GPT flagship 을 **기본 호출에 절대 넣지 않음**(스펙 금지 준수).
  - **paid × premium mode 에서만** + **비용 게이트**(cost_control_policy 상한 내) + revise 한도 불변.
  - 모델 후보는 registry 의 `tier_allowed`/cost 로 제한. flagship 은 명시적 opt-in 만.
- **구현 위치**: Critic agent 내부 또는 orchestrator 의 critic step 에 **additive** 분기 (MOA agent 수·Envelope·output_schema 불변).
- **multi-llm-validation Skill 정신과 정합**: 단일 모델 편향 감소(생성=mini, 검증=고급/대안).
- ★ **Phase 11 본 제안 범위 밖**(설계만). 실 활성은 provider 추가 + 유료 정책 확정 후.

---

## 8. Anthropic / Gemini provider 추가 — 후속 분리

- 본 제안(Phase 11)은 **OpenAI-only gateway 까지**. provider 추가는 **별도 phase**:
  1. `providers/anthropic_adapter.py` / `gemini_adapter.py` (base.ProviderAdapter 구현).
  2. registry 에 claude/gemini 항목 + config `ANTHROPIC_API_KEY`/`GOOGLE_API_KEY`.
  3. agents Stage B 전환(canonical complete) — 테스트 mock 갱신.
  4. **multi-llm-validation + eval-run 회귀**(provider 간 품질/비용 비교) → tech_stack_contract 갱신.
- tech_stack_contract 의 "Anthropic Phase 5+ 검토" + architecture "Anthropic/Gemini Phase 11+ A/B" 절차 그대로.

---

## 9. 변경 범위 / 변경하지 않을 범위

### 변경 범위 (Phase 11 실구현 시)
- 신규: `backend/fastapi/llm/` 패키지(7~8 파일) + `tests/test_llm_gateway.py`.
- 수정(Stage A, additive): agents 5개의 client 생성·모델선택 **2줄씩**(`gw.openai_client()` + `gw.resolve_model(alias,...)`). 호출부·응답파싱·에러전파 **불변**.
- config.py: registry/alias 선언 추가(기존 `openai_model_*` Field 는 **보존**, gateway 가 참조하거나 alias default 로 흡수).

### ★ 변경하지 않을 범위 (스펙 금지 + 본 설계 보장)
- endpoint(routers) / output_schema / **Envelope 구조** — gateway 는 agent 아래 레이어, 무관.
- **MOA agent 수 4 고정**(premium_review = Critic pass, 새 agent 아님).
- PlanCard.tsx / component_map.md / frontend(provider 직접 호출 절대 없음 — frontend→backend API만).
- Opus/GPT flagship 기본 호출 0(premium_review gated/off).
- LangGraph/CrewAI 등 외부 framework 0.
- docs/contracts **직접 수정 0**(본 문서는 proposal — 실 변경은 contract-change 경유).

---

## 10. 영향 받는 파일 / contracts

### 영향 파일 (실구현 시)
| 파일 | 변경 | 비고 |
|---|---|---|
| `llm/*` (신규 7~8) | 신규 | gateway/registry/aliases/types/errors/providers |
| `agents/{intent,planning,critic,rewriter,brand_memory_extractor}.py` | 2줄씩 additive | client 생성·모델해석만 (호출부 불변) |
| `config.py` | additive | registry/alias 선언 (기존 Field 보존) |
| `orchestration/moa_orchestrator.py` | 0~소폭 | agent 호출 그대로(monkeypatch 보존). tier/mode 전달만 선택적 |
| `tests/test_llm_gateway.py` (신규) | 신규 | gateway/alias/registry 단위 |

### 영향 contracts (contract-change 경유 — 본 제안은 미수정)
| contract | 변경 성격 |
|---|---|
| `cost_control_policy.md` | **tier×mode → alias→model 표** 추가(§6). 현 cost_saving 폴백 정식화 |
| `tech_stack_contract.md` | "LLM Gateway 도입(OpenAI-only)" 노트 + registry/alias 개념. provider 단일 불변 |
| `agent_io_contract.md` | (소폭) 모델 선택이 gateway-mediated 라는 노트. IO 스키마 불변 |
| `prompt_registry.md` | (소폭) prompt↔alias 매핑 노트(P-006→"planning" 등). prompt 본문 불변 |
| `ai_system/orchestration/moa_policy.md` | premium_review = Critic pass(agent 수 불변) 명문 — §7 |

→ 위는 전부 **contract-change Skill** + (큰 결정이므로) **ai-architecture-review** + **multi-llm-validation** 경유.

---

## 11. Migration 순서 (단계별)

```
M0 (설계)   : 본 제안서 검토 → 승인 → Phase 11 entry (ai-architecture-review + multi-llm-validation)
M1 (gateway): llm/ 패키지 신규 (OpenAI adapter only) + test_llm_gateway. agents 미변경 → 339 무영향
M2 (alias)  : registry/alias 선언 + gateway.resolve_model. free×standard = 현 default byte-identical 검증
M3 (agents) : agents 5개 Stage A 2줄 교체(client DI 보존) → pytest 339+ green(behavior-preserving)
M4 (cost)   : cost_control_policy 확장(tier×mode→alias) contract-change CC + cost_saving 폴백 정식화
M5 (close)  : eval-run 회귀(품질 동일 입증) + qa-check + 회고. ★ premium_review/provider 추가는 후속 phase
```
- 각 단계 **behavior-preserving 게이트**(기존 test green, Envelope byte-identical). M3 이전까지 agents 0 변경.

---

## 12. 테스트 전략

- **behavior-preserving 회귀**: 매 단계 `pytest`(현 381) 전부 green + **기존 test 수정 0**(신규만 추가). M2 에서 alias 해석값이 현 default 와 동일함을 단위 검증.
- **gateway 단위**(test_llm_gateway): alias→model 해석(tier×mode 표), registry 조회, 에러 정규화(OpenAIError→LLMError), 비용 추정, openai_client DI.
- **Envelope byte-identical**: M3 전후 `/generate` 응답 동일(기존 통합 test_integration_mvp 로 가드).
- **eval-run**: M5 에서 mock-deterministic golden_set 회귀 — 모델 해석 변경이 품질 점수 불변임을 입증(Phase 9.5 패턴).
- **mock-deterministic**: 실 LLM 0(키 0). gateway 도 `client` DI 로 mock 주입.

## 13. Rollback 전략

- **단계별 commit + revert 가능**(P-X1). M1~M3 는 additive(신규 파일 + agents 2줄) → 문제 시 agents 2줄 원복 = 즉시 복귀.
- **feature flag**: gateway 사용을 config 플래그(`LLM_GATEWAY_ENABLED`, default true)로 감싸 — false 시 기존 `OpenAI(...)+settings.X` 경로 폴백(과도기 안전망, 선택).
- contract 변경(M4)은 contract-change 로그 + ADR → rollback_policy 경유.
- ★ provider/premium_review 미도입 → 외부 의존 증가 0, rollback 표면 최소.

---

## 14. Codex 작업 티켓 (구현 위임 — Stage A, OpenAI-only)

> 각 티켓: behavior-preserving(기존 test 0 수정, 신규만) + editable/forbidden 명시. AGENTS.md 라우터 대상(Codex).

### T-1 — llm/ 패키지 skeleton + OpenAI adapter
- editable: `backend/fastapi/llm/{__init__,types,errors,registry,aliases,gateway}.py` + `llm/providers/{__init__,base,openai_adapter}.py` (신규)
- 내용: types(LLMRequest/Response/Usage), registry(gpt-4o-mini/gpt-4o 2항목), aliases(planning/critic/rewriter/memory/intent + premium_review.enabled=false), gateway(`openai_client()`, `resolve_model(alias,tier,mode)`, `complete(...)` 스텁), openai_adapter(OpenAI SDK 래핑).
- forbidden: agents/routers/orchestration/eval/contracts/frontend 수정.
- acceptance: import OK, `resolve_model("planning")=="gpt-4o-mini"`, `resolve_model("critic","-","standard")=="gpt-4o"`, `resolve_model("critic","-","cost_saving")=="gpt-4o-mini"`. 신규 `test_llm_gateway.py` green. 기존 381 무영향.

### T-2 — agents Stage A 전환 (2줄씩, behavior-preserving)
- editable: `agents/{intent,planning,critic,rewriter,brand_memory_extractor}.py` — `client or OpenAI(...)` → `client or get_gateway().openai_client()`, `model or settings.X` → `model or get_gateway().resolve_model("<alias>", tier, mode)`. 호출부/파싱/에러 **불변**.
- forbidden: 호출부 시그니처/응답 schema/Envelope/모델 default 값 의미 변경. routers/orchestration.
- acceptance: ★ **pytest 기존 381 전부 green, 기존 test 0 수정**(DI mock 보존). `/generate` Envelope byte-identical(test_integration_mvp).

### T-3 — config registry/alias 정식화 (additive)
- editable: `config.py`(registry/alias 선언 또는 llm/aliases 연결, 기존 `openai_model_*` Field **보존**).
- forbidden: 기존 Field 삭제/rename(backward-compat).
- acceptance: alias 표가 현 default 와 동일 해석. pytest green.

### T-4 — cost_control_policy 확장 (contract-change, 별도 승인)
- ★ **contract-change Skill 경유**(Codex 직접 수정 금지) — tier×mode→alias 표 + cost_saving 폴백 정식화. CC 로그 + agent-io-check.

### T-5 — eval-run 회귀 + qa-check (close)
- mock-deterministic golden_set 회귀(모델 해석 변경 품질 불변) + smoke + qa-check release gate.

> ★ premium_review 구현 / Anthropic·Gemini adapter 는 **별도 후속 티켓**(provider 추가 phase).

---

## 15. 리스크와 방어책

| 리스크 | 방어책 |
|---|---|
| 339/381 test/monkeypatch 깨짐 | Stage A 는 `client` DI 보존 + 2줄 교체만. 매 티켓 pytest green 게이트. M3 전 agents 0 변경 |
| Envelope/output 미세 변동 | gateway 는 agent 아래 — Envelope 조립(orchestrator) 불변. test_integration_mvp byte-identical 가드 |
| 모델 해석 값 drift(alias≠현 default) | M2 단위 test 로 alias→model = 현 default 동일 강제 |
| premium_review 가 flagship 기본 호출로 누수 | default OFF + paid×premium + 비용 게이트 + registry tier_allowed. 기본 경로 0 |
| MOA agent 수 증가 유혹 | premium_review = Critic pass(설계 명문). agent 4 불변 |
| provider 추가 scope creep | 본 제안 OpenAI-only. adapter 인터페이스만, 구현은 후속 phase(multi-llm-validation+eval) |
| cost_control 로직 분산 재발 | tier×mode→alias 표로 **선언적 단일화**(critic 폴백 흡수) |
| 키/자격증명 노출 | gateway 도 키 커밋 0(.env user-provided). registry 에 키 비포함 |

---

## 16. 최종 출력 (스펙 요청 6항 요약)

1. **현재 LLM 호출 구조**: agents 직접 OpenAI SDK(DI hook 有) + static config 모델 + cost_saving Critic 폴백. gateway/registry/alias/tier/premium **전무**. (§1)
2. **제안 디렉터리**: `backend/fastapi/llm/`(gateway/registry/aliases/types/errors/providers·openai_adapter). (§3)
3. **단계별 migration**: M0 설계→M1 gateway→M2 alias→M3 agents(2줄)→M4 cost contract→M5 close. provider/premium 후속. (§11)
4. **contract-change 필요**: cost_control_policy(tier×mode→alias) / tech_stack(gateway 노트) / agent_io(소폭) / prompt_registry(prompt↔alias) / moa_policy(premium_review=Critic pass). (§10)
5. **Codex 티켓**: T-1 gateway skeleton / T-2 agents Stage A / T-3 config alias / T-4 cost contract(CC) / T-5 eval+qa. (§14)
6. **리스크/방어**: test/monkeypatch·Envelope·alias drift·flagship 누수·MOA 증가·provider creep — 전부 behavior-preserving + alias 단위검증 + gated default-off 로 방어. (§15)

---

## 17. 다음 단계 (승인 시)
- 본 제안 → **ai-architecture-review + multi-llm-validation**(큰 아키텍처 결정) → **Phase 11 entry**(LLM Gateway + A안 cross-validation, §18).
- contract 변경(cost_control 등)은 각 **contract-change** + ADR.
- B안(완전 멀티-provider 다양성)은 **후속 phase 지침**(§18.B) — eval 누적 + cost 재조정 + 유료 정책 확정 후.

---

## 18. A안/B안 단계화 + 모델 선택 (2026-06 기준, 사용자 결정)

> 사용자 결정: **A안 먼저 구현 → B안은 이후 phase 지침으로 기록**. ★ 빌드는 **키 준비 후**.
> 모델 라인업은 2026-06 web 확인값(provider dev 페이지에서 최종 model ID 확인 필요).

### 18.0 현재(2026-06) registry 후보 모델

| Provider | 최상위(premium) | 강력(critic급) | 워크호스(저가) | 초저가 |
|---|---|---|---|---|
| OpenAI | GPT-5.5 ($5/$30) | GPT-5.4 ($2.5/$15) | GPT-5.4 Mini ($0.75/$4.5) · gpt-4o-mini ($0.15/$0.6) | 5.4 Nano ($0.2/$1.25) |
| Anthropic | Opus 4.8 ($5/$25) | Sonnet 4.6 ($3/$15) | Haiku 4.5 ($1/$5) | — |
| Google | Gemini 3.1 Pro ($2/$12) | 3.5 Flash ($1.5/$9) | 3 Flash ($0.5/$3) | 3.1 Flash-Lite ($0.25/$1.5) |

(가격 = 입력/출력 per 1M tokens. ★ Gemini 가 동급 최저가.)

### 18.A — A안 (Phase 11 구현 범위) ★ 먼저

**목표**: 기존 OpenAI 동작 보존 + **Critic 교차검증만 추가**(self-bias 감소). 최소 비용 증가.

| alias | A안 모델 | 비고 |
|---|---|---|
| workhorse (intent/planning/rewriter/memory) | `gpt-4o-mini` **유지** | 비용 유지 |
| critic | `gpt-4o` **유지** | 비용 유지 |
| **cross_validation** (신규, gated) | **`Gemini 3.1 Pro`** (또는 `Claude Sonnet 4.6`) | ★ 다른 family 1회 교차검증 → Critic 결과 비교 |

- gateway + registry(OpenAI 2 + Gemini 1) + **openai_adapter + gemini_adapter** + cross-validation 로직 + mock tests.
- cross-validation = Critic agent 의 **추가 pass**(MOA 4 agent 불변). default OFF, opt-in flag.
- behavior-preserving: 기존 381 test green, OpenAI default 불변, 키 없으면 graceful(교차검증 skip).
- cost_control: cross_validation 1회 호출 비용을 호출당 상한에 additive(소폭) — contract-change 소폭.

### 18.B — B안 (후속 phase 지침, Phase 12+) — ★ 확장용 보관

**목표**: 3안을 **3 provider 로 분산** → 진짜 모델 다양성(MOA 본래 취지).

| alias | B안 모델 | 비고 |
|---|---|---|
| 3-plan 슬롯 1 | `GPT-5.4 Mini` | provider 다양성 |
| 3-plan 슬롯 2 | `Claude Haiku 4.5` | |
| 3-plan 슬롯 3 | `Gemini 3 Flash` | Google Search grounding 내장 |
| critic | `Claude Sonnet 4.6` | 생성과 다른 시각 |
| cross_validation | `Gemini 3.1 Pro` | |
| premium (★ opt-in only, 기본 호출 금지) | `Claude Opus 4.8` / `GPT-5.5` | 고비용, 명시적 고위험 검증만 |

- 신규 adapter: **anthropic_adapter**(anthropic SDK) + (Grok 추가 시) **grok_adapter**(OpenAI 호환 api.x.ai, SDK 불필요).
- agents Stage B 전환(canonical `gw.complete()`) — 테스트 mock 갱신 수반.
- ★ **cost_control_policy 재조정 필수**: 신모델이 gpt-4o-mini 대비 5~7배 → 호출당/세션당 상한 상향 + tier×mode→alias 표(§6) 정식화. multi-llm-validation + eval-run(provider 간 품질·비용 비교) 후 tech_stack_contract 갱신.
- (선택) **Grok(xAI)**: OpenAI 호환 엔드포인트(api.x.ai)라 grok_adapter 추가 용이 — B안 이후 옵션.

### 18.C — API 키 요건 (★ .env user-provided, 저장소·채팅 절대 금지)

| 키 (env var) | provider | A안 | B안 | 비고 |
|---|---|---|---|---|
| `OPENAI_API_KEY` | OpenAI | ✅ 필수 | ✅ | 기존(config.py) — workhorse/critic |
| `GOOGLE_API_KEY` (또는 `GEMINI_API_KEY`) | Google Gemini | ✅ (교차검증) | ✅ | A안 cross-validation = Gemini 3.1 Pro |
| `ANTHROPIC_API_KEY` | Anthropic Claude | ⚪ 선택(cross-val을 Sonnet으로 할 때) | ✅ 필수 | B안 3-plan/critic |
| `XAI_API_KEY` | xAI Grok | ❌ | ⚪ 선택 | OpenAI 호환, B안 이후 옵션 |

- A안 최소 키: **OPENAI + GOOGLE** (교차검증 Gemini). cross-val을 Claude로 하려면 GOOGLE 대신 ANTHROPIC.
- 키는 `.env`(이미 .gitignore)에만. config.py 에 graceful Field 추가(미설정 시 해당 provider 비활성).
- ★ 어떤 키도 코드/commit/채팅에 평문 금지. registry 에 키 비포함(env 참조만).

### 18.D — cost_control 재조정 주의 (양안 공통)
- 현 상한(Planning $0.003 / Critic $0.006)은 gpt-4o-mini/gpt-4o 기준. 신모델 채택 시 상한 초과 abort 위험 → cost_control_policy 동반 상향(contract-change). A안은 cross_validation 1회분만 additive, B안은 전면 재조정.
