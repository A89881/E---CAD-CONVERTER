# Validation

Validation exists because ECAD conversions can produce files that open but are electrically wrong.

## First Checks

- Duplicate component references
- Duplicate pin numbers within a component
- Duplicate net names
- Net nodes that reference unknown components
- Net nodes that reference unknown pins
- Pin-to-net mismatches
- Pins that declare nets missing from the net list
- Unconnected pins
- Empty nets

## Graph Equivalence

The most important conversion validation is graph equivalence.

Before conversion:

```text
NET_A connects U1.3, R1.1, C2.1
```

After conversion:

```text
NET_A connects U1.3, R1.1, C2.1
```

If those node sets match, the electrical meaning is likely preserved.

## Report Shape

Every conversion should produce a report with at least:

- Input format
- Output format
- Component count
- Net count
- Connectivity result
- Missing symbols
- Missing footprints
- Unsupported objects
- Warnings
