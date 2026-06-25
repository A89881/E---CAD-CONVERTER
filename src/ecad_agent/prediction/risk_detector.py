"""Risk detector placeholder."""

from __future__ import annotations

from ecad_agent.model import CircuitProject
from ecad_agent.validation import validate_project


def detect_design_risks(project: CircuitProject) -> list[str]:
    report = validate_project(project)
    return [issue.message for issue in report.issues if issue.severity == "error"]
