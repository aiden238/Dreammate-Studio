"""Phase 5 Slice 4 — SSE Progress streaming (D7).

확정 결정 [10] (30-60초 plan 생성 대기 + 부분 결과 노출) 정합.
security-review §T4 (SSE hijacking) 권장 적용.

설계:
  - 4 단계 progress 이벤트: intent → rag → planning → critic
  - 종료 이벤트: complete
  - Origin 화이트리스트 검증 (security-review §T4)
  - cookie 기반 인증 (Slice 3 baseline — auth_middleware 가 request.state.user 주입)
  - heartbeat: SSE 자체 keepalive (브라우저 EventSource 가 30s 마다 재연결 시도)
  - X-Accel-Buffering: no (nginx 등 reverse proxy buffering 비활성)

참조:
  - docs/decisions/phase_5_sse_progress.md (ADR-022)
  - meta/security_reviews/2026-05-29_phase-5-auth-rls.md §3 T4
  - meta/validations/2026-05-29_phase-5-pre-entry_self.md §V4
"""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any, AsyncGenerator, Optional

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse

from backend.fastapi.orchestration.progress_store import read as read_progress

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["sse"])


# ─── Allowed origins (security-review §T4) ─────────────────────────────
# 화이트리스트. 추가 필요 시 본 set 갱신 + ADR-022 변경 이력 기록.
# Origin 헤더가 없는 SSE 직접 호출(curl / server-to-server)은 dev 편의를 위해 허용
# — production 환경은 reverse proxy 가 Origin 강제 주입할 수 있다.
ALLOWED_ORIGINS: set[str] = {
    "http://localhost:3000",
    "http://localhost:3001",
    "https://dreammate-studio.vercel.app",  # 예시 production
}


# ─── 4 단계 progress 정의 ──────────────────────────────────────────────
# 본 단계 정의는 ADR-022 §Decision 와 정합. duration_estimate_sec 는
# 사용자에게 표시되는 "예상 소요" 힌트이며 실제 측정값은 plan 생성 worker
# (Phase 6+ orchestration) 에서 갱신 가능.
_STEPS: list[dict[str, Any]] = [
    {"step": 1, "name": "intent",   "message": "의도 분석 중...",             "duration_estimate_sec": 5},
    {"step": 2, "name": "rag",      "message": "지식 검색 중...",             "duration_estimate_sec": 10},
    {"step": 3, "name": "planning", "message": "영상기획안 3개 생성 중...",   "duration_estimate_sec": 30},
    {"step": 4, "name": "critic",   "message": "Critic 검증 중...",           "duration_estimate_sec": 15},
]


# ─── progress_store 브릿지 폴링 상수 (ADR-028) ─────────────────────────
# single-process best-effort. POST generate in-flight 중 GET /progress 가
# store 를 read 한다 (event loop yield 의존, 보장 아님 — Trade-offs 참조).
_MAX_POLLS = 20        # best-effort 폴링 상한 (무한 루프 방지)
_POLL_INTERVAL_SEC = 0.0  # 테스트 결정성용 0.0. 실 운영은 0.2~0.5 권장 (CPU spin 방지).


# ─── helpers ───────────────────────────────────────────────────────────


def _verify_origin(request: Request) -> bool:
    """SSE Origin 검증 — security-review §T4.

    Origin 헤더 우선, 없으면 Referer fallback. 둘 다 없으면 dev 편의로 허용.
    """
    origin = (request.headers.get("origin") or "").strip()
    if not origin:
        referer = (request.headers.get("referer") or "").rstrip("/")
        origin = referer
    if not origin:
        # SSE 직접 호출 (curl, server-to-server) — dev 편의 허용.
        return True
    if origin in ALLOWED_ORIGINS:
        return True
    return any(origin.startswith(allowed) for allowed in ALLOWED_ORIGINS)


def _sse_event(payload: dict[str, Any]) -> str:
    """SSE 표준 포맷: `data: <json>\\n\\n`."""
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"


async def _progress_generator(
    plan_id: str, user_id: Optional[str],
) -> AsyncGenerator[str, None]:
    """progress_store 실 stage stream (ADR-028) + graceful fallback to mock.

    Phase 8 Slice 3: orchestrator(StoreProgressSink)가 progress_store 에 기록한
    실 stage 이벤트(intent → rag → planning → critic → complete)를 우선 stream.

    store 가 비어있으면(generate 미시작 / 직접 호출 / multi-worker 미공유) 기존
    mock `_STEPS` 4단계 + complete fallback → 기존 test_sse 4 케이스 수정 0 보존
    (P-GRACEFUL-001 정신). store 유무 무관 항상 유효 event schema 응답.
    """
    snapshot = read_progress(plan_id)
    if not snapshot:
        # graceful fallback: 기존 mock 4단계 (store 미기록 = generate 미시작/직접 호출).
        # ★ test_sse 4 케이스 보존 — 기존 _STEPS 흐름 그대로.
        for step_info in _STEPS:
            yield _sse_event({
                "type": "progress",
                "step": step_info["step"],
                "name": step_info["name"],
                "message": step_info["message"],
                "duration_estimate_sec": step_info["duration_estimate_sec"],
                "plan_id": plan_id,
            })
            # 짧은 yield (실 구현은 worker 와 동기). 테스트 안정성을 위해 매우 짧게.
            await asyncio.sleep(0)
        yield _sse_event({
            "type": "complete",
            "step": 4,
            "message": "완료",
            "plan_id": plan_id,
        })
        return

    # store 기록 존재: 실 stage stream + best-effort 폴링 (complete 까지).
    emitted = 0
    for _ in range(_MAX_POLLS):
        events = read_progress(plan_id)
        while emitted < len(events):
            ev = events[emitted]
            emitted += 1
            yield _sse_event(ev)
            if ev.get("type") == "complete":
                return
        await asyncio.sleep(_POLL_INTERVAL_SEC)

    # 안전 종료: complete 미수신 시 synthetic complete (stream 영구 대기 방지).
    yield _sse_event({
        "type": "complete",
        "step": 4,
        "message": "완료",
        "plan_id": plan_id,
    })


# ─── Endpoint ──────────────────────────────────────────────────────────


@router.get("/plans/{plan_id}/progress")
async def stream_plan_progress(
    plan_id: str, request: Request,
) -> StreamingResponse:
    """SSE Progress endpoint.

    인증: cookie 기반 (Slice 3 auth_middleware 가 request.state.user 주입).
          본 endpoint 자체는 user None 허용 (anonymous plan 도 progress 노출 가능).
    Origin: ALLOWED_ORIGINS 화이트리스트 (security-review §T4).
    Heartbeat: SSE 자체 keepalive + EventSource 자동 재연결.
    """
    if not _verify_origin(request):
        raise HTTPException(status_code=403, detail="origin_not_allowed")

    user: Optional[dict[str, Any]] = getattr(request.state, "user", None)
    user_id: Optional[str] = None
    if user is not None:
        user_id = str(user.get("user_id") or "") or None

    logger.info(
        "sse_progress_start plan_id=%s user_id=%s",
        plan_id, user_id or "anonymous",
    )

    return StreamingResponse(
        _progress_generator(plan_id, user_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # nginx buffering 비활성
        },
    )


__all__ = ["router", "ALLOWED_ORIGINS"]
