"""LLM agent layer.

Slice 2: Intent (P-001) + Planning (P-006) 분리. 직렬 호출.
Slice 3: Critic (P-007) 추가. Intent → Planning → Critic 직렬 (revise 없음).
"""

from .intent import run_intent
from .intent import PROMPT_ID as INTENT_PROMPT_ID
from .intent import PROMPT_VERSION as INTENT_PROMPT_VERSION
from .planning import run_planning
from .planning import PROMPT_ID as PLANNING_PROMPT_ID
from .planning import PROMPT_VERSION as PLANNING_PROMPT_VERSION
from .critic import run_critic
from .critic import PROMPT_ID as CRITIC_PROMPT_ID
from .critic import PROMPT_VERSION as CRITIC_PROMPT_VERSION

__all__ = [
    "run_intent",
    "INTENT_PROMPT_ID",
    "INTENT_PROMPT_VERSION",
    "run_planning",
    "PLANNING_PROMPT_ID",
    "PLANNING_PROMPT_VERSION",
    "run_critic",
    "CRITIC_PROMPT_ID",
    "CRITIC_PROMPT_VERSION",
]
