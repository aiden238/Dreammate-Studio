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

import json
import logging
from dataclasses import dataclass, field
from typing import Any, Sequence

from ..agents.critic import normalize_to_canonical, run_critic
from ..agents.planning import run_planning_parallel_3

logger = logging.getLogger(__name__)

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


# ══════════════════════════════════════════════════════════════════════
# Phase 16 S2 — 강한(binding) 주입 + 적합도(fit/adherence) 측정
# ══════════════════════════════════════════════════════════════════════
#
# ★ S1 결과(2026-06-04_phase-16-s1-ab.md)가 S2 를 낳았다:
#   (1) generic critic 은 **일반 품질**만 재므로 PKM 주입 효과가 flat(+0.013, 노이즈 내)이었고,
#   (2) PKM 을 rag_context 로 주입하면 planning._format_rag_context 가
#       "이 참고 자료는 ... 그대로 복제하지 말고" 프레이밍으로 렌더 → PKM 이 **비구속 참고**로
#       들어가 brand rules / locked preferences 가 희석됐다.
#
#   S2 는 둘 다 고친다:
#     A) build_constraint_preamble — pack 을 **구속(binding) 제약 프리앰블**로 만들어
#        user_input 앞에 prepend 한다 (rag_context 경로 ❌ → "복제하지 말고" 프레이밍 비적용).
#     B) score_fit — 객관 규칙(금지어 스캔) + LLM judge(0~1 fit) 로 **적합도**를 따로 잰다.
#        A arm 은 pack 을 못 받았으므로 fit 이 구조적으로 낮아야 정상 — 그 gap 이 진짜 B−A 신호다.
#
# ★★ 설계 불변 원칙 (S1 과 동일):
#   - production code 0 변경 (본 모듈은 eval/ additive 유틸 — 운영 경로 무변경).
#   - real-mode = opt-in: planning/critic/judge client 는 **주입**된다(테스트는 mock).
#     실 OpenAI client 주입은 opt-in 실측 배치만. ★ API 키는 .env 에만 두고 코드/commit/로그에
#     **절대** 평문으로 남기지 않는다 (judge prompt 도 키를 담지 않는다).

# 강한 주입 arm 이름 상수.
ARM_B_STRONG = "B_strong_inject"

# 제약 프리앰블 헤더 (구속 지시 — rag_context 의 "참고 자료" 와 의미가 정반대다).
CONSTRAINT_PREAMBLE_HEADER = "[기획 제약 — 반드시 반영]"

# pack section → 프리앰블 directive 라벨 매핑.
#   locked / tone / avoid 는 **구속**(반드시/금지), 나머지는 참고로 표기한다.
#   brand_guide 는 entry_type(preferred_tone / avoid_phrase)에 따라 분기하므로 별도 처리.
_PREAMBLE_LABELS: dict[str, str] = {
    "locked_preferences": "반드시 지킬 것",
    "series_format": "시리즈 포맷",
    "personal_patterns": "참고",
    "trends": "참고",
    "wiki_fallback": "참고",
}


def build_constraint_preamble(pack: dict[str, Any]) -> str:
    """PKM pack(설계서 §7.4) → **구속(binding) 제약 프리앰블** 문자열 (한국어, 결정적).

    rag_context 의 "참고 자료(그대로 복제하지 말고)" 프레이밍과 달리, 본 프리앰블은
    user_input 앞에 prepend 되는 **반드시 반영해야 할 지시**다. 그래서 brand rules /
    locked preferences 가 비구속 참고로 희석되지 않는다 (S1 §3~4 진단의 직접 처방).

    변환 규칙 (§6.2 우선순위 순서 — locked → personal → brand → series → trend → wiki):
      - locked_preferences      → "반드시 지킬 것: <content>"
      - brand_guide.preferred_tone → "톤: <content>"
      - brand_guide.avoid_phrase   → "금지: <content>"
      - series_format           → "시리즈 포맷: <content>"
      - personal_patterns/trends/wiki_fallback → "참고: <content/topic>"

    Args:
        pack: §7.4 형식 dict. 비어있거나 dict 가 아니거나 유효 directive 가 0개면 "" 반환 (graceful).

    Returns:
        헤더 1줄 + directive bullet("- ...") 들로 구성된 문자열. 유효 directive 0개면 "".
        동일 pack → 동일 출력 (random/now 미사용).
    """
    if not pack or not isinstance(pack, dict):
        return ""

    directives: list[str] = []
    for key, _label in _PACK_SECTIONS:
        entries = pack.get(key)
        if not isinstance(entries, list):
            continue
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            text = _entry_snippet(entry)
            if not text:
                continue
            if key == "brand_guide":
                etype = entry.get("entry_type")
                if etype == "preferred_tone":
                    prefix = "톤"
                elif etype == "avoid_phrase":
                    prefix = "금지"
                else:
                    prefix = "참고"
            else:
                prefix = _PREAMBLE_LABELS.get(key, "참고")
            directives.append(f"- {prefix}: {text}")

    if not directives:
        return ""

    return CONSTRAINT_PREAMBLE_HEADER + "\n" + "\n".join(directives)


