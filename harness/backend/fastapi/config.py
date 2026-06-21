"""Settings — env-driven configuration.

Loaded once at app startup via pydantic-settings.
.env 파일 미존재해도 동작 (test에서 fixture로 주입).
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field, model_validator
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

    # ─── Phase 27 S1 — 실사용 프로파일 (1차 MVP 실사용 마감, B-1) ──────────────
    # ★ 단일 스위치: APP_PROFILE=realuse 면 "처음 온 사용자가 도움 없이 director 기획안
    #   1개 생성 → 저장 → brain 축적 → 다음 반영" 핵심 루프 flag 묶음을 한 번에 ON.
    # ★ behavior-preserving / byte-identical 보장:
    #   - default = "default" → 아래 _apply_realuse_profile 검증기가 즉시 no-op return.
    #     즉 app_profile 미설정(기존 모든 경로 + 모든 기존 테스트)은 flag 변경 0 = pre-Phase-27 동일.
    #   - realuse 활성은 명시적으로 APP_PROFILE=realuse 를 env/`.env` 에 줄 때만 (.env.realuse.example 참조).
    #   - 개별 flag 를 env 로 명시(예: OUTPUT_MODE=commercial_viral)하면 model_fields_set 에 잡혀
    #     프로파일이 그 값을 덮어쓰지 않는다 (명시 env override 가 프로파일보다 우선).
    # ★ 코드 default flag(plans_repo_enabled=False 등)는 변경하지 않는다 — 프로파일은 런타임 env 로만 ON.
    app_profile: Literal["default", "realuse"] = Field(
        default="default",
        description=(
            "Phase 27 실사용 프로파일 스위치 (환경변수 APP_PROFILE). "
            "'default'(기본) = 기존 동작 byte-identical (검증기 no-op). "
            "'realuse' = 1차 MVP 실사용 핵심 루프 flag 묶음 ON (output_mode=director + "
            "rich + plans_repo + brand/personal PKM 주입·추출 + 브랜딩 시드). "
            "개별 env 명시는 프로파일보다 우선(override). 코드 default 는 불변 — env 로만 활성."
        ),
    )

    # ─── Phase 27 S3 — 최소 rate limit 게이트 (B-7, additive, default False) ──
    # ★ gated default-off: False 면 enforce_rate_limit 의존성이 즉시 no-op (기존 응답 byte-identical).
    #   True 면 핵심 비용 endpoint(generation)를 신원(user-우선/IP) 기준 fixed-window 로 제한(429).
    # ★ 실사용 프로파일(APP_PROFILE=realuse)과 별개 관심사 — 단일 로컬 사용자 테스트를 막지 않도록
    #   realuse 묶음에 포함하지 않는다. 배포(Gate B+) 시 RATE_LIMIT_ENABLED=true 로 별도 활성.
    rate_limit_enabled: bool = Field(
        default=False,
        description=(
            "Phase 27 S3 최소 rate limit on/off (환경변수 RATE_LIMIT_ENABLED). "
            "False(기본)=비용 endpoint 제한 0(byte-identical). True=generation endpoint "
            "신원별 fixed-window 제한(rate_limit_policy.md §3.2 free: 2/분·5/일). "
            "in-memory 단일 프로세스(U-2) — 분산은 운영 단계 후속."
        ),
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

    # ─── HIP-006 (2026-06-05) — agent_io 텔레메트리 발신기 (additive, gated default-off, graceful) ─
    # 배경: self_improvement_loop §1.2 패턴 마이닝 + cost-review 데이터원이 부재(meta/audits/2026-06-05.md §3).
    # ★ behavior-preserving: default False → 기존 hermetic pytest 파일쓰기 0 (byte-identical).
    #   ON 시 gateway.complete 가 LLM 호출 1건당 JSONL 1행 기록 (db_schema §7.1 agent_io_logs 정합, graceful).
    #   환경변수 AGENT_IO_LOG_ENABLED / AGENT_IO_LOG_PATH.
    agent_io_log_enabled: bool = Field(
        default=False,
        description=(
            "HIP-006 agent_io 텔레메트리 발신기 on/off. ★ gated default-off — False 면 "
            "LLM 호출 로깅 0 (behavior-preserving). True 면 cost-review/patterns 데이터원 활성."
        ),
    )
    agent_io_log_path: str = Field(
        default="logs/telemetry/agent_io.jsonl",
        description=(
            "HIP-006 텔레메트리 JSONL append 경로 (gitignore). 부모 디렉토리 자동 생성. "
            "환경변수 AGENT_IO_LOG_PATH 로 override."
        ),
    )

    # ─── HIP-007 S1 (2026-06-05) — critic 낙관편향 보정 (additive, gated default-off) ─
    # 배경: critic 전수 approve(낙관 편향, "88점 함정") — 얕은 plan 도 평균이 높아 통과
    #   (meta/audits/2026-06-05.md HIP-007). ★ behavior-preserving: default False → 프롬프트/게이트
    #   미적용 = critic 출력 byte-identical. ON 시 (1) anti-optimism 프롬프트 (2) 핵심 차원 게이트.
    # ★ 결착 (2026-06-21, HIP-B): RETAIN — 단독은 verdict 0건 변경(점수만 0.35 보정)이라 88점 함정
    #   fix 가 아님. 진짜 fix = critic_judge_provider='anthropic'(Phase 31). 본 flag 는 그 judge 의
    #   **보완**(judge=anthropic 와 짝으로 co-activate 시 Claude 채점을 더 엄격하게) → sunset 아님.
    critic_calibration_enabled: bool = Field(
        default=False,
        description=(
            "HIP-007 critic 낙관편향 보정 on/off. ★ gated default-off — False 면 critic "
            "프롬프트·verdict 불변(byte-identical). True 면 엄격 채점 프리앰블 + 핵심 차원 approve 게이트."
        ),
    )
    critic_calibration_min_score: int = Field(
        default=3,
        description=(
            "HIP-007 보정 ON 시 핵심 차원(모드별 CALIBRATION_KEY_DIMS) 최소 점수(0~5). "
            "이 미만이면 평균이 approve 라도 revise 로 강등(88점 함정 차단)."
        ),
    )

    # ─── Phase 31 (2026-06-21) — cross-provider judge (additive, gated default-openai) ─
    # 배경: HIP-007 calibration(프롬프트+게이트) 단독으론 verdict 를 0건도 못 뒤집음
    #   (human blind N=10 에서 false-approve 10/10 잔존 — eval/regression_results/2026-06-15).
    #   같은 plan 을 다른 provider(Claude)가 독립 채점하니 self-review 낙관편향이 깨져
    #   false-approve 10/10→0/10, 사람괴리 2.27→0.53 (2026-06-21 cross-provider 측정).
    # ★ behavior-preserving: default "openai" → 기존 OpenAI(gpt-4o) critic 경로 byte-identical.
    #   "anthropic" 시 critic 채점만 Claude(registry 'claude-sonnet')로 교체 — plan 생성·출력
    #   스키마·verdict 규칙은 불변(채점 모델만 교차). ANTHROPIC_API_KEY 없으면 ValueError(안전 차단).
    # ★ DEFAULT 를 anthropic 으로 전환하는 것은 모델 교체(major) → prompt-version-review 절차
    #   대상. 본 flag 는 opt-in 측정/운영 레버이며 realuse 프로파일에 포함하지 않는다.
    critic_judge_provider: str = Field(
        default="openai",
        description=(
            "Phase 31 cross-provider judge: critic 채점 provider 선택 "
            "('openai'=기본 gpt-4o critic, byte-identical / 'anthropic'=Claude 독립 judge로 "
            "self-review 낙관편향 차단). 환경변수 CRITIC_JUDGE_PROVIDER."
        ),
    )

    # ─── HIP-008 S3 (2026-06-05) — plan envelope 영속 (additive, gated default-off, graceful) ─
    # 배경: 생성 plan 이 _plan_store(in-memory)만 → 서버 재시작 시 휘발(meta/audits/2026-06-05.md §B).
    #   ★ behavior-preserving: default False → PlansRepo 미호출 = in-memory only = byte-identical.
    #   ON 시 orchestrator 가 envelope 를 PlansRepo upsert(graceful, Supabase 실패→in-memory fallback).
    plans_repo_enabled: bool = Field(
        default=False,
        description=(
            "HIP-008 plan envelope 영속(PlansRepo Supabase write) on/off. ★ gated default-off — "
            "False 면 _plan_store(in-memory)만(재시작 시 휘발). True 활성은 Supabase 설정 후. "
            "환경변수 PLANS_REPO_ENABLED."
        ),
    )

    # ─── HIP-006 S3 (2026-06-05) — agent_io 텔레메트리 DB 적재 승격 (additive, gated default-off) ─
    # JSONL(agent_io_log_enabled)과 별개 sub-flag. ON + Supabase 시 agent_io_logs 테이블에도 적재.
    # ★ JSONL 은 인프라 0(로컬 파일) — 본 flag 는 Supabase DB 적재 옵션(서버 배포 아님, Supabase 만 필요).
    agent_io_log_to_db: bool = Field(
        default=False,
        description=(
            "HIP-006 텔레메트리 Supabase agent_io_logs 적재 on/off. ★ gated default-off — "
            "False 면 JSONL 만(인프라 0). True + Supabase 설정 시 DB 적재(graceful). 환경변수 AGENT_IO_LOG_TO_DB."
        ),
    )

    # ─── Phase 11 A안 Slice 2 — cross-validation 게이트 + Gemini 튜닝 (additive) ─
    # ★ DEPRECATED (2026-06-21, HIP-B 결착): SUNSET. orchestrator 에 logging-only(Envelope 0 변경)로
    #   묻혀 의사결정 미반영. "다른 provider 로 교차검증" 의도는 Phase 31 cross-provider judge
    #   (critic_judge_provider='anthropic')가 실제 verdict 차단으로 정식 구현 → 중복. 코드 제거는
    #   후속(behavior-preserving 이라 비긴급). 신규 사용 금지 — judge 레버를 쓸 것.
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
    # ★ 결착 (2026-06-21, HIP-B): DEFER. A11 다양성 real(0.959→0.680)이나 취약(provider 503/JSON
    #   robustness). 활성 = orchestrator 분기(S2b-2b) + Claude JSON robustness + provider fallback
    #   선결 → 측정으로 product 필요 입증 시 진행. (Phase 31 _judge_via_anthropic 가 일부 de-risk.)
    # ★ behavior-preserving / gated default-off: True 여도 본 Slice 는 신규 함수
    #   run_planning_multi_provider_3 를 추가만 — 아무 곳도 호출 X (orchestrator 분기는
    #   후속 S2b-2b). False 일 때 기존 OpenAI 3-call(run_planning_parallel_3) 경로 유지.
    multi_provider_plans_enabled: bool = Field(
        default=False,
        description="B안: 3-plan 을 3-provider(GPT/Claude/Gemini) alias 로 다양화 (gated, default OFF).",
    )

    # ─── Phase 17 가-S2 — brand_memory 구속 주입 게이트 (additive, default False) ─
    # ★ behavior-preserving / gated default-off: OFF 면 orchestrator 가 brand_memory 를
    #   로드/주입하지 않아 planning user_input 이 byte-identical (가-S1 이전과 동일).
    #   ON + 신원(auth_user_id) + brand_memory 有 일 때만 build_brand_constraint_preamble 가
    #   user_input 앞에 prepend 된다(Phase 16 검증 메커니즘). 신원 없음/메모리 없음 →
    #   주입 0(byte-identical). 기존 561 테스트는 OFF default 라 불변.
    brand_memory_injection_enabled: bool = Field(
        default=False,
        description=(
            "Phase 17 가-S2: brand_memory_entries 구속 프리앰블을 planning user_input 에 "
            "주입할지 여부. ★ gated default-off — False 면 brand_memory 로드/주입 0 "
            "(익명/무메모리 경로 byte-identical). True 활성은 신원+brand_memory 有 일 때만 주입. "
            "환경변수 BRAND_MEMORY_INJECTION_ENABLED 로 override."
        ),
    )

    # ─── Phase 17 다-S5 — brand_memory 추출 루프 배선 게이트 (additive, default False) ─
    # ★ 추출(extract)과 주입(injection)은 별개 관심사 — 별도 flag 로 분리:
    #   · injection_enabled = 읽기(load → planning user_input prepend, 가-S2)
    #   · extract_enabled    = 쓰기(feedback/selection 신호 → brand_memory_entries 적재, 다-S5)
    # ★ behavior-preserving / gated default-off: OFF(default) OR 익명 → feedback/selection
    #   endpoint 가 brand_memory_extractor 를 호출하지 않아 brand_memory_entries 쓰기 0
    #   (응답 byte-identical, 기존 582 테스트 OFF default 라 불변). ON + 신원(auth_user_id) 일
    #   때만 feedback 저장 후 run_brand_memory_extractor(persist=True) best-effort 호출.
    # ★ governance (ADR-031 §P-AUX-2 / agent_io §7.5): persist=True 여도 자동 INSERT 는
    #   confidence ≥ 0.9 (명시 선호) 후보만 — 나머지(0.3/0.7)는 proposal (쓰기 0, pending UX).
    #   blanket 자동 승격 0 (persist_min_confidence 기본 0.9 유지 — NG12 계승).
    brand_memory_extract_enabled: bool = Field(
        default=False,
        description=(
            "Phase 17 다-S5: feedback/selection 신호로부터 brand_memory_entries 를 추출·적재할지 "
            "여부 (extraction). ★ gated default-off — False 면 추출/쓰기 0 (익명·OFF 경로 "
            "byte-identical). True + 신원(auth_user_id) 일 때만 feedback 저장 후 "
            "run_brand_memory_extractor(persist=True) 호출. 자동 INSERT 는 confidence ≥ 0.9 "
            "명시 선호만 (agent_io §7.5 / ADR-031 — 나머지는 제안). injection_enabled(가-S2 읽기)와 "
            "별개 관심사. 환경변수 BRAND_MEMORY_EXTRACT_ENABLED 로 override."
        ),
    )

    # ─── Phase 17 다-S3 — 개인 PKM 구속 주입 게이트 (additive, default False) ─
    # ★ behavior-preserving / gated default-off: OFF 면 orchestrator 가 personal PKM 을
    #   로드/주입하지 않아 planning user_input 이 brand-only 경로와 byte-identical.
    #   ON + 신원(auth_user_id) + personal PKM 有 일 때만 build_brand_constraint_preamble 가
    #   personal 프리앰블을 만들고, brand 프리앰블보다 **앞에** prepend 된다 (설계 §6.2
    #   user_locked/personal > brand). 신원 없음(익명)/엔트리 없음 → 주입 0(byte-identical).
    #   brand_memory_injection_enabled(가-S2)와 별개 관심사 — personal 은 그 위에 얹는 추가 레이어.
    personal_pkm_injection_enabled: bool = Field(
        default=False,
        description=(
            "Phase 17 다-S3: 개인 PKM(pkm_entries, scope=personal) 구속 프리앰블을 planning "
            "user_input 에 주입할지 여부. ★ gated default-off — False 면 personal PKM 로드/주입 0 "
            "(익명/무엔트리/brand-only 경로 byte-identical). True 활성은 신원(auth_user_id)+personal "
            "PKM 有 일 때만 주입하며, brand 프리앰블보다 앞에 prepend (personal > brand, 설계 §6.2). "
            "brand_memory_injection_enabled(가-S2)와 별개 관심사. "
            "환경변수 PERSONAL_PKM_INJECTION_ENABLED 로 override."
        ),
    )

    # ─── Phase 17 다-S6 — 개인 PKM 추출 루프 배선 게이트 (additive, default False) ─
    # ★ 추출(extract)과 주입(injection)은 별개 관심사 — 별도 flag 로 분리 (다-S5 brand 와 대칭):
    #   · personal_pkm_injection_enabled = 읽기(load → planning user_input prepend, 다-S3, brand 보다 앞)
    #   · personal_pkm_extract_enabled    = 쓰기(feedback 신호 → pkm_entries(scope=personal) 적재, 다-S6)
    # ★ behavior-preserving / gated default-off: OFF(default) OR 익명 → feedback endpoint 가
    #   개인 PKM 추출기를 호출하지 않아 pkm_entries 쓰기 0 (응답 byte-identical, 기존 600 테스트
    #   OFF default 라 불변). ON + 신원(auth_user_id) 일 때만 feedback 저장 후
    #   extract_brand_memory_candidates(...) 호출 → 고신뢰 후보를 PkmRepo.add_entry 로 적재.
    # ★ ★ personal scope 는 brand-독립(User 계층) — brand 해결 불필요, auth_user_id 만으로 적재한다.
    # ★ governance (ADR-031 §P-AUX-2 / agent_io §7.5): 자동 INSERT 는 confidence ≥ 0.9 (명시 선호)
    #   후보만 — 나머지(0.3/0.7)는 proposal (쓰기 0, pending UX). blanket 자동 승격 0 (NG12 계승).
    personal_pkm_extract_enabled: bool = Field(
        default=False,
        description=(
            "Phase 17 다-S6: feedback 신호로부터 개인 PKM(pkm_entries, scope=personal) 을 추출·적재할지 "
            "여부 (extraction, brand-독립 User 계층). ★ gated default-off — False 면 추출/쓰기 0 "
            "(익명·OFF 경로 byte-identical). True + 신원(auth_user_id) 일 때만 feedback 저장 후 "
            "extract_brand_memory_candidates 호출 → confidence ≥ 0.9 명시 선호 후보만 PkmRepo.add_entry "
            "(agent_io §7.5 / ADR-031 — 나머지는 제안). personal_pkm_injection_enabled(다-S3 읽기) 및 "
            "brand_memory_extract_enabled(다-S5 brand 쓰기)와 별개 관심사. "
            "환경변수 PERSONAL_PKM_EXTRACT_ENABLED 로 override."
        ),
    )

    # ─── Phase 18 Slice S4 — 브랜딩 후보 택1 → brand_memory 시드 게이트 (additive, default False) ─
    # ★ 발굴(P18 branding) → 축적(brand_memory) → 주입(P17 가-S2) 루프의 "축적" 단계 배선.
    #   사용자가 브랜딩 후보(주제/톤/타깃/포맷)를 **택1** 하면, 그 브랜딩 방향을 인증 사용자의
    #   기본 brand_memory_entries 로 시드한다 (다음 generate 부터 P17 주입 루프가 읽음).
    # ★ behavior-preserving / gated default-off: OFF(default) OR 익명 → /branding/select 가
    #   brand_memory 를 쓰지 않고 BrandRepo 도 호출하지 않는다 (no surprise write). 그래도
    #   selected/initial_input 은 항상 저장 → 후속 generate 가 택1 주제를 그대로 받는다
    #   (시드 유무와 무관하게 byte-identical). ON + 신원(auth_user_id) 일 때만 시드.
    # ★ governance (ADR-031 §P-AUX-2 / agent_io §7.5): 명시 택1 = 사용자 선택 = 고신뢰
    #   → confidence 0.9 로 적재 (P17 ≥0.9 auto-persist 선례 계승). blanket 자동 승격 0.
    #   extract_enabled(다-S5 feedback 추출)와 별개 관심사 — 이쪽은 명시 택1 신호.
    branding_pkm_seed_enabled: bool = Field(
        default=False,
        description=(
            "Phase 18 S4: 브랜딩 후보 택1(/branding/select) 시 그 브랜딩 방향(tone/target/format)을 "
            "인증 사용자의 brand_memory_entries 로 시드할지 여부. ★ gated default-off — False 면 "
            "brand_memory 쓰기 0, BrandRepo 미호출 (익명·OFF 경로 byte-identical, selected/initial_input "
            "은 항상 저장). True + 신원(auth_user_id) 일 때만 confidence 0.9 (명시 택1=고신뢰)로 시드 "
            "(발굴→축적→주입 루프의 축적 단계). 환경변수 BRANDING_PKM_SEED_ENABLED 로 override."
        ),
    )

    # ─── Phase 13 Slice S3 — rich 출력 게이트 (additive, default False) ─
    # ★ behavior-preserving / gated default-off: OFF=compact byte-identical
    #   (Plan.model_dump_compact() 가 rich 슬롯 제외 → Phase 13 이전 응답과 동일),
    #   ON=rich(확장 스키마+RICH_SYSTEM_PROMPT). 기존 486 테스트는 OFF default 라 불변.
    rich_output_enabled: bool = Field(
        default=False,
        description=(
            "Phase 13: rich 출력(확장 스키마+프롬프트) 활성. "
            "OFF=compact byte-identical, ON=rich. 환경변수 RICH_OUTPUT_ENABLED. "
            "★ Phase 15: output_mode(enum)와 공존 — effective_output_mode() 참조(backward-compat)."
        ),
    )

    # ─── Phase 15 S1 — output_mode enum (additive, default compact) ───────
    # ★ rich_output_enabled(boolean, Phase 13)를 일반화. director tier 추가.
    #   default compact → compact/rich 경로 byte-identical. director 는 명시 활성에서만.
    #   backward-compat: output_mode 미지정(compact) + rich_output_enabled=True → effective "rich"
    #   (effective_output_mode()). 기존 508 테스트는 default compact + 매핑으로 불변.
    # ── Phase 20 S1: 4번째 tier commercial_viral 추가 (additive, schema-only) ──
    #   compact<rich<director<commercial_viral. commercial_viral = director 슬롯 +
    #   Plan 상업 7슬롯(COMMERCIAL_FIELDS) + scene 상업 2필드. default compact 불변 → 회귀 0.
    output_mode: Literal["compact", "rich", "director", "commercial_viral"] = Field(
        default="compact",
        description=(
            "Phase 20: 출력 tier 4단계 (compact<rich<director<commercial_viral). default compact. "
            "환경변수 OUTPUT_MODE. rich_output_enabled(레거시)와 공존 — effective_output_mode() 가 종합."
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
    # ─── Phase 27 A9 — RAG 임베딩 provider (gated, default openai = byte-identical) ───
    rag_embedding_provider: Literal["openai", "gemini"] = Field(
        default="openai",
        description=(
            "RAG 임베딩 provider. default 'openai'(text-embedding-3-small)=기존 동작. "
            "'gemini'(gemini-embedding-2 @1536, taskType 비대칭)=A9 측정상 ko 압도(0.7 통과). "
            "★ 임베딩만 Gemini, 생성은 GPT 계열(분리). 환경변수 RAG_EMBEDDING_PROVIDER."
        ),
    )
    rag_embedding_gemini_model: str = Field(
        default="gemini-embedding-2",
        description="Gemini 임베딩 모델(provider=gemini 시). outputDimensionality=rag_embedding_dim(1536).",
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

    # ─── Phase 28 S3 — 나만의 컨셉 수렴 (concept surfacing) 게이트 ─────────
    # 누적된 개인 PKM(신호 더미)을 1회 LLM 합성으로 (a)모순 해소 (b)중요도 분화 (c)컨셉 한 줄
    # 로 표면화한다 (GET /me/concept, read-time, 영속 0 — NG12 계승). ★ gated default-off:
    # False(default) OR 익명 → 합성 미호출 = byte-identical. realuse 프로파일에서 ON.
    concept_surfacing_enabled: bool = Field(
        default=False,
        description=(
            "Phase 28 S3: 개인 PKM 종합 → '내 컨셉' 한 줄 + 핵심 기둥 + 모순쌍 표면화 "
            "(GET /me/concept, read-time LLM 합성, 영속 X). gated default-off — False/익명 시 "
            "합성/호출 0(byte-identical). 환경변수 CONCEPT_SURFACING_ENABLED 로 override."
        ),
    )

    # ─── Phase 27 S1 — 실사용 프로파일 적용 (B-1) ────────────────────────────
    @model_validator(mode="after")
    def _apply_realuse_profile(self) -> "Settings":
        """APP_PROFILE=realuse 면 1차 MVP 실사용 핵심 루프 flag 묶음을 ON.

        ★ app_profile != "realuse" (default) → 즉시 no-op return = 기존 동작 byte-identical.
          (이 검증기 추가로 인한 동작 변화는 realuse 명시 활성 시에만 발생.)
        ★ 명시 env override 존중: 개별 flag/output_mode 를 env 로 직접 준 경우
          (model_fields_set 에 포함) 프로파일이 덮어쓰지 않는다.
        ★ 코드 default 는 불변 — 본 메서드는 런타임 인스턴스 값만 조정(프로파일 활성 시).
        """
        if self.app_profile != "realuse":
            return self
        # core-loop flag 묶음. 개별 env 명시 설정은 model_fields_set 에 잡혀 제외(override 존중).
        realuse_flags = (
            "rich_output_enabled",
            "plans_repo_enabled",
            "brand_memory_injection_enabled",
            "brand_memory_extract_enabled",
            "personal_pkm_injection_enabled",
            "personal_pkm_extract_enabled",
            "branding_pkm_seed_enabled",
            "concept_surfacing_enabled",
            # Phase 27 A8 (측정 접지선): 실사용 시 agent_io 텔레메트리 기록 ON →
            #   cost_report.py(소비)가 실제 데이터를 집계. 코드 default 는 여전히 False
            #   (default 프로파일 byte-identical 유지) — realuse env 에서만 활성.
            "agent_io_log_enabled",
        )
        explicit = self.model_fields_set
        # output tier: 사용자 결정 director (명시 OUTPUT_MODE 가 있으면 존중).
        if "output_mode" not in explicit:
            self.output_mode = "director"
        for name in realuse_flags:
            if name not in explicit:
                setattr(self, name, True)
        return self

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


def effective_output_mode(settings: "Settings") -> str:
    """Phase 15/20: 유효 output_mode 종합 (compact/rich/director/commercial_viral).

    backward-compat: `output_mode` 가 명시(rich/director/commercial_viral)면 그것을 따른다.
    compact(default)이고 레거시 `rich_output_enabled=True` 면 "rich" 로 승격 → Phase 13/14 의
    rich_output_enabled ON 동작을 100% 보존. 둘 다 미활성이면 "compact".

    ★ Phase 20: output_mode="commercial_viral" 이면 != compact 분기로 그대로 반환된다 (로직 불변).
    ★ 단일 종합 지점 — S3 wiring(generate/orchestrator/planning/critic)이 이 함수로 모드를 결정.
    """
    if settings.output_mode != "compact":
        return settings.output_mode  # "rich" | "director" | "commercial_viral" (명시 우선)
    return "rich" if settings.rich_output_enabled else "compact"
