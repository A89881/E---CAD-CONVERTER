# Internal Model

The neutral internal model is the project's main technical asset. It is intentionally independent from KiCad, EasyEDA, EAGLE, Altium, or any other specific ECAD tool.

## Core Entities

### Schematic layer (always present)

| Class | File | Role |
|---|---|---|
| `CircuitProject` | `project.py` | Root container — holds all other entities |
| `ProjectInfo` | `project.py` | Name, source format, schema version |
| `Component` | `component.py` | One part instance (resistor, IC, connector, …) |
| `Pin` | `pin.py` | One connection point on a component |
| `Net` | `net.py` | Electrical node — the set of pins wired together |
| `NodeRef` | `net.py` | Reference to one pin on one component (`"R1.2"`) |
| `Wire` | `graphics.py` | Graphical wire segment (display only) |
| `Label` | `graphics.py` | Net label placed in the schematic (display only) |
| `Warning` | `warning.py` | One machine-readable issue from integrity / validation |
| `ValidationResult` | `warning.py` | Outcome of a full validation pass |

### PCB layer (optional)

| Class | File | Role |
|---|---|---|
| `BoardLayout` | `board.py` | Root of the physical layer; attached to `CircuitProject.pcb` |
| `Placement` | `board.py` | Where/how one component is placed on the board |
| `FootprintDef` | `board.py` | Physical footprint — pad list + optional 3D model id |
| `PadDef` | `board.py` | One pad in a footprint |
| `StackLayer` | `board.py` | One layer in the board stack-up |
| `BoardOutline` | `board.py` | Board edge — polygon points and/or arc segments |
| `ArcSegment` | `board.py` | One arc segment in the board outline |

Enums: `BoardSide`, `PadShape`, `PadType`, `LayerKind`.

---

## Connectivity — the source of truth

**`Net` objects are the single source of truth for what is electrically connected.**

- Each `Net` owns a list of `NodeRef` objects (`component` ref + pin `number`). The compact string form `"R1.2"` is accepted on JSON input and produced by `NodeRef.as_string()`.
- `Component.pins` define which pins exist; they do **not** store net membership.
- `CircuitProject.node_map()` builds the canonical `{NodeRef → net_name}` lookup from the net list. The validation engine and AI layer use this map — they do not read net info from any other field.
- The PCB layer references this graph; it never forks or duplicates net membership. A pad maps to a pin; the pin's net is already known via the schematic nets.

---

## Minimal Schematic-Only Example

```json
{
  "project": {
    "name": "voltage_divider",
    "source_format": "internal-json",
    "schema_version": "0.1.0"
  },
  "components": [
    {
      "ref": "R1",
      "type": "resistor",
      "value": "10k",
      "symbol": "Device:R",
      "footprint": "Resistor_SMD:R_0603_1608Metric",
      "pins": [
        { "number": "1", "name": "A", "electrical_type": "passive" },
        { "number": "2", "name": "B", "electrical_type": "passive" }
      ]
    }
  ],
  "nets": [
    { "name": "VIN", "net_class": "power", "nodes": ["R1.1"] }
  ],
  "warnings": []
}
```

---

## Modeling Rules (schematic layer)

- Component references (`ref`) must be unique across the project.
- Pin node IDs use the format `REF.PIN`, e.g. `U1.3`. `NodeRef.from_string()` splits on the **last** dot, so refs containing dots are supported.
- Nets contain the node IDs. The `nodes` list may use either the compact string form or the object form `{"component": "R1", "pin": "2"}`.
- Unknown or unsupported source data should become `Warning` objects, not silent loss.
- `extra="forbid"` is set on all model classes — unknown JSON keys are rejected at load time.

---

## PCB Layer

The PCB layer is an **optional** addition to `CircuitProject`. A model with `pcb: null` (or no `pcb` key) is fully valid and passes all existing integrity checks unchanged. The PCB layer is represented by `CircuitProject.pcb: Optional[BoardLayout]`.

### Design principles

- **Neutral, not KiCad.** Layer names, pad types, and board structure are described in tool-independent terms. Exporters map these onto tool-specific encodings.
- **Single source of truth for connectivity.** The PCB layer never stores net membership. A `Placement` references a `Component.ref`; a `PadDef.number` maps to a `Pin.number`; the net is looked up from the schematic `nets` list.
- **Routing excluded.** Tracks, vias, and copper pours are intentionally out of scope for this pass (see Open Decisions).

### `BoardLayout`

The root of the physical board data.

| Field | Type | Mandatory | Description |
|---|---|---|---|
| `placements` | `List[Placement]` | yes (may be empty) | One entry per physically placed component |
| `layer_stack` | `List[StackLayer]` | no | Ordered stack-up from top to bottom |
| `outline` | `BoardOutline \| null` | no | Board edge / edge-cuts |

### `Placement`

Where and how one component is physically positioned on the board.