def _collect_avoid_phrases(pack: dict[str, Any]) -> list[str]:
    """pack 의 brand_guide 중 entry_type == 'avoid_phrase' content 의 핵심 금지어를 추출한다.

    content 는 보통 문장 형태("'최저가' 같은 가격 경쟁 표현은 쓰지 않는다")이므로,
    작은따옴표('...') 안의 토큰을 우선 금지어로 뽑는다. 따옴표가 없으면 content 전체를
    fallback 금지 문자열로 쓴다 (객관 스캔 — deterministic, LLM 미사용).
    """
    out: list[str] = []
    entries = pack.get("brand_guide") if isinstance(pack, dict) else None
    if not isinstance(entries, list):
        return out
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        if entry.get("entry_type") != "avoid_phrase":
            continue
        content = entry.get("content")
        if not isinstance(content, str) or not content.strip():
            continue
        # 작은따옴표 안의 토큰 추출 (예: '최저가', '단숨에' → ["최저가", "단숨에"]).
        quoted = _extract_quoted(content)
        if quoted:
            out.extend(quoted)
        else:
            out.append(content.strip())
    # 중복 제거 (등장 순서 보존, deterministic).
    seen: set[str] = set()
    uniq: list[str] = []
    for p in out:
        if p not in seen:
            seen.add(p)
            uniq.append(p)
    return uniq


def _extract_quoted(text: str) -> list[str]:
    """작은따옴표(' 또는 ') 쌍 안의 토큰을 추출한다 (결정적, 정규식 미사용)."""
    out: list[str] = []
    # straight ' 와 typographic ' ' 둘 다 처리.
    for open_q, close_q in (("'", "'"), ("'", "'")):
        rest = text
        while True:
            i = rest.find(open_q)
            if i < 0:
                break
            j = rest.find(close_q, i + 1)
            if j < 0:
                break
            tok = rest[i + 1 : j].strip()
            if tok:
                out.append(tok)
            rest = rest[j + 1 :]
    return out


def _flatten_plan_text(plan_body: dict[str, Any]) -> str:
    """plan body 의 텍스트 필드를 1개 문자열로 평탄화한다 (금지어 스캔용).

    name/concept/hook/tone/cta/thumbnail/pros/risks 등 스칼라 텍스트 + flow beats +
    리스트형 필드(hook_variants/shots/title_candidates/references 등) + scene_breakdown 의
    텍스트를 재귀적으로 모은다. 키 이름은 제외하고 값만 모은다 (avoid_phrase 가 값에 등장하는지가 관심).
    """
    parts: list[str] = []

    def _walk(node: Any) -> None:
        if isinstance(node, str):
            if node.strip():
                parts.append(node)
        elif isinstance(node, dict):
            for v in node.values():
                _walk(v)
        elif isinstance(node, (list, tuple)):
            for v in node:
                _walk(v)
        # 숫자/None 은 무시 (금지어는 텍스트에만 등장).

    _walk(plan_body)
    return "\n".join(parts)


# judge 프롬프트 (LLM judge — fit 0~1). ★ pack 의 tone/avoid/locked/series 를 명시하고
#   plan 이 이를 얼마나 반영했는지 0~1 점수 + 근거를 JSON 으로 받는다 (real-mode 주입 client).
_FIT_JUDGE_SYSTEM_PROMPT = """당신은 영상기획안의 **개인화 적합도(fit)** 평가자이다.

주어진 브랜드/개인 선호(PKM)와 영상기획안(plan)을 비교해, 이 plan 이 선호를 얼마나
잘 반영했는지 0~1 점수로 채점한다. 다음 4가지를 각각 보고 종합한다:
  - 톤 준수      : preferred_tone 을 따르는가
  - 금지어 회피  : avoid_phrase 로 지정된 표현을 피했는가
  - 잠금 선호 준수: locked_preferences(반드시 지킬 것)를 지켰는가
  - 시리즈 포맷 반영: series_format 을 반영했는가

응답 형식 (JSON 1개 객체만, 자연어 머리말/꼬리말 금지):
{
  "fit_score": 0.0~1.0 사이 실수,
  "reasons": "각 항목별 근거 1~3줄"
}

fit_score 는 4항목을 종합한 0~1 실수다. 선호를 전혀 반영 못 했으면 0 쪽, 모두
충실히 반영했으면 1 쪽으로 준다.
"""

