
from __future__ import annotations

import os
from typing import Dict
import argparse
import json
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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--circuit', required=True, help='Path to CNF file')
    parser.add_argument('--zac', action="store_true", help='Compile using ZAC-style compiler.')
    parser.add_argument("--result-dir", default="results", help="Output directory.")
    parser.add_argument("--arch-json", type=Path, default=None, help="Architecture JSON file. If omitted, uses a default.")
    args = parser.parse_args()

    error, success = compile(args.circuit, args.result_dir, args.arch_json, args.zac)
    if success:
        print("Compilation successful.")
    else:
        print(f"Compilation failed with error: {error}")


def compile(circuitFile: str, resultDir: str, architecture: Path, zac: bool) -> Dict:

    if not os.path.exists(circuitFile):
        return {'error': f"Circuit file not found: {circuitFile}", 'success': False}

    # Architecture specification
    arch = _loadArchitecture(architecture)

    # Compilers:
    # - RoutingAgnosticCompiler: reuse-aware (often aligned with NALAC-style in discussions)
    # - RoutingAwareCompiler: routing-aware placer + reuse-aware (often aligned with ZAC-style)
    if zac:
        compiler = RoutingAwareCompiler(arch)
    else:
        compiler = RoutingAgnosticCompiler(arch)

    # Compile — returns `.naviz` program text per QMAP docs.
    circ = _loadQasmCircuit(circuitFile)
    navizResult = compiler.compile(circ)

    # Write result to file
    os.makedirs(resultDir, exist_ok=True)

    filename = os.path.basename(circuitFile)
    resultFilename = filename.replace(".qasm", "_result.naviz")

    resultPath = os.path.join(resultDir, resultFilename)
    with open(resultPath, "w") as f:
            f.write(navizResult)

    return {'error': None, 'success': True}



def _loadArchitecture(archJsonPath: Optional[Path]) -> ZonedNeutralAtomArchitecture:
    if archJsonPath is None:
        return ZonedNeutralAtomArchitecture.from_json_string(DEFAULT_ARCH_JSON)

    data = archJsonPath.read_text(encoding="utf-8")
    # Validate JSON early for clearer error messages
    json.loads(data)
    return ZonedNeutralAtomArchitecture.from_json_string(data)


def _loadQasmCircuit(qasmPath: Path):
    """
    Load OpenQASM file into an MQT circuit object.

    Strategy:
      1) Use Qiskit to parse OpenQASM.
      2) Convert to MQT core circuit via mqt.core.load.
    """
    qc = QuantumCircuit.from_qasm_file(str(qasmPath))
    return mqt_load(qc)




if __name__ == "__main__":
    raise SystemExit(main())