| Field | Type | Mandatory | Description |
|---|---|---|---|
| `ref` | `str` | yes | Must match a `Component.ref` in the schematic layer |
| `x` | `float` | yes | X position of the component origin, in mm |
| `y` | `float` | yes | Y position of the component origin, in mm |
| `rotation` | `float` | no (default `0.0`) | Rotation in degrees, clockwise |
| `side` | `BoardSide` | no (default `"top"`) | `"top"` or `"bottom"` |
| `footprint` | `FootprintDef \| null` | no | Physical footprint; may be absent when detail is unknown |

Power/ground symbols (`#PWR*`, `#FLG*`) are logical constructs with no physical package and are **typically omitted from placements**. Their absence does not trigger a warning.

### `FootprintDef`

The physical definition of one component's PCB footprint. Embedded directly in `Placement` (one footprint per placed component — see Open Decisions for the inline-vs-library trade-off).

| Field | Type | Mandatory | Description |
|---|---|---|---|
| `pads` | `List[PadDef]` | yes (may be empty) | All pads in this footprint |
| `library_ref` | `str \| null` | no | Source library id, e.g. `"Resistor_SMD:R_0603"`. Informational only |
| `model_3d` | `str \| null` | no | Opaque 3D model identifier (path or asset key). **No geometry is stored here — reference only** |

### `PadDef` and the pad-to-pin mapping rule

One pad in a footprint.

| Field | Type | Mandatory | Description |
|---|---|---|---|
| `number` | `str` | yes | Pad identifier; **must equal the `Pin.number` it maps to** |
| `pad_type` | `PadType` | no (default `"smd"`) | `"smd"`, `"through_hole"`, or `"npth"` |
| `shape` | `PadShape` | no (default `"rect"`) | `"circle"`, `"rect"`, or `"oval"` |
| `size_x` | `float` | yes | Pad width in mm |
| `size_y` | `float` | yes | Pad height in mm |
| `position` | `Point` | yes | Pad centre relative to the footprint origin, in mm |
| `drill_diameter` | `float \| null` | no | Required for `through_hole` and `npth` pads |
| `layers` | `List[str]` | no (default `["front_copper"]`) | Neutral layer names this pad occupies |

**Pad-to-pin mapping rule:** `PadDef.number == Pin.number` on the owning component — the same string, the same identity. This is a documented convention. `check_integrity` enforces it: it fires `PCB_PAD_UNKNOWN_PIN` when a pad number does not match any pin number on the component.

### `StackLayer` and neutral layer naming

One layer in the board stack-up. Layers are ordered top-to-bottom in `BoardLayout.layer_stack`.

| Field | Type | Mandatory | Description |
|---|---|---|---|
| `name` | `str` | yes | Neutral layer name (see naming convention below) |
| `kind` | `LayerKind` | yes | `"copper"`, `"dielectric"`, `"silk"`, or `"mask"` |
| `thickness_mm` | `float \| null` | no | Layer thickness in mm |

**Neutral layer naming convention** — these names are not tied to any specific tool:

| Neutral name | `LayerKind` | Approximate KiCad equivalent |
|---|---|---|
| `front_copper` | `copper` | `F.Cu` |
| `back_copper` | `copper` | `B.Cu` |
| `inner_copper_1`, `inner_copper_2`, … | `copper` | `In1.Cu`, `In2.Cu`, … |
| `prepreg_1`, `prepreg_2`, … | `dielectric` | — |
| `core_1`, `core_2`, … | `dielectric` | — |
| `front_silk` | `silk` | `F.SilkS` |
| `back_silk` | `silk` | `B.SilkS` |
| `front_mask` | `mask` | `F.Mask` |
| `back_mask` | `mask` | `B.Mask` |

### `BoardOutline`

The board edge, expressed as a combination of polygon vertices and arc segments.

| Field | Type | Mandatory | Description |
|---|---|---|---|
| `points` | `List[Point]` | no (default `[]`) | Ordered vertices for straight edges, in mm. Need not repeat the first point to close the polygon |
| `arcs` | `List[ArcSegment]` | no (default `[]`) | Arc segments (e.g. rounded corners) |

At least one of `points` or `arcs` should be non-empty; `check_integrity` emits `PCB_OUTLINE_TOO_FEW_POINTS` (WARNING) when a polygon has fewer than 3 points and there are no arc segments.

### `ArcSegment`

One arc segment in the board outline, defined by three points on the circle.

| Field | Type | Mandatory | Description |
|---|---|---|---|
| `start` | `Point` | yes | Arc start point, in mm |
| `end` | `Point` | yes | Arc end point, in mm |
| `center` | `Point` | yes | Centre of the circle the arc lies on, in mm |

---

## PCB Integrity Checks

`CircuitProject.check_integrity()` runs schematic checks first (unchanged), then the following PCB checks when `pcb` is not None:

