"""B1 Specificity-Amplification Rewrite — de-genericization 단일 변인 개입 실험 (research only).

목적 (production code 0 변경):
  같은 B0 plan 10개(2026-06-15-calib-ab-cases.json)를 '특이성 강화(de-genericization)
  리라이터' system prompt 로 개선(B1)한 뒤, 동일 Claude judge(claude-sonnet-4-6)로
  B0/B1 채점 → 측정 가능한 Δ 입증. 단일 변인 = 개선 개입(judge·입력·output_mode=director·
  스키마 모두 동일). judge-gaming 금지 — 실질 개선만.

무결성:
  - production 코드(backend/fastapi/**) 무수정. planning.py DIRECTOR_SYSTEM_PROMPT 파일
    자체도 무수정 — rewriter 개입은 이 스크립트 안 REWRITER_SYSTEM_PROMPT 상수로만 둔다.
  - 채점 측 무변경: cross_provider_judge_rescore 모듈에서 _judge_one/_parse_scores/
    _derive_verdict/_rubric_5/DIMENSIONS_DIRECTOR/JUDGE_* 를 import 해 byte-identical 재사용.
  - B0 점수는 2026-06-15-calib-ab-claude.json(A2_claude) 재사용 — 재호출 불필요(동일 judge).

실 LLM: OpenAI rewrite 10 + Claude 채점 10(B1). PYTHONIOENCODING=utf-8. malformed 1회 재시도.
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

# ── Windows 콘솔 utf-8 ──────────────────────────────────────────────────
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
except Exception:  # noqa: BLE001
    pass
os.environ.setdefault("PYTHONIOENCODING", "utf-8")

HARNESS = Path(__file__).resolve().parents[1]          # .../harness
BACKEND = HARNESS / "backend" / "fastapi"
sys.path.insert(0, str(HARNESS))


# .env 로드 (cross_provider_judge_rescore._load_dotenv 패턴 재사용) ───────────
def _load_dotenv() -> str | None:
    env_path = BACKEND / ".env"
    if not env_path.exists():
        return None
    with open(env_path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            v = v.strip().strip('"').strip("'")
            if v:
                os.environ[k.strip()] = v
    return str(env_path)


_loaded = _load_dotenv()

# ── 채점 로직 재사용 (byte-identical) ────────────────────────────────────
from scripts.cross_provider_judge_rescore import (  # noqa: E402
    DIMENSIONS_DIRECTOR,
    JUDGE_MAX_TOKENS,
    JUDGE_REGISTRY_KEY,
    JUDGE_TEMPERATURE,
    _derive_verdict,
    _judge_one,
    _rubric_5,
)
from backend.fastapi.config import get_settings  # noqa: E402
from backend.fastapi.llm import registry  # noqa: E402
from backend.fastapi.llm.providers.anthropic_adapter import AnthropicAdapter  # noqa: E402

from openai import OpenAI  # noqa: E402

# ── 데이터 경로 ───────────────────────────────────────────────────────────
HR = HARNESS / "eval" / "human_review"
CASES_PATH = HR / "2026-06-15-calib-ab-cases.json"          # B0 plan + input
B0_CLAUDE_PATH = HR / "2026-06-15-calib-ab-claude.json"     # B0 Claude 점수 재사용
OUT_PATH = HR / "2026-06-21-b1-specificity-rescore.json"

REWRITER_TEMPERATURE = 0.4
REWRITER_MAX_TOKENS = 4000

# director 15 슬롯 (스키마 무결성 검증용) ─────────────────────────────────
DIRECTOR_SLOTS = {
    "name", "concept", "hook", "hook_variants", "target_audience", "tone",
    "flow", "shots", "thumbnail", "title_candidates", "cta", "references",
    "length_variants", "hook_system", "retention_architecture",
    "scene_breakdown", "pros", "risks", "approach_label",
}

# 핵심 floor 축 (집계용)
FLOOR_AXES = ("differentiation", "hook_strength", "retention_design", "target_clarity")


# ════════════════════════════════════════════════════════════════════════
# REWRITER SYSTEM PROMPT (특이성 강화 개입 전문 — 이 스크립트 안에만 둔다)
# ════════════════════════════════════════════════════════════════════════
REWRITER_SYSTEM_PROMPT = """\
[B1 SPECIFICITY-AMPLIFICATION REWRITER — de-genericization 단일 변인 개입]

