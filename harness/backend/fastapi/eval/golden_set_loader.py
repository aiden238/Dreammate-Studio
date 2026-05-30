"""Phase 9.5 — golden_set.md → 구조화 케이스 로더 (ADR-033).

eval/golden_set.md 의 yaml 블록(GS- prefix) 파싱 → 11 케이스 (GS-001~GS-011).
golden_set.md 단일 출처 (파싱만, 수정 X — golden_set.md 는 contract).

ADR-033 §2.1 loader 설계:
  load_golden_set() -> list[dict]
    GoldenCase = {
      id: "GS-XXX",            # case_id (GS- prefix 필터)
      mode: discovery | quick,
      prompt_target: "P-XXX" | "full_flow" | "RAG ...",
      priority: "P0" | "P1" | "P2",
      input: { user_message, brand_context, rag_context, brand_memory },
      expected_properties: { body_keys, validation, passing_criteria },
    }

파싱 정책 (ADR-033 §2.1):
  - golden_set.md ` ```yaml ` 블록 → yaml.safe_load → case_id 가 `GS-` prefix 인
    dict 만 케이스 수집 (§1 template 블록 / §5.2 jsonl 예시 블록 배제).
  - 파싱 실패 graceful (빈 list 또는 부분 list + 경고 로그) — runner 가 차단 결정.
"""
from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# golden_set.md 기본 위치 — repo 의 eval/golden_set.md (harness 루트 기준).
# 본 파일: harness/backend/fastapi/eval/golden_set_loader.py
#   parents[0]=eval, [1]=fastapi, [2]=backend, [3]=harness
_DEFAULT_GOLDEN_SET = Path(__file__).resolve().parents[3] / "eval" / "golden_set.md"

# ` ```yaml ... ``` ` 코드 펜스 추출 (non-greedy, DOTALL).
_YAML_FENCE = re.compile(r"```yaml\s*\n(.*?)```", re.DOTALL)


def load_golden_set(path: str | None = None) -> list[dict[str, Any]]:
    """eval/golden_set.md → [{id, mode, prompt_target, priority, input, expected_properties}, ...].

    GS- prefix case_id 인 yaml 블록만 케이스로 수집 (단일 출처 파싱).
    §1 표준 형식 template (case_id: GS-XXX) / §5.2 jsonl 예시는 GS-XXX placeholder 또는
    case_id 부재로 배제된다.

    Args:
        path: golden_set.md 경로 (None → 기본 eval/golden_set.md).

    Returns:
        파싱된 케이스 list. 파일 없음/yaml 파싱 전면 실패 시 빈 list (graceful) + 경고.
    """
    try:
        import yaml
    except ImportError as exc:  # pragma: no cover — pyyaml 은 환경 의존성
        logger.warning("pyyaml 미설치 — golden_set 파싱 불가: %s", exc)
        return []

    gs_path = Path(path) if path else _DEFAULT_GOLDEN_SET
    if not gs_path.exists():
        logger.warning("golden_set.md 없음: %s — 빈 케이스 list 반환 (graceful)", gs_path)
        return []

    try:
        raw = gs_path.read_text(encoding="utf-8")
    except OSError as exc:  # pragma: no cover — 파일 읽기 실패 graceful
        logger.warning("golden_set.md 읽기 실패: %s — 빈 list 반환", exc)
        return []

    cases: list[dict[str, Any]] = []
    seen_ids: set[str] = set()

    for block in _YAML_FENCE.findall(raw):
        # golden_set.md yaml 블록은 일부 케이스에서 사람이 읽는 pseudo-yaml
        # ("{} | null", "plans[*].rag_used", "∈ [0, 5]", "<자동 규칙>") 를 포함하여
        # strict yaml.safe_load 가 실패할 수 있다. golden_set.md 는 단일 출처(수정 X)이므로
        # loader 가 이를 graceful 하게 흡수한다:
        #   1) 우선 strict safe_load 시도 (성공 시 전체 구조 확보).
        #   2) 실패 시 top-level scalar 메타(case_id/name/priority/mode/prompt_target)
        #      를 line 기반으로 추출 (케이스 누락 방지 — ADR-033 §2.1 11 케이스 보장).
        parsed: dict[str, Any] | None = None
        try:
            loaded = yaml.safe_load(block)
            if isinstance(loaded, dict):
                parsed = loaded
        except yaml.YAMLError as exc:
            logger.info(
                "golden_set yaml strict 파싱 실패 — scalar fallback 적용: %s",
                str(exc).splitlines()[0] if str(exc) else exc,
            )

        if parsed is None:
            parsed = _scalar_fallback(block)
        if parsed is None:
            # §5.2 jsonl/리스트 예시 블록 등 — case_id 없음 → 케이스 아님.
            continue

        case_id = parsed.get("case_id")
        if not isinstance(case_id, str):
            continue

        # GS- prefix 필터. §1 template 은 "GS-XXX" placeholder → 정규식으로 실제 번호만.
        if not re.fullmatch(r"GS-\d{3,}", case_id):
            continue
        if case_id in seen_ids:
            # 중복 case_id 방어 (cross-reference 표 등에서 재등장 가능 — 첫 정의 우선).
            continue
        seen_ids.add(case_id)

        cases.append(_normalize_case(parsed))

    if not cases:
        logger.warning("golden_set.md 에서 GS- 케이스를 찾지 못함: %s", gs_path)
    else:
        logger.info("golden_set 로드: %d 케이스 (%s)", len(cases), gs_path.name)
    return cases


# top-level scalar 추출용 — "  key: value" (들여쓰기 0~1 레벨 = 들여쓰기 ≤ 2 칸).
_SCALAR_LINE = re.compile(r"^(case_id|name|priority|mode|prompt_target)\s*:\s*(.+?)\s*$")


def _scalar_fallback(block: str) -> dict[str, Any] | None:
    """strict yaml 실패 블록 → top-level scalar 메타만 추출 (graceful).

    case_id 가 없으면 None (케이스 아님). expected_properties 는 빈 구조로 둔다
    (structural 채점은 mock Envelope 기반이므로 영향 없음 — ADR-033 §2.2).
    """
    out: dict[str, Any] = {}
    for line in block.splitlines():
        # top-level 키만 (들여쓰기 없는 라인) — 중첩 키 오인 방지.
        if line[:1] in (" ", "\t"):
            continue
        m = _SCALAR_LINE.match(line)
        if m:
            key, value = m.group(1), m.group(2).strip().strip('"').strip("'")
            out[key] = value
    if "case_id" not in out:
        return None
    return out


def _normalize_case(parsed: dict[str, Any]) -> dict[str, Any]:
    """yaml dict → 구조화 케이스 (ADR-033 §2.1 GoldenCase)."""
    expected_output = parsed.get("expected_output") or {}
    if not isinstance(expected_output, dict):
        expected_output = {}

    return {
        "id": parsed["case_id"],
        "name": parsed.get("name", ""),
        "priority": parsed.get("priority", "P1"),
        "mode": parsed.get("mode", ""),
        "prompt_target": parsed.get("prompt_target", ""),
        "input": parsed.get("input") or {},
        "expected_path": parsed.get("expected_path") or [],
        "expected_properties": {
            "body_keys": expected_output.get("body_keys") or [],
            "validation": expected_output.get("validation") or [],
            "passing_criteria": expected_output.get("passing_criteria") or [],
        },
        "notes": parsed.get("notes") or [],
    }
