"""Dreammate Studio FastAPI app — Phase 1 Slice 1.

Run:
    uvicorn backend.fastapi.main:app --reload --port 8000

또는 (backend/fastapi/ 디렉토리에서):
    uvicorn main:app --reload --port 8000

검증:
    curl -X POST http://localhost:8000/api/v1/generate \\
      -H "Content-Type: application/json" \\
      -d '{"input":"유튜브 채널 첫 영상 기획해줘"}'
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .routers import generate_router


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
            "영상기획 AI 에이전트 백엔드 (Phase 1 Slice 1).\n\n"
            "현재 활성 endpoint: `POST /api/v1/generate`.\n"
            "Phase 4에서 api_contract.md §8.3 (async + SSE) 형식으로 migration 예정."
        ),
        version="0.1.0",  # Phase 1 Slice 1
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
    app.include_router(generate_router)

    # Health check (Slice 1 부수적 — uvicorn 부트 확인용)
    @app.get("/health", tags=["meta"])
    def health() -> dict[str, str]:
        return {
            "status": "ok",
            "phase": "1",
            "slice": "1",
            "version": app.version,
        }

    return app


app = create_app()
