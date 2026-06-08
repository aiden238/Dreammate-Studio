"""Phase 28 S3 — 나만의 컨셉 수렴 (concept surfacing) 테스트 (mock, CI-safe, LLM 0).

검증 축:
  1. synthesize_concept([]) → enabled=False 빈 결과 (엔트리 0 → 호출 0).
  2. synthesize_concept(entries, client=fake) → canned JSON 파싱 (concept/pillars/conflicts/based_on).
  3. 게이트: GET /me/concept flag OFF(default) → enabled=False + synthesize **미호출** (byte-identical).
  4. 게이트: flag ON + 익명 → enabled=False + synthesize 미호출.
  5. flag ON + authed + 시드 repo → synthesize 결과를 ConceptResponse 로 반환 (배선).

★ LLM 0 — 순수 함수는 fake client 주입, 라우터는 synthesize_concept 를 stub 으로 대체.
"""

from __future__ import annotations

import json
from types import SimpleNamespace
from typing import Any, Optional

import pytest

from backend.fastapi.agents import concept_synthesizer as cs
from backend.fastapi.db import PkmRepo
from backend.fastapi.routers import me as me_router


def _request_with_user(auth_user_id: Optional[str]) -> Any:
    user = {"user_id": auth_user_id} if auth_user_id else None
    return SimpleNamespace(state=SimpleNamespace(user=user))


class _FakeResp:
    def __init__(self, content: str) -> None:
        self.choices = [SimpleNamespace(message=SimpleNamespace(content=content))]


class _FakeClient:
    """OpenAI chat.completions.create 만 흉내 (canned content 반환)."""

    def __init__(self, content: str) -> None:
        self._content = content

    @property
    def chat(self) -> Any:
        return SimpleNamespace(
            completions=SimpleNamespace(create=lambda **kwargs: _FakeResp(self._content))
        )


# ─── 1. 순수 함수: 빈 입력 → 빈 결과 (LLM 미호출) ──────────────────────


def test_synthesize_empty_returns_disabled() -> None:
    out = cs.synthesize_concept([])
    assert out == {
        "enabled": False, "concept": "", "pillars": [], "conflicts": [], "based_on": 0,
    }


# ─── 2. 순수 함수: fake client → canned JSON 파싱 ─────────────────────


def test_synthesize_parses_canned(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        cs, "get_settings",
        lambda: SimpleNamespace(openai_api_key="k", openai_model_default="gpt-4o-mini"),
    )
    canned = json.dumps({
        "concept": "따뜻하면서 강렬한 컨셉",
        "pillars": [{"label": "아늑한 사이버펑크", "detail": "결합 톤"}],
        "conflicts": [{"a": "아늑함", "b": "고대비", "note": "조화 필요"}],
    })
    entries = [
        {"entry_type": "preferred_tone", "content": "아늑하고 따뜻한 분위기", "confidence": 0.95, "is_user_locked": True},
        {"entry_type": "preferred_tone", "content": "사이버펑크 에너지", "confidence": 0.9},
    ]
    out = cs.synthesize_concept(entries, client=_FakeClient(canned))
    assert out["enabled"] is True
    assert out["concept"] == "따뜻하면서 강렬한 컨셉"
    assert len(out["pillars"]) == 1 and out["pillars"][0]["label"] == "아늑한 사이버펑크"
    assert len(out["conflicts"]) == 1 and out["conflicts"][0]["a"] == "아늑함"
    assert out["based_on"] == 2


def test_synthesize_no_api_key_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    """key 없음 → client 주입돼도 합성 안 함 (graceful)."""
    monkeypatch.setattr(
        cs, "get_settings",
        lambda: SimpleNamespace(openai_api_key="", openai_model_default="gpt-4o-mini"),
    )
    out = cs.synthesize_concept(
        [{"entry_type": "preferred_tone", "content": "담백한 톤", "confidence": 0.9}],
        client=_FakeClient("{}"),
    )
    assert out["enabled"] is False


# ─── 3. 라우터 게이트: flag OFF(default) → synthesize 미호출 ───────────


@pytest.mark.asyncio
async def test_concept_route_gated_off(monkeypatch: pytest.MonkeyPatch) -> None:
    def _must_not_run(*a: Any, **k: Any) -> Any:
        raise AssertionError("synthesize_concept must NOT run when gate OFF")

    monkeypatch.setattr(me_router, "synthesize_concept", _must_not_run)
    monkeypatch.setattr(
        me_router, "_get_settings",
        lambda: SimpleNamespace(concept_surfacing_enabled=False),
    )
    resp = await me_router.get_concept(_request_with_user("user-A"))
    assert resp.enabled is False
    assert resp.based_on == 0


# ─── 4. 라우터 게이트: flag ON + 익명 → synthesize 미호출 ──────────────


@pytest.mark.asyncio
async def test_concept_route_anon(monkeypatch: pytest.MonkeyPatch) -> None:
    def _must_not_run(*a: Any, **k: Any) -> Any:
        raise AssertionError("synthesize_concept must NOT run for anon")

    monkeypatch.setattr(me_router, "synthesize_concept", _must_not_run)
    monkeypatch.setattr(
        me_router, "_get_settings",
        lambda: SimpleNamespace(concept_surfacing_enabled=True),
    )
    resp = await me_router.get_concept(_request_with_user(None))
    assert resp.enabled is False


# ─── 5. 라우터: flag ON + authed + 시드 repo → 합성 결과 반환 ──────────


@pytest.mark.asyncio
async def test_concept_route_on_authed(monkeypatch: pytest.MonkeyPatch) -> None:
    repo = PkmRepo()
    await repo.add_entry("user-A", "preferred_tone", "담백한 톤", confidence=0.9)
    await repo.add_entry("user-A", "avoid_phrase", "과장 표현", confidence=0.8)

    monkeypatch.setattr(me_router, "_pkm_repo", repo)
    monkeypatch.setattr(
        me_router, "_get_settings",
        lambda: SimpleNamespace(concept_surfacing_enabled=True),
    )
    captured: dict[str, Any] = {}

    def _stub(entries: list[dict[str, Any]]) -> dict[str, Any]:
        captured["n"] = len(entries)
        return {
            "enabled": True, "concept": "내 컨셉",
            "pillars": [{"label": "축", "detail": "d"}],
            "conflicts": [], "based_on": len(entries),
        }

    monkeypatch.setattr(me_router, "synthesize_concept", _stub)
    resp = await me_router.get_concept(_request_with_user("user-A"))
    assert resp.enabled is True
    assert resp.concept == "내 컨셉"
    assert resp.based_on == 2
    assert captured["n"] == 2  # 본인 personal PKM 2개가 합성기로 전달됨
