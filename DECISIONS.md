# Decision Log

Use this file to keep architecture decisions visible and prevent repeated discussions.

## 0001: Use A Neutral Circuit Model As The Core

- Status: accepted
- Date: 2026-06-24

Every importer must output the neutral model. Every exporter must consume it. Validators and AI workflows inspect the same model.

Consequences:

- We avoid one-off direct converters.
- Connectivity validation becomes a central workflow.
- AI does not reason from raw ECAD files alone.

## 0002: Start Backend-First With Python

- Status: accepted
- Date: 2026-06-24

Python is the first implementation language because it is strong for parsing, graph analysis, scientific computing, AI integration, and quick prototyping.

Consequences:

- The frontend is intentionally deferred.
- The first cloud artifact is a containerized CLI/API-ready service.
- Pydantic, NetworkX, Typer, pytest, and FastAPI are the planned stack.

## 0003: Keep The First Milestone Schematic-Level

- Status: accepted
- Date: 2026-06-24

The first deliverable should preserve component-pin-net connectivity for simple schematics.

Consequences:

- PCB autorouting, Gerber reverse engineering, and advanced simulation are later work.
- Warnings are preferable to silent conversion.
- The validation report is as important as the exported file.
