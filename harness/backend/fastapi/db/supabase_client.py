"""Supabase 클라이언트 wrapper — Phase 1 Slice 5.

graceful 정책:
  - SUPABASE_URL 또는 SUPABASE_ANON_KEY 미설정 → None 반환 (정상 skip).
  - supabase-py import 실패 또는 create_client 예외 → None 반환 + warning 로그.
  - 어떤 경우에도 사용자 요청을 차단하지 않는다 (raise 금지).

호출자는 None 반환을 받으면 PersistenceResult(status="skipped_no_db") 로 처리한다.
"""

from __future__ import annotations

import logging
from typing import Any

from ..config import get_settings

logger = logging.getLogger(__name__)


def get_supabase_client() -> Any | None:
    """Supabase Client 또는 None 반환.

    Phase 1 graceful 정책:
      - env 미설정 → None (skip)
      - supabase 패키지 미설치 → None (skip + warning)
      - create_client 예외 → None (skip + warning)
    """
    settings = get_settings()
    if not (settings.supabase_url and settings.supabase_anon_key):
        return None

    try:
        # 지연 import — supabase 미설치 환경에서도 backend가 import-time crash 안 함.
        from supabase import create_client  # type: ignore[import-not-found]
    except Exception as e:  # ImportError 포함
        logger.warning("Supabase 패키지 import 실패 — DB 저장 skip: %s", e)
        return None

    try:
        return create_client(settings.supabase_url, settings.supabase_anon_key)
    except Exception as e:
        logger.warning("Supabase create_client 실패 — DB 저장 skip: %s", e)
        return None


__all__ = ["get_supabase_client"]