| Code | Severity | Condition |
|---|---|---|
| `PCB_UNKNOWN_REF` | ERROR | `Placement.ref` not found in `CircuitProject.components` |
| `PCB_DUPLICATE_PLACEMENT` | ERROR | Same `ref` appears in `pcb.placements` more than once |
| `PCB_PAD_UNKNOWN_PIN` | ERROR | `PadDef.number` on a placed footprint does not match any `Pin.number` on that component |
| `PCB_OUTLINE_TOO_FEW_POINTS` | WARNING | `pcb.outline.points` has fewer than 3 vertices and `pcb.outline.arcs` is empty |

---

## PCB Layer Example (excerpt)

The following `"pcb"` block can be added to any valid circuit JSON. Full examples are in `examples/voltage_divider_pcb/` and `examples/rc_filter_pcb/`.

```json
"pcb": {
  "placements": [
    {
      "ref": "R1",
      "x": 10.0, "y": 10.0,
      "rotation": 0.0, "side": "top",
      "footprint": {
        "library_ref": "Resistor_SMD:R_0603_1608Metric",
        "pads": [
          {
            "number": "1", "pad_type": "smd", "shape": "rect",
            "size_x": 1.8, "size_y": 1.2,
            "position": {"x": -0.8, "y": 0.0},
            "layers": ["front_copper"]
          },
          {
            "number": "2", "pad_type": "smd", "shape": "rect",
            "size_x": 1.8, "size_y": 1.2,
            "position": {"x": 0.8, "y": 0.0},
            "layers": ["front_copper"]
          }
        ],
        "model_3d": "Resistor_SMD/R_0603_1608Metric.step"
      }
    }
  ],
  "layer_stack": [
    { "name": "front_copper", "kind": "copper",     "thickness_mm": 0.035 },
    { "name": "core_1",       "kind": "dielectric", "thickness_mm": 1.5   },
    { "name": "back_copper",  "kind": "copper",     "thickness_mm": 0.035 }
  ],
  "outline": {
    "points": [
      {"x": 0.0,  "y": 0.0 },
      {"x": 30.0, "y": 0.0 },
      {"x": 30.0, "y": 20.0},
      {"x": 0.0,  "y": 20.0}
    ],
    "arcs": []
  }
}
```

---

## Open Decisions

These questions were flagged during design and need team ratification before a later workstream can depend on them.

### OD-1 · Footprint inline vs. shared library

Currently `FootprintDef` is embedded directly inside each `Placement`. This is simple and self-contained. The trade-off: when many identical parts share a footprint (e.g. 20 × 0603 resistors) the pad data is duplicated 20 times in the JSON.

**Alternative:** introduce `BoardLayout.footprint_library: Dict[str, FootprintDef]` and have `Placement.footprint_ref` point to a key in that dict, with `Placement.footprint` remaining for inline overrides.

**Team decision needed:** is duplication acceptable for the expected scale of designs, or should we add a shared library level now?

### OD-2 · Pad layers cross-validated against stack-up

`PadDef.layers` is a list of neutral layer name strings (e.g. `["front_copper"]`). Currently these strings are **not validated** against `BoardLayout.layer_stack`. A pad could reference a layer name that doesn't appear in the stack-up without triggering an integrity error.

**Team decision needed:** add a `PCB_PAD_UNKNOWN_LAYER` integrity check that cross-validates pad layer references, or document that `PadDef.layers` is advisory/informational?

### OD-3 · Routing in scope?

Copper routing (tracks, vias, copper pours) is **intentionally excluded** from this pass. The schematic nets are the sole connectivity source of truth; the PCB layer records placement and footprint geometry only.

**Team decision needed:** when routing is eventually modelled, should it live as an optional extension of `BoardLayout`, or in a separate top-level field on `CircuitProject`? Ratify the exclusion for this pass before starting any routing work.

### OD-4 · Arc segment interpretation

`ArcSegment` is a structural stub. The three-point definition (start, end, centre) is unambiguous for arcs smaller than 180°, but exporters must decide which arc direction (CW vs CCW) to draw for a given triple. The model does not encode direction.

**Team decision needed:** add an explicit `direction: "cw" | "ccw"` field to `ArcSegment`, or document that exporters infer the shorter arc? Should arc/polygon segments be required to form a closed contour, or can they be open edges?

### OD-5 · Virtual component placements

Power/ground symbols (`#PWR*`, `#FLG*`) are logical constructs in the schematic and are conventionally omitted from PCB placements. The current model allows but does not require their omission — there is no integrity check that flags an unplaced `#PWR` component.

**Team decision needed:** should `check_integrity` emit a `PCB_UNPLACED_COMPONENT` warning for real (non-virtual) components that have no placement? If so, how do we classify which components are "virtual"? By ref prefix, by `type`, or by a new `virtual: bool` field on `Component`?

---

## JSON Schema

The starter schema lives in [internal_model.schema.json](../schemas/internal_model.schema.json). The schema has not yet been updated to cover the PCB layer fields — this is tracked as a follow-up task.
