"""Phase 7 Slice 3 — OpenAI embedding wrapper (ADR-025).

text-embedding-3-small (1536 dim) 호출.
graceful fallback: 실패 시 None + warning (chunk 저장 X, plan 차단 X).

References:
  - docs/decisions/phase_7_rag_architecture.md (ADR-025 §2 Embedding)
  - knowledge/rag/metadata_schema.md
"""
from __future__ import annotations

import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)


async def embed(
    text: str,
    *,
    model: str = "text-embedding-3-small",
    client: Any | None = None,
) -> Optional[list[float]]:
    """OpenAI embedding API → 1536 dim float list.

    Args:
        text: 임베딩할 텍스트 (빈 / 공백만 → None)
        model: embedding model (env RAG_EMBEDDING_MODEL override 가능)
        client: AsyncOpenAI mock or runtime client. None 시 지연 import.

    Returns:
        embedding vector (list[float], 1536 dim) 또는 None (graceful 실패).

    Graceful 실패 사유 (모두 None 반환 + warning):
      - 빈 text / 공백만
      - openai 패키지 미설치
      - API 호출 예외 (network / quota / 인증)
      - 응답 empty / data 비어 있음
    """
    if not text or not text.strip():
        return None

    if client is None:
        try:
            from openai import AsyncOpenAI  # type: ignore[import-not-found]

            client = AsyncOpenAI()
        except ImportError:
            logger.warning(
                "embedding_failed: openai package not installed (graceful)"
            )
            return None
        except Exception as exc:
            logger.warning(
                "embedding_failed: client init %s (graceful)",
                exc.__class__.__name__,
            )
            return None

    try:
        resp = await client.embeddings.create(input=text, model=model)
        if not resp or not getattr(resp, "data", None):
            logger.warning("embedding_failed: empty response (graceful)")
            return None
        first = resp.data[0]
        embedding = getattr(first, "embedding", None)
        if embedding is None:
            logger.warning(
                "embedding_failed: data[0].embedding missing (graceful)"
            )
            return None
        if not isinstance(embedding, list):
            return list(embedding)
        return embedding
    except Exception as exc:
        logger.warning(
            "embedding_failed: %s (graceful)", exc.__class__.__name__
        )
        return None


async def embed_many(
    texts: list[str],
    *,
    model: str = "text-embedding-3-small",
    client: Any | None = None,
) -> list[Optional[list[float]]]:
    """다중 텍스트 embedding (graceful — 개별 실패 시 None).

    Phase 7 MVP: 순차 호출 (batch_size=10 정책은 ADR-025 §2 명시했으나
    Phase 9+ 운영 단계에서 동적 batch 도입). 본 함수는 단순 wrapper.
    """
    results: list[Optional[list[float]]] = []
    for text in texts:
        emb = await embed(text, model=model, client=client)
        results.append(emb)
    return results


__all__ = ["embed", "embed_many"]
