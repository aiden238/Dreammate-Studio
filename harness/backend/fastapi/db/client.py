"""Phase 5 Slice 2 — Supabase client factory (Protocol-based + graceful fallback).

기존 `supabase_client.py` (Phase 1 Slice 5) 와 공존한다.
- supabase_client.get_supabase_client() : Phase 1 baseline (save_video_planning orchestrator 용).
- client.get_supabase()                  : Phase 5 신규 (PlansRepo + 향후 PlansRepo CRUD 용).

두 factory 모두 동일한 환경변수 (SUPABASE_URL / SUPABASE_ANON_KEY) 를 참조한다.
graceful 정책 동일:
  - env 미설정 → None (in-memory fallback)
  - supabase 패키지 미설치 → None
  - create_client 예외 → None

Phase 5 신규 추가: SUPABASE_SERVICE_KEY (선택, RLS 우회 server-side 운영용).
"""

from __future__ import annotations

import logging
from typing import Any, Optional, Protocol, runtime_checkable

logger = logging.getLogger(__name__)


@runtime_checkable
class SupabaseClientLike(Protocol):
    """Minimal protocol for Supabase client (or mock).

    Phase 5 Slice 2 범위:
      - table(name) → query builder (PostgREST 호환).

    Slice 3 (Auth) / Slice 4 (RLS + SSE) 에서 auth, storage 등 메서드 확장 예정.
    """

    def table(self, name: str) -> Any: ...


def get_supabase() -> Optional[SupabaseClientLike]:
    """Get Supabase client or None (graceful fallback to in-memory).

    환경변수 SUPABASE_URL + SUPABASE_ANON_KEY 가 모두 설정되어 있어야 client 반환.
    미설정 시 None 반환 → 호출자는 in-memory _plan_store dict 로 graceful fallback.

    Slice 2 spec (ADR-020 §Implementation impact):
      - vendor lock-in 완화: 추상화 계층 (PlansRepo) 도입 후 본 factory 통해 주입.
      - 실패 시 raise 금지 (Phase 1 graceful 정책 계승).
    """
    from .. import config as _config_module

    settings = _config_module.get_settings()

    url = getattr(settings, "supabase_url", None) or ""
    key = getattr(settings, "supabase_anon_key", None) or ""

    if not url or not key:
        logger.info("supabase_unconfigured — falling back to in-memory store")
        return None

    try:
        # 지연 import — supabase 미설치 환경에서도 backend import-time crash 안 함.
        from supabase import create_client  # type: ignore[import-not-found]
    except ImportError:
        logger.warning("supabase package not installed — falling back to in-memory store")
        return None
    except Exception as exc:
        logger.warning(
            "supabase_import_failed: %s — falling back to in-memory",
            exc.__class__.__name__,
        )
        return None

    try:
        client = create_client(url, key)
        return client
    except Exception as exc:
        logger.warning(
            "supabase_client_init_failed: %s — falling back to in-memory",
            exc.__class__.__name__,
        )
        return None


__all__ = ["get_supabase", "SupabaseClientLike"]
