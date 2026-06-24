"""EasyEDA importer placeholder."""

from __future__ import annotations

from pathlib import Path

from ecad_agent.importers.base import ImporterNotImplementedError
from ecad_agent.model import CircuitProject


def load_easyeda_json(path: str | Path) -> CircuitProject:
    raise ImporterNotImplementedError(
        f"EasyEDA importer is not implemented yet: {Path(path)}. "
        "Start by preserving component IDs, pin mappings, labels, and net names."
    )
