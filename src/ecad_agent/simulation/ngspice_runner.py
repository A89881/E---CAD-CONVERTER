"""ngspice runner placeholder."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SimulationRunRequest:
    netlist: str
    analysis: str


def run_ngspice(request: SimulationRunRequest) -> str:
    del request
    raise NotImplementedError("ngspice execution is not wired yet.")
