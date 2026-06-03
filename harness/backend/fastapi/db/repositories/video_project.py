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
        # Phase 5(0001) video_projects 스키마에는 legacy(001) 컬럼(input_text/request_id/phase 등)이
        # 없어 insert 가 실패한다. 본 legacy save 는 DEPRECATED(ADR-023, Phase 5.5) 이며 Phase 5
        # 스키마에선 적용되지 않는다 → 정상적인 graceful skip 으로 간주(소음 제거: warning→info).
        # ★ plan 영속은 _plan_store(라우터) / PlansRepo(Phase 5, plans 테이블)가 담당하므로
        #   본 경로 실패가 사용자 흐름을 차단하지 않는다(graceful, return None).
        #   (proper 영속 = orchestrator → PlansRepo 마이그레이션, 별도 slice — 테스트 결합으로 분리.)
        msg = str(e)
        if any(k in msg for k in ("input_text", "column", "schema cache", "PGRST204")):
            logger.info(
                "video_projects legacy insert skip — Phase 5(0001) 스키마(레거시 컬럼 부재, "
                "deprecated ADR-023). plan 영속은 _plan_store/PlansRepo 담당."
            )
        else:
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
