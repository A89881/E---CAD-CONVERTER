"""Starter KiCad schematic exporter.

This exporter is intentionally minimal. It creates a KiCad-shaped schematic file
for early demos and tests, but it is not a complete KiCad writer yet.
"""

from __future__ import annotations

from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

from ecad_agent.model import CircuitProject, Component


def export_kicad_schematic(project: CircuitProject, path: str | Path | None = None) -> str:
    content = render_kicad_schematic(project)
    if path is not None:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    return content


def render_kicad_schematic(project: CircuitProject) -> str:
    lines = [
        "(kicad_sch",
        "  (version 20230121)",
        '  (generator "ecad-agent")',
        f'  (uuid "{_stable_uuid(project.name, "schematic")}")',
        '  (paper "A4")',
        "  (lib_symbols)",
    ]

    for index, component in enumerate(project.components):
        x = 25.4 + (index % 4) * 35.0
        y = 25.4 + (index // 4) * 25.0
        lines.extend(_render_symbol(project, component, x, y))

    for index, net in enumerate(project.nets):
        y = 170.0 + index * 5.0
        node_summary = ", ".join(node.as_string() for node in net.nodes) if net.nodes else "(empty)"
        lines.append(
            f'  (text "Net {_escape(net.name)}: {_escape(node_summary)}" '
            f'(at 15 {y:.2f} 0) (effects (font (size 1.27 1.27))))'
        )

    lines.append(")")
    return "\n".join(lines) + "\n"


def _render_symbol(project: CircuitProject, component: Component, x: float, y: float) -> list[str]:
    lib_id = component.symbol or _default_symbol(component)
    footprint = component.footprint or ""
    value = component.value or component.type
    symbol_uuid = _stable_uuid(project.name, component.ref)

    return [
        f"  (symbol (lib_id \"{_escape(lib_id)}\") (at {x:.2f} {y:.2f} 0) "
        f"(unit 1) (exclude_from_sim no) (in_bom yes) (on_board yes) "
        f"(uuid \"{symbol_uuid}\")",
        f'    (property "Reference" "{_escape(component.ref)}" '
        f'(at {x:.2f} {y - 5:.2f} 0) (effects (font (size 1.27 1.27))))',
        f'    (property "Value" "{_escape(value)}" '
        f'(at {x:.2f} {y + 5:.2f} 0) (effects (font (size 1.27 1.27))))',
        f'    (property "Footprint" "{_escape(footprint)}" '
        f'(at {x:.2f} {y + 7.5:.2f} 0) (effects (font (size 1.27 1.27)) hide))',
        "  )",
    ]


def _default_symbol(component: Component) -> str:
    normalized = component.type.lower()
    if normalized in {"resistor", "r"}:
        return "Device:R"
    if normalized in {"capacitor", "c"}:
        return "Device:C"
    if normalized in {"inductor", "l"}:
        return "Device:L"
    if normalized in {"ground", "gnd"}:
        return "power:GND"
    return "Device:Device"


def _stable_uuid(project_name: str, subject: str) -> str:
    return str(uuid5(NAMESPACE_URL, f"ecad-agent:{project_name}:{subject}"))


def _escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')
