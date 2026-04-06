from qiskit.quantum_info import SparsePauliOp
from pysat.formula import CNF
import numpy as np

class Max3satHamiltonian:
    def __init__(self, file):
        self.formula = CNF(from_file=file)
        self.single_terms = np.zeros(self.formula.nv)
        self.quadratic_terms = np.zeros((self.formula.nv, self.formula.nv))
        self.cubic_terms = np.zeros((self.formula.nv, self.formula.nv, self.formula.nv))
        for clause in self.formula.clauses:
            variables = np.sort(np.abs(clause)) - 1
            signs = np.sign([clause[i] for i in np.argsort(np.abs(clause))])
            for i in range(len(variables)):
                v_i = variables[i]
                self.single_terms[v_i] += -signs[i]
                for j in range(i + 1, len(variables)):
                    v_j = variables[j]
                    self.quadratic_terms[v_i][v_j] += -(signs[i] * signs[j])
                    for k in range(j + 1, len(variables)):
                        v_k = variables[k]
                        self.cubic_terms[v_i][v_j][v_k] += -(signs[i] * signs[j] * signs[k])

    def __pauli_string(self, indices):
        pauli_string = ["I"] * self.formula.nv
        for i in indices:
            pauli_string[i] = "Z"
        return "".join(pauli_string)
    
    def get_pauli_list(self):
        pauli_list = []
        for i in range(self.formula.nv):
            if self.single_terms[i] != 0:
                substring = self.__pauli_string([i])
                pauli_list.append((self.single_terms[i], substring, (i, )))
            for j in range(i + 1, self.formula.nv):
                if self.quadratic_terms[i][j] != 0:
                    substring = self.__pauli_string([i, j])
                    pauli_list.append((self.quadratic_terms[i][j], substring, (i, j)))
                for k in range(j + 1, self.formula.nv):
                    if self.cubic_terms[i][j][k] != 0:
                        substring = self.__pauli_string([i, j, k])
                        pauli_list.append((self.cubic_terms[i][j][k], substring, (i, j, k)))
        return pauli_list

    def get_sparse_pauli_operator(self):
        pauli_list = self.get_pauli_list()
        data, coeffs = [], []
        for coeff, pauli_str, qubits in pauli_list:
            data.append(pauli_str)
            coeffs.append(coeff)
        return SparsePauliOp(data, coeffs=coeffs)
    
    
                        