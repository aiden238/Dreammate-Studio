"""Phase 13 Slice S3 — rich 출력 gated wiring 검증 (CC-013 후속).

acceptance 매핑:
  - S3-A1 (OFF byte-identical): rich_output_enabled=False(default) 면 /generate 와
    /plans/{id}/generate 응답에 rich 슬롯이 **없다** (model_dump_compact). LLM(mock) 이
    rich 키를 포함해 반환해도 OFF 면 응답에 절대 새지 않는다 → Phase 13 이전과 동일.
  - S3-A2 (ON rich): rich_output_enabled=True 면 응답 plan 에 rich 슬롯이 채워진다
    (hook_variants / target_audience / tone / shots / thumbnail / title_candidates /
    cta / references / length_variants + beat visual/dialogue/caption).
  - S3-A3 (프롬프트 gating): run_planning / _run_planning_single 가 OFF 면 compact
    SYSTEM_PROMPT, ON 이면 RICH_SYSTEM_PROMPT 를 사용한다.

★ 전부 mock — 실 LLM 호출 0, 실 키 불필요. config override 는 기존 관례
  (monkeypatch.setenv + get_settings.cache_clear) 를 따른다.
"""

from __future__ import annotations

import copy
from typing import Any

import pytest
from fastapi.testclient import TestClient

from backend.fastapi.agents import planning as planning_mod
from backend.fastapi.config import get_settings
from backend.fastapi.db.types import PersistenceResult
from backend.fastapi.main import app
from backend.fastapi.rag.types import RetrievalResult
from backend.fastapi.schemas.output import PLAN_RICH_FIELDS

# rich 슬롯 이름 (plan 9 + beat 3) — 응답에 새는지 검사용.
_PLAN_RICH = sorted(PLAN_RICH_FIELDS)
_BEAT_RICH = ["visual", "dialogue", "caption"]


# ─── helpers ──────────────────────────────────────────────────────────

def _set_rich_flag(monkeypatch: pytest.MonkeyPatch, enabled: bool) -> None:
    """settings.rich_output_enabled override (lru_cache 재생성)."""
    monkeypatch.setenv("RICH_OUTPUT_ENABLED", "true" if enabled else "false")
    get_settings.cache_clear()
    assert get_settings().rich_output_enabled is enabled


def _rich_plan_dict(label: str = "narrative") -> dict[str, Any]:
    """rich 키를 전부 포함한 plan dict (rich 프롬프트가 반환했을 법한 모양)."""
    return {
        "name": "리치 기획안",
        "concept": "rich 슬롯 전부 채운 콘셉트",
        "hook": "이 영상은 rich 게이트 테스트용 hook 예시입니다.",
        "flow": [
            {
                "beat_index": 0,
                "beat": "도입",
                "duration_sec": 3,
                "purpose": "관심",
                "visual": "클로즈업 + 빠른 컷",
                "dialogue": "안녕하세요",
                "caption": "도입 자막",
            },
            {
                "beat_index": 1,
                "beat": "전개",
                "duration_sec": 20,
                "purpose": "핵심",
            },
        ],
        "pros": "장점",
        "risks": "위험",
        "approach_label": label,
        "hook_variants": ["대안 후크 1", "대안 후크 2"],
        "target_audience": "자취 2~3년차 20대",
        "tone": "담백하고 솔직한",
        "shots": ["B-roll 냉장고", "타임랩스"],
        "thumbnail": "냉장고 비포/애프터 + 큰 문구",
        "title_candidates": ["제목 1", "제목 2", "제목 3"],
        "cta": "구독하고 다음 편 보기",
        "references": ["미니멀 자취 채널 유형"],
        "length_variants": ["30초 컷", "60초 컷"],
    }


def _critic_approve(plan: dict[str, Any], *args: Any, **kwargs: Any) -> dict[str, Any]:
    scores = {
        "intent_fit": 4, "target_clarity": 4, "hook_strength": 4, "message_clarity": 4,
        "structure": 4, "feasibility": 4, "brand_consistency": 5, "differentiation": 4,
    }
    return {
        "target_plan_id": str(plan.get("plan_id") or ""),
        "scores": scores,
        "reasons": {k: "-" for k in scores},
        "suggestions": {k: "-" for k in scores},
        "overall_score_avg": 4.0,
        "overall_verdict": "approve",
        "blocking_issues": [],
        "revise_round": 0,
    }


def _db_ok(**kwargs: Any) -> PersistenceResult:
    return PersistenceResult(
        status="saved", project_id="pid", plan_candidate_ids=["x"], error_reason=None,
    )


def _rag_fallback(*args: Any, **kwargs: Any) -> RetrievalResult:
    return RetrievalResult(references=[], used_fallback=True, fallback_reason="x")


