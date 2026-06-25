"""Connectivity validation for the neutral circuit model."""

from __future__ import annotations

from collections import Counter

from ecad_agent.model import CircuitProject, NodeRef, Pin
from ecad_agent.validation.report import ValidationIssue, ValidationReport


def validate_project(project: CircuitProject) -> ValidationReport:
    issues: list[ValidationIssue] = []
    issues.extend(_component_reference_issues(project))
    issues.extend(_pin_issues(project))
    issues.extend(_net_issues(project))
    issues.extend(_missing_metadata_issues(project))

    stats = {
        "component_count": len(project.components),
        "net_count": len(project.nets),
        "pin_count": sum(len(component.pins) for component in project.components),
        "connected_pin_count": len(project.node_map()),
        "warning_count": len(project.warnings),
    }
    return ValidationReport.from_issues(issues, stats)


def _component_reference_issues(project: CircuitProject) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    refs = [component.ref for component in project.components]
    duplicates = [ref for ref, count in Counter(refs).items() if count > 1]
    for ref in duplicates:
        issues.append(
            ValidationIssue(
                code="duplicate-component-ref",
                severity="error",
                subject=ref,
                message="Component references must be unique.",
            )
        )

    if not project.components:
        issues.append(
            ValidationIssue(
                code="empty-project",
                severity="warning",
                message="Project has no components.",
            )
        )
    return issues


def _pin_issues(project: CircuitProject) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    connected_nodes = set(project.node_map())

    for component in project.components:
        pin_numbers = [pin.number for pin in component.pins]
        duplicates = [number for number, count in Counter(pin_numbers).items() if count > 1]
        for number in duplicates:
            issues.append(
                ValidationIssue(
                    code="duplicate-pin-number",
                    severity="error",
                    subject=f"{component.ref}.{number}",
                    message="Component has duplicate pin numbers.",
                )
            )

        for pin in component.pins:
            node_id = f"{component.ref}.{pin.number}"
            if node_id not in connected_nodes:
                issues.append(
                    ValidationIssue(
                        code="unconnected-pin",
                        severity="info",
                        subject=node_id,
                        message="Pin has no declared net.",
                    )
                )
    return issues


def _net_issues(project: CircuitProject) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    known_nodes = _known_nodes(project)
    net_names = [net.name for net in project.nets]
    duplicates = [name for name, count in Counter(net_names).items() if count > 1]

    for name in duplicates:
        issues.append(
            ValidationIssue(
                code="duplicate-net-name",
                severity="error",
                subject=name,
                message="Net names must be unique.",
            )
        )

    for net in project.nets:
        if not net.nodes:
            issues.append(
                ValidationIssue(
                    code="empty-net",
                    severity="warning",
                    subject=net.name,
                    message="Net has no nodes.",
                )
            )

        node_strings = [_node_id(node) for node in net.nodes]
        node_duplicates = [node for node, count in Counter(node_strings).items() if count > 1]
        for node in node_duplicates:
            issues.append(
                ValidationIssue(
                    code="duplicate-node-in-net",
                    severity="warning",
                    subject=f"{net.name}:{node}",
                    message="Net contains the same node more than once.",
                )
            )

        for node in node_strings:
            pin = known_nodes.get(node)
            if pin is None:
                issues.append(
                    ValidationIssue(
                        code="unknown-net-node",
                        severity="error",
                        subject=node,
                        message=f"Net {net.name!r} references a component pin that is not defined.",
                    )
                )
    return issues


def _missing_metadata_issues(project: CircuitProject) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for component in project.components:
        if not component.symbol:
            issues.append(
                ValidationIssue(
                    code="missing-symbol",
                    severity="warning",
                    subject=component.ref,
                    message="Component has no source/target symbol mapping.",
                )
            )
        if not component.footprint:
            issues.append(
                ValidationIssue(
                    code="missing-footprint",
                    severity="warning",
                    subject=component.ref,
                    message="Component has no footprint mapping.",
                )
            )
    return issues


def _known_nodes(project: CircuitProject) -> dict[str, Pin]:
    return {
        f"{component.ref}.{pin.number}": pin
        for component in project.components
        for pin in component.pins
    }


def _node_id(node: NodeRef | str) -> str:
    return node.as_string() if isinstance(node, NodeRef) else node
