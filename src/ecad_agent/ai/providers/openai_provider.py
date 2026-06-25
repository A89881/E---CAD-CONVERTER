"""OpenAI provider placeholder.

The interface is ready, but the SDK call is intentionally not wired until
runtime configuration, secrets, and model policy are decided.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from ecad_agent.ai.providers.base import (
    AIMessage,
    AIResponse,
    ProviderNotConfiguredError,
)


class OpenAIProvider:
    name = "openai"

    def complete(
        self,
        messages: Sequence[AIMessage],
        tools: Sequence[Mapping[str, Any]] | None = None,
        max_tokens: int = 2000,
    ) -> AIResponse:
        del messages, tools, max_tokens
        raise ProviderNotConfiguredError(
            "OpenAIProvider is a scaffold. Add SDK configuration before using it."
        )
