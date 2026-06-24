"""Net model."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class Net:
    """A logical electrical net made of component pin nodes."""

    name: str
    nodes: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {"name": self.name, "nodes": list(self.nodes)}
        if self.metadata:
            payload["metadata"] = self.metadata
        return payload

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> Net:
        return cls(
            name=str(payload["name"]),
            nodes=[str(node) for node in payload.get("nodes", [])],
            metadata=dict(payload.get("metadata", {})),
        )
