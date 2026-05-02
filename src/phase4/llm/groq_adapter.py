"""Groq OpenAI-compatible chat completions."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, List, Mapping, Optional


@dataclass(frozen=True)
class GroqConfig:
    """Groq API settings (see https://console.groq.com/)."""

    api_key: str
    model: str = "llama-3.3-70b-versatile"
    temperature: float = 0.2
    max_tokens: int = 4096
    timeout_sec: float = 90.0

    @classmethod
    def from_env(cls) -> GroqConfig:
        key = (os.environ.get("GROQ_API_KEY") or "").strip()
        if not key:
            raise RuntimeError("GROQ_API_KEY is not set in the environment.")
        model = (os.environ.get("GROQ_MODEL") or "llama-3.3-70b-versatile").strip()
        return cls(api_key=key, model=model)


class GroqChatClient:
    """Thin wrapper around the official ``groq`` SDK."""

    def __init__(self, config: GroqConfig) -> None:
        self._config = config

    def complete(self, messages: List[Mapping[str, str]]) -> str:
        from groq import Groq

        client = Groq(api_key=self._config.api_key)
        kwargs: dict[str, Any] = {
            "model": self._config.model,
            "messages": messages,
            "temperature": self._config.temperature,
            "max_tokens": self._config.max_tokens,
        }
        # groq-python accepts timeout on create()
        kwargs["timeout"] = self._config.timeout_sec
        resp = client.chat.completions.create(**kwargs)
        choice = resp.choices[0]
        content = choice.message.content
        return (content or "").strip()
