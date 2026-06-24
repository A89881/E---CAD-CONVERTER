"""Circuit project model."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ecad_agent.model.component import Component
from ecad_agent.model.net import Net
from ecad_agent.model.warning import WarningMessage


@dataclass(slots=True)
class Wire:
    """A visual schematic wire with optional net association."""

    start: tuple[float, float]
    end: tuple[float, float]
    net: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {"start": list(self.start), "end": list(self.end)}
        if self.net is not None:
            payload["net"] = self.net
        if self.metadata:
            payload["metadata"] = self.metadata
        return payload

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> Wire:
        start = payload.get("start", [0.0, 0.0])
        end = payload.get("end", [0.0, 0.0])
        return cls(
            start=(float(start[0]), float(start[1])),
            end=(float(end[0]), float(end[1])),
            net=payload.get("net"),
            metadata=dict(payload.get("metadata", {})),
        )


@dataclass(slots=True)
class Label:
    """A schematic label tied to a logical net."""

    text: str
    net: str | None = None
    at: tuple[float, float] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {"text": self.text}
        if self.net is not None:
            payload["net"] = self.net
        if self.at is not None:
            payload["at"] = list(self.at)
        if self.metadata:
            payload["metadata"] = self.metadata
        return payload

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> Label:
        at = payload.get("at")
        return cls(
            text=str(payload["text"]),
            net=payload.get("net"),
            at=(float(at[0]), float(at[1])) if at else None,
            metadata=dict(payload.get("metadata", {})),
        )


@dataclass(slots=True)
class CircuitProject:
    """Tool-independent ECAD circuit representation."""

    name: str
    source_format: str = "internal-json"
    schema_version: str = "0.1.0"
    components: list[Component] = field(default_factory=list)
    nets: list[Net] = field(default_factory=list)
    wires: list[Wire] = field(default_factory=list)
    labels: list[Label] = field(default_factory=list)
    warnings: list[WarningMessage] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def component_by_ref(self) -> dict[str, Component]:
        return {component.ref: component for component in self.components}

    def net_by_name(self) -> dict[str, Net]:
        return {net.name: net for net in self.nets}

    def pin_to_net_mapping(self) -> dict[str, str]:
        mapping: dict[str, str] = {}
        for component in self.components:
            for pin in component.pins:
                if pin.net is not None:
                    mapping[pin.node_id(component.ref)] = pin.net
        return mapping

    def all_node_ids(self) -> set[str]:
        return {
            pin.node_id(component.ref)
            for component in self.components
            for pin in component.pins
        }

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "schema_version": self.schema_version,
            "project": {
                "name": self.name,
                "source_format": self.source_format,
            },
            "components": [component.to_dict() for component in self.components],
            "nets": [net.to_dict() for net in self.nets],
            "wires": [wire.to_dict() for wire in self.wires],
            "labels": [label.to_dict() for label in self.labels],
            "warnings": [warning.to_dict() for warning in self.warnings],
        }
        if self.metadata:
            payload["project"]["metadata"] = self.metadata
        return payload

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, sort_keys=True) + "\n"

    def write_json(self, path: str | Path) -> Path:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(self.to_json(), encoding="utf-8")
        return target

    @classmethod
    def from_file(cls, path: str | Path) -> CircuitProject:
        return cls.from_json(Path(path).read_text(encoding="utf-8"))

    @classmethod
    def from_json(cls, content: str) -> CircuitProject:
        return cls.from_dict(json.loads(content))

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> CircuitProject:
        project_payload = dict(payload.get("project", {}))
        name = str(project_payload.get("name", payload.get("name", "unnamed_project")))
        source_format = str(
            project_payload.get("source_format", payload.get("source_format", "unknown"))
        )

        return cls(
            name=name,
            source_format=source_format,
            schema_version=str(payload.get("schema_version", "0.1.0")),
            components=[Component.from_dict(dict(item)) for item in payload.get("components", [])],
            nets=[Net.from_dict(dict(item)) for item in payload.get("nets", [])],
            wires=[Wire.from_dict(dict(item)) for item in payload.get("wires", [])],
            labels=[Label.from_dict(dict(item)) for item in payload.get("labels", [])],
            warnings=[WarningMessage.from_dict(dict(item)) for item in payload.get("warnings", [])],
            metadata=dict(project_payload.get("metadata", payload.get("metadata", {}))),
        )
