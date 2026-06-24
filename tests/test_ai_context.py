from pathlib import Path

from ecad_agent.ai import build_review_context
from ecad_agent.model import CircuitProject
from ecad_agent.validation import validate_project


FIXTURES = Path(__file__).resolve().parents[1] / "examples"


def test_review_context_uses_structured_model_data() -> None:
    project = CircuitProject.from_file(FIXTURES / "voltage_divider" / "model.json")
    report = validate_project(project)

    context = build_review_context(project, report)

    assert context["project"]["name"] == "voltage_divider"
    assert context["connectivity"]["VOUT"] == ("R1.2", "R2.1")
    assert context["validation"]["success"] is True
