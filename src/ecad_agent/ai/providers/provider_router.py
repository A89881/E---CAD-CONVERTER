"""AI provider selection."""

from __future__ import annotations

import os

from ecad_agent.ai.providers.anthropic_provider import AnthropicProvider
from ecad_agent.ai.providers.base import AIProvider
from ecad_agent.ai.providers.google_provider import GoogleProvider
from ecad_agent.ai.providers.local_llm_provider import LocalLLMProvider
from ecad_agent.ai.providers.openai_provider import OpenAIProvider


def get_provider(name: str | None = None) -> AIProvider:
    """Return a provider by name.

    Defaults to `ECAD_AGENT_AI_PROVIDER`, then `local`, so development and CI
    never require network access or API keys.
    """

    selected = (name or os.getenv("ECAD_AGENT_AI_PROVIDER") or "local").lower()
    providers: dict[str, AIProvider] = {
        "local": LocalLLMProvider(),
        "offline": LocalLLMProvider(),
        "openai": OpenAIProvider(),
        "anthropic": AnthropicProvider(),
        "google": GoogleProvider(),
    }
    if selected not in providers:
        supported = ", ".join(sorted(providers))
        raise ValueError(f"Unknown AI provider {selected!r}. Supported providers: {supported}.")
    return providers[selected]
