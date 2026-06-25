"""Connectivity graph comparison."""

from __future__ import annotations

from ecad_agent.model import CircuitProject, NodeRef
from ecad_agent.validation.report import ValidationIssue, ValidationReport


def canonical_connectivity(project: CircuitProject) -> dict[str, tuple[str, ...]]:
    """Return a stable net-to-node mapping for comparison and snapshots."""

    return {
        net.name: tuple(sorted({_node_id(node) for node in net.nodes}))
        for net in sorted(project.nets, key=lambda item: item.name)
    }


def _node_id(node: NodeRef | str) -> str:
    return node.as_string() if isinstance(node, NodeRef) else node


def compare_connectivity(
    before: CircuitProject,
    after: CircuitProject,
) -> ValidationReport:
    before_graph = canonical_connectivity(before)
    after_graph = canonical_connectivity(after)
    issues: list[ValidationIssue] = []

    for net_name in sorted(before_graph.keys() - after_graph.keys()):
        issues.append(
            ValidationIssue(
                code="missing-net-after-conversion",
                severity="error",
                subject=net_name,
                message="Net exists before conversion but is missing afterward.",
            )
        )

    for net_name in sorted(after_graph.keys() - before_graph.keys()):
        issues.append(
            ValidationIssue(
                code="extra-net-after-conversion",
                severity="error",
                subject=net_name,
                message="Net exists after conversion but not before conversion.",
            )
        )

    for net_name in sorted(before_graph.keys() & after_graph.keys()):
        if before_graph[net_name] != after_graph[net_name]:
            issues.append(
                ValidationIssue(
                    code="net-connectivity-changed",
                    severity="error",
                    subject=net_name,
                    message=(
                        f"Before nodes {before_graph[net_name]} do not match "
                        f"after nodes {after_graph[net_name]}."
                    ),
                )
            )

    stats = {
        "before_net_count": len(before_graph),
        "after_net_count": len(after_graph),
        "changed_net_count": len(issues),
    }
    return ValidationReport.from_issues(issues, stats)
