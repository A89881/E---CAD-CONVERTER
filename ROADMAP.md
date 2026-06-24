# Roadmap

## Milestone 0: Project Setup

- Repository structure
- Project scope
- Architecture docs
- Example circuits folder
- Meeting notes folder
- Decision log
- CI workflow
- Container build workflow

## Milestone 1: Internal Model

- Python model classes
- JSON schema
- Three to five manually created example circuits
- JSON load/save
- Basic model validation

## Milestone 2: KiCad Exporter

- Internal JSON to `.kicad_sch`
- Support simple resistor, capacitor, connector, power, and ground symbols
- Stable symbol and footprint mapping tables
- Output file opens in KiCad for selected examples

## Milestone 3: Import And Round Trip

- Basic KiCad importer
- Connectivity comparison
- Round-trip report: KiCad to internal model to KiCad
- Golden tests for example circuits

## Milestone 4: External Source Format

- Prototype EasyEDA or EAGLE importer
- Mapping warnings for unsupported objects
- External schematic to internal model to KiCad output

## Milestone 5: AI Review Layer

- Structured context builder
- Circuit explanation prompt
- Warning explanation prompt
- Review report grounded in components, pins, nets, and validation results

## Later Directions

- Circuit linter
- Circuit diff
- SPICE bridge
- Migration wizard
- Dataset pipeline
- Web upload and review dashboard
