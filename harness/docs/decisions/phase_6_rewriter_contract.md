# ADR-019 — Phase 6 Rewriter Contract Strengthening (P-008 v1.0.0 → v1.1.0)

> Date: 2026-05-29
> Status: Accepted
> Phase: 6 (Output Schema + Agent IO Stabilization)
> Slice: 2
> Related: ADR-016 (phase_4_5_critic_revise), ADR-018 (phase_6_critic_canonical),
>          docs/contracts/agent_io_contract.md §6

## Context

Phase 4.5 Slice 2 에서 `backend/fastapi/agents/rewriter.py` 신규 추가. dict 반환 + `_rewriter_warning` graceful 패턴으로 구현. `docs/contracts/agent_io_contract.md` §6 (Rewriter Agent) 는 Phase 0 시점 (v1.0.0, 2026-05-26) 부터 존재했지만 실 구현 (Phase 4.5) 의 graceful 정책 / Pydantic 미도입 / 시그니처 (`run_rewriter(plan, critic_verdict, ...)`) 와 정합되지 않은 부분이 있었다.

사전 검증 `meta/validations/2026-05-29_phase-6-pre-entry_self.md` §V2 에서 Phase 6 contract 정합 강화 + Pydantic 모델 정식 등록 결정 (semver minor bump v1.0.0 → v1.1.0).

## Decision

### 1. P-008 Rewriter semver bump (v1.0.0 → v1.1.0)

- **MINOR bump**: 신규 필드 추가 (Pydantic 모델) + 정책 명시 (graceful). Breaking change 없음.
- `backend/fastapi/agents/rewriter.py::PROMPT_VERSION = "v1.1.0"`.

### 2. `RewriterInput` Pydantic 모델 (typing 검증용)

```python
class RewriterInput(BaseModel):
    plan: dict[str, Any]
    critic_verdict: dict[str, Any]
    model: str = "gpt-4o-mini"
```

실제 `run_rewriter(plan, critic_verdict, *, model, client)` 시그니처는 호환 유지. 이 모델은 typing 검증 + frontend type mirror 용도.

### 3. `RewriterOutput` Pydantic 모델 (graceful 마커 포함)

```python
class RewriterOutput(BaseModel):
    revised_plan: dict[str, Any]
    rewriter_model: str | None = Field(default=None, alias="_rewriter_model")
    rewriter_warning: str | None = Field(default=None, alias="_rewriter_warning")
    model_config = {"populate_by_name": True}
```

`alias="_rewriter_*"` 로 기존 dict 키 호환 유지. Pydantic v2 `populate_by_name=True` 로 alias / field name 양쪽 지원.

실 `run_rewriter` 함수는 backward-compat 위해 dict 반환 (revised_plan 본문 + `_rewriter_model` / `_rewriter_warning` 키 inline). `routers/plans.py` 의 `revised_plan_dict = await run_rewriter(...)` 호출 패턴 변경 없음 (회귀 0).

### 4. Graceful failure 정책 명시

```
LLM 호출 실패 (네트워크 / API 에러 / JSON 파싱 실패):
  → 원본 plan 반환 + _rewriter_warning: "rewriter_failed: <ErrorClass>"

LLM 응답이 dict 가 아닌 경우 (JSON string / array / null):
  → 원본 plan + _rewriter_warning: "rewriter_failed: ValueError"

회로 차단:
  → revise loop max 2 (config.critic_max_revise — ADR-016)
  → max 도달 시 routers/plans.py 가 ReviseAttempt.max_reached=True 마커 추가
```

### 5. prompt body 정식 작성은 Phase 7+ 이관 (NG8)

- Phase 6 에서는 semver / io / rollback / graceful 정책만 contract 에 등록.
- prompt body (`REWRITER_SYSTEM_PROMPT` / `REWRITER_USER_TEMPLATE`) 는 인라인 유지 (Phase 7+ prompt_registry 정식화 후 본문 분리).
- 단일 함수만 사용하므로 drift risk 낮음.

