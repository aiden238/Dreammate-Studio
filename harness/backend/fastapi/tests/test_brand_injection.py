"""Phase 17 가-S2 — brand_memory 구속 주입 (preamble 빌더 + gated orchestrator) 테스트.

검증 축:
  - build_brand_constraint_preamble: entry_type 5종 → 구속 directive 매핑, 빈/무효 → "".
  - gated 주입: flag ON + seed brand_memory(fake repo) + auth_user_id →
    planning user_input 에 구속 프리앰블이 prepend 되고 정상 Envelope.
  - byte-identical: flag OFF(default) / 익명 / brand 없음 / 메모리 0개 → user_input 무변경.

★ DI seam: brand_memory_repo / brands_resolver 인자로 실 Supabase 없이 brand_memory seed.
  planning user_input 캡처는 run_planning_parallel_3 mock 이 받은 첫 인자(user_input) 로 확인.
"""

from __future__ import annotations

import copy
from typing import Any

import pytest

from backend.fastapi.agents.brand_injection import (
    BRAND_CONSTRAINT_PREAMBLE_HEADER,
    build_brand_constraint_preamble,
)
from backend.fastapi.config import get_settings
from backend.fastapi.db.types import PersistenceResult
from backend.fastapi.orchestration import generate_plan
from backend.fastapi.rag.types import RetrievalResult
from backend.fastapi.schemas.output import Envelope
from backend.fastapi.schemas.plans import GenerateRequest


# ─── 1. preamble 빌더 — entry_type 매핑 ────────────────────────────────


def test_preamble_maps_all_entry_types() -> None:
    """5종 entry_type → 구속 directive 라벨 매핑 + 헤더 + 입력 순서 보존."""
    entries = [
        {"entry_type": "preferred_tone", "content": "친근하고 담백한 톤"},
        {"entry_type": "avoid_phrase", "content": "'최저가' 같은 가격 경쟁 표현"},
        {"entry_type": "preferred_phrase", "content": "'함께 만들어가요'"},
        {"entry_type": "success_pattern", "content": "첫 3초 질문형 후크"},
        {"entry_type": "rejection_pattern", "content": "과장된 클릭베이트"},
    ]
    out = build_brand_constraint_preamble(entries)

    assert out.startswith(BRAND_CONSTRAINT_PREAMBLE_HEADER)
    assert "- 톤: 친근하고 담백한 톤" in out
    assert "- 금지: '최저가' 같은 가격 경쟁 표현" in out
    assert "- 선호 표현: '함께 만들어가요'" in out
    assert "- 성공 패턴(반영): 첫 3초 질문형 후크" in out
    assert "- 회피 패턴: 과장된 클릭베이트" in out
    # 입력 순서 보존 (결정적) — 톤이 금지보다 먼저.
    assert out.index("톤:") < out.index("금지:")


def test_preamble_empty_inputs_return_empty() -> None:
    """빈 리스트 / None / content 없는 행 / 알 수 없는 entry_type → "" (graceful)."""
    assert build_brand_constraint_preamble([]) == ""
    assert build_brand_constraint_preamble(None) == ""  # type: ignore[arg-type]
    # content 비어있거나 entry_type 미지원 → directive 0개 → "".
    assert build_brand_constraint_preamble([{"entry_type": "preferred_tone", "content": ""}]) == ""
    assert build_brand_constraint_preamble([{"entry_type": "unknown_type", "content": "x"}]) == ""
    assert build_brand_constraint_preamble([{"content": "톤 누락"}]) == ""


def test_preamble_deterministic() -> None:
    """동일 entries → 동일 출력 (random/now 미사용)."""
    entries = [{"entry_type": "preferred_tone", "content": "톤A"}]
    assert build_brand_constraint_preamble(entries) == build_brand_constraint_preamble(
        copy.deepcopy(entries)
    )


# ─── orchestrator gated 주입 helpers ──────────────────────────────────


_INTENT_OK: dict[str, Any] = {"intent_ok": True, "category": "video_planning"}


def _make_plan_entry() -> dict[str, Any]:
    return {
        "plan_id": "test-plan-id",
        "status": "created",
        "created_at": "2026-06-04T00:00:00Z",
        "updated_at": "2026-06-04T00:00:00Z",
        "locale": "ko-KR",
        "initial_input": "유튜브 쇼츠 만들기",
        "wizard_data": {},
        "envelope": None,
    }


def _parallel_3_payload() -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    labels = ["narrative", "informational", "experiment"]
    for i in range(3):
        out.append(
            {
                "plan": {
                    "name": f"기획안 {i + 1}",
                    "concept": f"콘셉트 {i + 1}",
                    "hook": f"후크 {i + 1} — 시청 유지율 검증",
                    "flow": [
                        {"beat_index": 0, "beat": "도입", "duration_sec": 3, "purpose": "관심"},
                        {"beat_index": 1, "beat": "전개", "duration_sec": 20, "purpose": "핵심"},
                        {"beat_index": 2, "beat": "마무리", "duration_sec": 7, "purpose": "CTA"},
                    ],
                    "pros": "장점",
                    "risks": "위험",
                    "approach_label": labels[i],
                }
            }
        )
    return out


