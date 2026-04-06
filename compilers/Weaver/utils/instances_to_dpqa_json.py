from qiskit import transpile
import pdb
from time import perf_counter
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import gridspec
from compilers.weaver.utils.hamiltonians import Max3satHamiltonian
from compilers.weaver.utils.sat_utils import uniformly_random_independent_clauses
from compilers.weaver.utils.qaoa import QAOA
from qiskit import QuantumCircuit
from compilers.weaver.utils.circuit_utils import calculate_expected_fidelity
import pickle
from pysat.formula import CNF
import json
import os

instances_names = ['uf20-01.cnf',
                    'uf20-02.cnf',
                    'uf20-03.cnf',
                    'uf20-04.cnf',
                    'uf20-05.cnf',
                    'uf20-06.cnf',
                    'uf20-07.cnf',
                    'uf20-08.cnf',
                    'uf20-09.cnf',
                    'uf20-010.cnf',]

#instances_names = ['uf3-01.cnf',
#                    'uf3-02.cnf',
#                    'uf3-03.cnf',
#                    'uf3-04.cnf',
#                    'uf3-05.cnf']

qaoa_depth = 1

def run():

    basis_gates = ["u3", "cz"]
    qaoas_instances = []
    #if not isinstance(instances_names, list):
    #    instances_names = [instances_names]

    #for file_name in instances_names:
    #    tmp_hamiltonion = Max3satHamiltonian('benchmarks/max3SAT/'+file_name)
    #    tmp_qaoa = QAOA(tmp_hamiltonion)#.naive_qaoa_circuit(qaoa_depth)
    #    qaoa_circuit, cost_params, mixer_params = tmp_qaoa.naive_qaoa_circuit(qaoa_depth)
    #    qaoas_instances.append([qaoa_circuit, cost_params, mixer_params])

    #for i, qaoas_instance in enumerate(qaoas_instances):
    #    qaoa_circuit, cost_params, mixer_params = qaoas_instance
    #    print(f"Transpiling circuit {i} out of {len(qaoas_instances)}")
    #    bound_circuit = qaoa_circuit.assign_parameters({cost_params: [np.pi / 2.123 for param in cost_params], mixer_params: [np.pi / 3.123 for param in mixer_params]})
    #    bound_circuit.measure_all()
    #    transpiled_circuits.append(transpile(bound_circuit, basis_gates=basis_gates, optimization_level=3))


    #for i, circuit in enumerate(transpiled_circuits):
    #    if os.path.exists('benchmarks/DPQA/' + instances_names[i].replace('.cnf', '.qasm')):
    #        continue
    #    with open('benchmarks/DPQA/' + instances_names[i].replace('.cnf', '.qasm'), 'x') as f:
    #        f.write(circuit.qasm())
    
    for name in instances_names:
        n_variables = int(name.split('-')[0].replace('uf', ''))
        n_variant = name.split('-')[1].strip('.cnf')

        with open('benchmarks/QASMBench/' + name.replace('.cnf', '.qasm'), 'r') as f:
            qasm = f.read()
            #transpiled_circuit.append(QuantumCircuit.from_qasm_str(qasm))
            transpiled_circuit = QuantumCircuit.from_qasm_str(qasm)
        
        cz_gates = []

        for instr in transpiled_circuit.data:
            if instr[0].name == 'cz':
                cz_gates.append([instr[1][0].index, instr[1][1].index])

        #n_variables = [transpiled_circuits[i].num_qubits for i in range(len(transpiled_circuits))]

        transformed_list = {}
        transformed_list[str(n_variables)] = [[]]

        for cz in cz_gates:
            #check if the last one added is not the same
            if transformed_list[str(n_variables)][0] == []:
                transformed_list[str(n_variables)][0].append([cz[0], cz[1]])
            elif transformed_list[str(n_variables)][0][-1] != [cz[0], cz[1]]:
                transformed_list[str(n_variables)][0].append([cz[0], cz[1]])

        with open(f"benchmarks/DPQA/graph{n_variables}_{n_variant}.json", "w") as outfile:
            json.dump(transformed_list, outfile, indent=4)

    #for circuit, name in zip(transpiled_circuits, instance_clauses if instance_type == 'generated' else instances_names):
    #    if instance_type == 'generated':
    #        name = 'generated_' + str(qaoa_depth) + 'n' + str(name)
    #    with open('./evaluation/benchmarks/QASMBench/' + name + '.qasm', 'w') as f:
    #        f.write(circuit.qasm())