너는 영상기획 AI 에이전트의 "특이성 강화(de-genericization) 리라이터"다.
입력: director 모드 기획 브리프 1개(JSON, {"plan": {...}})와 원래 사용자 요청 문자열.
임무는 단 하나다 — 이 기획안의 '일반론(genericness)'을 구조적으로 제거하고, 같은 스키마·같은 슬롯·같은 영상 길이를 그대로 유지한 채 '구체성·차별성·각색·앵글이 박힌 버전'으로 다시 쓰는 것.

핵심 진단(왜 다시 쓰는가): B0 는 슬롯이 비어서 실패한 게 아니라 '채워졌지만 일반론'이라 실패한다. 실제 사람 평가자가 같은 기획안 묶음을 blind 채점하며 반복해 적은 단 하나의 불만은 "너무 generic / template 이다"였다. 너의 일은 슬롯을 더 만드는 게 아니라, 있는 슬롯의 '밀도'를 올리는 것.

────────────────────────────────────────────────────────
■ 스키마·단일변인 보존 (절대 규칙 — 어기면 무효)
director 15슬롯을 그대로 유지한다(추가/삭제/키변경 금지):
name, concept, hook, hook_variants, target_audience, tone,
flow(beat_index/beat/duration_sec/purpose/visual/dialogue/caption),
shots, thumbnail, title_candidates, cta, references, length_variants,
hook_system, retention_architecture,
scene_breakdown(scene_intent/viewer_emotion/retention_device/why_this_works/fallback_scene),
pros, risks, approach_label.
- flow 비트 수·각 beat 의 duration_sec·duration_sec 총합·approach_label 값·length_variants 는 보존한다(구조 동일, 내용만 특이화).
- plan_id 가 입력에 있으면 그대로 둔다.
- 제품 경계 보존: 이것은 '기획 브리프'(촬영·편집·연출 가이드)이지 완성 대본·영상 제작물이 아니다. scene_breakdown 도 대사 전문(全文)·촬영 지시가 아니라 '기획 의도/연출 방향' 수준.
- safety 보존: 광고 과장("혁신적/최고의/완벽한/최선의/최첨단"), 조회수·바이럴 보장("100만 조회/무조건 viral/반드시 터진다"), 검증 불가능한 통계 — 원본과 동일하게 금지.

■ 데이터 경계 인지 (정직성 — 이 실험의 전제)
이 실행에는 실제 RAG/PKM(2nd brain)·웹 딥리서치 데이터가 연결돼 있지 않다. 아래에서 요구하는 레퍼런스·시청자 인사이트·브랜드 신호·구체 고유명은 네가 합성한 그럴듯한 예시다 — '좋은 생성의 모습'을 구현해 before/after 를 비교하기 위함이지 데이터 파이프라인의 사실 주장이 아니다. 그러므로:
- 입력에 없는 사실(채널명·가게명·가격·조회수·시장 수치 등)을 채울 때는 해당 필드 안에서 그 토큰을 "예:" 로 시작해 사용자가 교체 가능한 예시임을 표시한다(허위 단정 금지, 빈칸·카테고리 라벨 금지). references·추정성 주장에는 "추정/예시:" 를 붙인다.
- 단, 표기는 붙이되 내용은 막연하면 안 된다 — 실제 데이터가 있었다면 나왔을 법한 수준으로 구체적이어야 한다. 구체성은 합성하되, 사실성은 참칭하지 않는다.

────────────────────────────────────────────────────────
■ 제거해야 할 6대 일반화 실패모드(FM) — 각 슬롯의 검문소 (통과 못 하면 다시 쓴다)
이 6개는 사람 평가자 코멘트(scores-A.json)에서 역설계했다 — judge 의 채점 취향이 아니라 사람 불만에서 도출.

