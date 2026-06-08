"""Phase 8 Slice 2 — MOA Orchestrator (ADR-027) 단위 테스트.

`orchestration/moa_orchestrator.py::generate_plan` 직접 검증:
  - test_generate_plan_basic        : mock agents → Envelope 반환 (3-plan)
  - test_progress_sink_emits        : stage 순서 [intent, rag, planning, critic, complete]
  - test_null_progress_sink_noop    : NullProgressSink default 회귀 0 (Envelope 정상)
  - test_generate_plan_intent_blocked : INV-001 / 422 보존
  - test_generate_plan_intent_llm_failure : E-LLM-001 / 502 보존
  - test_generate_plan_planning_failure : E-LLM-001 / 502 보존
  - test_generate_plan_all_schema_fail : E-LLM-003 / 502 보존
  - test_plan_entry_mutation        : status="generated" + envelope 채워짐

★ behavior-preserving 게이트의 일부: 기존 e2e(test_plans/test_3_plan) 가
HTTP 경계 검증이라면, 본 파일은 orchestrator service layer 직접 검증.

monkeypatch 대상은 `backend.fastapi.routers.plans.*` — orchestrator 가 agent 호출을
router 모듈 namespace 로 call-time 해석하기 때문 (ADR-027, monkeypatch 보존).
"""

from __future__ import annotations

from typing import Any

import pytest
from fastapi.responses import JSONResponse

from backend.fastapi.config import get_settings
from backend.fastapi.db.types import PersistenceResult
from backend.fastapi.orchestration import NullProgressSink, generate_plan
from backend.fastapi.rag.types import RetrievalResult
from backend.fastapi.schemas.output import Envelope
from backend.fastapi.schemas.plans import GenerateRequest


# ─── helpers ──────────────────────────────────────────────────────────

_INTENT_OK: dict[str, Any] = {"intent_ok": True, "category": "video_planning"}
_INTENT_BLOCK: dict[str, Any] = {
    "intent_ok": False,
    "reason": "영상기획과 무관한 요청 (날씨 질의)",
}


def _make_plan_entry() -> dict[str, Any]:
    """generate_plan 이 받는 plan_entry (plans_start 가 만드는 형태)."""
    return {
        "plan_id": "test-plan-id",
        "status": "created",
        "created_at": "2026-05-30T00:00:00Z",
        "updated_at": "2026-05-30T00:00:00Z",
        "locale": "ko-KR",
        "initial_input": "유튜브 쇼츠 만들기",
        "wizard_data": {},
        "envelope": None,
    }


def _parallel_3_payload() -> list[dict[str, Any]]:
    """3 unique plans (narrative + informational + experiment)."""
    labels = ["narrative", "informational", "experiment"]
    out: list[dict[str, Any]] = []
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
        status="saved",
        project_id="fake-project-uuid",
        plan_candidate_ids=["fake-plan-candidate-uuid"],
        error_reason=None,
    )


def _rag_fallback(*args: Any, **kwargs: Any) -> RetrievalResult:
    return RetrievalResult(
        references=[], used_fallback=True, fallback_reason="pgvector_unreachable",
    )


@pytest.fixture
def patch_agents_ok(monkeypatch: pytest.MonkeyPatch) -> None:
    """정상 경로 — Intent allow + RAG fallback + 3-plan + Critic approve + DB save ok.

    orchestrator 가 routers.plans namespace 로 해석하므로 그 모듈을 patch 한다.
    """
    import copy

    async def fake_parallel(*args: Any, **kwargs: Any) -> list[dict[str, Any]]:
        return copy.deepcopy(_parallel_3_payload())

    monkeypatch.setattr("backend.fastapi.routers.plans.run_intent", lambda *a, **k: dict(_INTENT_OK))
    monkeypatch.setattr("backend.fastapi.routers.plans.run_rag_retrieval", _rag_fallback)
    monkeypatch.setattr("backend.fastapi.routers.plans.run_planning_parallel_3", fake_parallel)
    monkeypatch.setattr("backend.fastapi.routers.plans.run_critic", _critic_approve)
    monkeypatch.setattr("backend.fastapi.routers.plans.save_video_planning", _db_save_ok)


