"""Physical PCB layer — board layout, footprints, placements, and stack-up.

This module adds the physical layer to the neutral internal model. It is
intentionally tool-independent: no KiCad format assumptions, no S-expression
concerns, no .kicad_* anything.

The schematic connectivity graph (Net / NodeRef in net.py) remains the single
source of truth for what is electrically connected. The PCB layer references
Component refs and Pin numbers from the schematic; it never duplicates net
membership.

Pad-to-pin mapping rule:
    PadDef.number == Pin.number on the placed component — same string, same
    identity. This is documented convention, not enforced by a validator,
    because legacy source formats can occasionally diverge.

Routing is intentionally excluded from this pass. Tracks, vias, and copper
pours are not modelled here. The schematic nets are the sole connectivity
source of truth.
"""

from __future__ import annotations

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from .graphics import Point


class BoardSide(str, Enum):
    """Which physical side of the board a component is mounted on."""

    TOP = "top"
    BOTTOM = "bottom"


class PadShape(str, Enum):
    """Coarse pad shape. Importers map tool-specific shapes onto these."""

    CIRCLE = "circle"
    RECT = "rect"
    OVAL = "oval"


class PadType(str, Enum):
    """How the pad connects through the board."""

    SMD = "smd"
    THROUGH_HOLE = "through_hole"
    NPTH = "npth"


class PadDef(BaseModel):
    """One pad in a footprint.

    ``number`` must equal the ``Pin.number`` on the owning component — that
    string equality is the pad-to-pin mapping. See module docstring.
    """

    model_config = ConfigDict(extra="forbid")

    number: str = Field(
        ...,
        description="Pad identifier; must equal the Pin.number it maps to, e.g. '1', 'A3'.",
    )
    pad_type: PadType = Field(
        default=PadType.SMD,
        description="SMD, through-hole, or non-plated through-hole.",
    )
    shape: PadShape = Field(default=PadShape.RECT, description="Coarse pad shape.")
    size_x: float = Field(..., description="Pad width in mm.")
    size_y: float = Field(..., description="Pad height in mm.")
    position: Point = Field(
        ...,
        description="Pad centre relative to the footprint origin, in mm.",
    )
    drill_diameter: Optional[float] = Field(
        None,
        description="Drill diameter in mm. Required for through_hole and npth pads.",
    )
    layers: List[str] = Field(
        default_factory=lambda: ["front_copper"],
        description=(
            "Neutral copper-layer names this pad occupies. "
            "Typical values: 'front_copper', 'back_copper'. "
            "Not cross-validated against BoardLayout.layer_stack in this pass."
        ),
    )


class FootprintDef(BaseModel):
    """Physical footprint — pad layout with optional metadata.

    Embedded directly inside Placement (one footprint per placed component).
    This avoids a shared-library lookup for the first pass; the team can
    factor out a footprint_library dict in a later workstream if duplication
    becomes a concern (see Open Decisions in docs/internal_model.md).
    """

    model_config = ConfigDict(extra="forbid")

    library_ref: Optional[str] = Field(
        None,
        description="Source footprint library id, e.g. 'Resistor_SMD:R_0603'. Informational only.",
    )
    pads: List[PadDef] = Field(
        default_factory=list,
        description=(
            "All pads in this footprint. Each pad.number must match a "
            "Pin.number on the component this footprint is assigned to."
        ),
    )
    model_3d: Optional[str] = Field(
        None,
        description=(
            "Opaque 3D model identifier (e.g. a file path or asset key). "
            "No geometry is stored — this is a reference only."
        ),
    )


