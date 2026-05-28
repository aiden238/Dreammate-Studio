# ADR-015: Phase 4 3-plan Parallel Generation with Multi-model Interface

> Status: accepted (Phase 4 Slice 2, 2026-05-28)
> 사용자 결정 4-b 반영: 3 parallel async + 향후 모델 추가 가능 구조
> GPT 검토 채택 정신: Critic revise loop / Rewriter / SSE는 Phase 4.5+ deferred

---

## Context

Phase 1 baseline:
- 1 plan (sync, single model `gpt-4o-mini`)
- contract (`output_schema.md` §8 P-006)와 deviation: contract는 plans length 3, Phase 1은 1
- `validation.warnings: ["phase_1_single_plan"]`로 추적

Phase 4 (GPT 검토 채택):
- 3-plan 본격 활성 + multi-model 가능 구조
- 단, Critic revise loop / Rewriter / SSE는 다음 phase(4.5+)로 이관

대안 비교:

| 접근 | latency | cost | 다양성 | multi-model | 채택 여부 |
|---|---|---|---|---|---|
| A. 단일 호출 n=3 (OpenAI `n` param) | 1x | ~1.5x | 중간 | 불가 | 거부 |
| **B. 3 parallel async (gather)** | **1x** | **~3x** | **높음** | **가능** | **채택 (4-b)** |
| C. 3 sequential | ~3x | ~3x | 높음 | 가능 | 거부 |

---

## Decision

**3 parallel async** (`asyncio.gather`) + **multi-model 인터페이스**.

### 함수 시그니처

```python
async def run_planning_parallel_3(
    user_input: str,
    *,
    rag_context: Sequence[Any] | None = None,
    models: list[str] | None = None,
    client: OpenAI | None = None,
) -> list[dict[str, Any]]:
```

- `models: list[str] of 3` — default `config.openai_models_for_3plan_list`
- `models is None` → settings 기본값 (`gpt-4o-mini,gpt-4o-mini,gpt-4o-mini`)
- `models` 길이 != 3 → `ValueError("Expected 3 models, got N")`

### approach_hint 분기

각 호출마다 system prompt에 다른 hint 주입:
1. `narrative — 스토리텔링 중심, 감정 연결`
2. `informational — 명확한 정보 전달, 전문성 강조`
3. `experiment — 실험적 / 비교 / 챌린지 / 새 접근`

→ 3개 plan의 `approach_label` set 크기 === 3 (모두 unique).

### parallel error graceful

- `asyncio.gather(*tasks, return_exceptions=True)` 사용
- 일부 실패 → 해당 인덱스만 retry 1회
- retry 실패 → fallback dict (`name="(생성 실패 N)"`, `risks="graceful fallback"`)
- 사용자 응답은 항상 length 3 보장 (Slice 4/5 graceful 정책 계승)

### approach_label unique 강제

- 3 호출 모두 성공 후 `approach_label` 중복 검사
- 중복 발견 시 fallback pool (`narrative / informational / experiment / empathy / review / other`)에서 미사용 label로 교체
- 강한 정합 (prompt 재호출)은 Phase 5+ prompt 개선에서 (Phase 4는 graceful uniqueness)

### config

```python
# config.py
openai_models_for_3plan: str = Field(
    default="gpt-4o-mini,gpt-4o-mini,gpt-4o-mini",
)

@property
def openai_models_for_3plan_list(self) -> list[str]:
    """Length 3 (padding/truncating to 3 if mismatch)."""
```

`.env`:
```
# OPENAI_MODELS_FOR_3PLAN=gpt-4o-mini,gpt-4o-mini,gpt-4o-mini
```

### 향후 multi-provider 확장 (Phase 21+)

- 현재 Phase 4: OpenAI만 (default 동일 모델 × 3)
- Anthropic / Google 등 multi-provider 확장:
  - `models` 파라미터를 list로 받아 client factory에서 분기
  - 예: `["gpt-4o-mini", "claude-sonnet-4.5", "gemini-2.0-flash"]`
- Phase 21+에서 결정 (multi-llm-validation 필요)

---

## Alternatives

### A. 단일 호출 n=3 (OpenAI `n` parameter)

