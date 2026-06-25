"""Rule-backed design suggestions for the early copilot."""

from __future__ import annotations

from ecad_agent.model import CircuitProject
from ecad_agent.validation import validate_project


def suggest_design_actions(project: CircuitProject) -> list[str]:
    """Create simple deterministic suggestions from validation signals."""

    report = validate_project(project)
    suggestions: list[str] = []
    issue_codes = {issue.code for issue in report.issues}

    if "unconnected-pin" in issue_codes:
        suggestions.append("Inspect unconnected pins and confirm whether they are intentional.")
    if "missing-footprint" in issue_codes:
        suggestions.append("Add footprint mappings before PCB handoff or manufacturing export.")
    if "missing-symbol" in issue_codes:
        suggestions.append("Resolve missing symbol mappings before format conversion.")
    if not suggestions:
        suggestions.append("No deterministic design suggestions were generated from validation.")
    return suggestions
