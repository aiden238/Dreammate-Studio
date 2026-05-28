"""Dreammate Studio FastAPI app — Phase 1 Slice 5 + Phase 4 Slice 1.

Run:
    uvicorn backend.fastapi.main:app --reload --port 8000

또는 (backend/fastapi/ 디렉토리에서):
    uvicorn main:app --reload --port 8000

검증:
    # Phase 1 endpoint (Phase 8+ 제거 예정 — X-API-Deprecation header 노출)
    curl -X POST http://localhost:8000/api/v1/generate \\
      -H "Content-Type: application/json" \\
      -d '{"input":"유튜브 채널 첫 영상 기획해줘"}'

    # Phase 4 contract endpoints
    curl -X POST http://localhost:8000/api/v1/plans/start \\
      -H "Content-Type: application/json" -d '{"locale":"ko-KR"}'
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .routers import generate_router, plans_router


# ─── Logging ──────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("dreammate")


# ─── Lifespan ─────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """앱 시작 / 종료 hook."""
    settings = get_settings()
    logger.info(
        "Dreammate FastAPI 시작 — env=%s host=%s:%d model=%s",
        settings.app_env,
        settings.app_host,
        settings.app_port,
        settings.openai_model_default,
    )
    if not settings.openai_api_key:
        logger.warning("OPENAI_API_KEY 미설정 — 실제 LLM 호출 시 실패합니다")

    yield  # ─── 앱 실행 중 ───

    logger.info("Dreammate FastAPI 종료")


# ─── App ──────────────────────────────────────────────────────────────

def create_app() -> FastAPI:
    """FastAPI app factory (테스트 시 재사용 가능)."""
    settings = get_settings()

    app = FastAPI(
        title="Dreammate Studio API",
        description=(
            "영상기획 AI 에이전트 백엔드 (Phase 1 Slice 5 + Phase 4 Slice 1).\n\n"
            "Phase 1 endpoint (Phase 8+ 제거 예정 — ADR-014): "
            "`POST /api/v1/generate` "
            "(Intent → RAG → Planning(rag_context) → Critic → DB save, 1 plan).\n"
            "  - X-API-Deprecation 응답 header 노출 (실 동작 무변경).\n\n"
            "Phase 4 contract endpoints (api_contract.md §8):\n"
            "  - `POST /api/v1/plans/start` — 신규 plan_id 발급\n"
            "  - `POST /api/v1/plans/{plan_id}/wizard/{step}` — Discovery/Quick step (skeleton)\n"
            "  - `POST /api/v1/plans/{plan_id}/generate` — 3-plan generation (Slice 1 skeleton, Slice 2 본격)\n"
            "  - `GET /api/v1/plans/{plan_id}` — 결과 조회\n\n"
            "RAG는 pgvector 미가용 시 graceful fallback (빈 references).\n"
            "DB 저장은 Supabase 미설정/실패 시 graceful skip (meta.project_id=null, 200 응답).\n"
            "Critic은 8 차원 평가만 수행 (revise 없음, Phase 4.5+에서 추가)."
        ),
        version="0.6.0",  # Phase 4 Slice 1 (contract endpoints 추가)
        lifespan=lifespan,
    )

    # CORS (Slice 6에서 실사용)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )

    # Routers
    app.include_router(generate_router)  # Phase 1 endpoint (Phase 8+ 제거 예정)
    app.include_router(plans_router)  # Phase 4 contract endpoints

    # Health check (Slice 1 부수적 — uvicorn 부트 확인용).
    # Phase 1 baseline 보존: phase/slice 값은 Phase 1 베이스라인 유지 (회귀 0).
    # Phase 4 정보는 description / version에 반영됨.
    @app.get("/health", tags=["meta"])
    def health() -> dict[str, str]:
        return {
            "status": "ok",
            "phase": "1",
            "slice": "5",
            "version": app.version,
        }

    return app


app = create_app()
