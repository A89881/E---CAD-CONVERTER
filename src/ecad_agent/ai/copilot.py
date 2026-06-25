"""Copilot orchestration over structured ECAD model data."""

from __future__ import annotations

from dataclasses import dataclass

from ecad_agent.ai.context_builder import (
    ContextBudget,
    ContextBuilder,
    ContextSelection,
    CopilotContext,
)
from ecad_agent.ai.providers import AIProvider, AIResponse, get_provider
from ecad_agent.model import CircuitProject
from ecad_agent.validation import ValidationReport, validate_project


@dataclass(frozen=True, slots=True)
class CopilotResult:
    """Full copilot result with both provider answer and sent context metadata."""

    response: AIResponse
    context: CopilotContext

    def to_dict(self) -> dict[str, object]:
        return {
            "response": self.response.to_dict(),
            "context": {
                "task": self.context.task,
                "budget": self.context.budget.value,
                "estimated_tokens": self.context.estimated_tokens,
            },
        }


class CopilotEngine:
    """Coordinates context building, validation grounding, and provider calls."""

    def __init__(
        self,
        provider: AIProvider | None = None,
        context_builder: ContextBuilder | None = None,
    ) -> None:
        self.provider = provider or get_provider()
        self.context_builder = context_builder or ContextBuilder()

    def ask(
        self,
        project: CircuitProject,
        question: str,
        selection: ContextSelection | None = None,
        budget: ContextBudget = ContextBudget.MEDIUM,
        validation_report: ValidationReport | None = None,
    ) -> CopilotResult:
        report = validation_report or validate_project(project)
        context = self.context_builder.build(
            project=project,
            question=question,
            task="ask_about_circuit",
            budget=budget,
            selection=selection,
            validation_report=report,
        )
        response = self.provider.complete(
            messages=context.to_messages(),
            max_tokens=budget.max_tokens,
        )
        return CopilotResult(response=response, context=context)

    def review(
        self,
        project: CircuitProject,
        question: str = "Review this circuit for design and conversion risks.",
        budget: ContextBudget = ContextBudget.MEDIUM,
    ) -> CopilotResult:
        report = validate_project(project)
        context = self.context_builder.build(
            project=project,
            question=question,
            task="circuit_review",
            budget=budget,
            validation_report=report,
        )
        response = self.provider.complete(
            messages=context.to_messages(),
            max_tokens=budget.max_tokens,
        )
        return CopilotResult(response=response, context=context)
