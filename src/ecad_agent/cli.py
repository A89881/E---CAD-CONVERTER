"""Command line interface for the ECAD agent scaffold."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

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


if __name__ == "__main__":
    app()
