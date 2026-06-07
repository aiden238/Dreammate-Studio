"""Phase 28 S2 — PKM 강화/정리 (consolidate_entry + decay_and_prune) 단위.

검증:
  - 유사 재등장 → 강화(confidence↑) + dedup(중복 0)  [반복 강화]
  - 노이즈(일반·무정보) → 저장 안 함                  [불필요 안 쌓임]
  - 약한 entry decay → floor 미만 prune               [불필요 제거]
  - user_locked / protect 대상 보호
"""

from backend.fastapi.db.repositories.pkm_repo import PkmRepo


async def test_consolidate_reinforces_similar_and_dedups():
    repo = PkmRepo(in_memory_store={})
    a1 = await repo.consolidate_entry("u1", "preferred_tone", "담백하고 솔직한 톤", confidence=0.9)
    assert a1 is not None and a1[0] == "inserted"
    conf0 = (await repo.list_for_user("u1"))[0]["confidence"]

    # 유사 재등장 → 강화 + dedup
    a2 = await repo.consolidate_entry("u1", "preferred_tone", "담백하고 솔직한 톤이 좋아요", confidence=0.9)
    assert a2 is not None and a2[0] == "reinforced"
    entries = await repo.list_for_user("u1")
    assert len(entries) == 1  # 중복 0
    assert entries[0]["confidence"] > conf0  # 강화


async def test_consolidate_filters_noise():
    repo = PkmRepo(in_memory_store={})
    r = await repo.consolidate_entry("u1", "success_pattern", "사용자가 반복 선호한 기획 패턴", confidence=0.9)
    assert r is None  # 노이즈 스킵
    r2 = await repo.consolidate_entry("u1", "preferred_phrase", "짧", confidence=0.9)  # 5자 미만
    assert r2 is None
    assert await repo.list_for_user("u1") == []


async def test_distinct_entries_not_merged():
    repo = PkmRepo(in_memory_store={})
    await repo.consolidate_entry("u1", "preferred_tone", "담백한 톤", confidence=0.9)
    await repo.consolidate_entry("u1", "avoid_phrase", "과장·최저가 표현 싫음", confidence=0.9)
    assert len(await repo.list_for_user("u1")) == 2  # 다른 의미 → 별도 유지


async def test_decay_and_prune_removes_weak_protects_locked():
    repo = PkmRepo(in_memory_store={})
    await repo.add_entry("u1", "preferred_phrase", "약한 선호 문구", confidence=0.31)   # 0.31*0.95<0.3 → prune
    await repo.add_entry("u1", "preferred_tone", "잠금 선호 톤", confidence=0.31, is_user_locked=True)
    await repo.add_entry("u1", "preferred_phrase", "강한 선호 문구", confidence=0.9)
    decayed, pruned = await repo.decay_and_prune("u1", protect=set())
    contents = {e["content"] for e in await repo.list_for_user("u1")}
    assert "약한 선호 문구" not in contents      # 약함 → 제거
    assert "잠금 선호 톤" in contents            # user_locked 보호
    assert "강한 선호 문구" in contents          # 강함 → 생존
    assert pruned == 1


async def test_decay_protects_touched_content():
    repo = PkmRepo(in_memory_store={})
    await repo.add_entry("u1", "preferred_tone", "이번에 강화된 선호", confidence=0.31)
    await repo.decay_and_prune("u1", protect={"이번에 강화된 선호"})
    contents = {e["content"] for e in await repo.list_for_user("u1")}
    assert "이번에 강화된 선호" in contents  # protect → decay/prune 제외