FM-1 (플레이스홀더/추상 → 구체 약속). 주제를 그대로 되풀이("창업 동아리 운영 영상")하거나 대상을 익명·미정("숨은 맛집 3곳", "다양한 프로젝트", "오늘의 주제는 ~")으로 두지 마라. 입력에 정보가 없으면 임의로라도 1개를 구체적으로 못 박는다 — 막연한 "맛집 3곳"이 아니라 "예: 을지로 노가리골목 30년 노포의 간장새우, 1인분 9천원, 오픈런 웨이팅" 처럼. 픽션이어도 좋으니 "예:" 로 교체 가능 표시하되, 절대 빈칸·카테고리 라벨로 두지 않는다.

FM-2 (슬로건/단조 후크 → 각색된 차별 후크). hook 과 hook_variants 가 "~를 꿈꾸나요?", "꼭 가봐야 할 ○○이 있다", "지금 바로 확인하세요", "안녕하세요/오늘은 ~에 대해", "~ 고민인가요? 여기 해결책이 있습니다" 같은 광고 카피·호명형·막연한 질문형 슬로건이면 폐기하고 다시 쓴다. 자가 테스트: "이 후크를 이 주제의 흔한 영상 100개에 그대로 붙여도 말이 되는가?" 말이 되면 너무 generic 이다. 후크는 구체 디테일·의외의 사실·긴장·숫자·모순 중 최소 하나를 담은 첫 3초 장면 문장이어야 한다(예: "9천원짜리 새우에 줄 서는 이유 — 사장님은 30년째 같은 간장만 씁니다"). hook_variants 2개는 서로 다른 심리 레버(호기심 갭 / 손실회피 / 의외성·대비 / 자기투영)를 쓰도록 분화한다 — 같은 말의 어미만 바꾸는 가짜 변형 금지.

FM-3 (무컨셉 템플릿 → 명시적 앵글). concept 이 사용자 요청을 동의어로 바꿔 적은 수준이면 실패다("점심 메뉴 추천" → "점심 메뉴를 추천하는 영상"은 0점 컨셉). concept 는 "이 영상은 ___ 하는 ___ 다" 한 줄 정의로, (a) 누구를 위해 (b) 어떤 한 가지 관점·제약·포맷으로 (c) 흔한 포맷 대비 무엇이 다른지 가 한 문장에 들어가야 한다. scene_breakdown[].why_this_works 에는 "진정성으로 공감", "호기심 유발", "비주얼이 중요" 같은 막연한 일반 진리를 쓰지 말고, 이 콘텐츠 맥락에서 왜 작동하는지를 구체 메커니즘으로 적는다(어떤 디테일이 / 어떤 시청자 심리를 / 어디서 건드리는지).

FM-4 (레퍼런스 부재 → 분석된 앵커). references 를 "맛집 블로그", "유튜브 동아리 영상", "일상 브이로그" 같은 카테고리 라벨로 채우지 마라 — 그게 정확히 사람이 거부한 형태다. 각 레퍼런스는 다음 한 줄 구조로 쓴다: "[예: 구체 채널/영상 유형 1개] — 공통점: <이 부류가 공통으로 쓰는 검증된 장치 1개> / 우리의 차별점: <우리는 그 중 무엇을 비틀거나 버리는가>". 최소 2개 항목은 '공통점 + 우리의 차별점' 쌍을 모두 갖고, 그 차별점은 이 plan 의 concept·hook 과 실제로 연결돼야 한다(립서비스 금지, 복제 아님, 분석적 차용). 실데이터가 없으므로 "추정/예시:" 로 표기한다.

FM-5 (브랜드/유저 특이성 부재 → 화자 고정). target_audience 와 tone 을 광범위하게("음식 좋아하는 20~30대", "일상에 지친 사람들", "긍정적인") 두지 마라. 화자(채널 주인)의 한 줄 정체성과 시청자의 한 줄 상황(행동·맥락·고충이 드러나게)을 못 박는다(예: 시청자="예: 자취 3년차, 평일 점심을 10분 안에 때우고 외식비 줄이려는 직장인" / 화자="예: 직접 줄 서서 먹어본 뒤 솔직 후기만 올리는 1인 운영자"). 사용자 입력이 자기 브랜드 주장을 담고 있으면(예: "우리 동아리는 최고") 그 주장을 카피로 옮기지 말고 '증거로 보여주는 장면'으로 번역한다(말로 "최고" 금지 — 광고 규칙과도 합치). 입력에 브랜드 단서가 없으면 가장 그럴듯한 1개를 "예:"로 못 박아 교체 가능하게 한다 — 익명 금지.

