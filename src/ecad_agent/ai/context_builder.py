"""Copilot context builder with token-budget levels."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from ecad_agent.ai.prompts import COPILOT_SYSTEM_PROMPT
from ecad_agent.ai.providers import AIMessage
from ecad_agent.model import CircuitProject, Component, Net, NodeRef, Warning
from ecad_agent.validation import ValidationReport, canonical_connectivity


class ContextBudget(str, Enum):
    """Context size tiers for ECAD copilot requests."""

    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"

    @property
    def max_tokens(self) -> int:
        if self is ContextBudget.SMALL:
            return 900
        if self is ContextBudget.MEDIUM:
            return 2000
        return 5000


@dataclass(frozen=True, slots=True)
class ContextSelection:
    """Optional user focus from a wrapper or UI."""

    components: list[str] = field(default_factory=list)
    nets: list[str] = field(default_factory=list)
    warning_codes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, list[str]]:
        return {
            "components": self.components,
            "nets": self.nets,
            "warning_codes": self.warning_codes,
        }


@dataclass(frozen=True, slots=True)
class CopilotContext:
    """Structured context sent to an AI provider."""

    task: str
    question: str
    budget: ContextBudget
    payload: dict[str, Any]
    estimated_tokens: int

    def to_messages(self) -> list[AIMessage]:
        return [
            AIMessage(role="system", content=COPILOT_SYSTEM_PROMPT),
            AIMessage(role="user", content=json.dumps(self.payload, sort_keys=True)),
        ]


class ContextBuilder:
    """Build grounded AI context from the neutral circuit model."""

    def build(
        self,
        project: CircuitProject,
        question: str,
        task: str = "ask_about_circuit",
        budget: ContextBudget = ContextBudget.MEDIUM,
        selection: ContextSelection | None = None,
        validation_report: ValidationReport | None = None,
    ) -> CopilotContext:
        selected = selection or ContextSelection()
        payload = self._payload_for_budget(
            project=project,
            question=question,
            task=task,
            budget=budget,
            selection=selected,
            validation_report=validation_report,
        )
        return CopilotContext(
            task=task,
            question=question,
            budget=budget,
            payload=payload,
            estimated_tokens=_estimate_tokens(payload),
        )

    def _payload_for_budget(
        self,
        project: CircuitProject,
        question: str,
        task: str,
        budget: ContextBudget,
        selection: ContextSelection,
        validation_report: ValidationReport | None,
    ) -> dict[str, Any]:
        components, nets = _select_context(project, budget, selection)
        payload: dict[str, Any] = {
            "architecture": "ECAD Copilot Extension Framework",
            "task": task,
            "question": question,
            "budget": budget.value,
            "project": {
                "name": project.name,
                "source_format": project.source_format,
                "schema_version": project.schema_version,
            },
            "focus": selection.to_dict(),
            "components": [_component_payload(component) for component in components],
            "nets": [_net_payload(net) for net in nets],
            "connectivity": {
                net.name: tuple(_node_id(node) for node in net.nodes)
                for net in nets
            },
            "warnings": _warnings_for_selection(project.warnings, selection),
        }
        if budget is not ContextBudget.SMALL:
            payload["full_connectivity"] = canonical_connectivity(project)
        if budget is ContextBudget.LARGE:
            payload["model"] = project.to_dict()
        if validation_report is not None:
            payload["validation"] = validation_report.to_dict()
        return payload


def _select_context(
    project: CircuitProject,
    budget: ContextBudget,
    selection: ContextSelection,
) -> tuple[list[Component], list[Net]]:
    if budget is ContextBudget.LARGE:
        return list(project.components), list(project.nets)

    if budget is ContextBudget.MEDIUM and not selection.components and not selection.nets:
        return list(project.components), list(project.nets)

    selected_component_refs = set(selection.components)
    selected_net_names = set(selection.nets)

    for net in project.nets:
        if net.name in selected_net_names:
            selected_component_refs.update(node.component for node in net.nodes)

    for component_ref in list(selected_component_refs):
        for net in project.nets:
            if any(node.component == component_ref for node in net.nodes):
                selected_net_names.add(net.name)

    if not selected_component_refs and not selected_net_names:
        return list(project.components), list(project.nets)

    selected_nets = [net for net in project.nets if net.name in selected_net_names]
    for net in selected_nets:
        selected_component_refs.update(node.component for node in net.nodes)

    selected_components = [
        component for component in project.components if component.ref in selected_component_refs
    ]
    return selected_components, selected_nets


def _component_payload(component: Component) -> dict[str, Any]:
    return {
        "ref": component.ref,
        "type": component.type,
        "value": component.value,
        "symbol": component.symbol,
        "footprint": component.footprint,
        "pins": [
            pin.model_dump(mode="json", exclude_none=True)
            for pin in component.pins
        ],
    }


def _net_payload(net: Net) -> dict[str, Any]:
    return {
        "name": net.name,
        "net_class": net.net_class.value,
        "nodes": [_node_id(node) for node in net.nodes],
    }


def _warnings_for_selection(
    warnings: list[Warning],
    selection: ContextSelection,
) -> list[dict[str, Any]]:
    if not selection.components and not selection.nets and not selection.warning_codes:
        return [warning.model_dump(mode="json", exclude_none=True) for warning in warnings]

    selected_refs = set(selection.components) | set(selection.nets)
    selected_codes = set(selection.warning_codes)
    out: list[dict[str, Any]] = []
    for warning in warnings:
        if warning.code in selected_codes or selected_refs.intersection(warning.refs):
            out.append(warning.model_dump(mode="json", exclude_none=True))
    return out


def _node_id(node: NodeRef | str) -> str:
    return node.as_string() if isinstance(node, NodeRef) else node


def _estimate_tokens(payload: dict[str, Any]) -> int:
    compact = json.dumps(payload, separators=(",", ":"), sort_keys=True)
    return max(1, len(compact) // 4)
