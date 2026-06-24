"""Structured context for AI review workflows."""

from __future__ import annotations

from typing import Any

from ecad_agent.model import CircuitProject
from ecad_agent.validation import ValidationReport, canonical_connectivity


def build_review_context(
    project: CircuitProject,
    validation_report: ValidationReport | None = None,
) -> dict[str, Any]:
    """Create AI-ready context without handing raw ECAD files to an LLM."""

    context: dict[str, Any] = {
        "project": {
            "name": project.name,
            "source_format": project.source_format,
            "schema_version": project.schema_version,
        },
        "components": [component.to_dict() for component in project.components],
        "nets": [net.to_dict() for net in project.nets],
        "connectivity": canonical_connectivity(project),
        "warnings": [warning.to_dict() for warning in project.warnings],
    }
    if validation_report is not None:
        context["validation"] = validation_report.to_dict()
    return context
