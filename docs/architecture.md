# Architecture

## ECAD Copilot Extension Framework

The ECAD tool extension is a thin wrapper. The backend is the intelligence
layer. The neutral circuit model is the shared language between them.

## System Flow

```text
KiCad / EasyEDA / EAGLE / Altium
        |
        v
ECAD extension / wrapper
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
Copilot engine
        |
        v
Tools: conversion, review, simulation, prediction, documentation
        |
        v
Output ECAD project / report / netlist
```

## Module Responsibilities

### Format Detector

Identifies whether a file or project looks like internal JSON, KiCad, EasyEDA, EAGLE, or a later format.

### Importers

Parse source formats into the neutral model. Importers should preserve source references and emit warnings for unsupported objects.

### Wrappers

Wrappers live under `wrappers/` and should stay thin. They read the host ECAD
project, send files or a project sync envelope to the backend, display warnings
and copilot responses, and apply only user-approved changes.

### Project Sync Layer

The sync layer packages wrapper identity, source format, files, capabilities,
and the internal circuit model into a backend-friendly envelope.

### Neutral Model

Represents electrical intent independently from any ECAD tool. The core relationship is:

```text
Component -> Pin -> Net
```

### Validation Engine

Checks model consistency and compares connectivity before and after conversion. The first validation target is graph equivalence.

### Copilot Engine

Builds structured context for explanation, review, mapping suggestions, and
report generation. It uses context budgets:

- small: selected component/net plus nearby graph
- medium: schematic summary, components, nets, warnings
- large: full model and validation context

AI can propose; validators must verify.

### AI Provider Router

The copilot calls a provider-neutral interface so OpenAI, Anthropic, Google, or
local models can be selected without changing the rest of the app.

### Exporters

Convert the neutral model into target formats such as KiCad, internal JSON, SPICE, reports, and later manufacturing outputs.

## Cloud-Friendly Direction

The project starts as a CLI and library. That keeps the core workflow portable across local laptops, CI runners, containers, and future cloud workers.

The next cloud step should be a FastAPI service that accepts uploaded ECAD projects, runs import/validate/export jobs in isolated workspaces, and stores artifacts in object storage.
