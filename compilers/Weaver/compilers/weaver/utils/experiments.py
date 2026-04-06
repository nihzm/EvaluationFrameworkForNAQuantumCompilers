from qiskit import transpile
from qiskit.providers import BackendV2
from utils.circuit_utils import calculate_expected_fidelity, calculate_expected_fidelity_ideal, calculate_swap_overhead
from utils.qaoa import QAOA
from utils.hamiltonians import Max3satHamiltonian
import numpy as np
import pandas as pd

INSTANCES_FOLDER = "./instances/"
RESULTS_FOLDER = "./results/"

SUPERCONDUCTING_DATA_SCHEMA = [
    "Name",
    "Hardware",
    "QAOA Depth",
    "Average Circuit Depth",
    "Ideal Fidelity",
    "Ideal Estimated Shots",
    "Fidelity with Decoherence", 
    "Estimated Shots with Decoherence for 2/3 Success Rate", 
    "Fidelity without Decoherence", 
    "Estimated Shots without Decoherence for 2/3 Success Rate", 
    "Average Swap Overhead", 
    "Average Number of Two Qubit Gates", 
    "Iterations"
]

class SuperconductingExperiment:
    def __init__(self, experiment_name, problem_names: list[str], backend: BackendV2):
        self.experiment_name = experiment_name
        self.problem_names = problem_names
        self.backend = backend
        
    def run(self, max_depth=1, max_iterations=10) -> pd.DataFrame:
        data = []
        for problem_name in self.problem_names:
            hamiltonian = Max3satHamiltonian(INSTANCES_FOLDER + problem_name)
            qaoa = QAOA(hamiltonian)
            print(f">>> Starting experiments with Problem: {problem_name} ...")
            for p in range(1, max_depth + 1):
                qaoa_circuit, cost_params, mixer_params = qaoa.naive_qaoa_circuit(p)
                fidelity, estimated_shots = 0.0, 0
                fidelity_with_decoherence, estimated_shots_with_decoherence = 0.0, 0
                ideal_fidelity, ideal_estimated_shots = 0.0, 0
                circuit_depth, num_two_qubit_gates, swap_overhead = 0, 0, 0
                print(f">>> Parametrized circuit created, Depth: {p} ...")
                for i in range(max_iterations):
                    print(f">>> Transpiling parametrized circuit, Iteration: {i} ...") 
                    params = {
                        cost_params: np.random.uniform(low=0.0, high=2*np.pi, size=len(cost_params)),
                        mixer_params: np.random.uniform(low=0, high=np.pi, size=len(mixer_params))
                    }
                    bound_circuit = qaoa_circuit.assign_parameters(params)
                    bound_circuit.measure_all()
                    transpiled_circuit = transpile(bound_circuit, backend=self.backend, optimization_level=3)
                    fwd, f, eswd, es = calculate_expected_fidelity(transpiled_circuit, self.backend)
                    ideal_f, ideal_es = calculate_expected_fidelity_ideal(transpiled_circuit)
                    fidelity_with_decoherence += fwd
                    fidelity += f
                    estimated_shots_with_decoherence += eswd
                    estimated_shots += es
                    num_two_qubit_gates += transpiled_circuit.count_ops()["ecr"]
                    swap_overhead += calculate_swap_overhead(bound_circuit, transpiled_circuit)
                    ideal_fidelity += ideal_f
                    ideal_estimated_shots += ideal_es
                    circuit_depth += transpiled_circuit.depth()
                avg_results = np.array([circuit_depth, ideal_fidelity, ideal_estimated_shots, 
                                        fidelity_with_decoherence, estimated_shots_with_decoherence, 
                                        fidelity, estimated_shots, 
                                        swap_overhead, num_two_qubit_gates], 
                                       dtype=float) / max_iterations
                avg_results = avg_results.tolist()
                avg_results[-2] = int(np.ceil(avg_results[-2]))
                avg_results[-1] = int(np.ceil(avg_results[-1]))
                data.append([problem_name, self.backend.name, p] + avg_results + [max_iterations])
        df = pd.DataFrame(data, columns=SUPERCONDUCTING_DATA_SCHEMA)
        df.to_csv(RESULTS_FOLDER + self.experiment_name + ".csv", index=False)
        return df