"""Phase 17 다-S6 — 개인 PKM 추출 루프 배선 (gated, graceful) 테스트.

다-S3 가 pkm_entries(scope=personal) 테이블 + PkmRepo + planning 주입(읽기)을 만들었지만
pkm_entries 는 비어있었다 (추출기가 배선되지 않음). 본 슬라이스는 feedback 신호 →
pkm_entries(scope=personal) 적재(쓰기)를 feedback endpoint 에 배선한다 (다-S5 brand 의 개인 대칭).

검증 축 (test_brand_memory_extract_wiring 패턴 미러):
  - flag ON + 신원 → confidence ≥ 0.9 (명시 선호) 후보가 (in-memory) PkmRepo 에
    scope='personal' + 올바른 auth_user_id 로 영속화된다.
  - ★ governance (ADR-031 §7.5): confidence < 0.9 (1회성/반복, reason 없음) → 영속화 0 (제안만).
  - flag OFF(default) → 추출기 미호출, pkm_entries 쓰기 0 (no surprise write).
  - 익명(auth_user_id None) → 추출기 미호출, 쓰기 0.
  - graceful: 추출 실패해도 feedback endpoint 응답 byte-identical (HTTP 200, 차단 0).
  - ★ brand-독립: brand 해결 없이 auth_user_id 만으로 적재 (BrandRepo 미관여).

★ DI seam: _run_personal_pkm_extract_hook 에 feedback/selection/pkm repo 를 인자로 주입 →
  실 Supabase 없이 end-to-end 배선 입증 (test_pkm_repo / test_brand_memory_extract_wiring 패턴).
"""

from __future__ import annotations

from typing import Any

import pytest
from fastapi.testclient import TestClient

from backend.fastapi.config import get_settings
from backend.fastapi.db.repositories.feedback_repo import FeedbackRepo
from backend.fastapi.db.repositories.pkm_repo import PkmRepo
from backend.fastapi.db.repositories.selection_repo import SelectionRepo
from backend.fastapi.main import app
from backend.fastapi.routers.plans import _run_personal_pkm_extract_hook


# ─── helpers ──────────────────────────────────────────────────────────


def _set_extract_flag(monkeypatch: pytest.MonkeyPatch, enabled: bool) -> None:
    """settings.personal_pkm_extract_enabled 토글 + lru_cache 무효화 (다-S5 패턴 동일)."""
    monkeypatch.setenv("PERSONAL_PKM_EXTRACT_ENABLED", "true" if enabled else "false")
    get_settings.cache_clear()
    assert get_settings().personal_pkm_extract_enabled is enabled


def _fresh_repos() -> tuple[FeedbackRepo, SelectionRepo, PkmRepo]:
    return (
        FeedbackRepo(supabase_client=None, in_memory_store={}),
        SelectionRepo(supabase_client=None, in_memory_store={}),
        PkmRepo(supabase_client=None, in_memory_store={}),
    )


# ─── 1. flag ON + 신원 → 추출 + 고신뢰(≥0.9) personal 영속화 ────────────


