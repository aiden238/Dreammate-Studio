"""HIP-006 — agent_io 텔레메트리 발신기 (1 LLM 호출 = 1 JSONL record).

배경 (meta/audits/2026-06-05.md §3 / HIP-006):
  self_improvement_loop §1.2 가 패턴 마이닝 입력으로 'agent_io_logs' 를 선언했으나
  실제 기록 코드가 0건이었다 → cost-review / patterns 자동마이닝 / skill_usage_log /
  HIP-004(정량 임계) 가 동시에 "데이터 부재"로 동결. 본 모듈이 그 데이터원을 채운다.

설계 원칙 (하네스 규율 정합):
  - gated default-off (`agent_io_log_enabled` default False) → 기존 hermetic pytest 파일쓰기 0
    (behavior-preserving). flag OFF 면 즉시 False 반환 — 오버헤드 0.
  - graceful (P-GRACEFUL-001) — 로깅 실패(디스크/직렬화)가 생성 흐름을 절대 차단하지 않는다.
    log_agent_io 는 어떤 경우에도 raise 하지 않고 True/False 만 반환.
  - additive — Envelope/응답 불변 (관측만, 출력 변경 0).
  - 필드는 docs/contracts/db_schema.md §7.1 agent_io_logs 컬럼과 정합 (장차 DB write 승격 가능).
"""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from typing import Any

from ..config import get_settings

logger = logging.getLogger(__name__)

# ─── 가격 추정 맵 (USD per 1M tokens, (input_rate, output_rate)) ──────────
# ★ 추정치 — 정확/최신 단가의 단일 출처는 ai_system/orchestration/cost_control_policy.md.
#   미등록 모델은 None 반환(graceful) → cost-review 가 사후 보정. gemini-3.5-flash 단가는
#   config.cross_validation_model 설명($1.5/$9) 근거.
_PRICE_PER_1M: dict[str, tuple[float, float]] = {
    "gpt-4o-mini": (0.15, 0.60),
    "gpt-4o": (2.50, 10.00),
    "gemini-3.5-flash": (1.50, 9.00),
}


def estimate_cost_usd(
    model: str, input_tokens: int, output_tokens: int
) -> float | None:
    """model + 토큰 → 추정 비용(USD). 미등록 모델이면 None (graceful)."""
    price = _PRICE_PER_1M.get(model)
    if price is None:
        return None
    in_rate, out_rate = price
    return round((input_tokens * in_rate + output_tokens * out_rate) / 1_000_000, 6)


def log_agent_io(
    *,
    agent_name: str,
    model: str,
    provider: str = "",
    input_tokens: int = 0,
    output_tokens: int = 0,
    latency_ms: int | None = None,
    success: bool = True,
    fallback: bool = False,
    error: str | None = None,
    prompt_id: str | None = None,
    prompt_version: str | None = None,
    request_id: str | None = None,
    cost_usd: float | None = None,
    **extra: Any,
) -> bool:
    """agent_io 텔레메트리 1행 기록 (gated + graceful).

    flag(`agent_io_log_enabled`) OFF 면 아무것도 하지 않고 False 반환.
    ON 이면 settings.agent_io_log_path 에 JSON 한 줄을 append 한다.

    Returns:
        기록되면 True, (비활성/실패로) 미기록이면 False. ★ 절대 raise 하지 않는다.
    """
    try:
        settings = get_settings()
        if not getattr(settings, "agent_io_log_enabled", False):
            return False
        if cost_usd is None:
            cost_usd = estimate_cost_usd(model, input_tokens, output_tokens)
        record: dict[str, Any] = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "request_id": request_id,
            "agent_name": agent_name,
            "prompt_id": prompt_id,
            "prompt_version": prompt_version,
            "provider": provider,
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
            "cost_usd": cost_usd,
            "latency_ms": latency_ms,
            "success": success,
            "fallback": fallback,
            "error": error,
        }
        if extra:
            record.update(extra)
        path = getattr(
            settings, "agent_io_log_path", "logs/telemetry/agent_io.jsonl"
        )
        parent = os.path.dirname(path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
        return True
    except Exception as exc:  # ★ graceful — 로깅 실패가 생성 흐름을 막지 않는다
        logger.debug("agent_io_log 기록 실패 (graceful skip): %s", exc)
        return False
