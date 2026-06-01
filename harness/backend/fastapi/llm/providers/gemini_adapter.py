"""Google Gemini provider adapter — Phase 11 A안 Slice 1.

제안서 §3 / §7 / §18.A. A안 cross_validation(다른 family 1회 교차검증)용 adapter.
google-genai SDK 래핑:

    from google import genai
    genai.Client(api_key=...).models.generate_content(
        model=req.model_id,
        contents=...,
        config={"response_mime_type": "application/json", "temperature": ..., ...},
    )

→ canonical LLMResponse. provider 예외 → LLMError 정규화.
JSON 모드 = config.response_mime_type="application/json".

★ gated/default-off: A안에서 cross_validation alias 는 정의되지만 default 호출 경로
없음(제안서 §7). 본 Slice 는 adapter 를 만들기만 — agents 미연결(behavior-preserving).
★ DI: client 주입 가능 → 테스트가 mock genai client 주입(실 API 0).
★ SDK import 는 지연(complete 시점) — google-genai 미설치 환경에서도 모듈 import 는 성공(graceful).

OpenAI chat 의 role 기반 messages 와 달리 Gemini 는 system_instruction + contents 분리.
canonical LLMMessage(system/user/assistant)를 Gemini shape 로 매핑한다:
  - role=="system" → config.system_instruction (병합)
  - 그 외        → contents (user/assistant turn)

★ Slice 2 튜닝 (additive, behavior-preserving):
  1. thinking 처리 — Gemini 3.x flash 는 thinking 모델이라 max_output_tokens 가 작으면
     추론에 다 쓰여 출력 0. settings.gemini_thinking_budget(default 0=비활성)를
     ThinkingConfig 로 전달 → 출력에 온전히 사용. SDK 가 ThinkingConfig 미지원이면
     graceful(미설정 진행).
  2. 503 UNAVAILABLE(서버 수요) 재시도 — 짧은 backoff 로 1~2회 재시도 후 graceful LLMError.
  3. text 추출 견고화 — response.text 가 None/빈 경우 candidates[0].content.parts 에서 추출.
"""

from __future__ import annotations

import logging
import time
from typing import Any

from ...config import get_settings
from ..errors import LLMError
from ..types import LLMMessage, LLMRequest, LLMResponse, LLMUsage

logger = logging.getLogger(__name__)

# 503 재시도 정책 (Slice 2): 짧은 backoff 로 소량 재시도 후 graceful LLMError.
_RETRY_MAX_ATTEMPTS = 3  # 최초 1 + 재시도 2.
_RETRY_BACKOFF_SECONDS = (0.5, 1.0)  # 재시도 사이 대기 (소량).


class GeminiAdapter:
    """google-genai SDK 래퍼 (ProviderAdapter 구현)."""

    provider = "google"

    def __init__(self, client: Any = None) -> None:
        """Args:
            client: genai.Client 호환 client (테스트 mock 주입용 DI hook). None 이면
                    complete() 시점에 api_key 로 실 genai.Client 생성(SDK 지연 import).
        """
        self._client = client

    def _resolve_client(self, api_key: str) -> Any:
        if self._client is not None:
            return self._client
        try:
            from google import genai  # 지연 import (미설치 환경 graceful)
        except ImportError as e:  # pragma: no cover - 설치 환경에서 미발생
            raise LLMError(
                self.provider,
                "",
                "google-genai SDK 미설치 (requirements.txt: google-genai)",
                cause=e,
            ) from e
        return genai.Client(api_key=api_key)

    def complete(self, req: LLMRequest, *, api_key: str) -> LLMResponse:
        client = self._resolve_client(api_key)
        system_instruction, contents = _split_messages(req.messages)

        config: dict[str, Any] = {
            "temperature": req.temperature,
            # ★ Slice 2: thinking 비활성(budget 0) 시 max_output_tokens 가 출력에 온전히 사용.
            "max_output_tokens": req.max_tokens,
        }
        if system_instruction:
            config["system_instruction"] = system_instruction
        if req.json_mode:
            config["response_mime_type"] = "application/json"
        # ★ Slice 2: thinking 처리 — budget(default 0=비활성) 을 ThinkingConfig 로.
        _apply_thinking_config(config)

        logger.info("gemini adapter call model=%s json_mode=%s", req.model_id, req.json_mode)

        response = self._generate_with_retry(client, req, contents, config)

        text = _extract_text(response)
        usage = _extract_usage(response)
        return LLMResponse(
            text=text,
            model_id=req.model_id,
            alias="",  # gateway 가 alias 를 채워 반환.
            usage=usage,
            raw=response,
        )

    def _generate_with_retry(
        self, client: Any, req: LLMRequest, contents: str, config: dict[str, Any]
    ) -> Any:
        """generate_content 호출 + 503 UNAVAILABLE 재시도.

        Gemini flash 는 서버 수요로 일시적 503(ServerError/UNAVAILABLE)을 낼 수 있다.
        짧은 backoff 로 소량(1~2회) 재시도 후에도 실패하면 graceful LLMError 로 정규화한다.
        503 이 아닌 예외는 즉시 LLMError(재시도 X).
        """
        last_exc: Exception | None = None
        for attempt in range(1, _RETRY_MAX_ATTEMPTS + 1):
            try:
                return client.models.generate_content(
                    model=req.model_id,
                    contents=contents,
                    config=config,
                )
            except Exception as e:  # google-genai 예외 계층을 canonical 로 정규화
                last_exc = e
                if _is_retryable_unavailable(e) and attempt < _RETRY_MAX_ATTEMPTS:
                    backoff = _RETRY_BACKOFF_SECONDS[
                        min(attempt - 1, len(_RETRY_BACKOFF_SECONDS) - 1)
                    ]
                    logger.warning(
                        "Gemini 503 UNAVAILABLE — 재시도 %d/%d (backoff %.1fs) model=%s",
                        attempt,
                        _RETRY_MAX_ATTEMPTS - 1,
                        backoff,
                        req.model_id,
                    )
                    time.sleep(backoff)
                    continue
                logger.exception("Gemini adapter 호출 실패 model=%s", req.model_id)
                raise LLMError(
                    self.provider, req.model_id, f"Gemini 호출 실패: {e}", cause=e
                ) from e
        # 루프가 break 없이 끝나는 경우는 없음(매 분기 return/raise). 방어적 graceful.
        raise LLMError(  # pragma: no cover - 도달 불가(매 attempt return/raise)
            self.provider, req.model_id, f"Gemini 호출 실패(재시도 소진): {last_exc}", cause=last_exc
        )


