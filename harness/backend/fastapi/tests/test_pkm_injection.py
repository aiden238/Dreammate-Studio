"""Phase 17 다-S3 — 개인 PKM 구속 주입 (gated orchestrator, personal > brand) 테스트.

검증 축 (test_brand_injection.py 패턴 계승 — capturing-mock):
  - gated 주입: personal flag ON + seed PkmRepo + auth_user_id →
    planning user_input 에 개인 PKM 구속 프리앰블이 prepend 되고 정상 Envelope.
  - ★ 우선순위: personal+brand 둘 다 seed+flag ON → personal 블록이 brand 블록보다 앞.
  - byte-identical: personal flag OFF(default) / 익명 / personal 엔트리 0개 →
    personal 프리앰블 0 (user_input 에 personal directive 미포함, brand-only 경로 보존).

★ DI seam: pkm_repo / brand_memory_repo 인자로 실 Supabase 없이 seed.
  user_input 캡처는 run_planning_parallel_3 mock 이 받은 첫 인자(user_input) 로 확인.
"""

from __future__ import annotations

import copy
from typing import Any

import pytest

from backend.fastapi.agents.brand_injection import BRAND_CONSTRAINT_PREAMBLE_HEADER
from backend.fastapi.config import get_settings
from backend.fastapi.db.types import PersistenceResult
from backend.fastapi.orchestration import generate_plan
from backend.fastapi.rag.types import RetrievalResult
from backend.fastapi.schemas.output import Envelope
from backend.fastapi.schemas.plans import GenerateRequest


# ─── pipeline patch helpers (test_brand_injection.py 와 동일 패턴) ──────


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


class _FakePkmRepo:
    """PkmRepo-호환 fake — seed 한 rows 를 반환 (DI seam). list_for_user 호출 추적."""

    def __init__(self, rows: list[dict[str, Any]]) -> None:
        self.rows = rows
        self.calls: list[tuple[str, str]] = []

    async def list_for_user(self, auth_user_id: str, *, scope: str = "personal") -> list[dict[str, Any]]:
        self.calls.append((auth_user_id, scope))
        return list(self.rows)


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


def _set_flags(
    monkeypatch: pytest.MonkeyPatch, *, personal: bool, brand: bool = False,
) -> None:
    monkeypatch.setenv("PERSONAL_PKM_INJECTION_ENABLED", "true" if personal else "false")
    monkeypatch.setenv("BRAND_MEMORY_INJECTION_ENABLED", "true" if brand else "false")
    get_settings.cache_clear()
    s = get_settings()
    assert s.personal_pkm_injection_enabled is personal
    assert s.brand_memory_injection_enabled is brand


# ─── 1. gated 주입 — personal flag ON + seed PKM + 신원 ────────────────


@pytest.mark.asyncio
async def test_personal_injection_on_prepends_preamble(monkeypatch: pytest.MonkeyPatch) -> None:
    """personal flag ON + auth_user_id + seed PKM → user_input 에 개인 PKM 프리앰블 prepend."""
    planning = _CapturingPlanning()
    _patch_pipeline(monkeypatch, planning)
    _set_flags(monkeypatch, personal=True)

    fake_pkm = _FakePkmRepo([
        {"entry_type": "preferred_tone", "content": "담백하고 차분한 개인 톤"},
        {"entry_type": "preferred_phrase", "content": "'천천히 시작해요'"},
    ])

    result = await generate_plan(
        "test-plan-id", _make_plan_entry(), GenerateRequest(),
        auth_user_id="u-1",
        pkm_repo=fake_pkm,
    )

    assert isinstance(result, Envelope)
    assert len(result.body.plan_candidates) == 3
    captured = planning.captured_user_input
    assert captured is not None
    assert captured.startswith(BRAND_CONSTRAINT_PREAMBLE_HEADER)
    assert "- 톤: 담백하고 차분한 개인 톤" in captured
    assert "- 선호 표현: '천천히 시작해요'" in captured
    # 원본 user_input 보존 (prepend 이므로 뒤에 남음).
    assert "유튜브 쇼츠 만들기" in captured
    # ★ brand 무관 — auth_user_id 만으로 personal scope 조회.
    assert fake_pkm.calls == [("u-1", "personal")]


# ─── 2. ★ 우선순위 — personal + brand 둘 다 ON → personal 이 brand 앞 ──


