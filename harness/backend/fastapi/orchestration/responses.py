"""Phase 8 — orchestration response helpers (ADR-027 §3).

`routers/plans.py` 의 `_now_iso` / `_not_found_response` / `_error_envelope_response`
함수를 **그대로 이동** (이름만 public 으로: now_iso / not_found_response /
error_envelope_response). 동작·출력·status_code·필드 100% 보존.

plans.py 의 다른 endpoint(plans_start / wizard / get)도 helper 를 사용하므로
plans.py 는 backward-compat 별칭(`_now_iso = now_iso` 등)으로 re-export 한다
(ADR-027 §3 — helper 공유 + 순환 import 회피).
"""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi.responses import JSONResponse

from ..schemas.output import ErrorBody, ErrorEnvelope, ErrorMeta


def now_iso() -> str:
    """ISO8601 UTC ("...Z" 형식)."""
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def not_found_response(plan_id: str) -> JSONResponse:
    """plan_id 미발견 시 ErrorEnvelope (INV-006 — 4계층 참조 무결성)."""
    envelope = ErrorEnvelope(
        error=ErrorBody(
            code="INV-006",
            message=f"plan_id not found: {plan_id}",
            user_message="이전에 만든 데이터를 못 찾았어요. 페이지를 새로고침해주세요.",
            retry_allowed=False,
        ),
        meta=ErrorMeta.make(),
    )
    return JSONResponse(status_code=404, content=envelope.model_dump(mode="json"))


def error_envelope_response(
    *,
    status_code: int,
    code: str,
    message: str,
    user_message: str,
    retry_allowed: bool = True,
) -> JSONResponse:
    """generic ErrorEnvelope 응답 (E-LLM-* / INV-* 등)."""
    envelope = ErrorEnvelope(
        error=ErrorBody(
            code=code,
            message=message,
            user_message=user_message,
            retry_allowed=retry_allowed,
        ),
        meta=ErrorMeta.make(),
    )
    return JSONResponse(status_code=status_code, content=envelope.model_dump(mode="json"))
