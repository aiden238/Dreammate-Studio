"""Input schemas — POST /api/v1/generate request body.

Phase 1 Slice 1 범위:
  - input: 텍스트 1개 (영상기획 요청)
  - mode 자동 분기 없음 (Phase 3에서 추가)
"""

from pydantic import BaseModel, Field


class GenerateRequest(BaseModel):
    """Phase 1 generate endpoint 입력.

    api_contract.md §8.3는 plan_id + approved_direction + approved_components를
    요구하지만, Phase 1 Slice 1은 Simplest Slice 원칙으로 input 1개만 받는다.
    Phase 4 migration 시 api_contract.md 형식으로 정합.
    """

    input: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="영상기획 요청 텍스트",
        examples=["유튜브 채널 첫 영상 기획해줘"],
    )

    locale: str = Field(
        default="ko-KR",
        description="응답 locale (Phase 1은 ko-KR 고정)",
    )
