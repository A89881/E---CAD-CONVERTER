"""SPICE exporter placeholder."""

from __future__ import annotations

from ecad_agent.model import CircuitProject


def export_spice_netlist(project: CircuitProject) -> str:
    raise NotImplementedError(
        f"SPICE export is not implemented yet for project {project.name!r}. "
        "Add this after the internal model and KiCad path are stable."
    )
