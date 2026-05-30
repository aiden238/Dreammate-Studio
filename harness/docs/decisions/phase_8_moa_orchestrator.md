# ADR-027 — Phase 8 MOA Orchestrator 추출 (Behavior-Preserving)

> Date: 2026-05-29
> Status: Accepted
> Phase: 8 (MOA Lite 본격 — orchestrator 추출 + SSE worker 통합 + prompt_registry 정식화)
> Slice: 2 (구현) / Slice 1 (본 ADR 결정)
> Related: ADR-014 (phase_4_endpoint_migration), ADR-015 (phase_4_3plan_multi_model),
>          ADR-016 (phase_4_5_critic_revise), ADR-022 (phase_5_sse_progress — ADR-028이 통합),
>          ADR-028 (phase_8_sse_progress_integration), ADR-029 (phase_8_prompt_registry_semver)
> Skill: **ai-architecture-review ★ 첫 정식 트리거** (본문 §ai-architecture-review 결과)

## Context

`backend/fastapi/routers/plans.py::plans_generate()`는 약 400줄의 god-function으로, MOA orchestration 전 과정이 router에 인라인되어 있다:

1. Intent (`run_intent`) + graceful 에러 (E-LLM-001/002, INV-001)
2. RAG graceful (Phase 1 `run_rag_retrieval` + Phase 7 `run_rag` marker 병합)
3. 3-plan parallel (`run_planning_parallel_3` — multi-model asyncio.gather, ADR-015)
4. plan dict → Pydantic `Plan` × 3 (schema 검증 + graceful skip, E-LLM-003)
5. Critic + revise loop (`asyncio.gather`로 plan별 `_critic_revise_for_plan`, max 2 round, Rewriter 호출, best-plan idx ADR-017)
6. DB save graceful (`save_video_planning` + `PersistenceResult` fallback)
7. Envelope 조립 (`Meta` + `Body` + `Validation` 7 checks + warnings 병합) + `_plan_store` mutation

**문제점 (Gap)**:

- **moa_policy §2 위반**: "agent 간 직접 호출 금지. 오케스트레이터(backend service layer)가 항상 중개한다 (agent_io §1)" — 현재 orchestration이 service layer가 아닌 **router(HTTP 경계)에 인라인** → 정책 위반.
- **단일 책임 위반**: HTTP routing + orchestration + Envelope 조립 + DB save가 한 함수에 결합 → 테스트 격리 곤란, 변경 비용 ↑.
- **SSE decoupling**: `sse.py`가 실 orchestration stage와 분리(ADR-028 대상) → orchestrator가 progress emit point를 가져야 통합 가능.

## Decision

### 1. MOA Orchestrator 추출 (behavior-preserving)

`backend/fastapi/orchestration/` 신규 패키지에 orchestration 책임 이관:

| 파일 | 책임 |
|---|---|
| `orchestration/__init__.py` | orchestration layer export |
| `orchestration/moa_orchestrator.py` | `async def generate_plan(plan_id, plan_entry, req, *, progress: ProgressSink = NullProgressSink()) -> Envelope \| JSONResponse` — `plans_generate()` body 7단계 **그대로 이관** |
| `orchestration/progress_sink.py` | `ProgressSink` Protocol + `NullProgressSink` + `StoreProgressSink` (Slice 3 완성) |
| `orchestration/progress_store.py` | in-memory progress store (Slice 3 — ADR-028) |

`routers/plans.py::plans_generate()`는 **thin adapter**로 축소:

```python
async def plans_generate(plan_id: str, req: GenerateRequest):
    plan_entry = _plan_store.get(plan_id)
    if not plan_entry:
        return _not_found_response(plan_id)
    return await generate_plan(plan_id, plan_entry, req)  # orchestrator 위임
```

### 2. ProgressSink Protocol + NullProgressSink default

```python
class ProgressSink(Protocol):
    def emit(self, stage: str, **meta: Any) -> None: ...

class NullProgressSink:
    def emit(self, stage: str, **meta: Any) -> None:  # no-op — 회귀 0
        pass
```

