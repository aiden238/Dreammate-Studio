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

    Slice 4+ 추가 예정: Supabase, pgvector.
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

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    """싱글톤 settings."""
    return Settings()
