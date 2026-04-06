import time
import os
import argparse
import sys
import traceback
from typing import Dict
from compilers.weaver.compiler.entrypoint import Max3satQaoaCompiler
from compilers.weaver.nac.config import FPQAConfig
from compilers.weaver.utils.sat_utils import get_color_map
from pysat.formula import CNF

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--circuit', required=True, help='Path to CNF file')
    parser.add_argument('--result-dir', default='results', help='Output directory')
    parser.add_argument('--u3-gate-fidelity', type=float, default=0.999, help='Fidelity of a U3 gate')
    parser.add_argument('--cz-gate-fidelity', type=float, default=0.995, help='Fidelity of a CZ gate')
    parser.add_argument('--ccz-gate-fidelity', type=float, default=0.98, help='Fidelity of a CCZ gate')
    parser.add_argument('--u3-gate-duration', type=float, default=0.5, help='Duration of a U3 gate in microseconds')
    parser.add_argument('--cz-gate-duration', type=float, default=0.2, help='Duration of a CZ gate in microseconds')
    parser.add_argument('--ccz-gate-duration', type=float, default=1.0, help='Duration of a CCZ gate in microseconds')
    parser.add_argument('--qubit-decay', type=float, default=1e08, help='Qubit T1 decay time in microseconds')
    parser.add_argument('--qubit-dephasing', type=float, default=1.5e06, help='Qubit T2 dephasing time in microseconds')
    parser.add_argument('--shuttling-fidelity', type=float, default=1.0, help='Fidelity of a shuttling operation')
    parser.add_argument('--shuttling-speed', type=float, default=0.55, help='Shuttling speed in micrometers per microsecond')
    parser.add_argument('--trap-swap-duration', type=float, default=20.0, help='Trap swap duration in microseconds')
    parser.add_argument('--trap-swap-fidelity', type=float, default=1.0, help='Trap swap fidelity')
    parser.add_argument('--interaction-radius', type=float, default=2.0, help='Interaction radius in micrometers')
    parser.add_argument('--restriction-radius', type=float, default=4.0, help='Restriction radius in micrometers')
    parser.add_argument('--trap-transfer-proximity', type=float, default=1e-05, help='Trap transfer proximity threshold in micrometers')
    parser.add_argument('--aod-beam-proximity', type=float, default=1e-03, help='AOD beam proximity threshold in micrometers')
    args = parser.parse_args()

    fpqaConfigParameters = _buildDefaultsFromArgs(args) 
    result = compile(args.circuit, args.result_dir, fpqaConfigParameters)
    if result.get("success"):
        print("Compilation successful.")
        sys.exit(0)
    else:
        print(f"Compilation failed with error: {result.get('error')}")
        sys.exit(1)



def compile(circuitFile: str, resultDir: str, fpqaConfigParameters: Dict) -> Dict:

    try:
        # Check if circuit file exists
        if not os.path.exists(circuitFile):
            return {'error': f"Circuit file not found: {circuitFile}", 'success': False}

        # Load and sanitize CNF formula
        formula = _loadAndSanitizeMax3satCNF(circuitFile)
        
        # Create FPQA config with default parameters
        fpqaConfig = FPQAConfig({})
        
        # Create compiler instance
        compiler = Max3satQaoaCompiler(formula, fpqaConfig)

        num_colors, color_map = get_color_map(formula)
        num_slm_rows = (num_colors + 1) * 2
        num_slm_cols = len(formula.clauses) * 3 + formula.nv * 2
        num_aod_rows = 1
        num_aod_cols = formula.nv
        print(f"num_colors: {num_colors}, num_slm_rows: {num_slm_rows}, num_slm_cols: {num_slm_cols}, num_aod_rows: {num_aod_rows}, num_aod_cols: {num_aod_cols}")
        # Compile to FPQA program
        program = compiler.compile_single_layer()


        # Write result to file
        os.makedirs(resultDir, exist_ok=True)

        filename = os.path.basename(circuitFile)
        resultFilename = filename.replace(".cnf", "_result.txt")

        resultPath = os.path.join(resultDir, resultFilename)
        with open(resultPath, "w") as f:
                f.write(program.to_string())

        return {'error': None, 'success': True, 'result_path': resultPath}

    except Exception as e:
        return {'error': f"{e}\n{traceback.format_exc()}", 'success': False} 


def _loadAndSanitizeMax3satCNF(circuitFile: str) -> CNF:
    """
    Load DIMACS CNF and remove spurious empty clauses often produced by trailing
    '%'/'0' terminators. Ensures the resulting instance is proper MAX-3SAT.
    """

    formula = CNF(from_file=circuitFile)

    sanitized_clauses = [clause for clause in formula.clauses if len(clause) > 0]
    non_3sat_clauses = [clause for clause in sanitized_clauses if len(clause) != 3]

    if non_3sat_clauses:
        raise ValueError(
            f"Unsupported CNF: expected only 3-literal clauses, found clause lengths "
            f"{sorted({len(c) for c in non_3sat_clauses})} in '{circuitFile}'"
        )

    cleaned = CNF()
    for clause in sanitized_clauses:
        cleaned.append(clause)

    return cleaned
        

def _buildDefaultsFromArgs(args):
    return {
        "U3_GATE_FIDELITY": args.u3_gate_fidelity,
        "U3_GATE_DURATION": args.u3_gate_duration,
        "CZ_GATE_FIDELITY": args.cz_gate_fidelity,
        "CZ_GATE_DURATION": args.cz_gate_duration,
        "CCZ_GATE_FIDELITY": args.ccz_gate_fidelity,
        "CCZ_GATE_DURATION": args.ccz_gate_duration,
        "QUBIT_DECAY": args.qubit_decay,
        "QUBIT_DEPHASING": args.qubit_dephasing,
        "SHUTTLING_FIDELITY": args.shuttling_fidelity,
        "SHUTTLING_SPEED": args.shuttling_speed,
        "TRAP_SWAP_DURATION": args.trap_swap_duration,
        "TRAP_SWAP_FIDELITY": args.trap_swap_fidelity,
        "INTERACTION_RADIUS": args.interaction_radius,
        "RESTRICTION_RADIUS": args.restriction_radius,
        "TRAP_TRANSFER_PROXIMITY": args.trap_transfer_proximity,
        "AOD_BEAM_PROXIMITY": args.aod_beam_proximity,
    }


if __name__ == "__main__":
    main()
