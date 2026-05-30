"""Phase 8 — ProgressSink (ADR-027 §2 + ADR-028).

orchestrator 가 stage 경계에서 `progress.emit()` 호출.
- `NullProgressSink` (default) = no-op → orchestrator 추출 회귀 0 보장.
- `StoreProgressSink` = Slice 3 progress_store 연동 (본 Slice 2 는 store import 를
  지연/옵션 — store 미존재 시 graceful no-op).

stage 명은 고정 상수 (`intent` / `rag` / `planning` / `critic` / `complete`) —
sse.py `_STEPS` 4단계 + complete 와 1:1 정합 (ADR-027 §2). drift 방지.
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class ProgressSink(Protocol):
    """orchestration stage 진행 이벤트 sink 인터페이스 (의존성 역전).

    emit 반환값은 미사용 (side-effect only) → orchestration 흐름 불변.
    """

    def emit(
        self,
        stage: str,
        *,
        step: int | None = None,
        message: str | None = None,
        **meta: Any,
    ) -> None: ...


class NullProgressSink:
    """no-op sink (default). orchestrator 추출 회귀 0 보장.

    emit 호출돼도 아무 side-effect 없음 → Envelope / DB / plan_store 영향 0.
    """

    def emit(
        self,
        stage: str,
        *,
        step: int | None = None,
        message: str | None = None,
        **meta: Any,
    ) -> None:
        return None


class StoreProgressSink:
    """progress_store 연동 sink. Slice 3 에서 progress_store.record 와 완성.

    본 Slice 2 에서는 plan_id 보관 + record 호출은 graceful (store 미존재 시 no-op).
    progress_store 가 아직 없는 Slice 2 단계에서는 import 실패 → 조용히 no-op.
    """

    def __init__(self, plan_id: str) -> None:
        self.plan_id = plan_id

    def emit(
        self,
        stage: str,
        *,
        step: int | None = None,
        message: str | None = None,
        **meta: Any,
    ) -> None:
        try:
            from backend.fastapi.orchestration.progress_store import record

            event: dict[str, Any] = {
                "type": "progress" if stage != "complete" else "complete",
                "stage": stage,
                "plan_id": self.plan_id,
            }
            if step is not None:
                event["step"] = step
            if message is not None:
                event["message"] = message
            event.update(meta)
            record(self.plan_id, event)
        except Exception:
            return None  # graceful — Slice 3 progress_store 완성 전까지 no-op
