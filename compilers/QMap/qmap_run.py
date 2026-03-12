#!/usr/bin/env python3
"""
run.py — Compile a .qasm circuit with MQT QMAP's zoned neutral-atom compilers.

Outputs:
  - <out_dir>/<stem>_nalac.naviz   (routing-agnostic compiler; reuse-aware)
  - <out_dir>/<stem>_zac.naviz     (routing-aware compiler; reuse-aware + routing-aware placement)
  - <out_dir>/architecture.namachine (for MQT NAViz)

Requires:
  pip install mqt.qmap mqt.core qiskit
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

# QMAP zoned neutral atom compilers + architecture
from mqt.qmap.na.zoned import (
    ZonedNeutralAtomArchitecture,
    RoutingAgnosticCompiler,
    RoutingAwareCompiler,
)

# Circuit loading
try:
    # mqt-core can load from qiskit circuits and (depending on version) directly from files
    from mqt.core import load as mqt_load
except Exception as e:
    raise RuntimeError(
        "Could not import mqt.core.load. Ensure 'mqt-core'/'mqt.core' is installed."
    ) from e

try:
    from qiskit import QuantumCircuit
except Exception as e:
    raise RuntimeError("Could not import qiskit. Please 'pip install qiskit'.") from e


# A reasonable default architecture taken from the QMAP documentation example.
# You can override via --arch-json <file.json>.
DEFAULT_ARCH_JSON = r"""
{
  "name": "Architecture with one entanglement and one storage zone",
  "operation_duration": {"rydberg_gate": 0.36, "single_qubit_gate": 52, "atom_transfer": 15},
  "operation_fidelity": {"rydberg_gate": 0.995, "single_qubit_gate": 0.9997, "atom_transfer": 0.999},
  "qubit_spec": {"T": 1.5e6},
  "storage_zones": [{
    "zone_id": 0,
    "slms": [{"id": 0, "site_separation": [3, 3], "r": 20, "c": 100, "location": [0, 0]}],
    "offset": [0, 0],
    "dimension": [297, 57]
  }],
  "entanglement_zones": [{
    "zone_id": 0,
    "slms": [
      {"id": 1, "site_separation": [12, 10], "r": 7, "c": 20, "location": [35, 67]},
      {"id": 2, "site_separation": [12, 10], "r": 7, "c": 20, "location": [37, 67]}
    ],
    "offset": [35, 67],
    "dimension": [230, 60]
  }],
  "aods": [{"id": 0, "site_separation": 2, "r": 100, "c": 100}],
  "rydberg_range": [[[30, 62], [270, 132]]]
}
"""


def load_architecture(arch_json_path: Optional[Path]) -> ZonedNeutralAtomArchitecture:
    if arch_json_path is None:
        return ZonedNeutralAtomArchitecture.from_json_string(DEFAULT_ARCH_JSON)

    data = arch_json_path.read_text(encoding="utf-8")
    # Validate JSON early for clearer error messages
    json.loads(data)
    return ZonedNeutralAtomArchitecture.from_json_string(data)


def load_qasm_circuit(qasm_path: Path):
    """
    Load OpenQASM file into an MQT circuit object.

    Strategy:
      1) Use Qiskit to parse OpenQASM.
      2) Convert to MQT core circuit via mqt.core.load.
    """
    qc = QuantumCircuit.from_qasm_file(str(qasm_path))
    return mqt_load(qc)


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description="Run QMAP NALAC/ZAC-style zoned NA compilers on a .qasm file.")
    ap.add_argument("--bench-dir", type=Path, default=Path("WeaverBenchmarks"), help="Directory containing .qasm files.")
    ap.add_argument("--out-dir", type=Path, default=Path("qmap_results"), help="Output directory.")
    ap.add_argument("--arch-json", type=Path, default=None, help="Architecture JSON file. If omitted, uses a default.")
    ap.add_argument("--export-namachine", action="store_true", help="Export architecture.namachine for NAViz.")
    args = ap.parse_args()

    bench_dir: Path = args.bench_dir
    if not bench_dir.exists() or not bench_dir.is_dir():
        print(f"ERROR: benchmark directory does not exist: {bench_dir}", file=sys.stderr)
        return 2

    qasm_files = sorted(bench_dir.glob("*.qasm"))
    if not qasm_files:
        print(f"ERROR: no .qasm files found in {bench_dir}", file=sys.stderr)
        return 3

    out_dir: Path = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    # Architecture
    arch = load_architecture(args.arch_json)

    # Optional: export .namachine for NAViz (recommended if you plan to visualize)
    if args.export_namachine:
        namachine_path = out_dir / "architecture.namachine"
        # Method referenced in the QMAP docs for NAViz interoperability.
        arch.to_namachine_file(str(namachine_path))

    # Compilers:
    # - RoutingAgnosticCompiler: reuse-aware (often aligned with NALAC-style in discussions)
    # - RoutingAwareCompiler: routing-aware placer + reuse-aware (often aligned with ZAC-style)
    nalac_like = RoutingAgnosticCompiler(arch)
    zac_like = RoutingAwareCompiler(arch)

    # Compile — returns `.naviz` program text per QMAP docs.
    for qasm_path in qasm_files:
        print(f"Compiling {qasm_path.name} ...")

        circ = load_qasm_circuit(qasm_path)
        stem = qasm_path.stem

        nalac_naviz = nalac_like.compile(circ)
        zac_naviz = zac_like.compile(circ)

        nalac_out = out_dir / f"{stem}_nalac.naviz"
        zac_out = out_dir / f"{stem}_zac.naviz"

        write_text(nalac_out, str(nalac_naviz))
        write_text(zac_out, str(zac_naviz))

        print(f"  Wrote: {nalac_out}")
        print(f"  Wrote: {zac_out}")

    if args.export_namachine:
        print(f"Wrote: {out_dir / 'architecture.namachine'}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
