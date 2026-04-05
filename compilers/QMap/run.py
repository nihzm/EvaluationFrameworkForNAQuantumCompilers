
from __future__ import annotations

import os
import argparse
from pathlib import Path
import json
import math
import re
from qiskit import transpile
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence


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
    from qiskit import QuantumCircuit, qasm2, qasm3
except Exception as e:
    raise RuntimeError("Could not import qiskit. Please 'pip install qiskit'.") from e



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--circuit', required=True, help='Path to QASM file')
    parser.add_argument('--zac', action="store_true", help='Compile using ZAC-style compiler.')
    parser.add_argument("--result-dir", default="results", help="Output directory.")
    parser.add_argument("--array-width", type=int, default=16, help="Total logical array width in qubit sites.")
    parser.add_argument("--array-height", type=int, default=16, help="Total logical array height in qubit sites.")
    parser.add_argument("--aod-rows", type=int, default=8, help="Number of rows in the AOD.")
    parser.add_argument("--aod-columns", type=int, default=8, help="Number of columns in the AOD.")
    parser.add_argument("--slm-site-separation", type=float, default=2.0, help="Site separation for SLM traps.")
    parser.add_argument("--aod-site-separation", type=float, default=2.0, help="Site separation for AOD traps.")
    parser.add_argument("--rydberg-gate-duration", type=float, default=0.36, help="Duration of Rydberg gates in microseconds.")
    parser.add_argument("--single-qubit-gate-duration", type=float, default=52, help="Duration of single-qubit gates in microseconds.")
    parser.add_argument("--atom-transfer-duration", type=float, default=15, help="Duration of atom transfer operations in microseconds.")
    parser.add_argument("--rydberg-gate-fidelity", type=float, default=0.995, help="Fidelity of Rydberg gates.")
    parser.add_argument("--single-qubit-gate-fidelity", type=float, default=0.9997, help="Fidelity of single-qubit gates.")
    parser.add_argument("--atom-transfer-fidelity", type=float, default=0.999, help="Fidelity of atom transfer operations.")
    parser.add_argument("--qubit-coherence-time", type=float, default=1.5e6, help="Qubit coherence time T in microseconds.")
    
    args = parser.parse_args()

    if not os.path.exists(args.circuit):
        return (f"Circuit file not found: {args.circuit}", False)

    circuit = _loadQasmCircuit(Path(args.circuit))
    num_qubits = circuit.num_qubits

    # Build architecture JSON string based on command-line parameters and circuit qubit count
    archJson = _buildArchitectureJson(
        array_width=args.array_width,
        array_height=args.array_height,
        aod_rows=args.aod_rows,
        aod_cols=args.aod_columns,
        num_circuit_qubits=num_qubits,
        slm_site_separation=args.slm_site_separation,
        aod_site_separation=args.aod_site_separation,
        rydberg_gate_duration=args.rydberg_gate_duration,
        single_qubit_gate_duration=args.single_qubit_gate_duration,
        atom_transfer_duration=args.atom_transfer_duration,
        rydberg_gate_fidelity=args.rydberg_gate_fidelity,
        single_qubit_gate_fidelity=args.single_qubit_gate_fidelity,
        atom_transfer_fidelity=args.atom_transfer_fidelity,
        T=args.qubit_coherence_time
    )

    result = compile(circuit, args.circuit, args.result_dir, args.zac, archJson)
    if result['success']:
        print("Compilation successful.")
    else:
        print(f"Compilation failed with error: {result['error']}")

def compile(circuit, circuitFile: str, resultDir: str, zac: bool, archJson: str) -> Dict:

    # Load architecture from JSON string, returns a ZonedNeutralAtomArchitecture object from QMAP's zoned NA compiler module
    arch = _loadArchitecture(archJson)

    # Compilers:
    # - RoutingAgnosticCompiler: reuse-aware (often aligned with NALAC-style in discussions)
    # - RoutingAwareCompiler: routing-aware placer + reuse-aware (often aligned with ZAC-style)
    if zac:
        compiler = RoutingAwareCompiler(arch)
    else:
        compiler = RoutingAgnosticCompiler(arch)

    # Compile — returns `.naviz` program text per QMAP docs.
    navizResult = compiler.compile(circuit)

    # Write result to file
    os.makedirs(resultDir, exist_ok=True)

    filename = os.path.basename(circuitFile)
    stem, _ = os.path.splitext(filename)
    resultFilename = f"{stem}_result.naviz"

    resultPath = os.path.join(resultDir, resultFilename)
    with open(resultPath, "w") as f:
            f.write(navizResult)

    return {'error': None, 'success': True}


def _loadQasmCircuit(qasmPath: Path):
    """
    Load OpenQASM file into an MQT circuit object.

    Strategy:
      1) Parse OpenQASM 2 or 3 via Qiskit.
      2) Map to the gate set {u3, cz}.
      3) Convert to MQT core circuit via mqt.core.load.
    """
    qasm_str = qasmPath.read_text(encoding="utf-8")
    if re.search(r"OPENQASM\s+3", qasm_str, flags=re.IGNORECASE):
        qc = qasm3.loads(qasm_str)
    else:
        qc = qasm2.loads(qasm_str)

    qc = qc.remove_final_measurements(inplace=False)
    qc = transpile(qc, basis_gates=["u3", "cz"], optimization_level=2)
    return mqt_load(qc)


