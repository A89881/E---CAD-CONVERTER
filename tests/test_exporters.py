from pathlib import Path

from ecad_agent.exporters import export_internal_json, export_kicad_schematic
from ecad_agent.model import CircuitProject

FIXTURES = Path(__file__).resolve().parents[1] / "examples"


def test_json_exporter_returns_normalized_content() -> None:
    project = CircuitProject.from_file(FIXTURES / "voltage_divider" / "model.json")

    content = export_internal_json(project)

    assert '"name": "voltage_divider"' in content
    assert '"R1.2"' in content


def test_kicad_exporter_renders_starter_schematic() -> None:
    project = CircuitProject.from_file(FIXTURES / "voltage_divider" / "model.json")

    content = export_kicad_schematic(project)

    assert content.startswith("(kicad_sch")
    assert 'property "Reference" "R1"' in content
    assert "Net VOUT: R1.2, R2.1" in content
