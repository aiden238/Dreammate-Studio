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

    # ─── Phase 11 A안 Slice 1 — LLM Gateway (additive, graceful) ─────
    # 기존 openai_* Field 보존. gateway/registry 가 참조 (제안서 §9 / §18.C).
    # ★ behavior-preserving: 본 Field 추가는 gateway 신규 패키지 전용 — 기존 agents 미연결.
    # ★ 실 키 불필요: graceful default="" (미설정 시 해당 provider 비활성 → gateway LLMError).
    #   키는 .env(이미 .gitignore)에만. 코드/commit/채팅 평문 절대 금지.
    google_api_key: str = Field(
        default="",
        description=(
            "Google Gemini API key (Phase 11 A안 cross_validation). "
            "graceful: 미설정 시 Gemini provider 비활성. "
            "GEMINI_API_KEY 대신 GOOGLE_API_KEY 사용 (제안서 §18.C)."
        ),
    )
    cross_validation_model: str = Field(
        default="gemini-3.5-flash",
        description=(
            "Phase 11 A안 cross_validation Gemini model_id (registry 'gemini-cross'). "
            "★ 사용자 확정 (2026-06): gemini-3.5-flash (live models.list 확인, $1.5/$9, Search grounding). "
            "환경변수 CROSS_VALIDATION_MODEL 로 override 가능 (agent 코드 0 변경)."
        ),
    )

    # ─── Phase 11 B안 Slice 1 — Anthropic(Claude) provider (additive, graceful) ─
    # ★ behavior-preserving: gateway 신규 provider 전용 — 기존 agents 미연결.
    #   default 호출 경로(OpenAI workhorse/critic) 불변. anthropic 미설정 시 비활성.
    # ★ 실 키 불필요: graceful default="" (미설정 시 anthropic provider 비활성
    #   → gateway LLMError("missing key")). 키는 .env(이미 .gitignore)에만.
    #   코드/commit/채팅 평문 절대 금지 (제안서 §18.C).
    anthropic_api_key: str = Field(
        default="",
        description=(
            "Anthropic Claude API key (Phase 11 B안 — Claude provider). "
            "graceful: 미설정 시 Anthropic provider 비활성 (gateway LLMError). "
            "환경변수 ANTHROPIC_API_KEY (제안서 §18.C)."
        ),
    )
    # ★ Claude model_id 는 placeholder — 사용자가 dev 페이지에서 정확한 ID 를 확정한다.
    #   registry 'claude-haiku'/'claude-sonnet' 가 조회 시점에 이 값을 읽어 model_id 결정
    #   (provider 추가 = registry 항목 + config Field, agent 코드 0 변경 — 제안서 §2/§5.2).
    anthropic_model_haiku: str = Field(
        default="claude-haiku-4-5",
        description=(
            "Phase 11 B안: Anthropic workhorse model_id (registry 'claude-haiku'). "
            "★ placeholder (제안서 §18.B 2026-06 라인업) — 사용자 dev 페이지 확인값 확정 필요. "
            "환경변수 ANTHROPIC_MODEL_HAIKU 로 override 가능 (agent 코드 0 변경)."
        ),
    )
    anthropic_model_sonnet: str = Field(
        default="claude-sonnet-4-6",
        description=(
            "Phase 11 B안: Anthropic critic-급 model_id (registry 'claude-sonnet'). "
            "★ placeholder (제안서 §18.B 2026-06 라인업) — 사용자 dev 페이지 확인값 확정 필요. "
            "환경변수 ANTHROPIC_MODEL_SONNET 로 override 가능 (agent 코드 0 변경)."
        ),
    )
    # ★ Gemini workhorse model_id (registry 'gemini-flash', B안 3-plan 슬롯3 plan_tertiary).
    #   gemini-cross 와 동일하게 config Field 로 교체 가능 — 조회 시점에 registry 가 읽는다.
    #   default 는 live 확인된 gemini-3.5-flash (이전 placeholder "gemini-3-flash" 는 404 NOT_FOUND).
    gemini_flash_model: str = Field(
        default="gemini-3.5-flash",
        description=(
            "Phase 11 B안: Gemini workhorse model_id (registry 'gemini-flash', plan_tertiary). "
            "★ live 확인값 (2026-06): gemini-3.5-flash (cross_validation 과 동일 라인). "
            "환경변수 GEMINI_FLASH_MODEL 로 override 가능 (agent 코드 0 변경)."
        ),
    )

    # ─── Phase 11 A안 Slice 2 — cross-validation 게이트 + Gemini 튜닝 (additive) ─
    # ★ behavior-preserving / gated default-off: cross_validation_enabled=False →
    #   호출측(orchestrator 등)에서 교차검증 skip. 본 Slice 는 모듈만 추가 — 자동
    #   연결 0 (orchestrator 미변경). 기존 Field 전부 보존.
    cross_validation_enabled: bool = Field(
        default=False,
        description=(
            "Phase 11 A안 Slice 2: Critic 교차검증(Gemini) pass 활성 여부. "
            "★ gated default-off — False 면 호출측에서 cross_validate 를 skip "
            "(orchestrator 미연결, behavior-preserving). True 활성은 유료 정책/키 확정 후. "
            "환경변수 CROSS_VALIDATION_ENABLED 로 override."
        ),
    )
    gemini_thinking_budget: int = Field(
        default=0,
        ge=0,
        description=(
            "Phase 11 A안 Slice 2: Gemini 3.x flash thinking budget (tokens). "
            "★ default 0 = thinking 비활성 → max_output_tokens 가 추론에 소진되지 않고 "
            "출력에 온전히 사용(출력 0 문제 방지). SDK 가 ThinkingConfig 미지원이면 graceful skip. "
            "환경변수 GEMINI_THINKING_BUDGET 로 override."
        ),
    )

    # ─── Phase 11 B안 Slice S2b-2a — 3-provider 다양성 게이트 (additive) ─
    # ★ behavior-preserving / gated default-off: True 여도 본 Slice 는 신규 함수
    #   run_planning_multi_provider_3 를 추가만 — 아무 곳도 호출 X (orchestrator 분기는
    #   후속 S2b-2b). False 일 때 기존 OpenAI 3-call(run_planning_parallel_3) 경로 유지.
    multi_provider_plans_enabled: bool = Field(
        default=False,
        description="B안: 3-plan 을 3-provider(GPT/Claude/Gemini) alias 로 다양화 (gated, default OFF).",
    )

    # ─── Phase 13 Slice S3 — rich 출력 게이트 (additive, default False) ─
    # ★ behavior-preserving / gated default-off: OFF=compact byte-identical
    #   (Plan.model_dump_compact() 가 rich 슬롯 제외 → Phase 13 이전 응답과 동일),
    #   ON=rich(확장 스키마+RICH_SYSTEM_PROMPT). 기존 486 테스트는 OFF default 라 불변.
    rich_output_enabled: bool = Field(
        default=False,
        description=(
            "Phase 13: rich 출력(확장 스키마+프롬프트) 활성. "
            "OFF=compact byte-identical, ON=rich. 환경변수 RICH_OUTPUT_ENABLED."
        ),
    )

    # ─── Phase 4 Slice 2: multi-model (사용자 결정 4-b) ─────────────────
    # 향후 모델 추가 가능 구조 — Phase 4는 OpenAI만 (default 동일 모델 × 3).
    # Anthropic / Google 등 multi-provider 확장은 Phase 21+에서 검토.
    openai_models_for_3plan: str = Field(
        default="gpt-4o-mini,gpt-4o-mini,gpt-4o-mini",
        description=(
            "Comma-separated 3 model names for parallel 3-plan generation. "
            "Phase 4 default: 동일 모델 × 3 (cost 효율). "
            "향후 모델 추가 가능 (예: 'gpt-4o-mini,gpt-4o-mini,gpt-4o' 또는 multi-provider). "
            "사용자 결정 4-b: 모델 추가 가능성 염두."
        ),
    )

    # ─── Phase 4.5 — Critic revise loop ─────────────────────────────
    # 0=loop 비활성, 1~2 권장. 환경변수 CRITIC_MAX_REVISE 로 override 가능.
    # Critic verdict 가 'revise' 일 때 Rewriter(P-008) 를 최대 N회 호출한다.
    critic_max_revise: int = Field(
        default=2,
        ge=0,
        le=5,
        description=(
            "Phase 4.5: Critic revise loop 최대 횟수 (0=비활성). "
            "확정 결정 [5]: 무한 루프 차단 위해 2회 상한. "
            "환경변수 CRITIC_MAX_REVISE 로 override 가능."
        ),
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
    # Phase 5 Slice 2 신규 — RLS 우회 server-side 운영용 (Auth/RLS 도입 Slice 3/4 + ADR-021).
    # 절대 NEXT_PUBLIC_* prefix 금지 (llm_security_contract.md §5.2).
    supabase_service_key: str = Field(
        default="",
        description=(
            "Supabase service role key (server-side only, RLS bypass). "
            "Phase 5 Slice 2 신규. NEXT_PUBLIC_* prefix 절대 금지."
        ),
    )

    # ─── Phase 7 Slice 3 — RAG Lite (ADR-025) ───────────────────────
    # Phase 1 pgvector_* baseline 보존 + Phase 7 RAG Lite 정식 env 신규.
    # 환경변수 RAG_* prefix 자동 매핑 (pydantic_settings BaseSettings).
    # 교체 가능 구조 (Phase 21+ Custom embedding 대비, ADR-024 §B).
    rag_embedding_model: str = Field(
        default="text-embedding-3-small",
        description=(
            "Phase 7: OpenAI embedding model (ADR-025 §2). "
            "1536 dim. 환경변수 RAG_EMBEDDING_MODEL 로 override 가능 "
            "(Phase 21+ Custom embedding 교체 시 사용)."
        ),
    )
    rag_embedding_dim: int = Field(
        default=1536,
        description=(
            "Phase 7: embedding vector dimension (ADR-025 §2). "
            "text-embedding-3-small native 1536. "
            "model 교체 시 migration 필요 (ADR-025 §Trade-offs)."
        ),
    )
    rag_chunk_size: int = Field(
        default=512,
        description=(
            "Phase 7: chunk size in tokens (ADR-025 §1). "
            "ADR-024 글자 기준 → ADR-025 token 기준 재정의."
        ),
    )
    rag_chunk_overlap: int = Field(
        default=50,
        description=(
            "Phase 7: chunk overlap in tokens (ADR-025 §1, 10% 표준). "
            "문맥 보존 + retrieval recall ↑."
        ),
    )
    rag_top_k: int = Field(
        default=5,
        description=(
            "Phase 7: retrieval top_k (ADR-025 §3). "
            "Phase 1 pgvector_top_k=3 와 별개 — Phase 7 RAG Lite 정식."
        ),
    )
    rag_threshold: float = Field(
        default=0.7,
        description=(
            "Phase 7: cosine similarity threshold (ADR-025 §3). "
            "표준 cutoff (0.65~0.75 범위)."
        ),
    )

    # ─── Phase 5 Slice 3 — Auth dev mode ────────────────────────────
    # Supabase 미설정 환경에서 /auth/login mock user (mock-user-1) 발급 허용.
    # 절대 production = False 강제 (배포 환경 환경변수로 override).
    # security-review §T1 정합: mock 토큰도 httpOnly cookie 로만 노출.
    dev_auth_mock: bool = Field(
        default=True,
        description=(
            "Phase 5 Slice 3: Supabase 미설정 시 mock user 허용 (dev only). "
            "production 환경에서는 환경변수 DEV_AUTH_MOCK=false 로 비활성화. "
            "security-review §T1: mock 토큰도 httpOnly cookie 로만 노출."
        ),
    )

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def openai_models_for_3plan_list(self) -> list[str]:
        """3 model names list (length exactly 3, padding/truncating to 3 if mismatch).

        Phase 4 Slice 2 (사용자 결정 4-b): comma-separated env var → list of 3.
        graceful: 부족 시 default 단일 모델로 padding, 초과 시 truncate.
        """
        parts = [m.strip() for m in self.openai_models_for_3plan.split(",") if m.strip()]
        if len(parts) == 3:
            return parts
        default = parts[0] if parts else "gpt-4o-mini"
        if len(parts) < 3:
            return parts + [default] * (3 - len(parts))
        return parts[:3]


@lru_cache
def get_settings() -> Settings:
    """싱글톤 settings."""
    return Settings()