@pytest.mark.asyncio
async def test_extract_on_persists_high_confidence_personal_entry(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """★ flag ON + authed + 명시 사유(reason) → confidence 0.9 후보가 PkmRepo 에 personal 영속화."""
    _set_extract_flag(monkeypatch, True)
    fb, sel, pkm = _fresh_repos()

    # 명시 사유(reason) 동반 부정 신호 → avoid_phrase confidence 0.9 (명시 선호).
    await fb.record("plan-1", "dislike", reason="너무 과장된 톤은 피해주세요")

    await _run_personal_pkm_extract_hook(
        "plan-1", "u-1",
        feedback_repo=fb, selection_repo=sel, pkm_repo=pkm,
    )

    # confidence ≥ 0.9 후보가 personal scope + 올바른 auth_user_id 로 영속화.
    entries = await pkm.list_for_user("u-1", scope="personal")
    assert len(entries) >= 1
    assert all(float(e["confidence"]) >= 0.9 for e in entries)
    assert all(e["scope"] == "personal" for e in entries)
    assert all(e["auth_user_id"] == "u-1" for e in entries)
    # avoid_phrase (명시 사유 동반 부정 신호) 가 포함됨.
    assert any(e["entry_type"] == "avoid_phrase" for e in entries)


@pytest.mark.asyncio
async def test_extract_invokes_pure_extractor_with_current_pkm_dedup(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """순수 extract_brand_memory_candidates 가 current_pkm(dedup 입력) 으로 호출됨 (배선 입증)."""
    _set_extract_flag(monkeypatch, True)
    fb, sel, pkm = _fresh_repos()
    await fb.record("plan-x", "like", reason="이 후크가 정말 좋아요")
    # 기존 personal entry 1개 — dedup 입력으로 전달되는지 검증.
    await pkm.add_entry("u-9", "preferred_tone", "기존 톤", scope="personal", confidence=0.9)

    captured: dict[str, Any] = {}

    def fake_extractor(*args: Any, **kwargs: Any) -> dict[str, Any]:
        captured["args"] = args
        captured["kwargs"] = kwargs
        return {"proposed_entries": [], "conflicts": []}

    monkeypatch.setattr(
        "backend.fastapi.routers.plans.extract_brand_memory_candidates", fake_extractor,
    )

    await _run_personal_pkm_extract_hook(
        "plan-x", "u-9",
        feedback_repo=fb, selection_repo=sel, pkm_repo=pkm,
    )

    # current_brand_memory(dedup 입력) = 기존 personal PKM 이 전달됨.
    assert "current_brand_memory" in captured["kwargs"]
    current = captured["kwargs"]["current_brand_memory"]
    assert any(e.get("entry_type") == "preferred_tone" for e in current)


@pytest.mark.asyncio
async def test_extract_reuses_preloaded_signals_no_repo_read(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """호출자가 feedback_events/selected_plans 를 넘기면 repo.list_for_plan 재로드 안 함 (읽기 공유)."""
    _set_extract_flag(monkeypatch, True)
    _, sel, pkm = _fresh_repos()

    class _ForbiddenFeedbackRepo:
        async def list_for_plan(self, *a: Any, **k: Any):  # pragma: no cover
            raise AssertionError("list_for_plan must NOT be called when events pre-loaded")

    await _run_personal_pkm_extract_hook(
        "plan-pre", "u-pre",
        feedback_repo=_ForbiddenFeedbackRepo(), selection_repo=sel, pkm_repo=pkm,
        feedback_events=[{"event_type": "dislike", "reason": "과장된 톤 회피"}],
        selected_plans=[],
    )

    entries = await pkm.list_for_user("u-pre", scope="personal")
    assert any(e["entry_type"] == "avoid_phrase" for e in entries)


# ─── 2. governance — confidence < 0.9 (reason 없음) → 영속화 0 (제안만) ──


@pytest.mark.asyncio
async def test_extract_low_confidence_not_persisted(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """★ 명시 사유 없는 1회성/반복 신호 (confidence 0.3/0.7) → 자동 INSERT 0 (제안만 — NG12)."""
    _set_extract_flag(monkeypatch, True)
    fb, sel, pkm = _fresh_repos()

    # reason 없는 부정 신호 1회 → confidence 0.3 (1회성). 0.9 미만 → 영속화 안 됨.
    await fb.record("plan-2", "dislike")

    await _run_personal_pkm_extract_hook(
        "plan-2", "u-2",
        feedback_repo=fb, selection_repo=sel, pkm_repo=pkm,
    )

    # ★ confidence < 0.9 → pkm_entries 쓰기 0 (제안만, pending UX).
    entries = await pkm.list_for_user("u-2", scope="personal")
    assert entries == []


# ─── 3. behavior-preserving — flag OFF / 익명 → 추출기 미호출, 쓰기 0 ────


@pytest.mark.asyncio
async def test_extract_off_no_call_no_write(monkeypatch: pytest.MonkeyPatch) -> None:
    """★ flag OFF(default) → 추출기 미호출, pkm_entries 쓰기 0 (no surprise write)."""
    _set_extract_flag(monkeypatch, False)
    fb, sel, pkm = _fresh_repos()
    await fb.record("plan-3", "dislike", reason="명시 사유 있어도 OFF 면 추출 0")

    def fail_extractor(*args: Any, **kwargs: Any):  # pragma: no cover
        raise AssertionError("extractor must NOT be called when flag OFF")

    monkeypatch.setattr(
        "backend.fastapi.routers.plans.extract_brand_memory_candidates", fail_extractor,
    )

    await _run_personal_pkm_extract_hook(
        "plan-3", "u-3",
        feedback_repo=fb, selection_repo=sel, pkm_repo=pkm,
    )

    # pkm_entries 쓰기 0.
    assert pkm.store == {}


@pytest.mark.asyncio
async def test_extract_anonymous_no_call_no_write(monkeypatch: pytest.MonkeyPatch) -> None:
    """★ flag ON 이어도 익명(auth_user_id None) → 추출기 미호출, 쓰기 0."""
    _set_extract_flag(monkeypatch, True)
    fb, sel, pkm = _fresh_repos()
    await fb.record("plan-4", "like", reason="익명이면 추출 0")

    def fail_extractor(*args: Any, **kwargs: Any):  # pragma: no cover
        raise AssertionError("extractor must NOT be called for anonymous")

    monkeypatch.setattr(
        "backend.fastapi.routers.plans.extract_brand_memory_candidates", fail_extractor,
    )

    await _run_personal_pkm_extract_hook(
        "plan-4", None,  # 익명
        feedback_repo=fb, selection_repo=sel, pkm_repo=pkm,
    )

    assert pkm.store == {}


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
    """★ flag ON + 개인 PKM 추출 hook 이 예외를 던져도 feedback endpoint 는 200 (graceful, 차단 0)."""
    _set_extract_flag(monkeypatch, True)
    client = TestClient(app)

    async def boom(*args: Any, **kwargs: Any) -> None:
        raise RuntimeError("simulated personal pkm extract failure")

    monkeypatch.setattr(
        "backend.fastapi.routers.plans._run_personal_pkm_extract_hook", boom,
    )

    start = client.post("/api/v1/plans/start", json={"user_input": "유튜브 쇼츠"}).json()
    plan_id = start["plan_id"]

    r = client.post(f"/api/v1/plans/{plan_id}/feedback", json={"event_type": "dislike"})
    # ★ 추출 실패가 feedback 기록을 차단하지 않음 — 200 + 정상 응답.
    assert r.status_code == 200
    assert r.json()["event_type"] == "dislike"
