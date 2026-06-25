"""FastAPI route factory for future cloud/backend deployments."""

from __future__ import annotations

from typing import Any

from ecad_agent.ai import ContextBudget, ContextSelection, CopilotEngine, get_provider
from ecad_agent.model import CircuitProject


def create_app() -> Any:
    """Create a FastAPI app if the optional API dependencies are installed."""

    try:
        from fastapi import FastAPI
        from pydantic import BaseModel
    except ImportError as exc:
        raise RuntimeError(
            "Install API dependencies with `python -m pip install -e .[api]`."
        ) from exc

    class AskRequest(BaseModel):
        model: dict[str, Any]
        question: str
        provider: str = "local"
        budget: ContextBudget = ContextBudget.MEDIUM
        components: list[str] = []
        nets: list[str] = []

    app = FastAPI(title="ECAD Copilot Backend", version="0.1.0")

    @app.post("/copilot/ask")
    def ask(request: AskRequest) -> dict[str, object]:
        project = CircuitProject.from_dict(request.model)
        selection = ContextSelection(
            components=request.components,
            nets=request.nets,
        )
        engine = CopilotEngine(provider=get_provider(request.provider))
        return engine.ask(
            project=project,
            question=request.question,
            selection=selection,
            budget=request.budget,
        ).to_dict()

    return app
