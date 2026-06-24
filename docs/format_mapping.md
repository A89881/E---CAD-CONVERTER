# Format Mapping

This file tracks how ECAD formats represent schematic intent.

## Internal JSON

- Status: scaffolded
- Purpose: neutral model storage and golden tests
- Key data: project metadata, components, pins, nets, wires, labels, warnings

## KiCad `.kicad_sch`

- Status: exporter scaffolded, importer planned
- Priority: first target output format
- Key data to study:
  - `symbol`
  - `property`
  - `wire`
  - `label`
  - `junction`
  - `lib_symbols`
  - hierarchical sheets

## EasyEDA JSON

- Status: planned
- Priority: first or second external importer candidate
- Key data to study:
  - shape records
  - net labels
  - components
  - library IDs
  - pin mappings

## EAGLE XML `.sch`

- Status: planned
- Priority: first or second external importer candidate
- Key data to study:
  - libraries
  - parts
  - instances
  - nets
  - segments
  - pins and gates

## Manufacturing Formats

Gerber, Excellon drill, BOM, pick-and-place, STEP, IPC-2581, and ODB++ are useful later for output and validation. They should not be treated as the main basis for schematic translation in the MVP.
