from qiskit.converters import circuit_to_dag
import numpy as np

DESIRED_SUCCESS_PROBABILITY = 0.6666
    
def calculate_expected_fidelity(circuit, backend):
    dag = circuit_to_dag(circuit)
    fidelity = 1
    decoherence_fidelity = 1
    for gate in dag.gate_nodes():
        if gate.name in ("ecr", "cx", "cz"):
            q1, q2 = gate.qargs[0]._index, gate.qargs[1]._index
            fidelity *= (1 - backend.target[gate.name][(q1, q2)].error)
        else:
            q = gate.qargs[0]._index
            fidelity *= (1 - backend.target[gate.name][(q,)].error)
    for wire in dag.wires:
        duration = 0.0
        for gate in dag.nodes_on_wire(wire, only_ops=True):
            if gate.name == "barrier":
                continue
            elif gate.name in ("ecr", "cx", "cz"):
                q1, q2 = gate.qargs[0]._index, gate.qargs[1]._index
                q = gate.qargs[0]._index
                duration += backend.target[gate.name][(q1, q2)].duration
            else:
                q = gate.qargs[0]._index
                duration += backend.target[gate.name][(q,)].duration
        if duration > 0:
            qp = backend.qubit_properties(wire._index)
            t1 = np.exp(-duration / qp.t1)
            t2 = np.exp(-duration / qp.t2)
            decoherence_fidelity *= t1 * t2                
    estimated_shots_without_decoherence = np.log(1 - DESIRED_SUCCESS_PROBABILITY) / np.log(1 - fidelity)
    estimated_shots = np.log(1 - DESIRED_SUCCESS_PROBABILITY) / np.log(1 - fidelity * decoherence_fidelity)
    return fidelity * decoherence_fidelity, fidelity, estimated_shots, estimated_shots_without_decoherence

def calculate_expected_fidelity_ideal(circuit, two_qubit_gate_fidelity=0.995, single_qubit_gate_fidelity=0.999):
    dag = circuit_to_dag(circuit)
    fidelity = 1
    for gate in dag.gate_nodes():
        if gate.name in ("ecr", "cx", "cz"):
            fidelity *= two_qubit_gate_fidelity
        elif gate.name == "measure" or gate.name == "barrier":
            continue
        else:
            fidelity *= single_qubit_gate_fidelity
    estimated_shots = np.log(1 - DESIRED_SUCCESS_PROBABILITY) / np.log(1 - fidelity)
    return fidelity, estimated_shots

def calculate_swap_overhead(actual_circuit, transpiled_circuit):
    actual_ops = actual_circuit.count_ops()
    transpiled_ops = transpiled_circuit.count_ops()
    return int((transpiled_ops["ecr"] - actual_ops["cx"]) / 3)