class RecordingSink:
    """ProgressSink — emit 된 stage 순서를 캡처."""

    def __init__(self) -> None:
        self.stages: list[str] = []
        self.steps: list[int | None] = []

    def emit(
        self,
        stage: str,
        *,
        step: int | None = None,
        message: str | None = None,
        **meta: Any,
    ) -> None:
        self.stages.append(stage)
        self.steps.append(step)


# ─── 1. 기본 동작 ─────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_generate_plan_basic(patch_agents_ok) -> None:
    """generate_plan → Envelope 반환 (3-plan + critic_evaluation 노출)."""
    plan_entry = _make_plan_entry()
    result = await generate_plan("test-plan-id", plan_entry, GenerateRequest())

    assert isinstance(result, Envelope)
    assert len(result.body.plan_candidates) == 3
    assert result.body.critic_evaluation is not None
    # validation.checks 순서 7개 보존
    check_names = [c.name for c in result.validation.checks]
    assert check_names == [
        "schema_envelope", "intent_filter", "rag_retrieval", "plan_count",
        "critic_evaluation", "db_persistence", "multi_model",
    ]


# ─── 2. ProgressSink emit 순서 ────────────────────────────────────────

@pytest.mark.asyncio
async def test_progress_sink_emits(patch_agents_ok) -> None:
    """custom RecordingSink 로 stage 순서 캡처 → 정확히 5단계 순서."""
    sink = RecordingSink()
    plan_entry = _make_plan_entry()
    result = await generate_plan(
        "test-plan-id", plan_entry, GenerateRequest(), progress=sink,
    )

    assert isinstance(result, Envelope)
    assert sink.stages == ["intent", "rag", "planning", "critic", "complete"]
    assert sink.steps == [1, 2, 3, 4, 4]


# ─── 3. NullProgressSink default 회귀 0 ──────────────────────────────

@pytest.mark.asyncio
async def test_null_progress_sink_noop(patch_agents_ok) -> None:
    """NullProgressSink default 시도 emit 호출돼도 no-op, Envelope 정상."""
    plan_entry = _make_plan_entry()
    # progress 인자 미지정 → NullProgressSink default
    result = await generate_plan("test-plan-id", plan_entry, GenerateRequest())
    assert isinstance(result, Envelope)
    # 명시적 NullProgressSink 도 동일 결과
    result2 = await generate_plan(
        "test-plan-id", _make_plan_entry(), GenerateRequest(),
        progress=NullProgressSink(),
    )
    assert isinstance(result2, Envelope)
    assert len(result2.body.plan_candidates) == 3


# ─── 4. Intent 차단 → 422 INV-001 ─────────────────────────────────────

@pytest.mark.asyncio
async def test_generate_plan_intent_blocked(monkeypatch: pytest.MonkeyPatch) -> None:
    """Intent 차단(intent_ok=False) → JSONResponse 422 + INV-001 보존."""
    monkeypatch.setattr(
        "backend.fastapi.routers.plans.run_intent", lambda *a, **k: dict(_INTENT_BLOCK),
    )
    result = await generate_plan("test-plan-id", _make_plan_entry(), GenerateRequest())

    assert isinstance(result, JSONResponse)
    assert result.status_code == 422
    import json

    body = json.loads(bytes(result.body))
    assert body["ok"] is False
    assert body["error"]["code"] == "INV-001"
    assert body["error"]["retry_allowed"] is False


# ─── 5. Intent LLM 호출 실패 → 502 E-LLM-001 ─────────────────────────

@pytest.mark.asyncio
async def test_generate_plan_intent_llm_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    """Intent LLM 호출 raise → 502 + E-LLM-001 보존."""

    def boom(*args: Any, **kwargs: Any) -> dict[str, Any]:
        raise RuntimeError("openai down")

    monkeypatch.setattr("backend.fastapi.routers.plans.run_intent", boom)
    result = await generate_plan("test-plan-id", _make_plan_entry(), GenerateRequest())

    assert isinstance(result, JSONResponse)
    assert result.status_code == 502
    import json

    body = json.loads(bytes(result.body))
    assert body["error"]["code"] == "E-LLM-001"