def _split_messages(messages: list[LLMMessage]) -> tuple[str, str]:
    """canonical messages → (system_instruction, contents).

    Gemini 는 system 을 config.system_instruction 으로 분리한다. system 외 메시지는
    한 prompt 문자열로 병합(Phase 11 A안 단순화 — multi-turn 정밀 매핑은 후속).
    """
    system_parts: list[str] = []
    content_parts: list[str] = []
    for m in messages:
        if m.role == "system":
            system_parts.append(m.content)
        else:
            content_parts.append(m.content)
    return "\n\n".join(system_parts), "\n\n".join(content_parts)


def _apply_thinking_config(config: dict[str, Any]) -> None:
    """★ Slice 2: thinking 처리 — settings.gemini_thinking_budget 를 ThinkingConfig 로.

    Gemini 3.x flash 는 thinking 모델이라 max_output_tokens 가 작으면 추론에 다 소진되어
    출력 0 이 된다. budget(default 0=비활성)을 generate_content config 의 thinking_config 로
    전달해 추론 토큰을 제한 → max_output_tokens 가 출력에 온전히 사용되게 한다.

    SDK 버전이 ThinkingConfig 를 미지원하거나 google-genai 미설치면 graceful(미설정 진행).
    """
    try:
        budget = int(get_settings().gemini_thinking_budget)
    except Exception:  # pragma: no cover - settings 접근 실패 방어
        return
    try:
        from google.genai import types as genai_types  # 지연 import (미설치 graceful)

        config["thinking_config"] = genai_types.ThinkingConfig(thinking_budget=budget)
    except Exception:  # ImportError / AttributeError(구버전 SDK) 등 → graceful skip
        logger.debug(
            "Gemini ThinkingConfig 미지원/미설치 — thinking_config 미설정 (graceful) budget=%s",
            budget,
        )


def _is_retryable_unavailable(exc: Exception) -> bool:
    """503 / UNAVAILABLE 계열 예외인지 판정 (재시도 대상).

    google-genai 의 ServerError(혹은 status_code/code 503) 또는 메시지에 '503' /
    'UNAVAILABLE' 가 포함되는 경우 재시도 대상으로 본다 (SDK 버전 간 예외 형태 차이 흡수).
    """
    # 명시적 status code 속성 (google-genai ServerError 등).
    for attr in ("status_code", "code"):
        val = getattr(exc, attr, None)
        if val == 503 or str(val) == "503":
            return True
    name = type(exc).__name__.lower()
    if "servererror" in name or "unavailable" in name:
        return True
    text = str(exc).upper()
    return "503" in text or "UNAVAILABLE" in text


def _extract_text(response: Any) -> str:
    """Gemini 응답 → 본문 텍스트 (없으면 "").

    ★ Slice 2 견고화: response.text 가 None/빈 문자열이면 candidates[0].content.parts
    에서 part.text 를 이어붙여 추출 시도(thinking 모델이 .text 를 비우는 경우 대비).
    """
    text = getattr(response, "text", None)
    if isinstance(text, str) and text:
        return text
    # fallback: candidates[0].content.parts 의 text 병합.
    extracted = _extract_text_from_candidates(response)
    if extracted:
        return extracted
    return text if isinstance(text, str) else ""


def _extract_text_from_candidates(response: Any) -> str:
    """candidates[0].content.parts[*].text 를 이어붙여 반환 (없으면 "")."""
    candidates = getattr(response, "candidates", None)
    if not candidates:
        return ""
    try:
        first = candidates[0]
    except (IndexError, TypeError):
        return ""
    content = getattr(first, "content", None)
    parts = getattr(content, "parts", None)
    if not parts:
        return ""
    chunks: list[str] = []
    for part in parts:
        part_text = getattr(part, "text", None)
        if isinstance(part_text, str) and part_text:
            chunks.append(part_text)
    return "".join(chunks)


def _extract_usage(response: Any) -> LLMUsage:
    """Gemini usage_metadata → canonical LLMUsage (없으면 0)."""
    meta = getattr(response, "usage_metadata", None)
    if meta is None:
        return LLMUsage()
    prompt = getattr(meta, "prompt_token_count", 0) or 0
    completion = getattr(meta, "candidates_token_count", 0) or 0
    try:
        return LLMUsage(prompt_tokens=int(prompt), completion_tokens=int(completion))
    except (TypeError, ValueError):
        return LLMUsage()