- `generate_plan(..., *, progress=NullProgressSink())` — default no-op → SSE 미통합(Slice 2) 시 회귀 0.
- orchestrator가 stage 경계 5곳에서 `progress.emit("intent"/"rag"/"planning"/"critic"/"complete")` 호출 (`sse.py::_STEPS` 4단계 + complete와 1:1 정합).
- emit 반환값 미사용 → orchestration 흐름 불변 (side-effect만, Null이면 no-op).
- `StoreProgressSink`(Slice 3)는 `progress_store.record(plan_id, event)` — SSE 연결 시 주입 (의존성 역전).

stage 명은 고정 상수로 (`intent` / `rag` / `planning` / `critic` / `complete`) — drift 방지.

### 3. helper 공유

`_not_found_response` / `_error_envelope_response`는 orchestrator와 router가 공유한다. 위치는 router 잔류(import 공유) 또는 orchestration 이동 중 택일 — **순환 import 회피 우선**. 본 ADR은 router 잔류 + orchestrator import를 기본으로 하되, 순환 발생 시 `orchestration/responses.py` 분리 허용.

## §ai-architecture-review 결과 (★ 첫 정식 트리거)

`.claude/skills/ai-architecture-review/SKILL.md` 절차(7단계) 적용. MOA Lite + orchestration 전체 구조 점검.

### 검토 범위

MOA Lite (Intent / Planning / Critic / Rewriter 4 agent) + orchestration (moa_policy §2 중개) + cost/fallback policy 정합 + agent 격리 — Phase 8 진입 (MOA Lite 본격 구현 시작, SKILL.md 트리거 조건 정합).

### 2. MOA 흐름 점검 (SKILL.md §2)

| 경계 | 확인 | 결과 |
|---|---|---|
| Intent → Planning | `run_intent` 결과 `intent_ok` gate → 차단 시 INV-001, 통과 시 user_input + RAG context를 `run_planning_parallel_3`에 전달 | ✅ 호환 |
| Planning → Critic | 3 plan_candidates → Pydantic `Plan` × 3 → 각 plan을 `_critic_revise_for_plan`에 전달 (3개 그대로) | ✅ 호환 |
| Critic → Rewriter | revise 판정(`overall_verdict=="revise"`) + `attempt < max_revise(2)` 시 `run_rewriter` 트리거 (threshold 명확) | ✅ 명확 (moa_policy §1 revise_round 2 한도) |
| Rewriter → 사용자 | 개선 plan → `Plan` 재schema → `Envelope.body.plan_candidates` → `output_schema.md` 정합 | ✅ 일치 |

### 3. 정책 준수 검사 (SKILL.md §3)

| 정책 | 확인 항목 | 결과 |
|---|---|---|
| Critic revise 최대 2회 | `for attempt in range(max_revise + 1)` + `attempt >= max_revise` break — 무한 루프 차단 코드 존재 | ✅ PASS |
| cost_control_policy | 모델 라우팅 (`settings.openai_models_for_3plan_list` + Critic `openai_model_critic`) — 추출 후 동일 settings 참조 | ✅ 보존 |
| fallback_policy | 단일 agent 실패 시 부분 결과 노출 (Critic 실패 → graceful skip + critic_warning / Rewriter 실패 → 원본 plan 유지) | ✅ 보존 |
| RAG isolation | RAG graceful (use_rag gate + brand context는 Planning만) — 추출 후 동일 | ✅ 보존 (moa_policy §7) |
| 광고 표현 차단 | Critic `brand_consistency` 차원 + blocking_issues (Critic 단 2차 점수화) — 변경 0 | ✅ 보존 |
| PII / 인젝션 차단 | Intent + RAG quality_filter (Phase 7) — 추출 무관 | ✅ N/A (변경 0) |

### 4. 확장성 / 리스크 점검 (SKILL.md §4)