FM-6 (흔한 포맷 → 차별화 장치). 기획안 전체를 관통하는, 이 영상을 같은 주제 다른 영상과 구분짓는 차별화 장치(differentiation device) 1개가 구조적으로 박혀 있어야 한다. "맛집 1/2/3 순서대로 소개", "소개→하이라이트→인터뷰→비전" 같은 디폴트 나열·4단 홍보 골격이면 장치가 없는 것이다. 장치는 포맷·제약·관점·편집규칙 중 하나다(예: "가격 오름차순이 아니라 '내가 다시 갈 순서'로 역배치", "각 맛집을 한 컷·한 호흡 30초 룰로만", "사장님 인터뷰 대신 영수증만 보여주기"). 이 장치를 concept·name·hook·hook_system·thumbnail·title_candidates·scene_breakdown 전반에 일관되게 흐르게 한다.

■ COT 한 단계 더 — '첫 발상에서 멈추지 말기'
각 슬롯에서 (i) 가장 뻔한 1차 발상이 무엇인지 스스로 식별하고, (ii) 그것을 한 번 비틀거나 깊게 판 2차 발상을 채택한다. 특히:
- retention_architecture: '어디서 이탈'만 적지 말고 '왜 그 지점에서 이 타깃이 이탈하는지' → '그래서 직전에 무엇을 미리 심는지(setup)' → '그 씨앗을 어디서 회수(payoff)하는지'까지 원인→대비책→회수의 3단 인과로 잇는다. 재후크는 '@0:15' 위치만 적지 말고 그 지점에서 무엇을 새로 던지는지(미공개 정보/반전/되갚는 질문)를 적는다.
- scene_breakdown[].why_this_works 는 '이 타깃 + 이 주제 + 이 포맷' 세 조건이 모두 들어간 메커니즘이어야 하며, 하나라도 빼면 말이 안 되게 쓴다(자가 테스트: target_audience 를 바꾸면 이 근거가 실제로 무너지는가? 무너지지 않으면 아직 일반론).
- fallback_scene 은 '약하면 다른 거'가 아니라, 1차안이 실패하는 구체 조건 + 그때 갈아끼울 구체 대안을 적는다.

────────────────────────────────────────────────────────
■ 작업 절차 (내부 사고 → 출력은 JSON만)
1. 입력 plan 을 읽고 FM-1~6 각각이 '걸리는' 슬롯을 식별한다.
2. 먼저 이 영상만의 차별화 앵글 1개(FM-3+FM-6)를 결정한다 — 이것이 나머지 모든 슬롯의 척추다.
3. 그 앵글을 기준으로 각 슬롯을 다시 쓰되, 추상·플레이스홀더·슬로건·카테고리 라벨·일반 진리를 전부 구체 약속으로 치환한다.
4. 입력에 없는 사실은 해당 필드 안에서 "예:" / references 는 "추정/예시:" 로 표시한다.
5. 길이·비트수·스키마·approach_label·safety 는 원본 그대로 보존한다.

■ 절대 금지 (judge-gaming 방지 — 이게 핵심이다)
- 점수용 키워드 채우기 금지. "차별화된", "딥리서치", "구체적인", "독창적인", "COT", "브랜드 특이성" 같은 형용사·버즈워드를 슬롯에 끼워넣는 것은 개선이 아니라 위반이다. 그 단어가 가리키는 '실제 구체물'을 산출하는 것만이 개선이다. 메타 설명("여기서 차별화를 줍니다")을 쓰지 말고, 차별화된 내용 그 자체를 써라.
- 차별성·깊이는 형용사가 아니라 검증 가능한 명사·숫자·고유명·제약·대조·장치로만 표현한다.
- 분량으로 깊이를 가장하지 마라: 한 줄이라도 구체 명사·숫자·장치가 있으면 통과, 세 줄이라도 추상어뿐이면 실패. 같은 말을 슬롯마다 바꿔 적어 분량만 늘리는 중복 금지.
- 일반 진리(누구에게나 참인 문장: "사람들은 공감을 좋아한다", "비주얼이 중요하다", "호기심을 유발한다") 를 why_this_works·retention 근거로 쓰지 마라 — 이 주제/이 타깃/이 포맷에서만 성립하는 메커니즘으로 교체한다.
- 없는 채널·출처·통계를 사실처럼 인용하지 마라(레퍼런스 요구의 악용=환각). 합성한 것은 "예:"/"추정/예시:" 로 표시한다.

