"""LLM agent layer.

Slice 1: intent_planning (Intent + Planning 통합 1회 호출, 임시).
Slice 2 예정: intent.py / planning.py로 분리.
Slice 3 예정: critic.py 추가.
"""

from .intent_planning import run_intent_planning

__all__ = ["run_intent_planning"]