## Constraints

- **routers/plans.py 회귀 0**: `await run_rewriter(current_plan_dict, verdict)` 호출 패턴 호환 유지 (dict 반환 그대로).
- **PlanCard.tsx 0줄 / component_map.md 0줄 ★** (사용자 결정 6-a / NG6 / NG7).
- **Pydantic 모델은 typing + frontend mirror 용도** — 실 함수 시그니처는 호환 유지 (이중 패턴 의도적).
- **PROMPT_VERSION 변경 시 test 갱신 의무**: `test_rewriter_prompt_meta_constants` 가 v1.1.0 검증으로 갱신.

## Trade-offs

| 선택 | 채택 사유 | 미채택 후보 |
|---|---|---|
| dict + Pydantic 이중 패턴 | routers/plans.py 회귀 0 + typing 강화 동시 달성 | Pydantic 단일 (호환 깨짐 — routers/plans.py 갱신 필요, 회귀 위험 ↑) |
| alias `_rewriter_*` | dict 키 호환 유지 (Phase 4.5 패턴 보존) | snake_case 단일 (frontend 응답 키 변경 — breaking) |
| graceful 정책 contract 명시 | failure mode 표준화 + frontend handling 일관성 | log only — frontend 가 _rewriter_warning 무시할 위험 |
| prompt body 인라인 유지 (NG8) | drift risk 낮음 (단일 함수) + Phase 7+ prompt_registry 정식화 대기 | 즉시 분리 — over-engineering (Phase 7 의존성 ↑) |
| MINOR bump | breaking change 없음 (Pydantic + 정책 추가) | MAJOR bump — 외부 클라이언트 통지 불필요 (호환 유지이므로 과잉) |

## Verification

- `pytest backend/fastapi/tests/test_rewriter.py` (이전 7 케이스 + 신규 5~7 케이스):
  - `test_rewriter_input_pydantic_model`
  - `test_rewriter_output_pydantic_model_with_warning`
  - `test_rewriter_output_pydantic_no_warning`
  - `test_revise_attempt_model_canonical`
  - `test_revise_attempt_unknown_action`
  - `test_revise_attempt_max_reached`
  - `test_revise_attempt_dict_compat`
  - 기존 `test_rewriter_prompt_meta_constants` 갱신 (v1.0.0 → v1.1.0)
- `pytest backend/fastapi/tests/` 전체 회귀: Phase 4.5 baseline 109/109 → Phase 6 113~115/113~115
- **`git diff --cached --stat | grep -E "PlanCard|component_map|routers/plans"` = 0 lines** ★

## Migration

Phase 7+ prompt_registry 정식화 시 (별도 contract-change 절차):

1. prompt body (`REWRITER_SYSTEM_PROMPT` / `REWRITER_USER_TEMPLATE`) → `ai_system/prompts/prompt_registry.md` 본문 등록
2. `agents/rewriter.py` 인라인 prompt 제거 + registry import
3. P-008 semver v1.1.0 → v1.2.0 (MINOR bump — prompt body 분리)
4. golden_set 회귀 평가 통과 확인

Phase 9+ revise loop 효과 eval (NG9) 후 별도 결정 (자동 실행 임계치 / cost optimization).

## References

- `meta/validations/2026-05-29_phase-6-pre-entry_self.md` §V2
- `phases/active/phase-6-output-schema-stabilization/non_goals.md` NG8 (prompt body Phase 7+ 이관)
- `phases/active/phase-6-output-schema-stabilization/scope.md` Slice 2
- `docs/contracts/agent_io_contract.md` §6 (Phase 6 갱신)
- `docs/contracts/output_schema.md` §10 (P-008 body 정합)
- `docs/decisions/phase_4_5_critic_revise.md` (ADR-016 — revise loop max 2)
- `docs/decisions/phase_6_critic_canonical.md` (ADR-018 — Critic canonical)
