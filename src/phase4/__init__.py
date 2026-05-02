"""Phase 4 — LLM integration with Groq (see docs/phase-wise-architecture.md)."""

from phase4.llm import GroqChatClient, GroqConfig
from phase4.recommend import recommend_with_groq

__all__ = ["GroqChatClient", "GroqConfig", "recommend_with_groq"]
