"""Internal JSON importer."""

from __future__ import annotations

from pathlib import Path

from ecad_agent.model import CircuitProject


def load_internal_json(path: str | Path) -> CircuitProject:
    return CircuitProject.from_file(path)
