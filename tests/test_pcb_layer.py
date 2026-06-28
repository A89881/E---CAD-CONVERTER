"""Tests for the PCB physical layer."""

from __future__ import annotations

from pathlib import Path

import pytest

from ecad_agent.model import (
    ArcSegment,
    BoardLayout,
    BoardOutline,
    BoardSide,
    CircuitProject,
    Component,
    FootprintDef,
    LayerKind,
    Net,
    PadDef,
    PadShape,
    PadType,
    Pin,
    Placement,
    Point,
    ProjectInfo,
    Severity,
    StackLayer,
)

ROOT = Path(__file__).resolve().parents[1]
PCB_EXAMPLES = [
    ROOT / "examples" / "voltage_divider_pcb" / "model.json",
    ROOT / "examples" / "rc_filter_pcb" / "model.json",
]


# ---- PCB example circuits ----------------------------------------------------


@pytest.mark.parametrize("path", PCB_EXAMPLES, ids=lambda p: p.parent.name)
def test_pcb_examples_load_and_have_no_errors(path: Path) -> None:
    circuit = CircuitProject.load(path)
    assert circuit.pcb is not None, "Expected PCB layer to be present"
    errors = [w for w in circuit.check_integrity() if w.severity is Severity.ERROR]
    assert errors == [], f"{path.parent.name} has PCB integrity errors: {errors}"


@pytest.mark.parametrize("path", PCB_EXAMPLES, ids=lambda p: p.parent.name)
def test_pcb_examples_round_trip(path: Path) -> None:
    circuit = CircuitProject.load(path)
    reloaded = CircuitProject.model_validate_json(circuit.to_json())
    # Schematic layer is unchanged.
    assert circuit.node_map() == reloaded.node_map()
    assert circuit.component_count() == reloaded.component_count()
    assert circuit.net_count() == reloaded.net_count()
    # PCB layer round-trips faithfully.
    assert circuit.pcb == reloaded.pcb


# ---- schematic-only path is unaffected ----------------------------------------


def test_schematic_only_model_is_valid() -> None:
    """A model with no PCB data is still valid — pcb=None is the default."""
    c = CircuitProject(
        project=ProjectInfo(name="t", source_format="internal"),
        components=[
            Component(ref="R1", type="resistor", pins=[Pin(number="1"), Pin(number="2")])
        ],
        nets=[Net(name="N", nodes=["R1.1", "R1.2"])],
    )
    assert c.pcb is None
    errors = [w for w in c.check_integrity() if w.severity is Severity.ERROR]
    assert errors == []


# ---- helpers ------------------------------------------------------------------


def _minimal_project_with_r1() -> CircuitProject:
    """Minimal schematic project with one 2-pin resistor, used in PCB tests."""
    return CircuitProject(
        project=ProjectInfo(name="t", source_format="internal"),
        components=[
            Component(ref="R1", type="resistor", pins=[Pin(number="1"), Pin(number="2")])
        ],
        nets=[Net(name="N", nodes=["R1.1", "R1.2"])],
    )


def _smd_pad(number: str, x: float) -> PadDef:
    return PadDef(
        number=number,
        pad_type=PadType.SMD,
        shape=PadShape.RECT,
        size_x=1.8,
        size_y=1.2,
        position=Point(x=x, y=0.0),
        layers=["front_copper"],
    )


# ---- PCB integrity checks fire on broken data --------------------------------


def test_pcb_unknown_ref_fires() -> None:
    c = _minimal_project_with_r1().model_copy(update={
        "pcb": BoardLayout(placements=[Placement(ref="R99", x=0.0, y=0.0)])
    })
    codes = {w.code for w in c.check_integrity()}
    assert "PCB_UNKNOWN_REF" in codes


def test_pcb_duplicate_placement_fires() -> None:
    c = _minimal_project_with_r1().model_copy(update={
        "pcb": BoardLayout(placements=[
            Placement(ref="R1", x=0.0, y=0.0),
            Placement(ref="R1", x=10.0, y=0.0),
        ])
    })
    codes = {w.code for w in c.check_integrity()}
    assert "PCB_DUPLICATE_PLACEMENT" in codes


def test_pcb_pad_unknown_pin_fires() -> None:
    fp = FootprintDef(pads=[
        _smd_pad("1", -0.8),
        _smd_pad("99", 0.8),  # pin "99" does not exist on R1
    ])
    c = _minimal_project_with_r1().model_copy(update={
        "pcb": BoardLayout(placements=[Placement(ref="R1", x=0.0, y=0.0, footprint=fp)])
    })
    codes = {w.code for w in c.check_integrity()}
    assert "PCB_PAD_UNKNOWN_PIN" in codes


def test_pcb_outline_too_few_points_fires() -> None:
    c = _minimal_project_with_r1().model_copy(update={
        "pcb": BoardLayout(
            placements=[Placement(ref="R1", x=0.0, y=0.0)],
            outline=BoardOutline(
                points=[Point(x=0.0, y=0.0), Point(x=10.0, y=0.0)],  # only 2 — too few
                arcs=[],
            ),
        )
    })
    codes = {w.code for w in c.check_integrity()}
    assert "PCB_OUTLINE_TOO_FEW_POINTS" in codes