# avoid_phrase 위반(객관 규칙) 시 judge fit_score 에 적용하는 곱셈 페널티.
#   객관 위반은 judge 가 못 잡아도 fit 을 강제로 깎는다 (adherence 의 hard signal).
_AVOID_VIOLATION_PENALTY = 0.5


def score_fit(
    plan_body: dict[str, Any],
    pack: dict[str, Any],
    *,
    judge_client: Any,
    model: str | None = None,
) -> dict[str, Any]:
    """plan 1개의 PKM 적합도(fit/adherence)를 측정한다 — 객관 규칙 + LLM judge 결합.

    ★ S1 §4(a)의 처방: generic critic 이 못 보는 "이 브랜드/사용자에 맞는가(fit)"를 잰다.
    A arm 의 plan 은 받지 못한 pack 으로 채점되므로 fit 이 구조적으로 낮아야 정상이다.

    객관 파트 (deterministic, LLM 미사용):
      - plan 텍스트를 평탄화해 각 brand_guide avoid_phrase 토큰을 스캔.
      - 등장하면 adherence 위반 → avoid_clean=False + 위반 토큰 수집.

    LLM judge 파트 (real-mode, 주입 judge_client):
      - pack 의 tone/avoid/locked/series 와 plan 을 judge 에 주고 0~1 fit_score + reasons 요청.
      - 파싱 실패/무효 응답이면 judge_score=None (graceful).

    결합 (fit_0_1):
      - base = judge_score (judge 가 없으면 None).
      - avoid_clean=False 면 base × _AVOID_VIOLATION_PENALTY (객관 위반의 hard penalty).

    Args:
        plan_body: run_planning_parallel_3 envelope 의 plan body(dict).
        pack: §7.4 PKM pack (채점 기준).
        judge_client: judge LLM client (테스트 mock / opt-in 실 OpenAI). ★ 주입 전용.
        model: judge 모델 (None 이면 settings default — 호출자가 real-mode 에서 지정).

    Returns:
        {
          "fit_0_1": float | None,        # 결합 최종 fit (judge × 페널티)
          "judge_score": float | None,    # judge 원점수 (0~1)
          "avoid_clean": bool,            # 금지어 위반 없으면 True
          "avoid_violations": [str, ...], # 발견된 금지어 토큰
          "judge_reasons": str,           # judge 근거 (옵저버빌리티)
        }
    """
    # ── 객관 파트: 금지어 스캔 (deterministic) ──
    plan_text = _flatten_plan_text(plan_body if isinstance(plan_body, dict) else {})
    avoid_phrases = _collect_avoid_phrases(pack if isinstance(pack, dict) else {})
    violations = [p for p in avoid_phrases if p and p in plan_text]
    avoid_clean = not violations

    # ── judge 파트: LLM 0~1 fit ──
    judge_score, judge_reasons = _run_fit_judge(
        plan_body, pack, judge_client=judge_client, model=model
    )

    # ── 결합 ──
    if judge_score is None:
        fit_0_1: float | None = None
    else:
        fit_0_1 = judge_score
        if not avoid_clean:
            fit_0_1 = round(judge_score * _AVOID_VIOLATION_PENALTY, 6)

    return {
        "fit_0_1": fit_0_1,
        "judge_score": judge_score,
        "avoid_clean": avoid_clean,
        "avoid_violations": violations,
        "judge_reasons": judge_reasons,
    }


