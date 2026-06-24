"""Tests for the neutral internal ECAD model."""

from __future__ import annotations

from pathlib import Path

import pytest

from ecad_agent.model import (
    CircuitProject,
    Component,
    Net,
    NodeRef,
    Pin,
    ProjectInfo,
    Severity,
)

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = sorted((ROOT / "examples").glob("*/model.json"))


# ---- example circuits --------------------------------------------------------

@pytest.mark.parametrize("path", EXAMPLES, ids=lambda p: p.parent.name)
def test_examples_load_and_have_no_errors(path: Path) -> None:
    circuit = CircuitProject.load(path)
    errors = [w for w in circuit.check_integrity() if w.severity is Severity.ERROR]
    assert errors == [], f"{path.parent.name} has integrity errors: {errors}"


@pytest.mark.parametrize("path", EXAMPLES, ids=lambda p: p.parent.name)
def test_examples_round_trip(path: Path) -> None:
    circuit = CircuitProject.load(path)
    reloaded = CircuitProject.model_validate_json(circuit.to_json())
    assert circuit.node_map() == reloaded.node_map()
    assert circuit.component_count() == reloaded.component_count()
    assert circuit.net_count() == reloaded.net_count()


# ---- node reference parsing --------------------------------------------------

def test_noderef_string_coercion() -> None:
    net = Net(name="N", nodes=["R1.2", "C1.1"])
    assert net.nodes[0] == NodeRef(component="R1", pin="2")
    assert net.nodes[0].as_string() == "R1.2"


def test_noderef_splits_on_last_dot() -> None:
    # A component ref containing a dot still parses correctly.
    ref = NodeRef.from_string("SHEET.U1.3")
    assert ref.component == "SHEET.U1"
    assert ref.pin == "3"


def test_noderef_rejects_garbage() -> None:
    with pytest.raises(ValueError):
        NodeRef.from_string("noseparator")


# ---- integrity checks fire on bad input -------------------------------------

def _two_pin(ref: str, value: str = "10k") -> Component:
    return Component(ref=ref, type="resistor", value=value,
                     pins=[Pin(number="1"), Pin(number="2")])


def test_detects_duplicate_ref() -> None:
    c = CircuitProject(
        project=ProjectInfo(name="t", source_format="internal"),
        components=[_two_pin("R1"), _two_pin("R1")],
        nets=[Net(name="N", nodes=["R1.1", "R1.2"])],
    )
    codes = {w.code for w in c.check_integrity()}
    assert "DUPLICATE_REF" in codes


def test_detects_unknown_component_and_pin() -> None:
    c = CircuitProject(
        project=ProjectInfo(name="t", source_format="internal"),
        components=[_two_pin("R1")],
        nets=[
            Net(name="A", nodes=["R1.1", "R9.1"]),   # R9 does not exist
            Net(name="B", nodes=["R1.2", "R1.7"]),   # pin 7 does not exist
        ],
    )
    codes = {w.code for w in c.check_integrity()}
    assert "UNKNOWN_COMPONENT" in codes
    assert "UNKNOWN_PIN" in codes


def test_detects_unconnected_pin_and_dangling_net() -> None:
    c = CircuitProject(
        project=ProjectInfo(name="t", source_format="internal"),
        components=[_two_pin("R1")],
        nets=[Net(name="A", nodes=["R1.1"])],  # single-node net, R1.2 floating
    )
    codes = {w.code for w in c.check_integrity()}
    assert "DANGLING_NET" in codes
    assert "UNCONNECTED_PIN" in codes


def test_node_map() -> None:
    c = CircuitProject.load(ROOT / "examples" / "rc_filter" / "model.json")
    nm = c.node_map()
    assert nm["R1.1"] == "VIN"
    assert nm["R1.2"] == "VOUT"
    assert nm["C1.2"] == "GND"


# ---- schema hygiene ----------------------------------------------------------

def test_extra_fields_rejected() -> None:
    with pytest.raises(Exception):
        Pin.model_validate({"number": "1", "not_a_field": 7})
