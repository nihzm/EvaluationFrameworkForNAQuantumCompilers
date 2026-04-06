import mapomatic.layouts as mply
from qiskit import transpile
import pdb
import numpy as np
import mapomatic.circuits as mm
from qiskit.circuit import QuantumCircuit
from qiskit.compiler import transpile
from qiskit.quantum_info import hellinger_fidelity
from qiskit_aer import AerSimulator
#from quasi_distr import QuasiDistr
from qiskit import QuantumCircuit
from qiskit.converters import circuit_to_dag
import networkx as nx
#from qiskit_optimization.applications import Maxcut
from qiskit.circuit.library import QAOAAnsatz

FONTSIZE = 12
ISBETTER_FONTSIZE = FONTSIZE + 2
WIDE_FIGSIZE = (13, 2.8)
COLUMN_FIGSIZE = (6.5, 3.4)
COLUMN_FIGSIZE_2 = (7.5, 4)

DESIRED_SUCCESS_PROBABILITY = 0.666

def calculate_expected_fidelity(circuit, backend):
    dag = circuit_to_dag(circuit)
    fidelity = 1
    decoherence_fidelity = 1
    for gate in dag.gate_nodes():
        if gate.name == "ecr":
            q1, q2 = gate.qargs[0]._index, gate.qargs[1]._index
            fidelity *= (1 - backend.target["ecr"][(q1, q2)].error)
        elif gate.name == "cx":
            q1, q2 = gate.qargs[0]._index, gate.qargs[1]._index
            fidelity *= (1 - backend.target["cx"][(q1, q2)].error)
        else:
            q = gate.qargs[0]._index
            fidelity *= (1 - backend.target[gate.name][(q,)].error)
    for wire in dag.wires:
        duration = 0.0
        for gate in dag.nodes_on_wire(wire, only_ops=True):
            if gate.name == "barrier":
                continue
            elif gate.name == "ecr":
                q1, q2 = gate.qargs[0]._index, gate.qargs[1]._index
                q = gate.qargs[0]._index
                duration += backend.target["ecr"][(q1, q2)].duration
            elif gate.name == "cx":
                q1, q2 = gate.qargs[0]._index, gate.qargs[1]._index
                duration += backend.target["cx"][(q1, q2)].duration
            else:
                q = gate.qargs[0]._index
                duration += backend.target[gate.name][(q,)].duration
        if duration > 0:
            qp = backend.qubit_properties(wire._index)
            t1 = np.exp(-duration / qp.t1)
            t2 = np.exp(-duration / qp.t2)
            decoherence_fidelity *= t1 * t2                
    #estimated_shots_without_decoherence = np.log(1 - DESIRED_SUCCESS_PROBABILITY) / np.log(1 - fidelity)
    #estimated_shots = np.log(1 - DESIRED_SUCCESS_PROBABILITY) / np.log(1 - fidelity * decoherence_fidelity)
    #return fidelity * decoherence_fidelity, fidelity, int(np.ceil(estimated_shots)), int(np.ceil(estimated_shots_without_decoherence))
    return fidelity


'''

def qaoa_maxcut_gen(n_nodes: int, degree: int) -> QuantumCircuit:

    #random graph
    graph = nx.random_regular_graph(degree, n_nodes)
    #pdb.set_trace()

    maxcut = Maxcut(graph)
    cubo = maxcut.to_quadratic_program()
    hamiltonian = cubo.objective.to_dict()
    qaoa = QAOAAnsatz(hamiltonian['linear'], hamiltonian['quadratic'], reps=1)
    qc = qaoa.to_circuit()

    return qc

def predict_fidelity(circuit, backend, cost_function=None, call_limit=None) -> float:
    
    if cost_function is None:
        cost_function = mply.default_cost

    coupling_map = backend.configuration().coupling_map

    try:
        trans_qc_list = transpile([circuit]*5, backend, optimization_level=3, layout_method='sabre', routing_method='sabre')

        best_cx_count = [circ.num_nonlocal_gates() for circ in trans_qc_list]
        best_idx = np.argmin(best_cx_count)
        trans_qc = trans_qc_list[best_idx]

    except NameError as e:
        print("[ERROR] - Can't transpile circuit on backend {}".format(backend.name()))
        return 1
    
    circ = mm.deflate_circuit(trans_qc)

    circ_qubits = circ.num_qubits
    circuit_gates = set(circ.count_ops()).difference({'barrier', 'reset', 'measure'})
    
    layouts = mply.matching_layouts(circ, coupling_map, call_limit=(call_limit if call_limit else int(1e3)))
    layout_and_error = mply.evaluate_layouts(circ, layouts, backend,cost_function=cost_function)

    if any(layout_and_error):
        best_error = layout_and_error[0][1]
        for l in layout_and_error:
            if l[1] < best_error:
                best_error = l[1]
    else:
        print("[ERROR] - No layout found for circuit on backend {}".format(backend.name()))
        return 1            

    return 1-best_error


def calculate_fidelity(circuit: QuantumCircuit, results:list[list]) -> float:
    res = []
    for i in results:
        res.append(QuasiDistr.from_counts(i))
    
    ideal_result = QuasiDistr.from_counts(
        AerSimulator()
        .run(transpile(circuit, AerSimulator(), optimization_level=0), shots=20000)
        .result()
        .get_counts()
    )
    fids = []
    for i in res:
        fids.append(hellinger_fidelity(ideal_result, i))

    return np.mean(fids)


def estimate_fidelity(circ, backend):
    """
    Parameters:
        circ (QuantumCircuit): circuit of interest
        layouts (list of lists): List of specified layouts
        backend (IBMQBackend): An IBM Quantum backend instance

    Returns:
        list: Tuples of layout and error
    """

    # Make a single layout nested
    props = backend.properties()
    fid = 1
    for item in circ._data:
        if item[0].num_qubits == 2:
            q0 = circ.find_bit(item[1][0]).index
            q1 = circ.find_bit(item[1][1]).index
            fid *= (1-props.gate_error(item[0].name, [q0, q1]))

        elif item[0].name in ['sx', 'x', 'rz']:
            q0 = circ.find_bit(item[1][0]).index
            fid *= 1-props.gate_error(item[0].name, q0)

        elif item[0].name in ['measure', 'reset']:
            q0 = circ.find_bit(item[1][0]).index
            fid *= 1-props.readout_error(q0)

    return fid

#def predict_fidelity_transpiled(circuit, backend, cost_function=None) -> float:
#    
#    #(circ, layouts, backend, cost_function=None):
#    #    circ (QuantumCircuit): circuit of interest
#    #    layouts (list): Specified layouts
#    #    backend (IBMQBackend): An IBM Quantum backend instance
#    #    cost_function (callable): Custom cost function, default=None
#
#    #Returns:
#    #    list: Tuples of layout, backend name, and cost   
#
#    layouts =  mply.matching_layouts(circuit, backend.configuration().coupling_map, call_limit=int(1e3))
#
#    circuit_gates = set(circuit.count_ops()).difference({'barrier', 'reset', 'measure'})
#
#    if not circuit_gates.issubset(backend.configuration().basis_gates):
#        return []
#    
#    if not isinstance(layouts[0], list):
#        layouts = [layouts]
#    
#    if cost_function is None:
#        cost_function = mply.default_cost
#    
#    out = cost_function(circuit, layouts, backend)
#    
#    out.sort(key=lambda x: x[1])
#    
#    return out

'''