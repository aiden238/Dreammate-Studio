"""video_projects 테이블 insert — Phase 1 Slice 5.

graceful 정책: 어떤 실패도 raise 하지 않고 None 반환.

Phase 1 단순화 (db_schema.md §3.5 contract 와의 deviation):
  - Phase 1은 brand/series/domain 미도입 → series_id NOT NULL 미사용.
  - 익명 저장이므로 user_id NULL allow.
  - Phase 5에서 Auth 추가 시 user_id NOT NULL + RLS + series FK 정합.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


def insert_video_project(
    client: Any | None,
    *,
    request_id: str,
    input_text: str,
    locale: str,
) -> str | None:
    """video_projects row 1개 insert. 실패 시 None 반환 (raise 금지).

    Returns:
        project_id (uuid 문자열) 또는 None.
    """
    if client is None:
        return None

    row = {
        "request_id": request_id,
        "input_text": input_text,
        "locale": locale,
        "user_id": None,  # Phase 1: 익명 (Phase 5 Auth 도입 시 NOT NULL)
        "phase": 1,
        "slice": 5,
    }

    try:
        resp = client.table("video_projects").insert(row).execute()
    except Exception as e:
        logger.warning("video_projects insert failed: %s", e)
        return None

    try:
        data = getattr(resp, "data", None)
        if not data:
            logger.warning("video_projects insert returned empty data: %r", resp)
            return None
        project_id = data[0].get("id")
        if not project_id:
            logger.warning("video_projects insert: 'id' missing in response data: %r", data[0])
            return None
        return str(project_id)
    except Exception as e:
        logger.warning("video_projects insert response parse failed: %s", e)
        return None


__all__ = ["insert_video_project"]
