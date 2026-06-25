"""Provider-neutral AI interface.

The rest of the ECAD app talks to this contract instead of importing one vendor
SDK directly. Provider implementations can be OpenAI, Anthropic, Google, or a
local model without changing copilot orchestration.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any, Literal, Protocol

Role = Literal["system", "user", "assistant", "tool"]
Uncertainty = Literal["low", "medium", "high"]


@dataclass(frozen=True, slots=True)
class AIMessage:
    """A provider-neutral chat message."""

    role: Role
    content: str

    def to_dict(self) -> dict[str, str]:
        return {"role": self.role, "content": self.content}


@dataclass(frozen=True, slots=True)
class AIResponse:
    """Structured copilot response returned by every provider."""

    answer: str
    referenced_components: list[str] = field(default_factory=list)
    referenced_nets: list[str] = field(default_factory=list)
    uncertainty: Uncertainty = "medium"
    suggested_next_action: str | None = None
    raw: Mapping[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "answer": self.answer,
            "referenced_components": self.referenced_components,
            "referenced_nets": self.referenced_nets,
            "uncertainty": self.uncertainty,
        }
        if self.suggested_next_action is not None:
            payload["suggested_next_action"] = self.suggested_next_action
        if self.raw is not None:
            payload["raw"] = dict(self.raw)
        return payload


class AIProvider(Protocol):
    """Minimal provider interface used by the copilot engine."""

    name: str

    def complete(
        self,
        messages: Sequence[AIMessage],
        tools: Sequence[Mapping[str, Any]] | None = None,
        max_tokens: int = 2000,
    ) -> AIResponse:
        """Return a structured response for the supplied messages."""
        ...


class ProviderNotConfiguredError(RuntimeError):
    """Raised when a remote provider is selected without credentials or SDKs."""
