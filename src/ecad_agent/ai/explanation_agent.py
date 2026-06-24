"""Prompt templates for future explanation workflows."""

from __future__ import annotations

from ecad_agent.model import CircuitProject


def circuit_explanation_prompt(project: CircuitProject) -> str:
    return (
        "Explain this circuit using only the structured component, pin, net, "
        f"and warning data for project {project.name!r}. Cite specific refs, pins, and nets."
    )