- **새 agent 추가 시 영향 contract 수**: orchestrator 추출로 agent 추가 시 `moa_orchestrator.py` 단일 진입점만 수정 → 영향 작아짐 (현재는 router god-function 직접 수정). 단 Phase 0~10 새 agent 보류 (moa_policy §6 / NG4).
- **prompt 변경 폭주 시 회귀 비용**: prompt_registry semver 정식화(ADR-029)로 완화 — agent 상수 ↔ registry 단일 출처.
- **SSE 통합 경로**: ProgressSink Protocol이 orchestration ↔ SSE 결합도를 낮춤 (ADR-028 progress_store 브릿지). background task 미도입 (moa_policy §4 sync).
- **Phase 11+ 비동기 마이그레이션 경로**: orchestrator 추출이 Phase 11+ 비동기(큐 기반, moa_policy §4 11+) 전환의 선행 조건 — service layer 분리가 background worker 이관을 용이하게 함 (본 phase는 동기 유지 — NG1).

### 강점 / 약점 / 리스크 / 누락 / 권장 액션 (SKILL.md §6 출력 형식)

```
[ai-architecture-review 결과]
검토 범위 : MOA Lite (Intent/Planning/Critic/Rewriter) + orchestration 추출 (Phase 8 진입)
강점      : Critic revise 2회 정책 명확 (range(max_revise+1) + break), fallback 부분 결과 노출 경로 존재
            (Critic/Rewriter graceful skip), 3-plan parallel asyncio.gather 패턴 일관
약점      : orchestration이 router(HTTP 경계)에 인라인 → moa_policy §2 "service layer 중개" 위반
            → 본 ADR-027 추출로 해소
리스크    : 추출 중 graceful 분기(E-LLM-*/INV-*) 또는 validation.checks 순서 누락 시 Envelope 차이
            → behavior-preserving 게이트(pytest 223 수정 0)로 검출
누락      : SSE가 실 orchestration stage와 decoupled → ProgressSink emit point로 통합 (ADR-028)
권장 액션 :
  - contract-change 트리거 (Slice 4) → agent_io_contract.md §orchestrator 중개 명시
  - prompt-version-review 트리거 (Slice 1/4) → P-007 Critic semver (ADR-029)
  - multi-llm-validation (formal 다섯 번째, V1~V7 PASS) — 본 ADR 큰 결정 보강
  - Phase 11+ 비동기 마이그레이션은 본 추출을 선행 조건으로 (moa_policy §4)
```

### 5. 큰 결정 → multi-llm-validation (SKILL.md §5)

orchestration policy 영향 결정(service layer 추출)이므로 `multi-llm-validation` formal 트리거 완료 (`2026-05-29_phase-8-pre-entry_self.md` V1~V2 PASS — orchestrator 추출 behavior-preserving + ProgressSink). 큰 결정 단독 판단 회피.

### 7. 후속 라우팅 (SKILL.md §7)

- contract 변경 필요 → `contract-change` (Slice 4 — agent_io_contract.md orchestrator 중개)
- prompt 변경 필요 → `prompt-version-review` (Slice 1 분석 + Slice 4 적용 — ADR-029)
- 큰 결정 → `multi-llm-validation` (formal 다섯 번째 — 완료)

## Constraints

- **Envelope byte-identical**: `Envelope(meta, body, validation)` 조립 순서·필드·`validation.checks` 7개(schema_envelope / intent_filter / rag_retrieval / plan_count / critic_evaluation / db_persistence / multi_model) 순서·`warnings` 병합 순서(`compute_validation_warnings_phase4` + Phase 7 RAG marker) 모두 보존.
- **기존 pytest 223 수정 0**: `test_plans` / `test_e2e_slice1` / `test_3_plan` / `test_critic` 등 baseline test를 **수정하지 않고** PASS. 테스트 수정이 필요해지면 추출이 동작을 바꾼 것 → 재작업 (★ behavior-preserving 게이트, acceptance A3).
- **graceful / 에러 코드 / validation.checks 순서 100% 보존**: E-LLM-001/002/003, INV-001/006 분기 + graceful skip(Critic/Rewriter/RAG/DB) + `_plan_store` mutation(`status="generated"` + `envelope`) 위치 보존.
- **pure move only**: "리팩터 김에 Intent/Critic 로직 개선" 금지 (NG — scope creep). 로직 변경 0, 위치만 이동.
- **NullProgressSink default → 회귀 0**: emit no-op이 orchestration 흐름·Envelope·DB·plan_store에 영향 0.
- **PlanCard.tsx 0줄 / component_map.md 0줄 ★** (G7 / NG9 / NG10 — backend-only phase).

