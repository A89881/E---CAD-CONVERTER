"""Net model - the connectivity graph, which is the source of truth.

A Net is an electrical node: the set of pins that are wired together. Each
member is a ``NodeRef`` (component ref + pin number). The compact string form
``R1.2`` is accepted on input and produced by ``NodeRef.as_string()``.

Design decision (the "pin naming format" question from the kickoff):
    canonical node reference = {"component": <ref>, "pin": <pin number>}.
    The string form "<ref>.<pin>" is a convenience, parsed with rpartition so
    that a component ref may itself contain dots if a source format ever needs
    that.
"""

from __future__ import annotations

from enum import Enum
from typing import List

from pydantic import BaseModel, ConfigDict, Field, field_validator


class NetClass(str, Enum):
    """Coarse classification of a net, used by validation and the linter."""

    SIGNAL = "signal"
    POWER = "power"
    GROUND = "ground"
    UNSPECIFIED = "unspecified"


class NodeRef(BaseModel):
    """A reference to one pin of one component, e.g. component 'R1', pin '2'."""

    model_config = ConfigDict(extra="forbid")

    component: str = Field(..., description="Reference designator, e.g. 'R1'.")
    pin: str = Field(..., description="Pin number on that component, e.g. '2'.")

    def as_string(self) -> str:
        """Render as the compact 'REF.PIN' form."""
        return f"{self.component}.{self.pin}"

    @classmethod
    def from_string(cls, s: str) -> "NodeRef":
        """Parse 'REF.PIN' into a NodeRef. Splits on the *last* dot."""
        component, sep, pin = s.rpartition(".")
        if not sep or not component or not pin:
            raise ValueError(f"Invalid node reference {s!r}; expected 'REF.PIN'.")
        return cls(component=component, pin=pin)


class Net(BaseModel):
    """An electrical net: the set of pins tied together at one potential."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., description="Net name, e.g. 'VOUT', 'GND'.")
    net_class: NetClass = Field(
        default=NetClass.UNSPECIFIED, description="Coarse net classification."
    )
    nodes: List[NodeRef] = Field(
        default_factory=list,
        description="Pins on this net. May be written as 'R1.2' strings in JSON.",
    )

    @field_validator("nodes", mode="before")
    @classmethod
    def _coerce_nodes(cls, value: object) -> object:
        """Allow nodes to be given as compact 'REF.PIN' strings in JSON."""
        if not isinstance(value, list):
            return value
        return [NodeRef.from_string(item) if isinstance(item, str) else item for item in value]
