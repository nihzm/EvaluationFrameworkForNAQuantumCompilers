from qiskit.circuit import QuantumCircuit, Parameter, ParameterVector

class QAOA:
    def __init__(self, cost_operator):
        self.cost_operator = cost_operator.get_pauli_list()
        self.num_qubits = 0
        if len(self.cost_operator) > 0:
            self.num_qubits = len(self.cost_operator[0][1])

    def equal_superposition_circuit(self):
        circuit = QuantumCircuit(self.num_qubits)
        for i in range(self.num_qubits):
            circuit.h(i)
        return circuit

    def mixer_operator_circuit(self, parameter):
        circuit = QuantumCircuit(self.num_qubits)
        for i in range(self.num_qubits):
            circuit.rx(2 * parameter, i)
        return circuit
        
    def cost_operator_circuit(self, parameter):
        circuit = QuantumCircuit(self.num_qubits)
        for coeff, _, qubits in self.cost_operator:
            for i in range(len(qubits) - 1):
                circuit.cx(qubits[i], qubits[i + 1])
            circuit.rz(2 * coeff * parameter, qubits[-1])
            for i in reversed(range(1, len(qubits))):
                circuit.cx(qubits[i - 1], qubits[i])
        return circuit

    def naive_qaoa_circuit(self, depth):
        cost_params = ParameterVector("phi", length=depth)
        mixer_params = ParameterVector("beta", length=depth)
        circuit = self.equal_superposition_circuit()
        for i in range(depth):
            circuit.compose(self.cost_operator_circuit(cost_params[i]), inplace=True)
            circuit.compose(self.mixer_operator_circuit(mixer_params[i]), inplace=True)
        return circuit, cost_params, mixer_params