def _critic_approve(plan: dict[str, Any], *args: Any, **kwargs: Any) -> dict[str, Any]:
    scores = {
        "intent_fit": 4, "target_clarity": 4, "hook_strength": 4, "message_clarity": 4,
        "structure": 4, "feasibility": 4, "brand_consistency": 5, "differentiation": 4,
    }
    return {
        "target_plan_id": str(plan.get("plan_id") or ""),
        "scores": scores,
        "reasons": {k: "—" for k in scores},
        "suggestions": {k: "—" for k in scores},
        "overall_score_avg": round(sum(scores.values()) / len(scores), 4),
        "overall_verdict": "approve",
        "blocking_issues": [],
        "revise_round": 0,
    }


def _db_save_ok(**kwargs: Any) -> PersistenceResult:
    return PersistenceResult(
        status="saved", project_id="fake-project-uuid",
        plan_candidate_ids=["fake-pc-uuid"], error_reason=None,
    )


def _rag_fallback(*args: Any, **kwargs: Any) -> RetrievalResult:
    return RetrievalResult(references=[], used_fallback=True, fallback_reason="pgvector_unreachable")


class _CapturingPlanning:
    """run_planning_parallel_3 mock — 받은 user_input(첫 위치인자)을 캡처."""

    def __init__(self) -> None:
        self.captured_user_input: str | None = None

    async def __call__(self, user_input: str, *args: Any, **kwargs: Any) -> list[dict[str, Any]]:
        self.captured_user_input = user_input
        return copy.deepcopy(_parallel_3_payload())


class _FakeBrandMemoryRepo:
    """BrandMemoryRepo-호환 fake — seed 한 rows 를 brand 무관하게 반환 (DI seam)."""

    def __init__(self, rows: list[dict[str, Any]]) -> None:
        self.rows = rows
        self.calls: list[str] = []

    async def list_for_brand(self, brand_id: str) -> list[dict[str, Any]]:
        self.calls.append(brand_id)
        return list(self.rows)


def _patch_pipeline(monkeypatch: pytest.MonkeyPatch, planning: Any) -> None:
    monkeypatch.setattr("backend.fastapi.routers.plans.run_intent", lambda *a, **k: dict(_INTENT_OK))
    monkeypatch.setattr("backend.fastapi.routers.plans.run_rag_retrieval", _rag_fallback)
    monkeypatch.setattr("backend.fastapi.routers.plans.run_planning_parallel_3", planning)
    monkeypatch.setattr("backend.fastapi.routers.plans.run_critic", _critic_approve)
    monkeypatch.setattr("backend.fastapi.routers.plans.save_video_planning", _db_save_ok)


def _set_injection_flag(monkeypatch: pytest.MonkeyPatch, enabled: bool) -> None:
    monkeypatch.setenv("BRAND_MEMORY_INJECTION_ENABLED", "true" if enabled else "false")
    get_settings.cache_clear()
    assert get_settings().brand_memory_injection_enabled is enabled


# ─── 2. gated 주입 — flag ON + seed brand_memory + 신원 ────────────────


@pytest.mark.asyncio
async def test_injection_on_prepends_brand_preamble(monkeypatch: pytest.MonkeyPatch) -> None:
    """flag ON + auth_user_id + seed brand_memory(fake repo) → user_input 에 구속 프리앰블 prepend."""
    planning = _CapturingPlanning()
    _patch_pipeline(monkeypatch, planning)
    _set_injection_flag(monkeypatch, True)

    fake_repo = _FakeBrandMemoryRepo([
        {"entry_type": "preferred_tone", "content": "친근하고 담백한 톤"},
        {"entry_type": "avoid_phrase", "content": "'최저가' 표현"},
    ])

    result = await generate_plan(
        "test-plan-id", _make_plan_entry(), GenerateRequest(),
        auth_user_id="u-1",
        brand_id="b-9",
        brand_memory_repo=fake_repo,
    )

    assert isinstance(result, Envelope)
    assert len(result.body.plan_candidates) == 3
    # ★ planning 이 받은 user_input 앞에 구속 프리앰블이 붙음.
    assert planning.captured_user_input is not None
    assert planning.captured_user_input.startswith(BRAND_CONSTRAINT_PREAMBLE_HEADER)
    assert "- 톤: 친근하고 담백한 톤" in planning.captured_user_input
    assert "- 금지: '최저가' 표현" in planning.captured_user_input
    # 원본 user_input 도 보존 (prepend 이므로 뒤에 남음).
    assert "유튜브 쇼츠 만들기" in planning.captured_user_input
    # repo 가 resolved brand 로 조회됨 (PII 격리 — 전달된 brand 만).
    assert fake_repo.calls == ["b-9"]


