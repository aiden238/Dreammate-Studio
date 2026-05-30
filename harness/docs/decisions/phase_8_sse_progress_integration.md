# ADR-028 — Phase 8 SSE Progress Integration (in-memory progress_store 브릿지)

> Date: 2026-05-29
> Status: Accepted
> Phase: 8 (MOA Lite 본격)
> Slice: 3 (구현) / Slice 1 (본 ADR 결정)
> Related: ADR-022 (phase_5_sse_progress — SSE 4단계 baseline, 본 ADR이 실 stage 통합),
>          ADR-027 (phase_8_moa_orchestrator — ProgressSink Protocol)
> 사용자 결정 (2026-05-29): SSE 통합 = in-memory progress_store 브릿지 (graceful, background task 미도입)

## Context

`backend/fastapi/routers/sse.py`는 Phase 5 Slice 4(ADR-022)에서 도입된 SSE Progress endpoint로, 다음 한계를 가진다:

- **mock 4단계 decoupled**: `_progress_generator`가 `_STEPS`(intent → rag → planning → critic) 정적 리스트를 `asyncio.sleep(0)` 간격으로 순차 yield + `complete` 이벤트. 실 plan 생성 worker(`plans_generate` / Slice 2 추출 후 `generate_plan`)와 **분리**되어 있음.
- sse.py docstring 자체가 명시: "실 구현은 plan 생성 worker (Phase 6+ orchestration) 와 연동하여 각 단계 완료 시점에 emit 한다. 본 baseline 은 SSE event schema 검증용 최소 흐름."
- 즉 진행률이 **실제 stage 완료를 반영하지 않음** → 사용자에게 표시되는 progress가 mock.

ADR-027에서 orchestrator가 `ProgressSink.emit(stage, **meta)`를 stage 경계 5곳에서 호출하므로, 이 emit을 SSE가 read할 수 있는 브릿지가 필요하다.

## Decision

### 1. in-memory progress_store 브릿지 (사용자 결정)

`backend/fastapi/orchestration/progress_store.py` 신규:

```python
_store: dict[str, list[dict]] = {}   # plan_id → events (in-memory, graceful)

def record(plan_id: str, event: dict) -> None: ...   # append (maxlen 제한)
def read(plan_id: str) -> list[dict]: ...            # 현재까지 events
def clear(plan_id: str) -> None: ...                 # complete 시 정리 (메모리 누수 방지)
```

### 2. orchestrator StoreProgressSink emit

`orchestration/progress_sink.py::StoreProgressSink`(ADR-027 Protocol 구현):

```python
class StoreProgressSink:
    def __init__(self, plan_id: str): self.plan_id = plan_id
    def emit(self, stage: str, **meta) -> None:
        progress_store.record(self.plan_id, {"stage": stage, **meta})
```

`routers/plans.py`(Slice 3 소폭 수정)는 `generate_plan` 호출 시 `progress=StoreProgressSink(plan_id)`를 주입 (plan_id keyed). Slice 2는 default `NullProgressSink` → Slice 3에서 Store 주입 (순차 — 충돌 0).

### 3. sse.py가 실 stage read (graceful fallback to mock)

`sse.py::_progress_generator` 수정:

1. `progress_store.read(plan_id)` 우선 — 실 orchestration stage 이벤트 반영 (intent → rag → planning → critic → complete).
2. **store가 비어있으면(아직 generate 미시작 / 다른 worker / read 실패) 기존 mock `_STEPS` 4단계 fallback** → 기존 `test_sse` 4 케이스 수정 0 보존.
3. `complete` 이벤트 도달 또는 stream 종료 시 `progress_store.clear(plan_id)` (메모리 누수 방지).

graceful fallback이 핵심: store 유무와 무관하게 SSE는 항상 유효 event schema 응답. P-GRACEFUL-001 (Phase 1~7 5회 입증) 정신 6번째.

## §Decision rationale (V3/V7 정합)

`meta/validations/2026-05-29_phase-8-pre-entry_self.md` §V3 (progress_store 브릿지) + §V7 (best-effort concurrency) 결과 통합:

