"""Deterministic local provider used for tests and offline development."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from typing import Any

from ecad_agent.ai.providers.base import AIMessage, AIResponse, Uncertainty


class LocalLLMProvider:
    """A no-network provider that turns structured context into a grounded answer.

    This is intentionally not pretending to be a smart model. It gives the
    backend a stable provider target while real vendor adapters are added later.
    """

    name = "local"

    def complete(
        self,
        messages: Sequence[AIMessage],
        tools: Sequence[Mapping[str, Any]] | None = None,
        max_tokens: int = 2000,
    ) -> AIResponse:
        del tools, max_tokens
        context = _last_json_payload(messages)
        project = context.get("project", {})
        task = str(context.get("task", "ask_about_circuit"))
        question = str(context.get("question", ""))
        components = _refs(context.get("components", []), "ref")
        nets = _refs(context.get("nets", []), "name")
        warnings = context.get("warnings", [])
        validation = context.get("validation", {})

        if task == "circuit_review":
            status = "passes validation" if validation.get("success", True) else "has issues"
            answer = (
                f"{project.get('name', 'This project')} {status}. "
                f"I found {len(components)} component(s), {len(nets)} net(s), "
                f"and {len(warnings)} warning item(s) in the supplied context."
            )
            next_action = "Open the validation report and resolve error-severity issues first."
        else:
            focus = _focus_sentence(context)
            answer = (
                f"Using the structured circuit model for {project.get('name', 'this project')}, "
                f"I can answer the question {question!r}. {focus} "
                f"The response is grounded in {len(components)} component(s) and "
                f"{len(nets)} net(s) included in the current context."
            )
            next_action = "Expand the context budget if the answer needs surrounding circuitry."

        uncertainty: Uncertainty = "low" if validation.get("success", True) else "medium"
        return AIResponse(
            answer=answer,
            referenced_components=components,
            referenced_nets=nets,
            uncertainty=uncertainty,
            suggested_next_action=next_action,
            raw={"provider": self.name, "context_budget": context.get("budget")},
        )


def _last_json_payload(messages: Sequence[AIMessage]) -> dict[str, Any]:
    for message in reversed(messages):
        if message.role == "user":
            try:
                payload = json.loads(message.content)
            except json.JSONDecodeError:
                return {"question": message.content}
            return payload if isinstance(payload, dict) else {"payload": payload}
    return {}


def _refs(items: object, key: str) -> list[str]:
    if not isinstance(items, list):
        return []
    refs: list[str] = []
    for item in items:
        if isinstance(item, dict) and item.get(key) is not None:
            refs.append(str(item[key]))
    return refs


def _focus_sentence(context: dict[str, Any]) -> str:
    focus = context.get("focus", {})
    if not isinstance(focus, dict) or not focus:
        return "No explicit component or net focus was selected."

    pieces: list[str] = []
    components = focus.get("components")
    nets = focus.get("nets")
    if isinstance(components, list) and components:
        pieces.append(f"Focused component(s): {', '.join(str(item) for item in components)}.")
    if isinstance(nets, list) and nets:
        pieces.append(f"Focused net(s): {', '.join(str(item) for item in nets)}.")
    return " ".join(pieces) if pieces else "No explicit component or net focus was selected."
