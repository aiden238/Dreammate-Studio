"""Phase 16 S1 — A/B 실험 하네스 (Simplest Slice).

동일 입력 1개에 대해 두 arm 을 생성·채점하여 **B−A 품질 숫자 1개**를 산출하고,
두 arm 이 **주입된 PKM 컨텍스트(rag_context) 한 가지만** 다름을 보장한다 (단일 변수 통제).

  Arm A (baseline)    : run_planning_parallel_3(input, rag_context=[])        → 3 plans
  Arm B (agent-grade) : run_planning_parallel_3(input, rag_context=<sim PKM>) → 3 plans

두 arm 모두 동일 입력 · 동일 models · 동일 output_mode · 동일 client. 각 plan 을 run_critic 으로
채점해 평균 → arm score. delta = B_score − A_score.

★★ 설계 불변 원칙 (실험 기획안 §2 / §7, Phase 16 acceptance A1/A6):
  - **production code 0 변경**: planning.py / critic.py / config.py / orchestrator / routers
    무수정. 본 모듈은 eval/ 영역의 **additive** 유틸이며, 운영 경로 behavior 를 바꾸지 않는다.
  - **single-variable control**: A 와 B 의 유일한 차이는 `rag_context`(주입 PKM pack) 이다.
    그 외(input/models/output_mode/temperature/프롬프트/critic)는 전부 동일하게 고정한다.
    Arm A(rag_context=[]) = 현재 운영 OFF 경로 byte-identical (A6).
  - **real-mode = opt-in**: planning_client / critic_client 는 **주입**된다(테스트는 mock 주입).
    opt-in 실측 배치만 실 OpenAI client 를 주입하며, 실 LLM 호출이 발생한다. ★ API 키는
    .env 에만 두고(이미 .gitignore) 코드/commit/로그에 **절대** 평문으로 남기지 않는다.

NOTE: 본 S1 은 "B−A 숫자 1개 + 통제 입증" capability 만 제공한다. 케이스 부분집합(S2) /
사람 blind(S3) / 종적 N={0,5,20}(S4) / 종합 판정(S5) 은 후속 슬라이스에서 확장한다.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Sequence

from ..agents.critic import normalize_to_canonical, run_critic
from ..agents.planning import run_planning_parallel_3

# arm 이름 상수 (리포트/키 일관성).
ARM_A = "A_baseline"
ARM_B = "B_agent_grade"


# ─── PKM pack → rag_context 변환 ──────────────────────────────────────

# 설계서 §7.4 context pack 의 의미 있는 entry scope 목록 (변환 대상).
# 각 키는 dict 의 list 이며, 각 dict 의 "content" 를 snippet 으로 쓴다.
# 순서는 §6.2 검색 우선순위(locked → personal → brand → series → trend → wiki)를 따른다.
_PACK_SECTIONS: tuple[tuple[str, str], ...] = (
    ("locked_preferences", "잠금 선호 (user_locked — 최우선)"),
    ("personal_patterns", "개인 성공 패턴"),
    ("brand_guide", "브랜드 가이드"),
    ("series_format", "시리즈 포맷"),
    ("trends", "트렌드 스냅샷"),
    ("wiki_fallback", "공용 위키 (보조)"),
)


def pkm_pack_to_rag_context(pack: dict[str, Any]) -> list[dict[str, str]]:
    """PKM context pack(설계서 §7.4) → run_planning 의 rag_context dict list.

    pack 의 각 의미 entry(locked_preferences / personal_patterns / brand_guide /
    series_format / trends / wiki_fallback)를 `{"title": ..., "snippet": ...}` 1개로 변환한다
    (planning._format_rag_context 가 읽는 키). entry 1개 = rag_context 1개 (deterministic).

    Args:
        pack: §7.4 형식 dict. 비어있거나 None-유사면 빈 list 반환 (graceful).

    Returns:
        [{"title": str, "snippet": str}, ...] — 변환 순서는 §6.2 검색 우선순위.
        content 가 없는 entry 는 trend topic / 기타 텍스트 필드를 snippet 으로 폴백.
    """
    if not pack or not isinstance(pack, dict):
        return []

    out: list[dict[str, str]] = []
    for key, label in _PACK_SECTIONS:
        entries = pack.get(key)
        if not isinstance(entries, list):
            continue
        for i, entry in enumerate(entries, start=1):
            if not isinstance(entry, dict):
                continue
            snippet = _entry_snippet(entry)
            if not snippet:
                continue
            # title 은 scope 라벨 + entry_type/stage 같은 보조 식별자로 구성 (결정적).
            qualifier = (
                entry.get("entry_type")
                or entry.get("trend_stage")
                or ("locked" if entry.get("locked") else "")
            )
            title = f"{label}[{i}]" + (f" — {qualifier}" if qualifier else "")
            out.append({"title": title, "snippet": snippet})
    return out


def _entry_snippet(entry: dict[str, Any]) -> str:
    """pack entry → snippet 텍스트. content 우선, 없으면 topic/summary 폴백."""
    for k in ("content", "topic", "summary"):
        v = entry.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return ""


# ─── arm spec ─────────────────────────────────────────────────────────

@dataclass(frozen=True)
class ArmSpec:
    """A/B 실험의 한 arm 명세 — name + 주입 rag_context.

    ★ rag_context 외 모든 생성 파라미터(input/models/output_mode/client)는 arm 밖에서
    공유된다 (단일 변수 통제). arm 은 "무엇을 주입하는가"만 다르다.
    """

    name: str
    rag_context: list[dict[str, str]] = field(default_factory=list)


def build_arms(sim_pkm_pack: dict[str, Any]) -> tuple[ArmSpec, ArmSpec]:
    """시뮬 PKM pack 으로부터 (arm_a, arm_b) 를 구성한다.

    arm_a.rag_context == []  (baseline = 현재 OFF 경로, A6 byte-identical)
    arm_b.rag_context == pkm_pack_to_rag_context(sim_pkm_pack)  (agent-grade)
    그 외 모든 것은 arm 밖에서 공유 — arm 간 유일한 차이는 rag_context 다 (A1 통제).

    Returns:
        (arm_a, arm_b).
    """
    return (
        ArmSpec(name=ARM_A, rag_context=[]),
        ArmSpec(name=ARM_B, rag_context=pkm_pack_to_rag_context(sim_pkm_pack)),
    )


# ─── arm 실행 (생성 + 채점) ───────────────────────────────────────────

async def run_arm(
    user_input: str,
    arm: ArmSpec,
    *,
    planning_client: Any,
    critic_client: Any,
    models: list[str] | None = None,
) -> dict[str, Any]:
    """한 arm 을 생성(3 plans)하고 critic 으로 채점해 arm score 를 산출한다.

    plan 3개를 run_planning_parallel_3(rag_context=arm.rag_context)로 생성하고, 각 plan body 를
    run_critic 으로 채점한다. critic 의 overall_score_avg(0~5)와 normalize_to_canonical 의
    overall_score(0~1)를 plan 별로 모아 평균낸다.

    Args:
        user_input: 동일 입력 (A/B 공유).
        arm: ArmSpec (name + rag_context).
        planning_client: planning LLM client (테스트 mock / opt-in 실 OpenAI). ★ 주입 전용.
        critic_client: critic LLM client (테스트 mock / opt-in 실 OpenAI). ★ 주입 전용.
        models: 3개 모델 list (A/B 공유 — None 이면 settings default; arm 간 동일하게 넘겨야 통제 유지).

    Returns:
        {
          "arm": name,
          "avg_0_5": float | None,   # plan 별 overall_score_avg(0~5) 평균
          "avg_0_1": float | None,   # plan 별 canonical overall_score(0~1) 평균
          "per_plan": [{"index", "score_0_5", "score_0_1", "verdict"}...],
          "n_plans": int,
        }
        채점 가능한 plan 이 0개면 avg_* 는 None.
    """
    plans = await run_planning_parallel_3(
        user_input,
        rag_context=arm.rag_context,
        models=models,
        client=planning_client,
    )

    per_plan: list[dict[str, Any]] = []
    scores_0_5: list[float] = []
    scores_0_1: list[float] = []

    for i, plan_envelope in enumerate(plans):
        # run_planning_parallel_3 는 {"plan": {...}} envelope 를 반환 — critic 은 plan body 를 받는다.
        plan_body = (
            plan_envelope.get("plan", {})
            if isinstance(plan_envelope, dict)
            else {}
        )
        verdict = run_critic(plan_body, client=critic_client)
        canonical = normalize_to_canonical(verdict)

        s05 = verdict.get("overall_score_avg")
        s01 = canonical.get("overall_score")
        if isinstance(s05, (int, float)):
            scores_0_5.append(float(s05))
        if isinstance(s01, (int, float)):
            scores_0_1.append(float(s01))

        per_plan.append(
            {
                "index": i,
                "score_0_5": float(s05) if isinstance(s05, (int, float)) else None,
                "score_0_1": float(s01) if isinstance(s01, (int, float)) else None,
                "verdict": verdict.get("overall_verdict"),
            }
        )

    return {
        "arm": arm.name,
        "avg_0_5": _mean(scores_0_5),
        "avg_0_1": _mean(scores_0_1),
        "per_plan": per_plan,
        "n_plans": len(plans),
    }


async def run_ab_pair(
    user_input: str,
    sim_pkm_pack: dict[str, Any],
    *,
    planning_client: Any,
    critic_client: Any,
    models: list[str] | None = None,
) -> dict[str, Any]:
    """동일 입력 × {A, B} 쌍을 실행하고 B−A delta 를 산출한다 (S1 핵심 산출물).

    A/B 는 build_arms 로 구성되어 rag_context 한 가지만 다르고, 동일 input/models/client 를
    공유한다 (단일 변수 통제). 두 arm 을 run_arm 으로 채점 후 delta = B − A.

    Args:
        user_input: 동일 입력 (A/B 공유).
        sim_pkm_pack: 시뮬 PKM context pack (ab_personas 의 persona["pkm_pack"]).
        planning_client / critic_client: 주입 client (테스트 mock / opt-in 실 OpenAI).
        models: 3개 모델 list (A/B 동일하게 공유).

    Returns:
        {
          "arm_a": <run_arm 결과>,
          "arm_b": <run_arm 결과>,
          "delta_0_1": b.avg_0_1 - a.avg_0_1 | None,
          "delta_0_5": b.avg_0_5 - a.avg_0_5 | None,
        }
    """
    arm_a, arm_b = build_arms(sim_pkm_pack)

    a = await run_arm(
        user_input, arm_a,
        planning_client=planning_client, critic_client=critic_client, models=models,
    )
    b = await run_arm(
        user_input, arm_b,
        planning_client=planning_client, critic_client=critic_client, models=models,
    )

    return {
        "arm_a": a,
        "arm_b": b,
        "delta_0_1": _delta(b["avg_0_1"], a["avg_0_1"]),
        "delta_0_5": _delta(b["avg_0_5"], a["avg_0_5"]),
    }


# ─── 내부 헬퍼 ────────────────────────────────────────────────────────

def _mean(values: Sequence[float]) -> float | None:
    """빈 시퀀스면 None (채점 가능한 plan 0개 graceful)."""
    if not values:
        return None
    return round(sum(values) / len(values), 6)


def _delta(b: float | None, a: float | None) -> float | None:
    """B − A. 둘 중 하나라도 None 이면 None."""
    if b is None or a is None:
        return None
    return round(b - a, 6)