- **background task 미도입** (사용자 결정): orchestrator의 emit은 동기 호출 흐름 내 side-effect(`record`). 별도 background worker / 큐 / `asyncio.create_task` 도입 없음 → moa_policy §4 "Phase 0~10 동기 처리" 정합.
- **single-process best-effort**: 동기 blocking `generate`(POST) 처리 중, orchestrator 내 `await` 지점(asyncio.gather / run_in_executor / LLM 호출)에서 event loop가 yield되면 GET `/progress` SSE가 그 사이 `read` 가능 — best-effort (worker 수·yield 타이밍 의존). 보장 아님.
- **가용성 graceful 100%**: 실시간 read 실패 시 mock fallback → SSE 항상 응답. 실시간성은 best-effort, 가용성은 graceful 100%.

## Constraints

- **background task 미도입** — moa_policy §4 sync. 별도 worker / 큐 / `asyncio.create_task` 없음 (NG1). full async streaming은 Phase 11+ (트래픽 증가 후).
- **single-process best-effort** — POST `generate` in-flight 중 GET `/progress` read는 best-effort (event loop yield 의존). multi-worker(uvicorn --workers N) 시 in-memory 미공유 → mock fallback (회귀 아님, 정확도 저하만).
- **full async streaming Phase 11+** — 진정한 실시간 양방향·multi-worker 공유 progress(외부 store Redis pub/sub 등)는 Phase 11+ (NG13 WebSocket 미도입 / NG12 동반).
- **메모리 누수 방지** — `clear(plan_id)` on complete + `record` maxlen 제한 (U6). TTL은 complete-clear로 충분 (single-process MVP).
- **기존 test_sse 4 케이스 수정 0** — graceful fallback(store empty → mock) 보장 증거. test_sse 수정 필요 시 fallback 미보존 → 재작업.
- **Origin 검증 보존** — `_verify_origin` (ADR-022 security-review §T4) + `ALLOWED_ORIGINS` 변경 0.
- **PlanCard.tsx 0줄 / component_map.md 0줄 ★** (backend-only phase).

## Trade-offs

| 선택 | 채택 사유 | 미채택 후보 |
|---|---|---|
| in-memory progress_store 브릿지 | background task 없이 단순 + single-process MVP 충분 + graceful fallback | 외부 store (Redis) — 운영 부담 ↑ (Phase 11+) |
| single-process real-time (best-effort) | MVP UX(30~60초 진행 표시) 충분 + 추가 인프라 0 | 정확한 multi-worker real-time — background task/외부 store 필요 (NG1) |
| graceful fallback to mock | store 유무 무관 항상 유효 응답 + 기존 test_sse 보존 | store 강제 — store 미시작 시 빈 응답 (회귀) |
| clear on complete (TTL 없음) | single-process에서 누수 방지 충분 + 단순 | TTL 타이머 — 복잡도 ↑ (MVP 과설계) |
| background task 미도입 | moa_policy §4 sync (Phase 0~10) + 결정 단순 | 비동기 큐 — NG1 (Phase 11+) |

**핵심 trade-off**: single-process real-time(best-effort) vs 정확성(multi-worker 보장). MVP는 best-effort + graceful 100%를 채택 (정확한 보장은 Phase 11+ 비동기 인프라).

## Verification

- `pytest backend/fastapi/tests/test_sse_integration.py` (신규):
  - `test_progress_store_record_read_roundtrip` (record → sse read)
  - `test_sse_graceful_fallback_to_mock` (store empty → mock 4단계)
  - `test_progress_store_clear_on_complete` (complete 후 clear)
  - `test_sse_real_stage_reflects_orchestrator` (StoreProgressSink emit → sse read 실 stage)
- **기존 `test_sse` 4 케이스 수정 0 PASS** ★ (graceful fallback 보장 — Origin 검증 + mock 4단계 + complete 이벤트).
- **`git diff --cached --stat | grep -E "PlanCard|component_map"` = 0 lines** ★.

## References

- `docs/decisions/phase_5_sse_progress.md` (ADR-022 — SSE 4단계 baseline + Origin 검증 §T4)
- `docs/decisions/phase_8_moa_orchestrator.md` (ADR-027 — ProgressSink Protocol + emit point)
- `ai_system/orchestration/moa_policy.md` §4 (동기/비동기 — Phase 0~10 sync, 11+ 비동기 검토)
- `backend/fastapi/routers/sse.py` (mock 4단계 `_progress_generator` + `_STEPS` — 브릿지 대상)
- `meta/validations/2026-05-29_phase-8-pre-entry_self.md` §V3 (progress_store 브릿지), §V7 (best-effort concurrency)
- `phases/active/phase-8-moa-lite/{goals,scope,non_goals,acceptance,assumptions}.md` (NG1 background task / NG13 WebSocket)