class Placement(BaseModel):
    """Where and how a component is placed on the board.

    ``ref`` must match a Component.ref in the schematic layer. Power/ground
    symbols (#PWR*, #FLG*) are typically omitted from placements because they
    are logical constructs with no physical package.
    """

    model_config = ConfigDict(extra="forbid")

    ref: str = Field(
        ...,
        description="Component reference designator, e.g. 'R1', 'U3'.",
    )
    x: float = Field(..., description="X position of the component origin on the board, in mm.")
    y: float = Field(..., description="Y position of the component origin on the board, in mm.")
    rotation: float = Field(
        default=0.0,
        description="Rotation in degrees, clockwise from the component's default orientation.",
    )
    side: BoardSide = Field(
        default=BoardSide.TOP,
        description="Which side of the board the component is mounted on.",
    )
    footprint: Optional[FootprintDef] = Field(
        None,
        description=(
            "Physical footprint definition. May be omitted when only placement "
            "position is known and pad detail is not yet captured."
        ),
    )


class LayerKind(str, Enum):
    """Broad functional category of a board layer."""

    COPPER = "copper"
    DIELECTRIC = "dielectric"
    SILK = "silk"
    MASK = "mask"


class StackLayer(BaseModel):
    """One layer in the board stack-up.

    Layer names are neutral strings — not KiCad or Altium specific. Exporters
    map these to tool-specific identifiers. Recommended naming conventions:
      copper   : 'front_copper', 'back_copper', 'inner_copper_1', ...
      dielectric: 'prepreg_1', 'core_1', ...
      silk     : 'front_silk', 'back_silk'
      mask     : 'front_mask', 'back_mask'
    """

    model_config = ConfigDict(extra="forbid")

    name: str = Field(
        ...,
        description=(
            "Neutral layer name, e.g. 'front_copper', 'back_copper', "
            "'prepreg_1', 'core_1', 'front_silk', 'front_mask'."
        ),
    )
    kind: LayerKind = Field(..., description="Broad layer category.")
    thickness_mm: Optional[float] = Field(
        None,
        description="Layer thickness in mm. Optional; useful for impedance modelling.",
    )


class ArcSegment(BaseModel):
    """An arc segment in the board outline.

    Defined by start/end points on the arc and the centre of the circle.
    This allows rounded corners and non-rectangular outlines to be represented.

    Note: this is a structural stub for the first pass. How exporters should
    interpret overlapping arc/polygon segments is an open design decision —
    see docs/internal_model.md.
    """

    model_config = ConfigDict(extra="forbid")

    start: Point = Field(..., description="Arc start point, in mm.")
    end: Point = Field(..., description="Arc end point, in mm.")
    center: Point = Field(..., description="Centre of the circle the arc lies on, in mm.")


class BoardOutline(BaseModel):
    """The PCB edge / board outline.

    Represented as a combination of polygon vertices (for straight edges) and
    arc segments (for curved edges). A simple rectangular board populates
    ``points`` with four corners and leaves ``arcs`` empty.

    At least one of ``points`` or ``arcs`` should be non-empty; check_integrity
    emits PCB_OUTLINE_TOO_FEW_POINTS if both are effectively empty.
    """

    model_config = ConfigDict(extra="forbid")

    points: List[Point] = Field(
        default_factory=list,
        description=(
            "Ordered polygon vertices for straight outline segments, in mm. "
            "For a closed polygon the first and last points need not repeat."
        ),
    )
    arcs: List[ArcSegment] = Field(
        default_factory=list,
        description=(
            "Arc segments in the board outline (e.g. rounded corners). "
            "See ArcSegment and Open Decisions in docs/internal_model.md."
        ),
    )


class BoardLayout(BaseModel):
    """The physical PCB layer — optional attachment to CircuitProject.

    When ``CircuitProject.pcb`` is None the model is schematic-only and fully
    valid. This is the root of all physical board data.

    Routing (tracks, vias, copper pours) is intentionally excluded from this
    pass. The schematic nets remain the sole connectivity source of truth.
    """

    model_config = ConfigDict(extra="forbid")

    placements: List[Placement] = Field(
        default_factory=list,
        description="One entry per physically placed component.",
    )
    layer_stack: List[StackLayer] = Field(
        default_factory=list,
        description="Ordered stack-up from top to bottom. May be empty if unknown.",
    )
    outline: Optional[BoardOutline] = Field(
        None,
        description="Board outline / edge cuts. Absent means outline not yet defined.",
    )