def _build_fit_judge_user_message(plan_body: dict[str, Any], pack: dict[str, Any]) -> str:
    """judge user 메시지 — pack 의 tone/avoid/locked/series 요약 + plan JSON (결정적)."""
    pack = pack if isinstance(pack, dict) else {}
    tone = [
        e.get("content", "")
        for e in (pack.get("brand_guide") or [])
        if isinstance(e, dict) and e.get("entry_type") == "preferred_tone"
    ]
    avoid = [
        e.get("content", "")
        for e in (pack.get("brand_guide") or [])
        if isinstance(e, dict) and e.get("entry_type") == "avoid_phrase"
    ]
    locked = [
        _entry_snippet(e)
        for e in (pack.get("locked_preferences") or [])
        if isinstance(e, dict)
    ]
    series = [
        _entry_snippet(e)
        for e in (pack.get("series_format") or [])
        if isinstance(e, dict)
    ]
    pref_lines = [
        "[브랜드/개인 선호 (PKM)]",
        "톤(preferred_tone): " + (" / ".join(t for t in tone if t) or "(없음)"),
        "금지(avoid_phrase): " + (" / ".join(a for a in avoid if a) or "(없음)"),
        "잠금(locked_preferences): " + (" / ".join(l for l in locked if l) or "(없음)"),
        "시리즈 포맷(series_format): " + (" / ".join(s for s in series if s) or "(없음)"),
    ]
    return (
        "\n".join(pref_lines)
        + "\n\n[평가 대상 plan]\n"
        + json.dumps(plan_body, ensure_ascii=False)
    )


def _run_fit_judge(
    plan_body: dict[str, Any],
    pack: dict[str, Any],
    *,
    judge_client: Any,
    model: str | None = None,
) -> tuple[float | None, str]:
    """LLM judge 호출 → (fit_score 0~1 | None, reasons str). 실패/무효면 (None, "") (graceful).

    judge_client.chat.completions.create 를 동기 호출한다 (run_critic 패턴과 동일 인터페이스 —
    테스트 mock / opt-in 실 OpenAI 둘 다 호환).
    """
    if judge_client is None:
        return None, ""
    _model = model or "gpt-4o"
    user_msg = _build_fit_judge_user_message(
        plan_body if isinstance(plan_body, dict) else {},
        pack if isinstance(pack, dict) else {},
    )
    try:
        response = judge_client.chat.completions.create(
            model=_model,
            messages=[
                {"role": "system", "content": _FIT_JUDGE_SYSTEM_PROMPT},
                {"role": "user", "content": user_msg},
            ],
            response_format={"type": "json_object"},
            temperature=0.2,  # 채점 일관성 (critic 과 동일 기조)
            max_tokens=600,
        )
        raw = response.choices[0].message.content or "{}"
        parsed = json.loads(raw)
    except Exception as e:  # noqa: BLE001 — judge 실패는 graceful None (측정 차단 금지)
        logger.warning("fit judge 호출/파싱 실패 — judge_score=None (%s)", e)
        return None, ""

    score = parsed.get("fit_score")
    reasons = parsed.get("reasons")
    reasons_str = reasons if isinstance(reasons, str) else ""
    if not isinstance(score, (int, float)) or isinstance(score, bool):
        return None, reasons_str
    return max(0.0, min(1.0, float(score))), reasons_str


# ─── S2 fit-aware arm 실행 ────────────────────────────────────────────

async def _run_arm_fit(
    planning_input: str,
    arm_name: str,
    pack: dict[str, Any],
    *,
    planning_client: Any,
    critic_client: Any,
    judge_client: Any,
    models: list[str] | None = None,
) -> dict[str, Any]:
    """한 arm 을 생성(3 plans)하고 generic(critic) + fit(score_fit) 둘 다 채점한다.

    ★ rag_context=[] 고정 (강한 주입은 planning_input 의 프리앰블로만 — rag_context "참고 자료"
    프레이밍 비사용). generic 은 run_critic→normalize_to_canonical(0~1), fit 은 score_fit(0~1).

    Returns:
        {
          "arm": arm_name,
          "avg_generic_0_1": float | None,
          "avg_fit_0_1": float | None,
          "per_plan": [{index, generic_0_1, verdict, fit_0_1, judge_score, avoid_clean, avoid_violations}...],
          "n_plans": int,
        }
    """
    plans = await run_planning_parallel_3(
        planning_input,
        rag_context=[],  # ★ 강한 주입은 preamble 로만 — rag_context 경로 미사용 (단일 변수 = preamble).
        models=models,
        client=planning_client,
    )

    per_plan: list[dict[str, Any]] = []
    generic_scores: list[float] = []
    fit_scores: list[float] = []

    for i, plan_envelope in enumerate(plans):
        plan_body = (
            plan_envelope.get("plan", {}) if isinstance(plan_envelope, dict) else {}
        )
        # generic 품질 (S1 critic 경로 재사용).
        verdict = run_critic(plan_body, client=critic_client)
        canonical = normalize_to_canonical(verdict)
        g01 = canonical.get("overall_score")
        if isinstance(g01, (int, float)):
            generic_scores.append(float(g01))

        # fit/adherence (S2 신규).
        fit = score_fit(plan_body, pack, judge_client=judge_client)
        f01 = fit["fit_0_1"]
        if isinstance(f01, (int, float)):
            fit_scores.append(float(f01))

        per_plan.append(
            {
                "index": i,
                "generic_0_1": float(g01) if isinstance(g01, (int, float)) else None,
                "verdict": verdict.get("overall_verdict"),
                "fit_0_1": float(f01) if isinstance(f01, (int, float)) else None,
                "judge_score": fit["judge_score"],
                "avoid_clean": fit["avoid_clean"],
                "avoid_violations": fit["avoid_violations"],
            }
        )

    return {
        "arm": arm_name,
        "avg_generic_0_1": _mean(generic_scores),
        "avg_fit_0_1": _mean(fit_scores),
        "per_plan": per_plan,
        "n_plans": len(plans),
    }


