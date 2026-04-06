from qiskit.quantum_info import SparsePauliOp
from pysat.formula import CNF
import numpy as np

class Max3satHamiltonian:
    def __init__(self, file = None, formula = None):
        if formula is not None:
            self.formula = formula
        else:
            self.formula = CNF(from_file=file)
        self.single_map = {}
        self.quadratic_map = {}
        self.cubic_map = {}
        for clause in self.formula.clauses:
            variables = np.sort(np.abs(clause)) - 1
            signs = np.sign([clause[i] for i in np.argsort(np.abs(clause))])
            for i in range(len(variables)):
                v_i = variables[i]
                if v_i not in self.single_map:
                    self.single_map[v_i] = 0
                self.single_map[v_i] += -signs[i]
                if self.single_map[v_i] == 0:
                    self.single_map.pop(v_i)
                for j in range(i + 1, len(variables)):
                    v_j = variables[j]
                    if (v_i, v_j) not in self.quadratic_map:
                        self.quadratic_map[(v_i, v_j)] = 0
                    self.quadratic_map[(v_i, v_j)] += -(signs[i] * signs[j])
                    if self.quadratic_map[(v_i, v_j)] == 0:
                        self.quadratic_map.pop((v_i, v_j))
                    for k in range(j + 1, len(variables)):
                        v_k = variables[k]
                        if (v_i, v_j, v_k) not in self.cubic_map:
                            self.cubic_map[(v_i, v_j, v_k)] = 0
                        self.cubic_map[(v_i, v_j, v_k)] += -(signs[i] * signs[j] * signs[k])
                        if self.cubic_map[(v_i, v_j, v_k)] == 0:
                            self.cubic_map.pop((v_i, v_j, v_k))

    def __pauli_string(self, indices):
        pauli_string = ["I"] * self.formula.nv
        for i in indices:
            pauli_string[i] = "Z"
        return "".join(pauli_string)
    
    def get_pauli_list(self):
        pauli_list = []
        for i in range(self.formula.nv):
            if i in self.single_map:
                substring = self.__pauli_string([i])
                pauli_list.append((self.single_map[i], substring, (i, )))
            for j in range(i + 1, self.formula.nv):
                if (i, j) in self.quadratic_map:
                    substring = self.__pauli_string([i, j])
                    pauli_list.append((self.quadratic_map[(i, j)], substring, (i, j)))
                for k in range(j + 1, self.formula.nv):
                    if (i, j, k) in self.cubic_map:
                        substring = self.__pauli_string([i, j, k])
                        pauli_list.append((self.cubic_map[(i,j,k)], substring, (i, j, k)))
        return pauli_list

    def get_sparse_pauli_operator(self):
        pauli_list = self.get_pauli_list()
        data, coeffs = [], []
        for coeff, pauli_str, qubits in pauli_list:
            data.append(pauli_str)
            coeffs.append(coeff)
        return SparsePauliOp(data, coeffs=coeffs)
    
    
                        
