"""Phase 17 다-S5 — brand_memory 추출 루프 배선 (gated, graceful) 테스트.

가-S2/S3 가 brand_memory 를 planning 에 **주입**(읽기)했지만 brand_memory_entries 는 비어있었다
(추출기가 배선되지 않음). 본 슬라이스는 feedback/selection 신호 → brand_memory_entries 적재
(쓰기)를 feedback endpoint 에 배선한다.

검증 축:
  - flag ON + 신원 → run_brand_memory_extractor(persist=True) 가 resolved brand_id 로 호출되고,
    confidence ≥ 0.9 (명시 선호) 후보가 (in-memory) BrandMemoryRepo 에 영속화된다.
  - ★ governance (ADR-031 §7.5): confidence < 0.9 (1회성/반복, reason 없음) → 영속화 0 (제안만).
  - flag OFF(default) → 추출기 미호출, brand_memory 쓰기 0, BrandRepo 미호출 (no surprise write).
  - 익명(auth_user_id None) → 추출기 미호출, 쓰기 0.
  - graceful: 추출 실패해도 feedback endpoint 응답 byte-identical (HTTP 200, 차단 0).

★ DI seam: _run_brand_memory_extract_hook 에 feedback/selection/brand/brand_memory repo 를
  인자로 주입 → 실 Supabase 없이 end-to-end 배선 입증 (test_brand_repo / test_selection_feedback 패턴).
"""

from __future__ import annotations

from typing import Any

import pytest
from fastapi.testclient import TestClient

from backend.fastapi.config import get_settings
from backend.fastapi.db.repositories.brand_memory_repo import BrandMemoryRepo
from backend.fastapi.db.repositories.brand_repo import BrandRepo
from backend.fastapi.db.repositories.feedback_repo import FeedbackRepo
from backend.fastapi.db.repositories.selection_repo import SelectionRepo
from backend.fastapi.main import app
from backend.fastapi.routers.plans import _run_brand_memory_extract_hook


# ─── helpers ──────────────────────────────────────────────────────────


def _set_extract_flag(monkeypatch: pytest.MonkeyPatch, enabled: bool) -> None:
    """settings.brand_memory_extract_enabled 토글 + lru_cache 무효화 (가-S2 패턴 동일)."""
    monkeypatch.setenv("BRAND_MEMORY_EXTRACT_ENABLED", "true" if enabled else "false")
    get_settings.cache_clear()
    assert get_settings().brand_memory_extract_enabled is enabled


class _ForbiddenBrandRepo:
    """get_or_create_default 호출 시 즉시 실패 (no surprise write 보장 — test_brand_repo 패턴)."""

    async def get_or_create_default(self, *args: Any, **kwargs: Any) -> str:  # pragma: no cover
        raise AssertionError("BrandRepo.get_or_create_default must NOT be called (flag OFF/anon)")

    async def get_default_brand_id(self, *args: Any, **kwargs: Any) -> str:  # pragma: no cover
        raise AssertionError("BrandRepo.get_default_brand_id must NOT be called (flag OFF/anon)")


def _fresh_repos() -> tuple[FeedbackRepo, SelectionRepo, BrandRepo, BrandMemoryRepo]:
    return (
        FeedbackRepo(supabase_client=None, in_memory_store={}),
        SelectionRepo(supabase_client=None, in_memory_store={}),
        BrandRepo(supabase_client=None, in_memory_store={}),
        BrandMemoryRepo(supabase_client=None, in_memory_store={}),
    )


# ─── 1. flag ON + 신원 → 추출 + 고신뢰(≥0.9) 영속화 ────────────────────


