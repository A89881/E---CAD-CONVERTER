"""Graphical and library models.

These carry *source* detail that is not needed to know the connectivity but is
needed to round-trip a schematic faithfully and to do symbol/footprint mapping.
For the first MVP they are optional - connectivity comes from Net, not Wire.
"""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class Point(BaseModel):
    """A 2D point in schematic coordinates (units are source-defined)."""

    model_config = ConfigDict(extra="forbid")

    x: float
    y: float


class Wire(BaseModel):
    """A drawn wire segment / polyline. Graphical; connectivity is in Net."""

    model_config = ConfigDict(extra="forbid")

    points: List[Point] = Field(default_factory=list, description="Ordered vertices.")
    net: Optional[str] = Field(None, description="Net this wire belongs to, if known.")


class Label(BaseModel):
    """A net label placed in the schematic."""

    model_config = ConfigDict(extra="forbid")

    text: str = Field(..., description="Label text, usually the net name.")
    net: Optional[str] = Field(None, description="Net this label assigns, if resolved.")
    position: Optional[Point] = None
    kind: Optional[str] = Field(
        None, description="Source label scope: 'local' | 'global' | 'hierarchical' | 'power'."
    )


class Symbol(BaseModel):
    """A schematic symbol library reference (the thing Component.symbol names)."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(..., description="Library id, e.g. 'Device:R'.")
    name: Optional[str] = None
    library: Optional[str] = None
    pin_count: Optional[int] = None


class Footprint(BaseModel):
    """A PCB footprint library reference (the thing Component.footprint names)."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(..., description="Library id, e.g. 'Resistor_SMD:R_0603'.")
    name: Optional[str] = None
    library: Optional[str] = None
