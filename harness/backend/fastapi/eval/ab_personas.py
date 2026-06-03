"""Phase 16 S1 — A/B 실험용 시뮬 PKM 페르소나 fixture.

A/B 실험(`ab_experiment.py`)의 Arm B(agent-grade)가 주입하는 **시뮬 PKM context pack** 을
제공한다. pack 형식은 PKM/RAG orchestrator 설계서 §7.4(`locked_preferences / personal_patterns /
brand_guide / series_format / trends / wiki_fallback`)를 따른다.

★★ 정직한 한계 (실험 기획안 §5.1 / 5.2):
  - 이들은 **시뮬(synthetic) 페르소나**이며 실 누적 PKM 데이터의 proxy 일 뿐이다 (over-optimistic
    위험 — 시뮬이 채점 케이스에 과적합되면 실제보다 좋게 나온다).
  - ★ over-fit guard: 본 페르소나는 **golden_set 채점 케이스와 분리**된다 — golden_set 의
    특정 입력에 맞춘 정답을 담지 않고, 일반적인 브랜드/시리즈 선호 패턴만 담는다.
  - PII-free / synthetic: 실 사용자·브랜드 데이터를 담지 않는다 (전부 가공).
  - deterministic: 동일 호출 시 동일 dict (random/now 미사용) — 측정 재현성.

용법:
  from backend.fastapi.eval.ab_personas import CAFE_PERSONA, FITNESS_PERSONA, ALL_PERSONAS
  pack = CAFE_PERSONA["pkm_pack"]   # ab_experiment.pkm_pack_to_rag_context(pack) 로 변환
"""

from __future__ import annotations

from typing import Any

# ─── 시뮬 페르소나 1: 카페 브랜드 (설계서 §7 예시 계열) ──────────────────
# 무인/소규모 카페 운영자. PKM/RAG 설계서 §7.1~§7.4 의 카페 페르소나를 시뮬 fixture 로
# 고정한다 (실 orchestrator 미구축 — 실험은 "주입의 효과"만 본다).

CAFE_PERSONA: dict[str, Any] = {
    "persona_id": "sim-cafe-01",
    "label": "소규모 카페 브랜드 운영자 (시뮬)",
    "pkm_pack": {
        "mode": "trend_viral_director",
        # personal_pkm 중 사용자 명시 잠금 항목 (user_locked — 랭킹 최우선, §6.2).
        "locked_preferences": [
            {
                "scope": "personal_pkm",
                "locked": True,
                "content": "과한 자막을 지양하고 손글씨 톤의 담백한 자막을 선호한다",
            },
        ],
        # personal_pkm 중 본인 과거 성공 패턴 (vector 검색 결과 proxy).
        "personal_patterns": [
            {
                "scope": "personal_pkm",
                "content": "질문형 hook 으로 첫 3초를 열고 클로즈업으로 이어가는 구성이 잘 먹혔다",
                "similarity": 0.82,
            },
            {
                "scope": "personal_pkm",
                "content": "음식·음료 클로즈업 b-roll 비중을 높였을 때 시청 지속이 길었다",
                "similarity": 0.74,
            },
        ],
        # brand_pkm (= 기존 brand_memory_entries 재사용) — 톤/금지어/선호 표현.
        "brand_guide": [
            {"scope": "brand_pkm", "entry_type": "preferred_tone", "content": "따뜻하고 솔직한 동네 가게 톤"},
            {"scope": "brand_pkm", "entry_type": "avoid_phrase", "content": "'최저가' 같은 가격 경쟁 표현은 쓰지 않는다"},
        ],
        # series_pkm — 시리즈 단위 포맷 일관성.
        "series_format": [
            {"scope": "series_pkm", "content": "오프닝 5초는 원두 로스팅 b-roll 로 고정하는 시리즈 포맷"},
        ],
        # trend_snapshot — freshness 가중 단기 트렌드 (요약/패턴만, 원문 0).
        "trends": [
            {"scope": "trend_snapshot", "topic": "무인매장 브이로그", "trend_stage": "peaking", "freshness_score": 0.78},
        ],
        # global_wiki (보조 fallback) — 익명화 공용 패턴.
        "wiki_fallback": [
            {"scope": "global_wiki", "content": "브이로그는 진정성과 연출의 균형이 중요하다", "access_scope": "public"},
        ],
    },
}


# ─── 시뮬 페르소나 2: 홈트레이닝 크리에이터 (과적합 분산용) ────────────────
# 페르소나 2개 권장 (실험 기획안 §8-2: 1개는 과적합 위험, 2개로 견고성↑). 카페와
# 다른 도메인/톤으로 작성해 페르소나 특성이 결과에 미치는 영향을 분리한다.

FITNESS_PERSONA: dict[str, Any] = {
    "persona_id": "sim-fitness-01",
    "label": "홈트레이닝 크리에이터 (시뮬)",
    "pkm_pack": {
        "mode": "trend_viral_director",
        "locked_preferences": [
            {
                "scope": "personal_pkm",
                "locked": True,
                "content": "운동 효과를 과장하거나 단기간 보장 표현을 절대 쓰지 않는다",
            },
        ],
        "personal_patterns": [
            {
                "scope": "personal_pkm",
                "content": "흔한 실수 1가지를 먼저 짚어주는 도입이 저장·공유로 이어졌다",
                "similarity": 0.80,
            },
            {
                "scope": "personal_pkm",
                "content": "동작을 측면·정면 2앵글로 보여줄 때 따라하기 쉽다는 피드백이 많았다",
                "similarity": 0.71,
            },
        ],
        "brand_guide": [
            {"scope": "brand_pkm", "entry_type": "preferred_tone", "content": "차분하고 신뢰감 있는 코치 톤"},
            {"scope": "brand_pkm", "entry_type": "avoid_phrase", "content": "'단숨에', '폭발적' 같은 과장 표현 금지"},
        ],
        "series_format": [
            {"scope": "series_pkm", "content": "마지막 10초는 한 줄 요약 자막 + 다음 영상 예고로 고정"},
        ],
        "trends": [
            {"scope": "trend_snapshot", "topic": "초보자 폼 교정 숏폼", "trend_stage": "emerging", "freshness_score": 0.85},
        ],
        "wiki_fallback": [
            {"scope": "global_wiki", "content": "운동 영상은 안전 주의 문구가 신뢰를 높인다", "access_scope": "public"},
        ],
    },
}


# 페르소나 2개 (실험 기획안 §8-2 default). 추가 페르소나는 이 list 에 append.
ALL_PERSONAS: tuple[dict[str, Any], ...] = (CAFE_PERSONA, FITNESS_PERSONA)
