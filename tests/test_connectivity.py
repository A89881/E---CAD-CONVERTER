from pathlib import Path

from ecad_agent.model import CircuitProject, NodeRef
from ecad_agent.validation import compare_connectivity, validate_project

FIXTURES = Path(__file__).resolve().parents[1] / "examples"


def test_voltage_divider_validates_successfully() -> None:
    project = CircuitProject.from_file(FIXTURES / "voltage_divider" / "model.json")

    report = validate_project(project)

    assert report.success
    assert report.stats["component_count"] == 4
    assert report.stats["net_count"] == 3


def test_connectivity_compare_detects_changed_net() -> None:
    before = CircuitProject.from_file(FIXTURES / "voltage_divider" / "model.json")
    after = CircuitProject.from_dict(before.to_dict())
    after.nets[1].nodes = [NodeRef.from_string("R1.2")]

    report = compare_connectivity(before, after)

    assert not report.success
    assert report.issues[0].code == "net-connectivity-changed"