def test_pcb_outline_with_arc_only_does_not_fire_too_few_points() -> None:
    """An outline with only arcs and no polygon points is valid."""
    arc = ArcSegment(
        start=Point(x=10.0, y=0.0),
        end=Point(x=0.0, y=10.0),
        center=Point(x=0.0, y=0.0),
    )
    c = _minimal_project_with_r1().model_copy(update={
        "pcb": BoardLayout(
            placements=[Placement(ref="R1", x=0.0, y=0.0)],
            outline=BoardOutline(points=[], arcs=[arc]),
        )
    })
    codes = {w.code for w in c.check_integrity()}
    assert "PCB_OUTLINE_TOO_FEW_POINTS" not in codes


def test_pcb_valid_with_no_footprint() -> None:
    """A placement without a footprint is valid (footprint detail may be unknown)."""
    c = _minimal_project_with_r1().model_copy(update={
        "pcb": BoardLayout(placements=[Placement(ref="R1", x=5.0, y=5.0)])
    })
    errors = [w for w in c.check_integrity() if w.severity is Severity.ERROR]
    assert errors == []


def test_pcb_valid_footprint_with_all_pads_matching() -> None:
    """A footprint whose every pad maps to a real pin passes integrity."""
    fp = FootprintDef(
        library_ref="Resistor_SMD:R_0603_1608Metric",
        pads=[_smd_pad("1", -0.8), _smd_pad("2", 0.8)],
    )
    c = _minimal_project_with_r1().model_copy(update={
        "pcb": BoardLayout(placements=[Placement(ref="R1", x=5.0, y=5.0, footprint=fp)])
    })
    errors = [w for w in c.check_integrity() if w.severity is Severity.ERROR]
    assert errors == []


def test_through_hole_component_placement_passes() -> None:
    """Through-hole pads with drill diameters pass integrity checks."""
    proj = CircuitProject(
        project=ProjectInfo(name="t", source_format="internal"),
        components=[
            Component(ref="J1", type="connector", pins=[Pin(number="1"), Pin(number="2")])
        ],
        nets=[Net(name="N", nodes=["J1.1", "J1.2"])],
        pcb=BoardLayout(
            placements=[
                Placement(
                    ref="J1",
                    x=5.0,
                    y=5.0,
                    footprint=FootprintDef(
                        pads=[
                            PadDef(
                                number="1",
                                pad_type=PadType.THROUGH_HOLE,
                                shape=PadShape.CIRCLE,
                                size_x=1.6,
                                size_y=1.6,
                                position=Point(x=0.0, y=0.0),
                                drill_diameter=0.8,
                                layers=["front_copper", "back_copper"],
                            ),
                            PadDef(
                                number="2",
                                pad_type=PadType.THROUGH_HOLE,
                                shape=PadShape.CIRCLE,
                                size_x=1.6,
                                size_y=1.6,
                                position=Point(x=2.54, y=0.0),
                                drill_diameter=0.8,
                                layers=["front_copper", "back_copper"],
                            ),
                        ]
                    ),
                )
            ]
        ),
    )
    errors = [w for w in proj.check_integrity() if w.severity is Severity.ERROR]
    assert errors == []


def test_bottom_side_placement_accepted() -> None:
    """A component mounted on the bottom side is valid."""
    c = _minimal_project_with_r1().model_copy(update={
        "pcb": BoardLayout(
            placements=[Placement(ref="R1", x=5.0, y=5.0, side=BoardSide.BOTTOM, rotation=180.0)]
        )
    })
    errors = [w for w in c.check_integrity() if w.severity is Severity.ERROR]
    assert errors == []


def test_layer_stack_round_trips() -> None:
    """StackLayer objects survive to_json -> reload without data loss."""
    c = _minimal_project_with_r1().model_copy(update={
        "pcb": BoardLayout(
            placements=[Placement(ref="R1", x=0.0, y=0.0)],
            layer_stack=[
                StackLayer(name="front_copper", kind=LayerKind.COPPER, thickness_mm=0.035),
                StackLayer(name="core_1", kind=LayerKind.DIELECTRIC, thickness_mm=1.5),
                StackLayer(name="back_copper", kind=LayerKind.COPPER, thickness_mm=0.035),
            ],
        )
    })
    reloaded = CircuitProject.model_validate_json(c.to_json())
    assert c.pcb == reloaded.pcb


def test_extra_fields_on_placement_rejected() -> None:
    """extra='forbid' is enforced on Placement."""
    with pytest.raises(Exception):
        Placement.model_validate({"ref": "R1", "x": 0.0, "y": 0.0, "unknown_field": 42})


def test_extra_fields_on_pad_rejected() -> None:
    """extra='forbid' is enforced on PadDef."""
    with pytest.raises(Exception):
        PadDef.model_validate({
            "number": "1", "size_x": 1.0, "size_y": 1.0,
            "position": {"x": 0.0, "y": 0.0},
            "bogus": True,
        })
