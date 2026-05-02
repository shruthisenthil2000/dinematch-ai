"""Phase 4 LLM layer: Groq adapter, prompts, response parsing."""

from phase4.llm.groq_adapter import GroqChatClient, GroqConfig
from phase4.llm.prompt_builder import build_recommendation_prompt, dataframe_to_candidate_dicts
from phase4.llm.response_parse import get_response_validator, parse_and_validate_response

__all__ = [
    "GroqChatClient",
    "GroqConfig",
    "build_recommendation_prompt",
    "dataframe_to_candidate_dicts",
    "get_response_validator",
    "parse_and_validate_response",
]
