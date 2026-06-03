"""Phase 17 가-S3 — BrandRepo (기본 브랜드 get-or-create) + gated generate_plan 자동생성 wiring.

검증 축:
  - BrandRepo in-memory: get_or_create_default 없을 때 생성(새 id, 영속), 두 번째 호출 동일 id
    (idempotent), get_default_brand_id None/id, Supabase 실패 → graceful None.
  - generate_plan gated wiring: flag ON + 신원 + (빈) in-memory BrandRepo + seeded BrandMemoryRepo
    → 기본 브랜드 자동생성 → 그 brand 로 brand_memory 주입 발화. flag OFF / 익명 → BrandRepo
    미호출, brand 0 생성, user_input byte-identical (no surprise write).

★ DI seam: brand_repo / brand_memory_repo 인자로 실 Supabase 없이 end-to-end 자동생성→주입 입증.
  planning user_input 캡처는 run_planning_parallel_3 mock 의 첫 인자(user_input) 로 확인
  (test_brand_injection.py 패턴 재사용).
"""

from __future__ import annotations

import copy
from typing import Any
from unittest.mock import MagicMock

import pytest

from backend.fastapi.agents.brand_injection import (
    BRAND_CONSTRAINT_PREAMBLE_HEADER,
    build_brand_constraint_preamble,  # noqa: F401  (parity import — 빌더 존재 확인)
)
from backend.fastapi.config import get_settings
from backend.fastapi.db import DEFAULT_BRAND_NAME, BrandRepo
from backend.fastapi.db.types import PersistenceResult
from backend.fastapi.orchestration import generate_plan
from backend.fastapi.rag.types import RetrievalResult
from backend.fastapi.schemas.output import Envelope
from backend.fastapi.schemas.plans import GenerateRequest


# ─── 1. BrandRepo in-memory — get-or-create idempotency ────────────────


@pytest.mark.asyncio
async def test_get_default_brand_id_none_when_absent() -> None:
    """brand 없는 user → get_default_brand_id None (graceful)."""
    repo = BrandRepo()
    assert await repo.get_default_brand_id("u-absent") is None


@pytest.mark.asyncio
async def test_get_or_create_creates_when_none() -> None:
    """기존 brand 없으면 생성 → 새 id 반환 + in-memory store 에 영속 + 기본 이름."""
    repo = BrandRepo()
    bid = await repo.get_or_create_default("u-1")
    assert bid  # 새 id 발급
    # 영속 — get_default_brand_id 가 동일 id 반환.
    assert await repo.get_default_brand_id("u-1") == bid
    # store 에 정확히 1개, 기본 이름 + 요청 user 만.
    assert len(repo.store["u-1"]) == 1
    assert repo.store["u-1"][0]["name"] == DEFAULT_BRAND_NAME
    assert repo.store["u-1"][0]["auth_user_id"] == "u-1"


@pytest.mark.asyncio
async def test_get_or_create_idempotent_same_id() -> None:
    """★ 두 번째 호출도 동일 id (query-before-insert — 2번째 default 생성 0)."""
    repo = BrandRepo()
    first = await repo.get_or_create_default("u-2")
    second = await repo.get_or_create_default("u-2")
    assert first == second
    # 반복 호출에도 store 에 brand 는 1개뿐 (no duplicate).
    assert len(repo.store["u-2"]) == 1


@pytest.mark.asyncio
async def test_get_or_create_per_user_isolation() -> None:
    """서로 다른 user → 서로 다른 brand (교차 계정 0)."""
    repo = BrandRepo()
    a = await repo.get_or_create_default("u-a")
    b = await repo.get_or_create_default("u-b")
    assert a != b
    assert await repo.get_default_brand_id("u-a") == a
    assert await repo.get_default_brand_id("u-b") == b


@pytest.mark.asyncio
async def test_get_or_create_uses_existing_supabase_brand() -> None:
    """Supabase 에 기존 brand 있으면 그 id 반환 (INSERT 안 함 — idempotent)."""
    mock_client = MagicMock()
    mock_client.table.return_value.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value.data = [
        {"id": "existing-brand-uuid"}
    ]
    repo = BrandRepo(supabase_client=mock_client)
    bid = await repo.get_or_create_default("u-3")
    assert bid == "existing-brand-uuid"
    # 기존이 있으므로 insert 는 호출되지 않음.
    assert not mock_client.table.return_value.insert.called


