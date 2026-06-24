"""Neutral internal ECAD model.

Public API::

    from ecad_agent.model import CircuitProject, Component, Pin, Net, NodeRef

    circuit = CircuitProject.load("examples/rc_filter/model.json")
    print(circuit.components)
    print(circuit.nets)
    print(circuit.node_map())          # {'R1.1': 'VIN', ...}
    for w in circuit.check_integrity():
        print(w.severity, w.code, w.message)
"""

from __future__ import annotations

from .component import Component
from .graphics import Footprint, Label, Point, Symbol, Wire
from .net import Net, NetClass, NodeRef
from .pin import ElectricalType, Pin
from .project import SCHEMA_VERSION, CircuitProject, ProjectInfo
from .warning import Severity, ValidationResult, Warning

__all__ = [
    "CircuitProject",
    "ProjectInfo",
    "Component",
    "Pin",
    "ElectricalType",
    "Net",
    "NetClass",
    "NodeRef",
    "Wire",
    "Label",
    "Point",
    "Symbol",
    "Footprint",
    "Warning",
    "Severity",
    "ValidationResult",
    "SCHEMA_VERSION",
]
