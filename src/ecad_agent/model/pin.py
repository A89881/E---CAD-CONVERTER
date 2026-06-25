"""Pin model.

A Pin is a connection point on a Component. Its ``number`` is the stable
identifier used everywhere connectivity is referenced (see ``net.NodeRef``).
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class ElectricalType(str, Enum):
    """Coarse electrical role of a pin.

    Kept deliberately small for the MVP. Importers map source-format pin types
    onto these; ``unspecified`` is always a safe default.
    """

    INPUT = "input"
    OUTPUT = "output"
    BIDIRECTIONAL = "bidirectional"
    POWER_IN = "power_in"
    POWER_OUT = "power_out"
    PASSIVE = "passive"
    UNSPECIFIED = "unspecified"


class Pin(BaseModel):
    """A single pin on a component.

    The ``number`` field is the *identity* of the pin and is what net node
    references point at (e.g. ``R1.2`` -> component ``R1``, pin number ``2``).
    It is a string, not an int, because real pins are labelled ``1``, ``2``,
    ``A3``, ``E13``, etc.
    """

    model_config = ConfigDict(extra="forbid")

    number: str = Field(
        ...,
        description="Stable pin identifier within its component, e.g. '1', '2', 'A3'.",
    )
    name: str | None = Field(
        None,
        description="Functional pin name where the source provides one, e.g. 'VCC', 'OUT'.",
    )
    electrical_type: ElectricalType = Field(
        default=ElectricalType.UNSPECIFIED,
        description="Coarse electrical role; defaults to 'unspecified'.",
    )