# ─── fixtures: /generate (single-plan) mocks ──────────────────────────

@pytest.fixture
def patch_generate_rich(monkeypatch: pytest.MonkeyPatch) -> None:
    """routers.generate 경로 mock — Planning 이 rich 키 포함 plan 반환."""

    def fake_planning(*args: Any, **kwargs: Any) -> dict[str, Any]:
        return {"plan": copy.deepcopy(_rich_plan_dict())}

    monkeypatch.setattr("backend.fastapi.routers.generate.run_intent", lambda *a, **k: {"intent_ok": True, "category": "video_planning"})
    monkeypatch.setattr("backend.fastapi.routers.generate.run_rag_retrieval", _rag_fallback)
    monkeypatch.setattr("backend.fastapi.routers.generate.run_planning", fake_planning)
    monkeypatch.setattr("backend.fastapi.routers.generate.run_critic", _critic_approve)
    monkeypatch.setattr("backend.fastapi.routers.generate.save_video_planning", _db_ok)


# ─── fixtures: /plans (3-plan orchestrator) mocks ─────────────────────

@pytest.fixture
def patch_plans_rich(monkeypatch: pytest.MonkeyPatch) -> None:
    """routers.plans 경로 mock — 3-plan parallel 이 rich 키 포함 plan 반환."""

    async def fake_parallel(*args: Any, **kwargs: Any) -> list[dict[str, Any]]:
        labels = ["narrative", "informational", "experiment"]
        return [{"plan": copy.deepcopy(_rich_plan_dict(labels[i]))} for i in range(3)]

    monkeypatch.setattr("backend.fastapi.routers.plans.run_intent", lambda *a, **k: {"intent_ok": True, "category": "video_planning"})
    monkeypatch.setattr("backend.fastapi.routers.plans.run_rag_retrieval", _rag_fallback)
    monkeypatch.setattr("backend.fastapi.routers.plans.run_planning_parallel_3", fake_parallel)
    monkeypatch.setattr("backend.fastapi.routers.plans.run_critic", _critic_approve)
    monkeypatch.setattr("backend.fastapi.routers.plans.save_video_planning", _db_ok)


def _assert_no_rich(cand: dict[str, Any]) -> None:
    for key in _PLAN_RICH:
        assert key not in cand, f"OFF 응답에 rich 슬롯 '{key}' 가 새면 안 됨"
    for beat in cand["flow"]:
        for key in _BEAT_RICH:
            assert key not in beat, f"OFF 응답 beat 에 rich 슬롯 '{key}' 가 새면 안 됨"


def _assert_has_rich(cand: dict[str, Any]) -> None:
    for key in _PLAN_RICH:
        assert key in cand, f"ON 응답에 rich 슬롯 '{key}' 가 있어야 함"
    assert cand["hook_variants"] == ["대안 후크 1", "대안 후크 2"]
    assert cand["target_audience"] == "자취 2~3년차 20대"
    assert cand["tone"] == "담백하고 솔직한"
    beat0 = cand["flow"][0]
    assert beat0["visual"] == "클로즈업 + 빠른 컷"
    assert beat0["dialogue"] == "안녕하세요"
    assert beat0["caption"] == "도입 자막"


# ═══ 1. /generate (single plan) — OFF byte-identical ═══════════════════

def test_generate_off_excludes_rich(patch_generate_rich, monkeypatch: pytest.MonkeyPatch) -> None:
    """OFF(default): Planning mock 이 rich 키 반환해도 응답에 rich 슬롯 0 (compact)."""
    _set_rich_flag(monkeypatch, False)
    client = TestClient(app)
    resp = client.post("/api/v1/generate", json={"input": "쇼츠 만들기", "locale": "ko-KR"})
    assert resp.status_code == 200
    cand = resp.json()["body"]["plan_candidates"][0]
    _assert_no_rich(cand)
    # 기존 compact 키는 그대로 존재.
    for key in ("name", "concept", "hook", "flow", "pros", "risks", "approach_label", "rag_used"):
        assert key in cand


def test_generate_on_includes_rich(patch_generate_rich, monkeypatch: pytest.MonkeyPatch) -> None:
    """ON: rich 프롬프트 plan 의 rich 슬롯이 응답에 채워진다."""
    _set_rich_flag(monkeypatch, True)
    client = TestClient(app)
    resp = client.post("/api/v1/generate", json={"input": "쇼츠 만들기", "locale": "ko-KR"})
    assert resp.status_code == 200
    cand = resp.json()["body"]["plan_candidates"][0]
    _assert_has_rich(cand)


# ═══ 2. /plans/{id}/generate (3-plan) — OFF byte-identical ═════════════

