"""Project sync envelope used by ECAD tool wrappers."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ecad_agent.model import CircuitProject


@dataclass(frozen=True, slots=True)
class ProjectSyncEnvelope:
    """Payload shape wrappers send to the backend intelligence layer."""

    wrapper: str
    source_format: str
    project: CircuitProject
    files: dict[str, str] = field(default_factory=dict)
    capabilities: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "wrapper": self.wrapper,
            "source_format": self.source_format,
            "project": self.project.to_dict(),
            "files": self.files,
            "capabilities": self.capabilities,
            "metadata": self.metadata,
        }


def build_sync_envelope(
    project: CircuitProject,
    wrapper: str,
    files: dict[str, str] | None = None,
    capabilities: list[str] | None = None,
    metadata: dict[str, Any] | None = None,
) -> ProjectSyncEnvelope:
    return ProjectSyncEnvelope(
        wrapper=wrapper,
        source_format=project.source_format,
        project=project,
        files=files or {},
        capabilities=capabilities or [],
        metadata=metadata or {},
    )
