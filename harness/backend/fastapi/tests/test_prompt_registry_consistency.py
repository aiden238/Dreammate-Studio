"""Phase 8 Slice 4 — prompt_id/version 상수 ↔ registry 단일 출처 정합 + Critic adapter.

검증 대상 (ADR-029):
  - 각 agent 파일 PROMPT_ID/PROMPT_VERSION 모듈 상수 ↔ registry 매핑 dict 정합
    (registry = 단일 진실 출처 SoT, agent 상수는 미러).
  - Critic conservative adapter: normalize_to_canonical 이 0–5 scores → 0–1
    dimensions + overall_score 로 정규화하되 기존 0–5 deprecated 필드는 비파괴 보존
    (run_critic 출력 의미 불변 — helper additive, 미강제 주입 → 회귀 0).
  - prompt_registry.md 가 P-001~P-008 + AUX + P-EVAL-1 을 모두 문서화 (단일 출처).
"""
from __future__ import annotations

from pathlib import Path

from backend.fastapi.agents.critic import (
    PROMPT_ID as CRITIC_ID,
    PROMPT_VERSION as CRITIC_VER,
    normalize_to_canonical,
)
from backend.fastapi.agents.intent import (
    PROMPT_ID as INTENT_ID,
    PROMPT_VERSION as INTENT_VER,
)
from backend.fastapi.agents.planning import (
    PARALLEL_3_PROMPT_ID as PLAN_PARALLEL_ID,
    PARALLEL_3_PROMPT_VERSION as PLAN_PARALLEL_VER,
    PROMPT_ID as PLAN_ID,
    PROMPT_VERSION as PLAN_VER,
)
from backend.fastapi.agents.rewriter import (
    PROMPT_ID as REW_ID,
    PROMPT_VERSION as REW_VER,
)


# ─── 단일 출처 정합: registry SoT ↔ agent 상수 미러 (ADR-029 §3) ──────

# registry (단일 진실 출처)의 (id → version) 명시 매핑.
# registry.md 텍스트 파싱은 fragile → 명시적 dict 비교 (ADR-029 권장).
EXPECTED_REGISTRY: dict[str, str] = {
    "P-001": "v1.0.0",  # intent (Phase 1 임시 매핑)
    "P-006": "v1.0.0",  # planning
    "P-007": "v1.1.0",  # critic — Phase 8 ADR-029 adapter bump
    "P-008": "v1.1.0",  # rewriter — Phase 6 ADR-019
}


def test_critic_constants() -> None:
    """P-007 critic 상수 ↔ registry 정합 (v1.1.0 adapter bump)."""
    assert CRITIC_ID == "P-007"
    assert CRITIC_VER == "v1.1.0"  # Phase 8 ADR-029 adapter bump
    assert EXPECTED_REGISTRY[CRITIC_ID] == CRITIC_VER


def test_rewriter_constants() -> None:
    """P-008 rewriter 상수 ↔ registry 정합 (v1.1.0 — Phase 6 ADR-019)."""
    assert REW_ID == "P-008"
    assert REW_VER == "v1.1.0"  # Phase 6 ADR-019
    assert EXPECTED_REGISTRY[REW_ID] == REW_VER


def test_planning_constants() -> None:
    """P-006 planning 상수 ↔ registry 정합 (parallel-3 변형도 부모 version 상속)."""
    assert PLAN_ID == "P-006"
    assert PLAN_VER == "v1.0.0"
    # parallel-3 확장은 부모 P-006 version 상속 (별도 version 미부여 — ADR-029 §2).
    assert PLAN_PARALLEL_ID == "P-006"
    assert PLAN_PARALLEL_VER == PLAN_VER
    assert EXPECTED_REGISTRY[PLAN_ID] == PLAN_VER


def test_intent_constants() -> None:
    """P-001 intent 상수 ↔ registry 정합 (Phase 1 임시 매핑)."""
    assert INTENT_ID == "P-001"
    assert INTENT_VER == "v1.0.0"
    assert EXPECTED_REGISTRY[INTENT_ID] == INTENT_VER


