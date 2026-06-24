"""EAGLE XML importer placeholder."""

from __future__ import annotations

from pathlib import Path

from ecad_agent.importers.base import ImporterNotImplementedError
from ecad_agent.model import CircuitProject


def load_eagle_xml(path: str | Path) -> CircuitProject:
    raise ImporterNotImplementedError(
        f"EAGLE XML importer is not implemented yet: {Path(path)}. "
        "Start by mapping parts, instances, nets, segments, gates, and pins."
    )