# ─── 6. Planning 실패 → 502 E-LLM-001 ────────────────────────────────

@pytest.mark.asyncio
async def test_generate_plan_planning_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    """3-plan parallel raise → 502 + E-LLM-001 보존."""

    async def boom(*args: Any, **kwargs: Any) -> list[dict[str, Any]]:
        raise RuntimeError("planning failed")

    monkeypatch.setattr("backend.fastapi.routers.plans.run_intent", lambda *a, **k: dict(_INTENT_OK))
    monkeypatch.setattr("backend.fastapi.routers.plans.run_rag_retrieval", _rag_fallback)
    monkeypatch.setattr("backend.fastapi.routers.plans.run_planning_parallel_3", boom)

    result = await generate_plan("test-plan-id", _make_plan_entry(), GenerateRequest())
    assert isinstance(result, JSONResponse)
    assert result.status_code == 502
    import json

    body = json.loads(bytes(result.body))
    assert body["error"]["code"] == "E-LLM-001"


# ─── 7. 모든 plan schema fail → 502 E-LLM-003 ────────────────────────

@pytest.mark.asyncio
async def test_generate_plan_all_schema_fail(monkeypatch: pytest.MonkeyPatch) -> None:
    """planning 이 비-dict 만 반환 → 모든 plan schema skip → E-LLM-003 보존."""

    async def non_dict(*args: Any, **kwargs: Any) -> list[Any]:
        # plan_raw 가 {} 가 되어도 Plan 은 graceful 생성됨 → 강제 실패 위해
        # planning_results 자체를 빈 list 로 반환 (plans_list 길이 0).
        return []

    monkeypatch.setattr("backend.fastapi.routers.plans.run_intent", lambda *a, **k: dict(_INTENT_OK))
    monkeypatch.setattr("backend.fastapi.routers.plans.run_rag_retrieval", _rag_fallback)
    monkeypatch.setattr("backend.fastapi.routers.plans.run_planning_parallel_3", non_dict)

    result = await generate_plan("test-plan-id", _make_plan_entry(), GenerateRequest())
    assert isinstance(result, JSONResponse)
    assert result.status_code == 502
    import json

    body = json.loads(bytes(result.body))
    assert body["error"]["code"] == "E-LLM-003"


# ─── 8. plan_entry mutation ──────────────────────────────────────────

@pytest.mark.asyncio
async def test_plan_entry_mutation(patch_agents_ok) -> None:
    """성공 시 plan_entry dict mutation — status="generated" + envelope 채워짐."""
    plan_entry = _make_plan_entry()
    assert plan_entry["status"] == "created"
    assert plan_entry["envelope"] is None

    result = await generate_plan("test-plan-id", plan_entry, GenerateRequest())

    assert isinstance(result, Envelope)
    assert plan_entry["status"] == "generated"
    assert plan_entry["envelope"] is not None
    assert len(plan_entry["envelope"]["body"]["plan_candidates"]) == 3


# ─── 9. Phase 11 B안 S2b-2b: multi_provider_plans_enabled gate ────────
# step-3 의 gated 분기 검증:
#   - flag ON  → plans_router.run_planning_multi_provider_3 사용 (run_planning_parallel_3 미호출)
#   - flag OFF → 기존 run_planning_parallel_3 사용 (multi_provider 미호출, 회귀 가드)
# ★ behavior-preserving: flag default False 이므로 기존 경로 100% 동일.
#   다중-provider 증거는 함수 내부 로깅으로만 관측 — Envelope 불변.

def _set_multi_provider_flag(monkeypatch: pytest.MonkeyPatch, enabled: bool) -> None:
    """settings.multi_provider_plans_enabled override (lru_cache 재생성).

    test_cross_validation_wiring._set_cross_flag 와 동일 패턴 — env override + cache_clear.
    """
    monkeypatch.setenv("MULTI_PROVIDER_PLANS_ENABLED", "true" if enabled else "false")
    get_settings.cache_clear()
    assert get_settings().multi_provider_plans_enabled is enabled


