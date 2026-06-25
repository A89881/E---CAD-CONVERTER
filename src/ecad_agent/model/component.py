"""Component model.

A Component is one part in the design (resistor, capacitor, IC, power flag,
connector, ...). It owns its pins. Connectivity between components lives in
``Net`` objects, not here - this keeps the circuit graph in one place.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from .pin import Pin


class Component(BaseModel):
    """A single component / part instance.

    ``ref`` (the reference designator) must be unique across a project; it is
    the anchor used by net node references and warnings.
    """

    model_config = ConfigDict(extra="forbid")

    ref: str = Field(
        ...,
        description="Reference designator, unique in the project, e.g. 'R1', 'U3', '#PWR01'.",
    )
    type: str = Field(
        ...,
        description=(
            "Generic component type, e.g. 'resistor', 'capacitor', 'ic', "
            "'diode', 'power', 'ground'."
        ),
    )
    value: str | None = Field(
        None, description="Component value, e.g. '10k', '100nF', 'TL071'."
    )
    symbol: str | None = Field(
        None, description="Source symbol id, e.g. 'Device:R'. See Symbol for library detail."
    )
    footprint: str | None = Field(
        None,
        description=(
            "Footprint id, e.g. 'Resistor_SMD:R_0603'. "
            "See Footprint for library detail."
        ),
    )
    pins: list[Pin] = Field(
        default_factory=list, description="Pins on this component."
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Free-form source-specific extras that have no first-class field yet.",
    )

    def pin_numbers(self) -> list[str]:
        """Return all pin numbers on this component."""
        return [p.number for p in self.pins]

    def get_pin(self, number: str) -> Pin | None:
        """Return the pin with the given number, or None."""
        return next((p for p in self.pins if p.number == number), None)
