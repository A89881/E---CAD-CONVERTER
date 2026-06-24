"""Pin model."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class Pin:
    """A component pin and its logical net assignment."""

    number: str
    name: str | None = None
    net: str | None = None
    electrical_type: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def node_id(self, component_ref: str) -> str:
        """Return the canonical graph node ID for this pin."""

        return f"{component_ref}.{self.number}"

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {"number": self.number}
        if self.name is not None:
            payload["name"] = self.name
        if self.net is not None:
            payload["net"] = self.net
        if self.electrical_type is not None:
            payload["electrical_type"] = self.electrical_type
        if self.metadata:
            payload["metadata"] = self.metadata
        return payload

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> Pin:
        return cls(
            number=str(payload["number"]),
            name=payload.get("name"),
            net=payload.get("net"),
            electrical_type=payload.get("electrical_type"),
            metadata=dict(payload.get("metadata", {})),
        )