- 1회 호출로 3개 응답을 받는 OpenAI native 기능 활용
- 거부 사유:
  - multi-model 불가 (단일 endpoint 호출이므로 모델 분기 불가)
  - 사용자 결정 4-b 정신 위반 (모델 추가 가능 구조 요구)
  - approach_hint 분기 불가 (동일 prompt로 n=3)

### B. 3 parallel async + multi-model 인터페이스 (채택)

- 사용자 결정 4-b 정합
- multi-model 가능 (향후 multi-provider 확장 path)
- approach_hint 분기로 다양성 확보
- cost ~3x but latency ≈ 1x (parallel)

### C. 3 sequential

- latency 3x (parallel 대비)
- cost는 B와 동일 (3x)
- 거부 사유: latency 불리, parallel 대비 이점 없음

---

## Consequences

### Positive
- 다양성 확보 (approach_label 3개 unique 강제)
- multi-model 가능 (Phase 21+ multi-provider 확장 path)
- parallel latency ≈ single call (cost는 3x)
- Phase 1 endpoint 회귀 0 (기존 `run_planning` 1-plan 함수 보존)
- graceful — parallel 1개 실패해도 fallback dict로 length 3 보장

### Negative
- LLM cost 증가 (~3x of 1-plan) — Phase 9+ cost monitoring 필요
- Critic 1회만 평가 (3개 plan 중 첫 번째만) — best plan 선택 로직은 Phase 4.5+ deferred
- approach_label unique 강제는 graceful (prompt 재호출 없음) — Phase 5+ 개선 여지

---

## Cost Estimate

- gpt-4o-mini × 3 parallel: 약 $0.001~0.003 per 호출 (input ~500 tokens, output ~500 tokens)
- 일 100 호출 = $0.1~0.3 / 일 (수용 가능)
- 일 1,000 호출 = $1~3 / 일 (Phase 9 cost-review에서 재평가)
- multi-provider 확장 시 (예: claude-sonnet-4.5 1 + gpt-4o-mini 2):
  - 약 $0.005~0.010 per 호출 (claude cost 가산)
  - Phase 21+ multi-llm-validation 시 cost vs quality trade-off 평가

---

## Phase 4 비포함 사항 (Phase 4.5+ deferred)

- Critic revise loop (revise verdict 시 Rewriter 자동 호출)
- Rewriter agent (P-008)
- SSE Progress streaming
- best plan 선택 로직 (3개 중 Critic 점수 기반 최선 1개)
- multi-provider (Anthropic / Google 등 — Phase 21+)
- approach_label unique 강한 정합 (prompt 재호출 retry)

---

## Validation (Phase 4 Slice 2)

- pytest 93 PASS (77 baseline + 16 신규 — test_3_plan.py + test_plans.py 1 migration)
  - 3-plan length === 3
  - approach_label set === 3 (unique)
  - validation.warnings에서 phase_1_single_plan 제거
  - validation.warnings에 phase_4_no_revise_loop 추가
  - Phase 1 endpoint 회귀 0 (1-plan 유지)
  - multi-model validation.check 노출
  - parallel error graceful (1개 실패 시 fallback dict)
  - Critic 8 scores + verdict 노출
  - config.openai_models_for_3plan_list (default / padding / multi)
  - run_planning_parallel_3 models param 검증 (length != 3 → ValueError)
- audit_naming 0 drift (4 canonical 모두 OK)
- §SELF-VERIFICATION 7연속 PASS (Phase 3 5 + Phase 4 Slice 1 + Slice 2)

---

## Related

- ADR-014 (endpoint migration — Phase 1 / Phase 4 coexistence)
- ADR-008 (Phase 1 Simplest Slice — sync 1-plan 결정 근거)
- api_contract.md §8.3 (POST /plans/{id}/generate)
- output_schema.md §8 P-006 (plans length 3 + approach_label enum)
- output_schema.md §9 P-007 (Critic 8-dim verdict)
- prompt_registry.md P-006 (Planning prompt — Slice 2는 hint 추가만, 본 prompt 무수정)
- harness/phases/active/phase-4-fastapi-extension/acceptance.md A2 + A3 + A4

---

## 변경 이력

- 2026-05-28: 최초 작성 (Phase 4 Slice 2, 사용자 결정 4-b 반영)
