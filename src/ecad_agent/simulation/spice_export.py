"""Simulation-oriented SPICE export entrypoint."""

from __future__ import annotations

from ecad_agent.exporters.spice_exporter import export_spice_netlist
from ecad_agent.model import CircuitProject


def export_simulation_netlist(project: CircuitProject, focus_nets: list[str] | None = None) -> str:
    """Export a SPICE-ready netlist for a full model or selected subcircuit.

    The real SPICE writer is still planned. This wrapper names the future
    simulation boundary separately from general file export.
    """

    del focus_nets
    return export_spice_netlist(project)
