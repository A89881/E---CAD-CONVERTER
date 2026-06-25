"""Command line interface for the ECAD agent scaffold."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated

import typer

from ecad_agent.ai import ContextBudget, ContextSelection, CopilotEngine, get_provider
from ecad_agent.exporters import export_internal_json, export_kicad_schematic
from ecad_agent.importers import load_internal_json
from ecad_agent.validation import validate_project

app = typer.Typer(
    help="ECAD neutral model, validation, and export utilities.",
    no_args_is_help=True,
)


@app.command("validate")
def validate_cmd(
    model: Annotated[Path, typer.Argument(help="Path to an internal JSON model.")],
) -> None:
    project = load_internal_json(model)
    report = validate_project(project)
    typer.echo(report.to_markdown())
    if not report.success:
        raise typer.Exit(1)


@app.command("report")
def report_cmd(
    model: Annotated[Path, typer.Argument(help="Path to an internal JSON model.")],
    out: Annotated[Path | None, typer.Option(help="Optional markdown report output.")] = None,
) -> None:
    project = load_internal_json(model)
    report = validate_project(project)
    content = report.to_markdown()
    if out is not None:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(content, encoding="utf-8")
    typer.echo(content)


@app.command("export-json")
def export_json_cmd(
    model: Annotated[Path, typer.Argument(help="Path to an internal JSON model.")],
    out: Annotated[Path, typer.Option(help="Output path for normalized internal JSON.")],
) -> None:
    project = load_internal_json(model)
    export_internal_json(project, out)
    typer.echo(f"Wrote {out}")


@app.command("export-kicad")
def export_kicad_cmd(
    model: Annotated[Path, typer.Argument(help="Path to an internal JSON model.")],
    out: Annotated[Path, typer.Option(help="Output path for a KiCad schematic.")],
) -> None:
    project = load_internal_json(model)
    export_kicad_schematic(project, out)
    typer.echo(f"Wrote {out}")


@app.command("ask")
def ask_cmd(
    model: Annotated[Path, typer.Argument(help="Path to an internal JSON model.")],
    question: Annotated[str, typer.Argument(help="Question for the copilot.")],
    component: Annotated[
        list[str] | None,
        typer.Option("--component", "-c", help="Focus component reference."),
    ] = None,
    net: Annotated[
        list[str] | None,
        typer.Option("--net", "-n", help="Focus net name."),
    ] = None,
    budget: Annotated[
        ContextBudget,
        typer.Option(help="Context budget: small, medium, or large."),
    ] = ContextBudget.MEDIUM,
    provider: Annotated[
        str,
        typer.Option(help="AI provider name. Use 'local' for offline development."),
    ] = "local",
    as_json: Annotated[
        bool,
        typer.Option("--json", help="Emit the full structured copilot response."),
    ] = False,
) -> None:
    project = load_internal_json(model)
    selection = ContextSelection(components=component or [], nets=net or [])
    engine = CopilotEngine(provider=get_provider(provider))
    result = engine.ask(
        project=project,
        question=question,
        selection=selection,
        budget=budget,
    )

    if as_json:
        typer.echo(json.dumps(result.to_dict(), indent=2, sort_keys=True))
        return

    response = result.response
    typer.echo(response.answer)
    if response.referenced_components:
        typer.echo(f"Components: {', '.join(response.referenced_components)}")
    if response.referenced_nets:
        typer.echo(f"Nets: {', '.join(response.referenced_nets)}")
    typer.echo(f"Uncertainty: {response.uncertainty}")
    if response.suggested_next_action:
        typer.echo(f"Next action: {response.suggested_next_action}")


if __name__ == "__main__":
    app()
