"""DEPRECATED (Phase 5.5, 2026-05-29).

Phase 1 Slice 5 에서 작성된 legacy Supabase client factory.
Phase 5 에서 신규 `backend.fastapi.db.client.get_supabase()` 도입 → 본 모듈은 backward-compat 용.

새 코드는 `from backend.fastapi.db import get_supabase` 사용 권장.

Removal 일정: Phase 7+ RAG 통합 후 검토 (ADR-023 참조).

---

Supabase 클라이언트 wrapper — Phase 1 Slice 5 (원본 docstring).

graceful 정책:
  - SUPABASE_URL 또는 SUPABASE_ANON_KEY 미설정 → None 반환 (정상 skip).
  - supabase-py import 실패 또는 create_client 예외 → None 반환 + warning 로그.
  - 어떤 경우에도 사용자 요청을 차단하지 않는다 (raise 금지).

호출자는 None 반환을 받으면 PersistenceResult(status="skipped_no_db") 로 처리한다.
"""

from __future__ import annotations

import logging
import warnings as _warnings
from typing import Any

from ..config import get_settings

logger = logging.getLogger(__name__)

# Phase 5.5 ADR-023 — legacy factory deprecation marker.
# import 시 한 번만 발행 (호출 시 발행은 노이즈가 너무 큼).
_warnings.warn(
    "backend.fastapi.db.supabase_client is deprecated (Phase 5.5). "
    "Use backend.fastapi.db.client.get_supabase() instead. "
    "Scheduled removal: Phase 7+ (see ADR-023).",
    DeprecationWarning,
    stacklevel=2,
)


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
