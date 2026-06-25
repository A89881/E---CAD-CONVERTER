"""CircuitProject - the root of the neutral internal ECAD model.

Every importer produces a CircuitProject; every exporter consumes one; every
validator and AI agent reasons over one. The connectivity graph (nets) is the
source of truth.

Serialised shape::

    {
      "project":   {"name": ..., "source_format": ..., "schema_version": ...},
      "components": [...],
      "nets":       [...],
      "wires":      [...],
      "labels":     [...],
      "warnings":   [...],
      "metadata":   {...}
    }
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from .component import Component
from .graphics import Label, Wire
from .net import Net
from .warning import Severity, Warning

SCHEMA_VERSION = "0.1.0"


class ProjectInfo(BaseModel):
    """Top-level metadata about the design."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., description="Human project / schematic name.")
    source_format: str = Field(
        ..., description="Origin format: 'kicad' | 'easyeda' | 'eagle' | 'internal'."
    )
    schema_version: str = Field(
        default=SCHEMA_VERSION, description="Internal-model schema version this file targets."
    )


class CircuitProject(BaseModel):
    """The neutral internal circuit model."""

    model_config = ConfigDict(extra="forbid")

    project: ProjectInfo
    components: list[Component] = Field(default_factory=list)
    nets: list[Net] = Field(default_factory=list)
    wires: list[Wire] = Field(default_factory=list)
    labels: list[Label] = Field(default_factory=list)
    warnings: list[Warning] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    # ---- compatibility / convenience --------------------------------------

    @property
    def name(self) -> str:
        """Project name shortcut used by exporters, validators, and CLI code."""
        return self.project.name

    @property
    def source_format(self) -> str:
        """Source format shortcut."""
        return self.project.source_format

    @property
    def schema_version(self) -> str:
        """Schema version shortcut."""
        return self.project.schema_version

    # ---- lookups -----------------------------------------------------------

    def get_component(self, ref: str) -> Component | None:
        """Return the component with the given reference designator, or None."""
        return next((c for c in self.components if c.ref == ref), None)

    def get_net(self, name: str) -> Net | None:
        """Return the net with the given name, or None."""
        return next((n for n in self.nets if n.name == name), None)

    def node_map(self) -> dict[str, str]:
        """Map every connected pin ('R1.2') to its net name.

        This is the pin-to-net mapping the validation engine and AI layer use.
        """
        mapping: dict[str, str] = {}
        for net in self.nets:
            for node in net.nodes:
                mapping[node.as_string()] = net.name
        return mapping

    def pin_to_net_mapping(self) -> dict[str, str]:
        """Backward-compatible alias for :meth:`node_map`."""
        return self.node_map()

    # ---- model-level integrity --------------------------------------------

    def check_integrity(self) -> list[Warning]:
        """Structural self-check of the model itself.

        This is *not* the full validation engine (Workstream D). It only verifies
        that the model is internally consistent: references resolve, ids are
        unique, pins are real. Returns a list of Warning objects.
        """
        out: list[Warning] = []

        # Duplicate reference designators.
        seen: dict[str, int] = {}
        for c in self.components:
            seen[c.ref] = seen.get(c.ref, 0) + 1
        for ref, count in seen.items():
            if count > 1:
                out.append(Warning(
                    code="DUPLICATE_REF", severity=Severity.ERROR,
                    message=f"Reference designator '{ref}' is used {count} times.",
                    refs=[ref],
                ))

        # Duplicate pin numbers within a component.
        for c in self.components:
            pin_seen: dict[str, int] = {}
            for p in c.pins:
                pin_seen[p.number] = pin_seen.get(p.number, 0) + 1
            for num, count in pin_seen.items():
                if count > 1:
                    out.append(Warning(
                        code="DUPLICATE_PIN", severity=Severity.ERROR,
                        message=f"Component '{c.ref}' has pin '{num}' {count} times.",
                        refs=[f"{c.ref}.{num}"],
                    ))

        # Net node references must resolve to a real component + pin.
        by_ref = {c.ref: c for c in self.components}
        connected: set[str] = set()
        for net in self.nets:
            if len(net.nodes) < 2:
                out.append(Warning(
                    code="DANGLING_NET", severity=Severity.WARNING,
                    message=f"Net '{net.name}' has {len(net.nodes)} node(s); expected at least 2.",
                    refs=[net.name],
                ))
            for node in net.nodes:
                connected.add(node.as_string())
                comp = by_ref.get(node.component)
                if comp is None:
                    out.append(Warning(
                        code="UNKNOWN_COMPONENT", severity=Severity.ERROR,
                        message=(
                            f"Net '{net.name}' references unknown component "
                            f"'{node.component}'."
                        ),
                        refs=[net.name, node.component],
                    ))
                elif comp.get_pin(node.pin) is None:
                    out.append(Warning(
                        code="UNKNOWN_PIN", severity=Severity.ERROR,
                        message=(
                            f"Net '{net.name}' references pin '{node.pin}' "
                            f"not present on '{node.component}'."
                        ),
                        refs=[net.name, node.as_string()],
                    ))

        # Pins that are on no net at all.
        for c in self.components:
            for p in c.pins:
                node_id = f"{c.ref}.{p.number}"
                if node_id not in connected:
                    out.append(Warning(
                        code="UNCONNECTED_PIN", severity=Severity.WARNING,
                        message=f"Pin {node_id} ({p.name or 'unnamed'}) is not on any net.",
                        refs=[node_id],
                    ))

        return out

    # ---- counts (handy for validation reports) -----------------------------

    def component_count(self) -> int:
        return len(self.components)

    def net_count(self) -> int:
        return len(self.nets)

    # ---- io ----------------------------------------------------------------

    @classmethod
    def load(cls, path: str | Path) -> CircuitProject:
        """Load a model from a JSON file."""
        return cls.model_validate_json(Path(path).read_text(encoding="utf-8"))

    @classmethod
    def from_file(cls, path: str | Path) -> CircuitProject:
        """Backward-compatible alias for :meth:`load`."""
        return cls.load(path)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> CircuitProject:
        """Load a model from a Python dictionary."""
        return cls.model_validate(payload)

    def save(self, path: str | Path) -> None:
        """Write the model to a JSON file (stable, pretty-printed)."""
        Path(path).write_text(self.to_json(), encoding="utf-8")

    def to_json(self) -> str:
        """Serialise to a pretty JSON string, omitting unset optionals."""
        return self.model_dump_json(indent=2, exclude_none=True)

    def to_dict(self) -> dict[str, Any]:
        """Serialise to a JSON-compatible dictionary."""
        return self.model_dump(mode="json", exclude_none=True)
