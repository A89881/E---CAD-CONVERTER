"""Load every example circuit, run integrity checks, and prove round-trip.

Usage:  python3 scripts/check_examples.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ecad_agent.model import CircuitProject  # noqa: E402

EXAMPLES = sorted((ROOT / "examples").glob("*/model.json"))


def main() -> int:
    failures = 0
    for path in EXAMPLES:
        circuit = CircuitProject.load(path)
        issues = circuit.check_integrity()
        errors = [w for w in issues if w.severity.value == "error"]
        warns = [w for w in issues if w.severity.value == "warning"]

        # Round-trip: dump -> reload -> the node map must be identical.
        reloaded = CircuitProject.model_validate_json(circuit.to_json())
        roundtrip_ok = circuit.node_map() == reloaded.node_map()

        status = "PASS" if not errors and roundtrip_ok else "FAIL"
        if status == "FAIL":
            failures += 1
        roundtrip = "ok" if roundtrip_ok else "BROKEN"
        print(
            f"[{status}] {circuit.project.name:18s} "
            f"components={circuit.component_count():2d} nets={circuit.net_count():2d} "
            f"errors={len(errors)} warnings={len(warns)} roundtrip={roundtrip}"
        )
        for w in issues:
            print(f"         - {w.severity.value:7s} {w.code:18s} {w.message}")

    print()
    print("ALL EXAMPLES OK" if failures == 0 else f"{failures} EXAMPLE(S) FAILED")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