def test_all_agent_constants_match_registry_map() -> None:
    """4 agent (id, version) 상수 ↔ EXPECTED_REGISTRY 매핑 dict 전체 정합 (drift 0)."""
    actual = {
        INTENT_ID: INTENT_VER,
        PLAN_ID: PLAN_VER,
        CRITIC_ID: CRITIC_VER,
        REW_ID: REW_VER,
    }
    for pid, ver in actual.items():
        assert pid in EXPECTED_REGISTRY, f"{pid} 가 registry 매핑에 없음"
        assert EXPECTED_REGISTRY[pid] == ver, f"{pid} version drift: {ver}"


# ─── Critic conservative adapter (ADR-029 §1) ─────────────────────────

def test_normalize_to_canonical_maps_0_5_to_0_1() -> None:
    """0–5 scores → 0–1 dimensions + overall_score (overall_score_avg/5.0)."""
    verdict = {
        "scores": {"intent_fit": 5, "hook_strength": 0, "structure": 2.5},
        "overall_score_avg": 2.5,
        "overall_verdict": "revise",
    }
    out = normalize_to_canonical(verdict)
    assert out["dimensions"]["intent_fit"] == 1.0
    assert out["dimensions"]["hook_strength"] == 0.0
    assert abs(out["dimensions"]["structure"] - 0.5) < 1e-9
    assert abs(out["overall_score"] - 0.5) < 1e-9
    # 비파괴: 원본 0–5 deprecated 필드 보존 (회귀 0).
    assert out["scores"]["intent_fit"] == 5
    assert out["overall_score_avg"] == 2.5
    assert out["overall_verdict"] == "revise"


def test_normalize_overall_score_from_scores_average_when_no_avg() -> None:
    """overall_score_avg 부재 시 scores 평균/5.0 으로 overall_score 산출."""
    verdict = {"scores": {"a": 5, "b": 5}}  # avg5 = 5.0 → 1.0
    out = normalize_to_canonical(verdict)
    assert out["overall_score"] == 1.0
    assert out["dimensions"] == {"a": 1.0, "b": 1.0}


def test_normalize_preserves_existing_canonical() -> None:
    """기존 canonical (overall_score) 가 있으면 우선 보존 (정규화로 덮어쓰지 않음)."""
    verdict = {"scores": {"a": 4}, "overall_score": 0.99}
    out = normalize_to_canonical(verdict)
    assert out["overall_score"] == 0.99  # 기존 canonical 우선
    # dimensions 는 기존에 없었으므로 정규화 결과 주입.
    assert out["dimensions"] == {"a": 0.8}


def test_normalize_graceful_no_scores() -> None:
    """scores 없으면 무변경 (비파괴 사본만 반환)."""
    out = normalize_to_canonical({"overall_verdict": "approve"})
    assert out == {"overall_verdict": "approve"}


def test_normalize_is_non_destructive_copy() -> None:
    """입력 dict 를 mutate 하지 않는다 (사본 반환)."""
    verdict = {"scores": {"a": 5}, "overall_score_avg": 5.0}
    out = normalize_to_canonical(verdict)
    assert "dimensions" not in verdict  # 원본 미변경
    assert "dimensions" in out


# ─── registry 단일 출처 문서화 (ADR-029 §2) ───────────────────────────

def _registry_path() -> Path:
    # tests → fastapi → backend → harness (parents[3]).
    return (
        Path(__file__).resolve().parents[3]
        / "ai_system"
        / "prompts"
        / "prompt_registry.md"
    )


def test_registry_documents_all_prompts() -> None:
    """prompt_registry.md 에 P-001~P-008 + AUX + P-EVAL-1 명시 (단일 출처)."""
    content = _registry_path().read_text(encoding="utf-8")
    for pid in [
        "P-001",
        "P-002",
        "P-003",
        "P-004",
        "P-005",
        "P-006",
        "P-007",
        "P-008",
        "P-AUX-1",
        "P-AUX-2",
        "P-EVAL-1",
    ]:
        assert pid in content, f"{pid} 가 registry.md 에 없음"
    # P-007/P-008 v1.1.0 명시 (Phase 8 ADR-029 / Phase 6 ADR-019).
    assert "v1.1.0" in content