## Trade-offs

| 선택 | 채택 사유 | 미채택 후보 |
|---|---|---|
| pure move (behavior-preserving) | 회귀 0 + 추출 정당성을 기존 test가 증명 + 리스크 최소 | "추출 김에 개선" — scope creep + 회귀 위험 ↑ + test 수정 필요 |
| ProgressSink Protocol + NullSink default | SSE 결합도 ↓ (의존성 역전) + Slice 2/3 책임 분리 + 회귀 0 | orchestrator가 progress_store 직접 호출 — 결합도 ↑ + 테스트 mock 곤란 |
| helper 공유 (router 잔류 기본) | 순환 import 회피 + 최소 이동 | helper도 orchestration 이동 — 순환 import 위험 |
| orchestrator가 Envelope 조립까지 책임 | 단일 책임 (orchestration 결과 = Envelope) + router는 HTTP만 | router가 Envelope 조립 — orchestration/HTTP 결합 잔존 |
| 동기 유지 (background task 미도입) | moa_policy §4 sync (Phase 0~10) + MVP UX 30~60초 | 비동기 큐 — NG1 (Phase 11+ 트래픽 증가 후) |

## Verification

- `pytest backend/fastapi/tests/test_moa_orchestrator.py` (신규):
  - `test_generate_plan_basic` (mock agents — Intent→3-plan→Critic→Envelope)
  - `test_progress_sink_emits` (stage별 emit 호출 검증 — intent/rag/planning/critic/complete)
  - `test_null_progress_sink_noop` (NullSink 회귀 0)
  - `test_generate_plan_intent_blocked` (INV-001 보존)
  - `test_generate_plan_planning_failure` (E-LLM-001 보존)
  - `test_generate_plan_all_schema_fail` (E-LLM-003 보존)
- **`pytest backend/fastapi/tests/` 기존 223 수정 0 PASS** (특히 `test_plans` / `test_e2e_slice1` / `test_3_plan`) ★ behavior-preserving 핵심 게이트.
- **`git diff --cached --stat | grep -E "PlanCard|component_map"` = 0 lines** ★ (PlanCard 24연속 / component_map 34연속 목표).

## References

- `ai_system/orchestration/moa_policy.md` §2 (orchestrator 중개), §4 (동기/비동기), §5 (실패 격리), §7 (컨텍스트 격리)
- `backend/fastapi/routers/plans.py` (`plans_generate()` god-function — 추출 대상)
- `docs/decisions/phase_4_3plan_multi_model.md` (ADR-015 — 3-plan parallel multi-model)
- `docs/decisions/phase_4_5_critic_revise.md` (ADR-016 — revise loop max 2)
- `docs/decisions/phase_4_5_best_plan_selection.md` (ADR-017 — recommended_plan_index Z-X3)
- `docs/decisions/phase_8_sse_progress_integration.md` (ADR-028 — ProgressSink → progress_store 브릿지)
- `docs/decisions/phase_8_prompt_registry_semver.md` (ADR-029 — Critic adapter + prompt semver)
- `meta/validations/2026-05-29_phase-8-pre-entry_self.md` §V1, §V2 (behavior-preserving + ProgressSink)
- `.claude/skills/ai-architecture-review/SKILL.md` (★ 첫 정식 트리거 — 7단계 절차)
- `phases/active/phase-8-moa-lite/{goals,scope,non_goals,acceptance,assumptions,multi_slice_plan}.md`
