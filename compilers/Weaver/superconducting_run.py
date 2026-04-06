#from qiskit import QuantumCircuit
from qiskit import transpile
from qiskit.providers.fake_provider import FakeWashingtonV2, FakeWashington
import pdb
#from utils.utils_fid import calculate_fidelity, estimate_fidelity
#from utils.quasi_distr import QuasiDistr
from time import perf_counter
import numpy as np
#import mapomatic.circuits as mm
import pandas as pd
#import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib import gridspec

from compilers.weaver.utils.hamiltonians import Max3satHamiltonian
from compilers.weaver.utils.sat_utils import uniformly_random_independent_clauses
from compilers.weaver.utils.qaoa import QAOA
from qiskit import QuantumCircuit
from pysat.formula import CNF
from compilers.weaver.utils.circuit_utils import calculate_expected_fidelity
from compilers.geyser.code.map_circuit import MapCircuit
from compilers.geyser.code.block_circuit import BlockCircuit
from compilers.geyser.code.compose_circuit import ComposeCircuit
from qiskit.dagcircuit import DAGCircuit, DAGOpNode
from utils.gate_length_estimator import GateLengthEstimator
from qiskit.converters import circuit_to_dag
from utils.utils_fid import calculate_expected_fidelity

gate_time_1q = 5.0e-07
gate_time_1qplus = 2.0e-07
qaoa_depth = 1

instances_names = [ 'uf20-01.cnf',
                    'uf20-02.cnf',
                    'uf20-03.cnf',
                    'uf20-04.cnf',
                    'uf20-05.cnf',
                    'uf20-06.cnf',
                    'uf20-07.cnf',
                    'uf20-08.cnf',
                    'uf20-09.cnf',
                    'uf20-010.cnf',
                    'uuf50-01.cnf',
                    'uuf50-02.cnf',
                    'uuf50-03.cnf',
                    'uuf50-04.cnf',
                    'uuf50-05.cnf',
                    'uuf50-06.cnf',
                    'uuf50-07.cnf',
                    'uuf50-08.cnf',
                    'uuf50-09.cnf',
                    'uuf50-010.cnf',
                    'uuf75-01.cnf',
                    'uuf75-02.cnf',
                    'uuf75-03.cnf',
                    'uuf75-04.cnf',
                    'uuf75-05.cnf',
                    'uuf75-06.cnf',
                    'uuf75-07.cnf',
                    'uuf75-08.cnf',
                    'uuf75-09.cnf',
                    'uuf75-010.cnf',
                    'uuf100-01.cnf',
                    'uuf100-02.cnf',
                    'uuf100-03.cnf',
                    'uuf100-04.cnf',
                    'uuf100-05.cnf',
                    'uuf100-06.cnf',
                    'uuf100-07.cnf',
                    'uuf100-08.cnf',
                    'uuf100-09.cnf',
                    'uuf100-010.cnf']


def compute_execution_time(circuit):
    dag = circuit_to_dag(circuit)

    path = dag.longest_path()

    total_time = 0
    for i in path:
        if isinstance(i, DAGOpNode):
            if i.name == 'u3':
                total_time += gate_time_1q
            else:
                total_time += gate_time_1qplus
    return total_time

def run():

    basis_gates = ["rx", "rz", "x", "y", "z", "h", "id", "cz"]
    
    qaoas_instances = []
    backend = FakeWashingtonV2()

    transpiled_circuits = []

    for file_name in instances_names:
        tmp_hamiltonion = Max3satHamiltonian('benchmarks/max3SAT/'+file_name)
        tmp_qaoa = QAOA(tmp_hamiltonion)#.naive_qaoa_circuit(qaoa_depth)
        qaoa_circuit, cost_params, mixer_params = tmp_qaoa.naive_qaoa_circuit(qaoa_depth)
        qaoas_instances.append([qaoa_circuit, cost_params, mixer_params])

    for qaoa_circuit, cost_params, mixer_params in qaoas_instances:
        bound_circuit = qaoa_circuit.assign_parameters({cost_params: [np.pi / 2.123 for param in cost_params], mixer_params: [np.pi / 3.123 for param in mixer_params]})
        bound_circuit.measure_all()
        transpiled_circuits.append(transpile(bound_circuit, basis_gates=basis_gates, optimization_level=3))
    
    results = pd.DataFrame(columns=['instance_info', 'n_variables', 'qaoa_depth', '1q_gates', '2q_gates', 'runtime', 'execution_time', 'eps'])
    basis_gates = ["u3", "cz"]

    for circuit, instance_info in zip(transpiled_circuits, instances_names):
        print(f"Transpiling circuit {instance_info}")
        n_variables = circuit.num_qubits
        
        tmp = perf_counter()
        circuit = transpile(circuit, optimization_level=3, backend=backend)
        tmp = perf_counter()-tmp
        exec_time = GateLengthEstimator().estimate_circuit_execution_time(circuit, FakeWashington())

        eps = calculate_expected_fidelity(circuit, backend)

        gate_1q = circuit.count_ops()['x']
        gate_2q = circuit.count_ops()['cx'] + circuit.count_ops()['sx'] + circuit.count_ops()['rz']

        #exec_time = compute_execution_time(circuit)
        results.loc[len(results)] = [instance_info, n_variables, qaoa_depth, gate_1q, gate_2q, tmp, exec_time, eps]
    
    results.to_csv('./results/superconducting_results.csv')
