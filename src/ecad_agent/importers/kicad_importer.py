"""KiCad schematic importer placeholder."""

from __future__ import annotations

from pathlib import Path

from ecad_agent.importers.base import ImporterNotImplementedError
from ecad_agent.model import CircuitProject


def load_kicad_schematic(path: str | Path) -> CircuitProject:
    raise ImporterNotImplementedError(
        f"KiCad importer is not implemented yet: {Path(path)}. "
        "Start by mapping symbols, wires, labels, and lib_ids into the neutral model."
    )
