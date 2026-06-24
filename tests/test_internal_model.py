from pathlib import Path

from ecad_agent.model import CircuitProject


FIXTURES = Path(__file__).resolve().parents[1] / "examples"


def test_load_voltage_divider_fixture() -> None:
    project = CircuitProject.from_file(FIXTURES / "voltage_divider" / "model.json")

    assert project.name == "voltage_divider"
    assert len(project.components) == 2
    assert project.pin_to_net_mapping()["R1.2"] == "VOUT"


def test_model_round_trip_preserves_connectivity() -> None:
    project = CircuitProject.from_file(FIXTURES / "rc_filter" / "model.json")
    round_tripped = CircuitProject.from_json(project.to_json())

    assert round_tripped.to_dict() == project.to_dict()
