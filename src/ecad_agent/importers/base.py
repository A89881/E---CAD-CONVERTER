"""Importer contracts."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

from ecad_agent.model import CircuitProject


class Importer(Protocol):
    """Importer protocol for source-format implementations."""

    def load(self, path: Path) -> CircuitProject:
        """Parse a source artifact into a neutral circuit project."""
        ...


class ImporterNotImplementedError(NotImplementedError):
    """Raised by scaffolded importers that do not parse a format yet."""
