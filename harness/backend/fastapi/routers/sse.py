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
    """4 단계 progress + complete 이벤트 생성기.

    실 구현은 plan 생성 worker (Phase 6+ orchestration) 와 연동하여
    각 단계 완료 시점에 emit 한다. 본 baseline 은 SSE event schema 검증용
    최소 흐름으로, 단계 간 짧은 yield 만 수행.
    """
    for step_info in _STEPS:
        event = {
            "type": "progress",
            "step": step_info["step"],
            "name": step_info["name"],
            "message": step_info["message"],
            "duration_estimate_sec": step_info["duration_estimate_sec"],
            "plan_id": plan_id,
        }
        yield _sse_event(event)
        # 짧은 yield (실 구현은 worker 와 동기). 테스트 안정성을 위해 매우 짧게.
        await asyncio.sleep(0)

    complete = {
        "type": "complete",
        "step": 4,
        "message": "완료",
        "plan_id": plan_id,
    }
    yield _sse_event(complete)


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
