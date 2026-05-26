"""plan_candidates 테이블 insert — Phase 1 Slice 5.

Slice 4 QA report §5.3(a) 인계 가이드 적용:
  - body.rag_references 는 plan_candidates.raw_llm_json JSONB 컬럼에 통합 저장.
  - critic_evaluation 도 동일 raw_llm_json 에 같이 저장 (Phase 1 단순화).
  - Phase 2+ 정규화 (plan_candidate_rag_usage 테이블) 는 별도 migration.

graceful 정책: 어떤 실패도 raise 하지 않고 None 반환.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


def insert_plan_candidate(
    client: Any | None,
    *,
    project_id: str | None,
    plan: dict[str, Any],
    critic: dict[str, Any] | None,
    rag_refs: list[dict[str, Any]],
) -> str | None:
    """plan_candidates row 1개 insert. 실패 시 None 반환 (raise 금지).

    Args:
        client: Supabase 클라이언트 (None이면 skip).
        project_id: video_projects.id (None이면 FK 무결성을 위해 skip).
        plan: Plan.model_dump() 결과 dict.
        critic: CriticEvaluation.model_dump() 결과 또는 None.
        rag_refs: list[RAGReference.model_dump()] (Slice 4 결과).

    Returns:
        plan_candidate_id (uuid 문자열) 또는 None.
    """
    if client is None or project_id is None:
        return None

    raw_llm_json = {
        "plan": plan,
        "critic_evaluation": critic,
        "rag_references": rag_refs,  # Slice 4 QA 가이드 §5.3(a)
    }

    row = {
        "project_id": project_id,
        "option_index": int(plan.get("option_index", 0)),
        "name": plan.get("name"),
        "concept": plan.get("concept"),
        "hook": plan.get("hook"),
        "approach_label": plan.get("approach_label", "informational"),
        "raw_llm_json": raw_llm_json,
    }

    try:
        resp = client.table("plan_candidates").insert(row).execute()
    except Exception as e:
        logger.warning("plan_candidates insert failed: %s", e)
        return None

    try:
        data = getattr(resp, "data", None)
        if not data:
            logger.warning("plan_candidates insert returned empty data: %r", resp)
            return None
        plan_id = data[0].get("id")
        if not plan_id:
            logger.warning("plan_candidates insert: 'id' missing in response data: %r", data[0])
            return None
        return str(plan_id)
    except Exception as e:
        logger.warning("plan_candidates insert response parse failed: %s", e)
        return None


__all__ = ["insert_plan_candidate"]