@pytest.mark.asyncio
async def test_multi_provider_flag_on_uses_multi_provider_fn(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """flag ON → run_planning_multi_provider_3 사용 + run_planning_parallel_3 미호출.

    multi_provider 함수가 3-plan 을 반환하고, 정상 Envelope(200, plan 3개) 반환.
    """
    import copy

    multi_calls: list[tuple[Any, ...]] = []

    async def fake_multi(*args: Any, **kwargs: Any) -> list[dict[str, Any]]:
        multi_calls.append((args, kwargs))
        return copy.deepcopy(_parallel_3_payload())

    async def parallel_must_not_run(*args: Any, **kwargs: Any) -> list[dict[str, Any]]:
        raise AssertionError("run_planning_parallel_3 must NOT be called when flag ON")

    monkeypatch.setattr("backend.fastapi.routers.plans.run_intent", lambda *a, **k: dict(_INTENT_OK))
    monkeypatch.setattr("backend.fastapi.routers.plans.run_rag_retrieval", _rag_fallback)
    monkeypatch.setattr("backend.fastapi.routers.plans.run_planning_multi_provider_3", fake_multi)
    monkeypatch.setattr("backend.fastapi.routers.plans.run_planning_parallel_3", parallel_must_not_run)
    monkeypatch.setattr("backend.fastapi.routers.plans.run_critic", _critic_approve)
    monkeypatch.setattr("backend.fastapi.routers.plans.save_video_planning", _db_save_ok)

    _set_multi_provider_flag(monkeypatch, True)

    result = await generate_plan("test-plan-id", _make_plan_entry(), GenerateRequest())

    assert isinstance(result, Envelope)
    assert len(result.body.plan_candidates) == 3
    # ★ multi_provider 함수가 정확히 1회 사용됨 (parallel 은 raise 로 가드).
    assert len(multi_calls) == 1
    # validation.checks 순서 7개 보존 (Envelope 불변).
    check_names = [c.name for c in result.validation.checks]
    assert check_names == [
        "schema_envelope", "intent_filter", "rag_retrieval", "plan_count",
        "critic_evaluation", "db_persistence", "multi_model",
    ]


@pytest.mark.asyncio
async def test_multi_provider_flag_off_uses_parallel_fn(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """flag OFF(명시) → 기존 run_planning_parallel_3 사용 + multi_provider 미호출 (회귀 가드)."""
    import copy

    parallel_calls: list[tuple[Any, ...]] = []
    multi_calls: list[tuple[Any, ...]] = []

    async def fake_parallel(*args: Any, **kwargs: Any) -> list[dict[str, Any]]:
        parallel_calls.append((args, kwargs))
        return copy.deepcopy(_parallel_3_payload())

    async def fake_multi(*args: Any, **kwargs: Any) -> list[dict[str, Any]]:
        multi_calls.append((args, kwargs))
        return copy.deepcopy(_parallel_3_payload())

    monkeypatch.setattr("backend.fastapi.routers.plans.run_intent", lambda *a, **k: dict(_INTENT_OK))
    monkeypatch.setattr("backend.fastapi.routers.plans.run_rag_retrieval", _rag_fallback)
    monkeypatch.setattr("backend.fastapi.routers.plans.run_planning_parallel_3", fake_parallel)
    monkeypatch.setattr("backend.fastapi.routers.plans.run_planning_multi_provider_3", fake_multi)
    monkeypatch.setattr("backend.fastapi.routers.plans.run_critic", _critic_approve)
    monkeypatch.setattr("backend.fastapi.routers.plans.save_video_planning", _db_save_ok)

    _set_multi_provider_flag(monkeypatch, False)

    result = await generate_plan("test-plan-id", _make_plan_entry(), GenerateRequest())

    assert isinstance(result, Envelope)
    assert len(result.body.plan_candidates) == 3
    # ★ 기존 경로만 사용 — parallel 1회, multi_provider 0회 (회귀 가드).
    assert len(parallel_calls) == 1
    assert multi_calls == []


# ─── 10. Phase 17 가-S1: 신원(auth_user_id/brand_id) plumbing ─────────
# generate_plan 에 optional 신원 인자가 도달·관측 가능한지 검증한다.
#   - 신원 有 → plan_entry 에 stash + 로깅 (관측). Envelope/3-plan 동작 불변.
#   - 신원 無(익명, default None) → 기존과 동일 (anon byte-identical, 회귀 0).
# ★ 본 슬라이스는 plumbing only — brand_memory 로드/주입(가-S2) 없음.


@pytest.mark.asyncio
async def test_generate_plan_threads_auth_user_id(
    patch_agents_ok, caplog: pytest.LogCaptureFixture,
) -> None:
    """auth_user_id 가 generate_plan 까지 도달 → plan_entry stash + 로깅으로 관측 가능."""
    import logging

    plan_entry = _make_plan_entry()
    with caplog.at_level(logging.INFO, logger="backend.fastapi.orchestration.moa_orchestrator"):
        result = await generate_plan(
            "test-plan-id", plan_entry, GenerateRequest(),
            auth_user_id="u-1", brand_id="b-9",
        )

    # 동작 불변 — 여전히 정상 Envelope 3-plan.
    assert isinstance(result, Envelope)
    assert len(result.body.plan_candidates) == 3
    # ★ 신원이 orchestrator 까지 도달해 stash 됨 (가-S2 read 지점).
    assert plan_entry["auth_user_id"] == "u-1"
    assert plan_entry["brand_id"] == "b-9"
    # ★ 관측 가능 — 로깅에 신원 노출 (anon 아님).
    assert "auth_user_id=u-1" in caplog.text
    assert "brand_id=b-9" in caplog.text


@pytest.mark.asyncio
async def test_generate_plan_anonymous_byte_identical(
    patch_agents_ok, caplog: pytest.LogCaptureFixture,
) -> None:
    """신원 미지정(default None) → 익명 경로. 동작 불변 + 로깅은 anon 표기.

    ★ behavior-preserving: 신원 인자 없이 호출 = 가-S1 이전과 동일 동작(회귀 0).
    """
    import logging

    plan_entry = _make_plan_entry()
    with caplog.at_level(logging.INFO, logger="backend.fastapi.orchestration.moa_orchestrator"):
        # 신원 인자 미지정 → auth_user_id=None, brand_id=None (default).
        result = await generate_plan("test-plan-id", plan_entry, GenerateRequest())

    assert isinstance(result, Envelope)
    assert len(result.body.plan_candidates) == 3
    # validation.checks 순서 7개 보존 (Envelope 불변 — anon byte-identical).
    check_names = [c.name for c in result.validation.checks]
    assert check_names == [
        "schema_envelope", "intent_filter", "rag_retrieval", "plan_count",
        "critic_evaluation", "db_persistence", "multi_model",
    ]
    # stash 는 None (익명).
    assert plan_entry["auth_user_id"] is None
    assert plan_entry["brand_id"] is None
    # 로깅은 anon 표기.
    assert "auth_user_id=anon" in caplog.text


# ─── 11. Phase 29 A — 멀티모달 레퍼런스 키워드 PKM (순서 불변: 영속 → 적재) ─────
# 라이브 검증으로 발견한 회귀 가드: pkm_entries.source_plan_id 는 plans.id 를 FK 참조하므로,
# A2(키워드 적재)는 반드시 _persist_plan_envelope(plans 행 생성) **이후** 실행돼야 한다.
# 영속 전 적재 시 모든 INSERT 가 FK(23503)로 전량 실패(silent) → 키워드 학습 0.
# 본 테스트는 (1) 적재가 영속 뒤에 일어나고 (2) source_plan_id=plan_id 로 전달되며
# (3) 4개 키워드가 모두 consolidate_entry 로 도달함을 DI seam(fake pkm_repo)으로 가드한다.


class _RecordingPkmRepo:
    """consolidate_entry / list_for_user 호출을 기록하는 fake PkmRepo (DI seam)."""

    def __init__(self, order: list[str]) -> None:
        self.order = order
        self.consolidated: list[tuple[str, str, str | None]] = []

    async def list_for_user(self, auth_user_id: str, *, scope: str = "personal") -> list[Any]:
        return []

    async def consolidate_entry(
        self, auth_user_id: str, entry_type: str, content: str, *,
        scope: str = "personal", confidence: float = 0.5, source_plan_id: str | None = None,
    ) -> tuple[str, str]:
        self.order.append("consolidate")
        self.consolidated.append((entry_type, content, source_plan_id))
        return ("inserted", content)


@pytest.mark.asyncio
async def test_reference_keywords_persisted_after_plan_row(
    patch_agents_ok, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A2 키워드 적재가 plans 행 영속 **이후** + source_plan_id=plan_id 로 일어남 (FK 회귀 가드)."""
    order: list[str] = []

    # 비전 분석 → 고정 키워드 4종 (실 LLM 0).
    fake_keywords = [
        {"entry_type": "preferred_tone", "content": "아늑하고 따뜻한 분위기"},
        {"entry_type": "preferred_phrase", "content": "손글씨 스타일의 진솔함"},
        {"entry_type": "avoid_phrase", "content": "화려한 광고, 네온 사용 지양"},
        {"entry_type": "success_pattern", "content": "자연스럽고 편안한 느낌의 영상 구성"},
    ]
    monkeypatch.setattr(
        "backend.fastapi.agents.vision_analyzer.analyze_references",
        lambda images, **k: {"summary": "따뜻한 카페 무드보드", "keywords": fake_keywords},
    )

    # 영속 시점 기록 + plans 행이 생겼다고 신호 (return True → source_plan_id=plan_id).
    async def fake_persist(*args: Any, **kwargs: Any) -> bool:
        order.append("persist")
        return True

    monkeypatch.setattr(
        "backend.fastapi.orchestration.moa_orchestrator._persist_plan_envelope", fake_persist,
    )

    # 개인 PKM 추출 게이트 ON (env + cache_clear, _set_multi_provider_flag 패턴).
    monkeypatch.setenv("PERSONAL_PKM_EXTRACT_ENABLED", "true")
    get_settings.cache_clear()
    try:
        repo = _RecordingPkmRepo(order)
        result = await generate_plan(
            "test-plan-id", _make_plan_entry(), GenerateRequest(),
            auth_user_id="u-7", images=["data:image/png;base64,AAAA"], pkm_repo=repo,
        )
    finally:
        get_settings.cache_clear()  # 다음 테스트를 위해 (복원된) env 로 재빌드.

    assert isinstance(result, Envelope)
    # (1) 순서 불변 — 영속이 먼저, 그 다음 적재 (FK 충족).
    assert "persist" in order and "consolidate" in order
    assert order.index("persist") < order.index("consolidate")
    # (2) 4개 키워드 전부 도달 + (3) source_plan_id=plan_id (provenance 보존).
    assert len(repo.consolidated) == 4
    assert {c[0] for c in repo.consolidated} == {
        "preferred_tone", "preferred_phrase", "avoid_phrase", "success_pattern",
    }
    assert all(src == "test-plan-id" for (_, _, src) in repo.consolidated)


@pytest.mark.asyncio
async def test_no_images_no_reference_keyword_calls(
    patch_agents_ok, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """images 미첨부 → 비전 분석/키워드 적재 0 (additive, 기존 경로 byte-identical)."""
    def _must_not_run(*args: Any, **kwargs: Any) -> dict[str, Any]:
        raise AssertionError("analyze_references must NOT be called without images")

    monkeypatch.setattr(
        "backend.fastapi.agents.vision_analyzer.analyze_references", _must_not_run,
    )
    monkeypatch.setenv("PERSONAL_PKM_EXTRACT_ENABLED", "true")
    get_settings.cache_clear()
    try:
        repo = _RecordingPkmRepo([])
        result = await generate_plan(
            "test-plan-id", _make_plan_entry(), GenerateRequest(),
            auth_user_id="u-7", pkm_repo=repo,  # images 미지정 → None
        )
    finally:
        get_settings.cache_clear()

    assert isinstance(result, Envelope)
    assert repo.consolidated == []
