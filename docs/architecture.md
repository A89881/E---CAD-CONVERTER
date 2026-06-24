# Architecture

## System Flow

```text
Input ECAD project
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
AI agent layer
        |
        v
Exporter
        |
        v
Output ECAD project / report / netlist
```

## Module Responsibilities

### Format Detector

Identifies whether a file or project looks like internal JSON, KiCad, EasyEDA, EAGLE, or a later format.

### Importers

Parse source formats into the neutral model. Importers should preserve source references and emit warnings for unsupported objects.

### Neutral Model

Represents electrical intent independently from any ECAD tool. The core relationship is:

```text
Component -> Pin -> Net
```

### Validation Engine

Checks model consistency and compares connectivity before and after conversion. The first validation target is graph equivalence.

### AI Agent Layer

Builds structured context for explanation, review, mapping suggestions, and report generation. AI can propose; validators must verify.

### Exporters

Convert the neutral model into target formats such as KiCad, internal JSON, SPICE, reports, and later manufacturing outputs.

## Cloud-Friendly Direction

The project starts as a CLI and library. That keeps the core workflow portable across local laptops, CI runners, containers, and future cloud workers.

The next cloud step should be a FastAPI service that accepts uploaded ECAD projects, runs import/validate/export jobs in isolated workspaces, and stores artifacts in object storage.
