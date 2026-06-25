from pathlib import Path

from ecad_agent.ai import ContextBudget, ContextBuilder, ContextSelection, CopilotEngine
from ecad_agent.ai.providers import LocalLLMProvider
from ecad_agent.model import CircuitProject
from ecad_agent.sync import build_sync_envelope

FIXTURES = Path(__file__).resolve().parents[1] / "examples"


def test_context_builder_small_budget_uses_selected_neighborhood() -> None:
    project = CircuitProject.load(FIXTURES / "voltage_divider" / "model.json")
    context = ContextBuilder().build(
        project=project,
        question="What does R1 do?",
        budget=ContextBudget.SMALL,
        selection=ContextSelection(components=["R1"]),
    )

    component_refs = {component["ref"] for component in context.payload["components"]}
    net_names = {net["name"] for net in context.payload["nets"]}

    assert "R1" in component_refs
    assert {"VIN", "VOUT"}.issubset(net_names)
    assert context.estimated_tokens > 0


def test_copilot_engine_returns_structured_offline_answer() -> None:
    project = CircuitProject.load(FIXTURES / "voltage_divider" / "model.json")
    engine = CopilotEngine(provider=LocalLLMProvider())

    result = engine.ask(
        project=project,
        question="Explain the divider output.",
        selection=ContextSelection(nets=["VOUT"]),
        budget=ContextBudget.SMALL,
    )

    response = result.response.to_dict()

    assert "answer" in response
    assert "VOUT" in response["referenced_nets"]
    assert response["uncertainty"] in {"low", "medium", "high"}


def test_project_sync_envelope_keeps_wrapper_thin() -> None:
    project = CircuitProject.load(FIXTURES / "voltage_divider" / "model.json")

    envelope = build_sync_envelope(
        project=project,
        wrapper="kicad_extension",
        files={"schematic": "voltage_divider.kicad_sch"},
        capabilities=["ask", "review"],
    )

    payload = envelope.to_dict()

    assert payload["wrapper"] == "kicad_extension"
    assert payload["project"]["project"]["name"] == "voltage_divider"
    assert payload["capabilities"] == ["ask", "review"]
