"""Internal JSON exporter."""

from __future__ import annotations

from pathlib import Path

from ecad_agent.model import CircuitProject


def export_internal_json(project: CircuitProject, path: str | Path | None = None) -> str:
    content = project.to_json()
    if path is not None:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    return content
