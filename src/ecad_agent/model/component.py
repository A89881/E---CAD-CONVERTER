"""Component model."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ecad_agent.model.pin import Pin


@dataclass(slots=True)
class Component:
    """A schematic component with pins and optional source metadata."""

    ref: str
    type: str
    value: str | None = None
    symbol: str | None = None
    footprint: str | None = None
    pins: list[Pin] = field(default_factory=list)
    source_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def pin(self, number: str) -> Pin | None:
        for pin in self.pins:
            if pin.number == number:
                return pin
        return None

    def pin_node_ids(self) -> list[str]:
        return [pin.node_id(self.ref) for pin in self.pins]

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "ref": self.ref,
            "type": self.type,
            "pins": [pin.to_dict() for pin in self.pins],
        }
        if self.value is not None:
            payload["value"] = self.value
        if self.symbol is not None:
            payload["symbol"] = self.symbol
        if self.footprint is not None:
            payload["footprint"] = self.footprint
        if self.source_id is not None:
            payload["source_id"] = self.source_id
        if self.metadata:
            payload["metadata"] = self.metadata
        return payload

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> Component:
        raw_pins = payload.get("pins", [])
        if isinstance(raw_pins, dict):
            pins = [
                Pin(number=str(number), net=str(net) if net is not None else None)
                for number, net in raw_pins.items()
            ]
        else:
            pins = [Pin.from_dict(dict(item)) for item in raw_pins]

        return cls(
            ref=str(payload["ref"]),
            type=str(payload.get("type", "unknown")),
            value=payload.get("value"),
            symbol=payload.get("symbol"),
            footprint=payload.get("footprint"),
            pins=pins,
            source_id=payload.get("source_id"),
            metadata=dict(payload.get("metadata", {})),
        )
