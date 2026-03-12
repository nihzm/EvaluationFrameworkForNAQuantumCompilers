from enola.enola import Enola
import qiskit.qasm2
import argparse
import json
import qiskit.circuit
from qiskit import transpile
from typing import Dict

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--circuit', type=str, help='qasm file name')
    parser.add_argument('--result-dir', type=str, required=True, help='directory to save results')
    parser.add_argument('--array-width', type=int, help='Width of the qubit array')
    parser.add_argument('--array-height', type=int, help='Height of the qubit array')
    parser.add_argument('--aod-columns', type=int, help='Number of columns in the AOD')
    parser.add_argument('--aod-rows', type=int, help='Number of rows in the AOD')
    parser.add_argument('--routing-strategy', type=str, help='Routing strategy to use')
    parser.add_argument('--r2i', action='store_true', help='Whether to reverse to initial layout after each layer')
    parser.add_argument('--dependency', action='store_true', help='Whether to consider dependencies between gates')
    parser.add_argument('--use-window', action='store_true', help='Whether to use a sliding window approach for compilation')
    parser.add_argument('--full-code', action='store_true', help='Whether to save the full code of the compiler (including intermediate steps) instead of just the final results')
    parser.add_argument('--trivial-layout', action='store_true', help='Whether to use a trivial layout (mapping qubits in order of appearance in the circuit) instead of a more sophisticated initial layout strategy')
    args = parser.parse_args()

    error, success = compile(args.circuit, args.result_dir, args.array_width, args.array_height, args.aod_columns, args.aod_rows, args.routing_strategy, args.r2i, args.dependency, args.use_window, args.full_code, args.trivial_layout)
    if success:
        print("Compilation successful.")
    else:
        print(f"Compilation failed with error: {error}")
    pass



def compile(qasmFile: str, resultDir: str, array_width: int,
            array_height: int, aod_columns: int, aod_rows: int, routing_strategy: str,
            r2i: bool, dependency: bool, use_window: bool, full_code: bool, trivial_layout: bool) -> Dict:

    try:
        # Initialize compiler and its strategy
        compiler = Enola(qasmFile, 
            dir=resultDir,
            trivial_layout = trivial_layout,
            routing_strategy=routing_strategy,
            reverse_to_initial=r2i,
            dependency = dependency,
            use_window=use_window,
            full_code=full_code
        )

        # Extract two-qubit gates from qasm file
        twoQubitGates = []
        with open(qasmFile, 'r') as f:
            qasmStr = f.read()
            circuit = qiskit.qasm2.loads(qasmStr)
            cz_circuit = transpile(circuit, basis_gates=['cz', 'rx', 'ry', 'rz', 'h', 't']) #TODO configure basis gates
            instruction = cz_circuit.data
            for ins in instruction:
                if ins.operation.num_qubits == 2:
                    twoQubitGates.append((ins.qubits[0]._index, ins.qubits[1]._index))
        compiler.setProgram(twoQubitGates)

        # Set architecture parameters for the compiler
        compiler.setArchitecture([array_width, array_height, aod_columns, aod_rows])

        # Run the compiler and save results
        compiler.solve(save_file=True)
        return {'error': None, 'success': True}
    
    except Exception as e:
        return {'error': str(e), 'success': False}
    
    
if __name__ == "__main__":
    main()