def test_plans_off_excludes_rich(patch_plans_rich, monkeypatch: pytest.MonkeyPatch) -> None:
    """OFF(default): 3-plan mock 이 rich 키 반환해도 live POST 응답에 rich 슬롯 0."""
    _set_rich_flag(monkeypatch, False)
    client = TestClient(app)
    pid = client.post("/api/v1/plans/start", json={"input": "쇼츠", "locale": "ko-KR"}).json()["plan_id"]
    resp = client.post(f"/api/v1/plans/{pid}/generate", json={"use_rag": False})
    assert resp.status_code == 200
    cands = resp.json()["body"]["plan_candidates"]
    assert len(cands) == 3
    for cand in cands:
        _assert_no_rich(cand)
    # GET 경로(plan_store stored dict)도 동일하게 compact.
    got = client.get(f"/api/v1/plans/{pid}").json()
    for cand in got["envelope"]["body"]["plan_candidates"]:
        _assert_no_rich(cand)


def test_plans_on_includes_rich(patch_plans_rich, monkeypatch: pytest.MonkeyPatch) -> None:
    """ON: 3-plan rich 슬롯이 live POST + GET 응답에 채워진다."""
    _set_rich_flag(monkeypatch, True)
    client = TestClient(app)
    pid = client.post("/api/v1/plans/start", json={"input": "쇼츠", "locale": "ko-KR"}).json()["plan_id"]
    resp = client.post(f"/api/v1/plans/{pid}/generate", json={"use_rag": False})
    assert resp.status_code == 200
    cands = resp.json()["body"]["plan_candidates"]
    assert len(cands) == 3
    for cand in cands:
        _assert_has_rich(cand)
    # GET 경로도 rich 포함.
    got = client.get(f"/api/v1/plans/{pid}").json()
    for cand in got["envelope"]["body"]["plan_candidates"]:
        _assert_has_rich(cand)


# ═══ 3. 프롬프트 gating — RICH vs compact 분기 ═════════════════════════

def test_run_planning_uses_rich_prompt_when_on(monkeypatch: pytest.MonkeyPatch) -> None:
    """ON 이면 run_planning 이 RICH_SYSTEM_PROMPT 를 system content 로 사용."""
    _set_rich_flag(monkeypatch, True)
    captured: dict[str, Any] = {}

    class _FakeClient:
        class chat:  # noqa: N801
            class completions:  # noqa: N801
                @staticmethod
                def create(*args: Any, **kwargs: Any) -> Any:
                    captured["system"] = kwargs["messages"][0]["content"]

                    class _R:
                        choices = [type("C", (), {"message": type("M", (), {"content": '{"plan": {}}'})()})()]
                    return _R()

    planning_mod.run_planning("쇼츠", client=_FakeClient())  # type: ignore[arg-type]
    # rich 프롬프트의 고유 키워드 — compact 에는 없는 문구.
    assert "상세 영상기획 브리프" in captured["system"]
    assert "hook_variants" in captured["system"]


def test_run_planning_uses_compact_prompt_when_off(monkeypatch: pytest.MonkeyPatch) -> None:
    """OFF(default) 이면 run_planning 이 기존 compact SYSTEM_PROMPT 를 사용."""
    _set_rich_flag(monkeypatch, False)
    captured: dict[str, Any] = {}

    class _FakeClient:
        class chat:  # noqa: N801
            class completions:  # noqa: N801
                @staticmethod
                def create(*args: Any, **kwargs: Any) -> Any:
                    captured["system"] = kwargs["messages"][0]["content"]

                    class _R:
                        choices = [type("C", (), {"message": type("M", (), {"content": '{"plan": {}}'})()})()]
                    return _R()

    planning_mod.run_planning("쇼츠", client=_FakeClient())  # type: ignore[arg-type]
    assert "상세 영상기획 브리프" not in captured["system"]
    assert "hook_variants" not in captured["system"]


@pytest.mark.asyncio
async def test_run_planning_single_uses_rich_prompt_when_on(monkeypatch: pytest.MonkeyPatch) -> None:
    """ON 이면 _run_planning_single(parallel 슬롯) 이 rich hint 프롬프트 사용."""
    _set_rich_flag(monkeypatch, True)
    captured: dict[str, Any] = {}

    class _FakeClient:
        class chat:  # noqa: N801
            class completions:  # noqa: N801
                @staticmethod
                def create(*args: Any, **kwargs: Any) -> Any:
                    captured["system"] = kwargs["messages"][0]["content"]

                    class _R:
                        choices = [type("C", (), {"message": type("M", (), {"content": '{"plan": {}}'})()})()]
                    return _R()

    await planning_mod._run_planning_single(
        "쇼츠", model="gpt-4o-mini", approach_hint="narrative — 스토리텔링", client=_FakeClient(),  # type: ignore[arg-type]
    )
    assert "상세 영상기획 브리프" in captured["system"]