async def run_ab_pair_fit(
    base_input: str,
    pack: dict[str, Any],
    *,
    planning_client: Any,
    critic_client: Any,
    judge_client: Any,
    models: list[str] | None = None,
) -> dict[str, Any]:
    """동일 입력 × {A, B_strong} 쌍을 실행하고 generic·fit 양쪽 B−A delta 를 산출한다 (S2 핵심 산출물).

    ★ 단일 변수 통제 = **주입된 제약 프리앰블**:
      Arm A        : planning_input = base_input,                      rag_context=[]
      Arm B_strong : planning_input = preamble + "\\n\\n" + base_input, rag_context=[]
    그 외(models/critic/judge/output_mode)는 전부 동일. 두 arm 모두 rag_context=[] 이므로
    어느 쪽도 "참고 자료" 블록을 받지 않는다 → 차이는 오직 프리앰블 prefix 다.

    각 arm 의 plan 들을 generic(run_critic→0~1) + fit(score_fit→0~1) 으로 채점한다.
    A 의 plan 들은 받지 못한 pack 으로 fit 채점되므로 fit 이 구조적으로 낮아야 정상이며,
    B_strong 의 fit 이 높으면 (주입이 실제로 작동한다는) 진짜 B−A 신호다.

    Args:
        base_input: 동일 입력 (A/B 공유 — 프리앰블 제외).
        pack: §7.4 PKM pack (B 주입 + 양 arm fit 채점 기준).
        planning_client / critic_client / judge_client: 주입 client (테스트 mock / opt-in 실 OpenAI).
        models: 3개 모델 list (A/B 동일하게 공유).

    Returns:
        {
          "arm_a": <_run_arm_fit 결과>,
          "arm_b_strong": <_run_arm_fit 결과>,
          "delta_generic_0_1": b.avg_generic_0_1 - a.avg_generic_0_1 | None,
          "delta_fit_0_1": b.avg_fit_0_1 - a.avg_fit_0_1 | None,
          "preamble": <build_constraint_preamble(pack)>,  # 투명성 (옵저버빌리티)
        }

    ★ behavior-preserving: production code 0 변경. real-mode 는 opt-in(주입 client). 키는
      .env 에만 두고 코드/commit/로그에 평문으로 남기지 않는다 (judge prompt 포함).
    """
    preamble = build_constraint_preamble(pack)
    strong_input = (preamble + "\n\n" + base_input) if preamble else base_input

    a = await _run_arm_fit(
        base_input, ARM_A, pack,
        planning_client=planning_client,
        critic_client=critic_client,
        judge_client=judge_client,
        models=models,
    )
    b = await _run_arm_fit(
        strong_input, ARM_B_STRONG, pack,
        planning_client=planning_client,
        critic_client=critic_client,
        judge_client=judge_client,
        models=models,
    )

    return {
        "arm_a": a,
        "arm_b_strong": b,
        "delta_generic_0_1": _delta(b["avg_generic_0_1"], a["avg_generic_0_1"]),
        "delta_fit_0_1": _delta(b["avg_fit_0_1"], a["avg_fit_0_1"]),
        "preamble": preamble,
    }
