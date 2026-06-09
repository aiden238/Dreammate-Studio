"""Phase 27 S1 — 실사용 프로파일 (APP_PROFILE=realuse) 검증.

핵심 보장:
  1. default (APP_PROFILE 미설정) → 모든 core-loop flag OFF + output_mode=compact
     = pre-Phase-27 byte-identical (기존 802 테스트가 이 경로).
  2. realuse → 1차 MVP 실사용 핵심 루프 flag 묶음 ON (output_mode=director 등).
  3. 개별 env/kwarg 명시는 프로파일보다 우선 (override 존중).
  4. 환경변수 APP_PROFILE 경로(실제 실사용 활성 방식)로도 동작.
"""

from backend.fastapi.config import Settings, effective_output_mode

# 실사용 프로파일이 ON 으로 켜는 9개 core-loop flag
# (Phase 28 S3 concept_surfacing + Phase 27 A8 agent_io_log 측정 접지선 포함).
_REALUSE_FLAGS = (
    "rich_output_enabled",
    "plans_repo_enabled",
    "brand_memory_injection_enabled",
    "brand_memory_extract_enabled",
    "personal_pkm_injection_enabled",
    "personal_pkm_extract_enabled",
    "branding_pkm_seed_enabled",
    "concept_surfacing_enabled",  # Phase 28 S3 — 컨셉 수렴(GET /me/concept)
    "agent_io_log_enabled",  # A8 — 실사용 시 텔레메트리 기록(cost_report 소비)
)


def test_default_profile_is_byte_identical():
    """default 프로파일 = 기존 동작 (검증기 no-op)."""
    s = Settings(_env_file=None)
    assert s.app_profile == "default"
    assert s.output_mode == "compact"
    assert effective_output_mode(s) == "compact"
    for name in _REALUSE_FLAGS:
        assert getattr(s, name) is False, f"{name} 는 default 에서 OFF 여야 한다"


def test_realuse_profile_enables_core_loop():
    """realuse → director + 7 flag 전부 ON."""
    s = Settings(_env_file=None, app_profile="realuse")
    assert s.output_mode == "director"
    assert effective_output_mode(s) == "director"
    for name in _REALUSE_FLAGS:
        assert getattr(s, name) is True, f"{name} 는 realuse 에서 ON 이어야 한다"


def test_realuse_respects_explicit_output_mode_override():
    """realuse + 명시 OUTPUT_MODE 면 프로파일이 덮어쓰지 않는다."""
    s = Settings(_env_file=None, app_profile="realuse", output_mode="commercial_viral")
    assert s.output_mode == "commercial_viral"
    assert effective_output_mode(s) == "commercial_viral"
    # 나머지 flag 는 여전히 프로파일이 ON.
    assert s.plans_repo_enabled is True


def test_realuse_respects_explicit_flag_override():
    """realuse + 개별 flag 명시 False 면 그 flag 만 OFF 유지(override), 나머지는 ON."""
    s = Settings(_env_file=None, app_profile="realuse", plans_repo_enabled=False)
    assert s.plans_repo_enabled is False  # 명시 override 존중
    assert s.brand_memory_injection_enabled is True
    assert s.personal_pkm_extract_enabled is True


def test_realuse_via_env_var(monkeypatch):
    """실제 실사용 활성 방식 — 환경변수 APP_PROFILE=realuse (case-insensitive)."""
    monkeypatch.setenv("APP_PROFILE", "realuse")
    s = Settings(_env_file=None)
    assert s.app_profile == "realuse"
    assert effective_output_mode(s) == "director"
    assert s.plans_repo_enabled is True


def test_invalid_profile_value_rejected():
    """알 수 없는 프로파일 값은 Literal 검증으로 거부 (오타 방어)."""
    import pytest
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        Settings(_env_file=None, app_profile="prod")  # noqa: 정의 안 된 값
