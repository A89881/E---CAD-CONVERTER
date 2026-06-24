# Internal Model

The neutral internal model is the project's main technical asset. It is intentionally independent from KiCad, EasyEDA, EAGLE, Altium, or any other specific ECAD tool.

## Core Entities

- `CircuitProject`
- `Component`
- `Pin`
- `Net`
- `Wire`
- `Label`
- `WarningMessage`
- `ValidationReport`

## Minimal Example

```json
{
  "schema_version": "0.1.0",
  "project": {
    "name": "voltage_divider",
    "source_format": "internal-json"
  },
  "components": [
    {
      "ref": "R1",
      "type": "resistor",
      "value": "10k",
      "symbol": "Device:R",
      "footprint": "Resistor_SMD:R_0603_1608Metric",
      "pins": [
        { "number": "1", "name": "A", "net": "VIN" },
        { "number": "2", "name": "B", "net": "VOUT" }
      ]
    }
  ],
  "nets": [
    {
      "name": "VIN",
      "nodes": ["R1.1"]
    }
  ],
  "warnings": []
}
```

## Modeling Rules

- Component references must be unique.
- Pin node IDs use the format `REF.PIN`, such as `U1.3`.
- Nets contain node IDs.
- Pins may also declare their net for easier importer/exporter mapping.
- Validation checks that both views agree.
- Unknown or unsupported source data should become warnings, not silent loss.

## JSON Schema

The starter schema lives in [internal_model.schema.json](../schemas/internal_model.schema.json).
