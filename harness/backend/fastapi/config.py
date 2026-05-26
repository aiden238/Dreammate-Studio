"""Settings — env-driven configuration.

Loaded once at app startup via pydantic-settings.
.env 파일 미존재해도 동작 (test에서 fixture로 주입).
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """애플리케이션 설정.

    Phase 1 Slice 1 범위:
      - OpenAI API 키 / 모델
      - 앱 호스트 / 포트
      - 로그 레벨

    Slice 4 추가: pgvector (graceful fallback — env 미설정 시 자동 fallback).
    Slice 5 추가: Supabase URL / anon key (graceful — env 미설정 시 DB 저장 skip).
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # LLM
    openai_api_key: str = Field(default="", description="OpenAI API key")
    openai_model_default: str = Field(
        default="gpt-4o-mini",
        description="Intent + Planning 모델",
    )
    openai_model_critic: str = Field(
        default="gpt-4o",
        description="Critic 모델 (Slice 3 사용)",
    )

    # App
    app_env: Literal["development", "staging", "production"] = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    log_level: str = "INFO"

    # CORS
    cors_origins: str = "http://localhost:3000"

    # ─── DB / pgvector (Slice 4) ─────────────────────────────────────
    # Phase 1: 둘 다 미설정이면 RAG는 자동 fallback (env_missing).
    # Phase 5에서 Supabase DATABASE_URL 도입. pgvector_database_url 은 별도 분리도 가능.
    database_url: str = Field(
        default="",
        description="postgresql:// URL (Supabase Slice 5+에서 사용; Slice 4는 pgvector 통합용 fallback)",
    )
    pgvector_database_url: str = Field(
        default="",
        description="postgresql:// URL for pgvector (없으면 database_url 재사용)",
    )
    pgvector_table: str = Field(
        default="rag_chunks",
        description="pgvector chunks 테이블 이름 (rag_data_contract.md §3 정합)",
    )
    pgvector_top_k: int = Field(
        default=3,
        description="검색 상위 N (retrieval_policy.md §2 — Phase 1 default 3, contract default 5)",
    )
    pgvector_threshold: float = Field(
        default=0.7,
        description="cosine similarity 최소값 (retrieval_policy.md §2)",
    )

    # ─── Supabase (Slice 5) ─────────────────────────────────────────
    # Phase 1: 둘 다 미설정이면 DB 저장은 자동 skip (응답 meta.project_id=null + 200).
    # supabase-py 미설치 시에도 graceful skip (import 실패 catch).
    supabase_url: str = Field(
        default="",
        description="Supabase project URL (https://xxxx.supabase.co)",
    )
    supabase_anon_key: str = Field(
        default="",
        description="Supabase anon key (Phase 1 익명 저장용; Phase 5 Auth 도입 시 RLS + service_role 전환)",
    )

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    """싱글톤 settings."""
    return Settings()