@pytest.mark.asyncio
async def test_extract_on_persists_high_confidence_entry(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """★ flag ON + authed + 명시 사유(reason) → confidence 0.9 후보가 BrandMemoryRepo 에 영속화."""
    _set_extract_flag(monkeypatch, True)
    fb, sel, brand, mem = _fresh_repos()

    # 명시 사유(reason) 동반 부정 신호 → avoid_phrase confidence 0.9 (명시 선호).
    await fb.record("plan-1", "dislike", reason="너무 과장된 톤은 피해주세요")

    await _run_brand_memory_extract_hook(
        "plan-1", "u-1",
        feedback_repo=fb, selection_repo=sel, brand_repo=brand, brand_memory_repo=mem,
    )

    # 기본 brand 가 get-or-create 됨 (anchor).
    brand_id = await brand.get_default_brand_id("u-1")
    assert brand_id is not None
    # confidence ≥ 0.9 후보가 그 brand 로 영속화 (자동 INSERT — agent_io §7.5).
    entries = await mem.list_for_brand(brand_id)
    assert len(entries) >= 1
    assert all(float(e["confidence"]) >= 0.9 for e in entries)
    # avoid_phrase (명시 사유 동반 부정 신호) 가 포함됨.
    assert any(e["entry_type"] == "avoid_phrase" for e in entries)


@pytest.mark.asyncio
async def test_extract_invokes_extractor_with_persist_true_and_resolved_brand(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """run_brand_memory_extractor 가 persist=True + resolved brand_id 로 호출됨 (배선 입증)."""
    _set_extract_flag(monkeypatch, True)
    fb, sel, brand, mem = _fresh_repos()
    await fb.record("plan-x", "like", reason="이 후크가 정말 좋아요")

    captured: dict[str, Any] = {}

    async def fake_extractor(*args: Any, **kwargs: Any) -> dict[str, Any]:
        captured["args"] = args
        captured["kwargs"] = kwargs
        return {"proposed_entries": [], "conflicts": [], "persisted": []}

    monkeypatch.setattr(
        "backend.fastapi.routers.plans.run_brand_memory_extractor", fake_extractor,
    )

    await _run_brand_memory_extract_hook(
        "plan-x", "u-9",
        feedback_repo=fb, selection_repo=sel, brand_repo=brand, brand_memory_repo=mem,
    )

    expected_brand = await brand.get_default_brand_id("u-9")
    assert captured["kwargs"]["persist"] is True
    assert captured["kwargs"]["brand_id"] == expected_brand
    assert captured["kwargs"]["repo"] is mem
    # current_brand_memory(dedup 입력)도 전달됨.
    assert "current_brand_memory" in captured["kwargs"]


# ─── 2. governance — confidence < 0.9 (reason 없음) → 영속화 0 (제안만) ──


@pytest.mark.asyncio
async def test_extract_low_confidence_not_persisted(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """★ 명시 사유 없는 1회성/반복 신호 (confidence 0.3/0.7) → 자동 INSERT 0 (제안만 — NG12)."""
    _set_extract_flag(monkeypatch, True)
    fb, sel, brand, mem = _fresh_repos()

    # reason 없는 부정 신호 1회 → confidence 0.3 (1회성). 0.9 미만 → 영속화 안 됨.
    await fb.record("plan-2", "dislike")

    await _run_brand_memory_extract_hook(
        "plan-2", "u-2",
        feedback_repo=fb, selection_repo=sel, brand_repo=brand, brand_memory_repo=mem,
    )

    brand_id = await brand.get_default_brand_id("u-2")
    assert brand_id is not None  # brand 는 anchor 로 생성됨
    # ★ confidence < 0.9 → brand_memory_entries 쓰기 0 (제안만, pending UX).
    entries = await mem.list_for_brand(brand_id)
    assert entries == []


# ─── 3. behavior-preserving — flag OFF / 익명 → 추출기 미호출, 쓰기 0 ────


@pytest.mark.asyncio
async def test_extract_off_no_call_no_write(monkeypatch: pytest.MonkeyPatch) -> None:
    """★ flag OFF(default) → 추출기 미호출, BrandRepo 미호출, brand_memory 쓰기 0."""
    _set_extract_flag(monkeypatch, False)
    fb, sel, _, mem = _fresh_repos()
    await fb.record("plan-3", "dislike", reason="명시 사유 있어도 OFF 면 추출 0")

    def fail_extractor(*args: Any, **kwargs: Any):  # pragma: no cover
        raise AssertionError("extractor must NOT be called when flag OFF")

    monkeypatch.setattr(
        "backend.fastapi.routers.plans.run_brand_memory_extractor", fail_extractor,
    )

    # ★ _ForbiddenBrandRepo — 호출되면 AssertionError (no surprise write).
    await _run_brand_memory_extract_hook(
        "plan-3", "u-3",
        feedback_repo=fb, selection_repo=sel,
        brand_repo=_ForbiddenBrandRepo(), brand_memory_repo=mem,
    )

    # brand_memory 쓰기 0 (어떤 brand 도 entries 없음).
    assert mem.store == {}


@pytest.mark.asyncio
async def test_extract_anonymous_no_call_no_write(monkeypatch: pytest.MonkeyPatch) -> None:
    """★ flag ON 이어도 익명(auth_user_id None) → 추출기 미호출, 쓰기 0."""
    _set_extract_flag(monkeypatch, True)
    fb, sel, _, mem = _fresh_repos()
    await fb.record("plan-4", "like", reason="익명이면 추출 0")

    def fail_extractor(*args: Any, **kwargs: Any):  # pragma: no cover
        raise AssertionError("extractor must NOT be called for anonymous")

    monkeypatch.setattr(
        "backend.fastapi.routers.plans.run_brand_memory_extractor", fail_extractor,
    )

    await _run_brand_memory_extract_hook(
        "plan-4", None,  # 익명
        feedback_repo=fb, selection_repo=sel,
        brand_repo=_ForbiddenBrandRepo(), brand_memory_repo=mem,
    )

    assert mem.store == {}


# ─── 4. graceful — 추출 실패해도 feedback endpoint 응답 byte-identical ──


def test_feedback_endpoint_byte_identical_when_extract_off(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """flag OFF(default) → feedback endpoint 200 + 응답 schema 불변 (HTTP e2e, 회귀 0)."""
    _set_extract_flag(monkeypatch, False)
    client = TestClient(app)

    start = client.post("/api/v1/plans/start", json={"user_input": "유튜브 쇼츠"}).json()
    plan_id = start["plan_id"]

    r = client.post(f"/api/v1/plans/{plan_id}/feedback", json={"event_type": "like"})
    assert r.status_code == 200
    data = r.json()
    assert data["plan_id"] == plan_id
    assert data["event_type"] == "like"
    assert "recorded_at" in data


def test_feedback_endpoint_graceful_when_extract_raises(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """★ flag ON + 추출 hook 이 예외를 던져도 feedback endpoint 는 200 (graceful, 차단 0)."""
    _set_extract_flag(monkeypatch, True)
    client = TestClient(app)

    async def boom(*args: Any, **kwargs: Any) -> None:
        raise RuntimeError("simulated extract failure")

    monkeypatch.setattr(
        "backend.fastapi.routers.plans._run_brand_memory_extract_hook", boom,
    )

    start = client.post("/api/v1/plans/start", json={"user_input": "유튜브 쇼츠"}).json()
    plan_id = start["plan_id"]

    r = client.post(f"/api/v1/plans/{plan_id}/feedback", json={"event_type": "dislike"})
    # ★ 추출 실패가 feedback 기록을 차단하지 않음 — 200 + 정상 응답.
    assert r.status_code == 200
    assert r.json()["event_type"] == "dislike"