@pytest.mark.asyncio
async def test_personal_precedes_brand_when_both_on(monkeypatch: pytest.MonkeyPatch) -> None:
    """personal+brand 둘 다 seed+flag ON → personal 블록이 brand 블록보다 앞 (설계 §6.2)."""
    planning = _CapturingPlanning()
    _patch_pipeline(monkeypatch, planning)
    _set_flags(monkeypatch, personal=True, brand=True)

    fake_pkm = _FakePkmRepo([
        {"entry_type": "preferred_tone", "content": "PERSONAL_개인톤"},
    ])
    fake_brand = _FakeBrandMemoryRepo([
        {"entry_type": "preferred_tone", "content": "BRAND_브랜드톤"},
    ])

    result = await generate_plan(
        "test-plan-id", _make_plan_entry(), GenerateRequest(),
        auth_user_id="u-1",
        brand_id="b-9",
        pkm_repo=fake_pkm,
        brand_memory_repo=fake_brand,
    )

    assert isinstance(result, Envelope)
    captured = planning.captured_user_input or ""
    # 둘 다 주입됨.
    assert "PERSONAL_개인톤" in captured
    assert "BRAND_브랜드톤" in captured
    # ★ personal 이 brand 보다 앞 (personal > brand). 원본 입력은 맨 뒤.
    assert captured.index("PERSONAL_개인톤") < captured.index("BRAND_브랜드톤")
    assert captured.index("BRAND_브랜드톤") < captured.index("유튜브 쇼츠 만들기")
    # 각 repo 조회됨.
    assert fake_pkm.calls == [("u-1", "personal")]
    assert fake_brand.calls == ["b-9"]


# ─── 3. byte-identical — personal flag OFF / 익명 / 엔트리 0개 ──────────


@pytest.mark.asyncio
async def test_personal_off_no_preamble(monkeypatch: pytest.MonkeyPatch) -> None:
    """personal flag OFF(default) → seed 가 있어도 personal 주입 0, user_input 무변경."""
    planning = _CapturingPlanning()
    _patch_pipeline(monkeypatch, planning)
    _set_flags(monkeypatch, personal=False)

    fake_pkm = _FakePkmRepo([{"entry_type": "preferred_tone", "content": "개인톤"}])

    result = await generate_plan(
        "test-plan-id", _make_plan_entry(), GenerateRequest(),
        auth_user_id="u-1", pkm_repo=fake_pkm,
    )

    assert isinstance(result, Envelope)
    # ★ flag OFF — user_input 은 원본 그대로 (personal 프리앰블 0). repo 도 미호출.
    assert planning.captured_user_input == "유튜브 쇼츠 만들기"
    assert fake_pkm.calls == []


@pytest.mark.asyncio
async def test_personal_anonymous_no_preamble(monkeypatch: pytest.MonkeyPatch) -> None:
    """personal flag ON 이어도 익명(auth_user_id None) → personal 주입 0, user_input 무변경."""
    planning = _CapturingPlanning()
    _patch_pipeline(monkeypatch, planning)
    _set_flags(monkeypatch, personal=True)

    fake_pkm = _FakePkmRepo([{"entry_type": "preferred_tone", "content": "개인톤"}])

    result = await generate_plan(
        "test-plan-id", _make_plan_entry(), GenerateRequest(),
        auth_user_id=None, pkm_repo=fake_pkm,
    )

    assert isinstance(result, Envelope)
    assert planning.captured_user_input == "유튜브 쇼츠 만들기"
    assert fake_pkm.calls == []


@pytest.mark.asyncio
async def test_personal_no_entries_no_preamble(monkeypatch: pytest.MonkeyPatch) -> None:
    """personal flag ON + 신원 有 이지만 personal PKM 0개 → 주입 0, user_input 무변경."""
    planning = _CapturingPlanning()
    _patch_pipeline(monkeypatch, planning)
    _set_flags(monkeypatch, personal=True)

    fake_pkm = _FakePkmRepo([])  # 엔트리 없음

    result = await generate_plan(
        "test-plan-id", _make_plan_entry(), GenerateRequest(),
        auth_user_id="u-1", pkm_repo=fake_pkm,
    )

    assert isinstance(result, Envelope)
    assert planning.captured_user_input == "유튜브 쇼츠 만들기"
    # 조회는 했지만 0개 → 주입 없음.
    assert fake_pkm.calls == [("u-1", "personal")]


@pytest.mark.asyncio
async def test_brand_only_unchanged_when_personal_off(monkeypatch: pytest.MonkeyPatch) -> None:
    """personal OFF + brand ON → brand 주입만 (가-S2 경로 보존, personal directive 미포함)."""
    planning = _CapturingPlanning()
    _patch_pipeline(monkeypatch, planning)
    _set_flags(monkeypatch, personal=False, brand=True)

    fake_pkm = _FakePkmRepo([{"entry_type": "preferred_tone", "content": "PERSONAL_개인톤"}])
    fake_brand = _FakeBrandMemoryRepo([{"entry_type": "preferred_tone", "content": "BRAND_브랜드톤"}])

    result = await generate_plan(
        "test-plan-id", _make_plan_entry(), GenerateRequest(),
        auth_user_id="u-1", brand_id="b-9",
        pkm_repo=fake_pkm, brand_memory_repo=fake_brand,
    )

    assert isinstance(result, Envelope)
    captured = planning.captured_user_input or ""
    # brand 만 주입, personal 은 미주입 (personal flag OFF).
    assert "BRAND_브랜드톤" in captured
    assert "PERSONAL_개인톤" not in captured
    assert captured.startswith(BRAND_CONSTRAINT_PREAMBLE_HEADER)
    assert fake_pkm.calls == []  # personal repo 미호출.
    assert fake_brand.calls == ["b-9"]