@pytest.mark.asyncio
async def test_injection_on_resolves_brand_via_resolver(monkeypatch: pytest.MonkeyPatch) -> None:
    """brand_id 미지정 → brands_resolver(DI seam) 로 해결 후 주입."""
    planning = _CapturingPlanning()
    _patch_pipeline(monkeypatch, planning)
    _set_injection_flag(monkeypatch, True)

    fake_repo = _FakeBrandMemoryRepo([
        {"entry_type": "success_pattern", "content": "첫 3초 질문형 후크"},
    ])

    async def resolver(auth_user_id: str) -> str | None:
        assert auth_user_id == "u-7"
        return "brand-resolved"

    result = await generate_plan(
        "test-plan-id", _make_plan_entry(), GenerateRequest(),
        auth_user_id="u-7",
        brand_id=None,  # resolver 가 해결
        brand_memory_repo=fake_repo,
        brands_resolver=resolver,
    )

    assert isinstance(result, Envelope)
    assert "- 성공 패턴(반영): 첫 3초 질문형 후크" in (planning.captured_user_input or "")
    assert fake_repo.calls == ["brand-resolved"]


# ─── 3. byte-identical — flag OFF / 익명 / 메모리 0개 / brand 없음 ──────


@pytest.mark.asyncio
async def test_injection_off_byte_identical(monkeypatch: pytest.MonkeyPatch) -> None:
    """flag OFF(default) → seed 가 있어도 주입 0, user_input 무변경 (byte-identical)."""
    planning = _CapturingPlanning()
    _patch_pipeline(monkeypatch, planning)
    _set_injection_flag(monkeypatch, False)

    fake_repo = _FakeBrandMemoryRepo([{"entry_type": "preferred_tone", "content": "톤A"}])

    result = await generate_plan(
        "test-plan-id", _make_plan_entry(), GenerateRequest(),
        auth_user_id="u-1", brand_id="b-9", brand_memory_repo=fake_repo,
    )

    assert isinstance(result, Envelope)
    # ★ flag OFF — user_input 은 원본 그대로 (프리앰블 0). repo 도 미호출.
    assert planning.captured_user_input == "유튜브 쇼츠 만들기"
    assert fake_repo.calls == []


@pytest.mark.asyncio
async def test_injection_anonymous_byte_identical(monkeypatch: pytest.MonkeyPatch) -> None:
    """flag ON 이어도 익명(auth_user_id None) → 주입 0, user_input 무변경."""
    planning = _CapturingPlanning()
    _patch_pipeline(monkeypatch, planning)
    _set_injection_flag(monkeypatch, True)

    fake_repo = _FakeBrandMemoryRepo([{"entry_type": "preferred_tone", "content": "톤A"}])

    result = await generate_plan(
        "test-plan-id", _make_plan_entry(), GenerateRequest(),
        auth_user_id=None, brand_id="b-9", brand_memory_repo=fake_repo,
    )

    assert isinstance(result, Envelope)
    assert planning.captured_user_input == "유튜브 쇼츠 만들기"
    assert fake_repo.calls == []


@pytest.mark.asyncio
async def test_injection_no_memory_byte_identical(monkeypatch: pytest.MonkeyPatch) -> None:
    """flag ON + 신원 有 이지만 brand_memory 0개 → 주입 0, user_input 무변경."""
    planning = _CapturingPlanning()
    _patch_pipeline(monkeypatch, planning)
    _set_injection_flag(monkeypatch, True)

    fake_repo = _FakeBrandMemoryRepo([])  # 메모리 없음

    result = await generate_plan(
        "test-plan-id", _make_plan_entry(), GenerateRequest(),
        auth_user_id="u-1", brand_id="b-9", brand_memory_repo=fake_repo,
    )

    assert isinstance(result, Envelope)
    assert planning.captured_user_input == "유튜브 쇼츠 만들기"
    assert fake_repo.calls == ["b-9"]  # 조회는 했지만 0개 → 주입 없음


@pytest.mark.asyncio
async def test_injection_no_brand_byte_identical(monkeypatch: pytest.MonkeyPatch) -> None:
    """flag ON + 신원 有 이지만 brand 미해결(brand_id None + resolver None 반환) → 주입 0."""
    planning = _CapturingPlanning()
    _patch_pipeline(monkeypatch, planning)
    _set_injection_flag(monkeypatch, True)

    fake_repo = _FakeBrandMemoryRepo([{"entry_type": "preferred_tone", "content": "톤A"}])

    async def resolver(auth_user_id: str) -> str | None:
        return None  # brand 없음

    result = await generate_plan(
        "test-plan-id", _make_plan_entry(), GenerateRequest(),
        auth_user_id="u-1", brand_id=None,
        brand_memory_repo=fake_repo, brands_resolver=resolver,
    )

    assert isinstance(result, Envelope)
    assert planning.captured_user_input == "유튜브 쇼츠 만들기"
    # brand 미해결 → repo 미호출.
    assert fake_repo.calls == []
