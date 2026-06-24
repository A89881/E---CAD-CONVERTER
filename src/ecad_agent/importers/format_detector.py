"""Basic ECAD format detection."""

from __future__ import annotations

from enum import StrEnum
from pathlib import Path


class EcadFormat(StrEnum):
    INTERNAL_JSON = "internal-json"
    KICAD_SCHEMATIC = "kicad-schematic"
    KICAD_PCB = "kicad-pcb"
    EASYEDA_JSON = "easyeda-json"
    EAGLE_XML = "eagle-xml"
    UNKNOWN = "unknown"


def detect_format(path: str | Path) -> EcadFormat:
    source = Path(path)
    suffix = source.suffix.lower()
    name = source.name.lower()

    if suffix == ".kicad_sch":
        return EcadFormat.KICAD_SCHEMATIC
    if suffix == ".kicad_pcb":
        return EcadFormat.KICAD_PCB
    if suffix == ".json":
        return EcadFormat.EASYEDA_JSON if "easyeda" in name else EcadFormat.INTERNAL_JSON
    if suffix in {".sch", ".brd"}:
        return EcadFormat.EAGLE_XML
    return EcadFormat.UNKNOWN
