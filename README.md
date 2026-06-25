# ECAD AI Agentic Workspace

An engineering-first workspace for translating, validating, and reviewing ECAD projects through a neutral circuit model.

The core project principle is:

> The circuit graph is the source of truth.

The first milestone is deliberately narrow: represent a schematic as structured circuit data, validate component-pin-net connectivity, export useful artifacts, and prepare the architecture for future KiCad, EasyEDA, EAGLE, SPICE, AI review, and web workflows.

## What This Repo Contains

- A Python package under `src/ecad_agent`
- A neutral internal model for projects, components, pins, nets, labels, wires, warnings, and metadata
- JSON import/export helpers for the internal model
- Connectivity validation and graph comparison utilities
- A starter KiCad schematic exporter
- AI context builders that keep LLMs grounded in structured data
- Copilot core with context budgets, provider routing, and structured answers
- Thin wrapper scaffolds for KiCad, EasyEDA, EAGLE, and Altium
- Example circuits and tests
- GitHub Actions CI and container build workflows
- Docker and devcontainer files for cloud-friendly development

## Current MVP Flow

```text
Internal JSON circuit model
        |
        v
Python domain model
        |
        v
Connectivity validation
        |
        v
KiCad schematic export / validation report / AI-ready context
```

## Quick Start

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
pytest
```

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
pytest
```

## CLI Examples

```bash
ecad-agent validate examples/voltage_divider/model.json
ecad-agent report examples/voltage_divider/model.json --out datasets/reports/voltage_divider.md
ecad-agent export-kicad examples/voltage_divider/model.json --out datasets/processed/voltage_divider.kicad_sch
ecad-agent ask examples/voltage_divider/model.json "What does R1 do?" --component R1 --budget small --json
```

## Architecture

```text
KiCad / EasyEDA / EAGLE / Altium
        |
        v
Thin ECAD wrapper
        |
        v
Project sync layer
        |
        v
Format detector
        |
        v
Importer / parser
        |
        v
Neutral internal ECAD model
        |
        v
Validation engine
        |
        v
Copilot engine / AI provider router
        |
        v
Export / simulation / prediction tools
        |
        v
Output ECAD project / report / netlist
```

The repository is scaffolded so every importer produces the neutral model, every exporter consumes it, every validator inspects it, and every AI workflow reasons from structured context.

## Documentation

- [Project scope](PROJECT_SCOPE.md)
- [Roadmap](ROADMAP.md)
- [Architecture](docs/architecture.md)
- [Internal model](docs/internal_model.md)
- [Validation](docs/validation.md)
- [Format mapping](docs/format_mapping.md)
- [CI/CD](docs/ci_cd.md)
- [Cloud readiness](docs/cloud.md)
- [Decision log](DECISIONS.md)

## Status

This is a foundation scaffold, not a finished converter. The next high-value work is to make the KiCad exporter open cleanly in KiCad for simple resistor/capacitor circuits, then add a KiCad importer and round-trip connectivity tests.
