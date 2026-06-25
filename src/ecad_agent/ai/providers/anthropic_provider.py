"""Anthropic provider placeholder."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from ecad_agent.ai.providers.base import (
    AIMessage,
    AIResponse,
    ProviderNotConfiguredError,
)


class AnthropicProvider:
    name = "anthropic"

    def complete(
        self,
        messages: Sequence[AIMessage],
        tools: Sequence[Mapping[str, Any]] | None = None,
        max_tokens: int = 2000,
    ) -> AIResponse:
        del messages, tools, max_tokens
        raise ProviderNotConfiguredError(
            "AnthropicProvider is a scaffold. Add SDK configuration before using it."
        )
