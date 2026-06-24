"""Symbol and footprint mapping helper placeholders."""

from __future__ import annotations

from ecad_agent.model import Component


def describe_mapping_gap(component: Component) -> str | None:
    missing: list[str] = []
    if not component.symbol:
        missing.append("symbol")
    if not component.footprint:
        missing.append("footprint")
    if not missing:
        return None
    return f"{component.ref} is missing {', '.join(missing)} mapping data."
