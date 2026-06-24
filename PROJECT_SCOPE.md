# Project Scope

## Positioning

This project is an AI-assisted ECAD translation and validation workspace for schematics, PCB source files, and engineering review.

It is not just a file converter or chatbot. The long-term system converts ECAD files into a neutral circuit model, validates the design, supports AI-assisted review, and exports target ECAD formats or reports.

## Current Focus

Build a minimal but correct schematic-level translation and validation pipeline based on a neutral internal circuit model.

The current MVP scope is:

- Internal JSON circuit model
- Python model classes
- JSON load/save
- Basic validation report
- Basic KiCad schematic export
- Example circuits
- Tests for connectivity preservation

## First-Priority Inputs

- Internal JSON
- KiCad `.kicad_sch`
- EasyEDA schematic JSON
- EAGLE XML `.sch`

Only internal JSON is implemented in this scaffold. External format importers are placeholders with clear ownership boundaries.

## First-Priority Outputs

- Internal JSON
- Validation report
- KiCad `.kicad_sch`
- Later: SPICE/netlist export

## Out Of Scope For The First Milestone

- Full PCB autorouting
- Full Altium replacement
- Universal all-format conversion
- Gerber-to-schematic reverse engineering
- Automatic PCB layout from schematic
- Advanced signal integrity analysis
- Production commercial platform behavior

## Success Criteria

MVP success means:

- A simple schematic can be represented in the internal model.
- The model can be exported toward KiCad.
- Pin-to-net connectivity can be validated.
- A validation report is produced.
- AI workflows receive structured model context instead of raw file guesses.
