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
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, ConfigDict, Field

from .board import BoardLayout
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
    components: List[Component] = Field(default_factory=list)
    nets: List[Net] = Field(default_factory=list)
    wires: List[Wire] = Field(default_factory=list)
    labels: List[Label] = Field(default_factory=list)
    warnings: List[Warning] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    pcb: Optional[BoardLayout] = Field(
        None,
        description=(
            "Physical PCB layer. When absent the model is schematic-only and still valid. "
            "See docs/internal_model.md for the PCB layer reference."
        ),
    )

    # ---- lookups -----------------------------------------------------------

    def get_component(self, ref: str) -> Optional[Component]:
        """Return the component with the given reference designator, or None."""
        return next((c for c in self.components if c.ref == ref), None)

    def get_net(self, name: str) -> Optional[Net]:
        """Return the net with the given name, or None."""
        return next((n for n in self.nets if n.name == name), None)

    def node_map(self) -> Dict[str, str]:
        """Map every connected pin ('R1.2') to its net name.

        This is the pin-to-net mapping the validation engine and AI layer use.
        """
        mapping: Dict[str, str] = {}
        for net in self.nets:
            for node in net.nodes:
                mapping[node.as_string()] = net.name
        return mapping

    # ---- model-level integrity --------------------------------------------

    def check_integrity(self) -> List[Warning]:
        """Structural self-check of the model itself.

        This is *not* the full validation engine (Workstream D). It only verifies
        that the model is internally consistent: references resolve, ids are
        unique, pins are real. Returns a list of Warning objects.
        """
        out: List[Warning] = []

        # Duplicate reference designators.
        seen: Dict[str, int] = {}
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
            pin_seen: Dict[str, int] = {}
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
                        message=f"Net '{net.name}' references unknown component '{node.component}'.",
                        refs=[net.name, node.component],
                    ))
                elif comp.get_pin(node.pin) is None:
                    out.append(Warning(
                        code="UNKNOWN_PIN", severity=Severity.ERROR,
                        message=f"Net '{net.name}' references pin '{node.pin}' not present on '{node.component}'.",
                        refs=[net.name, node.as_string()],
                    ))

        # Pins that are on no net at all.
        for c in self.components:
            for p in c.pins:
                node = f"{c.ref}.{p.number}"
                if node not in connected:
                    out.append(Warning(
                        code="UNCONNECTED_PIN", severity=Severity.WARNING,
                        message=f"Pin {node} ({p.name or 'unnamed'}) is not on any net.",
                        refs=[node],
                    ))

        # PCB layer integrity (skipped when pcb is None — schematic-only is valid).
        if self.pcb is not None:
            placed_refs: Dict[str, int] = {}
            for placement in self.pcb.placements:
                placed_refs[placement.ref] = placed_refs.get(placement.ref, 0) + 1
                if by_ref.get(placement.ref) is None:
                    out.append(Warning(
                        code="PCB_UNKNOWN_REF", severity=Severity.ERROR,
                        message=f"PCB placement references unknown component '{placement.ref}'.",
                        refs=[placement.ref],
                    ))

            for ref, count in placed_refs.items():
                if count > 1:
                    out.append(Warning(
                        code="PCB_DUPLICATE_PLACEMENT", severity=Severity.ERROR,
                        message=f"Component '{ref}' has {count} placements; expected at most 1.",
                        refs=[ref],
                    ))

            for placement in self.pcb.placements:
                comp = by_ref.get(placement.ref)
                if comp is None or placement.footprint is None:
                    continue
                pin_numbers = {p.number for p in comp.pins}
                for pad in placement.footprint.pads:
                    if pad.number not in pin_numbers:
                        out.append(Warning(
                            code="PCB_PAD_UNKNOWN_PIN", severity=Severity.ERROR,
                            message=(
                                f"Footprint pad '{pad.number}' on placement '{placement.ref}' "
                                f"does not match any pin on that component."
                            ),
                            refs=[placement.ref, f"{placement.ref}.{pad.number}"],
                        ))

            if self.pcb.outline is not None:
                outline = self.pcb.outline
                if len(outline.points) < 3 and not outline.arcs:
                    out.append(Warning(
                        code="PCB_OUTLINE_TOO_FEW_POINTS", severity=Severity.WARNING,
                        message=(
                            f"Board outline has {len(outline.points)} polygon point(s) and no arcs; "
                            "a valid outline needs at least 3 points or at least one arc segment."
                        ),
                        refs=[],
                    ))

        return out

    # ---- counts (handy for validation reports) -----------------------------

    def component_count(self) -> int:
        return len(self.components)

    def net_count(self) -> int:
        return len(self.nets)

    # ---- io ----------------------------------------------------------------

    @classmethod
    def load(cls, path: Union[str, Path]) -> "CircuitProject":
        """Load a model from a JSON file."""
        return cls.model_validate_json(Path(path).read_text(encoding="utf-8"))

    def save(self, path: Union[str, Path]) -> None:
        """Write the model to a JSON file (stable, pretty-printed)."""
        Path(path).write_text(self.to_json(), encoding="utf-8")

    def to_json(self) -> str:
        """Serialise to a pretty JSON string, omitting unset optionals."""
        return self.model_dump_json(indent=2, exclude_none=True)