@pytest.mark.asyncio
async def test_get_or_create_inserts_when_supabase_empty() -> None:
    """Supabase 에 brand 없으면 INSERT 후 새 id 반환."""
    mock_client = MagicMock()
    # 조회 → 없음
    mock_client.table.return_value.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value.data = []
    # insert → 새 row
    mock_client.table.return_value.insert.return_value.execute.return_value.data = [
        {"id": "new-brand-uuid", "auth_user_id": "u-4", "name": DEFAULT_BRAND_NAME}
    ]
    repo = BrandRepo(supabase_client=mock_client)
    bid = await repo.get_or_create_default("u-4")
    assert bid == "new-brand-uuid"
    assert mock_client.table.return_value.insert.called


@pytest.mark.asyncio
async def test_get_or_create_supabase_failure_graceful_none() -> None:
    """★ graceful: Supabase insert 실패 → None (raise 0, no injection)."""
    mock_client = MagicMock()
    mock_client.table.return_value.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value.data = []
    mock_client.table.return_value.insert.return_value.execute.side_effect = (
        RuntimeError("simulated network failure")
    )
    repo = BrandRepo(supabase_client=mock_client)
    bid = await repo.get_or_create_default("u-5")
    assert bid is None  # graceful — 차단 0


@pytest.mark.asyncio
async def test_get_default_supabase_failure_graceful_none() -> None:
    """get_default_brand_id 조회 실패 → graceful None (in-memory 비어있음)."""
    mock_client = MagicMock()
    mock_client.table.return_value.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.side_effect = (
        RuntimeError("simulated select failure")
    )
    repo = BrandRepo(supabase_client=mock_client)
    assert await repo.get_default_brand_id("u-6") is None


# ─── 2. gated generate_plan wiring — 자동생성 → 주입 end-to-end ─────────

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


class _BrandKeyedMemoryRepo:
    """BrandMemoryRepo-호환 fake — brand_id 별 seed rows 반환 (자동생성 brand 매칭 입증용)."""

    def __init__(self, by_brand: dict[str, list[dict[str, Any]]]) -> None:
        self.by_brand = by_brand
        self.calls: list[str] = []

    async def list_for_brand(self, brand_id: str) -> list[dict[str, Any]]:
        self.calls.append(brand_id)
        return list(self.by_brand.get(brand_id, []))


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


@pytest.mark.asyncio
async def test_gated_auto_create_then_inject(monkeypatch: pytest.MonkeyPatch) -> None:
    """★ flag ON + 신원 + (빈) BrandRepo + seeded BrandMemoryRepo → 자동생성 brand 로 주입 발화."""
    planning = _CapturingPlanning()
    _patch_pipeline(monkeypatch, planning)
    _set_injection_flag(monkeypatch, True)

    brand_repo = BrandRepo()  # 비어있음 — 자동 생성 유도.

    # 자동 생성될 brand id 를 미리 알 수 없으므로, "어떤 brand_id 로 조회되든" seed 반환.
    class _AnyBrandMemory:
        def __init__(self, rows: list[dict[str, Any]]) -> None:
            self.rows = rows
            self.calls: list[str] = []

        async def list_for_brand(self, brand_id: str) -> list[dict[str, Any]]:
            self.calls.append(brand_id)
            return list(self.rows)

    mem_repo = _AnyBrandMemory([
        {"entry_type": "preferred_tone", "content": "친근하고 담백한 톤"},
    ])

    result = await generate_plan(
        "test-plan-id", _make_plan_entry(), GenerateRequest(),
        auth_user_id="u-auto",
        brand_id=None,           # 명시 없음
        brands_resolver=None,    # resolver 없음 → get-or-create 경로
        brand_repo=brand_repo,
        brand_memory_repo=mem_repo,
    )

    assert isinstance(result, Envelope)
    # 1) 기본 브랜드가 자동 생성됨 (idempotent store).
    created_id = await brand_repo.get_default_brand_id("u-auto")
    assert created_id is not None
    assert len(brand_repo.store["u-auto"]) == 1
    # 2) brand_memory 가 자동 생성된 그 brand 로 조회됨 (PII 격리).
    assert mem_repo.calls == [created_id]
    # 3) 주입 발화 — planning user_input 앞에 구속 프리앰블 prepend.
    assert (planning.captured_user_input or "").startswith(BRAND_CONSTRAINT_PREAMBLE_HEADER)
    assert "- 톤: 친근하고 담백한 톤" in (planning.captured_user_input or "")
    assert "유튜브 쇼츠 만들기" in (planning.captured_user_input or "")


