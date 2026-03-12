from qiskit import transpile

import numpy as np
import pandas as pd
import os
#import seaborn as sns
from ..compilers.Weaver.compilers.weaver.utils.hamiltonians import Max3satHamiltonian
from ..compilers.Weaver.compilers.weaver.utils.qaoa import QAOA

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
                    'uuf100-010.cnf',
                    'uuf150-01.cnf',
                    'uuf150-02.cnf',
                    'uuf150-03.cnf',
                    'uuf150-04.cnf',
                    'uuf150-05.cnf',
                    'uuf150-06.cnf',
                    'uuf150-07.cnf',
                    'uuf150-08.cnf',
                    'uuf150-09.cnf',
                    'uuf150-010.cnf',
                    'uuf250-01.cnf',
                    'uuf250-02.cnf',
                    'uuf250-03.cnf',
                    'uuf250-04.cnf',
                    'uuf250-05.cnf',
                    'uuf250-06.cnf',
                    'uuf250-07.cnf',
                    'uuf250-08.cnf',
                    'uuf250-09.cnf',
                    'uuf250-010.cnf']

def run():

    #basis_gates = ["rx", "rz", "x", "y", "z", "h", "id", "cz"]
    basis_gates = ["u3", "cz"]
    qaoas_instances = []

    transpiled_circuits = []
    
    # -- Iterates benchmarks/max3SAT files to create QAOA circuits into qaoas_instances ---
    for file_name in instances_names:
        
        # -- I added a check if this is not already done ------
        output_dir = "benchmarks/QASMBench"
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(
            output_dir, file_name.replace(".cnf", ".qasm")
        )

        if os.path.exists(output_path):
            print(f"Skipping {file_name}: QASM already exists.")
            continue
        # -----------------------------------------------------

        tmp_hamiltonion = Max3satHamiltonian('benchmarks/max3SAT/'+file_name)
        tmp_qaoa = QAOA(tmp_hamiltonion)
        qaoa_circuit, cost_params, mixer_params = tmp_qaoa.naive_qaoa_circuit(qaoa_depth)

        qaoas_instances.append([qaoa_circuit, cost_params, mixer_params])

    # --- Transpile QAOA circuits and save them as QASM files into transpiled_circuits ---
    for i, qaoas_instance in enumerate(qaoas_instances):
        qaoa_circuit, cost_params, mixer_params = qaoas_instance
        print(f"Transpiling circuit {i} out of {len(qaoas_instances)}")

        bound_circuit = qaoa_circuit.assign_parameters({cost_params: [np.pi / 2.123 for param in cost_params], mixer_params: [np.pi / 3.123 for param in mixer_params]})
        bound_circuit.measure_all()
        transpiled_circuits.append(transpile(bound_circuit, basis_gates=basis_gates, optimization_level=3))
        
    # --- Save transpiled circuits as QASM files in benchmarks/QASMBench/ ---
    for circuit, name in zip(transpiled_circuits, instances_names):
        with open('benchmarks/QASMBench/' + name.strip('.cnf') + '.qasm', 'w') as f:
            f.write(circuit.qasm())