def _buildArchitectureJson(
    array_width: int,
    array_height: int,
    aod_rows: int,
    aod_cols: int,
    num_circuit_qubits: int,
    slm_site_separation: float,
    aod_site_separation: float,
    rydberg_gate_duration: float,
    single_qubit_gate_duration: float,
    atom_transfer_duration: float,
    rydberg_gate_fidelity: float,
    single_qubit_gate_fidelity: float,
    atom_transfer_fidelity: float,
    T: float
) -> str:
    """
    Build a zoned architecture JSON specification with:
      - exactly one storage-zone SLM
      - exactly one entanglement-zone SLM
      - exactly one AOD array

    Geometry model
    --------------
    The full logical array is a grid of `array_width * array_height` sites.
    It is split row-wise into:
      - storage zone: the minimum number of rows required to hold
        `num_circuit_qubits`
      - entanglement zone: all remaining rows

    So:
      storage_rows = ceil(num_circuit_qubits / array_width)
      entanglement_rows = array_height - storage_rows

    The Rydberg range is encoded as the bounding box of the entanglement zone:
      [[[x_min, y_min], [x_max, y_max]]]

    Notes
    -----
    - `storage_site_separation` and `entanglement_site_separation` are [dx, dy].
    - If you want both zones to live on the same physical pitch, pass the same
      separation for both.
    - `dimension` is computed as the rectangular extent of the SLM field:
        [num_cols * dx, num_rows * dy]
      which is consistent with treating the zone as an area rather than only the
      coordinates of occupied trap centers.
    - By default, the storage zone starts at `origin`, and the entanglement zone
      is placed directly below it with an optional `zone_gap_y`.
    """


    # 1. Validate inputs
    def __validate_positive_int(name: str, value: int) -> None:
        if not isinstance(value, int) or value <= 0:
            raise ValueError(f"{name} must be a positive integer, got {value!r}")

    __validate_positive_int("array_width", array_width)
    __validate_positive_int("array_height", array_height)
    __validate_positive_int("num_circuit_qubits", num_circuit_qubits)
    __validate_positive_int("aod_rows", aod_rows)
    __validate_positive_int("aod_cols", aod_cols)

    if num_circuit_qubits > array_width * array_height:
        raise ValueError(
            "num_circuit_qubits cannot exceed total array capacity "
            f"({array_width * array_height})"
        )

    if aod_site_separation <= 0:
        raise ValueError("aod_site_separation must be > 0")

    if T <= 0:
        raise ValueError("T must be a positive float")

    storage_rows = math.ceil(num_circuit_qubits / array_width)
    entanglement_rows = array_height - storage_rows

    if entanglement_rows <= 0:
        raise ValueError(
            "The split leaves no entanglement zone. "
            "Increase array_height or reduce num_circuit_qubits."
        )


    # 2. Build architecture dict
    arch = {
        "name": "Single-SLM Single-AOD Zoned Neutral-Atom Architecture",
        "operation_duration": {
            "rydberg_gate": rydberg_gate_duration,
            "single_qubit_gate": single_qubit_gate_duration,
            "atom_transfer": atom_transfer_duration,
        },
        "operation_fidelity": {
            "rydberg_gate": rydberg_gate_fidelity,
            "single_qubit_gate": single_qubit_gate_fidelity,
            "atom_transfer": atom_transfer_fidelity,
        },
        "qubit_spec": {"T": T},
        "storage_zones": [
            {
                "zone_id": 0,
                "slms": [
                    {
                        "id": 0,
                        "site_separation": [slm_site_separation, slm_site_separation],
                        "r": storage_rows,
                        "c": array_width,
                        "location": [0, 0],
                    },
                ],
                "offset": [0, 0],
                "dimension": [array_width * slm_site_separation, storage_rows * slm_site_separation],
            }
        ],
        "entanglement_zones": [
            {
                "zone_id": 0,
                "slms": [
                    {
                        "id": 2,
                        "site_separation": [slm_site_separation, slm_site_separation],
                        "r": math.floor(entanglement_rows / 2),
                        "c": array_width,
                        "location": [0, storage_rows * slm_site_separation],
                    },
                    {
                        "id": 3,
                        "site_separation": [slm_site_separation, slm_site_separation],
                        "r": math.ceil(entanglement_rows / 2),
                        "c": array_width,
                        "location": [0, (storage_rows + math.floor(entanglement_rows / 2)) * slm_site_separation],
                    }
                ],
                "offset": [0, storage_rows * slm_site_separation],
                "dimension": [array_width * slm_site_separation, entanglement_rows * slm_site_separation],
            }
        ],
        "aods": [
            {
                "id": 0,
                "site_separation": aod_site_separation,
                "r": aod_rows,
                "c": aod_cols,
            }
        ],
        "rydberg_range": [
            [
                [0, storage_rows * slm_site_separation],
                [array_width * slm_site_separation, (storage_rows + entanglement_rows) * slm_site_separation],
            ]
        ],
    }

    return json.dumps(arch, indent=2)




def _loadArchitecture(archJsonString: str) -> ZonedNeutralAtomArchitecture:
    json.loads(archJsonString)
    return ZonedNeutralAtomArchitecture.from_json_string(archJsonString)

if __name__ == "__main__":
    raise SystemExit(main())