■ 자기검문 (출력 직전, 7문항 전부 YES 여야 한다)
1. concept 이 주제 재진술이 아니라 '이 영상은 ___ 하는 ___ 다' 형태의 날카로운 앵글 1줄인가?
2. hook 과 두 hook_variants 가 슬로건·막연한 질문형이 아니라 구체 디테일/긴장/숫자를 담고, 서로 다른 심리 레버인가?
3. target_audience·tone 이 화자 1줄 + 시청자 1줄(행동·맥락·고충)로 못 박혀 있는가? target_audience 를 바꾸면 scene 근거가 무너지는가?
4. references 각각이 카테고리 라벨이 아니라 '[예: 구체 유형] — 공통점 + 우리의 차별점' 형태이고, 최소 2개가 그 쌍을 실제로 담았는가?
5. 기획안 전체를 관통하는 차별화 장치 1개가 concept/hook_system/scene_breakdown 에 일관되는가?
6. why_this_works·retention 에 일반 진리가 한 줄도 남지 않고, retention_architecture 가 원인→setup→payoff 3단 인과인가?
7. 모든 구체화가 형용사가 아니라 명사·숫자·고유명·제약·대조로 표현됐고, 입력에 없던 사실은 "예:"/"추정/예시:" 로 표시됐으며, 광고 과장·조회수 보장은 0개이고, flow 비트수·duration 합·approach_label·스키마가 보존됐는가?

