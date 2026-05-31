"""Phase 10 Slice 3 — eval LLM mode capability (ADR-033 §1, §2.2 real mode flag).

실 LLM eval mode 의 **capability 경로**를 코드로 wire 한다. ★ default 는 mock-deterministic
(기존 Phase 9.5 runner 경로 불변). real 경로는 **opt-in** 이며 CI/test 에서 실 API 를 호출하지
않는다 (키 부재 시 graceful mock fallback, 단위 검증은 monkeypatch).

설계 원칙 (ADR-033 Constraints "mock-deterministic primary ★"):
  - mock (primary): 결정적 fixture/seed — 비결정성 0, 비용 0, CI per-commit 가능.
  - real  (capability): 실 LLM 8차원 의미 채점 — 비결정적, 운영 단계 야간 배치 (NG2).
    본 phase 는 **경로를 wire** 만 한다 (실 실행은 opt-in — 사용자가 키 제공 시).

★★ 절대 규칙 (Phase 10 S3):
  - 환경변수(EVAL_MODE / OPENAI_API_KEY / ANTHROPIC_API_KEY)는 **읽기만** 한다 (placeholder).
  - 키가 없으면 real 요청이라도 mock 으로 graceful fallback (예외 X) — CI 안전.
  - 실제 API client 호출은 주입 가능한 `llm_caller` 를 통해서만 일어난다. 본 모듈은 client 를
    import 하지 않으며, default `llm_caller` 는 키 부재 시 호출되지 않는다.
  - 따라서 본 모듈 단독으로는 어떤 실 네트워크 호출도 발생하지 않는다 (입증: 키 미설정 + caller
    미주입 → mock 경로). test 는 caller 를 monkeypatch 한 stub 으로 분기만 검증한다.

opt-in 사용법 (운영자, 키 제공 시):
  ```
  # 1) 환경변수로 real 모드 + 키 제공 (.env — 절대 commit 금지, placeholder 만 저장소에)
  #    EVAL_MODE=real
  #    OPENAI_API_KEY=sk-...        # user-provided, 저장소 미포함
  # 2) 실 LLM caller 를 주입 (운영 배치 스크립트에서):
  from backend.fastapi.eval.mode import resolve_mode, ScoreContext
  ctx = ScoreContext(requested_mode="real", llm_caller=my_openai_caller)
  effective = resolve_mode(ctx)   # 키 있으면 "real", 없으면 "mock" (graceful)
  ```
"""
from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)

# 지원 모드.
MODE_MOCK = "mock"
MODE_REAL = "real"
VALID_MODES = (MODE_MOCK, MODE_REAL)

# real 모드가 실제로 동작하려면 존재해야 하는 키 환경변수 (읽기 전용 — placeholder).
# 둘 중 하나라도 있으면 real 시도 가능 (OpenAI 8차원 채점 우선, Anthropic 대체).
_REAL_KEY_ENV = ("OPENAI_API_KEY", "ANTHROPIC_API_KEY")

# 환경변수로 default 모드를 지정할 수 있으나, 명시 인자(mode=)가 항상 우선한다.
_MODE_ENV = "EVAL_MODE"


# real eval 의 LLM 호출 시그니처 — case 입력을 받아 8차원 의미 채점 dict 를 반환.
# ★ 본 모듈은 default caller 를 제공하지 않는다 (None). 운영자가 명시 주입해야만 실 호출 발생.
LLMCaller = Callable[[dict[str, Any]], dict[str, Any]]


@dataclass
class ScoreContext:
    """eval 채점 컨텍스트 — 모드 결정 + (real 시) LLM caller 주입.

    Attributes:
        requested_mode: 호출자가 요청한 모드 ("mock" | "real"). None → 환경변수/default.
        llm_caller: real 채점용 LLM 호출 함수 (None 이면 real 불가 → mock fallback).
            ★ 주입된 경우에만 실 호출 가능 — CI/test 는 주입하지 않거나 stub 주입.
        env: 환경변수 dict (테스트 주입용 — None 이면 os.environ 읽기 전용).
    """

    requested_mode: Optional[str] = None
    llm_caller: Optional[LLMCaller] = None
    env: Optional[dict[str, str]] = field(default=None)

    def _getenv(self, key: str) -> Optional[str]:
        if self.env is not None:
            return self.env.get(key)
        return os.environ.get(key)


def has_real_key(ctx: ScoreContext | None = None) -> bool:
    """real 모드 키(OPENAI/ANTHROPIC)가 환경에 존재하는지 — **읽기만** (값 노출 X).

    빈 문자열/공백은 미설정으로 간주 (placeholder .env 안전).
    """
    ctx = ctx or ScoreContext()
    for key in _REAL_KEY_ENV:
        val = ctx._getenv(key)
        if val and val.strip():
            return True
    return False


def resolve_mode(ctx: ScoreContext | None = None) -> str:
    """요청 모드 → 실효 모드 결정 (graceful).

    우선순위: 명시 requested_mode > 환경변수 EVAL_MODE > default(mock).
    real 요청이라도 (키 부재 OR llm_caller 미주입) 시 → mock 으로 graceful fallback (예외 X).
    이로써 CI/test 는 키/caller 가 없으므로 **항상 mock 경로** (실 호출 0 입증).

    Returns:
        "mock" | "real".

    Raises:
        ValueError: 지원하지 않는 모드 문자열.
    """
    ctx = ctx or ScoreContext()

    requested = ctx.requested_mode
    if requested is None:
        env_mode = ctx._getenv(_MODE_ENV)
        requested = env_mode.strip() if (env_mode and env_mode.strip()) else MODE_MOCK

    if requested not in VALID_MODES:
        raise ValueError(f"지원하지 않는 eval mode: {requested!r} (mock | real)")

    if requested == MODE_MOCK:
        return MODE_MOCK

    # requested == real — capability 게이트 (graceful fallback).
    if ctx.llm_caller is None:
        logger.info(
            "EVAL mode=real 요청이나 llm_caller 미주입 — mock 으로 graceful fallback "
            "(CI/test 안전: 실 LLM 호출 0)."
        )
        return MODE_MOCK
    if not has_real_key(ctx):
        logger.info(
            "EVAL mode=real 요청이나 실 LLM 키(OPENAI/ANTHROPIC) 미설정 — mock fallback "
            "(키는 user-provided .env, 저장소 미포함)."
        )
        return MODE_MOCK

    logger.info("EVAL mode=real 활성 (opt-in, 운영 배치) — llm_caller 주입 + 키 확인됨.")
    return MODE_REAL


def real_score_envelope(case: dict[str, Any], ctx: ScoreContext) -> dict[str, Any]:
    """real 모드 채점 envelope 생성 — 주입된 llm_caller 를 통해서만 실 호출.

    ★ 본 함수는 resolve_mode 가 "real" 을 반환했을 때만 호출되어야 한다 (capability 경로).
    llm_caller 가 None 이면 RuntimeError (resolve_mode 게이트 우회 방지 — 방어적).
    실제 8차원 의미 채점/Envelope 합성은 주입된 caller 의 책임 (운영 배치 구현).

    Args:
        case: load_golden_set 케이스 dict.
        ctx: llm_caller 가 주입된 ScoreContext.

    Returns:
        caller 가 반환한 채점 결과 dict (Envelope.model_dump 호환 형태 기대).
    """
    if ctx.llm_caller is None:  # pragma: no cover — resolve_mode 게이트로 도달 불가
        raise RuntimeError(
            "real_score_envelope 는 llm_caller 주입 시에만 호출 가능 — resolve_mode 게이트 위반."
        )
    return ctx.llm_caller(case)