@pytest.mark.asyncio
async def test_gated_auto_create_idempotent_reuses_existing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """기존 brand 가 있으면 generate_plan 이 그 brand 로 조회 — 2번째 default 생성 0."""
    planning = _CapturingPlanning()
    _patch_pipeline(monkeypatch, planning)
    _set_injection_flag(monkeypatch, True)

    brand_repo = BrandRepo()
    pre_existing = await brand_repo.get_or_create_default("u-pre")  # 미리 1개

    mem_repo = _BrandKeyedMemoryRepo({
        pre_existing: [{"entry_type": "avoid_phrase", "content": "'최저가' 표현"}],
    })

    result = await generate_plan(
        "test-plan-id", _make_plan_entry(), GenerateRequest(),
        auth_user_id="u-pre", brand_id=None, brands_resolver=None,
        brand_repo=brand_repo, brand_memory_repo=mem_repo,
    )

    assert isinstance(result, Envelope)
    # 기존 brand 재사용 — store 는 여전히 1개 (no duplicate).
    assert len(brand_repo.store["u-pre"]) == 1
    assert mem_repo.calls == [pre_existing]
    assert "- 금지: '최저가' 표현" in (planning.captured_user_input or "")


# ─── 3. no surprise write — flag OFF / 익명 → BrandRepo 미호출, byte-identical ─


class _ForbiddenBrandRepo:
    """get_or_create_default / get_default_brand_id 호출 시 즉시 실패 (no surprise write 보장)."""

    async def get_or_create_default(self, *args: Any, **kwargs: Any) -> str:  # pragma: no cover
        raise AssertionError("BrandRepo.get_or_create_default must NOT be called (flag OFF/anon)")

    async def get_default_brand_id(self, *args: Any, **kwargs: Any) -> str:  # pragma: no cover
        raise AssertionError("BrandRepo.get_default_brand_id must NOT be called (flag OFF/anon)")


@pytest.mark.asyncio
async def test_flag_off_no_brand_created_byte_identical(monkeypatch: pytest.MonkeyPatch) -> None:
    """★ flag OFF(default) → BrandRepo 미호출, brand 0 생성, user_input byte-identical."""
    planning = _CapturingPlanning()
    _patch_pipeline(monkeypatch, planning)
    _set_injection_flag(monkeypatch, False)

    result = await generate_plan(
        "test-plan-id", _make_plan_entry(), GenerateRequest(),
        auth_user_id="u-1", brand_id=None, brands_resolver=None,
        brand_repo=_ForbiddenBrandRepo(),  # 호출되면 AssertionError.
    )

    assert isinstance(result, Envelope)
    assert planning.captured_user_input == "유튜브 쇼츠 만들기"


@pytest.mark.asyncio
async def test_anonymous_no_brand_created_byte_identical(monkeypatch: pytest.MonkeyPatch) -> None:
    """★ flag ON 이어도 익명(auth_user_id None) → BrandRepo 미호출, byte-identical."""
    planning = _CapturingPlanning()
    _patch_pipeline(monkeypatch, planning)
    _set_injection_flag(monkeypatch, True)

    result = await generate_plan(
        "test-plan-id", _make_plan_entry(), GenerateRequest(),
        auth_user_id=None, brand_id=None, brands_resolver=None,
        brand_repo=_ForbiddenBrandRepo(),  # 호출되면 AssertionError.
    )

    assert isinstance(result, Envelope)
    assert planning.captured_user_input == "유튜브 쇼츠 만들기"