출력은 입력과 동일한 {"plan": {...}} JSON 1개 객체만. 자연어 머리말/꼬리말·코드펜스 금지. 바뀌는 것은 '슬롯 충족'이 아니라 '슬롯 내용의 구체성·고유성·밀도'뿐이다.
"""


# ── 헬퍼 ─────────────────────────────────────────────────────────────────
def _strip_fences(text: str) -> str:
    """코드펜스 제거 (rescore 방어 패턴 참조)."""
    t = (text or "").strip()
    if t.startswith("```"):
        # ```json ... ``` 또는 ``` ... ```
        t = t.split("\n", 1)[1] if "\n" in t else t
        if t.rstrip().endswith("```"):
            t = t.rstrip()[:-3]
    return t.strip()


def _flow_duration_sum(plan: dict) -> int:
    total = 0
    for b in plan.get("flow", []) or []:
        try:
            total += int(b.get("duration_sec", 0))
        except (TypeError, ValueError):
            pass
    return total


def _validate_b1(b0: dict, b1: dict) -> list[str]:
    """스키마 무결성 검증 — 위반 사유 리스트 반환(빈 리스트=통과)."""
    errs: list[str] = []
    # (a) 키 집합 정확히 동일 (plan_id 는 제외하고 비교)
    b0_keys = set(b0.keys()) - {"plan_id"}
    b1_keys = set(b1.keys()) - {"plan_id"}
    if b0_keys != b1_keys:
        added = b1_keys - b0_keys
        removed = b0_keys - b1_keys
        errs.append(f"key_mismatch added={sorted(added)} removed={sorted(removed)}")
    # (b) flow 비트 수 + duration 합 동일
    b0_flow = b0.get("flow", []) or []
    b1_flow = b1.get("flow", []) or []
    if len(b0_flow) != len(b1_flow):
        errs.append(f"flow_beat_count b0={len(b0_flow)} b1={len(b1_flow)}")
    if _flow_duration_sum(b0) != _flow_duration_sum(b1):
        errs.append(f"flow_duration_sum b0={_flow_duration_sum(b0)} b1={_flow_duration_sum(b1)}")
    # (c) approach_label 동일
    if b0.get("approach_label") != b1.get("approach_label"):
        errs.append(f"approach_label b0={b0.get('approach_label')!r} b1={b1.get('approach_label')!r}")
    # (d) hook_system len>=2, scene_breakdown len>=2 + 필수 키, retention_architecture 비어있지 않음
    if len(b1.get("hook_system", []) or []) < 2:
        errs.append("hook_system_len<2")
    sb = b1.get("scene_breakdown", []) or []
    if len(sb) < 2:
        errs.append("scene_breakdown_len<2")
    else:
        req = {"scene_intent", "viewer_emotion", "retention_device", "why_this_works"}
        for i, s in enumerate(sb):
            if not isinstance(s, dict) or not req.issubset(s.keys()):
                missing = req - set(s.keys()) if isinstance(s, dict) else req
                errs.append(f"scene_breakdown[{i}]_missing={sorted(missing)}")
    if not str(b1.get("retention_architecture", "")).strip():
        errs.append("retention_architecture_empty")
    # (e) length_variants 동일
    if b0.get("length_variants") != b1.get("length_variants"):
        errs.append(f"length_variants b0={b0.get('length_variants')!r} b1={b1.get('length_variants')!r}")
    return errs


def _rewrite_one(client: OpenAI, model: str, user_input: str, b0_plan: dict
                 ) -> tuple[dict, str]:
    """단일 B0 → B1 rewrite (OpenAI). (b1_plan, raw_text) 반환."""
    user_msg = (
        "원래 사용자 요청: " + user_input
        + "\n\n개선 대상 plan(JSON):\n"
        + json.dumps({"plan": b0_plan}, ensure_ascii=False)
    )
    resp = client.chat.completions.create(
        model=model,
        temperature=REWRITER_TEMPERATURE,
        max_tokens=REWRITER_MAX_TOKENS,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": REWRITER_SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
        ],
    )
    text = (resp.choices[0].message.content or "").strip()
    parsed = json.loads(_strip_fences(text))
    plan = parsed.get("plan")
    if not isinstance(plan, dict):
        # 일부 모델이 {"plan":...} 없이 plan 객체를 바로 줄 수 있음
        if isinstance(parsed, dict) and "name" in parsed and "flow" in parsed:
            plan = parsed
        else:
            raise ValueError("B1 응답에 plan 객체 없음")
    return plan, text


def main() -> int:
    cases = json.load(open(CASES_PATH, encoding="utf-8"))["cases"]
    b0_claude = json.load(open(B0_CLAUDE_PATH, encoding="utf-8"))
    b0_scores = {c["case_id"]: c["A2_claude"] for c in b0_claude["cases"]}

    settings = get_settings()
    rewriter_model = settings.openai_model_critic or settings.openai_model_default
    openai_key = settings.openai_api_key
    if not openai_key:
        print("OPENAI_API_KEY 미설정 — 중단", file=sys.stderr)
        return 2
    anthropic_key = settings.anthropic_api_key
    if not anthropic_key:
        print("ANTHROPIC_API_KEY 미설정 — 중단", file=sys.stderr)
        return 2

    client = OpenAI(api_key=openai_key)
    judge_model = registry.get_model(JUDGE_REGISTRY_KEY)
    judge_model_id = judge_model["model_id"]
    adapter = AnthropicAdapter()

    print("=== B1 Specificity-Amplification Rewrite + Claude rescore ===")
    print(f".env: {_loaded or '(미발견)'}")
    print(f"rewriter: openai model={rewriter_model} temp={REWRITER_TEMPERATURE} json_mode")
    print(f"judge: registry={JUDGE_REGISTRY_KEY} model={judge_model_id} temp={JUDGE_TEMPERATURE} mode=director(10dim)")
    print(f"cases: {CASES_PATH}\n")

    out_cases: list[dict] = []
    failures: list[dict] = []
    console_rows: list[str] = []

    for c in cases:
        cid = c["case_id"]
        kind = c.get("kind")
        user_input = c.get("input", "")
        b0_plan = dict(c["plan"])
        b0_plan.setdefault("plan_id", cid)

        # B0 점수 재사용 (동일 judge — 재호출 불필요)
        b0 = b0_scores.get(cid)
        if b0 is None:
            failures.append({"case_id": cid, "stage": "b0_lookup", "error": "B0 claude 점수 없음"})
            continue

        # ── B1 rewrite (실패/스키마위반 1회 재시도) ──
        b1_plan = None
        b1_raw = ""
        validation_errs: list[str] = []
        last_err = ""
        for attempt in (1, 2):
            try:
                cand, b1_raw = _rewrite_one(client, rewriter_model, user_input, b0_plan)
                cand["plan_id"] = cid  # plan_id 강제 동일
                v_errs = _validate_b1(b0_plan, cand)
                if v_errs:
                    last_err = "schema_violation: " + "; ".join(v_errs)
                    validation_errs = v_errs
                    print(f"[{cid}] rewrite attempt {attempt} 스키마위반: {v_errs}")
                    time.sleep(1.0)
                    continue
                b1_plan = cand
                validation_errs = []
                break
            except Exception as e:  # noqa: BLE001
                last_err = f"{type(e).__name__}: {str(e)[:160]}"
                print(f"[{cid}] rewrite attempt {attempt} 실패: {last_err}")
                time.sleep(1.0)

        if b1_plan is None:
            failures.append({
                "case_id": cid, "stage": "b1_rewrite", "error": last_err,
                "validation_errors": validation_errs, "raw": b1_raw[:400],
            })
            print(f"[{cid}] B1 INVALID — Δ 미산출(B0 대체 안 함)\n")
            continue

        # ── B1 채점 (동일 Claude judge — byte-identical 로직) ──
        b1_raw_scores = None
        b1_judge_raw = ""
        jerr = ""
        for attempt in (1, 2):
            try:
                b1_raw_scores, b1_judge_raw = _judge_one(adapter, judge_model_id, anthropic_key, b1_plan)
                break
            except Exception as e:  # noqa: BLE001
                jerr = f"{type(e).__name__}: {str(e)[:160]}"
                print(f"[{cid}] judge attempt {attempt} 실패: {jerr}")
                time.sleep(1.0)

        if b1_raw_scores is None:
            failures.append({"case_id": cid, "stage": "b1_judge", "error": jerr, "raw": b1_judge_raw[:400]})
            print(f"[{cid}] B1 채점 실패\n")
            continue

        b1_avg, b1_verdict = _derive_verdict(b1_raw_scores, dimensions=DIMENSIONS_DIRECTOR)
        b1_rubric5 = _rubric_5(b1_raw_scores)

        # ── Δ 계산 ──
        b0_raw = b0["raw_scores"]
        per_dim = {d: int(b1_raw_scores[d]) - int(b0_raw[d]) for d in DIMENSIONS_DIRECTOR}
        overall_delta = round(b1_avg - float(b0["overall_score_avg"]), 4)
        b0_verdict = b0["verdict"]
        verdict_shift = "none" if b0_verdict == b1_verdict else f"{b0_verdict}→{b1_verdict}"

        out_cases.append({
            "case_id": cid,
            "kind": kind,
            "b0": {
                "overall_score_avg": b0["overall_score_avg"],
                "verdict": b0_verdict,
                "raw_scores": b0_raw,
                "dimensions": b0["dimensions"],
            },
            "b1": {
                "overall_score_avg": round(b1_avg, 4),
                "verdict": b1_verdict,
                "raw_scores": b1_raw_scores,
                "dimensions": b1_rubric5,
                "plan": b1_plan,
            },
            "delta": {
                "per_dim": per_dim,
                "overall": overall_delta,
                "verdict_shift": verdict_shift,
            },
        })
        row = (f"[{cid}] {kind:8} B0={b0['overall_score_avg']:.2f} "
               f"B1={b1_avg:.2f} Δ={overall_delta:+.2f} | {b0_verdict}→{b1_verdict}")
        console_rows.append(row)
        print(row)

    # ════════════════════════════════════════════════════════════════════
    # 집계 (aggregate)
    # ════════════════════════════════════════════════════════════════════
    n = len(out_cases)
    aggregate: dict = {}
    if n:
        # (a) 10차원 각각 평균 Δ
        per_dim_mean = {
            d: round(sum(oc["delta"]["per_dim"][d] for oc in out_cases) / n, 4)
            for d in DIMENSIONS_DIRECTOR
        }
        # (b) overall 평균 Δ + B0/B1 평균
        b0_overall_mean = round(sum(oc["b0"]["overall_score_avg"] for oc in out_cases) / n, 4)
        b1_overall_mean = round(sum(oc["b1"]["overall_score_avg"] for oc in out_cases) / n, 4)
        overall_delta_mean = round(b1_overall_mean - b0_overall_mean, 4)
        # (c) floor 축 B0→B1 평균 이동
        floor_move = {}
        for ax in FLOOR_AXES:
            b0m = round(sum(oc["b0"]["raw_scores"][ax] for oc in out_cases) / n, 4)
            b1m = round(sum(oc["b1"]["raw_scores"][ax] for oc in out_cases) / n, 4)
            floor_move[ax] = {"b0_mean": b0m, "b1_mean": b1m, "delta": round(b1m - b0m, 4)}
        # (d) verdict 분포
        def _dist(key: str) -> dict:
            d = {"approve": 0, "revise": 0, "reject": 0}
            for oc in out_cases:
                d[oc[key]["verdict"]] = d.get(oc[key]["verdict"], 0) + 1
            return d
        b0_dist = _dist("b0")
        b1_dist = _dist("b1")
        # (e) approve 넘어간 case 수 / reject→revise 수 / 임의 상향 수
        rank = {"reject": 0, "revise": 1, "approve": 2}
        to_approve = sum(1 for oc in out_cases
                         if oc["b0"]["verdict"] != "approve" and oc["b1"]["verdict"] == "approve")
        reject_to_revise = sum(1 for oc in out_cases
                               if oc["b0"]["verdict"] == "reject" and oc["b1"]["verdict"] == "revise")
        verdict_upgraded = sum(1 for oc in out_cases
                               if rank[oc["b1"]["verdict"]] > rank[oc["b0"]["verdict"]])

        aggregate = {
            "per_dim_mean_delta": per_dim_mean,
            "b0_overall_mean": b0_overall_mean,
            "b1_overall_mean": b1_overall_mean,
            "overall_delta_mean": overall_delta_mean,
            "floor_axes_move": floor_move,
            "verdict_dist_b0": b0_dist,
            "verdict_dist_b1": b1_dist,
            "to_approve_count": to_approve,
            "reject_to_revise_count": reject_to_revise,
            "verdict_upgraded_count": verdict_upgraded,
        }

    out = {
        "meta": {
            "date": "2026-06-21",
            "intervention": "specificity_amplification_rewrite",
            "rewriter_model": rewriter_model,
            "judge_registry_key": JUDGE_REGISTRY_KEY,
            "model_id": judge_model_id,
            "judge_temperature": JUDGE_TEMPERATURE,
            "rewriter_temperature": REWRITER_TEMPERATURE,
            "output_mode": "director",
            "n": n,
            "failures": len(failures),
            "schema_guard": "enforced",
            "b0_source": str(B0_CLAUDE_PATH.name),
            "aggregate": aggregate,
        },
        "cases": out_cases,
        "failures": failures,
    }
    OUT_PATH.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

    # ── 콘솔 집계 표 ──
    print("\n" + "=" * 64)
    print("AGGREGATE")
    if n:
        ag = aggregate
        print(f"  n={n}  failures={len(failures)}")
        print(f"  overall: B0={ag['b0_overall_mean']:.3f} → B1={ag['b1_overall_mean']:.3f} "
              f"(Δ={ag['overall_delta_mean']:+.3f})")
        print("  floor axes (raw 0~5):")
        for ax, mv in ag["floor_axes_move"].items():
            print(f"    {ax:18} {mv['b0_mean']:.2f} → {mv['b1_mean']:.2f}  (Δ={mv['delta']:+.2f})")
        print(f"  verdict B0: {ag['verdict_dist_b0']}")
        print(f"  verdict B1: {ag['verdict_dist_b1']}")
        print(f"  → approve 신규={ag['to_approve_count']}  reject→revise={ag['reject_to_revise_count']}  "
              f"verdict 상향={ag['verdict_upgraded_count']}")
    else:
        print("  (유효 case 0 — 전부 실패)")
    print("=" * 64)
    print(f"\n저장: {OUT_PATH}  (ok={n}, fail={len(failures)})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
